"""Shared machinery for the worked examples.  Stdlib only.

An example module is a *presentation layer* over `model.py`: it parses
arguments, calls model functions, and formats the result.  It must not define
a formula -- `model.py` is the single source of those (see CLAUDE.md).  If a
number the article quotes has no function behind it, add the function to
`model.py`; do not compute it here.

A module supplies:

    TITLE      one line: what it computes
    SECTION    the section anchor it serves, e.g. "sec:holding"
    EQ         the equation anchors it backs, e.g. ["eq:holding"]
    FIELDS     [(key, label, format)] -- what the CLI prints, in order
    EXTRA      optional [(flag, kwargs)] -- knobs beyond Config/measure/horizon
    requires() the expensive solves it needs, as a list of Need
    compute()  the numbers, as a dict keyed by FIELDS' keys
    CASES      the article's own invocations, and what it claims they print

and ends with the standard main guard.  Copy an existing module; the two
exemplars are `entry_strike.py` (closed form, no solve) and `holding_time.py`
(hangs off one killed walk).

Two properties this buys, both of which the verifier enforces:

*   **The footnote's command is the tested command.**  A Case carries a
    command line, not a parameter dict -- the same string the article's
    footnote prints.  The verifier parses it through the module's own parser,
    so the reader's command and the assertion cannot drift apart.

*   **One parallel solve for the whole article.**  Modules declare their
    expensive walks instead of running them.  `verify_examples.py` unions
    every declaration, deduplicates, and issues a single `model.pmap`.  Run
    standalone (ctx=None) a module solves its own, so the CLI still works.

`compute()` may itself call `model.pmap` (the sweeps do).  It must therefore
never be submitted *as* a pmap job -- nested pools deadlock.  The verifier
calls compute() directly, in the parent process, and that is deliberate.
"""

import argparse
import os
import shlex
import sys
from dataclasses import fields
from typing import NamedTuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model                                                  # noqa: E402
from model import Config                                      # noqa: E402


# ----------------------------------------------------------------------
# Expensive solves, declared rather than run
# ----------------------------------------------------------------------

def cfg_key(C):
    """A hashable stand-in for a Config.

    Config is a plain dataclass, so eq=True leaves it unhashable and it
    cannot be a dict key itself.  Every field is a scalar, so the sorted
    item tuple is a faithful identity -- and it covers the derived fields
    too, which is harmless (they are functions of the others).
    """
    return tuple(sorted(vars(C).items()))


class Need(NamedTuple):
    """One expensive solve: what it is, and enough to run it."""
    kind: str          # "occupation" | "stationary" | "census"
    cfg: Config
    measure: str
    kw: tuple = ()     # sorted extra arguments, e.g. (("edges", (...)),)

    @property
    def key(self):
        return (self.kind, cfg_key(self.cfg), self.measure, self.kw)


def need_occupation(cfg, measure="P", **kw):
    """The near-grid killed walk.  Correct for *horizon-weighted* numbers.

    Anything read through `economics(..., horizon=H)` is weighted so that the
    far tail contributes almost nothing, and the near grid (h = 0.01 over
    x_max = 4) resolves what is left.  Use this for E[I] at 5/10/30 years,
    the finite-horizon income and capital, and the shallow census.
    """
    return Need("occupation", cfg, measure, tuple(sorted(kw.items())))


def need_stationary(cfg, measure="P", **kw):
    """The Richardson-extrapolated walk.  Required for *whole-lifetime* numbers.

    A quantity summed over a lot's entire life -- E[J], E[W], the equilibrium
    inventory, the stationary census -- is carried by the tail, where the near
    grid both truncates (x_max = 4) and biases upward by O(h^2).  The two
    disagree by more than the article's own precision: E[W] reads 2.05 on the
    near grid against the extrapolated 2.10 that section 07 quotes.  Choosing
    between these is a correctness decision, not a speed one; stationary()
    costs well under a second at the running example.

    Off the running example there is a second trap -- the period cap can
    truncate before the grid does -- and then the figure must go through
    `model.stationary_converged()`.  See CLAUDE.md.
    """
    return Need("stationary", cfg, measure, tuple(sorted(kw.items())))


