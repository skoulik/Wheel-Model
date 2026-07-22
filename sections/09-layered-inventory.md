# The Layered Inventory: Testing the Homogeneous Approximation {#sec:layered}

## What we assumed, and how to test it

Everything so far rests on one large simplification, adopted openly in [the recovery section](#sec:recovery): **homogeneity** — every lot in inventory shares the same recovery probability q, the one computed for a freshly assigned lot. Reality is layered. Each lot's call strike is frozen at the price level where it was assigned, all lots ride the same price path, and a market that keeps falling leaves old strikes stranded far above it. We flagged the concern; now we test it.

The test is brutally direct: rebuild the wheel *exactly* — one simulated price path at a time, every put priced and struck by the rules of [the assignment section](#sec:assignment), every assigned lot carrying its own frozen strike, every call settled against the actual path — and let the inventory do whatever it does. No averaging anywhere. Then compare against the homogeneous predictions [eq:istar](#eq:istar), [eq:run-rate](#eq:run-rate), and [eq:capital](#eq:capital).

## Detour: Monte Carlo simulation

> A **Monte Carlo simulation** answers "what does this model imply?" by brute force: generate many random futures according to the model's own rules, run the system through each, and average the results. By the law of large numbers, with enough runs those averages converge to the model's true expectations — including ones far too tangled to compute by hand. Three things make such an experiment trustworthy: it must use *exactly* the same assumptions as the formulas it is checked against (ours does — the same lognormal price model, parameters, and mechanics; only the averaging step is removed); it must be *validated* on quantities that can be computed by hand; and it must be *reproducible* (ours runs from a fixed random seed; `code/wheel_sim.py`). Glasserman's *Monte Carlo Methods in Financial Engineering* is the standard finance reference.

## The experiment

Mechanics exactly as in [the strategy section](#sec:strategy), parameters of the running example: monthly puts struck by the p\* = 20% policy of [eq:kstar](#eq:kstar), quarterly calls at each lot's entry strike, total return μ = 7%, δ = 2.5% gross (δ_net ≈ 2.1%), σ = 20%, r = 5%. We simulate 200 independent 30-year paths — about 13,800 assigned lots.

Three validation checks tie the simulation to the formulas before we trust it further:

- Realized assignment frequency: **19.2%** per put — exactly the real-world probability [eq:p-rw](#eq:p-rw) predicts under this strike policy (and visibly below the risk-neutral 20%: the conservatism margin of [the assignment section](#sec:assignment), now on display in data).
- Mean drop at assignment: **7.6%**, against 7.7% from [eq:d-mean](#eq:d-mean) at the policy strike.
- Exit rates, binned by how far each lot sat below its strike when its call was sold, match [eq:q](#eq:q) evaluated at that depth to three decimals in every bin.

Same physics, then. Whatever differs from the earlier sections is the fault of the averaging, not of the model.

## Finding one: the warehouse is far fuller than I\*

The homogeneous equilibrium for these parameters is I\* ≈ 1.3 lots. The simulated 30-year average is **4.7 lots** — three and a half times more. The mechanism is visible in the composition of the standing inventory. Define a lot's **depth** as how far the current price sits below the lot's frozen strike:

    depth of lot          share of      exit rate    q at that
    below its strike      lot-quarters  observed     depth (eq:q)
    0 – 2%                    8%          0.48         0.49
    2 – 4%                    6%          0.41         0.41
    4 – 7%                    7%          0.31         0.32
    7 – 9%                    6%          0.22         0.22
    9 – 14%                   8%          0.12         0.12
    14 – 20%                 10%          0.04         0.04
    20 – 30%                 15%          0.004        0.005
    beyond 30%               39%          0.000        0.000

A *fresh* assignment lands about 3% below its strike, where recovery odds are near-even. But the standing inventory is not made of fresh lots: fast lots leave quickly and barely register, while every lot that catches a drawdown lingers for exactly as long as it stays deep. The census over-represents the slow — the same reason a hospital's beds hold sicker patients than its admissions desk sees. In the time-average, **39% of all lot-quarters sit more than 30% under their strike, where the recovery probability is zero to three decimals**, and over half sit beyond 20%. The inventory-weighted average recovery probability is 0.115 per quarter — not the 0.40 of a fresh lot — and dividing the arrival rate by *that* explains the fuller warehouse.

## Finding two: three kinds of lots

Homogeneous q makes a sharper prediction than a mean: each call period is an independent coin flip, so the number of call periods a lot needs should follow a geometric distribution. It does not:

    call periods to exit      1      2      3      4      5      6     >6
    simulated share         0.44   0.16   0.09   0.05   0.04   0.03   0.20
    geometric(q) share      0.40   0.24   0.14   0.09   0.05   0.03   0.05

First-period exits match — a fresh lot really does behave homogeneously. Beyond that the distributions part company: the simulated tail past six quarters is **four times** the geometric one. Following lots to the end (and counting the ones still held when a 30-year path closes — about 9% — as "at least this long"): a third are still held after one year, 17% after three years, 7% after ten. The inventory sorts itself into three populations — a **fast lane** that exits on the first call or two, a **metastable** middle that resolves in a year or three, and a **trapped** tail measured in decades. Nothing in the model puts them there; a single recovery formula and a common price path generate all three.

## Finding three: the income was right; the capital was not

The realized Track A run rate is 0.0181 of S₀ per month in premiums plus 0.0081 in dividends — the premium piece within 3% of what [eq:run-rate](#eq:run-rate) predicts. The self-recycling property holds; the income machine works exactly as advertised. But the **capital** committed averages **7.7·S₀ against the ≈1.5·S₀ of [the returns section](#sec:returns)**, and capital is the denominator of everything. The true excess return of the running example comes out at **−0.9% per year**, against the +10.9% the homogeneous accounting reported. The comfortable number was an artifact of averaging: it priced the warehouse as if it held fresh lots, when in fact it holds the deep ones — lots whose calls sell for nearly nothing and whose capital waits years for a recovery, earning only its dividend.

## Finding four: the dividend's trade-off resolves — against the wheel

Notice that the dividend carry came out at 0.0081 per month — **3.7 times** the homogeneous prediction. This is the flip side of finding one: carry accrues per unit of *holding time*, and holding time concentrates on exactly the deep lots the averaging misses. The suspicion raised at the end of [the returns section](#sec:returns) is confirmed, and quantitatively it resolves as follows (30-year averages, sweeping the gross yield at fixed total return):

    gross yield δ        0%      1%      2.5%     4%      6%
    mean inventory      3.7     4.0      4.7     5.5     6.8
    capital (·S₀)       5.3     6.1      7.7    10.0    14.3
    excess return    −0.7%   −0.8%    −0.9%   −1.1%   −1.2%

The carry is real and large — a third of all income at δ = 2.5% — but every point of yield is paid out of the very price drift the recovery leans on ([the recovery section](#sec:recovery)'s fourth monotonicity), so the strata deepen faster than the carry compensates. Under the honest convention — total return fixed, dividends carved out of it — yield is mildly *negative* for the wheel, monotonically. (If instead one assumes dividend payers simply return δ *more* in total, the sign flips; the conclusion is convention-sensitive, and we state ours openly: dividends are not extra return, they are a different route for the same return.)

## Finding five: forget the Poisson bell

The homogeneous model promised a Poisson-shaped inventory: variance equal to the mean, P(I = 0) = e^(−I\*). The simulated variance is **4.8 times** the mean, and the warehouse is empty 14% of the time — sixteen times the Poisson figure for the same average. The single-name inventory alternates between long empty-or-light stretches and deep drawdown pile-ups; simultaneous multi-lot call-aways (a recovery sweeping through several strikes at once) occur on 14% of exit dates. The caveat of [the queue section](#sec:queue) was directionally right but understated: on one underlying, only the rate-balance logic survives; the distributional comfort — the ±√I\* fluctuations, the e^(−I\*) idle probability — belongs to a diversified portfolio of independent wheels, not to a single name.

## What needs explaining

Five findings, one shape: everything the homogeneous model gets wrong, it gets wrong in the same direction, and by factors that beg for a formula — inventory ~3.5×, dividend carry ~3.7×, tail beyond six quarters ~4×. The regularity suggests these are not five separate phenomena but one: a lot's depth wanders under a simple random process, exits happen when that process crosses zero, and every finding above is a statistic of that crossing time. The next section makes this exact — and in doing so replaces simulation with formulas we can interrogate.

Every number quoted in this section is reproduced by `python code/wheel_sim.py --scenario check` (and the sweep by `--scenario sweep`) at the fixed seed.
