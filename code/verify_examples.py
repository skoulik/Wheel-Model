"""Numerical verification of every worked example quoted in the sections.

Run:  python code/verify_examples.py          (analytic, ~4 s)
      python code/verify_examples.py --full   (adds the extrapolated
                                               stationary figures, ~5 s)

Those used to be 7 and 12 minutes.  Two changes bought it back: model.py now
convolves the depth density with numpy when it is installed (~100x on the
single-config path, and the pure-Python path still runs unchanged when it is
not -- the two are checked against each other below), and the sweeps here,
which are lists of independent configurations, run through model.pmap over a
process pool.  Set WHEEL_WORKERS=1 to force the serial path.

The weekly cadence is what made it expensive: the call grid is 4 weeks, so
covering the same span of calendar years takes 4.3x more periods than the old
quarterly grid, and resolving a period's step (sigma*sqrt(tau_c) = 0.055)
needs h = 0.01 rather than 0.02.

Since 2026-07-30 this file no longer asserts the article's worked examples
itself.  Every numbered formula is produced by a standalone script under
`code/examples/`, which carries the article's own invocations as frozen cases
-- a case holds a *command line*, the same one the section's footnote prints,
so the command a reader runs and the command checked here cannot drift apart.
This file discovers those modules, unions their expensive solves into one
parallel batch, runs every case, and then checks the policy itself: that every
`{#eq:...}` in `sections/` has a script and every footnote leads to the script
backing its own formula.

What remains here directly is what no example module can own: invariants and
cross-checks between two independent routes to one number, regression guards on
figures the article does not print, arithmetic on a displayed quantity with no
model function behind it, and the comparisons against `wheel_sim.py` -- whose
simulated barrier is a different object from `model.py`'s static one.

The structural check at the end is the strongest one in the file: run the whole
machinery in the Q-world and the economic excess return must vanish up to the
dividend-withholding leak, because no strategy beats the risk-free rate under
the pricing measure. It exercises the entry law, the depth walk, the occupation
measure, premium pricing and the capital definition simultaneously.

Stdlib only (Python 3.8+).
"""

import argparse
from math import exp, log, pi, sqrt

import model
from model import (BETA, Config, N, buy_hold_excess, criteria, depth_census,
                   economics, entry_law, debit_growth, equity_required,
                   first_passage_prob, leverage, levered_excess,
                   liquidation_barrier, liquidation_prob, max_leverage,
                   max_debit_growth, max_sustainable_draw,
                   occupation, overshoot_wald, pmap, saturation, stationary,
                   stationary_converged, sticky_dividend_yield, strike,
                   survival_utilization, time_to_fraction, time_to_inventory,
                   trapped_fraction, trapped_fraction_walk, trapped_zero_depth)
from model import bs_call, phi

FAILURES = []


def check(label, got, expected, tol):
    ok = abs(got - expected) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got:.4f}, expected ~{expected}")
    if not ok:
        FAILURES.append(label)


# ----------------------------------------------------------------------
# pmap workers.  Each takes one independent configuration and returns only
# what its checks need; they must stay module-level to survive pickling.
# ----------------------------------------------------------------------

def _occ_job(job):
    """The full occupation measure, for checks that read the survival curve."""
    cfg, measure = job
    return occupation(cfg, measure)


