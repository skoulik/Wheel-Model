"""The article's analytic core: the wheel as a first-passage problem in depth.

One derivation chain, parameterized by the price drift m.  A lot's depth
x = ln(K_c/S) is, on the call grid, a Gaussian random walk with per-period
drift -nu*tau_c and volatility sigma*sqrt(tau_c), where

    nu = m - sigma^2/2,

and the lot leaves inventory at the first grid point with x <= 0.  A
"measure" is a value of m: the P-world uses (mu - delta, sigma_RV), the
Q-world uses (r - delta, sigma_IV).  Both are self-consistent worlds; the
same code computes either.

From the walk everything else follows:

  entry law for x0  ->  survival sequence S_j = P(J > j)  ->  E[T] = tau_c*E[J]
  ->  Little's law E[I] = lambda*E[T]  ->  the stationary depth census
  ->  income and capital as integrals against that census.

Two stability criteria fall out, and they are different:

  * lot count:  nu > 0            (depths mean-revert; otherwise lots are
                                   trapped forever with positive probability)
  * capital:    m > sigma^2       (a lot's basis relative to *current* spot
                                   is e^x, and E[1/S_t] must decay; equivalently
                                   the killed walk's tail exponent 2nu/sigma^2
                                   must exceed 1)

A third failure mode arrives with working capital, and it is the only fast
one: an account carrying shares on borrowed money is liquidated the first time
the price crosses a barrier fixed by its leverage.  That is a first passage
governed by the same tail exponent 2nu/sigma^2, and the closed forms for it
sit in their own block near the end of this file.  They are inert at the
defaults -- gamma_s = 1, A = inf -- which is the unconstrained operator every
figure in Parts I and II reports.

Numerics: finite-horizon quantities come from occupation() on a near grid
(default h = 0.01, x_max = 4), whose resolution is set by the per-period
step sigma*sqrt(tau_c); the stationary ones come from stationary(), which
Richardson-extrapolates two grids because a single one biases E[T] upward
by O(h^2) accumulated over the whole tail.  `code/mc_holding.py` is the
grid-free check on both.

Stdlib only -- with one optional accelerator.  The whole runtime of this
project is DepthWalk.step(), a convolution of a 400-cell density with a
69-point kernel, run for thousands of periods.  If numpy is importable it
does that convolution instead of the Python loop; the pure-Python path is
kept as the reference and is used verbatim when numpy is absent.  The two
agree to floating-point noise, which verify_examples.py checks.

Run:  python code/model.py
"""

import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from math import ceil, exp, log, pi, sqrt
from statistics import NormalDist

try:                                   # optional accelerator, see module docstring
    import numpy as _np
except ImportError:                    # pragma: no cover - the stdlib fallback
    _np = None


def pmap(fn, jobs, workers=None):
    """Map fn over independent jobs, in parallel when that pays.

    Every sweep in this project is a list of *independent* configurations, each
    of which runs its own killed walk: embarrassingly parallel.  `fn` must be a
    module-level function and the jobs picklable, since Windows spawns fresh
    interpreters.  Set WHEEL_WORKERS=1 to force the serial path (for profiling,
    or inside a worker -- pmap is only ever called from top-level code, never
    from a job, because nested pools deadlock more than they help).
    """
    jobs = list(jobs)
    if workers is None:
        workers = int(os.environ.get("WHEEL_WORKERS", 0)) or (os.cpu_count() or 1)
    workers = min(workers, len(jobs))
    if workers <= 1:
        return [fn(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, jobs))

N = NormalDist().cdf
Ninv = NormalDist().inv_cdf

BETA = 0.5826  # -zeta(1/2)/sqrt(2*pi), Siegmund's overshoot constant


def phi(z):
    return exp(-z * z / 2) / sqrt(2 * pi)


# ----------------------------------------------------------------------
# Primitives.  Probabilities take a price drift m and are evaluated in
# whichever world m names; prices are quotes and always carry the
# risk-neutral drift r - delta at the implied volatility.
# ----------------------------------------------------------------------

def d2(k, tau, sigma, m):
    """Black-Scholes d2 for strike fraction k = K/S under price drift m."""
    return (-log(k) + (m - sigma**2 / 2) * tau) / (sigma * sqrt(tau))


def assign_prob(k, tau_p, sigma, m):
    """Probability the put finishes in the money: p = N(-d2)."""
    return N(-d2(k, tau_p, sigma, m))


def k_star_drift(p_target, tau_p, sigma, m):
    """Strike fraction delivering assignment probability p_target."""
    return exp(Ninv(p_target) * sigma * sqrt(tau_p) + (m - sigma**2 / 2) * tau_p)


def bs_put(k, tau, sigma, r, delta=0.0):
    """European put price as a fraction of spot (S0 = 1).  A quote."""
    _d2 = d2(k, tau, sigma, r - delta)
    _d1 = _d2 + sigma * sqrt(tau)
    return k * exp(-r * tau) * N(-_d2) - exp(-delta * tau) * N(-_d1)


def bs_call(s, k, tau, sigma, r, delta=0.0):
    """European call price; s and k as fractions of S0.  A quote."""
    _d1 = (log(s / k) + (r - delta + sigma**2 / 2) * tau) / (sigma * sqrt(tau))
    _d2 = _d1 - sigma * sqrt(tau)
    return s * exp(-delta * tau) * N(_d1) - k * exp(-r * tau) * N(_d2)


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

