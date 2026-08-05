"""Why our split beta and the Cboe buy-write index's cannot be compared.

Section 09 reports the wheel's up- and down-beta on a terminal-payoff
estimator.  A reader who knows the covered-call literature will want to set
that against BXM's published pair, roughly **0.63 / 0.78**, and the comparison
is invalid.  This script measures how invalid, by replicating BXM's own
construction -- a plain at-the-money covered call on one name, rewritten every
month -- and then varying the two things that separate the estimators:

  * the MEASUREMENT CLOCK.  BXM reports calendar-monthly returns while its
    options expire mid-month, so every measured period straddles two different
    strikes and averages across the kink in the payoff.
  * the STRIKE OFFSET.  BXM writes the first strike listed *above* spot, not
    one exactly at it, so a small first slice of any rise is not sold.

Both push the up-beta away from the zero a kinked payoff must produce, and the
question is how much of the published figure they account for.

What it found (2026-08-05, sigma = 20%, 40y x 4000 paths, both seeds equal):

    measurement clock     strike             up     down
    on the roll           exactly at spot  -0.000    1.025
    on the roll           1% above spot     0.022    1.020
    on the roll           2% above spot     0.080    1.016
    off-cycle (calendar)  exactly at spot   0.164    0.827
    off-cycle (calendar)  1% above spot     0.222    0.878
    off-cycle (calendar)  2% above spot     0.289    0.918
    BXM published                           0.630    0.780

Three readings.  **The aligned at-the-money up-beta is exactly zero**, which
is analytic rather than simulated: an at-the-money call gives away the whole
of every rise, so the up-side payoff is flat and no slope exists to find.
**Misalignment is the larger of the two mechanisms**, worth about twice the
strike offset on the up side and essentially the only one that moves the down
side at all.  And **together they reach 0.29 against a published 0.63**, so
more than half the gap is neither -- a real index's returns are not a
geometric Brownian motion, and a beta estimated on one is a different object.
That is the finding: the estimators are further apart than the two mechanical
differences explain, which is a stronger reason not to compare them.

The down-beta here is 1.02 rather than section 09's exact 1.00 because the
denominators differ: a buy-write's return is on its own cost, share price less
premium, while section 09 normalises inventory by the share price itself.

    python code/bxm_beta.py
"""

import random
import sys
from math import exp, sqrt

from model import Config, bs_call

TAU = 1 / 12                  # one month between expiries
YEARS, PATHS, SEED = 40, 4000, 20260805


def split_ols(xs, ys):
    """(up-slope, down-slope): OLS of y on x, fitted separately by sign of x.

    The same estimator `model.split_beta` applies to the wheel -- a regression
    WITH an intercept on each side, which is what the covered-call literature
    reports.
    """
    out = []
    for keep in (lambda v: v > 0, lambda v: v < 0):
        px = [x for x in xs if keep(x)]
        py = [y for x, y in zip(xs, ys) if keep(x)]
        n = len(px)
        mx, my = sum(px) / n, sum(py) / n
        cov = sum((a - mx) * (b - my) for a, b in zip(px, py)) / n
        var = sum((a - mx) ** 2 for a in px) / n
        out.append(cov / var)
    return out[0], out[1]


def _path(C, offset, calendar, rng, years=YEARS):
    """One path's (underlying returns, buy-write returns)."""
    mu, sig = C.mu - C.delta, C.sigma
    steps = 2 if calendar else 1          # measure twice a month, roll once
    s = 1.0
    strike = s * (1 + offset)
    u_ret, b_ret = [], []
    u_mark = s
    b_mark = s - bs_call(s, strike, TAU, C.sigma_iv, C.r, C.delta)
    t = 0.0
    for _ in range(years * 12 * steps):
        dt = TAU / steps
        s *= exp((mu - sig**2 / 2) * dt + sig * sqrt(dt) * rng.gauss(0.0, 1.0))
        t += dt
        rolled = t >= TAU - 1e-12
        if rolled:
            value, t = s - max(s - strike, 0.0), 0.0
        else:
            value = s - bs_call(s, strike, TAU - t, C.sigma_iv, C.r, C.delta)
        if calendar or rolled:
            u_ret.append(s / u_mark - 1.0)
            b_ret.append(value / b_mark - 1.0)
            u_mark, b_mark = s, value
        if rolled:
            strike = s * (1 + offset)
            b_mark = s - bs_call(s, strike, TAU, C.sigma_iv, C.r, C.delta)
    return u_ret, b_ret


def measure(offset, calendar, C=None, paths=PATHS, years=YEARS, seed=SEED):
    """(up-beta, down-beta) of a monthly buy-write under one convention."""
    C = C if C is not None else Config()
    rng = random.Random(seed)
    U, B = [], []
    for _ in range(paths):
        u, b = _path(C, offset, calendar, rng, years)
        U += u
        B += b
    return split_ols(U, B)


def main():
    C = Config()
    print(f"monthly at-the-money buy-write, sigma={C.sigma:.0%}, "
          f"{YEARS}y x {PATHS} paths\n")
    print(f"{'measurement clock':<22}{'strike':<18}{'up':>8}{'down':>8}")
    for calendar in (False, True):
        for offset, name in ((0.0, "exactly at spot"), (0.01, "1% above spot"),
                             (0.02, "2% above spot")):
            up, dn = measure(offset, calendar, C)
            clock = "off-cycle (calendar)" if calendar else "on the roll"
            print(f"{clock:<22}{name:<18}{up:>8.3f}{dn:>8.3f}")
    print(f"{'BXM published':<40}{0.630:>8.3f}{0.780:>8.3f}")


if __name__ == "__main__":
    sys.exit(main())
