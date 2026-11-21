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
    h_t+1 = φ·h_t + θ·x_t + γ·(|x_t| − √(2/π)) + η·ε_t + κ↑·U_t + κ↓·D_t

z and ε are independent standard normals; U_t and D_t mark an up or a down jump, with
probability λ↑/252 and λ↓/252 a day. A jump's size in the day's units is
J = ±a·W·e^((β−1)·h_t), W a unit-scale Weibull of shape k (k = 1 is exponential, k < 1 a
heavier tail): β = 1 makes sizes scale with the volatility state, β = 0 fixes them in log
return. Each side has its own λ, a, k and β. The state responds to the whole move, jump
included, through θ (the direction: volatility rises as the price falls) and γ (the size:
a large move either way raises it); κ is what a jump adds beyond that. Step 3 saw no sign
of one, so the kicks are held at zero unless `--kicks` frees them.

**The fit.** The distance is Σ (simulated − data)² / variance over the statistics, the
variance from resampling the names (so that the spread between names counts), inflated by
1/REPLICAS for the simulation's own noise. The random numbers are drawn once and reused at
every evaluation, which keeps the distance smooth in the parameters; Nelder–Mead searches
it, in transformed parameters (logs of the positive ones). `--recover` is the
identification test: data simulated from known parameters, fitted from elsewhere, compared.

    python code/volfit.py                  # the pooled fit
    python code/volfit.py --group big      # names over $20B today; small: $10-20B
    python code/volfit.py --group sp       # the S&P 500 total-return index
    python code/volfit.py --kicks          # with the jump kicks free
    python code/volfit.py --recover        # simulate from START, fit, compare

Needs numpy: the fit runs some thousands of evaluations, each a simulation of the
universe five times over.
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
BURN = 250              # sessions simulated before a series starts
H_CLIP = 4.0
SEED_DRAWS, SEED_BOOT, SEED_FAKE = 20261121, 1, 2
RESULTS = os.path.join("data", "aristocrats", "volfit-{group}.json")

# name, transform, start
PARAMS = (
    ("half-life", "log", 40.0),     # sessions for h to halve
    ("theta", "lin", -0.02),
    ("gamma", "lin", 0.06),
    ("eta", "log", 0.03),
    ("lambda up", "log", 2.0),      # a year
    ("a up", "log", 2.0),
    ("k up", "log", 0.8),
    ("beta up", "lin", 1.0),
    ("lambda down", "log", 4.0),
    ("a down", "log", 2.0),
    ("k down", "log", 0.8),
    ("beta down", "lin", 1.0),
    ("kick up", "lin", 0.0),
    ("kick down", "lin", 0.0),
)
NAMES = [p[0] for p in PARAMS]
START = {p[0]: p[2] for p in PARAMS}
KICKS = ("kick up", "kick down")
E_ABS = sqrt(2 / pi)


class Draws:
    """The random numbers behind every evaluation, drawn once."""

    def __init__(self, rows, sessions, seed):
        g = np.random.default_rng(seed)
        n = BURN + sessions
        self.z = g.standard_normal((rows, n))
        self.eps = g.standard_normal((rows, n))
        self.u = g.random((rows, n))
        self.w = g.exponential(size=(rows, n))


def _jumps(p, d):
    """(up, down, unscaled up sizes, unscaled down sizes) for every day of `d`."""
    pu, pd = p["lambda up"] / V.SESSIONS, p["lambda down"] / V.SESSIONS
    up = d.u < pu
    dn = (d.u >= pu) & (d.u < pu + pd)
    return (up, dn, np.where(up, p["a up"] * d.w ** (1 / p["k up"]), 0.0),
            np.where(dn, p["a down"] * d.w ** (1 / p["k down"]), 0.0))