@dataclass
class Config:
    """Strategy and market parameters.  Defaults = the Standard regime.

    The working-capital block is inert at its defaults, and deliberately so:
    an operator who pays for shares in full (gamma_s = 1), has unlimited
    equity (A = inf) and borrows at the risk-free rate (fin_spread = 0) never
    has a put blocked and never receives a margin call.  That operator is the
    one every figure in Parts I and II reports, so the defaults reproduce the
    unconstrained model exactly and the constrained one is a departure from
    them.  Nothing above the "Working capital" block below reads these fields.
    """

    p_star: float = 0.20       # strike policy: assignment probability per put
    tau_p: float = 1 / 52      # put tenor: one week, the live-account cadence
    n: int = 4                 # tau_c = n * tau_p = 4 weeks, the "monthly" call
    cadence: float = None      # T >= tau_p; None -> T = tau_p
    r: float = 0.05
    mu: float = 0.07           # TOTAL expected return; price drifts at mu - delta
    sigma: float = 0.20        # realized volatility
    delta: float = 0.025       # gross dividend yield
    withhold: float = 0.15
    iv_spread: float = 0.0     # sigma_IV = sigma + spread (0 = no vol risk premium)
    gamma_p: float = 0.20      # margin fraction required against a short put
    # -- working capital.  Initial and maintenance requirements are one
    # parameter each, deliberately: the difference is small next to the
    # question of whether the account survives at all.
    gamma_s: float = 1.0       # equity fraction required against held shares:
                               # 1.00 fully paid, 0.50 Reg T, 0.25 portfolio
                               # margin, 0.15 aggressive PM
    equity: float = float("inf")   # A, account equity in share prices (one
                                   # unit = one share at today's spot)
    u_star: float = 1.0        # utilization at which the operator stops
                               # selling puts; u* = 1 runs to the broker's
                               # own limit, where L = 1/gamma_s
    fin_spread: float = 0.0    # r_b - r, charged on a debit balance
    label: str = "Standard"

    tau_c: float = field(init=False)
    delta_net: float = field(init=False)
    sigma_iv: float = field(init=False)
    r_b: float = field(init=False)

    def __post_init__(self):
        if self.cadence is None:
            self.cadence = self.tau_p
        self.tau_c = self.n * self.tau_p
        self.delta_net = self.delta * (1 - self.withhold)
        self.sigma_iv = self.sigma + self.iv_spread
        self.r_b = self.r + self.fin_spread

    def world(self, measure):
        """(price drift m, dynamics volatility) of the chosen world."""
        if measure == "P":
            return self.mu - self.delta, self.sigma
        if measure == "Q":
            return self.r - self.delta, self.sigma_iv
        raise ValueError(f"unknown measure {measure!r}")


# ----------------------------------------------------------------------
# Entry: strike policy and the law of the entry depth
# ----------------------------------------------------------------------

def strike(C, measure):
    """Strike fraction k* delivering assignment probability p* in `measure`."""
    m, s = C.world(measure)
    return k_star_drift(C.p_star, C.tau_p, s, m)


def entry_law(C, measure):
    """Law of the entry depth x0 = ln(K/S') given assignment.

    z = ln(S_T/S0) ~ Normal((m - s^2/2) tau_p, s^2 tau_p) conditioned on
    z < ln k; x0 = ln k - z > 0.  By construction of k* the conditioning
    event has probability exactly p*.

    Returns (k, realized assignment prob, E[x0], density of x0).
    """
    m, s = C.world(measure)
    k = strike(C, measure)
    mean_z = (m - s**2 / 2) * C.tau_p
    sd_z = s * sqrt(C.tau_p)
    alpha = (log(k) - mean_z) / sd_z            # = Ninv(p*) by construction
    Z = N(alpha)
    mean_x0 = log(k) - mean_z + sd_z * phi(alpha) / Z

    def dens(x):
        return phi((log(k) - x - mean_z) / sd_z) / (sd_z * Z) if x > 0 else 0.0

    return k, Z, mean_x0, dens


def entry_basis_ratio(C, measure):
    """E[e^x0 | assignment] = E[K/S'], the strike paid per unit of the price
    it was paid against — the immediate mark loss factor at acquisition."""
    m, s = C.world(measure)
    k = strike(C, measure)
    mean_z = (m - s**2 / 2) * C.tau_p
    sd_z = s * sqrt(C.tau_p)
    alpha = (log(k) - mean_z) / sd_z
    return k * exp(-mean_z + sd_z**2 / 2) * N(alpha + sd_z) / N(alpha)


def expected_drop(C, measure):
    """E[d | assignment], the fractional drop from the pre-assignment price."""
    m, s = C.world(measure)
    k = strike(C, measure)
    _d2 = d2(k, C.tau_p, s, m)
    _d1 = _d2 + s * sqrt(C.tau_p)
    return 1 - exp(m * C.tau_p) * N(-_d1) / N(-_d2)


def q_exit(C, measure, x):
    """One-step (per call period) exit probability from depth x."""
    m, s = C.world(measure)
    nu = m - s**2 / 2
    return N((nu * C.tau_c - x) / (s * sqrt(C.tau_c)))


def call_premium(C, x):
    """Call premium at depth x, as a fraction of the current spot.

    The lot's strike sits at K_c = S*e^x, so in spot units the call is
    struck at e^x.  A price: quoted at implied volatility.
    """
    return bs_call(1.0, exp(x), C.tau_c, C.sigma_iv, C.r, C.delta)


def put_premium(C, measure):
    """Put premium as a fraction of spot.  A price, quoted at implied vol."""
    return bs_put(strike(C, measure), C.tau_p, C.sigma_iv, C.r, C.delta)


# ----------------------------------------------------------------------
# The depth walk: forward occupation measure
# ----------------------------------------------------------------------

