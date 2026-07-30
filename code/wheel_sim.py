"""Monte Carlo simulator of the wheel, and the independent check on model.py.

Simulates the exact mechanics of Parts I-II on a common GBM price path, with
each lot's call strike frozen at its entry level: a put sold on the cadence
grid, assignment when it finishes in the money, and a covered call rewritten
every tau_c until the lot is called away. None of the analytic machinery is
used here -- the depth walk, the first passage and Little's law of `model.py`
are what this is meant to test -- so agreement between the two is evidence
rather than arithmetic.

`--scenario validate` is that comparison, component by component, from the
assignment rate through to the economic excess return. The other scenarios are
exploratory, and show what the analytic core cannot:

  * the emergent depth distribution of standing inventory (length-biased
    toward slow, deep layers),
  * correlated exits on the common path (a recovery flushes whole strata),
  * the shape of the holding-time distribution, fast lane to trapped tail,
  * dead-strata formation under crash-then-flatline stress.

`--scenario constrained` is the account with a finite balance: a put is sold
only if assignment would leave utilization under the operator's stopping rule,
the debit is tracked as a jump process, equity is marked to market, and the
broker's requirement is monitored CONTINUOUSLY, through a Brownian-bridge
crossing test that makes the answer independent of the event grid. It exists
because model.py's liquidation barrier is static -- it holds the book fixed
and lets only the price move -- and the wheel does several things to that
barrier at once. On each path two barriers are therefore carried side by side:
the account's own, and the same barrier frozen at the moment the account first
filled. The second is model.py's assumption measured rather than computed, so
it says whether the machinery is right; the difference between them is paired
on a common price path, so it says what the wheel does to it. Everything here
is the simulator's own ledger -- no formula is imported from the working
capital block -- and the frozen barrier agrees with `liquidation_prob` to
within its standard error at every horizon tested.

Defaults are the unlimited operator of Parts I and II, and inertly so: with
`equity = inf` the ledger is skipped entirely and the four scenarios above run
the same statements against the same random stream as before it existed.

Dividends under the total-return convention: mu is the asset's TOTAL expected
return, the price drifts at mu - delta, held lots accrue delta_net =
delta*(1 - withholding) per year of holding (reported as a separate Track A
line), and option pricing/probabilities use the dividend-yield Black-Scholes
generalization. delta = 0 reproduces the no-dividend model exactly. The
carry-vs-recovery trade-off: carry pays on held lots, but the depth drift
nu = mu - delta - sigma^2/2 shrinks with delta, so lots recycle slower and
inventory grows; nu > 0 is the stability boundary.

The cadence/tenor split is built in: cadence T >= tau_p, defaulting to
T = tau_p, the article's running example.

Stdlib only.  Run:  python code/wheel_sim.py
    [--scenario base|dividends|stress|sweep|validate|constrained|all]
"""

import argparse
import heapq
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from math import exp, log, sqrt

from model import (Config, N, bs_call, bs_put, entry_law, expected_drop,
                   k_star_drift, pmap)
import random

# Event priorities at equal timestamps: settle expiring options first, then
# sample state and sell the next put.
PUTEXP, CALLEXP, SALE = 0, 1, 2

DEPTH_EDGES = [0.0, 0.02, 0.04, 0.07, 0.10, 0.15, 0.22, 0.35, float("inf")]
KM_HORIZONS_M = [3, 6, 9, 12, 24, 36, 60, 120]
DRAW_POLICIES = ("service", "retain", "income", "stationary")

# Path batches for the constrained scenario.  Fixed, and NOT derived from the
# core count: each batch seeds its own generator, so the answer is the same
# whether the pool has one worker or thirty-two, which is the property that
# makes WHEEL_WORKERS=1 a debugging tool rather than a different experiment.
BATCHES = 32


@dataclass
class Regime:
    start: float
    mu: float
    sigma: float


@dataclass
class Params:
    p_star: float = 0.20
    tau_p: float = 1 / 52      # one week, matching model.Config
    n: int = 4                 # tau_c = n * tau_p = 4 weeks
    cadence: float = None      # T >= tau_p; None -> T = tau_p
    r: float = 0.05
    gamma_p: float = 0.20      # put margin fraction, matching model.Config
    mu: float = 0.07           # TOTAL expected return; price drifts at mu - delta
    sigma: float = 0.20
    delta: float = 0.0         # gross dividend yield
    withhold: float = 0.15     # withholding tax fraction on dividends
    iv_spread: float = 0.0     # sigma_iv = regime sigma + spread (0 = no VRP)
    # -- working capital.  The defaults are the operator of Parts I and II:
    # unlimited equity never has a put refused and never receives a margin
    # call, so the ledger in run_path is skipped entirely and every scenario
    # that existed before the constraint did runs the same statements against
    # the same random stream.  That is the regression guard, stated as a
    # branch rather than as an argument.
    gamma_s: float = 1.0       # equity fraction required against held shares
    equity: float = float("inf")   # A, in share prices at t = 0
    u_star: float = 1.0        # stop selling puts above this utilization;
                               # u* = 1 runs to the broker's own limit
    fin_spread: float = 0.0    # r_b - r, charged on a debit balance
    draw: object = "service"   # cash policy: "service" (withdraw income, pay
                               # the debit's interest out of it -- model.py's
                               # g = 0), "retain" (withdraw nothing), "income"
                               # (withdraw income and let the interest
                               # compound, g = r_b), "stationary" (retain
                               # everything but a fixed fraction of equity per
                               # year, see draw_frac), or a float of share
                               # prices per year
    draw_frac: float = 0.0     # the fraction under the "stationary" policy
    years: float = 30.0
    paths: int = 200
    seed: int = 20260722
    regimes: list = None

    def __post_init__(self):
        if self.cadence is None:
            self.cadence = self.tau_p
        if self.regimes is None:
            self.regimes = [Regime(0.0, self.mu, self.sigma)]
        self.tau_c = self.n * self.tau_p
        self.delta_net = self.delta * (1 - self.withhold)
        self.r_b = self.r + self.fin_spread
        self._starts = [rg.start for rg in self.regimes]
        if isinstance(self.draw, str) and self.draw not in DRAW_POLICIES:
            raise ValueError(f"unknown draw policy {self.draw!r}")

    def nominal_g(self):
        """The debit growth rate the closed forms would be told to assume.

        Only the two policies that pin g exactly have one: holding the debit
        flat is g = 0, and withdrawing the income while the interest accrues
        is g = r_b on the nose.  Retention and a fixed cash draw do not -- the
        first repays the debit at a rate that depends on how big it is, the
        second is the linearization model.py warns about -- so they return
        None and the report has only the realized figure to show.
        """
        return {"service": 0.0, "income": self.r_b}.get(self.draw)


class Lot:
    __slots__ = ("entry", "strike", "basis", "x", "periods")

    def __init__(self, entry, strike, basis):
        self.entry = entry
        self.strike = strike
        self.basis = basis
        self.x = 0.0        # depth ln(K_c/S) at the current call's sale
        self.periods = 0    # call periods run so far


