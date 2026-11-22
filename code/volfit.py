"""The volatility state and the jumps, fitted together by simulation: step 4 of the plan.

Decision 8 of `drafts/2026-11-21-moving-volatility-plan.md`: daily moves do not separate
into a diffusion and jumps at any threshold, so neither is fitted on what the other
leaves. The model below is simulated, the statistics of `volstats.py` are computed on its
paths exactly as on the data, and the parameters are those that bring the two closest --
the simulated method of moments. Each simulated replica copies the data's own structure:
a path for every name, as long as its history, NaN wherever the data has no clean return
(outside the sample, an earnings window, an undated quarter), so a gap or a short series
biases both sides alike.

**The model**, daily, for one stock, in units of its own volatility level, which every
statistic cancels:

    x_t = z_t + J_t                             the day's move, in the day's volatility
    r_t = e^(h_t) · x_t                         (times any level)
    h_t = f_t + s_t                             a fast and a slow factor
    a_t = θ·x_t                                 the response to the move's direction
    b_t = γ·(|x_t| − √(2/π)) + κ↑·U_t + κ↓·D_t  ... and to its size
    f_t+1 = φ_f·f_t + w_θ·a_t + w_γ·b_t + η_f·e^(ζ·f_t)·ε'_t
    s_t+1 = φ_s·s_t + (1 − w_θ)·a_t + (1 − w_γ)·b_t + η_s·ε_t

z, ε and ε' are independent standard normals; U_t and D_t mark an up or a down jump, with
probability λ↑/252 and λ↓/252 a day. A jump's size in the day's units is
J = ±a·W·e^((β−1)·h_t), W a unit-scale Weibull of shape k (k = 1 is exponential, k < 1 a
heavier tail): β = 1 makes sizes scale with the volatility state, β = 0 fixes them in log
return. Each side has its own λ, a, k and β. The state responds to the whole move, jump
included, through θ (the direction: volatility rises as the price falls) and γ (the size:
a large move either way raises it); κ is what a jump adds beyond that. How the model came
to this shape is the plan's step 4:

- **Two factors**, because one could not fit: volatility's autocorrelation falls fast and
  then lingers, and with one factor the jumps turned into a patch for thin daily tails.
  Chernov, Gallant, Ghysels and Tauchen (2003) found the same for daily index returns.
- **The direction and the size split apart** (w_θ, w_γ), because the leverage effect on a
  single stock is slow -- Bouchaud, Matacz and Potters (2001) measured its decay at about
  69 days for US stocks against 9 for indices -- while the response to a move's size need
  not be.
- **Feedback** (ζ): the fast factor's own volatility rises with its level, Chernov et al.'s
  remedy for the bursts a Poisson jump cannot mimic. `--no-feedback` holds ζ at zero. On
  these data it came out at −0.02 and gained nothing (the plan's step 4).
- The kicks are free unless `--no-kicks`.

**The fit.** The distance is Σ (simulated − data)² / variance over the statistics. Each
variance is the block jackknife over BLOCK_YEARS-year calendar periods, every name deleted
together (`block_jackknife_var`), floored at the larger of the names' bootstrap variance and
the model's own sampling variance at the starting point, plus the simulation's own noise:
the names share their episodes, and resampling them alone understated the variance thirteen
times over. The random numbers are drawn once and reused at every evaluation, which keeps
the distance smooth in the parameters; Nelder–Mead searches it, in transformed parameters
(see PARAMS), stopping a pass when it stops gaining. `--recover` is the identification test:
data simulated from known parameters, fitted from a perturbed start, compared; `--se` the
standard errors at a saved fit.

    python code/volfit.py --no-feedback --start FILE --fix gamma=0 --fix "k up=1" \\
        --fix "kick up=0" --tie "beta up=beta down" --tag reduced
                                           # the reduced model the plan settled on
    python code/volfit.py --group big      # names over $20B today; small: $10-20B
    python code/volfit.py --group sp       # the S&P 500 total-return index
    python code/volfit.py --no-kicks       # with the jump kicks held at zero
    python code/volfit.py --no-feedback    # with the fast factor's feedback held at zero
    python code/volfit.py --start FILE     # begin from a saved fit (--set k=v overrides one)
    python code/volfit.py --fix k=v        # hold a parameter; --tie a=b holds a equal to b
    python code/volfit.py --recover --start FILE --seed-fake 3
                                           # simulate from FILE's parameters, fit, compare
    python code/volfit.py --se FILE        # standard errors at a saved fit
    python code/volfit.py --variance names # the old weights, resampling names alone
    python code/volfit.py --tag NAME       # names the result file

Needs numpy: the fit runs some thousands of evaluations, each a simulation of the
universe REPLICAS times over.
"""

