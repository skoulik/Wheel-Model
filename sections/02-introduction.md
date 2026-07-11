# Introduction {#sec:introduction}

## The strategy, informally

Among retail and semi-professional option traders there is a popular income strategy known as **the wheel**. In its simplest telling: pick a stock you would not mind owning — a large, dividend-paying company unlikely to collapse permanently, trading at an attractive price — and sell a put option on it. (What makes a price "attractive" is a question of valuation, and answering it is beyond the scope of this article; we assume the operator has a defensible answer.) Selling a put means accepting an obligation: if the stock falls below a chosen level (the *strike price*) by the option's expiration, you must buy the stock at that strike. In exchange, you collect a cash payment upfront (the *premium*). Done prudently — with enough cash set aside to honor the purchase in full — the position is called a *cash-secured put*.

Each period there are two outcomes. If the stock stays above the strike, the put expires worthless, you keep the premium, and you sell another put. If the stock falls below the strike, you are *assigned*: you buy the shares at the strike, paying more than they are now worth. How often each outcome occurs is not a matter of luck but of choice — the further below the current price you set the strike, the rarer assignment becomes and the smaller the premium you are paid. A practitioner of the wheel typically sets the strike so that assignment is the exception rather than the rule (a probability around one in five per period is a common calibration, and the one we use in examples); making that trade-off precise is one of the first tasks of the model. The wheel's answer to this is not to sell in a panic but to turn around and sell a *covered call* against the newly acquired shares — the mirror-image obligation: promising to sell the stock at a chosen strike if it recovers there ("covered" because the shares to be delivered are already in hand), again collecting a premium. Should the stock eventually recover and the shares be *called away*, the cycle — the wheel — begins again.

> **Detour: payoff diagrams, and two names for one trade.** The standard picture for an option position is its *payoff diagram*: the horizontal axis is the stock price when the option expires, the vertical axis is the position's profit. Here are the wheel's two building blocks side by side (K is the strike, c the premium collected):
>
> ```
>      cash-secured put                     covered call
>   (cash + short put at K)          (shares + short call at K)
>
>  profit                            profit
>    │                                 │
>  +c┤ ·····┌────────────            +c┤ ·····┌────────────
>    │     /                           │     /
>   0┼────/─┴───────────→             0┼────/─┴───────────→
>    │   /  K                          │   /  K
>    │  /                              │  /
>    │ /                               │ /
>
>          (horizontal axis: stock price at expiration)
> ```
>
> Each picture reads the same way: end below the strike and the position loses dollar-for-dollar with the stock, cushioned only by the premium; end anywhere above and the profit is capped at c. The two pictures are identical, and that is the point: **at the same strike, a cash-secured put and a covered call have the same payoff.** Holding cash you have promised to spend at K is the same bet as holding shares you have promised to sell at K — either way, you keep the downside below the strike, give away the upside above it, and are paid a premium for the pair. (The formal version of this statement is *put–call parity*; any derivatives text covers it — Hull's *Options, Futures, and Other Derivatives* is the standard reference.)
>
> This symmetry recasts the wheel: its two phases are one trade in two costumes. Whether waiting to buy (short put, cash in reserve) or waiting to sell (short call, shares in hand), the operator holds the same payoff shape and re-sells the same promise each period; what alternates is only the collateral. The equivalence is about payoffs, not prices — the market does not pay equally for the two legs, because option buyers bid up downside strikes relative to upside ones (the *volatility skew*), making puts typically the richer side to sell. We set the skew aside in this detour.

Practitioners describe the strategy in comfortable terms: "you get paid to wait," "assignment just means buying a good company at a discount." These slogans contain truth, but they are not a model. They give no way to answer quantitative questions: How often will I be assigned? How much stock will I end up holding in a falling market? How much capital does this strategy really consume? What is the actual return once opportunity cost is charged? Under what market conditions does the comfortable picture break down?

## Our approach: the wheel as an inventory system

The central idea of this article is that the wheel is a **stochastic inventory system**, and that recognizing this unlocks a well-developed mathematical toolkit. Each put sold is a trial that, with some probability p, delivers a *lot* of stock into inventory. Each lot held in inventory has, per period, some probability of being removed — called away — with a capital gain. Arrivals compete with departures, and the questions above become classical questions about a queue: What is the average inventory level? How does it fluctuate? When does it stay bounded, and when does it grow without limit?

## Contributions

Working under an explicitly stated homogeneous approximation (all inventory lots behave alike), we derive:

1. **The assignment probability** p of a single put from the Black–Scholes framework, its inversion (choosing the strike to hit a target assignment probability), and the correction from risk-neutral to real-world probability — including why using the risk-neutral figure is a deliberately conservative choice.
2. **The recovery probability** q that an assigned lot is called away within one call period, and how it depends on the depth of the drawdown that caused assignment.
3. **The steady-state inventory distribution** — approximately Poisson with mean I\* = p·(τ_c/τ_p)/q — and the *self-recycling property*: in equilibrium the strategy sheds inventory at exactly the rate it acquires it.
4. **The realized income run rate and the capital committed** in steady state, kept in strictly separated accounting tracks (realized cash, market-priced capital, opportunity cost), and a convergence bound showing that under geometric price decline, total committed capital stays bounded even as lots accumulate.
5. **The failure modes** of the homogeneous approximation — inventory layers acquired at higher prices unwind more slowly than fresh ones, and stress moves p up and q down simultaneously — which set the agenda for the depth-dependent model of tier 2.

## How to read this article

The article is written for a general, numerate audience. We assume comfort with basic algebra and a willingness to meet a few probability concepts, each of which is introduced in a short self-contained detour at the point it is first needed, with pointers to further reading. Every modeling assumption is stated explicitly and its cost discussed; every parameter is explained when introduced. All numerical examples in the text are reproducible.