class Agg:
    """Statistics accumulated across all paths of one scenario."""

    def __init__(self):
        self.puts = 0
        self.assigned = 0
        self.d_sum = 0.0
        self.exits = 0
        self.prem_put = 0.0        # spot-normalized, summed
        self.prem_call = 0.0
        self.dividends = 0.0       # spot-normalized net dividend carry
        self.inv_hist = Counter()  # inventory level at cadence dates
        self.cap_sum = 0.0
        self.cap_n = 0
        # Economic ledger (the no-arbitrage-consistent one): inventory carried
        # at market value, the mark loss booked at acquisition, the upside
        # given away booked at call-away.  All spot-normalized when they occur.
        self.mvcap_sum = 0.0
        self.acq_loss = 0.0
        self.giveaway = 0.0
        self.inv_by_idx = Counter()    # for time profiles (stress scenario)
        self.eq_by_idx = Counter()     # log equity in shares, by cadence index
        self.eqn_by_idx = Counter()    # ...and how many paths contributed
        self.cap_by_idx = Counter()    # Track A (cost basis), by cadence index
        self.mvcap_by_idx = Counter()  # Track B (market value), by cadence index
        self.n_by_idx = Counter()
        self.durations = []        # (months, completed?) per lot
        self.period_hist = Counter()   # call periods per *completed* lot
        self.batch_hist = Counter()    # simultaneous exits per exit date
        # depth bins: [lot-periods, exits, sum q_theory, sum x]
        self.bins = [[0, 0, 0.0, 0.0] for _ in DEPTH_EDGES[:-1]]
        # -- the constrained account.  All of this stays zero unless Params
        # gives the operator a finite equity.
        self.paths = 0
        self.sales = 0             # cadence dates reached alive
        self.blocked = 0           # ...on which no put was sold
        self.withdrawn = 0.0
        self.t_liq = []            # liquidation time from an EMPTY book, or inf
        self.sat_times = []        # first refused put, per path that had one
        self.a_sat = []            # -ln f* as the ledger stood at that moment
        self.window = []           # years observed after it
        self.liq_dyn = []          # years from saturation to liquidation, or inf
        self.liq_stat = []         # ...of the frozen barrier, on the same path
        self.g_real = []           # realized log growth of the debit
        self.r_drift = []          # ...and of M/D, which is what the barrier sees
        self.e_drift = []          # ...and of equity measured in shares
        # Post-saturation, time-weighted: the regime the closed forms describe.
        self.ps_t = self.ps_inv = self.ps_lev = self.ps_income = 0.0
        self.ps_eq = self.ps_eqt = 0.0
        self.ps_sales = self.ps_blocked = 0
        self.bins_ps = [[0, 0, 0.0, 0.0] for _ in DEPTH_EDGES[:-1]]

    def record_call_period(self, x, exited, mu, sigma, tau_c, saturated=False):
        q_th = N(((mu - sigma**2 / 2) * tau_c - x) / (sigma * sqrt(tau_c)))
        i = bisect_right(DEPTH_EDGES, x) - 1
        for b in (self.bins, self.bins_ps) if saturated else (self.bins,):
            b[i][0] += 1
            b[i][1] += 1 if exited else 0
            b[i][2] += q_th
            b[i][3] += x

    _SCALARS = ("puts", "assigned", "d_sum", "exits", "prem_put", "prem_call",
                "dividends", "cap_sum", "cap_n", "mvcap_sum", "acq_loss",
                "giveaway", "paths", "sales", "blocked", "withdrawn", "ps_t",
                "ps_inv", "ps_lev", "ps_eq", "ps_eqt", "ps_income", "ps_sales",
                "ps_blocked")
    _COUNTERS = ("inv_hist", "inv_by_idx", "eq_by_idx", "eqn_by_idx",
                 "cap_by_idx", "mvcap_by_idx", "n_by_idx", "period_hist",
                 "batch_hist")
    _LISTS = ("durations", "t_liq", "sat_times", "a_sat", "window", "liq_dyn",
              "liq_stat", "g_real", "r_drift", "e_drift")

    def merge(self, o):
        """Absorb another Agg, so a run can be split over a process pool."""
        for k in self._SCALARS:
            setattr(self, k, getattr(self, k) + getattr(o, k))
        for k in self._COUNTERS:
            getattr(self, k).update(getattr(o, k))
        for k in self._LISTS:
            getattr(self, k).extend(getattr(o, k))
        for name in ("bins", "bins_ps"):
            for a, b in zip(getattr(self, name), getattr(o, name)):
                for i in range(4):
                    a[i] += b[i]
        return self


def regime_at(P, t):
    return P.regimes[max(0, bisect_right(P._starts, t + 1e-12) - 1)]


def advance(S, t0, t1, P, rng):
    """Exact GBM step from t0 to t1, split at regime boundaries."""
    if t1 - t0 <= 1e-12:
        return S
    i = max(0, bisect_right(P._starts, t0 + 1e-12) - 1)
    a = t0
    while a < t1 - 1e-12:
        b = t1 if i + 1 >= len(P._starts) else min(t1, P._starts[i + 1])
        rg = P.regimes[i]
        dt = b - a
        S *= exp((rg.mu - P.delta - rg.sigma**2 / 2) * dt
                 + rg.sigma * sqrt(dt) * rng.gauss(0.0, 1.0))
        a = b
        i += 1
    return S


def bridge_hit(s_a, s_b, b_a, b_b, var, u):
    """Did the price touch the barrier between two samples?

    Testing a continuous barrier only on the event grid misses every excursion
    that dips below and recovers inside a week, and the size of that miss is a
    function of the step -- so an uncorrected simulator answers a question
    about its own grid rather than about the account, and cannot be compared
    with a closed form that monitors continuously.  Conditional on the two
    endpoints the crossing probability is exactly

        exp( -2 * ln(S_a/B_a) * ln(S_b/B_b) / (sigma^2 * dt) ),

    the Brownian-bridge formula for a boundary linear in time, which ln B is
    here: the lot count cannot change between events and the debit accrues
    smoothly.  Being exact given the endpoints, it makes the answer
    independent of the partition rather than merely less wrong -- which is
    also what lets the shadow barrier below keep running on a coarser grid
    after the account is gone.

    `u` is passed in rather than drawn so that the frozen barrier and the
    moving one can be tested against the SAME uniform.  The probability is
    monotone in the barrier level, so one draw couples the two: whichever
    barrier is nearer is hit whenever the other is, and their difference --
    the whole object of the exercise -- is measured paired instead of as the
    gap between two separately noisy estimates.
    """
    if b_a <= 0.0 and b_b <= 0.0:
        return False                        # nothing borrowed, nothing to call
    if (b_a > 0.0 and s_a <= b_a) or (b_b > 0.0 and s_b <= b_b):
        return True
    if b_a <= 0.0 or b_b <= 0.0:
        # The debit was repaid inside the step, so the barrier fell away
        # partway through it.  Only income can do that between events, and
        # only to a debit already small enough to be paid off in a week, so
        # the excursion this ignores is one to a barrier already near zero.
        return False
    if var <= 0.0:
        return False
    return u < exp(-2.0 * log(s_a / b_a) * log(s_b / b_b) / var)