import json
import os
import sys
import time
from math import exp, log, pi, sqrt

import numpy as np

import volstats as V

REPLICAS = 8            # simulated copies of the data's structure per evaluation
BOOTSTRAP = 200         # resamples of the names behind each statistic's variance
BLOCK_YEARS = 2         # calendar block of the jackknife behind it (block_jackknife_var)
STALL_EVALS, STALL_DELTA = 600, 0.05    # a Nelder-Mead pass ends when it stops gaining
BURN = 250              # sessions simulated before a series starts
H_CLIP = 4.0
SEED_DRAWS, SEED_BOOT, SEED_FAKE = 20261121, 1, 2
RESULTS = os.path.join("data", "aristocrats", "volfit-{group}.json")

# name, transform, start. log: positive; ratio: above 1; unit: between 0 and 1.
# The starts are near the two-factor fit of 2026-11-21 (one shared split, no feedback).
PARAMS = (
    ("half-life fast", "log", 5.0),     # sessions for the fast factor to halve
    ("slow/fast", "ratio", 16.0),       # the slow factor's half-life over the fast one's
    ("theta fast share", "unit", 0.4),  # of the response to the move's direction
    ("gamma fast share", "unit", 0.7),  # of the response to its size, kicks included
    ("theta", "lin", -0.03),
    ("gamma", "lin", -0.02),
    ("eta fast", "log", 0.025),
    ("eta slow", "log", 0.006),
    ("feedback", "lin", 0.5),           # ζ: the fast factor's vol-of-vol rises with it
    ("lambda up", "log", 1.1),          # a year
    ("a up", "log", 2.2),
    ("k up", "log", 1.3),
    ("beta up", "lin", 0.5),
    ("lambda down", "log", 5.0),
    ("a down", "log", 2.6),
    ("k down", "log", 1.3),
    ("beta down", "lin", 0.6),
    ("kick up", "lin", 0.0),
    ("kick down", "lin", 0.6),
)
NAMES = [p[0] for p in PARAMS]
START = {p[0]: p[2] for p in PARAMS}
KICKS = ("kick up", "kick down")
FEEDBACK = ("feedback",)
E_ABS = sqrt(2 / pi)


class Draws:
    """The random numbers behind every evaluation, drawn once."""

    def __init__(self, rows, sessions, seed):
        g = np.random.default_rng(seed)
        n = BURN + sessions
        self.z = g.standard_normal((rows, n))
        self.eps = g.standard_normal((rows, n))         # the slow factor's own shock
        self.u = g.random((rows, n))
        self.w = g.exponential(size=(rows, n))
        self.eps_fast = g.standard_normal((rows, n))


def _factors(p):
    """(phi, share of the direction response, share of the size response, eta) for the
    fast and the slow factor."""
    hf = p["half-life fast"]
    hs = hf * p["slow/fast"]
    wa, wb = p["theta fast share"], p["gamma fast share"]
    return ((0.5 ** (1 / hf), wa, wb, p["eta fast"]),
            (0.5 ** (1 / hs), 1 - wa, 1 - wb, p["eta slow"]))


def _jumps(p, d):
    """(up, down, unscaled up sizes, unscaled down sizes) for every day of `d`."""
    pu, pd = p["lambda up"] / V.SESSIONS, p["lambda down"] / V.SESSIONS
    up = d.u < pu
    dn = (d.u >= pu) & (d.u < pu + pd)
    return (up, dn, np.where(up, p["a up"] * d.w ** (1 / p["k up"]), 0.0),
            np.where(dn, p["a down"] * d.w ** (1 / p["k down"]), 0.0))


def simulate_loop(p, d, states=False):
    """The model stepped day by day. It is the reference `simulate` is checked against,
    and the implementation whenever the feedback is on, which makes the fast factor
    nonlinear in itself. With `states`, (R, H): H each day's log volatility, the one its
    return was drawn at."""
    (pf, af, bf, ef), (ps, as_, bs, es) = _factors(p)
    up, dn, su, sd = _jumps(p, d)
    bu, bd = p["beta up"] - 1, p["beta down"] - 1
    kick = p["kick up"] * up + p["kick down"] * dn
    th, ga, zeta = p["theta"], p["gamma"], p["feedback"]
    rows, n = d.z.shape
    hf, hs = np.zeros(rows), np.zeros(rows)
    R = np.empty((rows, n))
    H = np.empty((rows, n)) if states else None
    for t in range(n):
        hc = np.clip(hf + hs, -H_CLIP, H_CLIP)
        if states:
            H[:, t] = hc
        x = d.z[:, t] + su[:, t] * np.exp(bu * hc) - sd[:, t] * np.exp(bd * hc)
        R[:, t] = np.exp(hc) * x
        a = th * x
        b = ga * (np.abs(x) - E_ABS) + kick[:, t]
        noise = ef * d.eps_fast[:, t]
        if zeta:
            noise = noise * np.exp(zeta * np.clip(hf, -H_CLIP, H_CLIP))
        hf = pf * hf + af * a + bf * b + noise
        hs = ps * hs + as_ * a + bs * b + es * d.eps[:, t]
    return (R[:, BURN:], H[:, BURN:]) if states else R[:, BURN:]


