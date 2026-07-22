"""Numerical verification of every worked example in the article sections.

Run:  python code/verify_examples.py

Each check recomputes a number quoted in sections/*.md from first principles
and asserts it matches. If a formula in the text is edited, re-run this script;
a sign error (this project's historical failure mode) will trip an assertion.

Stdlib only (Python 3.8+).
"""

from math import exp, log, pi, sqrt
from statistics import NormalDist

N = NormalDist().cdf
Ninv = NormalDist().inv_cdf


# ----------------------------------------------------------------------
# Core model formulas (single source of truth for the numbers in the text)
#
# All formulas carry a continuous dividend yield delta (default 0). The
# convention (sections 00/05/06): mu is the asset's TOTAL expected return,
# so the price itself drifts at mu - delta; the risk-neutral price drift is
# r - delta likewise.
# ----------------------------------------------------------------------

def d2(k, tau, sigma, r, delta=0.0):
    """Black-Scholes d2 with strike expressed as k = K/S0."""
    return (-log(k) + (r - delta - sigma**2 / 2) * tau) / (sigma * sqrt(tau))


def p_assign(k, tau_p, sigma, r, delta=0.0):
    """Risk-neutral probability the put expires in the money: p = N(-d2)."""
    return N(-d2(k, tau_p, sigma, r, delta))


def k_star(p_target, tau_p, sigma, r, delta=0.0):
    """Strike fraction that hits a target assignment probability."""
    return exp(Ninv(p_target) * sigma * sqrt(tau_p)
               + (r - delta - sigma**2 / 2) * tau_p)


def p_real_world(k, tau_p, sigma, r, mu, delta=0.0):
    """Real-world assignment probability (total-return drift mu instead of r).

    The dividend yield cancels in the measure shift: risk-neutral price
    drift r - delta vs real-world price drift mu - delta.
    """
    return N(-d2(k, tau_p, sigma, r, delta) + (r - mu) * sqrt(tau_p) / sigma)


def q_recover(k, d, tau_c, sigma, mu, delta=0.0):
    """Real-world probability the covered call finishes in the money.

    Stock sits at S' = S0*(1-d) after assignment; call strike is k*S0.
    Recovery is driven by the PRICE drift mu - delta: the dividend is paid
    out of the very growth the recovery relies on.
    """
    return N(((mu - delta - sigma**2 / 2) * tau_c - log(k / (1 - d)))
             / (sigma * sqrt(tau_c)))


def q_per_put_period(q, n):
    """Convert per-call-period exit probability to the put-period clock."""
    return 1 - (1 - q) ** (1 / n)


def bs_put(k, tau, sigma, r, delta=0.0):
    """Black-Scholes European put price as a fraction of spot (S0 = 1)."""
    _d2 = d2(k, tau, sigma, r, delta)
    _d1 = _d2 + sigma * sqrt(tau)
    return k * exp(-r * tau) * N(-_d2) - exp(-delta * tau) * N(-_d1)


def bs_call(s, k, tau, sigma, r, delta=0.0):
    """Black-Scholes European call price; s and k as fractions of S0."""
    _d1 = (log(s / k) + (r - delta + sigma**2 / 2) * tau) / (sigma * sqrt(tau))
    _d2 = _d1 - sigma * sqrt(tau)
    return s * exp(-delta * tau) * N(_d1) - k * exp(-r * tau) * N(_d2)


def expected_drop_given_assignment(k, tau_p, sigma, r, delta=0.0):
    """E[1 - S_T/S0 | S_T < k*S0] under the risk-neutral lognormal.

    Uses E[S_T/S0 * 1{S_T < K}] = e^{(r-delta) tau} N(-d1), a standard
    truncated-lognormal identity.
    """
    _d2 = d2(k, tau_p, sigma, r, delta)
    _d1 = _d2 + sigma * sqrt(tau_p)
    return 1 - exp((r - delta) * tau_p) * N(-_d1) / N(-_d2)


def expected_drop_numint(k, tau, sigma, r, delta=0.0, steps=20000):
    """Same conditional expectation by direct trapezoidal integration.

    Independent cross-check of the closed form above (the formula newly
    derived in the recovery section): integrates (1 - e^x) against the
    lognormal density of x = ln(S_T/S0) over x < ln k, then normalizes
    by P(S_T < K) = N(-d2).
    """
    m_, s_ = (r - delta - sigma**2 / 2) * tau, sigma * sqrt(tau)
    lo, hi = log(k) - 12 * s_, log(k)
    h = (hi - lo) / steps

    def f(x):
        return (1 - exp(x)) * exp(-((x - m_) / s_) ** 2 / 2) / (s_ * sqrt(2 * pi))

    total = (f(lo) + f(hi)) / 2 + sum(f(lo + i * h) for i in range(1, steps))
    return total * h / N(-d2(k, tau, sigma, r, delta))


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

FAILURES = []


def check(label, got, expected, tol):
    ok = abs(got - expected) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got:.4f}, expected ~{expected}")
    if not ok:
        FAILURES.append(label)


