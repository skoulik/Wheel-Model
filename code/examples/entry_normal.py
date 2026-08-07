"""The normal distribution as section 05's detour states it, checked by area.

    python code/examples/entry_normal.py
    python code/examples/entry_normal.py --sigma 0.30
    python code/examples/entry_normal.py --p-star 0.10
    python code/examples/entry_normal.py --measure Q

Backs eq:normal and eq:phi in section 05.

The quantity used throughout is the article's own: R = ln(S_tau/S), the log
return over one put tenor, whose mean is (m - sigma^2/2)*tau_p and whose
spread is sigma*sqrt(tau_p).  Using a real instance rather than an invented
one keeps the detour tied to what the section actually does with it.

Three of these lines are checks rather than readings, and none of them can
pass by construction:

  * TOTAL AREA.  Integrating eq:normal over the whole line must give 1.  A
    dropped sqrt(2*pi) or a lost 1/sigma_Y shows up here and nowhere else.
  * STANDARDIZATION.  P(R < ln k) is computed twice -- once by integrating
    the general density directly, once as N((ln k - mu_Y)/sigma_Y) -- and the
    two must agree.  `model.normal_density` is deliberately written from the
    exponential rather than as phi(z)/sigma_Y, so this compares two
    independent expressions instead of one expression with itself.
  * ROUND TRIP.  N and N^-1 are separate implementations; N(N^-1(p)) - p over
    the whole range says whether they are inverses to double precision.

Stdlib only.  Simpson's rule over +-12 spreads, which is far enough that the
truncated tails are below 1e-30 and fine enough that the rule's own error is
smaller than the round-off it is measuring.
"""

import os
import sys

from math import log, sqrt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Entry: the normal distribution, and what standardization costs"
SECTION = "sec:entry"
EQ = ["eq:normal", "eq:phi"]

PANELS = 20000          # even, for Simpson
SPREADS = 12.0

FIELDS = [
    ("mu_y", "mu_Y, the log return's mean over one put tenor", ".6f"),
    ("sigma_y", "sigma_Y, its spread", ".6f"),
    ("area", "total area under eq:normal, integrated", ".9f"),
    ("p_direct", "P(R < ln k), by integrating eq:normal", ".6f"),
    ("p_standard", "  the same, as N((ln k - mu_Y)/sigma_Y)", ".6f"),
    ("std_gap", "  difference", ".1e"),
    ("phi0", "phi(0), which is 1/sqrt(2*pi)", ".6f"),
    ("phi_at_dial", "phi(N^-1(p*)), the d2-to-probability factor", ".4f"),
    ("roundtrip", "max |N(N^-1(p)) - p|, p over 0.01..0.99", ".1e"),
    ("tail3", "P(|z| > 3), \"uncommon\"", ".2e"),
    ("tail5", "P(|z| > 5), \"essentially never\"", ".2e"),
]


def _simpson(f, lo, hi, panels=PANELS):
    """Composite Simpson over [lo, hi].  Stdlib, and accurate enough that the
    quantities it checks are limited by round-off rather than by the rule."""
    h = (hi - lo) / panels
    total = f(lo) + f(hi)
    for i in range(1, panels):
        total += f(lo + i * h) * (4 if i % 2 else 2)
    return total * h / 3


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    m, s = cfg.world(measure)
    tau = cfg.tau_p
    if s * sqrt(tau) == 0:
        raise ValueError("sigma*sqrt(tau_p) is zero: the distribution has no "
                         "spread and standardization is undefined.")

    mu_y = (m - s**2 / 2) * tau          # the log return's own mean ...
    sigma_y = s * sqrt(tau)              # ... and its own spread
    lo, hi = mu_y - SPREADS * sigma_y, mu_y + SPREADS * sigma_y

    def dens(y):
        return model.normal_density(y, mu_y, sigma_y)

    ln_k = log(model.strike(cfg, measure))
    _, p_star, _, _ = model.entry_law(cfg, measure)

    return {
        "mu_y": mu_y,
        "sigma_y": sigma_y,
        "area": _simpson(dens, lo, hi),
        "p_direct": _simpson(dens, lo, ln_k),
        "p_standard": model.N((ln_k - mu_y) / sigma_y),
        "std_gap": _simpson(dens, lo, ln_k) - model.N((ln_k - mu_y) / sigma_y),
        "phi0": model.phi(0.0),
        "phi_at_dial": model.phi(model.Ninv(p_star)),
        "roundtrip": max(abs(model.N(model.Ninv(p / 100.0)) - p / 100.0)
                         for p in range(1, 100)),
        "tail3": 2 * model.N(-3.0),
        "tail5": 2 * model.N(-5.0),
    }


CASES = [
    Case("", {
        "mu_y": (0.000481, 1e-6),         # (m - sigma^2/2)*tau_p
        "sigma_y": (0.027735, 1e-6),      # sigma*sqrt(tau_p), NOT sigma
        "area": (1.0, 1e-9),              # eq:normal integrates to one
        "p_direct": (0.20, 1e-6),         # and to p* below the strike, which
        "p_standard": (0.20, 1e-6),       #   is how k* was chosen
        "std_gap": (0.0, 1e-9),           # standardization costs nothing
        "phi0": (0.398942, 1e-6),
        "phi_at_dial": (0.2800, 1e-4),    # section 05's "approximately 0.28"
        "roundtrip": (0.0, 1e-12),
        "tail3": (0.0027, 1e-4),          # "uncommon"
        "tail5": (5.7e-7, 1e-8),          # "essentially never"
    }, note="Standard regime; the quantity is one week's log return"),
    # sigma_Y moves with sigma while phi(N^-1(p*)) does not: the conversion
    # factor is read at the DIAL, a position on the standard curve, and the
    # standard curve is the same one whatever the quantity's own spread.
    Case("--sigma 0.30", {
        "sigma_y": (0.041603, 1e-6),
        "area": (1.0, 1e-9),
        "std_gap": (0.0, 1e-9),
        "phi_at_dial": (0.2800, 1e-4),
    }, note="a more volatile name: the spread moves, the dial does not"),
    Case("--p-star 0.10", {
        "p_direct": (0.10, 1e-6),
        "p_standard": (0.10, 1e-6),
        "std_gap": (0.0, 1e-9),
        "phi_at_dial": (0.1755, 1e-4),    # the conversion factor is smaller
    }, note="Conservative: further out, so the bell curve is lower there"),
    Case("--measure Q", {
        "mu_y": (0.000096, 1e-6),         # r - delta in place of mu - delta
        "area": (1.0, 1e-9),
        "std_gap": (0.0, 1e-9),
    }, note="the same quantity under the pricing drift"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
