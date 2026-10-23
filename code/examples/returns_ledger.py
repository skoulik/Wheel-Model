"""The economic ledger: what Track A cannot see, and the true excess return.

    python code/examples/returns_ledger.py
    python code/examples/returns_ledger.py --p-star 0.10
    python code/examples/returns_ledger.py --measure Q

Backs eq:econ-pnl and eq:excess in section 09 -- the article's headline.
Track A's cash is not a return: it misses the appreciation of held shares (a
gain), the mark loss booked when a lot is bought above market, and the upside
surrendered when a lot is called away below market.  The three nearly cancel
at thirty years and at no other horizon, and option prices play no part in
it: the net is a lift of sigma^2/2 on the lots held against the drag of the
book still standing, which balance at 31 years (`model.hidden_terms`).  So
Track A's cash against market-value capital is not the economic return --
at five years it reads 5.9% over r against 1.60% -- and fig:hidden-terms
draws the three against the horizon.

The two-ledger table is fixed at 5/10/30 years, as section 09 tabulates it,
independent of --horizon (which drives the single-horizon breakdown above the
table).  The point of the table is that true excess is **flat** across
horizons to three decimal places, while cash-on-cost-basis is not.

Horizon-weighted; hangs off the near-grid killed walk (see `holding_time.py`).
Note: the appreciation term is E[I]*m -- the section writes it as exactly that
("11.40 lots drifting at m = 4.5% is 0.5128") -- and has no economics() field
of its own; it is the product of two returned fields.
"""

import os
import sys
from dataclasses import replace
from math import exp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, Figure, need_census,               # noqa: E402
                               need_occupation, resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "Returns: the economic ledger and true excess"
SECTION = "sec:returns"
EQ = ["eq:mark-loss", "eq:giveaway", "eq:econ-pnl", "eq:excess"]

# The horizons section 09's two-ledger table tabulates, in years.  The sticky-
# dividend table below is quoted at the same three.
HORIZONS = [5.0, 10.0, 30.0]

# Two side-questions section 09 answers with the ledger, off by default because
# each is a separate solve: "what if the dividend never falls?" (--sticky, the
# sticky-dividend fixed point at the three horizons) and the depth past which a
# payout frozen in dollars outruns the drift (--trap, one depth census).
EXTRA = [
    ("--sticky", dict(action="store_true",
                      help="the sticky-dividend fixed point at 5/10/30 years")),
    ("--trap", dict(action="store_true",
                    help="the depth x* past which a fixed payout outruns the drift")),
]

FIELDS = [
    # The eq:econ-pnl breakdown, at the chosen horizon (default 30y).
    ("appreciation", "appreciation of held shares  (+)", ".4f"),
    ("acq_loss", "mark loss at acquisition      (-)", ".4f"),
    ("call_away_loss", "upside surrendered at call-away (-)", ".4f"),
    ("net", "  net of the three", ".4f"),
    ("cost_ratio", "  the two costs as a multiple of the gain", ".2f"),
    # What drives that net (model.hidden_terms), and the horizon it is zero at.
    ("lift", "    lift: sigma^2/2 on the lots held", "+.4f"),
    ("drag", "    drag: depth of lots still held", "+.4f"),
    ("second_order", "    entry and exit, second order", "+.4f"),
    ("hidden_gap", "    left over: the near grid's own error", "+.4f"),
    ("balance", "  horizon at which the three net to zero, years", ".1f"),
    ("cash_mv", "Track A cash on market value, over r", ".2%"),
    ("econ_pnl", "economic P&L  E[Pi]", ".4f"),
    ("econ_excess", "TRUE EXCESS RETURN", ".2%"),
    # The two ledgers side by side, at 5/10/30y (eq:excess).
    ("h_labels", "  horizons", ">7s"),
    ("table_lots", "  lots held", ".2f"),
    ("table_mv", "  capital, market value", ".2f"),
    ("table_cost", "  capital, cost basis", ".2f"),
    # Flat across horizons at the running example -- and not flat once the
    # capital criterion fails, which is the point rather than a defect.
    ("table_excess", "  true excess return", ".2%"),
    ("table_cash", "  cash income on cost basis", ".2%"),
    # "What if the dividend never falls?" (only under --sticky), at 5/10/30 years.
    ("sticky_F", "  sticky-dividend inflation factor", ".3f"),
    ("sticky_delta_eff", "  effective yield delta_eff", ".2%"),
    ("sticky_excess", "  true excess at delta_eff", ".2%"),
    ("sticky_change", "  change from a constant delta", ".2%"),
    ("sticky_gap", "  gap vs buy-and-hold at delta_eff", ".2%"),
    ("sticky_inv_rise", "  inventory rise vs constant delta (30y)", ".1%"),
    ("sticky_capital_rise", "  cost-basis capital rise (30y)", ".1%"),
    # The runaway depth x* = ln(1 + nu/delta) (only under --trap), one measure.
    ("trap_xstar", "  trap depth x* (log units below strike)", ".3f"),
    ("trap_below", "    x* as a fraction below the strike", ".1%"),
    ("trap_beyond", "    30y census mass beyond x*", ".1%"),
]


