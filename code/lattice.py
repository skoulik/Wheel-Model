"""The moving-volatility lattice behind `model.py`: step 1 of
`drafts/2026-11-22-model-moving-volatility-plan.md`.

Under the fitted process (`volprocess.py`) a lot's depth is no longer a walk with independent
steps: a period's move depends on the volatility, and the volatility on the moves before it.
The state that makes the walk Markov again is the depth together with the two volatility
factors and the week of the earnings cycle. This module tabulates, for every node of a grid
of the two factors, what `model.py` needs to step that state a call period at a time and to
book the ledger at it. Nothing here is a formula of the model's: the walk and the ledger stay
in `model.py`; this is the fitted process, simulated from each node.

**The grid** (decision 2): h_fast from -0.2 to 1.4 and h_slow from 0.0 to 2.3, spacing 0.1.
A lot's volatility at the end of a period lands between nodes and is shared between the four
around it, so that its mean is where the process put it.

**The draws** (decision 3): one set of `fairprice.draws` -- each path's total diffusive shock
stratified -- shared by every node, so the tables are smooth in the state, PATHS a node,
stepped by `fairprice.simulate` in the real world and under the pricing measure on the same
draws. Each node's moves are shifted by one constant so that their gross return averages
e^(m*tau) exactly, which the process's compensation makes true and the ledger's exact tests
need of every node (test 5 of the plan).

**The chain and sigma-bar.** The volatility's dynamics under the real world do not depend on
sigma-bar, so the nodes' transition is built first and its stationary law found, which
weights the put's sale states. sigma-bar, the scale at which the year's total variance --
diffusion, jumps and earnings -- averages sigma^2, is the process's own, measured by
`fairprice.moments` from 1.6 million independent stationary reads and shared with the
simulator (decision 9). The lattice's own law would put it 0.65% lower, its grid's spread
being a little wide (decision 2, test 2).

**What each node gives** (for every grid the model runs, `GRIDS`), as means over its paths:
- the walk's transition: where its lots' volatility goes, jointly with the offset of their
  depth, floor(1/2 - R/h) as `model.DepthWalk` bins it;
- the call, for each kind of period (no earnings, or earnings in each of its four weeks, the
  session within the week averaged) and every depth x: over the paths with R >= x, the
  count and the sums of e^R, e^2R and R in the real world, and of e^R under the pricing
  measure, from which the model reads the fair premium, the exits and the betas; and, on
  the near grid, the sums of e^R times the volatility's channel of the life delta in both;
- the put, for each kind of week (no earnings, or earnings on each of its five sessions):
  the strike at the dial, its premium, mark loss, implied volatility and life delta, and
  the entry depth jointly with the volatility at entry, summed over the sale state's
  stationary law.

**The exact entry** (decision 10): puts are not sold at nodes. Eight million sales are read
from exact stationary states, each at a uniform point of the earnings calendar, and their
put's week and their lot's first call period stepped from that state; the grid takes the
surviving lots over at the start of their second call period (`_exact_chunk`). The gap at
assignment, its tail and the first expiry carry no grid; the nodes' put rows above serve
only to interpolate each sale's strike.

**The life delta** is first order in kappa_t = (mu - r)*dt/sigma_t, the shift of each session's
shock between the two measures, taken pathwise: d log S_T / d z_t carried forward through the
volatility's response, in the direction kappa, along both measures' paths and averaged (the
trapezoid in the drift). The price's channel is the shock's direct effect with the
volatility's path held, which is exactly the period's length; the volatility's channel is
the rest.

Run:  python code/lattice.py            # the running example's lattice, built and cached
      python code/lattice.py --still    # the volatility held still, for step 2's check
"""

import hashlib
import json
import os
import sys
import time
from math import exp, sqrt

import numpy as np

import fairprice as FP
import volprocess as VP

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "lattice")
VERSION = 2                           # the tables; 2: sigma-bar from fairprice.moments
EXACT_VERSION = 2                     # the exact entry (decision 10); 2: the dial per kind
PATHS = 200_000
SEED = 20261123
TP, TC = FP.TP, FP.TC                 # sessions: the weekly put, the four-week call
HF_GRID = [round(-0.2 + 0.1 * i, 10) for i in range(17)]
HS_GRID = [round(0.1 * j, 10) for j in range(24)]
# The model's grids: (cell width h, deepest depth).  "near" serves every finite horizon and
# the census; "coarse" and "fine" are the stationary figures' Richardson pair.
GRIDS = {"near": (0.01, 8.0), "coarse": (0.025, 20.0), "fine": (0.0125, 20.0)}
REACH = 1.2                           # a period's log move kept within +-REACH (see _offsets)
GAP_BINS = np.linspace(0.0, 0.5, 1001)
BUILD_WORKERS = 16
EARN_WEEKS = 13                       # the earnings calendar, in weeks
EXACT_PATHS = 2_000_000               # decision 10: stationary paths for the exact entry,
EXACT_READS = 4                       # ...each read this many times (8 million sales),
EXACT_CHUNKS = 8                      # ...in this many workers
PUT_KINDS = TP + 1                    # 0: no earnings in the week; 1 + o: on its session o
CALL_KINDS = 5                        # 0: none in the period; 1 + w: in its week w
# The put's row: what each column of data["put"][node, kind] holds.
PUT_COLS = ("log k", "premium", "mark loss", "assigned", "x0 sum", "drop sum",
            "e^R below P", "e^R G below P", "e^R below Q", "e^R G below Q", "iv", "below Q")


# ---------------------------------------------------------------------------- the process

def process(run, sig_bar):
    """`volprocess.Process` for `run`; with run["still"] the volatility is held still -- no
    response to the moves, no jumps, no earnings -- which is constant sigma on the lattice
    (step 2's structural check)."""
    if run.get("still"):
        p = VP.Process(sig_bar, False, False)
        p.th_f = p.th_s = p.k_f = p.k_s = 0.0
        return p
    return VP.Process(sig_bar, run["jumps"], run["earnings"])


