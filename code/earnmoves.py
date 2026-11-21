"""The earnings law, step 5(a) of the moving-volatility plan.

Decision 3 of `drafts/2026-11-21-moving-volatility-plan.md` makes earnings scheduled jumps:
known dates, two-sided, distinct from the unscheduled jumps `volfit.py` fits. Their dates are
known, so unlike the unscheduled jumps they need no simulation to be found: each date's move
is measured, and the law is fitted to the moves directly.

**The move** is the log return over the two sessions from each EDGAR date (`earnings.py`: the
8-K's day and the next, so that results released before the open and after the close are both
caught), the dividend added back as in `jumps.py`, on dates whose three closes are all in the
sample. It is measured in units of the yardstick before it -- the bipower sd of the 60 clean
sessions before the date, earlier earnings windows excluded, as `volstats.yardstick` -- and
the state h at the date is the log of that yardstick over the name's median.

**The law** is Kou's, as for the unscheduled jumps: the move is two sessions of diffusion plus
one jump, up with probability p and exponential of mean a_up, down otherwise with mean
a_down, its size scaling as volatility to the power beta_E. In yardstick units

    s = sqrt(2)*z + e^((beta_E - 1)*h) * Y,

fitted by maximum likelihood (a normal plus an exponential has a closed-form density).
Standard errors are a delete-a-block jackknife over two-year calendar blocks, every name's
dates in a block deleted together: earnings seasons are shared, as the volatility fit's
episodes were.

**Two checks** decide the shape: by sector (utilities and REITs, from EDGAR's SIC codes,
against the rest), and whether volatility steps after the date -- the kick, ln of the bipower
sd of the 20 sessions after the window over the 20 before, by size of move. The fitted
volatility model has no earnings term in h; the kick after the data's dates is set beside
the same kick after the fake dates of `--recover`, which the model without one produces.

**From yardstick units to the model's.** The simulator scales the jump by e^(beta_E*H), H the
model's own log volatility, not by a yardstick estimated from 60 noisy sessions. `--recover`
simulates the fitted volatility model (`volfit-final.json`) on the data's exact mask, adds an
earnings jump of a known law to the two sessions of every data date, and fits it as the data
are fitted. The law the simulator carries is the one whose fake fit reproduces the data's,
found by correcting the data's estimate for the bias the fake fits show (twice).

    python code/earnmoves.py            # the measurement and the fit
    python code/earnmoves.py --recover  # and the law in the model's units
"""

import json
import os
import sys
from bisect import bisect_left
from math import erfc, exp, log, pi, sqrt

import numpy as np

import earnings
import jumps
import volfit as F
import volstats as V

RESULTS = os.path.join("data", "aristocrats", "earnmoves.json")
VOL_FIT = os.path.join("data", "aristocrats", "volfit-final.json")
SECTORS = (("utilities", lambda sic: 4900 <= sic < 5000),
           ("REITs", lambda sic: sic == 6798),
           ("others", lambda sic: not (4900 <= sic < 5000 or sic == 6798)))
TAIL_C = (2.0, 3.0, 4.0, 6.0, 8.0)
LAW = ("p up", "a up", "a down", "beta E")
FAKE_SEEDS = (11, 12, 13, 14, 15, 16, 17, 18)
SIG = sqrt(2.0)                 # two sessions of diffusion, in one session's sd

_erfc = np.vectorize(erfc, otypes=[float])


# ---------------------------------------------------------------------------- the moves

def sic(sym):
    """EDGAR's SIC code for a name, from its cached submissions record."""
    cik = earnings.UNIVERSE[sym]
    sub = earnings._fetch(f"https://data.sec.gov/submissions/CIK{cik}.json",
                          os.path.join(earnings.EDGAR_DIR, f"CIK{cik}.json"))
    return int(sub.get("sic") or 0)


def universe():
    """(names, syms, days per row, clean R, raw R, in-sample mask)."""
    names, syms, days, R = jumps.universe_returns()
    raw = V.pad([jumps.log_returns(names[s])[1] for s in syms])
    ok = V.pad([np.array([names[s].in_sample(d) for d in names[s].series.days], float)
                for s in syms]) == 1.0
    return names, syms, days, R, raw, ok


