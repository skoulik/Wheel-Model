# TODO

Open work only. Everything finished, resolved or deliberately descoped lives in
[`DONE.md`](DONE.md), which also carries the map from the old flat numbering (#1–#25) to the
per-part numbering used here. Items are tagged `(was #n)` where a predecessor existed, so the
citations in `drafts/` stay traceable.

**Nothing resolved is kept in this file.** When an item closes its write-up goes to `DONE.md`, and
any figure a still-open item needs is folded into that item rather than left behind as a
hand-forward block. So every entry below is work someone still has to do. Numbers are never
recycled or closed up: the gaps — I-3, the whole of Part II, INF-1 — mean those items are in
`DONE.md`.

Sections reference items as "TODO I-1", "TODO IV-2" — at present **no section carries such a
flag** (checked 2026-07-30), and that is the intended steady state: an in-text flag is a promise
to a reader and should be added only when the text genuinely defers something.

## Where things stand

Thirteen of the seventeen planned section files exist, plus a generated reproduction appendix
(`sections/99-reproduction.md`, produced by `python -m examples --appendix`, never edited by
hand). Part I is written bar two stubs; **Part II is complete** as of 2026-07-31; **Part III and
Part IV are unwritten**, and between them they are now the whole of what is left besides those
stubs and the assembly work.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · 11 constrained | **complete** |
| III. Many assets | 12 portfolio · 13 correlation | **do not exist** |
| IV. Reality | 14 verification · 15 live-account · 16 outlook | **14 and 15 do not exist**; the outlook is a stub, on disk as `15-outlook.md` |

**This file uses the final numbering** — portfolio §12, correlation §13, verification §14, the
live account §15, the outlook §16 — as of 2026-07-30. It previously used the pre-§11 numbering
with a note saying so, which collided with the constrained section that actually occupies §11 on
disk: "write §11, the portfolio section" was an instruction to overwrite a finished section. The
*file* renames are still deferred to when Part III drafts — `15-outlook.md` becomes
`16-outlook.md` then — and nothing breaks in the meantime because anchors are name-based.

Six section files link to anchors in the missing files: `sec:verification` from 00, 07, 08 and 09;
`sec:live` from 00, 04 and 05; `sec:portfolio` from 08. Those cross-references are broken until
Parts III and IV land, and that is the assembly-time deadline. `sec:correlation` is so far
referenced from nowhere.

The two missing Part IV sections are **writing tasks, not modelling ones**: everything they report
is already measured, in `drafts/2026-07-27-discrepancy-catalogue.md` and the five scripts behind
it (`prices.py`, `live_ledger.py`, `model_vs_live.py`, `iv_panel.py`, `selection_fit.py`).

---

## Part I — Setup

**I-1. Prior work is a stub.** `sections/03-prior-work.md` needs a real literature pass before
assembly: the PUT and BXM indices, the volatility risk premium literature, Whaley, Israelov &
Nielsen. It must also **verify the novelty claim** for the inventory/queueing framing rather
than assert it — that claim is load-bearing for the article's contribution and is currently
unchecked.

**I-2. The abstract is written last.** `sections/01-abstract.md` is a stub by design; it cannot
be honest until Parts III and IV fix what the article concludes.

**I-4. §02 promises things Parts III and IV must actually deliver.** The contributions list
commits the article to five results that do not yet exist anywhere:

- diversification leaves expected return and expected capital **completely unchanged** while
  removing only the noise around them (contribution 7 → III-1);
- correlations rising toward one in a crisis is **the mechanism the strategy is most exposed
  to**, not a tail scenario (contribution 7 → III-2);
- the live comparison confirms the model **link by link** — entry law to within a percent, the
  depth census to within five (contribution 8 → IV-1);
- the account's advantage came entirely from the excluded lever while the option machinery
  earned nothing distinguishable from zero (contribution 8 → IV-2);
- the article shows **which of the model's predictions a career-length track record has no
  power to test** (contribution 8 → IV-1). *Nothing currently delivers this one* — see IV-1.

Either the sections deliver these or §02 is rewritten. Check the list against the finished
Parts III and IV before assembly. **This is now a check, not a rewrite**: II-16 made the other
editing pass over §02 on 2026-07-31, which added the finite account as contribution 6 and pushed
portfolios to 7 and the live comparison to 8 — hence the numbering above. Items 1 through 6 are
delivered and were re-read for stale figures in that pass; only 7 and 8 are still promises.

## Part III — Many assets

Neither file exists. This is Stage 3 of the restructure and the largest single block of
remaining work. Both sections have their inputs already measured or already derived; what is
missing is the derivation and the prose.

**III-1. Write §12, the portfolio section** (`{#sec:portfolio}`). It owes four things:

- **The diversification result** §02 promises: expected return and expected capital are
  unchanged by diversification, which removes only the variance around them. Little's law needs
  no independence assumption and so carries over directly; the statement to be careful with is
  what *does* change.
- **The distributional claims the single-name analysis handed forward** (was #1). The article
  states that ±√I\* and e^(−I\*) belong to a diversified portfolio of independent wheels, not to
  one name — on one name the inventory is nothing like Poisson (Var/Mean ≈ 4.8, P(I = 0) ≈ 14%
  against Poisson's 0.9%). §12 is where that promise is redeemed.
- **Position sizing** (was #6). The model sells exactly one put per period regardless of
  capital. A practitioner-facing subsection on sizing against total capital belongs here, and
  the warning it must carry is that capital demand is bursty and heavy-tailed, so **sizing
  against mean capital is precisely the mistake**.

  **Quantified 2026-07-29 (II-7), and the warning has a second half that is worse than the
  first.** The mistake is not only that demand is bursty *around* its mean: the mean itself is a
  near-singular function of two parameters nobody knows exactly. A\* runs **7.97 / 19.23 / 48.97
  / >126** across σ = 15/20/25/28% and diverges at 30%, a local elasticity of **3.5** rising to a
  4.2 secant by σ = 25% — a 1% relative error in the volatility estimate is a 3.5% error in the
  equity required, and the sensitivity worsens as volatility rises — while the dials the
  operator actually chooses (p\*, the cadence, n) move it proportionally and predictably. Sized
  for the running example and run on a σ = 25% stock, an account retains **39.3% throughput**.
  Both halves belong in this subsection: the distribution around the mean, and the fragility of
  the mean. Anything quoting the elasticity must say which of 3.5 and 4.2 it means.
- **The live book's width** (was #24, figures restated 2026-07-27). The account sells puts
  across **95 names while holding inventory in 34**, so put margin is **$43.4k = 31% of Track B
  capital** against the single-name model's 1.6%. Premium is generated across a far wider book
  than the inventory it creates. This is the structural difference that most damages
  comparability: **any direct comparison of Track A yields between model and live account is
  meaningless without it**, which makes it §12's business and a caveat §14 must reference.

**III-2. Write §13, the correlation section** (`{#sec:correlation}`). Two results:

- **Common-shock arrivals** (was #11). Assignments across a portfolio of wheels cluster on
  market-wide drawdown dates. Exits diversify across names; **arrivals do not**. A
  portfolio-level model needs a systematic component in p, and the sting is the timing: bursts
  arrive exactly when capital is scarcest. Clustering is measured in the live book and waiting
  to be used.
- **Correlation → 1 in a crisis**, framed as §02 promises it: the mechanism the strategy is
  most exposed to, not a tail scenario. Every diversification benefit claimed in §12 is a
  benefit that fails in exactly the state that matters.

## Part IV — Reality

Neither §14 nor §15 exists; the outlook is a stub. Everything below is measured — these are
write-ups.

**IV-1. Write §14, verification** (`{#sec:verification}`, was #21). The spine tested against
live data, not only simulation.

- **Entry law:** 71.5 assignments expected, 72 finished below the strike, 71 assigned, over 921
  contracts — an aggregate error of 0.7%.
- **Depth census:** mean depth 0.151 model against 0.146 live over 3,807 lot-days. The model
  fits at the article's **μ = 7% far better than at the window's realised drift** (0.151 against
  0.101) — that deserves its own paragraph, since it is a statement about which parameter the
  census is actually sensitive to.
- **q(x):** 26.3% of calls expected exercised against 19.6% realised, monotone in depth.
- **Survival:** the model exits lots faster than observed at every horizon, and the comparison
  is Kaplan–Meier, so **this is not censoring** (was #9). Show the compounding of the
  per-period gap.
- **The two internal checks:** the grid-free Monte Carlo (`mc_holding.py`) that proves the
  extrapolated stationary figures, and the **Q-world no-arbitrage identity** — run at ν_Q with
  Q-priced premiums, expected excess return over r must vanish up to the dividend-withholding
  leak; it holds to 8 bp at 30y and under 20 bp at every horizon, and it has already caught one
  real omission. This is the settled decision the restructure owed the article a theorem for.
  **What the leftover residual is, is open** (from II-2, 2026-07-28). It is *not* the Track C
  overcharge on collateral, which was this item's previous claim: the residual is positive
  (+17.5/+12.6/+7.9 bp at Standard's 5/10/30y) where that argument predicts negative
  (−16.0/−11.3/−6.7), and at Conservative it reads +2.3 bp against a predicted −31.5. The clue
  worth chasing is that Q-world `econ_pnl` exceeds r·E[I] − leak by ≈ **0.0020 per arrival** in
  both regimes at every horizon — a per-lot term, not a capital-proportional one. Either
  identify it or state the residual as numerical tolerance and say so; do not attribute it to
  the collateral.
- **Claim only the aggregates.** The restatement withdrew two bin-level results: T1's
  calibration curve is sensitive to whether entry is priced at the session open or close (top
  bucket 27.4% predicted against 8.0% realised at the open, 25.9% against 24.3% at the close —
  the operator sells into intraday weakness that partly reverts, so the truth is between), and
  q(x)'s two deepest bins now hold 70 and 20 contracts. No bucket-level claim should be
  reintroduced.
- **The calendar/session mismatch, found 2026-07-28 and deliberately not fixed.** Every τ in the
  live tests is in *calendar* years while every σ is annualised over **252 sessions**, so a put
  written Monday at the open for Friday's close — five sessions — is priced with four days of
  diffusion. The units are wrong and the understatement is large: σ·√τ is short by a factor
  √((5/252)/(4/365)) = **1.35** at the median put. **And the wrong convention is the one that
  fits.** At the window's drift, pricing each put on its own session count predicts **90.3**
  assignments against the **71** that occurred; the calendar reading predicts **71.5**. So either
  the operator's entries partly revert — which is T1's own bucket finding, the opening print
  overstating moneyness on puts written nearest the money — or session-annualised realised
  volatility overstates the volatility relevant to a five-session option, or both. Resolve it
  before claiming T1 as a clean pass, and note that the aggregate agreement currently rests on
  a cancellation rather than on each side being right. Nothing was changed in the code; the
  decision and its evidence are in `model_vs_live.py`'s T1 docstring. Note the article itself is
  unaffected: its τ_p = 1/52 is 4.85 sessions, so its own week is already a trading week.
- **Three measurement traps**, worth a paragraph because all three were fallen into: reading
  depth on the day before exit discards nearly every exit; sampling lots on a synthetic τ_c grid
  scores periods at tenors never traded; and pricing an entry at the day's close when the
  operator writes in the first hour builds a look-ahead into every measured entry depth.
- **What a career-length record cannot test** — owed to §02 (I-4) and not yet written anywhere.
  The natural material is already in Part II: equilibrium is approached over ~90 years and the
  mean holding time is 2.1 years against an 8-week median, so the stationary results are
  structurally untestable by any operator, and the 14-month window resolves 36 of 55 lots. State
  which predictions the data *can* discriminate and which it provably cannot.

**IV-2. Write §15, the live account** (`{#sec:live}`, was #20). The ledger and its verdict.
**Lead with the ledger gap, not the return.**

- **The ledger:** Track A on cost basis **+38.11%/yr** against Track B **+19.73%**; same-names
  buy-and-hold +24.50%; option-overlay excess **−4.77%/yr**; selection **+25.39%/yr**,
  exposure-matched.
- **This section owes the reader the intervals, and it is the only section that does.** Parts I
  and II assert three times — in `02-introduction`, `04-strategy` and `09-returns` — that the
  overlay "earned nothing distinguishable from zero", with no number anywhere behind it. That is
  deliberate, the statistics belong here, but it means §15 must actually deliver them or the
  claim is unsupported across the whole article. Required: the point estimate, the 90%
  resampling interval **−19.8% to +7.6% clustered by name** (quote the clustered one; −25.8% to
  +14.2% by lot is the looser alternative), P(excess < 0) = 69%, and the sample it rests on.
  `live_ledger.py --bootstrap` produces all of it.
- **The UNH lot is the worked example**, deliberately kept out of Part II so it lands here:
  assigned at 260, a four-week call written at the same 260 basis for $18.10, called away at 260
  with the stock at 393.85 — collected $1,810, surrendered $13,385. It is also, on its own, the
  difference between a negative and a positive overlay excess (−4.77% → +2.10%) **and** 50% of
  the selection gap. The same position carries both verdicts, and that is the point rather than
  a caveat: a lot that runs far enough to dominate selection is a lot whose call gave the run
  away. **Do not present it as an outlier to be set aside.** UNH, ELV and MSFT all show negative
  excess and positive selection together.
- **The by-leg decomposition**, which is where the restatement bites: the **put leg keeps 20.7%
  of premium, the call leg −32.9%**, frictions −$5,054. The old near-symmetry between the legs
  was cheap calls on falling names; on the universe the strategy actually claims, the call leg
  gives back a third of its own premium. Removing those names did not create the effect, it
  stopped hiding it.
- **Selection, reported not modelled** (was #22 and #14). The pre-registered rule
  (`drafts/2026-07-27-selection-rule-preregistration.md`) is fitted: rules 4 and 6 (fallen
  angels, oversold) confirmed at z ≈ −10 with a permutation check agreeing; rule 5 (avoid
  falling knives) **rejected outright** in both its simple and its interaction form — its
  partial rescue was withdrawn on the restated choice set. **Name what modelling it would
  commit to:** under GBM, entry timing cannot generate return by construction, so treating
  selection as profitable is a claim of mean reversion and must be argued as one. 20 lots in one
  bull market cannot support it. If it is ever modelled, the minimal form is a state-dependent
  thinning of the arrival process.
- **The cadence calibration** (was #7). τ_p = T is a good approximation because the dominant put
  is sold Monday at the open for Friday's close — live 5 of the week's 7 days, continuous in
  trading time. What the account does instead of selling every week is skip weeks: **18.1 puts
  per name-year while in rotation** against 52, **1.41 lots per name-year** against the model's
  10.4 at p\* = 20%, modal gap exactly 7 days (40% of gaps). Both rates are the discrepancy
  catalogue's and have no script behind them (INF-2); the lot count under the second moved
  56 → 55 on 2026-07-28, so re-measure before quoting rather than copying the digits.
  [The entry section](#sec:entry) now defers the arrival gap to here, deliberately without
  digits, so this is the only place they appear. When they are re-measured, **check the identity
  that closes the gap**: puts per name-year × the per-put assignment rate should reproduce lots
  per name-year, which at the current digits it does (18.1 × 7.7% ≈ 1.4). If it stops doing so,
  one of the three is measured over the wrong denominator.
- **The implied-volatility panel** (was #23). The put leg's spread over subsequent realised
  volatility runs **~+10 points, roughly double the call leg's**, and the within-name depth
  slope is **+30–40% relative IV** from shallow to deep. This is the measurement behind the
  article's decision to carry one scalar σ_IV; report it here and let [the returns
  section](#sec:returns)'s stated bias direction be checked against it.
- **The regime caveat, which bounds everything above:** the universe returned +8.96%/yr over the
  window and the held names +34.36%/yr, and **a covered-call overlay must lag in a strong
  up-market**. That is mechanical, not evidence. Neither the overlay nor the selection result is
  an unconditional estimate.
- Reference III-1's book-width caveat rather than restating it: Track A yields are not
  comparable between a 95-name put book and a single-name model.

**IV-3. Rewrite §16, the outlook.** Currently a stub whose standing content is the list of
things deliberately outside the model — the call-strike lever, permanent impairment and the
dividend cut, the entry filter, transaction costs, skew, moving volatility, depth-dependent
drift. That list is accurate and should survive. What it cannot be written around until Parts
III and IV land is the forward-looking half: what the model should become, given what the live
comparison actually showed. Write last, and rename the file to `16-outlook.md` when Part III
takes §12 and §13.

**IV-4. The next tranche of live data — standing.** The out-of-sample pre-registration
(`drafts/2026-07-27-out-of-sample-preregistration.md`) fixes twelve predictions and a procedure,
and it may not be edited once new data is examined. **Trigger: six months of new statements or
20 new completed lots, whichever comes first.** Rules that bind: refit, do not re-specify; no
new features in `selection_fit.py` without a dated amendment; classify the regime *before*
computing results; report failures as failures, in a dated appendix. P12 (impairment) is retired
rather than pending. If a tranche arrives before the article is assembled, the article reports
the out-of-sample result; if not, §14 says the test is pre-registered and pending.

## Infrastructure and assembly

One standing discipline, inherited from Part II's code half and closing with no item: **every
number a section quotes gets a check under that section's heading.** For anything with a formula
behind it that is now enforced mechanically by INF-5's coverage test; INF-2 carries the rest into
Parts III and IV. Prose figures with no formula behind them are the residue it cannot reach —
II-16's stale "four years" survived the weekly-cadence change of 2026-07-26 for exactly that
reason — so a section's narrative numbers still have to be re-read by hand when a running
parameter moves.

**INF-2. Extend `verify_examples.py` to Parts III and IV — and decide about the live figures.**
Every number in §12–§15 needs a check, on the same section-by-section discipline as the rest, and
every formula they display needs an example module under INF-5's policy. Two open questions:
whether the portfolio results get their own Monte Carlo cross-check the way the single-name spine
did, and — the real gap — that **no check reproduces the live-account figures at all**. §15 will
quote a ledger produced by `live_ledger.py` against statement data; if those numbers move, nothing
tells us. At minimum, pin the headline ledger figures in a regression check so a change in
`analyze_statement.py` cannot silently restate the article.

The withdrawal of I-3 sharpened this: a figure that lives only in a draft, with **no script
behind it**, survived into TODO as a finding and was wrong about what it measured. The concrete
piece of that episode worth keeping is the **per-lot call-strike classification** — every call
scored against the layers actually held when it was written, not against one basis per name.
It exists nowhere in `code/`; the reconstruction that withdrew I-3 was ad hoc. Put it in
`analyze_statement.py` beside the lot lifecycle, where it can be re-run.

**INF-3. The LaTeX assembly pipeline.** Unicode-math → LaTeX conversion, `{#sec:...}` anchors →
`\label`/`\ref`, `{#eq:...}` → numbered `equation` environments with `\eqref`. Tooling decision
deferred until the sections stabilise, which is now close: pick it once Part IV drafts. The
generated appendix (`sections/99-reproduction.md`) needs a place in that pipeline too.

**INF-4. Figures.** The ASCII payoff diagrams in the §02 detour are placeholders and must be
redrawn as proper vector figures (TikZ or similar) at assembly. Worth reviewing at the same time
whether Parts II–IV want figures they currently do without — the depth census, the survival
curve and the live-versus-model comparisons are all natural candidates and none is drawn.
**One more joined the list on 2026-07-29:** II-7's (σ, μ) plane, where both stability boundaries
are curves rather than points and the band between them — lot count stationary, capital integral
divergent — is visible as an area. `sensitivity()` prints it as a text grid; it wants to be drawn.

**INF-5. Every quoted number gets a formula, a runnable script and a footnote.** The
infrastructure landed 2026-07-30 — `code/examples/` with a harness, 19 modules covering all 46
numbered formulas, 96 frozen cases, a generated appendix (`sections/99-reproduction.md`), eleven
compositions promoted into `model.py`, and a coverage test wired into `verify_examples.py` that
asserts every displayed `{#eq:...}` has a registered example, every example is cited from the
prose, and every footnote names the script that actually backs its formula. The write-up, the
design decision behind it (a `Case` *is* a command line) and the three prose errors it surfaced
are in [`DONE.md`](DONE.md). **Two items of follow-up remain.**

- **Five lower-value formula gaps**, all of them numbers quoted without a displayed formula: the
  census moments (§08's mean depth 38% and weighted q 0.066), the cost-basis capital of §09
  (18.23, where `eq:capital` gives market value only), the volatility-premium slope ("about 45
  basis points" per point, a finite difference over the sweep), the sticky-dividend fixed point
  (§09:151, described in prose but never displayed), and x\* = ln(1 + ν/δ) (§09, displayed inline
  but unnumbered). Each is backed by a script and a footnote already; what is missing is only the
  display in the prose.
- **§00's anchor registry has drifted from the sections, and the coverage test cannot see it**
  (found 2026-07-30, during the TODO cleanup; halved the same day). `sections/00-notation.md`
  Conventions is declared the single source of truth for anchors, and it **omits** `eq:screen-gap`
  (05), `eq:little-finite` (08), `eq:mark-loss` and `eq:giveaway` (09) — the four formulas INF-5
  itself added. It was also wrong in the other direction, listing `eq:account-criterion` under §10
  where no section displayed it; **II-12 displayed it on 2026-07-30**, so that half is closed and
  the registry is now only incomplete rather than also false. `coverage()` reads
  `declared_anchors()` off the displays themselves, so a registry that disagrees with them is
  invisible to it. Fix the list, and add the missing guard: parse §00's registry and assert it
  matches the displayed set exactly, per section. That closes the one remaining way a numbered
  formula can be promised and not exist — and it is the guard that would have caught
  `eq:account-criterion` sitting promised-but-absent for a day.
