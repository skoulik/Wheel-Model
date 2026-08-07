"""The lognormal model and the Black-Scholes formula, as section 05 states them.

    python code/examples/entry_pricing.py
    python code/examples/entry_pricing.py --measure Q
    python code/examples/entry_pricing.py --sigma 0.30 --tau-p 0.5
    python code/examples/entry_pricing.py --delta 0.05 --tau-p 2.0
    python code/examples/entry_pricing.py --iv-spread 0.03

Backs eq:lognormal and eq:bs-put in section 05's detour.  Closed form
throughout, so nothing expensive is declared.

This is the module a reader is likeliest to drive to parameters of their own,
so it is built to be right off the running example rather than merely at it:

  * IT PRINTS WHICH VOLATILITY EACH LINE USED.  The article's discipline is
    that probabilities are computed at sigma and prices are quoted at
    sigma_IV.  `iv_spread` defaults to 0, so the two coincide and a mix-up
    would be invisible at the defaults -- and the reader who passes
    --iv-spread is exactly the one it would mislead.

  * IT CHECKS DELTA AGAINST A NUMERICAL DERIVATIVE of the put price rather
    than against another closed form.  Prices are homogeneous of degree one in
    (spot, strike), so bumping the spot is the same as bumping the strike the
    other way, which the existing bs_put gives us.  This is the check that
    caught model.put_delta dropping its e^(-delta*tau) on 2026-08-07: the
    shorthand delta = N(-d1) is worth 0.05% at the running example and 9.5% at
    a two-year tenor on a 5% yielder.

  * IT REFUSES DEGENERATE CELLS rather than approximating them, the same
    policy as model._sweep_cell.  sigma*sqrt(tau) = 0 has no d1.

Put-call parity is asserted at every case: it costs nothing, holds at any
parameters, and fails loudly if a sign or a discount factor is ever lost.
"""

import os
import sys

from math import exp, log, sqrt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, run_cli                   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Entry: the lognormal model and the Black-Scholes formula"
SECTION = "sec:entry"
EQ = ["eq:lognormal", "eq:bs-put", "eq:bs-call"]

FIELDS = [
    ("m", "m, this world's price drift", ".4f"),
    ("nu_log", "  the log walk's drift, m - sigma^2/2", ".4f"),
    ("mean_factor", "E[S_tau]/S over one put tenor", ".6f"),
    ("median_factor", "  median S_tau/S, the typical path", ".6f"),
    ("sigma_dyn", "sigma, which probabilities use", ".4f"),
    ("sigma_iv", "sigma_IV, which prices use", ".4f"),
    ("k", "k*, the strike being priced", ".4f"),
    ("d1", "  d1", ".4f"),
    ("d2", "  d2", ".4f"),
    ("n_md2", "N(-d2), the put's assignment probability", ".2%"),
    ("c_p", "c_p, the put premium", ".5f"),
    ("c_c", "c_c, a call at the same strike and tenor", ".5f"),
    ("delta_put", "the put's delta, e^(-delta*tau)*N(-d1)", ".4%"),
    ("delta_fd", "  the same, differenced from c_p", ".4%"),
    ("delta_naive", "  N(-d1) alone, the no-dividend shorthand", ".4%"),
    ("parity", "put-call parity residual", ".1e"),
    ("screen_check", "N(-d2) less model.screen_prob", ".1e"),
]


def _fd_put_delta(k, tau, sigma, r, delta, h=1e-6):
    """d(c_p)/d(spot), by central difference on the existing price.

    bs_put quotes at spot = 1, so a spot of 1+h with strike K is the same
    contract as a spot of 1 with strike k/(1+h), scaled by 1+h.  That is
    homogeneity of degree one, and it lets the derivative be taken without a
    second pricing routine to get wrong in the same way.
    """
    up = (1 + h) * model.bs_put(k / (1 + h), tau, sigma, r, delta)
    dn = (1 - h) * model.bs_put(k / (1 - h), tau, sigma, r, delta)
    return (up - dn) / (2 * h)


def requires(cfg, measure="P", horizon=None, **kw):
    return []