def event_cells(names, syms, days, raw, ok):
    """(rows, cols) of every dated earnings window's first session: the date's own
    session (or the next, when the 8-K came out on a non-trading day), with the close
    before it and the two after it in the sample."""
    rows, cols = [], []
    for k, s in enumerate(syms):
        T = len(days[k])
        for d in names[s].dates:
            i = bisect_left(days[k], d)
            if 1 <= i and i + 1 < T and ok[k, i - 1] and ok[k, i] and ok[k, i + 1] \
                    and np.isfinite(raw[k, i]) and np.isfinite(raw[k, i + 1]):
                rows.append(k)
                cols.append(i)
    return np.array(rows), np.array(cols)


def measure(R, raw, rows, cols):
    """The moves in yardstick units and what goes with them, for windows at (rows, cols).
    `R` is clean (every earnings window NaN), `raw` holds every return."""
    pairs = V._pairs(R)
    yard = V.yardstick(R, pairs)
    _, sd, _ = V.standardize(R, pairs)
    med = np.nanmedian(sd, axis=1)
    kick = V.kicks(R, pairs)
    E = raw[rows, cols] + raw[rows, cols + 1]
    y = yard[rows, cols]
    out = {"s": E / y, "h": np.log(y / med[rows]), "kick": kick[rows, cols + 1],
           "row": rows, "col": cols}
    good = np.isfinite(out["s"]) & np.isfinite(out["h"])
    return {k: v[good] for k, v in out.items()}


def ordinary_kicks(R):
    """(s, kick) on every clean day: the standardized move and the kick after it."""
    pairs = V._pairs(R)
    s, _, _ = V.standardize(R, pairs)
    k = V.kicks(R, pairs)
    good = np.isfinite(s) & np.isfinite(k)
    return s[good], k[good]


# ---------------------------------------------------------------------------- the law

def _log_ndtr(x):
    """log of the standard normal cdf, elementwise, safe far into the lower tail."""
    out = np.empty_like(x)
    lo = x < -20.0
    out[~lo] = np.log(0.5 * _erfc(-x[~lo] / sqrt(2.0)))
    xl = x[lo]
    out[lo] = (-0.5 * xl * xl - np.log(-xl) - 0.5 * log(2 * pi)
               + np.log1p(-1.0 / (xl * xl) + 3.0 / xl ** 4))
    return out


def _log_emg(s, A, sig):
    """log density at s of sig*z plus an exponential of mean A (A > 0)."""
    return (-np.log(A) + sig * sig / (2 * A * A) - s / A
            + _log_ndtr(s / sig - sig / A))


def to_law(x):
    return {"p up": 1 / (1 + exp(-x[0])), "a up": exp(x[1]), "a down": exp(x[2]),
            "beta E": x[3]}


def from_law(q):
    p = q["p up"]
    return np.array([log(p / (1 - p)), log(q["a up"]), log(q["a down"]), q["beta E"]])


def loglik(x, s, h, beta=None):
    """Mean log likelihood of the moves s at states h; `beta` holds beta_E fixed."""
    q = to_law(x)
    b = q["beta E"] if beta is None else beta
    g = np.exp((b - 1.0) * h)
    up = log(q["p up"]) + _log_emg(s, q["a up"] * g, SIG)
    dn = log(1 - q["p up"]) + _log_emg(-s, q["a down"] * g, SIG)
    return float(np.mean(np.logaddexp(up, dn)))


def fit_law(s, h, beta=None, x0=None):
    """The maximum-likelihood law of moves s at states h: (law, mean log likelihood)."""
    x0 = np.array([0.0, log(2.0), log(2.0), 0.5]) if x0 is None else np.asarray(x0, float)
    f = lambda x: -loglik(x, s, h, beta)
    x, v = x0, f(x0)
    for step in (0.4, 0.1):         # a restart from the first optimum, smaller simplex
        x, v, _ = F.nelder_mead(f, x, step=step, max_evals=3000, tol=1e-10,
                                stall_evals=300, stall_delta=1e-9)
    q = to_law(x)
    if beta is not None:
        q["beta E"] = beta
    return q, -v


def jackknife(s, h, blocks, q, beta=None):
    """Delete-a-block jackknife standard errors of each element of the law q."""
    keys = np.unique(blocks)
    reps = []
    for b in keys:
        keep = blocks != b
        reps.append(fit_law(s[keep], h[keep], beta, from_law(q))[0])
    n = len(keys)
    return {k: sqrt((n - 1) / n * sum((r[k] - np.mean([t[k] for t in reps])) ** 2
                                      for r in reps)) for k in q}