def _simulate_feedback(p, d):
    """`simulate_loop`'s model with the feedback on, stepped day by day but with every
    jump-free term computed beforehand and the arrays laid out by day, so that a step is a
    handful of short vector operations; the jumps are corrected on their own days only.
    Agrees with `simulate_loop` to rounding."""
    (pf, af, bf, ef), (ps, as_, bs, es) = _factors(p)
    up, dn, su, sd = _jumps(p, d)
    bu, bd = p["beta up"] - 1, p["beta down"] - 1
    th, ga, zeta = p["theta"], p["gamma"], p["feedback"]
    rows, n = d.z.shape
    z = np.ascontiguousarray(d.z.T)
    a0, b0 = th * z, ga * (np.abs(z) - E_ABS)
    u_f = af * a0 + bf * b0
    u_s = np.ascontiguousarray(as_ * a0 + bs * b0 + es * d.eps.T)
    e_f = np.ascontiguousarray(ef * d.eps_fast.T)
    kick = (p["kick up"] * up + p["kick down"] * dn).T
    jt, jr = np.nonzero((up | dn).T)            # jump days, in day order
    cut = np.searchsorted(jt, np.arange(n + 1))
    su_t, sd_t = su.T, sd.T
    x = z.copy()
    F, S = np.empty((n, rows)), np.empty((n, rows))
    f, s = np.zeros(rows), np.zeros(rows)
    for t in range(n):
        F[t], S[t] = f, s
        r_ = jr[cut[t]:cut[t + 1]]
        if r_.size:
            hc = np.clip(f[r_] + s[r_], -H_CLIP, H_CLIP)
            xj = z[t, r_] + su_t[t, r_] * np.exp(bu * hc) - sd_t[t, r_] * np.exp(bd * hc)
            x[t, r_] = xj
            da = th * (xj - z[t, r_])
            db = ga * (np.abs(xj) - np.abs(z[t, r_])) + kick[t, r_]
        f = pf * f + u_f[t] + e_f[t] * np.exp(zeta * np.clip(f, -H_CLIP, H_CLIP))
        s = ps * s + u_s[t]
        if r_.size:
            f[r_] += af * da + bf * db
            s[r_] += as_ * da + bs * db
    return (np.exp(np.clip(F + S, -H_CLIP, H_CLIP)) * x).T[:, BURN:]


def _ar1(u, phi, chunk=256):
    """h with h[:, 0] = 0 and h[:, t+1] = phi·h[:, t] + u[:, t], by cumulative sums in
    chunks short enough that phi^-chunk cannot overflow."""
    rows, n = u.shape
    h = np.zeros((rows, n))
    carry = np.zeros(rows)
    for a in range(0, n, chunk):
        b = min(a + chunk, n)
        L = b - a
        k = np.arange(L + 1)
        up = phi ** (-(k[:-1] + 1.0))
        V_ = np.concatenate([np.zeros((rows, 1)), np.cumsum(u[:, a:b] * up, axis=1)], axis=1)
        block = phi ** k * (carry[:, None] + V_)
        h[:, a:b] = block[:, :L]
        carry = block[:, L]
    return h


