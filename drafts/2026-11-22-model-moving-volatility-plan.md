# `model.py` carries the moving volatility — plan

**Status: agreed 2026-11-22**, decision by decision with Sergei, before any code; the
measurements under *What the tests found* were run first, in scratch scripts, so each
decision carried its crux. The sequence at the end is Claude's.

Step 8 of [the moving-volatility plan](2026-11-21-moving-volatility-plan.md) (TODO II-40).
Sergei, 2026-11-22: "I'd extend the model, to be consistent and support less
implementations." Its step 7 measured every Part II result under the fitted process in the
simulator, and Part II is to carry those results side by side with the constant-σ model's;
this plan makes `model.py`, the single source of formulas, produce them.

## What is required

From the handoff at the end of step 7:
- **At constant σ every present figure is reproduced exactly** — the present code path,
  untouched, and `verify_examples.py` passing as it does now.
- **With the volatility moving, the results agree with step 7's simulator figures within
  their errors** (`data/magnitudes.json`): the gap at assignment and its tail, the
  first-expiry share, holding, inventory at 5, 10 and 30 years, the census, the excess, the
  book's delta by channel, the betas, a volatility point's worth, §10's boundaries.
- **The exact tests hold.**

## The shape of it

The constant-σ model is one-dimensional because a lot's depth x is a walk with independent
steps. Under the fitted process the steps are not independent: a period's move depends on
the volatility, and the volatility on the moves before it. The state that makes the walk
Markov again is the lot's depth together with the stock's volatility state and the week of
the earnings cycle. The model becomes a walk on that larger state, stepped a call period at
a time, with each period's transition — the move in depth and where the volatility goes —
tabulated by simulating the fitted process (`volprocess`) from every volatility node, as
`fairprice` does for prices. The ledger downstream of the walk (`economics`, the census,
the betas) is the same arithmetic, summed over the larger state.

## What the tests found (2026-11-22)

All on the fitted process with jumps, earnings off (they do not enter h), the running
example, Standard regime; 600,000 stationary paths, 120,000 assigned lots. Tests 1 and 2
drew their own samples, so each table is read against its own exact column.

**1. Folding the fast factor away loses the lots that matter.** A lot's first call period
simulated exactly from its state at entry, against the same period with h_fast replaced by a
draw from its stationary law given h_slow — what a model carrying h_slow alone assumes.
Common random numbers.

| | exact | fast factor folded |
|---|---|---|
| h_fast at entry, all lots / gap > 5% | 0.212 / 0.508 | 0.123 / 0.223 |
| left at first expiry | 0.4299 | 0.4251 (−0.48 ± 0.04 points) |
| … gap 5–10% | 0.199 | 0.173 |
| … gap > 10% | 0.096 | 0.071 |
| first call premium | 161.0bp | 153.4bp (5% cheap) |

The simulator resolves the first-expiry share to ±0.04 points, so the fold misses by twelve
of its errors, and the miss is concentrated in the deep lots — the tail Part II now
foregrounds. A lot assigned by a down jump enters with its volatility nearly doubled, and
about a fifth of that is still there on average over its first call period (h_fast halves
in 6 sessions; φ_f^20 = 0.10).

**2. fairprice's grid is fine for prices and too coarse for a chain.** Its 13 × 11 nodes
(spacing 0.1 in h_fast, 0.2 in h_slow) interpolate prices well, but a chain stepped on them
compounds the grid's own error every period. Two constructions, against the exact process:

| grid (nodes) | construction | sd h_slow | E[e^(2H)] | corr of H at 1 / 3 / 6 periods | left at first expiry |
|---|---|---|---|---|---|
| exact | | 0.2862 | 8.366 | 0.618 / 0.448 / 0.297 | 0.4339 ± 0.0014 |
| 0.1 × 0.2 (143) | node | 0.3352 | 8.868 | 0.656 / 0.477 / 0.317 | 0.4296 |
| 0.1 × 0.2 (143) | cell | 0.2945 | 8.492 | 0.604 / 0.393 / 0.222 | 0.4319 |
| 0.1 × 0.1 (273) | node | 0.2961 | 8.444 | 0.622 / 0.449 / 0.298 | 0.4319 |
| 0.1 × 0.1 (273) | cell | 0.2889 | 8.366 | 0.615 / 0.434 / 0.280 | 0.4334 |
| 0.1 × 0.05 (533) | node | 0.2885 | 8.377 | 0.617 / 0.444 / 0.295 | 0.4322 |
| 0.1 × 0.05 (533) | cell | 0.2868 | 8.388 | 0.617 / 0.443 / 0.293 | 0.4328 |

