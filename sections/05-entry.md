# Entry: How Often, and How Deep {#sec:entry}

Everything the wheel does downstream is set by two numbers decided at the moment a put is assigned: **how often** assignment happens, and **how far below the strike** the stock has fallen when it does. This section derives both, and settles which probabilities the article is talking about.

## Detour: Bernoulli trials and the geometric distribution

> When something either happens or doesn't — a coin flip, a die roll checked for a six, a put option either assigning or not — probabilists call it a **Bernoulli trial**. Write X = 1 when it happens and X = 0 when it does not, and the whole object is two numbers: P(X = 1) = p and P(X = 0) = 1 − p. **That p is its only parameter**, and everything else follows from it — the average of X is p itself, and its spread, p(1 − p), is widest at p = 1/2, where the outcome is least predictable, and shrinks to nothing at either end, where it is not in doubt. A fair coin is p = 1/2; the puts in this article run at p = 0.2 or p = 0.1.
>
> String such trials together — all sharing one p, none aware of the others — and the first question worth asking is how long you wait for something to happen. That waiting time has its own name, the **geometric distribution**, and its shape is easiest to see from the back: the only way to still be waiting after j trials is for all j of them to have failed, so
>
> P(still waiting after j trials)  =  (1 − p)^j
>
> Every empty trial multiplies the chance of continuing by the same factor 1 − p. A constant factor per step is what *geometric* means, and it is what makes the tail long: the decline is steady rather than abrupt, so there is always some chance of a much longer wait than usual. Two numbers summarize that wait:
>
> E[trials to the first success]  =  1/p,   its median  =  ⌈ ln(1/2) / ln(1 − p) ⌉    {#eq:wait}
>
> The median is simply where (1 − p)^j first falls through a half, and the mean needs no more than arithmetic: if one trial in five succeeds, it takes five on average to get one. Behind both sits the property that gives the distribution its character — it is **memoryless**. Each trial is deaf to the ones before it, so after four failures the wait still ahead of you is exactly the wait you began with. Believing otherwise — that a run of near misses has made the next one more likely — is the **gambler's fallacy**, and the geometric distribution is precisely what it is a fallacy about: nothing is ever *due*. That is also why the mean outruns the median: short waits are the rule, and a long one never builds up any pressure to end.
>
> Any introductory probability text covers both; [Ross's *A First Course in Probability*](#ref:ross-first-course) is a standard choice.

Selling a put is one Bernoulli trial per cadence period: with probability p\* it assigns and delivers a lot of stock into inventory, otherwise it expires and the operator keeps the premium and sells another.

**The trials are independent, and that is an assumption rather than a finding.** Successive puts sit on one stock, so it is fair to suspect that a fall this week makes assignment likelier next. Within the model it does not, because **the strike floats**: it is set as a fraction of the *current* price, so each period's put is re-struck wherever the stock now stands and asks its question of the coming period alone. The price model of the detour below makes those periods independent, and the trials inherit it. That inheritance is the entire justification, and it cannot be checked by simulating the same model — a model whose periods are independent by construction will reproduce that independence whatever is asked of it. Real markets cluster their volatility, which would bunch assignments into runs that the arithmetic below does not contain.

So how long until a put assigns? Read [eq:wait](#eq:wait) at p\*: a lot arrives every **1/p\*** put periods on average. In the **Standard** regime p\* = 20%, and the running example sells one put a week, so this section's first question is answered — **a lot every five weeks on average, with a typical wait of four.** The gap between those two numbers is the mildest form of a pattern that runs through the whole article, and [the holding-time section](#sec:holding) is where it stops being mild.

That arrival rate is the one this article's machinery consumes, and everything downstream scales with it: [the inventory section](#sec:inventory) restates it in lots per year and builds the standing inventory on it.[^eq-wait]

## Detour: the normal distribution and N(·)

> The last two objects answered whether something happens and how long you wait for it. This one is about **size** — how far a price moves — which is what decides both. The **normal distribution** is the familiar bell curve. A quantity Y that follows it is pinned down by two numbers — where the curve is centred, its mean **μ_Y**, and how wide it is, its spread **σ_Y** — and its shape is one formula, the **density**
>
> f_Y(y)  =  e^( −(y − μ_Y)² / (2·σ_Y²) ) / ( σ_Y·√(2π) )    {#eq:normal}
>
> tallest at μ_Y and falling away symmetrically, fast enough that values more than three spreads from the mean are uncommon and more than five essentially never seen. The area beneath the density between two points is the probability Y lands between them, and the total area is one.
>
> Everything one asks of a distribution is an integral of that density, and the two questions asked here differ only in what is accumulated. Accumulate the density itself across a range and the answer is a probability. Weight each value by the density before accumulating and the answer is an average in which every outcome counts for how likely it is — the **expectation** E[Y] = ∫ y·f_Y(y) dy, which for this density returns μ_Y, the parameter it was built from.
>
> **Every normal distribution is the same one, shifted and stretched.** Measure Y not in its own units but in spreads away from its mean — replace it by z = (Y − μ_Y)/σ_Y, its **z-score** — and both parameters drop out. What is left is the **standard** normal, centred at zero with spread one, and its density has its own name:
>
> φ(z)  =  e^(−z²/2)/√(2π),   so that   f_Y(y)  =  φ(z)/σ_Y   with   z = (y − μ_Y)/σ_Y    {#eq:phi}
>
> That conversion is the step this article performs most often. The 1/σ_Y is what keeps the total area at one under the stretch, and it is the divisor sitting outside φ in [eq:x0-law](#eq:x0-law).
>
> Two lookups turn φ into answers. The **cumulative distribution function** N(z) is the area under φ to the left of z: the probability that a **draw** — one value picked at random according to the density — comes in below z. Its inverse N⁻¹ runs the other way, turning a probability into the threshold that delivers it. Neither can be written with elementary functions, and neither needs to be; every statistics package and spreadsheet has both.
>
> [Ross's *A First Course in Probability*](#ref:ross-first-course) covers the distribution and the conversion.[^eq-normal]

## Detour: the lognormal price model and the Black–Scholes formula

> Apply that bell curve to a stock's *logarithm*, period after period, and the result is the price model this article runs on. The **Black–Scholes model** ([1973](#ref:black-scholes-1973)) describes a stock price as drifting at some average rate while being knocked around by random shocks whose size is set by the volatility σ. Percentage changes are random, independent from period to period, and normally distributed. Written out, the price after a time τ is
>
> S_τ  =  S · exp( (m − σ²/2)·τ  +  σ·√τ·Z ),   Z a single draw from the standard normal distribution above    {#eq:lognormal}
>
> Two things to read off it. First, the price is the exponential of a normal quantity — that is what *lognormal* means — so the **logarithm** of the price is a **random walk**: a running total of independent random steps, each drawn from the same distribution. Those steps do not average to zero: the systematic tilt in them is the walk's **drift**, the first term in the exponent above, and the scatter around it is the wobble, the second. The two accumulate at different rates — the drift in proportion to τ, the wobble only in proportion to √τ — so a walk watched over a short span is nearly all wobble, and its drift emerges only with sufficient time. That the log price is such a walk is the fact this article leans on hardest, and every formula in this section is an algebraic rearrangement of it.
>
> Second, the drift of that walk is not m. The price is expected to grow at m, but the rate inside the exponent — the one the walk actually drifts at — is m − σ²/2. The σ²/2 between them has a name and a cost; [the depth section](#sec:depth) derives it, and is also where this walk stops being background and becomes the object of study.
>
> The same two parameters price an option. On this article's convention that prices are quoted as fractions of the share price, a European put struck at k is worth
>
> c_p  =  k·e^(−r·τ)·N(−d₂)  −  e^(−δ·τ)·N(−d₁),   d₁ = [ −ln k + (r − δ + σ²/2)·τ ] / (σ·√τ),   d₂ = d₁ − σ·√τ    {#eq:bs-put}
>
> and a call struck at the same k, on the same convention, is
>
> c_c  =  e^(−δ·τ)·N(d₁)  −  k·e^(−r·τ)·N(d₂)    {#eq:bs-call}
>
> Those are the only two option prices this article needs; the sections that follow build their own machinery on them.
>
> Both arguments are the standardization of the detour above, applied to the log price. **d₂ counts how far the strike sits below where the price is expected to end, in one-period moves σ·√τ** — so −d₂ is the strike's own z-score, and **N(−d₂) is the probability that the put finishes in the money**, computed at the drift that appears in the formula. d₁ is that same distance one move further out, and N(−d₁) a stock-weighted version of the same probability. The e^(−δ·τ) beside it is there because the option's holder collects no dividends, so a position hedged to deliver one share at expiry needs only e^(−δ·τ) shares today. That dividend-paying version of the formula is [Merton's](#ref:merton-1973), from the same year as the original.
>
> Notice which drift is in there: r, the risk-free rate, and nowhere the stock's own expected return μ. That is not an approximation. An option's payoff can be manufactured out of a continuously adjusted mixture of the stock and cash, and two things delivering the same payoff must cost the same — so the option's price is pinned by what that mixture costs, which depends on r and σ and not at all on how fast anyone expects the stock to grow. Two investors who disagree completely about μ must still agree on the option's price. Pricing as though the drift were r is called **risk-neutral** valuation, and the next subsection makes it the article's organizing distinction.
>
> The model is a simplification — real markets have jumps, fat tails, and volatility that changes over time — but it is the shared language in which option prices are quoted, and its probabilities are accurate enough for the structural questions asked here. [Hull's *Options, Futures, and Other Derivatives*](#ref:hull) is the standard reference.[^eq-bs-put]

## Which probabilities? One measure, two worlds

A price model needs a **drift**: the average rate at which the price climbs. Two different numbers can be put there, and they answer different questions.

- The **real-world** drift is what the stock is actually expected to do: total return μ, less the dividend yield δ, which is paid out of the price rather than added to it. So m = μ − δ.
- The **risk-neutral** drift is what option *prices* behave as if the stock will do: the risk-free rate r, less δ again. So m = r − δ. It is not a forecast, and nobody claims the stock will only return r; it is the drift replication forces, as the detour above showed, and it is what lets a formula built out of option prices be read straight off the market.

This article computes everything in terms of a single drift m, and reports two readings of the same chain of formulas: **m = μ − δ**, what actually happens, and **m = r − δ**, what the market's prices imply. Neither is ever mixed into the other. The real-world reading leads, because that is the world the operator lives in; the market's reading appears alongside wherever the two disagree, and [the stability section](#sec:stability) is where that disagreement matters most.

A probability in this article is **computed**: the model produces it from a drift and the stock's own volatility σ. A premium is not — it is **observed**, read off the market and taken as given. It too is quoted as a volatility, but a different one: the **implied volatility** σ_IV of a premium is the value at which [eq:bs-put](#eq:bs-put) returns it,

σ_IV:  the volatility for which  c_p( k, τ_p, σ_IV, r, δ )  equals the quoted premium    {#eq:iv}

In general there is no algebra for σ_IV and it is found by search, though a few special cases — an option struck exactly at the forward price, most usefully — do invert in closed form. **Applied to a premium, Black–Scholes is a unit rather than a valuation**, and the convention earns its keep because implied volatility compares across strikes and expiries where a raw price does not. A premium is priced off r and δ alone — μ never enters it, even where the probabilities beside it are read at μ − δ.[^eq-bs-put]

That leaves one honest question, which [the returns section](#sec:returns) answers with a number rather than an argument. Implied volatility is *systematically higher* than the volatility that subsequently materializes — [Bakshi and Kapadia](#ref:bakshi-kapadia-2003-jod) measured the gap across individual companies, [Carr and Wu](#ref:carr-wu-2009) over a later decade — and that gap, the **volatility risk premium**, is the documented source of return in put-write and covered-call studies alike. Every headline result below assumes it away, σ_IV = σ, so that what remains is the machinery of the strategy and nothing else.

## The strike dial

Operators rarely pick a strike directly. They pick how often they are willing to be assigned — a target probability p\*, and the strike follows from it. **That p\* is the strike dial**, the one control this article turns: everything the operator decides about entry is a setting of it, and every strike quoted below is what some setting produced. Under the lognormal model the strike fraction k\* delivering p\* is

k\*  =  exp( N⁻¹(p\*) · σ·√τ_p  +  (m − σ²/2) · τ_p )    {#eq:kstar}

Two settings of that dial are carried throughout: **Standard**, p\* = 20%, which leads every worked example, and **Conservative**, p\* = 10%, the more cautious setting. Against the running example's market — weekly puts, σ = 20%, total return μ = 7%, δ = 2.5%, so m = 4.5% — the first gives k\* ≈ **0.9774**, a strike about 2.3% below the market, and the second k\* ≈ **0.9655**, about 3.5% below. Because p\* is defined in the real world, it *is* the rate at which puts assign: one put in five, or one in ten.[^eq-kstar]

Standard leads for a reason worth stating rather than leaving as inertia. That market is a **stylized** one — a round volatility, a round return, a round rate — and p\* = 20% is the round, conventional number that belongs beside them, as well as the calibration practitioners quote to each other. [The live-account section](#sec:live) measures which setting a real book runs at; the examples here deliberately do not adopt that figure, because fitting the dial to a measurement while the volatility and the drift stayed round would claim more calibration than the example has.

What sets a strike's distance below the market is the size of one period's move, σ·√τ_p. Volatility scales it: the Conservative strike that sits 3.5% out on this stock sits 5.2% out on a 30%-volatility name — same dial, different strike, which is [eq:kstar](#eq:kstar) doing the job it exists for, since the operator picks a frequency and the market decides how far away that puts it. The tenor scales it the same way, and that is the half worth remembering: a week is not long enough for a 20%-volatility stock to travel far, which is why one chance in five sits only 2.3% away. This is the first appearance of a theme that runs through the whole article — **the cadence sets the scale of everything**. Both numbers this section produces, how far out of the money the strike sits and how deep an assignment lands when it comes, are multiples of that one-period move, so neither means anything until you know the cadence it was measured at.

Read the other way round — fixing that strike and asking the market what it thinks — the probability implied by option prices is

p_screen  =  N(−d₂),   d₂ = [ −ln(k) + (r − δ − σ²/2)·τ_p ] / (σ·√τ_p)    {#eq:p-screen}

which comes to **20.4%** at the Standard strike, a little higher than the 20% that will actually occur — higher because option prices behave as if the stock climbed at r − δ = 2.5% rather than the μ − δ = 4.5% it is actually expected to, and a stock that climbs more slowly finishes below any given strike more often. This is worth knowing because p_screen, not p\*, is the number practitioners quote to each other.

How far apart are the two worlds, then, and on what does the distance depend? The answer is short, and it is the *entire* difference between them: the drifts differ by μ − r and by nothing else, so over one tenor d₂ moves by the asset's **Sharpe ratio** — how much it returns above the risk-free rate for each unit of volatility, (μ − r)/σ, or 0.10 in the running example — times the square root of the tenor:

Δd₂  =  (μ − r)·√τ_p / σ  =  0.0139    {#eq:screen-gap}

It falls out of [eq:bs-put](#eq:bs-put) by subtraction. Write d₂ at each drift and, since this article prices at σ_IV = σ, everything but the drift is common to the two worlds and cancels. What is left is how much further the real world drifts over one tenor, (μ − r)·τ_p, divided by one period's move σ·√τ_p — the same units d₂ itself is measured in. d₁ shifts by exactly as much — the σ·√τ_p between them carries no drift — but it is d₂ that matters here, since p\* and p_screen are both N(−d₂), read at the two drifts.

The gap is given in d₂ units rather than in probability because in them it is the same at every strike, where the probability gap is not: converting depends on where on the bell curve the strike sits. −d₂ in the real world *is* N⁻¹(p\*), by construction of the dial, so the gap converts back directly:

Δp  =  N( N⁻¹(p\*) + Δd₂ )  −  p\*    {#eq:gap-prob}

For the running example that comes to **0.0039**, or 0.4 percentage points — exactly what p\* and p_screen delivered above, the distance from 20.0% to 20.4%, and about three and a half times smaller than the shift in d₂ it came from. *Why* it depends on the strike is easiest to see in the approximation φ(N⁻¹(p\*))·Δd₂: the factor is the height of the bell curve where the strike sits, 0.28 at Standard and 0.18 at Conservative. Both readings are small for short-dated options, and both shrink as √τ_p.

One clarification, because what a screen shows is not quite either number above. A broker displays the option's **delta** — how much its price moves for a one-point move in the stock, and equivalently how many shares it takes to replicate — which is ≈ 19.6% here, against the probability of finishing in the money, N(−d₂) ≈ 20.4%. They are different objects, a price sensitivity and a probability, built on d₁ and d₂ respectively, and the distance between them is about φ(N⁻¹(p\*))·σ·√τ_p: one period's move again. That comes to 0.8 of a percentage point at a weekly tenor, which is why traders call a strike a "20-delta put" and mean a one-in-five chance without anyone objecting. But it is a licence short tenors grant, not a fact about the two quantities — the gap grows as √τ_p, and by a one-year tenor it is several points wide. **This article always means a probability.**

That completes the dial: a probability in, a strike out, and the numbers a screen reports placed beside them. Every strike in this article is set this way, and everything the model does downstream begins with a lot acquired at one.

## How deep does assignment land?

Assignment tells us the stock finished below the strike; it does not say by how much, and that overshoot is what the lot must climb back out of. The quantity has a name here — the lot's **depth** — and its behaviour over time is the subject of everything that follows. At the moment of assignment,

x₀  =  ln( K_c / S )  >  0    {#eq:x0-def}

the log-distance from the price paid to the price the market is offering.

Why a logarithm, rather than the percentage drop most people would reach for? Partly because the logarithm is where the mathematics already lives: [eq:lognormal](#eq:lognormal) makes a price the *exponential* of a normal quantity, so a log ratio of two prices is normal and a percentage difference of them is not — the entry depth has a tidy distribution in logs and no tidy one in percentages. But the reason worth remembering is about the quantity rather than the algebra. Depth is what a lot must climb back out of, and in logs the fall in and the climb out are the **same number**: a lot that dropped by x needs a rise of x to get back to its strike. In percentages those are two different numbers, and they part company quickly — a lot 25% below its strike needs a 33% rise, not a 25% one. So x says both how far the lot fell and how far it has to travel to leave, where a percentage says only the first; and where a percentage is the more natural thing to quote, the article converts back, as [eq:d-mean](#eq:d-mean) does below. [The depth section](#sec:depth) adds a third reason once the lot starts moving, and makes this quantity the state variable of the whole model.

Assignment restricts the log price to one side of the strike, which makes the entry depth a **truncated normal**.[^eq-x0-def]

> **Detour: truncated distributions and conditional expectation.** Conditioning on an event needs no new machinery. It needs the two integrals of the detour above — the area under f_Y, which gives a probability, and the value-weighted area ∫ y·f_Y(y) dy, which gives the expectation E[Y] — taken over (a, ∞) instead of over the whole line, and then renormalized.
>
> Let Y be that detour's quantity, with density f_Y, and let the event be that Y came in above some point a, the **point of truncation**. Discard the probability density below a. The area under what remains no longer integrates to one, so what remains is not a probability density; it integrates instead to the probability of the event,
>
> P(Y > a)  =  ∫ₐ^∞ f_Y(y) dy
>
> the missing share having gone with the part that was cut away. Renormalizing it back to one — dividing through by that same P(Y > a) — repairs it, and the result is the **conditional density** of Y given the event:
>
> f_Y(y | Y > a)  =  f_Y(y) / P(Y > a),   y > a
>
> This is an ordinary probability density again, though one that now depends on a as well as on f_Y's own mean and spread, and ordinary questions can be asked of it in the ordinary way. Its mean is called the **conditional expectation** of Y given the event — the average of Y over the scenarios in which the event occurred:
>
> E[Y | Y > a]  =  ∫ₐ^∞ y·f_Y(y) dy / P(Y > a)
>
> That is the expectation of the detour above with both changes applied at once: the range cut at a, the result renormalized. For a normal distribution f_Y all three come out in closed form, built from the same N(·) used everywhere else — which is why what follows can be written down rather than simulated. [Hull](#ref:hull) computes one on the way to the Black–Scholes formula.

The assignment event means the stock finished below the strike that was set at a fraction k of the price when the put was sold: S_τ < k·S₀. Divide through by S₀ and take logs, and the same event reads R < ln k, where R = ln(S_τ/S₀) is the put's own log return — normal, with mean (m − σ²/2)·τ_p and spread σ·√τ_p, by [eq:lognormal](#eq:lognormal). A lot's call strike is frozen at what it cost, K_c = k·S₀, and the depth becomes x₀ = ln(k·S₀/S_τ) = ln k − R, conditioned on R < ln k, with density

f(x₀)  =  φ( (ln k − x₀ − (m − σ²/2)·τ_p) / (σ·√τ_p) ) / ( σ·√τ_p · p\* ),   x₀ > 0    {#eq:x0-law}

where φ is the standard normal bell curve and the division by p\* is the detour's renormalization: the event being conditioned on is x₀ > 0 — the put assigning — so the point of truncation is x₀ = 0, and the probability of that event is p\* by construction of the strike dial. Its mean is the conditional expectation of the detour, and for this density it has a closed form:

E[x₀]  =  σ·√τ_p · ( N⁻¹(p\*)  +  φ(N⁻¹(p\*)) / p\* )    {#eq:x0-mean}

one period's move, scaled by a factor that depends on nothing but the dial. Notice what is missing from it: the drift m. It has not left the problem, only this formula — it is inside k\*, which [eq:kstar](#eq:kstar) places wherever it must to hold p\* fixed whatever the drift is. And that is exactly why it cannot come back: the world with the higher drift needs its strike nearer the money to keep the same one-in-five chance, but moving the strike does not change how far, in logs, a lot overshoots it *given that it got there*. So the real world and the market's pricing world, which differ only in drift, do not merely agree closely on this number; they agree exactly. For the Standard regime **E[x₀] ≈ 0.0155**: the mean assignment lands about **1.6% below its own strike**, against a median of **1.2%** — the same one-period move times another factor the dial alone sets, N⁻¹(p\*) − N⁻¹(p\*/2). The mean is the deeper of the two because this is a bell curve's tail: most assignments are shallow, and the occasional deep one carries the average out past the middle. Conservative entries land slightly shallower, E[x₀] ≈ 0.0131 against a median of 0.0101 — the further out the strike, the thinner the bell curve beyond it.

The form practitioners usually think in is not the depth below the strike but **d**, the drop from S₀ — the price the stock stood at when the put was sold, a full tenor earlier. Its average is

E[d | assignment]  =  1 − e^(m·τ_p) · N(−d₁) / N(−d₂),   d₁ = d₂ + σ·√τ_p    {#eq:d-mean}

giving **3.8%** for Standard and **4.7%** for Conservative. d and x₀ measure one fall from two places, and the conversion is one line: the fall from S₀ is the strike's own distance out of the money, followed by the depth below it.

S_τ / S₀  =  k\* · e^(−x₀)    {#eq:fall-split}

Take expectations of that — of e^(−x₀) — and [eq:d-mean](#eq:d-mean) is what comes out. The drift comes back with the first factor and only with it — k\* is where it was hiding, and d includes that step where x₀ does not. Under the market's drift the figures are 3.8% and 4.7% as well, differing in the fourth decimal, because the strike is the only thing that moves between the two worlds and over one week it barely moves.

One thing about E[x₀] deserves emphasis: it is **much smaller than intuition suggests**. A weekly put assigned is not a disaster in progress; it is a lot bought about 1.6% under a strike the operator chose on purpose. Whether 1.6% is easy or hard to work off is the question the rest of Part II answers — and the answer is not the comfortable one, because it turns out to have almost nothing to do with the 1.6%.

One limit on all of this. A lognormal has no room for big jumps: it is a model of continuous drift and diffusion, so the depth it derives describes the assignment that *drifts* below the strike, not the one that gaps below it on an earnings miss or a profit warning. An operator sizing for the worst case should not take E[d | assignment] as the worst case. [The live-account section](#sec:live) measures how much of the average that tail carries.

So, how deep? About **1.6% below the strike the operator chose** (a log depth, 1.5% as a price) and **3.8% below S₀, the price at which they chose it** — one event, measured against a strike the drift places and against an S₀ it does not. Both are multiples of one period's move σ·√τ_p: the first exactly, scaled by a factor the dial alone sets, and the second with a small correction for the drift, which reaches it through the strike. Turning the dial down to Conservative makes the first number *smaller* and the second *larger* — 1.3% and 4.7% — because a strike further out of the money is a longer fall to reach and a shallower overshoot once reached. All four describe the ordinary assignment, not the worst one.

## A caveat on exercise style

The probabilities this section computes are **terminal**: p\* and p_screen both ask where the stock stands *at expiration* and say nothing about the path it took to get there, and so does the call-away probability [the depth section](#sec:depth) builds. Listed equity options are American and may be exercised early, so the model is using European mathematics on American contracts. That is a real simplification and it is worth saying what it costs, on each leg separately, because the two legs are not alike. The short version: on the call leg it costs almost nothing, for a structural reason; on the put leg early exercise is neither rare nor negligible, but the relief it gives other put writers is one the wheel cannot collect.

**On the call leg the early-exercise premium does not reach us, and the reason is structural.** [Bakshi and Kapadia](#ref:bakshi-kapadia-2003-jod) measure that premium and put it at about **two volatility points** — a figure to take seriously, since [the returns section](#sec:returns) ends up measuring this strategy's whole advantage in volatility points too. It does not apply here, because their figure is measured on calls *near the money and close to expiry*, and that is exactly the object this strategy never sells: a lot's call strike is frozen at what the operator paid, and a lot only still exists while it is below that strike. Every call written here is written out of the money.

The one channel that could bite on the call leg is a lot that rises above its strike *mid-period*, with a dividend falling due before the call expires — the classic case, where a call is exercised the day before the stock goes ex-dividend. That pays only when the call's remaining time value has fallen below the dividend about to be collected — at the running parameters, one quarterly instalment of the 2.5% yield, or 0.625% of the share price. Writing D for that dividend, the condition is

c_c(k, τ)  −  (1 − k)  ≤  D,   D = δ/4    {#eq:early-exercise-call}

where c_c(k, τ) is the call's price from [eq:bs-call](#eq:bs-call) and (1 − k) is the option's **intrinsic value**, what its holder collects by exercising it now. The difference between them is the **time value**, which exercising throws away — so the condition weighs what is given up against the dividend collected instead. Solving it at each τ gives how far above the strike the stock has to sit:[^eq-bs-put]

    days to expiry        28      21      14       7       3
    stock above strike  5.5%    4.1%    2.8%    1.2%    0.2%

**The threshold defeats itself from both ends.** Early in the period, where an exercise would genuinely shorten the wait, it asks for 5.5% — the whole of one call period's typical move, σ·√τ_c — and it asks for it starting from a lot that was *below* its strike when the period began, so the real requirement is that move plus whatever depth the lot started at. Late in the period the threshold collapses toward nothing, but so does the prize: being exercised three days early rather than at expiry changes almost nothing, because the lot was leaving either way. Early exercise on this leg accelerates departures that were already going to happen. Omitting it is conservative, and this is the size of what is omitted.

**On the put leg early exercise is real, and it is the tenor that saves us.** It is genuinely common once the stock has fallen far enough: over fourteen years of six-month contracts, [Merton, Scholes and Gladstein](#ref:merton-scholes-gladstein-1982) found **a quarter** of puts written 10% out of the money were exercised before expiry — not while they were out of the money, which would be irrational, but after the stock had dropped through the strike and far enough below it that the interest earned on the strike proceeds beat the time value left. Their timing makes the rest of the argument: almost none of those exercises fell in the first two months of the contract, and four fifths came in the last two. Their warning is aimed squarely at models like this one: any simulation assuming puts are held to expiration "will systematically… overstate the returns to the writers of puts."

What it is worth on a *weekly* put is something this article can settle for itself. Exercising collects the put's intrinsic value in cash — the strike less the spot — and forfeits whatever time value is left; what makes collecting it *early* worth anything is the interest those proceeds then earn. That interest enters differently from the call's dividend. It is not a payment on the side but the discounting already inside c_p, since a European put pays its strike only at expiry, and deep enough in the money that discount drives the formula's own price below intrinsic. So the condition is [eq:early-exercise-call](#eq:early-exercise-call) with the dividend set to zero:

c_p(k, τ_p)  ≤  k − 1    {#eq:early-exercise-put}

k being greater than one here, since the put is in the money, so k − 1 is again its intrinsic value. What drives a put to that line is the interest on the strike over the tenor, r·τ_p, and over one week that is **0.096%** — almost nothing with which to buy the time value out. So the stock has to sit **6.8% below the strike** before a weekly put is worth exercising early: **8.9%** below the price it was written at, or **3.4** of one week's moves. The chance of ever touching that inside one tenor is **0.074%** — a touching probability rather than a closing one, since the holder may act on any day. That is an overstatement, and deliberately so: where exercising early is genuinely optimal the American put is worth exactly its intrinsic value and never less than the European one, so a test written on the European price fires wherever exercise is optimal and across a margin beyond it. The true threshold is deeper than 6.8%, which leaves the approximation leaning the same way as on the call leg. Against the quarter of six-month puts Merton, Scholes and Gladstein found exercised early, it is the short tenor — not anything structural about the wheel — that lets us dismiss early exercise on this leg as insignificant.[^eq-bs-put]

One thing not to carry across, for a reader who knows that literature. For Merton, Scholes and Gladstein early exercise functions as a *stop-loss*: the position closes, the proceeds sit in cash for the rest of the period, and the loss is truncated. **The wheel has no such exit.** Assignment here does not end the exposure; it converts a short put into a lot that then rides its own price path to its own barrier, which is the subject of the rest of Part II. So the loss-truncation that gives their put strategies a friendlier tail does not carry over here — and the European treatment is the right model of what we do, for a reason that has nothing to do with the American premium being small, though on this tenor it is small too.

One consequence for anyone who would rather price the American feature than assume it away: the same authors found that valuing an American put by put–call parity understates it, badly in periods of high interest rates. This article does not take that shortcut — its put formula is a direct one — but it is the natural shortcut to reach for, and it is a worse approximation than the European assumption it would be trying to repair.

There is also a path-versus-endpoint distinction — the stock may cross a strike mid-period and come back, which a terminal probability never sees. [The holding-time section](#sec:holding) turns that from a caveat into a quantity, because on the call leg the same effect has a name and a measurable size.

[^eq-normal]: Reproduced by `python code/examples/entry_normal.py` — [eq:normal](#eq:normal), [eq:phi](#eq:phi), and the other readings quoted here are `sigma 0.30`; `p-star 0.10`; `measure Q`. Pass `--help` for the full parameter set. The quantity it works on is this section's own log return, and four of its lines are checks rather than readings: [eq:normal](#eq:normal) integrated over the whole line must come to one, the same density weighted by y must integrate back to μ_Y, the probability below the strike must agree whether it is integrated directly or standardized and read off N, and N must invert N⁻¹.

[^eq-wait]: Reproduced by `python code/examples/entry_wait.py` — [eq:wait](#eq:wait), and the other readings quoted here are `p-star 0.10`; `measure Q`. Pass `--help` for the full parameter set. The simulated columns walk the price path and re-strike a put each period, so they check [eq:kstar](#eq:kstar) end to end rather than re-drawing the distribution the formula already describes. They do not test the independence assumed above, which no simulation of this model could.

[^eq-x0-def]: Reproduced by `python code/examples/entry_depth.py` — [eq:x0-def](#eq:x0-def), [eq:x0-law](#eq:x0-law), [eq:x0-mean](#eq:x0-mean), [eq:d-mean](#eq:d-mean), [eq:fall-split](#eq:fall-split), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --measure Q`. Pass `--help` for the full parameter set. The median beside E[x₀] is σ·√τ_p·(N⁻¹(p\*) − N⁻¹(p\*/2)), which the module prints at every case. Three of its lines are checks rather than readings. [eq:x0-law](#eq:x0-law) integrated over x₀ > 0 must come to one, which is the detour's division by p\* and the only thing that tests it — the mean and the density readings all come from the same expression, so a wrong divisor would move them together and still look consistent. [eq:x0-mean](#eq:x0-mean), which carries no drift, is differenced against the same mean computed through the actual strike and the actual drift: that the two agree is what "exactly" above rests on. And [eq:fall-split](#eq:fall-split)'s depth factor is multiplied by k\* and differenced against [eq:d-mean](#eq:d-mean), which reaches the same quantity through d₁ and d₂ instead. That factor is printed to eight decimals because the two worlds return it identically — the drift is in k\*, and nowhere else in the fall.

[^eq-kstar]: Reproduced by `python code/examples/entry_strike.py` — [eq:kstar](#eq:kstar), [eq:p-screen](#eq:p-screen), [eq:screen-gap](#eq:screen-gap), [eq:gap-prob](#eq:gap-prob), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --sigma 0.297`. Pass `--help` for the full parameter set.

[^eq-bs-put]: Reproduced by `python code/examples/entry_pricing.py` — [eq:lognormal](#eq:lognormal), [eq:bs-put](#eq:bs-put), [eq:bs-call](#eq:bs-call), [eq:iv](#eq:iv), [eq:early-exercise-call](#eq:early-exercise-call), [eq:early-exercise-put](#eq:early-exercise-put), and the other readings quoted here are `measure Q`; `delta 0.05 --tau-p 2.0 --sigma 0.30`; `iv-spread 0.03`. Pass `--help` for the full parameter set. This is the module to reach for when trying parameters of your own: it prints which volatility each line used, checks the put's delta against a numerical derivative of its own price rather than against another formula, and asserts put–call parity at every case. It also computes the early-exercise threshold table above, at whatever dividend, volatility and rate a reader passes rather than only at the article's.
