"""Borrowed money: the excess return on equity, and the spread that cancels it.

    python code/examples/returns_leverage.py --gamma-s 0.25
    python code/examples/returns_leverage.py --gamma-s 0.25 --fin-spread 0.015
    python code/examples/returns_leverage.py --gamma-s 0.25 --fin-spread 0.03

Backs eq:levered-excess in section 09.  Equity earns the strategy's excess on
everything it carries and pays the financing spread on the borrowed part, so

    net excess on equity  =  excess*L - spread*(L - 1),

which is **exactly neutral at every L when the spread equals the strategy's own
excess return** -- 1.60% here, against retail spreads of 1-3% that straddle it.
Above that spread leverage subtracts.

Three readings, all printed together.  `equity_req` is the second ledger line of
section 04 -- gamma_p*k posted in full plus gamma_s of the shares -- and the
leverage it implies, `L_ceiling`, is the broker's own: it is where section 04's
"close to four times the excess return" comes from, and `p_liq_ceiling` is why
that number is not about any account that survives.  `L_max` is the leverage
section 11 finds survivable instead, and the ladder columns walk it across every
account type, because the article's claim is that the verdict holds at EVERY
gamma_s: leverage multiplies the wheel and a levered buy-and-hold identically,
so `diff_ladder` -- the gap between them -- merely scales by L.

Horizon-weighted, off the near-grid killed walk: the excess being levered is
section 09's own 30-year figure, not the stationary one section 11's frontier
uses.  The two differ by the put collateral (1.60% against 1.68%), which is the
collateral footnote's 8bp and nothing else; section 09 quotes its own.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, need_occupation, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Returns: leverage, and the spread at which it is neutral"
SECTION = "sec:returns"
EQ = ["eq:levered-excess"]

# The account types of section 11's own table, in the same order.
LADDER = (1.00, 0.50, 0.25, 0.15)

EXTRA = [("--eps", dict(type=float, default=0.10,
                        help="survival tolerance the leverage is capped at"))]

FIELDS = [
    ("equity_req", "equity required, gamma_p*k + gamma_s*E[I]", ".2f"),
    ("equity_frac", "  as a share of capital at market", ".1%"),
    ("L_ceiling", "L the broker's minimum equity implies", ".2f"),
    ("dd_ceiling", "  the fall that liquidates it, 1 - f*", ".1%"),
    ("p_liq_ceiling", "  P(sold out, ever) at that leverage", ".1%"),
    ("net_ceiling", "  net excess on equity there", "+.2%"),
    ("L_max", "L_max, the leverage that survives at eps", ".4f"),
    ("net_survivable", "  net excess on equity there", "+.2%"),
    ("unlevered", "net excess unlevered (= the true excess return)", "+.2%"),
    ("neutral_spread", "the spread at which leverage is exactly neutral", ".2%"),
    ("diff_levered", "wheel minus levered buy-and-hold, at L_max", "+.3%"),
    ("L_ladder", "L_max across gamma_s = 1.00/0.50/0.25/0.15", ".4f"),
    ("net_ladder", "  net excess on equity at each", "+.2%"),
    ("diff_ladder", "  wheel minus levered buy-and-hold at each", "+.3%"),
]


def requires(cfg, measure="P", horizon=30.0, eps=0.10, **kw):
    # gamma_s, the spread and eps never touch the depth walk, so the whole
    # ladder rides on the one solve the ledger already needs.
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, eps=0.10, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    excess = e["econ_excess"]
    spread = cfg.fin_spread
    # The benchmark, levered the same way: buy-and-hold scaled to the wheel's
    # equity exposure, as in returns_benchmark.py.
    bh = model.buy_hold_excess(cfg, measure) * e["I"] / e["mv_capital"]

    req = model.equity_required(cfg, e)
    L_ceiling = e["mv_capital"] / req
    L_max = model.max_leverage(cfg, measure, eps)

    def ladder(gs):
        Cg = model.replace(cfg, gamma_s=gs)
        return model.max_leverage(Cg, measure, eps)

    Ls = [ladder(gs) for gs in LADDER]
    return {
        "equity_req": req,
        "equity_frac": req / e["mv_capital"],
        "L_ceiling": L_ceiling,
        "dd_ceiling": 1.0 - model.liquidation_barrier(L_ceiling, cfg.gamma_s),
        "p_liq_ceiling": model.liquidation_prob(cfg, measure, L=L_ceiling),
        "net_ceiling": model.levered_excess(excess, L_ceiling, spread),
        "L_max": L_max,
        "net_survivable": model.levered_excess(excess, L_max, spread),
        "unlevered": model.levered_excess(excess, 1.0, spread),
        # Neutrality is an identity, not a fit: excess*L - s*(L-1) = excess for
        # every L exactly when s = excess.  Printed as the excess itself so the
        # reader can see the two are the same number.
        "neutral_spread": excess,
        "diff_levered": (model.levered_excess(excess, L_max, spread)
                         - model.levered_excess(bh, L_max, spread)),
        "L_ladder": Ls,
        "net_ladder": [model.levered_excess(excess, L, spread) for L in Ls],
        "diff_ladder": [model.levered_excess(excess, L, spread)
                        - model.levered_excess(bh, L, spread) for L in Ls],
    }


CASES = [
    Case("--gamma-s 0.25", {
        "equity_req": (3.04, 0.02),         # the capital table's new row, 30y
        "equity_frac": (0.263, 0.005),      # "about a quarter of what is committed"
        "L_ceiling": (3.81, 0.02),          # section 04's "close to four times"
        "dd_ceiling": (0.017, 0.001),       # "1.7% below today's price"
        "p_liq_ceiling": (0.979, 0.005),    # "97.9%": not a surviving account
        "net_ceiling": (0.0611, 0.0005),    # "+6.11% at no spread at all"
        "L_max": (1.1349, 0.0005),          # section 11's survivable leverage
        "net_survivable": (0.0182, 0.0003), # "+1.82% at zero spread"
        "unlevered": (0.0160, 0.0003),      # eq:excess, unchanged at L = 1
        "neutral_spread": (0.0160, 0.0003), # the crossover = the excess itself
        "diff_levered": (0.00008, 0.00002),  # still +0.01% to two decimals
        "L_ladder": ([1.0000, 1.0861, 1.1349, 1.1557], 0.0005),
        "net_ladder": ([0.0160, 0.0174, 0.0182, 0.0185], 0.0003),
        "diff_ladder": ([0.00007, 0.00007, 0.00008, 0.00008], 0.00002),
    }, note="portfolio margin, financing at r: leverage at its most flattering"),
    Case("--gamma-s 0.25 --fin-spread 0.015", {
        "net_ceiling": (0.0190, 0.0005),    # 3.8x the exposure, +0.29pp of return
        "net_survivable": (0.0162, 0.0003), # "+1.62% at 1.5%"
        "net_ladder": ([0.0160, 0.0161, 0.0162, 0.0162], 0.0003),
    }, note="the keenest retail financing: the whole ladder inside 2bp"),
    Case("--gamma-s 0.25 --fin-spread 0.03", {
        "net_ceiling": (-0.0231, 0.0005),   # "-2.31%": past the crossover
        "net_survivable": (0.0142, 0.0003), # "+1.42% at 3%"
        "net_ladder": ([0.0160, 0.0148, 0.0142, 0.0139], 0.0003),
    }, note="a 3% spread: every levered row below the unlevered one"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
