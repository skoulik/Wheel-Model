# Entry: How Often, and How Deep {#sec:entry}

Everything the wheel does downstream is set by two numbers decided at the moment a put is assigned: **how often** assignment happens, and **how far below the strike** the stock has fallen when it does. This section derives both, and settles which probabilities the article is talking about.

## Detour: Bernoulli trials

> When something either happens or doesn't — a coin flip, a die roll checked for a six, a put option either assigning or not — probabilists call it a **Bernoulli trial**. Write X = 1 when it happens and X = 0 when it does not, and the whole object is two numbers: P(X = 1) = p and P(X = 0) = 1 − p. **That p is its only parameter**, and everything else follows from it — the average of X is p itself, and its spread, p(1 − p), is widest at p = 1/2, where the outcome is least predictable, and shrinks to nothing at either end, where it is not in doubt. A fair coin is p = 1/2; the puts in this article run at p = 0.2 or p = 0.1.
>
> Strings of Bernoulli trials — all sharing one p, none aware of the others — are the atoms from which the more elaborate distributions later in this article are built. Any introductory probability text covers them; [Ross's *A First Course in Probability*](#ref:ross-first-course) is a standard choice.

Selling a put is one Bernoulli trial per cadence period: with probability p\* it assigns and delivers a lot of stock into inventory, otherwise it expires and the operator keeps the premium and sells another.

**The trials are independent, and that is an assumption rather than a finding.** Successive puts sit on one stock, so it is fair to suspect that a fall this week makes assignment likelier next. Within the model it does not, because **the strike floats**: it is set as a fraction of the *current* price, so each period's put is re-struck wherever the stock now stands and asks its question of the coming period alone. The price model of the detour below makes those periods independent, and the trials inherit it. That inheritance is the entire justification, and it cannot be checked by simulating the same model — a model whose periods are independent by construction will reproduce that independence whatever is asked of it. Real markets cluster their volatility, which would bunch assignments into runs that the arithmetic below does not contain.

So how long until a put assigns? Waiting on a string of independent trials at rate p\* is the **geometric distribution** — the first assignment falls on trial n with probability (1 − p\*)^(n−1)·p\* — and two numbers summarize it:

E[N]  =  1/p\*,   median N  =  ⌈ ln(1/2) / ln(1 − p\*) ⌉    {#eq:wait}

At **Standard**, p\* = 20%, a put assigns on the **fifth** attempt on average but on the **fourth** typically. The mean sits above the median because a tail of long waits drags it there — the mildest form of a pattern that runs through the whole article, and [the holding-time section](#sec:holding) is where it stops being mild.[^eq-wait]

## Detour: the normal distribution and N(·)

> The **normal distribution** is the familiar bell curve. A quantity Y that follows it is pinned down by two numbers — where the curve is centred, its mean **μ_Y**, and how wide it is, its spread **σ_Y** — and its shape is one formula, the **density**
>
> f_Y(y)  =  e^( −(y − μ_Y)² / (2·σ_Y²) ) / ( σ_Y·√(2π) )    {#eq:normal}
>
> tallest at μ_Y and falling away symmetrically, fast enough that values more than three spreads from the mean are uncommon and more than five essentially never seen. The area beneath the density between two points is the probability Y lands between them, and the total area is one.
>
> **Every normal distribution is the same one, shifted and stretched.** Measure Y not in its own units but in spreads away from its mean — replace it by z = (Y − μ_Y)/σ_Y — and both parameters drop out. What is left is the **standard** normal, centred at zero with spread one, and its density has its own name:
>
> φ(z)  =  e^(−z²/2)/√(2π),   so that   f_Y(y)  =  φ(z)/σ_Y   with   z = (y − μ_Y)/σ_Y    {#eq:phi}
>
> That conversion is the step this article performs most often. The 1/σ_Y is what keeps the total area at one under the stretch, and it is the divisor sitting outside φ in [eq:x0-law](#eq:x0-law).
>
> Two lookups turn φ into answers. The **cumulative distribution function** N(z) is the area under φ to the left of z: the probability that a **draw** — one value picked at random according to the density — comes in below z. Its inverse N⁻¹ runs the other way, turning a probability into the threshold that delivers it. Neither can be written with elementary functions, and neither needs to be; every statistics package and spreadsheet has both.
>
> [Ross's *A First Course in Probability*](#ref:ross-first-course) covers the distribution and the conversion.[^eq-normal]

## Detour: the lognormal price model and the Black–Scholes formula

> The **Black–Scholes model** ([1973](#ref:black-scholes-1973)) describes a stock price as drifting at some average rate while being knocked around by random shocks whose size is set by the volatility σ. Percentage changes are random, independent from period to period, and normally distributed. Written out, the price after a time τ is
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
> The two arguments recur throughout, so it is worth knowing what each one is: **N(−d₂) is the probability that the put finishes in the money**, computed at the drift that appears in the formula, and N(−d₁) is a stock-weighted version of the same thing. The e^(−δ·τ) beside it is there because the option's holder collects no dividends, so a position hedged to deliver one share at expiry needs only e^(−δ·τ) shares today. That dividend-paying version of the formula is [Merton's](#ref:merton-1973), from the same year as the original.
>
> Notice which drift is in there: r, the risk-free rate, and nowhere the stock's own expected return μ. That is not an approximation. An option's payoff can be manufactured out of a continuously adjusted mixture of the stock and cash, and two things delivering the same payoff must cost the same — so the option's price is pinned by what that mixture costs, which depends on r and σ and not at all on how fast anyone expects the stock to grow. Two investors who disagree completely about μ must still agree on the option's price. Pricing as though the drift were r is called **risk-neutral** valuation, and the next subsection makes it the article's organizing distinction.
>
> The model is a simplification — real markets have jumps, fat tails, and volatility that changes over time — but it is the shared language in which option prices are quoted, and its probabilities are accurate enough for the structural questions asked here. [Hull's *Options, Futures, and Other Derivatives*](#ref:hull) is the standard reference.[^eq-bs-put]

## Which probabilities? One measure, two worlds

A price model needs a **drift**: the average rate at which the price climbs. Two different numbers can be put there, and confusing them is the classic error in this subject.

- The **real-world** drift is what the stock is actually expected to do: total return μ, less the dividend yield δ, which is paid out of the price rather than added to it. So m = μ − δ.
- The **risk-neutral** drift is what option *prices* behave as if the stock will do: the risk-free rate r, less δ again. So m = r − δ. It is not a forecast, and nobody claims the stock will only return r. It is an artifact of how options are priced — and it is what lets a formula built out of option prices be read straight off the market.

This article computes everything in terms of a single drift m, and reports two readings of the same chain of formulas: **m = μ − δ**, what actually happens, and **m = r − δ**, what the market's prices imply. Neither is ever mixed into the other. The real-world reading leads, because that is the world the operator lives in; the market's reading appears alongside wherever the two disagree, and in [the stability section](#sec:stability) that disagreement becomes the sharpest result in the article.

Premiums are treated differently, and deliberately so. **A premium is not a probability; it is a price.** The operator does not compute what a put ought to cost, they read what it does cost. Premiums therefore enter as market data. That the market publishes those quotes in Black–Scholes form, at a number called implied volatility, is a quoting convention — the same way a bond price is published as a yield. Where a premium is needed, the article uses that convention at the quoted volatility σ_IV.

That leaves one honest question, which [the returns section](#sec:returns) answers with a number rather than an argument. Implied volatility is *systematically higher* than the volatility that subsequently materializes, and that gap — the volatility risk premium — is the documented edge of every option-selling strategy. Every headline result below assumes it away, σ_IV = σ, so that what remains is the machinery of the strategy and nothing else.

## The strike dial

Operators rarely pick a strike directly. They pick how often they are willing to be assigned, and the strike follows. Under the lognormal model the strike fraction k\* delivering a target assignment probability p\* is

k\*  =  exp( N⁻¹(p\*) · σ·√τ_p  +  (m − σ²/2) · τ_p )    {#eq:kstar}

For the **Standard** regime — p\* = 20%, weekly puts, σ = 20%, total return μ = 7%, δ = 2.5%, so m = 4.5% — this gives k\* ≈ **0.9774**, a strike about 2.3% below the market. For the **Conservative** regime, p\* = 10%, it gives k\* ≈ **0.9655**, about 3.5% below. Because p\* is defined in the real world, the realized assignment rate *is* p\*: one put in five, or one in ten. No correction is needed and none is applied.[^eq-kstar]

The strikes are close to the money because the tenor is short. A week is not long enough for a 20%-volatility stock to travel far, so a one-in-five chance of finishing below the strike is only 2.3% away. This is the first appearance of a theme that runs through the whole article: **the cadence sets the scale of everything**, and quantities that look comparable at one cadence are not at another.

Read the other way round — fixing that strike and asking the market what it thinks — the probability implied by option prices is

p_screen  =  N(−d₂),   d₂ = [ −ln(k) + (r − δ − σ²/2)·τ_p ] / (σ·√τ_p)    {#eq:p-screen}

which comes to **20.4%** at the Standard strike, a little higher than the 20% that will actually occur. This is worth knowing because p_screen, not p\*, is the number practitioners quote to each other.

The gap between the two worlds has a closed form, and it is the *entire* difference between them. The two drifts differ by μ − r, so over one tenor the argument of N(·) shifts by the asset's Sharpe ratio times the square root of the tenor:

Δd₂  =  (μ − r)·√τ_p / σ  =  0.0139    {#eq:screen-gap}

That is a shift in d₂, not in probability, and the distinction is worth keeping because the two differ by a factor of four here. Converting costs one evaluation of the bell curve at the threshold, φ(N⁻¹(p\*)) ≈ 0.28, which turns 0.0139 into **0.4 percentage points** — precisely the distance from 20.0% to 20.4%. Both readings are small for short-dated options, and both shrink as √τ_p.

(Strictly, the screen usually shows the option's **delta**, ≈ 19.6% here, rather than the probability of finishing in the money, N(−d₂) ≈ 20.4%. The two are close for short-dated options and traders conflate them freely. This article always means a probability.)

## Where a real operator sits on the dial

Two regimes are two settings of one dial, and it is fair to ask which of them describes practice. The account behind this article answers that, though not at first glance. Over fifteen months, 956 of its put contracts can be priced against the market on the day they were written, and 71 of those were assigned — **7.4%**, apparently more cautious than either regime on offer.

That number is not comparable, for two reasons that push it the same way. The first is the drift: the window was a bull market, its held names running at roughly +40% a year against the +4.5% assumed here, and a stock that is climbing finishes below the same strike less often. The second is that **a week is not seven days of market**. The account's dominant put is written Monday at the open and expires Friday at the close — five trading sessions, the weekend contributing nothing but a date. That is also exactly what this article's weekly tenor is worth: 1/52 of a year is 4.85 of the 252 sessions a year contains. The two clocks agree; it is only raw calendar arithmetic, which reads that put as four days rather than five sessions, that makes them look different.

Correct for the drift, then, and put the operator's *own* strikes on the article's week — the same distance out of the money, on the same names, at their own volatilities. The assignment probability they were actually choosing comes to **10.8%**. That is the Conservative regime, to within a point.

A second reading confirms it without any of that machinery. The names this operator trades carry volatility near 30%, not the running example's 20%, and the median put was written **5.5% out of the money**. At 30% volatility over one week, a one-in-ten strike sits **5.1%** out. Same dial, different strike — which is [eq:kstar](#eq:kstar) doing precisely the job it exists for: the operator picks a frequency, and volatility decides how far away that puts the strike.

So the two regimes bracket practice from above, and Conservative is where a real book sits. Standard leads the worked examples anyway, and the reason is worth being explicit about rather than leaving as inertia. The market of the running example is a **stylized** one — 20% volatility, a 7% total return, a 5% risk-free rate — and p\* = 20% is the round, conventional number that belongs beside them; it is also the calibration practitioners quote to each other. Calibrating the dial alone, while the volatility and the drift stayed round numbers, would suggest more calibration than there is. Little rests on the choice in any case, and [the returns section](#sec:returns) prices exactly how little: halving the dial halves the inventory, the capital and the income, and moves the strategy's advantage over simply owning the stock by less than a tenth of a percentage point — nearly all of which turns out to be an accounting artifact rather than economics.

One thing the dial does *not* account for, and it belongs here so it is not mistaken for a failure of [eq:kstar](#eq:kstar). The model sells a put every week. The live operator skips weeks, writing far fewer puts on any given name than a weekly cadence would, so lots arrive several times more slowly than even the Conservative regime predicts. None of that gap is p\*'s to close: it is an entry filter the model does not contain, and [the live-account section](#sec:live) takes it up.

## How deep does assignment land?

Assignment tells us the stock finished below the strike; it does not say by how much, and that overshoot is what the lot must climb back out of. The quantity has a name here — the lot's **depth** — and its behaviour over time is the subject of everything that follows. At the moment of assignment,

x₀  =  ln( K_c / S )  >  0    {#eq:x0-def}

the log-distance from the price paid to the price the market is offering. Since the log price is normally distributed and assignment is precisely the event that it finished below ln k, the entry depth is a **truncated normal** — the tail of a bell curve, cut at zero and flipped around.[^eq-x0-def]

> **Detour: truncated distributions and conditional expectation.** An ordinary expectation averages over all scenarios. A **conditional expectation** averages only over those in which some event occurred — "the average size of an insurance claim, *given* that a claim was filed". Computing one means cutting the distribution at the event's boundary and averaging what remains; the remaining piece is called a *truncated* distribution. For the normal distribution these truncated averages have closed forms built from the same N(·) used everywhere else. Any text deriving the Black–Scholes formula computes one along the way; [Hull](#ref:hull) covers it.

Writing R = ln(S_τ/S) for the log return over the put's life — normal, with mean (m − σ²/2)·τ_p and spread σ·√τ_p — the entry depth is x₀ = ln k − R conditioned on R < ln k, with density

f(x₀)  =  φ( (ln k − x₀ − (m − σ²/2)·τ_p) / (σ·√τ_p) ) / ( σ·√τ_p · p\* ),   x₀ > 0    {#eq:x0-law}

where φ is the standard normal bell curve. Its mean for the Standard regime is **E[x₀] ≈ 0.0155**: a typical assignment lands about **1.6% below its own strike**. Conservative entries land slightly shallower, E[x₀] ≈ 0.0131 — a strike further out of the money is reached only by a larger move, which then has less of the period left in which to overshoot.

Expressed as a drop from the pre-assignment price rather than from the strike — the form practitioners usually think in — the same result reads

E[d | assignment]  =  1 − e^(m·τ_p) · N(−d₁) / N(−d₂),   d₁ = d₂ + σ·√τ_p    {#eq:d-mean}

giving **3.8%** for Standard and **4.7%** for Conservative. Under the market's drift they are 3.8% and 4.7% as well — the two readings differ in the fourth decimal. Conditioning on assignment does all the work here, and one week of drift is invisible beside it.

Two things about this number deserve emphasis, because guessing it instead of deriving it is the most consequential shortcut available in this subject. First, it costs nothing: it falls out of the same σ and τ_p that priced the option, with no separate assumption. Second, it is **much smaller than intuition suggests**. A weekly put assigned is not a disaster in progress; it is a lot bought about 1.6% under a strike the operator chose on purpose. Whether 1.6% is easy or hard to work off is the question the rest of Part II answers — and the answer is not the comfortable one, because it turns out to have almost nothing to do with the 1.6%.

Live assignments support the shallow picture, and sharpen it in one respect worth stating here. In the account behind this article the ordinary assignment landed in the neighbourhood [eq:d-mean](#eq:d-mean) predicts — the formula sits between that account's median and its average — but the average landed nearly twice as deep as the median, because occasionally a stock does not drift below the strike: it gaps below it on an earnings miss or a profit warning, and the lot arrives a quarter of the way down. A lognormal has no room for that: it is a model of continuous drift and diffusion, and jumps are precisely what it excludes. So the derived depth should be read as a description of the ordinary case, with the understanding that the average is dragged by a tail this model does not contain. Nothing downstream breaks — the tail is rare enough to leave the census and the holding time where they are — but an operator sizing for the worst case should not take E[d | assignment] as the worst case.

## A caveat on exercise style

Both probabilities here are terminal: they ask where the stock is *at expiration*. Listed equity options are American and may be exercised early, so the model is using European mathematics on American contracts. That is a real simplification and it is worth saying what it costs, on each leg separately, because the two legs are not alike.

**On the call leg it does not reach us, and the reason is structural.** [Bakshi and Kapadia](#ref:bakshi-kapadia-2003-jod) measure what the right of early exercise is actually worth and put it at about **two volatility points** — which, at [the returns section](#sec:returns)'s roughly 45 basis points per point, would be the size of the entire claimed edge if it applied. It does not, because their figure is measured on calls *near the money and close to expiry*, and that is exactly the object this strategy never sells: a lot's call strike is frozen at what the operator paid, and a lot only still exists while it is below that strike. Every call written here is written out of the money.

The one channel that could bite is a lot that rises above its strike *mid-period*, with a dividend falling due before the call expires — the classic case, where a call is exercised the day before the stock goes ex-dividend. That pays only when the call's remaining time value has fallen below the dividend about to be collected, and at the running parameters that requires the stock to sit this far above the strike:

    days to expiry        28      21      14       7       3
    stock above strike  5.5%    4.1%    2.8%    1.2%    0.2%

**The threshold defeats itself from both ends.** Early in the period, where an exercise would genuinely shorten the wait, it asks for 5.5% — the whole of one call period's typical move, σ·√τ_c — and it asks for it starting from a lot that was *below* its strike when the period began, so the real requirement is that move plus whatever depth the lot started at. Late in the period the threshold collapses toward nothing, but so does the prize: being exercised three days early rather than at expiry changes almost nothing, because the lot was leaving either way. Early exercise on this leg accelerates departures that were already going to happen. Omitting it is conservative, and this is the size of what is omitted.

**On the put leg the story is different, and the honest version is not the flattering one.** Early exercise of a short put is genuinely common: over fourteen years of six-month contracts, [Merton, Scholes and Gladstein](#ref:merton-scholes-gladstein-1982) found a quarter of out-of-the-money puts exercised before expiry. Ours are weekly rather than six-month, so the window in which it can pay is a small fraction of theirs and the frequency will be far lower — but their own warning is aimed squarely at models like this one: any simulation assuming puts are held to expiration "will systematically… overstate the returns to the writers of puts."

What that costs is **the tail rather than the mean**, which their own results measure: re-running their simulation with early exercise switched off left the average return unchanged and roughly doubled the worst outcome, flipping the skew from positive to negative. And the reason is the one thing that does not carry across to this strategy. For them, early exercise is a *stop-loss* — the put is bought back at intrinsic value and the proceeds sit in cash for the rest of the period, closing the position and truncating the loss. **The wheel has no such exit.** Assignment here does not end the exposure; it converts a short put into a lot that then rides its own price path to its own barrier, which is the subject of the rest of Part II. So a reader who has met that literature should not expect this strategy's put leg to inherit its favorable tail — and the European treatment is the right model of what we do, for a reason that has nothing to do with the American premium being small.

One consequence for anyone extending the pricing: the same authors found that valuing an American put by put–call parity understates it, badly in high-rate periods. This article does not take that shortcut — its put formula is a direct one — but it is the natural shortcut to reach for, and it is a worse approximation than the European assumption it would be trying to repair.

There is also a path-versus-endpoint distinction — the stock may cross a strike mid-period and come back, which a terminal probability never sees. [The holding-time section](#sec:holding) turns that from a caveat into a quantity, because on the call leg the same effect has a name and a measurable size.

[^eq-normal]: Reproduced by `python code/examples/entry_normal.py` — [eq:normal](#eq:normal), [eq:phi](#eq:phi), and the other readings quoted here are `sigma 0.30`; `p-star 0.10`; `measure Q`. Pass `--help` for the full parameter set. The quantity it works on is this section's own log return, and three of its lines are checks rather than readings: [eq:normal](#eq:normal) integrated over the whole line must come to one, the probability below the strike must agree whether it is integrated directly or standardized and read off N, and N must invert N⁻¹.

[^eq-wait]: Reproduced by `python code/examples/entry_wait.py` — [eq:wait](#eq:wait), and the other readings quoted here are `p-star 0.10`; `measure Q`. Pass `--help` for the full parameter set. The simulated columns walk the price path and re-strike a put each period, so they check [eq:kstar](#eq:kstar) end to end rather than re-drawing the distribution the formula already describes. They do not test the independence assumed above, which no simulation of this model could.

[^eq-x0-def]: Reproduced by `python code/examples/entry_depth.py` — [eq:x0-def](#eq:x0-def), [eq:x0-law](#eq:x0-law), [eq:d-mean](#eq:d-mean), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --measure Q`. Pass `--help` for the full parameter set.

[^eq-kstar]: Reproduced by `python code/examples/entry_strike.py` — [eq:kstar](#eq:kstar), [eq:p-screen](#eq:p-screen), [eq:screen-gap](#eq:screen-gap), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --sigma 0.297`. Pass `--help` for the full parameter set.

[^eq-bs-put]: Reproduced by `python code/examples/entry_pricing.py` — [eq:lognormal](#eq:lognormal), [eq:bs-put](#eq:bs-put), [eq:bs-call](#eq:bs-call), and the other readings quoted here are `measure Q`; `delta 0.05 --tau-p 2.0 --sigma 0.30`; `iv-spread 0.03`. Pass `--help` for the full parameter set. This is the module to reach for when trying parameters of your own: it prints which volatility each line used, checks the put's delta against a numerical derivative of its own price rather than against another formula, and asserts put–call parity at every case.
