"""The wheel's two building blocks: payoff at expiration.

    python code/examples/strategy_payoff.py --figure

Draws fig:payoff-diagrams for section 02's detour on payoff diagrams: a
cash-secured put and a covered call at the same strike, side by side, to show
they are one payoff.  A schematic, not a model result -- nothing here is priced
or computed, the shape is drawn from its corners, and so this module has no
cases and backs no formula.  Its route to the reader is the figure's anchor.

Both panels share one scale and one colour on purpose: the point of the figure
is that they are the same line.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Figure, run_cli                # noqa: E402

TITLE = "The wheel's two building blocks: payoff at expiration"
SECTION = "sec:introduction"
EQ = []
FIELDS = []

# Schematic proportions: a strike of 1 and a premium large enough to see.  The
# article's own premium, 0.31% of the price, would be a hairline at this scale.
_K, _C, _LO, _HI = 1.0, 0.1, 0.70, 1.30


def requires(**kw):
    return []


def compute(**kw):
    return {}


def _panel(ax, title, holding, figures):
    xs = [_LO, _K, _HI]
    ys = [_C - (_K - _LO), _C, _C]              # the corners of the payoff
    ax.axhline(0.0, color=figures.AXIS, linewidth=0.6, zorder=1)
    ax.plot([_LO, _K], [_C, _C], color=figures.MUTED, linewidth=0.8,
            linestyle=(0, (1, 2)), zorder=1)
    ax.plot([_K, _K], [-0.24, _C], color=figures.MUTED, linewidth=0.8,
            linestyle=(0, (1, 2)), zorder=1)
    ax.plot(xs, ys, color=figures.SERIES[0], zorder=2)
    ax.set_title(f"{title}\n", color=figures.INK, fontsize=9, loc="left")
    ax.text(0.0, 1.02, holding, transform=ax.transAxes, color=figures.INK_2,
            fontsize=8, ha="left", va="bottom")
    ax.set_xlim(_LO, _HI)
    ax.set_ylim(-0.24, 0.18)
    ax.set_xticks([_K], ["K"])
    ax.set_yticks([0.0, _C], ["0", "+c"])
    ax.grid(False)
    ax.set_xlabel("stock price at expiration")


def _draw(fig, ax, **kw):
    """fig:payoff-diagrams -- the two panels, one shared profit axis."""
    import figures
    fig.delaxes(ax)
    fig.set_size_inches(figures.WIDTH_IN, 2.4)
    left, right = fig.subplots(1, 2, sharey=True)
    _panel(left, "Cash-secured put", "cash + short put at K", figures)
    _panel(right, "Covered call", "shares + short call at K", figures)
    left.set_ylabel("profit")
    fig.subplots_adjust(wspace=0.18)


FIGURES = [Figure("payoff-diagrams", _draw)]
CASES = []


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
