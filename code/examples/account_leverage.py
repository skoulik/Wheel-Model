"""The finite account: leverage, and the price at which it is sold out.

    python code/examples/account_leverage.py
    python code/examples/account_leverage.py --gamma-s 0.25 --u-star 1.0
    python code/examples/account_leverage.py --gamma-s 0.25 --u-star 0.5

Backs eq:leverage and eq:barrier in section 11.  Closed form throughout -- L
is one division and f* one more -- so there is nothing expensive to declare;
this is a leverage-and-barrier sibling of the entry_strike.py exemplar.

Two knobs, both Config fields: gamma_s (the account type -- 1.00 fully paid,
0.50 Reg T, 0.25 portfolio margin, 0.15 aggressive) and u_star (the operator's
stopping rule, u = 1 being the broker's own ceiling).  Leverage is L = u/gamma_s
and the liquidation barrier is f* = (1 - 1/L)/(1 - gamma_s): the price ratio
below which equity falls through the maintenance requirement and the book is
sold out.  Both boundary cases are the formula telling the truth -- an unlevered
book (f* <= 0) is never called, and a book at L = 1/gamma_s is in violation on
the day it is opened (f* >= 1).  The defaults are the unconstrained operator
(gamma_s = 1, u* = 1): L = 1, no barrier at any price.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "The finite account: leverage and the liquidation barrier"
SECTION = "sec:constrained"
EQ = ["eq:leverage", "eq:barrier"]

FIELDS = [
    ("L", "L = u*/gamma_s, leverage at the stopping rule", ".4f"),
    ("ceiling", "the broker's ceiling, L at u = 1 (= 1/gamma_s)", ".4f"),
    ("f_star", "f*, the liquidation barrier (price ratio)", ".4f"),
    ("drawdown", "  the fall it takes to be sold out, 1 - f*", ".1%"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    L = model.leverage(cfg)                       # at the configured u_star
    f = model.liquidation_barrier(L, cfg.gamma_s)
    return {
        "L": L,
        "ceiling": model.leverage(cfg, u=1.0),    # the broker's own limit
        "f_star": f,
        "drawdown": 1.0 - f,                       # the column frontier() prints
    }


CASES = [
    Case("", {
        "L": (1.0, 1e-9),               # defaults: the unconstrained operator
        "ceiling": (1.0, 1e-9),         # "no leverage at all for shares paid in full"
        "f_star": (0.0, 1e-9),          # unlevered: "no price at which it is called"
    }, note="the unconstrained operator (gamma_s = 1)"),
    Case("--gamma-s 0.25 --u-star 1.0", {
        "L": (4.0, 1e-6),               # "four times equity at portfolio margin"
        "ceiling": (4.0, 1e-6),
        "f_star": (1.0, 1e-6),          # "in violation on the day it is opened"
        "drawdown": (0.0, 1e-6),        # at L = 1/gamma_s the barrier is today's price
    }, note="the broker's ceiling: f* >= 1, in violation on day one"),
    Case("--gamma-s 0.50 --u-star 1.0", {
        "L": (2.0, 1e-6),               # "twice under Reg T"
        "ceiling": (2.0, 1e-6),
    }, note="Reg T's ceiling"),
    Case("--gamma-s 0.25 --u-star 0.5", {
        "L": (2.0, 1e-6),               # the detour's worked position
        "f_star": (0.6667, 0.0005),     # equity meets the requirement after...
        "drawdown": (0.3333, 0.0005),   # "...let the price fall by a third"
    }, note="the detour's margin call: L = 2 sold out on a one-third fall"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
