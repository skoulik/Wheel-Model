"""When lots never leave: the permanently trapped fraction at ν <= 0.

    python code/examples/holding_trapped.py
    python code/examples/holding_trapped.py --sigma 0.40   # the section's case

Backs eq:trapped in section 07.  This is a different regime from the rest of
the section -- the running example has ν > 0 and traps nobody -- so the default
prints a zero trapped fraction and the headline figures come out at --sigma
0.40, where ν goes negative.

The fraction itself is a closed form (`trapped_fraction`); the rate at which
the trapped stratum grows needs the arrival rate alongside it, which is why
this hangs off the same killed walk the rest of the section uses.  At ν <= 0
the mean holding time is infinite and the median may not exist -- the walk
never crosses a half if enough lots are trapped -- so those are printed
defensively rather than asserted.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, need_occupation, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Trapped lots: the fraction that never comes back"
SECTION = "sec:holding"
EQ = ["eq:trapped"]

FIELDS = [
    ("nu", "drift nu = m - sigma^2/2", ".4f"),
    ("count_ok", "lots return (nu > 0)?", ""),
    ("trapped", "P(J = infinity), the trapped fraction", ".4f"),
    ("lam", "arrival rate lambda (lots/year)", ".2f"),
    ("growth", "  trapped stratum growth, lambda*P (lots/year)", ".3f"),
    ("median", "median lifetime, in call periods", "d"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    # One walk, and only for the median -- the trapped fraction, the drift
    # sign and the arrival rate are all closed forms.  The near grid is right
    # for a shallow-curve quantity, as in holding_time.py.
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    near = resolve(ctx, need_occupation(cfg, measure))
    crit = model.criteria(cfg, measure)
    trapped = model.trapped_fraction(cfg, measure)
    lam = model.arrival_rate(cfg, measure)
    return {
        "nu": crit["nu"],
        "count_ok": crit["count_ok"],
        "trapped": trapped,
        "lam": lam,
        "growth": lam * trapped,
        "median": model.median_periods(near),
    }


CASES = [
    Case("", {
        "count_ok": (True, 0),          # section 07: "Everything above assumed ν > 0"
        "trapped": (0.0, 1e-9),         # a favourable drift traps nobody
        "growth": (0.0, 1e-9),
    }, note="running example: favourable drift, nothing trapped"),
    Case("--sigma 0.40", {
        "nu": (-0.035, 0.0005),         # "ν = −3.5%"
        "count_ok": (False, 0),
        "trapped": (0.041, 0.001),      # "4.1% of every assignment permanently trapped"
        "lam": (10.4, 0.1),             # arrivals unchanged by sigma under P
        "growth": (0.43, 0.02),         # "grows by λ × 4.1% ≈ 0.43 lots a year"
    }, note="sigma = 40%, where ν goes negative"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