def simulate(p, d):
    """Daily returns for every row of `d`, the burn-in dropped.

    Without jumps the day's move is z, known in advance, and h is a linear filter of
    known shocks. A jump's size depends on the state that day, through e^((β−1)·h), so
    the jumps are taken in time order: h on a jump day is the jump-free filter plus the
    decayed effect of the row's earlier jumps, which fixes this jump's size and so its
    own effect on what follows. Every row's k-th jump is handled at once; then h is
    refiltered with the jumps in. Each factor is its own filter of its shares of the
    move's response and of its own shock. Agrees with `simulate_loop` to rounding.
    With the feedback on, the fast factor is no longer a linear filter, and
    `_simulate_feedback` steps it day by day."""
    if p["feedback"]:
        return _simulate_feedback(p, d)
    (pf, af, bf, ef), (ps, as_, bs, es) = _factors(p)
    th, ga = p["theta"], p["gamma"]
    rows, n = d.z.shape
    pu, pd = p["lambda up"] / V.SESSIONS, p["lambda down"] / V.SESSIONS
    fu, fw, fz = d.u.ravel(), d.w.ravel(), d.z.ravel()
    idx = np.flatnonzero(fu < pu + pd)                  # sorted: by row, then day
    up = fu[idx] < pu
    size = np.where(up, p["a up"] * fw[idx] ** (1 / p["k up"]),
                    -p["a down"] * fw[idx] ** (1 / p["k down"]))
    bm1 = np.where(up, p["beta up"] - 1, p["beta down"] - 1)
    kick = np.where(up, p["kick up"], p["kick down"])
    ze = fz[idx]
    a0 = th * d.z                                       # the responses on a jump-free day
    b0 = ga * (np.abs(d.z) - E_ABS)
    u_fast = af * a0 + bf * b0 + ef * d.eps_fast
    u_slow = as_ * a0 + bs * b0 + es * d.eps
    h_free = (_ar1(u_fast, pf) + _ar1(u_slow, ps)).ravel()
    row, day = idx // n, idx % n
    starts = np.flatnonzero(np.r_[True, row[1:] != row[:-1]]) if idx.size else idx
    rank = np.arange(idx.size) - np.repeat(starts, np.diff(np.r_[starts, idx.size]))
    by_rank = np.argsort(rank, kind="stable")
    bounds = np.searchsorted(rank[by_rank], np.arange(rank.max() + 2 if idx.size else 1))
    # each factor's jump-driven part just after a row's last jump
    after_f, after_s = np.zeros(rows), np.zeros(rows)
    last = np.full(rows, -1)
    da, db, xe = np.zeros(idx.size), np.zeros(idx.size), np.zeros(idx.size)
    for k in range(len(bounds) - 1):
        sel = by_rank[bounds[k]:bounds[k + 1]]
        r_, t_ = row[sel], day[sel]
        seen = last[r_] >= 0
        gap = t_ - last[r_] - 1.0
        gf = np.where(seen, after_f[r_] * pf ** gap, 0.0)
        gs = np.where(seen, after_s[r_] * ps ** gap, 0.0)
        hc = np.clip(h_free[idx[sel]] + gf + gs, -H_CLIP, H_CLIP)
        x = ze[sel] + size[sel] * np.exp(bm1[sel] * hc)
        da[sel] = th * (x - ze[sel])
        db[sel] = ga * (np.abs(x) - np.abs(ze[sel])) + kick[sel]
        xe[sel] = x
        after_f[r_] = pf * gf + af * da[sel] + bf * db[sel]
        after_s[r_] = ps * gs + as_ * da[sel] + bs * db[sel]
        last[r_] = t_
    u_fast, u_slow = u_fast.ravel(), u_slow.ravel()
    u_fast[idx] += af * da + bf * db
    u_slow[idx] += as_ * da + bs * db
    h = _ar1(u_fast.reshape(rows, n), pf) + _ar1(u_slow.reshape(rows, n), ps)
    x = fz.copy()
    x[idx] = xe
    return (np.exp(np.clip(h, -H_CLIP, H_CLIP)) * x.reshape(rows, n))[:, BURN:]


_WORKER = {}


def _init_replica(mask, j):
    _WORKER["mask"] = mask
    _WORKER["draws"] = Draws(mask.shape[0], mask.shape[1], SEED_DRAWS + j)


def _replica_stats(p):
    R = simulate(p, _WORKER["draws"])
    return np.array(list(V.stats(np.where(_WORKER["mask"], R, np.nan)).values()))


class Replicas:
    """REPLICAS simulations shaped like the data, each with its own fixed draws.

    A replica's statistics are computed exactly as the data's, on a set of the same
    shape, so their mean over replicas carries the same small-sample bias as the data's
    and cancels it. Each replica lives in its own worker process, which keeps its draws
    between evaluations; WHEEL_WORKERS=1 runs them in this process instead."""

    def __init__(self, mask, k=REPLICAS):
        self.k = k
        self.serial = os.environ.get("WHEEL_WORKERS") == "1"
        if self.serial:
            self.local = [(mask, Draws(mask.shape[0], mask.shape[1], SEED_DRAWS + j))
                          for j in range(k)]
        else:
            from concurrent.futures import ProcessPoolExecutor
            self.pools = [ProcessPoolExecutor(1, initializer=_init_replica,
                                              initargs=(mask, j)) for j in range(k)]

    def stats(self, p):
        """(replicas, statistics) at parameters p."""
        if self.serial:
            return np.array([list(V.stats(np.where(m, simulate(p, d), np.nan)).values())
                             for m, d in self.local])
        futures = [pool.submit(_replica_stats, p) for pool in self.pools]
        return np.array([f.result() for f in futures])

    def close(self):
        for pool in getattr(self, "pools", ()):
            pool.shutdown()


