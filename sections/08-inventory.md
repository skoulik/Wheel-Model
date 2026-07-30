# The Inventory {#sec:inventory}

Lots arrive at a known rate and stay for a known average time. How much stock does the operator end up holding? There is a single formula for this, it requires almost no assumptions, and it is one of the most useful results in applied probability.

## Detour: Little's law

> Consider any system that things enter, spend time in, and leave: customers in a shop, patients in a hospital, jobs in a queue, stock lots in a wheel. **Little's law** says that the average number of items in the system equals the average arrival rate multiplied by the average time each item spends there. If forty customers an hour enter and each stays half an hour, there are twenty in the shop on average.
>
> What makes the law remarkable is what it does *not* require. Nothing about the arrival pattern, nothing about the order of service, nothing about whether items are independent, nothing about the shape of any distribution. Only that the system is in a steady state and that the averages exist. It is a conservation identity, not a model. Ross's *Introduction to Probability Models* proves it; Little's 1961 paper is the original.

## Applying it

Arrivals are one lot per put assigned, at rate

λ  =  p\* / T  =  0.20 / (1/52)  =  **10.4 lots per year**    {#eq:lambda}

and each stays E[W] = 2.10 years by [eq:holding](#eq:holding). So

E[I]  =  λ · E[W]  =  10.4 × 2.10  =  **21.8 lots**    {#eq:little}

Twenty-two lots. The strategy was described at the outset as one that sells puts and occasionally takes assignment; at equilibrium it is a strategy that owns twenty-two lots of stock and sells puts on the side. And it earned that inventory honestly: 10.4 assignments a year, each lingering two years, is twenty-two.[^eq-lambda]

Note what Little's law let us skip. Nothing here needed the exits to be independent, or the arrival stream to be smooth, or the holding times to follow any particular distribution — all of which are false for a single stock, whose lots ride one price path and are called away in batches. The average is exact regardless. That robustness is why this identity, rather than any distributional argument, is the load-bearing step of the article.

## The equilibrium the unconstrained operator will never see

Twenty-two lots is where the system settles. It is not where it will be found.

The wheel starts empty, and filling it is slow — because filling it requires the *tail* of the holding-time distribution to populate, and that tail is measured in decades. Before equilibrium, inventory is the arrival rate against however much of the survival curve has had time to accumulate:

E[I(t)]  =  λ · ∫₀^t S(u) du    {#eq:little-finite}

which recovers [eq:little](#eq:little) as t grows, since the whole integral is E[W]. Two readings of that trajectory matter, and they are different numbers:

    horizon H                          5 y     10 y     30 y     equilibrium
    E[I(H)], holdings at H            7.95    10.57    15.42        21.82
    average over [0, H]               5.41     7.39    11.40        21.82

The first row is what the operator is holding when the horizon arrives. The second is the average across the whole period, and it is the one the rest of Part II reports, because a return earned over a window has to be measured against the capital committed *throughout* that window rather than at its end. Every horizon-indexed figure from [the returns section](#sec:returns) onward is an average of the second kind, and the distinction is worth carrying: at thirty years the two differ by a third.

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

For the Standard regime over a thirty-year horizon:[^eq-census]

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

Over the full stationary limit the picture is starker still: mean depth 79%, inventory-weighted q of 0.036, and 53% of held time spent more than half a log-unit under water. That is the state the system is heading toward across its 90-year approach.

## Counting lots is not counting money

One warning before the economics. The census above counts *lots*, and every lot is one lot no matter how deep. Capital is not like that. A lot's cost basis relative to the current price is e^x — a lot 50% down in log terms ties up 65% more capital per share than a fresh one, and one 100% down ties up nearly triple. Capital therefore weights the deep tail *exponentially*, while the lot count weights it linearly.

That difference is not a detail. It is why [the returns section](#sec:returns) has to be careful about which capital it means, and why [the stability section](#sec:stability) needs a separate boundary for the capital from the one for the lot count.

## A note on the shape of the distribution

Everything above concerns averages, which is all Little's law provides and all the economics needs. The *distribution* of I on a single stock is another matter: it is not the tidy bell-shaped thing a queueing course would suggest, because lots on one name share one price path — they deepen together and are called away in batches. The realized distribution is heavily skewed, with long empty stretches punctuated by deep pile-ups, and its variance runs several times its mean.

The classical result — that an infinite-server queue settles into a **Poisson** distribution, whose variance equals its mean — needs arrivals and departures to be independent. That is false for one stock and true across many. So the distributional claims belong to [the portfolio section](#sec:portfolio), where they are earned, rather than here, where they would be assumed. [The verification section](#sec:verification) reports what the single-name distribution actually looks like.

[^eq-census]: Reproduced by `python code/examples/inventory_census.py` — [eq:census](#eq:census), and the other readings quoted here are `stationary`. Pass `--help` for the full parameter set.

[^eq-lambda]: Reproduced by `python code/examples/inventory_little.py` — [eq:lambda](#eq:lambda), [eq:little](#eq:little), [eq:little-finite](#eq:little-finite). Pass `--help` for the full parameter set.