def run_path(P, rng, agg):
    S, t = 1.0, 0.0
    heap = []
    seq = 0

    def push(te, prio, data):
        nonlocal seq
        heapq.heappush(heap, (te, prio, seq, data))
        seq += 1

    push(0.0, SALE, None)
    lots = []
    exits_at = Counter()

    # ---- the account.  `ledger` off is Parts I and II verbatim.
    ledger = P.equity != float("inf")
    cash = P.equity                 # negative is a debit, financed at r_b
    dead = False                    # liquidated: the account ends, the price does not
    t_liq = float("inf")            # ...when, measured from an empty book
    t_sat = None                    # first put refused for want of capacity
    b_frozen = 0.0                  # the barrier as it stood at that moment
    t_stat = float("inf")           # when that frozen barrier was first touched
    d_a = d_b = d_sat = d_last = 0.0
    m_sat = m_last = 0.0            # market value of the book at the same two points
    eq_sat = eq_last = s_sat = s_last = 0.0
    t_end = P.years
    ps_sales = ps_blocked = 0
    # Which flows stay in the account.  Income is premium plus net dividend;
    # the strike paid at assignment and received at call-away is principal and
    # always moves the cash.  "service" and "income" both withdraw the income;
    # they differ in the interest, which "service" pays out of it -- and only
    # when it is being PAID, since model.py's g = 0 is a statement about a
    # debit and its unlevered counterpart (max_sustainable_draw at D = 0) is
    # "withdraw the income", interest on an idle balance staying in.
    keep_income = not (isinstance(P.draw, str) and P.draw in ("service", "income"))
    service = P.draw == "service"
    # "stationary" is the policy that makes the analytic frontier's steady
    # state reachable at all.  model.py works in share prices, so its account
    # is stationary in LOTS -- which requires equity to compound at the price
    # drift.  An operator who withdraws the income (g = 0) holds equity flat in
    # dollars instead, and a dollar-flat account shrinks in lots at the drift:
    # that is the first thing the constrained simulator found, and it is why a
    # draw expressed as a fraction of equity is here beside one expressed in
    # cash.
    proportional = P.draw == "stationary"

    def earn(amount):
        """Book a premium: to the account under a policy that retains it, out
        of the door under one that does not.  Either way it is income, and it
        is accumulated per unit of the spot RULING AT THE TIME, which is the
        normalization every figure in model.py is quoted in."""
        nonlocal cash
        if ledger:
            if keep_income:
                cash += amount
            else:
                agg.withdrawn += amount
            if t_sat is not None:
                agg.ps_income += amount / S

    while heap:
        te, prio, _, data = heapq.heappop(heap)
        dt = min(te, P.years) - t
        div = len(lots) * P.delta_net * dt
        agg.dividends += div
        if ledger and not dead:
            # Interest is signed: earned on an idle balance, paid on a debit.
            interest = cash * (P.r if cash >= 0 else P.r_b) * dt
            m_last = len(lots) * S             # S is still the interval's start
            take = 0.0 if keep_income else div
            if service and interest < 0.0:
                take += interest              # the debit's interest, serviced
            elif proportional:
                take += P.draw_frac * max(0.0, cash + m_last) * dt
            elif not isinstance(P.draw, str):
                take += P.draw * dt
            d_a = max(0.0, -cash)
            cash += div + interest - take
            d_b = d_last = max(0.0, -cash)
            eq_last, s_last = cash + m_last, S
            agg.withdrawn += take
            if t_sat is not None:
                eq = cash + m_last
                agg.ps_t += dt
                agg.ps_inv += len(lots) * dt
                if eq > 0.0:                    # equity in SHARES, as A is,
                    agg.ps_eq += log(eq / S) * dt   # and in logs, see eq_by_idx
                    agg.ps_eqt += dt
                agg.ps_lev += (m_last / eq if eq > 0 else 0.0) * dt
                agg.ps_income += div / S
        if te > P.years + 1e-9:
            break
        s_a = S
        sig_step = regime_at(P, t).sigma       # constrained runs are single-regime
        S = advance(S, t, te, P, rng)
        t = te

        if ledger:
            operating = (not dead) and lots and P.gamma_s < 1.0 and (d_a > 0.0 or d_b > 0.0)
            shadow = b_frozen > 0.0 and t_stat == float("inf")
            if operating or shadow:
                u = rng.random()
                var = sig_step**2 * dt
                if operating:
                    den = (1.0 - P.gamma_s) * len(lots)
                    if bridge_hit(s_a, S, d_a / den, d_b / den, var, u):
                        dead, t_liq, t_end = True, t, t
                        for lot in lots:       # sold out from under the operator
                            agg.durations.append(
                                (round((t - lot.entry) * 12, 6), False))
                        lots = []
                        cash = 0.0
                if shadow and bridge_hit(s_a, S, b_frozen, b_frozen, var, u):
                    t_stat = t
            # Nothing is left to learn from a dead path once its shadow has
            # resolved; until then the price alone is stepped on, which is all
            # the frozen barrier is a statement about.
            if dead and (t_stat < float("inf") or b_frozen <= 0.0):
                break

        rg = regime_at(P, t)
        sig_iv = rg.sigma + P.iv_spread

        if prio == SALE:
            # Sample state at the cadence grid (after same-date settlements).
            idx = round(t / P.cadence)
            if dead:
                if t + P.cadence <= P.years + 1e-9:
                    push(t + P.cadence, SALE, None)
                continue
            agg.inv_hist[len(lots)] += 1
            agg.inv_by_idx[idx] += len(lots)
            agg.n_by_idx[idx] += 1
            agg.sales += 1
            if ledger and cash + len(lots) * S > 0.0:
                # In LOGS: equity/S is a ratio of two lognormals, and its
                # arithmetic mean over sixty years is carried entirely by the
                # paths on which the price collapsed.  The geometric mean is
                # the one that describes an account.
                agg.eq_by_idx[idx] += log((cash + len(lots) * S) / S)
                agg.eqn_by_idx[idx] += 1
            # Sell the put.  The strike dial is a real-world assignment
            # probability (the model's one measure), so k* inverts the
            # P-world probability; the premium is a quote, priced at IV.
            kf = k_star_drift(P.p_star, P.tau_p, rg.sigma, rg.mu - P.delta)
            K = kf * S
            # Blocked means skip the put: the operator does not sell what they
            # could not cover.  Equity is marked to market, so capacity in lots
            # moves with the price -- an unlevered account's rises as the price
            # falls and a levered one's falls -- which the static barrier, with
            # its fixed A, cannot see.  The put's own collateral is left out
            # here as it is left out of model.py's capacity and barrier: one
            # exclusion, applied uniformly, worth 1.5% of a saturated account.
            if ledger and (P.gamma_s * (len(lots) + 1) * S
                           > P.u_star * (cash + len(lots) * S) + 1e-12):
                agg.blocked += 1
                if t_sat is None:
                    # At the first refusal the book is at capacity by
                    # construction, so realized leverage is the stopping
                    # rule's -- exactly the state the closed form starts in,
                    # reached without a burn-in or an imported census.  Freeze
                    # the barrier here and let the price alone move it: that
                    # frozen level IS model.py's f*, computed from the ledger.
                    t_sat = t
                    d_sat, m_sat = max(0.0, -cash), len(lots) * S
                    eq_sat, s_sat = cash + m_sat, S
                    if len(lots) and P.gamma_s < 1.0 and d_sat > 0.0:
                        b_frozen = d_sat / ((1.0 - P.gamma_s) * len(lots))
                    agg.sat_times.append(t)
                    agg.a_sat.append(log(S / b_frozen) if b_frozen > 0.0
                                     else float("inf"))
                ps_blocked += 1
                ps_sales += 1
            else:
                c_p = S * bs_put(kf, P.tau_p, sig_iv, P.r, P.delta)
                agg.puts += 1
                agg.prem_put += c_p / S
                earn(c_p)
                if t_sat is not None:
                    ps_sales += 1
                # Both capital tracks, spot-normalized.  Track A is margin plus
                # what was paid for the standing lots; Track B is margin plus what
                # they are worth now -- and a share is worth one share however far
                # it has fallen, so Track B is just the lot count.  Their gap is
                # the accumulated paper loss on standing inventory.
                cost_cap = P.gamma_p * K + sum(l.basis for l in lots)
                mv_cap = P.gamma_p * kf + len(lots)
                agg.cap_sum += cost_cap / S
                agg.mvcap_sum += mv_cap
                agg.cap_n += 1
                agg.cap_by_idx[idx] += cost_cap / S
                agg.mvcap_by_idx[idx] += mv_cap
                push(t + P.tau_p, PUTEXP, (K, S, c_p))
            if t + P.cadence <= P.years + 1e-9:
                push(t + P.cadence, SALE, None)

        elif prio == PUTEXP:
            if dead:
                continue
            K, S_sale, c_p = data
            if S < K:
                agg.assigned += 1
                agg.d_sum += 1 - S / S_sale
                agg.acq_loss += (K - S) / S      # paid K for something worth S
                lot = Lot(entry=t, strike=K, basis=K - c_p)
                lots.append(lot)
                if ledger:
                    cash -= K                    # this is what grows the debit
                # Sell the first covered call at the frozen strike.
                c_c = bs_call(S, K, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                earn(c_c)
                lot.x = log(K / S)
                push(t + P.tau_c, CALLEXP, lot)

        else:  # CALLEXP
            if dead:
                continue
            lot = data
            lot.periods += 1
            exited = S >= lot.strike
            agg.record_call_period(lot.x, exited, rg.mu - P.delta, rg.sigma,
                                   P.tau_c, t_sat is not None)
            if exited:
                agg.exits += 1
                agg.giveaway += (S - lot.strike) / S   # delivered below market
                lots.remove(lot)
                if ledger:
                    cash += lot.strike           # ...and this is what repays it
                agg.durations.append((round((t - lot.entry) * 12, 6), True))
                agg.period_hist[lot.periods] += 1
                exits_at[round(t, 9)] += 1
            else:
                c_c = bs_call(S, lot.strike, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                earn(c_c)
                lot.x = log(lot.strike / S)
                push(t + P.tau_c, CALLEXP, lot)

    for lot in lots:  # censored at the horizon
        agg.durations.append((round((P.years - lot.entry) * 12, 6), False))
    for cnt in exits_at.values():
        agg.batch_hist[cnt] += 1

    agg.paths += 1
    if ledger:
        agg.t_liq.append(t_liq)
        agg.ps_sales += ps_sales
        agg.ps_blocked += ps_blocked
        if t_sat is not None:
            agg.window.append(max(0.0, P.years - t_sat))
            agg.liq_dyn.append(t_liq - t_sat if t_liq < float("inf")
                               else float("inf"))
            agg.liq_stat.append(t_stat - t_sat if t_stat < float("inf")
                                else float("inf"))
            # The realized growth rate of the debit, against the g the closed
            # forms were told to assume.  Defined only while there is a debit
            # at both ends; an account that repays itself has no log growth.
            # The second line is what actually governs survival: the barrier
            # is a statement about R = D/M, whose drift the closed form takes
            # to be nu - g with M moving on the price alone.
            #
            # Survivors only.  A liquidated path ends with its equity at the
            # barrier by definition, so including it would measure the
            # liquidation rather than the policy -- these three describe the
            # regime an account operates in, not how it leaves.
            if dead:
                pass
            elif d_sat > 0.0 and d_last > 0.0 and t_end > t_sat:
                agg.g_real.append(log(d_last / d_sat) / (t_end - t_sat))
                if m_sat > 0.0 and m_last > 0.0:
                    agg.r_drift.append(
                        log((d_sat / m_sat) / (d_last / m_last)) / (t_end - t_sat))
            # Equity measured in shares, which is the unit model.py's A is in.
            # Its drift says whether the account this run describes is the
            # stationary one the frontier prices, or one sliding away from it.
            if not dead and eq_sat > 0.0 and eq_last > 0.0 and t_end > t_sat:
                agg.e_drift.append(log((eq_last / s_last) / (eq_sat / s_sat))
                                   / (t_end - t_sat))


def simulate(P, seed=None, paths=None):
    rng = random.Random(P.seed if seed is None else seed)
    agg = Agg()
    for _ in range(P.paths if paths is None else paths):
        run_path(P, rng, agg)
    return agg


def _batch(job):
    """One block of paths with its own generator.  A pmap worker."""
    P, seed, npaths = job
    return simulate(P, seed=seed, paths=npaths)


def batch_jobs(P, batches=BATCHES):
    """The pmap jobs one run splits into.  Exposed so a caller with several
    runs to do can put them all through a single pool."""
    sizes = [P.paths // batches + (1 if i < P.paths % batches else 0)
             for i in range(batches)]
    return [(P, P.seed + 1009 * i, s) for i, s in enumerate(sizes) if s]


def merge_all(aggs):
    out = Agg()
    for a in aggs:
        out.merge(a)
    return out


def simulate_batched(P, batches=BATCHES):
    """`simulate`, split over a process pool without changing the answer."""
    return merge_all(pmap(_batch, batch_jobs(P, batches)))


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def km_survival(durations, horizons_m):
    """Kaplan-Meier survival of lot holding time (months), with censoring."""
    ds = sorted(durations)
    curve, surv, at_risk, i = [], 1.0, len(ds), 0
    while i < len(ds):
        tt = ds[i][0]
        ev = cen = 0
        while i < len(ds) and ds[i][0] == tt:
            if ds[i][1]:
                ev += 1
            else:
                cen += 1
            i += 1
        if ev:
            surv *= 1 - ev / at_risk
            curve.append((tt, surv))
        at_risk -= ev + cen
    out = []
    for h in horizons_m:
        s = 1.0
        for tt, sv in curve:
            if tt <= h:
                s = sv
            else:
                break
        out.append(s)
    return out


def as_config(P, label="sim"):
    """The analytic Config matching a simulator Params."""
    return Config(p_star=P.p_star, tau_p=P.tau_p, n=P.n, cadence=P.cadence,
                  r=P.r, mu=P.mu, sigma=P.sigma, delta=P.delta,
                  withhold=P.withhold, iv_spread=P.iv_spread,
                  gamma_p=P.gamma_p, gamma_s=P.gamma_s, equity=P.equity,
                  u_star=P.u_star, fin_spread=P.fin_spread, label=label)


def closed_forms(P):
    """The analytic core's entry-side predictions for this configuration.

    Closed forms only -- strike, assignment probability, expected drop and
    expected entry depth -- so they cost nothing and give `report` a reference
    column without running the depth walk. Everything downstream of entry
    needs the walk, and that comparison is `--scenario validate`.

    Single-regime only: `Config` has one mu and one sigma, so there is no
    honest reference for the stress scenario and `report` prints none.
    """
    C = as_config(P)
    k, p_real, mean_x0, _ = entry_law(C, "P")
    return {"k": k, "p_real": p_real, "E[d]": expected_drop(C, "P"),
            "E[x0]": mean_x0}


def report(P, agg, name):
    M = closed_forms(P) if len(P.regimes) == 1 else None
    line = "=" * 72
    print(f"\n{line}\nScenario: {name}   "
          f"({P.paths} paths x {P.years:g}y, tau_p={P.tau_p:.4f}, "
          f"T={P.cadence:.4f}, n={P.n}, p*={P.p_star:g}, seed={P.seed})")
    for rg in P.regimes:
        print(f"  regime from t={rg.start:>5.2f}y: mu={rg.mu:+.3f} (total), "
              f"sigma={rg.sigma:.2f}, nu={rg.mu - P.delta - rg.sigma**2 / 2:+.3f}")
    if P.delta:
        print(f"  dividends: delta={P.delta:.3f} gross, withholding {P.withhold:.0%}, "
              f"delta_net={P.delta_net:.4f}")
    print(line)

    if M:
        print("\n-- Analytic core, entry side (model.py closed forms) --")
        print(f"  k*={M['k']:.4f}  p_real={M['p_real']:.3f}  "
              f"E[d]={M['E[d]']:.3f}  E[x0]={M['E[x0]']:.4f}")
    else:
        print("\n-- No analytic reference: the core assumes a single regime --")
    print("  (the full component-by-component comparison is --scenario validate)")

    n_samples = sum(agg.inv_hist.values())
    mean_I = sum(k * v for k, v in agg.inv_hist.items()) / n_samples
    p_emp = agg.assigned / agg.puts
    mean_d = agg.d_sum / max(1, agg.assigned)
    periods_per_path = n_samples / P.paths
    exits_per_period = agg.exits / n_samples
    eff_qp = exits_per_period / mean_I if mean_I > 0 else float("nan")
    run_emp = (agg.prem_put + agg.prem_call) / agg.puts
    div_emp = agg.dividends / agg.puts
    cap_emp = agg.cap_sum / agg.cap_n
    mvcap_emp = agg.mvcap_sum / agg.cap_n
    ann = (run_emp + div_emp) / P.cadence
    excess = (ann - P.r * cap_emp) / cap_emp

    ref_p = f"   (model {M['p_real']:.3f})" if M else ""
    ref_d = f"   (model {M['E[d]']:.3f})" if M else ""
    print("\n-- Simulated (layered system on the common path) --")
    print(f"  assignment rate = {p_emp:.3f}{ref_p}")
    print(f"  mean d at assignment = {mean_d:.3f}{ref_d}")
    print(f"  mean inventory  = {mean_I:.2f}")
    pi0_emp = agg.inv_hist[0] / n_samples
    print(f"  P(I=0)          = {pi0_emp:.3f}   "
          f"(Poisson at same mean {exp(-mean_I):.3f})")
    var_I = sum((k - mean_I) ** 2 * v for k, v in agg.inv_hist.items()) / n_samples
    print(f"  Var(I)/Mean(I)  = {var_I / mean_I:.2f}   (Poisson: 1.00)")
    print(f"  effective q_p   = {eff_qp:.3f}")
    print(f"  run rate/period = {run_emp:.4f}")
    if P.delta:
        print(f"  dividends/period= {div_emp:.4f}")
    print(f"  capital (cost)  = {cap_emp:.2f}   Track A: margin + basis paid")
    print(f"  capital (market)= {mvcap_emp:.2f}   Track B: margin + market value")
    print(f"  annualized: income {ann:.3f} "
          f"(premiums {run_emp / P.cadence:.3f} + dividends {div_emp / P.cadence:.3f}), "
          f"excess over risk-free {excess:+.3f}/yr on COST-BASIS capital "
          f"(the Track A cash view; the economic ledger is --scenario validate)")

    completed = sorted(m for m, c in agg.durations if c)
    censored = [m for m, c in agg.durations if not c]
    print("\n-- Holding times --")
    print(f"  lots: {len(agg.durations)} total, {len(completed)} completed, "
          f"{len(censored)} censored at horizon")
    if completed:
        med = completed[len(completed) // 2]
        p90 = completed[int(len(completed) * 0.9)]
        print(f"  completed: median {med:.1f} mo, p90 {p90:.1f} mo, max {completed[-1]:.1f} mo")
    surv = km_survival(agg.durations, KM_HORIZONS_M)
    hdr = "".join(f"{h:>7}" for h in KM_HORIZONS_M)
    row = "".join(f"{s:>7.3f}" for s in surv)
    print(f"  KM survival (months):{hdr}\n"
          f"                       {row}")
    if agg.exits:
        tot = sum(agg.period_hist.values())
        shares = "  ".join(f"{j}: {agg.period_hist[j] / tot:.3f}"
                           for j in range(1, 7))
        tail = sum(v for k_, v in agg.period_hist.items() if k_ > 6) / tot
        print(f"  call periods per completed lot:\n"
              f"    {shares}  >6: {tail:.3f}")

    if len(P.regimes) == 1:
        print("\n-- Depth structure of call periods (x = ln(K_c/S) at call sale) --")
        print("    bin           lot-periods   exit rate   q(x) theory   mean x")
        for lo, hi, b in zip(DEPTH_EDGES, DEPTH_EDGES[1:], agg.bins):
            if b[0] == 0:
                continue
            hi_s = f"{hi:.2f}" if hi != float("inf") else " inf"
            print(f"    [{lo:.2f},{hi_s})   {b[0]:>9}      {b[1] / b[0]:.3f}       "
                  f"{b[2] / b[0]:.3f}        {b[3] / b[0]:.3f}")
        tot_per = sum(b[0] for b in agg.bins)
        mean_q_inv = sum(b[2] for b in agg.bins) / tot_per
        mean_x = sum(b[3] for b in agg.bins) / tot_per
        print(f"  inventory-weighted mean q(x) = {mean_q_inv:.3f}")
        print(f"  inventory-weighted mean depth = {mean_x:.3f}  vs  entry depth "
              f"E[x0] = {M['E[x0]']:.3f}")

    multi = sum(v for k_, v in agg.batch_hist.items() if k_ >= 2)
    tot_ev = sum(agg.batch_hist.values())
    if tot_ev:
        mx = max(agg.batch_hist)
        print("\n-- Exit clustering (lots called away on the same date) --")
        print(f"  exit dates: {tot_ev}; with >=2 simultaneous exits: "
              f"{multi / tot_ev:.3f}; largest batch: {mx}")


def report_time_profile(P, agg, checkpoints):
    """Both capital tracks over time, and the paper loss that is their gap.

    Track B moves with the lot count by construction, so through a crash it
    is the cost-basis row that runs away and the gap that carries the story.
    """
    print("\n-- Time profile (mean over paths) --")
    print("    t(y)   mean I   capital (market)   capital (cost)   paper loss")
    for y in checkpoints:
        idx = round(y / P.cadence)
        if agg.n_by_idx[idx] == 0:
            continue
        n_ = agg.n_by_idx[idx]
        mv = agg.mvcap_by_idx[idx] / n_
        cost = agg.cap_by_idx[idx] / n_
        print(f"   {y:>5.2f}   {agg.inv_by_idx[idx] / n_:>6.2f}   "
              f"{mv:>16.2f}   {cost:>14.2f}   {cost - mv:>10.2f}")


# ----------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------

def _sweep_row(P):
    """One row of the dividend sweep: its own simulation.  A pmap worker.

    Each row seeds its own generator from P.seed, so the row is the same
    whether the sweep runs on one core or on all of them.
    """
    agg = simulate(P)
    n_samples = sum(agg.inv_hist.values())
    mean_I = sum(k * v for k, v in agg.inv_hist.items()) / n_samples
    cap = agg.cap_sum / agg.cap_n          # Track A, cost basis
    mvcap = agg.mvcap_sum / agg.cap_n      # Track B, market value
    prem = (agg.prem_put + agg.prem_call) / agg.puts
    div = agg.dividends / agg.puts
    excess = ((prem + div) / P.cadence - P.r * cap) / cap
    return mean_I, mvcap, cap, prem, div, excess


def dividend_sweep(args):
    """Carry-vs-recovery trade-off: sweep the gross yield at fixed total return.

    The 'alt' row holds the PRICE drift at 7% instead (total return 9.5%) --
    the convention we argue against, included as a sensitivity check.
    """
    print("\n" + "=" * 72)
    print("Dividend sweep (30y, total-return convention, withholding 15%)")
    print("=" * 72)
    print("     delta     nu   mean I   cap(mkt)  cap(cost)   prem/T   div/T"
          "   excess/yr")
    rows = [("0.0%", 0.07, 0.000), ("1.0%", 0.07, 0.010), ("2.5%", 0.07, 0.025),
            ("4.0%", 0.07, 0.040), ("6.0%", 0.07, 0.060), ("alt 2.5%", 0.095, 0.025)]
    params = [Params(years=30.0, paths=args.paths or 200, seed=args.seed,
                     mu=mu, delta=delta) for _, mu, delta in rows]
    for (label, mu, delta), P, r in zip(rows, params, pmap(_sweep_row, params)):
        mean_I, mvcap, cap, prem, div, excess = r
        nu = mu - delta - P.sigma**2 / 2
        print(f"  {label:>8} {nu:+.3f}   {mean_I:>6.2f}   "
              f"{mvcap:>8.2f}  {cap:>9.2f}   {prem:.4f}  {div:.4f}   "
              f"{excess:+.4f}")
    print("  (capital: Track B market value and Track A cost basis; the excess")
    print("   is the Track A cash view, charged against cost basis)")
    print("  (alt row: price drift held at 7%, i.e. total return 9.5% -- the")
    print("   stacked convention, shown as a sensitivity check only)")


# ----------------------------------------------------------------------
# The constrained account
# ----------------------------------------------------------------------

def _fmt_years(t):
    return "never" if t == float("inf") else f"{t:.1f}y"


def _mean_se(xs):
    """Sample mean and the standard error of that mean."""
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n < 2:
        return m, float("nan")
    return m, sqrt(sum((x - m) ** 2 for x in xs) / (n - 1) / n)


def _time_to_mean_inventory(agg, cadence, target):
    """When the mean inventory curve first reaches `target` lots.

    Linear between cadence dates, matching model.py's own convention: the
    walk holds a lot at one depth for a whole period, so E[I(t)] is piecewise
    linear and interpolating inside a period is the model's continuum rather
    than a smoothing of it.
    """
    prev_t = prev_v = 0.0
    for idx in sorted(agg.n_by_idx):
        v = agg.inv_by_idx[idx] / agg.n_by_idx[idx]
        tt = idx * cadence
        if v >= target:
            return tt if v == prev_v else \
                prev_t + (tt - prev_t) * (target - prev_v) / (v - prev_v)
        prev_t, prev_v = tt, v
    return float("inf")


def survival_rows(agg, nu, sigma, horizons):
    """The paired survival comparison, one row per horizon.

    Three numbers on the same paths and the same price draws.  The closed form
    is evaluated at each path's OWN barrier distance, because integer lots
    leave realized leverage a little below the stopping rule's; the frozen
    barrier is that same statement measured rather than computed, and its
    agreement is the test of the ledger, the bridge and the price machinery
    together; and the operating book is the answer, differing from the frozen
    one only by what the wheel itself does to the debit.  ("Operating" against
    "frozen", never "live": in the article "the live account" is the author's
    real brokerage account, which none of this touches.)
    """
    from model import first_passage_prob
    rows = []
    for H in horizons:
        stat, dyn, closed, corr, err = [], [], [], [], []
        for a, w, ld, ls in zip(agg.a_sat, agg.window, agg.liq_dyn, agg.liq_stat):
            if w < H:
                continue               # the window has not run its course
            p = first_passage_prob(a, nu, sigma, H) if a < float("inf") else 0.0
            s, d = 1.0 if ls <= H else 0.0, 1.0 if ld <= H else 0.0
            stat.append(s)
            dyn.append(d)
            closed.append(p)
            corr.append(d - s)
            err.append(s - p)
        rows.append((H, len(stat), _mean_se(closed), _mean_se(stat),
                     _mean_se(dyn), _mean_se(corr), _mean_se(err)))
    return rows


def analytic_inventory(C, occ, lam, dates):
    """E[I(t)] on the unconstrained transient curve, at the given dates.

    lam*tau_c*sum_{j: j*tau_c < t} S_j, linear inside the period, which is the
    same convention model.time_to_inventory inverts -- so the simulator's
    filling-up curve is compared against the very object T_sat comes from.
    """
    out = []
    for t in dates:
        j = int(t / C.tau_c)
        acc = sum(occ["surv"][:j])
        if j < len(occ["surv"]):
            acc += occ["surv"][j] * (t / C.tau_c - j)
        out.append(lam * C.tau_c * acc)
    return out


def _run_totals(agg, P):
    """Mean inventory and income per year over a whole run.

    Time lived is counted in cadence dates rather than in paths x years, so a
    path that was liquidated contributes only the years it was alive -- which
    is what makes the constrained and unconstrained columns comparable.
    """
    n = sum(agg.n_by_idx.values())
    if n == 0:
        return float("nan"), float("nan")
    lived = n * P.cadence
    income = agg.prem_put + agg.prem_call + agg.dividends
    return sum(agg.inv_by_idx.values()) / n, income / lived


def _census_shares(bins):
    tot = sum(b[0] for b in bins)
    if tot == 0:
        return None, None, 0
    return ([b[0] / tot for b in bins],
            sum(b[3] for b in bins) / tot, tot)


def report_constrained(P, agg, ctl, ref, name):
    """Everything the finite account has to say, in the order it happens.

    `ctl` is the SAME simulator run with unlimited equity, on the same seed:
    the control that separates what blocking does from what a thirty-year
    window does.  Comparing a constrained run straight against the stationary
    census would charge blocking with the whole of the transient.
    """
    import model
    C = as_config(P)
    crit = model.criteria(C, "P")
    line = "=" * 78
    g_nom = P.nominal_g()
    print(f"\n{line}\nCONSTRAINED: {name}\n"
          f"  ({agg.paths} paths x {P.years:g}y, seed {P.seed}, "
          f"gamma_s={P.gamma_s:g}, u*={P.u_star:.4f}, r_b={P.r_b:.2%}, "
          f"draw '{P.draw}')\n{line}")
    print("\n-- what model.py says, for reference --")
    print(f"   L = {ref['L_max']:.4f}   capacity = {ref['capacity']:.2f} lots"
          f"   A* = {ref['A*']:.2f}   E[I(inf)] = {ref['I_inf']:.2f}"
          f"   E[W] = {ref['E[W]']:.2f}y"
          f"   [survivable at eps={ref['eps']:.0%}: {ref['L_surv']:.4f}]")
    print(f"   throughput A/A* = {ref['throughput']:.1%}   "
          f"T_sat = {_fmt_years(ref['T_sat'])}   f* = {ref['f*']:.4f} "
          f"(a drawdown of {1 - ref['f*']:.0%})")

    print("\n-- filling up --")
    if ctl is not None:
        t_free = _time_to_mean_inventory(ctl, P.cadence, ref["capacity"])
        print(f"   T_sat, unlimited equity reaching {ref['capacity']:.2f} lots:"
              f"  sim {_fmt_years(t_free)}   analytic {_fmt_years(ref['T_sat'])}")
    if agg.sat_times:
        st = sorted(agg.sat_times)
        print(f"   the constrained account is refused a put on "
              f"{len(st) / agg.paths:.1%} of paths, median {st[len(st) // 2]:.1f}y"
              f", p10 {st[int(0.1 * len(st))]:.1f}y")
        print(f"   -- earlier than T_sat, because a path fluctuates above its "
              f"own mean, and because lots are")
        print(f"      integers: the book stops at {int(ref['capacity'])} of a "
              f"capacity of {ref['capacity']:.2f}")
    else:
        print("   no path was ever refused a put")
    dates = [d for d in (2.0, 5.0, 10.0, 20.0, 30.0, 60.0) if d <= P.years]
    if dates and ctl is not None:
        ana = analytic_inventory(C, ref["occ"], ref["lambda"], dates)
        print(f"   mean I(t):  {'':>10}" + "".join(f"{d:>8.0f}y" for d in dates))
        for lbl, a in (("constrained", agg), ("unlimited", ctl)):
            cells = []
            for d in dates:
                idx = round(d / P.cadence)
                n_ = a.n_by_idx[idx]
                cells.append(f"{a.inv_by_idx[idx] / n_:>9.2f}" if n_ else f"{'-':>9}")
            print(f"   {lbl:>21}  " + "".join(cells))
        print(f"   {'analytic (unlim.)':>21}  " + "".join(f"{v:>9.2f}" for v in ana))
        cells = []
        for d in dates:
            idx = round(d / P.cadence)
            n_ = agg.n_by_idx[idx]
            n_ = agg.eqn_by_idx[idx]
            cells.append(f"{exp(agg.eq_by_idx[idx] / n_):>9.2f}" if n_
                         else f"{'-':>9}")
        print(f"   {'equity, in shares':>21}  " + "".join(cells)
              + f"   [started at {P.equity:.2f}]")

    alive = sum(1 for x in agg.t_liq if x == float("inf"))
    # agg.sales counts every cadence date reached alive, refused or not, and
    # agg.blocked is the subset refused -- so the denominator is sales alone.
    thr_all = 1 - agg.blocked / max(1, agg.sales)
    thr_ps = 1 - agg.ps_blocked / max(1, agg.ps_sales)
    print(f"\n-- uniform thinning, tested against the control over the same "
          f"{P.years:g} years --")
    print(f"   ({alive / max(1, len(agg.t_liq)):.0%} of paths survive the run,"
          f" and the rows below are conditional on that)")
    I_c, y_c = _run_totals(agg, P)
    I_u, y_u = _run_totals(ctl, P) if ctl is not None else (float("nan"),) * 2
    print(f"   {'':<26}{'constrained':>12} {'thinned ctl':>12} {'error':>9}"
          f" {'analytic':>10}")
    rows = [("throughput (puts sold)", thr_all, thr_all, ref["throughput"]),
            ("mean inventory, lots", I_c, thr_all * I_u, None),
            ("income per year", y_c, thr_all * y_u, ref["income"]),
            ("implied E[W] = I/lambda_eff",
             I_c / (ref["lambda"] * thr_all), I_u / ref["lambda"], ref["E[W]"])]
    for label, got, want, ana in rows:
        err = (got / want - 1.0) if want else float("nan")
        print(f"   {label:<26}{got:>12.3f} {want:>12.3f} {err:>+9.1%}"
              + (f" {ana:>10.3f}" if ana is not None else ""))
    print("   (thinning predicts the middle column: the constrained system is "
          "the unconstrained one")
    print("    scaled by lambda_eff/lambda, so inventory and income scale and "
          "E[W] does not move at all.")
    print("    The analytic column is the stationary frontier, which the run "
          "is too short to reach.)")

    print("\n-- the account itself, after the first refusal (time-weighted) --")
    if agg.ps_t > 0:
        print(f"   throughput {thr_ps:.1%}   mean inventory "
              f"{agg.ps_inv / agg.ps_t:.2f} of a capacity of "
              f"{ref['capacity']:.2f}   equity "
              f"{exp(agg.ps_eq / agg.ps_eqt) if agg.ps_eqt else float('nan'):.2f}"
              f" shares")
        print(f"   realized leverage {agg.ps_lev / agg.ps_t:.4f}, against the "
              f"stopping rule's {ref['L_max']:.4f}: a book that is refilled one"
              f" lot at a time")
        print(f"   sits below its own ceiling most of the time, and integer "
              f"lots keep it there.")
    g_mean, g_se = _mean_se(agg.g_real)
    r_mean, r_se = _mean_se(agg.r_drift)
    print(f"   realized debit growth g = {g_mean:+.4f} +-{g_se:.4f}/yr"
          + (f"   (assumed {g_nom:+.4f})" if g_nom is not None else
             "   (this policy pins no g in advance)")
          + f"   [{len(agg.g_real)} paths]")
    print(f"   realized drift of ln(M/D), which is what the barrier sees:"
          f" {r_mean:+.4f} +-{r_se:.4f}/yr"
          + (f"   (closed form: nu - g = {crit['nu'] - g_nom:+.4f})"
             if g_nom is not None else ""))
    e_mean, e_se = _mean_se(agg.e_drift)
    print(f"   realized drift of equity measured in SHARES: {e_mean:+.4f}"
          f" +-{e_se:.4f}/yr   (0 is the stationary account model.py prices)")

    print("\n-- survival from an EMPTY book: what the operator actually faces --")
    cells = []
    for H in sorted({10.0, 30.0, P.years}):
        if H > P.years:
            continue
        hit = sum(1 for x in agg.t_liq if x <= H)
        cells.append(f"{H:.0f}y {hit / max(1, len(agg.t_liq)):.4f}")
    print("   P(liquidated by)  " + "   ".join(cells)
          + f"   [{len(agg.t_liq)} paths]")
    print("   (an account borrows nothing while it fills, so those years are "
          "years it cannot be sold out in at all)")

    print("\n-- survival from FIRST SATURATION: what the closed form prices --")
    print(f"   {'H':>5} {'paths':>6} {'closed':>8} {'frozen (sim)':>17}"
          f" {'operating (sim)':>17} {'operating-frozen':>17}"
          f" {'frozen - closed':>17}")
    for H, n, cl, st, dy, co, er in survival_rows(
            agg, crit["nu"], P.sigma, (5.0, 10.0, 30.0)):
        if n == 0:
            print(f"   {H:>4.0f}y {n:>6}    (no path has a window that long)")
            continue
        print(f"   {H:>4.0f}y {n:>6} {cl[0]:>8.4f} {st[0]:>10.4f} +-{st[1]:.4f}"
              f" {dy[0]:>10.4f} +-{dy[1]:.4f}"
              f" {co[0]:>+10.4f} +-{co[1]:.4f}"
              f" {er[0]:>+10.4f} +-{er[1]:.4f}")
    print("   (frozen = the barrier as it stood at saturation with the price "
          "alone moving it, which is model.py's")
    print("    assumption measured rather than computed; operating = the "
          "account's own barrier.  Same paths, same draws.)")

    print("\n-- the census: is a blocked book the unconstrained one, thinned? --")
    sh_fin, x_fin, _ = model.depth_census(C, "P", DEPTH_EDGES, horizon=P.years)
    _, x_st, _ = model.depth_census(C, "P", DEPTH_EDGES)
    sh_ctl, x_ctl, n_ctl = _census_shares(ctl.bins) if ctl is not None \
        else (None, None, 0)
    sh_c, x_c, n_c = _census_shares(agg.bins)
    sh_ps, x_ps, n_ps = _census_shares(agg.bins_ps)
    if n_c == 0:
        print("   no lot-periods to census")
        return
    print(f"   {'bin':>14} {'analytic':>9} {'unlimited':>10} {'constrained':>12}"
          f" {'...saturated':>13} {'sat - unlim':>12}")
    for i, (lo, hi) in enumerate(zip(DEPTH_EDGES, DEPTH_EDGES[1:])):
        hi_s = f"{hi:.2f}" if hi != float("inf") else " inf"
        u = sh_ctl[i] if sh_ctl else float("nan")
        print(f"   [{lo:.2f},{hi_s})   {sh_fin[i]:>9.4f} {u:>10.4f}"
              f" {sh_c[i]:>12.4f} {sh_ps[i]:>13.4f} {sh_ps[i] - u:>+12.4f}")
    u = x_ctl if x_ctl is not None else float("nan")
    print(f"   {'mean depth':>14} {x_fin:>9.4f} {u:>10.4f} {x_c:>12.4f}"
          f" {x_ps:>13.4f} {x_ps - u:>+12.4f}")
    print(f"   [stationary census for scale: mean depth {x_st:.4f}; "
          f"lot-periods {n_ctl} unlimited, {n_c} constrained, {n_ps} saturated]")
    print("   (uniform thinning scales every bin by the same factor, so it "
          "predicts these shares UNCHANGED.")
    print("    The last column is therefore the thinning error, at a horizon "
          "the two columns share.)")


def constrained(args):
    """A finite account: what fills it, what it refuses, and what sells it out.

    The whole point is the pair of survival columns.  model.py prices a
    barrier that holds the book fixed and lets the price move; the wheel does
    three things to that barrier at once -- new assignments grow the debit
    during exactly the declines that threaten the account, premium income and
    called-away lots repay it, and capacity itself is marked to market so
    blocking tightens as the price falls -- and the net of the three is not
    obvious a priori.  Here it is measured, paired on a common price path.
    """
    import model
    eps, gs = args.eps, args.gamma_s
    C0 = model.Config(p_star=0.20, gamma_s=gs, label="Standard")
    far = model.stationary(C0, "P")
    econ = model.economics(C0, "P", far)
    L_max = model.max_leverage(C0, "P", eps)
    years = args.years or 60.0
    paths = args.paths or 2000
    # The draw that leaves equity compounding at the price drift, so that the
    # account is stationary in the lots model.py counts: the whole economic
    # return less what the stock itself supplies.  Derived, not tuned.
    w_stat = C0.r + econ["econ_excess"] - (C0.mu - C0.delta)

    # The control: the same simulator, the same seed, unlimited equity.  It is
    # what separates the effect of blocking from the effect of a finite window,
    # and it is also the only clean test of T_sat, which model.py computes off
    # the UNCONSTRAINED transient curve.
    ctl = simulate_batched(Params(delta=0.025, years=years, paths=paths,
                                  seed=args.seed))

    def run(A, L, draw, name, control=None, report=True):
        P = Params(delta=0.025, years=years, paths=paths, seed=args.seed,
                   gamma_s=gs, equity=A, u_star=gs * L, draw=draw,
                   draw_frac=w_stat)
        sat = model.saturation(C0, "P", far, eps, equity=A, econ=econ, L_max=L)
        ref = {"eps": eps, "L_max": L, "L_surv": L_max, "capacity": sat["capacity"],
               "A*": sat["A*"], "I_inf": econ["I"], "E[W]": econ["E[T]"],
               "throughput": sat["throughput"], "T_sat": sat["T_sat"],
               "f*": model.liquidation_barrier(L, gs),
               "income": sat["income"], "occ": far, "lambda": econ["lambda"]}
        agg = simulate_batched(P)
        if report:
            report_constrained(P, agg, control, ref, name)
        return P, agg

    # Two accounts, chosen for what each can settle.
    #
    # A_30 at the survivable stopping rule is the article's own case: the
    # model's 30-year capital, run under the leverage II-4 says carries a 10%
    # eventual risk.  It is where the census and the throughput mean something
    # -- and, as it turns out, where the barrier means nothing, because a
    # 1.13x rule and integer lots leave the account barely borrowing at all.
    #
    # A = 5 at L = 2 is the account that actually uses its margin: legal
    # (u = 0.50 against a broker's ceiling of 1) and far past survivable, so
    # the barrier is a 33% drawdown instead of an 84% one and the paired
    # estimator has something to measure.  It is the untended account of
    # II-13, in the one form that also blocks.
    A_30 = model.economics(C0, "P", model.occupation(C0, "P"),
                           horizon=30.0)["mv_capital"]
    # Every headline run takes the stationary draw, because that is the only
    # policy under which "the account sits at capacity" survives thirty years
    # of price drift -- and every frontier figure being tested here is a
    # statement about that steady state.
    base = run(A_30, L_max, "stationary",
               f"A = {A_30:.2f} lots, at the survivable stopping rule "
               f"L = {L_max:.4f}", control=ctl)
    run(5.0, 2.0, "stationary",
        "A = 5.00 lots, levered L = 2.00 (legal, and far past survivable)",
        control=ctl)

    # The cash policy, which II-15 found decides survival almost on its own:
    # servicing the interest holds the debit flat, withdrawing the income lets
    # it compound at r_b against a price whose median grows at nu, retaining
    # everything repays it, and the stationary draw is the one that keeps the
    # account the size model.py assumes.  Only two of the four pin a g in
    # advance; the others are measured against nothing, which is why they are
    # here.
    # It runs at the PRUDENT account, not the levered one: the columns below
    # are properties of a running account, and at L = 2 most paths are
    # liquidated inside the horizon, so every one of them would be measured on
    # the price-up survivors.  Here 88% survive.
    print("\n" + "=" * 78)
    print(f"CASH POLICY at A = {A_30:.2f} lots, L = {L_max:.4f}: what is done "
          f"with the income")
    print("=" * 78)
    # The horizon has to fit inside the run: a path that saturates at year 7
    # of a thirty-year run has no thirty-year window to be measured over.
    H_pol = min(30.0, years / 2)
    print(f"   {'policy':>10} {'g nominal':>9} {'g realized':>17}"
          f" {'d ln(E/S)':>10} {'thruput':>8} {'mean I':>7}"
          f" {f'P(liq|sat,{H_pol:.0f}y)':>14} {'frozen':>7}")
    for draw in DRAW_POLICIES:
        P, agg = base if draw == "stationary" else \
            run(A_30, L_max, draw, "", report=False)
        _, n, _, st, dy, _, _ = survival_rows(
            agg, model.criteria(as_config(P), "P")["nu"], P.sigma, (H_pol,))[0]
        gm, gse = _mean_se(agg.g_real)
        gn = P.nominal_g()
        print(f"   {draw:>10} {('%+.4f' % gn) if gn is not None else '--':>9}"
              f" {gm:>+10.4f} +-{gse:.4f} {_mean_se(agg.e_drift)[0]:>+10.4f}"
              f" {1 - agg.ps_blocked / max(1, agg.ps_sales):>8.1%}"
              f" {agg.ps_inv / agg.ps_t if agg.ps_t else float('nan'):>7.2f}"
              f" {dy[0]:>14.4f} {st[0]:>7.4f}")
    print("   ('frozen' is the same paths' static barrier, so the gap to "
          "P(liq) is what the wheel itself does;")
    print("    d ln(E/S) is the drift of equity in SHARES -- zero is the "
          "steady state the frontier prices)")


def validate(args):
    """Simulation vs. the analytic core, component by component."""
    import model
    for label, ps in (("Standard", 0.20), ("Conservative", 0.10)):
        P = Params(p_star=ps, delta=0.025, years=30.0,
                   paths=args.paths or 200, seed=args.seed)
        agg = simulate(P)
        C = as_config(P, label)
        occ = model.occupation(C, "P")
        a = model.economics(C, "P", occ, horizon=P.years)

        n_samples = sum(agg.inv_hist.values())
        per_yr = 1.0 / (agg.puts * P.cadence)
        sim = {
            "assignment rate": agg.assigned / agg.puts,
            "E[d]": agg.d_sum / max(1, agg.assigned),
            "E[I]": sum(k * v for k, v in agg.inv_hist.items()) / n_samples,
            "cost capital": agg.cap_sum / agg.cap_n,
            "market capital": agg.mvcap_sum / agg.cap_n,
            "premiums/yr": (agg.prem_put + agg.prem_call) * per_yr,
            "dividends/yr": agg.dividends / (agg.puts * P.cadence),
            "acq loss/yr": agg.acq_loss * per_yr,
            "call-away loss/yr": agg.giveaway * per_yr,
        }
        ana = {
            "assignment rate": a["p_real"], "E[d]": a["E[d]"], "E[I]": a["I"],
            "cost capital": a["capital"], "market capital": a["mv_capital"],
            "premiums/yr": a["premiums"], "dividends/yr": a["dividends"],
            "acq loss/yr": a["acq_loss"],
            "call-away loss/yr": a["call_away_loss"],
        }
        sim_pnl = (sim["premiums/yr"] + sim["dividends/yr"]
                   + sim["E[I]"] * (P.mu - P.delta)
                   - sim["acq loss/yr"] - sim["call-away loss/yr"])
        sim["economic excess/yr"] = ((sim_pnl - P.r * sim["market capital"])
                                     / sim["market capital"])
        ana["economic excess/yr"] = a["econ_excess"]

        print(f"\n{'=' * 72}\nVALIDATION: {label}  ({P.paths} paths x "
              f"{P.years:g}y, seed {P.seed})\n{'=' * 72}")
        print(f"{'quantity':>20} {'simulated':>12} {'analytic':>12} {'rel.diff':>10}")
        for key in sim:
            s, v = sim[key], ana[key]
            rel = (s - v) / abs(v) if v else float("nan")
            print(f"{key:>20} {s:>12.4f} {v:>12.4f} {rel:>+9.1%}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenario", default="all",
                    choices=["base", "dividends", "stress", "sweep",
                             "validate", "constrained", "all"])
    ap.add_argument("--paths", type=int, default=None)
    ap.add_argument("--seed", type=int, default=20260722)
    ap.add_argument("--years", type=float, default=None,
                    help="horizon for --scenario constrained (default 60)")
    ap.add_argument("--gamma-s", dest="gamma_s", type=float, default=0.25,
                    help="equity required against held shares (0.25 = PM)")
    ap.add_argument("--eps", type=float, default=0.10,
                    help="tolerance for eventual liquidation, setting u*")
    args = ap.parse_args()

    if args.scenario == "validate":
        validate(args)
        return

    if args.scenario == "constrained":
        constrained(args)
        return

    if args.scenario in ("base", "all"):
        P = Params(years=30.0, paths=args.paths or 200, seed=args.seed)
        report(P, simulate(P), "base (article running example: p*=20%, weekly puts / 4-week calls)")

    if args.scenario in ("dividends", "all"):
        P = Params(years=30.0, paths=args.paths or 200, seed=args.seed, delta=0.025)
        report(P, simulate(P), "base + dividends (delta=2.5%, total-return convention)")

    if args.scenario in ("sweep", "all"):
        dividend_sweep(args)

    if args.scenario in ("stress", "all"):
        # Crash-then-flatline: 2y calm, 3-month crash (expected log-drop 30%),
        # 3y flatline (mu=0), then calm again. IV assumed to track regime sigma,
        # so the p* strike policy responds to the vol spike (k* drops).
        P = Params(
            years=10.0, paths=args.paths or 300, seed=args.seed,
            regimes=[
                Regime(0.00, 0.07, 0.20),
                Regime(2.00, log(0.7) / 0.25, 0.35),
                Regime(2.25, 0.00, 0.20),
                Regime(5.25, 0.07, 0.20),
            ],
        )
        agg = simulate(P)
        report(P, agg, "crash-then-flatline stress")
        report_time_profile(
            P, agg,
            [1.0, 2.0, 2.25, 2.5, 3.0, 4.0, 5.0, 5.25, 6.0, 7.0, 8.0, 10.0])

    if args.scenario == "all":
        constrained(args)


if __name__ == "__main__":
    main()
