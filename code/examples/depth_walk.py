"""The depth process: its drift nu, one period's step, and where nu vanishes.

    python code/examples/depth_walk.py
    python code/examples/depth_walk.py --measure Q
    python code/examples/depth_walk.py --sigma 0.30      # nu falls to zero

Backs eq:depth-def, eq:depth-walk and eq:nu in section 06.  Closed form
throughout -- nu = m - sigma^2/2 and the per-period drift and jostle are
time-scalings of it -- so there is nothing expensive to declare.  All three
come from `model.py`: nu from `criteria()`, the per-period step and drift
from `period_step()` and `period_drift()`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "The depth walk: drift, jostle, and where nu vanishes"
SECTION = "sec:depth"
EQ = ["eq:depth-def", "eq:depth-walk", "eq:nu"]

FIELDS = [
    ("m", "price drift m = (mu or r) - delta", ".2%"),
    ("nu", "drift nu = m - sigma^2/2", ".2%"),
    ("jostle", "one period's jostle sigma*sqrt(tau_c)", ".4f"),
    ("drift_step", "one period's drift nu*tau_c", ".4f"),
    ("ratio", "  jostle as a multiple of drift (noise vs drift)", ".1f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    m, _ = cfg.world(measure)
    nu = model.criteria(cfg, measure)["nu"]
    jostle = model.period_step(cfg, measure)
    drift_step = model.period_drift(cfg, measure)
    return {
        "m": m,
        "nu": nu,
        "jostle": jostle,
        "drift_step": drift_step,
        # a ratio the section displays as one ("a factor of twenty-nine");
        # guarded so the vanishing-nu case prints inf rather than dividing by ~0.
        "ratio": jostle / drift_step if abs(drift_step) > 1e-12 else float("inf"),
    }


CASES = [
    Case("", {
        "m": (0.045, 0.0005),           # section 05: "delta = 2.5%, so m = 4.5%"
        "nu": (0.025, 0.0005),          # section 06: "nu = 7% - 2.5% - 2% = 2.5%"
        # Tolerances here are tighter than the article's own rounding on
        # purpose: these two set the scale of everything downstream, and the
        # checks they replaced in verify_examples.py pinned them to 1e-5.
        "jostle": (0.05547, 0.00002),   # "0.2 x sqrt(1/13) = 0.055"
        "drift_step": (0.001923, 0.000002),  # "0.025 / 13 = 0.0019"
        "ratio": (29.0, 1.0),           # "Noise beats drift by a factor of 29"
    }, note="Standard regime, real world"),
    Case("--measure Q", {
        "m": (0.025, 0.0005),           # m = r - delta = 5% - 2.5%
        "nu": (0.005, 0.0005),          # "the same formula gives nu = ... = 0.5%"
    }, note="under the market's pricing drift"),
    Case("--sigma 0.30", {
        "nu": (0.0, 1e-6),              # "sigma = 30% would cut nu ... to zero"
    }, note="the volatility at which nu vanishes"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
