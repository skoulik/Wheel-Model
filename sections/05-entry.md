# Entry: How Often, and How Deep {#sec:entry}

Everything the wheel does downstream is set by two numbers decided at the moment a put is assigned: **how often** assignment happens, and **how far below the strike** the stock has fallen when it does. This section derives both, and settles which probabilities the article is talking about.

## Detour: Bernoulli trials

> When something either happens or doesn't — a coin flip, a die roll checked for a six, a put option either assigning or not — probabilists call it a **Bernoulli trial**. Its only parameter is p, the probability the event happens. Strings of independent Bernoulli trials are the atoms from which the more elaborate distributions later in this article are built. Any introductory probability text covers them; Ross's *A First Course in Probability* is a standard choice.

Selling a put is one Bernoulli trial per cadence period: with probability p\* it assigns and delivers a lot of stock into inventory, otherwise it expires and the operator keeps the premium and sells another.

## Detour: the normal distribution and N(·)

> The **standard normal distribution** is the familiar bell curve, centered at zero with spread one. Its **cumulative distribution function** N(x) answers: what is the probability that a standard normal random variable lands below x? It is a lookup — every statistics package and spreadsheet provides it. Its inverse N⁻¹ goes the other way, converting a probability into the corresponding threshold. Under the price model below, probabilities of price events reduce to evaluations of N at the right argument.

## Detour: the lognormal price model

> The **Black–Scholes model** (1973) describes a stock price as drifting upward at some average rate while being knocked around by random shocks whose size is set by the volatility σ. Percentage changes are random, independent from period to period, and normally distributed — which makes the price itself *lognormally* distributed at any future date, and makes the **logarithm** of the price an ordinary random walk with drift. That last fact is the one this article leans on hardest. The model is a simplification — real markets have jumps, fat tails, and volatility that changes over time — but it is the shared language in which option prices are quoted, and its probabilities are accurate enough for the structural questions asked here. Hull's *Options, Futures, and Other Derivatives* is the standard reference.

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

which comes to **20.4%** at the Standard strike, a little higher than the 20% that will actually occur. This is worth knowing because p_screen is what a broker's screen displays and what practitioners quote to each other.

The gap between the two worlds has a closed form, and it is the *entire* difference between them. The two drifts differ by μ − r, so over one tenor the argument of N(·) shifts by the asset's Sharpe ratio times the square root of the tenor:

