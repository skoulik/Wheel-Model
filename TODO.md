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
section](#sec:stability) has to be restructured. The parameters, the survival closed forms, the
capacity frontier and the constrained simulator (II-3, II-4, II-5, II-6) all landed 2026-07-29;
**only the sweep remains, and II-7 below questions whether it is still an item.** The prose can
start.

### Code

**II-3, II-4, II-5 and II-6 were resolved on 2026-07-29**; the write-ups are in [`DONE.md`](DONE.md),
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

**II-7. The sweep — and it may have nothing left to parallelize** (amended 2026-07-29). The brief
was a γ_s × A grid through `model.pmap()`. II-5 then showed that **γ_s, A and ε never touch the
depth walk**: one stationary solve (0.7 s) serves an entire frontier, and `frontier()` already
prints the γ_s × A × ε cells including the one where **A equals the model's own E[Capital]**
(A = 11.59: 60.3% throughput, T_sat 18.5y). A pool over that grid would parallelize arithmetic.
So decide what this item actually is: either it folds into II-5's report, or it becomes the sweep
that *does* need the pool — **σ, μ, p\* and the cadence**, each of which re-solves the walk and
none of which the frontier currently varies. The second is the more useful item and is what the
"sizing against the mean is the mistake" warning still wants quantified: how far A\* moves when
the stock is not the running example's. Diff parallel against `WHEEL_WORKERS=1` before quoting.

### Prose

**II-8. §00 notation.** γ_p, γ_s, A, u\*, L, the financing spread, f\*, T_sat, and the new
section's anchor. II-5 added five more that need symbols: **A\*** (the equity a wheel needs,
E[I(∞)]/L_max), **λ_eff** and the throughput retention λ_eff/λ, **g_max** and the maximum
sustainable draw. Carry the prose note that initial and maintenance requirements are deliberately
merged — and a second one, that capacity, the barrier and the financing ledger all exclude the
put collateral, which is 1.5% of a saturated account's capacity.

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
**ν > g**, the price's median growth outrunning the debt's. Write the three as one list — the
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
  account earns four times a cash account's income on the same equity. It earns 13% more.
  **Checked by II-6** (2026-07-29) and it needs no correction: E[W] in that denominator survives
  blocking to **+0.7%**, and inventory and income to +0.7% and +0.4%, measured against a simulated
  unconstrained control at the same horizon. The proportionality can be written as it stands;
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
  stopping rule is mandatory rather than prudent. **Simulated 2026-07-29, and the migration is not
  a one-way trip to a destination but a ratchet.** The account returns to its stopping rule after
  every recovery, because a price rise raises equity and the rule then permits another put, while
  a price fall merely blocks. So the barrier follows the price up and not down, and the closed
  form's de-levering — which is the whole of its comfort — never happens. That is why the live
  account is liquidated 3.6× as often as the frozen one at the *same* leverage, and it is the
  cleanest statement of what a static barrier gets wrong. **Also measured, and the destination
  itself is not the broker's ceiling.** The drift stops at the strategy's own demand, E[I(∞)]/A = **1.883**
  at A = 11.59 — the permitted 4.00 is unreachable because the wheel has nothing to buy with the
  money. The pairing to write is that at 1.883 the **excess return on equity reads higher, 3.15%
  against 1.68% unlevered, while the sustainable draw has gone to −2.14% of equity**: a demand for
  deposits. Return on paper and cash in hand move in opposite directions, and only one is
  spendable. That is also the answer to "why is the stopping rule mandatory" — not because the
  drifted state loses money on the page, but because it cannot be drawn on;
- the **capacity derivative** — capacity in lots is A/(γ_s·S) with A marked to market, so as S
  falls an unlevered account's capacity *rises* while a levered account's falls and crosses zero;
- the **selectively distorted census** — **measured 2026-07-29, and this bullet had the sign
  backwards**. The claim was that blocking removes arrivals during drawdowns, so constrained
  inventory is missing precisely the lots that would have been bought cheapest, and the book is
  therefore shallower. It is **deeper**: +5.3% on mean depth after saturation against a simulated
  unconstrained control at the same horizon (0.5174 against 0.4916), with the deepest bin's share
  up 3.8 points, and the effect washes out to −1% once the unblocked fill-up years are averaged
  in — so it is a saturated-regime statement. What blocking removes
  is the *newest* arrivals, and a new lot is a shallow lot; and for a near-unlevered account
  capacity in lots *rises* as the price falls, so blocking is if anything less likely during a
  drawdown, not more. Write the effect, the corrected sign, and the reason the intuition failed —
  it is a good illustration of the capacity derivative two bullets down;
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

**II-14. Extend `verify_examples.py`.** Its own section, on the standing discipline. Three of the
four are in, under the structural headings (II-4 and II-5, 2026-07-29): the **γ_s = 1.0
regression** — which must go on holding at every later step, not just today, and which II-5
widened to the unconstrained limit A = ∞ — the **T → ∞ collapse** of the finite-horizon first
passage onto f\*^θ, alongside the L_max round trip, the f\* = 1 recovery of the broker's ceiling
and the Q-world pair; and the **Q-world identity extended to the constrained case**, which holds
to within 1 bp: at m = r − δ with r_b = r, a blocked, levered wheel earns exactly r on equity less
the withholding leak, at every γ_s and every account size. Note what that last one does *not*
test: uniform thinning makes every rate invariant to A and γ_s by construction, so the
independence is structural and only the **level** is evidence. The version with teeth is the
simulator's, where blocking is real.

