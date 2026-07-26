"""Formulas of the superseded homogeneous model.

These are NOT part of the article any more.  The restructure (see TODO.md,
"Campaign") replaced the homogeneous approximation -- one recovery probability
q for every lot -- with the depth process and its first-passage analysis in
`model.py`.  This module exists only to keep the pre-restructure paths in
`wheel_sim.py` (homogeneous_predictions, check_quoted) and `first_passage.py`
running until those are rewritten in the verification stage, at which point
this file and its importers go away together.

Do not add anything here, and do not quote anything computed here in the
sections.

Stdlib only.
"""

from math import exp, log, pi, sqrt

from model import N, Ninv, d2


def p_assign(k, tau_p, sigma, r, delta=0.0):
    """Risk-neutral probability the put expires in the money."""
    return N(-d2(k, tau_p, sigma, r - delta))


def k_star(p_target, tau_p, sigma, r, delta=0.0):
    """Strike hitting a target *risk-neutral* assignment probability."""
    return exp(Ninv(p_target) * sigma * sqrt(tau_p)
               + (r - delta - sigma**2 / 2) * tau_p)


def p_real_world(k, tau_p, sigma, r, mu, delta=0.0):
    """Real-world assignment probability, as a shift off the risk-neutral one."""
    return N(-d2(k, tau_p, sigma, r - delta) + (r - mu) * sqrt(tau_p) / sigma)


def q_recover(k, d, tau_c, sigma, mu, delta=0.0):
    """Homogeneous recovery probability for a lot sitting d below its strike."""
    return N(((mu - delta - sigma**2 / 2) * tau_c - log(k / (1 - d)))
             / (sigma * sqrt(tau_c)))


def q_per_put_period(q, n):
    """Convert a per-call-period exit probability to the put-period clock."""
    return 1 - (1 - q) ** (1 / n)


def expected_drop_given_assignment(k, tau_p, sigma, r, delta=0.0):
    """E[1 - S_T/S0 | S_T < k*S0] under the risk-neutral lognormal."""
    _d2 = d2(k, tau_p, sigma, r - delta)
    _d1 = _d2 + sigma * sqrt(tau_p)
    return 1 - exp((r - delta) * tau_p) * N(-_d1) / N(-_d2)


def expected_drop_numint(k, tau, sigma, r, delta=0.0, steps=20000):
    """The same conditional expectation by direct trapezoidal integration."""
    m_, s_ = (r - delta - sigma**2 / 2) * tau, sigma * sqrt(tau)
    lo, hi = log(k) - 12 * s_, log(k)
    h = (hi - lo) / steps

    def f(x):
        return (1 - exp(x)) * exp(-((x - m_) / s_) ** 2 / 2) / (s_ * sqrt(2 * pi))

    total = (f(lo) + f(hi)) / 2 + sum(f(lo + i * h) for i in range(1, steps))
    return total * h / N(-d2(k, tau, sigma, r - delta))
