"""The two capitals: market value, cost basis, and the gap between them.

    python code/examples/returns_capital.py
    python code/examples/returns_capital.py --p-star 0.10
    python code/examples/returns_capital.py --measure Q

Backs eq:capital in section 09.  Two quantities can be called "the capital",
and the section is emphatic about which is which: **market value** is the
right denominator for a return (it is what selling the book would release),
while **cost basis** is what a spreadsheet of purchases produces and is *not*
a return denominator.  The labels below keep the two apart.

Horizon-weighted (both capitals grow with the standing inventory), so it
hangs off the near-grid killed walk; see `holding_time.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, need_occupation, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Returns: market value vs cost basis"
SECTION = "sec:returns"
EQ = ["eq:capital"]

FIELDS = [
    ("inv", "E[I], lots held (at market)", ".2f"),
    ("mv_capital", "capital, MARKET VALUE (the return denominator)", ".2f"),
    ("capital", "capital, COST BASIS (a spreadsheet of purchases)", ".2f"),
    ("gap", "  gap (cost basis - market value)", ".2f"),
]


def requires(cfg, measure="P", horizon=30.0, **kw):
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    # E[Capital] = gamma_p*k + E[I]: the put margin plus inventory at market
    # (mv_capital), against the accumulated cost basis (capital).
    return {
        "inv": e["I"],
        "mv_capital": e["mv_capital"],
        "capital": e["capital"],
        "gap": e["capital"] - e["mv_capital"],
    }


CASES = [
    Case("", {
        "inv": (11.40, 0.05),           # section 09: "11.40 lots held"
        "mv_capital": (11.59, 0.05),    # eq:capital: "a total of 11.59"
        "capital": (18.23, 0.06),       # "expressed against today's price ... 18.23"
        "gap": (6.6, 0.1),              # "The gap between them -- 6.6 share prices"
    }, note="Standard regime, 30y"),
    Case("--p-star 0.10", {
        "inv": (5.50, 0.05),            # Conservative: "lots held 5.50"
        "mv_capital": (5.70, 0.05),     # "capital (market) 5.70"
        "capital": (8.90, 0.06),        # "capital (cost) 8.90"
    }, note="Conservative regime"),
    # The dividend sweep of section 09 ("Dividends, resolved"): yield doubles the
    # inventory and nearly triples the cost-basis capital.  The δ = 2.5% column is
    # the default Case above; the true excess each row earns is in
    # returns_benchmark.py, and ν in stability_criteria.py.
    Case("--delta 0.0", {
        "inv": (8.54, 0.05),            # the table: "δ 0%  lots held 8.54"
        "mv_capital": (8.74, 0.05),     # "capital (market) 8.74"
        "capital": (12.11, 0.10),       # "capital (cost) 12.11"
    }, note="no dividend"),
    Case("--delta 0.01", {
        "inv": (9.56, 0.05),            # "δ 1%  9.56"
        "mv_capital": (9.75, 0.05),     # "9.75"
        "capital": (14.15, 0.10),       # "14.15"
    }, note="a 1% yielder"),
    Case("--delta 0.04", {
        "inv": (13.65, 0.05),           # "δ 4%  13.65"
        "mv_capital": (13.84, 0.05),    # "13.84"
        "capital": (24.00, 0.10),       # "24.00"
    }, note="a 4% yielder"),
    Case("--delta 0.06", {
        "inv": (17.31, 0.05),           # "δ 6%  17.31"
        "mv_capital": (17.51, 0.05),    # "17.51"
        "capital": (35.50, 0.10),       # "35.50" -- ν < 0 here, a non-converging snapshot
    }, note="a 6% yielder, past the count boundary"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
