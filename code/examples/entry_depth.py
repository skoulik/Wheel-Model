"""How deep an assignment lands: the entry depth x0 and its law.

    python code/examples/entry_depth.py
    python code/examples/entry_depth.py --measure Q
    python code/examples/entry_depth.py --p-star 0.10

Backs eq:x0-def, eq:x0-law, eq:x0-mean, eq:d-mean and eq:fall-split in
section 05.  Closed form throughout -- x0 is a truncated normal and its
mean, its drop-from-price reading, and its density all have closed forms --
so there is nothing expensive to declare.  See `entry_strike.py`, the
sibling that picks the strike this depth is measured against.

Three lines are checks rather than readings, and none can pass by
construction:

  * DRIFT-FREE MEAN.  eq:x0-mean writes E[x0] as one period's move times a
    factor the dial alone decides, with no drift in it, while `entry_law`
    reaches the same number through the actual strike and the actual
    drift.  Differencing them tests that the drift really does cancel --
    which is why the two measures agree on this figure exactly rather
    than closely, and the article says so.
  * SPLIT.  eq:fall-split says the fall from the pre-assignment price is
    the strike's distance out of the money times the depth below it,
    S_T/S0 = k* e^-x0.  The depth factor is computed from the truncated
    lognormal directly and multiplied by k*; eq:d-mean reaches the same
    quantity through d1 and d2 instead.  Agreement is what licenses the
    article's reading that the drift enters E[d | assignment] through k*
    alone -- and the factor itself prints identically in the two worlds,
    which is that same statement seen from the other side.
  * AREA.  Truncating a density leaves less than area one behind, so a
    conditional law has to be divided by the probability of the event it
    conditions on -- the p* under eq:x0-law's fraction bar, which section
    05's truncation detour is about.  Integrating eq:x0-law over x0 > 0
    must therefore give 1.  Nothing else here tests that divisor: the mean
    and the density readings are computed from the same expression, so a
    wrong normalizer would move them together and look consistent.
    `entry_normal.py` runs the same check on the untruncated density.

Stdlib only.  Simpson's rule from just above zero -- eq:x0-law is defined
on x0 > 0 and `entry_law`'s density returns 0 at the endpoint itself, so
starting a hair inside avoids weighting that step -- out to 12 spreads
past the truncated mode, where the remaining tail is far below the
tolerance the area is asserted at.
"""

import os
import sys

from math import log, sqrt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "Entry: how deep assignment lands"
SECTION = "sec:entry"
EQ = ["eq:x0-def", "eq:x0-law", "eq:x0-mean", "eq:d-mean", "eq:fall-split"]

# Where eq:x0-law's density is sampled, so the law is shown rather than only
# asserted through its mean.  E[x0] and two depths past it, tracing the tail.
DENS_DEPTHS = [0.0155, 0.03, 0.05]

PANELS = 20000          # even, for Simpson
SPREADS = 12.0
INSET = 1e-12           # of one spread; see the AREA note above

FIELDS = [
    ("x0", "E[x0], mean entry depth (log)", ".4f"),
    ("x0_closed", "  the same by eq:x0-mean, which carries no drift", ".4f"),
    ("x0_gap", "  difference", ".1e"),
    ("x0_med", "  median depth, which the mean sits above", ".4f"),
    ("x0_pct", "  E[1 - e^-x0], the same depth as a price drop", ".2%"),
    ("drop", "E[d | assignment], drop from the prior price", ".2%"),
    ("factor", "E[e^-x0], eq:fall-split's depth factor, drift-free too", ".8f"),
    ("split_gap", "  k* x that, less 1 - E[d | assignment]", ".1e"),
    ("basis", "E[K/S'] = E[e^x0], the acquisition mark-loss factor", ".4f"),
    ("area", "area under eq:x0-law over x0 > 0, integrated", ".9f"),
    ("dens", "density f(x0) at the depths below", ".2f"),
    ("dens_at", "  those depths", ".4f"),
]


