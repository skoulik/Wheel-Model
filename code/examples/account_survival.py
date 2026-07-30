"""The finite account: how much leverage survives, and with what probability.

    python code/examples/account_survival.py --gamma-s 0.25
    python code/examples/account_survival.py --gamma-s 0.25 --eps 0.01
    python code/examples/account_survival.py --gamma-s 0.25 --measure Q --leverage 1.1349

Backs eq:first-passage, eq:survive and eq:lmax in section 11.  Closed form
throughout -- the survival exponent theta = 2*nu/sigma^2 is the census tail
exponent read a second time, and first passage of a drifting walk to the
barrier is one reflection formula -- so there is nothing expensive to declare.

Three distinctions this module keeps sharp.

*   FINITE vs UNBOUNDED horizon are different quantities and the section uses
    both.  `p_horizons` is P(sold out by H) at 5/10/30/60/100 years
    (eq:first-passage); `p_ever` is P(sold out, ever) (eq:survive), the
    tolerance the leverage was solved under.  eps is a statement about
    unbounded time, and the horizon row is what it costs over a career.

*   The Q-WORLD matched pair.  Under the pricing measure the exponent falls
    from theta = 1.25 to 0.25, so a leverage carrying a 10% real-world
    liquidation risk carries far more: run --measure Q --leverage <the real
    L_max> to price the same book under the market's own drift.

*   VERY SMALL probabilities are expected, not a bug.  P(sold out by 5y) at the
    survivable leverage is ~0.001%, and the reflection term needs log N in a
    tail where the ordinary normal CDF underflows to zero; model.py's
    first_passage_prob switches to a Mills-ratio asymptotic around z = -7 and
    the fields stay finite at every argument.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                    # noqa: E402
import model                                                   # noqa: E402

TITLE = "The finite account: survivable leverage and liquidation risk"
SECTION = "sec:constrained"
EQ = ["eq:first-passage", "eq:survive", "eq:lmax"]

# The horizons section 11 tabulates P(sold out) against, in years.
HORIZONS = [5.0, 10.0, 30.0, 60.0, 100.0]

EXTRA = [
    ("--eps", dict(type=float, default=0.10,
                   help="survival tolerance: the eventual liquidation probability")),
    ("--leverage", dict(type=float, default=None,
                        help="price the risk at this L; default is L_max at eps")),
]

FIELDS = [
    ("theta", "theta = 2*nu/sigma^2, the tail exponent", ".4f"),
    ("L_max", "L_max, largest leverage at tolerance eps", ".4f"),
    ("u_rule", "u* = gamma_s*L_max, the stopping rule", ".4f"),
    ("f_star", "f*, the barrier at the leverage priced", ".4f"),
    ("drawdown", "  the drawdown to it, 1 - f*", ".1%"),
    ("p_horizons", "P(sold out) by the horizons below", ".4%"),
    ("hlabels", "  ", ">6s"),
    ("p_ever", "P(sold out, ever) at that leverage", ".4%"),
]


def requires(cfg, measure="P", horizon=None, eps=0.10, leverage=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, eps=0.10, leverage=None,
            ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    theta = model.criteria(cfg, measure)["tail_exponent"]
    L_max = model.max_leverage(cfg, measure, eps)
    L = L_max if leverage is None else leverage
    f = model.liquidation_barrier(L, cfg.gamma_s)
    return {
        "theta": theta,
        "L_max": L_max,
        "u_rule": model.survival_utilization(cfg, measure, eps),
        "f_star": f,
        "drawdown": 1.0 - f,
        "p_horizons": [model.liquidation_prob(cfg, measure, L=L, horizon=h)
                       for h in HORIZONS],
        "hlabels": [f"{h:.0f} y" for h in HORIZONS],
        "p_ever": model.liquidation_prob(cfg, measure, L=L),
    }


CASES = [
    Case("--gamma-s 0.25", {
        "theta": (1.25, 0.005),         # "where theta = 1.25"
        "L_max": (1.1349, 0.0005),      # L_max table, portfolio margin at eps=10%
        "u_rule": (0.2837, 0.0010),     # "u* = gamma_s*L_max = 0.28"
        "f_star": (0.158, 0.001),       # "f* = 0.158, an 84% drawdown"
        "drawdown": (0.84, 0.005),      # "an 84% drawdown"
        # the horizon row: "0.001%  0.11%  2.49%  5.68%  7.79%"
        "p_horizons": ([0.00001, 0.0011, 0.0249, 0.0568, 0.0779], 0.0005),
        "p_ever": (0.10, 1e-4),         # the tolerance it was solved under
    }, note="portfolio margin at eps = 10%, the section's worked account"),
    Case("--gamma-s 1.00", {
        "L_max": (1.0000, 0.0005),      # "fully paid ... 1.0000"
    }, note="shares paid in full: no leverage whatever the tolerance"),
    Case("--gamma-s 0.50", {
        "L_max": (1.0861, 0.0005),      # Reg T, eps = 10%
    }, note="Reg T at eps = 10%"),
    Case("--gamma-s 0.50 --eps 0.01", {
        "L_max": (1.0127, 0.0005),      # Reg T, eps = 1%
    }, note="Reg T at eps = 1%"),
    Case("--gamma-s 0.25 --eps 0.01", {
        "L_max": (1.0192, 0.0005),      # portfolio margin, eps = 1%
    }, note="portfolio margin at eps = 1%"),
    Case("--gamma-s 0.15", {
        "L_max": (1.1557, 0.0005),      # "most aggressive", eps = 10%
    }, note="the most aggressive margin at eps = 10%"),
    Case("--gamma-s 0.25 --measure Q", {
        "theta": (0.25, 0.005),         # "the tail exponent falls ... to theta = 0.25"
        "L_max": (1.00008, 0.0001),     # "L_max is 1.00008"
    }, note="the market's pricing drift permits no leverage at all"),
    Case("--gamma-s 0.25 --measure Q --leverage 1.1349", {
        "p_ever": (0.631, 0.002),       # "carries 63% under the pricing measure"
    }, note="the real-world L_max priced under the market's drift"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