def name_bootstrap_var(R):
    """Each statistic's variance across BOOTSTRAP resamples of the rows (names)."""
    g = np.random.default_rng(SEED_BOOT)
    rows = R.shape[0]
    boot = np.array([list(V.stats(R[g.integers(0, rows, rows)]).values())
                     for _ in range(BOOTSTRAP)])
    return np.nanvar(boot, axis=0, ddof=1)


def block_jackknife_var(R, blocks):
    """Each statistic's variance by the delete-a-block jackknife over calendar periods,
    every name's returns in the period deleted together: Künsch's (1989) deletion, on
    non-overlapping blocks as Carlstein (1986) took them, carried to a panel.

    Resampling names treats them as independent; they are not -- 2008 and 2020 reached
    every one of them at once, and the persistence and leverage statistics at long lags
    are carried by a handful of such episodes. Measured 2026-11-21 on the universe with
    BLOCK_YEARS-year blocks: a median 13 times the names' variance, 20 to 100 times at the
    long lags. A deleted block leaves a gap that every statistic already skips, so no
    series is cut and joined."""
    ids = np.unique(blocks[blocks >= 0])
    K = len(ids)
    jk = np.array([list(V.stats(np.where(blocks == k, np.nan, R)).values()) for k in ids])
    with np.errstate(invalid="ignore"):
        return (K - 1) / K * np.nansum((jk - np.nanmean(jk, axis=0)) ** 2, axis=0)


