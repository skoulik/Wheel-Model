"""Signed claims: prose that rests on another part of the article.  Stdlib only.

Quoted numbers have cases and generated files are regenerated and compared,
but a sentence that restates or leans on something said elsewhere had no check
at all.  Section 02 told readers the wheel "clears in four years" for weeks
after the cadence change made it two, carried by nothing but prose.

A **claim** is a paragraph whose statement rests on another part of the
article.  Signing it records a fingerprint of both sides in
`sections/claims.tsv`; when either side is reworded the check fails and names
the claim, and it is reread against its source and signed again.  A signature
says someone read both sides, so it is never renewed in a loop.

The **target** is what the claim rests on, and it has to be precise or the
check is noise: a whole section's every edit would flag every claim on any of
it.  So it is one of

*   a displayed formula `{#eq:}` or a figure `{#fig:}` -- the paragraph
    holding the display or the image line;
*   a heading below the title carrying an anchor -- its subsection, to the
    next heading of the same or a higher level;
*   a **paragraph anchor** `<a id="para:name"></a>` -- one paragraph, or one
    list item.

A section's own title anchor is refused as too coarse.  A paragraph anchor sits
on its own line directly above its paragraph, or just after a list item's
marker; GitHub renders it as an invisible anchor, and at assembly a pandoc
filter makes it a PDF target (`drafts/2026-10-22-drift-checks-plan.md`).  Prose
may link one like any anchor, and such a link must resolve.

The **citing side** is named either as a file -- the paragraphs in it that link
the target -- or by a paragraph anchor, for a paragraph that restates a result
without linking it.  Which links are claims lives here and not in the prose:
most links are pointers, and pointers are not signed.

A fingerprint covers the words only: blind to wrapping, emphasis, anchors, and
where a link points, so retargeting a link is not a rewording.

**Promises.** A claim on a section section 00 registers but nobody has written
yet cannot be fingerprinted, and it is exactly the claim most likely to be
wrong once the section exists.  Signing one records it as *pending*.  Every
prose link into an unwritten section must be registered so -- an unregistered
one fails, so none slips in -- and the day the section declares its anchor
every pending row on it fails, to be read against what the section says and
signed against a precise target in it.  Any other link must land on a declared
anchor.
"""

import datetime
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples import _report as R                             # noqa: E402

CLAIMS = os.path.join(R.SECTIONS, "claims.tsv")
_HEADER = ("# Written by python -m examples --sign and --unsign; "
           "do not edit by hand.\n"
           "# citing\ttarget\tciting fingerprint\ttarget fingerprint\tsigned\n")

_PANDOC = re.compile(r"\{#([a-z]+:[a-z0-9-]+)\}")
_HTML_ID = re.compile(r'<a id="([^"]*)"></a>')
_PARA = re.compile(r"para:[a-z0-9-]+")
_LINK = re.compile(r"\]\(#([a-z]+:[^)\s]*)\)")
PENDING = "pending"
_HEADING = re.compile(r"^(#{1,6})\s")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")
_QUOTE = re.compile(r"^\s*>\s?")
# Where a paragraph anchor may stand: alone on its line, inside a blockquote
# or not, or straight after a list item's marker.
_ALONE = re.compile(r'^(?:\s*>\s?)?\s*<a id="[^"]*"></a>\s*$')
_IN_ITEM = re.compile(r'^\s*(?:[-*+]|\d+\.)\s+<a id="[^"]*"></a>')


def _blocks(lines):
    """Split a file into blocks: paragraphs, list items, headings, displays.

    Blank lines separate, inside a blockquote too; a heading is a block of its
    own; a list item starts a new one; and so does stepping into or out of a
    blockquote.  Returns [(first, last)] line indices, inclusive.
    """
    out, start, quoted = [], None, None

    def close(last):
        nonlocal start
        if start is not None:
            out.append((start, last))
        start = None

    for i, line in enumerate(lines):
        q = bool(_QUOTE.match(line))
        bare = _QUOTE.sub("", line, count=1) if q else line
        if not bare.strip():
            close(i - 1)
            continue
        if _HEADING.match(bare):
            close(i - 1)
            out.append((i, i))
            continue
        if start is not None and (q != quoted or _LIST_ITEM.match(bare)):
            close(i - 1)
        if start is None:
            start, quoted = i, q
    close(len(lines) - 1)
    return out


def _block_of(blocks, i):
    return next(b for b in blocks if b[0] <= i <= b[1])


def _lines(name):
    return R._read(name).splitlines()