def grid(run):
    """(h_fast nodes, h_slow nodes): one node at zero when the volatility is still.
    run["hs step"], when given, is h_slow's spacing in place of HS_GRID's 0.1 over the
    same range: decision 2's fallback."""
    if run.get("still"):
        return np.array([0.0]), np.array([0.0])
    if not run["jumps"]:
        # The factors alone: with no kick the volatility moves only through theta, its
        # stationary sd about 0.045 in h_fast and 0.073 in h_slow around zero -- under the
        # jumps' grid's spacing, and partly below its floor of zero.  The same spacing per
        # stationary sd as the jumps' grid, about a third of h_slow's, over +-4.5 sd.
        return (np.round(np.arange(-0.2, 0.2 + 1e-9, 0.025), 10),
                np.round(np.arange(-0.35, 0.35 + 1e-9, 0.025), 10))
    if run.get("hs step"):
        step = run["hs step"]
        return np.array(HF_GRID), np.round(np.arange(0.0, HS_GRID[-1] + 1e-9, step), 10)
    return np.array(HF_GRID), np.array(HS_GRID)


def split(HF, HS, hf, hs):
    """Each end state shared linearly between the four nodes around it, clamped to the grid:
    (node index [4, n], weight [4, n])."""
    ns = HS.size

    def axis(v, g):
        if g.size == 1:
            return np.zeros(v.shape, int), np.zeros(v.shape), 0
        a = np.clip((v - g[0]) / (g[1] - g[0]), 0.0, g.size - 1 - 1e-12)
        i = a.astype(int)
        return i, a - i, 1

    i, ti, si = axis(hf, HF)
    j, tj, sj = axis(hs, HS)
    idx = np.stack([i * ns + j, (i + si) * ns + j, i * ns + j + sj, (i + si) * ns + j + sj])
    w = np.stack([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj])
    return idx, w


def _comp_slope(proc, H):
    """d/dH of the jumps' log-mgf compensator, `volprocess.Process.log_jump_mgf`."""
    s = proc.sig_bar * np.exp(proc.beta * H)
    A = 1.0 - proc.pu - proc.pd + proc.pu / (1.0 - s * proc.au) + proc.pd / (1.0 + s * proc.ad)
    dA = proc.pu * proc.au / (1.0 - s * proc.au) ** 2 - proc.pd * proc.ad / (1.0 + s * proc.ad) ** 2
    return proc.beta * s * dA / A


def _earn(proc, H, ue, we):
    """(log of the earnings session's gross return beyond its diffusion, its slope in H)."""
    s = proc.sig_bar * np.exp(proc.be * H)
    Y = np.where(ue < proc.pe, proc.aeu, -proc.aed) * we
    A = proc.pe / (1.0 - s * proc.aeu) + (1.0 - proc.pe) / (1.0 + s * proc.aed)
    dA = (proc.pe * proc.aeu / (1.0 - s * proc.aeu) ** 2
          - (1.0 - proc.pe) * proc.aed / (1.0 + s * proc.aed) ** 2)
    return s * Y - np.log(A), proc.be * s * (Y - dA / A)


def paths(proc, hf0, hs0, m, excess, d):
    """One node's paths: `fairprice.simulate` from (hf0, hs0), then the pathwise derivative of
    the log return in the direction kappa_t = dt/sigma_t (per unit of mu - r).

    Returns {"R": the period's log return, "hf", "hs": the factors at its end, "H": the state
    at the start of each session, "Gv": the volatility's channel of the derivative (the
    price's is exactly the period's length, since kappa_t*sigma_t = dt), "dH": the state's
    derivative at each session, for an earnings jump's own channel}."""
    L, Hs, hf, hs = FP.simulate(proc, hf0, hs0, m, excess, d, final=True)
    T, N = d["z"].shape
    dt = VP.DT
    dhf, dhs = np.zeros(N), np.zeros(N)
    Gv = np.zeros(N)
    dHs = np.empty((T, N))
    for t in range(T):
        H = Hs[t]
        dH = np.where(np.abs(H) < VP.H_CLIP, dhf + dhs, 0.0)
        dHs[t] = dH
        sd = proc.sig_bar * np.exp(H)
        dret = -sd * sd + sd * d["z"][t]          # d(session's log return)/dH
        dx = excess / sd                          # d(the factors' shock)/dH
        if proc.jumps:
            _, jump, _ = FP._jump_parts(proc, H, d["u"][t], d["w"][t])
            dret = dret - _comp_slope(proc, H) + proc.beta * jump
            dx = dx + (proc.beta - 1.0) * jump / sd
        Gv += dret * dH
        x = dt / sd + dx * dH
        dhf = proc.phi_f * dhf + proc.th_f * x
        dhs = proc.phi_s * dhs + proc.th_s * x
    return {"R": L[-1], "hf": hf, "hs": hs, "H": Hs, "Gv": Gv, "dH": dHs}


def pin(R, m, tau):
    """R shifted by the one constant that makes its gross return average e^(m*tau)."""
    return R + (m * tau - np.log(np.mean(np.exp(R))))


# ---------------------------------------------------------------------------- phase A: the chain

def _chain_row(job):
    """One row of nodes' real-world transition over a call period, and each node's expected
    variance over it in units of sigma-bar^2: a pmap worker."""
    run, i = job
    HF, HS = grid(run)
    proc = process(run, 0.004)        # the volatility's dynamics ignore sigma-bar
    d = FP.draws(TC, PATHS, SEED)
    var_j = (proc.pu * 2 * proc.au ** 2 + proc.pd * 2 * proc.ad ** 2
             - (proc.pu * proc.au - proc.pd * proc.ad) ** 2)
    var_e = (proc.pe * 2 * proc.aeu ** 2 + (1 - proc.pe) * 2 * proc.aed ** 2
             - (proc.pe * proc.aeu - (1 - proc.pe) * proc.aed) ** 2) if proc.earnings else 0.0
    nodes = HF.size * HS.size
    rows, V = [], []
    for j in range(HS.size):
        _, Hs, hf, hs = FP.simulate(proc, HF[i], HS[j], 0.0, 0.0, d, final=True)
        idx, w = split(HF, HS, hf, hs)
        rows.append(np.bincount(idx.ravel(), w.ravel(), nodes) / PATHS)
        v = np.exp(2 * Hs).sum(0) + var_j * np.exp(2 * proc.beta * Hs).sum(0)
        v += var_e / VP.EARNINGS_EVERY * np.exp(2 * proc.be * Hs).sum(0)
        V.append(float(v.mean()))
    return rows, V


