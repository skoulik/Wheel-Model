"""The benchmark that matters: the wheel against owning the stock.

    python code/examples/returns_benchmark.py
    python code/examples/returns_benchmark.py --p-star 0.10
    python code/examples/returns_benchmark.py --measure Q

Backs eq:excess-return (defined in section 04, applied in section 09).  T-bills
are the wrong comparison: the wheel keeps almost all its capital in equity, so
the question is not whether it beats cash but whether it beats owning the same
stock.  Buy-and-hold earns mu - r - w*delta over the risk-free rate; scaled by
the wheel's equity exposure it is the honest benchmark, and the section's
central result is that the difference against the wheel is essentially zero.

Horizon-weighted (equity exposure and the wheel's excess both move with the
standing inventory); hangs off the near-grid killed walk.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, need_occupation, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Returns: the wheel against buy-and-hold"
SECTION = "sec:strategy"
EQ = ["eq:excess-return"]

# The collateral footnote is an accounting correction on top of the ledger, not
# part of eq:excess -- section 09 is emphatic about that -- so it is off by
# default and only printed under --collateral.
EXTRA = [("--collateral", dict(action="store_true",
                               help="also show Track C's collateral overcharge "
                                    "(the section 09 footnote), off by default"))]

FIELDS = [
    ("wheel", "the wheel's true excess return", ".2%"),
    ("equity_frac", "  wheel equity exposure (% of capital)", ".1%"),
    ("buy_hold", "buy & hold excess, mu - r - w*delta", ".2%"),
    ("buy_hold_adj", "  equity-adjusted to the wheel's exposure", ".2%"),
    ("difference", "wheel minus equity-adjusted buy & hold", ".2%"),
    # The collateral footnote (only under --collateral): Track C charges r on the
    # put margin that in fact earns ~r at the broker, so it overcharges by
    # r*gamma_p*k a year.  Crediting it back is what makes the two regimes agree.
    ("overcharge", "Track C overcharge on the put collateral", ".2%"),
    ("gap_corrected", "  difference once the collateral earns r", ".2%"),
    ("cash_secured", "  cash-secured overcharge, as a multiple", ".2f"),
]


def requires(cfg, measure="P", horizon=30.0, **kw):
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, collateral=False, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    equity_frac = e["I"] / e["mv_capital"]      # section 09's "98%"
    buy_hold = model.buy_hold_excess(cfg, measure)
    buy_hold_adj = buy_hold * equity_frac
    difference = e["econ_excess"] - buy_hold_adj
    # The collateral correction is arithmetic on the ledger, not a model formula:
    # r on the put margin gamma_p*k, over the capital of eq:capital.
    overcharge = cfg.r * cfg.gamma_p * e["k"] / e["mv_capital"]
    # The fully-cash-secured convention posts k, not gamma_p*k, so its overcharge
    # -- k over the whole capital -- is the larger multiple the footnote names.
    cash_secured = ((e["k"] / (e["k"] + e["I"]))
                    / (cfg.gamma_p * e["k"] / e["mv_capital"]))
    return {
        "wheel": e["econ_excess"],
        "equity_frac": equity_frac,
        "buy_hold": buy_hold,
        "buy_hold_adj": buy_hold_adj,
        "difference": difference,
        "overcharge": overcharge if collateral else None,
        "gap_corrected": difference + overcharge if collateral else None,
        "cash_secured": cash_secured if collateral else None,
    }


CASES = [
    Case("", {
        "wheel": (0.0160, 0.0005),          # section 09: "the wheel +1.60%"
        "equity_frac": (0.98, 0.005),       # "98% at the thirty-year mark"
        "buy_hold": (0.0163, 0.0002),       # "mu - r - w*delta = +1.63%"
        "buy_hold_adj": (0.0160, 0.0005),   # "+1.60% after scaling by the wheel's 98%"
        "difference": (0.0001, 0.0005),     # "difference +0.01%"
    }, note="Standard regime, 30y"),
    Case("--p-star 0.10", {
        "wheel": (0.0149, 0.0005),          # Conservative: "true excess +1.49%"
        "buy_hold_adj": (0.0157, 0.0005),   # "against a benchmark of +1.57%"
        "difference": (-0.0008, 0.0005),    # "The eight-basis-point deficit"
    }, note="Conservative regime"),

    # The volatility-risk-premium sweep of section 09: the excess a richer quote
    # buys, and the gap over buy-and-hold that grows with it -- "about 45 basis
    # points per volatility point".  (Premiums per year are in returns_income.py.)
    Case("--iv-spread 0.005", {
        "wheel": (0.0183, 0.0005),          # the table: "20.5%  +1.83%"
        "difference": (0.0023, 0.0005),     # "vs buy-and-hold  +0.23%"
    }, note="sigma_IV = 20.5%"),
    Case("--iv-spread 0.010", {
        "wheel": (0.0205, 0.0005),          # "21.0%  +2.05%"
        "difference": (0.0046, 0.0005),     # "+0.46%"
    }, note="sigma_IV = 21.0%"),
    Case("--iv-spread 0.020", {
        "wheel": (0.0252, 0.0005),          # "22.0%  +2.52%"
        "difference": (0.0092, 0.0005),     # "+0.92%"
    }, note="sigma_IV = 22.0%, two vol points dear"),

    # The dividend sweep of section 09: the true excess falls ~90bp across it,
    # almost all of it the withholding tax -- so the gap over a buy-and-hold that
    # pays the same tax stays "essentially zero throughout -- never more than two
    # basis points, at any yield".  (Lots and capital are in returns_capital.py.)
    Case("--delta 0.0", {
        "wheel": (0.0198, 0.0005),          # the table: "δ 0%  +1.98%"
        "difference": (0.0001, 0.0003),     # "the gap is essentially zero"
    }, note="no dividend"),
    Case("--delta 0.01", {
        "wheel": (0.0183, 0.0005),          # "δ 1%  +1.83%"
        "difference": (0.0001, 0.0003),
    }, note="a 1% yielder"),
    Case("--delta 0.04", {
        "wheel": (0.0138, 0.0005),          # "δ 4%  +1.38%"
        "difference": (0.0001, 0.0003),
    }, note="a 4% yielder"),
    Case("--delta 0.06", {
        "wheel": (0.0108, 0.0005),          # "δ 6%  +1.08%" -- a non-converging snapshot
        "difference": (0.0001, 0.0003),
    }, note="a 6% yielder, past the count boundary"),

    # The collateral footnote and the regime-comparison table it explains.  The
    # difference "as modelled" and the difference "once the collateral earns r"
    # are the middle two and last two rows of that table; the overcharge is the
    # footnote's own 17/13/8 bp.  Crediting the collateral makes the regimes agree.
    Case("--horizon 5 --collateral", {
        "difference": (0.0003, 0.0001),     # table: "Standard, as modelled  5y +0.03%"
        "overcharge": (0.0017, 0.0001),     # footnote: "17 basis points ... at five years"
        "gap_corrected": (0.0020, 0.0001),  # "Standard, collateral earning r  +0.20%"
    }, note="Standard, five years: the fixed margin is a large share of a small book"),
    Case("--horizon 10 --collateral", {
        "difference": (0.0001, 0.0001),     # "Standard, as modelled  10y +0.01%"
        "overcharge": (0.0013, 0.0001),     # "13 at ten"
        "gap_corrected": (0.0014, 0.0001),  # "collateral earning r  +0.14%"
    }, note="Standard, ten years"),
    Case("--collateral", {
        "difference": (0.0001, 0.0002),     # "Standard, as modelled  30y +0.01%"
        "overcharge": (0.0008, 0.0001),     # "8 at thirty"
        "gap_corrected": (0.0009, 0.0001),  # "collateral earning r  +0.09%"
        "cash_secured": (4.5, 0.3),         # "about four and a half times" the margin one
    }, note="Standard, thirty years"),
    Case("--p-star 0.10 --horizon 5 --collateral", {
        "difference": (-0.0014, 0.0001),    # "Conservative, as modelled  5y −0.14%"
        "gap_corrected": (0.0020, 0.0001),  # "Conservative, collateral earning r  +0.20%"
    }, note="Conservative, five years"),
    Case("--p-star 0.10 --horizon 10 --collateral", {
        "difference": (-0.0011, 0.0001),    # "Conservative, as modelled  10y −0.11%"
        "gap_corrected": (0.0014, 0.0001),  # "+0.14%"
    }, note="Conservative, ten years"),
    Case("--p-star 0.10 --collateral", {
        "difference": (-0.0008, 0.0002),    # "Conservative, as modelled  30y −0.08%"
        "overcharge": (0.0017, 0.0001),     # "Track C's overcharge doubles ... from 8 to 17"
        "gap_corrected": (0.0009, 0.0001),  # "+0.09%"
    }, note="Conservative, thirty years: same fixed margin over half the book"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