def _stationary_job(job):
    """A Richardson-extrapolated stationary solve (two grids, run serially)."""
    cfg, measure = job
    occ = stationary(cfg, measure)
    return occ, economics(cfg, measure, occ), time_to_fraction(cfg, occ, 0.9)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--full", action="store_true",
                    help="also check the far-grid stationary figures (slow)")
    args = ap.parse_args()

    STD = Config(p_star=0.20, label="Standard")
    CON = Config(p_star=0.10, label="Conservative")

    # The three base walks the rest of the file reads: independent, so they go
    # out together rather than one after another.
    occ_p, occ_q, occ_c, occ_cq = pmap(
        _occ_job, [(STD, "P"), (STD, "Q"), (CON, "P"), (CON, "Q")])

    # Derived quantities the structural blocks below read.  They are hoisted
    # here rather than left where they were first needed because the
    # per-section assertion blocks that used to define them now live in
    # `code/examples/` -- this file keeps the setup and drops the duplicated
    # checks, so anything consumed further down has to be defined above the
    # first heading.
    crit_p, crit_q = criteria(STD, "P"), criteria(STD, "Q")
    nu_p = crit_p["nu"]
    e30 = economics(STD, "P", occ_p, horizon=30.0)
    # The extrapolated pair, hoisted for the same reason as the rest of this
    # block.  Capacity needs it because the transient inverse runs centuries
    # into the tail, where a single grid's O(h^2) bias has accumulated; section
    # 07's Wald bracket needs it because the identity is only as exact as the
    # E[W] put into it, and the near grid reads 2.05 against 2.10.  Solved here
    # rather than under --full, and --full reuses it.
    (far_p, f, t90), (far_q, g, _) = pmap(
        _stationary_job, [(STD, "P"), (STD, "Q")])

    # ------------------------------------------------------------------
    # Sections 05 to 08 are now checked by `code/examples/`, a module per
    # numbered formula: the entry law and the strike dial, the depth walk and
    # its two tables, the survival curve and E[W], Little's law and the depth
    # census.  `python -m examples --list` enumerates them.  What survives
    # here is only what no module can own.
    #
    # One comparison is checked nowhere at all, and should not be mistaken for
    # covered: section 05's live-account figures -- the 7.7% realized rate, the
    # 10.9% revealed dial, the 5.5% median moneyness -- are measured by
    # `model_vs_live.py` against statement data, and nothing reproduces them
    # (INF-2).
    print("--- Sections 05-08: what no example module can own ---")
    # Arithmetic on a displayed quantity, with no model function behind it and
    # no reason to add one: section 06's "a 30% fall leaves the yield 43%
    # higher", and section 08's e^0.5, the capital a lot half a log-unit down
    # ties up per share.
    check("yield lift from a 30% fall with the payout unchanged",
          1 / 0.70 - 1, 0.43, 0.005)
    check("capital per share of a lot 50% down in log terms", exp(0.5), 1.65, 0.01)
    # Section 05's caveat on exercise style.  A dividend-driven early call
    # exercise pays when the call's remaining TIME value falls below the
    # dividend about to be paid, so the threshold is the S/K at which
    # C - (S - K) = delta/4 * S.  The point the section makes is that the
    # threshold at the START of a call period is the whole of one period's
    # typical move -- and the lot begins that period BELOW its strike, so the
    # required move is that plus the depth it starts at.
    #
    # These were 6.8/4.9/3.1/1.3/0.3 when II-25 raised them, computed with a
    # ZERO dividend yield inside Black-Scholes while assuming the stock pays
    # 2.5%.  Pricing a payer as a non-payer overstates the call and so its
    # time value, which is why every figure ran high.
    def _early_call_threshold(days):
        tau, lo, hi = days / 365, 1.0, 3.0
        for _ in range(200):
            mid = (lo + hi) / 2
            tv = bs_call(mid, 1.0, tau, STD.sigma, STD.r, STD.delta) - (mid - 1)
            lo, hi = ((lo, mid) if tv < STD.delta / 4 * mid else (mid, hi))
        return (lo + hi) / 2 - 1

    for days, want in ((28, 0.055), (21, 0.041), (14, 0.028),
                       (7, 0.012), (3, 0.002)):
        check(f"early call exercise needs the stock this far above the strike, "
              f"{days}d out", _early_call_threshold(days), want, 0.0007)
    # The comparison the section draws: at the start of a period the threshold
    # IS one period's standard deviation, and the lot starts below the strike.
    check("...against one call period's typical move, sigma*sqrt(tau_c)",
          STD.sigma * sqrt(STD.tau_c), 0.055, 0.0007)
    # An ex-dividend date falls inside a four-week call about 4 times in 13.
    check("chance an ex-dividend date lands inside one call period",
          STD.tau_c / 0.25, 4 / 13, 0.01)
    # An invariant of the occupation walk rather than a quoted figure: the exit
    # mass sums to one whenever nu > 0.  Worth keeping beside
    # `examples/holding_trapped.py`, which reaches the same conclusion by a
    # closed form -- two independent routes to one answer.
    check("every lot eventually exits when nu > 0", occ_p["P[exit]"], 1.0, 0.002)
    # Section 07 replaced a one-sided "9% below" with a bracket, and the claim
    # that makes it worth printing is that BOTH ends are published constants and
    # the exact answer lies between them.  A module case can pin the three
    # numbers; only this can assert the ordering that is the point of them.
    wald = overshoot_wald(STD, "P", far_p)
    EW = far_p["E[J]"] * STD.tau_c
    check("Wald's identity recovers E[W] from the overshoot it implies",
          (economics(STD, "P", far_p)["E[x0]"] + wald["tax"]) / far_p["nu"],
          EW, 1e-12)
    if wald["E[T]_far"] < EW < wald["E[T]_near"]:
        print("PASS  E[W] sits inside the two published overshoot constants "
              f"({wald['E[T]_far']:.2f} < {EW:.2f} < {wald['E[T]_near']:.2f})")
    else:
        FAILURES.append("E[W] outside the far/near overshoot bracket")
    check("the grid charges more than beta says, by the barrier-distance gap",
          wald["overshoot"] / BETA, 1.144, 0.01)
    # BETA is asserted nowhere else, and section 07 now tells a reader that the
    # -0.5824 printed in the origin paper is a slip in its arithmetic rather
    # than a rival constant.  Chernoff (1965) Corollary 1(b) gives the number as
    # a Wiener-Hopf integral, even in lambda, which is a route to it independent
    # of the zeta closed form:
    #     -(1/2pi) int_{-inf}^{inf} lam^-2 log[ lam^2 / (2(1-e^(-lam^2/2))) ]
    # The integrand tends to 1/4 at the origin (both parts vanish to second
    # order) and beyond lam = 20 the exponential is dead, leaving a tail that
    # integrates in closed form.
    def _chernoff(lam):
        if lam < 1e-4:
            return 0.25 + lam * lam / 96
        return log(lam * lam / (2 * (1 - exp(-lam * lam / 2)))) / (lam * lam)

    L, n = 20.0, 2000
    h_c = L / n
    quad = sum((4 if i % 2 else 2) * _chernoff(i * h_c) for i in range(1, n))
    quad = (quad + _chernoff(0.0) + _chernoff(L)) * h_c / 3
    quad += (2 * log(L) + 2 - log(2)) / L        # the analytic tail past L
    check("beta as Chernoff's Wiener-Hopf integral, not as a zeta value",
          quad / pi, BETA, 5e-5)
    # Section 08 now says its [0,H] inventory row IS Little's law read over the
    # window -- "nothing is being approximated" -- and that rests on a claim
    # about what economics(horizon=H) computes: that _time_avg_weights gives
    # period j the expected time a lot spends in the window, not an
    # approximation to it.  The window residence has an independent definition,
    #     W(H) = (1/H) * integral_0^H (H - s) * S(s) ds,
    # S being the survival curve, which is the mean of min(W, H-U) for a lot
    # arriving uniformly in the window.  Integrating that on a grid that knows
    # nothing about call periods must reproduce E[I(over [0,H])]/lambda.
    lam_p = e30["lambda"]
    for H in (5.0, 10.0, 30.0):
        surv, steps = occ_p["surv"], 400          # sub-intervals per call period
        acc, ds = 0.0, STD.tau_c / steps
        s_pos = ds / 2
        while s_pos < H:
            j = int(s_pos / STD.tau_c)
            if j >= len(surv):
                break
            acc += (H - s_pos) * surv[j] * ds
            s_pos += ds
        check(f"in-window residence at {H:g}y: quadrature vs E[I]/lambda",
              acc / H,
              economics(STD, "P", occ_p, horizon=H)["I"] / lam_p, 2e-4)
    # A regression guard on a number no section prints, so it has no home in a
    # module: module cases assert what the article claims, and this is not a
    # claim the article makes.
    check("E[I] over 30 years (Standard, Q)",
          economics(STD, "Q", occ_q, horizon=30.0)["I"], 14.49, 0.12)

    # ------------------------------------------------------------------
    # Section 09's ledger, both sweeps, the sticky-dividend fixed point,
    # the trap depth, the Conservative regime and the collateral footnote
    # are all checked by `code/examples/returns_*.py`; section 10's two
    # boundaries and the tail exponent by `examples/stability_*.py`.
    # What is left here is what a module cannot own.
    print("--- Sections 09-10: what no example module can own ---")
    # The correction has no stationary value: held lot-time thins like the
    # holding-time tail while the yield inflates faster.
    check("yield inflation rate sigma^2/2", STD.sigma**2 / 2, 0.0200, 0.0001)
    check("held-time thinning rate nu^2/(2 sigma^2)",
          nu_p**2 / (2 * STD.sigma**2), 0.0078, 0.0002)
    # A buy-and-hold anchor stands the whole horizon, so it inflates by more.
    a = STD.sigma**2 * 30.0 / 2
    check("buy-and-hold inflation factor at 30y", (exp(a) - 1) / a, 1.370, 0.002)
    # The rejected per-lot version, kept as a check that it is the cost-basis
    # capital in disguise -- an unfunded +1.24pp, which is why it is wrong.
    naive = e30["dividends"] * ((e30["capital"] - STD.gamma_p * e30["k"])
                                / e30["I"] - 1)
    check("unfunded return from per-lot dividend anchoring (rejected)",
          naive / e30["mv_capital"], 0.0122, 0.0003)
    # Section 09 sets its own 45bp-per-volatility-point slope beside
    # Merton-Scholes-Gladstein's, and theirs has to be converted first: their
    # axis is *percent of model premium*, ours is volatility points.  The
    # bridge is vega -- one point of quoted volatility adds vega*0.01 to the
    # premium, so 10% of premium is 0.10*P/(vega*0.01) points.
    #
    # Every input is off the papers.  1978 fn. 11: the at-the-money six-month
    # CALL runs ~10% of stock price on the 136-stock sample.  1982 p. 8: the
    # average put/call price ratio is 84.9% at E/S = 1.  1978 fn. 14: the
    # semiannual dividend yield is 1.5%.  Their measured slopes are +100bp of
    # semiannual return per 10% of premium on the 1978 calls (Table 8) and
    # +80bp on the 1982 puts (Table 7).
    #
    # The one input NOT off the papers is the short rate, so the check runs
    # the whole plausible 1963-77 range and asserts the answer is insensitive
    # to it.  r = 6% is the internally consistent reading -- it is where their
    # observed put/call ratio reproduces put-call parity -- and it implies a
    # volatility of 33.6%, which the item had guessed at 30%.
    print("--- Section 09: converting MSG's premium axis to volatility points ---")
    T_msg, DIV = 0.5, 0.03
    call_px, put_px = 0.10, 0.10 * 0.849

    def _msg_sigma(r):
        lo, hi = 0.01, 3.0
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = ((mid, hi) if bs_call(1.0, 1.0, T_msg, mid, r, DIV)
                      < call_px else (lo, mid))
        return (lo + hi) / 2

    def _msg_vega(sigma, r):
        d1 = ((r - DIV + sigma**2 / 2) * T_msg) / (sigma * sqrt(T_msg))
        return exp(-DIV * T_msg) * phi(d1) * sqrt(T_msg)

    for r, sig_lo, sig_hi in ((0.05, 0.34, 0.35), (0.06, 0.33, 0.34),
                              (0.08, 0.31, 0.33)):
        s = _msg_sigma(r)
        check(f"MSG's 10%-of-spot ATM call implies sigma at r = {r:.0%}",
              s, (sig_lo + sig_hi) / 2, (sig_hi - sig_lo) / 2)
        v = _msg_vega(s, r)
        # Their slope, annualised by doubling the semiannual figure, per point.
        check(f"...1982 put slope, bp per vol point per year at r = {r:.0%}",
              2 * 0.0080 / (0.10 * put_px / (v * 0.01)), 0.0052, 0.0004)
        check(f"...1978 call slope, same units at r = {r:.0%}",
              2 * 0.0100 / (0.10 * call_px / (v * 0.01)), 0.0055, 0.0004)
    # Their observed put/call ratio reproduces parity at r = 6%, which is what
    # licenses quoting that column rather than assuming a rate.
    check("MSG's observed put price against put-call parity at r = 6%",
          call_px - exp(-DIV * T_msg) + exp(-0.06 * T_msg), put_px, 0.001)

    # Section 09's leverage result rests on two identities in L, and
    # `examples/returns_leverage.py` can only pin the article's own points on
    # them.  Both are checked here across the whole axis instead.
    #
    # Neutrality: the spread at which leverage is exactly neutral is the
    # strategy's own excess return, at EVERY leverage.  A single case cannot
    # show "at every L", which is the whole content of the claim.
    ex30 = e30["econ_excess"]
    for L in (1.0, 1.0861, 1.1349, 1.5, 2.0, 4.0, 10.0):
        check(f"leverage is neutral at L = {L:g} when the spread is the excess",
              levered_excess(ex30, L, ex30), ex30, 1e-12)
    check("an unlevered book pays no spread, whatever the rate",
          levered_excess(ex30, 1.0, 0.03), ex30, 1e-12)
    # And the verdict is invariant to financing: the same L and the same spread
    # apply to a levered buy-and-hold, so the gap merely scales by L.  If this
    # ever fails, the wheel-versus-stock headline has become a claim about
    # borrowing.
    bh30 = buy_hold_excess(STD, "P") * e30["I"] / e30["mv_capital"]
    for L in (1.0861, 1.1349, 1.1557, 2.0):
        for spread in (0.0, 0.015, 0.03):
            gap = levered_excess(ex30, L, spread) - levered_excess(bh30, L, spread)
            check(f"wheel - buy-and-hold at L = {L:.4f}, spread {spread:.1%},"
                  f" scales by L", gap / L - (ex30 - bh30), 0.0, 1e-15)
    # The equity-required row against the capital it is a fraction of: shares
    # paid for in full require the whole of Track B, which is the row's
    # definition checked from the boundary rather than restated.
    check("equity required at gamma_s = 1 is Track B itself",
          equity_required(Config(gamma_s=1.0), e30) - e30["mv_capital"],
          0.0, 1e-12)

    # ------------------------------------------------------------------
    print("--- Section 10: stability ---")
    print(f"      P-world: count {'stable' if crit_p['count_ok'] else 'UNSTABLE'}, "
          f"capital {'stable' if crit_p['capital_ok'] else 'UNSTABLE'}")
    print(f"      Q-world: count {'stable' if crit_q['count_ok'] else 'UNSTABLE'}, "
          f"capital {'stable' if crit_q['capital_ok'] else 'UNSTABLE'}")
    if crit_p["capital_ok"] and not crit_q["capital_ok"]:
        print("PASS  the two measures disagree on capital stability (the "
              "article's sharpest comparison)")
    else:
        FAILURES.append("measure disagreement on capital stability")
    hi_vol = Config(sigma=0.40)
    # The trapped fraction, three ways.  This block replaced a check that
    # integrated eq:trapped's own integrand against the entry density and
    # called the agreement a cross-check: it tested the truncated-normal
    # expectation and could not see the approximation being made, which is
    # the one thing here that is wrong (TODO II-29).
    #
    # First, the closed form against the walk it is an approximation of.  The
    # gap is not noise and is not allowed to drift: BETA is a b -> infinity
    # constant applied at b = 0.28 of a step, and it reads low by 8%.
    walk = trapped_fraction_walk(hi_vol, "P")
    cf = trapped_fraction(hi_vol, "P")
    check("trapped fraction: the walk itself (section 07 quotes this)",
          walk["trapped"], 0.04436, 5e-5)
    check("  ...and eq:trapped's closed form runs this far below it",
          1 - cf / walk["trapped"], 0.078, 0.004)
    check("  the walk's own [lower, upper] bracket has closed",
          walk["bracket"], 0.0, 2e-6)
    # Second, the zero-depth end, where the answer is published rather than
    # measured -- and two independent series land on it.  Janssen & van
    # Leeuwaarden's theorem 1 is a zeta expansion; Spitzer's identity is a
    # sum over P(S_n > 0) that knows nothing about zeta functions.  Agreement
    # to ten digits is a check on the coefficients ZETA_HALF as much as on the
    # theorem, since a mistyped constant would show up here and nowhere else.
    m_h, s_h = hi_vol.world("P")
    theta = abs(m_h - s_h**2 / 2) * sqrt(hi_vol.tau_c) / s_h
    spitzer, n = 0.0, 1
    while True:                       # P(M = 0) = exp(-sum_n P(S_n > 0)/n)
        term = N(-theta * sqrt(n)) / n
        spitzer += term
        if term < 1e-14 and n > 100:
            break
        n += 1
    check("P(M = 0): Janssen & van Leeuwaarden's series vs Spitzer's",
          trapped_zero_depth(hi_vol, "P"), exp(-spitzer), 1e-9)
    check("  ...and eq:trapped runs 17.6% low there, its worst case",
          1 - trapped_fraction(hi_vol, "P", zero_depth=True)
          / trapped_zero_depth(hi_vol, "P"), 0.176, 0.002)
    # Third, the walk against that published endpoint: same machinery as the
    # figure above, run at a point where the exact answer is known, which is
    # what makes it evidence for the figure rather than for itself.  Coarser
    # grids and a linear extrapolation, since the entry point is the lowest
    # cell and so moves with h -- hence the looser tolerance.
    check("  the walk reproduces that endpoint from a standing start",
          trapped_fraction_walk(hi_vol, "P", h=0.04, zero_depth=True)["trapped"],
          trapped_zero_depth(hi_vol, "P"), 0.005)

    # ------------------------------------------------------------------
    # Line endings, because a whole-file rewrite that silently flips them
    # produces a diff in which every line has changed and the real edit is
    # invisible inside it.  That happened twice on 2026-08-05, both times from
    # reading a section with universal newlines and writing it back with
    # newline="" -- the Edit tooling preserves endings and an ad-hoc rewrite
    # does not.
    #
    # The repo is genuinely mixed and has been since before this check: the
    # body sections are CRLF and the earliest files and stubs are LF, with no
    # .gitattributes and core.autocrlf off.  That is nobody's decision to
    # relitigate here, so this does NOT demand one convention.  What it catches
    # is a file *flipping*, which is the actual failure -- so LF_SECTIONS is a
    # baseline, and a new section is expected to match the body.
    print("--- Structural: section files keep their line endings ---")
    import glob as _glob
    import os as _os
    LF_SECTIONS = {"00-notation.md", "01-abstract.md", "02-introduction.md",
                   "03-prior-work.md", "15-outlook.md", "98-bibliography.md"}
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _flipped = []
    for _p in sorted(_glob.glob(_os.path.join(_os.path.dirname(_here),
                                              "sections", "*.md"))):
        _name = _os.path.basename(_p)
        with open(_p, "rb") as _fh:
            _is_crlf = b"\r\n" in _fh.read()
        if _is_crlf is (_name in LF_SECTIONS):
            _flipped.append(f"{_name} is now {'CRLF' if _is_crlf else 'LF'}")
    check("no section file has flipped its line endings", not _flipped, True, 0)
    for _msg in _flipped:
        print(f"      {_msg}")

    # ------------------------------------------------------------------
    # Section 09's detour declines to compare its betas with BXM's published
    # pair, and quotes three numbers to say how far apart the estimators are.
    # `bxm_beta.py` measures them by replicating BXM's own construction; this
    # pins what the prose quotes.  400 paths reproduces the script's 4000 to
    # three decimals, so the cheap run is the one wired in here.
    print("--- Section 09: our split beta against BXM's estimator ---")
    import bxm_beta
    kw = dict(C=STD, paths=400)
    up_aligned, _ = bxm_beta.measure(0.0, False, **kw)
    up_cal, dn_cal = bxm_beta.measure(0.0, True, **kw)
    up_both, _ = bxm_beta.measure(0.02, True, **kw)
    # Analytic, not simulated: an at-the-money call gives away the whole of
    # every rise, so the up-side payoff is flat and no slope exists.  If this
    # ever drifts off zero the replication has stopped being at the money.
    check("aligned at-the-money buy-write has an up-beta of exactly zero",
          up_aligned, 0.0, 0.004)
    check("...measuring off the roll instead lifts it", up_cal, 0.165, 0.010)
    check("...and a strike above spot takes it further", up_both, 0.289, 0.012)
    # The point of the detour: both mechanisms together still fall well short.
    check("...both together still fall short of BXM's published 0.63",
          up_both < 0.45, True, 0)
    # Section 09's own inventory down-beta is exactly 1; a buy-write's is 1.02
    # because its return is on cost (share less premium), not on the share.
    check("a buy-write's down-beta exceeds 1 by its own premium",
          dn_cal < 1.0, True, 0)

    # ------------------------------------------------------------------
    # The example harness turns a command line into a Config, and it must not
    # pin a field that __post_init__ derives.  `cadence` is declared None and
    # resolved to tau_p; taking the parser's default off a CONSTRUCTED Config
    # therefore handed back 1/52 and made every `--tau-p` case silently wrong
    # (INF-6).  `holding_trapped.py` carries the behavioural case; this checks
    # the mechanism, so a new derived field cannot reopen the same trap
    # somewhere no Case happens to look.
    print("--- Structural: the example harness does not pin derived fields ---")
    from dataclasses import MISSING, fields
    from examples._harness import build_parser, params_from
    from examples import holding_trapped as _ht
    _defaults = vars(build_parser(_ht).parse_args([]))
    # `fld`, not `f`: main() already binds `f` to a far-grid result at the top
    # and reads it again several hundred lines below.
    for fld in fields(Config):
        if not fld.init or fld.name == "label":
            continue
        check(f"parser default for --{fld.name.replace('_', '-')} is declared",
              _defaults[fld.name] == fld.default, True, 0)
        check(f"...and {fld.name} declares one at all",
              fld.default is not MISSING, True, 0)
    # The whole point, stated as one assertion: no flags must reproduce the
    # model's own defaults exactly, or every headline figure is off by whatever
    # the harness pinned.
    check("an empty command line reproduces Config()",
          params_from(_ht, "")["cfg"] == Config(), True, 0)
    # And a derived field must follow its parent rather than sit where the
    # reference instance left it.
    for tp, want in ((1 / 52, 1 / 52), (1 / 12, 1 / 12), (0.25, 0.25)):
        check(f"cadence follows --tau-p {tp:.4f}",
              params_from(_ht, f"--tau-p {tp}")["cfg"].cadence, want, 1e-9)
    # An explicit --cadence still wins, which is the behaviour the flag exists
    # for: T > tau_p is a real configuration (a put every month at a weekly
    # tenor), and the fix must not have made the two fields one.
    _c = params_from(_ht, "--tau-p 0.0192308 --cadence 0.25")["cfg"]
    check("an explicit --cadence still overrides tau_p", _c.cadence, 0.25, 1e-9)
    check("...without disturbing tau_p", _c.tau_p, 0.0192308, 1e-9)

    # ------------------------------------------------------------------
    # The convolution has two implementations, and only one of them is the
    # reference: if numpy is installed everything above ran through it, so the
    # stdlib loop it replaced is exercised here on a short walk.
    print("--- Structural: numpy fast path == pure-Python reference ---")
    if model._np is None:
        print("SKIP  numpy not installed; the reference path is the only path")
    else:
        short = dict(j_max=40, min_steps=0)
        fast = occupation(STD, "P", **short)
        try:
            model._np, saved = None, model._np
            ref = occupation(STD, "P", **short)
        finally:
            model._np = saved
        for key in ("E[J]", "E[prem]", "E[basis]", "E[exitcost]", "P[exit]",
                    "q(x0)", "escaped"):
            check(f"{key}: numpy vs. reference (relative)",
                  fast[key] / ref[key] - 1.0, 0.0, 1e-12)
        check("survival curve: largest absolute disagreement",
              max(abs(a - b) for a, b in zip(fast["surv"], ref["surv"])),
              0.0, 1e-14)

    # ------------------------------------------------------------------
    print("--- Structural: no-arbitrage in the Q-world ---")
    for label, cfg, occ in (("Standard", STD, occ_q), ("Conservative", CON, occ_cq)):
        for H in (5.0, 10.0, 30.0):
            x = economics(cfg, "Q", occ, horizon=H)
            resid = x["econ_excess"] + x["leak"] / x["mv_capital"]
            check(f"{label} @ {H:.0f}y: Q-world excess = -(withholding leak)",
                  resid, 0.0, 0.003)

    # ------------------------------------------------------------------
    # Section 11 is unwritten, so the working-capital closed forms sit with
    # the structural checks rather than under a section heading: what is
    # verified here is that the formulas agree with each other and with the
    # exponent the census already uses, not that some paragraph is right.
    print("--- Structural: the liquidation barrier and survival ---")
    # The defaults are the unconstrained operator, and that is II-3's
    # regression guard stated as a property rather than as a diff: shares paid
    # for in full, so no leverage is available, so nothing is ever sold out.
    check("default gamma_s is fully paid", STD.gamma_s, 1.0, 0.0)
    check("default leverage at the stopping rule u*", leverage(STD), 1.0, 0.0)
    check("an unlevered book is never liquidated", liquidation_prob(STD, "P"),
          0.0, 0.0)
    check("...nor over any finite horizon",
          liquidation_prob(STD, "P", horizon=30.0), 0.0, 0.0)
    # The barrier recovers the broker's own ceiling rather than assuming it:
    # at L = 1/gamma_s the position violates the requirement on day one.
    for gs in (0.50, 0.25, 0.15):
        check(f"f* = 1 at the broker's ceiling L = 1/{gs:g}",
              liquidation_barrier(1.0 / gs, gs), 1.0, 1e-12)
    check("f* = 0 for an unlevered book", liquidation_barrier(1.0, 0.25), 0.0, 0.0)

    # L_max over the gamma_s grid, on the unbounded horizon.  The hand figures
    # from the design discussion were 1.02 at eps = 1% and 1.14 at eps = 10%
    # for gamma_s = 0.25: the first is confirmed, the second is 1.13.
    check("survival exponent is the census exponent, not a new constant",
          crit_p["tail_exponent"], 1.25, 0.01)
    LMAX = [(1.00, 1.0000, 1.0000), (0.50, 1.0127, 1.0861),
            (0.25, 1.0192, 1.1349), (0.15, 1.0218, 1.1557)]
    print(f"      {'gamma_s':>8} {'ceiling':>8} {'L(eps=1%)':>10}"
          f" {'L(eps=10%)':>11} {'% of ceiling':>13}")
    for gs, l1, l10 in LMAX:
        Cg = Config(p_star=0.20, gamma_s=gs)
        got1, got10 = max_leverage(Cg, "P", 0.01), max_leverage(Cg, "P", 0.10)
        print(f"      {gs:>8.2f} {1 / gs:>8.2f} {got1:>10.4f} {got10:>11.4f}"
              f" {got10 * gs:>12.1%}")
        check(f"L_max at gamma_s = {gs:.2f}, eps = 1%", got1, l1, 0.0005)
        check(f"L_max at gamma_s = {gs:.2f}, eps = 10%", got10, l10, 0.0005)
        for eps, L in ((0.01, got1), (0.10, got10)):
            if L > 1.0:                     # gamma_s = 1 has nothing to invert
                check(f"round trip at gamma_s = {gs:.2f}: P at L_max = eps",
                      liquidation_prob(Cg, "P", L), eps, 1e-12)

    # What that leverage actually costs, and over what horizon.  The barrier
    # is far away -- an unbounded horizon is what makes a 10% risk of reaching
    # it -- so the finite-horizon form is the one an operator lives under.
    G = Config(p_star=0.20, gamma_s=0.25)
    L10 = max_leverage(G, "P", 0.10)
    f10 = liquidation_barrier(L10, G.gamma_s)
    check("barrier at the 10%-tolerance leverage", f10, 0.15849, 0.00005)
    check("...which is a drawdown of", 1 - f10, 0.84151, 0.00005)
    prev = -1.0
    for H, want, tol in [(5.0, 0.0000116, 1e-7), (10.0, 0.0010614, 1e-6),
                         (30.0, 0.0249255, 1e-6), (100.0, 0.0778552, 1e-6),
                         (1000.0, 0.0999984, 1e-6)]:
        got = liquidation_prob(G, "P", L10, horizon=H)
        check(f"P(liquidated by {H:.0f}y) at L = {L10:.4f}", got, want, tol)
        if got <= prev:
            FAILURES.append(f"first passage not monotone in the horizon at {H}y")
        prev = got
    # The unit test the two forms owe each other: the finite-horizon first
    # passage must collapse onto f*^theta as the horizon grows.
    nu_p, th_p = crit_p["nu"], crit_p["tail_exponent"]
    a10 = -log(f10)
    check("T -> infinity collapse of the finite-horizon first passage",
          first_passage_prob(a10, nu_p, STD.sigma, 1e6)
          / first_passage_prob(a10, nu_p, STD.sigma) - 1.0, 0.0, 1e-12)
    check("and that limit is f*^theta", f10 ** th_p, 0.10, 1e-9)

    # The Q-world matched pair.  At theta_Q = 0.25 the same book is priced as
    # one that gets sold out: the leverage carrying a 10% real-world risk
    # carries 63% under the pricing measure, alongside section 10's "the
    # market prices this stock as one whose inventory never clears".
    check("Q-world liquidation probability at the P-world's L_max",
          liquidation_prob(G, "Q", L10), 0.63096, 0.00005)
    check("Q-world liquidation probability at 30y",
          liquidation_prob(G, "Q", L10, horizon=30.0), 0.07312, 0.00005)
    check("Q-world L_max at eps = 10% is no leverage at all",
          max_leverage(G, "Q", 0.10), 1.0001, 0.0002)
    # The reflection term needs log N(z) in a tail where NormalDist.cdf is
    # exactly zero (below z = -8.3, erf having saturated), so the asymptotic
    # has to take over while the two still agree.  It does, at -7; the visible
    # disagreement further out is the CDF losing digits to cancellation, not
    # the series.  Getting this threshold wrong made short horizons raise.
    for z in (-3.0, -5.0, -6.9, -7.0):
        check(f"log N({z}) across the asymptotic crossover",
              model._log_ncdf(z) - log(N(z)), 0.0, 2e-5)
    for H in (1e-9, 1e-3, 0.1, 1.0):
        p = first_passage_prob(a10, nu_p, STD.sigma, H)
        if not 0.0 <= p <= 1e-12:
            FAILURES.append(f"first passage at H = {H:g} is not a small probability")
    print(f"PASS  short horizons stay finite and tiny "
          f"(H = 1e-9 .. 1y at a = {a10:.3f})")

    # The cash policy enters as a displacement of nu, so the whole survival
    # block above is the g = 0 case: an operator who services the interest and
    # withdraws the rest.  The two policies that pin g exactly bracket it.
    D_ex, y_ex = 1.56, 0.772          # a saturated account's debit and income
    check("draw = None holds the debit flat", debit_growth(STD, D_ex, y_ex),
          0.0, 0.0)
    hold = Config(p_star=0.20, gamma_s=0.25, draw=y_ex - STD.r_b * D_ex)
    check("...and so does the draw that policy names",
          debit_growth(hold, D_ex, y_ex), 0.0, 1e-15)
    allout = Config(p_star=0.20, gamma_s=0.25, draw=y_ex)
    check("withdrawing income and accruing the interest gives g = r_b",
          debit_growth(allout, D_ex, y_ex), STD.r, 1e-15)
    check("survival exponent at g = 0 is the census exponent",
          2 * model._drift(STD, "P", 0.0)[0] / STD.sigma**2, th_p, 1e-12)
    # nu - g <= 0 is the third boundary: the debt outgrows the price's median.
    check("the drift the debit-to-value ratio sees, at g = r_b",
          model._drift(STD, "P", STD.r_b)[0], -0.025, 1e-12)
    check("liquidation is certain once the debt outgrows the price",
          liquidation_prob(G, "P", L10, g=STD.r_b), 1.0, 0.0)
    check("...and no leverage survives it", max_leverage(G, "P", 0.10, g=STD.r_b),
          1.0, 0.0)
    check("the boundary sits at g = nu", nu_p, 0.025, 1e-12)
    # And it is independent of the other two, which is what earns it a place
    # beside them in section 10 rather than a footnote: at g = r_b the account
    # fails on a stock whose own two criteria are untouched by the financing.
    c_g = criteria(STD, "P", g=STD.r_b)
    if not (c_g["count_ok"] and c_g["capital_ok"] and not c_g["account_ok"]):
        FAILURES.append("the account criterion is not independent of the other two")
    print("PASS  the account criterion fails where both of the stock's hold")
    # A deposit runs it the other way: g < 0 buys leverage back.
    if not (liquidation_prob(G, "P", L10, g=-0.01)
            < liquidation_prob(G, "P", L10)
            < liquidation_prob(G, "P", L10, g=0.01)):
        FAILURES.append("liquidation probability is not monotone in g")
    print(f"PASS  deposits lower and withdrawals raise the risk "
          f"({liquidation_prob(G,'P',L10,g=-0.01):.4f} < "
          f"{liquidation_prob(G,'P',L10):.4f} < "
          f"{liquidation_prob(G,'P',L10,g=0.01):.4f} at g = -1%, 0, +1%)")

    # ------------------------------------------------------------------
    print("--- Structural: capacity, saturation and the sustainable draw ---")
    G25 = Config(p_star=0.20, gamma_s=0.25)
    I_inf, lam = f["I"], f["lambda"]
    L_max = max_leverage(G25, "P", 0.10)
    A_star = I_inf / L_max
    check("A*, the equity a wheel needs at portfolio margin (eps = 10%)",
          A_star, 19.23, 0.02)
    check("...unlevered, which is just E[I(inf)]",
          I_inf / max_leverage(STD, "P", 0.10), 21.82, 0.02)
    check("...and at the most aggressive margin available",
          I_inf / max_leverage(Config(p_star=0.20, gamma_s=0.15), "P", 0.10),
          18.88, 0.02)
    check("the stopping rule implementing a 10% tolerance",
          survival_utilization(G25, "P", 0.10), 0.25 * L_max, 1e-15)

    # The transient inverse.  Both entry points must agree exactly, since a
    # capacity of frac*E[I(inf)] lots IS a fraction frac of the stationary
    # inventory -- the two differ only in what units the caller thinks in.
    check("time_to_inventory and time_to_fraction are one map",
          time_to_inventory(STD, far_p, lam, 0.9 * I_inf)
          - time_to_fraction(STD, far_p, 0.9), 0.0, 1e-9)
    # Interpolating inside the call period: the answer must land in the period
    # the staircase named, and strictly below it (the staircase rounds up).
    worst, prev_t = 0.0, -1.0
    for cap in (1.0, 5.0, 11.4, 13.15, 17.02, 21.5):
        t = time_to_inventory(STD, far_p, lam, cap)
        # what the map returned before interpolation: the right-hand end of
        # whichever call period the target fell in.
        acc, step = 0.0, float("inf")
        for j, S in enumerate(far_p["surv"]):
            acc += S
            if acc >= cap / (lam * STD.tau_c):
                step = (j + 1) * STD.tau_c
                break
        if not t <= step:
            FAILURES.append(f"interpolated T_sat above its own period at {cap}")
        if t <= prev_t:
            FAILURES.append(f"T_sat is not increasing in capacity at {cap}")
        prev_t, worst = t, max(worst, step - t)
    print(f"PASS  interpolation stays inside its call period "
          f"(worst {worst * 365:.1f} days of {STD.tau_c * 365:.0f})")
    check("...and it barely moves the 90%-of-stationary figure", t90, 90.4, 0.1)

    # Throughput retention is A/A* exactly, and the stopping rule binds --
    # realized leverage IS L_max -- everywhere below A*.  Above it the account
    # never fills, so capacity stops mattering and leverage falls away.
    for frac in (0.05, 0.30, 0.60, 0.99):
        s = saturation(G25, "P", far_p, 0.10, equity=frac * A_star, econ=f)
        if abs(s["throughput"] - frac) > 1e-12 or abs(s["L"] - L_max) > 1e-12:
            FAILURES.append(f"throughput/leverage off at A = {frac}*A*")
    print("PASS  below A*: throughput = A/A* and realized leverage = L_max")
    sat_star = saturation(G25, "P", far_p, 0.10, equity=A_star, econ=f)
    check("at A* the account fills exactly, and never saturates",
          sat_star["throughput"], 1.0, 1e-12)
    if sat_star["T_sat"] != float("inf"):
        FAILURES.append("T_sat is finite at A*")
    check("just below A* it does saturate, but only after centuries",
          saturation(G25, "P", far_p, 0.10, equity=0.99 * A_star,
                     econ=f)["T_sat"], 270.0, 5.0)

    # The unconstrained limit, which is II-3's regression guard carried into
    # the capacity block: unlimited equity never blocks, never borrows, and
    # earns exactly the risk-free rate on the equity it is not using.
    inf_sat = saturation(STD, "P", far_p, 0.10, equity=float("inf"), econ=f)
    check("unlimited equity: full throughput", inf_sat["throughput"], 1.0, 0.0)
    check("...no debit", inf_sat["debit"], 0.0, 0.0)
    check("...and excess return on equity of zero (it all sits in cash)",
          inf_sat["roe_excess"], 0.0, 0.0)
    if inf_sat["T_sat"] != float("inf"):
        FAILURES.append("an account of unlimited equity saturates")
    full = saturation(STD, "P", far_p, 0.10, equity=10.0, econ=f)
    check("fully paid shares (the default gamma_s): capacity is the equity",
          full["capacity"], 10.0, 1e-12)
    check("...and A* is the stationary inventory itself", full["A*"], I_inf, 1e-12)

    # The gap between this block's shares-only excess and economics()'s Track B
    # excess is exactly the put collateral, deliberately excluded from capacity,
    # from the barrier and from the financing ledger alike.
    check("the excluded put collateral, as a formula",
          full["econ_excess_shares"] - f["econ_excess"],
          f["econ_pnl"] * (f["mv_capital"] - I_inf) / (I_inf * f["mv_capital"]),
          1e-15)

    # The draw.  g_max inverts the same equation as L_max, in the other
    # variable, so at L = L_max(eps) it must return exactly the policy that
    # equation was solved under: g = 0, the operator who services the interest
    # and withdraws the rest.  That is a tautology and it is the point -- the
    # draw axis has no slack wherever the stopping rule binds.
    check("g_max at the survivable leverage is the interest-servicing policy",
          max_debit_growth(G25, "P", L_max, 0.10), 0.0, 1e-15)
    for L in (1.05, 1.1349, 1.25, 1.5, 2.0):
        gm = max_debit_growth(G25, "P", L, 0.10)
        if abs(liquidation_prob(G25, "P", L, g=gm) - 0.10) > 1e-12:
            FAILURES.append(f"g_max round trip fails at L = {L}")
        D, y = (L - 1.0) * 11.59, 0.6095
        draw = max_sustainable_draw(G25, "P", L, 0.10, y, D)
        if abs(debit_growth(Config(p_star=0.20, gamma_s=0.25, draw=draw),
                            D, y) - gm) > 1e-12:
            FAILURES.append(f"draw does not deliver g_max at L = {L}")
    print("PASS  g_max round-trips through the barrier, and the draw delivers it")
    check("an unlevered book may withdraw its income and no more",
          max_sustainable_draw(G25, "P", 1.0, 0.10, 0.6095, 0.0), 0.6095, 0.0)
    # -inf will not go through check(), which subtracts: inf - inf is nan.
    if max_debit_growth(G25, "P", 4.0, 0.10) != float("-inf"):
        FAILURES.append("some draw is sustainable at the broker's ceiling")
    print("PASS  nothing whatever is sustainable at the broker's ceiling "
          "(f* = 1, so g_max = -inf)")
    # The draw at the leverage an untended account drifts to: it is negative,
    # which is a demand for deposits rather than a permission to withdraw, and
    # it happens at a leverage whose reported return on equity is HIGHER.
    L_reach = I_inf / 11.59
    drift = saturation(G25, "P", far_p, 0.10, equity=11.59,
                       L_max=L_reach, econ=f)
    check("...where the sustainable draw is a deposit, per year",
          drift["draw"], -0.248, 0.001)
    check("...while its excess return on equity reads higher, not lower",
          drift["roe_excess"], 0.0315, 0.0005)

    # II-14's constrained no-arbitrage identity, in its analytic half.  Under
    # the pricing measure a blocked, levered wheel must still earn r on equity
    # up to the withholding leak, at every gamma_s and every account size:
    # blocking arrivals creates no arbitrage.  Uniform thinning makes the RATE
    # invariant, so the A-independence below is structural rather than
    # evidential -- what is evidential is the LEVEL, which no part of the
    # capacity block was fitted to.
    ee_q = saturation(STD, "Q", far_q, 0.10, equity=10.0,
                      econ=g)["econ_excess_shares"]
    for gs in (1.00, 0.50, 0.25, 0.15):
        Cg = Config(p_star=0.20, gamma_s=gs)
        for A in (1.0, 10.0, 50.0, 200.0):
            s = saturation(Cg, "Q", far_q, 0.10, equity=A, econ=g)
            if s["L"] > 0 and abs(s["roe_excess"] / s["L"] - ee_q) > 1e-12:
                FAILURES.append(f"Q-world RoE not r + ee*L at gamma_s={gs}, A={A}")
    print("PASS  Q-world return on equity is r + ee*L at every gamma_s and A")
    check("Q-world: a blocked levered wheel earns r less the withholding leak",
          ee_q + STD.delta * STD.withhold
          - STD.r * G25.gamma_p * strike(STD, "Q") / g["I"], 0.0, 0.003)

    # ------------------------------------------------------------------
    # The sensitivity sweep (II-7).  Section 11 is unwritten, so what is
    # pinned here is structural: the one exact identity the sweep contains,
    # the tail converger it needs, and the boundary guard that keeps it from
    # trying to resolve a cell that has no answer.
    print("--- Structural: the sensitivity sweep ---")

    # A* along the CADENCE is an identity, not a measurement: selling puts
    # half as often halves lambda and touches neither the walk nor E[W], so
    # A* halves exactly.  It is checked off the running example's own solve,
    # because reusing far_p for a different cadence is exactly the claim.
    A_star_T = {}
    for weeks in (1, 2, 4):
        CT = Config(p_star=0.20, gamma_s=0.25, cadence=weeks / 52)
        eT = economics(CT, "P", far_p)
        A_star_T[weeks] = saturation(CT, "P", far_p, 0.10, equity=1.0,
                                     econ=eT)["A*"]
        if abs(eT["E[T]"] - f["E[T]"]) > 1e-12:
            FAILURES.append(f"cadence moved E[W] at T = {weeks} weeks")
    for weeks in (2, 4):
        if abs(A_star_T[weeks] * weeks - A_star_T[1]) > 1e-9:
            FAILURES.append(f"A* is not exactly 1/T at T = {weeks} weeks")
    print(f"PASS  A* goes exactly as 1/T along the cadence "
          f"({A_star_T[1]:.2f} / {A_star_T[2]:.2f} / {A_star_T[4]:.2f} lots "
          f"at 1 / 2 / 4 weeks), and E[W] does not move")

    # The article's own stationary figures must not move when the period cap
    # is raised -- the sweep's converger exists for cells far from here, and
    # this says the running example was never one of them.
    check("doubling the period cap leaves the running example's E[J] alone",
          stationary(STD, "P", j_max=16000)["E[J]"] / far_p["E[J]"], 1.0, 1e-4)

    # Both sides of the converger's own verdict, on cheap cells.  A walk that
    # dies inside the cap is converged and never doubles; a cap set far too
    # low is a truncation and must be reported as one rather than averaged in.
    lo_vol = stationary_converged(Config(p_star=0.20, sigma=0.15), "P")
    if not lo_vol["tail_ok"] or lo_vol["tail_gap"] is not None:
        FAILURES.append("the converger doubled a walk that had already died")
    cut = stationary_converged(STD, "P", j_max=1000, j_cap=2000)
    if cut["tail_ok"] or not cut["tail_gap"] > 1e-2:
        FAILURES.append("a truncated tail was reported as converged")
    print(f"PASS  the tail converger calls both cases "
          f"(sigma=15% dies in {lo_vol['steps']} periods; a cap of 2000 is "
          f"still growing at {cut['tail_gap']:.1%} a doubling)")

    # The boundary guard.  sigma = 30% at mu = 7% is nu = 0 exactly, which
    # floating point delivers as 7e-18: theta*x_max > 8 then asks for a grid
    # of 4e18 cells.  The cell must be refused, not attempted.
    edge = model._sweep_cell(Config(sigma=0.30), "P", 19.23, 0.25, 0.10)
    if edge["resolved"] or not edge["count_ok"]:
        FAILURES.append("the nu = 0 cell was not refused as unresolvable")
    print(f"PASS  the sweep refuses the boundary cell rather than resolving it "
          f"(sigma = 30%, mu = 7%: nu = {edge['nu']:.1e} > 0 by rounding alone)")

    # One pinned cell, at the cheap end of the sweep: a quieter stock needs
    # less than half the equity, and survivable leverage -- which is 1.13 at
    # the running example -- is worth three times as much discount there.
    quiet = model._sweep_cell(Config(sigma=0.15), "P", 19.23, 0.25, 0.10)
    check("A* at sigma = 15%", quiet["A*"], 7.97, 0.02)
    check("...where survivable leverage is much higher", quiet["L_max"],
          1.5340, 0.001)
    check("...and the equity discount leverage buys, against 12% at sigma=20%",
          1 - 1 / quiet["L_max"], 0.348, 0.002)

    # ------------------------------------------------------------------
    # Section 11's own numbers.  The blocks above check that the working-capital
    # formulas agree with each other; this one checks that the PROSE quotes them
    # correctly, which is a different failure mode and the one an article has.
    #
    # What is deliberately absent: every simulated figure section 11 quotes --
    # the ratchet's 3.95% against 1.09%, the four cash policies, the census
    # depths, the thinning table, realized leverage of 0.745 -- comes from
    # `wheel_sim.py --scenario constrained --paths 4000`, which costs minutes
    # rather than seconds.  The small seeded run below pins the same machinery
    # at a configuration this file can afford; the section's figures are the
    # scenario's and are cited as such in the text.
    print("--- Section 11: the constrained wheel ---")

    # Three of this section's tables are now `examples/account_capacity.py`'s
    # cases and are not repeated here: the A* table down gamma_s (with the
    # income overstatement 1/(gamma_s*L_max) as its `permission_gap` column),
    # the throughput-and-T_sat frontier down account size, and the Q-world
    # A* of 93.65.  Section 08 quotes three of the T_sat figures too, and they
    # are those same cases -- one check, cited from two sections.
    #
    # The draw ladder at A = 11.59.  Every column of it is a case in
    # `examples/account_cash.py`; what is left here is the SHAPE the section
    # claims, which no single case can assert -- the two bottom rows of the
    # table move in opposite directions all the way up the ladder.
    LADDER = (1.0000, 1.0192, 1.1349, 1.2500, 1.5000, 1.8829)
    # The draw is NOT monotone at the bottom of the ladder: from L = 1 to
    # L = 1.0192 it rises by 2bp, because a barrier that far away (f* = 0.025,
    # a 97.5% drawdown) tolerates a debit that GROWS at 1.25%/yr, which is worth
    # slightly more than the interest on the tiny debit costs.  So the claim the
    # section makes -- and the one checked here -- is that the draw is flat to
    # within a few basis points as far as the survivable leverage and collapses
    # past it, while the reported return rises the whole way.
    prev_roe = -1.0
    for L in LADDER:
        s = saturation(G25, "P", far_p, 0.10, equity=11.59, L_max=L, econ=f)
        if s["roe_excess"] <= prev_roe:
            FAILURES.append(f"RoE does not rise with leverage at L = {L}")
        prev_roe = s["roe_excess"]
    flat = [saturation(G25, "P", far_p, 0.10, equity=11.59, L_max=L,
                       econ=f)["draw"] / 11.59 for L in (1.0, 1.0192, 1.1349)]
    if max(flat) - min(flat) > 0.001:
        FAILURES.append("the draw is not flat up to the survivable leverage")
    steep = [saturation(G25, "P", far_p, 0.10, equity=11.59, L_max=L,
                        econ=f)["draw"] / 11.59 for L in (1.1349, 1.25, 1.5, 1.8829)]
    if not all(b < a for a, b in zip(steep, steep[1:])) or steep[-1] >= 0:
        FAILURES.append("the draw does not collapse through zero past L_max")
    print("PASS  up the leverage ladder the reported return rises the whole "
          "way while the cash that may be drawn is flat, then falls through zero")

    # ...and it is flat along the OTHER axis, which is the tautology that makes
    # the frontier's A column constant: g_max solves the equation L_max was
    # solved from, so wherever the stopping rule binds it returns g = 0.
    for A in (1.0, 5.0, 11.59, 19.0):
        s = saturation(G25, "P", far_p, 0.10, equity=A, econ=f)
        check(f"draw is a flat 4.58% of equity at A = {A}", s["draw"] / A,
              0.0458, 0.0002)

    # Two quantities both called sustainable, a factor of two apart.  The draw
    # that keeps the account stationary in SHARES is derived, not tuned.
    check("the draw that holds the account's size, r + excess - m",
          STD.r + f["econ_excess"] - (STD.mu - STD.delta), 0.0212, 0.0005)

    if not I_inf / 11.59 < 1.0 / G25.gamma_s:
        FAILURES.append("the strategy's own demand exceeds the broker's ceiling")

    # The capacity derivative, as an identity rather than an example: capacity
    # in lots is I/gamma_s + C/(gamma_s*S), so it rises as the price falls for a
    # net creditor and falls for a net debtor -- and it meets the book exactly
    # at the maintenance requirement, which is what a margin call is.
    for I_lots, C, S in ((10.0, 3.0, 1.0), (10.0, -3.0, 1.0), (10.0, 0.0, 1.0)):
        for S_new in (0.7, 1.0, 1.4):
            cap_direct = (C + I_lots * S_new) / (0.25 * S_new)
            cap_formula = I_lots / 0.25 + C / (0.25 * S_new)
            if abs(cap_direct - cap_formula) > 1e-12:
                FAILURES.append("the capacity decomposition does not hold")
        rising = ((C + I_lots * 0.7) / (0.25 * 0.7)
                  > (C + I_lots * 1.4) / (0.25 * 1.4))
        if rising != (C > 0):
            FAILURES.append(f"capacity moves the wrong way with the price at C={C}")
    # The margin call is capacity falling to meet the book: I_max = I exactly
    # when equity = gamma_s*I*S.  Solve for the price and it is the barrier.
    I_lots, D = 10.0, 3.0
    S_call = D / (I_lots * (1 - 0.25))
    check("capacity meets the book exactly at the liquidation barrier",
          S_call, liquidation_barrier(I_lots / (I_lots - D), 0.25), 1e-12)
    print("PASS  capacity in lots rises with a falling price for a net creditor "
          "and falls to meet the book for a net debtor")

    # Section 11's sweep figures.  The structural block pinned the cheap cell;
    # these are the ones the prose quotes, including the expensive one that
    # carries the whole "A* is a function of the stock" argument.  Six cells,
    # each its own stationary solve, so they go out together rather than one
    # after another -- serially they are half this script's runtime.
    loud, lo, hi, mu10, mu13, dead, edge = pmap(
        model._sweep_job,
        [(Config(sigma=0.25), "P", 19.23, 0.25, 0.10),
         (Config(sigma=0.195), "P", 19.23, 0.25, 0.10),
         (Config(sigma=0.205), "P", 19.23, 0.25, 0.10),
         (Config(mu=0.10), "P", 19.23, 0.25, 0.10),
         (Config(mu=0.13), "P", 19.23, 0.25, 0.10),
         (Config(mu=0.04), "P", 19.23, 0.25, 0.10),
         (Config(sigma=0.212), "P", 19.23, 0.25, 0.10)])
    check("A* at sigma = 25%", loud["A*"], 48.97, 0.05)
    check("...E[W] there", loud["E[W]"], 4.73, 0.02)
    check("...what an account sized for the running example retains",
          loud["throughput"], 0.393, 0.003)
    check("...and how long it takes to find out", loud["T_sat"], 29.9, 0.3)
    check("...where survivable leverage has collapsed to nearly nothing",
          1 - 1 / loud["L_max"], 0.004, 0.001)
    check("the ratio in equity required between a 20-vol and a 25-vol stock",
          loud["A*"] / A_star, 2.5, 0.05)
    # The elasticity is LOCAL, and the local value is not the secant out to
    # sigma = 25% (4.19), which is what makes the sensitivity worse as
    # volatility rises rather than constant.  Both are quoted, so both are here.
    check("d ln A* / d ln sigma at the running example",
          log(hi["A*"] / lo["A*"]) / log(0.205 / 0.195), 3.46, 0.05)
    check("...against the secant out to sigma = 25%",
          log(loud["A*"] / A_star) / log(0.25 / 0.20), 4.19, 0.05)
    for cell, mu, want in ((mu10, 0.10, 6.81), (mu13, 0.13, 3.74)):
        check(f"A* at mu = {mu:.0%}", cell["A*"], want, 0.02)
    if dead["count_ok"]:
        FAILURES.append("mu = 4% should have no stationary anything")
    print("PASS  at mu = 4% there is no A* at all (nu <= 0: lots never return)")

    # Section 10's reinterpretation of the capital boundary (II-12), which is a
    # figure about section 10 read off section 11's machinery, so it rides along
    # with the sweep batch rather than under the stability heading.  The point
    # of the cell is that theta = 1 is NOT a cliff for an account with a
    # balance: what diverges past the capital boundary is the equity demanded,
    # and the collapse to zero throughput belongs to the COUNT boundary.
    if abs(edge["theta"] - 1.0) > 0.005:
        FAILURES.append("sigma = 21.2% is not the capital boundary")
    check("A* on the capital boundary itself (sigma = 21.2%)",
          edge["A*"], 23.69, 0.05)
    check("...what an account sized for the running example still runs there",
          edge["throughput"], 0.812, 0.005)
    if not (edge["throughput"] > loud["throughput"] > 0.0):
        FAILURES.append("throughput does not decay across the capital boundary")

    # ------------------------------------------------------------------
    # II-14's last requirement, and the only check in this file with teeth on
    # the working-capital block: everything above is closed forms agreeing
    # with each other, and uniform thinning makes most of that agreement
    # structural.  Here blocking is real, the debit is a jump process, the
    # barrier moves, and nothing was fitted.  It is a Monte Carlo, so it is
    # small, seeded, and reported with the standard error its own paths carry;
    # the full-size run is `wheel_sim.py --scenario constrained`.
    print("--- Structural: the constrained simulator against the closed forms ---")
    import wheel_sim as W
    GS, LEV, EQ, YEARS, NP = 0.25, 2.0, 5.0, 30.0, 384
    # The account is levered well past survivable on purpose.  At the
    # survivable 1.13x the barrier is an 84% drawdown and P(liquidation) is a
    # few parts in a thousand -- unmeasurable at any path count this file can
    # afford -- while at L = 2 it is a 33% drawdown and the same machinery is
    # exercised against a probability of order a half.
    w_stat = STD.r + f["econ_excess"] - (STD.mu - STD.delta)
    P_con = W.Params(delta=0.025, years=YEARS, paths=NP, seed=20260729,
                     gamma_s=GS, equity=EQ, u_star=GS * LEV,
                     draw="stationary", draw_frac=w_stat)
    P_free = W.Params(delta=0.025, years=YEARS, paths=NP // 2, seed=20260729)
    j_con, j_free = W.batch_jobs(P_con), W.batch_jobs(P_free)
    out = pmap(W._batch, j_con + j_free)
    con = W.merge_all(out[:len(j_con)])
    free = W.merge_all(out[len(j_con):])

    # The unconstrained limit, in the simulator this time: unlimited equity
    # refuses nothing, borrows nothing and cannot be sold out.  II-3's
    # regression guard, carried into the machinery that can actually break it.
    check("unlimited equity refuses no put", free.blocked, 0, 0)
    check("...and never reaches a barrier", len(free.t_liq), 0, 0)

    # T_sat.  model.py reads it off the UNCONSTRAINED transient curve, so the
    # simulator's matching object is the unlimited run's mean inventory
    # reaching the same capacity -- not the constrained account, which starts
    # refusing puts well before its mean gets there.
    cap = LEV * EQ
    check("T_sat: unlimited equity reaching capacity, years",
          W._time_to_mean_inventory(free, P_free.cadence, cap),
          time_to_inventory(STD, far_p, lam, cap), 1.0)

    # The barrier itself.  `frozen` holds the book as it stood at the first
    # refused put and lets the price alone move it, which is exactly what
    # liquidation_prob computes -- so this compares a closed form against the
    # same statement measured, through a ledger and a Brownian-bridge crossing
    # test that share none of its machinery.
    nu_sim = crit_p["nu"]
    rows = W.survival_rows(con, nu_sim, STD.sigma, (5.0, 10.0, 20.0))
    print(f"      {'H':>4} {'paths':>6} {'closed':>8} {'frozen':>8} {'operating':>9}"
          f" {'operating-frozen':>16} {'frozen-closed':>16}")
    for H, n, cl, st, dy, co, er in rows:
        print(f"      {H:>3.0f}y {n:>6} {cl[0]:>8.4f} {st[0]:>8.4f} {dy[0]:>9.4f}"
              f" {co[0]:>+8.4f} +-{co[1]:.4f} {er[0]:>+11.4f} +-{er[1]:.4f}")
        if abs(er[0]) > 3 * er[1] + 1e-12:
            FAILURES.append(f"frozen barrier disagrees with the closed form at {H}y")
    print("PASS  the frozen barrier matches liquidation_prob within 3 s.e. "
          "at every horizon")

    # And the answer the item exists to produce: the operating book is sold out
    # MORE often than the frozen barrier says, and by a margin that grows with
    # the horizon.  A frozen book de-levers as the price rises; an operator
    # running a utilization rule buys instead, so the leverage that the closed
    # form lets decay is held at the stopping rule indefinitely.  Pinned,
    # because it is a result rather than an identity.
    for (H, _, _, _, _, co, _), want in zip(rows, (0.0422, 0.0851, 0.2098)):
        check(f"the wheel's own correction to survival at {H:.0f}y", co[0],
              want, 0.03)
        if co[0] <= 0:
            FAILURES.append(f"the correction is not adverse at {H}y")
    check("operating-book liquidation by 20y at L = 2", rows[2][4][0], 0.6236,
          0.05)
    check("...against the closed form's", rows[2][2][0], 0.4312, 0.001)
    # The mechanism is a ratchet: a price rise lets the operator sell more
    # puts, so the debit grows with the book and the account never de-levers
    # the way a frozen one does, while a price fall blocks and leaves it where
    # it is.  It is visible as the drift of ln(M/D), which the closed form
    # takes to be nu - g -- but it is only MEASURABLE where most paths
    # survive, so the figure quoted for it is the prudent configuration's in
    # `--scenario constrained`, not this run's.  Here the survivors are the
    # price-up paths by construction.
    #
    # Uniform thinning is NOT checked here either.  At L = 2 most paths are
    # liquidated inside the run, so every steady-state figure is conditioned
    # on the price having risen, and a census read off it would be a
    # survivorship artifact.  That measurement belongs to the prudent
    # configuration, and it is `wheel_sim.py --scenario constrained`'s.

    # ------------------------------------------------------------------
    if args.full:
        print("--- Stationary figures, Richardson-extrapolated (slow) ---")
        check("stationary E[T] (Standard, P), years", f["E[T]"], 2.10, 0.03)
        check("Siegmund closed form for E[T]", f["E[T]_siegmund"], 1.91, 0.03)
        check("stationary E[I] (Standard, P)", f["I"], 21.82, 0.30)
        check("years to reach 90% of stationary E[I]", t90, 90.4, 1.0)
        # The Q-world stationary figures are quoted as round numbers in the
        # text: at nu = 0.5% the mean is carried by the far tail, so the
        # tolerances here are what the article actually claims, not more.
        check("stationary E[T] (Standard, Q), years", g["E[T]"], 9.0, 0.4)
        check("stationary E[I] (Standard, Q)", g["I"], 93.7, 4.0)

    # ------------------------------------------------------------------
    # The worked examples: one runnable script per numbered formula, each
    # carrying the article's own invocations as frozen cases.  This is the
    # half a reader can reproduce -- a Case holds a *command line*, so the
    # command a footnote prints is the command checked here.  The needs of
    # every case are unioned and solved in one parallel batch.
    print("--- Worked examples (code/examples/, one script per formula) ---")
    from examples import _harness as H, _report as R
    mods = H.discover(strict=True)
    ctx = H.solve_all(H.collect_needs(mods))
    FAILURES.extend(H.report_cases(mods, ctx, quiet=True))
    print(f"  {sum(len(m.CASES) for m in mods)} cases over {len(mods)} modules, "
          f"{len({n.key for n in H.collect_needs(mods)})} distinct solves")

    # And the policy itself, as a test rather than an aspiration: every
    # numbered formula has a script, every script is cited from the prose,
    # and every footnote leads to the script that actually backs its formula.
    print("--- Reproducibility coverage ---")
    FAILURES.extend(R.coverage(mods))

    # The same policy for citations: every #ref: the prose cites is an entry
    # in the bibliography, and no section declares one of its own.
    print("--- Citation coverage ---")
    FAILURES.extend(R.references())

    # And section 00 against the sections it claims to be the source of truth
    # for: both checks above read the sections directly, so its hand-maintained
    # anchor registers were the one cross-reference set nothing was reading.
    print("--- Register coverage ---")
    FAILURES.extend(R.registers())

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
