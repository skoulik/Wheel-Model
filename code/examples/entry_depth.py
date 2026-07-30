"""How deep an assignment lands: the entry depth x0 and its law.

    python code/examples/entry_depth.py
    python code/examples/entry_depth.py --measure Q
    python code/examples/entry_depth.py --p-star 0.10

Backs eq:x0-def, eq:x0-law and eq:d-mean in section 05.  Closed form
throughout -- x0 is a truncated normal and its mean, its drop-from-price
reading, and its density all have closed forms -- so there is nothing
expensive to declare.  See `entry_strike.py`, the sibling that picks the
strike this depth is measured against.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "Entry: how deep assignment lands"
SECTION = "sec:entry"
EQ = ["eq:x0-def", "eq:x0-law", "eq:d-mean"]

# Where eq:x0-law's density is sampled, so the law is shown rather than only
# asserted through its mean.  E[x0] and two depths past it, tracing the tail.
DENS_DEPTHS = [0.0155, 0.03, 0.05]

FIELDS = [
    ("x0", "E[x0], typical entry depth (log)", ".4f"),
    ("drop", "E[d | assignment], drop from the prior price", ".2%"),
    ("basis", "E[K/S'] = E[e^x0], the acquisition mark-loss factor", ".4f"),
    ("dens", "density f(x0) at the depths below", ".2f"),
    ("dens_at", "  those depths", ".4f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    _, _, mean_x0, dens = model.entry_law(cfg, measure)
    return {
        "x0": mean_x0,
        "drop": model.expected_drop(cfg, measure),
        "basis": model.entry_basis_ratio(cfg, measure),
        "dens": [dens(x) for x in DENS_DEPTHS],
        "dens_at": list(DENS_DEPTHS),
    }


CASES = [
    Case("", {
        "x0": (0.0155, 0.0005),         # section 05: "E[x0] ~ 0.0155"
        "drop": (0.038, 0.001),         # eq:d-mean, "giving 3.8% for Standard"
    }, note="Standard regime"),
    Case("--measure Q", {
        "drop": (0.038, 0.001),         # "Under the market's drift they are
    }, note="the same, read under the pricing drift"),  # 3.8% ... as well"
    Case("--p-star 0.10", {
        "x0": (0.0131, 0.0005),         # "Conservative entries ... E[x0] ~ 0.0131"
        "drop": (0.047, 0.001),         # eq:d-mean, "4.7% for Conservative"
    }, note="Conservative regime"),
    Case("--p-star 0.10 --measure Q", {
        "drop": (0.047, 0.001),         # "3.8% and 4.7% as well" under Q --
    }, note="Conservative under the pricing drift"),   # differ in the 4th decimal
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
