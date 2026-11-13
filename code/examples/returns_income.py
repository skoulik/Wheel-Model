"""Track A income: the cash the strategy realizes, decomposed.

    python code/examples/returns_income.py
    python code/examples/returns_income.py --p-star 0.10
    python code/examples/returns_income.py --measure Q

Backs eq:income in section 09 -- the put premiums, call premiums, dividends
and the interest the account's cash earns, which sum to the Track A cash
income.  The interest is r on the put's collateral and on each premium until
its option expires (TODO II-35).  Horizon-weighted (income
scales with the standing inventory), so it hangs off the near-grid killed
walk; see `holding_time.py` for the pattern.

One gap is flagged in the source and repeated in the report: economics()
returns the two premium legs already summed, so only the *put* leg (a unit
conversion of the returned per-contract premium) and the *combined* total are
directly reachable.  The call leg is shown as the difference, and pinned only
transitively -- asserting put, dividends and the total fixes it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples._harness import Case, need_occupation, resolve, run_cli   # noqa: E402
import model                                                  # noqa: E402

TITLE = "Returns: the Track A income decomposition"
SECTION = "sec:returns"
EQ = ["eq:income"]

FIELDS = [
    ("put", "put premiums / yr", ".4f"),
    ("call", "call premiums / yr", ".4f"),
    ("premiums", "  the two premium legs together", ".4f"),
    ("dividends", "dividends / yr", ".4f"),
    ("interest", "interest on the account's cash / yr", ".4f"),
    ("collateral", "  on the put's collateral", ".4f"),
    ("float", "  on premiums until their options expire", ".4f"),
    ("income", "Track A income / yr", ".4f"),
]


def requires(cfg, measure="P", horizon=30.0, **kw):
    return [need_occupation(cfg, measure)]


def compute(cfg=None, measure="P", horizon=30.0, ctx=None, **kw):
    cfg = cfg if cfg is not None else model.Config()
    occ = resolve(ctx, need_occupation(cfg, measure))
    e = model.economics(cfg, measure, occ, horizon=horizon)
    # One put a week: the per-contract premium turned into a per-year rate.
    put = e["premiums_put"]
    # GAP: economics() returns prem_income already summed over the two legs
    # (put c_p/cadence + call lam*sum_prem).  The call leg alone has no
    # accessor, so it is shown as the difference -- see the report.
    return {
        "put": put,
        "call": e["premiums_call"],
        "premiums": e["premiums"],
        "dividends": e["dividends"],
        "interest": e["cash_interest"],
        "collateral": e["collateral_interest"],
        "float": e["premium_float"],
        "income": e["income"],
    }


# Economic and Track A figures moved with TODO II-35 (the account's cash earns
# r, the window's edge closed).  Where a comment quotes a section, that prose
# is being rewritten to these values (drafts/2026-11-13-account-cash-and-
# window-edge-plan.md) and still shows the old.
CASES = [
    Case("", {
        "put": (0.1591, 0.0010),        # section 09: "put premiums 0.1591 per year"
        "call": (0.3706, 0.0020),       # "call premiums 0.3706 per year"
        "premiums": (0.5297, 0.0010),   # the vol-risk-premium table: "20.0% (fair) 0.5297"
        "dividends": (0.2422, 0.0010),  # "dividends 0.2422 per year"
        # The account's cash at r (TODO II-35); section 09 does not quote these
        # yet.  r*gamma_p*k on the collateral, and each leg's premiums times
        # e^(r*tau) - 1, checked by hand: 0.05*0.2*0.98 and 0.1591*(e^(0.05/52) - 1)
        # + 0.3706*(e^(0.05/13) - 1).
        "interest": (0.0114, 0.0002),
        "collateral": (0.0098, 0.0001),
        "float": (0.0016, 0.0001),
        "income": (0.7832, 0.0020),     # eq:income "Track A income 0.7718 per year"
    }, note="Standard regime, 30y; call leg pinned transitively"),
    Case("--p-star 0.10", {
        "income": (0.3816, 0.0020),     # Conservative: "Track A income 0.371/yr"
    }, note="Conservative regime"),
    # The volatility-risk-premium sweep of section 09 -- premiums per year as the
    # quote gets richer.  Only the quote moves, so this is the premiums column of
    # that table; the excess it buys is in returns_benchmark.py.
    Case("--iv-spread 0.005", {
        "premiums": (0.5555, 0.0010),   # the table: "20.5%  0.5555"
    }, note="sigma_IV = 20.5%, half a vol point of overpricing"),
    Case("--iv-spread 0.010", {
        "premiums": (0.5818, 0.0010),   # "21.0%  0.5818"
    }, note="sigma_IV = 21.0%"),
    Case("--iv-spread 0.020", {
        "premiums": (0.6358, 0.0010),   # "22.0%  0.6358"
    }, note="sigma_IV = 22.0%"),
]


if __name__ == "__main__":
    run_cli(sys.modules[__name__])
