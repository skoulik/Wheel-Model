"""Monte Carlo simulator of the wheel, and the independent check on model.py.

Simulates the exact mechanics of Parts I-II on a common GBM price path, with
each lot's call strike frozen at its entry level: a put sold on the cadence
grid, assignment when it finishes in the money, and a covered call rewritten
every tau_c until the lot is called away. None of the analytic machinery is
used here -- the depth walk, the first passage and Little's law of `model.py`
are what this is meant to test -- so agreement between the two is evidence
rather than arithmetic.

`--scenario validate` is that comparison, component by component, from the
assignment rate through to the economic excess return. `--scenario dollars`
books the same paths' two exit flows in dollars per period beside the ledger's
convention and sets both against the book's own delta (TODO II-34). The other
scenarios are exploratory, and show what the analytic core cannot:

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

`--scenario stochvol` lets the volatility move, which model.py cannot: one
sigma is what makes a lot's depth a complete description of its prospects, and
the whole analytic spine rests on it (drafts/2026-11-20-published-betas-plan.md).
The log of the volatility mean-reverts with the S&P 500's measured swings,
around a level that keeps E[sigma^2] at sigma^2, and options are struck and
priced at the volatility ruling on the day they are sold.  It reports the
book's split and plain betas, its inventory and its time in the window, beside
the same run at constant sigma, which must agree with model.py.  The default
sv_eta = 0 keeps no state and draws nothing, so every other scenario is
byte-identical with it present.

`--scenario fittedvol` runs the process fitted on the Aristocrats instead (TODO
II-40, step 5; volprocess.py): two factors of log volatility moved only by the
stock's own moves, a kick on down jumps, Kou jumps and an earnings jump every
13 weeks, stepped a session at a time.  Puts are struck at the dial as a
real-world probability at the state and every option is priced fair there,
from fairprice.py's tables, so both exact tests hold with the volatility
moving: at the pricing drift the excess is minus the leak, and in the real
world it is the book's delta times mu - r less the leak, each option's delta
taken through the price and through the volatility the price moves.  Off
(Params.vol_fitted False), nothing is kept and nothing is drawn.

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

Stdlib only, but for fittedvol's tables, which fairprice.py builds with numpy.
Run:  python code/wheel_sim.py
    [--scenario base|dividends|stress|sweep|validate|dollars|constrained|stochvol|
                fittedvol|earnterm|magnitudes|all]
"""

import argparse
import heapq
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from math import exp, log, pi, sqrt

from model import (Config, N, bs_call, bs_put, entry_law, expected_drop,
                   k_star_drift, pmap)
import random
import volprocess as VP

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
    book_delta: bool = False   # sample the book's delta (--scenario dollars)
    # -- changing volatility (--scenario stochvol).  sv_eta = 0 is the constant
    # sigma of Parts I and II, and inertly so: no state is kept and no draw is
    # made, so every other scenario runs the same stream as before.  With
    # sv_eta > 0 the log of the volatility mean-reverts (Ornstein-Uhlenbeck)
    # around a level set so that E[sigma_t^2] = sigma^2, the article's one
    # volatility on average: the price's long-run variance and drift are
    # unchanged, and only how the variance is spread over time differs.
    sv_eta: float = 0.0        # volatility of log-volatility, per sqrt(year)
    sv_half_life: float = 1.9 / 12   # years for a log-vol deviation to halve
    sv_rho: float = 0.0        # correlation of the price's and the log-vol's shocks
    sv_step: float = 1 / 252   # largest step the joint path is advanced by
    # -- the fitted process (--scenario fittedvol, TODO II-40 step 5): two factors of
    # log volatility moved by the stock's own moves, jumps and earnings, from
    # volprocess.py, stepped a session at a time; options struck and priced fair at the
    # state, from fairprice.py's tables.  Off, nothing is kept and nothing is drawn.
    vol_fitted: bool = False
    vol_jumps: bool = True     # the unscheduled jumps (and so the down-jump kick)
    vol_earnings: bool = True  # the earnings jump, every 13 weeks
    vol_earn_feedback: tuple = None  # (c0, c1): an earnings term in h, to measure its cost
    record_gaps: bool = False  # keep each assignment's gap 1 - S/K (d's tail)

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
        self.sv_kappa = log(2) / self.sv_half_life
        self.sv_var = self.sv_eta**2 / (2 * self.sv_kappa)   # stationary var of log-vol
        if self.sv_eta > 0 and (len(self.regimes) > 1 or self.equity != float("inf")):
            raise ValueError("changing volatility is single-regime and unconstrained only")
        if self.vol_fitted:
            if len(self.regimes) > 1 or self.equity != float("inf") or self.sv_eta > 0:
                raise ValueError("the fitted process is single-regime and unconstrained")
            if (round(self.tau_p * VP.SESSIONS) != 5 or self.n != 4
                    or abs(self.cadence - self.tau_p) > 1e-12):
                raise ValueError("the fitted process's tables are for a weekly put sold "
                                 "every week and a four-week call")

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
    __slots__ = ("entry", "strike", "basis", "x", "periods", "s_sale", "t_exp",
                 "c_sale")

    def __init__(self, entry, strike, basis):
        self.entry = entry
        self.strike = strike
        self.basis = basis
        self.x = 0.0        # depth ln(K_c/S) at the current call's sale
        self.periods = 0    # call periods run so far
        self.s_sale = 0.0   # the price the current call was sold at
        self.t_exp = 0.0    # ...and when it expires
        self.c_sale = 0.0   # ...and the premium it was sold for


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
        # The same two exit flows in dollars per period: measured against the
        # price the option was sold at, not the price at exit (TODO II-34).
        self.acq_loss_d = 0.0
        self.giveaway_d = 0.0
        # The account's cash at r (TODO II-35): each premium from its sale
        # until its option expires or the run ends, and the put's collateral
        # while the put is live.  Spot-normalized at the sale, as the premium.
        self.prem_float = 0.0
        self.coll_int = 0.0
        # Lot-years held over the window: inventory as a time average, which is
        # what model.py's horizon figures are.  The census sampled at sale
        # dates counts both of a run's end dates, overweighting its last week.
        self.lot_time = 0.0
        # Options still open when the run ends, marked to market there: the
        # run's last puts and every standing lot's call.  Booked with the exits
        # they stand in for, so a window that closes mid-option counts its
        # cost as well as its premium.
        self.open_put = 0.0
        self.open_call = 0.0
        # The book's delta in shares, summed over the same dates as the
        # capital; only with Params.book_delta, since it prices every lot's call.
        self.delta_sum = 0.0
        # The put's strike over spot, summed over put sales: its margin's average when
        # the strike moves with the state (the fitted process).
        self.kf_sum = 0.0
        # The book's delta through the price's channel alone, beside delta_sum: equal to
        # it at constant sigma; under the fitted process the difference is the volatility
        # channel's share, measured on the same dates without noise of its own.
        self.delta_px_sum = 0.0
        self.gaps = []             # 1 - S/K at each assignment, with Params.record_gaps
        # Why a lot leaves when it does, under a changing volatility: the
        # volatility at its assignment over that at its put's sale, summed
        # over assignments, and how many lots reached their first call
        # expiry and how many left there.
        self.vol_rise = 0.0
        self.first_n = 0
        self.first_exit = 0
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
        # The split beta, measured as model.split_beta defines it: each lot over
        # one call period, its return against the stock's from the call's sale
        # to its expiry.  The lot's return includes the premium -- under one
        # volatility a level, which leaves the slope alone; under a changing one
        # it is not, which is the point of measuring it here.  Per side
        # [up, down, all]: [n, sum u, sum p, sum u^2, sum u*p].
        self.beta = [[0, 0.0, 0.0, 0.0, 0.0] for _ in range(3)]
        # ...and the same with the premium left out of the lot's return, which
        # separates what the premium does to the slope from what the cap at
        # the strike does.  Below its strike a lot is then the share exactly,
        # so this down-beta is 1 by identity.
        self.beta_ex = [[0, 0.0, 0.0, 0.0, 0.0] for _ in range(3)]
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

    def record_beta(self, u, p, p_ex):
        for side in ((0, 2) if u > 0 else (1, 2) if u < 0 else (2,)):
            for b, y in ((self.beta[side], p), (self.beta_ex[side], p_ex)):
                b[0] += 1
                b[1] += u
                b[2] += y
                b[3] += u * u
                b[4] += u * y

    def betas(self, premium=True):
        """(up, down, plain): least-squares slopes with an intercept, per side;
        with premium=False, of the lot's return without its call's premium."""
        out = []
        for n, su, sp, suu, sup in (self.beta if premium else self.beta_ex):
            var = suu / n - (su / n) ** 2 if n else 0.0
            out.append((sup / n - su / n * sp / n) / var if var > 0 else float("nan"))
        return tuple(out)

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
                "giveaway", "acq_loss_d", "giveaway_d", "prem_float", "coll_int", "lot_time",
                "open_put", "open_call", "delta_sum", "kf_sum", "delta_px_sum",
                "vol_rise", "first_n",
                "first_exit",
                "paths", "sales", "blocked", "withdrawn", "ps_t",
                "ps_inv", "ps_lev", "ps_eq", "ps_eqt", "ps_income", "ps_sales",
                "ps_blocked")
    _COUNTERS = ("inv_hist", "inv_by_idx", "eq_by_idx", "eqn_by_idx",
                 "cap_by_idx", "mvcap_by_idx", "n_by_idx", "period_hist",
                 "batch_hist")
    _LISTS = ("durations", "gaps", "t_liq", "sat_times", "a_sat", "window", "liq_dyn",
              "liq_stat", "g_real", "r_drift", "e_drift")

    def merge(self, o):
        """Absorb another Agg, so a run can be split over a process pool."""
        for k in self._SCALARS:
            setattr(self, k, getattr(self, k) + getattr(o, k))
        for k in self._COUNTERS:
            getattr(self, k).update(getattr(o, k))
        for k in self._LISTS:
            getattr(self, k).extend(getattr(o, k))
        for name in ("bins", "bins_ps", "beta", "beta_ex"):
            for a, b in zip(getattr(self, name), getattr(o, name)):
                for i in range(len(a)):
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


