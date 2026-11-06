"""Does the economic ledger agree with dollar accounting?  The check behind TODO II-34.

    python code/ledger_dollar_check.py
    python code/ledger_dollar_check.py --horizon 10

The economic ledger (`model.economics`, eq:econ-pnl) measures every flow against
the share price ruling when it happens: a call's upside surrendered as
(S_T - K)/S_T at expiry, a put's mark loss as (K - S')/S' at assignment.  A
dollar return per period measures both against the capital at the period's
start, the price the option was sold at: (S_T - K)/S_w and (K - S')/S.  The two
differ at second order -- about sigma^2*tau_c/2 of a share price for a call
period at the strike, nothing twenty log-points deep -- and this script sums the
difference over the horizon's census of call periods and the year's puts.

It then sets the result against an independent prediction: Black-Scholes's
result that an option's expected excess return is its delta times the stock's,
so the book earns its own delta (`model.book_delta`, per unit of market-value
capital) times mu - r, less the dividend-withholding leak and the collateral
overcharge.  Under the pricing drift (Q) the delta term vanishes and what is
left is exact.

A diagnostic, not a source of the article's numbers: nothing in `sections/`
quotes it and `verify_examples.py` does not run it.  It integrates against the
model's census rather than simulating, so it shares the depth walk with
model.py and is independent of it only in how the flows are booked.  Needs
numpy.
"""

import argparse
import os
import sys
from math import sqrt

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

# Standard-normal quadrature: a fine uniform grid, weights normalised to one.
_Z = np.linspace(-12.0, 12.0, 200001)
_W = np.exp(-_Z**2 / 2)
_W = _W / _W.sum()


def _ratio(drift, sigma, tau):
    """R = S_end / S_start over tau under a price drift, on the quadrature grid."""
    return np.exp((drift - sigma**2 / 2) * tau + sigma * sqrt(tau) * _Z)


def call_gap(x, drift, sigma, tau):
    """Dollar giveaway less ledger giveaway, one call period at depth x.

    Dollar E[(R - e^x)^+], per unit of the price at the call's sale; ledger
    E[(1 - e^x/R)^+], per unit of the price at expiry.  Positive: the ledger
    books the smaller cost, so its excess is the higher.
    """
    R = _ratio(drift, sigma, tau)
    K = np.exp(x)
    return float((_W * (np.maximum(R - K, 0.0)
                        - np.maximum(1.0 - K / R, 0.0))).sum())


def put_gap(k, drift, sigma, tau):
    """Ledger mark loss less dollar put loss, per put sold.

    Ledger E[(k/R - 1)^+], per unit of the price at assignment; dollar
    E[(k - R)^+], per unit of the price at the put's sale.  Positive: the
    ledger books the larger cost, so its excess is the lower.
    """
    R = _ratio(drift, sigma, tau)
    return float((_W * (np.maximum(k / R - 1.0, 0.0)
                        - np.maximum(k - R, 0.0))).sum())


def check(C, measure, horizon):
    """The ledger's excess, its exit-measurement bias, and the delta prediction."""
    m, s = C.world(measure)
    occ = model.occupation(C, measure)
    e = model.economics(C, measure, occ, horizon=horizon)
    xs, U = model.census_weights(C, measure, horizon=horizon)
    U = np.asarray(U)
    share = U / U.sum()
    gaps = np.array([call_gap(x, m, s, C.tau_c) if w > 1e-12 else 0.0
                     for x, w in zip(xs, share)])
    cap = e["mv_capital"]
    # E[I]/tau_c call periods a year, spread over depth as the census is.
    calls = e["I"] / C.tau_c * float((share * gaps).sum()) / cap
    k = model.strike(C, measure)
    puts = put_gap(k, m, s, C.tau_p) / C.cadence / cap
    leak = e["I"] * C.delta * C.withhold / cap
    over = C.r * C.gamma_p * k / cap
    inv, put = model.book_delta(C, measure, 0.0, horizon=horizon)
    delta_cap = (e["I"] * inv + put) / cap
    theory = delta_cap * (m + C.delta - C.r) - leak - over
    bias = calls - puts
    return dict(ledger=e["econ_excess"], calls=calls, puts=-puts, bias=bias,
                dollar=e["econ_excess"] - bias, delta_cap=delta_cap,
                leak=leak, over=over, theory=theory)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--horizon", type=float, default=30.0)
    ap.add_argument("--p-star", type=float, default=None)
    args = ap.parse_args(argv)
    C = model.Config()
    if args.p_star is not None:
        C = model.replace(C, p_star=args.p_star)
    m, s = C.world("P")
    print("One call period, dollar giveaway less ledger giveaway (P):")
    for x in (0.0, 0.02, 0.05, 0.1, 0.2):
        print(f"  depth {x:4.2f}   {call_gap(x, m, s, C.tau_c):.4%} of a share price")
    print(f"  sigma^2*tau_c/2 = {s * s * C.tau_c / 2:.4%}")
    for meas in ("Q", "P"):
        r = check(C, meas, args.horizon)
        print(f"\n{meas}, {args.horizon:g} years")
        print(f"  ledger true excess                       {r['ledger']:+.3%}")
        print(f"  exit-measurement bias                    {r['bias']:+.3%}"
              f"   (calls {r['calls']:+.3%}, puts {r['puts']:+.3%})")
        print(f"  dollar excess = ledger - bias            {r['dollar']:+.3%}")
        print(f"  delta {r['delta_cap']:.3f} x (mu - r) - leak - overcharge"
              f"   {r['theory']:+.3%}")


if __name__ == "__main__":
    main()
