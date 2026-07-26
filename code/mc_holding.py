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

Run:  python code/mc_holding.py [--paths N] [--measure P|Q] [--no-grid]

Stdlib only (Python 3.8+).
"""

import argparse
import random
from math import log, sqrt

from model import Config, Ninv, economics, stationary, strike


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paths", type=int, default=300000)
    ap.add_argument("--measure", default="P", choices=("P", "Q"))
    ap.add_argument("--no-grid", dest="grid", action="store_false",
                    help="skip the analytic comparison (MC only)")
    args = ap.parse_args()

    C = Config(p_star=0.20, label="Standard")
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
