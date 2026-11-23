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
9. **σ̄ is the process's, measured once and shared** (Sergei, 2026-11-22: "Option A"),
   revising decision 2's "σ̄ from the lattice's own stationary law". σ̄ is the scale at
   which the stock's total variance averages σ², a property of the fitted process and not
   of either model's grid: `fairprice.moments` measures it from 1.6 million independent
   stationary reads, good to about 0.05%, and both the simulator's tables and the lattice
   use it. Found under *Progress*: the simulator's old estimate, 400 correlated paths, read
   0.6% high at its seed, and the lattice's own law reads 0.65% low at its 0.1 grid. The
   simulator's tables are rebuilt and step 7's figures move about 0.5%, rerun on fresh
   seeds as decision 8 already asks. The lattice keeps h_slow at 0.1; its remaining error
   is the spread's shape (the gap's mean/median about 0.006 high, some four of the
   simulator's errors), with 0.05 the fallback. Rejected: each model's own σ̄ with the
   lattice at 0.05, four times the cost of every run; leaving both, which keeps a known 1%
   offset at the gap's centre.
10. **The sale, the put's week and the first call period are simulated exactly** (Sergei,
    2026-11-22: "Yes, I meant A"). Puts are sold from exact stationary
    states — independent paths, several reads each, as `fairprice.moments` takes them —
    each at a uniform point of the earnings calendar, its strike interpolated from the
    nodes' (the dial's exactness becomes the interpolation's, as in the simulator); the put's
    week and the lot's first call period are stepped from that state, in the real world and
    under the pricing measure on the same draws, so each premium pairs with its payout path
    by path and both exact tests stay exact. The grid takes the surviving lots over at the
    start of their second call period. The gap at assignment, its tail and the first expiry
    then carry no grid at all (*Progress*: the sale states' snapping to nodes was the gap's
    tail error). Untested: whether it closes the down-beta and the delta's volatility
    channel, which also involve later periods. Rejected: the exact sale state alone, which
    fixes the tail and leaves the first expiry about 0.2 points low; a finer grid in both
    factors, four to eight times every run; accepting the residuals.

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
checklist, now with these items more (Sergei, 2026-11-22: "make sure the fixes end up in the
formulas, if we show them in the article"):
- §11's statement that `model.py`'s barrier figures are the simplified model's (decision 7);
- test 9's excess long-run variance, explained by test 10;
- **σ̄'s definition and measurement** (decision 9): wherever the article or the appendix
  shows how σ̄ is set, the formula is the year's total variance averaged over the
  stationary law of the volatility state, E[e^(2H)] + Var(J)·E[e^(2βH)] + Var(Y)/65 ·
  E[e^(2β_E·H)] = σ²/(260·σ̄²), with the averages measured from independent stationary
  reads, and the appendix says how many and how well they pin σ̄ (0.05%);
- **§10's capital boundary under the moving volatility**: if the article shows a formula
  for it, it is the growth rate of E[S₀/S_T], (1/T) log E~[exp Σ K(H_t)] — equivalently the
  Markov additive process's eigenvalue, m + κ(−1) — and never the time-average of the
  tilted cumulant, which Jensen's inequality puts below it; the lots' boundary is the
  long-run drift m − κ′(0), where no such term arises;
- **sources not yet held**, wanted only when the prose is written: Asmussen, *Applied
  Probability and Queues* (2nd ed., Springer 2003), ch. XI, for the Markov additive
  process's eigenvalue and its derivatives (test 10, the boundaries, the long-run variance;
  cited above from memory, to be opened first); Ney & Nummelin (1987), *Annals of
  Probability* 15(2), for the same on a general state space, the continuous process the
  lattice approximates (optional); Tauchen (1986), *Economics Letters* 20, the standard
  reference for carrying a continuous-state Markov process on a finite grid, the lattice's
  construction (or Kushner & Dupuis, *Numerical Methods for Stochastic Control Problems in
  Continuous Time*, for the Markov chain approximation method);
- **the exact entry** (decision 10), once built: where the article describes how the model
  treats the sale and the first call period, it says they are simulated from the
  stationary state and the grid carries lots from the second period on.

## Progress

**Steps 1 and 2, 2026-11-22** (uncommitted, for Sergei's review). `code/lattice.py` builds
the running example's fitted lattice in about ten minutes on sixteen workers (σ̄ = 0.003839 a
session; stationary mass on 365 of 408 nodes); `model.py` carries `Config.vol` and the walk
(about 0.4 s a call period, three minutes to 30 years). **The structural check passes**: with
the volatility held still (one node, no response, jumps or earnings) the lattice against the
constant-σ model reads
- strike, put and call premiums, exits, upside surrendered and mark loss to 5–7 digits, the
  walk's transition to 7e-6, the gap's mean, median and tail to the simulator's constant run;
- **both exact tests to 1e-12bp** at 1, 5, 10 and 30 years — the pricing-drift test, and the
  real-world one in its exact form; by channel the real-world test reads +0.001bp;
- the betas to 1e-4 and the book's life delta to 1e-4;
- survival 7e-4 higher from the first period on, the entry's discretization: the lattice
  bins sampled entries into cells, where the constant model takes the density at each
  cell's centre (II-32's effect, from another side). So the moving lattice is read against
  the still lattice, never against the constant model, which cancels it.

**First comparison with step 7** (its one seed; the agreed check, on fresh seeds, is to come),
fitted less still against the simulator's full less constant, Standard, 30 years:

| | lattice | simulator | errors apart |
|---|---|---|---|
| excess + leak, paired | +0.3bp | +0.1 ± 0.3bp | 0.5 |
| book delta, both channels / price's alone | +0.00137 / −0.00236 | +0.00140 / −0.00389 | 0.0 / 1.8 |
| E[I] at 5 / 10 / 30 years | −0.255 / −0.346 / −0.466 | −0.156 / −0.370 / −0.678 | 1.5 / 0.3 / 1.4 |
| left at first expiry | +0.0198 | +0.0214 ± 0.0007 | 2.3 |
| up-beta / down-beta | +0.0091 / −0.0073 | +0.0073 / −0.0070 | 0.9 / 2.3 |
| gap: mean / median | 1.643% / 1.066% | 1.651% / 1.075% | 3.3 / 4.4 |
| gap: mean/median, beyond 5%, beyond 10% | 1.542, 5.43%, 0.66% | 1.535, 5.48%, 0.65% | 3.8, 2.4, 1.7 |