def advance_sv(S, h, t0, t1, P, rng):
    """The price and the log-volatility deviation h, stepped jointly to t1.

    The volatility is sigma_bar * e^h with sigma_bar = sigma * e^(-Var h), so
    E[sigma_t^2] = sigma^2.  h is an Ornstein-Uhlenbeck process, stepped
    exactly; the price is stepped as a lognormal at the volatility ruling at
    the start of each substep, which is exact in the limit of the step and
    within the simulator's resolution at a trading day.  The two shocks are
    correlated rho: negative rho is the leverage effect, volatility rising as
    the price falls.
    """
    if t1 - t0 <= 1e-12:
        return S, h
    rg = P.regimes[0]
    k = max(1, int((t1 - t0) / P.sv_step + 1 - 1e-9))
    dt = (t1 - t0) / k
    sig_bar = rg.sigma * exp(-P.sv_var)
    decay = exp(-P.sv_kappa * dt)
    h_sd = sqrt(P.sv_var * (1 - decay * decay))
    rho, rho_c = P.sv_rho, sqrt(1 - P.sv_rho**2)
    for _ in range(k):
        s = sig_bar * exp(h)
        z1, z2 = rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)
        S *= exp((rg.mu - P.delta - s * s / 2) * dt + s * sqrt(dt) * z1)
        h = h * decay + h_sd * (rho * z1 + rho_c * z2)
    return S, h


_FITTED = {}


def fitted_parts(P):
    """(volprocess.Process, volprocess.Tables) for a fitted-process run, built or loaded
    once per process.  Build them in the parent before a pool runs (fittedvol does), or
    every worker would build the same tables at once."""
    key = (P.sigma, P.mu, P.r, P.delta, P.p_star, P.vol_jumps, P.vol_earnings,
           P.vol_earn_feedback)
    if key not in _FITTED:
        # One set at a time: a pool worker running many cases would otherwise hold every
        # set it met, about a hundred megabytes each as Python lists, and step 7's run was
        # stopped for want of memory that way (2026-11-22). A reload is a second or two.
        _FITTED.clear()
        import fairprice
        data = fairprice.load({"sigma": P.sigma, "mu": P.mu, "r": P.r, "delta": P.delta,
                               "p_star": P.p_star, "jumps": P.vol_jumps,
                               "earnings": P.vol_earnings})
        T = VP.Tables(data)
        # The tables do not know the earnings term: with it on, options are priced as if it
        # were off, which the scenario that switches it on reads paired to cancel.
        _FITTED[key] = (VP.Process(T.sig_bar, P.vol_jumps, P.vol_earnings,
                                   earn_feedback=P.vol_earn_feedback), T)
    return _FITTED[key]


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


