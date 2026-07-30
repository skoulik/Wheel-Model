"""The three stability boundaries: do lots come back, the capital, the account?

    python code/examples/stability_criteria.py
    python code/examples/stability_criteria.py --measure Q
    python code/examples/stability_criteria.py --g 0.05
    python code/examples/stability_criteria.py --sigma 0.28 --mu 0.07

Backs eq:count-criterion, eq:capital-criterion and eq:account-criterion in
section 10.  Closed form throughout -- all three criteria are algebra on the
drift, so there is nothing expensive to declare.

The one thing to run with your own stock's numbers.  Plug in your sigma, mu
and delta and read two margins: nu = m - sigma^2/2 (lots come back when it is
positive) and m - sigma^2 (their capital comes back when it is positive).  The
tail exponent theta = 2*nu/sigma^2 packages both -- above 0 the lots recycle,
above 1 the capital does.  The count boundary sits at theta = 0, the capital
boundary at theta = 1, and the running example's sigma = 20% puts it at 1.25:
inside both, the second by a slim margin.  Read the same config under --measure
Q and the stock crosses back over the capital line it was comfortably inside.

The third margin is nu - g, and --g is the only input here that is not a fact
about the stock: it is the rate the operator's own cash policy grows a debit
at, so nu is the ceiling on it.  The default g = 0 is the operator who
services the interest and withdraws the rest, where the third criterion
collapses onto the first; --g 0.05 is the closed form's withdraw-everything
policy at the article's borrowing rate, which fails on a stock that clears
both of the other two comfortably.  An unlevered account has no debit and is
exempt whatever this reads.  Section 11 derives g and measures what it does;
here it is a dial, and what this module shows is only that the third boundary
is independent of the first two.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Stability: the three boundaries"
SECTION = "sec:stability"
EQ = ["eq:count-criterion", "eq:capital-criterion", "eq:account-criterion"]

EXTRA = [
    ("--g", dict(type=float, default=0.0,
                 help="growth rate of the debit under the operator's cash "
                      "policy; 0 = service the interest and withdraw the rest")),
]

FIELDS = [
    ("nu", "nu = m - sigma^2/2  (count margin)", "+.4f"),
    ("count_ok", "  lots come back  (nu > 0)", "d"),
    ("m", "m = mu - delta  (price drift)", ".4f"),
    ("sigma2", "sigma^2", ".4f"),
    ("capital_ok", "  capital comes back  (m > sigma^2)", "d"),
    ("g", "g, debit growth under the cash policy", "+.4f"),
    ("nu_minus_g", "nu - g  (account margin)", "+.4f"),
    ("account_ok", "  a levered account survives  (nu > g)", "d"),
    ("theta", "tail exponent theta = 2*nu/sigma^2", ".4f"),
    ("sigma_count", "boundary in sigma: lots come back below", ".2%"),
    ("sigma_capital", "  and capital comes back below", ".2%"),
    ("delta_count", "boundary in delta: lots come back below", ".2%"),
    ("delta_capital", "  and capital comes back below", ".2%"),
]


def requires(cfg, measure="P", horizon=None, g=0.0, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, g=0.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    crit = model.criteria(cfg, measure, g)
    return {
        "nu": crit["nu"],
        "count_ok": crit["count_ok"],
        "m": crit["m"],
        "sigma2": crit["sigma2"],
        "capital_ok": crit["capital_ok"],
        "g": crit["g"],
        "nu_minus_g": crit["nu_minus_g"],
        "account_ok": crit["account_ok"],
        "theta": crit["tail_exponent"],
        **model.stability_bounds(cfg, measure),
    }


CASES = [
    Case("", {
        "nu": (0.025, 0.0005),          # section 10: "ν +2.5%"
        "count_ok": (1, 0),             # "lots come back ✔"
        "m": (0.045, 0.0005),           # "real world (m = 4.5%)"
        "sigma2": (0.04, 0.0005),       # sigma = 20%
        "capital_ok": (1, 0),           # "capital comes back ✔ by 1.2 points"
        "nu_minus_g": (0.025, 0.0005),  # "ν is the ceiling on g": 2.5% of room
        "account_ok": (1, 0),           # at g = 0 the third collapses onto the first
        "theta": (1.25, 0.01),          # "tail exponent θ 1.25"
        "sigma_count": (0.300, 0.001),    # the table: "sigma < 30.0%"
        "sigma_capital": (0.212, 0.001),  # "sigma < 21.2%"
        "delta_count": (0.050, 0.001),    # "delta < 5.0%"
        "delta_capital": (0.030, 0.001),  # "delta < 3.0%"
    }, note="Standard regime, real world"),
    Case("--measure Q", {
        "nu": (0.005, 0.0005),          # "ν +0.5%"
        "count_ok": (1, 0),             # "lots come back ✔ barely"
        "m": (0.025, 0.0005),           # "the market's prices (m = 2.5%)"
        "capital_ok": (0, 0),           # "capital comes back ✘ fails"
        "nu_minus_g": (0.005, 0.0005),  # "the room ... falls from 2.5% to half
                                        #  a point"
        "theta": (0.25, 0.01),          # "tail exponent θ 0.25"
    }, note="the market's pricing drift crosses the capital boundary"),
    # The third boundary, which is a statement about the operator rather than
    # the stock: the same stock clears both of its own criteria at every g.
    Case("--g 0.05", {
        "nu_minus_g": (-0.025, 0.0005),  # "g = r_b = 5% against ν = 2.5%"
        "account_ok": (0, 0),            # the account does not survive it
        "count_ok": (1, 0),              # while the stock is untouched:
        "capital_ok": (1, 0),            #   both of ITS criteria still hold
    }, note="withdraw the income and accrue the interest: the closed form's "
            "g = r_b, which fails on a stock that clears the other two"),
    Case("--g 0.025", {
        "nu_minus_g": (0.0, 1e-12),      # the boundary itself, g = nu
    }, note="the account boundary in the operator's own dial; the sign of a "
            "margin this small is float noise, so only its size is claimed"),
    Case("--sigma 0.30", {
        "nu": (0.0, 1e-6),              # "μ − δ > σ²/2 ... σ below 30%"
        "theta": (0.0, 1e-6),           # count boundary is theta = 0
    }, note="the count boundary in sigma; nu arrives as +7e-18, not 0"),
    Case("--sigma 0.212", {
        "theta": (1.0, 0.005),          # "the capital boundary sits at σ < 21.2%"
    }, note="the capital boundary in sigma is theta = 1"),
    Case("--delta 0.05", {
        "nu": (0.0, 1e-6),              # table: count boundary "δ < 5.0%"
        "theta": (0.0, 1e-6),
    }, note="the count boundary in dividend yield"),
    Case("--delta 0.03", {
        "theta": (1.0, 0.005),          # table: capital boundary "δ < 3.0%"
    }, note="the capital boundary in dividend yield"),
    # The ν row of section 09's dividend sweep: ν = μ − δ − σ²/2 = 5.0% − δ.  The
    # δ = 2.5% column is the default Case above (ν +2.5%); the lots and capital
    # each row grows are in returns_capital.py, the excess in returns_benchmark.py.
    Case("--delta 0.0", {
        "nu": (0.050, 0.0005),          # the sweep: "δ 0%  ν +5.0%"
    }, note="no dividend"),
    Case("--delta 0.01", {
        "nu": (0.040, 0.0005),          # "δ 1%  ν +4.0%"
    }, note="a 1% yielder"),
    Case("--delta 0.04", {
        "nu": (0.010, 0.0005),          # "δ 4%  ν +1.0%"
    }, note="a 4% yielder"),
    Case("--delta 0.06", {
        "nu": (-0.010, 0.0005),         # "δ 6%  ν −1.0%" -- past the count boundary
        "count_ok": (0, 0),             # "ν has gone negative there"
    }, note="a 6% yielder: ν negative, lots no longer all return"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
