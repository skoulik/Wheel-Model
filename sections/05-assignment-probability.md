# The Assignment Probability

## Detour: Bernoulli trials

> When something either happens or doesn't — a coin flip, a die roll checked for a six, a put option either assigning or not — probabilists call it a **Bernoulli trial**. Its only parameter is p, the probability the event happens. Strings of independent Bernoulli trials are the atoms from which the more elaborate distributions later in this article are built. Any introductory probability text covers them; Ross's *A First Course in Probability* is a standard choice.

When you sell a put, you are running one Bernoulli trial per period: with probability p it assigns, with probability 1−p it expires worthless. Our first task is to compute p.

## Detour: the normal distribution and N(·)

> The **standard normal distribution** is the familiar bell curve, centered at zero with spread one. Its **cumulative distribution function** N(x) answers: what is the probability that a standard normal random variable lands below x? It is a lookup — every statistics package and spreadsheet provides it. Its inverse N⁻¹ goes the other way, converting a probability into the corresponding threshold. Under the Black–Scholes model of stock prices (next detour), probabilities of price events reduce to evaluations of N at the right argument.

## Detour: the Black–Scholes model

> The **Black–Scholes model** (1973) is the standard mathematical description of stock prices used in option pricing. It assumes the stock's *percentage* changes are random, independent from period to period, and normally distributed — which makes the price itself *lognormally* distributed at any future date. Two parameters govern it: a drift (average growth rate) and a volatility σ (the size of typical fluctuations, annualized). The model is a simplification — real markets have jumps, fat tails, and volatility that changes over time — but it is the shared language in which option prices are quoted, and its probabilities are accurate enough for the structural questions this article asks. Hull's *Options, Futures, and Other Derivatives* is the standard reference.

## The formula

Let k = K/S₀ be the strike expressed as a fraction of the current price, so k = 0.95 means a put struck 5% below the market. Under Black–Scholes, the probability that the stock finishes below the strike at expiration — the assignment probability — is

p = N(−d₂),    d₂ = [−ln(k) + (r − σ²/2) · τ_p] / (σ·√τ_p)

where r is the risk-free rate and σ the volatility implied by the option's market price.

**Numerical verification.** For k = 0.95, monthly puts (τ_p = 1/12), σ = 20%, r = 5%: d₂ ≈ 0.93 and p ≈ 17.6%. Traders would loosely call this a "20-delta put." (Strictly, the put's *delta* is N(−d₁) ≈ 16% here, a related but distinct quantity from the in-the-money probability N(−d₂) ≈ 18%; the two are close for short-dated options and traders conflate them freely. We will always mean the probability.)

## Choosing the strike by target probability

In practice the operator often thinks in the opposite direction: "I want to be assigned about once every five periods — where should I set the strike?" Inverting the formula for a target probability p\*:

k\*(τ_p) = exp( N⁻¹(p\*) · σ·√τ_p + (r − σ²/2) · τ_p )

For p\* = 20% (N⁻¹(0.20) ≈ −0.842) with the same parameters, k\* ≈ 0.955: a 20% monthly assignment probability corresponds to a strike about 4.5% below the current price.

This inversion is how the strategy's strike parameter is actually set in the rest of the article: the operator fixes p\*, and k floats with volatility and the period length.

## Risk-neutral versus real-world probability

A subtlety that deserves honesty: the p above is the **risk-neutral** probability — the one embedded in option prices. It is not the best forecast of how often assignment actually happens. Real stocks — certainly the fundamentally sound, dividend-paying kind this strategy targets — drift upward over time at some rate μ that exceeds the risk-free rate r. The real-world assignment probability replaces r with μ, which after simplification gives

p_rw = N( −d₂ + (r − μ) · √τ_p / σ )

Since μ > r for equities, the correction term is negative and p_rw < p. The size of the gap is controlled by (μ − r)/σ — the asset's Sharpe ratio — times √τ_p. With μ = 7% in our running example, p_rw ≈ 16.8% versus the risk-neutral 17.6%.

We nonetheless use the risk-neutral p throughout the model, and this is a deliberate choice, not an oversight: it assumes assignments come *more often* than they realistically will, making every downstream result — inventory levels, capital committed — conservative for a fundamentally sound asset. The gap grows with √τ_p, so longer-dated puts are modeled more conservatively relative to reality.

> **[Flagged for revision — see TODO #4]** The model currently mixes probability measures: risk-neutral for the put leg (conservative) and real-world for the call leg (realistic). Both choices are individually defensible, but the policy needs to be stated once, prominently, as a design decision. Likewise, the σ entering p is *implied* volatility while the σ entering real-world dynamics should be *forecast/realized* volatility; the gap between them is precisely the strategy's documented edge and deserves its own discussion.
