# First-reader report — Parts I–II

- **Date:** 2026-08-05
- **Reader:** first outside reader (adversarial pass), Claude
- **Read, end to end:** `00-notation`, `02-introduction`, `04-strategy`, `05-entry`,
  `06-depth-process`, `07-holding-time`, `08-inventory`, `09-returns`, `10-stability`,
  `11-constrained`; supporting `98-bibliography`, `99-reproduction`; stubs `01`, `03`, `15`
  noted below.
- **Ran:** `python code/verify_examples.py` (all checks passed); `python -m examples
  --appendix`, `--references`; individual `code/examples/*.py` scripts for entry, holding,
  returns, and constrained; `model.expected_drop` directly; measure-Q ledger/benchmark.
- **Baseline:** green. `verify_examples.py` reports "All checks passed"; 48/48 formulas
  backed, citation apparatus clean (16 uncited entries, all in unwritten §03 territory).

## Stubs (noted, not graded)
`01-abstract.md`, `03-prior-work.md`, `15-outlook.md` are deliberate placeholders. `15`
is unusually complete for a stub and already reads well as a "what's out of scope" list.

## Summary

This is a strong, unusually disciplined draft. The economics are internally consistent,
the numbers reproduce, the accounting-track discipline is real and visible, and the
prose is honest about its own weak points (the live-account section repeatedly undercuts
the strategy rather than selling it). I tried hard to break the central chain — entry law
→ survival → E[W] → Little → census → ledger → stability — and could not. The measure-Q
"free test" holds at 8 bp exactly as advertised.

Nothing rises to a blocker, and I found no substantive economic error. What I did find is
mostly integrity-of-apparatus and pedagogy: one checked-in reproduction figure that does
not match the command printed beside it, an authoritative symbol register that has
silently drifted out of sync, and two named mathematical constructs used without the
house-style detour.

**Fix first, by ID:**
1. **F-99-1** — the reproduction appendix prints *asserted* values, not command output, so
   `entry_depth.py`'s row says `drop = 3.80%` while the command prints `3.75%`. Touches the
   project's core reproducibility claim.
2. **F-00-1** — `00-notation.md`'s formula-anchor register is missing four anchors that
   exist, are backed, and are reproduced (`eq:screen-gap`, `eq:little-finite`,
   `eq:mark-loss`, `eq:giveaway`).
3. **F-07-1** — Wald's identity is invoked by name and does load-bearing work (the 0.667
   overshoot and the 1.93/2.22 bounds) with no detour.
4. **F-11-1** — the reflection principle is named without a detour or pointer.

## Findings

### §00 — Notation

**F-00-1 — The formula-anchor register omits four live anchors**
- **Severity:** minor
- **Kind:** consistency
- **Where:** `00-notation.md`, Conventions, the "Current anchors, in reading order within
  each section:" list (the `eq:...` register).
- **What:** The register lists, for §05 `eq:kstar, eq:p-screen, eq:x0-def, eq:x0-law,
  eq:d-mean`; for §08 `eq:lambda, eq:little, eq:census`; for §09 `eq:income, eq:capital,
  eq:econ-pnl, eq:excess, eq:levered-excess`. But the sections actually declare, in
  addition: `eq:screen-gap` (§05), `eq:little-finite` (§08), and `eq:mark-loss` +
  `eq:giveaway` (§09). All four are backed by example modules and appear in
  `99-reproduction.md`. I enumerated every `{#eq:...}` per section and diffed against the
  register to confirm these four and only these four are missing.
- **Why it matters:** `00-notation.md` declares itself the single source of truth and "When
  a section introduces a new symbol, it must be added here." `_report.coverage()` checks
  anchors-vs-modules but does **not** check this hand-maintained list, so the drift is
  silent — exactly the failure mode the project guards against for citations.
- **Suggested fix:** Add the four anchors to the register in reading order. Optionally,
  extend `coverage()` to assert the register matches `declared_anchors()` so it cannot
  drift again.

### §02 — Introduction

**F-02-1 — "5.5 … and 5.8 times" mixes an absolute with a ratio**
- **Severity:** nit
- **Kind:** clarity
- **Where:** §02 Contributions, item 6: "needs about **nineteen share prices** … against
  the 5.5 a portfolio-margin ceiling implies, and 5.8 times what the most aggressive margin
  available implies."
