"""The three clocks, and n = tau_c / tau_p that ties two of them together.

    python code/examples/strategy_cadence.py
    python code/examples/strategy_cadence.py --n 1     # calls on the put clock
    python code/examples/strategy_cadence.py --n 13    # quarterly calls

Backs eq:n in section 04.  Closed form -- the clocks are Config, the entry
depth and the call-grid tax are analytic -- so there is nothing to declare.

The tenor carries a square root of its own, which is why section 04 can say
the three clocks are paid on different scales.  Premium goes as sigma*sqrt(tau),
so a put run for half as long at an unchanged cadence gives up about 29% of the
premium rather than half of it -- 1 - 1/sqrt(2) = 29.3% is the pure law, and
the dial's strike moving with the tenor accounts for the rest.  Assignments do
not follow the tenor at all: at a target p* per put they arrive at p*/T, set by
the cadence alone.

n is a bookkeeping ratio, but it is not inert.  Section 07 finds the call-grid
tax beta*sigma*sqrt(tau_c) as a multiple of the typical entry depth E[x0], and
since the tax carries sqrt(tau_c) = sqrt(n)*sqrt(tau_p) while E[x0] does not
depend on n at all, that multiple scales as sqrt(n): 2.1 at the running n = 4,
about 1.0 at n = 1, about 3.8 at n = 13.  Longer calls collect more premium but
outrun the puts, and the tax they levy on holding time never washes out.  Run
this at a few values of n and watch the last line move.
"""

import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Cadence: the three clocks and n = tau_c/tau_p"
SECTION = "sec:strategy"
EQ = ["eq:n"]

FIELDS = [
    ("n", "n = tau_c / tau_p", ".0f"),
    ("tau_p", "put tenor tau_p (years)", ".4f"),
    ("cadence", "cadence T (years)", ".4f"),
    ("tau_c", "call period tau_c (years)", ".4f"),
    ("tau_c_wk", "  the same, in weeks", ".1f"),
    ("tax", "call-grid tax beta*sigma*sqrt(tau_c)", ".4f"),
    ("x0", "typical entry depth E[x0]", ".4f"),
    ("ratio", "  the tax as a multiple of it (~sqrt(n))", ".2f"),
    ("c_p", "put premium c_p at the strike dial", ".4f"),
    ("c_p_half", "  the same at half the tenor, cadence unmoved", ".4f"),
    ("half_drop", "  premium given up (~1 - 1/sqrt 2)", ".1%"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    _, _, mean_x0, _ = model.entry_law(cfg, measure)
    tax = model.grid_tax(cfg, measure)
    # Separating the clocks means shortening the tenor while the cadence holds
    # still, so `cadence` is carried across explicitly rather than left to
    # follow tau_p as it does at the defaults.
    short = dataclasses.replace(cfg, tau_p=cfg.tau_p / 2, cadence=cfg.cadence)
    c_p = model.put_premium(cfg, measure)
    c_p_half = model.put_premium(short, measure)
    return {
        "n": cfg.n,
        "tau_p": cfg.tau_p,
        "cadence": cfg.cadence,
        "tau_c": cfg.tau_c,
        "tau_c_wk": cfg.tau_c * 52,
        "tax": tax,
        "x0": mean_x0,
        "ratio": tax / mean_x0,
        "c_p": c_p,
        "c_p_half": c_p_half,
        "half_drop": 1 - c_p_half / c_p,
    }


CASES = [
    Case("", {
        "n": (4, 0),                    # section 04: "n = 4"
        "tau_p": (1 / 52, 0.0002),      # "T = τ_p = 1/52"
        "cadence": (1 / 52, 0.0002),    # T = τ_p, the always-covered case
        "tau_c": (1 / 13, 0.0002),      # "τ_c = 1/13 of a year"
        "tau_c_wk": (4.0, 0.05),        # "calls written for four weeks"
        "ratio": (2.09, 0.05),          # section 07: "2.1 times the entry depth"
        "tax": (0.0323, 0.0005),        # "0.5826 x 0.20 x sqrt(1/13)"
        "x0": (0.0155, 0.0005),
        "half_drop": (0.290, 0.005),    # "about 29% of the premium rather
                                        # than half of it"
    }, note="the running example's rhythm"),
    Case("--n 1", {
        "n": (1, 0),                    # calls on the put clock, n = 1
        "tau_c": (1 / 52, 0.0002),      # tau_c = tau_p when n = 1
        "tau_c_wk": (1.0, 0.05),
    }, note="n = 1: the sqrt(n) tax multiple falls to about 1.0"),
    Case("--n 13", {
        "n": (13, 0),                   # quarterly calls, n = 13
        "tau_c": (0.25, 0.0002),        # tau_c = 13/52 = a quarter
        "tau_c_wk": (13.0, 0.05),
    }, note="n = 13: the tax multiple climbs toward 3.8, never vanishing"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
