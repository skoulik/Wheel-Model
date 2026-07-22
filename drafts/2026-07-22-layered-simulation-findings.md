# Layered Simulation vs. the Homogeneous Model: First Tier-2 Results

Source: code/wheel_sim.py — a Monte Carlo simulator of the exact wheel mechanics of
sections 04–08 on a common GBM price path with each lot's call strike frozen at its
entry level, i.e. *without* the homogeneous-q approximation. Formula implementations
are imported from code/verify_examples.py; the cadence/tenor split of TODO #7 is
built in (default T = τ_p, the article's special case). Stdlib only, deterministic
(seed 20260722). Base scenario: the article's running example (p\* = 20%, monthly
puts, quarterly calls, μ = 7%, σ = 20%, r = 5%, m = 0.20), 200 paths × 30 years.
Stress scenario: crash-then-flatline (2y calm, 3-month crash with expected log-drop
30% at σ = 35%, 3y flatline at μ = 0, then calm), 300 paths × 10 years.

Design note: each individual call period exits with probability q(x) of eq:q given
the lot's current depth x = ln(K_c/S) — that is a mechanical consequence of the
price model, not a finding. What the simulation reveals is what the homogeneous
model averages away: the emergent depth distribution of *standing* inventory, the
holding-time mixture, correlated exits on the common path, and the resulting
economics.

