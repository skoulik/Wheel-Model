"""How long a lot stays: the call-grid tax, the survival curve, and E[W].

    python code/examples/holding_time.py
    python code/examples/holding_time.py --measure Q
    python code/examples/holding_time.py --n 1        # calls on the put clock

Backs eq:siegmund, eq:survival, eq:holding and eq:holding-siegmund in
section 07.  This is the exemplar for a module that hangs off a killed walk.

Note what is merged here and what is not.  Everything above comes out of one
`occupation()` solve, or is the closed form the section compares that solve
against -- one argument, one footnote, one script.  eq:trapped is a different
formula on a different regime and lives in its own module, even though it
sits in the same section.  The cut follows the code, not the headings.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_occupation, need_stationary,      # noqa: E402
                               resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "Holding time: first passage on the call grid"
SECTION = "sec:holding"
EQ = ["eq:siegmund", "eq:wald", "eq:wald-holding", "eq:survival",
      "eq:survival-step",
      "eq:holding", "eq:holding-siegmund"]

# The columns section 07 tabulates, in years.  Quoted in weeks up to half a
# year and in years after that; they land on exact call periods only when the
# call grid divides them, which is why the printed labels are recomputed.
COLUMNS = [4 / 52, 8 / 52, 12 / 52, 24 / 52, 1.0, 2.0, 5.0, 10.0, 20.0]

FIELDS = [
    ("tax", "call-grid tax, beta*sigma*sqrt(tau_c)", ".4f"),
    ("x0", "typical entry depth E[x0]", ".4f"),
    ("ratio", "  the tax as a multiple of it", ".2f"),
    # BETA is the overshoot a barrier infinitely far away would charge; the
    # article's barrier is 0.28 of a step off, and Wald's identity says what it
    # is really paying.  Both are printed because the section quotes both.
    ("b", "barrier distance E[x0]/(sigma*sqrt(tau_c)), in steps", ".3f"),
    ("overshoot", "the overshoot actually charged, in steps", ".3f"),
    ("theta", "  a period's drift in step units, nu*sqrt(tau_c)/sigma", ".3f"),
    ("far", "  the b -> infinity constant, beta + theta/4", ".3f"),
    ("near", "  the b -> 0 constant, the mean first ladder height", ".3f"),
    ("tax_charged", "  the tax that makes", ".4f"),
    ("ratio_charged", "  and its multiple over E[x0]", ".2f"),
    ("entry_share", "  entry's share of the hole a lot must climb", ".1%"),
    ("q_Ex0", "exit probability of a fresh lot, q(E[x0])", ".3f"),
    ("naive", "  the naive 1/q answer, in periods", ".2f"),
    ("columns", "survival curve, at the columns below", ".2f"),
    ("depth_cols", "  mean depth of those still held, same columns", ".2f"),
    ("cc_age", "  call premium at entry / 1 y / 2 y, in bp", ".4f"),
    ("closed_mean", "mean life of lots closing inside 2 y, in years", ".2f"),
    ("closed_median", "  their median, in call periods", "d"),
    ("over_measured", "overshoot measured off the absorbed mass, in steps", ".3f"),
    ("wald_gap", "  Wald identity: relative gap between its two sides", ".1e"),
    ("labels", "  ", ">6s"),
    ("median", "median lifetime, in call periods", "d"),
    ("median_wk", "  the same, in weeks", ".0f"),
    ("EW", "E[W], the mean holding time (years)", ".2f"),
    ("EW_siegmund", "  the Siegmund closed form", ".2f"),
    ("EW_far", "  Wald at the far-barrier constant beta + theta/4", ".2f"),
    ("EW_near", "  Wald at the mean ladder height, the b -> 0 end", ".2f"),
    ("prem", "call premiums collected per lot over its life", ".4f"),
    ("exitcost", "upside surrendered per lot at call-away", ".4f"),
]


def _label(years):
    return f"{years * 52:.0f} wk" if years < 1 else f"{years:.0f} y"


def requires(cfg, measure="P", horizon=None, **kw):
    # Two walks, and the split is not an oversight.  E[W] sums over a lot's
    # whole life, so it is carried by the tail the near grid truncates and
    # biases -- it reads 2.05 there against the extrapolated 2.10.  The early
    # survival columns are the other way round: the near grid runs at h = 0.01
    # against the extrapolation's 0.0125, so it resolves the fast lane better,
    # and it is where the section's 0.60/0.46 come from.
    return [need_occupation(cfg, measure), need_stationary(cfg, measure)]



def _closed(surv, tau_c, years):
    """Mean and median life of the lots that close inside a window.

    The window censors the slow lots, which is the whole point: they are
    still open, so a track record cannot see them.  Returns (mean in years,
    median in call periods) over the closed ones only.
    """
    W = round(years / tau_c)
    pmf = [surv[j] - surv[j + 1] for j in range(min(W, len(surv) - 1))]
    tot = sum(pmf)
    mean = sum((j + 1) * p for j, p in enumerate(pmf)) / tot
    c = 0.0
    for j, p in enumerate(pmf):
        c += p
        if c >= tot / 2:
            return mean * tau_c, j + 1
    return mean * tau_c, len(pmf)


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    # This module answers a nu > 0 question.  At nu = 0 the depth walk is
    # driftless: every lot still leaves, with probability one, but the expected
    # wait is infinite -- null recurrence, not a degeneracy.  Below zero a
    # positive fraction never leaves at all.  Either way the grid returns a
    # finite number only because it truncates the tail (17.10 years at
    # sigma = 30%, which is the lattice and not the strategy), so refuse rather
    # than print it.  eq:count-criterion is the boundary; holding_trapped.py is
    # the module for the far side of it.
    _m, _s = cfg.world(measure)
    _nu = _m - _s * _s / 2
    if _nu <= 0:
        raise SystemExit(
            "nu = %+.4f at sigma = %.1f%%: past the count boundary "
            "(eq:count-criterion, nu = m - sigma^2/2 > 0), where a positive "
            "fraction of lots never leaves and the mean is infinite.  Use "
            "holding_trapped.py." % (_nu, cfg.sigma * 100))
    # A sign test is not enough.  At sigma = 30% exactly, nu is zero in real
    # arithmetic and a hair above it in floating point, so the walk sails past
    # the check and prints 1.2e16 years.  Refuse on the estimate instead: if
    # the closed form puts a lot's mean life past a century the answer is not
    # about a strategy any more, and what the grid returns is its own
    # truncation rather than the tail.
    _est = (model.entry_mean(cfg, measure) + model.grid_tax(cfg, measure)) / _nu
    if _est > 100.0:
        raise SystemExit(
            "nu = %.2e at sigma = %.1f%%: on the count boundary, where the "
            "walk is driftless.  Every lot still leaves, with probability one, "
            "but the expected wait is infinite -- eq:holding-siegmund puts it "
            "at %.3g years.  Whatever this module printed would be the "
            "lattice, not the strategy."
            % (_nu, cfg.sigma * 100, _est))
    near = resolve(ctx, need_occupation(cfg, measure))
    full = resolve(ctx, need_stationary(cfg, measure))
    econ = model.economics(cfg, measure, full)
    surv = near["surv"]
    median = model.median_periods(near)
    tax = model.grid_tax(cfg, measure)
    # Off the extrapolated walk, not the near grid: the identity is only as
    # exact as the E[W] put into it, and the near grid reads 2.05 against 2.10.
    wald = model.overshoot_wald(cfg, measure, full)
    # The section's opening names q at the *typical* entry depth: the naive 1/q
    # argument treats every period as one coin at one depth, so the object is
    # eq:qx evaluated at E[x0], which is the 0.404 section 06 tabulates.  Not
    # near["q(x0)"], which despite its name is 1 - S_1 -- q averaged over the
    # whole entry law.  Both round to 0.40 and they are not the same quantity;
    # this checks the one the sentence makes a claim about.
    q_entry = model.q_exit(cfg, measure, econ["E[x0]"])
    step = cfg.world(measure)[1] * model.sqrt(cfg.tau_c)
    return {
        "tax": tax,
        "x0": econ["E[x0]"],
        "ratio": tax / econ["E[x0]"],
        "b": wald["b"],
        "overshoot": wald["overshoot"],
        # The two ends of the bracket, quoted in the text as the values that
        # 0.667 has to fall between.  Both are Chang & Peres constants.
        "theta": wald["theta"], "far": wald["far"], "near": wald["near"],
        "tax_charged": wald["tax"],
        "ratio_charged": wald["ratio"],
        "entry_share": wald["entry_share"],
        "q_Ex0": q_entry,
        "naive": 1 / q_entry,
        "depth_cols": [near["depth"][round(y / cfg.tau_c)] for y in COLUMNS
                       if round(y / cfg.tau_c) < len(near["depth"])],
        # Survivorship: average only the lots that have *closed* inside a
        # two-year window and the mean collapses, because the lots carrying
        # it are the ones still open.  The median barely moves.  This is a
        # prediction for section 14 to test, not a report of what it found.
        "closed_mean": _closed(full["surv"], cfg.tau_c, 2.0)[0],
        "closed_median": _closed(full["surv"], cfg.tau_c, 2.0)[1],
        "haz": [1 - surv[j + 1] / surv[j] for j in (0, 1, 7)],
        # The overshoot read straight off the absorbed mass, which owes
        # nothing to Wald -- so the identity can be tested rather than
        # assumed.  The gap is O(h^2) and is the grid, not the identity.
        "over_measured": near["E[overshoot]"] / step,
        "wald_gap": abs((econ["E[x0]"] + near["E[overshoot]"])
                        / (near["E[J]"] * econ["nu"] * cfg.tau_c) - 1),
        # What the call is still paying at those depths: the premium a lot
        # carries fresh, after a year, and after two.
        "cc_age": [model.call_premium(cfg, near["depth"][j]) * 1e4
                   for j in (0, 13, 26)],
        "columns": [surv[round(y / cfg.tau_c)] for y in COLUMNS
                    if round(y / cfg.tau_c) < len(surv)],
        "labels": [_label(y) for y in COLUMNS
                   if round(y / cfg.tau_c) < len(surv)],
        "median": median,
        "median_wk": None if median is None else median * cfg.tau_c * 52,
        "EW": econ["E[T]"],
        "EW_siegmund": econ["E[T]_siegmund"],
        "EW_far": wald["E[T]_far"],
        "EW_near": wald["E[T]_near"],
        # Per-lot lifetime sums over the same killed walk: premium taken in and
        # upside handed back.  Quoted in section 09, but they come off this walk.
        "prem": near["E[prem]"],
        "exitcost": near["E[exitcost]"],
    }


CASES = [
    Case("", {
        "tax": (0.0323, 0.0005),        # section 07: "0.5826 x 0.20 x sqrt(1/13)"
        "ratio": (2.09, 0.05),          # what beta alone would say
        "x0": (0.0155, 0.0005),
        "b": (0.279, 0.002),            # "0.28 of one period's step"
        "overshoot": (0.667, 0.005),    # "the grid charges 0.667"
        "theta": (0.035, 0.001),        # "theta = nu*sqrt(tau_c)/sigma = 0.035"
        "far": (0.591, 0.002),          # "beta + theta/4 = 0.591"
        "near": (0.722, 0.002),         # "e^(beta*theta)/sqrt(2) = 0.722"
        "tax_charged": (0.0370, 0.0005),
        "ratio_charged": (2.39, 0.03),  # "2.4 times the typical entry depth"
        "entry_share": (0.295, 0.01),   # "29% entry, 71% grid"
        "q_Ex0": (0.403, 0.005),        # "a 40% chance of leaving on its first call"
        "naive": (2.48, 0.02),          # "would have said ten weeks" (x4 wk)
        "columns": ([0.60, 0.46, 0.38, 0.27, 0.18, 0.12, 0.07, 0.04, 0.02], 0.005),
        # "0.40 on the first call, 0.23 on the second, 0.07 by the eighth"
        "haz": ([0.405, 0.234, 0.068], 0.002),
        # "160 basis points ... about a hundredth of one ... below a millionth"
        "cc_age": ([159.593, 0.0105, 0.0000], 0.002),
        # "0.666 steps, measured" -- against 0.667 inferred through Wald
        "over_measured": (0.666, 0.005),
        # "the mean holding time is 0.30 years against the true 2.10"
        "closed_mean": (0.30, 0.01),
        # "eight weeks either way" -- 2 call periods, as the true median
        "closed_median": (2, 0),
        "depth_cols": ([0.05, 0.08, 0.09, 0.14, 0.21, 0.31, 0.48, 0.66, 0.90], 0.005),
        "median": (2, 0),               # "a median of eight weeks"
        "EW": (2.10, 0.02),             # eq:holding
        "EW_siegmund": (1.9, 0.05),     # eq:holding-siegmund, "9% below"
        # The bracket: both ends are published constants and the exact 2.10
        # sits between them, which is what section 07 quotes instead of "9%".
        "EW_far": (1.93, 0.02),
        "EW_near": (2.22, 0.02),
        "prem": (0.0372, 0.001),        # section 09: "a lot collects 3.72% ... in call premiums"
        "exitcost": (0.0358, 0.001),    # section 09: "and surrenders 3.58% in upside at call-away"
    }, note="Standard regime"),
    Case("--measure Q", {
        "EW": (9.0, 1.0),               # "E[W] ~ 9 years" -- a round figure on
    }, note="under the market's pricing drift"),   # purpose, see the section
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
