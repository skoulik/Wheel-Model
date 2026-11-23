"""Grid-free Monte Carlo of the depth walk, as a check on model.stationary().

The analytic core computes holding times by pushing a discretized density
through the killed walk, which puts the absorbing boundary on cell centres
and holds lots marginally too long.  `model.stationary()` corrects that by
Richardson extrapolation; this script is the independent evidence that the
correction is right, because it uses no spatial grid at all: it draws the
entry depth from the exact truncated-normal entry law by inversion and then
steps

    x  ->  x - nu*tau_c + sigma*sqrt(tau_c)*Z

until the first period end with x <= 0, exactly as the model defines exit.
E[J] is the mean number of periods lived and E[T] = tau_c*E[J].

What it found (2026-07-26, Standard regime, mean holding time in years):

    cadence            h=0.05   h=0.025   h=0.0125   extrapolated    MC 300k
    weekly / 4-week     2.589    2.202     2.125        2.099      2.08 / 2.13
    monthly / quarterly 4.183    4.026     3.989        3.977         3.981

The single coarse grid the article quoted before this was written overstated
the mean holding time by 23% at the weekly cadence and by 5% at the monthly
one.  Note the MC's own precision: J has a standard deviation about 5.6x its
mean, so 300k paths give roughly +-1% and two seeds can sit 2sd apart (the
two weekly figures above are different seeds).  The grid sequence, whose
error falls by 4x per halving of h, is the more precise instrument here; the
MC's job is to rule out a systematic error common to every grid, which it
does.

`--window` asks the same of the finite-horizon figures, which come off the near grid
Richardson-extrapolated from h = 0.01 and 0.005 (TODO II-32): it counts the walks still
alive at each period start, which is the survival sequence occupation() returns, and puts it
through the same two functionals -- the lots held at thirty years (inventory_at) and their
average over the window (economics' "I"). What it found (2026-11-24, 30 years):

                            MC                      single h=0.01   extrapolated
    Standard      held      15.322 +- 0.005 (1e8)        15.424         15.325
                  average   11.324 +- 0.003              11.396         11.327
    Conservative  held       7.377 +- 0.002 (2e8)         7.440          7.378
                  average    5.459 +- 0.001               5.503          5.460

The single grid sits 20 to 45 standard errors high, the extrapolated pair within one.

Run:  python code/mc_holding.py [--paths N] [--measure P|Q] [--no-grid]
      python code/mc_holding.py --window [--paths N] [--p-star 0.10]

Stdlib only (Python 3.8+), except `--window`, which needs numpy for its 1e8 walks.
"""

import argparse
import random
from math import log, sqrt

from model import (Config, Ninv, _time_avg_weights, arrival_rate, economics,
                   inventory_at, occupation, stationary, strike)


def sample_x0(C, measure, rng):
    """One draw of the entry depth x0 = ln k - z, given z < ln k.

    Inverse-CDF sampling of the truncated normal: by construction of k*,
    P(z < ln k) = p*, so scaling a uniform by p* lands inside the tail.
    """
    m, s = C.world(measure)
    k = strike(C, measure)
    mean_z = (m - s**2 / 2) * C.tau_p
    sd_z = s * sqrt(C.tau_p)
    z = mean_z + sd_z * Ninv(rng.random() * C.p_star)
    return log(k) - z


def mc_holding(C, measure, n_paths, seed=20260726):
    """Mean periods lived, and the standard error of that mean."""
    rng = random.Random(seed)
    m, s = C.world(measure)
    drift = -(m - s**2 / 2) * C.tau_c
    sc = s * sqrt(C.tau_c)
    total = total_sq = 0.0
    for _ in range(n_paths):
        x = sample_x0(C, measure, rng)
        j = 0
        while x > 0.0:
            x += drift + sc * rng.gauss(0.0, 1.0)
            j += 1
        total += j
        total_sq += j * j
    mean = total / n_paths
    var = max(0.0, total_sq / n_paths - mean * mean)
    return mean, sqrt(var / n_paths)


