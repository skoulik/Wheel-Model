"""The benchmark that matters: the wheel against owning the stock.

    python code/examples/returns_benchmark.py
    python code/examples/returns_benchmark.py --p-star 0.10
    python code/examples/returns_benchmark.py --measure Q

Backs eq:excess-return (defined in section 04, applied in section 09).  T-bills
are the wrong comparison: the wheel keeps almost all its capital in equity, so
the question is not whether it beats cash but whether it beats owning the same
stock.  Buy-and-hold earns mu - r - w*delta over the risk-free rate; scaled by
the wheel's capital in shares it is the operator's own alternative.  In
dollars per period (TODO II-34) the wheel trails it by about 0.1 points at
thirty years: per unit of the exposure the book actually carries, its delta
averaged over each option's life, the wheel earns what the stock does less the
withholding, and the shortfall is exactly the exposure its calls sell.

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
EQ = ["eq:excess-return", "eq:delta-return", "eq:life-delta"]

FIELDS = [
    ("wheel", "the wheel's true excess return", ".2%"),
    ("equity_frac", "  wheel equity exposure (% of capital)", ".1%"),
    ("buy_hold", "buy & hold excess, mu - r - w*delta", ".3%"),
    ("buy_hold_adj", "  equity-adjusted to the wheel's exposure", ".2%"),
    ("difference", "wheel minus equity-adjusted buy & hold", ".2%"),
    # The book's delta, each option's averaged over its life with its drift
    # (model.book_delta_life): a share less its call's, plus the short put's.
    # Black-Scholes's result -- an instrument earns its delta times the stock's
    # -- then holds exactly, so the gap to the equity-adjusted stock is the
    # exposure the calls sell, (shares - delta)*(mu - r), and the gap to the
    # delta-scaled stock is the withholding on those shares, nothing else.
    ("delta_frac", "  the book's delta (% of capital)", ".1%"),
    ("calls_sold", "    the exposure the calls take away", ".1%"),
    ("put_adds", "    the exposure the put adds back", ".2%"),
    ("buy_hold_delta", "  buy & hold scaled to the book's delta", ".2%"),
    ("difference_delta", "wheel minus delta-scaled buy & hold", ".3%"),
    ("exposure_sold", "  the exposure the calls sell, at mu - r", ".3%"),
    # The usual shortcut: each option's delta at the moment it is sold, what a
    # broker's screen shows (model.book_delta).  It overstates the exposure by
    # the drift of delta over an option's life.
    ("delta_sale_frac", "  the book's delta at sale (% of capital)", ".2%"),
    ("shortcut", "  what the shortcut adds to the delta-scaled gap", ".3%"),
]


def requires(cfg, measure="P", horizon=30.0, **kw):
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    cap = e["mv_capital"]
    equity_frac = e["I"] / cap                  # section 09's "98%"
    buy_hold = model.buy_hold_excess(cfg, measure)
    buy_hold_adj = buy_hold * equity_frac
    difference = e["econ_excess"] - buy_hold_adj
    m, _ = cfg.world(measure)
    premium = m + cfg.delta - cfg.r             # the stock's own, mu - r
    inv, put = model.book_delta_life(cfg, measure, horizon=horizon)
    delta_frac = float((e["I"] * inv + put) / cap)
    buy_hold_delta = buy_hold * delta_frac
    inv_s, put_s = model.book_delta(cfg, measure, 0.0, horizon=horizon)
    delta_sale = float((e["I"] * inv_s + put_s) / cap)
    return {
        "wheel": e["econ_excess"],
        "equity_frac": equity_frac,
        "buy_hold": buy_hold,
        "buy_hold_adj": buy_hold_adj,
        "difference": difference,
        "delta_frac": delta_frac,
        "calls_sold": float(e["I"] * (1.0 - inv) / cap),
        "put_adds": float(put / cap),
        "buy_hold_delta": buy_hold_delta,
        "difference_delta": e["econ_excess"] - buy_hold_delta,
        "exposure_sold": (equity_frac - delta_frac) * premium,
        "delta_sale_frac": delta_sale,
        "shortcut": (delta_sale - delta_frac) * buy_hold,
    }


# Economic figures are in dollars per period (TODO II-34), with the account's
# cash earning r and the window's edge closed (TODO II-35).  Where a comment
# quotes section 09 or 11, that prose is being rewritten to these values
# (drafts/2026-11-13-account-cash-and-window-edge-plan.md) and still shows the
# old.
CASES = [
    Case("", {
        "wheel": (0.0149, 0.0001),          # section 09: "+1.49%"; the table's 30 y
        "equity_frac": (0.983, 0.0005),     # "98% at the thirty-year mark"; "98.3%"
        "buy_hold": (0.01625, 0.00001),     # "mu - r - w*delta = +1.625%"
        "buy_hold_adj": (0.0160, 0.0001),   # "the same capital in the stock  +1.60%"
        "difference": (-0.00105, 0.00002),  # "difference  -0.10%"; "a tenth of a point"
        # The identities the structural checks hold exactly: the gap to the
        # equity-adjusted stock is minus the exposure sold, and to the
        # delta-scaled stock 0.375% of withholding on the 5.2 points of capital
        # between shares and delta, by hand: 0.00375*(0.9831 - 0.9309).
        "exposure_sold": (0.00105, 0.00002),
        "delta_frac": (0.931, 0.0005),      # "leaves 93.1%"
        "calls_sold": (0.069, 0.0005),      # "less 6.9"
        "put_adds": (0.0168, 0.0005),       # "plus 1.7"
        "buy_hold_delta": (0.0151, 0.0001), # "the stock, scaled to the book's delta  +1.51%"
        "difference_delta": (-0.00020, 0.00002),  # "the wheel, minus it  -0.020%"; "2.0"
        "delta_sale_frac": (0.9324, 0.0001),     # the shortcut: "93.2%"
        "shortcut": (0.000025, 0.000005),        # "a quarter of one at thirty"
    }, note="Standard regime, 30y"),
    Case("--p-star 0.10", {
        "wheel": (0.0146, 0.0001),          # Conservative: "true excess +1.49%"
        "buy_hold_adj": (0.0157, 0.0001),   # "against a benchmark of +1.57%"
        "difference": (-0.00107, 0.00002),  # "The eight-basis-point deficit"
        "difference_delta": (-0.00020, 0.00002),
    }, note="Conservative regime"),

    # The volatility-risk-premium sweep of section 09: the excess a richer quote
    # buys, and the gap over buy-and-hold that grows with it -- "about 45 basis
    # points per volatility point".  (Premiums per year are in returns_income.py.)
    Case("--iv-spread 0.005", {
        "wheel": (0.0172, 0.0001),          # the table: "20.5%  +1.83%"
        "difference": (0.0012, 0.0001),     # "vs buy-and-hold  +0.23%"
    }, note="sigma_IV = 20.5%"),
    Case("--iv-spread 0.010", {
        "wheel": (0.0194, 0.0001),          # "21.0%  +2.05%"
        "difference": (0.0035, 0.0001),     # "+0.46%"
    }, note="sigma_IV = 21.0%"),
    # 1.5 points is the top of the single-name range section 09 now quotes
    # (Bakshi & Kapadia: 1.07 dropping dividend payers, 1.5 across all
    # options), so the range is bracketed by checks rather than interpolated.
    Case("--iv-spread 0.015", {
        "wheel": (0.0218, 0.0001),          # the table: "21.5%  +2.29%"
        "difference": (0.0058, 0.0001),     # "vs buy-and-hold  +0.69%"
    }, note="sigma_IV = 21.5%, the top of the single-name range"),
    Case("--iv-spread 0.020", {
        "wheel": (0.0241, 0.0001),          # "22.0%  +2.52%"
        "difference": (0.0081, 0.0001),     # "+0.92%"
    }, note="sigma_IV = 22.0%, two vol points dear"),

    # The cadence sweep of section 09: thirteen basis points across a
    # thirteenfold change in how often a put is written, which is the section's
    # "the one dial the model says is free".  n = 4 throughout, so tau_c moves
    # with tau_p and the call period stays four put periods.  These are the
    # first Cases in the suite to vary --tau-p, and they were wrong until
    # INF-6: the harness pinned `cadence` at 1/52, so --tau-p 0.08333 sold a
    # monthly put every WEEK and reported +1.74% here instead of +1.56%.
    Case("--tau-p 0.0384615385", {
        "wheel": (0.0144, 0.0001),          # the table: "biweekly  +1.59%"
        "difference": (-0.0015, 0.0001),     # "vs buy-and-hold  +0.00%"
    }, note="biweekly cadence, n = 4"),
    Case("--tau-p 0.0833333333", {
        "wheel": (0.0135, 0.0001),          # "monthly  +1.56%"
        "difference": (-0.0022, 0.0001),    # "-0.01%"
    }, note="monthly cadence, n = 4"),
    Case("--tau-p 0.25", {
        "wheel": (0.0116, 0.0001),          # "quarterly  +1.47%"
        "difference": (-0.0038, 0.0001),    # "-0.07%"
    }, note="quarterly cadence, n = 4"),
    # The residual tilt the section admits to: at a FLAT premium the model
    # harvests more per point the faster it writes, because premium volume goes
    # as 1/sqrt(tau).  45.0bp weekly against 42.0 monthly -- the wrong way round
    # against the record, which is the whole point of the subsection.
    Case("--tau-p 0.0833333333 --iv-spread 0.010", {
        "wheel": (0.0178, 0.0001),          # 42.0bp per point, against 45.0 weekly
    }, note="monthly at one vol point, for the per-point harvest"),

    # The dividend sweep of section 09: the true excess falls ~90bp across it,
    # almost all of it the withholding tax -- so the gap over a buy-and-hold that
    # pays the same tax stays "essentially zero throughout -- never more than two
    # basis points, at any yield".  (Lots and capital are in returns_capital.py.)
    Case("--delta 0.0", {
        "wheel": (0.0181, 0.0001),          # the table: "δ 0%  +1.98%"
        "difference": (-0.0014, 0.0003),     # "the gap is essentially zero"
    }, note="no dividend"),
    Case("--delta 0.01", {
        "wheel": (0.0169, 0.0001),          # "δ 1%  +1.83%"
        "difference": (-0.0013, 0.0003),
    }, note="a 1% yielder"),
    Case("--delta 0.04", {
        "wheel": (0.0129, 0.0001),          # "δ 4%  +1.38%"
        "difference": (-0.0009, 0.0003),
    }, note="a 4% yielder"),
    Case("--delta 0.06", {
        "wheel": (0.0102, 0.0001),          # "δ 6%  +1.08%" -- a non-converging snapshot
        "difference": (-0.0007, 0.0003),
    }, note="a 6% yielder, past the count boundary"),

    # The benchmark tables' other horizons, and the Conservative regime beside
    # them.  The collateral footnote these cases used to back is gone: since
    # TODO II-35 the collateral earns r inside the ledger, and Standard and
    # Conservative agree on both gaps to a basis point.
    Case("--horizon 5", {
        "wheel": (0.0138, 0.0001),          # the benchmark tables' 5 y column
        "equity_frac": (0.965, 0.0005),     # "96.5% at five years"
        "buy_hold_adj": (0.0157, 0.0001),   # "+1.57%"
        "difference": (-0.00187, 0.00002),  # "-0.19%"; "a fifth of a point at five"
        "exposure_sold": (0.00187, 0.00002),
        "delta_frac": (0.872, 0.0005),      # "leaving 87.2%"
        "calls_sold": (0.128, 0.0005),      # "the calls take 12.8 points"
        "put_adds": (0.0347, 0.0005),       # "the put adds 3.5 back"
        "buy_hold_delta": (0.0142, 0.0001), # "+1.42%"
        "difference_delta": (-0.00035, 0.00002),  # "-0.035%"; "3.5 basis points"
        "delta_sale_frac": (0.8747, 0.0001),     # the shortcut: "87.5%"
        "shortcut": (0.000045, 0.000005),        # "under half a basis point wider"
    }, note="Standard, five years"),
    Case("--horizon 10", {
        "wheel": (0.0143, 0.0001),          # the 10 y column
        "buy_hold_adj": (0.0158, 0.0001),   # "+1.58%"
        "difference": (-0.00149, 0.00002),  # "-0.15%"
        "delta_frac": (0.900, 0.0005),
        "buy_hold_delta": (0.0146, 0.0001), # "+1.46%"
        "difference_delta": (-0.00028, 0.00002),  # "-0.028%"
        "shortcut": (0.000036, 0.000005),
    }, note="Standard, ten years"),
    Case("--p-star 0.10 --horizon 5", {
        "wheel": (0.0133, 0.0001),
        "difference": (-0.00187, 0.00002),  # "Conservative, as modelled  5y"
        "difference_delta": (-0.00035, 0.00002),
    }, note="Conservative, five years"),
    Case("--p-star 0.10 --horizon 10", {
        "wheel": (0.0139, 0.0001),
        "difference": (-0.00150, 0.00002),  # "Conservative, as modelled  10y"
        "difference_delta": (-0.00028, 0.00002),
    }, note="Conservative, ten years"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
