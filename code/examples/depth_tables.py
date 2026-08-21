"""The two tables of section 06: exit probability and call premium by depth.

    python code/examples/depth_tables.py
    python code/examples/depth_tables.py --depths 0.0155,0.03,0.05
    python code/examples/depth_tables.py --measure Q

Backs eq:qx and eq:ccx in section 06.  Closed form throughout -- q(x) is one
evaluation of N(.) and c_c(x) one Black-Scholes call -- so there is nothing
expensive to declare.  Both are functions of depth, so the fields are
sequences: pass your own depths with --depths, which defaults to the list the
section tabulates.  See `holding_time.py` for the other sequence-valued module.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "Depth tables: exit probability and call premium"
SECTION = "sec:depth"
EQ = ["eq:qx", "eq:ccx"]

# The depths section 06 tabulates both tables at, starting from E[x0].
DEFAULT_DEPTHS = [0.0155, 0.03, 0.05, 0.10, 0.15, 0.20]


def _depths(s):
    """Parse a comma-separated depth list, e.g. "0.0155,0.03,0.05"."""
    return [float(t) for t in s.split(",") if t.strip()]


EXTRA = [("--depths", dict(type=_depths, default=DEFAULT_DEPTHS,
                           help="comma-separated depths to tabulate"))]

FIELDS = [
    ("depths", "depth x", ".4f"),
    ("q", "q(x), one-period exit probability", ".3f"),
    ("cc", "c_c(x), call premium (fraction of spot)", ".4f"),
]


def requires(cfg, measure="P", horizon=None, depths=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, depths=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    depths = DEFAULT_DEPTHS if depths is None else depths
    return {
        "depths": list(depths),
        "q": [model.q_exit(cfg, measure, x) for x in depths],
        "cc": [model.call_premium(cfg, x) for x in depths],
    }


CASES = [
    Case("", {
        "depths": ([0.0155, 0.03, 0.05, 0.10, 0.15, 0.20], 1e-9),
        # section 06, the q(x) row:
        "q": ([0.404, 0.306, 0.193, 0.039, 0.004, 0.000], 0.002),
        # section 06, the c_c(x) row:
        "cc": ([0.0161, 0.0110, 0.0060, 0.0009, 0.0001, 0.0000], 0.0002),
    }, note="the running example, four-week calls"),
    Case("--depths 0.0155,0.03,0.05", {
        # the same first three columns, reached through the reader's --depths
        "q": ([0.404, 0.306, 0.193], 0.002),
        "cc": ([0.0161, 0.0110, 0.0060], 0.0002),
    }, note="a reader's own depth list"),
    Case("--n 13", {
        # section 06 contrasts the four-week clock with a quarterly one: the
        # same ten log-points that read 0.039 above read 0.174 here, because
        # the depth is 1.8 of one period's jostle there and 1.0 of it here.
        "q": ([0.463, 0.406, 0.331, 0.174, 0.075, 0.026], 0.002),
        "cc": ([0.0354, 0.0293, 0.0221, 0.0098, 0.0036, 0.0011], 0.0002),
    }, note="a quarterly call clock, for section 06's cliff-edge comparison"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
