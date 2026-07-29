# The Finite Account: Capacity and Survival {#sec:constrained}

Every result so far belongs to an operator with unlimited money. [The strategy section](#sec:strategy)'s step 1 sells a put every cadence period *regardless* of how much inventory is already held, and that "regardless" has been doing quiet work ever since: it is what makes arrivals independent of the system's state, which is what makes Little's law apply in the direction it was applied, which is what produced twenty-two lots and 2.10 years and every figure downstream of them.

Real accounts have a balance. Eventually one of two things happens — the operator cannot pay for the next assignment, or the broker will not lend them the difference — and the put does not get sold. This section is about that operator.

The change is not a refinement. An unconstrained wheel is a system in which every arrival is served immediately and forever, no matter how many are already inside; a constrained one refuses arrivals when it is full. The first is the classical infinite-server queue that Part II has been describing. The second is a **loss system**, and its arrival rate is no longer something the operator sets. It is something the account's capital decides.

**Everything before this section is the case A = ∞, and this section recovers it exactly.** With unlimited equity, capacity is unlimited, no put is ever refused, nothing is ever borrowed, and every formula in Parts I and II stands unaltered. That is not a reassurance offered in passing — it is the property against which the whole of what follows is checked, and the code's defaults are the unconstrained operator precisely so that the equality has to hold rather than be claimed.

## Detour: margin, and what a margin call is

> A broker will lend against shares held in an account. How much depends on the account type, and the rule is written as a fraction: the operator must keep their own money in the account equal to at least **γ_s** of what the shares are worth at market. Shares paid for in full are γ_s = 1 — every dollar is the operator's. A standard margin account is γ_s = 0.50, a portfolio-margin account 0.25, and the most aggressive arrangements available go to about 0.15.
>
> The fraction is not a loan the operator draws down deliberately. It is a *permission*, continuously re-evaluated against the market price. Buy ten share prices' worth of stock with five share prices of your own money at γ_s = 0.25 and the broker is content: the debit is five, your equity is five, and the requirement is 2.5. Now let the price fall by a third. The position is worth 6.67, the debit is still five — it does not move when the price does — so your equity is 1.67 against a requirement of exactly 1.67, and the broker sells the entire book at whatever the market pays that morning. That is a **margin call**, or more precisely a forced liquidation, since at retail scale the call and the sale are often the same event. Note how little of the fall it took: a third, on a position only twice the operator's own money.
>
> Two features of this matter for everything below. It is *not* a loss the operator chooses to realize: the position is closed by someone else, at the worst possible moment, and a subsequent recovery is of no use because the shares are gone. And it depends on the price path rather than the price at any horizon — the account is destroyed by the *lowest* point the market visits, not by where it ends up. That is what makes survival a first-passage problem, of exactly the kind [the holding-time section](#sec:holding) already met from the other side.

## Three numbers

The finite account adds three parameters to the model, and no more.

**γ_s, the equity fraction.** A property of the account type rather than a dial the operator turns: a fact about their broker and their paperwork.

**A, the account's equity**, measured — like everything else in this article — in share prices. A = 11.59 means the operator's own money would buy eleven and a half lots outright at today's price. The unconstrained model is A = ∞.

**ε, the survival tolerance.** The probability of being sold out that the operator is willing to live with. The examples use ε = 10%, and one property of it has to be flagged immediately because it recurs: **it is a statement about unbounded time.** A 10% eventual risk is not a 10% risk over any particular decade, and every probability derived from it below carries a horizon.

Margin posted as a fraction of equity is the **utilization** u, and posting γ_s per unit of exposure means u of equity carries

L  =  u / γ_s    {#eq:leverage}

of stock. The broker's own ceiling is u = 1, which is L = 1/γ_s: four times equity at portfolio margin, twice under Reg T, and no leverage at all for shares paid in full. The operator's **stopping rule** u\* is where they choose to stop selling new puts, and it need not be — and, it will turn out, should emphatically not be — the broker's.

One clarification before the machinery, since [the strategy section](#sec:strategy) has already made the argument and it should not be made twice. The quantity γ_s governs is **equity required**, which is not Track B and does not replace it. Track B remains exposure — what the position is worth at market, independent of how it was paid for — and it stays the denominator of every return in [the returns section](#sec:returns). What the finite account adds is a second ledger line beside the three tracks, and what that line determines is not return but **capacity**: how much of the strategy a given balance can run, and how far the price can fall before someone else closes it.

## The barrier

A book carried on borrowed money has a price below which it is sold out, and the price is arithmetic. A position worth M carried on equity A = M/L is financed by a debit D = M·(1 − 1/L), and the debit does not move when the price does. After the price multiplies by f, the broker compares f·M − D against γ_s·f·M and calls when

f\*  =  ( 1 − 1/L ) / ( 1 − γ_s )    {#eq:barrier}

Both boundary cases are the formula telling the truth rather than being patched. f\* ≤ 0 is an unlevered book: it owes nothing, and there is no price at which it is called. f\* ≥ 1 is a position in violation on the day it is opened, and it happens exactly at L ≥ 1/γ_s — the broker's own ceiling, recovered from the barrier rather than assumed alongside it.

The account survives if the price never touches f\* times where it started. Since ln(S_t/S₀) = ν·t + σ·W_t, this is first passage of a drifting random walk to a level a = −ln f\* below its start. Over a horizon H the reflection principle gives

P( sold out by H )  =  N( (−a − ν·H)/(σ·√H) )  +  e^(−2ν·a/σ²) · N( (−a + ν·H)/(σ·√H) )    {#eq:first-passage}

whose first term counts the paths that finish below the barrier and whose second counts those that touched it and came back. Let H grow and the first term dies while the second collapses onto a strikingly simple limit:

P( sold out, ever )  =  e^(−θ·a)  =  f\*^θ,    θ = 2ν/σ²    {#eq:survive}

**That θ is not a new constant, and the coincidence is worth stopping on.** It is the tail exponent of the depth census — the same 2ν/σ² that [the stability section](#sec:stability) uses to decide whether the capital tied up in standing inventory converges. One constant, read twice: once as the rate at which the deep strata of the warehouse thin out, and once as the rate at which a levered account's chance of destruction falls with the distance to its barrier. They are the same number because they are the same object, the exponential martingale of one drifting walk, read in two directions. The parameter that says whether expected capital is finite also says whether the account holding it survives, and an operator who has computed one has computed the other.

Inverting [eq:survive](#eq:survive) through [eq:barrier](#eq:barrier) at f\* = ε^(1/θ) gives the leverage a tolerance permits:

L_max  =  1 / ( 1 − (1 − γ_s) · ε^(1/θ) )    {#eq:lmax}

## How little leverage survives

At the running example, where θ = 1.25:

| γ_s | broker's ceiling | L_max at ε = 1% | L_max at ε = 10% | usable share of the permission |
|---|---|---|---|---|
| 1.00 (fully paid) | 1.00 | 1.0000 | 1.0000 | 100% |
| 0.50 (Reg T) | 2.00 | 1.0127 | 1.0861 | 54% |
| 0.25 (portfolio margin) | 4.00 | 1.0192 | 1.1349 | 28% |
| 0.15 (most aggressive) | 6.67 | 1.0218 | 1.1557 | 17% |

**Survivable leverage lands near 1.1 to 1.2 times total, not 1.1 to 1.2 times whatever the broker allows.** The binding constraint is very nearly independent of the permission — and the usable share of that permission *falls* as the broker grows more generous, from all of it at γ_s = 1 to a sixth of it at γ_s = 0.15. A portfolio-margin account is offered four times its equity in stock and can survive 1.13 times. The stopping rule that implements the tolerance is u\* = γ_s·L_max = **0.28**: an account that stops selling puts at twenty-eight percent utilization, where the broker would let it run to a hundred.

The reason the permitted number is so much larger is not that brokers are reckless. It is that ε is a statement about unbounded time, and the barrier at L_max = 1.1349 is far away — f\* = 0.158, an **84% drawdown**. Waiting for a stock to fall 84% takes a while:

    horizon              5 y     10 y     30 y     60 y    100 y    ever
    P(sold out)       0.001%    0.11%    2.49%    5.68%    7.79%     10%

So the eventual-risk dial is a conservative one, and deliberately so. An operator who reasons over a career rather than over eternity will accept more leverage — the same 10% risk taken over thirty years rather than forever corresponds to a considerably larger book. What the unbounded reading buys is a number that needs no horizon convention, and the rest of this section shows why that matters: the natural horizons here are emergent, not chosen.

## Capacity, and Little's law backwards

Equity A carrying leverage L_max buys room for

I_max  =  L_max · A    {#eq:capacity}

lots. A put whose assignment would breach that is not sold. And now Little's law, which [the inventory section](#sec:inventory) used to turn a known arrival rate into an inventory, runs the other way. Inventory is no longer an output — it is pinned at capacity by the account's capital. So the arrival rate becomes the output:

λ_eff  =  I_max / E[W]    {#eq:lambda-eff}

That inversion is the most useful thing in this section, and it is worth stating without the algebra around it. **The binding resource is capital, and the thing that consumes capital is holding time.** An account cannot sell more puts than its capital will let it hold assignments for, and how long it holds them is [the holding-time section](#sec:holding)'s 2.10 years. That figure has until now been the article's most *surprising* number; here it becomes its most load-bearing one. Halve the holding time and the same account runs twice the strategy.

Income follows, since every flow scales with the arrival rate:

income  ∝  L_max(γ_s, ε) · A / E[W]    {#eq:income-capacity}

It is worth writing down the version of that statement one reaches by mistake, because it is the natural one and it is badly wrong. Read capacity off the *broker's* ceiling instead of the survivable one and it becomes income ∝ A/(γ_s·E[W]) — which says a portfolio-margin account earns four times a cash account's income on the same equity, and an aggressive-margin account six and a half times. The overstatement is the ratio 1/(γ_s·L_max): **1.8× at γ_s = 0.50, 3.5× at 0.25, 5.8× at 0.15.** Correctly risked, a portfolio-margin account earns **13% more** than a cash account on the same equity, not four times as much. The broker's fraction is a nearly irrelevant parameter dressed as a decisive one.

### The approximation this rests on

The constrained steady state is taken to be the unconstrained one **thinned uniformly** — every flow and every stock scaled by λ_eff/λ, with the shape of the depth census unchanged. That is an assumption, and it is the assumption a whole section of results rests on, so it was measured rather than argued. Simulating a blocked account against an unconstrained control on the same price paths over sixty years:

    quantity                     constrained   thinned prediction    error
    puts sold                          0.699                0.699    +0.0%
    mean inventory, lots              10.140               10.065    +0.7%
    income per year                    0.590                0.588    +0.4%
    implied E[W]                       1.395                1.385    +0.7%

Under one percent on everything count-like. Thinning is a good approximation, and the capacity and income figures below rest on solid ground. Where it bends is composition, not count — a subject this section returns to once the machinery it depends on is in place.

## A\*, the equity a wheel actually needs

Capacity has to be at least the strategy's own appetite, or the account spends its life refusing trades. The strategy's appetite is the stationary inventory E[I(∞)], so the equity above which the constraint never binds is

A\*  =  E[I(∞)] / L_max    {#eq:astar}

and this is the sharpest single result of the reframe:

| γ_s | equity the broker's ceiling implies | A\*, the equity actually needed |
|---|---|---|
| 1.00 | 21.82 | 21.82 |
| 0.50 | 10.91 | 20.10 |
| 0.25 | 5.46 | 19.23 |
| 0.15 | 3.27 | 18.88 |

Read the two columns against each other. A portfolio-margin operator, told they may hold four times their equity, would size the account at 5.46 share prices to run a strategy that demands 21.82 lots. They need **19.23** — a factor of 3.5. At the most aggressive margin available the same gap is **5.8×**, and it widens with every increase in the permission, which is the opposite of what the permission is for.

And the whole of that permission, correctly risked, buys a **12% discount** on the equity required. Not four times more strategy per dollar; twelve percent less capital. **Capacity comes from equity, and leverage is nearly irrelevant to it.** Nineteen share prices of the operator's own money, to run one weekly put on one name.

### Below A\*, and how slowly it bites

An account smaller than A\* does not fail. It runs a fraction of the strategy, and the fraction is exact: throughput retention is **A/A\***, and the realized leverage of such an account is exactly L_max. Both are identities rather than fits — the account fills to capacity and stays there, so its inventory *is* I_max and its arrival rate *is* [eq:lambda-eff](#eq:lambda-eff).

The interesting part is how long the account takes to notice. **T_sat**, the time until expected inventory reaches capacity, replaces the unconstrained model's arbitrary "90% of the asymptote" convention with a real threshold — the date the account starts refusing puts:

    equity A            1.00    3.00    5.00   11.59   15.00   19.04   19.23
    capacity, lots      1.13    3.40    5.67   13.15   17.02   21.61   21.82
    throughput          5.2%   15.6%   26.0%   60.3%   78.0%   99.0%    100%
    T_sat, years         0.1     0.9     2.4    18.5    44.4     270   never

Two things in that table, pointing opposite ways.

**The good news is real but it is a trade, not an escape.** [The inventory section](#sec:inventory) reported that the unconstrained equilibrium takes ninety years to approach, and called it a limit no participant reaches. A constrained account does reach its equilibrium, because a capacity ceiling truncates exactly the slow deep tail that made the approach take a lifetime — 2.4 years at A = 5, under a year at A = 3. But it reaches it in proportion to how little of the strategy it is running. An operator who wants to be at equilibrium in two years gets there by running a quarter of the wheel. An operator running all of it inherits the ninety years unchanged, and one running 99% of it waits 270.

**The bad news is the top of the table.** An account at the model's own thirty-year capital — 11.59 share prices, which is what [the returns section](#sec:returns) reports the strategy as consuming — runs at **60% throughput**, and takes 18.5 years to find out. Smaller accounts are worse in a way that deserves to be stated rather than softened: at A = 5 the strategy runs at a quarter of its rate, and at A = 1 at a twentieth. These are reachable steady states in which the wheel is barely running. That is a legitimate negative result about the strategy at small scale, and it is not a range of outcomes to be presented optimistically.

### And every number above is a number about one stock

A\* = E[I(∞)]/L_max inherits everything E[I(∞)] is sensitive to, which is a great deal. Sweeping the parameters one at a time, each cell re-solving the whole walk:

    sigma            15%      20%      25%      28%        30%
    E[W], years     1.18     2.10     4.73   >12.12   infinite
    A*              7.97    19.23    48.97  >126.08   infinite

    mu                4%       7%      10%      13%
    A*              none    19.23     6.81     3.74

Two notes on the edges of that table. "**>**" is a lower bound: the walk was still shedding lots when the computation was cut off, so the true figure is larger. And the two failing cells fail in different ways. At σ = 30% the drift ν is exactly zero — this is [the stability section](#sec:stability)'s first boundary, σ = √(2(μ−δ)), arrived at from the capital side — so holding time is infinite and no finite equity suffices. At μ = 4% the drift has gone negative and there is no A\* at all: a fixed fraction of every year's assignments never returns, so the account does not need more equity, it needs a different stock.

The dials an operator *chooses* behave: A\* moves exactly as 1/T along the cadence, nearly proportionally with p\*, sub-linearly in the call length. The two parameters an operator only *estimates* do not. The elasticity of A\* to volatility at the running example is **3.5** — a 1% relative error in the volatility estimate is a 3.5% error in the equity required — and it *rises* as volatility does, averaging 4.2 over the move from 20% to 25% and growing without bound as the stability boundary is approached. Two stocks a practitioner would describe identically, "a quality name around 20 vol", differ by **2.5×** in the capital their wheels need if one of them is actually at 25.

The effect compounds, because both terms of A\* move the same way: survivable leverage collapses toward 1 exactly where inventory demand explodes. **The 12% equity discount that the broker's permission buys is 35% at σ = 15% and 0.4% at σ = 25%.** Leverage stops helping precisely where capital is scarcest.

And the operational consequence, which is the one to carry: an account sized correctly for the running example — A = 19.23 — and run on a σ = 25% stock retains **39.3% throughput and saturates in 29.9 years**. Sizing for the wrong stock does not produce an error of a few percent. It produces an operator running a fraction of the strategy they think they are running, and it takes them decades to find out.

**So A\* must be read as a function of the stock and never as a number.** It is not a constant of the strategy; it is the strategy's most parameter-sensitive output.

## What the operator does with the cash

Nothing so far has said what happens to the income. It turns out to matter more than γ_s, more than the broker, and more than almost anything else in this section — and it is the one lever on this list that the operator fully controls.

Liquidation is a statement about the ratio of debit to market value, R = D/M. With inventory pinned at capacity, M moves only with the price, so ln M has drift ν. The debit compounds at the borrowing rate r_b and is fed by whatever cash is taken out beyond what the strategy brings in, so dD/dt = r_b·D + draw − income and

g  =  r_b + ( draw − income ) / D    {#eq:debit-growth}

Then ln R is a Brownian motion with drift g − ν, started at ln(1 − 1/L) and absorbed at ln(1 − γ_s) — the same barrier, the same distance, the same reflection formula. **A cash policy enters survival in exactly one way, by displacing the drift.** Only the exponent moves:

θ_eff  =  2 ( ν − g ) / σ²    {#eq:theta-eff}

Every survival result above reads ν − g where it read ν, and that is the whole change.

This immediately exposes something that was hidden in plain sight: **the static barrier of [eq:barrier](#eq:barrier) is a policy, not the absence of one.** g = 0 holds exactly when draw = income − r_b·D — the operator who *services the interest and withdraws the rest*. That is a perfectly sensible way to run an account, and every figure above is its figures. Its two neighbours are nowhere near it.

Simulating four cash policies on the same account, the same paths and the same stopping rule, thirty years past saturation:

| what is done with the income | liquidated | what the static barrier says |
|---|---|---|
| retain everything | **0.35%** | 0.92% |
| service the interest, withdraw the rest (g = 0) | 1.11% | 0.78% |
| draw only enough to keep the account's size | 3.95% | 1.09% |
| withdraw the income, let the interest accrue | **8.64%** | 1.06% |

**The cash policy moves survival by a factor of twenty-five. The barrier formula does not see it at all** — it reads between 0.78% and 1.09% for all four. Full retention is *safer* than the closed form; withdrawing the income is eight times worse than servicing it.

The mechanism is the ranking's own explanation. Retained income repays the debit, so g goes strongly negative and the account de-levers itself. Withdrawn income leaves the interest compounding against a price whose median grows at ν = 2.5% while r_b = 5% — a race the borrower loses, and only the dividend closes any of the gap, which a withdrawn dividend does not.

One honest qualification, because it withdraws an appealing piece of arithmetic. The closed form says the withdraw-everything policy pins g = r_b = 5% exactly, against ν = 2.5%, so the third stability boundary below is crossed by a factor of two. Simulated, the realized g under that policy is **+1.3%, not 5%** — withdrawing the income shrinks the account faster than the interest compounds the debit, and the linearization behind [eq:debit-growth](#eq:debit-growth) is exact only where the drain is proportional to the debit. The boundary is crossed by rather less than the closed form advertises. It is crossed nonetheless, and the ranking of the four policies survives intact. Quote ν > g as the criterion and the table as the evidence; do not quote g = r_b as a measured rate.

**A third stability boundary.** [The stability section](#sec:stability) found two conditions for the wheel to work: lots come back iff ν > 0, and the capital in them comes back iff m > σ². The finite account adds a third in the same currency — the account survives iff **ν > g**, the price's median growth outrunning the debt's — and [the stability section](#sec:stability) is where the three are set beside each other and compared.

It belongs beside the other two rather than above them, for a reason worth naming: it is the only one of the three that does not bind an unlevered account at all. An operator who borrows nothing is exempt. It is also the only one of the three the operator can *move*, since g is a cash policy and the other two are properties of the stock.

### The maximum sustainable draw

[eq:survive](#eq:survive) is one equation in two unknowns. [eq:lmax](#eq:lmax) read it as an equation in L at g = 0; read instead as an equation in g at a given L,

ν − g  =  σ² · ln(ε) / ( 2 · ln f\* )    {#eq:gmax}

both logarithms being negative, so the sustainable growth rate falls as the barrier is approached. Inverting through [eq:debit-growth](#eq:debit-growth) turns it into cash:

draw_max  =  income + ( g_max − r_b ) · D    {#eq:draw}

This is a **constraint, not an optimum.** It does not say what an operator should withdraw; it says what a chosen leverage costs in spendable cash. And what makes it worth reporting is that the answer goes negative, at a leverage far below anything a broker would query. At A = 11.59 and γ_s = 0.25:

    leverage L         1.000    1.019    1.135    1.250    1.500    1.883
    barrier f*         0.000    0.025    0.158    0.267    0.444    0.625
    P(sold out, ever)   0.0%     1.0%    10.0%    19.2%    36.3%    55.6%
    draw, % of equity  4.63%    4.65%    4.58%    4.30%    2.86%   -2.14%
    excess RoE        +1.68%   +1.71%   +1.90%   +2.09%   +2.51%   +3.15%

Two readings of the same six columns, and they point in opposite directions. Down the last row, leverage improves the reported return on equity monotonically, from 1.68% to 3.15%. Down the row above it, the cash the operator may actually take out is flat to within a few basis points as far as the survivable leverage — the first rungs buy nothing and cost nothing — and then **collapses, and goes negative**: a demand for deposits rather than a permission to withdraw. Return on paper and cash in hand move opposite ways, and only one of them is spendable.

Note also what the draw column does *not* do along the account-size axis: it is a flat 4.58% of equity at every A below A\*. That degeneracy is not a coincidence but a tautology — g_max solves the same equation L_max was solved from, so wherever the stopping rule binds it returns exactly the policy that rule was chosen under, g = 0. There is no slack anywhere the constraint is active. The draw axis is sharp along leverage and empty along size.

**And a warning about the phrase "sustainable", which this section uses in two incompatible ways.** The 4.58–4.63% above holds the *liquidation risk* fixed. It does not hold the *account* fixed: the g = 0 policy keeps the debit constant in dollars, while everything in this article counts an account in share prices, and a dollar-constant account shrinks against a compounding price. Simulated, an account following the frontier's own cash policy **loses half its throughput** — 31.8% against the 60.3% the table above reports — sliding away from its capacity at over 2% a year. Staying stationary in the units the model counts costs a draw of r + excess − m = **2.12% of equity per year**. Two figures, both called sustainable, a factor of two apart, because they hold different things constant. **The article's frontier figures are the arithmetic of an account that stays the same size; an operator who wants to draw 4.6% is choosing a shrinking business.**

## The ratchet: where the closed form breaks

Everything to this point has treated the barrier as static — the book frozen, the price moving. That is the assumption [eq:barrier](#eq:barrier) is built on, and it is time to test it, because a real account does not hold still.

Simulate the same paths twice. Once with the book frozen at the moment the account first saturates, the price alone moving it; once with the account allowed to go on operating under its stopping rule. The frozen run is [eq:survive](#eq:survive)'s assumption measured rather than computed, and it passes cleanly: 1.09% against a closed form's 1.01% at thirty years past saturation, well inside a standard error of 0.17 points, and across two orders of magnitude of probability at a more heavily levered testbed the worst disagreement is 1.6 standard errors. **The closed forms are right about what they describe.**

What they describe is not an operator. The same paths, with the account operating:

    thirty years past saturation      frozen book       live account
    P(sold out)                            1.09%             3.95%
    standard error                        +-0.17            +-0.33

**A factor of 3.6, at identical leverage on identical prices.** The mechanism is a ratchet, and it is the cleanest statement in this section of what a static barrier gets wrong.

A frozen book *de-levers as the price rises*. That is the whole of the closed form's comfort: every rally puts distance between the account and its barrier, permanently. An operator on a utilization rule does the opposite. A price rise raises their equity, the rule then permits another put, and they sell it — so the barrier follows the price up. A price fall merely blocks, and the barrier stays where it is. **The barrier ratchets upward and never comes back down.** Measured directly: the drift of ln(M/D), which is precisely what the barrier sees, is **−1.55% ± 0.10 per year** where the closed form assumes ν − g = **+2.50%**. The quantity the formula treats as drifting safely away from the barrier is in fact drifting toward it.

So the untended steady state is the state of maximum fragility, and **the stopping rule is mandatory rather than prudent**: a mechanical put-selling rule with no withdrawals converts the broker's permission into actual leverage without the operator ever deciding to lever anything.

### Where the drift stops, and why it is not the broker's ceiling

The account does not ratchet up forever. It stops at the strategy's own appetite: an account cannot hold more than the stationary inventory however much it is permitted, so realized leverage is capped at E[I(∞)]/A — **1.883** at A = 11.59, against a permitted 4.00. The wheel simply has nothing to buy with the rest of the money.

And 1.883 is the last column of the draw table above. At that drifted leverage the account's excess return on equity reads **higher, 3.15% against 1.68% unlevered**, while the cash it may sustainably withdraw has gone to **−2.14% of equity per year**. That pairing is the answer to why the stopping rule is mandatory, and it is not the obvious answer. The drifted account does not look bad on paper — it looks *better*. What it cannot do is pay anybody. An untended wheel migrates to a state of higher reported return, higher fragility, and negative distributable cash, and only one of those three is visible in a performance figure.

### Two smaller corrections, both in the operator's favour

**Realized leverage sits well below the stopping rule.** The prudent account's is **0.745** against a rule of 1.1349, because a book refilled one lot a week is under its ceiling most of the time. At small account sizes the effect is stronger still and becomes discrete: at A = 5, integer lots mean the book stops at 5 lots against a capacity of 5.67, the account **never borrows at all**, and its permitted 13% leverage is unreachable. Its barrier is vacuous.

**And the fill-up years are years the account cannot be sold out in.** The closed form starts a saturated account; a real one is unlevered for its entire fill-up. From an empty book the prudent account's liquidation probability is **0.92% by thirty years and 12.15% by sixty** — against 3.95% in the thirty years *after* saturation. Note the second figure against the ε = 10% the stopping rule was solved under. Allowed to keep buying, the account exceeds its own eventual-risk tolerance inside sixty years, which is the ratchet showing up in the one number the operator chose.

## Capacity moves with the price

One mechanism has been implicit throughout and deserves to be stated on its own, because it is short and it overturns an intuition.

Capacity in *lots* is equity over the requirement per lot. With the account holding I lots and a cash balance C — negative when it is a debit — equity marked to market is C + I·S, so

I_max  =  I / γ_s  +  C / ( γ_s · S )    {#eq:capacity-lots}

and the price-dependence runs entirely through the second term. **A net creditor's capacity in lots rises as the price falls**: the same cash buys more of a cheaper stock, and it buys it faster than the held lots lose value. **A net debtor's capacity falls**, and it falls to meet the book — I_max = I exactly when equity reaches γ_s·I·S, which is the maintenance requirement. That is the margin call, seen from the other side: *the margin call is the moment capacity falls to meet the book.*

The prudent account is a net creditor for most of its life, realized leverage of 0.745 being what that looks like. So for the accounts this section recommends, a falling market makes blocking *less* likely, not more.

## The census the constraint leaves behind

Which settles a question the reframe raised and got backwards.

Blocking does not remove arrivals at random; it removes them when the account is full. The natural guess is that a constrained book is *shallower* than an unconstrained one — blocking bites during drawdowns, so the account misses exactly the lots it would have bought cheapest, which are the ones that would have gone deepest. Measured against a simulated unconstrained control on the same paths, that guess is **wrong, and wrong in sign**:

    depth census                      unconstrained    constrained, after saturation
    share of lot-time deeper than 35%        0.494                            0.532
    mean depth                              0.4916                           0.5174

**A blocked book is 5.3% deeper**, with the deepest bin's share up 3.8 points.

Two reasons the intuition failed, and both are already on the page. Blocking removes the *newest* arrivals — and a new lot is a shallow lot, entering 1.6% below its strike by [the entry section](#sec:entry)'s law. Refusing arrivals therefore strips the shallow end of the census, not the deep end. And the drawdown story was backwards too, by the previous subsection: a near-unlevered account's capacity in lots *rises* as the price falls, so blocking is if anything rarer during a drawdown, not more common.

The effect is a saturated-regime statement and should be quoted as one: averaged over the whole run, fill-up years included, the same comparison reads −1% and the distortion washes out. But its direction matters, because it points the wrong way for the operator. The composition error of uniform thinning makes the constrained book slightly deeper — slightly slower, slightly less able to earn on its calls — than the count-based figures above assume.

## What the option market thinks

[The stability section](#sec:stability) ran the two stability boundaries under the market's own pricing drift and found that the option market prices this stock as one whose wheel inventory never clears. The finite account has a matched pair, and it is the free test of whether any of this machinery is right.

Under m = r − δ the tail exponent falls from θ = 1.25 to θ = 0.25. Everything in this section moves with it:

| | real world | the market's prices |
|---|---|---|
| L_max at ε = 10% | 1.1349 | **1.00008** |
| P(sold out) at L = 1.1349 | 10.0% | **63.1%** |
| A\*, equity required | 19.23 | 93.65 |
| E[W] | 2.10 y | 9.01 y |

**The leverage carrying a 10% eventual liquidation risk in the real world carries 63% under the pricing measure, and the measure permits no leverage at all** — L_max is 1.00008, which is a rounding error away from paying for everything in full. The market prices this stock as one whose levered wheel is sold out, beside its verdict that the same stock's inventory never clears. The two statements are the same statement, because they are the same θ — which is [eq:survive](#eq:survive)'s "read twice" arriving as a consistency check rather than as a remark.

None of this section was fitted to that. It is the strongest evidence available that the machinery is doing what it claims.

## Summary

The finite account changes four things and leaves one alone.

1. **Capacity comes from equity, not from permission.** A\* = E[I(∞)]/L_max is **19.23** share prices at portfolio margin against a broker's ceiling that implies 5.46, and **18.88** against 3.27 at the most aggressive margin available — a factor of 5.8 — while the whole of that permission, correctly risked, buys a **12% discount** on the equity required.
2. **Survivable leverage is near-independent of what the broker allows**, landing at 1.1–1.2× total across every account type, so that the usable share of the permission falls from 100% to 17% as the permission grows.
3. **Little's law runs backwards**, so income is proportional to L_max·A/E[W] and mean holding time becomes the strategy's binding operational quantity.
4. **The account has a failure mode the unlevered wheel does not**, governed by ν > g, and it is the only one of the three stability boundaries the operator can move — by a factor of twenty-five, by deciding what to do with the income.

What it leaves alone is the return. Leverage multiplies both the wheel and the buy-and-hold benchmark it is measured against, so [the returns section](#sec:returns)'s verdict survives the reframe untouched. The finite account is not a story about making more money. It is a story about how much of the strategy an operator can actually run, how long it takes them to find out, and who closes the position when it goes wrong.

And one warning that outranks all four. **The closed forms in this section are right about capacity and wrong about survival**, and by a knowable amount: uniform thinning holds to under 1%, T_sat lands at 18.9 years simulated against 18.5 analytic, and the static barrier understates a live account's liquidation risk by a factor of 3.6 because a book that is refilled after every recovery ratchets its barrier upward and never lowers it. Every survival figure here should be read as a lower bound on what an operating account faces.

(The simulated figures in this section come from `python code/wheel_sim.py --scenario constrained --paths 4000`, at a fixed seed; the analytic ones from `python code/model.py`.)