def _trap_edges(cfg, measure):
    """The two-bin census that isolates the mass past the runaway depth x*."""
    return (0.0, model.sticky_dividend_trap(cfg, measure), float("inf"))


def _balance(cfg, measure, occ):
    """Where the three hidden terms net to zero, or None if they never do.

    At a reader's own parameters the net need not change sign inside the
    window searched -- a book that never grows past its costs -- and that is
    an answer to print, not an error.
    """
    try:
        return model.hidden_terms_balance(cfg, measure, occ)
    except ValueError:
        return None


def _draw_hidden(fig, ax, cfg=None, measure="P", ctx=None, **kw):
    """fig:hidden-terms -- the gain Track A misses against its two costs.

    Each averaged over the first t years, to a hundred, on the near grid the
    5/10/30-year cases use, so the curves pass through the ledger's quoted
    figures and cross where `balance` says.
    """
    import figures
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    ts = [0.5 * i for i in range(1, 201)]
    es = [model.economics(cfg, measure, occ, horizon=t) for t in ts]
    gain = [e["appreciation"] for e in es]
    mark = [e["acq_loss"] for e in es]
    costs = [e["acq_loss"] + e["call_away_loss"] for e in es]
    t0 = model.hidden_terms_balance(cfg, measure, occ)
    y0 = model.economics(cfg, measure, occ, horizon=t0)["appreciation"]

    ax.plot(ts, gain, color=figures.SERIES[0],
            label="appreciation of held shares")
    ax.plot(ts, costs, color=figures.SERIES[1],
            label="mark loss + upside surrendered")
    ax.plot(ts, mark, color=figures.SERIES[1], linewidth=0.8,
            linestyle=(0, (1, 2)), label="of which mark loss")
    ax.plot([t0], [y0], "o", color=figures.INK, markersize=4.5,
            markeredgecolor=figures.GROUND, markeredgewidth=1.0, zorder=3)
    ax.annotate(f"equal at {t0:.0f} years", (t0, y0), xytext=(6, -16),
                textcoords="offset points", color=figures.INK, fontsize=8)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("years since the first put")
    ax.set_ylabel("per year, in share prices")
    ax.legend(loc="upper left")


FIGURES = [Figure("hidden-terms", _draw_hidden)]


def requires(cfg, measure="P", horizon=30.0, trap=False, **kw):
    needs = [need_occupation(cfg, measure)]
    if trap:
        needs.append(need_census(cfg, measure, edges=_trap_edges(cfg, measure),
                                 horizon=30.0))
    return needs