def stationary(P, tol=1e-15, iters=200_000):
    """The chain's stationary law, by power iteration."""
    v = np.full(P.shape[0], 1.0 / P.shape[0])
    for _ in range(iters):
        nv = v @ P
        if np.abs(nv - v).sum() < tol:
            return nv
        v = nv
    return v


# ---------------------------------------------------------------------------- phase B: the tables

def _offsets(R, h):
    """The depth offset a period's move R gives a lot, floor(1/2 - R/h) as DepthWalk bins it,
    kept within +-REACH/h: beyond that only nodes no lot reaches move, and their excess is
    put on the edge rather than widening every node's transition."""
    W = int(round(REACH / h))
    return np.clip(np.floor(0.5 - R / h).astype(int), -W, W) + W, 2 * W + 1


def _tails(R, G):
    """R sorted, and the means over the paths of 1, e^R, e^2R, R and e^R*G restricted to
    R >= each of its values: the columns from which every depth's figures are read."""
    o = np.argsort(R)
    Rs = R[o]
    e = np.exp(Rs)
    cols = (np.ones_like(Rs), e, e * e, Rs, e * G[o])
    return Rs, np.vstack([np.concatenate([np.cumsum(c[::-1])[::-1], [0.0]]) / R.size
                          for c in cols])


def _node(run, proc, HF, HS, a, dc, dp):
    """Everything one node contributes (see the module docstring)."""
    i, j = divmod(a, HS.size)
    hf0, hs0 = HF[i], HS[j]
    r, delta, mu, p_star = run["r"], run["delta"], run["mu"], run["p_star"]
    mP, mQ, exc = mu - delta, r - delta, (mu - r) * VP.DT
    tc, tp = TC * VP.DT, TP * VP.DT
    nodes = HF.size * HS.size
    xs = {g: (np.arange(int(round(xmax / h))) + 0.5) * h for g, (h, xmax) in GRIDS.items()}
    out = {}

    # --- the call period: where the lots go, and what each depth books
    P = paths(proc, hf0, hs0, mP, 0.0, dc)
    Q = paths(proc, hf0, hs0, mQ, exc, dc)
    idx, w = split(HF, HS, P["hf"], P["hs"])
    RP0 = pin(P["R"], mP, tc)
    for g, (h, _) in GRIDS.items():
        off, D = _offsets(RP0, h)
        flat = (idx * D + off[None, :]).ravel()
        out[f"kern {g}"] = (np.bincount(flat, w.ravel(), nodes * D) / PATHS).reshape(nodes, D)
    # variants: no earnings, and earnings on each of the period's sessions
    variants = [(P["R"], Q["R"], P["Gv"], Q["Gv"])]
    if proc.earnings:
        for s in range(TC):
            eP, sP = _earn(proc, P["H"][s], dc["ue"], dc["we"])
            eQ, sQ = _earn(proc, Q["H"][s], dc["ue"], dc["we"])
            variants.append((P["R"] + eP, Q["R"] + eQ, P["Gv"] + sP * P["dH"][s],
                             Q["Gv"] + sQ * Q["dH"][s]))
    per = []
    for RP, RQ, GP, GQ in variants:
        RP, RQ = pin(RP, mP, tc), pin(RQ, mQ, tc)
        sP, cP = _tails(RP, GP)
        sQ, cQ = _tails(RQ, GQ)
        res = {}
        for g, x in xs.items():
            kP, kQ = np.searchsorted(sP, x), np.searchsorted(sQ, x)
            if g == "near":     # 1, e^R, e^2R, R, e^R*G under P; 1, e^R, e^R*G under Q
                res[g] = np.vstack([cP[:, kP], cQ[[0, 1, 4]][:, kQ]])
            else:               # 1, e^R, e^2R, R under P; 1, e^R under Q
                res[g] = np.vstack([cP[:4, kP], cQ[:2][:, kQ]])
        up = RP > 0
        u = np.exp(RP) - 1.0
        res["const"] = np.array([up.sum(), u[up].sum(), (u[up] ** 2).sum(),
                                 (~up).sum(), u[~up].sum(), (u[~up] ** 2).sum()]) / PATHS
        per.append(res)
    kinds = ([[0]] + [[1 + 5 * wk + o for o in range(5)] for wk in range(4)]
             if proc.earnings else [[0]] * CALL_KINDS)
    for g in list(xs) + ["const"]:
        out[f"call {g}"] = np.stack([np.mean([per[v][g] for v in kd], axis=0) for kd in kinds])
    del P, Q, variants, per

    # --- the put's week: the strike, the premium, the entry
    P = paths(proc, hf0, hs0, mP, 0.0, dp)
    Q = paths(proc, hf0, hs0, mQ, exc, dp)
    idx, w = split(HF, HS, P["hf"], P["hs"])
    put = np.zeros((PUT_KINDS, len(PUT_COLS)))
    gaps = np.zeros((PUT_KINDS, GAP_BINS.size - 1))
    entry = {g: np.zeros((PUT_KINDS, nodes, x.size)) for g, x in xs.items()}
    for kind in range(PUT_KINDS if proc.earnings else 1):
        RP, RQ, GP, GQ = P["R"], Q["R"], P["Gv"], Q["Gv"]
        if kind:
            s = kind - 1
            eP, sP = _earn(proc, P["H"][s], dp["ue"], dp["we"])
            eQ, sQ = _earn(proc, Q["H"][s], dp["ue"], dp["we"])
            RP, RQ = RP + eP, RQ + eQ
            GP, GQ = GP + sP * P["dH"][s], GQ + sQ * Q["dH"][s]
        RP, RQ = pin(RP, mP, tp), pin(RQ, mQ, tp)
        logk = float(np.quantile(RP, p_star))
        k = exp(logk)
        asg, asq = RP < logk, RQ < logk
        eP, eQ = np.exp(RP), np.exp(RQ)
        prem = exp(-r * tp) * (k * asq.sum() - eQ[asq].sum()) / PATHS
        x0 = logk - RP[asg]
        iv = FP.implied("put", np.array(prem), np.array(k), tp, r, delta)
        put[kind] = (logk, prem, (k * asg.sum() - eP[asg].sum()) / PATHS, asg.mean(),
                     x0.sum() / PATHS, (1.0 - eP[asg]).sum() / PATHS,
                     eP[asg].sum() / PATHS, (eP * GP)[asg].sum() / PATHS,
                     eQ[asq].sum() / PATHS, (eQ * GQ)[asq].sum() / PATHS, float(iv),
                     asq.mean())
        gaps[kind] = np.histogram(1.0 - np.exp(-x0), GAP_BINS)[0] / PATHS
        for g, x in xs.items():
            # Each entry to the cell it falls in.  Splitting it between the two centres
            # around it instead, which keeps its mean depth, was tried and reads the first
            # expiry further off (0.4027 against 0.4039 at constant sigma, the continuum
            # about 0.4067): below the first centre no split is possible, and there the
            # cell's own lower half partly offsets.  The grid is the limit (TODO II-32).
            h, n = GRIDS[g][0], x.size
            cell = np.minimum((x0 / h).astype(int), n - 1)
            flat = (idx[:, asg] * n + cell[None, :]).ravel()
            entry[g][kind] = (np.bincount(flat, w[:, asg].ravel(), nodes * n)
                              / PATHS).reshape(nodes, n)
    if not proc.earnings:
        put[1:], gaps[1:] = put[0], gaps[0]
        for g in entry:
            entry[g][1:] = entry[g][0]
    out["put"], out["gaps"] = put, gaps
    # A week holds earnings once in thirteen, on one of its five sessions: the entry is kept
    # as the plain week's and the earnings week's, its five sessions averaged.
    out["entry"] = {g: np.stack([e[0], e[1:].mean(axis=0)]) for g, e in entry.items()}
    return out