def need_trapped_walk(cfg, measure="P", **kw):
    """The unshifted killed walk behind the exact trapped fraction.

    Costs a couple of seconds where nu <= 0 -- two grids, and each runs until
    the trapped mass has drifted out through x_max -- and nothing at all where
    nu > 0, which is every case the article runs bar one.  Declared like any
    other solve so it lands in the same parallel batch.
    """
    return Need("trapped", cfg, measure, tuple(sorted(kw.items())))


def need_census(cfg, measure="P", *, edges, horizon=None, **kw):
    """A depth census.  `edges` must be a tuple -- it goes into a cache key."""
    kw = dict(kw, edges=tuple(edges), horizon=horizon)
    return Need("census", cfg, measure, tuple(sorted(kw.items())))


def _solve_one(need):
    """Run one declared solve.  Module-level and picklable: it is a pmap job."""
    kw = dict(need.kw)
    if need.kind == "occupation":
        return model.occupation(need.cfg, need.measure, **kw)
    if need.kind == "stationary":
        return model.stationary(need.cfg, need.measure, **kw)
    if need.kind == "trapped":
        return model.trapped_fraction_walk(need.cfg, need.measure, **kw)
    if need.kind == "census":
        edges = list(kw.pop("edges"))
        return model.depth_census(need.cfg, need.measure, edges, **kw)
    raise ValueError(f"unknown solve {need.kind!r}")


def solve_all(needs, workers=None):
    """Deduplicate declared solves and run them in one parallel batch."""
    uniq = {}
    for n in needs:
        uniq.setdefault(n.key, n)
    results = model.pmap(_solve_one, list(uniq.values()), workers=workers)
    return dict(zip(uniq.keys(), results))


def resolve(ctx, need):
    """The solve's result: from the shared batch, or run it here if standalone."""
    if ctx is not None and need.key in ctx:
        return ctx[need.key]
    return _solve_one(need)


# ----------------------------------------------------------------------
# Cases: the article's own invocations
# ----------------------------------------------------------------------

class Case(NamedTuple):
    """One invocation the article quotes.

    `flags` is a command line -- exactly what the footnote prints, so that
    the reader's command and the verifier's assertion are the same string.
    `expect` maps a FIELDS key to (value, tolerance).  For a sequence field
    the value is a list of the same length, checked elementwise against the
    one tolerance; None as an element skips it.  A field the article does
    not quote is simply left out.
    """
    flags: str
    expect: dict
    note: str = ""


# ----------------------------------------------------------------------
# The common command line: every Config field, plus measure and horizon
# ----------------------------------------------------------------------

_SKIP_ARGS = {"label"}          # bookkeeping, not a model parameter


def _field_type(f):
    t = f.type
    if isinstance(t, str):                    # annotations may arrive as text
        t = {"int": int, "float": float, "str": str}.get(t, float)
    return t if t in (int, float, str) else float


