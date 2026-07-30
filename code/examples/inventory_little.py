"""Little's law: arrival rate, equilibrium inventory, and the slow approach.

    python code/examples/inventory_little.py
    python code/examples/inventory_little.py --measure Q

Backs eq:lambda and eq:little in section 08 (eq:little is also registered in
sections/00-notation.md).  E[I] = λ·E[W]: lots arrive at rate λ, stay E[W] on
average, so the standing inventory is their product.

Two walks, for the reason holding_time.py documents.  The equilibrium
inventory and the time to approach it are whole-lifetime quantities, carried by
the tail the near grid truncates and biases, so they come off the extrapolated
walk.  The 5/10/30-year trajectory is horizon-weighted -- the far tail barely
contributes -- and comes off the near grid, through economics(..., horizon=H).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_occupation, need_stationary,      # noqa: E402
                               resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "The inventory: Little's law"
SECTION = "sec:inventory"
EQ = ["eq:lambda", "eq:little", "eq:little-finite"]

# The horizons section 08 tabulates against equilibrium, in years.
HORIZONS = [5.0, 10.0, 30.0]

FIELDS = [
    ("lam", "arrival rate lambda = p*/T (lots/year)", ".1f"),
    ("EW", "mean holding time E[W] (years)", ".2f"),
    ("EI_eq", "equilibrium E[I] = lambda*E[W] (lots)", ".2f"),
    ("at_h", "E[I(H)], holdings at H", ".2f"),
    ("horizons", "  average over [0, H]", ".2f"),
    ("hlabels", "  ", ">6s"),
    ("approach90", "years to reach 90% of equilibrium", ".0f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return [need_occupation(cfg, measure), need_stationary(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    near = resolve(ctx, need_occupation(cfg, measure))
    full = resolve(ctx, need_stationary(cfg, measure))
    eq = model.economics(cfg, measure, full)              # horizon=None: equilibrium
    return {
        "lam": eq["lambda"],
        "EW": eq["E[T]"],
        "EI_eq": eq["I"],
        # Two different quantities, and section 08 tabulates both: what is
        # held *at* H, and the average across [0, H] that a return over the
        # window has to be divided by.  They differ by a third at 30 years.
        "at_h": [model.inventory_at(cfg, measure, near, h) for h in HORIZONS],
        "horizons": [model.economics(cfg, measure, near, horizon=h)["I"]
                     for h in HORIZONS],
        "hlabels": [f"{h:.0f} y" for h in HORIZONS],
        "approach90": model.time_to_fraction(cfg, full, 0.9),
    }


CASES = [
    Case("", {
        "lam": (10.4, 0.05),            # eq:lambda: "0.20 / (1/52) = 10.4 lots per year"
        "EW": (2.10, 0.02),             # eq:holding, carried into eq:little
        "EI_eq": (21.8, 0.1),           # eq:little: "10.4 × 2.10 = 21.8 lots"
        "at_h": ([7.95, 10.57, 15.42], 0.05),      # eq:little-finite, top row
        "horizons": ([5.41, 7.39, 11.40], 0.05),   # the [0,H] average row
        "approach90": (90.0, 3.0),      # "Reaching 90% of the equilibrium level takes 90 years"
    }, note="Standard regime"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