def main():
    # Baseline parameters used throughout the article: a dividend-paying
    # quality name. mu is TOTAL return; delta_net = delta*(1 - withholding).
    k, tau_p, sigma, r, mu = 0.95, 1 / 12, 0.20, 0.05, 0.07
    delta, withhold = 0.025, 0.15
    dn = delta * (1 - withhold)
    n, tau_c = 3, 0.25
    m = 0.20

    print("--- No-dividend anchor (historical known-correct example) ---")
    check("d2 (k=0.95, monthly, delta=0)", d2(k, tau_p, sigma, r), 0.93, 0.01)
    check("p = N(-d2) (delta=0)", p_assign(k, tau_p, sigma, r), 0.176, 0.005)

    print("--- Section 5: assignment probability ---")
    check("d2 (k=0.95, monthly)", d2(k, tau_p, sigma, r, delta), 0.90, 0.01)
    check("p = N(-d2)", p_assign(k, tau_p, sigma, r, delta), 0.185, 0.005)
    check("k* for p*=20%", k_star(0.20, tau_p, sigma, r, delta), 0.953, 0.002)
    check("real-world p (mu=7% total)",
          p_real_world(k, tau_p, sigma, r, mu, delta), 0.178, 0.005)
    check("put delta N(-d1)",
          N(-(d2(k, tau_p, sigma, r, delta) + sigma * sqrt(tau_p))), 0.170, 0.005)

    print("--- Section 6: recovery probability ---")
    e_d = expected_drop_given_assignment(k, tau_p, sigma, r, delta)
    check("E[d | assignment] (monthly)", e_d, 0.079, 0.003)
    check("E[d | A] closed form vs num. integration", e_d,
          expected_drop_numint(k, tau_p, sigma, r, delta), 1e-4)
    check("E[d | A] under real-world drift (< 0.1pp shift)",
          expected_drop_given_assignment(k, tau_p, sigma, mu, delta), e_d, 0.001)
    check("d1 (k=0.95, monthly)",
          d2(k, tau_p, sigma, r, delta) + sigma * sqrt(tau_p), 0.95, 0.01)
    check("required recovery % (base d=0.08)", k / (1 - 0.08) - 1, 0.033, 0.002)
    check("q (base d=0.08, quarterly)",
          q_recover(k, 0.08, tau_c, sigma, mu, delta), 0.398, 0.005)
    check("required recovery % (stress d=0.15)", k / (1 - 0.15) - 1, 0.118, 0.002)
    check("q (stress d=0.15, quarterly)",
          q_recover(k, 0.15, tau_c, sigma, mu, delta), 0.147, 0.005)

    print("--- Section 7: inventory queue ---")
    p = p_assign(k, tau_p, sigma, r, delta)
    q08 = q_recover(k, 0.08, tau_c, sigma, mu, delta)
    q15 = q_recover(k, 0.15, tau_c, sigma, mu, delta)
    check("q_p vs q/n approx (d=0.15)", q_per_put_period(q15, n), q15 / n, 0.004)
    check("I* (base d=0.08)", p * n / q08, 1.40, 0.02)
    check("I* (stress d=0.15)", p * n / q15, 3.78, 0.05)
    check("P(I=0) for I*=1", exp(-1.0), 0.37, 0.005)
    check("P(I=0) for I*=2", exp(-2.0), 0.14, 0.005)
    check("P(I=0) for I*=3", exp(-3.0), 0.05, 0.003)
    check("self-recycling: exit rate = p",
          (p * n / q15) * q_per_put_period(q15, n), p, 0.02)

    print("--- Section 8: returns and capital ---")
    c_p = bs_put(k, tau_p, sigma, r, delta)
    check("c_p (BS put premium)", c_p, 0.0054, 0.0005)

    for d, q_d, cc_expect, run_expect, cap_expect, exc_expect in [
        # base case first, as in the text
        (0.08, q08, 0.0262, 0.0200, 1.51, 0.109),
        (0.15, q15, 0.0067, 0.0206, 3.76, 0.016),
    ]:
        c_c = bs_call(1 - d, k, tau_c, sigma, r, delta)
        I_star = p * n / q_d
        # Track A per put period, per S0: premiums + dividend carry, both
        # readable by lifecycle (each call period yields c_c + dn*tau_c)
        # or by standing inventory (I* lots x dn per year).
        run_rate = c_p + p * (c_c + dn * tau_c) / q_d
        capital = m * k + I_star * (k - c_p)
        check(f"c_c (d={d})", c_c, cc_expect, 0.0005)
        check(f"Track A run rate/period (d={d})", run_rate, run_expect, 0.0005)
        check(f"E[Capital]/S0 (d={d})", capital, cap_expect, 0.02)
        annual = run_rate / tau_p
        excess = (annual - r * capital) / capital
        check(f"excess return (d={d})", excess, exc_expect, 0.002)
        print(f"      d={d}: annual Track A = {annual:.3f}, "
              f"excess over risk-free = {excess:+.3f}/yr on capital")

    check("capital bound (k-c_p)/d", (0.95 - 0.0054) / 0.15, 6.3, 0.05)

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