def _simpson(f, lo, hi, panels=PANELS):
    """Composite Simpson over [lo, hi].  Stdlib, and accurate enough that the
    quantity it checks is limited by round-off rather than by the rule."""
    h = (hi - lo) / panels
    total = f(lo) + f(hi)
    for i in range(1, panels):
        total += f(lo + i * h) * (4 if i % 2 else 2)
    return total * h / 3


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    k, _, mean_x0, dens = model.entry_law(cfg, measure)

    # The truncated law is a normal in x0 centred at ln k - mean_z, kept only
    # where x0 > 0.  For any dial short of certain assignment that centre is
    # negative -- the surviving piece is a tail -- so the range is taken from
    # the wider of the centre and zero, and the sweep is valid at whatever
    # parameters a reader passes rather than only at the article's.
    m, s = cfg.world(measure)
    sd = s * sqrt(cfg.tau_p)
    if sd == 0:
        raise ValueError("sigma*sqrt(tau_p) is zero: the entry depth has no "
                         "spread and its law is a point mass.")
    centre = log(k) - (m - s**2 / 2) * cfg.tau_p

    factor = model.entry_depth_factor(cfg, measure)

    return {
        "x0": mean_x0,
        "x0_closed": model.entry_mean(cfg, measure),
        "x0_gap": model.entry_mean(cfg, measure) - mean_x0,
        "x0_med": model.entry_median(cfg, measure),
        # x0 is a log distance and the article quotes it as one.  This is the
        # price-terms companion, and it is E[1 - e^-x0] rather than
        # 1 - e^-E[x0]: the average of the price drop, not the price drop of
        # the average.  Both round to 1.5%, which is the point -- at this
        # depth the two conventions have not yet parted company.
        "x0_pct": 1 - factor,
        "drop": model.expected_drop(cfg, measure),
        "factor": factor,
        "split_gap": k * factor - (1 - model.expected_drop(cfg, measure)),
        "basis": model.entry_basis_ratio(cfg, measure),
        "area": _simpson(dens, sd * INSET, max(centre, 0.0) + SPREADS * sd),
        "dens": [dens(x) for x in DENS_DEPTHS],
        "dens_at": list(DENS_DEPTHS),
    }


CASES = [
    Case("", {
        "x0": (0.0155, 0.0005),         # section 05: "E[x0] ~ 0.0155"
        "x0_closed": (0.0155, 0.0005),  # eq:x0-mean reaches it without m
        "x0_gap": (0.0, 1e-15),
        "x0_med": (0.0122, 0.0005),     # "against a median of 1.2%": the mean
                                        #   sits above it, one-sided tail
        "x0_pct": (0.0153, 0.0005),     # "a log depth, 1.5% as a price"
        "drop": (0.038, 0.001),         # eq:d-mean, "giving 3.8% for Standard"
        "factor": (0.98472021, 1e-8),   # eq:fall-split's second factor, to
        "split_gap": (0.0, 1e-14),      #   eight decimals because the Q case
        "area": (1.0, 1e-9),            #   below repeats the value exactly
    }, note="Standard regime"),
    Case("--measure Q", {
        "x0": (0.0155, 0.0005),         # the SAME entry depth as under P --
        "x0_gap": (0.0, 1e-15),         #   "they agree exactly", section 05
        "drop": (0.038, 0.001),         # "Under the market's drift they are
        "factor": (0.98472021, 1e-8),   # 3.8% ... as well".  The depth below
        "split_gap": (0.0, 1e-14),      #   the strike is what carries no
        "area": (1.0, 1e-9),            #   drift; k* is what carries all of it
    }, note="the same, read under the pricing drift"),
    Case("--p-star 0.10", {
        "x0": (0.0131, 0.0005),         # "Conservative entries ... E[x0] ~ 0.0131"
        "x0_closed": (0.0131, 0.0005),
        "x0_gap": (0.0, 1e-15),
        "drop": (0.047, 0.001),         # eq:d-mean, "4.7% for Conservative"
        "factor": (0.98701906, 1e-8),
        "split_gap": (0.0, 1e-14),
        "area": (1.0, 1e-9),            # and the divisor is the dial, so this
    }, note="Conservative regime"),     #   is where a p*-vs-N(-d2) slip shows
    Case("--p-star 0.10 --measure Q", {
        "x0": (0.0131, 0.0005),         # again identical across the two worlds
        "x0_gap": (0.0, 1e-15),
        "drop": (0.047, 0.001),         # "3.8% and 4.7% as well" under Q --
        "factor": (0.98701906, 1e-8),   #   differ in the 4th decimal, and the
        "split_gap": (0.0, 1e-14),      #   whole of that difference is k*
        "area": (1.0, 1e-9),
    }, note="Conservative under the pricing drift"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
