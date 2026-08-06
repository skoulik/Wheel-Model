"""Coverage and the reproduction appendix.  Stdlib only.

Four things the policy needs to stay true rather than aspirational:

*   `coverage()` reads every `{#eq:...}` anchor out of `sections/` and checks
    it against the formulas the example modules claim to back.  A formula
    with no script is a number a reader cannot check; a script backing no
    formula is either dead or an anchor someone forgot to add.

*   `references()` does the same job for citations: every `#ref:` a section
    cites must be an entry in the bibliography, and every entry must be an
    anchor.  Same reasoning -- a hand-maintained cross-reference set drifts
    within a month, and here the drift is silent, because a dead citation
    link still renders as text.

*   `registers()` checks section 00's two hand-maintained anchor lists against
    what the sections actually declare.  The other two checks left a hole
    between them: both read the sections directly, so four formula anchors
    stayed absent from the register that calls itself the single source of
    truth while every other check ran green.

*   `appendix()` generates the reproduction table -- every figure the article
    quotes, the command that produces it, and what that command prints.  It is
    generated rather than written because a hand-maintained version of this
    table drifts within a month, and it runs the cases rather than reading
    their assertions because a table that disagrees with its own printed
    command is worse than no table.

All four are called from `verify_examples.py`; `python -m examples
--coverage`, `--references`, `--registers` and `--appendix` are the shortcuts.
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
BIBLIOGRAPHY = "98-bibliography.md"  # the only file that may declare {#ref:}
NOTATION = "00-notation.md"          # declares both registers; see registers()

# Section 00's two registers, each introduced by its own phrase.  They are
# *declarations* of what the article means to contain, where declared_anchors()
# and section_heads() are what it does contain -- which is why registers()
# checks the two against each other rather than generating one from the other.
# One statement copied twice is not two statements agreeing.
_SEC_REGISTER = "Current anchors: "
_EQ_REGISTER = "Current anchors, in reading order within each section: "
# Groups in the formula register read `a, b, c (05)`, the first spelling it
# "(section 04)" in full.
_EQ_GROUP = re.compile(r"\((?:section\s+)?(\d\d)\)")
_SEC_TOKEN = re.compile(r"sec:[a-z0-9-]+")
_EQ_TOKEN = re.compile(r"eq:[a-z0-9-]+")

# A citation is a markdown link to a bibliography anchor; the numbers a reader
# sees are assigned at assembly, so the source never carries one.
_REF_ANCHOR = re.compile(r"\{#(ref:[a-z0-9-]+)\}")
_REF_CITE = re.compile(r"\]\(#(ref:[a-z0-9-]+)\)")
_ENTRY = re.compile(r"^- (.*)$", re.MULTILINE)
_UNVERIFIED = "[cite unverified]"

# Conventions get *quoted* in section 00, and a code span showing what a
# citation looks like is not one: it survives assembly as verbatim text and
# never becomes a \cite.  Counting it would inflate the citation census and,
# worse, let an entry look cited when nothing cites it.
_CODE = re.compile(r"`[^`]*`")


def section_files():
    """The article's prose sections.

    The reproduction appendix is excluded deliberately: it names every module,
    so counting it would let the citation check pass without a single footnote
    in the prose -- the appendix would certify itself.
    """
    return sorted(f for f in os.listdir(SECTIONS)
                  if f.endswith(".md") and f != APPENDIX)


def prose_files():
    """Sections that may *cite*, as opposed to define.

    The bibliography is excluded for the same reason the appendix is excluded
    above: its preamble shows what a citation looks like, and an example of
    the form is not a use of it.
    """
    return [f for f in section_files() if f != BIBLIOGRAPHY]


def section_heads():
    """Every `{#sec:...}` the article declares, mapped to the file declaring it.

    The counterpart of `declared_anchors` for whole sections, so a module that
    backs prose rather than a displayed formula can still say where it lives.
    """
    pat = re.compile(r"^#\s+.*\{#(sec:[A-Za-z0-9:_-]+)\}", re.M)
    out = {}
    for name in section_files():
        with open(os.path.join(SECTIONS, name), encoding="utf-8") as fh:
            for anchor in pat.findall(fh.read()):
                out.setdefault(anchor, name)
    return out


def declared_anchors():
    """Every {#eq:...} the article defines, mapped to the file defining it.

    Code spans are stripped for the reason given at `_CODE`, which applies to
    formula anchors word for word: section 00 shows what a declaration looks
    like -- ``E[I] = λ · E[W]  {#eq:little}`` -- and an example of the form is
    not a use of it.  Counting it filed eq:little under 00-notation.md, since
    that sorts first, and the appendix asks this function which section a
    module belongs to.
    """
    out = {}
    for name in section_files():
        for anchor in _EQ.findall(_read(name, strip_code=True)):
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


def _read(name, strip_code=False):
    with open(os.path.join(SECTIONS, name), encoding="utf-8") as fh:
        text = fh.read()
    return _CODE.sub("", text) if strip_code else text


def bibliography_entries():
    """Every {#ref:...} the bibliography declares, anchor -> its entry line."""
    if not os.path.exists(os.path.join(SECTIONS, BIBLIOGRAPHY)):
        return {}, []
    out, malformed = {}, []
    for line in _ENTRY.findall(_read(BIBLIOGRAPHY)):
        anchors = _REF_ANCHOR.findall(line)
        if not anchors:
            malformed.append(line)
        for a in anchors:
            out.setdefault(a, []).append(line)
    return out, malformed


def citations():
    """Every reference the prose cites, anchor -> the sections citing it."""
    out = {}
    for name in prose_files():
        for anchor in _REF_CITE.findall(_read(name, strip_code=True)):
            out.setdefault(anchor, set()).add(name)
    return out


def references():
    """Check the citation apparatus.  Returns a list of failure strings.

    Uncited entries are reported but do not fail: the bibliography is seeded
    with the whole reading list, and section 03 -- which will cite most of it
    -- is not written yet.  That tolerance is what stops the article shipping
    a padded bibliography by accident: the count is printed every run, so it
    has to fall to zero visibly rather than be discovered at assembly.
    """
    entries, malformed = bibliography_entries()
    cited = citations()

    failures = []
    for line in malformed:
        failures.append(f"bibliography entry has no {{#ref:}} anchor: {line[:60]}...")
    for anchor, lines in sorted(entries.items()):
        if len(lines) > 1:
            failures.append(f"{anchor} is declared by {len(lines)} bibliography entries")
    for anchor, where in sorted(cited.items()):
        if anchor not in entries:
            failures.append(f"{anchor} is cited by {sorted(where)} but the bibliography has no entry")

    # Anchors are name-based precisely so that no section hand-numbers a
    # citation; a {#ref:} declared outside the bibliography is a second
    # source of truth and would silently split the list at assembly.
    for name in prose_files():
        for anchor in _REF_ANCHOR.findall(_read(name, strip_code=True)):
            failures.append(f"{anchor} is declared in {name}; only {BIBLIOGRAPHY} may declare one")

    uncited = sorted(set(entries) - set(cited))
    unverified = sorted(a for a, lines in entries.items() if _UNVERIFIED in lines[0])
    print(f"  {len(entries)} entries, {len(cited)} cited from "
          f"{len({s for w in cited.values() for s in w})} sections; "
          f"{len(uncited)} uncited, {len(unverified)} unverified; {len(failures)} gap(s)")
    if uncited:
        print(f"    uncited: {', '.join(a[len('ref:'):] for a in uncited)}")
    if unverified:
        print(f"    bibliographic details unverified: "
              f"{', '.join(a[len('ref:'):] for a in unverified)}")
    return failures


def _register_line(marker):
    """Whatever section 00's register following `marker` says, or None."""
    for line in _read(NOTATION).splitlines():
        i = line.find(marker)
        if i != -1:
            return line[i + len(marker):]
    return None


def registered_sections():
    """The `sec:` anchors section 00's cross-reference convention lists."""
    text = _register_line(_SEC_REGISTER)
    return None if text is None else _SEC_TOKEN.findall(text)


def registered_anchors():
    """The `eq:` register, as [(section number, [anchors as listed]), ...].

    Order is preserved twice over -- the groups as the register runs, and the
    anchors within each -- because the register claims to be in reading order
    and a check that ignored order would certify half of what it claims.
    """
    text = _register_line(_EQ_REGISTER)
    if text is None:
        return None
    out = []
    for group in text.split(";"):
        number = _EQ_GROUP.search(group)
        out.append((number.group(1) if number else None,
                    _EQ_TOKEN.findall(group)))
    return out


def registers():
    """Check section 00's anchor registers against the sections.  Failures.

    The two registers make different promises, so they get different checks.
    The formula register claims every `{#eq:}` "in reading order within each
    section", so it is held to exact agreement -- grouping and order included.
    The section register is checked one way only: Part III and IV's anchors are
    registered before their files exist, which is a promise rather than a
    fault, while a declared anchor missing from the register is the drift this
    function exists to catch.
    """
    failures = []

    declared_secs = section_heads()
    registered_secs = registered_sections()
    if registered_secs is None:
        failures.append(f"{NOTATION} declares no section register")
    else:
        for anchor in sorted(declared_secs):
            if anchor not in registered_secs:
                failures.append(f"{anchor} ({declared_secs[anchor]}) is missing "
                                f"from {NOTATION}'s cross-reference register")

    declared = declared_anchors()
    by_file = {}
    for anchor, name in declared.items():
        by_file.setdefault(name, []).append(anchor)

    groups = registered_anchors()
    if groups is None:
        return failures + [f"{NOTATION} declares no formula register"]

    by_number = {f[:2]: f for f in section_files()}
    listed = {}
    for number, anchors in groups:
        if number is None:
            if anchors:
                failures.append(f"{NOTATION}'s formula register has a group "
                                f"naming no section: {', '.join(anchors)}")
            continue
        if number not in by_number:
            failures.append(f"{NOTATION}'s formula register names section "
                            f"{number}, which has no file")
            continue
        listed[by_number[number]] = anchors

    for name in sorted(set(listed) | set(by_file)):
        want, got = by_file.get(name, []), listed.get(name, [])
        if want == got:
            continue
        missing = [a for a in want if a not in got]
        stale = [a for a in got if a not in want]
        if missing:
            failures.append(f"{name} declares {', '.join(missing)}, which "
                            f"{NOTATION}'s formula register omits")
        if stale:
            failures.append(f"{NOTATION}'s formula register lists "
                            f"{', '.join(stale)} under {name}, which does not "
                            f"declare them")
        if not missing and not stale:
            failures.append(f"{name}: register order {', '.join(got)} against "
                            f"reading order {', '.join(want)}")

    print(f"  {len(declared)} formula and {len(declared_secs)} section anchors "
          f"against {NOTATION}'s registers; {len(failures)} gap(s)")
    return failures


def appendix(mods=None):
    """The reproduction appendix, as markdown.

    Every figure is what the printed command prints: the case is run, and the
    result is formatted through `_harness._fmt_one`, the CLI's own formatter.
    Rendering `case.expect` instead was wrong in 50 of 375 figures, two ways --
    an author-rounded target shown at a finer field spec than the rounding
    (`EI_eq` read 21.80 where the command prints 21.82), and a list field whose
    assertion pins only some elements shown as those alone where the command
    prints all of them.  The `--check` tolerance is what makes running the case
    safe here: it guarantees the printed value is within a hair of the target
    the article quotes.

    Use the CLI's formatter and nothing else.  A private `_show` here once
    claimed in its docstring to format "as the module's own CLI would print it"
    and did not -- it rendered booleans as yes/no where the CLI prints 1/0, and
    joined lists on one space where the CLI uses two.  Reading the assertion hid
    that, because assertions store 1 rather than True; computing exposed it.
    """
    mods = H.discover() if mods is None else mods
    # The same solve --check does, and the reason this generator is not instant.
    ctx = H.solve_all(H.collect_needs(mods))
    anchors = declared_anchors()
    # A module's home is the file defining the first formula it backs.  Modules
    # that back no *displayed* formula -- a section's prose figures, like the
    # risk statistics of section 09 -- have no anchor to look up, so they fall
    # back to the section they declare serving.
    heads = section_heads()
    by_section = {}
    for m in mods:
        where = (anchors.get(m.EQ[0], "?") if m.EQ
                 else heads.get(getattr(m, "SECTION", None), "?"))
        by_section.setdefault(where, []).append(m)

    out = ["# Reproducing every figure in this article", "",
           "Every number quoted in the text is produced by a script in "
           "`code/examples/`, listed here with the arguments that produce the "
           "article's own value and with what those arguments print. Each "
           "script takes the model's full parameter set, so any row can be "
           "re-run at other values: pass `--help` to see them. Figures the "
           "prose rounds may carry a digit more here, since these are the "
           "command's output rather than the article's wording. This table is "
           "generated by `python -m examples --appendix`, not maintained by "
           "hand.", ""]

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
                got = m.compute(**H.params_from(m, case.flags), ctx=ctx)
                figs = ", ".join(f"{k} = {H._fmt_one(got[k], spec.get(k, ''))}"
                                 for k in case.expect)
                out.append(f"| {eqs} | `{cmd}` | {figs} |")
                eqs = ""            # only label the first row of a module
        out.append("")
    return "\n".join(out)