- **What:** "5.5" is an absolute (share prices the PM ceiling implies, cf. §11's 5.46),
  but "5.8 times" is a ratio (19.23 / 3.27 at aggressive margin). Presented in parallel
  they read as like-for-like and are not. Also "nineteen" is the PM A\* (19.23) while the
  5.8× uses the aggressive A\* (18.88); harmless since 18.88 ≈ 19, but it compounds the
  slight muddle.
- **Why it matters:** A numerate reader parsing the sentence for a factor gets two
  incompatible quantities.
- **Suggested fix:** Make both the same kind, e.g. "against the 5.5 a portfolio-margin
  ceiling implies (a factor of 3.5), and 3.3 at the most aggressive margin (a factor of
  5.8)."

### §04 — The Strategy and Its Accounting

**F-04-1 — "premium scales with √tenor, assignments with the cadence" is asserted**
- **Severity:** minor
- **Kind:** unjustified assumption
- **Where:** §04 Three clocks: "premium scales roughly with the square root of the tenor
  while assignments scale with the cadence."
- **What:** A true statement (ATM premium ≈ 0.4·σ·√τ) but dropped without derivation or
  pointer, in a section whose whole job is to justify separating the three clocks. The
  project rule is that every modeling assumption is justified in plain terms for a general
  audience.
- **Why it matters:** This scaling is the economic reason the cadence/tenor split matters;
  a reader is asked to take the load-bearing half on faith.
- **Suggested fix:** One clause tying it to the option-price √τ dependence, or a pointer to
  the depth section's `σ·√τ_c` scale which already makes the same point.

### §05 — Entry

**F-05-1 — "the two differ by a factor of four here" overstates a factor of 3.57**
- **Severity:** minor
- **Kind:** dangling number / imprecision
- **Where:** §05: "the two differ by a factor of four here" (Δd₂ = 0.0139 vs Δp = 0.0039).
- **What:** 0.0139 / 0.0039 = 3.56, and the sentence itself then gives the mechanism as
  1/φ(N⁻¹(p\*)) = 1/0.28 = 3.57. "A factor of four" rounds 3.57 up past its nearest
  integer.
- **Why it matters:** Small, but the same paragraph quotes 0.28 to two figures, so "four"
  reads as careless next to it.
- **Suggested fix:** "a factor of about three and a half," or state it as "≈ 1/0.28."

**F-05-2 — Live-account entry figures are stated as fact ahead of their support**
- **Severity:** nit
- **Kind:** clarity (forward reference)
- **Where:** §05 "Where a real operator sits on the dial": 7.4%, corrected to 10.8%; median
  put 5.5% OTM; "a fifth of held time above strike" (that last is in §07).
- **What:** These are empirical claims about the live account whose derivation lives in the
  unwritten §sec:live. Not a broken forward link (tracked), and the section is careful to
  say the measurement is made properly later — flagging only so the author is aware a reader
  cannot check any of these until Part IV, and several headline sentences lean on them.
- **Suggested fix:** None needed now; ensure §sec:live actually reproduces each of these
  numbers when written.

### §06 — The Depth Process

**F-06-1 — "the model has essentially one parameter" is immediately contradicted**
- **Severity:** nit
- **Kind:** clarity / overstatement
- **Where:** §06 "What the parameters do": "the model has essentially one parameter. Two
  configurations with the same ν, σ and τ_c behave identically …"
- **What:** The very next clause names three parameters. The real (correct) claim is that
  μ and δ enter only through ν, collapsing two inputs into one — not that the model has one
  parameter.
- **Why it matters:** A careful reader trips on the contradiction between the bolded claim
  and its own justification.
- **Suggested fix:** "μ and δ enter the model only through ν — so two configurations with
  the same ν, σ and τ_c behave identically."

### §07 — How Long a Lot Stays

**F-07-1 — Wald's identity is used load-bearing without a detour**
- **Severity:** minor
- **Kind:** needs detour
- **Where:** §07 "Exits happen on a grid": "How much larger is settled by **Wald's
  identity**, which is exact rather than approximate: a lot's mean life is the hole it has
  to climb divided by the rate the drift fills it, E[W] = (E[x₀] + E[overshoot]) / ν."
- **What:** Wald's identity is named and used to back out the 0.667-step overshoot and, at
  the end of the section, the 1.93/2.22 bounds — genuinely load-bearing. Every other
  probability construct in the article (Bernoulli, normal, random walk, first passage,
  Little, length bias, H=λG) gets a blockquote detour with a further-reading pointer; this
  one gets a one-line gloss.
- **Why it matters:** House-style consistency, and a general reader meets "Wald's identity"
  cold at the moment it is asked to carry the section's headline correction.
- **Suggested fix:** A short detour: a random sum's expectation is the expected count times
  the expected step, with a pointer (Ross, *Introduction to Probability Models*, already
  cited in this section).

### §08 — The Inventory

*(No independent findings. Cross-checked E[I] = λ·E[W] = 21.8, the window-law residence
row 0.52/0.71/1.10, and the census shares — all consistent. Two of its anchors are the
register omissions in F-00-1.)*

### §09 — Returns and Capital

**F-09-1 — "50 to 70 basis points … the two middle rows" doesn't map cleanly to the table**
- **Severity:** minor
- **Kind:** dangling number / clarity
- **Where:** §09 "So where could an edge come from?": "against the single-name premium of
  roughly a point … the whole of it is edge — some 50 to 70 basis points a year, the two
  middle rows of the table."
- **What:** The vs-buy-and-hold column reads +0.01 / +0.23 / +0.46 / +0.69 / +0.92 for
  σ_IV 20.0 / 20.5 / 21.0 / 21.5 / 22.0. "50 to 70 bp" is the 21.0% and 21.5% rows
  (+0.46, +0.69). But "the two middle rows" of a five-row table most naturally reads as
  20.5 and 21.0 (+0.23, +0.46), which is 23–46 bp, not 50–70. The premium the sentence
  invokes ("roughly a point," i.e. 1.07–1.5) does land at 50–70 bp — the wording just
  points at the wrong rows.
- **Why it matters:** A reader who follows the pointer to "the two middle rows" reads the
  wrong pair and sees a range that contradicts the sentence.
- **Suggested fix:** Name the rows ("the 21.0% and 21.5% rows") or the input ("one to one
  and a half points over fair").

**F-09-2 — Capital/P&L display formulas are not tagged with a track letter**
- **Severity:** nit
- **Kind:** track label
- **Where:** `eq:capital` (Track B), `eq:mark-loss`, `eq:giveaway`, `eq:econ-pnl`,
  `eq:excess` in §09.
- **What:** The project rule is "label every P&L/capital formula with its track." These
  displays carry no explicit A/B/C tag at the formula; the track is identified in
  surrounding prose (Track B for market-value capital, the economic ledger as the composite
  that satisfies no-arbitrage). Defensible, but `eq:capital` in particular is a pure Track-B
  capital formula and could carry the label the way the rule intends.
- **Why it matters:** Low; the discipline is honored in spirit. Flagged so the author can
  decide whether the letter belongs on the display line.
- **Suggested fix:** Author's call — either tag `eq:capital` "(Track B)" or leave, since the
  economic ledger is explicitly a composite rather than a single track.

### §10 — Stability

*(No independent findings. Verified both boundaries' σ/δ crossings, the between-boundaries
regime, θ = 2ν/σ² = 1.25 real / 0.25 under Q, and the equilibrium-lots ≈ 94 under Q. The
adjustment-coefficient / Cramér–Lundberg aside is enrichment, not load-bearing, and is
adequately glossed.)*

### §11 — The Finite Account

**F-11-1 — The reflection principle is named without a detour or pointer**
- **Severity:** nit
- **Kind:** needs detour
- **Where:** §11 "The barrier": "Over a horizon H the reflection principle gives
  P(sold out by H) = …" producing `eq:first-passage`.
- **What:** The reflection principle is invoked by name to produce the first-passage
  probability a general reader is then asked to trust. No detour, no pointer. Less
  load-bearing than F-07-1 (the exact form matters less than that survival is a
  first-passage problem, which the margin detour already frames), but same house-style gap.
- **Suggested fix:** A one-line pointer (Ross again) or fold it into the margin-call detour
  that already sets up first passage.

**F-11-2 — "the book is empty about 14% of the time" is a dangling simulation figure**
- **Severity:** minor
- **Kind:** dangling number
- **Where:** §11 Glynn–Whitt paragraph: "A wheel does — on one name the book is empty about
  14% of the time — so the inversion is legitimate here."
- **What:** This 14% licenses the backward-Little inversion (system empties infinitely
  often), so it is doing real work, but it carries no reproduction footnote and is not in
  `99-reproduction.md`. Same for the related "a fifth of held time above strike" (§07) and
  the empty-fraction claims elsewhere, though those are explicitly live-account/sim.
- **Why it matters:** In an article whose whole selling point is that every number is
  reproducible, a load-bearing figure with no pointer stands out.
- **Suggested fix:** Point it at the simulator scenario that produces it, or footnote it as
  a live-account measurement deferred to §sec:live.

### §99 — Reproduction (generated file)

**F-99-1 — The appendix prints asserted values, not command output — and they can differ**
- **Severity:** major
- **Kind:** code-vs-text
- **Where:** `99-reproduction.md`, §05 row: "`python code/examples/entry_depth.py` |
  x0 = 0.0155, drop = **3.80%**". Generator: `code/examples/_report.py` `appendix()`,
  line 295, which renders `case.expect[k][0]` — the asserted target — for each figure.
- **What:** Running the exact printed command prints **`drop = 3.75%`**, not 3.80%. I
  confirmed `model.expected_drop(Config(), "P")` = 0.037537 via every invocation path
  (standalone, `params_from`, with `ctx`), so 3.75% is the genuine computed value. The
  appendix shows 3.80% because the `Case` asserts `drop: (0.038, 0.001)` and the generator
  formats the assertion (0.038 → "3.80%" at the field's `.2%` spec), not the output. The
  ±0.001 tolerance is why `verify_examples` stays green (0.03754 is inside [0.037, 0.039]).
  The prose "3.8%" is a *correct* one-decimal rounding of 3.754%; the defect is confined to
  the reproduction file rendering the target at two decimals as "3.80%", which the command
  contradicts.
- **Why it matters:** The file's own preamble says it lists "the arguments that produce the
  article's own value," and the docstring calls it "the value asserted" — but a reader who
  runs the printed command and compares digit-for-digit finds a mismatch, in the one
  artifact whose entire purpose is to earn trust in the numbers. It is systemic, not a
  one-off: any figure whose author-rounded assertion differs from the computed value within
  tolerance, at a field spec finer than the rounding, will show the same gap. `entry_depth`
  `drop` is the clearest instance I found.
- **Suggested fix:** Have `appendix()` render the *computed* value (call `m.compute(...)`
  and format the result) rather than `case.expect[0]`; the check tolerance then guarantees
  it is within a hair of the asserted target while matching what the command actually
  prints. Alternatively tighten the `drop` assertion to the computed value and let the
  prose keep "3.8%."

### §98 — Bibliography

*(Checked, no findings.) I spot-verified the citations §09 leans on hardest. The
single-name-vs-index Bakshi & Kapadia distinction is handled carefully: the JoD entry is
tagged as the single-name source (1.5 vs SPX 3.3, 1.07 ex-dividend) and the RFS entry
explicitly warns "cite for the index side and never for a single-name number," matching
§09's usage. Israelov & Nielsen's corrected BXM betas (0.46/0.85) match §09's detour.
Read levels are enforced; the two [cite unverified] Siegmund entries are not quoted for
figures, as the rule requires.*

## Things I checked that were fine

- **Baseline reproducibility.** `verify_examples.py` green, including the structural
  numpy/loop agreement and the constrained-vs-closed-form simulator checks.
- **The free no-arbitrage test.** Ran the ledger and benchmark under `--measure Q`: wheel
  economic excess −0.29% at 30y, buy-and-hold-adjusted −0.37%, **difference +0.08% = 8 bp**
  — the residual CLAUDE.md advertises. The strongest test passes.
- **The economic ledger cancellation.** appreciation +0.5128 − mark loss 0.1632 − upside
  0.3559 = −0.0063, ≈1% of the largest term; E[Π] = 0.7655; excess = (0.7655 −
  0.05·11.591)/11.591 = +1.60%. All recomputed and consistent.
- **Holding-time bounds bracket the exact.** far-barrier 1.93 and near-barrier 2.22 bracket
  the exact 2.10; Wald back-out gives overshoot 0.667 steps → tax 0.037 = 2.4× the 0.0155
  entry depth; the 30/70 entry/grid split holds.
- **Little's law chain.** λ = 10.4, E[W] = 2.10 → E[I] = 21.8; window residence
  0.52/0.71/1.10 = average inventory / λ; census shares sum to ~100%, deep-30 = 46%,
  stationary mean depth 79% / q 0.036 / deep-50 53%.
- **Entry law.** k\* = 0.9774 (2.26% OTM), p_screen 20.39%, delta 19.61%, Δd₂ 0.0139;
  Conservative 4.70% drop matches prose.
- **The collateral footnote.** overcharge 17/13/8 bp at 5/10/30y; corrected gap
  0.20/0.14/0.09; the cash-secured 4.5× multiple. All reproduce.
- **Regime invariance.** Standard and Conservative "collateral earning r" rows agree to
  0.3 bp at every horizon, as claimed — the visible 8 bp gap really is the Track-C
  overcharge.
- **Leverage.** break-even spread = excess return (both 1.60%); the L_max ladder
  1.0000/1.0861/1.1349/1.1557 and the ε-horizon table reproduce; θ "read twice" is
  genuinely the same 2ν/σ² in the census tail and the survival exponent.
- **Payoff-diagram detour** (§02): the two ASCII diagrams are correctly identical in shape,
  and the "equivalence is about payoffs, not prices" caveat is right.
