# Introduction

## The strategy, informally

Among retail and semi-professional option traders there is a popular income strategy known as **the wheel**. In its simplest telling: pick a stock you would not mind owning — a large, dividend-paying company unlikely to collapse permanently, trading at an attractive price — and sell a put option on it. (What makes a price "attractive" is a question of valuation, and answering it is beyond the scope of this article; we assume the operator has a defensible answer.) Selling a put means accepting an obligation: if the stock falls below a chosen level (the *strike price*) by the option's expiration, you must buy the stock at that strike. In exchange, you collect a cash payment upfront (the *premium*).

Each period there are two outcomes. If the stock stays above the strike, the put expires worthless, you keep the premium, and you sell another put. If the stock falls below the strike, you are *assigned*: you buy the shares at the strike, paying more than they are now worth. How often each outcome occurs is not a matter of luck but of choice — the further below the current price you set the strike, the rarer assignment becomes and the smaller the premium you are paid. A practitioner of the wheel typically sets the strike so that assignment is the exception rather than the rule (a probability around one in five per period is a common calibration, and the one we use in examples); making that trade-off precise is one of the first tasks of the model. The wheel's answer to this is not to sell in a panic but to turn around and sell a *covered call* against the newly acquired shares — the mirror-image obligation, promising to sell the stock at a chosen strike if it recovers there, again collecting a premium. Should the stock eventually recover and the shares be *called away*, the cycle — the wheel — begins again.

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
