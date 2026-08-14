# The Depth Process {#sec:depth}

A lot has entered inventory. From here on the operator's situation is entirely described by one number, and the rest of this article is the study of that number.

## The state variable

When a lot is assigned, its call strike is frozen at the price that was paid for it. The market then moves; the strike does not. Everything the operator will experience with that lot — how much premium its calls fetch, how likely it is to be called away, how long its capital stays committed — depends on one quantity, the gap between the frozen strike and the current price:

x  =  ln( K_c / S )    {#eq:depth-def}

Positive x means the stock is below the strike and the lot is stuck; x = 0 means the stock has climbed back to the strike and the lot leaves. Call it the lot's **depth** — a distance rather than a direction: it deepens as the stock falls, shallows as the stock recovers, and the way out is shallower.

Two features make it the right variable. First, it is *self-contained*: two lots at the same depth face identical prospects regardless of what was paid for them or when, so a single function of x answers every question about a lot. Second, it is a *logarithm*, which converts the stock's multiplicative wandering into ordinary addition — and a quantity that moves by independent additive jolts is the most thoroughly understood object in probability.

> **Detour: the random walk with drift.** A **random walk** is a running total of independent random steps: each period, add a number drawn from the same distribution. If those numbers have a nonzero average, the walk has a **drift** — a systematic tilt in one direction, on top of the wobble. Over many steps the drift accumulates in proportion to time while the wobble accumulates in proportion to the *square root* of time, so drift eventually wins over any fixed distance; but "eventually" can be very long, and before then the wobble dominates. When steps are normally distributed the walk is called Brownian motion with drift, and questions like "when does it first reach zero?" have well-developed answers. [Ross's *Introduction to Probability Models*](#ref:ross-probability-models) covers both the walk and the first-passage questions used in [the next section](#sec:holding).

## Depth is a random walk, sampled on the call grid

The log price is a random walk with drift; the strike is a constant; so depth is the same walk with the sign flipped. Over a call period of length τ_c the depth changes by

x  →  x  −  ν·τ_c  +  σ·√τ_c · (a standard normal draw)    {#eq:depth-walk}

Depth is drawn *toward exit* at rate ν per year, and jostled by an amount σ·√τ_c each period. At the article's parameters the jostle is 0.2 × √(1/13) = **0.055**, five and a half log-points per four-week period, against a pull toward exit of just 0.025 ÷ 13 = **0.0019**. Noise beats drift by a factor of twenty-nine over one period. Depth does not march toward zero; it staggers, and the drift only asserts itself over many periods.

The drift itself is

**ν  =  m − σ²/2  =  μ − δ − σ²/2**    {#eq:nu}

and it deserves unpacking, because all three terms will matter and the last one surprises people.

- **μ, the total return**, makes lots shallower: a stock that climbs recovers toward its old strikes. This is where "fundamentally sound asset" stops being a slogan and becomes arithmetic. The assumption is not that the company is admirable; it is that μ is positive and reliable.
- **δ, the dividend yield**, keeps them deeper. A dividend is paid *out of the price* — on the ex-dividend day the stock is worth less by exactly that amount. At a fixed total return, every point of yield is a point of price appreciation the operator does not get, and the climb back to the strike takes correspondingly longer. The stock pays you to wait, and makes you wait longer *because* it pays. What holding δ *constant* commits us to is the next subsection.
- **σ²/2, the volatility drag**, also keeps them deeper, and it is not a modelling artifact. A price that swings symmetrically in percentage terms drifts *downward* in logarithm: gain 20% then lose 20% and you are down 4%. Over long horizons what matters to a multiplicative process is not its average return but its average log return, and the difference is exactly σ²/2. At σ = 20% this costs 2% a year — of the same order as everything else in the formula.

For the running example ν = 7% − 2.5% − 2% = **2.5% per year**, against a typical entry depth of 1.55%. Read that comparison slowly: the drift needs **the better part of a year** to work off the hole a *typical* assignment starts in, and the typical assignment is the shallow case.

Under the market's pricing drift the same formula gives ν = 5% − 2.5% − 2% = **0.5%**, five times smaller. The market prices this stock as one whose strikes are worked off at a crawl.

## What a constant dividend yield assumes

δ is a single number throughout this article, and it is worth being exact about what that commits us to, because the natural misreading is severe.

A constant yield does **not** say the company cuts its dividend whenever the price falls. It says the payout tracks the price's *trend*. A company raising its dividend at the price's log drift ν has, by construction, a constant yield — the price and the payout compound together — and that is precisely the dividend aristocrat of [the strategy section](#sec:strategy), not a company that trims its cheque every time the stock has a bad quarter. The model is therefore right about the trend, and the assumption is doing exactly the work it appears to.

What a constant yield leaves out is the *fluctuation* around that trend. Between raises the payout is fixed in dollars, so a price that falls 30% without a matching cut leaves the yield 43% higher, and the operator waiting out a drawdown collects more than δ while they wait. That is real, and two things bound how much it can matter.

First, it is a property of the *market level*, not of a lot's depth. Every share of one company pays the same cash on the same day, so a lot 40% below its own frozen strike and a freshly assigned lot receive identical dividends. Depth is measured against a lot's own strike, which is a private accident of when it was bought; the yield is measured against the market. The two are different variables and they do not interact. Whatever a sticky dividend does, it does not pay deep lots more than shallow ones.

Second, the effect and its own justification pull in opposite directions. The correction grows with how long a payout stands unchanged, and the deviation between price and payout accumulates like σ·√t. The lot that exits in eight weeks — the median lot, by [the holding-time section](#sec:holding) — has given the price no time to wander, so the correction is nil. The lot still held after a decade has a large correction and has also long since outlived the premise, because over a decade both its dividend and the market have moved a great deal. **The correction is negligible where the assumption is safe and unsafe where the correction is large.** [The returns section](#sec:returns) prices it out and gets four basis points.

## The exit probability at depth x

A lot at depth x is called away at the end of the current call period if the stock closes at or above the strike — that is, if the walk in [eq:depth-walk](#eq:depth-walk) lands at or below zero:

q(x)  =  N( (ν·τ_c − x) / (σ·√τ_c) )    {#eq:qx}

This is the same recovery probability a practitioner would compute for a freshly assigned lot, but written as a *function* rather than a constant — and that difference is the entire content of this article. Evaluated for the running example, four-week calls:

    depth x        0.0155     0.03      0.05      0.10      0.15      0.20
    q(x)            0.404     0.306     0.193     0.039     0.004     0.000

A fresh lot is close to a coin flip: **q ≈ 0.40**, so about two lots in five leave on their first call. Five log-points down, the odds are one in five. Ten points down, one in twenty-six. Fifteen points down, one in two hundred and sixty. Twenty points down — a stock that has fallen by a fifth since the lot was bought — the call is a formality, worth nothing and virtually certain to expire.

The collapse is fast because the *drift term is negligible next to the noise*. Over one four-week period, ν·τ_c contributes 0.0019 while a standard deviation is 0.055; a lot escapes not because the stock is trending up but because it got lucky this month. Depth is worked off by luck in the short run and by drift only in the long run, and how long "the long run" takes is [the next section](#sec:holding).

Notice how much steeper this collapse is than it would be on a slower call clock. The scale on which depth matters is the one period's jostle σ·√τ_c, so shortening the call period does not merely change the units — it moves the cliff edge closer. A lot ten points under water is a live position against a quarterly call and a dead one against a four-week call.

## The premium at depth x

The other thing that depends on depth is what the covered call is worth. A lot at depth x carries a strike sitting e^x above the current price, so in units of that price it is a call struck at e^x, and its quote is the ordinary Black–Scholes call price at that moneyness:

c_c(x)  =  BlackScholesCall( spot = 1, strike = e^x, tenor = τ_c, σ_IV, r, δ )    {#eq:ccx}

    depth x        0.0155     0.03      0.05      0.10      0.15      0.20
    c_c(x)         0.0161   0.0110    0.0060    0.0009    0.0001    0.0000

A fresh lot's four-week call sells for **1.6% of the share price** — a real income stream, better than 20% a year on the value of the shares. A lot ten points down sells for 0.09%. A lot fifteen points down sells for **one basis point**: nothing.

Put the two tables side by side and the mechanism driving the whole strategy is visible in one sentence. **Depth simultaneously destroys a lot's chance of leaving and its ability to earn while it waits.** The lots that are stuck are exactly the lots that pay nothing for being stuck. There is no compensating force — the same variable governs both, and governs them in the same direction.

The one thing a deep lot does still collect is its dividend — and "regardless of depth" is the point, not a convenience. δ_net accrues on the *market value* of the shares, at the same rate for every lot in the book, because the company pays the same cash on every share it has issued and has no idea what any particular lot cost. For a stuck lot that dividend is the entire return, and it is why [the returns section](#sec:returns) has to take the dividend seriously rather than treating it as a rounding error.

One trap to name, since it is where an operator's own arithmetic will disagree with the model. Measured against what a deep lot *cost*, its yield has fallen — you paid 100, the price is 60, and you are collecting 2.5% of 60 rather than of 100. Measured against what the shares are *worth today*, it has not moved. The second is the right measure here for the same reason [the returns section](#sec:returns) uses market value for capital: the 40 is a loss that has already happened, not a commitment still being funded. Yield on cost feels like the honest number and is the one convention that double-counts the drawdown.

## What the parameters do

Since ν is the only channel through which μ, δ and σ reach the model, their effects are read straight off [eq:nu](#eq:nu):

- **Higher expected return raises ν**, and everything improves. The strategy is a leveraged bet on being right about μ.
- **Higher volatility lowers ν** — quadratically. Volatility is the option seller's friend on the premium side, since it is what makes options worth selling, and its enemy on the inventory side. σ = 30% would cut ν from 2.5% to zero at these parameters, which [the stability section](#sec:stability) shows is not a gradual deterioration but a boundary.
- **Higher dividend yield lowers ν** point for point, while adding δ_net of carry. That trade — a slower climb, paid for in cash — looks like it might be neutral. [The returns section](#sec:returns) shows it is not.

And since ν enters everything downstream, one more observation is worth registering now: **the model has essentially one parameter.** Two configurations with the same ν, σ and τ_c behave identically no matter how they got there — high growth with high yield behaves exactly like modest growth with no yield.