def build_parser(mod):
    """The parser a module gets: Config fields, measure, horizon, its own EXTRA."""
    ap = argparse.ArgumentParser(
        prog=f"python code/examples/{mod.__name__.rsplit('.', 1)[-1]}.py",
        description=getattr(mod, "TITLE", mod.__doc__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ref = Config()
    for f in fields(Config):
        if not f.init or f.name in _SKIP_ARGS:
            continue
        ap.add_argument(f"--{f.name.replace('_', '-')}", dest=f.name,
                        type=_field_type(f), default=getattr(ref, f.name))
    ap.add_argument("--measure", choices=("P", "Q"), default="P",
                    help="P = real world (mu), Q = what option prices imply (r)")
    ap.add_argument("--horizon", type=float, default=30.0,
                    help="years; the article quotes finite horizons")
    ap.add_argument("--stationary", action="store_const", const=None,
                    dest="horizon", help="the equilibrium limit instead")
    for flag, kw in getattr(mod, "EXTRA", []):
        ap.add_argument(flag, **kw)
    return ap


def _params_from_args(args):
    """Split a parsed namespace into a Config and the loose keyword arguments."""
    seen = vars(args)
    cfg_kw = {f.name: seen[f.name] for f in fields(Config)
              if f.init and f.name not in _SKIP_ARGS}
    extra = {k: v for k, v in seen.items()
             if k not in cfg_kw and k not in ("measure", "horizon")}
    return dict(cfg=Config(**cfg_kw), measure=args.measure,
                horizon=args.horizon, **extra)


def params_from(mod, flags=""):
    """Turn a command line into the kwargs `requires` and `compute` take."""
    return _params_from_args(build_parser(mod).parse_args(shlex.split(flags)))


# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------

def _fmt_one(value, spec):
    if value is None:
        return "--"
    if isinstance(value, (list, tuple)):
        return "  ".join(format(v, spec) for v in value)
    return format(value, spec)


def render(mod, out):
    """The module's result as the CLI prints it, one field per line."""
    width = max(len(label) for _, label, _ in mod.FIELDS)
    lines = []
    for key, label, spec in mod.FIELDS:
        lines.append(f"  {label:<{width}}  {_fmt_one(out[key], spec)}")
    return "\n".join(lines)


def run_cli(mod, argv=None):
    """The standard main(): parse, compute, print."""
    params = _params_from_args(build_parser(mod).parse_args(argv))
    print(mod.TITLE)
    print(render(mod, mod.compute(**params)))


# ----------------------------------------------------------------------
# Discovery, for the verifier and the reproduction appendix
# ----------------------------------------------------------------------

def collect_needs(mods):
    """Every expensive solve every case of every module asks for."""
    needs = []
    for mod in mods:
        for case in mod.CASES:
            needs.extend(mod.requires(**params_from(mod, case.flags)))
    return needs


def check_case(mod, case, ctx=None):
    """Run one case.  Returns [(label, got, want, tol, ok)], one per claim."""
    out = mod.compute(ctx=ctx, **params_from(mod, case.flags))
    rows = []

    def one(label, got, want, tol):
        ok = got is not None and abs(got - want) <= tol
        rows.append((label, got, want, tol, ok))

    for key, (want, tol) in case.expect.items():
        got = out[key]
        if isinstance(want, (list, tuple)):
            if len(got) != len(want):
                rows.append((f"{key} (length)", len(got), len(want), 0, False))
                continue
            for i, (g, w) in enumerate(zip(got, want)):
                if w is not None:
                    one(f"{key}[{i}]", g, w, tol)
        else:
            one(key, got, want, tol)
    return rows


def report_cases(mods, ctx=None, quiet=False):
    """Check every case of every module.  Returns the list of failures."""
    failures = []
    for mod in mods:
        name = mod.__name__.rsplit(".", 1)[-1]
        for case in mod.CASES:
            head = f"{name} {case.flags}".rstrip()
            for label, got, want, tol, ok in check_case(mod, case, ctx):
                if not quiet or not ok:
                    shown = "None" if got is None else f"{got:.4f}"
                    print(f"{'PASS' if ok else 'FAIL'}  {head}  {label}: "
                          f"got {shown}, expected ~{want} (+/- {tol})")
                if not ok:
                    failures.append(f"{head}  {label}")
    return failures


def discover(strict=False):
    """Every example module, sorted by name.

    A module that fails to import is reported and skipped rather than taking
    the run down with it -- several of these are often being written at once,
    and a broken sibling should not stop you testing your own.  The verifier
    passes strict=True, where an unimportable example *is* a failure.
    """
    import importlib
    import pkgutil
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for mi in sorted(pkgutil.iter_modules([here]), key=lambda m: m.name):
        if mi.name.startswith("_"):
            continue
        try:
            out.append(importlib.import_module(f"examples.{mi.name}"))
        except Exception as exc:                       # noqa: BLE001
            if strict:
                raise
            print(f"  (skipping examples.{mi.name}: {type(exc).__name__}: {exc})")
    return out