class DepthWalk:
    """Gaussian walk in depth on (0, x_max], absorbed at x <= 0 (exit).

    Mass escaping above x_max is *dropped*, not parked: for the survival
    sequence that is conservative, and for the capital functional (which
    weights depth by e^x) it makes the x_max sensitivity an honest
    divergence diagnostic rather than a boundary artifact.
    """

    def __init__(self, nu, sigma, tau_c, h=0.02, x_max=4.0, band=6.0):
        self.h, self.x_max = h, x_max
        self.n = int(round(x_max / h))
        self.xs = [(i + 0.5) * h for i in range(self.n)]
        c = -nu * tau_c                       # drift of the step, in x units
        sc = sigma * sqrt(tau_c)
        self.sc = sc
        D = int(ceil((band * sc + abs(c)) / h))
        kern = []
        for d in range(-D, D + 1):
            lo = (d * h - h / 2 - c) / sc
            hi = (d * h + h / 2 - c) / sc
            w = N(hi) - N(lo)
            if w > 1e-13:
                kern.append((d, w))
        self.kern = kern
        self.D = D
        # Dense form of the same kernel, for the numpy path.  The entries the
        # sparse list drops are below 1e-13 and enter as the zeros they are.
        if _np is not None:
            dense = [0.0] * (2 * D + 1)
            for d, w in kern:
                dense[d + D] = w
            self.kern_np = _np.array(dense)
        # Per-cell probability of escaping above x_max in one step, so the
        # truncation error can be reported rather than silently absorbed.
        self.up = [sum(w for d, w in kern if i + d >= self.n)
                   for i in range(self.n)]
        # Per-cell expected cost of being called away this period: the shares
        # are delivered at K_c while the market sits at S >= K_c, so the giveaway
        # is (S - K_c)/S = 1 - e^X for the exit depth X <= 0.
        # E[(1 - e^X) 1{X<=0}] with X ~ Normal(x - nu*tau_c, sc^2), in closed form.
        self.exit_cost = []
        self.exit_prob = []
        for x in self.xs:
            mu_x = x - nu * tau_c
            p_exit = N(-mu_x / sc)
            e_part = exp(mu_x + sc * sc / 2) * N((-mu_x - sc * sc) / sc)
            self.exit_cost.append(p_exit - e_part)
            self.exit_prob.append(p_exit)
        if _np is not None:
            self.up_np = _np.array(self.up)
            self.exit_cost_np = _np.array(self.exit_cost)
            self.exit_prob_np = _np.array(self.exit_prob)
            self.xs_np = _np.array(self.xs)

    def escaped(self, u):
        if _np is not None and not isinstance(u, list):
            return float(u @ self.up_np)
        return sum(ui * pi for ui, pi in zip(u, self.up))

    def step(self, u):
        """One period: convolve, absorb below 0, drop above x_max."""
        if _np is not None and not isinstance(u, list):
            # full[t] = sum_i u[i]*w(t-i-D), i.e. mass landing at cell t-D;
            # the slice drops what fell below 0 (absorbed) or past x_max.
            return _np.convolve(u, self.kern_np)[self.D:self.D + self.n]
        n = self.n
        v = [0.0] * n
        for off, w in self.kern:
            if off >= 0:
                for i in range(n - off):
                    ui = u[i]
                    if ui:
                        v[i + off] += w * ui
            else:
                for i in range(-off, n):
                    ui = u[i]
                    if ui:
                        v[i + off] += w * ui
        return v

    def entry_vector(self, dens):
        w = [dens(x) * self.h for x in self.xs]
        tot = sum(w)
        w = [wi / tot for wi in w]
        return _np.array(w) if _np is not None else w


def occupation(C, measure, h=0.01, x_max=4.0, j_max=8000, eps=1e-9,
               min_steps=40):
    """Per-arrival functionals of the killed walk, summed over its life.

    Returns a dict with the per-period sequences (S_j, call premium, and
    basis e^x) and their geometric-tail-closed totals.  Each sequence is
    indexed by j = 0, 1, ... where period j+1 of the lot's life is spent at
    depth x_j; S_0 = 1 and sum_j S_j = E[J].
    """
    m, s = C.world(measure)
    nu = m - s**2 / 2
    _, _, _, dens = entry_law(C, measure)
    walk = DepthWalk(nu, s, C.tau_c, h=h, x_max=x_max)
    u = walk.entry_vector(dens)
    cc = [call_premium(C, x) for x in walk.xs]
    ex = [exp(x) for x in walk.xs]
    if _np is not None:
        cc, ex = _np.array(cc), _np.array(ex)
        cost_v, exit_v = walk.exit_cost_np, walk.exit_prob_np
    else:
        cost_v, exit_v = walk.exit_cost, walk.exit_prob

    surv, prem, basis, exitcost, exits = [], [], [], [], []
    escaped = 0.0
    for j in range(j_max):
        if _np is not None:
            S = float(u.sum())
            surv.append(S)
            prem.append(float(u @ cc))
            basis.append(float(u @ ex))
            exitcost.append(float(u @ cost_v))
            exits.append(float(u @ exit_v))
        else:
            S = sum(u)
            surv.append(S)
            prem.append(sum(ui * ci for ui, ci in zip(u, cc)))
            basis.append(sum(ui * ei for ui, ei in zip(u, ex)))
            exitcost.append(sum(ui * ci for ui, ci in zip(u, cost_v)))
            exits.append(sum(ui * pi for ui, pi in zip(u, exit_v)))
        if S < eps and j >= min_steps:
            break
        escaped += walk.escaped(u)
        u = walk.step(u)

    def close(seq, win=10):
        """Sum with geometric closure, ratio smoothed over a window."""
        total = sum(seq)
        if len(seq) < win + 2 or seq[-1 - win] <= 0:
            return total, None
        ratio = (seq[-1] / seq[-1 - win]) ** (1.0 / win)
        if ratio < 1.0:
            total += seq[-1] * ratio / (1 - ratio)
        return total, ratio

    EJ, r_s = close(surv)
    Eprem, r_p = close(prem)
    Ebasis, r_b = close(basis)
    Ecost, _ = close(exitcost)
    Eexits, _ = close(exits)
    return {
        "nu": nu, "m": m, "sigma": s, "steps": len(surv),
        "surv": surv, "prem": prem, "basis": basis, "exitcost": exitcost,
        "E[J]": EJ, "E[prem]": Eprem, "E[basis]": Ebasis,
        "E[exitcost]": Ecost, "P[exit]": Eexits,
        "ratio": (r_s, r_p, r_b), "escaped": escaped,
        "h": h, "x_max": x_max,
        "q(x0)": 1 - surv[1] if len(surv) > 1 else float("nan"),
    }