Everything the article quotes to two figures agrees. The gap's centre does not, by about 1%:
**the lattice's σ̄ is 1.25% below the simulator's** (0.003839 against 0.003888), because the
grid's wider stationary law (decision 2, test 2) has σ̄ calibrated down to keep the year's
variance at σ², and the diffusion at a typical state is that much calmer. This is decision
2's untested spread, now measured. A tail closure with the killed walk's j^(−3/2) prefactor
was tried as a way to cut the stationary runs and rejected: it errs as far the other way and
is unstable at short runs.

**The σ̄ gap is half the simulator's** (traced 2026-11-22). The fallback, h_slow at 0.05 (799
nodes, built in twenty minutes), gives σ̄ = 0.003854 and the gap's mean/median 1.538 (the
simulator's 1.535 ± 0.0015, 1.7 errors; 1.542 at 0.1), but closes only a third of the σ̄
gap. The rest is the simulator's: σ̄ is set from `fairprice.moments`, and at its seed that
reads E[e^(2H)] = 8.250, where three other seeds give 8.405, 8.359 and 8.371, and 600,000
independent stationary paths give 8.366 ± 0.016. A one-second estimate on 400 correlated
rows; its seed's draw happened to be low. Measured against σ̄ from the 600,000 paths,
0.003864:

| | σ̄ | against the exact |
|---|---|---|
| simulator (`fairprice.moments` at its seed) | 0.003888 | +0.62% |
| lattice, h_slow 0.1 (its own stationary law) | 0.003839 | −0.65% |
| lattice, h_slow 0.05 | 0.003854 | −0.26% |

So step 7's fitted runs sit at a total variance about 1.2% above σ² (σ ≈ 20.12%), and the
lattice at 0.1 about 1.3% below it. Decision 9 below.

**Decision 9 carried out the same day.** `fairprice.moments` now reads 400,000 independent
paths four times each, 650 sessions apart, in parallel and cached: E[e^(2H)] = 8.384 ±
0.010 (8.381 on a second seed), σ̄ = 0.003861 at σ = 20%, 0.70% below the simulator's old
value, in eleven seconds. `fairprice.VERSION` 6 and `lattice.VERSION` 2 retire every table
and lattice built on the old σ̄; step 7's twelve fitted table sets are rebuilt.

**Test 10's c2 gap, traced: the simulator's estimator omitted Jensen's term.**
`fairprice.boundaries` read c2 as the time-average of the tilted cumulant along each path,
E~[Σ K]/T, and called it exact. The growth of E[S₀/S_T] is (1/T) log E~[exp(Σ K)], larger
by Var(Σ K)/(2T) for the near-Gaussian Σ K, which the paths' own spread measures. On the new
σ̄ (400 paths × 200 years):

| process | c1 | c2, time-average | Jensen's term | c2 | by log-mean-exp over paths | eigenvalue, h_slow 0.05 |
|---|---|---|---|---|---|---|
| jumps, no earnings | 1.995 ± 0.006% | 4.290% | +0.074 | 4.363% | 4.367% | 4.369% (c1 1.997%) |
| full | 1.995 ± 0.005% | 4.247% | +0.060 | 4.307% | 4.309% | — |

So test 10's 0.08 points were two errors partly cancelling: the old σ̄ 0.6% high, which put
c2 about 0.05 higher, and Jensen's term missing, which put it about 0.07 lower. The
eigenvalue is right. Step 7's §10 figures move: **the lots' boundary is 2.00%, not 2.02%;
the capital boundary under the full process stays 4.31%** — the same figure, by the two
errors' offset — so the running example still sits 0.19 points inside it. `boundaries`
now returns c2 with the term and the time-average beside it (uncommitted, for review). The
long-run variance of log S at the new σ̄ is 0.0430 by the eigenvalue, 7.5% above σ².

**Decision 8's comparison, on the new σ̄** (`wheel_sim.py --scenario magnitudes --seed 1` and
`--seed 2`, each horizon on its own seed, `MAG_HORIZON_SEED`; pooled), Standard regime, each
model less its constant-σ reference, z the difference in the simulator's errors:

| | fitted: lattice | simulator | z | jumps: z | factors: z |
|---|---|---|---|---|---|
| E[I] at 5 / 10 / 30 years | −0.246 / −0.329 / −0.418 | −0.291 / −0.240 / −0.465 | 1.0 / −1.5 / 0.5 | 0.4 / −0.4 / −0.1 | 0.3 / −0.6 / 0.4 |
| excess + leak, paired | +0.3bp | +0.2bp | 0.4 | 0.3 | −0.7 |
| book delta, both channels | +0.00165 | +0.00289 | −2.2 | −2.4 | −2.4 |
| book delta, the price's alone | −0.00207 | −0.00229 | 0.4 | 0.1 | 0.1 |
| up-beta / down-beta | +0.0097 / −0.0073 | +0.0091 / −0.0067 | 0.4 / −6.6 | −0.2 / −6.1 | 0.3 / −0.8 |
| left at first expiry | +0.0197 | +0.0224 | −6.3 | −4.5 | −1.1 |
| gap: median | −0.00141 | −0.00139 | −1.6 | −0.9 | 0.1 |
| gap: mean/median | +0.281 | +0.272 | +7.5 | +5.8 | +1.3 |
| gaps beyond 5% / 10% | +0.0372 / +0.0067 | +0.0361 / +0.0064 | +6.9 / +4.8 | +5.6 / +5.5 | +1.6 / +1.5 |
| assignment rate | exactly p\* | −0.0002 | 1.2 | 0.6 | 5.4 |

- **The factors alone needed a grid of their own.** With no kick their volatility moves only
  through θ, a stationary sd of 0.045 in h_fast and 0.073 in h_slow around zero, under the
  jumps' spacing and partly below its floor: the first build read the gap's median 6% high
  and inventory moving the wrong way. On a grid with the same spacing per sd (0.025, ±4.5
  sd; `lattice.grid`) everything agrees but the assignment rate, which is the simulator's:
  its tables' strike sits 0.0008 off the dial, where the lattice's is the quantile itself.
  The cache key now names the grid actually built.
- **With jumps, three things miss**, each a few percent of the effect it measures: the gap's
  tail (3% heavy), the first expiry (12% short), the down-beta (9% more negative). The
  volatility channel of the delta is 30% short at 2.2–2.4 errors in all three processes.