def mc_window(C, measure, n_paths, horizon=30.0, seed=20261124, batch=1_000_000):
    """Lots held at the horizon and their window average, each with its standard error.

    Each batch of walks gives one survival sequence S_j = P(J > j), the fraction still alive
    at the start of period j, and so one reading of each figure; their spread over batches is
    the error.  The entry is drawn exactly, by rejection from the untruncated normal.
    """
    import numpy as np
    m, s = C.world(measure)
    lk = log(strike(C, measure))
    mean_z, sd_z = (m - s ** 2 / 2) * C.tau_p, s * sqrt(C.tau_p)
    drift, sc = -(m - s ** 2 / 2) * C.tau_c, s * sqrt(C.tau_c)
    j_max = int(round(horizon / C.tau_c)) + 1
    lam = arrival_rate(C, measure)
    rng = np.random.default_rng(seed)
    held, avg = [], []
    for _ in range(max(2, n_paths // batch)):
        x = np.empty(0)
        while x.size < batch:
            z = mean_z + sd_z * rng.standard_normal(int(batch / C.p_star * 1.1) + 1000)
            x = np.concatenate([x, lk - z[z < lk]])
        x = x[:batch]
        surv = []
        for _ in range(j_max + 1):
            surv.append(x.size / batch)
            x = x + drift + sc * rng.standard_normal(x.size)
            x = x[x > 0.0]
        held.append(inventory_at(C, measure, {"surv": surv}, horizon))
        w = _time_avg_weights(surv, C.tau_c, horizon)
        avg.append(lam * sum(f * wi for f, wi in zip(surv, w)))
    out = []
    for v in (held, avg):
        a = np.array(v)
        out.append((float(a.mean()), float(a.std(ddof=1) / sqrt(len(a)))))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paths", type=int, default=300000)
    ap.add_argument("--measure", default="P", choices=("P", "Q"))
    ap.add_argument("--no-grid", dest="grid", action="store_false",
                    help="skip the analytic comparison (MC only)")
    ap.add_argument("--window", action="store_true",
                    help="the finite-horizon figures at thirty years instead (needs numpy)")
    ap.add_argument("--p-star", dest="p_star", type=float, default=0.20)
    args = ap.parse_args()

    C = Config(p_star=args.p_star,
               label="Standard" if args.p_star == 0.20 else "Conservative")
    if args.window:
        (h, h_se), (a, a_se) = mc_window(C, args.measure, args.paths)
        print(f"p*={C.p_star}  measure={args.measure}  walks={args.paths:,}, 30 years")
        print(f"  MC        held {h:8.4f} +- {h_se:.4f}   average {a:8.4f} +- {a_se:.4f}")
        if args.grid:
            for name, occ in (("single h=0.01", occupation(C, args.measure, h=0.01)),
                              ("extrapolated", occupation(C, args.measure))):
                hg = inventory_at(C, args.measure, occ, 30.0)
                ag = economics(C, args.measure, occ, horizon=30.0)["I"]
                print(f"  {name:<13} held {hg:8.4f} ({(hg - h) / h_se:+5.1f} se)"
                      f"   average {ag:8.4f} ({(ag - a) / a_se:+5.1f} se)")
        return
    print(f"{C.label}: tau_p={C.tau_p:.5f}  tau_c={C.tau_c:.5f}  "
          f"measure={args.measure}  paths={args.paths}")
    ej, se = mc_holding(C, args.measure, args.paths)
    print(f"  MC        E[J] = {ej:8.3f} +- {se:.3f}   "
          f"E[T] = {ej * C.tau_c:6.3f} y +- {se * C.tau_c:.3f}")
    if args.grid:
        far = stationary(C, args.measure)
        e = economics(C, args.measure, far)
        gap = (e["E[T]"] / (ej * C.tau_c) - 1) * 100
        print(f"  analytic  E[J] = {far['E[J]']:8.3f}          "
              f"E[T] = {e['E[T]']:6.3f} y   ({far['method']}, "
              f"{gap:+.2f}% vs MC)")


if __name__ == "__main__":
    main()
