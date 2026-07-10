"""Numerical verification of every worked example in the article sections.

Run:  python code/verify_examples.py

Each check recomputes a number quoted in sections/*.md from first principles
and asserts it matches. If a formula in the text is edited, re-run this script;
a sign error (this project's historical failure mode) will trip an assertion.

Stdlib only (Python 3.8+).
"""

from math import exp, log, sqrt
from statistics import NormalDist

N = NormalDist().cdf
Ninv = NormalDist().inv_cdf


# ----------------------------------------------------------------------
# Core model formulas (single source of truth for the numbers in the text)
# ----------------------------------------------------------------------

def d2(k, tau, sigma, r):
    """Black-Scholes d2 with strike expressed as k = K/S0."""
    return (-log(k) + (r - sigma**2 / 2) * tau) / (sigma * sqrt(tau))


def p_assign(k, tau_p, sigma, r):
    """Risk-neutral probability the put expires in the money: p = N(-d2)."""
    return N(-d2(k, tau_p, sigma, r))


def k_star(p_target, tau_p, sigma, r):
    """Strike fraction that hits a target assignment probability."""
    return exp(Ninv(p_target) * sigma * sqrt(tau_p) + (r - sigma**2 / 2) * tau_p)


def p_real_world(k, tau_p, sigma, r, mu):
    """Real-world assignment probability (drift mu instead of r)."""
    return N(-d2(k, tau_p, sigma, r) + (r - mu) * sqrt(tau_p) / sigma)


def q_recover(k, d, tau_c, sigma, mu):
    """Real-world probability the covered call finishes in the money.

    Stock sits at S' = S0*(1-d) after assignment; call strike is k*S0.
    """
    return N(((mu - sigma**2 / 2) * tau_c - log(k / (1 - d))) / (sigma * sqrt(tau_c)))


def q_per_put_period(q, n):
    """Convert per-call-period exit probability to the put-period clock."""
    return 1 - (1 - q) ** (1 / n)


def bs_put(k, tau, sigma, r):
    """Black-Scholes European put price as a fraction of spot (S0 = 1)."""
    _d2 = d2(k, tau, sigma, r)
    _d1 = _d2 + sigma * sqrt(tau)
    return k * exp(-r * tau) * N(-_d2) - N(-_d1)


def bs_call(s, k, tau, sigma, r):
    """Black-Scholes European call price; s and k as fractions of S0."""
    _d1 = (log(s / k) + (r + sigma**2 / 2) * tau) / (sigma * sqrt(tau))
    _d2 = _d1 - sigma * sqrt(tau)
    return s * N(_d1) - k * exp(-r * tau) * N(_d2)


def expected_drop_given_assignment(k, tau_p, sigma, r):
    """E[1 - S_T/S0 | S_T < k*S0] under the risk-neutral lognormal.

    Uses E[S_T/S0 * 1{S_T < K}] = e^{r tau} N(-d1), a standard
    truncated-lognormal identity.
    """
    _d2 = d2(k, tau_p, sigma, r)
    _d1 = _d2 + sigma * sqrt(tau_p)
    return 1 - exp(r * tau_p) * N(-_d1) / N(-_d2)


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

FAILURES = []


def check(label, got, expected, tol):
    ok = abs(got - expected) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got:.4f}, expected ~{expected}")
    if not ok:
        FAILURES.append(label)


# Baseline parameters used throughout the article
k, tau_p, sigma, r, mu = 0.95, 1 / 12, 0.20, 0.05, 0.07
n, tau_c = 3, 0.25

print("--- Section 5: assignment probability ---")
check("d2 (k=0.95, monthly)", d2(k, tau_p, sigma, r), 0.93, 0.01)
check("p = N(-d2)", p_assign(k, tau_p, sigma, r), 0.176, 0.005)
check("k* for p*=20%", k_star(0.20, tau_p, sigma, r), 0.955, 0.002)
check("real-world p (mu=7%)", p_real_world(k, tau_p, sigma, r, mu), 0.166, 0.005)
check("put delta N(-d1)", N(-(d2(k, tau_p, sigma, r) + sigma * sqrt(tau_p))), 0.161, 0.005)

print("--- Section 6: recovery probability ---")
check("q (d=0.15, quarterly)", q_recover(k, 0.15, tau_c, sigma, mu), 0.162, 0.005)
check("required recovery %", k / (1 - 0.15) - 1, 0.118, 0.002)
check("q (d=0.08, quarterly)", q_recover(k, 0.08, tau_c, sigma, mu), 0.422, 0.005)
check("E[d | assignment] (monthly)", expected_drop_given_assignment(k, tau_p, sigma, r), 0.079, 0.003)

print("--- Section 7: inventory queue ---")
p = p_assign(k, tau_p, sigma, r)
q15 = q_recover(k, 0.15, tau_c, sigma, mu)
I_star_15 = p * n / q15
check("q_p vs q/n approx (d=0.15)", q_per_put_period(q15, n), q15 / n, 0.004)
check("I* (d=0.15)", I_star_15, 3.26, 0.05)
check("P(I=0) for I*=1", exp(-1.0), 0.37, 0.005)
check("P(I=0) for I*=2", exp(-2.0), 0.14, 0.005)
check("P(I=0) for I*=3", exp(-3.0), 0.05, 0.003)
check("self-recycling: exit rate = p", I_star_15 * q_per_put_period(q15, n), p, 0.02)

print("--- Section 8: returns and capital ---")
c_p = bs_put(k, tau_p, sigma, r)
check("c_p (BS put premium)", c_p, 0.0050, 0.0005)

for d, q_d, cc_expect, run_expect, cap_expect in [
    (0.15, q15, 0.0077, 0.0134, 3.27),
    (0.08, q_recover(k, 0.08, tau_c, sigma, mu), 0.0286, 0.0169, 1.37),
]:
    c_c = bs_call(1 - d, k, tau_c, sigma, r)
    I_star = p * n / q_d
    run_rate = c_p + p * c_c / q_d                # Track A per put period, per S0
    capital = 0.20 * k + I_star * (k - c_p)       # margin m=0.20 on live put + inventory basis
    check(f"c_c (d={d})", c_c, cc_expect, 0.0005)
    check(f"Track A run rate/period (d={d})", run_rate, run_expect, 0.0005)
    check(f"E[Capital]/S0 (d={d})", capital, cap_expect, 0.02)
    annual = run_rate / tau_p
    excess = (annual - r * capital) / capital
    print(f"      d={d}: annual Track A = {annual:.3f}, excess over risk-free = {excess:+.3f}/yr on capital")

check("capital bound (k-c_p)/d", (0.95 - 0.005) / 0.15, 6.3, 0.05)

print()
if FAILURES:
    raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
print("All checks passed.")