def simulate_loop(p, d):
    """The model stepped day by day: the reference `simulate` is checked against."""
    phi = 0.5 ** (1 / p["half-life"])
    up, dn, su, sd = _jumps(p, d)
    bu, bd = p["beta up"] - 1, p["beta down"] - 1
    kick = p["kick up"] * up + p["kick down"] * dn
    rows, n = d.z.shape
    h = np.zeros(rows)
    R = np.empty((rows, n))
    for t in range(n):
        hc = np.clip(h, -H_CLIP, H_CLIP)
        x = d.z[:, t] + su[:, t] * np.exp(bu * hc) - sd[:, t] * np.exp(bd * hc)
        R[:, t] = np.exp(np.clip(h, -H_CLIP, H_CLIP)) * x
        h = (phi * h + p["theta"] * x + p["gamma"] * (np.abs(x) - E_ABS)
             + p["eta"] * d.eps[:, t] + kick[:, t])
    return R[:, BURN:]


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
    refiltered with the jumps in. Agrees with `simulate_loop` to rounding."""
    phi = 0.5 ** (1 / p["half-life"])
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
    base = th * d.z + ga * (np.abs(d.z) - E_ABS) + p["eta"] * d.eps
    h_free = _ar1(base, phi).ravel()
    row, day = idx // n, idx % n
    starts = np.flatnonzero(np.r_[True, row[1:] != row[:-1]]) if idx.size else idx
    rank = np.arange(idx.size) - np.repeat(starts, np.diff(np.r_[starts, idx.size]))
    by_rank = np.argsort(rank, kind="stable")
    bounds = np.searchsorted(rank[by_rank], np.arange(rank.max() + 2 if idx.size else 1))
    after = np.zeros(rows)                  # jump-driven h just after a row's last jump
    last = np.full(rows, -1)
    du, xe = np.zeros(idx.size), np.zeros(idx.size)
    for k in range(len(bounds) - 1):
        sel = by_rank[bounds[k]:bounds[k + 1]]
        r_, t_ = row[sel], day[sel]
        g = np.where(last[r_] >= 0, after[r_] * phi ** (t_ - last[r_] - 1.0), 0.0)
        hc = np.clip(h_free[idx[sel]] + g, -H_CLIP, H_CLIP)
        x = ze[sel] + size[sel] * np.exp(bm1[sel] * hc)
        du[sel] = th * (x - ze[sel]) + ga * (np.abs(x) - np.abs(ze[sel])) + kick[sel]
        xe[sel] = x
        after[r_] = phi * g + du[sel]
        last[r_] = t_
    u = base.ravel().copy()
    u[idx] += du
    h = _ar1(u.reshape(rows, n), phi)
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


class Target:
    """The data's statistics, their variances, and simulations shaped like the data."""

    def __init__(self, R, variance=None):
        self.mask = ~np.isnan(R)
        st = V.stats(R)
        self.keys = list(st)
        self.data = np.array(list(st.values()))
        rows = R.shape[0]
        if variance is None:
            g = np.random.default_rng(SEED_BOOT)
            boot = np.array([list(V.stats(R[g.integers(0, rows, rows)]).values())
                             for _ in range(BOOTSTRAP)])
            variance = np.nanvar(boot, axis=0, ddof=1)
        self.var = variance * (1 + 1 / REPLICAS)
        self.use = ~np.isnan(self.data) & (self.var > 0)
        self.sims = Replicas(self.mask)

    def simulated(self, p):
        with np.errstate(all="ignore"):
            return np.nanmean(self.sims.stats(p), axis=0)

    def distance(self, p):
        m = self.simulated(p)
        bad = self.use & np.isnan(m)
        d = (m - self.data)[self.use & ~bad] ** 2 / self.var[self.use & ~bad]
        return float(d.sum() + 1e6 * bad.sum())


def to_params(x, free, fixed):
    p = dict(fixed)
    for name, v in zip(free, x):
        p[name] = exp(v) if dict((q[0], q[1]) for q in PARAMS)[name] == "log" else v
    return p


def from_params(p, free):
    kind = dict((q[0], q[1]) for q in PARAMS)
    return np.array([log(p[n]) if kind[n] == "log" else p[n] for n in free])


def nelder_mead(f, x0, step=0.2, max_evals=4000, tol=1e-4):
    """Minimize f from x0; adaptive coefficients (Gao and Han 2012) for many dimensions."""
    n = len(x0)
    a, g, c, s = 1.0, 1 + 2 / n, 0.75 - 1 / (2 * n), 1 - 1 / n
    X = [np.array(x0, float)] + [np.array(x0, float) + step * np.eye(n)[i] for i in range(n)]
    F = [f(x) for x in X]
    evals = n + 1
    while evals < max_evals:
        order = np.argsort(F)
        X, F = [X[i] for i in order], [F[i] for i in order]
        if abs(F[-1] - F[0]) <= tol * (abs(F[0]) + 1e-12):
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


