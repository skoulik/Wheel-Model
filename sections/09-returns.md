# Returns and Capital {#sec:returns}

Now the question the whole model was built to answer. All quantities below are per unit of the current share price, so "capital of 5.08" means five times what one share costs today, and an income of 0.33 means a third of a share price per year.

## What comes in

Take the Standard regime at a thirty-year horizon, which by [the inventory section](#sec:inventory) means 4.89 lots held on average. Cash arrives from three places:

    put premiums      0.0753 per year     one put a month, at 0.63% each
    call premiums     0.1495 per year     4.89 lots, each selling a call a quarter
    dividends         0.1038 per year     δ_net on the market value of 4.89 lots
    ------------------------------------
    Track A income    0.3287 per year    {#eq:income}

A third of a share price per year, in cash, realized. It is a genuinely impressive-looking number, and it is the number that makes this strategy popular. Note also what the composition says: **the calls out-earn the puts two to one**, and the dividends nearly match the puts. The strategy is named after selling puts, but by the time it is running at scale, put premium is its smallest cash source.

The number is also, on its own, meaningless. It says nothing until we ask what had to be tied up to earn it.

## What is tied up

Two different quantities can be called "the capital", and choosing between them decides the answer.

**Cost basis.** The operator paid k per share for 4.89 lots. Summed, and expressed against today's price, that comes to **7.82**. This is the number a spreadsheet of purchases produces, and it is what practitioners usually mean by "capital deployed".

**Market value.** Those same shares can be sold today for what the market pays: 4.89 share prices, plus margin on the live put, for a total of **5.08**.

The gap between them — 2.7 share prices — is the accumulated paper loss on the standing inventory, which is large precisely because the census in [the inventory section](#sec:inventory) is dominated by deep lots.

The right choice for measuring *return* is market value, and the reason is worth stating carefully because the other choice is so tempting. Capital committed means capital that could otherwise be doing something else. A share bought at 100 and now worth 60 does not commit 100 to the strategy; it commits 60, because 60 is what selling it would release. The other 40 is gone — it is a loss that has already happened, not an ongoing commitment. Charging opportunity cost on it counts the same loss twice: once when the price fell, and again every year afterwards.

This is also what [the strategy section](#sec:strategy) promised — Track B was defined as capital at market prices — and it is the definition that survives the consistency test in [the verification section](#sec:verification), which the cost-basis version fails.

E[Capital]  =  γ·k  +  E[I]    {#eq:capital}

## What Track A leaves out

Cash accounting is internally consistent but it is not a return, because two real economic events pass through it without leaving a trace.

**The mark loss at acquisition.** A lot is bought at the strike while the market offers less. That difference is a loss the moment it happens. Track A calls it "acquisition at the operator's chosen basis" and books nothing. Over a year of arrivals it comes to **0.0795**.

**The upside surrendered at call-away.** When a lot is called away, the shares are delivered at the strike while the market is *above* the strike — that is precisely why the call was exercised. The operator hands over something worth more than what they receive. Track A sees an exit at the same price as the entry and books nothing. Over a year this comes to **0.1393**, larger than the put premiums.

Against those, one real gain is also invisible to Track A: the **appreciation of shares held**, which for 4.89 lots drifting at m = 4.5% is **0.2199** a year.

Add all three and something striking happens:

    appreciation of held shares    +0.2199
    mark loss at acquisition       −0.0795
    upside surrendered             −0.1393
    -------------------------------------
    net                            +0.0011

**They cancel.** The gain that Track A ignores is almost exactly consumed by the two costs Track A ignores. That is not a coincidence — it is what near-fair option pricing means — and it has a convenient consequence: the honest economic return is Track A's cash income, measured against *market-value* capital.

E[Π]  =  Track A income  +  E[I]·m  −  (mark loss)  −  (upside surrendered)    {#eq:econ-pnl}

**True excess return  =  ( E[Π] − r · E[Capital] ) / E[Capital]**    {#eq:excess}

= (0.3297 − 0.05 × 5.077) / 5.077 = **+1.49% per year**.

## The two ledgers, side by side

| Standard regime | 5 y | 10 y | 30 y |
|---|---|---|---|
| lots held | 2.22 | 3.10 | 4.89 |
| capital, market value | 2.41 | 3.29 | 5.08 |
| capital, cost basis | 2.82 | 4.18 | 7.82 |
| **true excess return** | **+1.39%** | **+1.43%** | **+1.49%** |
| cash income on cost basis | +3.73% | +1.64% | −0.80% |

The true excess return is nearly flat across horizons, as a genuine risk premium should be: the position earns what it earns, whatever size it has grown to.

The cash-on-cost-basis line does something else entirely, and it is worth understanding because **it is what an operator's own records will show them**. Early on it is spectacular — a strategy apparently earning 3.7% over T-bills. Then it decays, crosses zero somewhere around year twenty, and keeps falling. Nothing in the strategy has changed. What changes is that cost basis keeps inflating relative to market value as deep lots accumulate, so the denominator grows while the numerator does not. An operator watching this happen will conclude the strategy has stopped working. It has not; the measurement was wrong at both ends — too flattering at the start, too damning later.

> **A pitfall worth naming.** There is a second, popular way to get this wrong. Under the "net cost basis" convention an assigned lot is booked at strike minus premium, so the exit at the strike shows a *capital gain of exactly the put premium* — the premium apparently recovered a second time at the exit door. The recycling image is appealing and the arithmetic is a double count: the premium was already booked as income when it was received. Any of these conventions is fine applied consistently; the failure mode is mixing the income of one with the capital of another, which is exactly what "cash income on cost basis" does.

## The benchmark that matters

An excess return of +1.49% over the risk-free rate sounds like a verdict. It isn't, because T-bills are the wrong comparison. This strategy keeps over 90% of its capital in equity — 96% at the thirty-year mark, and [the inventory section](#sec:inventory)'s census shows the warehouse is rarely empty — so the relevant question is not whether it beats cash but whether it beats **owning the stock**.

Buying and holding the same stock earns μ − r − w·δ = **+1.63%** over the risk-free rate, or **+1.56%** after scaling by the wheel's 96% equity exposure. Against the wheel's +1.49%:

| Standard regime, 30 y | excess return |
|---|---|
| the wheel | +1.49% |
| buy and hold, equity-adjusted | +1.56% |
| **difference** | **−0.07%** |

**At fair option prices the wheel is economically identical to owning the stock.** Seven basis points, on a number this uncertain, is nothing.

This is not a disappointing result; it is a clarifying one, and it is what a no-arbitrage argument would have predicted before any of the machinery was built. Selling a fairly priced option is a fairly priced transaction. Doing it repeatedly, in a loop, with inventory, is still a fairly priced transaction. **The third of a share price per year that Track A reports is not income the strategy generates — it is the equity risk premium, relabelled, plus the operator's own capital handed back to them in instalments.**

The per-lot accounts make the same point in miniature: over its lifetime a lot collects **6.78%** of a share price in call premiums and surrenders **6.34%** in upside at call-away. The covered-call leg, the part that feels most like free income, is very nearly a wash.

What the machinery *does* determine is everything other than the mean: how much capital is required to run the strategy, how long it stays committed, how large the inventory grows, and under what conditions the whole thing stops resolving. Those are not small questions — they decide whether the strategy is operable — but they are questions about capital and risk, not about return.

## So where could an edge come from?

Only from options being priced richer than fair. That is not a hypothetical: implied volatility exceeds subsequently realized volatility systematically, by 2–4 points on liquid equities, and this **volatility risk premium** is the documented source of return in every put-write and covered-call study.

The model can price exactly how much of it is needed. Holding everything else fixed and raising only the volatility at which premiums are quoted:

| σ_IV | premiums/yr | wheel | vs buy-and-hold |
|---|---|---|---|
| 20.0% (fair) | 0.2249 | +1.49% | −0.07% |
| 20.5% | 0.2358 | +1.71% | +0.15% |
| 21.0% | 0.2470 | +1.93% | +0.37% |
| 22.0% | 0.2699 | +2.38% | +0.82% |

**The break-even is about 0.2 volatility points.** Above that, the wheel beats holding the stock; below it, it doesn't. Against a documented premium of 2–4 points, that is a comfortable margin — the strategy works, and now we know precisely what it works *on*.

Two honest qualifications. The single number σ_IV hides the volatility skew: the puts the operator sells carry a fatter premium than the calls they sell, so the edge concentrates in the put leg and in shallow lots, while deep lots — most of the inventory — contribute nothing regardless. And the edge is paid on premium volume, which is largest exactly when inventory is shallow and smallest when it is deep.

## Dividends, resolved

[The depth section](#sec:depth) left a trade-off open: dividend yield pays carry but slows the climb back to the strike, since at a fixed total return every point of yield comes out of price appreciation. Sweeping the yield with everything else held fixed:

    gross yield δ         0%      1%     2.5%      4%      6%
    ν                  +5.0%   +4.0%   +2.5%   +1.0%   −1.0%
    lots held            3.72    4.14    4.89    5.79    7.23
    capital (market)     3.91    4.33    5.08    5.98    7.42
    capital (cost)       5.32    6.15    7.82   10.14   14.68
    true excess        +1.85%  +1.71%  +1.49%  +1.28%  +1.00%

Yield is **mildly negative for the wheel, monotonically** — but the interesting part is where the damage falls. The return declines by 85 basis points across the sweep, most of which is simply the withholding tax on a larger dividend stream; measured against a buy-and-hold benchmark that suffers the same tax, the gap is roughly constant at about −0.06% throughout. What yield really does is **double the inventory and nearly triple the cost-basis capital**. A high-yield name does not make the wheel much less profitable per unit of capital; it makes the wheel need far more capital, and take far longer to release it.

The δ = 6% row deserves its flag: ν has gone negative there, which by [the holding-time section](#sec:holding) means a fixed fraction of lots never come back at all. Its thirty-year figures are a snapshot of a system that does not converge. [The stability section](#sec:stability) takes that up.

(One convention note, since the conclusion depends on it. Total return is held fixed as yield varies — dividends are treated as a *route* for return, not extra return. Assume instead that a 2.5% yielder returns 2.5% more in total than a non-payer, and the sign flips. The equal-total-return assumption is the neutral one, and it is stated here rather than buried.)

## The Conservative regime

Everything above used p\* = 20%. At p\* = 10%, with strikes 7% out of the money rather than 4.5%:

    lots held 2.35 · capital (market) 2.54 · capital (cost) 3.86
    Track A income 0.157/yr · true excess +1.26% · cash-on-cost −0.93%

Half the assignments, half the inventory, half the capital — and a slightly *worse* excess return than Standard, against a benchmark of +1.51%. Selling further out of the money buys a quieter strategy, not a better one: the premium given up scales down faster than the risk. This is the tidiest illustration in the article of what the model is for. The choice of strike moves everything the operator experiences — how often they are assigned, how much capital they need, how busy their account is — and moves the expected return essentially not at all.