def run_path(P, rng, agg, states=None):
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

    # ---- changing volatility.  Off, nothing is kept and nothing is drawn.
    sv = P.sv_eta > 0
    h = rng.gauss(0.0, sqrt(P.sv_var)) if sv else 0.0   # started stationary
    sig_now = P.regimes[0].sigma * exp(h - P.sv_var) if sv else P.regimes[0].sigma
    # ---- the fitted process.  Off, nothing is kept and nothing is drawn.
    fv = P.vol_fitted
    if fv:
        proc, tables = fitted_parts(P)
        # The path, stepped beforehand with its batch (fairprice.path_states, TODO INF-9):
        # read at the weekly events, from the stationary state, with its earnings calendar.
        st, i_ = states
        w_logS, w_hf, w_hs = (st[k][:, i_].tolist() for k in ("logS", "hf", "hs"))
        e0 = int(st["e0"][i_])
        hf, hs = w_hf[0], w_hs[0]
        n_now = 0                           # sessions stepped so far
        sig_now = proc.annual_vol(hf, hs)

        def phase(sessions):
            """The session of an option's life its earnings date falls on, or 0."""
            j = (e0 - n_now) % VP.EARNINGS_EVERY + 1
            return j if j <= sessions else 0

        def eff_delta(strike, sessions):
            """A call's delta through both of its channels, in shares: the price's own
            (with the smile, since the depth moves with the price) and the volatility's,
            the vega times how far a one-sd diffusive shock moves each factor, per unit of
            the move it makes in the price.  The pricing measure shifts exactly that
            shock, so this is the exposure mu - r is earned on (decision 4); a put's is
            the call's less e^(-delta tau), by parity.  Returns (both channels, the
            price's alone)."""
            tau = sessions * VP.DT
            iv, d_f, d_s, d_x = tables.call_iv_grad(hf, hs, phase(sessions),
                                                    log(strike / S), sessions)
            iv += P.iv_spread
            sq = iv * sqrt(tau)
            d1 = (log(S / strike) + (P.r - P.delta + iv * iv / 2) * tau) / sq
            carry = exp(-P.delta * tau)
            vega = S * carry * exp(-d1 * d1 / 2) / sqrt(2 * pi) * sqrt(tau)
            H = max(-VP.H_CLIP, min(VP.H_CLIP, hf + hs))
            sd = proc.sig_bar * exp(H)
            price = carry * N(d1) - vega * d_x / S
            return price + (proc.th_f * d_f + proc.th_s * d_s) * vega / (sd * S), price

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

    pending = []                    # (expiry, premium) waiting to be withdrawn

    def earn(amount, expiry):
        """Book a premium.  It goes into the account on the day of sale and,
        under a policy that withdraws income, comes out when its option
        expires and the period's books close (TODO II-35): until then it is
        the account's cash, earning r on a credit balance and saving r_b on a
        debit.  Either way it is income, accumulated per unit of the spot
        RULING AT THE TIME, which is the normalization every figure in
        model.py is quoted in."""
        nonlocal cash
        if ledger:
            cash += amount
            if not keep_income:
                pending.append((expiry, amount))
            if t_sat is not None:
                agg.ps_income += amount / S

    while heap:
        te, prio, sq, data = heapq.heappop(heap)
        dt = min(te, P.years) - t
        div = len(lots) * P.delta_net * dt
        agg.dividends += div
        agg.lot_time += len(lots) * dt
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
            # Premiums whose options expire now leave the account, having
            # earned the interval's interest above.
            if pending:
                due = [a for e_, a in pending if e_ <= te + 1e-12]
                if due:
                    pending[:] = [(e_, a) for e_, a in pending if e_ > te + 1e-12]
                    cash -= sum(due)
                    agg.withdrawn += sum(due)
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
            heapq.heappush(heap, (te, prio, sq, data))   # still open: marked below
            break
        s_a = S
        sig_step = regime_at(P, t).sigma       # constrained runs are single-regime
        if sv:
            S, h = advance_sv(S, h, t, te, P, rng)
        elif fv:
            n_now = round(te * VP.SESSIONS)
            k_ = n_now // 5
            S, hf, hs = exp(w_logS[k_]), w_hf[k_], w_hs[k_]
        else:
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
                        pending.clear()          # sold out with the rest
                if shadow and bridge_hit(s_a, S, b_frozen, b_frozen, var, u):
                    t_stat = t
            # Nothing is left to learn from a dead path once its shadow has
            # resolved; until then the price alone is stepped on, which is all
            # the frozen barrier is a statement about.
            if dead and (t_stat < float("inf") or b_frozen <= 0.0):
                break

        rg = regime_at(P, t)
        # The volatility ruling now: the regime's, or the path's own when it
        # moves.  Strikes and premiums are both set at it, as an operator
        # quoting the day's volatility would.
        sig_now = (P.regimes[0].sigma * exp(h - P.sv_var) if sv
                   else proc.annual_vol(hf, hs) if fv else rg.sigma)
        sig_iv = sig_now + P.iv_spread

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
            if fv:
                # The dial is a real-world probability at the state, and the premium
                # the fair price there: both from the tables.
                kf, iv = tables.put(hf, hs, phase(5))
                sig_iv = iv + P.iv_spread
            else:
                kf = k_star_drift(P.p_star, P.tau_p, sig_now, rg.mu - P.delta)
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
                agg.kf_sum += kf
                agg.prem_put += c_p / S
                live = min(t + P.tau_p, P.years) - t
                agg.prem_float += c_p / S * (exp(P.r * live) - 1)
                agg.coll_int += P.r * P.gamma_p * kf * live
                earn(c_p, t + P.tau_p)
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
                if P.book_delta and fv:
                    # The same book, each option's delta through both channels, and
                    # through the price's alone.
                    book = book_px = 0.0
                    for lot in lots:
                        ell = round((lot.t_exp - t) * VP.SESSIONS)
                        if ell > 0:
                            full, px = eff_delta(lot.strike, ell)
                            book += 1.0 - full
                            book_px += 1.0 - px
                        else:
                            book += 0.0 if S >= lot.strike else 1.0
                            book_px += 0.0 if S >= lot.strike else 1.0
                    full, px = eff_delta(K, 5)
                    carry = exp(-P.delta * P.tau_p)
                    book -= full - carry
                    book_px -= px - carry
                    agg.delta_sum += book
                    agg.delta_px_sum += book_px
                elif P.book_delta:
                    # Shares, each less its call's spot delta at the call's
                    # remaining tenor, plus the short put just sold.
                    book = 0.0
                    for lot in lots:
                        tau = lot.t_exp - t
                        if tau > 1e-12:
                            d1 = ((log(S / lot.strike)
                                   + (P.r - P.delta + sig_iv**2 / 2) * tau)
                                  / (sig_iv * sqrt(tau)))
                            book += 1.0 - exp(-P.delta * tau) * N(d1)
                        else:
                            book += 0.0 if S >= lot.strike else 1.0
                    d1p = ((log(1.0 / kf) + (P.r - P.delta + sig_iv**2 / 2) * P.tau_p)
                           / (sig_iv * sqrt(P.tau_p)))
                    book += exp(-P.delta * P.tau_p) * N(-d1p)
                    agg.delta_sum += book
                    agg.delta_px_sum += book     # one channel: the price's
                push(t + P.tau_p, PUTEXP, (K, S, c_p, sig_now))
            if t + P.cadence <= P.years + 1e-9:
                push(t + P.cadence, SALE, None)

        elif prio == PUTEXP:
            if dead:
                continue
            K, S_sale, c_p, sig_sale = data
            if S < K:
                agg.assigned += 1
                agg.vol_rise += sig_now / sig_sale
                agg.d_sum += 1 - S / S_sale
                agg.acq_loss += (K - S) / S      # paid K for something worth S
                agg.acq_loss_d += (K - S) / S_sale   # ...per unit of the sale price
                if P.record_gaps:
                    agg.gaps.append(1 - S / K)
                lot = Lot(entry=t, strike=K, basis=K - c_p)
                lots.append(lot)
                if ledger:
                    cash -= K                    # this is what grows the debit
                # Sell the first covered call at the frozen strike.
                if fv:
                    sig_iv = tables.call_iv(hf, hs, phase(20), log(K / S)) + P.iv_spread
                c_c = bs_call(S, K, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                agg.prem_float += c_c / S * (exp(P.r * (min(t + P.tau_c, P.years) - t)) - 1)
                earn(c_c, t + P.tau_c)
                lot.x = log(K / S)
                lot.s_sale, lot.t_exp, lot.c_sale = S, t + P.tau_c, c_c
                push(t + P.tau_c, CALLEXP, lot)

        else:  # CALLEXP
            if dead:
                continue
            lot = data
            lot.periods += 1
            exited = S >= lot.strike
            if lot.periods == 1:
                agg.first_n += 1
                agg.first_exit += exited
            agg.record_beta(S / lot.s_sale - 1.0,
                            (min(S, lot.strike) + lot.c_sale) / lot.s_sale - 1.0,
                            min(S, lot.strike) / lot.s_sale - 1.0)
            agg.record_call_period(lot.x, exited, rg.mu - P.delta, rg.sigma,
                                   P.tau_c, t_sat is not None)
            if exited:
                agg.exits += 1
                agg.giveaway += (S - lot.strike) / S   # delivered below market
                agg.giveaway_d += (S - lot.strike) / lot.s_sale
                lots.remove(lot)
                if ledger:
                    cash += lot.strike           # ...and this is what repays it
                agg.durations.append((round((t - lot.entry) * 12, 6), True))
                agg.period_hist[lot.periods] += 1
                exits_at[round(t, 9)] += 1
            else:
                if fv:
                    sig_iv = (tables.call_iv(hf, hs, phase(20), log(lot.strike / S))
                              + P.iv_spread)
                c_c = bs_call(S, lot.strike, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                agg.prem_float += c_c / S * (exp(P.r * (min(t + P.tau_c, P.years) - t)) - 1)
                earn(c_c, t + P.tau_c)
                lot.x = log(lot.strike / S)
                lot.s_sale, lot.t_exp, lot.c_sale = S, t + P.tau_c, c_c
                push(t + P.tau_c, CALLEXP, lot)

    for lot in lots:  # censored at the horizon
        agg.durations.append((round((P.years - lot.entry) * 12, 6), False))
    if not dead:
        # Mark what is still open to market where the run ends, each against
        # the price it was sold at as its exit would have been.  No random
        # draw: every other scenario runs the same stream as before.
        sig_end = (sig_now if sv else regime_at(P, t).sigma) + P.iv_spread

        def mark_iv(strike, left):
            """The fitted process's volatility for an option with `left` years to run:
            the tables' call with that much of its life left, at its depth -- a put's by
            parity.  A window that does not end on a put sale leaves other remainders,
            and those take the four-week call with the earnings variance, if its date
            falls inside, spread over the time left: an approximation."""
            if not fv:
                return sig_end
            x = log(strike / S)
            ell = max(1, round(left * VP.SESSIONS))
            if ell in tables.call_lniv:
                return tables.call_iv(hf, hs, phase(ell), x, ell) + P.iv_spread
            iv0 = tables.call_iv(hf, hs, 0, x)
            j = phase(ell)
            if not j:
                return iv0 + P.iv_spread
            ivj = tables.call_iv(hf, hs, j, x)
            return (sqrt(max(iv0 * iv0 + (ivj * ivj - iv0 * iv0) * 20 / ell, 1e-8))
                    + P.iv_spread)

        for te, prio, _, data in heap:
            left = te - t
            if prio == PUTEXP:
                K, S_sale, c_sold, _ = data
                if fv and abs(left - P.tau_p) < 1e-9:
                    v = c_sold * S / S_sale      # sold at this close: worth its premium
                else:
                    v = S * bs_put(K / S, left, mark_iv(K, left), P.r, P.delta)
                agg.open_put += v / S_sale
                agg.acq_loss += v / S
                agg.acq_loss_d += v / S_sale
            elif prio == CALLEXP:
                v = bs_call(S, data.strike, left, mark_iv(data.strike, left), P.r,
                            P.delta)
                agg.open_call += v / data.s_sale
                agg.giveaway += v / S
                agg.giveaway_d += v / data.s_sale
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
    seed = P.seed if seed is None else seed
    rng = random.Random(seed)
    agg = Agg()
    n = P.paths if paths is None else paths
    states = None
    if P.vol_fitted:
        # The fitted process is stepped for the whole batch at once, in numpy: the wheel
        # never feeds back into the price (TODO INF-9).
        import fairprice
        proc, _ = fitted_parts(P)
        states = fairprice.path_states(proc, n, P.years, P.mu - P.delta, seed)
    for i in range(n):
        run_path(P, rng, agg, None if states is None else (states, i))
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
    """Simulation vs. the analytic core, component by component.

    `--years` sets the horizon (default 30).  A short one is where the two
    treatments of the window's edge are tested against each other: model.py
    gives a call's upside surrendered its premium's weights, and this marks
    the options open at the end to market, which agree to first order.
    """
    import model
    for label, ps in (("Standard", 0.20), ("Conservative", 0.10)):
        P = Params(p_star=ps, delta=0.025, years=args.years or 30.0,
                   paths=args.paths or 200, seed=args.seed)
        agg = simulate(P)
        C = as_config(P, label)
        occ = model.occupation(C, "P")
        a = model.economics(C, "P", occ, horizon=P.years)

        n_samples = sum(agg.inv_hist.values())
        # Per year of the window simulated.  Not puts*cadence: a run sells a
        # put on both of its end dates, one more than it has weeks, which
        # overstates the window by a week in its length -- 2% at one year.
        per_yr = 1.0 / (agg.paths * P.years)
        sim = {
            "assignment rate": agg.assigned / agg.puts,
            "E[d]": agg.d_sum / max(1, agg.assigned),
            "E[I]": agg.lot_time * per_yr,
            "cost capital": agg.cap_sum / agg.cap_n,
            "market capital": (P.gamma_p * k_star_drift(P.p_star, P.tau_p, P.sigma,
                                                        P.mu - P.delta)
                               + agg.lot_time * per_yr),
            "premiums/yr": (agg.prem_put + agg.prem_call) * per_yr,
            "dividends/yr": agg.dividends * per_yr,
            # In dollars per period, as model.economics books them: each exit
            # against the price its option was sold at (TODO II-34).
            "acq loss/yr": agg.acq_loss_d * per_yr,
            "call-away loss/yr": agg.giveaway_d * per_yr,
            # The account's cash at r (TODO II-35), and its two parts.
            "cash interest/yr": (agg.prem_float + agg.coll_int) * per_yr,
            "  premium float/yr": agg.prem_float * per_yr,
            "  collateral/yr": agg.coll_int * per_yr,
        }
        ana = {
            "assignment rate": a["p_real"], "E[d]": a["E[d]"], "E[I]": a["I"],
            "cost capital": a["capital"], "market capital": a["mv_capital"],
            "premiums/yr": a["premiums"], "dividends/yr": a["dividends"],
            "acq loss/yr": a["acq_loss"],
            "call-away loss/yr": a["call_away_loss"],
            "cash interest/yr": a["cash_interest"],
            "  premium float/yr": a["premium_float"],
            "  collateral/yr": a["collateral_interest"],
        }
        sim_pnl = (sim["premiums/yr"] + sim["dividends/yr"]
                   + sim["cash interest/yr"]
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


def _dollar_row(P, g):
    """One run's economic excess three ways, from an Agg sampled with book_delta.

    The ledger books the mark loss and the upside surrendered per unit of the
    price at exit, as model.economics did until TODO II-34; the dollar version
    per unit of the price the option was sold at, the capital the period
    started with, as it does now.
    Everything else -- premiums at sale, the account's cash at r, dividends and
    the appreciation E[I]*m per unit of the price ruling -- is the same in both.
    The theory row is Black-Scholes's: each instrument's expected excess return
    is its delta times the stock's, so the book earns its sampled delta times
    mu - r, less the withheld dividends.  The delta is sampled at every put sale
    across each call's life, so it is a life average, as book_delta_life()'s.
    """
    m = P.mu - P.delta
    per_yr = 1.0 / (g.paths * P.years)           # the window, as in validate()
    n = sum(g.inv_hist.values())
    inv = g.lot_time * per_yr                    # time-averaged, as model.py's
    kf = (g.kf_sum / g.puts if P.vol_fitted     # the strike moves with the state
          else k_star_drift(P.p_star, P.tau_p, P.sigma, m))
    cap = P.gamma_p * kf + inv
    income = (g.prem_put + g.prem_call + g.prem_float + g.coll_int
              + g.dividends) * per_yr
    base = income + inv * m - P.r * cap
    ledger = (base - (g.acq_loss + g.giveaway) * per_yr) / cap
    dollar = (base - (g.acq_loss_d + g.giveaway_d) * per_yr) / cap
    leak = inv * P.delta * P.withhold / cap
    delta = g.delta_sum / g.mvcap_sum             # per unit of the sampled capital
    theory = delta * (P.mu - P.r) - leak
    return {"ledger": ledger, "dollar": dollar, "theory": theory,
            "delta": delta, "dollar - theory": dollar - theory,
            "ledger - theory": ledger - theory}


def dollars(args):
    """Ledger against dollars per period, on simulated paths (TODO II-34).

    Three runs through one pool: Standard and Conservative in the real world,
    and Standard at the pricing drift mu = r, where no-arbitrage makes the
    dollar answer exact -- minus the leak, nothing else.
    Standard errors are across the batches each run is split into.
    """
    import model
    runs = (("Standard, real world", dict(p_star=0.20)),
            ("Conservative, real world", dict(p_star=0.10)),
            ("Standard, pricing drift mu = r", dict(p_star=0.20, mu=0.05)))
    paths = args.paths or 1600
    jobs, spans = [], []
    for label, kw in runs:
        P = Params(delta=0.025, years=args.years or 30.0, paths=paths,
                   seed=args.seed, book_delta=True, **kw)
        js = batch_jobs(P)
        spans.append((label, P, len(jobs), len(jobs) + len(js)))
        jobs += js
    aggs = pmap(_batch, jobs)
    for label, P, a, b in spans:
        rows = [_dollar_row(P, g) for g in aggs[a:b]]
        whole = _dollar_row(P, merge_all(aggs[a:b]))
        nb = len(rows)
        C = as_config(P, label)
        ana = model.economics(C, "P", model.occupation(C, "P"),
                              horizon=P.years)["econ_excess"]
        print(f"\n{'=' * 72}\nDOLLARS PER PERIOD: {label}  ({P.paths} paths x "
              f"{P.years:g}y in {nb} batches, seed {P.seed})\n{'=' * 72}")
        print(f"{'':>34} {'estimate':>10} {'s.e.':>9}")
        for key in ("ledger", "dollar", "theory", "dollar - theory",
                    "ledger - theory"):
            vals = [r[key] for r in rows]
            mean = sum(vals) / nb
            se = sqrt(sum((v - mean) ** 2 for v in vals) / (nb - 1) / nb)
            print(f"{key + ' excess' if ' ' not in key else key:>34} "
                  f"{whole[key]:>+10.3%} {se:>9.3%}")
        print(f"{'book delta / market-value capital':>34} {whole['delta']:>10.3f}")
        print(f"{'dollars, analytic (model.economics)':>34} {ana:>+10.3%}")


# The S&P 500's own volatility, measured from its daily total-return history
# 1988-2026 (drafts/2026-11-20-published-betas-plan.md): the log of monthly
# realized volatility has a standard deviation of about 0.50 and a half-life of
# about 1.9 months, and a month's return correlates about -0.4 with that
# month's change in it.  Borrowed for a single stock, at the running example's
# sigma, and the leverage correlation run at zero and near the index's (TODO
# II-38 checks the structure on single names).  rho = -0.9 is a daily
# correlation; in this process it gives a monthly one of about -0.34.
SV_SD_LOGVOL = 0.50
SV_HALF_LIFE = 1.9 / 12
SV_RHO_INDEX = -0.9


def _sv_row(P, g):
    """One run's betas, inventory and time in the window, from an Agg.

    Two figures say why the up-beta moves.  The up-beta with the premium left
    out isolates the cap at the strike from the premium's pairing with the
    size of the move; the spread of a rise -- the standard deviation of the
    stock's return over the call periods in which it rose -- says how far the
    rises reach, which is what decides how often they run through a strike.
    The share of call periods begun within 2% of the strike is the census's
    side of it: those are the lots a modest rise caps.

    Two more say why lots leave sooner when volatility moves.  The volatility
    at a lot's assignment over the volatility when its put was sold is how far
    the fall that assigned it raised volatility -- with the leverage effect,
    the lot meets turbulent weeks from a depth set in a calmer one -- and the
    share of lots leaving at their first call expiry is what that does."""
    up, dn, plain = g.betas()
    n, su, _, suu, _ = g.beta[0]
    periods = sum(b[0] for b in g.bins)
    inv = g.lot_time / (g.paths * P.years)
    lam = g.assigned / (g.paths * P.years)
    return {"up-beta": up, "down-beta": dn, "plain beta": plain,
            "up-beta, no premium": g.betas(premium=False)[0],
            "sd of a rise": sqrt(suu / n - (su / n) ** 2) if n else float("nan"),
            "within 2% of strike": g.bins[0][0] / periods if periods else float("nan"),
            "vol rise to assignment": g.vol_rise / g.assigned if g.assigned else float("nan"),
            "left at first expiry": g.first_exit / g.first_n if g.first_n else float("nan"),
            "E[I], lots": inv, "E[I]/lambda, years": inv / lam if lam else float("nan")}


def stochvol(args):
    """The wheel under changing volatility: its betas and holding time.

    Three runs through one pool, the Standard regime at thirty years: constant
    sigma, the reference that must agree with model.py; volatility swinging
    as the S&P 500's does but with no leverage effect; and with one near the
    index's.  Each holds E[sigma^2] at the running example's 20%, so the price's
    long-run drift and variance are the same in all three, and only how the
    variance is spread over time differs.  Standard errors are across the
    batches each run is split into.
    """
    import model
    eta = SV_SD_LOGVOL * sqrt(2 * log(2) / SV_HALF_LIFE)
    runs = (("constant volatility", dict()),
            ("changing volatility, no leverage effect",
             dict(sv_eta=eta, sv_half_life=SV_HALF_LIFE, sv_rho=0.0)),
            (f"changing volatility, leverage rho = {SV_RHO_INDEX}",
             dict(sv_eta=eta, sv_half_life=SV_HALF_LIFE, sv_rho=SV_RHO_INDEX)))
    paths = args.paths or 640
    jobs, spans = [], []
    for label, kw in runs:
        P = Params(delta=0.025, years=args.years or 30.0, paths=paths,
                   seed=args.seed, **kw)
        js = batch_jobs(P)
        spans.append((label, P, len(jobs), len(jobs) + len(js)))
        jobs += js
    aggs = pmap(_batch, jobs)
    P0 = spans[0][1]
    C = as_config(P0, "Standard")
    a = model.economics(C, "P", model.occupation(C, "P"), horizon=P0.years)
    up_m, dn_m = model.split_beta(C, "P", horizon=P0.years)
    ref = {"up-beta": up_m, "down-beta": dn_m, "up-beta, no premium": up_m,
           "E[I], lots": a["I"], "E[I]/lambda, years": a["I"] / (C.p_star / C.cadence)}
    print(f"\n{'=' * 72}\nCHANGING VOLATILITY  ({paths} paths x {P0.years:g}y per run, "
          f"seed {P0.seed})\n  log-vol: sd {SV_SD_LOGVOL}, half-life "
          f"{SV_HALF_LIFE * 12:.1f} months (eta {eta:.3f}); E[sigma^2] = "
          f"{P0.sigma:.2f}^2 in every run\n{'=' * 72}")
    keys = ("up-beta", "down-beta", "plain beta", "up-beta, no premium",
            "sd of a rise", "within 2% of strike", "vol rise to assignment",
            "left at first expiry", "E[I], lots", "E[I]/lambda, years")
    for label, P, i, j in spans:
        rows = [_sv_row(P, g) for g in aggs[i:j]]
        whole_agg = merge_all(aggs[i:j])
        whole = _sv_row(P, whole_agg)
        nb = len(rows)
        print(f"\n-- {label} --")
        for key in keys:
            vals = [r[key] for r in rows]
            mean = sum(vals) / nb
            se = sqrt(sum((v - mean) ** 2 for v in vals) / (nb - 1) / nb)
            m_ref = f"   model.py {ref[key]:.3f}" if key in ref else ""
            print(f"  {key:>20} {whole[key]:>8.3f}  s.e. {se:.3f}{m_ref}")
        surv = km_survival(whole_agg.durations, KM_HORIZONS_M)
        print(f"  KM survival, months {''.join(f'{h:>7}' for h in KM_HORIZONS_M)}\n"
              f"                       {''.join(f'{s:>7.3f}' for s in surv)}")
        # The exit rate per call period by depth below the strike at the
        # call's sale: where in the census lots leave sooner or later.
        print("  exit rate by depth  " + "".join(
            f"{f'{a:.2f}-':>7}" for a in DEPTH_EDGES[:-1]))
        print("                      " + "".join(
            f"{b[1] / b[0]:>7.4f}" if b[0] else f"{'-':>7}" for b in whole_agg.bins))
        med = next((h for h, s in zip(*_km_curve(whole_agg.durations)) if s <= 0.5),
                   float("nan"))
        print(f"  median holding time  {med:.2f} months")


def _fv_row(P, g):
    """One run's figures for --scenario fittedvol, from an Agg.

    The economic excess in dollars per period, as _dollar_row books it, with the put's
    margin at its average strike when the strike moves with the state; the leak; and
    their sum, which no-arbitrage makes zero at the pricing drift whatever the
    volatility does, provided every option is priced fair -- the test of the tables.
    Then _sv_row's betas and inventory, and d's tail: the gap 1 - S/K at assignment,
    whose mean has run about 2.3 times its median in the live account."""
    m = P.mu - P.delta
    per_yr = 1.0 / (g.paths * P.years)
    inv = g.lot_time * per_yr
    kf = (g.kf_sum / g.puts if P.vol_fitted
          else k_star_drift(P.p_star, P.tau_p, P.sigma, m))
    cap = P.gamma_p * kf + inv
    income = (g.prem_put + g.prem_call + g.prem_float + g.coll_int
              + g.dividends) * per_yr
    dollar = (income + inv * m - P.r * cap - (g.acq_loss_d + g.giveaway_d) * per_yr) / cap
    leak = inv * P.delta * P.withhold / cap
    row = {"excess": dollar, "minus the leak": -leak, "excess + leak": dollar + leak}
    if g.delta_sum:
        d = _dollar_row(P, g)
        d_px = g.delta_px_sum / g.mvcap_sum
        row.update({"delta x (mu - r) - leak": d["theory"],
                    "excess - that": d["dollar - theory"], "book delta": d["delta"],
                    "book delta, price only": d_px,
                    "excess - that, price only": d["dollar"] - (d_px * (P.mu - P.r)
                                                                - leak)})
    row.update(_sv_row(P, g))
    gaps = sorted(g.gaps)
    if gaps:
        n = len(gaps)
        mean, med = sum(gaps) / n, gaps[n // 2]
        row.update({"gap: mean": mean, "gap: median": med, "gap: mean/median": mean / med,
                    "gap > 5%": sum(1 for x in gaps if x > 0.05) / n,
                    "gap > 10%": sum(1 for x in gaps if x > 0.10) / n})
    return row


def fittedvol(args):
    """The wheel on the fitted process (TODO II-40, step 5), against constant sigma.

    Four runs through one pool, the Standard regime at thirty years: constant sigma and
    the fitted process, each at the real-world drift and at the pricing drift mu = r.
    At the pricing drift the excess plus the leak must be zero -- at constant sigma
    because Black-Scholes is exact there, on the fitted process only if the tables price
    every option fair, so that row is their test.  Standard errors are across batches.

    In the real world the excess must be the book's delta times mu - r, less the leak,
    and under the fitted process the delta has two channels, the price's and the
    volatility's the price moves; the price's alone is reported beside it.  Read on its
    own that test resolves about 1.7bp, which is the size of the volatility channel, so
    it is also read paired: each batch's pricing-drift run has the same draws (the price
    drift moves no random number) and its excess plus leak is zero by no-arbitrage, so
    subtracting it removes the noise the two runs share and leaves an estimate with the
    same expectation.  At 640 paths a run that one reads to about 0.7bp; --paths 5120
    (about 35 minutes) reads it to 0.2bp, which separates the two channels by four
    standard errors.
    """
    runs = (("constant volatility, real world", dict(book_delta=True)),
            ("constant volatility, pricing drift mu = r", dict(mu=0.05)),
            ("fitted process, pricing drift mu = r", dict(mu=0.05, vol_fitted=True)),
            ("fitted process, real world", dict(vol_fitted=True, book_delta=True)))
    paths = args.paths or 640
    jobs, spans = [], []
    for label, kw in runs:
        P = Params(delta=0.025, years=args.years or 30.0, paths=paths, seed=args.seed,
                   record_gaps=True, **kw)
        if P.vol_fitted:
            fitted_parts(P)                  # build or load the tables before the pool
        js = batch_jobs(P)
        spans.append((label, P, len(jobs), len(jobs) + len(js)))
        jobs += js
    aggs = pmap(_batch, jobs)
    print(f"\n{'=' * 72}\nTHE FITTED PROCESS  ({paths} paths x {spans[0][1].years:g}y per "
          f"run, seed {spans[0][1].seed})\n{'=' * 72}")
    for label, P, i, j in spans:
        rows = [_fv_row(P, g) for g in aggs[i:j]]
        whole = _fv_row(P, merge_all(aggs[i:j]))
        nb = len(rows)
        print(f"\n-- {label} --")
        for key in whole:
            vals = [r[key] for r in rows if key in r]
            mean = sum(vals) / len(vals)
            se = sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1) / len(vals))
            pct = key.startswith(("excess", "minus", "gap", "delta x"))
            fmt = (lambda v: f"{v:>+9.3%}") if pct else (lambda v: f"{v:>9.3f}")
            print(f"  {key:>26} {fmt(whole[key])}  s.e. {fmt(se).strip()}")
    print("\n-- paired: real world less its pricing-drift run, batch by batch --")
    for real, priced in ((0, 1), (3, 2)):
        label, P, i, j = spans[real]
        _, Pq, iq, jq = spans[priced]
        rows = [_fv_row(P, g) for g in aggs[i:j]]
        zero = [_fv_row(Pq, g)["excess + leak"] for g in aggs[iq:jq]]
        print(f"  {label}:")
        for key in ("excess - that", "excess - that, price only"):
            vals = [r[key] - z for r, z in zip(rows, zero)]
            mean = sum(vals) / len(vals)
            se = sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1) / len(vals))
            print(f"  {key:>26} {mean:>+9.3%}  s.e. {se:.3%}")