# ----------------------------------------------------------------------
# Economics: Little's law applied to inventory, income and capital
# ----------------------------------------------------------------------

def stationary(C, measure, h=0.025, x_max=20.0, eps=1e-7, **kw):
    """Stationary functionals, Richardson-extrapolated in the grid step.

    occupation()'s absorbing boundary sits on cell centres, so the first
    live cell is at h/2 rather than 0+ and a lot is held marginally too
    long; the resulting bias is O(h^2) and positive.  It matters here and
    not for the finite-horizon numbers because the stationary sums run over
    the whole heavy tail.  Combining a run at h with one at h/2,

        F  =  ( 4*F_{h/2} - F_h ) / 3,

    cancels the leading term.  Successive halvings of h shrink the error by
    4x at both cadences, confirming the order; the extrapolated value agrees
    with a grid-free Monte Carlo of the same walk to within its sampling
    error (`code/mc_holding.py`).  A single run at h = 0.05 -- what the
    article quoted before 2026-07-26 -- overstates E[T] by 5% at the old
    monthly cadence and by 23% at the weekly one.

    The default x_max is sized for the COUNT functionals the article quotes
    (E[J], E[T], E[I], the survival curve): they are converged by x_max = 20
    in both worlds, and going to 50 changes E[T] in the fifth decimal.  The
    capital integral E[basis] is a different matter -- it needs the far
    sweep in convergence_check(), which is where its divergence is the
    finding rather than an error.
    """
    coarse = occupation(C, measure, h=h, x_max=x_max, eps=eps, **kw)
    fine = occupation(C, measure, h=h / 2, x_max=x_max, eps=eps, **kw)

    def rich(a, b):
        return (4 * b - a) / 3

    out = dict(fine)
    for key in ("E[J]", "E[prem]", "E[basis]", "E[exitcost]", "P[exit]"):
        out[key] = rich(coarse[key], fine[key])
    j = min(len(coarse["surv"]), len(fine["surv"]))
    for key in ("surv", "prem", "basis", "exitcost"):
        out[key] = [rich(a, b) for a, b in zip(coarse[key][:j], fine[key][:j])]
    out["q(x0)"] = 1 - out["surv"][1] if len(out["surv"]) > 1 else float("nan")
    out["method"] = f"richardson({h:g}, {h / 2:g})"
    out["steps"] = j
    return out


def _time_avg_weights(seq, tau_c, horizon):
    """Weights turning per-period functionals into a [0,H] time average.

    E[F(t)] = lambda * sum_j F_j * |[j*tau_c,(j+1)*tau_c) cap [0,t]|, so the
    average of E[F(t)] over [0,H] weights F_j by tau_c*(H-(j+0.5)*tau_c)/H,
    clamped for the period straddling H.
    """
    out = []
    for j in range(len(seq)):
        a, b = j * tau_c, (j + 1) * tau_c
        if a >= horizon:
            out.append(0.0)
            continue
        if b <= horizon:
            out.append(tau_c * (horizon - (j + 0.5) * tau_c) / horizon)
        else:                                  # partial period
            d = horizon - a
            out.append((d * d / 2) / horizon)
    return out


def economics(C, measure, occ, horizon=None):
    """Inventory, income and capital, stationary (horizon=None) or over [0,H].

    Pure post-processing of a precomputed occupation measure.  All quantities
    are per unit of the *current* spot price, matching the simulator's
    normalization.  Capital = put margin + the basis of every standing lot,
    and a lot's basis relative to current spot is e^x * (1 - c_p/k).
    """
    k, p_real, mean_x0, _ = entry_law(C, measure)
    c_p = put_premium(C, measure)
    lam = p_real / C.cadence                   # arrivals per year
    basis_factor = 1 - c_p / k                 # basis / strike

    if horizon is None:
        sum_S, sum_prem, sum_basis = occ["E[J]"], occ["E[prem]"], occ["E[basis]"]
        sum_cost = occ["E[exitcost]"]
    else:
        w = _time_avg_weights(occ["surv"], C.tau_c, horizon)
        sum_S = sum(f * wi for f, wi in zip(occ["surv"], w)) / C.tau_c
        sum_prem = sum(f * wi for f, wi in zip(occ["prem"], w)) / C.tau_c
        sum_basis = sum(f * wi for f, wi in zip(occ["basis"], w)) / C.tau_c
        # The call-away giveaway is a point flow at the end of period j, not an
        # occupancy, so it carries its own weights.
        sum_cost = sum(f * max(0.0, horizon - (j + 1) * C.tau_c) / horizon
                       for j, f in enumerate(occ["exitcost"]))

    inventory = lam * C.tau_c * sum_S
    capital = C.gamma_p * k + lam * C.tau_c * sum_basis * basis_factor
    prem_income = c_p / C.cadence + lam * sum_prem
    div_income = inventory * C.delta_net
    income = prem_income + div_income

    # Economic ledger: inventory carried at market value (a share is worth the
    # current spot, whatever was paid for it), the acquisition mark loss booked
    # when it happens, and the unrealized appreciation of held shares counted.
    m_price = occ["m"]
    mv_capital = C.gamma_p * k + inventory
    acq_loss = lam * (entry_basis_ratio(C, measure) - 1.0)
    call_away_loss = lam * sum_cost
    econ_pnl = (prem_income + div_income + inventory * m_price
                - acq_loss - call_away_loss)
    return {
        "mv_capital": mv_capital, "acq_loss": acq_loss, "econ_pnl": econ_pnl,
        "call_away_loss": call_away_loss,
        "econ_excess": (econ_pnl - C.r * mv_capital) / mv_capital,
        "leak": inventory * C.delta * C.withhold,
        "k": k, "p_real": p_real, "E[x0]": mean_x0, "E[d]": expected_drop(C, measure),
        "c_p": c_p, "lambda": lam, "nu": occ["nu"], "m": occ["m"],
        "q(x0)": occ["q(x0)"], "E[J]": occ["E[J]"], "E[T]": occ["E[J]"] * C.tau_c,
        "E[T]_siegmund": (mean_x0 + BETA * occ["sigma"] * sqrt(C.tau_c))
                         / occ["nu"] if occ["nu"] > 0 else float("inf"),
        "I": inventory, "capital": capital,
        "income": income, "premiums": prem_income, "dividends": div_income,
        "excess": (income - C.r * capital) / capital,
    }


