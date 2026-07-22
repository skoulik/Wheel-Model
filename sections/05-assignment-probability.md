# The Assignment Probability {#sec:assignment}

## Detour: Bernoulli trials

> When something either happens or doesn't — a coin flip, a die roll checked for a six, a put option either assigning or not — probabilists call it a **Bernoulli trial**. Its only parameter is p, the probability the event happens. Strings of independent Bernoulli trials are the atoms from which the more elaborate distributions later in this article are built. Any introductory probability text covers them; Ross's *A First Course in Probability* is a standard choice.

When you sell a put, you are running one Bernoulli trial per period: with probability p it assigns, with probability 1−p it expires worthless. Our first task is to compute p.

## Detour: the normal distribution and N(·)

> The **standard normal distribution** is the familiar bell curve, centered at zero with spread one. Its **cumulative distribution function** N(x) answers: what is the probability that a standard normal random variable lands below x? It is a lookup — every statistics package and spreadsheet provides it. Its inverse N⁻¹ goes the other way, converting a probability into the corresponding threshold. Under the Black–Scholes model of stock prices (next detour), probabilities of price events reduce to evaluations of N at the right argument.

## Detour: the Black–Scholes model

> The **Black–Scholes model** (1973) is the standard mathematical description of stock prices used in option pricing. It assumes the stock's *percentage* changes are random, independent from period to period, and normally distributed — which makes the price itself *lognormally* distributed at any future date. Two parameters govern it: a drift (average growth rate) and a volatility σ (the size of typical fluctuations, annualized). The model is a simplification — real markets have jumps, fat tails, and volatility that changes over time — but it is the shared language in which option prices are quoted, and its probabilities are accurate enough for the structural questions this article asks. Hull's *Options, Futures, and Other Derivatives* is the standard reference.

## The formula

Let k = K/S₀ be the strike expressed as a fraction of the current price, so k = 0.95 means a put struck 5% below the market. Under Black–Scholes, the probability that the stock finishes below the strike at expiration — the assignment probability — is

p = N(−d₂),    d₂ = [−ln(k) + (r − δ − σ²/2) · τ_p] / (σ·√τ_p)    {#eq:p}

where r is the risk-free rate, σ the volatility implied by the option's market price, and δ the stock's **dividend yield** — annual dividends as a fraction of the price.

The dividend yield deserves a word, because the assets this strategy targets pay one (typical quality names run 1.5–4.5% a year; our running example uses δ = 2.5%). A dividend is cash handed out of the company: on the day it is paid, the stock is worth that much less, so a dividend payer's *price* grows slower than its total return by exactly δ. Option prices know this — the market's risk-neutral price drift for a dividend payer is r − δ, not r — which is why δ enters d₂ with a minus sign: at the same strike, a dividend payer is slightly *more* likely to finish below it. (Withholding taxes on the dividend are the owner's problem, not the option market's; they will matter when we count income in [the returns section](#sec:returns), not here.)

**Numerical verification.** For k = 0.95, monthly puts (τ_p = 1/12), σ = 20%, r = 5%, δ = 2.5%: d₂ ≈ 0.90 and p ≈ 18.5%. Traders would loosely call this a "20-delta put." (Strictly, the put's *delta* is N(−d₁) ≈ 17.0% here, a related but distinct quantity from the in-the-money probability N(−d₂) ≈ 18.5%; the two are close for short-dated options and traders conflate them freely. We will always mean the probability.)

## Choosing the strike by target probability

In practice the operator often thinks in the opposite direction: "I want to be assigned about once every five periods — where should I set the strike?" Inverting the formula for a target probability p\*:

k\*(τ_p) = exp( N⁻¹(p\*) · σ·√τ_p + (r − δ − σ²/2) · τ_p )    {#eq:kstar}

For p\* = 20% (N⁻¹(0.20) ≈ −0.842) with the same parameters, k\* ≈ 0.953: a 20% monthly assignment probability corresponds to a strike about 4.7% below the current price.

This inversion is how the strategy's strike parameter is actually set in the rest of the article: the operator fixes p\*, and k floats with volatility and the period length.

## Risk-neutral versus real-world probability

A subtlety that deserves honesty: the p above is the **risk-neutral** probability — the one embedded in option prices. It is not the best forecast of how often assignment actually happens. Real stocks — certainly the fundamentally sound kind this strategy targets — deliver an expected **total return** μ (price growth plus dividends) that exceeds the risk-free rate r. The real-world assignment probability replaces the risk-neutral price drift r − δ with the real-world price drift μ − δ; the dividend yield cancels in the substitution, leaving

p_rw = N( −d₂ + (r − μ) · √τ_p / σ )    {#eq:p-rw}

Since μ > r for equities, the correction term is negative and p_rw < p. The size of the gap is controlled by (μ − r)/σ — the asset's Sharpe ratio — times √τ_p. With a total return μ = 7% in our running example, p_rw ≈ 17.8% versus the risk-neutral 18.5%.

We nonetheless use the risk-neutral p throughout the model, and this is a deliberate choice, not an oversight: it assumes assignments come *more often* than they realistically will, making every downstream result — inventory levels, capital committed — conservative for a fundamentally sound asset. The gap grows with √τ_p, so longer-dated puts are modeled more conservatively relative to reality.

> **[Flagged for revision — see TODO #4]** The model currently mixes probability measures: risk-neutral for the put leg (conservative) and real-world for the call leg (realistic). Both choices are individually defensible, but the policy needs to be stated once, prominently, as a design decision. Likewise, the σ entering p is *implied* volatility while the σ entering real-world dynamics should be *forecast/realized* volatility; the gap between them is precisely the strategy's documented edge and deserves its own discussion.