def _total_variance(proc, paths=300, sessions=26_000, seed=7):
    """A session's total variance over the stationary state, in units of sigma-bar squared:
    the diffusion's, the unscheduled jumps' and the earnings jump's (on the earnings sessions
    it falls on, over the cycle), from a long run of `proc`'s own state. The state ignores
    the scale, so this is the factor sigma-bar multiplies."""
    p = proc
    var_j = p.pu * 2 * p.au ** 2 + p.pd * 2 * p.ad ** 2 - (p.pu * p.au - p.pd * p.ad) ** 2
    var_e = (p.pe * 2 * p.aeu ** 2 + (1 - p.pe) * 2 * p.aed ** 2
             - (p.pe * p.aeu - (1 - p.pe) * p.aed) ** 2)
    rng = random.Random(seed)
    s2h = s2b = s2e = 0.0
    n = ne = 0
    for _ in range(paths):
        hf = hs = 0.0
        e0 = rng.randrange(VP.EARNINGS_EVERY)
        for t in range(VP.BURN + sessions):
            earn = (t - e0) % VP.EARNINGS_EVERY == 0
            if t >= VP.BURN:
                H = max(-VP.H_CLIP, min(VP.H_CLIP, hf + hs))
                s2h += exp(2 * H)
                s2b += exp(2 * p.beta * H)
                n += 1
                if earn:
                    s2e += exp(2 * p.be * H)
                    ne += 1
            _, hf, hs = p.step(0.0, hf, hs, 0.045, 0.0, earn, rng)
    return s2h / n + var_j * s2b / n + var_e * (s2e / ne) / VP.EARNINGS_EVERY


