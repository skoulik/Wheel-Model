"""The model's buy-write: why a published beta reads differently from this book's.

    python code/bxm_beta.py               # the full table
    python code/bxm_beta.py --paths 60    # quicker, noisier

Section 09 measures this book's split beta (eq:split-beta) and sets it beside
the one published for the Cboe S&P 500 BuyWrite Index (BXM): Israelov and
Nielsen (2015, Table 6) give 0.46 up and 0.85 down over 1996-2014, with a
plain beta of 0.62, "computed using 21-day overlapping returns".  This script
runs the index's construction through the model -- the index held, one call
written on it every 21 trading days at the money (or `offset` above), held to
expiry, and the position marked to Black-Scholes every day -- and fits the
estimator section 09 uses, least squares with an intercept on each side of a
zero stock return, on two clocks:

  * over each option's own life, from the day it is written to the day it
    expires: how section 09 measures its book;
  * on 21-day windows starting on every trading day: how the published figures
    are measured.  Most such windows begin partway through one option's life
    and end partway through the next.

and in two worlds: the article's constant sigma, and a volatility whose log
mean-reverts with the S&P 500's measured swings (wheel_sim.SV_*), around a
level that keeps E[sigma^2] = sigma^2.  There each call is written at the
volatility of its day and marked at the day's; `iv_mult` scales both, a
volatility risk premium when above one.

What it found (2026-11-20; see the table this prints, and
drafts/2026-11-20-published-betas-plan.md for the real index's figures):

  * Over each option's life an at-the-money call gives away the whole of any
    rise to its expiry, so the up-beta is exactly zero -- analytic, not
    simulated.  The down-beta is a little above one because a buy-write's
    return is on its cost, the share less the premium received.
  * On overlapping windows the up-beta rises to about 0.17 at constant sigma
    and the down-beta falls to about 0.83, close to the published 0.85.  No
    variant of the constant-sigma world reaches the published up-beta: a
    strike 2% above spot gives about 0.30, a volatility risk premium a few
    hundredths.
  * With volatility swinging as the S&P 500's does and rising in falls, the
    up-beta reaches about 0.40 and the plain beta about 0.61, against the
    published 0.46 and 0.62, while the down-beta stays near 0.83.  Within one
    option's life the premium is a level, which lifts the fitted line without
    tilting it; pooled over calm and turbulent months it is not, because the
    large moves come with the large premiums.

The `stats` this reports are the swing structure measured on the simulated
paths exactly as it was measured on the index (monthly realized volatility
from 21-day blocks): the standard deviation of its log, its month-to-month
autocorrelation, and a month's return's correlation with its change.  The
index's: 0.48-0.51, 0.64-0.73, -0.35 to -0.43.

Stdlib only.
"""

import argparse
import random
import sys
from math import exp, log, sqrt

from model import Config, bs_call, pmap
from wheel_sim import SV_HALF_LIFE, SV_RHO_INDEX, SV_SD_LOGVOL

DAYS = 21                     # trading days per option, and per window
DT = 1 / 252
YEARS, PATHS, SEED = 40, 200, 20261120
PUBLISHED = (0.46, 0.85, 0.62)   # Israelov and Nielsen (2015), Table 6


class Fit:
    """Least squares with an intercept, accumulated per side: up, down, all."""

    def __init__(self):
        self.s = [[0, 0.0, 0.0, 0.0, 0.0] for _ in range(3)]

    def add(self, x, y):
        for side in ((0, 2) if x > 0 else (1, 2) if x < 0 else (2,)):
            b = self.s[side]
            b[0] += 1
            b[1] += x
            b[2] += y
            b[3] += x * x
            b[4] += x * y

    def merge(self, o):
        for a, b in zip(self.s, o.s):
            for i in range(5):
                a[i] += b[i]
        return self

    def slopes(self):
        """(up, down, plain)."""
        out = []
        for n, sx, sy, sxx, sxy in self.s:
            var = sxx / n - (sx / n) ** 2
            out.append((sxy / n - sx / n * sy / n) / var)
        return tuple(out)


def _path(C, rng, years, offset, iv_mult, sv, rho):
    """One path: the index and the buy-write, daily, and the daily log returns."""
    n = years * 12 * DAYS
    m = C.mu - C.delta
    if sv:
        var = SV_SD_LOGVOL**2
        decay = exp(-log(2) / SV_HALF_LIFE * DT)
        h_sd = sqrt(var * (1 - decay * decay))
        sig_bar = C.sigma * exp(-var)
        rho_c = sqrt(1 - rho * rho)
        h = rng.gauss(0.0, sqrt(var))
    s = v = 1.0
    S, V, R = [s], [v], []
    for _ in range(0, n, DAYS):
        sig = sig_bar * exp(h) if sv else C.sigma
        iv = sig * iv_mult if sv else C.sigma_iv * iv_mult
        k = s * (1 + offset)
        units = v / (s - bs_call(s, k, DAYS * DT, iv, C.r, C.delta))
        for d in range(1, DAYS + 1):
            z = rng.gauss(0.0, 1.0)
            step = (m - sig * sig / 2) * DT + sig * sqrt(DT) * z
            s *= exp(step)
            R.append(step)
            if sv:
                h = h * decay + h_sd * (rho * z + rho_c * rng.gauss(0.0, 1.0))
                sig = sig_bar * exp(h)
                iv = sig * iv_mult
            tau = (DAYS - d) * DT
            v = units * (s - (max(s - k, 0.0) if d == DAYS
                              else bs_call(s, k, tau, iv, C.r, C.delta)))
            S.append(s)
            V.append(v)
    return S, V, R