def declared():
    """Every anchor a claim could rest on: anchor -> (file, first, last, level).

    `level` is the heading level for a heading's anchor and 0 otherwise.  Also
    returns the problems found on the way: paragraph anchors misplaced,
    misnamed or declared twice.
    """
    out, problems = {}, []
    for name in R.section_files():
        lines = _lines(name)
        blocks = _blocks(lines)
        for i, line in enumerate(lines):
            plain = R._CODE.sub("", line)
            head = _HEADING.match(plain)
            for anchor in _PANDOC.findall(plain):
                if head:
                    level, end = len(head.group(1)), i + 1
                    while end < len(lines):
                        nxt = _HEADING.match(lines[end])
                        if nxt and len(nxt.group(1)) <= level:
                            break
                        end += 1
                    out.setdefault(anchor, (name, i, end - 1, level))
                else:
                    out.setdefault(anchor, (name, *_block_of(blocks, i), 0))
            for anchor in _HTML_ID.findall(plain):
                where = f"{name}:{i + 1}"
                if not _PARA.fullmatch(anchor):
                    problems.append(f"{where}: <a id=\"{anchor}\"> -- a paragraph "
                                    f"anchor is named para:lowercase-words")
                    continue
                first, last = _block_of(blocks, i)
                if _ALONE.match(line):
                    if first != i or last == i:
                        problems.append(f"{where}: {anchor} must sit directly "
                                        f"above its paragraph, with no blank line "
                                        f"between and nothing above it in the block")
                        continue
                elif not _IN_ITEM.match(line):
                    problems.append(f"{where}: {anchor} must stand alone above a "
                                    f"paragraph or just after a list marker")
                    continue
                if anchor in out:
                    problems.append(f"{where}: {anchor} is already declared in "
                                    f"{out[anchor][0]}")
                    continue
                out[anchor] = (name, first, last, 0)
    return out, problems


def unwritten():
    """Sections section 00 registers whose file does not exist yet."""
    written = set(R.section_heads()) | set(_PANDOC.findall(R._read(R.APPENDIX)))
    return [s for s in (R.registered_sections() or []) if s not in written]


def _links(name):
    """The anchors a section file links, code spans aside."""
    return _LINK.findall(R._read(name, strip_code=True))


def _promise_ok(citing, target, anchors):
    """Raise ValueError unless the citing side of a promise still stands."""
    if citing.startswith("para:"):
        if citing not in anchors:
            raise ValueError(f"{citing} is declared nowhere")
    elif citing not in R.section_files():
        raise ValueError(f"{citing} is not a section file")
    elif target not in _links(citing):
        raise ValueError(f"{citing} no longer links #{target}")


def wording(text):
    """What a fingerprint covers: the words, as a reader would read them."""
    text = _HTML_ID.sub("", text)
    text = _PANDOC.sub("", text)
    text = re.sub(r"\]\([^)]*\)", "]()", text)
    text = "\n".join(_QUOTE.sub("", ln) for ln in text.splitlines())
    return " ".join(text.replace("*", "").split())


def fingerprint(text):
    return hashlib.sha256(wording(text).encode("utf-8")).hexdigest()[:12]


def _extent_text(extent):
    name, first, last, _ = extent
    return "\n".join(_lines(name)[first:last + 1])


def _citing_text(citing, target, anchors):
    """The citing side's text, or raise ValueError saying why there is none."""
    if citing.startswith("para:"):
        if citing not in anchors:
            raise ValueError(f"{citing} is declared nowhere")
        return _extent_text(anchors[citing])
    if citing not in R.section_files():
        raise ValueError(f"{citing} is not a section file")
    lines = _lines(citing)
    link = f"](#{target})"
    found = [b for b in _blocks(lines)
             if link in R._CODE.sub("", "\n".join(lines[b[0]:b[1] + 1]))]
    if not found:
        raise ValueError(f"no paragraph in {citing} links #{target}")
    return "\n\n".join("\n".join(lines[a:b + 1]) for a, b in found)


def _target_text(target, anchors):
    if target not in anchors:
        raise ValueError(f"{target} is declared nowhere")
    if anchors[target][3] == 1:
        raise ValueError(f"{target} is a whole section, too coarse to rest a "
                         f"claim on; anchor the paragraph or subsection meant")
    return _extent_text(anchors[target])


def read_claims():
    """The signed claims: [(citing, target, citing fp, target fp, signed)]."""
    if not os.path.exists(CLAIMS):
        return []
    with open(CLAIMS, encoding="utf-8") as fh:
        return [tuple(ln.rstrip("\n").split("\t")) for ln in fh
                if ln.strip() and not ln.startswith("#")]


def _write_claims(rows):
    body = _HEADER + "".join("\t".join(r) + "\n" for r in sorted(rows))
    tmp = CLAIMS + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(body.encode("utf-8"))
    os.replace(tmp, CLAIMS)


