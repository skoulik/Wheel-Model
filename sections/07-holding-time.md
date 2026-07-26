# How Long a Lot Stays {#sec:holding}

A fresh lot has a 40% chance of leaving on its first call. The obvious next step is to multiply: if each quarter is a coin weighted 0.40, a lot should last about 1/0.40 = 2.5 quarters, call it seven and a half months, and the operator can plan around that.

That reasoning is wrong, and it is wrong by a factor of six. This section computes the real answer.

## Why the obvious calculation fails

The 1/q rule assumes every period is the same coin. It is not. A lot that fails to exit has, by that very fact, usually drifted *deeper* — and at greater depth its next coin is worse. Failure makes failure more likely. The survivors are not a random sample of the original lots; they are the unlucky ones, selected for exactly the property that keeps them from leaving.

So the question "how long does a lot stay?" is not a question about a coin at all. It is a question about a wandering path: **when does the depth walk of [eq:depth-walk](#eq:depth-walk) first reach zero?** That is one of the classical questions of probability.

> **Detour: first-passage time.** Given a random walk, the **first-passage time** is the number of steps until it first reaches a specified level. It is a much subtler quantity than it looks. Even for a walk with a favourable drift, the first-passage time has a **heavy tail**: most paths arrive quickly, but a minority wander the wrong way and take enormously longer, and those rare paths dominate the average. The result is a distribution whose mean sits far above its median — the mean is not "the typical outcome" and using it as one is a standard way to be badly surprised. If the drift is unfavourable, the walk may never arrive at all, and the mean is infinite. Ross's *Introduction to Probability Models* treats first passage for random walks and Brownian motion.

## Exits happen on a grid, and the grid is expensive

One complication has to go in before any numbers come out. The depth walk moves continuously, but a lot can only *leave* when a call expires. If the stock rallies through the strike in the middle of a quarter and slips back before expiry, nothing happens: the call finishes out of the money, the lot stays, and the visit is wasted.

The cost of this is not small, and it has a known size. For a walk sampled at discrete times, the effective barrier sits deeper than the true one by

β · σ·√τ_c ,   β = −ζ(1/2)/√(2π) ≈ 0.5826    {#eq:siegmund}

a classical correction due to Siegmund. At the running parameters this **call-grid tax** is 0.5826 × 0.20 × √0.25 = **0.058** — which is **1.8 times the typical entry depth of 0.032**.

Read that again, because it reorders the intuition completely. The hole a lot has to climb out of is not mainly the 3.2% it fell through at assignment. It is mostly the *sampling* — the requirement that the recovery be standing on the right day, once a quarter. **The exit grid, not the entry overshoot, is what keeps lots in inventory.** An operator worried about being assigned too deep is worrying about the smaller half of the problem.

## The survival curve

Write S_j for the probability that a lot is still held after j call periods:

S_j  =  P( J > j )  =  P( x₁ > 0, x₂ > 0, …, x_j > 0 )    {#eq:survival}

Each x is the running depth from [eq:depth-walk](#eq:depth-walk), started from an entry depth drawn from [eq:x0-law](#eq:x0-law). There is no closed form, but the sequence is easy to compute exactly: the chance of surviving one more period, from wherever the walk currently is, is a Gaussian integral over the surviving region, and applying that step repeatedly gives S_j to any accuracy wanted. (`code/model.py` does this on a grid in x; [the verification section](#sec:verification) checks it against two independent simulations.)

For the Standard regime:

    still held after     3 mo    6 mo     1 y     2 y     3 y     5 y    10 y    20 y
    probability          0.60    0.46    0.33    0.22    0.18    0.13    0.08    0.04

and the mean of the whole distribution is

E[W]  =  τ_c · E[J]  =  τ_c · Σ_j S_j  =  **4.18 years**    {#eq:holding}

against a **median of six months**. The distribution is exactly as advertised: most lots are handled quickly, a minority never really are, and the mean belongs to the minority. One lot in eight is still held after five years; one in thirteen after ten; one in twenty-four after twenty.

Nothing in the model was set up to produce this. There are no separate populations, no mixture of "good" and "bad" lots, no regime switch. A single random walk with a single drift, sampled quarterly, generates a fast lane, a slow middle, and a tail measured in decades — because that is what first-passage times *are*.

Siegmund's correction also gives a usable closed form. Treating the entry depth as a hole of size E[x₀] deepened by the grid tax, and dividing by the rate at which drift works it off,

E[W]  ≈  ( E[x₀] + β·σ·√τ_c ) / ν  =  (0.032 + 0.058) / 0.025  =  **3.6 years**

which lands 13% below the exact 4.18 and is the right formula to reason with. Every term is legible: the hole, the grid tax, and the drift that has to fill it. It also makes plain why the answer is so large — the numerator is dominated by a term that has nothing to do with how deep the assignment was, and the denominator is the small difference of three quantities of similar size.

Under the market's pricing drift, where ν = 0.5%, the same computation gives **E[W] = 20.1 years**. The option market prices this stock as one whose lots, once acquired, are effectively permanent.

## When lots never leave

Everything above assumed ν > 0. If the drift is unfavourable — ν ≤ 0 — the walk still reaches zero *sometimes*, but not always, and a definite fraction of lots wander up and never come back. That fraction has a closed form: averaging the escape probability of a drifting walk over the entry law, and applying the same grid correction,

P( J = ∞ )  =  1 − E[ exp( −2|ν|·(x₀ + β·σ·√τ_c) / σ² ) ]    {#eq:trapped}

At σ = 40% with the same μ and δ, ν = −3.5% and this comes to **7.6% of every assignment permanently trapped**. Not delayed — trapped, with no mechanism in the strategy that will ever release them. The rest of the inventory keeps recycling around them while the trapped stratum grows by λ × 7.6% ≈ 0.18 lots a year, without bound.

This is the first appearance of something the model will keep saying in different ways: the wheel does not fail by losing money on trades. It fails by accumulating positions that never resolve. [The stability section](#sec:stability) makes the boundary precise.

## What this section changed

The naive 1/q calculation said seven and a half months. The correct answer is a median of six months and a mean of four years — and the gap between those two numbers is not a technicality, because capital is committed for the *mean*, not the median. Every lot that leaves quickly frees its capital quickly; the operator's balance sheet is dominated by the ones that don't.

Turning "a mean holding time of 4.18 years" into "how much stock am I holding and what does it cost me" takes one more step, and it is a famous one. That is [the inventory section](#sec:inventory).