- **The gap's tail is the sale state's snapping to nodes** (tested): puts sold from 600,000
  exact stationary states, strikes interpolated from the lattice's nodes, give mean/median
  1.5143, 5.24% beyond 5% and 0.620% beyond 10%, against the simulator's 1.5139, 5.28% and
  0.630% (jumps), where the lattice reads 1.5206, 5.37% and 0.655%. The first expiry's miss
  is the same snapping at entry (test 2: −0.002 at this grid).
- An entry split between the two neighbouring cell centres, to keep each lot's mean depth,
  was tried and reverted: it read the first expiry further off at constant σ (0.4027
  against 0.4039 binned; the continuum is about 0.4067), since below the first centre no
  split is possible.

**Decision 10 built, 2026-11-22** (`lattice._exact_chunk`, phase C, cached apart from the
tables so that a change to the entry rebuilds only it, about three minutes). Eight million
sales from two million independent stationary paths, four reads each; the put's week and the
first call period stepped from each sale's state, both measures on the same draws; each
kind of sale's interpolated strikes moved by the one shift that assigns exactly p\* of its
sales — the nodes' strikes are quantiles of draws every node shares, so their errors were
common, and interpolated they assigned 0.2004. At constant σ the still lattice now reads the
first expiry 0.40666, the continuum's 0.4067 (the constant model on the near grid reads
0.4046, II-32), and inventory at 30 years 11.35; both exact tests hold to 1e-13bp. Against
the simulator, pooled over seeds 1 and 2, z as before:

| | fitted | jumps | factors |
|---|---|---|---|
| left at first expiry | −1.3 | −0.9 | −0.3 |
| assignment rate (the lattice's exactly p\*) | +1.2 | +0.6 | +5.4, the simulator's |
| E[I] at 5 / 10 / 30 years | +0.5 / −2.1 / −0.1 | +0.1 / −0.8 / −0.5 | +0.3 / −0.6 / +0.4 |
| excess + leak, paired | 0.0 | 0.0 | −0.7 |
| book delta, both channels / the price's alone | −2.9 / −0.3 | −2.8 / −0.5 | −2.4 / +0.1 |
| up-beta / down-beta | +0.5 / −3.3 | +0.3 / −3.1 | +0.4 / −0.2 |
| gap: mean / median / mean/median | −1.2 / −2.4 / +2.0 | −1.9 / −1.2 / −0.9 | +0.7 / 0.0 / +0.7 |
| gaps beyond 5% / 10% | −0.8 / −1.9 | −1.9 / −3.2 | +0.3 / −1.3 |

What remains past two errors, each small against what it measures:
- **The book's delta through the volatility's channel** (0.0037 against the simulator's
  0.0052 in the fitted process) — **the simulator's estimate, not the lattice's.** The
  lattice's real-world test by channel holds to 0.001bp at 5, 10 and 30 years. The
  simulator's paired test leaves −0.38bp at constant σ (its weekly sampling), −0.71bp with
  both channels and +0.33bp with the price's alone: its own excess implies a channel of
  about 0.0036 ± 0.0008, the lattice's, while its direct estimate from the tables'
  gradients sits about two errors above that.
- **The down-beta**, −0.0070 against −0.0067 (5% of the effect; both 0.993 at three
  figures), with jumps only: periods after the first ride the grid, whose spread is a little
  wide (decision 2).
- **Gaps beyond 10% under jumps alone**, 0.617% against 0.630%, three errors.

**Both regimes, both models' errors** (2026-11-22). The exact entry is itself a simulation
— 1.6 million lots at p\* = 20%, 0.8 million at 10% — so its own sampling error belongs in
the comparison beside the simulator's (it had been left out above). The z of every figure,
pooled over seeds 1 and 2:

| | fit/Std | jmp/Std | fac/Std | fit/Con | jmp/Con | fac/Con |
|---|---|---|---|---|---|---|
| left at first expiry | −0.8 | −0.6 | −0.2 | −1.0 | −0.3 | −0.2 |
| assignment rate | +1.2 | +0.6 | +5.4 | −0.4 | +0.5 | +6.4 |
| E[I] 5 / 10 / 30 years | +0.5 / −2.1 / −0.1 | +0.1 / −0.8 / −0.5 | +0.3 / −0.6 / +0.4 | +0.6 / −2.1 / −0.4 | 0.0 / −0.7 / −0.6 | +0.4 / −0.4 / +0.7 |
| excess + leak, paired | 0.0 | 0.0 | −0.7 | +0.1 | +0.1 | −0.4 |
| book delta, both / price | −2.9 / −0.3 | −2.8 / −0.5 | −2.4 / +0.1 | −2.6 / −0.4 | −2.6 / −0.5 | −1.9 / +0.3 |
| up-beta / down-beta | +0.5 / −3.3 | +0.3 / −3.1 | +0.4 / −0.2 | +0.8 / −1.4 | +0.8 / −1.8 | +0.6 / −1.6 |
| gap mean / median / ratio | −0.8 / −1.4 / +0.8 | −1.3 / −0.7 / −0.4 | +0.4 / 0.0 / +0.3 | −0.6 / +0.4 / −0.7 | −2.0 / −0.3 / −1.1 | +0.7 / +0.9 / −0.4 |
| gaps beyond 5% / 10% | −0.5 / −1.2 | −1.2 / −1.9 | +0.2 / −0.8 | −0.4 / −1.2 | −2.3 / −2.1 | +0.1 / −0.5 |

**§10's boundaries in `model.py`** (`vol_boundaries`, from `lattice.long_run`: the tilted
transition on h_slow 0.05, 200,000 paths a node, the earnings calendar as the cycle of
thirteen periods' product). Common draws across nodes left c2 moving 0.03 between seeds —
their errors common, not averaging — so each node draws its own; then two seeds agree to
0.0001:

| | c1 | c2 | long-run variance of log S |
|---|---|---|---|
| jumps, eigenvalue | 2.004% | 4.380% | 0.0431 |
| jumps, simulated (`boundaries`, Jensen's term in) | 1.995 ± 0.006% | 4.363% (4.367% by log-mean-exp) | |
| fitted, eigenvalue | 2.003% | 4.320% | 0.0427 |
| fitted, simulated | 1.995 ± 0.005% | 4.307% (4.309%) | |

Within about one and a half of the simulation's errors. The running example's μ − δ = 4.5%
sits 0.18 points inside the capital boundary under the fitted process.

**Step 5's checks, in `verify_examples.py`** ("the moving volatility's lattice", reading the
cache and reporting a missing lattice as skipped): the still lattice against the continuum
(h = 0.0025) on the first expiry and inventory at 30 years; the pricing-drift test on the
still and the fitted lattices at μ = r, to 1e-9; under the fitted process the real-world
test exactly (1e-9) and by channel (decision 8's 0.5bp), and the dial at p\*. All pass. The
README and CLAUDE.md describe the lattice, its caches and their costs.

**Stationary, decision 6** (4,000 periods on the coarse and fine grids, Richardson; about 70
minutes for the fitted process):

| | still lattice | constant model | fitted |
|---|---|---|---|
| E[T], years (Standard) | 2.0996 | 2.0985 | 2.1100 |
| E[I(∞)], lots (Standard) | 21.84 | 21.83 | 21.94 |
| 90% of E[I(∞)] reached in, years (Standard) | 90.2 | 90 (the article) | **103.4** |
| E[T], years (Conservative) | 2.0194 | | **2.1441** |
| E[I(∞)], lots (Conservative) | 10.50 | | **11.15** |
| 90% reached in, years (Conservative) | 90.0 | | **103.9** |

The still lattice is the constant model. Under the fitted process the stationary means barely
move (+0.5%) while inventory at 30 years falls 4%: lots leave sooner at first, but the deep
ones linger — the long-run variance of log S is 7.5% above σ² — so equilibrium is approached
more slowly, and §08's "90 years" becomes about 103. A side-by-side figure for §08. In the
Conservative regime the stationary means rise 6% (E[T] 2.14 against 2.02 years) where its
30-year inventory barely moves: a 10% dial is assigned mostly by large falls — its gaps beyond
5% are six times the constant model's — so its lots start deeper and linger longer.

**A volatility spread on the moving path** (2026-11-23, `model._vol_spread`): every option
sold at its fair implied volatility plus the spread, as the simulator sells it, kept as
increments BS(iv + spread) − BS(iv) on the fair prices — the cells' from their premiums'
implied volatilities (`lattice.spread_tables`, cached; no simulation), the first call
period's over the exact entry's lots by node, kind and depth, the put's over the nodes. A
volatility point at 30 years:

| | Standard | Conservative |
|---|---|---|
| constant model / still lattice | 45.14 / 45.26bp | 50.46 / 50.65bp |
| simulator, constant (seeds 1, 2) | 45.37, 45.61bp | 50.70, 51.12bp |
| fitted lattice | **47.03bp** | **52.75bp** |
| simulator, full process (seeds 1, 2) | 47.04, 47.20bp | 52.72, 52.81bp |
| jumps lattice / simulator | 47.23 / 47.62, 46.85bp | 52.86 / 53.25, 52.37bp |
| factors lattice / simulator | 44.55 / 45.45, 44.28bp | 49.91 / 50.92, 49.74bp |

The volatility's moving alone lowers a point's worth a little; the jumps are what raise it.

Step 7's +48.1bp was on the old σ̄; on the measured one a volatility point is worth about 4%
more under the fitted process than at constant σ, not 6%.

**Part II side by side** (2026-11-23, material for the section revisions; scratch
`side_by_side.py`). The constant-σ model as the article computes it (the near grid), the
same with the volatility held still on the lattice (the continuum's figures, the first
period from the exact entry), and the fitted process:

| figure | Std constant | Std still | Std fitted | Con constant | Con still | Con fitted |
|---|---|---|---|---|---|---|
| §05 E[x0], entry depth | 1.548% | 1.548% | 1.675% | 1.313% | 1.313% | 1.615% |
| §05 E[d], drop from the sale | 3.754% | 3.754% | 3.502% | 4.699% | 4.699% | 4.579% |
| §05 put premium, of spot | 0.306% | 0.306% | 0.329% | 0.129% | 0.129% | 0.156% |
| §05 gap: mean / median | | 1.26 | 1.535 | | 1.295 | 1.606 |
| §05 gaps beyond 5% / 10% | | 1.78% / 0.001% | 5.38% / 0.63% | | 0.87% / 0% | 5.35% / 0.65% |
| §07 left at first expiry | 0.4046 | 0.4067 | 0.4285 | 0.4192 | 0.4220 | 0.4356 |
| §07 median holding, call periods | 2 | 2 | 2 | 2 | 2 | 2 |
| §07 mean holding E[T], years | 2.099 | 2.100 | 2.110 | 2.018 | 2.019 | 2.144 |
| §07 still held after 3 / 12 / 24 months | 0.381 / 0.179 / 0.119 | 0.380 / 0.178 / 0.119 | 0.359 / 0.166 / 0.112 | 0.369 / 0.172 / 0.115 | 0.367 / 0.171 / 0.114 | 0.356 / 0.167 / 0.113 |
| §08 E[I] over 5 / 10 / 30 years | 5.41 / 7.39 / 11.40 | 5.39 / 7.36 / 11.35 | 5.12 / 7.00 / 10.87 | 2.63 / 3.58 / 5.50 | 2.61 / 3.56 / 5.47 | 2.57 / 3.52 / 5.49 |
| §08 E[I(∞)] / years to 90% of it | 21.82 / 90.4 | 21.84 / 90.2 | 21.94 / 103.4 | 10.49 / 90.2 | 10.50 / 90.0 | 11.15 / 103.9 |
| §09 true excess over 5 / 10 / 30 years, bp | 138.2 / 143.5 / 149.3 | 138.1 / 143.4 / 149.3 | 138.3 / 143.6 / 149.5 | 132.6 / 139.1 / 146.3 | 132.5 / 139.0 / 146.2 | 133.5 / 140.0 / 147.1 |
| §09 book delta over its life, 30y | 0.931 | 0.931 | 0.932 | 0.913 | 0.912 | 0.917 |
| §09 up-beta / down-beta, 30y | 0.828 / 1 | 0.828 / 1 | 0.838 / 0.993 | 0.824 / 1 | 0.823 / 1 | 0.832 / 0.991 |
| §09 a volatility point, bp | 45.1 | 45.3 | 47.0 | 50.5 | 50.7 | 52.8 |
| §10 lots' / capital boundary | 2.00% / 4.00% | 2.00% / 4.00% | 2.00% / 4.32% | | | |
| §10 long-run variance of log S | 0.0400 | 0.0400 | 0.0427 | | | |

Two cautions for whoever writes from it:
- **The constant column carries TODO II-32.** The article's model starts its walk from the
  entry density at each near-grid cell's centre, which reads the first expiry 0.2 points low
  and inventory 0.3–0.6% high against the continuum; the lattice's first period runs from
  the exact entry and carries no grid. So the fair side by side is still against fitted, and
  II-32 is best settled before the sections quote both: either the constant model moves to
  h = 0.0025 (II-32's own proposal) or Part II quotes the still lattice's continuum figures.
- **Track A's capital under the moving volatility averages one small ratio** (Track A is not
  in the table): each lot's basis is e^x(1 − c_p/k), and the lattice takes c_p/k averaged
  over the sales where each lot's is its own sale's. The ratio is a few tenths of a percent
  and varies little across states, so this costs well under 0.1% of the capital; Track A's
  larger fall at 30 years (−101 against −69bp, Standard) is the fitted process's, its deeper
  lots held at cost. The true excess carries no such average.

**Decision 2's fallback, measured** (h_slow at 0.05, 799 nodes, the fitted process, Standard):
against 0.1, inventory at 5, 10 and 30 years moves by +0.0001, +0.0001 and −0.005 lots, the
first expiry by −0.0002, the excess by −0.005bp, the book's delta by −0.00003, the up-beta
by −0.0005, the down-beta by less than 0.00001, the gaps not at all. With σ̄ shared
(decision 9) and the entry exact (decision 10), h_slow's spread at 0.1 costs nothing the
article quotes; the down-beta's residual is not its doing. **h_fast at 0.05** (792 nodes)
likewise: inventory −0.001 to −0.004 lots, the first expiry +0.0002, the excess −0.003bp,
the up-beta +0.0003, the down-beta less than 0.00001. Neither factor's grid explains the
down-beta's 0.0003 against the simulator (−0.0070 against −0.0067), and the two estimators
are the same — each call period observed within the window, the lot's move against its
price at the call's sale, the premium in, a slope with an intercept a side — with the
window's weights differing only by half a period, (H − (j + ½)τ_c) against (H − (j + 1)τ_c).
Left open: 5% of an effect both models put at 0.993 to three figures.

Decision 8's test passes but for two of the simulator's own figures — the volatility channel
of its delta, every process, and its tables' strike under the factors alone — and the
down-beta in the Standard regime (5% of the effect); four other figures sit between 2.0 and
2.3, about what chance puts among ninety-six. (All three traced the next day, below.)

**The three divergences, traced** (2026-11-23; Sergei: "Whether each is real or a modelling
artifact, it is better to know explicitly rather than dismiss as insignificant"). Each is the
simulator's, and each is reproduced inside the lattice by doing what the simulator does
(scratch `div_edges.py`, `div_tests23.py`, `div_test1*.py`, `lattice_seed.py`, `sim_ell.py`,
`sim_order.py`). None touches `model.py` or a figure it gives.

*First, an error never counted: the lattice's own.* Its tables come from one set of draws
shared by every node, and every z above counted the simulator's errors and the exact entry's,
not the tables'. Rebuilt on two more seeds (fitted, Standard), the sd across the three:

| figure | lattice's sd across seeds | the simulator's error |
|---|---|---|
| down-beta | 0.00009 | 0.00008 |
| up-beta | 0.00015 | 0.0017 |
| E[I] at 5 / 10 / 30 years | 0.003 / 0.003 / 0.002 lots | 0.03 / 0.03 / 0.06 |
| left at first expiry | 0.00015 | 0.0009 |
| gaps beyond 5% / 10% | 0.0001 / 0.00004 | 0.0003 / 0.0001 |
| book delta, both channels | 0.00001 | 0.0008 |
| excess + leak | 0.003bp | 0.3bp |
| a volatility point | 0.016bp | 0.2bp |

Small beside the simulator's everywhere but the down-beta, where it is as large and doubles the
comparison's variance.

**1. The assignment rate under the factors alone: the simulator's tables stop short of the
state.** `fairprice`'s grid starts h_slow at −0.1 (`HS_GRID`); with no kick the factors'
h_slow sits around zero with sd 0.073, and 8.6% of stationary states lie below the floor, 0.034
below it on average, where the tables read the strike off the edge: at a higher volatility than
the state's, so deeper. From four million stationary states at the tables' own strikes, on
their grid 0.20004 ± 0.00021 are assigned, below it 0.1913 ± 0.0007, over all 0.1993 ± 0.0002
— the simulator's shortfall, 0.0008 ± 0.0001, within its error. With jumps the kicks keep
h_slow far above the floor (no state below it); the lattice's grid for the factors spans ±0.35.

**2. The down-beta: the same tables' ceiling, and the lattice's own error.** The tables stop at
h_fast 1.0 and h_slow 1.9. Beyond them lie 0.11% of stationary states but 2.4% of the variance:
the turbulent states, whose falls are the largest. There the simulator's call premiums, read
at the edge, are 25% below fair (on the grid, 0.1–0.3% below the lattice's). The down-beta's
distance from 1 *is* that pairing — below the strike a lot is the share, so the slope less 1 is
Cov(c, u | down)/Var(u | down), the premium larger where the falls are — and a premium clamped
low in exactly those states reads it short. The lattice's down-beta at 30 years with every call
premium replaced by the simulator's, the first period's too:

| | lattice | with the simulator's premiums | simulator, seeds 1–2 pooled | z before / after |
|---|---|---|---|---|
| fitted, Standard | 0.99295 (three seeds) | 0.99307 | 0.99328 ± 0.00008 | −3.7 / −2.3 |
| fitted, Conservative | 0.99119 | 0.99135 | 0.99126 ± 0.00010 | −0.6 / +0.6 |
| jumps, Standard | 0.99305 | 0.99320 | 0.99332 ± 0.00009 | −2.1 / −0.9 |
| jumps, Conservative | 0.99098 | 0.99116 | 0.99111 ± 0.00011 | −1.0 / +0.4 |

z with both models' errors (the lattice's, 0.00009 a seed, as measured above); the
simulator's constant-σ run reads 1 within its noise (0.99993, 0.99997), as it must, so the
fitted figures are compared directly. The clamp accounts for 0.00012–0.00019 of each gap; what
is left is within both models' errors, the largest 2.3 of them (fitted, Standard), and averages
−0.00005 over the four: nothing systematic is left.

**3. The delta's volatility channel: the simulator's estimator, and its event order.**
`wheel_sim.py` reads the book at each put sale, a week apart, each call's delta through the
volatility (`eff_delta`: the vega times the tables' gradient in each factor times θ, per unit
of the price's move) at 20, 15, 10 and 5 sessions to expiry and each put's at its sale. Against
the life delta that the exact test needs, it departs four ways, each reproduced on the lattice's
own draws by an adjoint pass that splits the pathwise derivative by the session whose shock it
comes from (exact against `lattice.paths` to 3e-17), aggregated over the lattice's census:

- **a left-endpoint rule.** The price's channel has a flat profile over an option's life by the
  session of its shock (every session's shock moves the price at expiry alike), so in this split
  the rule costs it nothing — though the samples the simulator takes, E[Δ_t S_t], are flat only
  under the pricing measure, which costs it 0.0006 at constant σ (*4.*, below); the volatility's falls to
  zero at expiry with the vega — a call's from its four weeks' shocks 0.40, 0.32, 0.21 and
  0.07, at every depth — so the rule reads 1.17 of it, and a put's, all from one week, about 1.9;
- **timing**: it reads ∂V/∂h at the state before the session whose shock moves h, so the
  sensitivity includes that session's own variance, which its shock cannot change — material
  for the fast factor, half-life six sessions;
- **shares**: it averages deltas in shares at the sampling date, where the life delta is in
  dollars per unit of the price at the option's sale (small, −0.00004);
- **the measure**: it reads the pricing-measure price's delta along real-world paths, where the
  exact average is the trapezoid of the two measures (reweighted to the real world up to each
  sample by Girsanov: 0.00001).

| the book's vol channel per capital, 30y | fitted Std | fitted Con | jumps Std | jumps Con | factors Std | factors Con |
|---|---|---|---|---|---|---|
| exact (the lattice's, as `model.py`) | 0.00375 | 0.00378 | 0.00386 | 0.00388 | 0.00365 | 0.00379 |
| the weekly left-endpoint rule | 0.00488 | 0.00505 | 0.00503 | 0.00517 | 0.00473 | 0.00502 |
| ...with its timing | 0.00533 | 0.00553 | 0.00549 | 0.00567 | 0.00520 | 0.00554 |
| ...in shares, at its measure: the simulator's estimator | 0.00530\* | 0.00549\* | 0.00545 | 0.00563 | 0.00515 | 0.00550 |
| the simulator, seeds 1, 2 | 0.00517, 0.00519 | 0.00537, 0.00539 | 0.00537, 0.00528 | 0.00555, 0.00546 | 0.00515, 0.00502 | 0.00551, 0.00538 |

\* Without the measure's 0.00001, which needs an adjoint pass per earnings day more.

The tables' gradients are not at fault: at the same states they read the instantaneous vol
channel within 0.3% of the pathwise derivative, for calls at the census's depths and the put
at its strike. That left 0.0001, consistently, the replica above the simulator in all six
(2% of its figure). Split by the sample's tenor (jumps, Standard, five simulator seeds), all of
it sat in the samples at 20 sessions, the call's sale: 0.00128 ± 0.00001 against the replica's
0.00139, where 15, 10, 5 and the put agree within 1%. **The cause is the simulator's event
order.** A renewed call falls due at t + τ_c, one addition; the put sale four weeks on at four
additions of the cadence. The two floats differ by about 6e-15 years, and on 9% of expiries the
sale sorted first — 1.94 million samples with the expiring call still standing, 0 sessions
left, and the renewed call's first sample lost — though the code's comment at the sale reads
"after same-date settlements". With every event time rounded when it is pushed, so that equal
dates are equal floats, the simulator's vol channel reads 0.00545 (jumps, Standard, seed 1),
the replica's 0.00545. All of the 0.0015 is accounted for (jumps, Standard): 80% the
left-endpoint rule, 32% the timing, −7% the event order, −3% the shares and the measure.

The event order touches more than this figure. At every sale it samples, the book still holds the
lots about to be called away (the sampled inventory reads 0.024 lots, 0.2%, above the
time-average; fixed, they agree to 0.003), so the sampled capitals and the book's delta are a
little off — the delta 0.0006–0.0008 low in either process, which moves the simulator's paired
test by −0.15bp. At constant σ that test's residual then reads −0.56bp at seed 1 (−0.44bp
before), traced in *4.* below. The run's draws are not otherwise disturbed, with one exception
found on the way: the times' drift reaches 1e-12 years by the thirtieth year, crossing
`advance`'s threshold for a step and inserting a spurious draw now and then (11 paths in 400),
which reshuffles the rest of a batch's stream: noise, not bias. In a finite account the order
also checks a put's capacity before the strike of a lot being called away has arrived, so a put
the account could carry is now and then refused: at most on about 1% of weeks (a call-away in a
given week, 0.12, times the 9%), and only when the account is at its capacity. Section 11's
simulated figures (`--scenario constrained --paths 4000`), the original against the order fixed,
on four seeds each (unpaired: fixing the order also removes the spurious draws, so the streams
differ): the prudent account's throughput +0.35 ± 0.1 points (61.8% against 61.7% at the
article's seed), its liquidation from an empty book 0.0 ± 0.1 points by thirty years and
−0.5 ± 0.4 by sixty, after saturation −0.2 ± 0.2, T_sat +0.2 ± 0.3 years, the levered
account's and the cash policies' within their noise. All within the runs' own spread between
seeds, which is itself wider than §11's quoted precision: the sixty-year figure moves about half
a point from one seed to the next where §11 quotes it to two decimals. Found on the way, and not
this bug's:
at the article's own command and seed the current simulator gives 0.85% and 11.80% from empty by
thirty and sixty years, 3.78% after saturation and 31.7% throughput where §11 quotes 0.92%,
12.15%, 3.95% and 31.8%. §11's simulated figures date from 2026-07-29, and the simulator's
account has changed since (TODO II-35, 2026-11-13), so they are due a rerun with that section's
revision, quoted to the precision the seeds allow.

**4. The constant-σ paired residual: the simulator reads its delta in shares** (traced
2026-11-23). The paired test sets the simulator's excess against the delta it samples, and that
delta is not the one its ledger earns on. The ledger books each option's flows per unit of the
price the option was sold at (II-34), so the exposure the excess is earned on is a call's dollar
delta per unit of that price, Δ_t·S_t/S_sale, averaged over its life (`model.life_delta`); the
simulator reads Δ_t in shares — per unit of the price ruling — at each weekly sale. The calls'
delta per lot over a call's life, census-weighted at the running example (Standard, 30 years),
in dollars carried to expiry, e^(r(τ−t))·E[Δ_t S_t]/S_sale, and in shares, E[Δ_t]:

| | at sale | 1 week | 2 weeks | 3 weeks | life average |
|---|---|---|---|---|---|
| real world, dollars | 0.06906 | 0.06961 | 0.07018 | 0.07074 | 0.07018 |
| real world, shares | 0.06879 | 0.06830 | 0.06780 | 0.06731 | — |
| pricing measure, dollars | 0.06906 | 0.06906 | 0.06906 | 0.06906 | 0.06906 |
| pricing measure, shares | 0.06879 | 0.06777 | 0.06676 | 0.06575 | — |

In dollars the discounted delta is a martingale under the pricing measure, flat across the life,
and rises 3.3% over it in the real world, by the gamma term (μ − r)·S²Γ: the weekly samples at
the start of each week read it 0.00056 a lot short of the life average. In shares it *falls*
instead, because Δ_t and S_t/S_sale move together — a covariance of order σ²t, which does not
vanish under the pricing measure — 0.00157 a lot further. A short call's delta read low is the
book's read high: through the census, +0.00059 for the rule and +0.00165 for the units, together
+0.00224 (Conservative +0.00230), a paired residual of −0.45bp (−0.46bp). In the simulator itself
— a scratch copy with the event order fixed, each call's delta also read times S/S_sale, the same
runs, eight seeds:

| | observed | predicted |
|---|---|---|
| paired residual, delta in shares (the simulator's) | −0.467 ± 0.053bp | −0.448bp |
| paired residual, delta in dollars per unit of the sale price | −0.135 ± 0.053bp | −0.117bp, the weekly rule |
| shares less dollars, in the delta | 0.00166 (sd 0.00001) | 0.00165 |

**All of it is accounted for**: −0.02 ± 0.05bp left. (The excess alone implies a delta 0.00055 ±
0.00030 below `model.py`'s life delta, 1.8 errors: the simulator's census against the model's.)
The magnitudes comparisons are each model less its own constant-σ reference, so the price
channel's bias cancels from them as far as it is the same at fitted and constant σ — and there the
price channel's own comparison agreed, within half an error in all six — while the lattice's
price channel is exact by the real-world test. Only the simulator's absolute paired test carries
it.

**5. §11's simulated figures, recounted** (2026-11-23, II-35's step 7 for §11). §11's command
(`wheel_sim.py --scenario constrained --paths 4000`, seed 20260722) run at each simulator commit
since its figures were taken: `4e7ec57` (2026-07-29) reproduces every figure §11 quotes, to the
last digit; II-34's simulator commit (`4e73b59`) moves none; II-34's model commit (`bb629e2`) and
II-35's first (`96521d1`) move every run under the stationary draw, and only those — through
the draw, r + excess − m from `model.py`'s stationary excess, now 2.05% of equity where §11
quotes 2.12%, a figure no check covers. A draw a few basis points different reshuffles the
account's blocking on the same price paths, so every figure of those runs moves by its noise:
across those commits the operating book's liquidation after saturation read 3.95%, 3.19%,
3.78%. II-35's second (`fce81fb`, premiums withdrawn at expiry rather than at sale) moves the
service and income policies — on four seeds, before against after, +0.28 points liquidated
under service (−0.12 to +0.68) and +0.35 under income, both within about 1.6 errors — and
nothing after it moves any. So §11's figures are stale by II-34 and II-35, and the bug of
*3.* is in all of them alike.

The current simulator on six seeds (the article's, 1–5), the prudent account unless named:

| | the article's seed | mean of six | sd across them |
|---|---|---|---|
| thinning: inventory, constrained against thinned | +1.9% | +1.9% | 0.9 |
| thinning: income | +0.9% | +0.8% | 0.4 |
| puts sold | 0.705 | 0.706 | 0.003 |
| T_sat, simulated (analytic 18.5) | 18.9y | 18.4y | 0.4 |
| realized leverage | 0.743 | 0.741 | 0.003 |
| liquidated from empty by 30 / 60 years | 0.85% / 11.8% | 0.90% / 11.4% | 0.18 / 0.4 |
| after saturation, 30y: frozen (closed form 0.98%) | 1.25% | 1.08% | 0.18 |
| ...operating | 3.78% | 3.64% | 0.24 |
| ...operating over frozen | 3.0 | 3.4 (pooled) | 2.6 to 4.3 |
| ...frozen less closed, in its errors | +1.4 | +0.5 | −0.3 to +1.9 |
| the testbed's worst frozen less closed, in errors | 0.4 | — | 0.1 to 1.9 |
| census after saturation: deepest bin, points | +3.9 | +4.2 | 0.4 |
| ...mean depth | +6.1% | +7.4% | 1.0 |
| ...the whole run's mean depth | −0.9% | +0.4% | 1.0 |
| cash: retain / service / stationary / income, liquidated | 0.35 / 1.79 / 3.78 / 8.60% | 0.43 / 1.44 / 3.64 / 8.92% | 0.17 / 0.27 / 0.24 / 0.46 |
| ...the same paths' frozen barrier | 0.92 / 1.34 / 1.25 / 0.81% | 1.00 / 0.96 / 1.08 / 0.88% | 0.1–0.2 |
| ...income over retain / over service | 24.6 / 4.8 | 20.7 / 6.2 (pooled) | 12.6–30.4 / 4.8–8.9 |
| ...income: realized g | +1.44% | +1.38% | 0.03 |
| ...service: throughput, equity's drift in shares | 31.7%, −2.2%/y | 31.8%, −2.2%/y | 0.4, 0.0 |

**One of §11's statistics is not measured by its estimator.** The drift of ln(M/D) — the
ratchet's "−1.55% ± 0.10 per year" — read −1.70, +0.52, +0.13, −1.54, −1.83 and −1.75% on the six
seeds, each quoting an error near 0.1. The scenario averages each surviving path's rate,
log(R_sat/R_end)/(T − t_sat), unweighted; a path that first saturates in the run's last months
carries a rate of ±3 to ±17 a year on a span of 0.02–0.3 years, and two or three of them carry
the mean (a scratch copy keeping each path's log ratio and span, four seeds). The median, −1.42
to −1.56%, and the span-weighted rate, Σ log ratio / Σ span, −1.40 to −1.48%, are steady: the
book drifts toward its barrier at about 1.4% a year, and §11's conclusion stands on a sound
estimate of it. The realized g under the stationary and retain policies shares the estimator
and its instability (0.011 to 0.037 on four seeds); under the income policy, the only g §11
quotes, it is steady.

What this does to §11's prose, for the paragraph review: the ratchet's factor of 3.6 is about
three (3.0 at the article's seed, 3.4 pooled), in its table and in the closing warning;
uniform thinning holds to about 2% on inventory and holding time, not under 1%, and its error
is positive on all six seeds — the composition effect of *The census the constraint leaves
behind*, seen in the counts; withdrawing the income is about six times worse than servicing it,
not eight; the cash policy moves survival by a factor of about twenty, not twenty-five (§10's
restatement too); the blocked book 6–7% deeper, not 5.3%; the realized leverage 0.74 (§09 and §11
quote 0.745); the stationary draw 2.05%; the frozen barrier's agreement with the closed form
1.4 errors at the article's seed, 0.5 pooled; the rest within a digit of what §11 quotes.
Whether the scenario's drift estimator becomes the span-weighted one, so that the command
prints the figure §11 quotes, is Sergei's call.

What follows, for Sergei's call — none of it changes a figure `model.py` gives:
- **the simulator's tables' grid**, widened to the lattice's (h_fast to 1.4; h_slow from −0.5
  for the factors alone, to 2.3), twelve table sets, about an hour, and the magnitudes reruns;
- **its event times tied** — *done 2026-11-23, below*;
- **`eff_delta`'s direct estimate of the volatility channel** is biased by design, about 40%
  high, and is not a check of the lattice's: its excess-implied delta (the paired test) is.
  Either read each option at every session from tables at every tenor, or report the direct
  estimate as what it is;
- **the simulator's sampled delta in the ledger's units** — *done 2026-11-23, below*;
- **decision 8's comparisons** count the lattice's own error from now on, which only the
  down-beta's needs;
- **§11's prose**, on the recount below; and the scenario's drift estimator, span-weighted —
  *done 2026-11-23, below*.

**Three of them done, 2026-11-23** (Sergei: "Please do 1 and 2 now. Then the draft of the
prose" — 1 the simulator's own fixes, 2 the recount at four times the paths):
- **The event clock** (`wheel_sim._event_clock`): every event date is put on the grid of the
  run's own rhythm, k/N with N the smallest number making the cadence and the put's tenor
  whole multiples of 1/N (52 at the running example, 12 at a monthly rhythm; left as summed
  when either is not a ratio of small whole numbers). One date is then one float, and same-date
  events go by priority. A lighter fix was tried first — the heap ordered by the date rounded
  to 1e-9 years, each event keeping its own float — and does not preserve the draws either:
  wherever the old order had inserted a draw over a vanishing interval, the reordered pair steps
  back over a negative one and skips it. So the random stream moves on the 1–3% of paths that
  carried such a draw whatever the fix, and the clock, which also takes the drift away, is the
  one kept. Every scenario moves by its noise. Re-pinned in `verify_examples.py`: eight of
  `--scenario stochvol`'s figures at their printed digits, each inside its standard error, the
  largest E[I] with the leverage effect, 9.909 to 9.939 lots; none at the precision §09 quotes.
  **§10's crash-and-flatline table moves beyond noise** at years 2 to 7 (lots held at year 2,
  5.12 to 4.98; years 1, 8 and 10 unchanged; the paper loss unchanged at every row): at those
  dates the old float order put every call expiry after the sale, so the sample counted the
  day's call-aways as held. HEAD reproduces §10's printed table exactly; the new one is in the
  draft, with the three figures its prose reads off it (5.1 to 5.0, 5.3 to 5.2, 6.0 to 5.9).
- **The delta in the ledger's units**: each call's sampled delta times S/S_sale, in both
  branches, as *4.* measured.
- **The drifts span-weighted** (`wheel_sim._span_rate`): the realized g, the drift of ln(M/D)
  and the equity's in shares, each total log change over total years, with the ratio
  estimator's error.

**§11 recounted at 16,000 paths** on the fixed simulator, the article's seed and seed 1:

| | the article's seed | seed 1 |
|---|---|---|
| thinning: inventory / income / E[W] | +1.1 / +0.5 / +1.1% | +1.2 / +0.5 / +1.2% |
| puts sold; T_sat simulated (analytic 18.5) | 0.707; 18.2y | 0.706; 18.4y |
| realized leverage | 0.743 | 0.742 |
| drift of ln(M/D), span-weighted | −1.47 ± 0.04% | −1.51 ± 0.03% |
| liquidated from empty by 30 / 60 years | 0.97 / 11.0% | 0.89 / 11.0% |
| after saturation, 30y: closed / frozen / operating | 0.99 / 0.89 ± 0.08 / 3.62 ± 0.16% | 0.99 / 1.06 / 3.70% |
| ...operating over frozen; over closed | 4.1; 3.7 | 3.5; 3.7 |
| testbed's worst frozen less closed | 0.3 errors | 0.7 |
| census after saturation: deepest bin; mean depth | +4.1 points; +6.6% | +4.0; +6.8% |
| cash: retain / service / stationary / income | 0.26 / 1.36 / 3.62 / 8.99% | 0.32 / 1.27 / 3.70 / 8.73% |
| ...the same paths' frozen barrier | 1.09 / 0.84 / 0.89 / 0.88% | 0.85 / 0.86 / 1.06 / 0.88% |
| ...income over retain; over service | 35; 6.6 | 27; 6.9 |
| ...income: realized g; service: throughput | +1.46%; 31.7% | +1.41%; 31.8% |

The draft quotes the article's seed, the ratios as the two seeds allow them: the ratchet "a
factor of four" (3.7 against the closed form itself, on both), the cash policy "about thirty",
income against service "nearly seven". Thinning now holds to about 1% on the fixed simulator,
where the old one read +1.9 ± 0.4% on six seeds of 4,000 paths: 1.5 errors apart, so the old
order's refusals may account for part of it, not shown to. Two of §11's
sentences read against these figures for the review, not changed in the draft: the retained
account's "g goes strongly negative", where the realized g of the paths still owing is +4.2%
(the ones that repay drop out of it); and the withdraw-everything account's boundary "crossed
nonetheless" at a realized g of 1.5% against ν = 2.5%, which by ν > g alone it is not — it is
the account shrinking (equity −2.7% a year in shares) that keeps M from growing with the
price, which the criterion as stated leaves out.

Committed 2026-11-23 as drafted (Sergei: "The draft changes are fine, please commit them"),
with five restatements of the old figures the draft had missed, found by grepping each
replaced figure: §09's stationary draw (2.12 to 2.05%), §10's realized g under withdrawal
(+1.3 to about +1.5%), §11's own closing list ("twenty-five" to "about thirty"), and two
comments in `model.py`. The two sentences above are left as they were, still open.
