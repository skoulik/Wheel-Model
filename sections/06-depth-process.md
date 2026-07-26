# The Depth Process {#sec:depth}

A lot has entered inventory. From here on the operator's situation is entirely described by one number, and the rest of this article is the study of that number.

## The state variable

When a lot is assigned, its call strike is frozen at the price that was paid for it. The market then moves; the strike does not. Everything the operator will experience with that lot — how much premium its calls fetch, how likely it is to be called away, how long its capital stays committed — depends on one quantity, the gap between the frozen strike and the current price:

**x  =  ln( K_c / S )**

Positive x means the stock is below the strike and the lot is stuck; x = 0 means the stock has climbed back to the strike and the lot leaves. Call it the lot's **depth**.

Two features make it the right variable. First, it is *self-contained*: two lots at the same depth face identical prospects regardless of what was paid for them or when, so a single function of x answers every question about a lot. Second, it is a *logarithm*, which converts the stock's multiplicative wandering into ordinary addition — and a quantity that moves by independent additive jolts is the most thoroughly understood object in probability.

> **Detour: the random walk with drift.** A **random walk** is a running total of independent random steps: each period, add a number drawn from the same distribution. If those numbers have a nonzero average, the walk has a **drift** — a systematic tilt in one direction, on top of the wobble. Over many steps the drift accumulates in proportion to time while the wobble accumulates in proportion to the *square root* of time, so drift eventually wins over any fixed distance; but "eventually" can be very long, and before then the wobble dominates. When steps are normally distributed the walk is called Brownian motion with drift, and questions like "when does it first reach zero?" have well-developed answers. Ross's *Introduction to Probability Models* covers both the walk and the first-passage questions used in [the next section](#sec:holding).

## Depth is a random walk, sampled on the call grid

The log price is a random walk with drift; the strike is a constant; so depth is the same walk with the sign flipped. Over a call period of length τ_c the depth changes by

x  →  x  −  ν·τ_c  +  σ·√τ_c · (a standard normal draw)    {#eq:depth-walk}

The depth is dragged *down* — toward exit — at rate ν per year, and jostled by an amount σ·√τ_c each period. At the article's parameters the jostle is 0.2 × √0.25 = **0.10**, ten log-points per quarter, against a downward pull of just 0.025 × 0.25 = **0.006**. Noise beats drift by a factor of sixteen over one period. Depth does not march toward zero; it staggers, and the drift only asserts itself over many periods.

The drift itself is

**ν  =  m − σ²/2  =  μ − δ − σ²/2**    {#eq:nu}

and it deserves unpacking, because all three terms will matter and the last one surprises people.

- **μ, the total return**, pulls depth down: a stock that climbs recovers toward its old strikes. This is where "fundamentally sound asset" stops being a slogan and becomes arithmetic. The assumption is not that the company is admirable; it is that μ is positive and reliable.
- **δ, the dividend yield**, pushes depth back up. A dividend is paid *out of the price* — on the ex-dividend day the stock is worth less by exactly that amount. At a fixed total return, every point of yield is a point of price appreciation the operator does not get, and the climb back to the strike takes correspondingly longer. The stock pays you to wait, and makes you wait longer *because* it pays.
- **σ²/2, the volatility drag**, also pushes depth up, and it is not a modelling artifact. A price that swings symmetrically in percentage terms drifts *downward* in logarithm: gain 20% then lose 20% and you are down 4%. Over long horizons what matters to a multiplicative process is not its average return but its average log return, and the difference is exactly σ²/2. At σ = 20% this costs 2% a year — of the same order as everything else in the formula.

For the running example ν = 7% − 2.5% − 2% = **2.5% per year**, against a typical entry depth of 3.2%. Read that comparison slowly: the drift needs **more than a year** to work off the hole a *typical* assignment starts in, and the typical assignment is the shallow case.

Under the market's pricing drift the same formula gives ν = 5% − 2.5% − 2% = **0.5%**, five times smaller. The market prices this stock as one whose strikes are worked off at a crawl.

## The exit probability at depth x

A lot at depth x is called away at the end of the current call period if the stock closes at or above the strike — that is, if the walk in [eq:depth-walk](#eq:depth-walk) lands at or below zero:

q(x)  =  N( (ν·τ_c − x) / (σ·√τ_c) )    {#eq:qx}

This is the same recovery probability a practitioner would compute for a freshly assigned lot, but written as a *function* rather than a constant — and that difference is the entire content of this article. Evaluated for the running example, quarterly calls:

    depth x        0.032      0.05      0.10      0.15      0.20      0.30
    q(x)           0.398     0.331     0.174     0.075     0.026     0.002

A fresh lot is close to a coin flip: **q ≈ 0.40**, so about two lots in five leave on their first call. Ten log-points down, the odds are one in six. Twenty points down, one in thirty-eight. Thirty points down — a stock that has fallen by a quarter since the lot was bought — the call is a formality, worth nothing and virtually certain to expire.

The collapse is fast because the *drift term is negligible next to the noise*. Over one quarter, ν·τ_c contributes 0.006 while a standard deviation is 0.10; a lot escapes not because the stock is trending up but because it got lucky this quarter. Depth is worked off by luck in the short run and by drift only in the long run, and how long "the long run" takes is [the next section](#sec:holding).

## The premium at depth x

The other thing that depends on depth is what the covered call is worth. A lot at depth x carries a strike sitting e^x above the current price, so in units of that price it is a call struck at e^x, and its quote is the ordinary Black–Scholes call price at that moneyness:

c_c(x)  =  BlackScholesCall( spot = 1, strike = e^x, tenor = τ_c, σ_IV, r, δ )    {#eq:ccx}

    depth x        0.032      0.05      0.10      0.15      0.20      0.30
    c_c(x)        0.0284    0.0221    0.0098    0.0036    0.0011    0.0001

A fresh lot's quarterly call sells for **2.8% of the share price** — a real income stream, better than 11% a year on the value of the shares. A lot ten points down sells for 1.0%. A lot thirty points down sells for **one basis point**: nothing.

Put the two tables side by side and the mechanism driving the whole strategy is visible in one sentence. **Depth simultaneously destroys a lot's chance of leaving and its ability to earn while it waits.** The lots that are stuck are exactly the lots that pay nothing for being stuck. There is no compensating force — the same variable governs both, and governs them in the same direction.

The one thing a deep lot does still collect is its dividend, δ_net per year on the market value of the shares, regardless of depth. For a stuck lot that is the entire return, and it is why [the returns section](#sec:returns) has to take the dividend seriously rather than treating it as a rounding error.

## What the parameters do

Since ν is the only channel through which μ, δ and σ reach the model, their effects are read straight off [eq:nu](#eq:nu):

- **Higher expected return raises ν**, and everything improves. The strategy is a leveraged bet on being right about μ.
- **Higher volatility lowers ν** — quadratically. Volatility is the option seller's friend on the premium side, since it is what makes options worth selling, and its enemy on the inventory side. σ = 30% would cut ν from 2.5% to zero at these parameters, which [the stability section](#sec:stability) shows is not a gradual deterioration but a boundary.
- **Higher dividend yield lowers ν** point for point, while adding δ_net of carry. That trade — a slower climb, paid for in cash — looks like it might be neutral. [The returns section](#sec:returns) shows it is not.

And since ν enters everything downstream, one more observation is worth registering now: **the model has essentially one parameter.** Two configurations with the same ν, σ and τ_c behave identically no matter how they got there — high growth with high yield behaves exactly like modest growth with no yield.