Headline: the queue architecture survives — arrivals, departures and Track A income
all land where the formulas put them. The homogeneous *approximation* does not: in
the calm base regime (not in stress — in the article's own base case) equilibrium
inventory is ~3× the homogeneous I\*, and the true excess return collapses from the
+9.9%/yr of section 08 to ≈ 0. The fast/metastable/trapped holding-time structure
observed in the live statements (2026-07-10 draft, finding #4) emerges from depth
dependence alone. Numbered findings below, each with the model implication.

---

## 1. Validation: the mechanics land exactly where the formulas predict

Three built-in cross-checks tie the simulation to the article's formulas:

- Realized assignment rate 0.192 = p_rw exactly (risk-neutral p = 0.200). The
  TODO #4 measure-mixing gap is now visible in data: the risk-neutral p overstates
  arrivals by the predicted margin, confirming its role as a deliberate
  conservatism on the entry side.
- Mean drop at assignment 0.074 vs. the eq:d-mean prediction 0.075.
- Exit rates binned by depth match the q(x) curve to three decimals in every bin
  (from 0.506 vs. 0.511 at the money down to 0.005 vs. 0.006 at x ∈ [0.22, 0.35)).

Model implication: none — this is the license to trust the findings below. Every
deviation from the homogeneous model is an emergent effect of layering, not a
simulation artifact.

## 2. Equilibrium inventory is ~3× the homogeneous I\* — in the calm base regime

Simulated mean inventory: **3.65 lots** vs. the homogeneous I\* = 1.19 (risk-neutral
p) / 1.15 (real-world p). The mechanism is length bias: lots that ride a drawdown
deepen, deep lots linger, so standing inventory over-represents them. The
inventory-weighted depth distribution tells the story:

    bin of x        lot-qtrs   exit rate   q(x)
    [0.00,0.02)        8693      0.506     0.511
    [0.02,0.04)        6853      0.435     0.432
    [0.04,0.07)        7556      0.339     0.339
    [0.07,0.10)        5953      0.239     0.236
    [0.10,0.15)        8191      0.135     0.134
    [0.15,0.22)        9443      0.046     0.047
    [0.22,0.35)       13006      0.005     0.006
    [0.35, inf)       24900      0.000     0.000

Inventory-weighted mean depth is 0.289 vs. 0.032 for a fresh assignment; the
inventory-weighted mean q(x) is 0.154 vs. the homogeneous q(E[d]) = 0.423; the
effective per-put-period exit rate is 0.049 vs. q_p = 0.168. **29% of all
lot-quarters sit at depths where q ≈ 0** — a standing dead stratum, in a calm
market with healthy drift.

Model implication: the homogeneous I\* is not conservative; it understates
equilibrium inventory by a factor of ~3 at the article's own base parameters
(and the start-from-empty transient biases the simulated mean *down*, so 3× is
if anything an understatement). Sections 07/08 need a prominent flag until tier 2
replaces the estimate.

## 3. The fast/metastable/trapped mixture emerges — nothing needs to be postulated

Homogeneous q predicts geometric(q) call-period counts per completed lot. Simulated
(base scenario, 12,971 completed lots, 856 censored at the 30y horizon):

    periods:      1      2      3      4      5      6     >6
    simulated   0.447  0.160  0.087  0.053  0.040  0.029  0.184
    geometric   0.423  0.244  0.141  0.081  0.047  0.027  0.037

    KM survival (months):   3      6      9     12     24     36     60    120
                          0.578  0.425  0.342  0.290  0.182  0.131  0.083  0.040

The first-period exit share matches (fresh lots behave homogeneously), then the
distributions diverge: the simulated tail beyond six periods is **5× geometric**.
Median completed holding time 6 months, p90 36 months, max 27 years. This is
precisely the three-regime structure of TODO #9 — a fast lane, a metastable
middle, a trapped tail — arising from depth dependence plus the common path,
with a single q(x) function and no mixture parameters.

Model implication: answers the open question in TODO #9 — the mixture *emerges
from* depth dependence; it is not a separate parameterization. Tier 2 should
model depth dynamics and derive the mixture, not fit it.

## 4. Track A survives; Track B triples; the base-case excess return collapses to ≈ 0

Per-put-period Track A run rate: simulated 0.0188 vs. predicted 0.0191 (real-world
p) — eq:run-rate survives layering essentially intact. But average committed
capital is **5.29·S₀ vs. the predicted 1.32·S₀**, so the true excess return is
**−0.7%/yr, vs. the +9.9%/yr that section 08's base case reports for the same
parameters**. The deep strata are the reason: a lot at depth x ≥ 0.35 sells calls
worth ≈ 0 while its full basis stays committed — capital earning nothing, patiently
waiting for a recovery that is years away.

Model implication: section 08's base-case economics are an artifact of the
homogeneous approximation. The strategy's *income* formula is right; its *capital*
formula is wrong by the length-biased factor. And the operator levers the model
currently omits stop being refinements: call-strike policy (TODO #10) and dividend
carry (TODO #2/#16) are exactly what makes deep strata earn something, i.e. they
are load-bearing for the strategy having any edge at all.

## 5. The inventory distribution is nothing like Poisson

Var(I)/E[I] = 4.2 (Poisson: 1). P(I = 0) = 0.175, vs. 0.026 for a Poisson with the
same mean. The distribution is zero-inflated and heavy-tailed: the warehouse fully
empties in good stretches, piles deep in drawdowns. The Poisson picture of section
07 describes neither the typical state nor the fluctuations on a single name.

Model implication: strengthens TODO #1 — on one underlying, the Poisson claims
(P(I=0), ±√I\* fluctuations) are unusable; only the rate-balance logic survives.
The diversified-portfolio framing is the one worth defending.

## 6. Exit clustering is real but modest at base parameters

14.3% of exit dates clear more than one lot; the largest simultaneous batch is 4.
The mass-flush effect exists (a recovery through a strike level calls away the
strata below it) but at p\* = 20% with quarterly calls the inventory rarely holds
many lots at neighboring strikes.

Model implication: burstiness at these parameters comes less from simultaneous
exits than from the alternation of empty stretches and deep-drawdown accumulations
(finding 5). The TODO #1 caveat is directionally right but the single-name tail
risk is dominated by depth, not by batch exits.

## 7. Crash-then-flatline ratchets capital and heals on a decade scale

Mean over 300 paths (calm I\* would be ~1.2):

    t (years)    1.0   2.0   2.25   2.5   3.0   4.0   5.0   5.25   6.0   7.0   8.0   10.0
    mean I      1.35  2.06   3.83  4.28  4.90  5.51  6.25   6.42  6.43  5.98  5.87   5.37
    capital     1.64  2.47   5.83  6.40  7.30  8.32  9.66  10.05 10.25  9.61  9.33   8.64

The crash triples inventory in one quarter; the flatline then *keeps accumulating*
(arrivals continue, exits nearly stop — the μ = 0 regime has ν = μ − σ²/2 < 0, so
depths drift deeper). Five years of restored calm drift claw back only ~15% of the
peak. Capital peaks above 10·S₀ against a homogeneous prediction of 1.3.

Model implication: quantifies section 08's "crash-then-flatline is the primary
practical failure mode" and section 09's ratchet narrative. The healing timescale
(decade) belongs in tier 2's phase diagram as a first-class output.

## 8. The clean tier-2 formulation: Little's law + grid-sampled first passage

The simulation suggests replacing the geometric-q argument, not merely correcting
it. A lot's depth x_t = ln(K_c/S_t) follows arithmetic Brownian motion with drift
−ν, ν = μ − σ²/2, volatility σ, sampled on the call grid; the lot exits at the
first grid point with x ≤ 0. Then:

- **Little's law replaces eq:istar**: E[I] = (arrival rate) × E[holding time],
  with the holding time a grid-sampled first-passage time. Simulated E[T] ≈ 1.6y
  vs. the homogeneous τ_c/q ≈ 0.5y — the factor-3 inventory inflation is exactly
  the first-passage tail that geometric(q) truncates. (The continuous-passage
  naive x₀/ν ≈ 0.65y also undershoots: sampling only at call expiries roughly
  doubles the holding time. The call grid itself is economically material.)
- **A true stability condition falls out**: depths mean-revert iff ν = μ − σ²/2 > 0.
  At the article's base parameters ν = 5% — stable. At σ = 40% the same μ = 7%
  gives ν < 0: depths random-walk away and dead strata form *in calm markets*.
  The homogeneous model's "always stable whenever q > 0" (section 09) is replaced
  by a sharp, parameter-level criterion — and it is a condition on μ − σ²/2, not
  on q.

Model implication: tier 2's core should be the first-passage formulation — it
subsumes depth-dependent q_i (q(x) is just the one-step exit probability of the
same process), yields the stability condition for free, and reduces the phase
diagram to properties of grid-sampled ABM passage times. The q_i-per-layer
bookkeeping of the original tier-2 sketch becomes a derived object, not the
primitive.

## 9. Dividends: the carry does not pay for the deeper hole  [added same day]

Dividends added under the total-return convention (TODO #2a): μ stays the asset's
*total* expected return, the price drifts at μ − δ, held lots accrue
δ_net = δ·(1 − 15% withholding) per year of holding, and pricing/probabilities use
the dividend-yield Black–Scholes generalization (δ = 0 reproduces findings 1–8
exactly; the generalized helpers live in wheel_sim.py and are asserted equal to
the verify_examples.py formulas at δ = 0). Sweep at the base parameters:

    delta      nu    I*_rw   mean I   capital   prem/T   div/T   excess/yr
     0.0%   +0.050    1.15    3.65      5.29    0.0188   0.0000   -0.0073
     1.0%   +0.040    1.18    4.01      6.09    0.0185   0.0028   -0.0081
     2.5%   +0.025    1.23    4.71      7.71    0.0181   0.0081   -0.0092
     4.0%   +0.010    1.29    5.51      9.95    0.0175   0.0152   -0.0105
     6.0%   -0.010    1.36    6.76     14.31    0.0166   0.0282   -0.0124
    alt 2.5% +0.050   1.09    3.46      5.01    0.0171   0.0059   +0.0052

Three observations:

- **The trade-off resolves against the wheel, monotonically.** Every percentage
  point of yield taken out of the price drift deepens the strata (ν = μ − δ − σ²/2
  falls; at δ = 2.5% mean inventory rises 3.65 → 4.71 and capital 5.3 → 7.7·S₀).
  The carry is substantial — at δ = 2.5% dividends contribute 9.7%/yr of S₀,
  a third of total income — but it recovers *most, not all* of the extra capital
  charge and slower recycling: excess return declines smoothly from −0.7% to
  −1.2%/yr across the sweep. No wash, no free lunch: under equal total return,
  dividend yield is mildly negative for the wheel.
- **Dividend carry scales with the dead strata, as #16 predicted.** Realized
  carry per period is 0.0081 vs the homogeneous prediction 0.0022 — understated
  by the same length-bias factor (~3.5×) as inventory itself, because carry
  accrues per unit holding time and holding time concentrates on deep lots. The
  trapped tail also deepens: KM survival at 10y rises 0.040 → 0.072, and lot-
  quarters at q ≈ 0 depths go from 29% to 39%. The δ = 6% row has ν < 0 —
  unstable; its 30y mean masks unbounded accumulation — which *derives* the live
  account's STRF behavior (bond-like ~9% yielder, permanently trapped, held for
  carry) rather than footnoting it as an outlier.
- **The conclusion is convention-sensitive, and honestly so.** The alt row
  (price drift held at 7%, δ stacked on top — total return 9.5%) is the only
  positive-excess row. If high yield came with no price-drift sacrifice, carry
  would help; under the equal-total-return null it hurts. The article should
  state the convention and this sensitivity explicitly when TODO #2 lands.

Model implication: #16 is quantified — the patience of deep lots is indeed
carry-financed, but the financing is partial. The stability condition of finding
8 generalizes to **ν = μ − δ − σ²/2 > 0**: yield moves the phase boundary, and
high-yield wheeling sits in the unstable region by construction. Tier 2's phase
diagram gains δ as a first-class axis.

## 10. First-passage analytics validated; the homogeneous gap fully decomposed  [added same day]

`code/first_passage.py` implements the tier-2 formulation of finding 8 as
deterministic analytics: the exact truncated-normal entry law for x₀, an
integral-equation solver for the survival sequence P(J > j) (Gaussian step
kernel on the positive half-line, geometric tail closure), the Siegmund
closed form, and Little's law plus a finite-horizon transient integral.
Everything cross-checks:

- The IE survival curve matches the wheel simulation's Kaplan–Meier to
  **three decimals at every horizon** in both configs, and matches a pure
  random-walk Monte Carlo (400k walks, no wheel machinery) to four decimals
  on survival and <0.5% on E[J]. The first-passage formulation *is* the
  layered wheel, computed two independent ways.
- Headline quantities (base / δ=2.5%): E[T] = **2.04y / 3.97y** vs the
  homogeneous τ_c/q of 0.59y / 0.63y; stationary I\* = **4.70 / 9.14** vs
  homogeneous 1.15 / 1.23. The Siegmund form (x₀ + βσ√τ_c)/(ν·τ_c) lands
  within 9–12% of exact — good enough for prose, with the interpretable
  decomposition: the call-grid tax βσ√τ_c is 1.8× the typical entry depth,
  i.e. *the exit grid, not the entry overshoot, dominates holding time*.
- **The discrepancy flagged when the closed form first overshot the 30y MC is
  fully resolved: horizon truncation plus MC noise, no model error.** The
  finite-horizon prediction integrated from the same survival curve
  reproduces the 30y MC within 3% (3.55 vs 3.65; 4.67 vs 4.71); multi-seed
  long-window MC brackets the window prediction (4.21–5.24 across seeds vs
  4.63); a 120-path × 300y run gives 4.82 vs stationary 4.70.
- New article-grade quantity: **time for E[I(t)] to reach 90% of stationary:
  24 years at base, 88 years at δ = 2.5%.** At moderate yield the wheel never
  sees its own equilibrium within an operator's lifetime — every 30y number
  in findings 2 and 9 is a *transient* reading on the way to worse stationary
  values, and the finite-horizon integral (not the stationary formula) is the
  practically relevant capital number.
- Unstable corner (ν < 0), now computed honestly: at σ = 40% (ν = −0.01) the
  trapped-forever fraction is P(J = ∞) ≈ 2.2% per assignment — the dead
  stratum grows at λ·P_trap ≈ 0.05 lots/year without bound. Methods note: the
  first IE attempt used a sticky top boundary that let far-escaped walks
  artificially return and destroyed the plateau; the pure-walk bisect caught
  it, and the trapped fraction now comes from the analytic escape probability
  with the Siegmund boundary shift, 1 − E[exp(−2|ν|(x₀+βσ√τ_c)/σ²)].

Model implication: the tier-2 derivation chain is complete and verified —
entry law → grid-sampled first passage (IE exact; Siegmund for prose) →
Little's law for stationary I\*, transient integral for operator horizons,
escape probability for the unstable phase. The homogeneous model is exactly
the first-period truncation of this object (E[q(x₀)] = 0.425 vs q(E[d]) =
0.423 — first-period behavior is homogeneous; everything after is not).
What remains for #19 is writing: the tier-2 sections, with detours for
Little's law and first-passage times.

---

## Caveats (what the simulator deliberately omits)

- **Dividends are continuous-accrual** (finding 9): no discrete ex-dates, no
  dividend-driven early exercise (TODO #5/#2c — the latter *helps* the strategy,
  so its omission is conservative here); withholding a single blended rate.
- **No call-strike policy** (TODO #10): K_c frozen at entry forever. Real operators
  strike down to harvest dead strata; finding 4 quantifies the cost of *not*
  doing so, i.e. the value of that lever.
- **IV = RV** (no volatility risk premium, TODO #4): premiums are priced at the
  path volatility. The strategy's documented IV > RV edge would add income on top.
- **Single name**: findings 5–6 are the single-name picture; diversification
  restores Poisson-like aggregates (TODO #1).
- **No transaction costs** (TODO #12), European exercise only (TODO #5).