def earnterm(args):
    """What leaving the earnings term out of h costs the wheel (Sergei, 2026-11-22: measure
    it first, and leave it out with the reason stated if it is small).

    The term is Ederington and Lee's: on an earnings session h falls c0 for the expected
    part and rises c1 per unit of surprise beyond the typical move, with (c0, c1) from
    `earnmoves.py --feedback`. Four runs of the fitted process on the same draws -- the term
    off and on, each at the real-world drift and at mu = r -- so every difference is paired,
    batch by batch. The tables do not know the term, so with it on the options are priced as
    if it were off; that mismatch is shared with the run's pricing-drift twin, and each
    excess is read against its twin, which cancels it with the paths' noise.

    On balance the term lowers volatility -- the expected part's fall outweighs the average
    surprise's rise -- so at the same sigma-bar the run would also carry less variance than
    sigma^2, and its effect would mix the term's shape with a lower level. So the term-on
    runs are set at the nominal sigma whose tables' sigma-bar, carried through the term,
    gives sigma^2 a year (`_total_variance` gives the ratio): the tables then price the
    term's level -- the strike for the dial included -- and only its shape is left unpriced,
    shared with the twin. (Re-matching sigma-bar in the process alone, tables unchanged, was
    tried first: options came out about 2.4% cheap in volatility and puts struck too near,
    and the comparison read the tables, not the term.)
    """
    import json
    import os
    path = os.path.join("data", "aristocrats", "earnmoves.json")
    fb = json.load(open(path))["feedback"]
    term = (fb["c0"], fb["c1"])
    base = Params(delta=0.025, vol_fitted=True)
    proc, _ = fitted_parts(base)
    v_off = _total_variance(proc)
    v_on = _total_variance(VP.Process(proc.sig_bar, True, True, earn_feedback=term))
    scale = sqrt(v_off / v_on)
    print(f"total variance a session with the term on over off: {v_on / v_off:.4f}; "
          f"term-on runs at nominal sigma {base.sigma * scale:.5f}")
    on = dict(vol_earn_feedback=term, sigma=base.sigma * scale)
    runs = (("off, real world", dict()), ("off, mu = r", dict(mu=0.05)),
            ("on, real world", dict(on)), ("on, mu = r", dict(on, mu=0.05)))
    paths = args.paths or 1280
    jobs, spans = [], []
    for label, kw in runs:
        P = Params(delta=0.025, years=args.years or 30.0, paths=paths, seed=args.seed,
                   record_gaps=True, vol_fitted=True, **kw)
        fitted_parts(P)
        js = batch_jobs(P)
        spans.append((label, P, len(jobs), len(jobs) + len(js)))
        jobs += js
    aggs = pmap(_batch, jobs)
    rows = {label: [_fv_row(P, g) for g in aggs[i:j]] for label, P, i, j in spans}
    print(f"\n{'=' * 72}\nTHE EARNINGS TERM  c0 {term[0]:+.4f}, c1 {term[1]:+.4f} "
          f"({paths} paths x {spans[0][1].years:g}y per run, seed {spans[0][1].seed})\n"
          f"{'=' * 72}")

    def mean_se(vals):
        m = sum(vals) / len(vals)
        return m, sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1) / len(vals))

    off, on = rows["off, real world"], rows["on, real world"]
    print(f"  {'':>24} {'off':>10} {'on':>10} {'on - off':>10} {'s.e.':>8}")
    for key in off[0]:
        a = [r[key] for r in off]
        b = [r[key] for r in on]
        d, se = mean_se([y - x for x, y in zip(a, b)])
        pct = key.startswith(("excess", "minus", "gap"))
        f = (lambda v: f"{v:>+10.3%}") if pct else (lambda v: f"{v:>10.3f}")
        print(f"  {key:>24} {f(mean_se(a)[0])} {f(mean_se(b)[0])} {f(d)} {f(se).strip():>8}")
    twin = {}
    for side in ("off", "on"):
        real, q = rows[f"{side}, real world"], rows[f"{side}, mu = r"]
        twin[side] = [r["excess + leak"] - z["excess + leak"] for r, z in zip(real, q)]
    d, se = mean_se([y - x for x, y in zip(twin["off"], twin["on"])])
    print(f"\n  excess + leak, each read against its mu = r twin: off "
          f"{mean_se(twin['off'])[0]:+.3%}, on {mean_se(twin['on'])[0]:+.3%}, "
          f"on - off {d:+.3%} ± {se:.3%}")


