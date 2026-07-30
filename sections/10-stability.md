# Stability: Two Ways to Be Buried {#sec:stability}

The wheel never stops selling puts. Lots arrive whatever else is happening, and they leave only when the market comes back to fetch them. So the question that decides whether the strategy is operable at all is whether the warehouse stays finite — and it turns out there are two separate ways for the answer to be no, with two different boundaries, and the stricter one is not the one people worry about.

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

In volatility terms the capital boundary sits at **σ < 21.2%** — against 30% for the lot count. The two are far apart, and the running example lives between them in an uncomfortable way:

| | condition | boundary in σ | boundary in δ | Standard regime |
|---|---|---|---|---|
| lots come back | μ − δ > σ²/2 | σ < 30.0% | δ < 5.0% | ✔ comfortable |
| capital comes back | μ − δ > σ² | σ < 21.2% | δ < 3.0% | ✔ **by 1.2 points** |

At σ = 20% and δ = 2.5%, the strategy clears the capital boundary by 1.2 volatility points, or half a point of dividend yield. A quality name at 22% volatility, or the same name raising its payout to 3.5%, is on the other side — where lots still recycle, one by one, but the expected capital tied up in them does not converge.

Between the two boundaries lies a regime worth naming, because it is genuinely counterintuitive: **every lot comes back, and the capital still runs away.** Inventory is finite, each individual position resolves eventually, nothing looks broken from the inside — and expected capital is unbounded, because the rare very deep lots cost exponentially more than the common shallow ones. An operator in this band who reasons "every position I have ever held has eventually recycled" is stating something true and irrelevant.

## What the option market thinks

Now run the same two tests under the market's pricing drift, m = r − δ = 2.5%, which by [the entry section](#sec:entry) is a full reading of the model rather than a different model:

| | real world (m = 4.5%) | the market's prices (m = 2.5%) |
|---|---|---|
| ν | +2.5% | +0.5% |
| tail exponent θ | 1.25 | **0.25** |
| lots come back | ✔ | ✔ barely |
| capital comes back | ✔ barely | ✘ **fails** |
| mean holding time | 2.1 years | ≈ 9 years |
| equilibrium lots | 21.8 | ≈ 94 |

**The option market prices this stock as one whose wheel inventory never clears.** Under the measure that sets the premiums the operator collects, holding times run to nine years, equilibrium inventory approaches a hundred lots, and expected capital is infinite.

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

The effect compounds: everything downstream depends on ν, ν is a difference of quantities of similar size, and stress attacks every term in it simultaneously. A configuration calibrated comfortably inside both boundaries in calm markets can be outside both in a quarter, and the transition is not gradual — [eq:trapped](#eq:trapped) turns on as soon as ν changes sign.

## Summary

The wheel has two failure modes, and neither is "losing money on a trade":

1. **ν ≤ 0** — lots stop coming back, and a fixed fraction of every year's assignments is trapped permanently.
2. **m ≤ σ²** — lots come back but the capital in them does not converge, so the strategy's demands grow without bound even while every individual position eventually resolves.

The second boundary is the tighter one and the less intuitive one, and at the article's own running parameters it is 1.2 volatility points away. Whether an operator is inside it is not a matter of temperament or conviction about the company; it is arithmetic on three numbers.

[^eq-basis-multiplier]: Reproduced by `python code/examples/stability_basis.py` — [eq:basis-multiplier](#eq:basis-multiplier), [eq:theta](#eq:theta), and the other readings quoted here are `measure Q`; `sigma 0.212`. Pass `--help` for the full parameter set.

[^eq-count-criterion]: Reproduced by `python code/examples/stability_criteria.py` — [eq:count-criterion](#eq:count-criterion), [eq:capital-criterion](#eq:capital-criterion), and the other readings quoted here are `measure Q`; `sigma 0.30`; `sigma 0.212`; `delta 0.05`. Pass `--help` for the full parameter set.