def calendar_blocks(days_per_row, shape, start_year=2005):
    """BLOCK_YEARS-year calendar blocks for every cell of a padded return array."""
    b = np.full(shape, -1)
    for i, days in enumerate(days_per_row):
        b[i, :len(days)] = [(d.year - start_year) // BLOCK_YEARS for d in days]
    return b


class Target:
    """The data's statistics, their variances, and simulations shaped like the data."""

    def __init__(self, R, blocks=None, floor_at=None):
        """`blocks`: each return's calendar block (an int, -1 where R is NaN), or None to
        weight by resampling names alone. `floor_at`: parameters at which the model's own
        sampling variance -- the spread of a statistic across the replicas, each a sample of
        the data's shape -- floors every variance.

        The floor is for statistics resting on a handful of events: the S&P has few moves
        beyond 6 sd, so deleting a calendar block hardly changes the kick after them, its
        jackknife variance comes out near zero, and with one series there is no name to
        resample -- one such statistic took the distance to 10^18 (2026-11-22)."""
        self.mask = ~np.isnan(R)
        st = V.stats(R)
        self.keys = list(st)
        self.data = np.array(list(st.values()))
        self.sims = Replicas(self.mask)
        self.var_names = name_bootstrap_var(R)
        self.var_model = None
        if floor_at is not None:
            with np.errstate(all="ignore"):
                self.var_model = np.nanvar(self.sims.stats(floor_at), axis=0, ddof=1)
        floor = (self.var_names if self.var_model is None
                 else np.fmax(self.var_names, self.var_model))
        self.var_blocks = None if blocks is None else block_jackknife_var(R, blocks)
        total = floor if blocks is None else np.fmax(self.var_blocks, floor)
        # the simulation's own noise: a replica's variance over the number of replicas
        own = self.var_names if self.var_model is None else self.var_model
        self.var = total + own / REPLICAS
        self.use = ~np.isnan(self.data) & (self.var > 0)

    def simulated(self, p):
        with np.errstate(all="ignore"):
            return np.nanmean(self.sims.stats(p), axis=0)

    def distance(self, p):
        m = self.simulated(p)
        bad = self.use & np.isnan(m)
        d = (m - self.data)[self.use & ~bad] ** 2 / self.var[self.use & ~bad]
        return float(d.sum() + 1e6 * bad.sum())


KIND = {q[0]: q[1] for q in PARAMS}
_TO = {"lin": lambda v: v, "log": exp, "ratio": lambda v: 1 + exp(v),
       "unit": lambda v: 1 / (1 + exp(-v))}
_FROM = {"lin": lambda y: y, "log": log, "ratio": lambda y: log(y - 1),
         "unit": lambda y: log(y / (1 - y))}


TIES = {}       # parameter -> the parameter it is held equal to (`--tie a=b`)


def to_params(x, free, fixed):
    p = dict(fixed)
    for name, v in zip(free, x):
        p[name] = _TO[KIND[name]](min(max(v, -50.0), 50.0))
    for dep, src in TIES.items():
        p[dep] = p[src]
    return p


def from_params(p, free):
    return np.array([_FROM[KIND[n]](p[n]) for n in free])


def nelder_mead(f, x0, step=0.2, max_evals=4000, tol=1e-4, stall_evals=STALL_EVALS,
                stall_delta=STALL_DELTA):
    """Minimize f from x0; adaptive coefficients (Gao and Han 2012) for many dimensions.

    Stops at the tolerance, or when the best value has gained less than `stall_delta` over
    `stall_evals` evaluations: on a simulated distance the simplex can keep shuffling within
    the simulation's own noise long after there is nothing left to find."""
    n = len(x0)
    a, g, c, s = 1.0, 1 + 2 / n, 0.75 - 1 / (2 * n), 1 - 1 / n
    X = [np.array(x0, float)] + [np.array(x0, float) + step * np.eye(n)[i] for i in range(n)]
    F = [f(x) for x in X]
    evals = n + 1
    best, since = min(F), evals
    while evals < max_evals:
        order = np.argsort(F)
        X, F = [X[i] for i in order], [F[i] for i in order]
        if abs(F[-1] - F[0]) <= tol * (abs(F[0]) + 1e-12):
            break
        if F[0] < best - stall_delta:
            best, since = F[0], evals
        elif evals - since > stall_evals:
            break
        mid = np.mean(X[:-1], axis=0)
        xr = mid + a * (mid - X[-1])
        fr = f(xr)
        evals += 1
        if fr < F[0]:
            xe = mid + g * (xr - mid)
            fe = f(xe)
            evals += 1
            X[-1], F[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < F[-2]:
            X[-1], F[-1] = xr, fr
        else:
            inside = fr >= F[-1]
            xc = mid - c * (xr - mid) if inside else mid + c * (xr - mid)
            fc = f(xc)
            evals += 1
            if fc < min(fr, F[-1]):
                X[-1], F[-1] = xc, fc
            else:
                X = [X[0]] + [X[0] + s * (x - X[0]) for x in X[1:]]
                F = [F[0]] + [f(x) for x in X[1:]]
                evals += n
    i = int(np.argmin(F))
    return X[i], F[i], evals


def fit(target, start, fixed=None, max_evals=8000, label="", checkpoint=None):
    """Minimize the distance from `start`, the parameters in `fixed` held at their values."""
    fixed = dict(fixed or {})
    free = [n for n in NAMES if n not in fixed and n not in TIES]
    t0 = time.time()
    count = [0]
    best = [float("inf"), None]

    def f(x):
        count[0] += 1
        q = target.distance(to_params(x, free, fixed))
        if q < best[0]:
            best[0], best[1] = q, np.array(x)
        if count[0] % 200 == 0:
            print(f"    {label} {count[0]} evaluations, {time.time() - t0:.0f}s, "
                  f"best distance {best[0]:.2f}", file=sys.stderr)
            if checkpoint:
                with open(checkpoint, "w") as fh:
                    json.dump({"params": to_params(best[1], free, fixed), "fixed": fixed,
                               "distance": best[0], "evaluations": count[0]}, fh, indent=1)
        return q

    x, q, evals = nelder_mead(f, from_params(start, free), max_evals=max_evals)
    # One restart from the optimum, against a collapsed simplex, and with a larger one:
    # Gao and Han (2012, §3) find a larger restart simplex helps in many dimensions.
    x, q, more = nelder_mead(f, x, step=0.3, max_evals=max_evals)
    return to_params(x, free, fixed), q, evals + more, time.time() - t0


def describe(p):
    hf = p["half-life fast"]
    hs = hf * p["slow/fast"]
    wa, wb = p["theta fast share"], p["gamma fast share"]
    lines = [f"  fast factor: half-life {hf:.1f} sessions, eta {p['eta fast']:.4f}, "
             f"feedback {p['feedback']:+.3f}",
             f"  slow factor: half-life {hs:.1f} sessions ({hs / V.MONTH:.1f} months), "
             f"eta {p['eta slow']:.4f}",
             f"  response to the move: theta {p['theta']:+.4f} ({wa:.2f} into the fast "
             f"factor), gamma {p['gamma']:+.4f} ({wb:.2f} into the fast factor)"]
    for side in ("up", "down"):
        lines.append(f"  {side:4} jumps: lambda {p[f'lambda {side}']:.3f} a year, size "
                     f"a {p[f'a {side}']:.3f} x Weibull(k {p[f'k {side}']:.3f}), "
                     f"beta {p[f'beta {side}']:.3f}, kick {p[f'kick {side}']:+.3f}")
    return "\n".join(lines)


def standard_errors(target, p, fixed, step=0.05):
    """Each free parameter's standard error by the simulated-moments sandwich,
    (G'WG)⁻¹ G'WΣWG (G'WG)⁻¹ with W = Σ⁻¹ diagonal: G is the statistics' derivative in the
    transformed parameters, by central differences on the fixed draws, carried to natural
    units by the delta method. Σ is taken diagonal -- the statistics' covariances are not
    estimable from eleven calendar blocks -- so the errors are approximate: correlated
    statistics count as more information than they carry, and the errors come out too small
    if anything."""
    free = [n for n in NAMES if n not in fixed and n not in TIES]
    x0 = from_params(p, free)
    use = target.use
    G = np.empty((int(use.sum()), len(free)))
    for j in range(len(free)):
        up, dn = x0.copy(), x0.copy()
        up[j] += step
        dn[j] -= step
        G[:, j] = ((target.simulated(to_params(up, free, fixed))
                    - target.simulated(to_params(dn, free, fixed)))[use] / (2 * step))
    W = 1 / target.var[use]
    info = G.T @ (G * W[:, None])
    cov_x = np.linalg.pinv(info)        # with W = Σ⁻¹ the sandwich collapses to this
    jac = np.array([(_TO[KIND[n]](x0[j] + 1e-6) - _TO[KIND[n]](x0[j] - 1e-6)) / 2e-6
                    for j, n in enumerate(free)])
    return {n: float(abs(jac[j]) * np.sqrt(max(cov_x[j, j], 0.0)))
            for j, n in enumerate(free)}


def table(target, p):
    m = target.simulated(p)
    sd = np.sqrt(target.var)
    print(f"  {'statistic':30} {'data':>9} {'fit':>9} {'z':>6}")
    for k, a, b, s, u in zip(target.keys, target.data, m, sd, target.use):
        z = (b - a) / s if u else float("nan")
        print(f"  {k:30} {a:9.4f} {b:9.4f} {z:6.1f}")


def data_returns(group):
    """(R, calendar blocks) for a group: all, big, small, or sp."""
    import jumps
    if group == "sp":
        days, r = jumps.market_returns()
        return r[None, :], calendar_blocks([days], (1, len(days)), start_year=days[0].year)
    names, syms, days, R = jumps.universe_returns()
    blocks = calendar_blocks(days, R.shape)
    if group == "all":
        return R, blocks
    big = np.array([names[s].cap(names[s].series.days[-1]) >= 20e9 for s in syms])
    keep = big if group == "big" else ~big
    return R[keep], blocks[keep]


def main():
    args = sys.argv[1:]
    group = args[args.index("--group") + 1] if "--group" in args else "all"
    fixed = {}
    if "--no-kicks" in args:
        fixed.update({k: 0.0 for k in KICKS})
    if "--no-feedback" in args:
        fixed.update({k: 0.0 for k in FEEDBACK})
    suffix = "".join(f"-no{k}" for k in ("kicks", "feedback") if f"--no-{k}" in args)
    # --start FILE: begin from a saved fit (the truth, with --recover); --set k=v overrides
    # a value, --fix k=v holds one there; --tag names the result file
    base = dict(START)
    if "--start" in args:
        with open(args[args.index("--start") + 1]) as f:
            base.update({k: v for k, v in json.load(f)["params"].items() if k in START})
        suffix += "-warm"
    for i, a in enumerate(args):
        if a in ("--set", "--fix"):
            k, v = args[i + 1].rsplit("=", 1)
            if k not in START:
                sys.exit(f"no parameter {k!r}")
            base[k] = float(v)
            if a == "--fix":
                fixed[k] = float(v)
    for i, a in enumerate(args):
        if a == "--tie":
            dep, src = args[i + 1].split("=")
            if dep not in START or src not in START:
                sys.exit(f"no parameter in {args[i + 1]!r}")
            TIES[dep] = src
    if "--tag" in args:
        suffix += "-" + args[args.index("--tag") + 1]
    by_names = "--variance" in args and args[args.index("--variance") + 1] == "names"
    seed_fake = int(args[args.index("--seed-fake") + 1]) if "--seed-fake" in args else SEED_FAKE
    R, blocks = data_returns(group)
    blocks = None if by_names else blocks
    if "--se" in args:
        # standard errors at a saved fit, on the data and weights it was fitted with
        path = args[args.index("--se") + 1]
        with open(path) as f:
            saved = json.load(f)
        p = dict(START)
        p.update(saved["params"])
        TIES.update(saved.get("ties", {}))
        target = Target(R, blocks, floor_at=p)
        se = standard_errors(target, p, saved.get("fixed", {}))
        print(f"standard errors at {path} (distance {target.distance(p):.1f}):")
        for k, v in se.items():
            print(f"  {k:18} {p[k]:10.4f} ± {v:.4f}")
        with open(path.replace(".json", "-se.json"), "w") as f:
            json.dump({"source": path, "params": p, "se": se}, f, indent=1)
        target.sims.close()
        return
    if "--recover" in args:
        truth = {k: fixed.get(k, v) for k, v in base.items()}
        fake = simulate(truth, Draws(R.shape[0], R.shape[1], seed_fake))
        target = Target(np.where(~np.isnan(R), fake, np.nan), blocks, floor_at=truth)
        # --perturb: how far from the truth the search starts (0: at it, which makes the
        # spread of fitted values over --seed-fake samples the estimator's sampling error)
        k_ = float(args[args.index("--perturb") + 1]) if "--perturb" in args else 0.3
        start = {k: (v if k in fixed else v * (1 + k_) if k not in KICKS and v > 0 else v)
                 for k, v in truth.items()}
        start = {k: (min(v, 0.95) if KIND[k] == "unit" else v) for k, v in start.items()}
        if "theta" not in fixed:
            start["theta"] = truth["theta"] * (1 + k_)
        if "gamma" not in fixed:
            start["gamma"] = truth["gamma"] + 0.02 * k_ / 0.3
        for dep, src in TIES.items():
            start[dep] = start[src]
        p, q, evals, secs = fit(target, start, fixed, label="recover" + suffix)
        print(f"recovery: {evals} evaluations, {secs:.0f}s, distance {q:.1f} over "
              f"{int(target.use.sum())} statistics")
        print(f"  {'parameter':12} {'truth':>9} {'start':>9} {'fitted':>9}")
        for k in NAMES:
            print(f"  {k:12} {truth[k]:9.4f} {start[k]:9.4f} {p[k]:9.4f}")
        table(target, p)
        out = RESULTS.format(group=f"{group}-recover{suffix}-seed{seed_fake}")
        with open(out, "w") as f:
            json.dump({"truth": truth, "start": start, "fitted": p, "fixed": fixed,
                       "distance": q, "evaluations": evals}, f, indent=1)
        print(f"\nwritten {out}")
        target.sims.close()
        return
    # One series (the S&P) cannot be resampled by name; its calendar blocks still can be.
    start = {k: fixed.get(k, v) for k, v in base.items()}
    for dep, src in TIES.items():
        start[dep] = start[src]
    target = Target(R, blocks, floor_at=start)
    print(f"group {group}: {R.shape[0]} series, {int(target.use.sum())} statistics, "
          f"{REPLICAS} replicas a evaluation; variance "
          f"{'by names' if blocks is None else f'by {BLOCK_YEARS}-year calendar blocks'}; "
          f"held: {', '.join(f'{k}={v:g}' for k, v in fixed.items()) or 'nothing'}")
    q0 = target.distance(start)
    p, q, evals, secs = fit(target, start, fixed, label=group + suffix,
                            checkpoint=RESULTS.format(group=group + suffix + "-checkpoint"))
    print(f"distance {q0:.1f} at START, {q:.1f} fitted; {evals} evaluations, {secs:.0f}s\n")
    print(describe(p))
    print()
    table(target, p)
    out = RESULTS.format(group=group + suffix)
    m = target.simulated(p)
    with open(out, "w") as f:
        json.dump({"group": group, "params": p, "fixed": fixed, "distance": q,
                   "ties": TIES,
                   "statistics": int(target.use.sum()),
                   "free": len(NAMES) - len(fixed) - len(TIES),
                   "evaluations": evals,
                   "variance": "names" if blocks is None else f"blocks of {BLOCK_YEARS} years",
                   "table": {k: [float(a), float(b), float(np.sqrt(v))] for k, a, b, v
                             in zip(target.keys, target.data, m, target.var)}},
                  f, indent=1)
    print(f"\nwritten {out}")
    target.sims.close()


if __name__ == "__main__":
    main()