def draw_moves(q, h, g):
    """Moves from law q at states h, the jump's draws from generator g (fixed draws, so
    the moves move smoothly with q)."""
    n = len(h)
    z, u, w = g.standard_normal(n), g.random(n), g.exponential(size=n)
    scale = np.exp((q["beta E"] - 1.0) * h)
    return SIG * z + scale * np.where(u < q["p up"], q["a up"] * w, -q["a down"] * w)


def tails(s, cs=TAIL_C):
    return {c: ((s > c).mean(), (s < -c).mean()) for c in cs}


# ---------------------------------------------------------------------------- reporting

def _law_line(q, se=None):
    parts = []
    for k in LAW:
        v = f"{k} {q[k]:.3f}"
        if se and k in se:
            v += f" ± {se[k]:.3f}"
        parts.append(v)
    return ", ".join(parts)


def report_moves(ev, sectors_of_row, s_ord, k_ord):
    s, h = ev["s"], ev["h"]
    print(f"{len(s)} dated earnings windows on {len(np.unique(ev['row']))} names")
    print(f"  in yardstick units: mean {s.mean():+.3f}, median {np.median(s):+.3f}, "
          f"sd {s.std():.3f}, mean |s| {np.abs(s).mean():.3f}  (two sessions of pure "
          f"diffusion: sd {SIG:.3f}, mean |s| {SIG * sqrt(2 / pi):.3f})")
    print("  beyond c, each side:  " + "  ".join(
        f"{c:g}: {u:.1%}/{d:.1%}" for c, (u, d) in tails(s).items()))
    print("\n  by volatility state (tercile of h): mean |s|, and mean |s| - 3 beyond 3")
    for lab, part in zip(("calm", "middle", "turbulent"), jumps._terciles(
            np.arange(len(s)), h)):
        a = s[part]
        big = np.abs(a)[np.abs(a) > 3]
        print(f"    {lab:9} h {np.mean(h[part]):+.2f}: mean |s| {np.abs(a).mean():.3f}, "
              f"beyond 3 {big.size / a.size:.1%}, mean excess {np.mean(big - 3):.3f}")
    print("\n  by sector: windows, mean |s|, sd, beyond 3, beyond 6")
    for name, _ in SECTORS:
        a = s[sectors_of_row[ev["row"]] == name]
        if a.size:
            print(f"    {name:9} {a.size:5}  {np.abs(a).mean():.3f}  {a.std():.3f}  "
                  f"{(np.abs(a) > 3).mean():.1%}  {(np.abs(a) > 6).mean():.1%}")
    print("\n  kick after the window, by size of move (ln sd after / before), "
          "earnings | ordinary days")
    for side, sign in V.SIDES:
        for lo, hi in V.KICK_BANDS:
            e = ev["kick"][(sign * s >= lo) & (sign * s < hi) & np.isfinite(ev["kick"])]
            o = k_ord[(sign * s_ord >= lo) & (sign * s_ord < hi)]
            print(f"    {side:4} {lo:g}-{hi:g}: {e.mean() if e.size else np.nan:+.3f} "
                  f"({e.size:4}) | {o.mean() if o.size else np.nan:+.3f} ({o.size:6})")


def report_fit(ev, blocks):
    s, h = ev["s"], ev["h"]
    out = {}
    q, ll = fit_law(s, h)
    se = jackknife(s, h, blocks, q)
    out["free"] = {"law": q, "se": se, "loglik": ll * len(s)}
    print(f"\n  fit, beta_E free:  {_law_line(q, se)}   log L {ll * len(s):.1f}")
    for b in (0.0, 0.58, 1.0):
        qb, llb = fit_law(s, h, beta=b, x0=from_law(q))
        out[f"beta {b:g}"] = {"law": qb, "loglik": llb * len(s)}
        print(f"  fit, beta_E = {b:<4g}: {_law_line(qb)}   log L {llb * len(s):.1f} "
              f"(LR {2 * (ll - llb) * len(s):.1f})")
    g = np.random.default_rng(1)
    sim = np.concatenate([draw_moves(q, h, g) for _ in range(20)])
    print("  tails, data | fitted law:  " + "  ".join(
        f"{c:g}: {u:.1%}/{d:.1%} | {us:.1%}/{ds:.1%}"
        for (c, (u, d)), (_, (us, ds)) in zip(tails(s).items(), tails(sim).items())))
    return out, q


# ---------------------------------------------------------------------------- recovery

