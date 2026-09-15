"""The depth census: what the standing inventory is made of.

    python code/examples/inventory_census.py
    python code/examples/inventory_census.py --stationary
    python code/examples/inventory_census.py --edges 0,0.1,0.3,inf

Backs eq:census in section 08.  Length bias: inventory is sampled by time, not
by arrival, so a random held lot is far deeper than a random assignment.  The
census pushes the entry law forward through the depth walk and accumulates the
survivors ([eq:census]); its own grid lives in `depth_census`, so this declares
a census solve rather than an occupation or a stationary one.

The section gives the census at two horizons -- thirty years and the stationary
limit -- and the CLI reaches them through the standard --horizon / --stationary
flags.  The mid-depth exit column beside it is the closed form q_exit at each
bin's midpoint, and the deep-share rows are sums of census bins.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, Figure, need_census, resolve,   # noqa: E402
                               run_cli)
import model                                                  # noqa: E402

TITLE = "The inventory: depth census"
SECTION = "sec:inventory"
EQ = ["eq:census"]

# The section's bins: equal five-point steps to 50%, then the open tail.  Equal
# widths so that a share reads as a density -- the earlier 2/3/5/5/5/10/20-point
# bins made a steadily falling census look multimodal.  A tuple: it goes into a
# cache key, and --edges rebuilds it from the reader's own cut points.
DEFAULT_EDGES = tuple([i / 100 for i in range(0, 55, 5)] + [float("inf")])


def _parse_edges(s):
    return tuple(float("inf") if t.strip().lower() in ("inf", "oo") else float(t)
                 for t in s.split(","))


EXTRA = [("--edges", dict(type=_parse_edges, default=DEFAULT_EDGES,
                          help="comma-separated depth cut points; 'inf' for the open end"))]

FIELDS = [
    ("binlabels", "depth bin", ">10s"),
    ("shares", "  share of held time", ".1%"),
    ("q_mid", "  q at mid-depth", ".3f"),
    ("mean_x", "inventory-weighted mean depth", ".1%"),
    ("mean_q", "inventory-weighted exit probability", ".4f"),
    ("deep10", "share of held time within 10% of the strike", ".1%"),
    ("deep30", "share of held time deeper than 30%", ".1%"),
    ("deep50", "share deeper than half a log-unit", ".1%"),
    ("first_share", "share of held time in a lot's first call period", ".1%"),
    ("later_peak", "later periods' densest depth", ".1%"),
]


def _mids(edges):
    return [lo if hi == float("inf") else (lo + hi) / 2
            for lo, hi in zip(edges[:-1], edges[1:])]


def _labels(edges):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        out.append(f">{lo:.0%}" if hi == float("inf") else f"{lo:.0%}-{hi:.0%}")
    return out


def _deep_share(shares, edges, threshold):
    return sum(s for s, lo in zip(shares, edges[:-1]) if lo >= threshold)


def requires(cfg, measure="P", horizon=None, edges=DEFAULT_EDGES, **kw):
    return [need_census(cfg, measure, edges=edges, horizon=horizon)]


def compute(cfg=None, measure="P", horizon=None, edges=DEFAULT_EDGES, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    shares, mean_x, mean_q = resolve(ctx, need_census(cfg, measure, edges=edges,
                                                      horizon=horizon))
    return {
        "binlabels": _labels(edges),
        "shares": shares,
        "q_mid": [model.q_exit(cfg, measure, x) for x in _mids(edges)],
        "mean_x": mean_x,
        "mean_q": mean_q,
        "deep10": 1.0 - _deep_share(shares, edges, 0.10),
        "deep30": _deep_share(shares, edges, 0.30),
        "deep50": _deep_share(shares, edges, 0.50),
        **_components(cfg, measure, horizon),
    }


def _components(cfg, measure, horizon):
    """The census's two parts: a lot's first call period, and every later one.

    The first is the spike of fig:depth-census; the second rises away from the
    strike to a shoulder before it thins, and where it peaks is the depth the
    prose calls "a little more than one call's move deeper".
    """
    xs, first, later = model.census_weights(cfg, measure, horizon=horizon,
                                            split=True)
    total = sum(first) + sum(later)
    peak = max(range(len(later)), key=lambda i: later[i])
    return {"first_share": sum(first) / total, "later_peak": xs[peak]}


def _per_point(xs, weights):
    """Census weights as percent of held time per point of depth."""
    h = xs[1] - xs[0]
    total = sum(weights)
    return [100.0 * w / total * (0.01 / h) for w in weights]


def _draw_census(fig, ax, cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    """fig:depth-census -- the census as a density, finite horizon and limit.

    Plotted per point of depth, which is what the old uneven bins hid: a
    share read off a wider bin is larger without the density being higher.
    Drawn to 150% below the strike; the stationary census carries on past it.
    """
    import figures
    cfg = cfg if cfg is not None else model.Config()
    finite = horizon if horizon is not None else 30.0
    xs, first, later = model.census_weights(cfg, measure, horizon=finite,
                                            split=True)
    w_fin = [a + b for a, b in zip(first, later)]
    _, w_st = model.census_weights(cfg, measure, horizon=None)
    pct = [100.0 * x for x in xs]
    keep = [i for i, p in enumerate(pct) if p <= 150.0]
    fin, st = _per_point(xs, w_fin), _per_point(xs, w_st)
    # The two parts on the finite curve's own scale, so they sum to it.
    scale = sum(w_fin)
    part = [[100.0 * w / scale * (0.01 / (xs[1] - xs[0])) for w in ws]
            for ws in (first, later)]
    deep30 = sum(w for x, w in zip(xs, w_fin) if x >= 0.30) / sum(w_fin)

    X = [pct[i] for i in keep]
    # The parts only where they differ from the whole: past about 15 points
    # the first-period part is zero and the later part IS the curve, so
    # drawing them on would add a line along the axis and one under the curve.
    near = [i for i in keep if pct[i] <= 15.0]
    ax.plot(X, [fin[i] for i in keep], color=figures.SERIES[0], zorder=3,
            label=f"averaged over the first {finite:.0f} years")
    ax.plot([pct[i] for i in near], [part[0][i] for i in near],
            color=figures.SERIES[0], linewidth=0.9, linestyle=(0, (1, 1.6)),
            zorder=2, label="of which, lots in their first call period")
    ax.plot([pct[i] for i in near], [part[1][i] for i in near],
            color=figures.SERIES[0], linewidth=0.9, linestyle=(0, (4, 2)),
            zorder=2, label="of which, lots held longer")
    ax.plot(X, [st[i] for i in keep], color=figures.SERIES[1], zorder=3,
            label="the stationary limit")
    top = max(fin[i] for i in keep)
    figures.reference_line(ax, x=30.0,
                           label=f"{deep30:.0%} of the {finite:.0f}-year census\n"
                                 "lies deeper than 30%",
                           where=(31.5, top * 0.44))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, top * 1.05)
    ax.set_xlabel("depth below the lot's own call strike, log-points")
    ax.set_ylabel("% of held time per point of depth")
    ax.legend(loc="upper right")


FIGURES = [Figure("depth-census", _draw_census)]


CASES = [
    Case("", {
        # fig:depth-census, binned: the shares are the figure's density summed
        # over five-point bins, checked to 0.06 of a point -- the old
        # whole-percent tolerance of 1.2 points was wider than the grid
        # artifact it should have caught (see census_weights).  The prose
        # quotes the tail bin and two of the q values.
        "shares": ([0.151, 0.094, 0.086, 0.077, 0.069, 0.061,
                    0.055, 0.049, 0.043, 0.038, 0.276], 0.0006),
        "q_mid": ([0.339, 0.094, 0.013, 0.001, 0.000, 0.000,
                   0.000, 0.000, 0.000, 0.000, 0.000], 0.0005),  # "0.094 at 7.5 points, 0.013 at 12.5"
        "mean_x": (0.377, 0.005),       # "mean depth of standing inventory is 38%"
        "mean_q": (0.067, 0.0005),      # "0.067 per four-week period"
        "deep30": (0.46, 0.005),        # "Forty-six percent ... more than 30% below"
        "deep50": (0.28, 0.005),        # "28% ... more than 50% below the strike"
        "deep10": (0.245, 0.005),       # "only a quarter of all held time is that shallow"
        # the two parts drawn dashed under the thirty-year curve
        "first_share": (0.070, 0.005),
        "later_peak": (0.07, 0.01),     # "a little more than one call's move deeper" (0.055)
    }, note="Standard regime, thirty-year horizon"),
    Case("--stationary", {
        "mean_x": (0.78, 0.005),        # "mean depth 78%"
        "mean_q": (0.036, 0.0005),      # "inventory-weighted q of 0.036"
        "deep50": (0.52, 0.005),        # "52% of held time spent more than half a log-unit"
    }, note="the stationary limit the system heads toward"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
