# TODO

Open work only. Everything finished, resolved or deliberately descoped lives in
[`DONE.md`](DONE.md), which also carries the map from the old flat numbering (#1–#25) to the
per-part numbering used here. Items are tagged `(was #n)` where a predecessor existed, so the
citations in `drafts/` stay traceable.

Sections reference items as "TODO I-1", "TODO IV-2" — at present **no section carries such a
flag**, and that is the intended steady state: an in-text flag is a promise to a reader and
should be added only when the text genuinely defers something.

## Where things stand

Twelve of the seventeen planned files exist. Part I is written; **Part II was reopened on
2026-07-29** for the working-capital reframe, which adds a section to it; **Part III and Part IV
are unwritten**, and between them they remain the bulk of what is left.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · **11 constrained** | written, and **reopened**: II-5…II-14 below; 11 does not exist |
| III. Many assets | 12 portfolio · 13 correlation | **do not exist** |
| IV. Reality | 14 verification · 15 live-account · 16 outlook | **14, 15 do not exist**; outlook is a stub, currently on disk as `15-outlook.md` |

Part III and Part IV shift by one because of the new §11. Anchors are name-based, so no
cross-reference breaks and only filenames move; the renumbering is deferred until Part III drafts,
per II-13.

Five existing sections already link to anchors in the missing files — `sec:portfolio`,
`sec:verification` and `sec:live` are referenced from 00, 04, 07, 08 and 09 — so those
cross-references are broken until Parts III and IV land. That is the assembly-time deadline.

The two Part IV sections are **writing tasks, not modelling ones**: everything they report is
already measured, in `drafts/2026-07-27-discrepancy-catalogue.md` and the five scripts behind
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
  removing only the noise around them (contribution 6 → III-1);
- correlations rising toward one in a crisis is **the mechanism the strategy is most exposed
  to**, not a tail scenario (contribution 6 → III-2);
- the live comparison confirms the model **link by link** — entry law to within a percent, the
  depth census to within five (contribution 7 → IV-1);
- the account's advantage came entirely from the excluded lever while the option machinery
  earned nothing distinguishable from zero (contribution 7 → IV-2);
- the article shows **which of the model's predictions a career-length track record has no
  power to test** (contribution 7 → IV-1). *Nothing currently delivers this one* — see IV-1.

Either the sections deliver these or §02 is rewritten. Check the list against the finished
Parts III and IV before assembly.

## Part II — One asset

II-1 (the strike dial) and II-2 (Track C on put collateral) were resolved on 2026-07-28; both
write-ups, and the two errors they turned up, are in [`DONE.md`](DONE.md).

**Everything below is the working-capital reframe, agreed 2026-07-29.** Part II currently models
an operator with unlimited capital: a put is sold every period regardless of what is already
held. Real accounts have a finite balance and a margin requirement, and the constraint changes
what the model *is* — arrivals become state-dependent, so the system stops being M/G/∞ and
becomes a loss system. Every existing figure survives as the **unconstrained limit**, recovered
exactly when the account is large enough never to block, and that equivalence is the regression
guard on the whole exercise.

Four decisions fixed before any code (2026-07-29):

- **Track B stays exposure.** The margin fraction governs *capacity*, not risk. Putting it in the
  denominator of [eq:excess](#eq:excess) would roughly quadruple the reported excess at γ_s = 0.25
  and appear to break the wheel-versus-stock result while nothing economic had changed. Equity
  required is a **second ledger line**, never a replacement.
- **Blocked means skip the put.** The operator does not sell what they could not cover. Blocking
  is binary per put, not proportional — which is what keeps saturation a hitting time.
- **Initial and maintenance requirements are deliberately not distinguished.** One parameter, and
  a prose note saying so.
- **No horizon cap is an input.** The saturation date T_sat is emergent: the first time E[I(t)]
  reaches capacity. The unconstrained "90 years" needed an arbitrary 90%-of-asymptote convention;
  a finite capacity is a real threshold and needs none. A career-length horizon returns only as an
  annotation on the output.

  **Amended 2026-07-29:** the decision stands, but T_sat turned out to answer a different question
  than it was adopted for. It is the right convention-free clock for **throughput** — when the
  account fills and arrivals start being refused — and it is *not* the horizon for **survival**,
  because a saturated account stays levered afterwards rather than stopping. So the reframe still
  takes no horizon as an input, and the price is that the survival horizon is unbounded, which is
  what makes II-6 rather than II-5 the item that produces a quotable liquidation probability. See
  II-5.

Code before prose: the survival figures decide how much of [the stability
section](#sec:stability) has to be restructured. The parameters and the survival closed forms
(II-3, II-4) landed 2026-07-29; the capacity fixed point, the simulator and the sweep remain.

### Code

**II-3 and II-4 were resolved on 2026-07-29**; both write-ups are in [`DONE.md`](DONE.md), and
the numbers they settled are quoted below where later items need them. `model.py` now carries
γ_p, γ_s, A, u\* and the financing spread, plus `liquidation_barrier`, `first_passage_prob`,
`liquidation_prob`, `max_leverage` and `leverage` in a working-capital block; `verify_examples.py`
checks them under a structural heading. Note that **"II-3" names two items** — the 2026-07-28
stress-table mislabel and the 2026-07-29 parameters — which `DONE.md` records.

**II-5. Capacity, T_sat and throughput. The fixed point is gone — see below.** Extend the
transient inverse at `model.py:703` (`time_to_fraction`) so it maps an absolute capacity in lots
to the first time E[I(t)] reaches it, interpolating inside the call period so the map is
continuous in capacity rather than a 4-week step (worth 46 days at capacity 11.4). Then report
the frontier over (γ_s, A, ε): capacity, T_sat, throughput retention λ_eff/λ, saturation
leverage, and steady-state return on equity **net of financing**. Leverage itself is *not* solved
for — it is II-4's closed form, for the reason below.

**The pre-flight (2026-07-29) confirmed the two design points and then broke the third.**
Monotonicity holds exactly: P(u\*) is non-decreasing over 30,000 scanned points at every (γ_s, A),
with P = 0 below u\* = γ_s (L ≤ 1, no debt) and P = 1 at u\* = 1 (f\* = 1, violation on day one),
so **the bracket [γ_s, 1] is valid and bisection is the right solver** — if there were anything to
solve. And static capacity belongs here, moving capacity in II-6, as agreed.

**What broke: T_sat is not the survival horizon, so it drops out of the survival question.** The
chain as written — "capacity sets T_sat, which sets survival probability" — assumes exposure ends
at saturation. It does not. Once E[I(t)] reaches capacity, arrivals block, inventory *sits* at
capacity with a fixed debit, and that is precisely the static-barrier configuration, held for
unbounded time. T_sat is when full leverage **begins**, not when it ends. Evaluate the barrier
over the correct horizon and the fixed point degenerates: solved u\* returns realized leverage
equal to **L_max(γ_s, ε) to 2e-16 at every A where the stopping rule binds at all**. There is no
frontier in leverage — II-4 already closed it.

Above a critical equity the stopping rule stops binding entirely, because inventory never reaches
capacity: realized leverage is min(capacity, E[I(∞)])/A, which falls below 1 and the account never
borrows. The crossover is **A\* = E[I(∞)]/L_max**, and it is item II-13's headline (below).

**Consequently II-6 is now load-bearing rather than confirmatory, and should probably run before
the sweep.** The static answer is an upper bound of unknown tightness: a saturated, blocked
account still collects premium, dividends and call-away proceeds with nowhere to redeploy them,
so the debit is repaid and the account *deleverages* — until repayment frees capacity, a new lot
arrives, and the debit grows again. That oscillation is the "net sign is not obvious a priori"
the item already names, and it is now the only thing standing between the closed form and a
survival number the article can quote. **Do not quote a liquidation probability from `model.py`
alone.**

**II-6. The constrained simulator — promoted, 2026-07-29.** `wheel_sim.py --scenario
constrained`: skip-when-blocked arrivals, debit tracking, mark-to-market equity, the liquidation
trigger, premium income and call-away repayment. It exists to catch the three corrections the
static barrier misses — new assignments grow the debit during exactly the declines that threaten
the account, while premium income and called-away lots repay it, and the net sign is not obvious a
priori. Shares no machinery with `model.py`, per the standing discipline; agreement is the
evidence.

**It is no longer a check on II-5, it is the item that answers the survival question**, because
II-5's pre-flight showed the analytic side has no fixed point left to solve and its static number
is an upper bound of unknown tightness. Two things it must report that the barrier cannot: whether
a saturated account's debit drifts up or down under blocked arrivals, and the **realized** leverage
path against the static L. Consider running it before II-7, since the sweep has nothing worth
sweeping until the survival number is trustworthy.

**II-7. The sweep.** γ_s × A grid through `model.pmap()` (module-level worker, picklable args,
called only from top level). Report the cell where **A equals the model's own E[Capital]** — an
account sized at the strategy's mean capital demand — since its liquidation probability is the
quantitative form of the "sizing against the mean is the mistake" warning, which is currently an
assertion with nothing behind it. Diff parallel against `WHEEL_WORKERS=1` before quoting anything.

### Prose

**II-8. §00 notation.** γ_p, γ_s, A, u\*, L, the financing spread, f\*, T_sat, and the new
section's anchor. Carry the prose note that initial and maintenance requirements are deliberately
merged.

**II-9. §04 strategy.** The exposure-versus-equity-required distinction belongs where the three
tracks are defined. State plainly that Track B remains exposure at market and that the constraint
runs on a different quantity.

**II-10. §09 returns.** An equity-required row in the capital table, plus the leverage result:
net excess on equity = excess·L − spread·(L−1), so **leverage is exactly neutral at every L when
the broker's spread equals the strategy's own excess return** — here 1.60%, against retail
spreads of 1–3%. Confirm the wheel-versus-buy-and-hold headline survives unchanged at every γ_s,
since leverage applies identically to both sides; if it does not, something is wrong.

**Measured 2026-07-29, and it makes the neutrality result nearly moot in the operator's favour.**
Evaluated at survivable leverage rather than at arbitrary L, the whole effect is small: at
γ_s = 0.25 the net excess runs **+1.82% at zero spread, +1.62% at 1.5%, +1.42% at 3%**, against
+1.60% unlevered. So leverage adds at most 22bp, and past the 1.60% crossover it *subtracts* —
at a 3% retail spread a levered wheel earns less than an unlevered one. Say this plainly: the
borrowing that survives the liquidation constraint is too small to pay for itself at any retail
financing rate. The neutral-spread formula is the mechanism; this is the number.

**II-11. §08 inventory.** Reframe "the equilibrium the operator will never see". The constrained
operator *does* reach theirs, because a capacity ceiling truncates the slow tail that made the
approach take ninety years. Note that T_sat is convention-free where the 90% was not.

**Measured 2026-07-29, and the reframe needs a qualifier or it replaces one false comfort with
another.** Small accounts reach equilibrium quickly — 0.9y at A = 3 lots, 2.4y at 5 — but T_sat
rises explosively as capacity approaches the strategy's own stationary demand: **18.5y at A =
11.59, 44y at 15, 254y at 19, never at A\* = 19.23**. So the truncation only helps an operator
whose account is *far* below A\*, and it helps exactly in proportion to how little of the strategy
they are running (60% throughput at 11.59, 5% at A = 1). The honest statement is the trade, not
the escape: an operator reaches equilibrium quickly only by running a small fraction of the
strategy, and an operator running all of it inherits the ninety years unchanged.

**II-12. §10 stability.** Three changes. The two boundaries **do not move** — both are statements
about e^x and E[1/S], and financing does not enter either. The second boundary is
**reinterpreted**: expected capital cannot diverge inside a finite account, so m ≤ σ² shows up as
throughput collapsing to zero and the account quietly ceasing to be a wheel. And a **third failure
mode** joins the two, which needs the section's summary rewritten — it currently reads "neither
is losing money on a trade", and forced liquidation is exactly that, and is the only fast one
against two that are slow and invisible.

**II-13. New section, the constrained wheel** (`sections/11-constrained.md`, `{#sec:constrained}`).
The whole survival and steady-state analysis in one place, so the existing tables keep their
unconstrained base case with a stated qualifier instead of doubling in width. It owes:

- Little's law **run backwards** — inventory pinned by capacity, so the arrival rate becomes the
  output, λ_eff = capacity / E[W]. The binding resource is capital and the thing that consumes
  capital is holding time, which makes [the holding-time section](#sec:holding)'s 2.1 years the
  economically load-bearing number in the article rather than merely its most surprising one.
  **But the stated proportionality income ∝ A/(γ_s·E[W]) is wrong and must not be written**
  (measured 2026-07-29): it prices capacity at the *broker's* ceiling A/γ_s, and survivable
  capacity is L_max·A, not A/γ_s. The correct form is **income ∝ L_max(γ_s, ε)·A / E[W]**, and
  since L_max runs 1.00–1.16 the naive version overstates γ_s's contribution by **1.8× / 3.5× /
  5.8×** at γ_s = 0.50 / 0.25 / 0.15. Written the wrong way it would say a portfolio-margin
  account earns four times a cash account's income on the same equity. It earns 13% more;
- **A\*, the equity a wheel actually needs, which is the sharpest form of the result.** Throughput
  stops being lost at A\* = E[I(∞)]/L_max: **21.82 lots unlevered, 19.23 at portfolio margin,
  18.88 at the most aggressive margin available**, against a broker's ceiling that would claim
  3.27. So the broker's permission is **5.8× off the binding constraint**, and correctly risked,
  the whole of that permission buys a **12% discount on required equity**. Capacity comes from
  equity; leverage is nearly irrelevant to it. Below A\* the loss is severe and slow: an account
  sized at the model's own 30-year capital (11.59) runs at **60% throughput** and takes **18.5
  years** to get there, and T_sat then explodes — 44y at 78%, 254y at 98.8%, never at A\*;
- the account **migrating to its own boundary**: a mechanical put-selling rule with no
  withdrawals converts the broker's permission into actual leverage without the operator ever
  deciding to lever, so the untended steady state is the state of maximum fragility, and the
  stopping rule is mandatory rather than prudent;
- the **capacity derivative** — capacity in lots is A/(γ_s·S) with A marked to market, so as S
  falls an unlevered account's capacity *rises* while a levered account's falls and crosses zero;
- the **selectively distorted census**: blocking removes arrivals when the account is full, which
  is during drawdowns, so constrained inventory is missing precisely the lots that would have been
  bought cheapest;
- the **Q-world matched pair**, which **came out** (II-4, 2026-07-29): the leverage carrying a 10%
  eventual-liquidation risk in the real world carries **63.1%** under the pricing measure, and
  Q-world L_max at ε = 10% is 1.00008 — no leverage at all. The market prices this stock as one
  whose levered wheel is liquidated, alongside [the stability section](#sec:stability)'s "prices it
  as one whose inventory never clears". The machinery passes its own test;
- **θ read twice**, which is the cleanest thing the reframe turned up: first passage to the
  liquidation barrier is governed by the same 2ν/σ² as the census tail, so the constant that says
  whether expected capital converges also says whether a levered account survives. State it as a
  result, not as a convenience.

Two results to report **as they come out**, agreed before seeing them. The first still stands: the
reachable steady states may be small enough that the strategy is barely running, which is a
legitimate negative result and is not to be softened into a range. **The second is now measured,
and the guess was too generous** (II-4, 2026-07-29). γ_s barely matters — survivable leverage at
ε = 10% runs **1.0000 / 1.0861 / 1.1349 / 1.1557** across γ_s = 1.00 / 0.50 / 0.25 / 0.15 against
broker ceilings of 1 / 2 / 4 / 6.67, so the usable fraction of the broker's permission *falls*
from 100% to 54% to 28% to 17%. Survivable leverage lands near 1.1–1.2× **total**, not 1.1–1.2×
what the broker allows: the binding limit is near-independent of the permission, and the gap
widens the more generous the broker is. That is the form the swept parameter earns its place in.

**File numbering is deferred.** The new section takes 11, so Part III moves to 12/13 and Part IV
to 14/15/16. Anchors are name-based, so nothing cross-referential breaks and only filenames move;
make the decision when Part III drafts rather than renumbering twice.

### Verification

**II-14. Extend `verify_examples.py`.** Its own section, on the standing discipline. Two of the
four are already in, under the structural heading (II-4, 2026-07-29): the **γ_s = 1.0 regression**
— which must go on holding at every later step, not just today — and the **T → ∞ collapse** of the
finite-horizon first passage onto f\*^θ, alongside the L_max round trip, the f\* = 1 recovery of
the broker's ceiling and the Q-world pair. Still required: agreement between `model.py` and the
constrained simulator on T_sat and P(survive); and the **Q-world identity extended to the
constrained case** —
at m = r − δ with r_b = r, a blocked, levered wheel must still earn exactly r on equity at every
γ_s and every account size. Blocking arrivals creates no arbitrage, so any failure there is a bug
in the new machinery, and this is the strongest free test the reframe gets.

## Part III — Many assets

Neither file exists. This is Stage 3 of the restructure and the largest single block of
remaining work. Both sections have their inputs already measured or already derived; what is
missing is the derivation and the prose.

**The section numbers below are stale by one** and deliberately not yet updated: §11 is now the
constrained-wheel section of Part II (II-13), so the portfolio section is §12 and the correlation
section §13. Anchors (`sec:portfolio`, `sec:correlation`) are unaffected. Renumber once, when
Part III drafts.

**III-1. Write §11, the portfolio section** (`{#sec:portfolio}`). It owes four things:

- **The diversification result** §02 promises: expected return and expected capital are
  unchanged by diversification, which removes only the variance around them. Little's law needs
  no independence assumption and so carries over directly; the statement to be careful with is
  what *does* change.
- **The distributional claims the single-name analysis handed forward** (was #1). The article
  states that ±√I\* and e^(−I\*) belong to a diversified portfolio of independent wheels, not to
  one name — on one name the inventory is nothing like Poisson (Var/Mean ≈ 4.8, P(I = 0) ≈ 14%
  against Poisson's 0.9%). §11 is where that promise is redeemed.
- **Position sizing** (was #6). The model sells exactly one put per period regardless of
  capital. A practitioner-facing subsection on sizing against total capital belongs here, and
  the warning it must carry is that capital demand is bursty and heavy-tailed, so **sizing
  against mean capital is precisely the mistake**.
- **The live book's width** (was #24, figures restated 2026-07-27). The account sells puts
  across **95 names while holding inventory in 34**, so put margin is **$43.4k = 31% of Track B
  capital** against the single-name model's 1.6%. Premium is generated across a far wider book
  than the inventory it creates. This is the structural difference that most damages
  comparability: **any direct comparison of Track A yields between model and live account is
  meaningless without it**, which makes it §11's business and a caveat §14 must reference.

**III-2. Write §12, the correlation section** (`{#sec:correlation}`). Two results:

- **Common-shock arrivals** (was #11). Assignments across a portfolio of wheels cluster on
  market-wide drawdown dates. Exits diversify across names; **arrivals do not**. A
  portfolio-level model needs a systematic component in p, and the sting is the timing: bursts
  arrive exactly when capital is scarcest. Clustering is measured in the live book and waiting
  to be used.
- **Correlation → 1 in a crisis**, framed as §02 promises it: the mechanism the strategy is
  most exposed to, not a tail scenario. Every diversification benefit claimed in §11 is a
  benefit that fails in exactly the state that matters.

## Part IV — Reality

Neither §13 nor §14 exists; §15 is a stub. Everything below is measured — these are write-ups.

**IV-1. Write §13, verification** (`{#sec:verification}`, was #21). The spine tested against
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

**IV-2. Write §14, the live account** (`{#sec:live}`, was #20). The ledger and its verdict.
**Lead with the ledger gap, not the return.**

- **The ledger:** Track A on cost basis **+38.11%/yr** against Track B **+19.73%**; same-names
  buy-and-hold +24.50%; option-overlay excess **−4.77%/yr**; selection **+25.39%/yr**,
  exposure-matched.
- **This section owes the reader the intervals, and it is the only section that does.** Parts I
  and II assert three times — in `02-introduction`, `04-strategy` and `09-returns` — that the
  overlay "earned nothing distinguishable from zero", with no number anywhere behind it. That is
  deliberate, the statistics belong here, but it means §14 must actually deliver them or the
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

**IV-3. Rewrite §15, the outlook.** Currently a stub whose standing content is the list of
things deliberately outside the model — the call-strike lever, permanent impairment and the
dividend cut, the entry filter, transaction costs, skew, moving volatility, depth-dependent
drift. That list is accurate and should survive. What it cannot be written around until Parts
III and IV land is the forward-looking half: what the model should become, given what the live
comparison actually showed. Write last.

**IV-4. The next tranche of live data — standing.** The out-of-sample pre-registration
(`drafts/2026-07-27-out-of-sample-preregistration.md`) fixes twelve predictions and a procedure,
and it may not be edited once new data is examined. **Trigger: six months of new statements or
20 new completed lots, whichever comes first.** Rules that bind: refit, do not re-specify; no
new features in `selection_fit.py` without a dated amendment; classify the regime *before*
computing results; report failures as failures, in a dated appendix. P12 (impairment) is retired
rather than pending. If a tranche arrives before the article is assembled, the article reports
the out-of-sample result; if not, §13 says the test is pre-registered and pending.

## Infrastructure and assembly

**INF-2. Extend `verify_examples.py` to Parts III and IV — and decide about the live figures.**
Every number in §11–§14 needs a check, on the same section-by-section discipline as the rest.
Two open questions: whether the portfolio results get their own Monte Carlo cross-check the way
the single-name spine did, and — the real gap — that **no check reproduces the live-account
figures at all**. §14 will quote a ledger produced by `live_ledger.py` against statement data;
if those numbers move, nothing tells us. At minimum, pin the headline ledger figures in a
regression check so a change in `analyze_statement.py` cannot silently restate the article.

The withdrawal of I-3 sharpened this: a figure that lives only in a draft, with **no script
behind it**, survived into TODO as a finding and was wrong about what it measured. The concrete
piece of that episode worth keeping is the **per-lot call-strike classification** — every call
scored against the layers actually held when it was written, not against one basis per name.
It exists nowhere in `code/`; the reconstruction that withdrew I-3 was ad hoc. Put it in
`analyze_statement.py` beside the lot lifecycle, where it can be re-run.

**INF-3. The LaTeX assembly pipeline.** Unicode-math → LaTeX conversion, `{#sec:...}` anchors →
`\label`/`\ref`, `{#eq:...}` → numbered `equation` environments with `\eqref`. Tooling decision
deferred until the sections stabilise, which is now close: pick it once Part IV drafts.

**INF-4. Figures.** The ASCII payoff diagrams in the §02 detour are placeholders and must be
redrawn as proper vector figures (TikZ or similar) at assembly. Worth reviewing at the same time
whether Parts II–IV want figures they currently do without — the depth census, the survival
curve and the live-versus-model comparisons are all natural candidates and none is drawn.
