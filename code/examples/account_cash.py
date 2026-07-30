"""The finite account: what the operator does with the cash.

    python code/examples/account_cash.py --gamma-s 0.25 --equity 11.59
    python code/examples/account_cash.py --gamma-s 0.25 --equity 11.59 --leverage 1.1349
    python code/examples/account_cash.py --gamma-s 0.25 --equity 11.59 --leverage 1.883

Backs eq:debit-growth, eq:theta-eff, eq:gmax and eq:draw in section 11.  A cash
policy enters survival in exactly one way, by displacing the drift: the debit
grows at g = r_b + (draw - income)/D (eq:debit-growth), and every survival
result reads nu - g where it read nu, so theta_eff = 2*(nu - g)/sigma^2
(eq:theta-eff).  Read the same equation as a bound on g at a fixed leverage and
it gives the fastest survivable debit growth g_max (eq:gmax), which inverts into
the maximum cash an operator may take out, draw_max = income + (g_max - r_b)*D
(eq:draw).

The point of the draw is that it is a CONSTRAINT, not an optimum: down the
leverage axis at A = 11.59 the sustainable draw is flat to a few basis points
as far as the survivable leverage -- it even rises about 2bp first -- and then
collapses and goes negative, a demand for deposits, while the reported RoE
climbs monotonically the whole way.  Return on paper and cash in hand move
opposite ways.

The whole-lifetime income the draw is measured against comes off the
extrapolated stationary walk (need_stationary), matching frontier().  --leverage
walks the leverage axis at a fixed account size; the default cash policy is
g = 0 (Config.draw = None: service the interest, withdraw the rest), which is
the static barrier the section's earlier figures assume.

Two limits to name.  The g = r_b figure the section quotes for the withdraw-
everything policy is debit_growth() at draw = income, but the section's realized
+1.3% and the four-policy liquidation column are SIMULATED (wheel_sim.py
--scenario constrained), not closed form, and are not this module's to
reproduce.  And theta_eff (eq:theta-eff) has no standalone model.py function --
it lives inside max_leverage/max_debit_growth via the displaced drift -- so it
is exercised here through g and g_max rather than printed as its own field.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_stationary,          # noqa: E402
                               resolve, run_cli)
import model                                                    # noqa: E402

TITLE = "The finite account: the debit, and the maximum sustainable draw"
SECTION = "sec:constrained"
EQ = ["eq:debit-growth", "eq:theta-eff", "eq:gmax", "eq:draw"]

EXTRA = [
    ("--eps", dict(type=float, default=0.10,
                   help="survival tolerance the draw is held at")),
    ("--leverage", dict(type=float, default=None,
                        help="walk the leverage axis; default is L_max at eps")),
]

FIELDS = [
    ("L", "realized leverage L", ".4f"),
    ("f_star", "f*, the barrier", ".4f"),
    ("p_liq", "P(sold out, ever) at this leverage", ".1%"),
    ("g", "g, debit growth under the cash policy", ".4f"),
    ("g_max", "g_max, fastest survivable debit growth", ".4f"),
    ("draw", "draw_max, cash the operator may take (share prices/yr)", ".4f"),
    ("draw_frac", "  the same, as % of equity", ".2%"),
    ("roe_excess", "excess return on equity", "+.3%"),
]


def requires(cfg, measure="P", horizon=None, eps=0.10, leverage=None, **kw):
    return [need_stationary(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, eps=0.10, leverage=None,
            ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_stationary(cfg, measure))
    econ = model.economics(cfg, measure, occ)
    L = model.max_leverage(cfg, measure, eps) if leverage is None else leverage
    cell = model.saturation(cfg, measure, occ, eps, L_max=L, econ=econ)
    return {
        "L": cell["L"],
        "f_star": model.liquidation_barrier(L, cfg.gamma_s),
        "p_liq": model.liquidation_prob(cfg, measure, L=L),
        # g under the configured cash policy (Config.draw); None -> the g = 0
        # policy that holds the debit flat and makes the barrier static.
        "g": model.debit_growth(cfg, cell["debit"], cell["income"]),
        "g_max": cell["g_max"],
        "draw": cell["draw"],
        "draw_frac": cell["draw"] / cfg.equity,
        "roe_excess": cell["roe_excess"],
    }


CASES = [
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.0", {
        "f_star": (0.000, 0.001),       # draw table, L = 1.000
        "p_liq": (0.000, 0.002),
        "draw_frac": (0.0463, 0.0003),  # "4.63% ... unlevered"
        "roe_excess": (0.0168, 0.0005),
    }, note="unlevered: the first rung buys nothing and costs nothing"),
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.0192", {
        "f_star": (0.025, 0.001),       # draw table, L = 1.019
        "p_liq": (0.010, 0.002),
        "draw_frac": (0.0465, 0.0003),  # the +2bp peak: "rises about 2bp"
        "roe_excess": (0.0171, 0.0005),
    }, note="the sustainable draw's non-monotone peak, +2bp"),
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.1349", {
        "f_star": (0.158, 0.001),       # draw table, L = 1.135
        "p_liq": (0.100, 0.002),
        "g": (0.0, 1e-9),               # the g = 0 policy: the static barrier
        "draw_frac": (0.0458, 0.0003),  # "4.58% at survivable leverage"
        "roe_excess": (0.0190, 0.0005),
    }, note="the survivable leverage under the g = 0 cash policy"),
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.25", {
        "f_star": (0.267, 0.001),       # draw table, L = 1.250
        "p_liq": (0.192, 0.002),
        "draw_frac": (0.0430, 0.0003),
        "roe_excess": (0.0209, 0.0005),
    }, note="past the stopping rule: the draw starts falling"),
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.5", {
        "f_star": (0.444, 0.001),       # draw table, L = 1.500
        "p_liq": (0.363, 0.002),
        "draw_frac": (0.0286, 0.0003),
        "roe_excess": (0.0251, 0.0005),
    }, note="the draw collapsing while RoE keeps climbing"),
    Case("--gamma-s 0.25 --equity 11.59 --leverage 1.883", {
        "f_star": (0.625, 0.001),       # draw table, L = 1.883 = E[I(inf)]/A
        "p_liq": (0.556, 0.002),
        "draw_frac": (-0.0214, 0.0003), # "-2.14%": a demand for deposits
        "roe_excess": (0.0315, 0.0005), # "+3.15% ... higher"
    }, note="the strategy's own leverage cap: RoE up, cash negative"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
