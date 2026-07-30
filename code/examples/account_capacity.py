"""The finite account: Little's law backwards -- capacity, A*, and income.

    python code/examples/account_capacity.py
    python code/examples/account_capacity.py --gamma-s 0.25
    python code/examples/account_capacity.py --gamma-s 0.25 --equity 11.59

Backs eq:capacity, eq:astar, eq:lambda-eff, eq:income-capacity and
eq:capacity-lots in section 11.  Inventory is no longer an output: a finite
account pins it at capacity, so Little's law runs the other way and the arrival
rate becomes the output, lambda_eff = I_max/E[W].  The binding resource is
capital and the thing that consumes it is holding time.

The whole-lifetime quantities here -- E[I(inf)], E[W], and the transient
inverse T_sat that runs centuries into the tail -- come off the extrapolated
stationary walk (need_stationary), which is what model.py's report feeds
frontier(); the near grid would truncate and bias them.

Two knobs beyond gamma_s: --equity (A, the account's own money in share prices;
the default is the unconstrained inf) and --eps (the survival tolerance L_max
is solved under).  At the defaults (gamma_s = 1, A = inf) the account is never
constrained, A* = E[I(inf)], and every figure in Parts I and II stands.

One gap.  eq:capacity-lots (I_max = I/gamma_s + C/(gamma_s*S)) is the
price-dependent capacity, and its cash/price decomposition has no model.py
function -- Config carries neither the cash balance C nor a spot away from 1.
`cap_broker` below is that formula evaluated at today's price, where it
collapses to A/gamma_s (the broker's raw ceiling capacity, via saturation at
L = 1/gamma_s); the net-creditor/debtor behaviour it describes is not reachable
through this interface.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import (Case, need_stationary,          # noqa: E402
                               resolve, run_cli)
import model                                                    # noqa: E402

TITLE = "The finite account: capacity, A*, and income"
SECTION = "sec:constrained"
EQ = ["eq:capacity", "eq:astar", "eq:lambda-eff", "eq:income-capacity",
      "eq:capacity-lots"]

EXTRA = [
    ("--eps", dict(type=float, default=0.10,
                   help="survival tolerance L_max is solved under")),
]

FIELDS = [
    ("I_inf", "E[I(inf)], stationary inventory (lots)", ".2f"),
    ("EW", "E[W], mean holding time (years)", ".2f"),
    ("L_max", "L_max, survivable leverage", ".4f"),
    ("A_ceiling", "equity the broker's ceiling implies (E[I]/ceiling)", ".2f"),
    ("A_star", "A*, the equity actually needed (share prices)", ".2f"),
    ("permission_gap", "  how far the broker's ceiling is off, A*/A_ceiling", ".1f"),
    ("equity_discount", "  what the permission actually buys, 1 - 1/L_max", ".1%"),
    ("cap_broker", "I_max at the broker's ceiling, today (eq:capacity-lots)", ".2f"),
    ("drift_L", "leverage an untended account drifts to (E[I(inf)]/A)", ".4f"),
    ("capacity", "I_max = L_max*A, survivable capacity (lots)", ".2f"),
    ("throughput", "throughput = min(1, A/A*)", ".1%"),
    ("lambda_eff", "lambda_eff = I_max/E[W] (lots/year)", ".2f"),
    ("T_sat", "T_sat, years to reach capacity", ".1f"),
    ("income", "income the capacity supports (share prices/year)", ".4f"),
]


def requires(cfg, measure="P", horizon=None, eps=0.10, **kw):
    return [need_stationary(cfg, measure)]


def compute(cfg=None, measure="P", horizon=None, eps=0.10, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_stationary(cfg, measure))
    econ = model.economics(cfg, measure, occ)
    cell = model.saturation(cfg, measure, occ, eps, econ=econ)
    ceiling = model.leverage(cfg, u=1.0)                      # = 1/gamma_s
    # eq:capacity-lots at today's price: I_max = A/gamma_s = ceiling*A, computed
    # by saturation at the broker's ceiling so model.py does the arithmetic.
    # Its realized L is the leverage an untended account drifts to: the strategy
    # holds only E[I(inf)] however much it is permitted, so L = E[I(inf)]/A caps
    # out below the ceiling (1.883 against a permitted 4.00 at A = 11.59).
    broker_sat = model.saturation(cfg, measure, occ, eps,
                                  L_max=ceiling, econ=econ)
    return {
        "I_inf": econ["I"],
        "EW": econ["E[T]"],
        "L_max": cell["L_max"],
        "A_ceiling": econ["I"] / ceiling,
        "A_star": cell["A*"],
        # Two ratios the section states as ratios: the factor by which the
        # broker's ceiling misstates the equity required (also the income
        # overstatement 1/(gamma_s*L_max)), and the discount the permission
        # actually buys once it is risked correctly.
        "permission_gap": cell["A*"] / (econ["I"] / ceiling),
        "equity_discount": 1 - 1 / cell["L_max"],
        "cap_broker": broker_sat["capacity"],
        "drift_L": broker_sat["L"],
        "capacity": cell["capacity"],
        "throughput": cell["throughput"],
        "lambda_eff": cell["lambda_eff"],
        "T_sat": cell["T_sat"],
        "income": cell["income"],
    }


CASES = [
    Case("", {
        "I_inf": (21.82, 0.05),         # eq:little's "21.8 lots" carried in
        "EW": (2.10, 0.02),             # eq:holding
        "L_max": (1.0000, 0.0005),      # fully paid: no leverage
        "A_ceiling": (21.82, 0.05),     # A* table, gamma_s = 1.00
        "A_star": (21.82, 0.05),        # "1.00 | 21.82 | 21.82"
    }, note="the unconstrained operator (gamma_s = 1, A = inf)"),
    Case("--gamma-s 0.25", {
        "L_max": (1.1349, 0.0005),
        "A_ceiling": (5.46, 0.02),      # "sized ... at 5.46 share prices"
        "A_star": (19.23, 0.05),        # "They need 19.23"
        "permission_gap": (3.5, 0.05),  # "a factor of 3.5"; also the income
                                        # overstatement "3.5x at 0.25"
        "equity_discount": (0.12, 0.005),  # "buys a 12% discount"
    }, note="portfolio margin: A* is 19.23 against a ceiling implying 5.46"),
    Case("--gamma-s 0.50", {
        "A_ceiling": (10.91, 0.02),     # A* table, gamma_s = 0.50
        "A_star": (20.10, 0.05),
        "permission_gap": (1.8, 0.05),  # "1.8x at gamma_s = 0.50"
    }, note="Reg T"),
    Case("--gamma-s 0.15", {
        "A_ceiling": (3.27, 0.02),      # A* table, gamma_s = 0.15
        "A_star": (18.88, 0.05),        # "18.88 against 3.27 ... a factor of 5.8"
        "permission_gap": (5.8, 0.05),  # "5.8x at 0.15", and the summary's
                                        # "a factor of 5.8"
    }, note="the most aggressive margin"),
    Case("--gamma-s 0.25 --equity 11.59", {
        "capacity": (13.15, 0.05),      # throughput table, A = 11.59
        "throughput": (0.603, 0.005),   # "runs at 60% throughput"
        "T_sat": (18.5, 0.2),           # "takes 18.5 years to find out"
        "drift_L": (1.883, 0.001),      # "realized leverage is capped at
                                        #  E[I(inf)]/A -- 1.883 at A = 11.59"
    }, note="the model's own 30y capital, at portfolio margin"),
    Case("--gamma-s 0.25 --equity 3.00", {
        "capacity": (3.40, 0.05),       # throughput table, A = 3.00
        "throughput": (0.156, 0.005),   # throughput table, A = 3.00
        "T_sat": (0.9, 0.1),            # "under a year at A = 3"
    }, note="a small account: under a year to saturate"),
    Case("--gamma-s 0.25 --equity 15.00", {
        "capacity": (17.02, 0.05),      # throughput table, A = 15.00
        "throughput": (0.780, 0.005),   # throughput table, A = 15.00
        "T_sat": (44.4, 1.0),           # throughput table, A = 15.00
    }, note="a large account short of A*: 78% throughput"),
    Case("--gamma-s 0.25 --equity 5.00", {
        "capacity": (5.67, 0.05),       # throughput table, A = 5.00
        "throughput": (0.260, 0.005),   # "a quarter of its rate"
        "T_sat": (2.4, 0.1),            # "2.4 years at A = 5"
    }, note="a small account: a quarter of the strategy"),
    Case("--gamma-s 0.25 --equity 1.00", {
        "capacity": (1.13, 0.05),       # throughput table, A = 1.00
        "throughput": (0.052, 0.003),   # "at A = 1 at a twentieth"
        "T_sat": (0.1, 0.1),            # "0.1"
    }, note="a tiny account: a twentieth of the strategy"),
    Case("--gamma-s 0.25 --equity 19.04", {
        "capacity": (21.61, 0.05),      # throughput table, A = 19.04
        "throughput": (0.990, 0.003),   # throughput table, A = 19.04
        "T_sat": (270.0, 5.0),          # "one running 99% of it waits 270"
    }, note="just below A*: 99% throughput, 270 years to saturate"),
    Case("--gamma-s 0.25 --measure Q", {
        "A_star": (93.65, 0.10),        # Q matched pair: "A*, equity required 93.65"
        "EW": (9.01, 0.05),             # "E[W] 9.01 y"
    }, note="the market's pricing drift: A* balloons to 93.65"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
