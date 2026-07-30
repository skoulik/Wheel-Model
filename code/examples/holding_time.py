"""How long a lot stays: the call-grid tax, the survival curve, and E[W].

    python code/examples/holding_time.py
    python code/examples/holding_time.py --measure Q
    python code/examples/holding_time.py --n 1        # calls on the put clock

Backs eq:siegmund, eq:survival, eq:holding and eq:holding-siegmund in
section 07.  This is the exemplar for a module that hangs off a killed walk.

Note what is merged here and what is not.  Everything above comes out of one
`occupation()` solve, or is the closed form the section compares that solve
against -- one argument, one footnote, one script.  eq:trapped is a different
formula on a different regime and lives in its own module, even though it
sits in the same section.  The cut follows the code, not the headings.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_occupation, need_stationary,      # noqa: E402
                               resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "Holding time: first passage on the call grid"
SECTION = "sec:holding"
EQ = ["eq:siegmund", "eq:survival", "eq:holding", "eq:holding-siegmund"]

# The columns section 07 tabulates, in years.  Quoted in weeks up to half a
# year and in years after that; they land on exact call periods only when the
# call grid divides them, which is why the printed labels are recomputed.
COLUMNS = [4 / 52, 8 / 52, 12 / 52, 24 / 52, 1.0, 2.0, 5.0, 10.0, 20.0]

FIELDS = [
    ("tax", "call-grid tax, beta*sigma*sqrt(tau_c)", ".4f"),
    ("x0", "typical entry depth E[x0]", ".4f"),
    ("ratio", "  the tax as a multiple of it", ".2f"),
    ("q_x0", "exit probability of a fresh lot", ".3f"),
    ("naive", "  the naive 1/q answer, in periods", ".2f"),
    ("columns", "survival curve, at the columns below", ".2f"),
    ("labels", "  ", ">6s"),
    ("median", "median lifetime, in call periods", "d"),
    ("median_wk", "  the same, in weeks", ".0f"),
    ("EW", "E[W], the mean holding time (years)", ".2f"),
    ("EW_siegmund", "  the Siegmund closed form", ".2f"),
    ("prem", "call premiums collected per lot over its life", ".4f"),
    ("exitcost", "upside surrendered per lot at call-away", ".4f"),
]


def _label(years):
    return f"{years * 52:.0f} wk" if years < 1 else f"{years:.0f} y"


def requires(cfg, measure="P", horizon=None, **kw):
    # Two walks, and the split is not an oversight.  E[W] sums over a lot's
    # whole life, so it is carried by the tail the near grid truncates and
    # biases -- it reads 2.05 there against the extrapolated 2.10.  The early
    # survival columns are the other way round: the near grid runs at h = 0.01
    # against the extrapolation's 0.0125, so it resolves the fast lane better,
    # and it is where the section's 0.60/0.46 come from.
    return [need_occupation(cfg, measure), need_stationary(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    near = resolve(ctx, need_occupation(cfg, measure))
    full = resolve(ctx, need_stationary(cfg, measure))
    econ = model.economics(cfg, measure, full)
    surv = near["surv"]
    median = model.median_periods(near)
    tax = model.grid_tax(cfg, measure)
    return {
        "tax": tax,
        "x0": econ["E[x0]"],
        "ratio": tax / econ["E[x0]"],
        "q_x0": near["q(x0)"],
        "naive": 1 / near["q(x0)"],
        "columns": [surv[round(y / cfg.tau_c)] for y in COLUMNS
                    if round(y / cfg.tau_c) < len(surv)],
        "labels": [_label(y) for y in COLUMNS
                   if round(y / cfg.tau_c) < len(surv)],
        "median": median,
        "median_wk": None if median is None else median * cfg.tau_c * 52,
        "EW": econ["E[T]"],
        "EW_siegmund": econ["E[T]_siegmund"],
        # Per-lot lifetime sums over the same killed walk: premium taken in and
        # upside handed back.  Quoted in section 09, but they come off this walk.
        "prem": near["E[prem]"],
        "exitcost": near["E[exitcost]"],
    }


CASES = [
    Case("", {
        "tax": (0.0323, 0.0005),        # section 07: "0.5826 x 0.20 x sqrt(1/13)"
        "ratio": (2.09, 0.05),          # "2.1 times the typical entry depth"
        "x0": (0.0155, 0.0005),
        "q_x0": (0.405, 0.005),         # "a 40% chance of leaving on its first call"
        "naive": (2.47, 0.02),          # "about 2.5 periods, call it ten weeks"
        "columns": ([0.60, 0.46, 0.38, 0.27, 0.18, 0.12, 0.07, 0.04, 0.02], 0.005),
        "median": (2, 0),               # "a median of eight weeks"
        "EW": (2.10, 0.02),             # eq:holding
        "EW_siegmund": (1.9, 0.05),     # eq:holding-siegmund, "9% below"
        "prem": (0.0372, 0.001),        # section 09: "a lot collects 3.72% ... in call premiums"
        "exitcost": (0.0358, 0.001),    # section 09: "and surrenders 3.58% in upside at call-away"
    }, note="Standard regime"),
    Case("--measure Q", {
        "EW": (9.0, 1.0),               # "E[W] ~ 9 years" -- a round figure on
    }, note="under the market's pricing drift"),   # purpose, see the section
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