**The fourth landed with II-6 (2026-07-29), and this item is now complete.** A seeded 384-path
constrained run plus a 192-path unconstrained control, inside `verify_examples.py` at a cost of
2.2 s: the unconstrained limit (no put refused, no barrier reached), **T_sat** against
`time_to_inventory`, the **frozen barrier** against `liquidation_prob` to within 3 s.e. at every
horizon, and the live-versus-frozen correction pinned as a regression. Uniform thinning is
deliberately *not* pinned there — at the levered configuration the run needs, most paths are
liquidated inside it, so a census read off the survivors would be a survivorship artifact. It is
measured instead by `wheel_sim.py --scenario constrained` at the prudent configuration.

What remains for II-14 is only what §11 will need when it is written: **section-level** checks
against the prose, which is II-13's to specify.

**II-15 (the cash drawing rate) was resolved on 2026-07-29**; the write-up is in
[`DONE.md`](DONE.md). `Config.draw`, `debit_growth()` and a `g` argument on `liquidation_prob` and
`max_leverage`; a cash policy enters survival only as ν → ν − g, verified against a 400,000-path
Monte Carlo carrying the debit and the book as separate objects. The consequences are folded into
II-5, II-6 and II-12 below. What follows is the derivation, kept here only until §11 carries it.

<details><summary>Derivation, for II-13 to lift</summary>

**It enters as a shift in the drift, and every closed form of II-4 carries over unchanged.**
Liquidation is a statement about the ratio of debit to market value, R = D/M. With inventory pinned
at capacity, M moves only with the price, so ln M has drift ν and volatility σ; the debit compounds
at the borrowing rate and is fed by the net cash drain, so ln D has drift

    g  =  r_b + (draw − y)/D,

y being the strategy's cash income. Then ln R is a Brownian motion with drift **g − ν** and
volatility σ, started at ln(1 − 1/L) and absorbed at ln(1 − γ_s) — the same barrier, the same
distance a = −ln f\*, the same reflection formula. Only the exponent changes:

    θ_eff  =  2(ν − g) / σ².

So `first_passage_prob`, `liquidation_prob` and `max_leverage` need no new machinery at all; they
need ν − g where they currently read ν.

**What that immediately reveals — the current static barrier is a policy, not an assumption.**
g = 0 holds exactly when draw = y − r_b·D: the operator **services the interest and withdraws the
rest**. That is a perfectly sensible operating rule, and II-4's numbers are its numbers. Two
neighbours bracket it, and they are far apart:

- **Withdraw everything, interest included** (draw = y): g = r_b exactly, so ν_eff = ν − r_b =
  2.5% − 5% = **−2.5% < 0, and liquidation becomes certain at any leverage whatever.** The debt
  compounds at 5% while the price's median growth is 2.5%; it is a race the borrower loses. Only
  the dividend closes the gap, and a withdrawn dividend does not service a loan.
- **Retain everything** (draw = 0): at the running example's saturated account — capacity 13.15
  lots on A = 11.59, so a debit of **1.56** — the unconstrained 30-year income of **0.772/yr** is
  half the debit again, ν_eff is strongly positive and liquidation becomes negligible. (The
  *constrained* income is not that figure and is not a scaling of it: blocking cuts put premium
  while the larger inventory raises call premium and dividends. It is II-6's to produce, and this
  bullet's claim needs only the order of magnitude, which no plausible correction moves.)

  **Produced 2026-07-29**, and the caution was right and the order of magnitude held: constrained
  income runs **0.590/yr** against a thinned control's 0.647, a −8.7% correction rather than a
  scaling. Retention is indeed the safe policy — **0.35%** eventual liquidation against a *frozen*
  barrier's 0.92%, the only policy measured that comes out safer than the closed form.

So the survival of a levered wheel turns almost entirely on **whether income is retained to service
the debt** — a lever that is currently invisible in the model, and one an operator actually
controls, unlike γ_s. **Confirmed by simulation** (II-6): across the four cash policies, eventual
liquidation runs 0.35% / 1.11% / 3.95% / 8.64% while the frozen barrier reads 0.78–1.09% for all
four. The cash policy moves survival by a factor of twenty-five; the barrier formula does not see
it at all.

**Three further reasons it earns its place.** It gives II-12's third failure mode a criterion in
the same currency as the other two — lots return iff ν > 0, their capital returns iff m > σ², the
**account survives iff ν > g**. It makes `r_b` and `fin_spread` (added in II-3, so far declared and
unconsumed) do real work. And it converts the open question II-6 was left holding — which way the
debit drifts under blocked arrivals — from an unknown into a parameter, with the simulator
measuring where the linearization breaks rather than what the answer is.

**Costs, stated honestly.** g is constant only when the net drain is proportional to the debit,
which the two policies above satisfy *exactly* (g = 0 and g = r_b) and a fixed-dollar withdrawal
does not — for that it is a linearization around the current debit, and II-6 is the check. Income y
is likewise only steady once the account is saturated, which is the regime that matters but is not
the whole path. And the parameter invites "what is the optimal withdrawal rate", which is a control
problem the article does not want: it must be posed as **the maximum sustainable draw**, a
constraint, not an optimization.

**The default is g = 0** — the interest-servicing policy, derived — and not draw = 0, which is a
*different* policy and would have moved every current figure. Agreed 2026-07-29.

</details>

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