def _table_row(job):
    """One row of nodes' tables: a pmap worker.  The entry and the gaps are wanted only
    summed over the sale state, so each node's are weighted by its stationary share and
    summed over the row here, rather than carried back node by node."""
    run, sig_bar, i, pi = job
    HF, HS = grid(run)
    proc = process(run, sig_bar)
    dc = FP.draws(TC, PATHS, SEED)
    dp = FP.draws(TP, PATHS, SEED + 1)
    out = {"put": [], "kern": {g: [] for g in GRIDS},
           "call": {g: [] for g in list(GRIDS) + ["const"]}}
    gaps, entry = 0.0, {g: 0.0 for g in GRIDS}
    for j in range(HS.size):
        a = i * HS.size + j
        n = _node(run, proc, HF, HS, a, dc, dp)
        out["put"].append(n["put"])
        for g in GRIDS:
            out["kern"][g].append(n[f"kern {g}"].astype(np.float32))
            entry[g] = entry[g] + n["entry"][g] * pi[a]
        for g in out["call"]:
            out["call"][g].append(n[f"call {g}"])
        gaps = gaps + n["gaps"] * pi[a]
    out["gaps"], out["entry"] = gaps, entry
    return out


# ---------------------------------------------------------------------------- phase C: the exact entry

def _cubic(v, g):
    """Four-point Lagrange in v on the uniform grid g, clamped: (first index, weights (4, n));
    a grid of one node (the volatility held still) puts everything on it."""
    if g.size < 4:
        return np.zeros(v.shape, int), np.vstack([np.ones(v.shape)] + [np.zeros(v.shape)] * 3)
    a = np.clip((v - g[0]) / (g[1] - g[0]), 0.0, g.size - 1.0)
    i = np.clip(np.floor(a).astype(int) - 1, 0, g.size - 4)
    t = a - i
    return i, np.vstack([-(t - 1) * (t - 2) * (t - 3) / 6, t * (t - 2) * (t - 3) / 2,
                         -t * (t - 1) * (t - 3) / 2, t * (t - 1) * (t - 2) / 6])


def _at_state(table, HF, HS, hf, hs, *index):
    """A node table (nodes, ...) read at the states (hf, hs), cubic in each factor; `index`
    picks from its trailing dimensions, an array per lot each."""
    i, wi = _cubic(hf, HF)
    j, wj = _cubic(hs, HS)
    ns = HS.size
    out = np.zeros(hf.shape)
    for a in range(4 if HF.size >= 4 else 1):
        for b in range(4 if HS.size >= 4 else 1):
            node = (i + a) * ns + (j + b)
            out += wi[a] * wj[b] * table[(node,) + index]
    return out


def _stationary_states(proc, n, reads, seed):
    """n independent paths from h = 0, run BURN sessions into the stationary state and read
    `reads` times, MOMENT_GAP sessions apart: (hf, hs) of the n*reads reads."""
    g = np.random.default_rng(seed)
    hf, hs = np.zeros(n), np.zeros(n)
    out_f, out_s = [], []
    for stretch in [VP.BURN] + [FP.MOMENT_GAP] * (reads - 1):
        for start in range(0, stretch, 50):
            T = min(50, stretch - start)
            d = {"z": g.standard_normal((T, n)), "u": g.random((T, n)),
                 "w": g.exponential(size=(T, n))}
            _, _, hf, hs = FP.simulate(proc, hf, hs, 0.0, 0.0, d, final=True)
        out_f.append(hf.copy())
        out_s.append(hs.copy())
    return np.concatenate(out_f), np.concatenate(out_s)


