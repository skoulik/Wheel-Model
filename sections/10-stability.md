# Stability: Two Ways to Be Buried, and a Third if You Borrow {#sec:stability}

The wheel never stops selling puts. Lots arrive whatever else is happening, and they leave only when the market comes back to fetch them. So the question that decides whether the strategy is operable at all is whether the warehouse stays finite — and it turns out there are two separate ways for the answer to be no, with two different boundaries, and the stricter one is not the one people worry about.

Both of those are properties of the stock. An operator who borrows to hold the warehouse acquires a third that is a property of themselves, and it is the only one of the three that is fast.

## The first boundary: do lots come back?

By [the holding-time section](#sec:holding), a lot leaves when its depth walk first reaches zero. A walk drifting downward gets there eventually with certainty; a walk drifting upward may never get there at all. The condition is simply that the drift points the right way:

**ν  =  μ − δ − σ²/2  >  0**    {#eq:count-criterion}

Above the line, every lot eventually comes back, mean holding time is finite, and Little's law returns a finite inventory. Below it, a fixed fraction of every year's assignments — [eq:trapped](#eq:trapped) — never returns. Those lots accumulate at a constant rate, forever, and no amount of patience recovers them. The failure is not that returns are poor; it is that the strategy has an absorbing state and keeps feeding it.[^eq-count-criterion]

Rearranged, this is a statement about volatility: the wheel needs **μ − δ > σ²/2**. At μ = 7% and δ = 2.5%, that means σ below **30%**.

## The second boundary: does the capital come back?

Counting lots is not counting money, as [the inventory section](#sec:inventory) warned. A lot's cost basis, measured against today's price, is e^x — exponential in depth. So even where the *number* of trapped lots is finite, the capital they represent need not be.

Follow one surviving lot for a call period. Its depth moves by −ν·τ_c + σ·√τ_c·Z, so its basis-to-price ratio is multiplied by e^(−ν·τ_c + σ·√τ_c·Z), whose expectation is

E[ multiplier ]  =  e^( (σ² − m) · τ_c )    {#eq:basis-multiplier}

The lot's relative basis shrinks in expectation only if σ² < m. Equivalently — and this is the version worth remembering — the operator's capital is denominated in shares while their commitment is denominated in dollars paid, so what has to decay is E[1/S]. For a lognormal price that decays exactly when[^eq-basis-multiplier]

**m  =  μ − δ  >  σ²**    {#eq:capital-criterion}

The same condition appears from the other end. The depth census of [eq:census](#eq:census) has an exponentially decaying tail, ρ(x) ~ e^(−θ·x), with

θ  =  2ν / σ²    {#eq:theta}

and capital integrates e^x against that census. The integral converges only if θ > 1 — which is [eq:capital-criterion](#eq:capital-criterion) again. The tail exponent is the single most informative number about a configuration of this strategy: it says how fast the deep strata thin out, and whether the money in them is bounded.

Seen through [the inventory section](#sec:inventory)'s generalised law, the two boundaries stop being two unrelated convergence questions and become one. H = λG needs a finite arrival rate and a finite per-lot total G, and [Whitt's](#ref:whitt-1991) statement of it is an equivalence, so each boundary is one of those requirements failing:

- **lots return if and only if W is finite** — the weighting f = 1, which is the count;
- **their capital returns if and only if G is finite at f = e^x** — the same law, weighted by what a lot actually ties up.

Below the first boundary the holding times themselves diverge and the count goes with them. Between the two, the count law survives intact and it is the *weighted* total that runs away. So this section is not a separate stability theory bolted onto the inventory section; it is the failure analysis of the identity that section is built on, and the strategy has exactly as many boundaries as that identity has hypotheses.

In volatility terms the capital boundary sits at **σ < 21.2%** — against 30% for the lot count. The two are far apart, and the running example lives between them in an uncomfortable way:

| | condition | boundary in σ | boundary in δ | Standard regime |
|---|---|---|---|---|
| lots come back | μ − δ > σ²/2 | σ < 30.0% | δ < 5.0% | ✔ comfortable |
| capital comes back | μ − δ > σ² | σ < 21.2% | δ < 3.0% | ✔ **by 1.2 points** |

At σ = 20% and δ = 2.5%, the strategy clears the capital boundary by 1.2 volatility points, or half a point of dividend yield. A quality name at 22% volatility, or the same name raising its payout to 3.5%, is on the other side — where lots still recycle, one by one, but the expected capital tied up in them does not converge.

Between the two boundaries lies a regime worth naming, because it is genuinely counterintuitive: **every lot comes back, and the capital still runs away.** Inventory is finite, each individual position resolves eventually, nothing looks broken from the inside — and expected capital is unbounded, because the rare very deep lots cost exponentially more than the common shallow ones. An operator in this band who reasons "every position I have ever held has eventually recycled" is stating something true and irrelevant.

### What the divergence looks like to someone with a balance

Unbounded expected capital is a statement about an operator with unlimited money, and no real account has any. [The constrained section](#sec:constrained) gives capacity a ceiling set by the account's equity, and a put whose assignment would breach it is not sold. Nothing can then diverge: the account holds what it can pay for and refuses the rest.

So past the capital boundary what runs away is not the capital committed but the capital *demanded* — A\*, the equity at which the ceiling stops binding — and what shrinks is the fraction of the strategy the account manages to run. Reading that fraction for an account sized at the running example's own A\* of 19.23 share prices, and moving the stock underneath it:

| σ | where it sits | A\* | share of the strategy that account runs |
|---|---|---|---|
| 20.0% | inside both | 19.23 | 100% |
| 21.2% | *on* the capital boundary | 23.69 | 81% |
| 25.0% | past it | 48.97 | 39% |
| 30.0% | on the count boundary | infinite | 0% |

The crossing is not a cliff. At the capital boundary itself the account is still running four fifths of the wheel, and the fraction reaches zero only at the *first* boundary, where holding time itself is infinite. What the second boundary marks is where the equity required begins to move much faster than the stock does: 25% volatility is not a different asset class from 21%, and it asks for more than twice the money.

And note what that failure mode looks like from the inside: **no margin call, no loss, nothing a statement would show.** An account past the capital boundary holds a handful of deep lots, sells a put only when one of them finally leaves, and has quietly stopped being a wheel while every position in it still resolves exactly as promised.

## The third boundary: does the account outrun its own debt?

Neither boundary so far moves when the operator buys the stock on borrowed money. [eq:count-criterion](#eq:count-criterion) is a statement about the drift of a random walk and [eq:capital-criterion](#eq:capital-criterion) one about E[1/S]; financing changes who paid for the shares, not how the price moves. What borrowing adds is a boundary of its own, and it is derived in [the constrained section](#sec:constrained) by the same first-passage argument as everything else here.

Its two ingredients are a race. A book carried on a debit is sold out when the debit rises to a fixed fraction of what the book is worth at market; the market value moves with the price, whose median grows at ν; and the debit grows at a rate the operator sets by deciding what to do with the income — call it g, defined in [eq:debit-growth](#eq:debit-growth). The ratio of the two is one more drifting walk against one more barrier, and it drifts away from that barrier rather than toward it only if

**ν  >  g**    {#eq:account-criterion}

Three things about it earn it a place beside the other two rather than above them.[^eq-account-criterion]

**It is the only one of the three that spares an unlevered account.** An operator who borrows nothing has no debit, no barrier, and no exposure to this boundary whatever the stock does. That is the whole reason it is third rather than first: the other two bind everybody.

**It is the only one of the three the operator can move.** ν belongs to the stock, and all an operator can do about it is own something else. g is a cash policy, revisited every time income arrives, and it moves survival by a factor of twenty-five: measured over the thirty years after an account fills up, retaining all income gets **0.35%** of accounts sold out, and withdrawing the income while the interest accrues gets **8.64%** — on identical stocks, at identical leverage, on the same price paths. Retained income repays the debit and de-levers the account; withdrawn income leaves the interest compounding against a price whose median grows at 2.5% while the loan costs 5%. [The constrained section](#sec:constrained) has all four policies and the mechanism in full.

**And it is the fast one.** The other two can be crossed for years before an operator notices, because all they withhold is recoveries that were never on a schedule to begin with. This one ends the account on a particular morning, at a price someone else chose, and the recovery that follows is no use because the shares are gone.

One caution about the arithmetic, which the same section carries in full. The closed form pins the withdraw-everything policy at g = r_b = 5%, which would cross ν = 2.5% by a clean factor of two; simulated, the rate that policy actually realizes is **+1.3%**, because withdrawing the income shrinks the account faster than the interest compounds the debit. So the boundary is crossed by rather less than the closed form advertises, and it is crossed nonetheless. The criterion is ν > g, and the evidence for it is the ranking of the policies, not any nominal rate.

(The two liquidation figures are from `python code/wheel_sim.py --scenario constrained --paths 4000`, at a fixed seed.)

## What the option market thinks

Now run both of the stock's own tests under the market's pricing drift, m = r − δ = 2.5%, which by [the entry section](#sec:entry) is a full reading of the model rather than a different model:

| | real world (m = 4.5%) | the market's prices (m = 2.5%) |
|---|---|---|
| ν | +2.5% | +0.5% |
| tail exponent θ | 1.25 | **0.25** |
| lots come back | ✔ | ✔ barely |
| capital comes back | ✔ barely | ✘ **fails** |
| mean holding time | 2.1 years | ≈ 9 years |
| equilibrium lots | 21.8 | ≈ 94 |

**The option market prices this stock as one whose wheel inventory never clears.** Under the measure that sets the premiums the operator collects, holding times run to nine years, equilibrium inventory approaches a hundred lots, and expected capital is infinite. The third boundary tightens in step, since ν is the ceiling on g: the room a levered operator has to take cash out of the account falls from 2.5% a year to half a point.

This is the sharpest statement in the article, and it is not a paradox. Risk-neutral pricing is what the market charges to bear risk; it deliberately assumes away the compensation for holding equities. Reading the wheel in that measure therefore shows the strategy stripped of its only real engine — and what remains does not clear. **The entire difference between a wheel that recycles in two years and one that never recycles is the equity risk premium μ − r = 2%.** The strategy is not an income machine that happens to hold stock. It is a leveraged bet that stocks go up, wearing the costume of an income machine, and its stability rests on the same assumption its returns do.

## The ratchet: crash, then flatline

Boundaries describe steady states. The way real portfolios get into trouble is a transition, and one shape of transition is far worse than the others.

A geometric decline — the stock falling by the same percentage repeatedly — is the *benign* case, which is worth knowing because it is the one that sounds most alarming. Each successive assignment happens at a lower price, so each new lot's basis is a fixed fraction of the last, and the total cost basis of infinitely many lots converges like a geometric series. Falling markets, by themselves, do not bury the strategy; they buy inventory ever more cheaply.

What buries it is falling and then *stopping*. Simulating a crash (a quarter with an expected 30% log-drop at 35% volatility) followed by three years of flat market at μ = 0, then a return to calm:

    year                     1.0    2.0   2.25    3.0    4.0    5.0    6.0    8.0   10.0
    lots held               3.23   5.12   7.04   9.63  11.51  12.39  13.13  12.89  12.68
    capital, market value   3.42   5.30   7.23   9.83  11.71  12.58  13.33  13.08  12.88
    capital, cost basis     3.74   6.02  11.04  14.16  17.64  19.55  21.12  21.49  21.37
    paper loss (the gap)    0.32   0.72   3.80   4.33   5.94   6.97   7.79   8.41   8.49

Two things happen, and on a weekly cadence the first is no longer negligible. Through the crash quarter itself inventory rises from 5.1 to 7.0 lots: thirteen puts are sold into a falling market in the space of that quarter, where an operator selling monthly would have written three.

Market-value capital rises with the lot count, 5.3 to 7.2, and it can do nothing else — at market a share is worth a share however far it has fallen, so Track B counts lots and only lots. What nearly doubles is the *cost basis*, 6.0 to 11.0. The difference between the two rows is the accumulated paper loss on standing inventory, as [the returns section](#sec:returns) named it, and it is the one quantity in the table that behaves violently: **more than fivefold in a single quarter, 0.7 to 3.8.** That is the crash's real signature. It is not capital newly committed; it is capital already committed and now under water. And it does not come back with the market: between years 6 and 10 the lot count *falls*, 13.1 to 12.7, while the paper loss goes on *rising*, 7.8 to 8.5.

But the larger damage is still the flatline that follows. With μ = 0 the drift becomes ν = −4.5%, deep in the unstable region on *both* criteria, and the warehouse simply fills: lots keep arriving at 10.4 a year and essentially none leave. Inventory **more than doubles again** from its pre-crash level over the next four years, and then four *further* years of restored, healthy drift claw back barely a tenth of the peak.

(Those figures come from 300 simulated paths at a fixed seed: `python code/wheel_sim.py --scenario stress --paths 300`.)

That asymmetry — filled in three years, drained in decades — is the ratchet, and it follows directly from the transient of [the inventory section](#sec:inventory). Accumulation happens at the arrival rate, which is fast and constant. Release happens at the first-passage rate, which is slow and gets slower with depth. Through the flatline the warehouse gains about 1.6 lots a year; once healthy drift returns it sheds about 0.35. A strategy whose inventory fills four to five times faster than it drains does not mean-revert in any sense an operator would recognize.

## Reflexivity: the parameters move together

One last reason the boundaries are closer than they look. The model treats μ, σ and δ as constants. In stress they move, they move at the same time, and every one of them moves the wrong way.

- **Volatility rises in falling markets** — reliably, and by a lot. Since it enters ν quadratically and enters both criteria, a move from 20% to 30% is enough to cross both boundaries at once.
- **Rising volatility widens the strikes** the operator sells at a fixed p\*, which sounds protective, but the assignments that do occur land deeper.
- **Dividend cuts** arrive in exactly the same conditions, and δ falling helps ν — but a cut usually signals a fall in μ that more than offsets it.
- **The operator's own μ estimate** is at its least reliable precisely when it matters most, since the "fundamentally sound" judgment that justifies μ > 0 is being tested by the same event.

The effect compounds: everything downstream depends on ν, ν is a difference of quantities of similar size, and stress attacks every term in it simultaneously. A configuration calibrated comfortably inside both of the stock's boundaries in calm markets can be outside both in a quarter, and the transition is not gradual — [eq:trapped](#eq:trapped) turns on as soon as ν changes sign. The borrower's boundary goes the same way and for the same reason, since ν is one side of it too: the cash policy that was survivable at 20% volatility need not be at 30%, and nothing about the policy has changed.

## Summary

The wheel has three failure modes. The first two are slow, silent, and are not "losing money on a trade":

1. **ν ≤ 0** — lots stop coming back, and a fixed fraction of every year's assignments is trapped permanently.
2. **m ≤ σ²** — lots come back but the capital in them does not converge, so the strategy's demands grow without bound even while every individual position eventually resolves. Inside a finite account nothing can diverge, and the same crossing appears instead as the equity the strategy demands running away from the equity the account has, with the share of the strategy it manages to run decaying behind it.
3. **ν ≤ g** — the debit outgrows the price and someone else closes the account. This one *is* losing money on a trade, and it is the fast one; it is also the only one an unlevered operator is exempt from, and the only one any operator can move.

Of the two that bind everybody, the second is the tighter and the less intuitive, and at the article's own running parameters it is 1.2 volatility points away. Whether an operator is inside it is not a matter of temperament or conviction about the company; it is arithmetic on three numbers. Whether they are inside the third is not arithmetic on the stock at all — it is arithmetic on what they do with the cash.

[^eq-account-criterion]: Reproduced by `python code/examples/stability_criteria.py` — [eq:account-criterion](#eq:account-criterion), and the other readings quoted here are `g 0.05`; `g 0.025`. Pass `--help` for the full parameter set.

[^eq-basis-multiplier]: Reproduced by `python code/examples/stability_basis.py` — [eq:basis-multiplier](#eq:basis-multiplier), [eq:theta](#eq:theta), and the other readings quoted here are `measure Q`; `sigma 0.212`. Pass `--help` for the full parameter set.

[^eq-count-criterion]: Reproduced by `python code/examples/stability_criteria.py` — [eq:count-criterion](#eq:count-criterion), [eq:capital-criterion](#eq:capital-criterion), and the other readings quoted here are `measure Q`; `sigma 0.30`; `sigma 0.212`; `delta 0.05`. Pass `--help` for the full parameter set.