Δd₂  =  (μ − r)·√τ_p / σ  =  0.0139    {#eq:screen-gap}

That is a shift in d₂, not in probability, and the distinction is worth keeping because the two differ by a factor of four here. Converting costs one evaluation of the bell curve at the threshold, φ(N⁻¹(p\*)) ≈ 0.28, which turns 0.0139 into **0.4 percentage points** — precisely the distance from 20.0% to 20.4%. Both readings are small for short-dated options, and both shrink as √τ_p.

(Strictly, the screen usually shows the option's **delta**, N(−d₁) ≈ 19.6% here, rather than the probability of finishing in the money, N(−d₂) ≈ 20.4%. The two are close for short-dated options and traders conflate them freely. This article always means a probability.)

## Where a real operator sits on the dial

Two regimes are two settings of one dial, and it is fair to ask which of them describes practice. The account behind this article answers that, though not at first glance. Over fourteen months, 921 of its put contracts can be priced against the market on the day they were written, and 71 of those were assigned — **7.7%**, apparently more cautious than either regime on offer.

That number is not comparable, for two reasons that push it the same way. The first is the drift: the window was a bull market, its held names running at roughly +34% a year against the +4.5% assumed here, and a stock that is climbing finishes below the same strike less often. The second is that **a week is not seven days of market**. The account's dominant put is written Monday at the open and expires Friday at the close — five trading sessions, the weekend contributing nothing but a date. That is also exactly what this article's weekly tenor is worth: 1/52 of a year is 4.85 of the 252 sessions a year contains. The two clocks agree; it is only raw calendar arithmetic, which reads that put as four days rather than five sessions, that makes them look different.

Correct for the drift, then, and put the operator's *own* strikes on the article's week — the same distance out of the money, on the same names, at their own volatilities. The assignment probability they were actually choosing comes to **10.9%**. That is the Conservative regime, to within a point.

A second reading confirms it without any of that machinery. The names this operator trades carry volatility near 30%, not the running example's 20%, and the median put was written **5.5% out of the money**. At 30% volatility over one week, a one-in-ten strike sits **5.1%** out. Same dial, different strike — which is [eq:kstar](#eq:kstar) doing precisely the job it exists for: the operator picks a frequency, and volatility decides how far away that puts the strike.

So the two regimes bracket practice from above, and Conservative is where a real book sits. Standard leads the worked examples anyway, and the reason is worth being explicit about rather than leaving as inertia. The market of the running example is a **stylized** one — 20% volatility, a 7% total return, a 5% risk-free rate — and p\* = 20% is the round, conventional number that belongs beside them; it is also the calibration practitioners quote to each other. Calibrating the dial alone, while the volatility and the drift stayed round numbers, would suggest more calibration than there is. Little rests on the choice in any case, and [the returns section](#sec:returns) prices exactly how little: halving the dial halves the inventory, the capital and the income, and moves the strategy's advantage over simply owning the stock by less than a tenth of a percentage point — nearly all of which turns out to be an accounting artifact rather than economics.

One thing the dial does *not* account for, and it belongs here so it is not mistaken for a failure of [eq:kstar](#eq:kstar). The model sells a put every week. The live operator skips weeks, writing far fewer puts on any given name than a weekly cadence would, so lots arrive several times more slowly than even the Conservative regime predicts. None of that gap is p\*'s to close: it is an entry filter the model does not contain, and [the live-account section](#sec:live) takes it up.

## How deep does assignment land?

Assignment tells us the stock finished below the strike; it does not say by how much, and that overshoot is what the lot must climb back out of. The quantity has a name here — the lot's **depth** — and its behaviour over time is the subject of everything that follows. At the moment of assignment,

x₀  =  ln( K_c / S )  >  0    {#eq:x0-def}

the log-distance from the price paid to the price the market is offering. Since the log price is normally distributed and assignment is precisely the event that it finished below ln k, the entry depth is a **truncated normal** — the tail of a bell curve, cut at zero and flipped around.[^eq-x0-def]

> **Detour: truncated distributions and conditional expectation.** An ordinary expectation averages over all scenarios. A **conditional expectation** averages only over those in which some event occurred — "the average size of an insurance claim, *given* that a claim was filed". Computing one means cutting the distribution at the event's boundary and averaging what remains; the remaining piece is called a *truncated* distribution. For the normal distribution these truncated averages have closed forms built from the same N(·) used everywhere else. Any text deriving the Black–Scholes formula computes one along the way; Hull covers it.

Writing z = ln(S_T/S) for the log return over the put's life — normal, with mean (m − σ²/2)·τ_p and standard deviation σ·√τ_p — the entry depth is x₀ = ln k − z conditioned on z < ln k, with density

f(x₀)  =  φ( (ln k − x₀ − (m − σ²/2)·τ_p) / (σ·√τ_p) ) / ( σ·√τ_p · p\* ),   x₀ > 0    {#eq:x0-law}

where φ is the standard normal bell curve. Its mean for the Standard regime is **E[x₀] ≈ 0.0155**: a typical assignment lands about **1.6% below its own strike**. Conservative entries land slightly shallower, E[x₀] ≈ 0.0131 — a strike further out of the money is reached only by a larger move, which then has less of the period left in which to overshoot.

Expressed as a drop from the pre-assignment price rather than from the strike — the form practitioners usually think in — the same result reads

E[d | assignment]  =  1 − e^(m·τ_p) · N(−d₁) / N(−d₂),   d₁ = d₂ + σ·√τ_p    {#eq:d-mean}

giving **3.8%** for Standard and **4.7%** for Conservative. Under the market's drift they are 3.8% and 4.7% as well — the two readings differ in the fourth decimal. Conditioning on assignment does all the work here, and one week of drift is invisible beside it.

Two things about this number deserve emphasis, because guessing it instead of deriving it is the most consequential shortcut available in this subject. First, it costs nothing: it falls out of the same σ and τ_p that priced the option, with no separate assumption. Second, it is **much smaller than intuition suggests**. A weekly put assigned is not a disaster in progress; it is a lot bought about 1.6% under a strike the operator chose on purpose. Whether 1.6% is easy or hard to work off is the question the rest of Part II answers — and the answer is not the comfortable one, because it turns out to have almost nothing to do with the 1.6%.

Live assignments support the shallow picture, and sharpen it in one respect worth stating here. In the account behind this article the ordinary assignment landed in the neighbourhood [eq:d-mean](#eq:d-mean) predicts — the formula sits between that account's median and its average — but the average landed nearly twice as deep as the median, because occasionally a stock does not drift below the strike: it gaps below it on an earnings miss or a profit warning, and the lot arrives a quarter of the way down. A lognormal has no room for that: it is a model of continuous drift and diffusion, and jumps are precisely what it excludes. So the derived depth should be read as a description of the ordinary case, with the understanding that the average is dragged by a tail this model does not contain. Nothing downstream breaks — the tail is rare enough to leave the census and the holding time where they are — but an operator sizing for the worst case should not take E[d | assignment] as the worst case.

## A caveat on exercise style

Both probabilities here are terminal: they ask where the stock is *at expiration*. Listed equity options are American and may be exercised early. For short puts the approximation is good — early exercise of a put is rare, and slightly raises the effective assignment rate. For covered calls on dividend payers it is not negligible: a deep in-the-money call is often exercised the day before the stock goes ex-dividend, which shortens holding periods and therefore *helps* the strategy, so omitting it is conservative. There is also a path-versus-endpoint distinction — the stock may cross a strike mid-period and come back, which a terminal probability never sees. [The holding-time section](#sec:holding) turns that from a caveat into a quantity, because on the call leg the same effect has a name and a measurable size.

[^eq-x0-def]: Reproduced by `python code/examples/entry_depth.py` — [eq:x0-def](#eq:x0-def), [eq:x0-law](#eq:x0-law), [eq:d-mean](#eq:d-mean), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --measure Q`. Pass `--help` for the full parameter set.

[^eq-kstar]: Reproduced by `python code/examples/entry_strike.py` — [eq:kstar](#eq:kstar), [eq:p-screen](#eq:p-screen), [eq:screen-gap](#eq:screen-gap), and the other readings quoted here are `measure Q`; `p-star 0.10`; `p-star 0.10 --sigma 0.297`. Pass `--help` for the full parameter set.