FIRST_COLS = ("lots", "prem", "basis", "depth", "exitcost", "exits", "exitdepth",
              "D both", "D price",
              "up n", "up u", "up uu", "up p0", "up p0u", "up c", "up cu",
              "dn n", "dn u", "dn uu", "dn p0", "dn p0u", "dn c", "dn cu")
EXACT_PUT_COLS = ("sales", "k", "prem", "mark", "assigned", "x0", "drop",
                  "D both", "D price")


def _exact_chunk(job):
    """Decision 10: puts sold from exact stationary states, each at a uniform point of the
    earnings calendar; their week and the lot's first call period stepped from that state in
    the real world and under the pricing measure on the same draws.  A pmap worker; returns
    sums over its sales, to be pooled.

    Each sale's strike is the nodes' interpolated to its state (cubic), so the dial is exact
    to the interpolation, as in the simulator.  The premiums are one path's discounted payoff
    under the pricing measure, beside the same path's payoff in the real world: an unbiased
    price summed over the sales, and paired with its payout path by path, which is what
    keeps both exact tests exact.  The betas take the lot's premium as a price, interpolated
    from the nodes' (a payoff would pair with the move it is regressed on)."""
    run, sig_bar, seed, n_paths, logk_nodes, prem_near = job
    HF, HS = grid(run)
    proc = process(run, sig_bar)
    r, delta, mu = run["r"], run["delta"], run["mu"]
    mP, mQ, exc = mu - delta, r - delta, (mu - r) * VP.DT
    tc, tp = TC * VP.DT, TP * VP.DT
    nodes = HF.size * HS.size
    g = np.random.default_rng(seed + 1)
    hf, hs = _stationary_states(proc, n_paths, EXACT_READS, seed)
    N = hf.size
    p_put = g.integers(0, EARN_WEEKS, N)          # weeks from the sale to the earnings week
    off = g.integers(0, 5, N)                     # the earnings session within its week
    if not proc.earnings:
        p_put[:] = 1                              # never an earnings week
    kind = np.where(p_put == 0, 1 + off, 0)
    logk = np.empty(N)
    for kd in np.unique(kind):
        s = kind == kd
        logk[s] = _at_state(logk_nodes[:, kd], HF, HS, hf[s], hs[s])

    # --- the put's week
    d = FP.draws(TP, N, seed + 2)
    P = paths(proc, hf, hs, mP, 0.0, d)
    Q = paths(proc, hf, hs, mQ, exc, d)
    RP, RQ, GP, GQ = P["R"], Q["R"], P["Gv"], Q["Gv"]
    e = kind > 0
    if e.any():
        ii = np.nonzero(e)[0]
        eP, sP = _earn(proc, P["H"][off[ii], ii], d["ue"][ii], d["we"][ii])
        eQ, sQ = _earn(proc, Q["H"][off[ii], ii], d["ue"][ii], d["we"][ii])
        RP, RQ, GP, GQ = RP.copy(), RQ.copy(), GP.copy(), GQ.copy()
        RP[ii] += eP
        RQ[ii] += eQ
        GP[ii] += sP * P["dH"][off[ii], ii]
        GQ[ii] += sQ * Q["dH"][off[ii], ii]
    RP, RQ = pin(RP, mP, tp), pin(RQ, mQ, tp)
    # The dial on the sales themselves: each kind's interpolated strikes moved by the one
    # shift that assigns exactly p* of its sales.  The nodes' strikes are quantiles of
    # draws every node shares, so their errors are common rather than averaging out, and
    # interpolated they assigned 0.2004 of the sales at p* = 0.2 (decision 10's check).
    for kd in np.unique(kind):
        s = kind == kd
        logk[s] += np.quantile(RP[s] - logk[s], run["p_star"])
    k = np.exp(logk)
    asg, asq = RP < logk, RQ < logk
    eRP, eRQ = np.exp(RP), np.exp(RQ)
    put = {"sales": float(N), "k": k.sum(),
           "prem": exp(-r * tp) * ((k - eRQ) * asq).sum(), "mark": ((k - eRP) * asg).sum(),
           "assigned": float(asg.sum()), "x0": (logk - RP)[asg].sum(),
           "drop": (1.0 - eRP)[asg].sum(),
           "D both": (0.5 * ((tp * eRP + eRP * GP) * asg + (tp * eRQ + eRQ * GQ) * asq) / tp).sum(),
           "D price": (0.5 * (eRP * asg + eRQ * asq)).sum()}
    x0 = (logk - RP)[asg]
    gaps = np.histogram(1.0 - np.exp(-x0), GAP_BINS)[0].astype(float)
    hf1, hs1 = P["hf"][asg], P["hs"][asg]
    q = (p_put[asg] - 1) % EARN_WEEKS              # the lot's phase at entry
    off1 = off[asg]
    del P, Q, d, RP, RQ, GP, GQ, eRP, eRQ

    # --- the lot's first call period, from its exact state at entry
    m = x0.size
    d = FP.draws(TC, m, seed + 3)
    P = paths(proc, hf1, hs1, mP, 0.0, d)
    Q = paths(proc, hf1, hs1, mQ, exc, d)
    R1P, R1Q, G1P, G1Q = P["R"].copy(), Q["R"].copy(), P["Gv"].copy(), Q["Gv"].copy()
    ck = np.where(q < 4, 1 + q, 0)                 # the period's call kind
    if proc.earnings:
        ii = np.nonzero(q < 4)[0]
        ses = 5 * q[ii] + off1[ii]
        eP, sP = _earn(proc, P["H"][ses, ii], d["ue"][ii], d["we"][ii])
        eQ, sQ = _earn(proc, Q["H"][ses, ii], d["ue"][ii], d["we"][ii])
        R1P[ii] += eP
        R1Q[ii] += eQ
        G1P[ii] += sP * P["dH"][ses, ii]
        G1Q[ii] += sQ * Q["dH"][ses, ii]
    R1P, R1Q = pin(R1P, mP, tc), pin(R1Q, mQ, tc)
    ex0, eP1, eQ1 = np.exp(x0), np.exp(R1P), np.exp(R1Q)
    outP, outQ = R1P >= x0, R1Q >= x0
    # the lot's premium as a price, for the betas: the nodes' at its state, linear in depth
    h = GRIDS["near"][0]
    n_near = int(round(GRIDS["near"][1] / h))
    pos = np.clip(x0 / h - 0.5, 0.0, n_near - 1 - 1e-12)
    c0 = pos.astype(int)
    tt = pos - c0
    c = ((1 - tt) * _at_state(prem_near, HF, HS, hf1, hs1, ck, c0)
         + tt * _at_state(prem_near, HF, HS, hf1, hs1, ck, np.minimum(c0 + 1, n_near - 1)))
    u = eP1 - 1.0
    p0 = np.minimum(eP1, ex0) - 1.0
    up = R1P > 0
    first = {"lots": float(m),
             "prem": exp(-r * tc) * ((eQ1 - ex0) * outQ).sum(), "basis": ex0.sum(),
             "depth": x0.sum(), "exitcost": ((eP1 - ex0) * outP).sum(),
             "exits": float(outP.sum()), "exitdepth": ((x0 - R1P) * outP).sum(),
             "D both": (0.5 * ((tc * eP1 + eP1 * G1P) * outP + (tc * eQ1 + eQ1 * G1Q) * outQ)
                        / tc).sum(),
             "D price": (0.5 * (eP1 * outP + eQ1 * outQ)).sum()}
    for side, sel in (("up", up), ("dn", ~up)):
        first.update({f"{side} n": float(sel.sum()), f"{side} u": u[sel].sum(),
                      f"{side} uu": (u[sel] ** 2).sum(), f"{side} p0": p0[sel].sum(),
                      f"{side} p0u": (p0[sel] * u[sel]).sum(), f"{side} c": c[sel].sum(),
                      f"{side} cu": (c[sel] * u[sel]).sum()})
    # the first period's lots by node, call kind and depth cell on the near grid, which a
    # volatility spread reprices (model._vol_spread)
    idx0, w0 = split(HF, HS, hf1, hs1)
    cellN = np.minimum((x0 / h).astype(int), n_near - 1)
    flat0 = ((idx0 * CALL_KINDS + ck[None, :]) * n_near + cellN[None, :]).ravel()
    first_census = np.bincount(flat0, w0.ravel(), nodes * CALL_KINDS * n_near).reshape(
        nodes, CALL_KINDS, n_near).astype(np.float32)
    # the depth census of the first period, and its exits, on each grid
    first_cells = {}
    for gname, (hg, xmax) in GRIDS.items():
        n = int(round(xmax / hg))
        cell0 = np.minimum((x0 / hg).astype(int), n - 1)
        first_cells[gname] = np.vstack([np.bincount(cell0, minlength=n),
                                        np.bincount(cell0, outP.astype(float), n)])
    # the survivors enter the grid at the start of their second call period
    stay = ~outP
    x1 = (x0 - R1P)[stay]
    idx, w = split(HF, HS, P["hf"][stay], P["hs"][stay])
    q2 = (q[stay] - 4) % EARN_WEEKS
    entry2 = {}
    for gname, (hg, xmax) in GRIDS.items():
        n = int(round(xmax / hg))
        cell = np.minimum((x1 / hg).astype(int), n - 1)
        flat = ((q2[None, :] * nodes + idx) * n + cell[None, :]).ravel()
        entry2[gname] = np.bincount(flat, w.ravel(), EARN_WEEKS * nodes * n).reshape(
            EARN_WEEKS, nodes, n).astype(np.float32)
    return {"put": put, "gaps": gaps, "first": first, "first cells": first_cells,
            "first census": first_census, "entry2": entry2}


