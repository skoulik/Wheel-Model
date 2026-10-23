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

import math
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
    ("lots_basis", "  of which the lots' bases", ".2f"),
    ("basis_per_lot", "  a lot's basis on average, in today's share prices", ".2f"),
    ("gap", "  gap (cost basis - market value)", ".2f"),
    ("gap_per_lot", "  gap per lot", ".2f"),
    ("deep_gap", "  share of the gap in lots deeper than 50 log-points", ".1%"),
]

# Where the section draws the line between deep lots and the rest: the same 50
# log-points as section 08's deep-share row, so the two shares are of one set.
DEEP = 0.50


def requires(cfg, measure="P", horizon=30.0, **kw):
    return [need_occupation(cfg, measure)]


def _deep_gap_share(cfg, measure, horizon, e):
    """The share of the gap carried by lots deeper than DEEP.

    A lot at depth x has basis e^x * (1 - c_p/k) of today's price against a
    market value of 1, so its share of the gap is that difference, weighted by
    held time in the census.
    """
    xs, w = model.census_weights(cfg, measure, horizon=horizon)
    f = 1 - e["c_p"] / e["k"]
    loss = [wi * (math.exp(x) * f - 1) for x, wi in zip(xs, w)]
    return sum(l for x, l in zip(xs, loss) if x >= DEEP) / sum(loss)


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    # E[Capital] = gamma_p*k + E[I]: the put margin plus inventory at market
    # (mv_capital), against the accumulated cost basis (capital).  The margin
    # is in both, so the gap is the lots' alone.
    lots_basis = e["capital"] - cfg.gamma_p * e["k"]
    return {
        "inv": e["I"],
        "mv_capital": e["mv_capital"],
        "capital": e["capital"],
        "lots_basis": lots_basis,
        "basis_per_lot": lots_basis / e["I"],
        "gap": e["capital"] - e["mv_capital"],
        "gap_per_lot": (e["capital"] - e["mv_capital"]) / e["I"],
        "deep_gap": _deep_gap_share(cfg, measure, horizon, e),
    }


CASES = [
    Case("", {
        "inv": (11.40, 0.05),           # section 09: "11.40 lots held"
        "mv_capital": (11.59, 0.05),    # eq:capital: "a total of 11.59"
        "capital": (18.23, 0.06),       # "the margin ... brings the total to 18.23"
        "lots_basis": (18.04, 0.06),    # "the bases come to 18.04"
        "basis_per_lot": (1.58, 0.005),  # "1.58 share prices a lot on average"
        "gap": (6.6, 0.1),              # "the gap between them -- 6.6 share prices"
        "gap_per_lot": (0.58, 0.005),   # "or 0.58 a lot"
        "deep_gap": (0.73, 0.005),      # "account for 73% of the gap"
    }, note="Standard regime, 30y"),
    Case("--p-star 0.10", {
        "inv": (5.50, 0.05),            # Conservative: "lots held 5.50"
        "mv_capital": (5.70, 0.05),     # "capital (market) 5.70"
        "capital": (8.90, 0.06),        # "capital (cost) 8.90"
    }, note="Conservative regime"),
    # The cadence sweep of section 09 ("The one dial the model says is free").
    # What cadence really sets is the capital the position needs -- 11.59 share
    # prices a name at weekly against 3.28 at quarterly -- while the return per
    # unit of that capital barely moves.  The weekly column is the default Case
    # above; the excess each row earns is in returns_benchmark.py.  n = 4
    # throughout, so the call period stays four put periods.
    Case("--tau-p 0.0384615385", {
        "inv": (8.02, 0.05),            # the table: "biweekly  lots held 8.02"
        "mv_capital": (8.21, 0.05),     # "capital (market) 8.21"
    }, note="biweekly cadence, n = 4"),
    Case("--tau-p 0.0833333333", {
        "inv": (5.42, 0.05),            # "monthly  5.42"
        "mv_capital": (5.61, 0.05),     # "5.61"
    }, note="monthly cadence, n = 4"),
    Case("--tau-p 0.25", {
        "inv": (3.09, 0.05),            # "quarterly  3.09"
        "mv_capital": (3.28, 0.05),     # "3.28"
    }, note="quarterly cadence, n = 4"),
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
