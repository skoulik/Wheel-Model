"""The strike dial: pick an assignment probability, read off the strike.

    python code/examples/entry_strike.py
    python code/examples/entry_strike.py --p-star 0.10
    python code/examples/entry_strike.py --p-star 0.10 --sigma 0.297

Backs eq:kstar and eq:p-screen in section 05.  Closed form throughout, so
there is nothing expensive to declare -- this is the exemplar for a module
that needs no walk.  See `holding_time.py` for one that does.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Entry: the strike dial"
SECTION = "sec:entry"
EQ = ["eq:kstar", "eq:p-screen", "eq:screen-gap", "eq:gap-prob"]

FIELDS = [
    ("k", "k*, strike fraction", ".4f"),
    ("otm", "out of the money", ".2%"),
    ("p_real", "realized assignment rate", ".2%"),
    ("p_screen", "p_screen = N(-d2), the screen's number", ".2%"),
    ("sharpe", "  the asset's Sharpe ratio, (mu - r)/sigma", ".4f"),
    ("gap_z", "  the two worlds' gap, in d2 units", ".4f"),
    ("gap_p", "  eq:gap-prob, the same gap in probability", ".4f"),
    ("delta", "delta, what the screen shows instead", ".2%"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    k, p_real, _, _ = model.entry_law(cfg, measure)
    return {
        "k": k,
        "otm": 1 - k,
        "p_real": p_real,
        "p_screen": model.screen_prob(cfg, measure),
        # gap_z is this times sqrt(tau_p), which is what makes eq:screen-gap
        # checkable by eye: 0.10 * sqrt(1/52) = 0.0139.
        "sharpe": (cfg.mu - cfg.r) / cfg.sigma,
        "gap_z": model.screen_gap(cfg),
        "gap_p": model.screen_gap(cfg, in_prob=True),
        "delta": model.put_delta(cfg, measure),
    }


CASES = [
    Case("", {
        "k": (0.9774, 0.0005),          # section 05: "k* ~ 0.9774"
        "otm": (0.0226, 0.0005),        # "about 2.3% below the market"
        "p_real": (0.20, 1e-9),         # p* is real-world: no correction
        "p_screen": (0.2039, 0.001),    # "comes to 20.4%"
        "sharpe": (0.10, 0.0005),       # section 05: "which is 0.10 here"
        "gap_z": (0.0139, 0.0005),      # eq:screen-gap, the shift in d2
        # Exact, not the linearization: this must equal p_screen - p_real to
        # the digit, which is what makes the two readings above consistent.
        "gap_p": (0.003905, 1e-6),
        "delta": (0.19605, 1e-4),       # section 05: "~ 19.6% here".  Not
                                        # N(-d1) = 0.19614: see put_delta.
    }, note="Standard regime"),
    Case("--measure Q", {
        "k": (0.9770, 0.0005),
    }, note="the same dial read under the pricing drift"),
    Case("--p-star 0.10", {
        "k": (0.9655, 0.0005),          # "k* ~ 0.9655, about 3.5% below"
        "otm": (0.0345, 0.0005),
    }, note="Conservative regime"),
    Case("--p-star 0.10 --sigma 0.297", {
        "otm": (0.051, 0.001),          # "a one-in-ten strike sits 5.1% out"
    }, note="the live account's names, at their own volatility"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