# ---------------------------------------------------------------------------- the long run

LONG_RUN_PATHS = 200_000
LONG_RUN_HS = 0.05                    # h_slow's spacing for the eigenvalues (test 10)
LONG_RUN_THETAS = (-0.02, 0.0, 0.02, -1.0)


def _long_run_row(job):
    """One row of nodes' tilted transitions over a call period, F(theta)_ab =
    E[e^(theta*R); next node b | node a], for each theta and kind of period: a pmap worker."""
    run, sig_bar, i, seed = job
    HF, HS = long_run_grid(run)
    proc = process(run, sig_bar)
    m, tc = run["mu"] - run["delta"], TC * VP.DT
    nodes = HF.size * HS.size
    out = np.zeros((len(LONG_RUN_THETAS), CALL_KINDS, HS.size, nodes))
    for j in range(HS.size):
        # Draws of each node's own: an eigenvalue needs no smoothness across nodes, and on
        # draws every node shares their errors are common and c2 moved 0.03 between seeds.
        d = FP.draws(TC, LONG_RUN_PATHS, seed + 1009 * (i * HS.size + j))
        L, Hs, hf, hs = FP.simulate(proc, HF[i], HS[j], m, 0.0, d, final=True)
        idx, w = split(HF, HS, hf, hs)
        R0 = L[-1]
        variants = [R0]
        if proc.earnings:
            variants += [R0 + _earn(proc, Hs[s], d["ue"], d["we"])[0] for s in range(TC)]
        kinds = ([[0]] + [[1 + 5 * wk + o for o in range(5)] for wk in range(4)]
                 if proc.earnings else [[0]] * CALL_KINDS)
        for kd, vs in enumerate(kinds):
            for v in vs:
                R = pin(variants[v], m, tc)
                for t, th in enumerate(LONG_RUN_THETAS):
                    e = np.exp(th * R)
                    out[t, kd, j] += np.bincount(idx.ravel(), (w * e[None, :]).ravel(),
                                                 nodes) / (LONG_RUN_PATHS * len(vs))
    return out


def long_run_grid(run):
    """The eigenvalues' grid: h_slow at LONG_RUN_HS where the process has jumps (test 10:
    the boundary c2 is the figure most sensitive to h_slow's spread), the process's own
    grid otherwise."""
    if run.get("still") or not run["jumps"]:
        return grid(run)
    return grid(dict(run, **{"hs step": LONG_RUN_HS}))


