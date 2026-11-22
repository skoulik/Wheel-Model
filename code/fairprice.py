"""Fair option prices at the volatility state: step 5(c) of the moving-volatility plan.

Decision 4 of `drafts/2026-11-21-moving-volatility-plan.md`: fair prices only the stock's own
diffusive risk. Under the fitted process (`volprocess.py`) volatility has no shocks of its own
-- every move of h is the stock's move -- so the volatility risk decision 4 leaves unpriced is
empty, and the pricing measure is one shift: z moved by κ_t = (μ − r)·Δt/σ_t so that the drift
is r − δ, the jumps and earnings keeping their real-world law, h following the shifted shocks.

**The tables.** Each option is priced at the state it is sold in, which is the two factors
(h_fast, h_slow), the sessions to the next earnings date, and for the call its depth. Prices
come from Monte Carlo at every node of a grid of the two factors, with one set of draws for
every node (so the tables are smooth in the state), stored as log implied volatility, and read
by `volprocess.Tables`, which interpolates cubically in the state (log implied volatility is
convex in it, and linear interpolation priced every option about 0.1% high) and linearly in
depth. For each node:

- **the put** (5 sessions): the strike at the dial p* -- the p*-quantile of the price at
  expiry under the real-world measure, which is what p* means -- and its fair price under the
  pricing measure;
- **the call**, at depths x = ln(K/S) = u·σ·√τ_c for u on U_GRID, below the money as well as
  above, with 20 sessions left (the premium) and with 15, 10 and 5 (what an open call has at
  a put sale: its delta, and its mark if the window ends there). A put's delta is its call's
  by parity.

**Earnings** do not move h, so a path with an earnings date on its j-th session is the same
path times one earnings factor drawn at that session's state: every phase of the earnings
cycle is priced from one set of paths. Phase 0 is a window with no earnings date in it.

**Three variance reductions** keep the Monte Carlo error under the simulator's. One set of
draws serves every node, so the tables are smooth in the state. Each path's total diffusive
shock is stratified (`draws`). And the terminal price is a control variate, with its
regression coefficient for each strike: its fair mean is the forward S·e^((r−δ)τ) exactly,
because each session's drift is compensated exactly. Each node pools CHUNKS sets of PATHS
draws, 800,000 paths. Measured over five sets of draws at a typical node (`--check`), a
put's implied volatility is then good to about 0.07%, a call's to about 0.05% near the money
(0.07% with earnings in its window), 0.4% two standard deviations out and 0.9% three out,
where the premium is a few thousandths of the money's. Plain draws at a quarter of the paths
left 0.3% at the money; a control on the realized variance was tried and gained nothing.
The test that matters is the simulator's: at the pricing drift its excess plus the leak
must be zero (`wheel_sim.py --scenario fittedvol`). With one chunk the tables read 1.1 ±
0.5bp rich there at 5,120 paths, a level common to the whole table; with four, 0.2 ± 0.5bp.

**σ̄** is set by `moments`: the averages of e^(2H), e^(2βH) and e^(2β_E·H) over the stationary
state in the real world, from which the year's total variance is σ². They do not depend on σ̄,
since the state's dynamics are scale-free.

Tables are cached under data/fair/, keyed by everything they depend on. A missing one is built
a row of nodes per worker, BUILD_WORKERS at a time, each regenerating the same seeded draws,
so the result is bit-identical to a serial build (checked 2026-11-22): about five minutes on
the Windows desktop, against seventeen serially.

    python code/fairprice.py --check     # the tables' own checks, at the running example
"""

import hashlib
import json
import os
import sys
from math import erfc, exp, log, pi, sqrt

import numpy as np

import volprocess as VP

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fair")
VERSION = 5
PATHS = 200_000                 # a chunk of draws
CHUNKS = 4                      # chunks pooled at every node: 800,000 paths
BUILD_WORKERS = 8               # rows built at once; each holds its own draws, ~1.6 GB
SEED = 20261122
TP, TC = 5, 20                  # sessions: the weekly put, the four-week call
CALL_TENORS = (5, 10, 15, 20)   # a call's life left at each put sale; the sale is the last
HF_GRID = [round(-0.2 + 0.1 * i, 10) for i in range(13)]
HS_GRID = [round(-0.1 + 0.2 * i, 10) for i in range(11)]
U_GRID = [round(-3.0 + 0.1 * i, 10) for i in range(111)]     # below the money too
MOMENT_ROWS, MOMENT_SESSIONS = 400, 12_000

_erfc = np.vectorize(erfc, otypes=[float])