def fit(target, start, free_kicks=False, max_evals=4000, label=""):
    fixed = {k: 0.0 for k in KICKS} if not free_kicks else {}
    free = [n for n in NAMES if n not in fixed]
    t0 = time.time()
    count = [0]

    def f(x):
        count[0] += 1
        q = target.distance(to_params(x, free, fixed))
        if count[0] % 200 == 0:
            print(f"    {label} {count[0]} evaluations, {time.time() - t0:.0f}s, "
                  f"distance {q:.1f}", file=sys.stderr)
        return q

    x, q, evals = nelder_mead(f, from_params(start, free), max_evals=max_evals)
    # one restart from the optimum, the usual guard against a collapsed simplex
    x, q, more = nelder_mead(f, x, step=0.1, max_evals=max_evals)
    return to_params(x, free, fixed), q, evals + more, time.time() - t0


def describe(p):
    hl = p["half-life"]
    lines = [f"  half-life {hl:.1f} sessions ({hl / V.MONTH:.1f} months), "
             f"phi {0.5 ** (1 / hl):.4f}; theta {p['theta']:+.4f}, gamma {p['gamma']:+.4f}, "
             f"eta {p['eta']:.4f}"]
    for side in ("up", "down"):
        lines.append(f"  {side:4} jumps: lambda {p[f'lambda {side}']:.3f} a year, size "
                     f"a {p[f'a {side}']:.3f} x Weibull(k {p[f'k {side}']:.3f}), "
                     f"beta {p[f'beta {side}']:.3f}, kick {p[f'kick {side}']:+.3f}")
    return "\n".join(lines)


def table(target, p):
    m = target.simulated(p)
    sd = np.sqrt(target.var)
    print(f"  {'statistic':30} {'data':>9} {'fit':>9} {'z':>6}")
    for k, a, b, s, u in zip(target.keys, target.data, m, sd, target.use):
        z = (b - a) / s if u else float("nan")
        print(f"  {k:30} {a:9.4f} {b:9.4f} {z:6.1f}")


def data_returns(group):
    import jumps
    if group == "sp":
        _, r = jumps.market_returns()
        return r[None, :]
    names, syms, _, R = jumps.universe_returns()
    if group == "all":
        return R
    big = np.array([names[s].cap(names[s].series.days[-1]) >= 20e9 for s in syms])
    return R[big] if group == "big" else R[~big]


def main():
    args = sys.argv[1:]
    group = args[args.index("--group") + 1] if "--group" in args else "all"
    free_kicks = "--kicks" in args
    R = data_returns(group)
    if "--recover" in args:
        truth = dict(START)
        fake = simulate(truth, Draws(R.shape[0], R.shape[1], SEED_FAKE))
        target = Target(np.where(~np.isnan(R), fake, np.nan))
        start = {k: (v * 1.3 if k not in KICKS and v > 0 else v) for k, v in START.items()}
        start["theta"], start["gamma"] = -0.04, 0.04
        p, q, evals, secs = fit(target, start, free_kicks, label="recover")
        print(f"recovery: {evals} evaluations, {secs:.0f}s, distance {q:.1f} over "
              f"{int(target.use.sum())} statistics")
        print(f"  {'parameter':12} {'truth':>9} {'start':>9} {'fitted':>9}")
        for k in NAMES:
            print(f"  {k:12} {truth[k]:9.4f} {start[k]:9.4f} {p[k]:9.4f}")
        table(target, p)
        target.sims.close()
        return
    variance = None
    if group == "sp":
        # One series cannot be resampled by name: the variance is the model's own,
        # across simulated copies of the series at START.
        mask = ~np.isnan(R)
        reps = [list(V.stats(np.where(mask, simulate(START, Draws(1, R.shape[1],
                                                                  SEED_BOOT + k)),
                                      np.nan)).values()) for k in range(BOOTSTRAP // 4)]
        variance = np.nanvar(np.array(reps), axis=0, ddof=1)
    target = Target(R, variance)
    print(f"group {group}: {R.shape[0]} series, {int(target.use.sum())} statistics, "
          f"{REPLICAS} replicas a evaluation; kicks {'free' if free_kicks else 'held at 0'}")
    q0 = target.distance(START)
    p, q, evals, secs = fit(target, START, free_kicks, label=group)
    print(f"distance {q0:.1f} at START, {q:.1f} fitted; {evals} evaluations, {secs:.0f}s\n")
    print(describe(p))
    print()
    table(target, p)
    out = RESULTS.format(group=group + ("-kicks" if free_kicks else ""))
    with open(out, "w") as f:
        json.dump({"group": group, "params": p, "distance": q, "statistics":
                   int(target.use.sum()), "evaluations": evals}, f, indent=1)
    print(f"\nwritten {out}")
    target.sims.close()


if __name__ == "__main__":
    main()