def fake_sample(p_vol, law, R, ev, seed):
    """The fitted volatility model on the data's mask, with an earnings jump of `law`
    (model units: the jump is e^(beta_E*H)*Y, H the model's log volatility) added to the
    first session of every data window. Returns (clean R, raw R) shaped like the data."""
    d = F.Draws(R.shape[0], R.shape[1], seed)
    Rf, H = F.simulate_loop(p_vol, d, states=True)
    g = np.random.default_rng(seed + 1000)
    rows, cols = ev["row"], ev["col"]
    n = len(rows)
    u, w = g.random(n), g.exponential(size=n)
    Y = np.where(u < law["p up"], law["a up"] * w, -law["a down"] * w)
    raw = Rf.copy()
    raw[rows, cols] += np.exp(law["beta E"] * H[rows, cols]) * Y
    clean = np.where(np.isnan(R), np.nan, Rf)
    return clean, raw


def fake_fit(p_vol, law, R, ev, seed):
    clean, raw = fake_sample(p_vol, law, R, ev, seed)
    evf = measure(clean, raw, ev["row"], ev["col"])
    return fit_law(evf["s"], evf["h"])[0], evf


def recover(ev, R, q_data):
    """The law in model units whose fake fit reproduces the data's (two bias corrections),
    with the fake fits' spread beside the data's own estimate."""
    p_vol = dict(F.START)
    p_vol.update(json.load(open(VOL_FIT))["params"])
    x_data = from_law(q_data)
    x_model = x_data.copy()
    for it in range(2):
        fits = [fake_fit(p_vol, to_law(x_model), R, ev, sd) for sd in FAKE_SEEDS]
        xs = np.array([from_law(f[0]) for f in fits])
        bias = xs.mean(axis=0) - x_model
        print(f"\n  recovery {it + 1}: truth {_law_line(to_law(x_model))}")
        print(f"              fits  {_law_line(to_law(xs.mean(axis=0)))}  "
              f"(spread over {len(FAKE_SEEDS)} samples: "
              + ", ".join(f"{k} {v:.3f}" for k, v in zip(LAW, xs.std(axis=0, ddof=1)))
              + " in the fitted scale)")
        x_model = x_data - bias
    fits = [fake_fit(p_vol, to_law(x_model), R, ev, sd) for sd in FAKE_SEEDS]
    xs = np.array([from_law(f[0]) for f in fits])
    print(f"\n  model units: {_law_line(to_law(x_model))}")
    print(f"  its fake fits: {_law_line(to_law(xs.mean(axis=0)))}  (data's: "
          f"{_law_line(q_data)})")
    kf = np.concatenate([f[1]["kick"] for f in fits])
    sf = np.concatenate([f[1]["s"] for f in fits])
    print("\n  kick after the window, data | the model with no earnings term, fake dates")
    for side, sign in V.SIDES:
        for lo, hi in V.KICK_BANDS:
            e = ev["kick"][(sign * ev["s"] >= lo) & (sign * ev["s"] < hi)
                           & np.isfinite(ev["kick"])]
            m = kf[(sign * sf >= lo) & (sign * sf < hi) & np.isfinite(kf)]
            print(f"    {side:4} {lo:g}-{hi:g}: {e.mean() if e.size else np.nan:+.3f} "
                  f"({e.size:4}) | {m.mean() if m.size else np.nan:+.3f} ({m.size:5})")
    return to_law(x_model)


def main():
    args = sys.argv[1:]
    names, syms, days, R, raw, ok = universe()
    rows, cols = event_cells(names, syms, days, raw, ok)
    ev = measure(R, raw, rows, cols)
    blocks = F.calendar_blocks(days, R.shape)[ev["row"], ev["col"]]
    sector = np.array([next(n for n, test in SECTORS if test(sic(s))) for s in syms])
    s_ord, k_ord = ordinary_kicks(R)
    report_moves(ev, sector, s_ord, k_ord)
    result, q = report_fit(ev, blocks)
    for group in (("utilities", "REITs"), ("others",)):
        keep = np.isin(sector[ev["row"]], group)
        qg, llg = fit_law(ev["s"][keep], ev["h"][keep], x0=from_law(q))
        seg = jackknife(ev["s"][keep], ev["h"][keep], blocks[keep], qg)
        result[" & ".join(group)] = {"law": qg, "se": seg, "loglik": llg * keep.sum(),
                                     "windows": int(keep.sum())}
        print(f"  {' & '.join(group):19} ({keep.sum():4}): {_law_line(qg, seg)}")
    if "--recover" in args:
        result["model units"] = recover(ev, R, q)
    with open(RESULTS, "w") as f:
        json.dump(result, f, indent=1)
    print(f"\nwritten {RESULTS}")


if __name__ == "__main__":
    main()