def sign(citing, target):
    """Sign one claim, replacing any earlier signature of the same pair.

    A target section 00 registers but nobody has written yet is recorded as a
    promise, pending until the section exists.
    """
    citing = os.path.basename(citing)
    anchors, problems = declared()
    if problems:
        raise SystemExit("fix the paragraph anchors first:\n  " + "\n  ".join(problems))
    today = datetime.date.today().isoformat()
    try:
        if target in unwritten():
            _promise_ok(citing, target, anchors)
            row = (citing, target, PENDING, PENDING, today)
        else:
            row = (citing, target,
                   fingerprint(_citing_text(citing, target, anchors)),
                   fingerprint(_target_text(target, anchors)), today)
    except ValueError as e:
        raise SystemExit(f"not signed: {e}")
    rows = [r for r in read_claims() if r[:2] != (citing, target)]
    _write_claims(rows + [row])
    if row[2] == PENDING:
        print(f"  registered: {citing} promises {target}, pending until it is written")
    else:
        print(f"  signed: {citing} rests on {target}")


def unsign(citing, target):
    """Drop one claim's signature, or one promise."""
    citing = os.path.basename(citing)
    rows = read_claims()
    kept = [r for r in rows if r[:2] != (citing, target)]
    if len(kept) == len(rows):
        raise SystemExit(f"no signed claim of {citing} on {target}")
    _write_claims(kept)
    print(f"  unsigned: {citing} on {target}")


def check():
    """Every signed claim and promise against the text as it stands.  Failures."""
    anchors, failures = declared()
    rows = read_claims()
    waiting = unwritten()
    appendix = set(_PANDOC.findall(R._read(R.APPENDIX)))
    seen, stale, pending = set(), 0, {}
    for row in rows:
        if len(row) != 5:
            failures.append(f"claims.tsv: malformed row {row}")
            continue
        citing, target, citing_fp, target_fp, signed = row
        if (citing, target) in seen:
            failures.append(f"claims.tsv signs {citing} on {target} twice")
        seen.add((citing, target))
        resign = f"python -m examples --sign {citing} {target}"
        if citing_fp == PENDING:
            if target in anchors:
                failures.append(f"{target} has been written, so the promise {citing} "
                                f"made on it is due: read the claim against what "
                                f"the section says, sign it against a precise "
                                f"target there, then --unsign {citing} {target}")
            elif target not in waiting:
                failures.append(f"promise of {citing} on {target}: section 00 no "
                                f"longer registers it; --unsign {citing} {target}")
            else:
                try:
                    _promise_ok(citing, target, anchors)
                    pending[target] = pending.get(target, 0) + 1
                except ValueError as e:
                    failures.append(f"promise of {citing} on {target}: {e}; "
                                    f"--unsign {citing} {target}")
            continue
        try:
            now_citing = fingerprint(_citing_text(citing, target, anchors))
            now_target = fingerprint(_target_text(target, anchors))
        except ValueError as e:
            failures.append(f"claim of {citing} on {target}: {e}; restore it, "
                            f"or drop it with --unsign {citing} {target}")
            continue
        moved = [side for side, was, now in (("the claim", citing_fp, now_citing),
                                              (target, target_fp, now_target))
                 if was != now]
        if moved:
            stale += 1
            failures.append(f"claim of {citing} on {target}: "
                            f"{' and '.join(moved)} "
                            f"{'have' if len(moved) > 1 else 'has'} been reworded "
                            f"since it was signed on {signed}; reread the two "
                            f"together, then {resign}")
    # Every link lands: on a declared anchor, on the generated appendix, or on
    # an unwritten section the linking file has registered a promise to.
    promised = {r[:2] for r in rows if len(r) == 5 and r[2] == PENDING}
    for name in R.section_files():
        for anchor in sorted(set(_links(name))):
            if anchor in anchors or anchor in appendix:
                continue
            if anchor not in waiting:
                failures.append(f"{name} links #{anchor}, which is declared nowhere")
            elif (name, anchor) not in promised:
                failures.append(f"{name} links #{anchor}, which is not written yet; "
                                f"register the promise: "
                                f"python -m examples --sign {name} {anchor}")
    paras = sum(1 for a in anchors if a.startswith("para:"))
    npend = sum(pending.values())
    print(f"  {len(rows) - npend} signed claims, {paras} paragraph anchors; "
          f"{npend} promises pending on unwritten sections"
          + (f" ({', '.join(f'{k} {v}' for k, v in sorted(pending.items()))})"
             if pending else "")
          + f"; {stale} reworded since signing; {len(failures) - stale} other gap(s)")
    return failures