MAG_PROCESSES = (("constant", dict()),
                 ("factors", dict(vol_fitted=True, vol_jumps=False, vol_earnings=False)),
                 ("+jumps", dict(vol_fitted=True, vol_earnings=False)),
                 ("full", dict(vol_fitted=True)))


def _mag_row(P, g):
    """_fv_row plus what step 7 also reads: the assignment rate, the holding time (median
    and Kaplan-Meier survival), the two capitals."""
    row = _fv_row(P, g)
    times, survs = _km_curve(g.durations)
    row["assignment rate"] = g.assigned / g.puts
    row["median holding, months"] = next((h for h, s in zip(times, survs) if s <= 0.5),
                                         float("nan"))
    for h, s in zip(KM_HORIZONS_M, km_survival(g.durations, KM_HORIZONS_M)):
        row[f"survival {h} mo"] = s
    row["cost capital"] = g.cap_sum / g.cap_n
    row["market capital"] = g.mvcap_sum / g.cap_n
    return row


def magnitudes(args):
    """Step 7 of the moving-volatility plan: Part II's results under four processes, each at
    total variance sigma^2 with its own tables -- constant sigma; the fitted factors alone;
    with the unscheduled jumps and their kick; the full fitted process with earnings -- in
    both regimes, at 30 years (and 5 and 10 for the excess and the inventory), each
    real-world run beside its pricing-drift twin on the same draws, and at 30 years again
    with a volatility point of spread. Every figure is written, with its error across
    batches, to data/magnitudes.json; the excess is also read against its twin."""
    import json
    import os
    paths = args.paths or 5120
    cases = []
    for proc, kw in MAG_PROCESSES:
        for regime, ps in (("Standard", 0.20), ("Conservative", 0.10)):
            for years, spread in ((30.0, 0.0), (30.0, 0.01), (10.0, 0.0), (5.0, 0.0)):
                for drift, mu in (("real", 0.07), ("twin", 0.05)):
                    cases.append((proc, regime, years, spread, drift, Params(
                        p_star=ps, delta=0.025, mu=mu, years=years, paths=paths,
                        seed=args.seed, iv_spread=spread, record_gaps=True,
                        book_delta=(drift == "real" and years == 30.0 and spread == 0.0),
                        **kw)))
    path = os.path.join("data", "magnitudes.json")
    out = {}
    if os.path.exists(path):              # resume: a group already written is not rerun
        with open(path) as f:
            out = json.load(f)

    def mean_se(vals):
        m = sum(vals) / len(vals)
        return m, sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1) / len(vals))

    def name(proc, regime, years, spread, drift):
        return f"{proc} | {regime} | {years:g}y | spread {spread:g} | {drift}"

    # One process and regime at a time -- its eight cases, real runs beside their twins --
    # each group written as it finishes, so an interruption costs one group at most.
    groups = {}
    for c in cases:
        groups.setdefault(c[:2], []).append(c)
    for (proc, regime), group in groups.items():
        if all(name(*c[:5]) in out for c in group):
            continue
        for c in group:
            if c[-1].vol_fitted:
                fitted_parts(c[-1])         # tables built in the parent, once per key
        jobs, spans = [], []
        for c in group:
            js = batch_jobs(c[-1])
            spans.append((c, len(jobs), len(jobs) + len(js)))
            jobs += js
        aggs = pmap(_batch, jobs)
        rows = {}
        for c, i, j in spans:
            rs = [_mag_row(c[-1], g) for g in aggs[i:j]]
            rows[c[:5]] = rs
            out[name(*c[:5])] = {k: mean_se([r[k] for r in rs if k in r]) for k in rs[0]}
        for key, rs in rows.items():
            if key[4] == "real":
                twin = rows[key[:4] + ("twin",)]
                out[name(*key)]["excess + leak, against its twin"] = mean_se(
                    [a["excess + leak"] - b["excess + leak"] for a, b in zip(rs, twin)])
        os.makedirs("data", exist_ok=True)
        with open(path + ".tmp", "w") as f:
            json.dump(out, f, indent=1)
        os.replace(path + ".tmp", path)
        print(f"  {proc}, {regime}: written", flush=True)
    keys = ("excess + leak, against its twin", "book delta", "book delta, price only",
            "up-beta", "down-beta", "assignment rate", "gap: mean", "gap: mean/median",
            "gap > 5%", "median holding, months", "left at first expiry", "E[I], lots",
            "E[I]/lambda, years", "market capital")
    for regime in ("Standard", "Conservative"):
        for years, spread in ((30.0, 0.0), (30.0, 0.01), (10.0, 0.0), (5.0, 0.0)):
            print(f"\n== {regime}, {years:g} years, spread {spread:g} "
                  f"({paths} paths, seed {args.seed}) ==")
            print(f"  {'':>32}" + "".join(f"{p:>16}" for p, _ in MAG_PROCESSES))
            for k in keys:
                cells = []
                for p, _ in MAG_PROCESSES:
                    v = out[f"{p} | {regime} | {years:g}y | spread {spread:g} | real"].get(k)
                    cells.append(f"{v[0]:>9.4f}±{v[1]:.4f}" if v else f"{'-':>16}")
                print(f"  {k:>32}" + "".join(f"{c:>16}" for c in cells))
    print("\nwritten data/magnitudes.json")