- *node*: paths start at each node; an end state is split linearly onto its four nodes.
  The split adds Δ²/6 of spread a period on average — 35% of h_slow's own at Δ = 0.2, 9% at
  0.1, 2% at 0.05 — and the stationary law widens by the same fraction.
- *cell* (Ulam's construction): each node stands for its cell, paths start at the stationary
  points inside it, ends are binned to cells. The stationary law is right by construction,
  but a lot forgets where in its cell it was, so the volatility forgets too fast.
- A third, *shrink* — each end's deviation scaled so the split adds nothing — matched the
  spread but distorted its shape (E[e^(2H)] 1–5% low) and was dropped.
- At 0.1 × 0.1 the node chain's persistence is exact and its spread 3.5% wide (E[e^(2H)]
  +0.9%); at 0.1 × 0.05 both are within about 1%. Every chain gets the first expiry within
  sampling once h_fast is carried.
- **The grid's edges clip the deep lots.** fairprice's range, h_fast −0.2 to 1.0 and h_slow
  −0.1 to 1.9, holds all but 0.06% and 0.04% of the stationary state, but of the lots
  assigned more than 5% deep, 2.4% enter with h_fast above 1.0 and 0.9% with h_slow above
  1.9 (99.9% quantiles 1.32 and 2.14); at the bottom, h_slow's 0.1% quantile is 0.06. A lot
  clipped at the edge is run at too low a volatility, so the lattice's grid must reach
  further up: h_fast to 1.4, h_slow from 0.0 to 2.3.

**3. Cost.** One call period of the walk — depth density × volatility nodes × 13 earnings
weeks, the transition applied as a batched product in Fourier space (numpy), measured on the
Windows desktop:

| volatility nodes | a call period | transition in memory |
|---|---|---|
| 11 (h_slow alone) | 3 ms | 1 MB |
| 143 | 90 ms | 170 MB |
| 330 | 300 ms | 0.9 GB |

So 273 nodes is about 0.2 s a period: a 30-year figure (390 periods) about a minute and a
half, and a stationary one — the constant-σ walk runs 8,000 periods at the running example
before its tail is closed — far more, which is decision 6's question.

**4. The constant-σ comparison has a gap of its own, mostly explained.** model.py and the
simulator at constant σ: first-expiry share 0.4046 against 0.4069 ± 0.0004, inventory at 30
years 11.40 against 11.34 ± 0.10. Both are TODO II-32's near-grid entry: at h = 0.0025 the
model reads 0.4067 and 11.33. At 5 years it reads 5.39 at h = 0.0025 against the simulator's
5.26 ± 0.05, 2.5 errors — **step 7's seed, traced 2026-11-22**: its runs at 5, 10 and 30
years share one seed, and each batch seeds its generator from it alone, so the shorter runs
are the first years of the longer one, and one fluctuation shows at every horizon, diluted
with length (2.5 errors at 5 years, 1 at 10, none at 30, in the twin alike). Rerun on three
other seeds the simulator reads 5.38 ± 0.04, 5.39 ± 0.04 and 5.34 ± 0.05 against the
model's 5.386. So the agreement test (decision 8) reads step 7's horizons as one draw, not
three, and is better run on fresh seeds.

**5. A transition tabulated by simulation is accurate enough, with the forward pinned.**
The walk's drift a call period is ν·τ_c = 0.0019 at the running example, so an error of
10⁻⁵ in a node's mean log move is half a percent of ν. Standard deviation of a node's E[R]
across six seeds:

| node | paths | plain draws | stratified (fairprice's) | stratified, shifted to the exact forward |
|---|---|---|---|---|
| typical (0.1, 0.8) | 50,000 | 2.6e-4 | 8.8e-5 | 5.2e-6 |
| typical | 200,000 | 3.4e-5 | 3.0e-5 | 4.4e-6 |
| after a jump (0.9, 1.5) | 50,000 | 8.8e-4 | 4.3e-4 | 2.4e-5 |
| after a jump | 200,000 | 1.6e-4 | 8.2e-5 | 3.1e-5 |

*Shifted*: each node's moves moved by one constant so that their gross return averages
e^(m·τ_c), which the process's compensation makes exact; it does what a control variate on
e^R does (4.6e-6 and 2.1e-5 that way), and it is also what the ledger's exact tests need of
every node. Then a typical node's drift is good to about 0.25% of ν, a turbulent one's to
about 1.5%, and the walk averages over nodes drawn independently. The error did not fall
from 50,000 paths to 200,000 at these seeds, so more paths buy little; an exit probability,
P(R ≥ 5%), is good to about 0.001 at 50,000 and 0.0004 at 200,000.

**6. The lattice can price from its own simulations.** fairprice's node pricer on fewer
paths, six seeds, at two of its nodes, against its cached tables (800,000 paths a node):

| node | paths | put's strike | put's IV | call's IV at the money / 1 sd out / 2 sd out |
|---|---|---|---|---|
| (0.1, 0.7) | 50,000 | ± 3.6e-5 | ± 0.28% | ± 0.26% / 0.22% / 0.78% |
| (0.1, 0.7) | 200,000 | ± 3.5e-5 | ± 0.15% | ± 0.11% / 0.15% / 0.34% |
| (0.8, 1.5) | 50,000 | ± 1.9e-4 | ± 0.24% | ± 0.23% / 0.23% / 0.26% |
| (0.8, 1.5) | 200,000 | ± 1.6e-4 | ± 0.10% | ± 0.08% / 0.09% / 0.13% |

Every mean agrees with the table within its error. That error is the premiums' *level*; the
excess return carries something else, a premium less its real-world payoff, and on the same
draws that difference is good to 0.01bp of spot a period at either path count (a call 2%
out at the typical node: −5.59bp, both sides shifted to their exact forwards).

**7. The earnings calendar against a chance of 4 in 13.** Full fitted process; puts sold
from the stationary state at a uniform week of the cycle, each priced knowing whether its
week holds earnings (7.6% of assigned lots come from one); the lots' first two call periods
with earnings where the calendar puts them, and again with earnings drawn at 4/13 a period
at a uniform session. Common draws, 119,622 lots:

| | calendar | 4 in 13 | difference |
|---|---|---|---|
| left at first expiry | 0.4288 | 0.4280 | +0.085 ± 0.077 points |
| left at the second | 0.1389 | 0.1391 | −0.022 ± 0.076 points |
| … lots assigned in an earnings week, first expiry | 0.343 | 0.347 | |
| … lots more than 5% deep, first expiry | 0.172 | 0.170 | |

Below the test's resolution, which at 0.08 points is coarser than the simulator's 0.04. The
cost differs more: at 350 nodes a call period takes 262 ms with the thirteen weeks carried
and 82 ms without (transition 1 GB either way).

**8. Stationary figures need thousands of periods.** The constant-σ walk's stationary
figures at the running example, by the cap on periods before the geometric closure:

| periods (years) | 500 (38) | 1,000 (77) | 2,000 (154) | 4,000 (308) | 8,000 (615) |
|---|---|---|---|---|---|
| E[T], years | 1.929 | 2.043 | 2.088 | 2.098 | 2.099 |
| E[I(∞)], lots | 20.06 | 21.25 | 21.72 | 21.82 | 21.83 |

The closure reads the tail's ratio off the last ten periods and is exact only once the walk
has settled into its slowest mode (`stationary_converged`): 2.6% short at 1,000 periods,
0.5% at 2,000, 0.04% at 4,000. On the lattice, at about 0.3 s a period and two grids for
the Richardson step, 4,000 periods is about 45 minutes a parameter set.

**9. A deep lot's far future, handed to the constant-σ walk.** 40,000 lots started at
depth 0.3 and 0.6 from the stationary volatility state, the full process run 60 years with
exits checked every call period, against `model.DepthWalk` from the same depth at ν_eff = m
− c1 (c1 = 2.02%, step 7) and the long-run variance:

| start | variance used | survival at 5 / 10 / 30 / 60 years | periods held within 60 years |
|---|---|---|---|
| 0.3 | process | 0.436 / 0.268 / 0.104 / 0.047 | 135.5 |
| 0.3 | σ² = 0.0400 | 0.449 / 0.284 / 0.108 / 0.046 | 139.5 (+3.0%) |
| 0.3 | measured, 0.0437 | 0.436 / 0.277 / 0.108 / 0.047 | 137.3 (+1.3%) |
| 0.6 | process | 0.784 / 0.538 / 0.225 / 0.104 | 250.4 |
| 0.6 | σ² | 0.774 / 0.550 / 0.231 / 0.101 | 253.2 (+1.1%) |
| 0.6 | measured | 0.756 / 0.535 / 0.227 / 0.101 | 248.6 (−0.7%) |

The walk at the process's own long-run variance follows the far tail to 1–3% of its held
time, worst in the first five years. **A finding on the way:** over sixty years log S
spreads at 0.0437 a year, 9% more than the σ² = 0.04 that each session's variance averages
to. Not traced; plausibly the drift's dependence on the state (a turbulent stretch, brought
on by falls, also drags the log price at σ_t²/2), which is also what puts §10's capital
boundary at 4.31% against twice the lots' 2.02%. Owed to the article if it holds.