def sticky_dividend_yield(C, measure, horizon, iters=40, tol=1e-10):
    """The yield to run the model at when the payout never falls with the price.

    A constant delta assumes the dividend tracks the price's *trend*: a company
    raising its payout at the price's log drift nu has, by construction, a
    constant median yield.  What a constant does not carry is the fluctuation.
    With the payout fixed in dollars between raises, the yield the operator
    actually collects is delta*e^y, where y is the market's log deviation from
    the level at which it yielded delta.  When dividend growth equals nu, y is
    driftless with volatility sigma, so over a position of a given age
    E[e^y] = exp(sigma^2 * age / 2).

    Averaging that over HELD lot-time and solving the fixed point -- a larger
    delta lowers nu, which ages the book, which raises the factor again --
    collapses the whole correction to one scalar, delta_eff: a single row of
    the dividend sweep.  This is a uniform recalibration, NOT a per-lot income.
    Every lot is credited the same yield, as it must be, since all shares of
    one company pay the same cash on the same day; weighting a lot's income by
    its own realized depth (E[e^x], the cost-basis capital) would credit
    different dividends to identical shares and breaks no-arbitrage.

    The held-time average has no limit as the horizon grows: the age density
    decays like the holding-time tail, exp(-nu^2*t/(2*sigma^2)), while the
    integrand grows like exp(sigma^2*t/2), and at the running parameters
    0.0078 < 0.02.  That divergence is the finding rather than a nuisance -- a
    payout cannot be assumed fixed forever, which is the permanent-impairment
    question (TODO #13) -- so the correction is only ever quoted at a finite
    horizon.

    Returns (delta_eff, factor).

    Cost note: only periods inside the horizon carry weight, so occupation()
    is truncated there rather than run out to its own convergence -- exact for
    this average (the dropped weights are identically zero) and ~20x cheaper
    at H = 30, which matters because this is a fixed point over full solves.
    """
    d = C.delta
    for _ in range(iters):
        Cd = replace(C, delta=d)
        occ = occupation(Cd, measure,
                         j_max=int(horizon / Cd.tau_c) + 2, min_steps=0)
        s = occ["sigma"]
        w = _time_avg_weights(occ["surv"], Cd.tau_c, horizon)
        num = den = 0.0
        for j, (S, wj) in enumerate(zip(occ["surv"], w)):
            if wj <= 0:
                continue
            num += S * wj * exp(s * s * (j + 0.5) * Cd.tau_c / 2)
            den += S * wj
        d_new = C.delta * num / den
        if abs(d_new - d) < tol:
            d = d_new
            break
        d = d_new
    return d, d / C.delta


def sticky_dividend_trap(C, measure):
    """Depth beyond which a payout fixed in dollars outruns the drift.

    Hold the total return fixed and freeze the dividend in dollars: a lot at
    depth x sees a yield of delta*e^x on the market value of its shares, so the
    price drag rises with depth and the depth drift becomes

        nu(x) = nu - delta*(e^x - 1),

    which changes sign at x* = ln(1 + nu/delta) and grows more negative beyond
    it -- a runaway region, not merely a slow one.  It is the Gordon-model
    price at which a fixed payout stops being sustainable, and it is why the
    fixed-dividend correction cannot be extrapolated: see TODO #13.
    """
    m, s = C.world(measure)
    nu = m - s**2 / 2
    if nu <= 0:
        return 0.0
    return log(1 + nu / C.delta)


def criteria(C, measure):
    """The two stability criteria and their margins."""
    m, s = C.world(measure)
    return {"nu": m - s**2 / 2, "count_ok": m - s**2 / 2 > 0,
            "m": m, "sigma2": s**2, "capital_ok": m > s**2,
            "tail_exponent": 2 * (m - s**2 / 2) / s**2}


