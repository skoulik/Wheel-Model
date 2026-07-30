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

from examples._harness import Case, need_census, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "The inventory: depth census"
SECTION = "sec:inventory"
EQ = ["eq:census"]

# The section's eight bins, as nine depth edges.  A tuple: it goes into a
# cache key, and --edges rebuilds it from the reader's own cut points.
DEFAULT_EDGES = (0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, float("inf"))


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
    ("deep30", "share of held time deeper than 30%", ".1%"),
    ("deep50", "share deeper than half a log-unit", ".1%"),
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
        "deep30": _deep_share(shares, edges, 0.30),
        "deep50": _deep_share(shares, edges, 0.50),
    }


CASES = [
    Case("", {
        # section 08 table: shares and q at mid-depth, top row to bottom
        "shares": ([0.08, 0.05, 0.11, 0.07, 0.09, 0.13, 0.18, 0.28], 0.012),
        "q_mid": ([0.442, 0.275, 0.094, 0.013, 0.001, 0.000, 0.000, 0.000], 0.005),
        "mean_x": (0.380, 0.01),        # "mean depth of standing inventory is 38%"
        "mean_q": (0.066, 0.003),       # "0.066 per four-week period"
        "deep30": (0.46, 0.01),         # "Forty-six percent ... more than 30% below"
    }, note="Standard regime, thirty-year horizon"),
    Case("--stationary", {
        "mean_x": (0.79, 0.01),         # "mean depth 79%"
        "mean_q": (0.036, 0.003),       # "inventory-weighted q of 0.036"
        "deep50": (0.53, 0.01),         # "53% of held time spent more than half a log-unit"
    }, note="the stationary limit the system heads toward"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
