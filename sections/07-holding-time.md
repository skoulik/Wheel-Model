# How Long a Lot Stays {#sec:holding}

A fresh lot has a 40% chance of leaving on its first call — the exit probability [eq:qx](#eq:qx) read at the typical entry depth of 1.6%, tabulated in [the depth section](#sec:depth). But that is one period's odds at one depth, and neither holds still.

## What the question actually is

A lot that fails to exit has, by that very fact, usually drifted *deeper* — and at greater depth its next coin is worse. The periods themselves are independent; what changes is who is still playing. The survivors are not a random sample of the original lots; they are the ones selected for exactly the property that keeps them from leaving. Both halves of that are in [the survival curve](#eq:survival) below: the exit rate falls with every period a lot stays — **0.40** on the first call, **0.23** on the second, **0.07** by the eighth — because the lots still standing are steadily deeper. That is what separates this from [the geometric waiting time](#sec:entry): those trials are memoryless, and these are not.

So the question "how long does a lot stay?" is not a question about a coin at all. It is a question about a wandering path: **when does the depth walk of [eq:depth-walk](#eq:depth-walk) first stand at or below zero on a day a call expires?** That is one of the classical questions of probability.

> **Detour: first-passage time.** Given a random walk, the **first-passage time** is the number of steps until it first reaches a specified level. It is a much subtler quantity than it looks. Even for a walk with a favourable drift, the first-passage time has a **heavy tail**: most paths arrive quickly, but a minority wander the wrong way and take enormously longer, and those rare paths dominate the average. The result is a distribution whose mean sits far above its median — the mean is not "the typical outcome" and using it as one is a standard way to be badly surprised. If the drift is unfavourable, the walk may never arrive at all, and the mean is infinite. [Ross's *Introduction to Probability Models*](#ref:ross-probability-models) treats first passage for random walks and Brownian motion.
>
> One detail of the version used here matters more than it sounds. The price moves continuously, and is watched continuously, but it is only *acted on* when a call expires — so what is wanted is the first passage **as sampled on a schedule**, not the first moment the price touches the strike. Those are different quantities, and the second is not a good approximation to the first: the literature on discretely monitored barriers finds the gap closes only slowly as the observation dates are packed closer together, so that substituting the continuous answer can be badly wrong even at daily monitoring, let alone monthly ([Li and Linetsky](#ref:li-linetsky)). The rest of this section is about exactly how much that costs — it is the largest single correction in the article — and a reader who has met a knock-out note or an autocallable, which terminates on the first scheduled observation date that clears a fixed level, has already met the same object.

## Exits happen on a grid, and the grid is expensive

One complication has to go in before any numbers come out, and the detour above has already named it: the exit is sampled on a schedule rather than watched. If the stock rallies through the strike midway through the four-week call and slips back before expiry, nothing happens: the call finishes out of the money, the lot stays, and the visit is wasted.

The cost of this is not small, and it has a known size. Those wasted visits are also what produces the second effect: the crossing that barely happens is the one that slips back before anything acts on it, so the crossings that survive to an expiry are the decisive ones. A lot standing on the right side on the right day has usually gone well past its strike rather than just reached it, and the climb it actually has to make is longer than the climb to the strike, by

β · σ·√τ_c ,   β = −ζ(1/2)/√(2π) ≈ 0.5826    {#eq:siegmund}

a classical correction. What β measures is an **expected overshoot** — the renewal-theory name, in which *over* means *past* rather than *above*: how far beyond a level a walk typically stands the first time it counts, in units of one period's step. Nothing has moved the strike. What the grid changes is where the lot is standing when the strike finally counts, on average 0.58 steps past it — so the distance a lot has to cover is its own depth plus that excess.

Shifting a continuously watched barrier to price something watched only on a schedule is [Broadie, Glasserman & Kou](#ref:broadie-glasserman-kou-1997)'s technique, whose discretely monitored knock-out option is a wheel lot with the call strike as the barrier. [Siegmund](#ref:siegmund-1979) supplied the diffusion approximation this section uses below, and [Chang & Peres](#ref:chang-peres-1997) the expansion its digits and its limitations come from.

> **Detour: where 0.5826 came from, and what it was for.** Nobody knew it measured an overshoot when the number was first computed, which is the more interesting half of its history. It appears in [Chernoff (1965)](#ref:chernoff-1965), where the problem is not a barrier at all but when to stop a sequential experiment that can only be inspected at fixed times, and where it arrives as a definite integral — one that Gordon Latta recognised as −ζ(1/2)/√(2π). That it *measures an overshoot* was established twenty-one years later, in the work the paragraph above draws on. A reader who opens Chernoff will find −0.5824 printed beside the integral; evaluating the integral gives −0.5826, so that is a slip in his arithmetic and not a second constant.

One caveat about β, and it cuts against the operator rather than for them. 0.5826 is a limit rather than a fixed feature of the problem: it is what the overshoot settles down to when the barrier is many steps away, so that the walk only reaches it after a long run and no longer arrives from any particular place. A lot is not in that regime. Measured in the unit that governs it — one period's step, σ·√τ_c — a fresh lot sits

E[x₀] / (σ·√τ_c)  =  **0.28** of one period's step

below its own call strike. A single step is several times that whole distance, so a lot usually clears the strike on its first or second one, straight from where it started, and the overshoot is set by the size of one step rather than by the limit β describes. At such short range it is larger. β stays in the argument as a bound rather than as the answer: it fixes what the tax would be if this strategy operated where the textbook does, and the distance between that and what the tax actually is turns out to be the more interesting quantity. It earns its keep later, at [the closed form](#eq:holding-siegmund), where β and the opposite extreme bracket the exact answer from both sides — which is what makes that answer evidence rather than merely output. How much larger is settled by **Wald's identity**.

> **Detour: Wald's identity.** Take a walk whose steps are independent and identically distributed, and stop it at a time chosen without knowledge of the future. The identity says the expected total distance travelled is the expected number of steps times the average size of one:
>
> E[S_N]  =  E[N] · E[X]    {#eq:wald}
>
> which looks as though it ought to be obvious and is not. N is random and depends on the very path being measured, so the number of steps and their sizes are not independent quantities. That the average step can be pulled out anyway is what earns the result a name. [Ross](#ref:ross-probability-models) covers it in the renewal chapter.

Here the walk is a lot's depth and one step is one call period. Each step moves the depth by −ν·τ_c on average, and the walk stops at the first period-end where the depth stands at or below zero — by which point it has travelled x₀ downward, plus however far past zero it landed. Both of the identity's conditions hold: the steps are independent, and the stopping time has a finite mean because ν > 0. Equating those two accounts of the same distance gives a lot's mean life as the hole it has to climb divided by the rate the drift fills it, with the overshoot entering as a depth like x₀ rather than as a count of steps:

E[W]  =  ( E[x₀] + E[overshoot] ) / ν .    {#eq:wald-holding}

Run that backwards from the exact 2.10 years computed below, and the overshoot the model is really paying is **0.667** of one period's step, not β's 0.583. Nor does that rest on the identity alone: the same overshoot read straight off the mass that leaves — the mean depth a lot actually stands at when its call is finally assigned — comes to **0.666** steps, owing nothing to Wald or to E[W]. In depth terms it is the **call-grid tax**, 0.667 × 0.20 × √(1/13) = **0.037** — which is **2.4 times the typical entry depth of 0.0155**. Read off β alone it would have been 2.1, and β understates the very thing it is there to measure.

That ratio is the section's result. The hole a lot has to climb out of is not mainly the 1.6% it fell through at assignment. It is mostly the *sampling* — the requirement that the recovery be standing on the right day, once every four weeks. Of the total hole, roughly **30% is the entry and 70% is the grid**. **The exit grid, not the entry overshoot, is what keeps lots in inventory.** An operator worried about being assigned too deep is worrying about less than a third of the problem.

The ratio is worth a second look, because it is the one quantity here that does not depend on how the clocks are set in absolute terms. Both the tax and the entry depth scale with volatility and with the square root of a period, so their ratio is governed by n = τ_c/τ_p — roughly √n. Selling calls on a slower clock than the puts is what creates the tax, and there is no cadence at which it goes away: as long as calls run longer than puts, the grid costs more than the entry. The 0.28 above moves the same way, as 1/√n, so the faster the calls outrun the puts the further inside β's limit the strategy operates: the lever that makes the tax matter is the one that makes the textbook constant least appropriate for measuring it.

So the grid tax is settled: 0.037 in depth, 2.4 times what assignment itself costs, fixed by the cadence rather than by anything the operator picks at the strike. What it has not settled is time. A lot's mean life follows from the tax through [eq:wald-holding](#eq:wald-holding), but a mean is a poor summary of a quantity this skewed, and the operator's question is not what a lot costs on average — it is how long the position will be there. That needs the whole distribution, which is the next thing to build.

## The survival curve

Write S_j for the probability that a lot is still held after j call periods:

S_j  =  P( J > j )  =  P( x₁ > 0, x₂ > 0, …, x_j > 0 )    {#eq:survival}

Each x is the running depth from [eq:depth-walk](#eq:depth-walk), started from an entry depth drawn from [eq:x0-law](#eq:x0-law). There is no closed form, but the sequence can be computed exactly. What has to be carried from one period to the next is not a number but a distribution: knowing what fraction of lots survived period j says nothing about period j+1 unless you also know where the survivors are standing.

So write f_j for the density of depth among the lots still held after j periods — a sub-density, since it integrates to S_j rather than to 1, the missing mass being the lots already called away. One call period moves a lot's depth by −ν·τ_c plus a Gaussian shock of width σ·√τ_c, so

f_{j+1}(y)  =  ∫₀^∞ f_j(x) · φ( (y − x + ν·τ_c) / (σ·√τ_c) ) dx / (σ·√τ_c) ,   y > 0    {#eq:survival-step}

with S_j = ∫₀^∞ f_j(x) dx. The procedure is three steps: start f₀ at the entry law, convolve with the step density, and discard whatever lands at or below zero — those are the lots called away this period. What remains integrates to S_{j+1}, and the mass discarded is that period's exit probability. [eq:qx](#eq:qx) is the same integral done from a single starting depth instead of against a distribution.

(`code/model.py` does this on a grid in x. The grid needs care: representing the depth in cells effectively places the exit boundary half a cell too deep, which holds lots marginally too long, so the long-run figures below are computed at two resolutions and extrapolated. [The verification section](#sec:verification) checks the result against a simulation of the same walk that uses no grid at all.)

For the Standard regime, tabulated in call periods — every column is an exact multiple of the four-week call, and thirteen of them make a year. Two rows: the chance that a lot is still held, and how deep the ones still held are. The first row doubles as a share of a cohort — of a hundred lots opened together, about sixty are still on the books after four weeks, twelve after two years, and two after twenty.

    still held after     4 wk    8 wk   12 wk   24 wk     1 y     2 y     5 y    10 y    20 y
    probability          0.60    0.46    0.38    0.27    0.18    0.12    0.07    0.04    0.02
    their mean depth     0.05    0.08    0.09    0.14    0.21    0.31    0.48    0.66    0.90

The second row is the selection effect of the section's opening, made numerical. It is not that lots deepen with age — every period applies the same drift and the same volatility, and the drift points *toward* the exit. It is that the shallow ones keep leaving. A lot still held at two years is sitting **31% below its own call strike**, and one still held at twenty years is **90%** below it: by then the position is a different object from the one the operator opened, and the call written against it has stopped paying. A fresh lot's call is worth **160 basis points**; the call on a lot a year old is worth **about a hundredth of one**, and past that the model prices it below a millionth of the share price. This is also where [the inventory section](#sec:inventory)'s standing-inventory depths come from — deep inventory is old inventory.

The mean follows from the same row with no new machinery. J counts the periods a lot survives, so J = Σ_{j≥0} 1{J > j} — one indicator for each period it gets through — and taking expectations turns each indicator into the survival probability itself. The mean number of periods is therefore the sum of the whole survival sequence, tail included, and the mean holding time is that times the period length:

E[W]  =  τ_c · E[J]  =  τ_c · Σ_j S_j  =  **2.10 years**    {#eq:holding}

against a **median of eight weeks** — the column where survival first drops below a half. The distribution is exactly as advertised: most lots are handled quickly, a minority never really are, and the mean belongs to the minority. One lot in fifteen is still held after five years; one in twenty-five after ten; one in forty-six after twenty.

Nothing in the model was set up to produce this. There are no separate populations, no mixture of "good" and "bad" lots, no regime switch. A single random walk with a single drift, sampled every four weeks, generates a fast lane, a slow middle, and a tail measured in decades — because that is what first-passage times *are*.

The ratio of mean to median is the number to carry away: **two years against eight weeks, a factor of thirteen**. It is larger here than it would be on a slower call clock, because a fine grid resolves the fast lane — a lucky lot can leave after four weeks rather than waiting a quarter for its chance — while doing nothing at all for the deep tail, which is governed by the drift and not by the sampling.

This is also the point at which a track record will mislead its owner. An operator who averages the holding times of the lots that have *finished* is not measuring this distribution; they are measuring the fast lane, because the slow lots are by construction still on the books and have not produced a number yet. The model can say how large that distortion is on its own terms: among lots that close within two years, the mean holding time is **0.30 years** against the true **2.10**. The median is almost untouched — **eight weeks** either way — which is why the median is the statistic worth quoting from a young book and the mean is not. Any statistic computed over closed positions inherits this bias, and the ones that lean on the tail inherit nearly all of it.

Siegmund's correction also gives a usable closed form, and it is [eq:wald-holding](#eq:wald-holding) with a single substitution. Wald gives the mean exactly, but only in terms of an overshoot the model has to compute; put β's far-barrier limit in its place — the entry depth as a hole of size E[x₀], deepened by the grid tax, divided by the rate at which drift works it off — and it becomes something evaluable by hand:

E[W]  ≈  ( E[x₀] + β·σ·√τ_c ) / ν  =  (0.0155 + 0.0323) / 0.025  =  **1.9 years**    {#eq:holding-siegmund}

which lands 9% below the exact 2.10 and is the right formula to reason with. Every term is legible: the hole, the grid tax, and the drift that has to fill it. It also makes plain why the answer is so large. The numerator is dominated by a term that has nothing to do with how deep the assignment was; and the denominator is a small difference of larger quantities, ν = μ − δ − σ²/2 = 0.07 − 0.025 − 0.02 = **0.025**, so a modest move in any of the three carries the holding time a long way.

The 9% is not slack in the reasoning, and the way to close it is not a better approximation but a bracket around the exact answer. Everything in [eq:holding-siegmund](#eq:holding-siegmund) is exact except the overshoot — Wald gives the mean, E[x₀] is known, ν is a parameter — and the overshoot depends on exactly one thing: how far the barrier sits from where the walk starts, measured in steps. Call it b. That function has no closed form at a general b, but it is known at both ends of the range, and a lot's b lies between them. So the overshoot lies between the two end values, and so does E[W]. The result is a bound rather than an estimate — and it is the only check on the exact 2.10 that does not run back through the same grid that produced it.

The two ends are one dial at its extremes. **Far** is b → ∞: the barrier is many steps off, the walk reaches it only after a long run, and the excess has settled to β, corrected for the drift accumulated over one period — β + θ/4 = **0.591**, with θ = ν·√τ_c/σ = **0.035** being a period's drift in step units, so the correction is under a hundredth. **Near** is b → 0: the walk starts *on* the barrier, so the first step alone carries it past and the excess is a whole step's worth, nothing having been spent getting there. That is the mean first ladder height — how far a walk beginning on a level stands beyond it the first time it is across — and it comes to e^(βθ)/√2 = **0.722**, or 1/√2 with no drift. Both are [Chang & Peres](#ref:chang-peres-1997)'s.

A lot sits at b = **0.279**, much nearer the close end. The overshoot falls as b rises, so a lot's value has to lie between the two, and it does: **0.667**, closer to 0.722 than to 0.591, as 0.279 steps would lead you to expect. Putting the two constants through [eq:wald-holding](#eq:wald-holding) brackets the holding time itself — **1.93 years** at the far end, **2.22** at the near — with the exact 2.10 inside. A reader who wants one number should use the closed form and expect it to run light; a reader who wants to know how light has both bounds.

Under the market's pricing drift the same three terms give ν = 5% − 2.5% − 2% = **0.5%** — one substitution, r for μ — and the same computation gives **E[W] ≈ 9 years**, more than four times the real-world figure from a drift five times smaller. Option prices therefore behave as if lots of this stock, once acquired, were effectively permanent. That is a statement about the drift replication forces, not a forecast that they will be: it is the same distinction [the entry section](#sec:entry) draws, met again on the other side of a holding time. (Round figures are the honest ones here: with a drift that small the mean is carried by the far tail, and the third significant digit is a property of the numerics rather than of the strategy.)

Two things are worth carrying out of this subsection. The 2.10 is not merely computed but bounded — 1.93 and 2.22, from opposite ends of a dial that never touches the grid — which is a stronger claim than a computed number usually gets, and it is why the exact figure can be quoted without hedging about resolution. And what that figure is most sensitive to is ν: three terms of ordinary size differencing to something small, with the holding time inversely proportional to whatever is left. The pricing drift has just shown what a single substitution in that denominator does.

## When lots never leave

Everything above assumed ν > 0, and that assumption was doing more work than it looks. A favourable drift pulls the depth walk toward zero, so every lot leaves eventually and the only question is when. Reverse it — ν ≤ 0, which arrives through σ rather than through anything the operator chooses, since ν = m − σ²/2 — and the walk is pushed away from its own exit. Lots still leave, by luck rather than by drift, but some wander deeper and never return.

The size of that group is classical, and the shape of the answer follows from a single observation. Write p(h) for the chance that a walk drifting away from a barrier at distance h ever reaches it anyway. To cover 2h it must first cover h, and from there it faces the same problem over again from the same distance — so p(2h) = p(h)², and a function turning addition of distance into multiplication of probability is an exponential. Only the rate in the exponent is left to compute, and it is the drift measured against the variance: p(h) = exp(−2|ν|·h/σ²). Here h is the hole from before, x₀ deepened by the same grid tax, so averaging over the entry law and taking the complement gives

P( J = ∞ )  =  1 − E[ exp( −2|ν|·(x₀ + β·σ·√τ_c) / σ² ) ]    {#eq:trapped}

At σ = 40%, with μ and δ unchanged, ν = −3.5% and the closed form gives 4.1%. But it carries β, so it inherits β's problem in the same direction as before: run the walk with no constant standing in for anything and the answer is **4.4% of every assignment permanently trapped**, the closed form running **7.8%** low. Not delayed. Trapped, with no mechanism in the strategy that will ever release them. The rest of the inventory recycles around them while the trapped stratum grows at λ × 4.4% ≈ **0.46 lots a year**, without bound.

Selling puts more often makes the per-assignment fraction *smaller*, because a shorter put period means shallower entries and a shallower hole is easier to escape — but it multiplies the arrivals. Against a monthly put clock the trapped share falls from **5.6%** to 4.4% while the arrival rate quadruples, and the stratum grows three times faster: 0.46 lots a year against **0.15**. The arithmetic favours the arrivals.

The closed form remains the one to reason with, because it shows that only two things govern the answer — the depth a lot enters at, and the tax sitting on top of it — but it should be read knowing which way it errs. It runs about 8% low here, and it is worst precisely where an operator would go to escape the problem. Write the puts so far out of the money that assignment lands at no depth at all, and the formula reads 2.8% where the truth is **3.4%**: short by nearly a fifth, in the regime chosen for safety. That last figure is one of the few numbers in this article known exactly rather than computed — it has a closed form, due to [Janssen & van Leeuwaarden](#ref:janssen-vanleeuwaarden-2007), and the walk above is checked against it.

This is the first appearance of something the model will keep saying in different ways: the wheel does not fail by losing money on trades. It fails by accumulating positions that never resolve. [The stability section](#sec:stability) makes the boundary precise.

## What this section changed

Repeating one period's odds would have said ten weeks. The correct answer is a median of eight weeks and a mean of two years — and the gap between those two numbers is not a technicality, because capital is committed for the *mean*, not the median. Every lot that leaves quickly frees its capital quickly; the operator's balance sheet is dominated by the ones that don't.

Turning "a mean holding time of 2.10 years" into "how much stock am I holding and what does it cost me" takes one more step, and it is a famous one. That is [the inventory section](#sec:inventory).