def depth_census(C, measure, edges, horizon=None, h=0.02, x_max=8.0,
                 j_max=8000, eps=1e-9):
    """How standing inventory is distributed over depth ([eq:census]).

    Returns (share of held time per bin, mean depth, inventory-weighted exit
    probability).  With `horizon` set, the census is the one an operator
    starting from an empty book sees averaged over [0, horizon]; without it,
    the stationary census.
    """
    m, s = C.world(measure)
    _, _, _, dens = entry_law(C, measure)
    walk = DepthWalk(m - s**2 / 2, s, C.tau_c, h=h, x_max=x_max)
    u = walk.entry_vector(dens)
    U = _np.zeros(walk.n) if _np is not None else [0.0] * walk.n
    for j in range(j_max):
        wt = 1.0 if horizon is None else \
            max(0.0, horizon - (j + 0.5) * C.tau_c) / horizon
        if wt:
            if _np is not None:
                U += u * wt
            else:
                for i, ui in enumerate(u):
                    U[i] += ui * wt
        if sum(u) < eps and j >= 40:
            break
        u = walk.step(u)

    total = sum(U)
    bins = [0.0] * (len(edges) - 1)
    mean_x = mean_q = 0.0
    for x, ui in zip(walk.xs, U):
        b = min(len(bins) - 1, max(0, sum(1 for e in edges[1:] if x >= e)))
        bins[b] += ui
        mean_x += ui * x
        mean_q += ui * q_exit(C, measure, x)
    return [b / total for b in bins], mean_x / total, mean_q / total


def trapped_fraction(C, measure):
    """P(J = infinity): the share of lots that never come back, when nu <= 0.

    Continuous escape probability with Siegmund's boundary shift, averaged
    over the entry law in closed form:
        1 - E[exp(-theta*(x0 + beta*sigma*sqrt(tau_c)))],  theta = 2|nu|/sigma^2.
    """
    m, s = C.world(measure)
    nu = m - s**2 / 2
    if nu > 0:
        return 0.0
    theta = 2 * abs(nu) / s**2
    k = strike(C, measure)
    mean_z = (m - s**2 / 2) * C.tau_p
    sd_z = s * sqrt(C.tau_p)
    alpha = (log(k) - mean_z) / sd_z
    sc = s * sqrt(C.tau_c)
    # E[e^{-theta*x0}] with x0 = ln k - z, z truncated normal below ln k.
    e_x0 = (k ** -theta) * exp(theta * mean_z + theta**2 * sd_z**2 / 2) \
        * N(alpha - theta * sd_z) / N(alpha)
    return 1 - exp(-theta * BETA * sc) * e_x0


def time_to_fraction(C, occ, frac=0.9):
    """Years for E[I(t)] to reach `frac` of its stationary value."""
    target, acc = frac * occ["E[J]"], 0.0
    for j, S in enumerate(occ["surv"]):
        acc += S
        if acc >= target:
            return (j + 1) * C.tau_c
    return float("inf")


# ----------------------------------------------------------------------
# Working capital: leverage, the liquidation barrier and survival
#
# Everything above describes an operator who buys whatever the puts assign.
# A real account has a finite equity A and a broker who insists that equity
# stay above a fraction gamma_s of what the shares are worth, and a book
# carried on borrowed money therefore has a price below which it is sold out
# from under the operator.  The account's life is a first-passage time.
#
# It is governed by the SAME exponent theta = 2nu/sigma^2 that decides whether
# the depth census's capital integral converges ([eq:capital-criterion]).
# That is not a coincidence: both are the exponent of the exponential
# martingale of the same drifting walk, once as the decay rate of a stationary
# tail and once as the decay rate of a hitting probability in the barrier.
# One constant, read twice.
#
# The barrier below is STATIC: it holds the lot count fixed and lets only the
# price move.  The wheel's own dynamics push both ways -- new assignments grow
# the debit during exactly the declines that threaten the account, while
# premium income and called-away lots repay it -- and the net sign is not
# obvious a priori.  Settling it is the constrained simulator's job, not this
# block's; these are the closed forms it will be checked against.
# ----------------------------------------------------------------------

def _log_ncdf(z):
    """log N(z), usable in the far left tail where N(z) itself underflows."""
    if z > -20.0:
        return log(N(z))
    zz = z * z                     # Mills-ratio asymptotic, ~1e-7 relative here
    return -zz / 2 - log(-z) - log(2 * pi) / 2 + log(1 - 1 / zz + 3 / (zz * zz))


def leverage(C, u=None):
    """Gross exposure per unit of equity at utilization u.

    Utilization is margin posted over equity.  Posting gamma_s per unit of
    exposure, u of equity carries L = u/gamma_s of stock, so the broker's own
    ceiling u = 1 is L = 1/gamma_s: four times equity at portfolio margin,
    twice it under Reg T, and no leverage at all when shares must be paid for
    in full.  Defaults to the configured stopping rule u*.
    """
    return (C.u_star if u is None else u) / C.gamma_s


def liquidation_barrier(L, gamma_s):
    """f*, the price ratio at which equity / market value crosses gamma_s.

    A book worth M carried on equity A = M/L is financed by a debit
    D = M*(1 - 1/L), and the debit does not move when the price does.  After
    the price multiplies by f the broker weighs f*M - D against gamma_s*f*M,
    and calls when

        f* = (1 - 1/L) / (1 - gamma_s).                        [eq:barrier]

    Two boundary cases are the formula telling the truth rather than special
    pleading.  f* <= 0 is an unlevered book, which owes nothing and is never
    called.  f* >= 1 is a position already in violation on the day it is put
    on, and it happens exactly when L >= 1/gamma_s -- the broker's ceiling,
    recovered from the barrier instead of assumed.
    """
    if L <= 1.0:
        return 0.0
    if gamma_s >= 1.0:                     # nothing may be borrowed at all
        return float("inf")
    return (1.0 - 1.0 / L) / (1.0 - gamma_s)