def _ncdf(x):
    return 0.5 * _erfc(-np.asarray(x, float) / sqrt(2.0))


# ---------------------------------------------------------------------------- the state

def _jump_parts(proc, H, u, w):
    """(log-mgf compensator, jump in units of σ̄, down-jump flag) for arrays H, u, w."""
    s = proc.sig_bar * np.exp(proc.beta * H)
    comp = np.log(1.0 - proc.pu - proc.pd + proc.pu / (1.0 - s * proc.au)
                  + proc.pd / (1.0 + s * proc.ad))
    up = u < proc.pu
    down = (u >= proc.pu) & (u < proc.pu + proc.pd)
    J = np.where(up, proc.au * w, np.where(down, -proc.ad * w, 0.0))
    return comp, s * J, down


def simulate(proc, hf0, hs0, m, excess, draws, final=False):
    """`volprocess.Process.advance` on arrays, from the state (hf0, hs0), no earnings:
    (log S after each session, H at the start of each), and with `final` the factors
    after the last session too. hf0 and hs0 may be arrays."""
    z, u, w = draws["z"], draws["u"], draws["w"]
    T, N = z.shape
    hf = np.broadcast_to(np.asarray(hf0, float), (N,)).copy()
    hs = np.broadcast_to(np.asarray(hs0, float), (N,)).copy()
    logS = np.zeros(N)
    L, Hs = np.empty((T, N)), np.empty((T, N))
    for t in range(T):
        H = np.clip(hf + hs, -VP.H_CLIP, VP.H_CLIP)
        Hs[t] = H
        sd = proc.sig_bar * np.exp(H)
        ret = m * VP.DT - 0.5 * sd * sd + sd * z[t]
        x = z[t] - excess / sd
        if proc.jumps:
            comp, jump, down = _jump_parts(proc, H, u[t], w[t])
            ret = ret - comp + jump
            x = x + jump / sd
            hf = proc.phi_f * hf + proc.th_f * x + proc.k_f * down
            hs = proc.phi_s * hs + proc.th_s * x + proc.k_s * down
        else:
            hf = proc.phi_f * hf + proc.th_f * x
            hs = proc.phi_s * hs + proc.th_s * x
        logS += ret
        L[t] = logS
    return (L, Hs, hf, hs) if final else (L, Hs)


