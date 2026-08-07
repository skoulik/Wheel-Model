"""How long until a put assigns: the geometric wait, closed form and simulated.

    python code/examples/entry_wait.py
    python code/examples/entry_wait.py --p-star 0.10
    python code/examples/entry_wait.py --measure Q
    python code/examples/entry_wait.py --sim-periods 4000000

Backs eq:wait in section 05.

WHAT THE SIMULATION IS FOR, AND WHAT IT IS NOT FOR.  Drawing Bernoulli
variates to check that the mean wait is 1/p would be theatre: it samples the
very distribution the formula describes and can only fail if `random` is
broken.
So this draws the PRICE PATH instead.  Each period it re-strikes a put at
k* times the current price, draws that period's lognormal return, and calls
the put assigned if the return finishes below the strike.  That runs the
whole chain -- eq:kstar -> a strike -> actual assignments -> the realized
rate and the observed waits -- and would catch an inverted N^-1 in
`k_star_drift`, which is the kind of error this project has shipped before
in d2 and in q.

It does NOT test the independence of successive puts.  In this model the
periods are independent by construction, so the trials inherit it, and a
simulation of a model cannot refute that model's own assumption.  Section 05
says so in those words; nothing here should be read as evidence for it.

Seeded, so the appendix row is stable and the assertions are reproducible.
Stdlib only, like every module here.
"""

import os
import sys

from math import ceil, log, sqrt
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Entry: how long until a put assigns"
SECTION = "sec:entry"
EQ = ["eq:wait"]

SEED = 20260807

EXTRA = [("--sim-periods", dict(type=int, default=1000000,
                                help="periods of price path to simulate"))]

FIELDS = [
    ("p_star", "p*, the dial", ".2%"),
    ("mean_closed", "E[puts to the first assignment]", ".3f"),
    ("median_closed", "  its median", ".0f"),
    ("tail7", "  P(still waiting after 7)", ".3f"),
    ("tail13", "  P(still waiting after 13)", ".3f"),
    ("sim_rate", "simulated: assignments per put", ".4f"),
    ("sim_mean", "  mean wait", ".3f"),
    ("sim_median", "  median wait", ".0f"),
    ("sim_periods", "  periods drawn", ".0f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def _simulate(cfg, measure, periods, seed=SEED):
    """Walk the price, re-striking a put each period; return (rate, waits).

    The strike floats -- it is k* times whatever the price is now -- so the
    only thing that decides a period is that period's own return, and the
    price level never has to be carried.  That is the same fact section 05
    gives as the reason the trials are identical from period to period.
    """
    m, s = cfg.world(measure)
    k = model.strike(cfg, measure)
    ln_k = log(k)
    mean_z = (m - s**2 / 2) * cfg.tau_p
    sd_z = s * sqrt(cfg.tau_p)

    rng = Random(seed)
    gauss = rng.gauss
    hits, waits, since = 0, [], 0
    for _ in range(periods):
        since += 1
        if gauss(mean_z, sd_z) < ln_k:
            hits += 1
            waits.append(since)
            since = 0
    waits.sort()
    n = len(waits)
    median = waits[n // 2] if n % 2 else 0.5 * (waits[n // 2 - 1] + waits[n // 2])
    return hits / periods, sum(waits) / n, median


def compute(cfg=None, measure="P", horizon=None, ctx=None, sim_periods=1000000,
            **kw):
    cfg = cfg if cfg is not None else model.Config()
    _, p, _, _ = model.entry_law(cfg, measure)
    if not 0 < p < 1:
        raise ValueError(f"p* must lie strictly in (0, 1), got {p}")

    rate, mean_sim, median_sim = _simulate(cfg, measure, sim_periods)
    return {
        "p_star": p,
        "mean_closed": 1.0 / p,
        "median_closed": float(ceil(log(0.5) / log(1.0 - p))),
        "tail7": (1.0 - p) ** 7,
        "tail13": (1.0 - p) ** 13,
        "sim_rate": rate,
        "sim_mean": mean_sim,
        "sim_median": median_sim,
        "sim_periods": float(sim_periods),
    }


# Tolerances are set from the sampling error, not from taste.  At p* = 20%
# over 1e6 periods there are ~2e5 waits with a standard deviation of 4.47, so
# the mean carries a standard error near 0.010 and 0.05 is five of them.  The
# rate is ~2e5 successes in 1e6 Bernoulli trials, s.e. 4e-4.
CASES = [
    Case("", {
        "p_star": (0.20, 1e-9),
        "mean_closed": (5.0, 1e-9),
        "median_closed": (4.0, 1e-9),     # not 5: the wait's median is below
        "tail7": (0.210, 0.001),          #   its mean, and this is the mildest
        "tail13": (0.055, 0.001),         #   case of that in the article
        "sim_rate": (0.20, 0.002),        # the dial, recovered from the path
        "sim_mean": (5.0, 0.05),
        "sim_median": (4.0, 0.5),
    }, note="Standard regime, the dial recovered end to end from eq:kstar"),
    Case("--p-star 0.10", {
        "p_star": (0.10, 1e-9),
        "mean_closed": (10.0, 1e-9),
        "median_closed": (7.0, 1e-9),
        "sim_rate": (0.10, 0.002),
        "sim_mean": (10.0, 0.15),
        "sim_median": (7.0, 0.5),
    }, note="Conservative: both figures double, the gap with them"),
    Case("--measure Q", {
        "p_star": (0.20, 1e-9),           # the dial is the dial in either
        "sim_rate": (0.20, 0.002),        #   world; only the strike moves
    }, note="the same dial read under the pricing drift"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