def first_passage_prob(a, nu, sigma, horizon=None):
    """P(the log price ever falls a below where it started), for a > 0.

    ln(S_t/S_0) = nu*t + sigma*W_t, so this is first passage of a Brownian
    motion with drift down to -a.  Over an unbounded horizon it is the
    classical

        P = exp(-2*nu*a/sigma^2) = e^(-theta*a) = f*^theta,     [eq:survive]

    theta = 2nu/sigma^2 being the census tail exponent again; over [0, H] the
    reflection principle gives

        N((-a - nu*H)/(sigma*sqrt(H)))
          + e^(-2*nu*a/sigma^2) * N((-a + nu*H)/(sigma*sqrt(H))),

    whose first term is the paths that end below the barrier and whose second
    is those that touched it and came back.  As H grows the first term dies
    and the second collapses onto f*^theta -- checked as a unit test, since
    the finite- and infinite-horizon forms are the pair the constrained
    analysis reads in opposite directions.

    With nu <= 0 the walk hits any barrier almost surely and the unbounded
    answer is 1, which the exponential delivers on its own.
    """
    if a <= 0:
        return 1.0
    theta = 2 * nu / sigma**2
    if horizon is None:
        return min(1.0, exp(-theta * a))
    if horizon <= 0:
        return 0.0
    sd = sigma * sqrt(horizon)
    direct = N((-a - nu * horizon) / sd)
    # For nu < 0 the exponential overflows while its companion N(.) underflows;
    # their product is a probability either way, so they are paired in logs.
    reflect = exp(min(0.0, -theta * a + _log_ncdf((-a + nu * horizon) / sd)))
    return min(1.0, direct + reflect)


def liquidation_prob(C, measure, L=None, horizon=None):
    """P(a book levered L times is sold out), in `measure`'s world."""
    m, s = C.world(measure)
    f = liquidation_barrier(leverage(C) if L is None else L, C.gamma_s)
    if f <= 0.0:
        return 0.0
    if f >= 1.0:
        return 1.0
    return first_passage_prob(-log(f), m - s**2 / 2, s, horizon)


def max_leverage(C, measure, eps, gamma_s=None):
    """Largest L whose eventual-liquidation probability is at most eps.

    Inverting [eq:survive] through [eq:barrier] at f* = eps^(1/theta),

        L_max = 1 / (1 - (1 - gamma_s) * eps^(1/theta)).

    theta <= 0 leaves nothing to invert: the barrier is hit almost surely at
    any leverage whatever, so the answer is an unlevered book.  gamma_s = 1
    gives L_max = 1 for the same reason from the other side -- shares paid for
    in full cannot be levered, whatever the tolerance.
    """
    g = C.gamma_s if gamma_s is None else gamma_s
    theta = criteria(C, measure)["tail_exponent"]
    if theta <= 0:
        return 1.0
    den = 1.0 - (1.0 - g) * eps ** (1.0 / theta)
    return float("inf") if den <= 0 else 1.0 / den


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

def report(C, args):
    print("\n" + "=" * 78)
    print(f"REGIME: {C.label}   p*={C.p_star:.0%}  tau_p={C.tau_p:.4f}  "
          f"T={C.cadence:.4f}  tau_c={C.tau_c:.2f}  sigma={C.sigma:.0%}  "
          f"delta={C.delta:.1%}  mu={C.mu:.0%}  r={C.r:.0%}")
    print("=" * 78)

    for measure in ("P", "Q"):
        crit = criteria(C, measure)
        m, s = C.world(measure)
        theta = crit["tail_exponent"]
        print(f"\n-- {measure}-world:  m = {m:+.4f}   nu = {crit['nu']:+.4f}   "
              f"tail exponent 2nu/sigma^2 = {theta:.2f}")
        print(f"   lot count stable (nu > 0):    "
              f"{'YES' if crit['count_ok'] else 'NO':>3}   ({crit['nu']:+.4f})")
        print(f"   capital stable (m > sigma^2): "
              f"{'YES' if crit['capital_ok'] else 'NO':>3}"
              f"   ({m:.4f} vs {crit['sigma2']:.4f})")
        if not crit["count_ok"]:
            print("   -> lots trap forever with positive probability; "
                  "E[T] and stationary I* diverge.")
            continue

        occ = occupation(C, measure, h=args.h, x_max=args.x_max)
        e = economics(C, measure, occ)
        print(f"   k* = {e['k']:.4f}   realized assignment {e['p_real']:.3f}"
              f"   E[d] = {e['E[d]']:.3f}   E[x0] = {e['E[x0]']:.4f}"
              f"   q(x0) = {e['q(x0)']:.3f}")
        print(f"   c_p = {e['c_p']:.5f}   lambda = {e['lambda']:.2f}/yr")
        print(f"   {'horizon':>10} {'E[I]':>8} | {'cost cap':>9} {'cash inc':>9}"
              f" {'excess/yr':>10} | {'mkt cap':>8} {'econ P&L':>9} {'excess/yr':>10}")
        for H in (5.0, 10.0, 30.0):
            x = economics(C, measure, occ, horizon=H)
            print(f"   {f'{H:.0f}y':>10} {x['I']:>8.2f} | {x['capital']:>9.2f}"
                  f" {x['income']:>9.4f} {x['excess']:>+10.4f}"
                  f" | {x['mv_capital']:>8.2f} {x['econ_pnl']:>9.4f}"
                  f" {x['econ_excess']:>+10.4f}")
            if measure == "Q":
                resid = x["econ_excess"] + x["leak"] / x["mv_capital"]
                print(f"   {'':>10} {'':>8}   no-arbitrage residual "
                      f"{x['econ_excess']:+.4f} + leak {x['leak'] / x['mv_capital']:.4f}"
                      f" = {resid:+.4f}")
        x30 = economics(C, measure, occ, horizon=30.0)
        print(f"   per lot: P[eventual exit] = {occ['P[exit]']:.4f}"
              f"   call premiums {occ['E[prem]']:.4f}"
              f"   upside given away at call-away {occ['E[exitcost]']:.4f}")
        print(f"   30y flows/yr: premiums {x30['premiums']:.4f}"
              f"   dividends {x30['dividends']:.4f}"
              f"   acquisition loss {x30['acq_loss']:.4f}"
              f"   call-away loss {x30['call_away_loss']:.4f}")
        esc = occ["escaped"]
        print(f"   [near grid h={occ['h']}, x_max={occ['x_max']}, "
              f"{occ['steps']} periods; mass escaping the grid: {esc:.2e}]")

        if not args.far:
            continue
        # Counts converge by x_max = 20 and want the extrapolation; the
        # capital integral below wants the far tail and tolerates a coarse h,
        # so the two are computed on grids sized for their own job.
        far = stationary(C, measure, h=args.far_h)
        f = economics(C, measure, far)
        t90 = time_to_fraction(C, far, 0.9)
        print(f"   stationary ({far['method']}, x_max={far['x_max']},"
              f" {far['steps']} periods, escaped {far['escaped']:.2e}):")
        print(f"     E[T] = {f['E[T]']:.2f}y ({f['E[J]']:.1f} call periods)"
              f"   Siegmund {f['E[T]_siegmund']:.2f}y"
              f"   E[I] = {f['I']:.2f}   time to 90% of it: {t90:.0f}y")
        if crit["capital_ok"]:
            wide = economics(C, measure, occupation(
                C, measure, h=args.far_h, x_max=args.far_x_max, eps=1e-7))
            conv = (theta - 1) * args.far_x_max
            flag = "" if conv > 8 else f"  [NOT converged: (theta-1)*x_max={conv:.1f}]"
            print(f"     stationary capital = {wide['capital']:.1f}"
                  f"   excess = {wide['excess']:+.4f}/yr"
                  f"   [single grid h={args.far_h}, x_max={args.far_x_max}]{flag}")
        else:
            print("     stationary capital = INFINITE (m < sigma^2): the mean is "
                  "carried by depths the system reaches only over centuries.")


