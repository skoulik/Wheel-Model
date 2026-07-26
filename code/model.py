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

Numerics: finite-horizon quantities come from occupation() on a near grid
(default h = 0.01, x_max = 4), whose resolution is set by the per-period
step sigma*sqrt(tau_c); the stationary ones come from stationary(), which
Richardson-extrapolates two grids because a single one biases E[T] upward
by O(h^2) accumulated over the whole tail.  `code/mc_holding.py` is the
grid-free check on both.

Stdlib only.  Run:  python code/model.py
"""

import argparse
from dataclasses import dataclass, field
from math import ceil, exp, log, pi, sqrt
from statistics import NormalDist

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
    """Strategy and market parameters.  Defaults = the Standard regime."""

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
    margin: float = 0.20
    label: str = "Standard"

    tau_c: float = field(init=False)
    delta_net: float = field(init=False)
    sigma_iv: float = field(init=False)

    def __post_init__(self):
        if self.cadence is None:
            self.cadence = self.tau_p
        self.tau_c = self.n * self.tau_p
        self.delta_net = self.delta * (1 - self.withhold)
        self.sigma_iv = self.sigma + self.iv_spread

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

    def escaped(self, u):
        return sum(ui * pi for ui, pi in zip(u, self.up))

    def step(self, u):
        """One period: convolve, absorb below 0, drop above x_max."""
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
        return [wi / tot for wi in w]


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

    surv, prem, basis, exitcost, exits = [], [], [], [], []
    escaped = 0.0
    for j in range(j_max):
        S = sum(u)
        surv.append(S)
        prem.append(sum(ui * ci for ui, ci in zip(u, cc)))
        basis.append(sum(ui * ei for ui, ei in zip(u, ex)))
        exitcost.append(sum(ui * ci for ui, ci in zip(u, walk.exit_cost)))
        exits.append(sum(ui * pi for ui, pi in zip(u, walk.exit_prob)))
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
    capital = C.margin * k + lam * C.tau_c * sum_basis * basis_factor
    prem_income = c_p / C.cadence + lam * sum_prem
    div_income = inventory * C.delta_net
    income = prem_income + div_income

    # Economic ledger: inventory carried at market value (a share is worth the
    # current spot, whatever was paid for it), the acquisition mark loss booked
    # when it happens, and the unrealized appreciation of held shares counted.
    m_price = occ["m"]
    mv_capital = C.margin * k + inventory
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
    U = [0.0] * walk.n
    for j in range(j_max):
        wt = 1.0 if horizon is None else \
            max(0.0, horizon - (j + 0.5) * C.tau_c) / horizon
        if wt:
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


def convergence_check(args):
    """(a) finite-horizon numbers are grid-insensitive; (b) the criterion bites."""
    print("\n" + "=" * 78)
    print("GRID CHECK (a): 30-year numbers vs. grid resolution and extent")
    print("=" * 78)
    C = Config(label="Standard")
    print(f"{'meas':>5} {'h':>6} {'x_max':>6} {'E[I]':>8} {'capital':>9}"
          f" {'income':>9} {'excess':>10} {'escaped':>10}")
    for measure in ("P", "Q"):
        for h, xm in ((0.02, 4.0), (0.01, 4.0), (0.01, 6.0), (0.005, 4.0)):
            occ = occupation(C, measure, h=h, x_max=xm)
            x = economics(C, measure, occ, horizon=30.0)
            print(f"{measure:>5} {h:>6.3f} {xm:>6.1f} {x['I']:>8.3f}"
                  f" {x['capital']:>9.3f} {x['income']:>9.4f}"
                  f" {x['excess']:>+10.4f} {occ['escaped']:>10.2e}")

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
    for label, cfg, measure in cases:
        crit = criteria(cfg, measure)
        if not crit["count_ok"]:
            continue
        vals = [occupation(cfg, measure, h=0.05, x_max=xm, eps=1e-7)["E[basis]"]
                for xm in grid]
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
