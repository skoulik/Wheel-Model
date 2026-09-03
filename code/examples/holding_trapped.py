"""When lots never leave: the permanently trapped fraction at ν <= 0.

    python code/examples/holding_trapped.py
    python code/examples/holding_trapped.py --sigma 0.40   # the section's case

Backs eq:trapped in section 07.  This is a different regime from the rest of
the section -- the running example has ν > 0 and traps nobody -- so the default
prints a zero trapped fraction and the headline figures come out at --sigma
0.40, where ν goes negative.

The rate at which the trapped stratum grows needs the arrival rate alongside
the fraction, which is why this hangs off the same killed walk the rest of the
section uses.  At ν <= 0 the mean holding time is infinite and the median may
not exist -- the walk never crosses a half if enough lots are trapped -- so
those are printed defensively rather than asserted.

Three readings of one quantity, and the section quotes the middle one.
eq:trapped (`trapped_fraction`) is the closed form: the continuously-monitored
escape probability with Siegmund's shift standing in for the overshoot.  It is
a reasoning aid rather than the answer -- BETA is a far-barrier constant and a
lot sits 0.28 of a step from its exit -- and it runs 7.8% low at the entry law
and 17.6% low at zero entry depth.  `trapped_fraction_walk` runs the walk
instead and is what the section prints.  `trapped_zero_depth` is the zero-depth
end, where the exact answer is published in closed form rather than computed.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_occupation, need_trapped_walk,   # noqa: E402
                               resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "Trapped lots: the fraction that never comes back"
SECTION = "sec:holding"
EQ = ["eq:trapped"]

FIELDS = [
    ("nu", "drift nu = m - sigma^2/2", ".4f"),
    ("count_ok", "lots return (nu > 0)?", ""),
    ("trapped", "P(J = infinity), on the walk itself", ".4f"),
    ("trapped_cf", "  eq:trapped's closed form, for comparison", ".4f"),
    ("shortfall", "  how far the closed form runs low", ".1%"),
    ("lam", "arrival rate lambda (lots/year)", ".2f"),
    ("growth", "  trapped stratum growth, lambda*P (lots/year)", ".3f"),
    ("zero", "at zero entry depth: exact (Janssen & van Leeuwaarden)", ".4f"),
    ("zero_cf", "  the closed form there", ".4f"),
    ("zero_shortfall", "  and how far low it runs", ".1%"),
    ("median", "median lifetime, in call periods", "d"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    # Two walks.  The near grid is for the median alone, as in holding_time.py;
    # the unshifted one is the trapped fraction and is the expensive half --
    # though only where nu <= 0, since it returns zero without running above it.
    return [need_occupation(cfg, measure), need_trapped_walk(cfg, measure)]


def _short(cf, exact):
    """How far the closed form runs below the exact answer, as a fraction."""
    return 1 - cf / exact if exact > 0 else 0.0


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    near = resolve(ctx, need_occupation(cfg, measure))
    walk = resolve(ctx, need_trapped_walk(cfg, measure))
    crit = model.criteria(cfg, measure)
    trapped, cf = walk["trapped"], model.trapped_fraction(cfg, measure)
    # At zero entry depth there is no hole to climb out of and the grid tax is
    # the whole of the exponent -- which is where the closed form is worst.
    zero = model.trapped_zero_depth(cfg, measure)
    zero_cf = model.trapped_fraction(cfg, measure, zero_depth=True)
    lam = model.arrival_rate(cfg, measure)
    return {
        "nu": crit["nu"],
        "count_ok": crit["count_ok"],
        "trapped": trapped,
        "trapped_cf": cf,
        "shortfall": _short(cf, trapped),
        "lam": lam,
        "growth": lam * trapped,
        "zero": zero,
        "zero_cf": zero_cf,
        "zero_shortfall": _short(zero_cf, zero),
        "median": model.median_periods(near),
    }


CASES = [
    Case("", {
        "count_ok": (True, 0),          # section 07: "Everything above assumed ν > 0"
        "trapped": (0.0, 1e-9),         # a favourable drift traps nobody
        "trapped_cf": (0.0, 1e-9),
        "growth": (0.0, 1e-9),
        "zero": (0.0, 1e-9),
    }, note="running example: favourable drift, nothing trapped"),
    Case("--sigma 0.40", {
        "nu": (-0.035, 0.0005),         # "ν = −3.5%"
        "count_ok": (False, 0),
        "trapped": (0.0444, 0.0002),    # "4.4% of every assignment permanently trapped"
        "trapped_cf": (0.0409, 0.0002),  # what eq:trapped as printed gives
        "shortfall": (0.078, 0.005),    # "the closed form runs 8% low"
        "lam": (10.4, 0.1),             # arrivals unchanged by sigma under P
        "growth": (0.461, 0.005),       # "grows by λ × 4.4% ≈ 0.46 lots a year"
        # The published endpoint, and the one number here that is exact rather
        # than computed: Janssen & van Leeuwaarden theorem 1.  A route that
        # gets the entry-law figure right and misses this has the shape wrong.
        "zero": (0.033838, 0.000005),
        "zero_cf": (0.027881, 0.000005),
        "zero_shortfall": (0.176, 0.002),   # "17.6% low, worst where strikes are furthest out"
    }, note="sigma = 40%, where ν goes negative"),
    # The put clock, not the call clock, is what moves the arrival rate: tau_c
    # is 4 wk in both this case and the one above, so the grid tax is identical
    # and the whole difference in the trapped share is the entry law getting
    # shallower.  Section 07 quotes the pair against each other.
    Case("--sigma 0.40 --tau-p 0.07692 --n 1", {
        "nu": (-0.035, 0.0005),
        "trapped": (0.0559, 0.0002),    # "falls from 5.6% to 4.4%"
        "lam": (2.60, 0.02),            # "the arrival rate quadruples"
        "growth": (0.145, 0.002),       # "0.46 lots a year against 0.15"
    }, note="monthly put clock: fewer arrivals, deeper entries, more trapped"),
    # INF-6's regression guard, and the only Case in the suite that varies the
    # cadence.  lambda = p*/T, so a monthly put sold monthly arrives 2.40 times
    # a year against the weekly 10.40.  Until 2026-08-05 the harness took each
    # flag's default from a POST-INIT Config, which had already resolved
    # `cadence` from None to tau_p -- so every CLI-built Config passed
    # cadence=1/52 explicitly and this case would have read 10.40, a monthly
    # put sold every week.  Nothing else in the suite varies --tau-p, which is
    # why the trap sat live and invisible; if this case ever reads 10.40 again,
    # the defaulting has regressed.
    Case("--tau-p 0.0833333", {
        "lam": (2.40, 0.01),
        "count_ok": (True, 0),          # cadence does not touch the drift
        "nu": (0.025, 0.0005),
    }, note="monthly cadence: the arrival rate must follow tau_p"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
