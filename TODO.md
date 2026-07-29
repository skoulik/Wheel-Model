# TODO

Open work only. Everything finished, resolved or deliberately descoped lives in
[`DONE.md`](DONE.md), which also carries the map from the old flat numbering (#1–#25) to the
per-part numbering used here. Items are tagged `(was #n)` where a predecessor existed, so the
citations in `drafts/` stay traceable.

Sections reference items as "TODO I-1", "TODO IV-2" — at present **no section carries such a
flag**, and that is the intended steady state: an in-text flag is a promise to a reader and
should be added only when the text genuinely defers something.

## Where things stand

Thirteen of the seventeen planned files exist. Part I is written; **Part II was reopened on
2026-07-29** for the working-capital reframe, whose new §11 landed the same day, leaving four
prose edits to existing sections; **Part III and Part IV are unwritten**, and between them they
remain the bulk of what is left.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · **11 constrained** | all seven written; four edits outstanding (II-10, II-11, II-12, II-16) |
| III. Many assets | 12 portfolio · 13 correlation | **do not exist** |
| IV. Reality | 14 verification · 15 live-account · 16 outlook | **14, 15 do not exist**; outlook is a stub, currently on disk as `15-outlook.md` |

Part III and Part IV shift by one because of §11. Anchors are name-based, so no cross-reference
breaks and only filenames move; the renumbering is deferred until Part III drafts, and the note
recording that decision now lives in the Part III preamble below.

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
Parts III and IV before assembly. **II-16 is the other item on this list** — the constrained
account, which the list does not mention at all — so §02 gets one editing pass, not two.

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
section](#sec:stability) has to be restructured. The parameters, the survival closed forms, the
capacity frontier, the constrained simulator and the sensitivity sweep (II-3 through II-7) all
landed 2026-07-29. **The code half of the reframe is complete; everything remaining in Part II
is prose.**

### Code

**II-3 through II-7 were resolved on 2026-07-29**; the write-ups are in [`DONE.md`](DONE.md),
and the numbers they settled are quoted below where later items need them. `model.py` now carries
γ_p, γ_s, A, u\* and the financing spread, plus `liquidation_barrier`, `first_passage_prob`,
`liquidation_prob`, `max_leverage` and `leverage` in a working-capital block, and a capacity block
beside it — `survival_utilization`, `max_debit_growth`, `max_sustainable_draw`, `saturation`,
`time_to_inventory` — reported by `frontier()`. `wheel_sim.py` carries the matching ledger and
`--scenario constrained`. `verify_examples.py` checks all of it under structural headings. Note
that **"II-3" names two items** — the 2026-07-28 stress-table mislabel and the 2026-07-29
parameters — which `DONE.md` records.

**What II-5 handed forward, since three items below depend on it.** Throughput retention below
A\* is exactly **A/A\***, and realized leverage there is exactly **L_max** — identities, not fits.
T_sat is **2.4y at A = 5, 18.5y at 11.59, 44.4y at 15, 270y at 0.99·A\*, never at A\***. The
sustainable draw is **degenerate along A** (g_max ≡ 0 wherever the stopping rule binds, since the
leverage was chosen under the same ε) and sharp along L: at A = 11.59 and γ_s = 0.25 it runs
**4.63% of equity unlevered, 4.58% at L_max, 2.86% at L = 1.5, −2.14% at L = 1.883**. And realized
leverage is capped by the strategy's own demand, **E[I(∞)]/A**, not by the broker — that account
cannot reach the permitted 4.00 however much it is allowed. **Do not quote a liquidation
probability from `model.py` alone**; that is II-6's, and it is now measured.

**Two qualifiers II-6 attached to the block above** (2026-07-29), which any prose using these
figures must carry. First, **throughput = A/A\* is a statement about an account of constant size
in shares**, and the g = 0 cash policy the frontier is computed under holds the debit constant in
*dollars* instead — a dollar-constant account shrinks against a compounding price, and simulated,
that **halves the throughput**, 31.8% against the reported 60.3%. Staying stationary costs a draw
of **r + econ_excess − m = 2.12% of equity per year**, so the "maximum sustainable draw" of
4.58–4.63% and the draw that sustains the *business* differ by a factor of two, and the article
must say which it means. Second, **realized leverage sits far below the stopping rule** — 0.745
against 1.1349 at A = 11.59 — because a book refilled one lot a week is under its ceiling most of
the time; at A = 5 integer lots keep the account from borrowing at all, so its permitted 13%
leverage is unreachable and its barrier is vacuous.

**II-6 was resolved on 2026-07-29**; the write-up is in [`DONE.md`](DONE.md). `wheel_sim.py
--scenario constrained`, with a ledger inside `run_path` that is inert at `equity = inf` (so the
five pre-existing scenarios are byte-identical), continuous barrier monitoring through a
Brownian bridge, and a **frozen** shadow barrier carried beside the live one on the same price
path so the correction is measured paired. What it settled, since most of the items below depend
on it:

- the closed forms are **right about what they describe** — the frozen barrier reproduces
  `liquidation_prob` to within 1.6 standard errors at probabilities from 1% to 47%, and T_sat lands
  at **18.9y against 18.5y**;
- and what they describe is **not an operator**: the live account is liquidated **3.6× as often**
  at the prudent stopping rule (3.95% against 1.09% at 30y past saturation), because a frozen book
  de-levers as the price rises and an operator on a utilization rule buys instead. The barrier
  ratchets up with the price and does not come back down;
- **the sign of the correction is a function of the cash policy**, not a constant: full retention
  is *safer* than the frozen barrier (0.35%), withdrawing the income is eight times worse (8.64%);
- **uniform thinning is right to under 1%** in count, income and E[W] — so the frontier's income
  and RoE figures are sound — while its composition error is **+5% on mean depth after
  saturation: deeper, not shallower**, which reverses II-13's stated expectation;
- the frontier's own cash policy (g = 0) **halves the throughput** it reports, because it holds the
  debit constant in dollars while the model counts an account in shares.

**II-7 was resolved on 2026-07-29** as the second of the two things it might have been — the sweep
over σ, μ, p\*, n and T, each of which re-solves the walk; the write-up is in [`DONE.md`](DONE.md).
`sensitivity()` in `model.py`, on by default, `--no-sweep` to skip. What it hands the prose:

- **the parameters sort into two kinds.** The dials an operator chooses move A\* proportionally —
  exactly as 1/T along the cadence, nearly as λ along p\*, sub-linearly in n. The two they only
  estimate do not: A\* runs **7.97 / 19.23 / 48.97 / >126** across σ = 15/20/25/28% and diverges at
  30%, and **3.74 / 6.81 / 19.23 / none** down μ = 13/10/7/4%. Local elasticity to σ is **3.5**, so a
  1% relative error in the volatility estimate is a 3.5% error in the equity required — and it
  *rises* with volatility, averaging 4.2 over the 20% → 25% move (corrected by II-13, 2026-07-29;
  the 4.2 originally recorded here is that secant, not the derivative — see the amendment in
  [`DONE.md`](DONE.md));
- **the effect compounds**, because survivable leverage collapses toward 1 exactly where inventory
  demand explodes: the equity discount the broker's permission buys is **35% at σ = 15%, 12% at
  20%, 0.4% at 25%**;
- **sized for the wrong stock, an operator runs a fraction of the strategy**: at A = 19.23, a
  σ = 25% stock retains **39.3% throughput and saturates in 29.9 years**;
- and **ν = 0 is not a value the grid rule can be handed** — σ = 30% at μ = 7% is ν = +6.9e-18 by
  rounding, which asks for a grid of 4e18 cells. Cells that flat are refused, not approximated.

### Prose

**II-8 (§00 notation) was resolved on 2026-07-29**; the write-up is in [`DONE.md`](DONE.md). The
symbols are fixed, γ is now **γ_p** throughout (seven occurrences in §09 moved with it), and the
notation carries the three conventions — merged initial/maintenance requirements, the put
collateral excluded uniformly, and the defaults being the unconstrained operator. **What it hands
the prose items below is a set of equation anchors that are now promises**: §11 must display the
twelve listed in §00 (`eq:leverage`, `eq:barrier`, `eq:first-passage`, `eq:survive`, `eq:lmax`,
`eq:capacity`, `eq:astar`, `eq:lambda-eff`, `eq:debit-growth`, `eq:theta-eff`, `eq:gmax`,
`eq:draw`) and §10 must display `eq:account-criterion`. Capacity in lots has a symbol it did not
have in the code, **I_max = L_max·A**.

**II-9 (§04 strategy) was resolved on 2026-07-29**; the write-up is in [`DONE.md`](DONE.md). The
tracks now carry the exposure-versus-equity-required distinction, and §04 flags the "a put every
period regardless of inventory" rule as the unconstrained idealization rather than the definition.
Two things it hands forward: the argument against dividing by equity required is made **as a
statement about financing rather than as an arithmetic error** — the levered number is correct and
answers a different question — so II-10 and II-13 must not re-argue it as a mistake; and §04 now
promises the reader that **everything before §11 is the unconstrained limit §11 recovers**, which
II-13 owes a demonstration of rather than an assertion.

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

**II-5 reached the same verdict in the other currency** (2026-07-29), which is worth one sentence
here and the full treatment in II-13: the maximum sustainable draw is **4.63% of equity unlevered
and 4.58% at survivable leverage**, so borrowing that survives buys no drawing power either.
Two independent ledgers, one conclusion.

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

**T_sat itself survived II-6's check** (2026-07-29): simulated **18.9y against the analytic 18.5y**
at capacity 13.15 and **8.6y against 8.8y** at capacity 10, with the whole transient inventory
curve tracking to a few per cent. So the reframe's clock is sound; what II-6 qualified is the
*throughput* the operator gets while it runs, not the time.

**II-12. §10 stability.** Three changes. The two boundaries **do not move** — both are statements
about e^x and E[1/S], and financing does not enter either. The second boundary is
**reinterpreted**: expected capital cannot diverge inside a finite account, so m ≤ σ² shows up as
throughput collapsing to zero and the account quietly ceasing to be a wheel. And a **third failure
mode** joins the two, which needs the section's summary rewritten — it currently reads "neither
is losing money on a trade", and forced liquidation is exactly that, and is the only fast one
against two that are slow and invisible.

**The third mode now has a boundary, in the same currency as the other two** (II-15, 2026-07-29).
Lots return iff **ν > 0**; their capital returns iff **m > σ²**; the account survives iff
**ν > g**, the price's median growth outrunning the debt's. Write the three as one list, the third
displayed and numbered as `eq:account-criterion` (II-8 registered the anchor) — the
section is built around exactly this kind of comparison, and the third is the first one an
operator can *move*, since g is a cash policy rather than a property of the stock. Its sharpest
form: withdrawing income while the interest accrues puts g = r_b = 5% against ν = 2.5%, so the
boundary is not merely crossed but crossed by a factor of two, and liquidation becomes certain at
any leverage. Note also that the third boundary is the only one of the three that **does not**
bind an unlevered account, which is why it belongs beside them rather than above them.

**II-6 confirmed the ranking and disowned the arithmetic** (2026-07-29). Withdrawing the income is
indeed the policy that gets liquidated — **8.64%** within thirty years of saturation against
**1.11%** for servicing the interest and **0.35%** for retaining everything — so ν > g is the
right boundary and the right ordering. But the realized g under that policy is **+1.3%, not the
nominal 5%**, because withdrawing the income shrinks the account faster than the interest
compounds the debit; the boundary is crossed by rather less than the factor of two the closed form
suggests, and it is crossed nonetheless. Write ν > g as the criterion and the ranking as the
evidence; do not quote g = r_b as a measured rate.

**II-13 (§11, the constrained wheel) was resolved on 2026-07-29**, and **II-14 completed with
it**; both write-ups are in [`DONE.md`](DONE.md). `sections/11-constrained.md` carries all twelve
displays II-8 registered, and `verify_examples.py` gained the matching `--- Section 11 ---` block
(8.6 s → 11.2 s). Three things it hands the four prose items still open:

- **the elasticity of A\* to σ is 3.5, not the 4.2 recorded by II-7** — that figure is the secant
  out to σ = 25% rather than the local derivative. Corrected above and in III-1, with an
  `**Amended:**` note on II-7 in [`DONE.md`](DONE.md). Anything quoting it must say which it means;
- **the sustainable draw is not monotone in leverage**: it rises 2bp from L = 1.0000 to 1.0192
  before collapsing, so “falls, then goes negative” is wrong and “flat as far as survivable
  leverage, then collapses through zero” is right;
- **§11 does not display `eq:account-criterion`** — §00 assigns it to §10, so it remains II-12's to
  write. §11 states ν > g inline and points at [the stability section](#sec:stability).

**II-16. §02 introduction** (raised 2026-07-29, when II-8 landed). The contributions list runs to
seven items and **none of them is the constrained account**, though the reframe added a whole
section to Part II — and §02 is the one section whose job is to promise the reader what the
article delivers. It owes three things:

- **a contribution for the finite account**: A\* is 5.8× the broker's ceiling, capacity comes from
  equity rather than from permission, survivable leverage is near-independent of what the broker
  allows, and the account has a failure mode the unlevered wheel does not;
- **a fix to contribution 3**, whose "the equilibrium takes decades to approach, so the
  operator-relevant numbers are never the equilibrium ones" is exactly what II-11 reframes with
  T_sat. It must carry II-11's qualifier rather than the escape alone: the truncation helps only
  an account far below A\*, and in proportion to how little of the strategy it is running;
- **a decision on contribution 5**, headlined "**Two** stability boundaries, not one" against [the
  stability section](#sec:stability)'s three. II-12 has already decided the third belongs *beside*
  the other two rather than above them, since it alone does not bind an unlevered account, so the
  likely resolution is a qualifier and not a recount — but the headline cannot stand unexamined.
  The same sentence exists as a forward reference in [the inventory section](#sec:inventory)
  ("two boundaries instead of one"), which is II-12's to keep in sync.

Note that **I-4 is the other item on this same list** — it checks contributions 6 and 7 against
the finished Parts III and IV. Resolve both in one pass over §02, at assembly time, rather than
editing the list twice.

### Verification

**II-14 (extending `verify_examples.py`) was resolved on 2026-07-29**; the write-up is spread over
the II-4, II-5, II-6, II-7 and II-13 entries in [`DONE.md`](DONE.md). The standing discipline it
encodes does not close with it: every number a section quotes gets a check under that section's
heading, and INF-2 carries the same requirement into Parts III and IV.

**II-15 (the cash drawing rate) was resolved on 2026-07-29**; the write-up is in
[`DONE.md`](DONE.md). `Config.draw`, `debit_growth()` and a `g` argument on `liquidation_prob` and
`max_leverage`; a cash policy enters survival only as ν → ν − g, verified against a 400,000-path
Monte Carlo carrying the debit and the book as separate objects. The consequences are folded into
II-5, II-6 and II-12. The derivation it carried here for II-13 to lift has been lifted: [the
constrained section](sections/11-constrained.md) now owns it, under "What the operator does with
the cash".

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

  **Quantified 2026-07-29 (II-7), and the warning has a second half that is worse than the
  first.** The mistake is not only that demand is bursty *around* its mean: the mean itself is a
  near-singular function of two parameters nobody knows exactly. A\* runs **7.97 / 19.23 / 48.97
  / >126** across σ = 15/20/25/28% and diverges at 30%, a local elasticity of **3.5** rising to a
  4.2 secant by σ = 25% — a 1% relative error in the volatility estimate is a 3.5% error in the
  equity required, and the sensitivity worsens as volatility rises — while the dials the
  operator actually chooses (p\*, the cadence, n) move it proportionally and predictably. Sized
  for the running example and run on a σ = 25% stock, an account retains **39.3% throughput**.
  Both halves belong in this subsection: the distribution around the mean, and the fragility of
  the mean.
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
**One more joined the list on 2026-07-29:** II-7's (σ, μ) plane, where both stability boundaries
are curves rather than points and the band between them — lot count stationary, capital integral
divergent — is visible as an area. `sensitivity()` prints it as a text grid; it wants to be drawn.
