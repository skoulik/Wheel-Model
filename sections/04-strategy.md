# The Strategy and Its Accounting {#sec:strategy}

## Mechanics

The wheel this article models is the **mechanical wheel**: one run by rule, with the operator's judgment taken out. Judgment enters a real wheel at two points — which stock to buy and when, and whether to cut a stuck position loose rather than keep waiting for it to recover — and the model removes both, selling a put every cadence period whatever the price is doing and leaving every call strike where it was first struck. Both exclusions are deliberate, and each is taken up below where it arises.

The strategy operates on assets considered fundamentally sound — large, dividend-paying companies unlikely to collapse permanently, and that raise their dividend rather than cutting it — and entered at an attractive price, a discount to what the asset is worth. The two halves of that requirement play different roles here. The price half we leave to the operator: what counts as "attractive" is the discipline of valuation, and out of scope here. The soundness half is not a throwaway qualifier; it is a load-bearing assumption. Everything that follows about recovery presumes an asset whose deep drawdowns are eventually bought back up. The model does not apply to speculative names, and [the depth section](#sec:depth) turns "fundamentally sound" from a slogan into a specific inequality — while [the stability section](#sec:stability) shows that the strategy's survival, not merely its profitability, is what rests on it.

The price half is the first of those exclusions, and what excluding it costs is larger than an aside deserves. The model sells a put every cadence period no matter what the price is doing; a real operator waits, and sells only when the price is worth entering at. That waiting is not a refinement — measured on the live account behind this article, choosing *which* names to enter and *when* contributed more than everything else in this article combined, while the option machinery contributed nothing distinguishable from zero. [The live-account section](#sec:live) reports the measurement. The reader should carry the consequence from here: what follows prices the machine, not the judgment applied to it, and a verdict that the machine is worth nothing is not a verdict that the strategy is.

The dividend clause inside that qualifier is a genuine restriction and is better named than smuggled. The model's asset is a **dividend aristocrat**: a company whose payout rises year after year and never falls. This is a premise, not a finding — the article does not test which names qualify — and it is what licenses the constant dividend yield of [the depth section](#sec:depth), where the consequences are spelled out. A company that does cut is a different object, and it belongs with the permanent impairment that [the outlook](#sec:outlook) records as outside the model.

One full turn of the wheel:

1. **Sell a put.** Choose a strike below the current price and sell a put expiring in τ_p years. Collect the premium c_p (expressed, like all premiums here, as a fraction of the stock price).
2. **If the put expires worthless** (the stock stayed above the strike), keep the premium and go to step 1.
3. **If the put is assigned** (the stock fell below the strike), buy the shares at the strike. This lot of stock enters *inventory*.
4. **Sell a covered call** against the lot, expiring in τ_c years, struck at the same level you paid — the put's strike. Collect the premium c_c.
5. **If the call expires worthless** (the stock has not recovered to the strike), keep the premium and go to step 4 — sell another call on the same lot.
6. **If the call is exercised** (the stock recovered), deliver the shares at the strike. The lot leaves inventory. Go to step 1.

Crucially, step 1 does not wait for steps 4–6 to finish. A new put is sold every cadence period *regardless* of how much inventory is currently held. Puts keep arriving; calls keep working off the backlog. This is what makes the system a queue rather than a single loop, and it is also what makes the capital question nontrivial: in a falling market, inventory can pile up faster than it unwinds. The "regardless" is an idealization of unlimited capital, and it is worth flagging as one — an account with a finite balance eventually cannot fund the next assignment and must skip the put, which is [the constrained section](#sec:constrained)'s subject. Everything up to that section is the unconstrained limit, recovered exactly when the balance is large enough that no put sale is ever skipped.

One rule in step 4 does a great deal of work and should be flagged as a modelling choice rather than a law of nature: the call strike is **frozen at the price the lot was bought at**, and stays there for as long as the lot is held. Real operators do sometimes move a call strike down to force an exit from a stuck position, accepting a realized loss to release the capital. That lever is deliberately outside this model — it is a policy question, and answering it well would require modelling the operator's judgment rather than the strategy. It is the second of the two, and where the results are unflattering, the possibility that active strike management improves them stays open.

## Three clocks

Three period lengths govern the strategy, and keeping them separate matters more than it first appears.

- **The cadence T** — how often a new put is sold.
- **The tenor τ_p ≤ T** — how long each put runs. Premium is collected once per cadence period, but priced off the tenor.
- **The call period τ_c ≥ τ_p** — how long each covered call runs.

Most descriptions of the wheel collapse the first two, assuming a put is always live: sell a monthly put, it expires, sell another. Real operation separates them, though usually by less than it first appears — a put sold Monday at the open and expiring Friday at the close is live five of the week's seven days, leaving the stock uncovered only over the weekend, when the market is shut in any case. The separation still changes the economics, because the two clocks drive different quantities: what a put pays is set by the tenor it runs for, while how often assignment can arise is set by the cadence. Shorten the tenor without touching the cadence and the operator collects less premium for the same number of chances at assignment. Every example in Parts II and III sets T = τ_p, the always-covered case — for the Monday-to-Friday weekly pattern, very nearly the truth; [the live-account section](#sec:live) is where they come apart.

For the put and call clocks the ratio

n = τ_c / τ_p ≥ 1    {#eq:n}

is the natural bookkeeping unit. Every worked example in this article uses the rhythm of the live account behind it: **a put sold every week, T = τ_p = 1/52, and calls written for four weeks, so n = 4** and τ_c = 1/13 of a year. Why would an operator choose τ_c > τ_p at all? One reason needs nothing from the model: shorter puts let the operator re-price the entry strike more often as conditions change. The premium reason is not the obvious one — a longer call collects more per contract, but whether it collects more per unit of *time* depends on how far the lot has fallen, and [the depth section](#sec:depth) is where that is settled. Neither is what decides the choice: the call period also fixes how often a lot can leave at all, and [the holding-time section](#sec:holding) is where that is priced.[^eq-n]

## Three accounting tracks

Throughout, three parallel accounting tracks are maintained. They answer three different questions, and much confusion about strategies like this one comes from mixing them.

**Track A — realized cash flows.** Premiums received, dividends collected on held inventory, and the cash exchanged when lots are bought and sold. Under Track A, assignment is *inventory acquisition, not a loss*: buying stock at the strike is recorded as an exchange of cash for an asset. This is the operator's philosophy of the strategy, it is internally consistent, and it is what a brokerage statement shows — but it is only one lens, and [the returns section](#sec:returns) shows it is not a return.

**Track B — capital committed, valued at market.** Whatever the operator's philosophy, capital committed means capital that could otherwise be doing something else, and what a position ties up is what the market prices it at today. Track B records margin held against the open short put plus the **market value** of the shares held — not what was paid for them. The two legs are measured differently because they are different things: shares have been bought, so what is tied up is what they are worth, while a short put has bought nothing and ties up only the collateral standing behind it. The share leg deliberately ignores what a broker would lend against those shares, because leverage is priced once, in [the returns section](#sec:returns), and taking the haircut here as well would count the financing twice. Track B is the quantity against which both the strategy's size and its survival are measured.

**Track C — opportunity cost.** Money committed to this strategy could be earning the risk-free rate elsewhere. Track C charges r against the capital in Track B. A strategy that earns 6% while T-bills pay 5% on the same capital has earned 1%, not 6%.

The number that ultimately matters is the **true excess return**:

(economic profit − Track C) / Track B, annualized    {#eq:excess-return}

where the economic profit is Track A's cash *plus* the two things cash accounting cannot see — the shares' change in value, and the mark loss taken at the moment of assignment. [The returns section](#sec:returns) assembles it precisely.[^eq-excess-return]

**Exposure is not the same as equity required.** Track B answers "what is committed?", and its answer does not depend on how the commitment was paid for: ten thousand dollars of stock is ten thousand dollars of capital at market whether it was bought outright or half on credit. A finite account asks a second question — "what must be *in* the account to hold that?" — and its answer is smaller, because a broker lends against held shares and requires only a fraction of their value in the operator's own money: all of it for shares paid for in full, a quarter of it in a portfolio-margin account, where the same ten thousand dollars of stock can be carried on twenty-five hundred of the operator's own. Call that quantity the **equity required**. It is not a fourth track, and it never displaces Track B in a return calculation.

The temptation to divide by it instead is worth naming, because the resulting number is not arithmetically wrong — it is answering a question about financing while appearing to answer one about the strategy. At portfolio margin it reports close to four times the excess return, and an account financed that way really would earn four times as much on its own money, and lose it four times as fast. But the same borrowing is available to someone who simply buys the shares and sells no options at all, so it multiplies both sides of the comparison [the returns section](#sec:returns) actually makes — the wheel against owning the stock — and settles nothing about either. What the margin fraction governs is **capacity**: how much of the strategy a given balance can run before it must start refusing trades, and how far the price may fall before the broker sells the book out from under it. Those are the questions of [the constrained section](#sec:constrained), which finds the leverage an account can actually survive to be a small fraction of what the broker permits, and where equity required appears as a second ledger line beside the three tracks — never as a replacement for one.

Keeping the tracks separate is a discipline enforced on every formula in this article. It is not pedantry: the most natural-looking formula for this strategy's return mixes the income of one track with the capital of another, and the resulting number is both far too flattering in the early years and far too damning later.

[^eq-excess-return]: Reproduced by `python code/examples/returns_benchmark.py` — [eq:excess-return](#eq:excess-return), and the other readings quoted here are `p-star 0.10`. Pass `--help` for the full parameter set.

[^eq-n]: Reproduced by `python code/examples/strategy_cadence.py` — [eq:n](#eq:n), and the other readings quoted here are `n 1`; `n 13`. Pass `--help` for the full parameter set.