def compute(cfg=None, measure="P", horizon=30.0, ctx=None,
            sticky=False, trap=False, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    # Appreciation is E[I]*m; no dedicated economics() field (see docstring).
    apprec = e["appreciation"]
    hidden = model.hidden_terms(cfg, measure, occ, horizon=horizon)
    table = [model.economics(cfg, measure, occ, horizon=H) for H in HORIZONS]

    # The sticky-dividend correction is a row of the dividend sweep at a larger,
    # self-consistent delta_eff -- so it runs its own occupation at each horizon
    # (delta moves nu, which moves the walk).  Serial and opt-in; a few solves.
    sticky_F = sticky_delta_eff = sticky_excess = sticky_change = None
    sticky_gap = None
    sticky_inv_rise = sticky_capital_rise = None
    if sticky:
        sticky_F, sticky_delta_eff, sticky_excess = [], [], []
        sticky_change, sticky_gap = [], []
        for H, base in zip(HORIZONS, table):
            d_eff, F = model.sticky_dividend_yield(cfg, measure, H)
            cfg_eff = replace(cfg, delta=d_eff)
            e_eff = model.economics(cfg_eff, measure,
                                    model.occupation(cfg_eff, measure), horizon=H)
            bh = (model.buy_hold_excess(cfg_eff, measure)
                  * e_eff["I"] / e_eff["mv_capital"])
            sticky_F.append(F)
            sticky_delta_eff.append(d_eff)
            sticky_excess.append(e_eff["econ_excess"])
            sticky_change.append(e_eff["econ_excess"] - base["econ_excess"])
            sticky_gap.append(e_eff["econ_excess"] - bh)
            if H == 30.0:      # the parenthetical mechanism: a deeper, larger book
                sticky_inv_rise = e_eff["I"] / base["I"] - 1
                sticky_capital_rise = e_eff["capital"] / base["capital"] - 1

    trap_xstar = trap_below = trap_beyond = None
    if trap:
        xstar = model.sticky_dividend_trap(cfg, measure)
        shares, _, _ = resolve(ctx, need_census(cfg, measure,
                                                edges=_trap_edges(cfg, measure),
                                                horizon=30.0))
        trap_xstar = xstar
        trap_below = 1 - exp(-xstar)
        trap_beyond = shares[1]

    return {
        "appreciation": apprec,
        "acq_loss": e["acq_loss"],
        "call_away_loss": e["call_away_loss"],
        "net": apprec - e["acq_loss"] - e["call_away_loss"],
        "cost_ratio": (e["acq_loss"] + e["call_away_loss"]) / apprec,
        "lift": hidden["lift"],
        "drag": hidden["drag"],
        "second_order": hidden["second_order"],
        "hidden_gap": hidden["gap"],
        "balance": _balance(cfg, measure, occ),
        "cash_mv": (e["income"] - cfg.r * e["mv_capital"]) / e["mv_capital"],
        "econ_pnl": e["econ_pnl"],
        "econ_excess": e["econ_excess"],
        "h_labels": [f"{H:.0f} y" for H in HORIZONS],
        "table_lots": [t["I"] for t in table],
        "table_mv": [t["mv_capital"] for t in table],
        "table_cost": [t["capital"] for t in table],
        "table_excess": [t["econ_excess"] for t in table],
        "table_cash": [t["excess"] for t in table],
        "sticky_F": sticky_F,
        "sticky_delta_eff": sticky_delta_eff,
        "sticky_excess": sticky_excess,
        "sticky_change": sticky_change,
        "sticky_gap": sticky_gap,
        "sticky_inv_rise": sticky_inv_rise,
        "sticky_capital_rise": sticky_capital_rise,
        "trap_xstar": trap_xstar,
        "trap_below": trap_below,
        "trap_beyond": trap_beyond,
    }


CASES = [
    Case("", {
        "appreciation": (0.5128, 0.0020),   # "for 11.40 lots ... is 0.5128 a year"
        "acq_loss": (0.1632, 0.0010),       # "mark loss ... comes to 0.1632"
        "call_away_loss": (0.3559, 0.0020),  # "upside surrendered ... 0.3559"
        "net": (-0.0063, 0.0015),           # the ledger's "net -0.0063"
        # The decomposition table's 30 y column, and the horizon the figure marks.
        "lift": (0.23, 0.005),              # "lift ... +0.23"
        "drag": (-0.25, 0.005),             # "drag ... -0.25"
        "second_order": (0.01, 0.005),      # "entry and exit, second order +0.01"
        "hidden_gap": (0.0, 0.006),         # the rows add to the net, within the grid
        "balance": (31.1, 0.1),             # "a little past thirty years"; "equal at 31"
        "econ_pnl": (0.7655, 0.0020),       # eq:excess: E[Pi] = 0.7655
        "econ_excess": (0.0160, 0.0005),    # eq:excess: "+1.60% per year"
        # The two-ledger table (5/10/30y): true excess is flat, cash is not.
        "table_lots": ([5.41, 7.39, 11.40], 0.05),
        "table_mv": ([5.61, 7.59, 11.59], 0.05),
        "table_cost": ([6.70, 9.83, 18.23], 0.06),
        "table_excess": ([0.0160, 0.0160, 0.0160], 0.0005),  # "flat ... to three decimals"
        "table_cash": ([0.0411, 0.0181, -0.0077], 0.0005),
    }, note="Standard regime"),
    # The decomposition table's other columns.  At five years the costs are
    # twice the gain, and Track A's cash on market value is the number an
    # operator would take for the economic return: 5.9% over r, against 1.60%.
    Case("--horizon 5", {
        "net": (-0.24, 0.005),              # "the net is -0.24 a year"
        "cost_ratio": (2.0, 0.05),          # "the costs are twice the gain"
        "lift": (0.11, 0.005),
        "drag": (-0.36, 0.005),
        "second_order": (0.01, 0.005),
        "hidden_gap": (0.0, 0.006),
        "cash_mv": (0.059, 0.0005),         # "would report an excess return of +5.9%"
    }, note="Standard regime, five years"),
    Case("--horizon 10", {
        "net": (-0.17, 0.005),
        "lift": (0.15, 0.005),
        "drag": (-0.33, 0.005),
        "second_order": (0.01, 0.005),
        "hidden_gap": (0.0, 0.006),
    }, note="Standard regime, ten years"),
    Case("--horizon 50", {
        "net": (0.08, 0.005),               # "by fifty the gain is ahead"
        "lift": (0.27, 0.005),
        "drag": (-0.20, 0.005),
        "second_order": (0.01, 0.005),
        "hidden_gap": (0.0, 0.006),
    }, note="Standard regime, fifty years"),
    Case("--p-star 0.10", {
        "econ_excess": (0.0149, 0.0005),    # Conservative: "true excess +1.49%"
        "table_lots": ([None, None, 5.50], 0.05),   # "lots held 5.50"
        "table_mv": ([None, None, 5.70], 0.05),     # "capital (market) 5.70"
        "table_cost": ([None, None, 8.90], 0.06),   # "capital (cost) 8.90"
        "table_excess": ([None, None, 0.0149], 0.0005),
        "table_cash": ([None, None, -0.0083], 0.0005),  # "cash-on-cost -0.83%"
    }, note="Conservative regime"),
    # "What if the dividend never falls?" -- the sticky-dividend fixed point.  The
    # extra carry is real and outweighed: four basis points at thirty years, and
    # negative.  All four rows of that table.
    Case("--sticky", {
        "sticky_F": ([1.020, 1.039, 1.113], 0.001),        # "inflation factor 1.020 1.039 1.113"
        "sticky_delta_eff": ([0.0255, 0.0260, 0.0278], 0.0001),  # "δ_eff 2.55% 2.60% 2.78%"
        "sticky_excess": ([0.0159, 0.0158, 0.0156], 0.0002),     # "true excess +1.59% +1.58% +1.56%"
        "sticky_change": ([-0.0001, -0.0001, -0.0004], 0.0001),  # "change −0.01pp −0.01pp −0.04pp"
        "sticky_gap": ([0.0003, 0.0001, 0.0001], 0.0001),        # "gap vs buy-and-hold +0.03pp +0.01pp +0.01pp"
        "sticky_inv_rise": (0.034, 0.003),      # "inventory rises 3.4%"
        "sticky_capital_rise": (0.051, 0.004),  # "cost-basis capital 5.1%"
    }, note="Standard regime: the dividend frozen in dollars, at 5/10/30 years"),
    # The depth past which a payout frozen in dollars outruns the drift,
    # x* = ln(1 + ν/δ), with the census mass already beyond it.
    Case("--trap", {
        "trap_xstar": (0.693, 0.005),       # x* = ln(1 + ν/δ) = ln 2
        "trap_below": (0.500, 0.001),       # "x* sits 50% below the strike"
        "trap_beyond": (0.16, 0.01),        # "16% of the thirty-year census already past it"
    }, note="real world: x* is 50% below the strike"),
    Case("--measure Q --trap", {
        "trap_xstar": (0.182, 0.005),
        "trap_below": (0.167, 0.002),       # "17% below the strike"
        "trap_beyond": (0.69, 0.01),        # "69% of the census beyond" -- prices reject a fixed payout
    }, note="the market's pricing drift: a far tighter boundary"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