**10. The long run is the lattice's eigenvalues** (after Sergei's thought, 2026-11-22:
"whenever we can mathematically proof that in the limit/long horison the more complex model
converges to a simpler one, we can use this fact to simplify the simulation"). The lattice
is a Markov additive process — the volatility state a Markov chain, log S summing
increments whose law depends on it — and such a process's long run is carried by κ(θ), the
log of the largest eigenvalue of F(θ)_ab = E[e^(θR); next node b | node a], a year
(Asmussen, *Applied Probability and Queues*, ch. XI — from memory, to be opened before it is
cited): the long-run drift of log S is κ′(0), its long-run variance κ″(0), the growth of
E[S₀/S_t] is κ(−1). So §10's boundaries are c1 = m − κ′(0) and c2 = m + κ(−1), read off a
matrix of the volatility nodes alone. Jumps, no earnings, against `fairprice.boundaries`
(400 paths × 200 years: c1 = 2.026 ± 0.006%, c2 = 4.359 ± 0.014%):

| h_slow spacing (nodes), paths a node | c1 | c2 | long-run variance |
|---|---|---|---|
| 0.1 (408), 20,000 | 2.066% | 4.530% | 0.0445 |
| 0.1 (408), 60,000 | 2.052% | 4.497% | |
| 0.05 (799), 12,000 | 2.042% | 4.463% | 0.0439 |
| 0.05 (799), 40,000 | 2.029% | 4.441% | |
| 0.025, 12,000 | 2.034% | 4.448% | |

- κ(0) = 10⁻¹⁴: the chain keeps its mass, as it must.
- **The 9% excess variance of test 9 is structural**: κ″(0) = 0.044 against σ² = 0.04,
  where the 60-year simulation measured 0.0437. A Markov additive process's long-run
  variance carries the covariance between a move and the drift it later causes, which an
  average of each session's variance does not.
- **c1 converges to the simulation** (2.029% at 0.05 and 40,000 paths). **c2 does not**: it
  settles near 4.44–4.45%, 0.08 points (six errors) above the simulated 4.36%, after
  falling with both finer spacing and more paths. Not traced: the paths' noise biases a
  largest eigenvalue upward and may not be gone at 40,000, the top of the grid may clip
  the tilted chain, or the simulation's estimator may be the one off.
- **For decision 2's "see how it goes":** c2 is the figure most sensitive to h_slow's
  spread. At the main lattice's 0.1 it reads 4.50–4.53%, which would put the running
  example 0.0–0.03 points inside the capital boundary instead of 0.19. The eigenvalue
  problem needs no depth axis, so it can run at 0.05 or finer for seconds' cost whatever
  the main lattice's spacing.

## Decisions

Taken one at a time, in this order; each is recorded here as it is made.

