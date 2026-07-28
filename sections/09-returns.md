# Returns and Capital {#sec:returns}

Now the question the whole model was built to answer. All quantities below are per unit of the current share price, so "capital of 11.59" means eleven and a half times what one share costs today, and an income of 0.77 means three quarters of a share price per year.

## What comes in

Take the Standard regime at a thirty-year horizon, which by [the inventory section](#sec:inventory) means 11.40 lots held on average. Cash arrives from three places:

    put premiums      0.1591 per year     one put a week, at 0.31% each
    call premiums     0.3706 per year     11.40 lots, each selling a call every four weeks
    dividends         0.2422 per year     δ_net on the market value of 11.40 lots
    ------------------------------------
    Track A income    0.7718 per year    {#eq:income}

Three quarters of a share price per year, in cash, realized. It is a genuinely impressive-looking number, and it is the number that makes this strategy popular. Note also what the composition says: **the calls out-earn the puts more than two to one**, and the dividends out-earn the puts as well. The strategy is named after selling puts, but by the time it is running at scale, put premium is its smallest cash source.

The number is also, on its own, meaningless. It says nothing until we ask what had to be tied up to earn it.

## What is tied up

Two different quantities can be called "the capital", and choosing between them decides the answer.

**Cost basis.** The operator paid k per share for 11.40 lots. Summed, and expressed against today's price, that comes to **18.23**. This is the number a spreadsheet of purchases produces, and it is what practitioners usually mean by "capital deployed".

**Market value.** Those same shares can be sold today for what the market pays: 11.40 share prices, plus margin on the live put, for a total of **11.59**.

The gap between them — 6.6 share prices — is the accumulated paper loss on the standing inventory, which is large precisely because the census in [the inventory section](#sec:inventory) is dominated by deep lots.

The right choice for measuring *return* is market value, and the reason is worth stating carefully because the other choice is so tempting. Capital committed means capital that could otherwise be doing something else. A share bought at 100 and now worth 60 does not commit 100 to the strategy; it commits 60, because 60 is what selling it would release. The other 40 is gone — it is a loss that has already happened, not an ongoing commitment. Charging opportunity cost on it counts the same loss twice: once when the price fell, and again every year afterwards.

This is also what [the strategy section](#sec:strategy) promised — Track B was defined as capital at market prices — and it is the definition that survives the consistency test in [the verification section](#sec:verification), which the cost-basis version fails.

E[Capital]  =  γ·k  +  E[I]    {#eq:capital}

## What Track A leaves out

Cash accounting is internally consistent but it is not a return, because two real economic events pass through it without leaving a trace.

**The mark loss at acquisition.** A lot is bought at the strike while the market offers less. That difference is a loss the moment it happens. Track A calls it "acquisition at the operator's chosen basis" and books nothing. Over a year of arrivals it comes to **0.1632**.

**The upside surrendered at call-away.** When a lot is called away, the shares are delivered at the strike while the market is *above* the strike — that is precisely why the call was exercised. The operator hands over something worth more than what they receive. Track A sees an exit at the same price as the entry and books nothing. Over a year this comes to **0.3559**, more than twice the put premiums.

Against those, one real gain is also invisible to Track A: the **appreciation of shares held**, which for 11.40 lots drifting at m = 4.5% is **0.5128** a year.

Add all three and something striking happens:

    appreciation of held shares    +0.5128
    mark loss at acquisition       −0.1632
    upside surrendered             −0.3559
    -------------------------------------
    net                            −0.0063

**They cancel** — to within about one percent of the largest of them. The gain that Track A ignores is almost exactly consumed by the two costs Track A ignores. That is not a coincidence — it is what near-fair option pricing means — and it has a convenient consequence: the honest economic return is Track A's cash income, measured against *market-value* capital.

E[Π]  =  Track A income  +  E[I]·m  −  (mark loss)  −  (upside surrendered)    {#eq:econ-pnl}

**True excess return  =  ( E[Π] − r · E[Capital] ) / E[Capital]**    {#eq:excess}

= (0.7655 − 0.05 × 11.591) / 11.591 = **+1.60% per year**.

## The two ledgers, side by side

| Standard regime | 5 y | 10 y | 30 y |
|---|---|---|---|
| lots held | 5.41 | 7.39 | 11.40 |
| capital, market value | 5.61 | 7.59 | 11.59 |
| capital, cost basis | 6.70 | 9.83 | 18.23 |
| **true excess return** | **+1.60%** | **+1.60%** | **+1.60%** |
| cash income on cost basis | +4.11% | +1.81% | −0.77% |

The true excess return is flat across horizons to three decimal places, as a genuine risk premium should be: the position earns what it earns, whatever size it has grown to.

The cash-on-cost-basis line does something else entirely, and it is worth understanding because **it is what an operator's own records will show them**. Early on it is spectacular — a strategy apparently earning 4.1% over T-bills. Then it decays, crosses zero somewhere around year twenty, and keeps falling. Nothing in the strategy has changed. What changes is that cost basis keeps inflating relative to market value as deep lots accumulate, so the denominator grows while the numerator does not. An operator watching this happen will conclude the strategy has stopped working. It has not; the measurement was wrong at both ends — too flattering at the start, too damning later.

> **A pitfall worth naming.** There is a second, popular way to get this wrong. Under the "net cost basis" convention an assigned lot is booked at strike minus premium, so the exit at the strike shows a *capital gain of exactly the put premium* — the premium apparently recovered a second time at the exit door. The recycling image is appealing and the arithmetic is a double count: the premium was already booked as income when it was received. Any of these conventions is fine applied consistently; the failure mode is mixing the income of one with the capital of another, which is exactly what "cash income on cost basis" does.

## The benchmark that matters

An excess return of +1.60% over the risk-free rate sounds like a verdict. It isn't, because T-bills are the wrong comparison. This strategy keeps almost all of its capital in equity — 98% at the thirty-year mark, and [the inventory section](#sec:inventory)'s census shows the warehouse is rarely empty — so the relevant question is not whether it beats cash but whether it beats **owning the stock**.

Buying and holding the same stock earns μ − r − w·δ = **+1.63%** over the risk-free rate, or **+1.60%** after scaling by the wheel's 98% equity exposure. Against the wheel's +1.60%:

| Standard regime, 30 y | excess return |
|---|---|
| the wheel | +1.60% |
| buy and hold, equity-adjusted | +1.60% |
| **difference** | **+0.01%** |

**At fair option prices the wheel is economically identical to owning the stock.** One basis point is not a result; it is the model's numerical noise floor, and the true difference is zero.

This is not a disappointing result; it is a clarifying one, and it is what a no-arbitrage argument would have predicted before any of the machinery was built. Selling a fairly priced option is a fairly priced transaction. Doing it repeatedly, in a loop, with inventory, is still a fairly priced transaction. **The third of a share price per year that Track A reports is not income the strategy generates — it is the equity risk premium, relabelled, plus the operator's own capital handed back to them in instalments.**

The per-lot accounts make the same point in miniature: over its lifetime a lot collects **3.72%** of a share price in call premiums and surrenders **3.58%** in upside at call-away. The covered-call leg, the part that feels most like free income, is very nearly a wash.

What the machinery *does* determine is everything other than the mean: how much capital is required to run the strategy, how long it stays committed, how large the inventory grows, and under what conditions the whole thing stops resolving. Those are not small questions — they decide whether the strategy is operable — but they are questions about capital and risk, not about return.

## So where could an edge come from?

Only from options being priced richer than fair. That is not a hypothetical: implied volatility exceeds subsequently realized volatility systematically, by 2–4 points on liquid equities, and this **volatility risk premium** is the documented source of return in every put-write and covered-call study.

The model can price exactly how much of it is needed. Holding everything else fixed and raising only the volatility at which premiums are quoted:

| σ_IV | premiums/yr | wheel | vs buy-and-hold |
|---|---|---|---|
| 20.0% (fair) | 0.5297 | +1.60% | +0.01% |
| 20.5% | 0.5555 | +1.83% | +0.23% |
| 21.0% | 0.5818 | +2.05% | +0.46% |
| 22.0% | 0.6358 | +2.52% | +0.92% |

**The break-even is zero.** At fair prices the wheel matches the stock, and every volatility point of overpricing is worth about 45 basis points of excess return on top. There is no hurdle to clear first: against a documented premium of 2–4 points, the whole of it is edge. That is a cleaner statement than it looks, and it is the no-arbitrage argument showing up as arithmetic — a fairly priced loop earns exactly what the asset earns, so whatever the strategy makes above that has to come from the options being sold dear.

## The premium is real. It also does not arrive.

That table invites a straightforward conclusion — find a few points of overpricing and collect 45 basis points apiece — and the live account is the reason to resist it. Inverting the option premiums that account actually paid and comparing them with the volatility that actually followed, the puts it sold were dear by a wide margin, several points clear of the 2–4 the literature reports. Its option overlay nevertheless earned **nothing**: measured against simply holding the same shares over the same days, the entire apparatus of puts, assignments, calls and call-aways came to zero within the precision fourteen months can support.

The two facts are not in conflict, and the reconciliation is the most useful thing in this section. A rich put is rich because it is likely to be assigned into a falling stock, and the premium is collected in the same transaction that hands the operator a lot below water. Of every dollar of put premium the live account collected, the mark loss taken at assignment consumed about four fifths. And the fifth that survives on the put leg is more than given back on the call leg, which surrendered a third more at call-away than it collected in premium. **The volatility risk premium is real, and it is very nearly the price of the inventory it creates.**

Two things follow for reading the table above. It is a *comparative static* — it holds the entry policy fixed and asks what a richer quote is worth — and so it correctly prices a spread that arrives without a matching change in assignment. It is not a promise that a measured spread converts at 45 basis points a point, because the spread that is easiest to measure is the one on far-out-of-the-money puts, and that one is quoted precisely because those puts are not as far out of the money as they look.

## What the single σ_IV leaves out

One number stands in for the entire volatility surface here, and the simplification should be named rather than left implicit, because a real surface is not flat in either direction that matters to this strategy.

**Across strikes.** The puts the operator sells carry a fatter implied volatility than the calls they sell — the skew of [the introduction](#sec:introduction)'s detour. So the edge concentrates in the put leg and in shallow lots, while deep lots, which are most of the inventory, contribute little regardless. In the live account the put leg's spread over realized volatility ran to roughly twice the call leg's. Splitting σ_IV into two numbers would capture this and is a small change; it is not made here because it buys detail in a quantity the article has already deliberately set to zero.

**With depth.** The more interesting omission. A lot is deep because its stock fell, and a stock that has fallen is quoted at a higher implied volatility — so the model, holding σ_IV fixed, understates what deep lots earn on their calls. The live account confirms the direction: calls written against its deepest lots were quoted materially dearer than calls on its shallow ones. But most of that gap is not depth at all — deep lots sit on names that are volatile to begin with, and once each name is compared against its own typical level, the genuine depth effect is roughly a third. **That is why it is left out: a third more implied volatility on the smallest income term in the ledger, measured across a few dozen contracts, is not worth carrying a strike- and state-dependent volatility surface through every formula in this article.** It is recorded here as a known bias, and its sign is favourable — the model is, in this one respect, pessimistic about deep inventory.

And a third, which no surface captures: the edge is paid on premium volume, which is largest exactly when inventory is shallow and smallest when it is deep.

## Dividends, resolved

[The depth section](#sec:depth) left a trade-off open: dividend yield pays carry but slows the climb back to the strike, since at a fixed total return every point of yield comes out of price appreciation. Sweeping the yield with everything else held fixed:

    gross yield δ         0%      1%     2.5%      4%      6%
    ν                  +5.0%   +4.0%   +2.5%   +1.0%   −1.0%
    lots held            8.54    9.56   11.40   13.65   17.31
    capital (market)     8.74    9.75   11.59   13.84   17.51
    capital (cost)      12.11   14.15   18.23   24.00   35.50
    true excess        +1.98%  +1.83%  +1.60%  +1.38%  +1.08%

Yield is **mildly negative for the wheel, monotonically** — but the interesting part is where the damage falls. The return declines by 90 basis points across the sweep, most of which is simply the withholding tax on a larger dividend stream; measured against a buy-and-hold benchmark that suffers the same tax, the gap is essentially zero throughout — never more than two basis points, at any yield. What yield really does is **double the inventory and nearly triple the cost-basis capital**. A high-yield name does not make the wheel much less profitable per unit of capital; it makes the wheel need far more capital, and take far longer to release it.

The δ = 6% row deserves its flag: ν has gone negative there, which by [the holding-time section](#sec:holding) means a fixed fraction of lots never come back at all. Its thirty-year figures are a snapshot of a system that does not converge. [The stability section](#sec:stability) takes that up.

(One convention note, since the conclusion depends on it. Total return is held fixed as yield varies — dividends are treated as a *route* for return, not extra return. Assume instead that a 2.5% yielder returns 2.5% more in total than a non-payer, and the sign flips. The equal-total-return assumption is the neutral one, and it is stated here rather than buried.)

## What if the dividend never falls?

[The depth section](#sec:depth) held δ constant on the grounds that an aristocrat's payout tracks the price trend, and flagged one residual: between raises the payout is fixed in dollars, so an operator waiting out a drawdown collects a *higher* yield than δ while they wait. The sweep above is enough to price that, and the reason is worth seeing, because it is the whole answer.

δ reaches the model through exactly two channels — the drift ν = μ − δ − σ²/2 and the income δ_net·E[I] — so any story about the yield being effectively higher is a story about running the model at a larger δ. It is a *row of the table above*, not a new model. Writing y for the market's log deviation from the level at which it yielded δ, and taking dividend growth equal to the price's log drift, y is driftless with volatility σ, so a position of age t collects a yield inflated by e^(σ²·t/2). Averaging over held lot-time and solving the fixed point — a larger δ lowers ν, which ages the book, which inflates the yield again:

    horizon                      5 y      10 y      30 y
    inflation factor            1.020     1.039     1.113
    δ_eff                       2.55%     2.60%     2.78%
    true excess               +1.59%    +1.58%    +1.56%
    change from constant δ    −0.01pp   −0.01pp   −0.04pp
    gap vs buy-and-hold       +0.03pp   +0.01pp   +0.01pp

**Four basis points at thirty years, and negative.** The extra carry is real and it is outweighed, by the same two mechanisms the sweep above already identified: a higher yield drags harder on the price, so the book deepens (inventory rises 3.4%, cost-basis capital 5.1%), and a larger share of the total return arrives in the one form that is taxed on the way in.

The last line is the one that settles it. The article's verdict is not the wheel's excess return in isolation but its *gap* against owning the stock, and the sweep above showed that gap is flat in δ to a basis point or two. A sticky dividend moves the wheel and the benchmark together, so it cannot change the verdict — and if anything it favours the wheel, since a buy-and-hold position holds one anchor for the entire horizon and picks up a larger inflation factor for it (1.37 at thirty years, against the wheel's 1.11) while the wheel's lots turn over.

Two boundaries on this, both worth stating because they mark where the analysis stops rather than where it is comfortable.

The inflation factor **has no limit**. Held lot-time thins out like the holding-time tail, e^(−ν²·t/(2σ²)), at 0.8% a year, while the yield inflates at σ²/2 = 2% a year; the second wins, so the average has no stationary value and the correction above is only ever a finite-horizon statement. That divergence is not a numerical defect — it is the model reporting that a payout cannot be assumed fixed forever.

And there is a depth past which the assumption is self-defeating. Freeze the payout in dollars and a lot at depth x faces a yield of δ·e^x on the market value of its shares, so the drag grows with depth and the depth drift becomes ν − δ·(e^x − 1). That changes sign at x\* = ln(1 + ν/δ), and beyond it grows more negative — a runaway region rather than a slow one. At the running parameters x\* sits **50% below the strike**, with 16% of the thirty-year census already past it. It is the Gordon-model price at which a fixed payout stops being payable, which is to say it is the point where a company stops being an aristocrat and starts being [the outlook](#sec:outlook)'s permanent-impairment case. Under the market's pricing drift the boundary is far tighter — 17% below the strike, with 69% of the census beyond it — which is a sharp way of putting the limitation: **option prices are not consistent with a dividend that never falls.**

## The Conservative regime

Everything above used p\* = 20%. At p\* = 10%, with strikes 3.5% out of the money rather than 2.3%:

    lots held 5.50 · capital (market) 5.70 · capital (cost) 8.90
    Track A income 0.371/yr · true excess +1.49% · cash-on-cost −0.83%

Half the assignments, half the inventory, half the capital — and a slightly *worse* excess return than Standard, against a benchmark of +1.57%. Selling further out of the money buys a quieter strategy, not a better one: the premium given up scales down faster than the risk. This is the tidiest illustration in the article of what the model is for. The choice of strike moves everything the operator experiences — how often they are assigned, how much capital they need, how busy their account is — and moves the expected return essentially not at all.