def _grid_job(job):
    """One (measure, h, x_max) cell of grid check (a).  A pmap worker."""
    C, measure, h, xm = job
    occ = occupation(C, measure, h=h, x_max=xm)
    return economics(C, measure, occ, horizon=30.0), occ["escaped"]


def _basis_job(job):
    """One (config, measure, x_max) cell of grid check (b).  A pmap worker."""
    cfg, measure, xm = job
    return occupation(cfg, measure, h=0.05, x_max=xm, eps=1e-7)["E[basis]"]


def convergence_check(args):
    """(a) finite-horizon numbers are grid-insensitive; (b) the criterion bites."""
    print("\n" + "=" * 78)
    print("GRID CHECK (a): 30-year numbers vs. grid resolution and extent")
    print("=" * 78)
    C = Config(label="Standard")
    print(f"{'meas':>5} {'h':>6} {'x_max':>6} {'E[I]':>8} {'capital':>9}"
          f" {'income':>9} {'excess':>10} {'escaped':>10}")
    cells = [(C, measure, h, xm)
             for measure in ("P", "Q")
             for h, xm in ((0.02, 4.0), (0.01, 4.0), (0.01, 6.0), (0.005, 4.0))]
    for (_, measure, h, xm), (x, esc) in zip(cells, pmap(_grid_job, cells)):
        print(f"{measure:>5} {h:>6.3f} {xm:>6.1f} {x['I']:>8.3f}"
              f" {x['capital']:>9.3f} {x['income']:>9.4f}"
              f" {x['excess']:>+10.4f} {esc:>10.2e}")

    print("\n" + "=" * 78)
    print("GRID CHECK (b): does sum_j E[e^{x_j}; alive] converge?  (m > sigma^2 ?)")
    print("=" * 78)
    grid = [4.0, 8.0, 16.0, 32.0]
    print(f"{'regime':>14} {'meas':>5} {'m':>8} {'sig^2':>8} {'2nu/s^2':>8}   "
          + "".join(f"{f'xmax={v:g}':>11}" for v in grid))
    cases = [("Standard", Config(label="Standard"), "P"),
             ("Standard", Config(label="Standard"), "Q"),
             ("sigma=25%", Config(sigma=0.25), "P"),
             ("delta=4.5%", Config(delta=0.045), "P")]
    cases = [c for c in cases if criteria(c[1], c[2])["count_ok"]]
    jobs = [(cfg, measure, xm) for _, cfg, measure in cases for xm in grid]
    got = pmap(_basis_job, jobs)
    for i, (label, cfg, measure) in enumerate(cases):
        crit = criteria(cfg, measure)
        vals = got[i * len(grid):(i + 1) * len(grid)]
        print(f"{label:>14} {measure:>5} {crit['m']:>8.4f} {crit['sigma2']:>8.4f}"
              f" {crit['tail_exponent']:>8.2f}   "
              + "".join(f"{v:>11.1f}" for v in vals)
              + ("   converges" if crit["capital_ok"] else "   DIVERGES"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--h", type=float, default=0.01)
    ap.add_argument("--x-max", type=float, default=4.0)
    ap.add_argument("--far-h", type=float, default=0.025)
    ap.add_argument("--far-x-max", type=float, default=50.0)
    ap.add_argument("--no-far", dest="far", action="store_false")
    ap.add_argument("--no-grid-check", dest="grid_check", action="store_false")
    args = ap.parse_args()

    for C in (Config(p_star=0.20, label="Standard"),
              Config(p_star=0.10, label="Conservative")):
        report(C, args)
    if args.grid_check:
        convergence_check(args)


if __name__ == "__main__":
    main()