def _stats(R):
    """The swing structure of one path, measured as on the index."""
    vols, rets = [], []
    for j in range(len(R) // DAYS):
        blk = R[j * DAYS:(j + 1) * DAYS]
        mu = sum(blk) / DAYS
        vols.append(log(sqrt(sum((x - mu) ** 2 for x in blk) / DAYS * 252)))
        rets.append(sum(blk))

    def corr(a, b):
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        ca = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        va = sum((x - ma) ** 2 for x in a)
        vb = sum((y - mb) ** 2 for y in b)
        return ca / sqrt(va * vb)

    ml = sum(vols) / len(vols)
    sd = sqrt(sum((x - ml) ** 2 for x in vols) / len(vols))
    dl = [b - a for a, b in zip(vols, vols[1:])]
    return sd, corr(vols[:-1], vols[1:]), corr(rets[1:], dl)


def _job(job):
    """A block of paths with its own generator.  A pmap worker."""
    C, seed, npaths, years, offset, iv_mult, sv, rho = job
    rng = random.Random(seed)
    life, over = Fit(), Fit()
    st = [0.0, 0.0, 0.0]
    for _ in range(npaths):
        S, V, R = _path(C, rng, years, offset, iv_mult, sv, rho)
        for i in range(0, len(S) - DAYS):
            x = S[i + DAYS] / S[i] - 1
            y = V[i + DAYS] / V[i] - 1
            over.add(x, y)
            if i % DAYS == 0:
                life.add(x, y)
        for i, val in enumerate(_stats(R)):
            st[i] += val
    return life, over, st, npaths


def measure(C=None, offset=0.0, iv_mult=1.0, sv=False, rho=SV_RHO_INDEX,
            paths=PATHS, years=YEARS, seed=SEED, blocks=8):
    """{'life': (up, down, plain), 'over': (...), 'stats': (sd, autocorr, corr)}.

    Split into fixed blocks, each seeding its own generator, so the answer is
    the same however many workers the pool has."""
    C = C if C is not None else Config()
    sizes = [paths // blocks + (1 if i < paths % blocks else 0) for i in range(blocks)]
    jobs = [(C, seed + 7919 * i, n, years, offset, iv_mult, sv, rho)
            for i, n in enumerate(sizes) if n]
    out = pmap(_job, jobs)
    life, over = Fit(), Fit()
    st, total = [0.0, 0.0, 0.0], 0
    for lf, ov, s, n in out:
        life.merge(lf)
        over.merge(ov)
        st = [a + b for a, b in zip(st, s)]
        total += n
    return {"life": life.slopes(), "over": over.slopes(),
            "stats": tuple(x / total for x in st)}


CASES = (
    ("constant sigma, at the money", dict()),
    ("constant sigma, strike 2% above spot", dict(offset=0.02)),
    ("constant sigma, implied 1.2x", dict(iv_mult=1.2)),
    ("changing sigma, no leverage effect", dict(sv=True, rho=0.0)),
    (f"changing sigma, leverage rho = {SV_RHO_INDEX}", dict(sv=True)),
    ("changing sigma, leverage, implied 1.2x", dict(sv=True, iv_mult=1.2)),
)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paths", type=int, default=PATHS)
    ap.add_argument("--years", type=int, default=YEARS)
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    print(f"BXM's construction in the model: {a.paths} paths x {a.years}y per case, "
          f"seed {a.seed}\n")
    print(f"{'':<42}{'each option life':>20}{'21-day overlapping':>22}   swing structure")
    print(f"{'':<42}{'up':>7}{'down':>7}{'plain':>7}{'up':>8}{'down':>7}{'plain':>7}"
          f"   {'sd':>5}{'ac':>6}{'corr':>7}")
    for label, kw in CASES:
        r = measure(paths=a.paths, years=a.years, seed=a.seed, **kw)
        lu, ld, lp = r["life"]
        ou, od, op = r["over"]
        sd, ac, co = r["stats"]
        print(f"{label:<42}{lu:>7.3f}{ld:>7.3f}{lp:>7.3f}{ou:>8.3f}{od:>7.3f}{op:>7.3f}"
              f"   {sd:>5.2f}{ac:>6.2f}{co:>+7.2f}")
    pu, pd, pp = PUBLISHED
    print(f"{'published, BXM 1996-2014':<42}{'':>21}{pu:>8.2f}{pd:>7.2f}{pp:>7.2f}")


if __name__ == "__main__":
    sys.exit(main())
