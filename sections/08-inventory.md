# The Inventory {#sec:inventory}

Lots arrive at a known rate and stay for a known average time. How much stock does the operator end up holding? There is a single formula for this, it requires almost no assumptions, and it is one of the most useful results in applied probability.

## Detour: Little's law

> Consider any system that things enter, spend time in, and leave: customers in a shop, patients in a hospital, jobs in a queue, stock lots in a wheel. **Little's law** says that the average number of items in the system equals the average arrival rate multiplied by the average time each item spends there. If forty customers an hour enter and each stays half an hour, there are twenty in the shop on average.
>
> What makes the law remarkable is what it does *not* require. Nothing about the arrival pattern, nothing about the order of service, nothing about whether items are independent, nothing about the shape of any distribution. Only that the system is in a steady state and that the averages exist. It is a conservation identity, not a model. Ross's *Introduction to Probability Models* proves it; Little's 1961 paper is the original.

## Applying it

Arrivals are one lot per put assigned, at rate

λ  =  p\* / T  =  0.20 / (1/12)  =  **2.4 lots per year**

and each stays E[W] = 4.18 years by [eq:holding](#eq:holding). So

E[I]  =  λ · E[W]    {#eq:little}

= 2.4 × 4.18 = **10.0 lots**.

Ten lots. The strategy was described at the outset as one that sells puts and occasionally takes assignment; at equilibrium it is a strategy that owns ten lots of stock and sells puts on the side. And it earned that inventory honestly: 2.4 assignments a year, each lingering four years, is ten.

Note what Little's law let us skip. Nothing here needed the exits to be independent, or the arrival stream to be smooth, or the holding times to follow any particular distribution — all of which are false for a single stock, whose lots ride one price path and are called away in batches. The average is exact regardless. That robustness is why this identity, rather than any distributional argument, is the load-bearing step of the article.

## The equilibrium the operator will never see

Ten lots is where the system settles. It is not where it will be found.

The wheel starts empty, and filling it is slow — because filling it requires the *tail* of the holding-time distribution to populate, and that tail is measured in decades. Integrating the survival curve gives the whole trajectory:

    after           5 y     10 y     30 y     equilibrium
    E[I]           2.22     3.10     4.89        10.04

Reaching 90% of the equilibrium level takes **94 years**. An operator running this strategy for a full career sees inventory a little under half of where it is heading, still rising, with no indication from the recent past that it is going to keep rising.

This is worth stating plainly because it inverts the usual relationship between a model and its reader. The stationary answer, the one a queueing textbook would call *the* answer, is here a statement about a limit that no participant reaches. **The operator-relevant numbers are the finite-horizon ones**, and every table in the rest of Part II is therefore indexed by horizon rather than reported at equilibrium.

The slowness also explains a trap in live data. An account three years into this strategy has inventory well below both its own eventual level and its own model-implied level, and every year of experience it accumulates *confirms* the comfortable reading. The strategy looks like it is working, and is, and is also filling up.

## Arrivals, departures, and self-recycling

At equilibrium the two flows must balance: 2.4 lots arrive per year and 2.4 leave. This is the **self-recycling property** — the strategy sheds inventory at exactly the rate it acquires it — and it is exact, not approximate, because it is what equilibrium means.

Two remarks keep it from being read as more comforting than it is.

First, during the transient the flows do *not* balance: arrivals run at 2.4 a year while departures lag, and the gap is precisely what accumulates on the balance sheet. At thirty years the system is still absorbing more than it releases.

Second, self-recycling is a statement about *counts*, not about money. Every departing lot exits at exactly the strike it entered at, so the round trip through inventory costs nothing at the price level — the appealing fact practitioners point to. But the lots arriving and the lots departing are not the same lots. Departures come from the shallow end; arrivals join wherever the market happens to be. The count balances while the composition drifts, and composition is where the money is.

## What the warehouse is actually made of

That composition is the last piece. Write ρ(x) for the **depth census**: how the standing inventory is distributed across depth — equivalently, how a randomly chosen lot-quarter of holding is distributed. It is obtained by pushing the entry law forward through the depth walk and accumulating the survivors:

ρ(x)  ∝  Σ_j  P( x_j ∈ dx,  J > j )    {#eq:census}

For the Standard regime over a thirty-year horizon:

    depth of lot below its strike     share of held time     q at mid-depth
    0 –  2%                                   8%                  0.485
    2 –  5%                                   6%                  0.387
    5 – 10%                                  13%                  0.246
    10 – 15%                                  7%                  0.118
    15 – 20%                                  9%                  0.046
    20 – 30%                                 13%                  0.007
    30 – 50%                                 18%                  0.000
    deeper than 50%                          27%                  0.000

**Forty-five percent of all inventory time is spent more than 30% below the strike**, where the exit probability is zero to three decimals and the covered call sells for a basis point. The mean depth of standing inventory is 37%, against 3.2% for a freshly assigned lot. The inventory-weighted average exit probability is **0.112 per quarter, against 0.398 for a fresh lot** — a factor of three and a half.

The mechanism is not exotic. It is **length bias**, and it appears wherever a population is sampled by time rather than by item:

> **Detour: length bias.** Sample a hospital's beds on a given day and the patients you find are far sicker than the patients admitted, because a patient staying six months occupies a bed six months' worth while a patient staying a day occupies it for a day. Nothing about admissions has changed; the *sampling* is biased toward the slow. The same effect makes any bus you catch at random busier than the average bus, and makes a random inventory lot far deeper than a random assignment. A census of what is *present* is not a census of what *arrives*.

Fast lots leave quickly and barely register in the census. Slow lots register for exactly as long as they are slow. So the warehouse fills, unavoidably, with the lots that are least able to leave and least able to earn — and by [the depth section](#sec:depth)'s tables, those two properties are the same property.

Over the full stationary limit the picture is starker still: mean depth 78%, inventory-weighted q of 0.062, and 52% of held time spent more than half a log-unit under water. That is the state the system is heading toward across its 94-year approach.

## Counting lots is not counting money

One warning before the economics. The census above counts *lots*, and every lot is one lot no matter how deep. Capital is not like that. A lot's cost basis relative to the current price is e^x — a lot 50% down in log terms ties up 65% more capital per share than a fresh one, and one 100% down ties up nearly triple. Capital therefore weights the deep tail *exponentially*, while the lot count weights it linearly.

That difference is not a detail. It is why [the returns section](#sec:returns) has to be careful about which capital it means, and why [the stability section](#sec:stability) ends up with two boundaries instead of one.

## A note on the shape of the distribution

Everything above concerns averages, which is all Little's law provides and all the economics needs. The *distribution* of I on a single stock is another matter: it is not the tidy bell-shaped thing a queueing course would suggest, because lots on one name share one price path — they deepen together and are called away in batches. The realized distribution is heavily skewed, with long empty stretches punctuated by deep pile-ups, and its variance runs several times its mean.

The classical result — that an infinite-server queue settles into a **Poisson** distribution, whose variance equals its mean — needs arrivals and departures to be independent. That is false for one stock and true across many. So the distributional claims belong to [the portfolio section](#sec:portfolio), where they are earned, rather than here, where they would be assumed. [The verification section](#sec:verification) reports what the single-name distribution actually looks like.
