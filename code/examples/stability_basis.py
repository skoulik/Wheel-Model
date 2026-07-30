"""The cost-basis multiplier and the census tail exponent theta.

    python code/examples/stability_basis.py
    python code/examples/stability_basis.py --measure Q
    python code/examples/stability_basis.py --sigma 0.212

Backs eq:basis-multiplier and eq:theta in section 10.  Closed form -- theta is
algebra on the drift, so there is nothing expensive to declare.

eq:basis-multiplier says a surviving lot's basis-to-price ratio is multiplied
each call period by e^((sigma^2 - m)*tau_c), so the relative basis shrinks in
expectation exactly when sigma^2 < m -- the capital criterion.  eq:theta is the
same statement read off the census tail: inventory thins with depth as
rho(x) ~ e^(-theta*x) with theta = 2*nu/sigma^2, and the capital integral (e^x
against that census) converges only when theta > 1.  Both boundaries are one
number: theta > 0 recycles the lots, theta > 1 the capital.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Stability: the basis multiplier and the tail exponent"
SECTION = "sec:stability"
EQ = ["eq:basis-multiplier", "eq:theta"]

FIELDS = [
    ("multiplier", "one period on the basis, e^((sigma^2-m)*tau_c)", ".6f"),
    ("theta", "tail exponent theta = 2*nu/sigma^2", ".4f"),
    ("m", "m = mu - delta", ".4f"),
    ("sigma2", "sigma^2", ".4f"),
    ("basis_shrinks", "relative basis shrinks  (sigma^2 < m)", "d"),
    ("capital_converges", "  and so capital converges  (theta > 1)", "d"),
]


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    crit = model.criteria(cfg, measure)
    return {
        "multiplier": model.basis_multiplier(cfg, measure),
        "theta": crit["tail_exponent"],
        "m": crit["m"],
        "sigma2": crit["sigma2"],
        # e^((sigma^2 - m)*tau_c) < 1  <=>  sigma^2 < m  <=>  capital_ok
        "basis_shrinks": crit["capital_ok"],
        "capital_converges": crit["capital_ok"],
    }


CASES = [
    Case("", {
        "theta": (1.25, 0.01),          # section 10: "tail exponent θ 1.25"
        "m": (0.045, 0.0005),           # "real world (m = 4.5%)"
        "sigma2": (0.04, 0.0005),       # sigma = 20%
        "basis_shrinks": (1, 0),        # "shrinks in expectation only if σ² < m"
        "capital_converges": (1, 0),    # "converges only if θ > 1" -- 1.25 > 1
    }, note="Standard regime, real world"),
    Case("--measure Q", {
        "theta": (0.25, 0.01),          # "tail exponent θ 0.25"
        "basis_shrinks": (0, 0),        # sigma^2 = 4% > m = 2.5%
        "capital_converges": (0, 0),    # "expected capital is infinite" -- 0.25 < 1
    }, note="under the market's pricing drift the tail no longer decays"),
    Case("--sigma 0.212", {
        "theta": (1.0, 0.005),          # "the capital boundary sits at σ < 21.2%"
    }, note="theta = 1 is the boundary the capital integral converges at"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
