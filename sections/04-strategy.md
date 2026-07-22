# The Strategy and Its Accounting {#sec:strategy}

## Mechanics

The strategy operates on assets considered fundamentally sound — large, dividend-paying companies unlikely to collapse permanently — and entered at an attractive price, a discount to what the asset is worth. The two halves of that requirement play different roles here. The price half we leave to the operator: deciding what counts as "attractive" is the discipline of valuation, and it is out of scope of this article — the model takes the entry level as given. The soundness half is not a throwaway qualifier; it is a load-bearing assumption. Everything that follows about recovery probabilities presumes an asset whose deep drawdowns are eventually bought back up. The model does not apply to speculative names, and we will return to what "fundamentally sound" buys us mathematically in [the recovery section](#sec:recovery).

One full turn of the wheel:

1. **Sell a put.** Choose a strike below the current price and sell a put expiring in τ_p years. Collect the premium c_p (expressed, like all premiums here, as a fraction of the stock price).
2. **If the put expires worthless** (the stock stayed above the strike), keep the premium and go to step 1.
3. **If the put is assigned** (the stock fell below the strike), buy the shares at the strike. This lot of stock enters *inventory*.
4. **Sell a covered call** against the lot, expiring in τ_c years, struck at the same level you paid — the put's strike. Collect the premium c_c.
5. **If the call expires worthless** (the stock has not recovered to the strike), keep the premium and go to step 4 — sell another call on the same lot.
6. **If the call is exercised** (the stock recovered), deliver the shares at the strike. The lot leaves inventory. Go to step 1.

Crucially, step 1 does not wait for steps 4–6 to finish. A new put is sold every put period *regardless* of how much inventory is currently held. Puts keep arriving; calls keep working off the backlog. This is what makes the system a queue rather than a single loop, and it is also what makes the capital question nontrivial: in a falling market, inventory can pile up faster than it unwinds.

## Two clocks

Two period lengths govern the strategy: τ_p, how long each put runs, and τ_c, how long each covered call runs, with τ_c ≥ τ_p. One can use weekly puts with monthly calls, or monthly puts with quarterly calls. The ratio

n = τ_c / τ_p ≥ 1    {#eq:n}

turns out to matter considerably: as we will show, it acts as a direct multiplier on how much inventory the strategy holds at equilibrium.

Why would an operator choose τ_c > τ_p at all? Longer-dated calls collect more premium per contract and give a depressed stock more time to recover before the next decision point; shorter puts let the operator re-price the entry strike more frequently as conditions change. The trade-off — more premium per call versus more capital locked in inventory — is exactly what the model quantifies.

## Three accounting tracks

Throughout, three parallel accounting tracks are maintained. They answer three different questions, and much confusion about strategies like this one comes from mixing them.

**Track A — realized cash flows.** Premiums received and capital gains taken when lots are called away. Under Track A, assignment is *inventory acquisition, not a loss*: buying stock at the strike is recorded as an exchange of cash for an asset, at the operator's chosen basis. This is the operator's philosophy of the strategy, and it is internally consistent — but it is only one lens.

**Track B — capital committed at market prices.** Whatever the operator's philosophy, the broker computes margin on live prices. Track B records the capital actually tied up: margin held against the open short put, plus the market-priced cost basis of all inventory. Track B is what limits how large the strategy can run and what determines whether it survives stress.

**Track C — opportunity cost.** Money committed to this strategy could be earning the risk-free rate elsewhere. Track C charges r against the capital in Track B. A strategy that earns 6% while T-bills pay 5% on the same capital has earned 1%, not 6%.

The number that ultimately matters is the **true excess return**:

(Track A − Track C) / Track B, annualized    {#eq:excess-return}

Keeping the tracks separate is a discipline we enforce on every formula in this article: each result will be labeled with the track it belongs to. As we will see in [the returns section](#sec:returns), at least one natural-looking formula for the strategy's income turns out to mix tracks and silently double-count — the separation is not pedantry.
