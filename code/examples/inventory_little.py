"""Little's law: arrival rate, equilibrium inventory, and the slow approach.

    python code/examples/inventory_little.py
    python code/examples/inventory_little.py --measure Q

Backs eq:lambda and eq:little in section 08 (eq:little is also registered in
sections/00-notation.md).  E[I] = λ·E[W]: lots arrive at rate λ, stay E[W] on
average, so the standing inventory is their product.

Two walks, for the reason holding_time.py documents.  The equilibrium
inventory and the time to approach it are whole-lifetime quantities, carried by
the tail the near grid truncates and biases, so they come off the extrapolated
walk.  The 5/10/30-year trajectory is horizon-weighted -- the far tail barely
contributes -- and comes off the near grid, through economics(..., horizon=H).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, Figure, need_occupation,                # noqa: E402
                               need_stationary, resolve, run_cli)
import model                                                  # noqa: E402

TITLE = "The inventory: Little's law"
SECTION = "sec:inventory"
EQ = ["eq:lambda", "eq:little", "eq:little-finite"]

# The horizons section 08 tabulates against equilibrium, in years.
HORIZONS = [5.0, 10.0, 30.0]
# The years at which section 08 reads the departure rate off a cold start.
DEPARTURES_AT = [1.0, 5.0, 30.0]

FIELDS = [
    ("lam", "arrival rate lambda = p*/T (lots/year)", ".1f"),
    ("EW", "mean holding time E[W] (years)", ".2f"),
    ("EI_eq", "equilibrium E[I] = lambda*E[W] (lots)", ".2f"),
    ("at_h", "E[I(H)], holdings at H", ".2f"),
    ("at_h_counted", "  the same, counted put by put", ".2f"),
    ("horizons", "  average over [0, H]", ".2f"),
    ("residence", "  W(H) = that over lambda: in-window residence (y)", ".2f"),
    ("hlabels", "  ", ">6s"),
    ("approach90", "years to reach 90% of equilibrium", ".0f"),
    ("departures", "departure rate lambda*(1 - S(t)) at year t", ".2f"),
    ("dlabels", "  ", ">6s"),
    ("still_held", "S(30 y): share of lots staying beyond thirty years", ".4f"),
    ("late_share", "  their share of the equilibrium inventory", ".2f"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return [need_occupation(cfg, measure), need_stationary(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    near = resolve(ctx, need_occupation(cfg, measure))
    full = resolve(ctx, need_stationary(cfg, measure))
    eq = model.economics(cfg, measure, full)              # horizon=None: equilibrium
    return {
        "lam": eq["lambda"],
        "EW": eq["E[T]"],
        "EI_eq": eq["I"],
        # Two different quantities, and section 08 tabulates both: what is
        # held *at* H, and the average across [0, H] that a return over the
        # window has to be divided by.  They differ by a third at 30 years.
        "at_h": [model.inventory_at(cfg, measure, near, h) for h in HORIZONS],
        # The same holdings with each put landing in one lump at its expiry
        # instead of as a steady flow.  Section 08 says the two agree at every
        # call date; 5, 10 and 30 years are call dates, so this row must match.
        "at_h_counted": [model.inventory_counted(cfg, measure, near, h)
                         for h in HORIZONS],
        "horizons": [model.economics(cfg, measure, near, horizon=h)["I"]
                     for h in HORIZONS],
        # Little's law read over the window rather than over a lot's whole
        # life: dividing the window's average inventory by the arrival rate
        # returns the time a lot spends INSIDE the window, which is the
        # quantity the window form of the law is about.  It is a ratio of two
        # numbers already above, not a new solve -- and the point of printing
        # it is that at 30 years it reads 1.10 against a full E[W] of 2.10, so
        # the window sees about half of each lot and holds about half the
        # equilibrium inventory.
        "residence": [model.economics(cfg, measure, near, horizon=h)["I"]
                      / eq["lambda"] for h in HORIZONS],
        "hlabels": [f"{h:.0f} y" for h in HORIZONS],
        "approach90": model.time_to_fraction(cfg, full, 0.9),
        # Why the stock builds up: holdings grow at lambda*S(t), so departures
        # run at lambda*(1 - S(t)) and close on arrivals only as fast as the
        # survival curve dies.  Off the near grid, like the trajectory above.
        "departures": [model.departure_rate(cfg, measure, near, t)
                       for t in DEPARTURES_AT],
        "dlabels": [f"{t:.0f} y" for t in DEPARTURES_AT],
        "still_held": 1 - model.departure_rate(cfg, measure, near, 30.0)
                      / eq["lambda"],
        # At equilibrium the lots older than thirty years are exactly the ones
        # whose stay exceeds thirty, and they hold lambda * integral_30^inf
        # S(u) du -- the equilibrium less what a cold start holds at thirty.
        # The same two numbers as the "seven tenths" of section 08, so the
        # same mix of walks: equilibrium extrapolated, thirty years near.
        "late_share": 1 - model.inventory_at(cfg, measure, near, 30.0)
                      / eq["I"],
    }


def _draw_approach(fig, ax, cfg=None, measure="P", ctx=None, **kw):
    """fig:inventory-approach -- holdings and their running average, to 150 y.

    Off the extrapolated walk, not the near grid the 5/10/30-year cases use:
    a curve that has to reach the equilibrium and cross 90% of it where
    `approach90` says needs the tail the near grid truncates (it runs 0.1 lot
    high at thirty years and 0.1 low at 150).
    """
    import figures
    cfg = cfg if cfg is not None else model.Config()
    full = resolve(ctx, need_stationary(cfg, measure))
    eq = model.economics(cfg, measure, full)["I"]
    t90 = model.time_to_fraction(cfg, full, 0.9)
    ts = [0.5 * i for i in range(0, 301)]
    held = [model.inventory_at(cfg, measure, full, t) for t in ts]
    avg_ts = ts[1::2]
    avg = [model.economics(cfg, measure, full, horizon=t)["I"] for t in avg_ts]

    ax.plot(ts, held, color=figures.SERIES[0], label="held at year t")
    ax.plot(avg_ts, avg, color=figures.SERIES[1],
            label="averaged over the first t years")
    figures.reference_line(ax, y=eq, label=f"equilibrium, {eq:.1f} lots",
                           where=(2, eq + 0.3))
    ax.plot([t90], [0.9 * eq], "o", color=figures.SERIES[0], markersize=5,
            markeredgecolor=figures.GROUND, markeredgewidth=1.2, zorder=3)
    ax.annotate(f"90% of equilibrium\nafter {t90:.0f} years", (t90, 0.9 * eq),
                xytext=(8, -26), textcoords="offset points",
                color=figures.INK, fontsize=8)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, eq * 1.12)
    ax.set_xlabel("years since the first put")
    ax.set_ylabel("lots")
    ax.legend(loc="lower right")


FIGURES = [Figure("inventory-approach", _draw_approach)]


CASES = [
    Case("", {
        "lam": (10.4, 0.05),            # eq:lambda: "0.20 / (1/52) = 10.4 lots per year"
        "EW": (2.10, 0.02),             # eq:holding, carried into eq:little
        "EI_eq": (21.8, 0.1),           # eq:little: "10.4 × 2.10 = 21.8 lots"
        # fig:inventory-approach's two curves read at 5/10/30 years; the prose
        # quotes "15.4 lots against an average of 11.4" at thirty.
        "at_h": ([7.95, 10.57, 15.42], 0.05),      # eq:little-finite, upper curve
        # "counting week by week gives the same total at every call date"
        "at_h_counted": ([7.95, 10.57, 15.42], 0.005),
        "horizons": ([5.41, 7.39, 11.40], 0.05),   # the [0,H] average, lower curve
        # "0.52 years over a five-year window, 0.71 over ten, and 1.10 over
        # thirty, against a full life of 2.10" -- the window reading of the law
        "residence": ([0.52, 0.71, 1.10], 0.005),
        "approach90": (90.0, 3.0),      # "Reaching 90% of the equilibrium level takes 90 years"
        # "departures reach 8.5 lots a year by the end of the first year, 9.7
        # by the fifth and 10.25 by the thirtieth"
        "departures": ([8.54, 9.72, 10.25], 0.01),
        # "within 1.4% of arrivals ... one lot in seventy"
        "still_held": (0.0144, 0.0003),
        # "they carry the three tenths of the equilibrium the operator does
        # not yet hold"
        "late_share": (0.29, 0.01),
    }, note="Standard regime"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
