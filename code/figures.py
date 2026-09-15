"""Shared style and output for the article's figures.

The one module in `code/` that needs matplotlib, and it is imported only when a
figure is actually drawn: every example still runs, checks and prints without
it.  A figure is a presentation of numbers `model.py` computes -- nothing here
may compute a model quantity, for the same reason no example module may.

What a figure looks like is fixed here and nowhere else, so every figure in the
article shares it:

*   **Print, not screen.**  A white ground, one light theme, no interaction:
    these go into a LaTeX article.  Sized for a single text column.
*   **Quiet chrome, loud data.**  Hairline axes and grid one step off the
    ground, tick labels in secondary ink, 1.5 pt data lines.  Colour only on
    the data; text never wears a series colour.
*   **A fixed series order.**  Series take `SERIES` in order and never cycle.
    The first two validate against a white surface for colour-vision
    deficiency (worst adjacent protan dE 24.7, normal-vision dE 33.6); a
    figure needing a third series takes slot 3 and must be re-validated.
*   **A legend for two or more series**, with sparing direct labels; one
    series needs none, since the caption names it.  One y-axis per plot.

Deterministic output, so a regenerated figure diffs clean when nothing moved:
no creation date in the metadata, a fixed hash salt for the SVG's internal
ids, and text left as text rather than outlined -- which is also what lets the
assembly step typeset labels in the article's own font.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(ROOT, "figures")

# Categorical slots, light mode, in fixed order: blue, orange, aqua.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")

INK = "#0b0b0b"          # titles, direct labels
INK_2 = "#52514e"        # tick labels, axis labels, legend text
MUTED = "#898781"        # reference lines and their labels
GRID = "#e1e0d9"         # gridlines
AXIS = "#c3c2b7"         # axis lines
GROUND = "#ffffff"

WIDTH_IN = 6.0           # a single text column
HEIGHT_IN = 3.0
LINE_PT = 1.5

_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],     # ships with matplotlib; has Greek
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.labelcolor": INK_2,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.6,
    "axes.facecolor": GROUND,
    "axes.grid": True,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "grid.linestyle": "-",
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "legend.labelcolor": INK_2,
    "lines.linewidth": LINE_PT,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "figure.facecolor": GROUND,
    "savefig.facecolor": GROUND,
    "svg.fonttype": "none",
    "svg.hashsalt": "wheel-model",
}


def pyplot():
    """matplotlib's pyplot with the article's style applied, headless.

    Imported here rather than at module level so that nothing which merely
    imports an example module pays for, or depends on, matplotlib.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update(_RC)
    return plt


def new(width=WIDTH_IN, height=HEIGHT_IN):
    """A fresh figure and its single axes."""
    plt = pyplot()
    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax


def reference_line(ax, *, x=None, y=None, label=None, where=None):
    """A thin muted guide at a fixed x or y -- an asymptote or a threshold.

    Dashed on purpose: a guide is a threshold, which is what a dash reads as,
    and it keeps the guide from being mistaken for a data series.  `label`
    is set in muted ink beside it; `where` is the (x, y) of the label's
    anchor in data coordinates.
    """
    kw = dict(color=MUTED, linewidth=0.8, linestyle=(0, (4, 3)), zorder=1)
    if x is not None:
        ax.axvline(x, **kw)
    if y is not None:
        ax.axhline(y, **kw)
    if label and where:
        ax.annotate(label, where, color=MUTED, fontsize=8,
                    ha="left", va="bottom")


def save(fig, path):
    """Write `fig` as a deterministic SVG and close it."""
    plt = pyplot()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.05,
                metadata={"Date": None, "Creator": None})
    plt.close(fig)