def compute(cfg=None, measure="P", horizon=None, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    m, s = cfg.world(measure)
    tau = cfg.tau_p

    # Refused, not approximated: without a step there is no d1 to speak of.
    if s * sqrt(tau) == 0 or cfg.sigma_iv * sqrt(tau) == 0:
        raise ValueError(
            "sigma*sqrt(tau) is zero: d1 and d2 are undefined.  "
            "This is refused rather than approximated -- pick a positive "
            "sigma and tau_p.")
    if not 0 < cfg.p_star < 1:
        raise ValueError(f"p_star must lie strictly in (0, 1), got {cfg.p_star}")

    nu_log = m - s**2 / 2
    k = model.strike(cfg, measure)

    # A price is a price: the pricing formula always reads the market's drift
    # and the market's volatility, whichever world the probabilities are in.
    m_q, s_q = cfg.world("Q")
    _d2 = model.d2(k, tau, s_q, m_q)
    _d1 = _d2 + s_q * sqrt(tau)

    c_p = model.put_premium(cfg, measure)
    c_c = model.bs_call(1.0, k, tau, cfg.sigma_iv, cfg.r, cfg.delta)
    disc_d, disc_r = exp(-cfg.delta * tau), exp(-cfg.r * tau)

    return {
        "m": m,
        "nu_log": nu_log,
        "mean_factor": exp(m * tau),
        "median_factor": exp(nu_log * tau),
        "sigma_dyn": s,
        "sigma_iv": cfg.sigma_iv,
        "k": k,
        "d1": _d1,
        "d2": _d2,
        "n_md2": model.N(-_d2),
        "c_p": c_p,
        "c_c": c_c,
        "delta_put": model.put_delta(cfg, measure),
        "delta_fd": -_fd_put_delta(k, tau, cfg.sigma_iv, cfg.r, cfg.delta),
        "delta_naive": model.N(-_d1),
        "parity": c_c - c_p - (disc_d - k * disc_r),
        "screen_check": model.N(-_d2) - model.screen_prob(cfg, measure),
    }


# The structural fields -- parity, screen_check, and delta_fd against
# delta_put -- are asserted in EVERY case, because they are what makes the
# off-default cases evidence rather than decoration.
CASES = [
    Case("", {
        "m": (0.045, 1e-9),              # mu - delta, the real world
        "nu_log": (0.025, 1e-9),         # section 06's nu, written longhand
        "mean_factor": (1.000866, 1e-6),   # the price grows at m
        "median_factor": (1.000481, 1e-6),  # the typical path at m - sigma^2/2
        "k": (0.9774, 0.0005),           # the strike entry_strike also prints
        "n_md2": (0.2039, 0.001),        # = p_screen: section 05's "20.4%"
        "delta_put": (0.196046, 1e-6),
        "delta_fd": (0.196046, 1e-6),    # the derivative agrees to 1e-10
        "delta_naive": (0.196140, 1e-6),  # the shorthand, 0.05% high
        "parity": (0.0, 1e-12),
        "screen_check": (0.0, 1e-12),
    }, note="Standard regime, the article's parameters"),
    Case("--measure Q", {
        "m": (0.025, 1e-9),              # r - delta, the pricing drift
        "nu_log": (0.005, 1e-9),         # section 06's "five times smaller"
        "k": (0.9770, 0.0005),
        "n_md2": (0.2000, 1e-4),         # strike and price in the same world:
        "delta_put": (0.192234, 1e-6),   #   N(-d2) comes back to p* exactly
        "delta_fd": (0.192234, 1e-6),
        "parity": (0.0, 1e-12),
        "screen_check": (0.0, 1e-12),
    }, note="the same dial read under the pricing drift"),
    Case("--delta 0.05 --tau-p 2.0 --sigma 0.30", {
        "delta_fd": (0.109194, 1e-6),    # the derivative is the truth,
        "delta_put": (0.109194, 1e-6),   #   and the formula matches it
        "delta_naive": (0.120678, 1e-6),  # while the shorthand reads
        "parity": (0.0, 1e-12),          #   e^(-0.10) = 9.5% high
        "screen_check": (0.0, 1e-12),
    }, note="two-year tenor, 5% yield: where the no-dividend shorthand fails"),
    # The strike is picked at sigma and the option priced at sigma_IV, so the
    # screen's number moves to 23.7% while the realized rate stays at p* = 20%.
    # A module that used one volatility for both would print 20.4% here and
    # look perfectly reasonable doing it.  That is why this case exists.
    Case("--iv-spread 0.03", {
        "sigma_dyn": (0.20, 1e-9),       # probabilities still at sigma
        "sigma_iv": (0.23, 1e-9),        # prices at sigma + spread
        "k": (0.9774, 0.0005),
        "n_md2": (0.2370, 0.001),
        "parity": (0.0, 1e-12),
        "screen_check": (0.0, 1e-12),
    }, note="a volatility risk premium: the two volatilities separate"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
