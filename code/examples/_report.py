"""Coverage and the reproduction appendix.  Stdlib only.

Two things the policy needs to stay true rather than aspirational:

*   `coverage()` reads every `{#eq:...}` anchor out of `sections/` and checks
    it against the formulas the example modules claim to back.  A formula
    with no script is a number a reader cannot check; a script backing no
    formula is either dead or an anchor someone forgot to add.

*   `appendix()` generates the reproduction table -- every figure the article
    quotes, the command that produces it, and the value asserted.  It is
    generated rather than written because a hand-maintained version of this
    table drifts within a month.

Both are called from `verify_examples.py`; `python -m examples --coverage`
and `--appendix` are the shortcuts.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples import _harness as H                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTIONS = os.path.join(ROOT, "sections")

_EQ = re.compile(r"\{#(eq:[a-z0-9-]+)\}")
_FOOTNOTE = re.compile(r"code/examples/([a-z0-9_]+)\.py")

# The article's footnote convention: a formula tagged {#eq:holding} is
# reproduced by a footnote defined as [^eq-holding], whose body names the
# script.  Keying the two together is what lets coverage() check that the
# footnote a reader follows actually leads to the code for *that* formula.
_FOOTNOTE_DEF = re.compile(r"^\[\^(eq-[a-z0-9-]+)\]:(.*)$", re.MULTILINE)


def _anchor_of(footnote_label):
    return "eq:" + footnote_label[len("eq-"):]


APPENDIX = "99-reproduction.md"     # generated; see appendix() below


def section_files():
    """The article's prose sections.

    The reproduction appendix is excluded deliberately: it names every module,
    so counting it would let the citation check pass without a single footnote
    in the prose -- the appendix would certify itself.
    """
    return sorted(f for f in os.listdir(SECTIONS)
                  if f.endswith(".md") and f != APPENDIX)


def declared_anchors():
    """Every {#eq:...} the article defines, mapped to the file defining it."""
    out = {}
    for name in section_files():
        with open(os.path.join(SECTIONS, name), encoding="utf-8") as fh:
            for anchor in _EQ.findall(fh.read()):
                out.setdefault(anchor, name)
    return out


def cited_modules():
    """Every example module the article's footnotes point a reader at."""
    out = {}
    for name in section_files():
        with open(os.path.join(SECTIONS, name), encoding="utf-8") as fh:
            for mod in _FOOTNOTE.findall(fh.read()):
                out.setdefault(mod, set()).add(name)
    return out


def footnote_defs():
    """Every reproduction footnote the article defines, label -> its text."""
    out = {}
    for name in section_files():
        with open(os.path.join(SECTIONS, name), encoding="utf-8") as fh:
            for label, text in _FOOTNOTE_DEF.findall(fh.read()):
                out[label] = text
    return out


def coverage(mods=None, require_citations=True):
    """Check the policy holds.  Returns a list of failure strings."""
    mods = H.discover() if mods is None else mods
    anchors = declared_anchors()
    backed = {}
    for m in mods:
        for eq in m.EQ:
            backed.setdefault(eq, []).append(m.__name__.rsplit(".", 1)[-1])

    failures = []
    for anchor, where in sorted(anchors.items()):
        if anchor not in backed:
            failures.append(f"{anchor} ({where}) has no example module")
    for anchor, owners in sorted(backed.items()):
        if anchor not in anchors:
            failures.append(f"{anchor} is backed by {owners} but no section defines it")
        elif len(owners) > 1:
            failures.append(f"{anchor} is claimed by more than one module: {owners}")

    if require_citations:
        # Every module must be reachable from the prose, and every reproduction
        # footnote must lead to the script that actually backs its formula --
        # a footnote pointing at the wrong module is worse than none.
        cited = cited_modules()
        owner = {name: m for m in mods
                 for name in [m.__name__.rsplit(".", 1)[-1]]}
        for m in mods:
            name = m.__name__.rsplit(".", 1)[-1]
            if name not in cited:
                failures.append(f"{name} is not cited by any section footnote")
        for label, text in footnote_defs().items():
            anchor = _anchor_of(label)
            named = _FOOTNOTE.findall(text)
            if anchor not in anchors:
                failures.append(f"footnote [^{label}] names no formula in any section")
            elif not named:
                failures.append(f"footnote [^{label}] names no script")
            elif not any(anchor in owner[n].EQ for n in named if n in owner):
                failures.append(
                    f"footnote [^{label}] points at {named}, which does not back {anchor}")

    print(f"  {len(anchors)} formulas in {len(section_files())} sections; "
          f"{len(backed)} backed by {len(mods)} modules; {len(failures)} gap(s)")
    return failures


def _show(value, spec):
    """One asserted figure, formatted as the module's own CLI would print it."""
    if isinstance(value, (list, tuple)):
        return " ".join(_show(v, spec) for v in value if v is not None)
    if isinstance(value, bool):
        return "yes" if value else "no"
    try:
        return format(value, spec) if spec else f"{value:g}"
    except (ValueError, TypeError):
        return f"{value:g}" if isinstance(value, float) else str(value)


def appendix(mods=None):
    """The reproduction appendix, as markdown."""
    mods = H.discover() if mods is None else mods
    anchors = declared_anchors()
    by_section = {}
    for m in mods:
        where = anchors.get(m.EQ[0], "?") if m.EQ else "?"
        by_section.setdefault(where, []).append(m)

    out = ["# Reproducing every figure in this article", "",
           "Every number quoted in the text is produced by a script in "
           "`code/examples/`, listed here with the arguments that produce the "
           "article's own value. Each script takes the model's full parameter "
           "set, so any row can be re-run at other values: pass `--help` to "
           "see them. This table is generated by "
           "`python -m examples --appendix`, not maintained by hand.", ""]

    for where in sorted(by_section):
        out += [f"## {where}", "",
                "| formula | command | the article's figures |",
                "|---|---|---|"]
        for m in sorted(by_section[where], key=lambda m: m.__name__):
            name = m.__name__.rsplit(".", 1)[-1]
            eqs = ", ".join(f"`{e}`" for e in m.EQ)
            spec = {k: s for k, _, s in m.FIELDS}
            for case in m.CASES:
                cmd = f"python code/examples/{name}.py {case.flags}".rstrip()
                figs = ", ".join(f"{k} = {_show(v[0], spec.get(k, ''))}"
                                 for k, v in case.expect.items())
                out.append(f"| {eqs} | `{cmd}` | {figs} |")
                eqs = ""            # only label the first row of a module
        out.append("")
    return "\n".join(out)
