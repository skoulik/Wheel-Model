"""What the wheel's beta is, and why the downside one is worse than the stock's.

    python code/examples/returns_beta.py
    python code/examples/returns_beta.py --n 13     # quarterly calls
    python code/examples/returns_beta.py --p-star 0.10

Backs section 09's risk subsection, which is the only risk statistic anywhere
in the article.  Two objects, and they answer different halves of the question:

**The split beta** (`model.split_beta`, eq:split-beta) regresses standing inventory's payoff
change on the underlying's, separately for up and down periods, over one call
period and census-weighted over depth.  Inventory only.  Down-beta is exactly
1 in every configuration -- below its strike a lot is pure stock, so the whole
decline arrives -- and the up-beta is what the short calls give away.  The gap
between them is governed by n, the number of put periods in a call period, and
barely by the strike dial: it is the same sqrt(n) grid tax section 07 charges
against holding time, showing up a second time as risk.

**The book delta** (`model.book_delta`, eq:book-exposure) is the whole book,
marked, after an instantaneous price shock; fig:book-exposure draws it from
-30% to +30% beside the inventory alone.  It carries the leg the beta cannot: the live short
put, whose delta runs to +1 as it goes into the money.  That is what takes the
book past *fully* exposed on a fall -- the operator holds the shares and owes
on a losing put at the same time -- and it exhibits the reversal directly,
delta climbing toward one share per lot as the price falls and toward zero as
it rises.  Israelov & Nielsen call this dynamic exposure *equity reversal* and
attribute about a quarter of a covered call's risk to it.

Both are P-measure and use the thirty-year census, as section 09's ledger does.
Nothing here is comparable with BXM's published 0.46/0.85 -- that is a
different estimator on a different book, and the comparison has its own detour.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, Figure, need_occupation,   # noqa: E402
                               resolve, run_cli)
import model                                                     # noqa: E402

TITLE = "Risk: the wheel's beta, up and down"
SECTION = "sec:returns"
EQ = ["eq:split-beta", "eq:book-exposure"]

SHOCKS = (-0.20, -0.10, 0.0, 0.10, 0.20)

FIELDS = [
    ("beta_up", "up-beta, inventory over one call period", ".3f"),
    ("beta_dn", "down-beta, same", ".3f"),
    ("beta_gap", "  the asymmetry the calls create", ".3f"),
    ("delta_dn20", "book delta / capital, price -20%", ".3f"),
    ("delta_dn10", "  price -10%", ".3f"),
    ("delta_flat", "  unshocked", ".3f"),
    ("delta_up10", "  price +10%", ".3f"),
    ("delta_up20", "  price +20%", ".3f"),
    ("held_dn20", "the shares with their calls alone, at -20%", ".3f"),
    ("put_dn20", "of which the short put, at -20%", ".3f"),
    ("put_up20", "  and at +20%", ".3f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    inv, cap = e["I"], e["mv_capital"]
    up, dn = model.split_beta(cfg, measure, horizon=horizon)
    # Deltas come back per unit of inventory and as one whole put; the book
    # holds E[I] lots against `mv_capital` of committed capital.
    d = {}
    for shock in SHOCKS:
        lot, put = model.book_delta(cfg, measure, shock, horizon=horizon)
        d[shock] = (lot * inv, put)
    return {
        "beta_up": up,
        "beta_dn": dn,
        "beta_gap": dn - up,
        "delta_dn20": sum(d[-0.20]) / cap,
        "delta_dn10": sum(d[-0.10]) / cap,
        "delta_flat": sum(d[0.0]) / cap,
        "delta_up10": sum(d[0.10]) / cap,
        "delta_up20": sum(d[0.20]) / cap,
        "held_dn20": d[-0.20][0] / cap,
        "put_dn20": d[-0.20][1],
        "put_up20": d[0.20][1],
    }


CASES = [
    Case("", {
        "beta_up": (0.828, 0.0005),     # section 09: "0.83", and "0.828" beside Conservative
        "beta_dn": (1.000, 0.001),      # "exactly one on the way down"
        "delta_dn20": (1.069, 0.005),   # "1.07" after a 20% fall
        "held_dn20": (0.983, 0.005),    # "0.98 of the capital, the part of it in shares"
        "delta_flat": (0.932, 0.0005),  # "the 0.932 ... at thirty years"
        "delta_up20": (0.608, 0.005),   # "0.61 after a 20% rise"
        "put_dn20": (1.000, 0.002),     # the put is the whole of the excess
        "put_up20": (0.000, 0.002),     # and contributes nothing on the way up
    }, note="Standard regime, 30y census"),
    Case("--horizon 5", {
        "delta_flat": (0.8747, 0.0005),  # "0.875 ... at five", the young book fig:book-exposure adds
        "delta_dn20": (1.143, 0.005),   # "1.14 after a 20% fall against 1.07"
    }, note="the five-year book, the figure's second pair of curves"),
    Case("--p-star 0.10", {
        "beta_up": (0.824, 0.0005),     # "0.828 to 0.824": the strike dial barely moves it
        "beta_dn": (1.000, 0.001),
    }, note="Conservative: the dial barely moves the asymmetry"),
    # n is the lever that does move it, and it is section 07's grid tax again:
    # a call period four times the put period gives the stock four times as
    # long to run away from a strike frozen at the start of it.
    Case("--n 1", {
        "beta_up": (0.927, 0.005),      # "0.93 when calls run on the put clock"
        "beta_gap": (0.073, 0.005),
    }, note="calls on the put clock"),
    Case("--n 13", {
        "beta_up": (0.683, 0.005),      # "0.68 at quarterly calls"
        "beta_gap": (0.317, 0.005),
    }, note="quarterly calls against weekly puts"),
    # Higher volatility REDUCES the asymmetry: lots run deeper, so their frozen
    # calls sit further out of the money and give away less of the recovery.
    Case("--sigma 0.30", {
        "beta_up": (0.870, 0.005),
        "beta_gap": (0.130, 0.005),
    }, note="sigma = 30%, where the asymmetry shrinks"),
]


def _draw_book_exposure(fig, ax, cfg=None, measure="P", ctx=None, **kw):
    """fig:book-exposure -- eq:book-exposure against the shock, -30% to +30%.

    Two books, the thirty-year one section 09 follows (solid) and a young
    five-year one (dotted), each as the whole book and as its inventory alone,
    so the gap between a pair is the short put: wide after a fall, nothing
    after a rise, and wider in the young book, whose capital is smaller.  The
    stock's own exposure, one, is the reference line, and each undisturbed
    book is marked.  Horizons are fixed, as the ledger table's are.
    """
    import figures
    from matplotlib.ticker import PercentFormatter
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    shocks = [-0.30 + 0.01 * i for i in range(61)]
    figures.reference_line(ax, y=1.0, label="the stock",
                           where=(0.155, 1.008))
    for horizon, style, off in ((30.0, "-", (6, 4)),
                                (5.0, (0, (1, 1.5)), (-38, -12))):
        e = model.economics(cfg, measure, occ, horizon=horizon)
        inv, cap = e["I"], e["mv_capital"]
        book, held = [], []
        for s in shocks:
            lot, put = model.book_delta(cfg, measure, s, horizon=horizon)
            held.append(lot * inv / cap)
            book.append((lot * inv + put) / cap)
        years = f"{horizon:.0f} years"
        ax.plot(shocks, book, color=figures.SERIES[0], linestyle=style,
                label=f"the whole book, {years}")
        ax.plot(shocks, held, color=figures.SERIES[1], linestyle=style,
                label=f"the shares with their calls, {years}")
        y0 = book[30]
        ax.plot([0.0], [y0], "o", color=figures.INK, markersize=4.5,
                markeredgecolor=figures.GROUND, markeredgewidth=1.0, zorder=3)
        ax.annotate(f"{y0:.3f}", (0.0, y0), xytext=off,
                    textcoords="offset points", color=figures.INK, fontsize=8)
    ax.set_xlim(-0.30, 0.30)
    ax.set_ylim(0.2, 1.2)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("instantaneous change in the share price")
    ax.set_ylabel("exposure per unit of capital")
    ax.legend(loc="lower left")


FIGURES = [Figure("book-exposure", _draw_book_exposure)]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