def long_run(run, verbose=True, seed=SEED + 7):
    """Section 10's boundaries under the fitted process, from the lattice read as a Markov
    additive process (test 10): kappa(theta), the log of the largest eigenvalue of the tilted
    transition over the thirteen-period earnings cycle, a year.  c1 = m - kappa'(0), the
    lots' boundary, the long-run drag of log S; c2 = m + kappa(-1), the capital's, the
    growth of E[S0/S_t]; kappa''(0) the long-run variance of log S.  Cached."""
    key = {"lattice": _key(run)[1], "paths": LONG_RUN_PATHS, "hs": LONG_RUN_HS,
           "thetas": LONG_RUN_THETAS, "version": 2, "seed": seed}
    path = os.path.join(CACHE, "longrun-" + hashlib.sha1(
        json.dumps(key, sort_keys=True).encode()).hexdigest()[:12] + ".json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    from model import pmap
    t0 = time.time()
    data = load(run, verbose)
    sig_bar = float(data["sig bar"])
    HF, HS = long_run_grid(run)
    rows = pmap(_long_run_row, [(run, sig_bar, i, seed) for i in range(HF.size)],
                workers=min(BUILD_WORKERS, os.cpu_count() or 1, HF.size))
    F = np.concatenate(rows, axis=2)             # (theta, kind, node a, node b)
    tc = TC * VP.DT
    # The cycle: a lot's phase falls 4 weeks a period, mod 13, so over 13 periods it meets
    # every phase once; the spectral radius of the product is the cycle's growth.
    order = [(-4 * j) % EARN_WEEKS for j in range(EARN_WEEKS)]
    kap = []
    for t in range(len(LONG_RUN_THETAS)):
        M = np.eye(F.shape[2])
        for p in order:
            M = M @ F[t, 1 + p if p < 4 else 0]
        kap.append(float(np.log(np.max(np.abs(np.linalg.eigvals(M))))) / (EARN_WEEKS * tc))
    (km, k0, kp, k1), eps = kap, LONG_RUN_THETAS[2]
    m = run["mu"] - run["delta"]
    out = {"c1": m - (kp - km) / (2 * eps), "c2": m + k1,
           "long-run variance": (kp - 2 * k0 + km) / eps ** 2, "kappa(0)": k0,
           "nodes": int(F.shape[2])}
    os.makedirs(CACHE, exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(out, f)
    os.replace(path + ".tmp", path)
    if verbose:
        print(f"  lattice: long run on {out['nodes']} nodes [{time.time() - t0:.0f}s]",
              file=sys.stderr, flush=True)
    return out


# ---------------------------------------------------------------------------- build and cache

def _key(run):
    HF, HS = grid(run)                # the grid actually used, which depends on the process
    k = dict(run, version=VERSION, paths=PATHS, seed=SEED, tp=TP, tc=TC, hf=HF.tolist(),
             hs=HS.tolist(), grids=GRIDS, reach=REACH, fit=VP.FIT, earn=VP.EARN,
             sessions=VP.SESSIONS, every=VP.EARNINGS_EVERY, clip=VP.H_CLIP)
    return k, hashlib.sha1(json.dumps(k, sort_keys=True).encode()).hexdigest()[:12]


def _exact_key(run):
    """Phase C's key: the tables' it reads, and its own parameters."""
    k = {"tables": _key(run)[1], "version": EXACT_VERSION, "paths": EXACT_PATHS,
         "reads": EXACT_READS, "chunks": EXACT_CHUNKS, "gap": FP.MOMENT_GAP, "seed": SEED}
    return k, hashlib.sha1(json.dumps(k, sort_keys=True).encode()).hexdigest()[:12]


def build(run, verbose=True):
    """Phases A and B for one run's parameters (sigma, mu, r, delta, p_star, jumps,
    earnings, and optionally still): the chain and the nodes' tables."""
    from model import pmap
    t0 = time.time()
    HF, HS = grid(run)
    nodes = HF.size * HS.size
    workers = min(BUILD_WORKERS, os.cpu_count() or 1, HF.size)
    res = pmap(_chain_row, [(run, i) for i in range(HF.size)], workers=workers)
    P = np.array([r for rows, _ in res for r in rows])
    V = np.array([v for _, vs in res for v in vs])
    pi = stationary(P)
    # sigma-bar is the process's, measured once from its stationary law (decision 9) and
    # shared with the simulator; pi @ V, the lattice's own, is kept to show the grid's
    # share of the difference.
    if run.get("still"):
        sig_bar = run["sigma"] * sqrt(TC * VP.DT / float(pi @ V))
    else:
        sig_bar = FP.sig_bar(run["sigma"], FP.moments(run["jumps"], run["earnings"]),
                             run["jumps"], run["earnings"])
    if verbose:
        print(f"  lattice: chain of {nodes} nodes, sigma-bar {sig_bar:.6f} a session "
              f"[{time.time() - t0:.0f}s]", file=sys.stderr, flush=True)
    rows = pmap(_table_row, [(run, sig_bar, i, pi) for i in range(HF.size)], workers=workers)
    data = {"hf": HF, "hs": HS, "chain": P, "pi": pi, "V": V, "sig bar": np.array(sig_bar),
            "put": np.stack([p for row in rows for p in row["put"]]),
            "gaps": np.sum([row["gaps"] for row in rows], axis=0)}
    for g in GRIDS:
        data[f"kern {g}"] = np.stack([k for row in rows for k in row["kern"][g]])
        data[f"entry {g}"] = np.sum([row["entry"][g] for row in rows], axis=0)
    for g in list(GRIDS) + ["const"]:
        data[f"call {g}"] = np.stack([c for row in rows for c in row["call"][g]])
    if verbose:
        print(f"  lattice: tables built [{time.time() - t0:.0f}s]", file=sys.stderr, flush=True)
    return data


def build_exact(run, data, verbose=True):
    """Phase C, the exact entry (decision 10), on the tables of phases A and B."""
    from model import pmap
    t0 = time.time()
    h, xmax = GRIDS["near"]
    x = (np.arange(int(round(xmax / h))) + 0.5) * h
    call = data["call near"]
    prem_near = exp(-run["r"] * TC * VP.DT) * (call[:, :, 6, :] - np.exp(x) * call[:, :, 5, :])
    jobs = [(run, float(data["sig bar"]), SEED + 100 * (c + 1), EXACT_PATHS // EXACT_CHUNKS,
             data["put"][:, :, 0], prem_near) for c in range(EXACT_CHUNKS)]
    parts = pmap(_exact_chunk, jobs, workers=min(EXACT_CHUNKS, os.cpu_count() or 1))
    out = {"exact put": np.array([sum(p["put"][c] for p in parts) for c in EXACT_PUT_COLS]),
           "exact gaps": np.sum([p["gaps"] for p in parts], axis=0),
           "first": np.array([sum(p["first"][c] for p in parts) for c in FIRST_COLS]),
           "first census": np.sum([p["first census"] for p in parts], axis=0)}
    for g in GRIDS:
        out[f"first cells {g}"] = np.sum([p["first cells"][g] for p in parts], axis=0)
        out[f"entry2 {g}"] = np.sum([p["entry2"][g] for p in parts], axis=0)
    if verbose:
        print(f"  lattice: exact entry, {int(out['exact put'][0]):,} sales "
              f"[{time.time() - t0:.0f}s]", file=sys.stderr, flush=True)
    return out


def _cached(path, key, make):
    """An npz from the cache, or made and cached."""
    if os.path.exists(path):
        with np.load(path) as z:
            return {k: z[k] for k in z.files if k != "key"}
    data = make()
    os.makedirs(CACHE, exist_ok=True)
    tmp = path[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, key=np.array(json.dumps(key, sort_keys=True)), **data)
    os.replace(tmp, path)
    return data


def _iv_rows(job):
    """Implied volatilities of one row of nodes' fair call premiums on the near grid, each
    kind and depth: a pmap worker.  A premium too small to carry one takes its shallower
    neighbour's, as fairprice's tables do (`fairprice._fill`)."""
    prem, x, r, delta = job
    tc = TC * VP.DT
    k = np.broadcast_to(np.exp(x), prem.shape)
    iv = FP.implied("call", prem, k, tc, r, delta)
    return np.exp(FP._fill(np.log(iv)))


def spread_tables(run, data, verbose=True):
    """What a volatility spread needs on the near grid (model._vol_spread), cached apart:
    each node's fair call premiums as implied volatilities, (nodes, kinds, cells), and the
    first call period's lots by node, kind and cell from the exact entry -- which, for a
    lattice whose entry was built before it kept them, reruns phase C on its own seeds and
    keeps only that, the rest coming out bit for bit as cached."""
    ekey, eh = _exact_key(run)
    key = {"exact": eh, "version": 1}

    def make():
        from model import pmap
        t0 = time.time()
        h, xmax = GRIDS["near"]
        x = (np.arange(int(round(xmax / h))) + 0.5) * h
        call = data["call near"]
        prem = exp(-run["r"] * TC * VP.DT) * (call[:, :, 6, :] - np.exp(x) * call[:, :, 5, :])
        rows = np.array_split(np.arange(prem.shape[0]), min(BUILD_WORKERS, prem.shape[0]))
        ivs = pmap(_iv_rows, [(prem[rr], x, run["r"], run["delta"]) for rr in rows],
                   workers=min(BUILD_WORKERS, os.cpu_count() or 1, len(rows)))
        out = {"call iv near": np.concatenate(ivs)}
        if "first census" in data:
            out["first census"] = data["first census"]
        else:
            jobs = [(run, float(data["sig bar"]), SEED + 100 * (c + 1),
                     EXACT_PATHS // EXACT_CHUNKS, data["put"][:, :, 0], prem)
                    for c in range(EXACT_CHUNKS)]
            parts = pmap(_exact_chunk, jobs, workers=min(EXACT_CHUNKS, os.cpu_count() or 1))
            out["first census"] = np.sum([p["first census"] for p in parts], axis=0)
        if verbose:
            print(f"  lattice: spread tables [{time.time() - t0:.0f}s]", file=sys.stderr,
                  flush=True)
        return out

    return _cached(os.path.join(CACHE, f"spread-{hashlib.sha1(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12]}.npz"), key, make)


def cached(run):
    """Whether `run`'s lattice -- tables and exact entry -- is in the cache, so that a check
    can read it without building it."""
    return (os.path.exists(os.path.join(CACHE, f"lattice-{_key(run)[1]}.npz"))
            and os.path.exists(os.path.join(CACHE, f"exact-{_exact_key(run)[1]}.npz")))


def load(run, verbose=True):
    """The lattice for `run`, from the cache or built and cached: the tables (phases A and
    B) and the exact entry (phase C) in caches of their own, so a change to the entry does
    not rebuild the tables."""
    key, h = _key(run)
    data = _cached(os.path.join(CACHE, f"lattice-{h}.npz"), key, lambda: build(run, verbose))
    ekey, eh = _exact_key(run)
    data.update(_cached(os.path.join(CACHE, f"exact-{eh}.npz"), ekey,
                        lambda: build_exact(run, data, verbose)))
    return data


RUNNING = {"sigma": 0.20, "mu": 0.07, "r": 0.05, "delta": 0.025, "p_star": 0.20,
           "jumps": True, "earnings": True}


if __name__ == "__main__":
    run = dict(RUNNING, still=True) if "--still" in sys.argv else RUNNING
    t = time.time()
    data = load(run)
    print(f"loaded in {time.time() - t:.0f}s; sigma-bar {float(data['sig bar']):.6f}; "
          f"stationary mass on {int((data['pi'] > 1e-9).sum())} of {data['pi'].size} nodes")
