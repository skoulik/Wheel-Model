# How Long a Lot Stays {#sec:holding}

A fresh lot has a 40% chance of leaving on its first call. The obvious next step is to multiply: if each four-week period is a coin weighted 0.40, a lot should last about 1/0.40 = 2.5 periods, call it ten weeks, and the operator can plan around that.

That reasoning is wrong, and it is wrong by a factor of eleven. This section computes the real answer.

## Why the obvious calculation fails

The 1/q rule assumes every period is the same coin. It is not. A lot that fails to exit has, by that very fact, usually drifted *deeper* — and at greater depth its next coin is worse. Failure makes failure more likely. The survivors are not a random sample of the original lots; they are the unlucky ones, selected for exactly the property that keeps them from leaving.

So the question "how long does a lot stay?" is not a question about a coin at all. It is a question about a wandering path: **when does the depth walk of [eq:depth-walk](#eq:depth-walk) first reach zero?** That is one of the classical questions of probability.

> **Detour: first-passage time.** Given a random walk, the **first-passage time** is the number of steps until it first reaches a specified level. It is a much subtler quantity than it looks. Even for a walk with a favourable drift, the first-passage time has a **heavy tail**: most paths arrive quickly, but a minority wander the wrong way and take enormously longer, and those rare paths dominate the average. The result is a distribution whose mean sits far above its median — the mean is not "the typical outcome" and using it as one is a standard way to be badly surprised. If the drift is unfavourable, the walk may never arrive at all, and the mean is infinite. [Ross's *Introduction to Probability Models*](#ref:ross-probability-models) treats first passage for random walks and Brownian motion.
>
> One detail of the version used here matters more than it sounds. The price moves continuously, but nobody *looks* except on the dates a call expires — so what is wanted is the first passage **as sampled on a schedule**, not the first moment the price touches the strike. Those are different quantities, and the second is not a good approximation to the first: the literature on discretely monitored barriers finds the gap closes only slowly as the observation dates are packed closer together, so that substituting the continuous answer can be badly wrong even at daily monitoring, let alone monthly ([Li and Linetsky](#ref:li-linetsky)). The rest of this section is about exactly how much that costs — it is the largest single correction in the article — and a reader who has met a knock-out note or an autocallable, which terminates on the first scheduled observation date that clears a fixed level, has already met the same object.

## Exits happen on a grid, and the grid is expensive

One complication has to go in before any numbers come out. The depth walk moves continuously, but a lot can only *leave* when a call expires. If the stock rallies through the strike midway through the four-week call and slips back before expiry, nothing happens: the call finishes out of the money, the lot stays, and the visit is wasted.

The cost of this is not small, and it has a known size. For a walk sampled at discrete times, the effective barrier sits deeper than the true one by

β · σ·√τ_c ,   β = −ζ(1/2)/√(2π) ≈ 0.5826    {#eq:siegmund}

a classical correction. What β measures is an **expected overshoot**: how far past a level a walk typically stands at the first moment anyone looks, in units of one period's step. The grid does not merely delay a lot's exit, it records the exit late — a barrier crossed between two expiries behaves as though it had been sitting 0.58 steps deeper all along.

Nobody knew that when the number was first computed, which is the more interesting half of its history. It appears in [Chernoff (1965)](#ref:chernoff-1965), where the problem is not a barrier at all but when to stop a sequential experiment that can only be inspected at fixed times, and where it arrives as a definite integral — one that Gordon Latta recognised as −ζ(1/2)/√(2π). That it *measures an overshoot* was established twenty-one years later. [Siegmund](#ref:siegmund-1979) built on it the diffusion approximation this section uses below; [Chang & Peres](#ref:chang-peres-1997) supplied the expansion its digits and its limitations come from; and the use being made of it here — take a formula for a continuously watched barrier, shift the barrier, and price something that is only watched on a schedule — is [Broadie, Glasserman & Kou](#ref:broadie-glasserman-kou-1997)'s, whose discretely monitored knock-out option is a wheel lot with the call strike as the barrier. (A reader who opens Chernoff will find −0.5824 printed beside the integral. Evaluating the integral gives −0.5826, so that is a slip in his arithmetic and not a second constant.)

One caveat about β, and it cuts against the operator rather than for them. 0.5826 is the overshoot for a barrier *infinitely far away*, and a fresh lot is not far from its barrier at all: it sits

E[x₀] / (σ·√τ_c)  =  **0.28** of one period's step

below its own call strike — near enough that β's limiting value has barely begun to apply. At such short range the overshoot is larger. How much larger is settled by **Wald's identity**, which is exact rather than approximate: a lot's mean life is the hole it has to climb divided by the rate the drift fills it,

E[W]  =  ( E[x₀] + E[overshoot] ) / ν .

Run that backwards from the exact 2.10 years computed below, and the overshoot the model is really paying is **0.667** steps, not 0.583. So the **call-grid tax** at the running parameters is 0.667 × 0.20 × √(1/13) = **0.037** — which is **2.4 times the typical entry depth of 0.0155**. Read off β alone it would have been 2.1, and β understates the very thing it is there to measure.[^eq-siegmund]

Read that again, because it reorders the intuition completely. The hole a lot has to climb out of is not mainly the 1.6% it fell through at assignment. It is mostly the *sampling* — the requirement that the recovery be standing on the right day, once every four weeks. Of the total hole, roughly **30% is the entry and 70% is the grid**. **The exit grid, not the entry overshoot, is what keeps lots in inventory.** An operator worried about being assigned too deep is worrying about less than a third of the problem.

The ratio is worth a second look, because it is the one quantity here that does not depend on how the clocks are set in absolute terms. Both the tax and the entry depth scale with volatility and with the square root of a period, so their ratio is governed by n = τ_c/τ_p — roughly √n. Selling calls on a slower clock than the puts is what creates the tax, and there is no cadence at which it goes away: as long as calls run longer than puts, the grid costs more than the entry. The 0.28 above moves the same way, as 1/√n, so the faster the calls outrun the puts the further inside β's limit the strategy operates: the lever that makes the tax matter is the one that makes the textbook constant least appropriate for measuring it.

The tax is also directly visible in a real book, which is reassuring for a correction that arrives here as pure theory. Tracking the live account's inventory day by day, **a fifth of all the time its lots spent in inventory was spent above their own call strikes** — shares that had already recovered past the price they would be sold at, sitting there only because the call had not expired yet. That is the grid, in the flesh: not a subtlety of the mathematics but a stack of positions waiting for a date on the calendar.

## The survival curve

Write S_j for the probability that a lot is still held after j call periods:

S_j  =  P( J > j )  =  P( x₁ > 0, x₂ > 0, …, x_j > 0 )    {#eq:survival}

Each x is the running depth from [eq:depth-walk](#eq:depth-walk), started from an entry depth drawn from [eq:x0-law](#eq:x0-law). There is no closed form, but the sequence is easy to compute exactly: the chance of surviving one more period, from wherever the walk currently is, is a Gaussian integral over the surviving region, and applying that step repeatedly gives the whole sequence. (`code/model.py` does this on a grid in x. The grid needs care: representing the depth in cells effectively places the exit boundary half a cell too deep, which holds lots marginally too long, so the long-run figures below are computed at two resolutions and extrapolated. [The verification section](#sec:verification) checks the result against a simulation of the same walk that uses no grid at all.)

For the Standard regime, tabulated in call periods — every column is an exact multiple of the four-week call, and thirteen of them make a year:

    still held after     4 wk    8 wk   12 wk   24 wk     1 y     2 y     5 y    10 y    20 y
    probability          0.60    0.46    0.38    0.27    0.18    0.12    0.07    0.04    0.02

and the mean of the whole distribution is

E[W]  =  τ_c · E[J]  =  τ_c · Σ_j S_j  =  **2.10 years**    {#eq:holding}

against a **median of eight weeks** — the column where survival first drops below a half. The distribution is exactly as advertised: most lots are handled quickly, a minority never really are, and the mean belongs to the minority. One lot in fifteen is still held after five years; one in twenty-five after ten; one in forty-six after twenty.

Nothing in the model was set up to produce this. There are no separate populations, no mixture of "good" and "bad" lots, no regime switch. A single random walk with a single drift, sampled every four weeks, generates a fast lane, a slow middle, and a tail measured in decades — because that is what first-passage times *are*.

The ratio of mean to median is the number to carry away: **two years against eight weeks, a factor of thirteen**. It is larger here than it would be on a slower call clock, because a fine grid resolves the fast lane — a lucky lot can leave after four weeks rather than waiting a quarter for its chance — while doing nothing at all for the deep tail, which is governed by the drift and not by the sampling.

This is also the point at which a track record will mislead its owner, and the live account shows how. An operator who averages the holding times of the lots that have *finished* is not measuring this distribution; they are measuring the fast lane, because the slow lots are by construction still on the books and have not produced a number yet. Correcting the live account for that — the standard survival-analysis adjustment for observations that are still running — **lengthens its apparent median holding time by more than half**. The mean is worse still, and cannot be estimated at all from fifteen months, since the tail that carries it is measured in decades. Any statistic computed over closed positions inherits this bias.

Siegmund's correction also gives a usable closed form. Treating the entry depth as a hole of size E[x₀] deepened by the grid tax, and dividing by the rate at which drift works it off,

E[W]  ≈  ( E[x₀] + β·σ·√τ_c ) / ν  =  (0.0155 + 0.0323) / 0.025  =  **1.9 years**    {#eq:holding-siegmund}

which lands 9% below the exact 2.10 and is the right formula to reason with. Every term is legible: the hole, the grid tax, and the drift that has to fill it. It also makes plain why the answer is so large — the numerator is dominated by a term that has nothing to do with how deep the assignment was, and the denominator is the small difference of three quantities of similar size.

The 9% is not slack in the reasoning; it is β again, and it can be bounded on both sides. Wald's identity above is exact, so the only thing standing between this formula and the truth is which overshoot goes into it — and the two ends of the range are both published constants. Taking β corrected for the period's drift, the far-barrier end, gives **1.93 years**; taking the mean first ladder height, which is the overshoot of a barrier the walk starts *on* and so the opposite extreme, gives **2.22 years**. The exact 2.10 lies between them, as it has to. A reader who wants one number should use this formula and expect it to run a little light; a reader who wants to know how light now has both bounds.

Under the market's pricing drift, where ν = 0.5%, the same computation gives **E[W] ≈ 9 years** — more than four times the real-world figure, from a drift five times smaller. The option market prices this stock as one whose lots, once acquired, are effectively permanent. (Round figures are the honest ones here: with a drift that small the mean is carried by the far tail, and the third significant digit is a property of the numerics rather than of the strategy.)

## When lots never leave

Everything above assumed ν > 0. If the drift is unfavourable — ν ≤ 0 — the walk still reaches zero *sometimes*, but not always, and a definite fraction of lots wander up and never come back. That fraction has a closed form: averaging the escape probability of a drifting walk over the entry law, and applying the same grid correction,

P( J = ∞ )  =  1 − E[ exp( −2|ν|·(x₀ + β·σ·√τ_c) / σ² ) ]    {#eq:trapped}

At σ = 40% with the same μ and δ, ν = −3.5%, and this comes to 4.1%. But it carries β, so it inherits β's problem, and in the same direction as before: run the walk itself, with no constant standing in for anything, and the answer is **4.4% of every assignment permanently trapped**. Not delayed — trapped, with no mechanism in the strategy that will ever release them. The rest of the inventory keeps recycling around them while the trapped stratum grows by λ × 4.4% ≈ 0.46 lots a year, without bound. The per-assignment fraction is *smaller* than it would be on a slower call clock — a finer grid gives a doomed lot more chances to slip out early — but the arrival rate is more than four times higher, which more than undoes it. Selling more often traps a smaller share of more lots, and the arithmetic favours the arrivals.[^eq-trapped]

The closed form remains the one to reason with, because it shows that only two things govern the answer — the depth a lot enters at, and the tax sitting on top of it — but it should be read knowing which way it errs. It runs about 8% low here, and it is worst precisely where an operator would go to escape the problem. Write the puts so far out of the money that assignment lands at no depth at all, and the formula reads 2.8% where the truth is **3.4%**: short by nearly a fifth, in the regime chosen for safety. That last figure is one of the few numbers in this article known exactly rather than computed — it has a closed form, due to [Janssen & van Leeuwaarden](#ref:janssen-vanleeuwaarden-2007), and the walk above is checked against it.

This is the first appearance of something the model will keep saying in different ways: the wheel does not fail by losing money on trades. It fails by accumulating positions that never resolve. [The stability section](#sec:stability) makes the boundary precise.

## What this section changed

The naive 1/q calculation said ten weeks. The correct answer is a median of eight weeks and a mean of two years — and the gap between those two numbers is not a technicality, because capital is committed for the *mean*, not the median. Every lot that leaves quickly frees its capital quickly; the operator's balance sheet is dominated by the ones that don't.

Turning "a mean holding time of 2.10 years" into "how much stock am I holding and what does it cost me" takes one more step, and it is a famous one. That is [the inventory section](#sec:inventory).

[^eq-siegmund]: Reproduced by `python code/examples/holding_time.py` — [eq:siegmund](#eq:siegmund), [eq:survival](#eq:survival), [eq:holding](#eq:holding), [eq:holding-siegmund](#eq:holding-siegmund), and the other readings quoted here are `measure Q`. Pass `--help` for the full parameter set.

[^eq-trapped]: Reproduced by `python code/examples/holding_trapped.py` — [eq:trapped](#eq:trapped), and the other readings quoted here are `sigma 0.40`. Pass `--help` for the full parameter set.
