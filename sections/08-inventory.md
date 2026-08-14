# The Inventory {#sec:inventory}

Lots arrive at a known rate and stay for a known average time. How much stock does the operator end up holding? There is a single formula for this, it requires almost no assumptions, and it is one of the most useful results in applied probability.

## Detour: Little's law

> Consider any system that things enter, spend time in, and leave: customers in a shop, patients in a hospital, jobs in a queue, stock lots in a wheel. **Little's law** says that the average number of items in the system equals the average arrival rate multiplied by the average time each item spends there. If forty customers an hour enter and each stays half an hour, there are twenty in the shop on average.
>
> What makes the law remarkable is what it does *not* require. Nothing about the arrival pattern, nothing about the order of service — [Little](#ref:little-1961) says of his own diagram that it is drawn for items leaving in the order they arrived, "but this is not required for the proofs" — nothing about whether items are independent, and nothing about the shape of any distribution. It is not even fussy about what counts as "the system": any boundary will do, so long as *number in the system*, *time spent in the system* and *arrival to the system* all mean the same thing by it. That last permission is what lets a warehouse of stock be treated as a queue at all. It is a conservation identity, not a model.
>
> One qualification, because the freedom just described is not quite the 1961 paper's. [Little's original](#ref:little-1961) assumes rather more than it needs — that the queue length, the waiting times and the arrivals are all strictly stationary — and he says so himself, calling it "probably not the weakest requirement possible". The assumption-free versions came later: a sample-path form that asks only that the averages exist, and [Little's own finite-window form](#ref:little-2011), which asks for nothing whatever and is the one this section actually leans on a few paragraphs below. [Ross's *Introduction to Probability Models*](#ref:ross-probability-models) proves the standard statement.

## Applying it

Arrivals are one lot per put assigned, at rate

λ  =  p\* / T  =  0.20 / (1/52)  =  **10.4 lots per year**    {#eq:lambda}

and each stays E[W] = 2.10 years by [eq:holding](#eq:holding). So

E[I]  =  λ · E[W]  =  10.4 × 2.10  =  **21.8 lots**    {#eq:little}

Twenty-two lots. The strategy was described at the outset as one that sells puts and occasionally takes assignment; at equilibrium it is a strategy that owns twenty-two lots of stock and sells puts on the side. And it earned that inventory honestly: 10.4 assignments a year, each lingering two years, is twenty-two.

Note what Little's law let us skip. Nothing here needed the exits to be independent, or the arrival stream to be smooth, or the holding times to follow any particular distribution — all of which are false for a single stock, whose lots ride one price path and are called away in batches. The average is exact regardless. That robustness is why this identity, rather than any distributional argument, is the load-bearing step of the article.

There is also a way to say the answer with no clock in it at all, and it may be the version worth keeping. Count time in *arrivals* rather than in years, and the law reads: **while you hold one lot, about twenty-two more are assigned.** Same number, nothing for the reader to multiply, and no rate to be quoted per year.

## The equilibrium the unconstrained operator will never see

Twenty-two lots is where the system settles. It is not where it will be found.

The wheel starts empty, and filling it is slow — because filling it requires the *tail* of the holding-time distribution to populate, and that tail is measured in decades. Before equilibrium, inventory is the arrival rate against however much of the survival curve has had time to accumulate:

E[I(t)]  =  λ · ∫₀^t S(u) du    {#eq:little-finite}

which recovers [eq:little](#eq:little) as t grows, since the whole integral is E[W]. Two readings of that trajectory matter, and they are different numbers:

    horizon H                          5 y     10 y     30 y     equilibrium
    E[I(H)], holdings at H            7.95    10.57    15.42        21.82
    average over [0, H]               5.41     7.39    11.40        21.82

The first row is what the operator is holding when the horizon arrives. The second is the average across the whole period, and it is the one the rest of Part II reports, because a return earned over a window has to be measured against the capital committed *throughout* that window rather than at its end. Every horizon-indexed figure from [the returns section](#sec:returns) onward is an average of the second kind, and the distinction is worth carrying: at thirty years the two differ by a third.

That second row is not a truncated version of Little's law. It *is* Little's law, read over the window — and reading it that way turns the gap between 11.40 and 21.82 from an apology into a figure. Divide the window's average inventory by the arrival rate and what comes back is the time a lot spends inside the window:

    horizon H                        5 y      10 y      30 y
    average inventory over [0, H]   5.41      7.39     11.40
    time a lot spends in-window     0.52 y    0.71 y    1.10 y

**Over a thirty-year window a lot spends 1.10 years inside it, against a full life of 2.10.** The window sees about half of each lot, so it holds about half the equilibrium inventory. Nothing is being approximated: a lot assigned in year 28 is genuinely two years old at most by the time the window closes, and counting it as such is the arithmetic rather than a concession to it.

That the law survives being read this way is [Little's own result](#ref:little-2011), proved for exactly this case — a window that starts empty and ends with the queue still occupied, which is a filling wheel to the letter — and it needs no stationarity at all, which the 1961 version did. It is not an exotic reading either: the same identity is standard in computer performance analysis, where it has been used to measure real systems for decades, and where defining a lot's residence as inventory divided by arrival rate is simply the convention when the system is not empty at the end.

One thing it does not do, and the distinction matters for everything that follows. The window law licenses the *measurement* — it says the 11.40 is exactly right for a thirty-year window — and says nothing whatever about the relation between that and the 21.82. Connecting the two is a separate question about how fast the system fills, which is the next thing this section takes up.

Reaching 90% of the equilibrium level takes **90 years** — the horizon at which the integral in [eq:little-finite](#eq:little-finite) reaches nine tenths of E[W]. An operator running this strategy for a full career holds about **seven tenths** of where it is heading, still rising, with no indication from the recent past that it is going to keep rising.

That 90% is a convention, and an arbitrary one: nine tenths of an asymptote is a threshold chosen by whoever is writing, not a date on which anything happens. An operator with a finite account gets a real threshold instead. A ceiling on how much stock the account can carry truncates exactly the slow deep tail that made the approach take a lifetime, and the date the ceiling starts refusing puts is a fact about the account rather than a choice about reporting. [The constrained section](#sec:constrained) computes it: **0.9 years** for an account of three share prices, 2.4 for five, **18.5** for the 11.59 that the rest of Part II reports this strategy as consuming, 270 for 19.04 — and never for an account of 19.23 or more, where the ceiling never binds at all and the ninety years come back in full.

Read that as the trade it is and not the escape it resembles. The accounts that arrive at equilibrium quickly are the accounts running almost none of the strategy: at 11.59 share prices the wheel turns at **60%** of its unconstrained rate, and the fraction falls with the account until, at one share price, it is a twentieth. An operator who wants to be at equilibrium within a few years buys that by running a quarter of a wheel; an operator running the whole of it inherits the ninety years unchanged. Even the 60% is the count-based figure, and [the constrained section](#sec:constrained) qualifies what an account following its own cash policy actually achieves.

This is worth stating plainly because it inverts the usual relationship between a model and its reader. The stationary answer, the one a queueing textbook would call *the* answer, is here a statement about a limit an operator reaches only by not running the strategy. **The operator-relevant numbers are the finite-horizon ones**, and every table in the rest of Part II is therefore indexed by horizon rather than reported at equilibrium.

The slowness also explains a trap in live data. An account three years into this strategy has inventory well below both its own eventual level and its own model-implied level, and every year of experience it accumulates *confirms* the comfortable reading. The strategy looks like it is working, and is, and is also filling up.

## Arrivals, departures, and self-recycling

At equilibrium the two flows must balance: 10.4 lots arrive per year and 10.4 leave. This is the **self-recycling property** — the strategy sheds inventory at exactly the rate it acquires it — and it is exact, not approximate, because it is what equilibrium means.

Two remarks keep it from being read as more comforting than it is.

First, during the transient the flows do *not* balance: arrivals run at 10.4 a year while departures lag, and the gap is precisely what accumulates on the balance sheet. At thirty years the system is still absorbing more than it releases.

Second, self-recycling is a statement about *counts*, not about money. Every departing lot exits at exactly the strike it entered at, so the round trip through inventory costs nothing at the price level — the appealing fact practitioners point to. But the lots arriving and the lots departing are not the same lots. Departures come from the shallow end; arrivals join wherever the market happens to be. The count balances while the composition drifts, and composition is where the money is.

## What the warehouse is actually made of

That composition is the last piece. Write ρ(x) for the **depth census**: how the standing inventory is distributed across depth — equivalently, how a randomly chosen lot-period of holding is distributed. It is obtained by pushing the entry law forward through the depth walk and accumulating the survivors:

ρ(x)  ∝  Σ_j  P( x_j ∈ dx,  J > j )    {#eq:census}

For the Standard regime over a thirty-year horizon:

    depth of lot below its strike     share of held time     q at mid-depth
    0 –  2%                                   8%                  0.442
    2 –  5%                                   5%                  0.275
    5 – 10%                                  11%                  0.094
    10 – 15%                                  7%                  0.013
    15 – 20%                                  9%                  0.001
    20 – 30%                                 13%                  0.000
    30 – 50%                                 18%                  0.000
    deeper than 50%                          28%                  0.000

**Forty-six percent of all inventory time is spent more than 30% below the strike**, where the exit probability is zero to three decimals and the covered call is worth nothing at all. The mean depth of standing inventory is 38%, against 1.6% for a freshly assigned lot. The inventory-weighted average exit probability is **0.066 per four-week period, against 0.404 for a fresh lot** — a factor of six.

Note where the census sits relative to where q survives. On this call clock a lot needs to be within about ten log-points of its strike to have any realistic chance of leaving — and only the top three rows, a quarter of all held time, are that shallow. The other three quarters is spent in positions that, on any given expiry, are not going anywhere.

The mechanism is not exotic. It is **length bias**, and it appears wherever a population is sampled by time rather than by item:

> **Detour: length bias.** Sample a hospital's beds on a given day and the patients you find are far sicker than the patients admitted, because a patient staying six months occupies a bed six months' worth while a patient staying a day occupies it for a day. Nothing about admissions has changed; the *sampling* is biased toward the slow. The same effect makes any bus you catch at random busier than the average bus, and makes a random inventory lot far deeper than a random assignment. A census of what is *present* is not a census of what *arrives*.

Fast lots leave quickly and barely register in the census. Slow lots register for exactly as long as they are slow. So the warehouse fills, unavoidably, with the lots that are least able to leave and least able to earn — and by [the depth section](#sec:depth)'s tables, those two properties are the same property.

There is a second way to see the same thing, and for a reader who knows any behavioural finance it may be the more memorable one:

> **Detour: the disposition effect, performed by contract.** One of the most robust findings about how people actually trade is that they sell their winners and keep their losers — [Shefrin and Statman](#ref:shefrin-statman-1985) named it the **disposition effect**, and [Odean](#ref:odean-1998) confirmed it across thousands of ordinary brokerage accounts, where it is not explained away by rebalancing, transaction costs, taxes or by the sold winners doing worse afterwards. It is generally presented as a mistake, and in a taxable account it is a measurable one. Now notice what the strategy in this article does. Every lot that rises to its strike is sold, automatically. No lot below its strike is ever sold at all. **The wheel is the disposition effect written into a contract, with the discretion removed and the frequency raised to certainty** — and the standing inventory described above is exactly what that produces over time. The analogy is structural and should not be pushed further than that: what makes the disposition effect costly for Odean's investors is largely tax, which this article does not model at all.

Over the full stationary limit the picture is starker still: mean depth 79%, inventory-weighted q of 0.036, and 53% of held time spent more than half a log-unit under water. That is the state the system is heading toward across its 90-year approach.

## Counting lots is not counting money

One warning before the economics. The census above counts *lots*, and every lot is one lot no matter how deep. Capital is not like that. A lot's cost basis relative to the current price is e^x — a lot 50% down in log terms ties up 65% more capital per share than a fresh one, and one 100% down ties up nearly triple. Capital therefore weights the deep tail *exponentially*, while the lot count weights it linearly.

That difference is not a detail. It is why [the returns section](#sec:returns) has to be careful about which capital it means, and why [the stability section](#sec:stability) needs a separate boundary for the capital from the one for the lot count.

It is also not a departure from Little's law. Weighting the inventory by something other than one lot per lot is covered by the same identity, in a form that has been available since the 1970s:

> **Detour: the same law, carrying a weight.** Little's law *counts* what is in the system. Its generalisation, written **H = λG**, *prices* it. Attach to each item any quantity it accumulates while it is in the system — the capital a lot ties up, the premium its call brings in, the dividends it pays — and let G be the total one item accumulates over its whole stay. Then the long-run rate at which the whole system accrues that quantity is **H = λ·G**: the same arrival rate, the same per-item total, whatever the weighting. Taking the weight to be 1 gives back L = λW, and the inventory count is the special case rather than the general rule. The form used here is [Whitt's](#ref:whitt-1991) theorem 6.3, which asks only two things: that arrivals and departures share one long-run rate — which is the self-recycling property above, 10.4 lots in and 10.4 out — and that an item accrues nothing before it arrives or after it leaves. Under those two, the per-item total settles down *exactly when* the system-wide rate does. The result is due to Brumelle and to Heyman and Stidham; Whitt's version is the one to reach for because it covers quantities that arrive in lumps as well as quantities that accrue steadily, and the wheel has both.

The article leans on that four times, and only the first is Little's law as it is usually quoted:

    weighting                          gives                          quoted in
    1                                  E[I] = 21.8 lots               this section
    e^x                                the capital tied up            the returns section
    the call premium at depth x        call income                    the returns section
    the dividend on market value       dividend income                the returns section

Every one is an integral of some function against the depth census, and every one is the same theorem with a different weight — which is why the census, once built, does not have to be rebuilt for each question. Two things are worth noticing about the conditions. The premium and the surrendered upside are not steady accruals at all: they land in a lump at a call expiry. That is precisely the case Whitt's version covers and the older statement does not. And nothing anywhere requires a lot's earnings and its exit time to be independent — which is fortunate, because here they are as dependent as two quantities can be, the same price path deciding both what a lot earns and when it leaves.

None of this is new, and the person who said so first was Little. His own illustration of a weighting other than one-per-item is the dollar return on the *i*th asset in a portfolio of assets: the application is his, and what this article supplies is the specific holding time and the specific census to put into it.

## A note on the shape of the distribution

Everything above concerns averages, which is all Little's law provides and all the economics needs. The *distribution* of I on a single stock is another matter: it is not the tidy bell-shaped thing a queueing course would suggest, because lots on one name share one price path — they deepen together and are called away in batches. The realized distribution is heavily skewed, with long empty stretches punctuated by deep pile-ups, and its variance runs several times its mean.

The classical result — that an infinite-server queue settles into a **Poisson** distribution, whose variance equals its mean — needs arrivals and departures to be independent. That is false for one stock and true across many.

There is also a distributional version of Little's law itself, which would seem to be exactly the tool for the job, and it is worth naming the reason it is not. It requires items to leave **in the order they arrived**. The wheel does no such thing: lots leave in order of *depth*, so a lot assigned last week can be called away years before one assigned in a drawdown, which is the whole of [the holding-time section](#sec:holding). That is the precise reason only the mean carries over — and it is a sharper reason than the shared price path, though the shared path is why the law's other condition fails too.

So the distributional claims belong to [the portfolio section](#sec:portfolio), where they are earned, rather than here, where they would be assumed. [The verification section](#sec:verification) reports what the single-name distribution actually looks like.