def path_states(proc, n, years, m, seed, daily=False):
    """`volprocess.Process.step` on arrays, for the simulator (TODO INF-9): n whole paths of
    the process at price drift m, each from the stationary state (BURN sessions from h = 0)
    with its own earnings calendar, the earnings term too when `proc` carries one. Kept at
    every fifth session, the simulator's weekly events: {"logS", "hf", "hs"} of shape
    (weeks + 1, n), and "e0", each path's earnings phase. The wheel never feeds back into
    the price, so a batch's paths can be stepped together before its event loop runs, which
    then reads them at the events alone; the draws are numpy's, so the results match the
    session-by-session stepping in distribution, not draw for draw."""
    g = np.random.default_rng(seed)
    T = int(round(years * VP.SESSIONS))
    if T % 5:
        raise ValueError("the simulator's events fall every five sessions")
    hf, hs, logS = np.zeros(n), np.zeros(n), np.zeros(n)
    e0 = g.integers(0, VP.EARNINGS_EVERY, n)
    out = {k: np.empty((T // 5 + 1, n)) for k in ("logS", "hf", "hs")}
    if daily:                       # every close too, for a barrier checked daily
        out["daily"] = np.empty((T + 1, n))
    for t in range(-VP.BURN, T):
        if t >= 0 and t % 5 == 0:
            out["logS"][t // 5], out["hf"][t // 5], out["hs"][t // 5] = logS, hf, hs
        if daily and t >= 0:
            out["daily"][t] = logS
        H = np.clip(hf + hs, -VP.H_CLIP, VP.H_CLIP)
        sd = proc.sig_bar * np.exp(H)
        z, u, w = g.standard_normal(n), g.random(n), g.exponential(size=n)
        ret = m * VP.DT - 0.5 * sd * sd + sd * z
        x = z
        down = 0.0
        if proc.jumps:
            comp, jump, down = _jump_parts(proc, H, u, w)
            ret = ret - comp + jump
            x = x + jump / sd
        nf = proc.phi_f * hf + proc.th_f * x + proc.k_f * down
        ns = proc.phi_s * hs + proc.th_s * x + proc.k_s * down
        if proc.earnings and t >= 0:
            earn = (t - e0) % VP.EARNINGS_EVERY == 0
            if earn.any():
                ue, we = g.random(n), g.exponential(size=n)
                ret = np.where(earn, ret + earnings_factor(proc, H, ue, we), ret)
                if proc.efb:
                    Y = np.where(ue < proc.pe, proc.aeu, -proc.aed) * we
                    dh = np.where(earn, -proc.efb[0] + proc.efb[1]
                                  * np.maximum(np.abs(Y) / proc.ey - 1.0, 0.0), 0.0)
                    nf = nf + proc.kf_share * dh
                    ns = ns + (1.0 - proc.kf_share) * dh
        hf, hs = nf, ns
        if t >= 0:
            logS = logS + ret
    out["logS"][T // 5], out["hf"][T // 5], out["hs"][T // 5] = logS, hf, hs
    if daily:
        out["daily"][T] = logS
    out["e0"] = e0
    return out


def boundaries(proc, n=400, years=200, seed=SEED):
    """§10's two boundaries under `proc`, as convexity costs a year (step 7 of the plan): lots
    return iff mu - delta > c1, and their capital iff mu - delta > c2 -- sigma^2/2 and sigma^2
    at constant sigma. With the price drift compensated, c1 is the long-run drag of log S,
    the mean over the state of K+(H) - E[noise] a session; c2 is the long-run growth of
    E[S_0/S_T], the mean of K+(H) + K-(H), K the noise's log moment generating function at
    +1 and -1. The second mean is taken along the path tilted by e^(-log S), z shifted by
    -sigma_t and the jumps tilted, which by the change of measure makes it exact. Earnings
    sessions add their own cumulants; they do not move h, so the tilt leaves them be."""
    g = np.random.default_rng(seed)
    T = int(years * VP.SESSIONS)
    p = proc
    out = {}
    for tilt in (False, True):
        hf, hs = np.zeros(n), np.zeros(n)
        acc = np.zeros(n)
        cnt = 0
        for t in range(-VP.BURN, T):
            H = np.clip(hf + hs, -VP.H_CLIP, VP.H_CLIP)
            sd = p.sig_bar * np.exp(H)
            s = p.sig_bar * np.exp(p.beta * H)
            nj = 1.0 - p.pu - p.pd
            kp = 0.5 * sd * sd + (np.log(nj + p.pu / (1 - s * p.au) + p.pd / (1 + s * p.ad))
                                  if p.jumps else 0.0)
            km = 0.5 * sd * sd + (np.log(nj + p.pu / (1 + s * p.au) + p.pd / (1 - s * p.ad))
                                  if p.jumps else 0.0)
            mean = s * (p.pu * p.au - p.pd * p.ad) if p.jumps else 0.0
            if t >= 0:
                acc += (kp + km) if tilt else (kp - mean)
                if p.earnings and t % VP.EARNINGS_EVERY == 0:
                    se = p.sig_bar * np.exp(p.be * H)
                    ep = np.log(p.pe / (1 - se * p.aeu) + (1 - p.pe) / (1 + se * p.aed))
                    em = np.log(p.pe / (1 + se * p.aeu) + (1 - p.pe) / (1 - se * p.aed))
                    emean = se * (p.pe * p.aeu - (1 - p.pe) * p.aed)
                    acc += (ep + em) if tilt else (ep - emean)
                cnt += 1
            z = g.standard_normal(n) - (sd if tilt else 0.0)
            u, w = g.random(n), g.exponential(size=n)
            x = z
            down = 0.0
            if p.jumps:
                if tilt:
                    a_u, a_d = p.pu / (1 + s * p.au), p.pd / (1 - s * p.ad)
                    D = nj + a_u + a_d
                    up, down = u < a_u / D, (u >= a_u / D) & (u < (a_u + a_d) / D)
                    J = np.where(up, p.au / (1 + s * p.au) * w,
                                 np.where(down, -p.ad / (1 - s * p.ad) * w, 0.0))
                else:
                    up, down = u < p.pu, (u >= p.pu) & (u < p.pu + p.pd)
                    J = np.where(up, p.au * w, np.where(down, -p.ad * w, 0.0))
                x = x + s * J / sd
            hf = p.phi_f * hf + p.th_f * x + p.k_f * down
            hs = p.phi_s * hs + p.th_s * x + p.k_s * down
        rate = acc / cnt * VP.SESSIONS
        out["c2" if tilt else "c1"] = (float(rate.mean()), float(rate.std(ddof=1) / sqrt(n)))
    return out


def earnings_factor(proc, H, ue, we):
    """Log of the earnings session's gross return beyond its diffusion, at state H."""
    if not proc.earnings:
        return np.zeros_like(H)
    s = proc.sig_bar * np.exp(proc.be * H)
    comp = np.log(proc.pe / (1.0 - s * proc.aeu) + (1.0 - proc.pe) / (1.0 + s * proc.aed))
    Y = np.where(ue < proc.pe, proc.aeu, -proc.aed) * we
    return s * Y - comp


def _ndtri(p):
    """The standard normal quantile, elementwise: Acklam's rational approximation and one
    Halley step, good to about 1e-15."""
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    p = np.asarray(p, float)
    x = np.empty_like(p)
    lo, hi = p < 0.02425, p > 1 - 0.02425
    mid = ~(lo | hi)
    for sel, q, sign in ((lo, np.sqrt(-2 * np.log(p[lo])), 1.0),
                         (hi, np.sqrt(-2 * np.log1p(-p[hi])), -1.0)):
        x[sel] = sign * ((((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
                         / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1))
    q = p[mid] - 0.5
    t = q * q
    x[mid] = ((((((a[0] * t + a[1]) * t + a[2]) * t + a[3]) * t + a[4]) * t + a[5]) * q
              / (((((b[0] * t + b[1]) * t + b[2]) * t + b[3]) * t + b[4]) * t + 1))
    e = _ncdf(x) - p
    u = e * sqrt(2 * pi) * np.exp(0.5 * x * x)
    return x - u / (1 + 0.5 * x * u)


def _strata(g, shape):
    """Uniforms stratified along the last axis: one in each of N equal cells, shuffled."""
    N = shape[-1]
    return (np.argsort(g.random(shape), axis=-1) + g.random(shape)) / N


def draws(T, N, seed):
    """One set of draws for N paths of T sessions, stratified where the price is made. Each
    path's total diffusive shock is stratified -- one path in each of N equal-probability
    cells of its N(0, T) law -- and spread over the sessions by a Brownian bridge (the
    sessions' shocks less their mean, plus the total's share), which leaves the shocks iid
    standard normal; the jump draws are stratified session by session, and the earnings
    draws once. A table's error is then a few hundredths of a percent where plain draws
    leave tenths."""
    g = np.random.default_rng(seed)
    xi = g.standard_normal((T, N))
    total = _ndtri(_strata(g, (N,))) * sqrt(T)
    z = xi - xi.mean(axis=0, keepdims=True) + total / T
    return {"z": z, "u": _strata(g, (T, N)), "w": -np.log1p(-_strata(g, (T, N))),
            "ue": _strata(g, (N,)), "we": -np.log1p(-_strata(g, (N,)))}


def draw_sets(seed, chunks=None):
    """The draws `node_prices` pools: CHUNKS sets (or `chunks`) of the three it takes,
    each of PATHS paths. Chunk c's seeds are seed + 10c and the two after it."""
    return [{"strike": draws(TP, PATHS, seed + 10 * c + 1),
             "put": draws(TP, PATHS, seed + 10 * c + 2),
             "call": draws(TC, PATHS, seed + 10 * c)}
            for c in range(CHUNKS if chunks is None else chunks)]


def moments(jumps=True, earnings=True, seed=SEED):
    """Stationary real-world averages of e^(2H), e^(2βH), e^(2β_E·H), and H's quantiles."""
    proc = VP.Process(1.0, jumps, earnings)        # the state's dynamics ignore σ̄
    g = np.random.default_rng(seed)
    hf, hs = np.zeros(MOMENT_ROWS), np.zeros(MOMENT_ROWS)
    acc = np.zeros(3)
    n = 0
    Hs = []
    chunk = 500
    for start in range(0, VP.BURN + MOMENT_SESSIONS, chunk):
        T = min(chunk, VP.BURN + MOMENT_SESSIONS - start)
        d = {"z": g.standard_normal((T, MOMENT_ROWS)), "u": g.random((T, MOMENT_ROWS)),
             "w": g.exponential(size=(T, MOMENT_ROWS))}
        _, H, hf, hs = simulate(proc, hf, hs, 0.0, 0.0, d, final=True)
        keep = H[max(0, VP.BURN - start):]
        if keep.size:
            acc += [np.exp(2 * keep).sum(), np.exp(2 * proc.beta * keep).sum(),
                    np.exp(2 * proc.be * keep).sum()]
            n += keep.size
            Hs.append(keep[::10].ravel())
    Hs = np.concatenate(Hs)
    return {"e2H": acc[0] / n, "e2bH": acc[1] / n, "e2bEH": acc[2] / n,
            "H quantiles": dict(zip(("0.1%", "5%", "50%", "95%", "99.9%"),
                                    np.quantile(Hs, [0.001, 0.05, 0.5, 0.95, 0.999]).tolist()))}


def sig_bar(sigma, mom, jumps=True, earnings=True):
    """σ̄, per session, at which the year's total variance averages σ²."""
    p = VP.Process(1.0, jumps, earnings)
    var_j = p.pu * 2 * p.au ** 2 + p.pd * 2 * p.ad ** 2 - (p.pu * p.au - p.pd * p.ad) ** 2
    var_e = (p.pe * 2 * p.aeu ** 2 + (1 - p.pe) * 2 * p.aed ** 2
             - (p.pe * p.aeu - (1 - p.pe) * p.aed) ** 2) if earnings else 0.0
    v1 = mom["e2H"] + var_j * mom["e2bH"] + var_e / VP.EARNINGS_EVERY * mom["e2bEH"]
    return sigma / sqrt(VP.SESSIONS * v1)


# ---------------------------------------------------------------------------- prices

def bs(kind, k, tau, sig, r, delta):
    """Black-Scholes, spot 1, strike k: the formula of model.bs_call / bs_put, on arrays."""
    k, sig = np.asarray(k, float), np.asarray(sig, float)
    st = sig * sqrt(tau)
    d1 = (-np.log(k) + (r - delta + 0.5 * sig * sig) * tau) / st
    d2 = d1 - st
    if kind == "call":
        return exp(-delta * tau) * _ncdf(d1) - k * exp(-r * tau) * _ncdf(d2)
    return k * exp(-r * tau) * _ncdf(-d2) - exp(-delta * tau) * _ncdf(-d1)


def implied(kind, price, k, tau, r, delta, lo=1e-4, hi=5.0, iters=70):
    """Implied volatility by bisection, elementwise; NaN where the price is below the
    zero-volatility bound or too small to carry one."""
    price, k = np.broadcast_arrays(np.asarray(price, float), np.asarray(k, float))
    a, b = np.full(price.shape, lo), np.full(price.shape, hi)
    for _ in range(iters):
        mid = 0.5 * (a + b)
        high = bs(kind, k, tau, mid, r, delta) > price
        b, a = np.where(high, mid, b), np.where(high, a, mid)
    iv = 0.5 * (a + b)
    floor = bs(kind, k, tau, np.full(price.shape, lo), r, delta)
    return np.where((price > floor + 1e-13) & (price > 1e-12), iv, np.nan)


def _fill(lniv):
    """Carry the last defined value outward along the last axis (deep calls priced at
    nothing), and the first one inward."""
    out = lniv.copy()
    flat = out.reshape(-1, out.shape[-1])
    for row in flat:
        ok = np.isfinite(row)
        if not ok.any():
            row[:] = np.log(0.2)
            continue
        idx = np.where(ok, np.arange(row.size), 0)
        np.maximum.accumulate(idx, out=idx)
        row[:] = row[idx]
        first = np.argmax(ok)
        row[:first] = row[first]
    return out


def node_prices(proc, hf0, hs0, run, chunks, u_grid=U_GRID):
    """At one node: the put's (log k*, ln iv) per phase, and {tenor: the call's ln iv per
    phase and depth} for each of CALL_TENORS. `chunks` is a list of draw sets (`draw_sets`),
    pooled: each holds three, stratified at its own expiry (`draws`) -- "strike" (the put's
    tenor, real world), "put" (the put's tenor, pricing measure, which also prices the
    five-session call), "call" (the call's, pricing measure, which prices the longer ones).
    The strike is the quantile of every chunk's paths together, and each price uses every
    chunk's sums, control variate included, so the pool is one sample of chunks x PATHS.
    The calls at fewer than twenty sessions are for an open call's delta and its mark at
    the window's end; the premiums are the full-tenor ones."""
    r, delta, mu, p_star = run["r"], run["delta"], run["mu"], run["p_star"]
    excess = (mu - r) * VP.DT
    tp = TP * VP.DT
    # The strike first: the real-world quantile over the whole pool.
    RP = [[] for _ in range(TP + 1)]
    for ds in chunks:
        dp = ds["strike"]
        Lp, Hp = simulate(proc, hf0, hs0, mu - delta, 0.0, dp)
        for phase in range(TP + 1):
            ep = earnings_factor(proc, Hp[phase - 1], dp["ue"], dp["we"]) if phase else 0.0
            RP[phase].append(np.exp(Lp[TP - 1] + ep))
    ks = [float(np.quantile(np.concatenate(x), p_star)) for x in RP]
    # Then the prices, from sums accumulated chunk by chunk: for each payoff, its sum and
    # its sum times the terminal price, and the terminal price's first two moments.
    K = np.exp(np.array(u_grid) * run["u scale"])
    put_acc = np.zeros((TP + 1, 4))                 # sum pay, sum pay*R, sum R, sum R^2
    call_acc = {t: [np.zeros((t + 1, len(K))), np.zeros((t + 1, len(K))),
                    np.zeros(t + 1), np.zeros(t + 1)] for t in CALL_TENORS}
    n_paths = 0
    for ds in chunks:
        d5, dq = ds["put"], ds["call"]
        L5, H5 = simulate(proc, hf0, hs0, r - delta, excess, d5)
        Lq, Hq = simulate(proc, hf0, hs0, r - delta, excess, dq)
        n_paths += d5["z"].shape[1]
        for phase in range(TP + 1):
            eq = earnings_factor(proc, H5[phase - 1], d5["ue"], d5["we"]) if phase else 0.0
            RQ = np.exp(L5[TP - 1] + eq)
            pay = np.maximum(ks[phase] - RQ, 0.0)
            put_acc[phase] += (pay.sum(), (pay * RQ).sum(), RQ.sum(), (RQ * RQ).sum())
        for tenor in CALL_TENORS:
            Lc, Hc, dc = (L5, H5, d5) if tenor == TP else (Lq, Hq, dq)
            sp, spr, sr, srr = call_acc[tenor]
            for phase in range(tenor + 1):
                eq = earnings_factor(proc, Hc[phase - 1], dc["ue"], dc["we"]) if phase else 0.0
                R = np.sort(np.exp(Lc[tenor - 1] + eq))
                t1 = np.concatenate([np.cumsum(R[::-1])[::-1], [0.0]])       # sum of R[i:]
                t2 = np.concatenate([np.cumsum((R * R)[::-1])[::-1], [0.0]])
                i = np.searchsorted(R, K, side="right")
                n, s1, s2 = R.size - i, t1[i], t2[i]
                sp[phase] += s1 - K * n                  # sum (R - K)+
                spr[phase] += s2 - K * s1                # sum (R - K)+ * R
                sr[phase] += t1[0]
                srr[phase] += t2[0]

    def priced(s_pay, s_payr, s_r, s_rr, tau):
        """The control-variate price from pooled sums: the payoff's mean less its
        regression on the terminal price times that price's error against its forward."""
        pay, payr, m1, m2 = s_pay / n_paths, s_payr / n_paths, s_r / n_paths, s_rr / n_paths
        b = (payr - pay * m1) / (m2 - m1 * m1)
        return exp(-r * tau) * (pay - b * (m1 - exp((r - delta) * tau)))

    out_put_k, out_put_iv = [], []
    for phase in range(TP + 1):
        price = priced(*put_acc[phase], tp)
        out_put_k.append(log(ks[phase]))
        out_put_iv.append(float(np.log(implied("put", price, ks[phase], tp, r, delta))))
    calls = {}
    for tenor in CALL_TENORS:
        sp, spr, sr, srr = call_acc[tenor]
        tau = tenor * VP.DT
        calls[tenor] = np.array([
            np.log(implied("call", priced(sp[ph], spr[ph], sr[ph], srr[ph], tau), K, tau,
                           r, delta)) for ph in range(tenor + 1)])
    return out_put_k, out_put_iv, calls


def _key(run):
    k = dict(run, version=VERSION, paths=PATHS, seed=SEED, tp=TP, tc=TC, hf=HF_GRID,
             hs=HS_GRID, u=U_GRID, fit=VP.FIT, earn=VP.EARN, burn=VP.BURN,
             sessions=VP.SESSIONS, every=VP.EARNINGS_EVERY)
    return k, hashlib.sha1(json.dumps(k, sort_keys=True).encode()).hexdigest()[:12]


def _build_row(job):
    """One row of the tables, every node at h_fast = HF_GRID[i]: a pmap worker."""
    sb, run, i = job
    proc = VP.Process(sb, run["jumps"], run["earnings"])
    ds = draw_sets(SEED)
    return [node_prices(proc, HF_GRID[i], hs, run, ds) for hs in HS_GRID]


def build(run, verbose=True):
    """The tables for one run's parameters (a dict: sigma, mu, r, delta, p_star, jumps,
    earnings), as `volprocess.Tables` reads them."""
    mom = moments(run["jumps"], run["earnings"])
    sb = sig_bar(run["sigma"], mom, run["jumps"], run["earnings"])
    proc = VP.Process(sb, run["jumps"], run["earnings"])
    run = dict(run, **{"u scale": run["sigma"] * sqrt(TC * VP.DT)})
    nf, ns = len(HF_GRID), len(HS_GRID)
    put_k = np.empty((TP + 1, nf, ns))
    put_iv = np.empty((TP + 1, nf, ns))
    call = {t: np.empty((t + 1, nf, ns, len(U_GRID))) for t in CALL_TENORS}
    jobs = [(sb, run, i) for i in range(nf)]
    # A row of nodes a worker: each regenerates the same draws from the same seeds, so the
    # tables are bit-identical however many workers build them. Inside a worker (a table
    # missing when a pool's job asks for it) the rows run serially, as pmap requires.
    from multiprocessing import parent_process
    if parent_process() is None:
        from model import pmap
        rows = pmap(_build_row, jobs, workers=min(BUILD_WORKERS, os.cpu_count() or 1))
    else:
        rows = [_build_row(job) for job in jobs]
    for i, row in enumerate(rows):
        for j, (pk, piv, c) in enumerate(row):
            put_k[:, i, j], put_iv[:, i, j] = pk, piv
            for t in CALL_TENORS:
                call[t][:, i, j, :] = c[t]
    if verbose:
        print(f"  fairprice: {nf} rows built", file=sys.stderr, flush=True)
    return {"hf": HF_GRID, "hs": HS_GRID, "u": U_GRID, "u scale": run["u scale"],
            "sig bar": sb, "moments": mom,
            "put": {"logk": put_k.tolist(), "lniv": _fill(put_iv).tolist()},
            "call": {"lniv": {str(t): _fill(call[t]).tolist() for t in CALL_TENORS}}}


def load(run, verbose=True):
    """The tables for `run`, from the cache or built and cached."""
    key, h = _key(run)
    path = os.path.join(CACHE, f"tables-{h}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    data = build(run, verbose)
    data["key"] = key
    os.makedirs(CACHE, exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(data, f)
    os.replace(path + ".tmp", path)
    return data


# ---------------------------------------------------------------------------- checks

def _ui(u):
    """The index of depth u on U_GRID."""
    return int(round((u - U_GRID[0]) / (U_GRID[1] - U_GRID[0])))


RUNNING = {"sigma": 0.20, "mu": 0.07, "r": 0.05, "delta": 0.025, "p_star": 0.20,
           "jumps": True, "earnings": True}


def check(run=RUNNING):
    """The tables' checks: the stepping agrees with `volprocess`, σ̄ gives σ, the
    moments are converged, and the tables price off-grid states as a fresh Monte Carlo
    does."""
    data = load(run)
    T = VP.Tables(data)
    proc = VP.Process(data["sig bar"], run["jumps"], run["earnings"])
    print(f"sigma bar {data['sig bar']:.6f} a session; moments {data['moments']}")

    # 1. the arithmetic: volprocess.advance and simulate on one set of draws
    d = draws(TC, 50, 7)
    L, H = simulate(proc, 0.3, 0.8, run["r"] - run["delta"], (run["mu"] - run["r"]) * VP.DT, d)
    worst = 0.0
    for n in range(50):
        logS, hf, hs = 0.0, 0.3, 0.8
        for t in range(TC):
            logS, hf, hs = proc.advance(logS, hf, hs, run["r"] - run["delta"],
                                        (run["mu"] - run["r"]) * VP.DT, False,
                                        d["z"][t, n], d["u"][t, n], d["w"][t, n], 0.0, 0.0)
            worst = max(worst, abs(logS - L[t, n]))
    print(f"1. volprocess against the array stepping, 50 paths x {TC} sessions: "
          f"largest difference {worst:.1e}")

    # 2. the year's variance, by simulation in the real world from the stationary state
    mom2 = moments(run["jumps"], run["earnings"], seed=SEED + 99)
    print(f"2. moments again on other draws: " + ", ".join(
        f"{k} {mom2[k] / data['moments'][k] - 1:+.2%}" for k in ("e2H", "e2bH", "e2bEH")))
    g = np.random.default_rng(5)
    rows, years = 400, 6
    sess = years * VP.SESSIONS
    dd = {"z": g.standard_normal((VP.BURN, rows)), "u": g.random((VP.BURN, rows)),
          "w": g.exponential(size=(VP.BURN, rows))}
    _, _, hf0, hs0 = simulate(proc, 0.0, 0.0, run["mu"] - run["delta"], 0.0, dd, final=True)
    dd = {"z": g.standard_normal((sess, rows)), "u": g.random((sess, rows)),
          "w": g.exponential(size=(sess, rows))}
    L, H = simulate(proc, hf0, hs0, run["mu"] - run["delta"], 0.0, dd)
    r_day = np.diff(np.vstack([np.zeros(rows), L]), axis=0)
    if run["earnings"]:
        phase = g.integers(0, VP.EARNINGS_EVERY, rows)
        for n in range(rows):
            idx = np.arange(phase[n], sess, VP.EARNINGS_EVERY)
            r_day[idx, n] += earnings_factor(proc, H[idx, n], g.random(idx.size),
                                             g.exponential(size=idx.size))
    annual = r_day.var() * VP.SESSIONS
    print(f"   the year's variance on {rows} x {years} years: sd {sqrt(annual):.4f} "
          f"against sigma {run['sigma']:.4f}; mean gross return a session "
          f"{np.exp(r_day).mean() - 1:.3e} against {exp((run['mu'] - run['delta']) * VP.DT) - 1:.3e}")

    # 3. interpolation: off-grid states priced on the tables' own draws, so that the
    # difference is the interpolation's alone
    run2 = dict(run, **{"u scale": data["u scale"]})
    ds = draw_sets(SEED)
    picks = [(0.03, 0.55), (0.27, 0.93), (-0.08, 0.31), (0.61, 1.27), (0.12, 0.74),
             (0.45, 1.61)]
    print("3. interpolation, off-grid states on the tables' draws: table / direct - 1 for "
          "the strike, the put's iv, the call's at u = 0.5, 1, 2, 3; phases 0 and 3")
    for hf, hs in picks:
        pk, piv, c = node_prices(proc, hf, hs, run2, ds)
        for phase in (0, 3):
            k_t, iv_t = T.put(hf, hs, phase)
            rel = [k_t / exp(pk[phase]) - 1, iv_t / exp(piv[phase]) - 1] + [
                T.call_iv(hf, hs, phase, u * data["u scale"]) / exp(c[TC][phase][_ui(u)]) - 1
                for u in (0.5, 1, 2, 3)]
            print(f"   hf {hf:+.2f} hs {hs:.2f} ph {phase}: "
                  + "  ".join(f"{v:+.3%}" for v in rel))

    # 3b. between depth nodes, where the call is linear in u
    us = [0.05, 0.25, 0.55, 0.75, 1.05, 1.45, 1.95, 2.45]
    print("   between depth nodes, u = " + ", ".join(f"{u:g}" for u in us) + ":")
    for hf, hs in picks[:3]:
        _, _, c = node_prices(proc, hf, hs, run2, ds, u_grid=us)
        for phase in (0, 3):
            print(f"   hf {hf:+.2f} hs {hs:.2f} ph {phase}: " + "  ".join(
                f"{T.call_iv(hf, hs, phase, u * data['u scale']) / exp(c[TC][phase][n]) - 1:+.3%}"
                for n, u in enumerate(us)))

    # 4. Monte Carlo error: one node priced on five other sets of draws
    rows = []
    for seed in range(5):
        pk, piv, c = node_prices(proc, 0.1, 0.7, run2, draw_sets(SEED + 1000 + 100 * seed))
        rows.append([exp(pk[0]), exp(piv[0]), exp(piv[3])]
                    + [exp(c[TC][0][_ui(u)]) for u in (0.5, 1, 2, 3)]
                    + [exp(c[TC][3][_ui(1)])])
    rows = np.array(rows)
    print("4. Monte Carlo error at (0.1, 0.7), relative sd over five sets of draws: strike "
          "{:.3%}, put iv {:.3%} (with earnings {:.3%}), call iv at u = 0.5, 1, 2, 3 "
          "{:.3%} {:.3%} {:.3%} {:.3%} (with earnings, u = 1: {:.3%})".format(
              *(rows.std(axis=0, ddof=1) / rows.mean(axis=0))))


def report_boundaries(sigma=0.20):
    """§10's boundaries for the four processes of step 7, each at total variance sigma^2."""
    print(f"§10's boundaries at sigma = {sigma:.2f}: lots return iff mu - delta > c1, their "
          f"capital iff mu - delta > c2 (a year)")
    print(f"  constant sigma: c1 {sigma ** 2 / 2:.4f}, c2 {sigma ** 2:.4f}")
    for name, jumps, earnings in (("factors", False, False), ("+jumps", True, False),
                                  ("full", True, True)):
        sb = sig_bar(sigma, moments(jumps, earnings), jumps, earnings)
        b = boundaries(VP.Process(sb, jumps, earnings))
        print(f"  {name:8}: c1 {b['c1'][0]:.4f} ± {b['c1'][1]:.4f}, "
              f"c2 {b['c2'][0]:.4f} ± {b['c2'][1]:.4f}", flush=True)


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    if "--boundaries" in sys.argv:
        report_boundaries()
