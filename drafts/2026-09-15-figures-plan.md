# Figures instead of tables — plan

**Status: agreed 2026-09-15.** Tables that sample a continuous function become graphs;
graphs are made with **matplotlib**; the project's stdlib-only rule is lifted to allow
it. The four questions at the end are settled as leaned.

## Why

Most of the article's tables are a continuous function read off at a handful of points,
and what the reader needs from them is the *shape*: §08's census was printed as eight
uneven bins and read as multimodal when the density falls monotonically (fixed in
`7758fac`). A graph shows a spike-then-exponential census, a heavy-tailed survival
curve or a ninety-year approach at a glance; a table makes the reader rebuild it.

Tables stay where the reader follows the arithmetic row by row — ledgers, account
types, cash policies, regime comparisons.

## Principles

1. **One source of numbers.** A figure plots what an example script's `compute()`
   already returns, so the checks that pin the table's figures also pin the plotted
   data. No plotting code computes a model quantity; `model.py` stays the only home of
   formulas.
2. **Generated, never hand-edited**, like the reproduction appendix: one command
   regenerates every figure, and a model change that moves a number regenerates the
   figures in the same commit.
3. **Deterministic output**, so a regenerated figure diffs clean when nothing moved:
   no timestamp in the SVG metadata (`metadata={"Date": None}`), a fixed
   `svg.hashsalt`, text kept as text (`svg.fonttype: "none"`).
4. **Readable raw.** The Markdown keeps a caption and anchor on its own line, so the
   drafts still read without a renderer; VS Code and GitHub show the SVG inline.
5. **A conversion is a prose edit, not a swap.** Replacing a table means re-reading
   everything that leans on it — sentences that read values off it, "the table above",
   row references ("the top two rows"), footnotes, and other sections that cite its
   figures — and rewriting them to read against the figure. The table's exact values
   survive in the appendix, not in the prose. (Sergei, 2026-09-15.)

## Design

- **Where the code lives.** A new `code/figures.py` holds the shared style (size for a
  single LaTeX column, fonts, palette, Unicode axis labels in the article's notation)
  and small helpers. Each example module that owns a figure declares it beside its
  `FIELDS` — a `FIGURES` list naming the fields plotted and how — and the harness
  renders it. Mirrors how `FIELDS` drives the printed table and the appendix.
- **Commands.** `python code/examples/<script>.py --figure` writes that script's
  figures; `python -m examples --figures` writes all of them; `python -m examples
  --figures-check` regenerates into a temporary directory and fails if any committed
  SVG differs. The last runs inside `verify_examples.py`.
- **Output.** `figures/<name>.svg`, committed.
- **In the sections.** `![Caption.](../figures/census.svg){#fig:census}` on its own
  line; prose references `[fig:census](#fig:census)`, which becomes `\ref` at assembly
  like `eq:` and `sec:`. `00-notation.md` Conventions gains a `fig:` register, and
  `--registers` checks it.
- **Assembly (later).** pdflatex cannot include SVG. Inkscape (installed, not on PATH)
  pre-converts each SVG to PDF, or to PDF plus LaTeX-typeset labels with
  `--export-latex` so labels match the body font. MiKTeX 2.9 is due a look at that
  point anyway. Nothing here needs deciding now.
- **Docs made stale by this, fixed in the same change.** `CLAUDE.md`'s "Performance,
  and the stdlib rule" paragraph; the "Stdlib only" lines in module docstrings that
  would stop being true (see Q1 — under the lean, only the harness's does).

## Candidates

Converted in the section-by-section review as it reaches each one, starting with §08.

| section | table now | as a figure |
|---|---|---|
| §08 | inventory at 5/10/30 y and equilibrium, two rows | E[I(t)] and its [0, t] average over 0–100 y, the equilibrium and its 90% line marked |
| §08 | depth census, eleven bins | census density, thirty-year and stationary overlaid |
| §07 | survival and mean depth of survivors at nine ages | survival curve on a log-age axis, mean depth beside it |
| §06 | q(x) and c_c(x) at six depths | one figure, two panels: exit probability and call premium against depth |
| §05 | early-exercise threshold at five days-to-expiry | threshold against days to expiry |
| §09 | σ_IV sweep | excess return and gap against σ_IV |
| §09 | book exposure at five price shocks | exposure against shock |
| §10 | crash-then-flatline path | lots, market and cost-basis capital against time |
| §10 | share of the strategy run against σ | throughput and A\* against σ, boundaries marked |
| §11 | P(sold out) at six horizons | liquidation probability against horizon |
| §11 | throughput and T_sat against equity | both against A, A\* marked |
| §11 | draw and RoE against leverage | the two curves diverging, survivable leverage marked |

**Kept as tables:** §09's income and gap ledgers, the two-ledger table, the cadence and
dividend sweeps (several unlike quantities per column), sticky dividend, the regime
tables; §10's boundary and two-worlds tables; §11's account types, cash policies,
frozen-vs-operating, census comparison and two-worlds tables.

## Decisions

- **Q1. Hard or optional dependency?** **Optional**. matplotlib is imported only
  when figures are requested, so every example still runs, checks and prints without
  it, and a reader who only wants the numbers installs nothing. `verify_examples.py`
  runs the figure check when matplotlib is importable and says so plainly when it is
  not — the pattern numpy already follows.
- **Q2. Figure replaces table, or both?** **Replaces**, with the one or two
  figures the prose argues from kept in the text, and the exact values left to the
  appendix, which prints them anyway.
- **Q3. Commit the SVGs?** **Yes** — so the Markdown renders on GitHub and in
  review, and so the determinism check has something to compare against.
- **Q4. Install matplotlib?** **Yes**, per the machine's convention: `uv pip install
  --system matplotlib` into the one global Python 3.12.