def _km_curve(durations):
    """The Kaplan-Meier curve as (event times in months, survival after each)."""
    ds = sorted(durations)
    times, survs, surv, at_risk, i = [], [], 1.0, len(ds), 0
    while i < len(ds):
        tt = ds[i][0]
        ev = cen = 0
        while i < len(ds) and ds[i][0] == tt:
            ev, cen = (ev + 1, cen) if ds[i][1] else (ev, cen + 1)
            i += 1
        if ev:
            surv *= 1 - ev / at_risk
            times.append(tt)
            survs.append(surv)
        at_risk -= ev + cen
    return times, survs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenario", default="all",
                    choices=["base", "dividends", "stress", "sweep",
                             "validate", "dollars", "constrained", "stochvol",
                             "fittedvol", "earnterm", "magnitudes", "all"])
    ap.add_argument("--paths", type=int, default=None)
    ap.add_argument("--seed", type=int, default=20260722)
    ap.add_argument("--years", type=float, default=None,
                    help="horizon for --scenario constrained (default 60), "
                         "validate and dollars (default 30)")
    ap.add_argument("--gamma-s", dest="gamma_s", type=float, default=0.25,
                    help="equity required against held shares (0.25 = PM)")
    ap.add_argument("--eps", type=float, default=0.10,
                    help="tolerance for eventual liquidation, setting u*")
    args = ap.parse_args()

    if args.scenario == "validate":
        validate(args)
        return

    if args.scenario == "dollars":
        dollars(args)
        return

    if args.scenario == "constrained":
        constrained(args)
        return

    if args.scenario == "stochvol":
        stochvol(args)
        return

    if args.scenario == "earnterm":
        earnterm(args)
        return

    if args.scenario == "magnitudes":
        magnitudes(args)
        return

    if args.scenario == "fittedvol":
        fittedvol(args)
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