1. **The state: both volatility factors** (Sergei, 2026-11-22: "Let's proceed with the
   option A"). A lot's state is its depth, h_fast, h_slow and the week of the earnings cycle.
   Rejected: the slow factor alone with the fast one folded into each period's move, about
   twenty times cheaper and twelve of the simulator's errors short on the first expiry,
   the miss concentrated in the deep lots (test 1).
2. **The grid: spacing 0.1 in both factors, ends split linearly** (Sergei, 2026-11-22: "let's
   begin with option A and see how it goes"). h_fast from −0.2 to 1.4, h_slow from 0.0 to
   2.3, nodes no state reaches pruned; σ̄ set from the lattice's own stationary law, so the
   year's total variance averages σ² on the lattice itself and the split's +0.9% in
   E[e^(2H)] drops out, leaving h_slow's spread 3.5% wide (test 2). Untested: what that
   spread does to the wheel's figures — estimated at about 0.4% of inventory, if the
   volatility's effects scale with H's variance — which the comparison with step 7
   (decision 8) measures. If it shows, the fallback is spacing 0.05 in h_slow, about four
   times the cost and nothing else changed. Rejected: binning ends to cells (Ulam), whose
   stationary law is right but whose volatility forgets about 6% too fast over six periods;
   fairprice's own grid, too coarse for a chain and too low at the top.
3. **The transitions come from a new numpy module** (Sergei, 2026-11-22: "Option A is the
   way"). It simulates the fitted process from every node with fairprice's stratified draws,
   shifts each node's moves so their gross return is exactly e^(m·τ) (test 5), and caches
   the result under `data/`, keyed by everything it depends on; a build is estimated at a
   minute or two a parameter set. `model.py` imports it only when the volatility moves, so
   the moving path needs numpy and the constant-σ path stays stdlib and unchanged; the
   ledger stays in `model.py`. The one thing shared with the simulator is the process's own
   stepping, `fairprice.simulate`, which is its definition and is checked against
   `volprocess` draw for draw (`fairprice --check`). Rejected: the transitions added to
   `fairprice.py`, which would tie the model to the simulator's pricing module; committing
   them for the article's parameter sets, about 100 MB a set.
4. **Prices come from the lattice's own simulations** (Sergei, 2026-11-22: "Ok, option A"),
   200,000 paths a node, each priced under the pricing measure on the same draws that move
   its lots in the real world: the put's strike at the dial (the real-world p\*-quantile),
   its premium, and the call's at every depth. At the pricing drift the excess is then minus
   the leak exactly on the lattice, and the model prices independently of `fairprice`'s
   tables, so its agreement with the simulator checks them too. Premium levels are good to
   about 0.1–0.15% in implied volatility (0.3% two sd out), the premium less its real-world
   payoff to 0.01bp a period (test 6). Rejected: reading `fairprice`'s tables — the
   simulator's prices exactly, but the test only to their accuracy (0.2 ± 0.5bp), the two
   sharing their prices, and a second build of five minutes a parameter set.
5. **The earnings calendar is carried** (Sergei, 2026-11-22: "Option A"): a lot's state
   includes its week of the thirteen-week cycle, so the lattice is the simulator's process,
   and each call is priced knowing whether its life holds earnings. About 262 ms a call
   period at 350 nodes, 1.7 minutes a 30-year figure. Rejected: earnings at a chance of 4 in
   13 a period, three times faster, whose effect on the first two expiries test 7 could not
   resolve, and which loses the pairing of a richer call with the earnings move in its life
   (the betas, not the means). It remains the contained fallback if running time binds.
6. **Stationary figures are run long on the lattice** (Sergei, 2026-11-22: "Option A"):
   4,000 periods, about 45 minutes a parameter set, once, cached — about an hour and a half
   for the two regimes the article quotes. Rejected: the lattice to 60 years and the
   constant-σ walk after it, about ten minutes, E[T] 0.2–0.5% off (test 9), kept as the
   fallback for a reader's own parameters; and no stationary figures under the moving
   volatility.
7. **What gains the moving path, and how a caller asks** (Sergei, 2026-11-22: "A with a
   disclamer that the model is simplified"). One `Config` field, `vol = "constant" |
   "factors" | "jumps" | "fitted"`, step 7's four processes; the functions that gain the
   path keep their names and arguments and dispatch on it, and constant σ runs the present
   code untouched. `economics()` is shared: only its inputs — strike, put premium, mark
   loss, entry depth — come from the lattice when the field is set. The moving path covers:
   - §05's entry: the strike, the gap at assignment and its tail, the put premium, the
     mark loss;
   - §07: survival, median and mean holding, the first-expiry share;
   - §08: inventory at 5, 10 and 30 years and stationary, the census, the time to 90%, and
     §11's A\* = E[I(∞)]/L_max;
   - §09: the excess in both tracks, the book's delta by channel, the betas, a volatility
     point's worth;
   - §10's boundaries, as eigenvalues (test 10).

   Constant σ only: the closed forms that explain a mechanism (the grid tax and its √n law,
   Siegmund's E[T], the overshoot, the trapped fraction, the early-exercise thresholds) —
   the simplified model step 7's decision keeps; and the sensitivity sweeps, a lattice
   build and run a cell. **§11's static barrier** (the liquidation probability, the largest
   leverage, saturation) **stays constant-σ in `model.py`**, beside step 7's simulator
   figures at daily closes, and **the article says so**: §11 states that `model.py`'s
   barrier figures are the simplified constant-σ model's, with the fitted process's from
   the simulator beside them. Rejected: a second lattice stepped a session at a time for
   the barrier, about twenty times the cost a period, since checking once a call period
   would miss what jumps do between checks; separate function names for the moving path,
   which would split every example and check in two.
8. **The checks** (Sergei, 2026-11-22: "Agreed as you suggest, go ahead"):
   - **Constant σ untouched**: `verify_examples.py`, the appendix and the figures
     byte-identical before and after, by diff.
   - **The pricing-drift test** on the lattice: excess = −leak to floating point, at every
     horizon, both regimes, all four processes.
   - **The real-world test**: excess = Δ̄·(μ − r) − leak, Δ̄ through the price's channel
     and the volatility's, to a tolerance of 0.5bp — the session lattice leaves a
     second-order remainder, estimated at about 0.1bp and printed — with Δ̄ reported split
     by channel; and beside it its exact discrete form, the ledger's excess against the
     sum of each instrument's own real-world edge, to floating point.
   - **Against the simulator**: differences, moving less constant, which cancel the near
     grid's offset (II-32); the simulator rerun on two fresh seeds with every horizon on a
     seed of its own (test 4); each figure of step 7's list within two standard errors of
     the difference.
   - **The lattice's own error**: h_slow at 0.05 run once at the running example (decision
     2's fallback, measured); and c2 (test 10) traced before §10 quotes it.
   - Rejected: reading step 7's figures as they stand, whose horizons are one draw.

## Sequence

Each step reviewed with Sergei before it is committed.

1. **`code/lattice.py`** (numpy), the build. For each node of decision 2's grid, one set of
   stratified draws (`fairprice.draws`, the same for every node, so the tables are smooth
   in the state), 200,000 paths, stepped by `fairprice.simulate` over a call period (20
   sessions) and a put's week (5), in the real world and under the pricing measure on the
   same draws, each node's moves shifted to the exact forward:
   - **the chain first**: the volatility nodes' transition under the real world, which
     does not depend on σ̄; its stationary law; σ̄ from that law (decision 2);
   - **the walk's transition**, per node: where its lots' volatility goes (split linearly)
     jointly with how far their depth moves, binned as `DepthWalk` bins, offset
     ⌊½ − R/h⌋, for each grid the model runs (h = 0.01 to depth 8; 0.025 and 0.0125 to 20
     for the stationary step). An earnings week convolves the move with the earnings jump
     at the period's starting state — the one approximation here, its scale off by
     e^(β_E·ΔH) with β_E = 0.25 over at most three weeks of ΔH, against the simulator's
     state at the earnings session;
   - **the entry**, per node and put kind (no earnings in the week, or earnings on each of
     its five sessions): the strike at the dial, the assignment, the entry depth jointly
     with the volatility at entry, the put's premium and its mark loss;
   - **per node, call kind (no earnings, or earnings in each of the period's four weeks,
     the session within the week averaged) and depth cell**: the fair premium and its
     implied volatility (a spread is added to the latter by the model), the real-world exit
     probability, upside surrendered and depth at exit, the betas' regression sums with
     and without the premium, and the life delta through each channel — first order in
     κ, pathwise along the pricing-measure paths (∂ log S_T/∂z_t carried forward through
     the volatility's response), no tables and no interpolation; the put's likewise;
   - **the long run** (test 10): κ′(0), κ″(0) and κ(−1) of the volatility chain, at
     h_slow 0.05 or finer.

   Built a row of nodes a worker, cached under `data/lattice/`, keyed by everything it
   depends on.
2. **A structural check before any figure**: the lattice run on a process with the
   volatility held still (θ, kicks, jumps and earnings off, one node) must reproduce
   `model.py`'s constant-σ figures to its own Monte Carlo accuracy — the walk, the entry,
   the premiums against Black–Scholes, the ledger.
3. **`model.py`**: `Config.vol`; the lattice walk (depth × node × earnings week, a call
   period at a time as a batched product in Fourier space, absorbing below zero) behind
   `occupation`, returning what it returns now plus the entry's aggregates; `economics`
   reading those; the census, the betas, `book_delta_life` by channel, stationary figures
   run long (decision 6) and cached, the time to 90%, §10's boundaries from the eigenvalues.
4. **The checks** of decision 8, the simulator's reruns in the background.
5. **`verify_examples.py`** cases for the moving path, reading the cache; the reproduction
   appendix; §00's notation for anything new; CLAUDE.md and the README brought up to date
   (the moving path's numpy dependency and its cache).

Then the section revisions of the moving-volatility plan, with *Owed to the article* as the
checklist, now with two more items: §11's statement that `model.py`'s barrier figures are
the simplified model's (decision 7), and test 9's excess long-run variance, explained by
test 10.
