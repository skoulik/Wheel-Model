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

Each check recomputes a number from `model.py` and asserts it matches what the
text says. If a formula in the text is edited, re-run this script; a sign error
(this project's historical failure mode) will trip an assertion.

The structural check at the end is the strongest one in the file: run the whole
machinery in the Q-world and the economic excess return must vanish up to the
dividend-withholding leak, because no strategy beats the risk-free rate under
the pricing measure. It exercises the entry law, the depth walk, the occupation
measure, premium pricing and the capital definition simultaneously.

Stdlib only (Python 3.8+).
"""

import argparse
from math import exp, log, sqrt

import model
from model import (BETA, Config, N, assign_prob, bs_call, criteria,
                   d2, depth_census, economics, entry_law, expected_drop,
                   debit_growth, first_passage_prob, k_star_drift, leverage,
                   liquidation_barrier, liquidation_prob, max_leverage,
                   max_debit_growth, max_sustainable_draw,
                   occupation, pmap, put_premium, q_exit,
                   saturation, stationary, stationary_converged,
                   sticky_dividend_trap, sticky_dividend_yield, strike,
                   survival_utilization, time_to_fraction, time_to_inventory,
                   trapped_fraction)

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


def _econ_job(job):
    """A sweep row: economics at one horizon, its own walk."""
    cfg, measure, H = job
    return economics(cfg, measure, occupation(cfg, measure), horizon=H)


def _sticky_job(job):
    """The sticky-dividend fixed point at one horizon, and what it implies."""
    cfg, measure, H = job
    d, F = sticky_dividend_yield(cfg, measure, H)
    at_eff = Config(p_star=cfg.p_star, delta=d)
    return d, F, economics(at_eff, measure, occupation(at_eff, measure), horizon=H)


def _census_job(job):
    cfg, measure, edges, horizon = job
    return depth_census(cfg, measure, edges, horizon=horizon)


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

    # ------------------------------------------------------------------
    print("--- Section 05: entry ---")
    k_p, p_p, x0_p, _ = entry_law(STD, "P")
    k_q, p_q, x0_q, _ = entry_law(STD, "Q")
    check("k* (Standard, P-world)", k_p, 0.9774, 0.0005)
    check("k* (Standard, Q-world)", k_q, 0.9770, 0.0005)
    check("realized assignment rate = p* by construction", p_p, 0.20, 1e-9)
    check("E[x0] (Standard)", x0_p, 0.0155, 0.0005)
    check("E[d | assignment] (Standard, P)", expected_drop(STD, "P"), 0.0375, 0.001)
    check("E[d | assignment] (Standard, Q)", expected_drop(STD, "Q"), 0.0379, 0.001)
    # What the broker screen shows at the same strike: the risk-neutral number.
    m_q, _ = STD.world("Q")
    check("screen (risk-neutral) p at the P-strike",
          assign_prob(k_p, STD.tau_p, STD.sigma, m_q), 0.2039, 0.001)
    check("what the screen usually shows instead: delta N(-d1)",
          N(-(d2(k_p, STD.tau_p, STD.sigma, m_q) + STD.sigma * sqrt(STD.tau_p))),
          0.1961, 0.002)
    check("c_p, the put quote (Standard)", put_premium(STD, "P"), 0.00306, 0.0002)
    check("k* (Conservative, P-world)", strike(CON, "P"), 0.9655, 0.0005)
    check("E[x0] (Conservative)", entry_law(CON, "P")[2], 0.0131, 0.0005)
    check("E[d | assignment] (Conservative, P)", expected_drop(CON, "P"), 0.0470, 0.001)
    check("E[d | assignment] (Conservative, Q)", expected_drop(CON, "Q"), 0.0474, 0.001)
    # "Where a real operator sits on the dial": the live account's names carry a
    # volatility near 30%, not the running example's 20%, so the same one-in-ten
    # dial puts the strike further out.  The live side of that comparison -- the
    # 7.7% realized rate, the 10.9% revealed dial, the 5.5% median moneyness --
    # is measured by `model_vs_live.py`, which nothing here reproduces (INF-2).
    m_p_, _ = STD.world("P")
    check("k* for p*=10% at the live account's sigma = 29.7%",
          1 - k_star_drift(0.10, STD.tau_p, 0.297, m_p_), 0.051, 0.001)

    # ------------------------------------------------------------------
    print("--- Section 06: the depth process ---")
    crit_p, crit_q = criteria(STD, "P"), criteria(STD, "Q")
    check("nu (P-world)", crit_p["nu"], 0.025, 1e-9)
    check("nu (Q-world)", crit_q["nu"], 0.005, 1e-9)
    # The two tables of section 06: exit odds and premium, both against depth.
    for x, q_want, cc_want in [(x0_p, 0.404, 0.0161), (0.03, 0.306, 0.0110),
                               (0.05, 0.193, 0.0060), (0.10, 0.039, 0.0009),
                               (0.15, 0.004, 0.0001), (0.20, 0.000, 0.0000)]:
        check(f"q at depth {x:.3f}", q_exit(STD, "P", x), q_want, 0.001)
        check(f"call quote at depth {x:.3f}",
              bs_call(1.0, exp(x), STD.tau_c, STD.sigma_iv, STD.r, STD.delta),
              cc_want, 0.0002)
    check("one period's jostle, sigma*sqrt(tau_c)",
          STD.sigma * sqrt(STD.tau_c), 0.05547, 1e-5)
    check("one period's drift, nu*tau_c", crit_p["nu"] * STD.tau_c, 0.001923, 1e-6)
    # "What a constant dividend yield assumes": a 30% fall with no cut.
    check("yield lift from a 30% fall with the payout unchanged",
          1 / 0.70 - 1, 0.43, 0.005)
    check("volatility at which nu vanishes", sqrt(2 * (STD.mu - STD.delta)),
          0.30, 0.001)

    # ------------------------------------------------------------------
    print("--- Section 07: holding time ---")
    sc = STD.sigma * sqrt(STD.tau_c)
    check("call-grid tax beta*sigma*sqrt(tau_c)", BETA * sc, 0.0323, 0.0005)
    check("grid tax as a multiple of the entry depth", BETA * sc / x0_p, 2.09, 0.05)
    check("first-period exit probability (P)", occ_p["q(x0)"], 0.405, 0.005)
    check("the naive 1/q answer, in call periods", 1 / occ_p["q(x0)"], 2.47, 0.02)
    check("every lot eventually exits when nu > 0", occ_p["P[exit]"], 1.0, 0.002)
    check("call premiums collected per lot (P)", occ_p["E[prem]"], 0.0372, 0.001)
    check("upside given away per lot (P)", occ_p["E[exitcost]"], 0.0358, 0.001)
    # The survival curve quoted in section 07. The call period is 4 weeks, so
    # every column is an exact multiple of it: j periods = 4j weeks, 13 = 1 y.
    for label, j, want in [("4 wk", 1, 0.60), ("8 wk", 2, 0.46), ("12 wk", 3, 0.38),
                           ("24 wk", 6, 0.27), ("1 y", 13, 0.18),
                           ("2 y", 26, 0.12), ("5 y", 65, 0.07),
                           ("10 y", 130, 0.04), ("20 y", 260, 0.02)]:
        check(f"still held after {label}", occ_p["surv"][j], want, 0.005)
    median_j = next(j for j, s in enumerate(occ_p["surv"]) if s < 0.5)
    check("median holding time, in call periods", median_j, 2, 0)

    # ------------------------------------------------------------------
    print("--- Section 08: inventory ---")
    e30 = economics(STD, "P", occ_p, horizon=30.0)
    check("arrival rate lambda (Standard)", e30["lambda"], 10.40, 0.01)
    check("E[I] over 30 years (Standard, P)", e30["I"], 11.40, 0.10)
    check("E[I] over 30 years (Standard, Q)",
          economics(STD, "Q", occ_q, horizon=30.0)["I"], 14.49, 0.12)
    check("E[I] over 30 years (Conservative, P)",
          economics(CON, "P", occ_c, horizon=30.0)["I"], 5.50, 0.06)
    # The depth census: what the standing inventory is made of.  The 30-year
    # and stationary censuses are separate walks, and the two trap censuses of
    # section 09 below are two more, so all four are issued at once.
    EDGES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, float("inf")]
    x_trap_p, x_trap_q = sticky_dividend_trap(STD, "P"), sticky_dividend_trap(STD, "Q")
    (shares, mean_x, mean_q), (s_st, mx_st, mq_st), trap_p, trap_q = pmap(
        _census_job, [(STD, "P", EDGES, 30.0), (STD, "P", EDGES, None),
                      (STD, "P", [0.0, x_trap_p, float("inf")], 30.0),
                      (STD, "Q", [0.0, x_trap_q, float("inf")], 30.0)])
    for i, want in enumerate([0.08, 0.05, 0.11, 0.07, 0.09, 0.13, 0.18, 0.28]):
        check(f"census share, bin {i + 1} of 8", shares[i], want, 0.006)
    check("inventory-weighted mean depth (30y)", mean_x, 0.380, 0.005)
    check("inventory-weighted exit probability (30y)", mean_q, 0.066, 0.003)
    check("share of held time deeper than 30%", shares[6] + shares[7], 0.46, 0.01)
    check("stationary inventory-weighted mean depth", mx_st, 0.790, 0.01)
    check("stationary inventory-weighted exit probability", mq_st, 0.036, 0.003)
    check("stationary share of held time deeper than 50%", s_st[7], 0.53, 0.01)
    check("capital per share of a lot 50% down in log terms", exp(0.5), 1.65, 0.01)

    # ------------------------------------------------------------------
    print("--- Section 09: returns and capital ---")
    for H, inv, mv, cost, econ, cash in [(5.0, 5.41, 5.61, 6.70, 0.0160, 0.0411),
                                         (10.0, 7.39, 7.59, 9.83, 0.0160, 0.0181),
                                         (30.0, 11.40, 11.59, 18.23, 0.0160, -0.0077)]:
        x = economics(STD, "P", occ_p, horizon=H)
        check(f"E[I] at {H:.0f}y", x["I"], inv, 0.05)
        check(f"market-value capital at {H:.0f}y", x["mv_capital"], mv, 0.05)
        check(f"cost-basis capital at {H:.0f}y", x["capital"], cost, 0.06)
        check(f"economic excess at {H:.0f}y", x["econ_excess"], econ, 0.0005)
        check(f"cash-view excess at {H:.0f}y", x["excess"], cash, 0.0005)
    # The wheel against simply owning the stock, on the same capital.
    m_p, _ = STD.world("P")
    buy_hold = m_p + STD.delta_net - STD.r
    check("buy-and-hold excess return", buy_hold, 0.01625, 1e-6)
    equity_frac = e30["I"] / e30["mv_capital"]
    check("wheel's equity fraction of capital", equity_frac, 0.983, 0.005)
    check("gap: wheel minus equity-adjusted buy-and-hold",
          e30["econ_excess"] - buy_hold * equity_frac, 0.0001, 0.0005)
    # The income decomposition quoted at the top of the section.
    cp_yr = e30["c_p"] / STD.cadence
    check("put premiums per year", cp_yr, 0.1591, 0.0010)
    check("call premiums per year", e30["premiums"] - cp_yr, 0.3706, 0.0020)
    check("dividends per year", e30["dividends"], 0.2422, 0.0010)
    check("Track A income per year", e30["income"], 0.7718, 0.0020)
    m_price, _ = STD.world("P")
    apprec = e30["I"] * m_price
    check("appreciation of held shares per year", apprec, 0.5128, 0.0020)
    check("mark loss at acquisition per year", e30["acq_loss"], 0.1632, 0.0010)
    check("upside surrendered per year", e30["call_away_loss"], 0.3559, 0.0020)
    check("the three nearly cancel",
          apprec - e30["acq_loss"] - e30["call_away_loss"], -0.0063, 0.0015)

    # The volatility-risk-premium sweep: how much edge is needed, and what it
    # buys.  Independent configs -- one pmap, one row each.
    VRP = [(0.000, 0.5297, 0.0160, 0.0001), (0.005, 0.5555, 0.0183, 0.0023),
           (0.010, 0.5818, 0.0205, 0.0046), (0.020, 0.6358, 0.0252, 0.0092)]
    vrp_cfgs = [Config(p_star=0.20, iv_spread=s) for s, *_ in VRP]
    vrp_rows = pmap(_econ_job, [(c, "P", 30.0) for c in vrp_cfgs])
    for (spread, prem, exc, gap), cfg, xs in zip(VRP, vrp_cfgs, vrp_rows):
        check(f"premiums/yr at sigma_IV = {cfg.sigma_iv:.3f}",
              xs["premiums"], prem, 0.0010)
        check(f"excess at sigma_IV = {cfg.sigma_iv:.3f}", xs["econ_excess"],
              exc, 0.0005)
        check(f"gap vs buy-and-hold at sigma_IV = {cfg.sigma_iv:.3f}",
              xs["econ_excess"] - buy_hold * (xs["I"] / xs["mv_capital"]),
              gap, 0.0005)

    # The dividend sweep.
    DIV = [(0.000, 8.54, 8.74, 12.11, 0.0198), (0.010, 9.56, 9.75, 14.15, 0.0183),
           (0.025, 11.40, 11.59, 18.23, 0.0160), (0.040, 13.65, 13.84, 24.00, 0.0138),
           (0.060, 17.31, 17.51, 35.50, 0.0108)]
    div_cfgs = [Config(p_star=0.20, delta=d) for d, *_ in DIV]
    div_rows = pmap(_econ_job, [(c, "P", 30.0) for c in div_cfgs])
    for (d, inv, mv, cost, exc), cfg, xd in zip(DIV, div_cfgs, div_rows):
        check(f"E[I] at delta = {d:.3f}", xd["I"], inv, 0.05)
        check(f"market capital at delta = {d:.3f}", xd["mv_capital"], mv, 0.05)
        check(f"cost capital at delta = {d:.3f}", xd["capital"], cost, 0.10)
        check(f"true excess at delta = {d:.3f}", xd["econ_excess"], exc, 0.0005)
        bh_d = (cfg.mu - cfg.r - cfg.withhold * d) * xd["I"] / xd["mv_capital"]
        check(f"gap vs buy-and-hold at delta = {d:.3f}",
              xd["econ_excess"] - bh_d, 0.0001, 0.0003)

    # "What if the dividend never falls?" -- the sticky-dividend bound. delta
    # reaches the model only through nu and through income, so the whole
    # correction is a row of the sweep above at a larger delta.
    STICKY = [(5.0, 1.020, 0.02550, 0.01588, -0.00008, 0.00027),
              (10.0, 1.039, 0.02597, 0.01581, -0.00015, 0.00012),
              (30.0, 1.113, 0.02782, 0.01562, -0.00042, 0.00006)]
    sticky_rows = pmap(_sticky_job, [(STD, "P", H) for H, *_ in STICKY])
    for (H, F, d_eff, exc, shift, gap), (d_got, F_got, xs) in zip(STICKY, sticky_rows):
        check(f"sticky-dividend inflation factor at {H:.0f}y", F_got, F, 0.001)
        check(f"delta_eff at {H:.0f}y", d_got, d_eff, 0.0001)
        cfg = Config(p_star=0.20, delta=d_got)
        base = economics(STD, "P", occ_p, horizon=H)
        check(f"true excess at delta_eff, {H:.0f}y", xs["econ_excess"], exc, 0.0002)
        check(f"change from constant delta at {H:.0f}y",
              xs["econ_excess"] - base["econ_excess"], shift, 0.0001)
        bh_s = (cfg.mu - cfg.r - cfg.withhold * d_got) * xs["I"] / xs["mv_capital"]
        check(f"gap vs buy-and-hold at delta_eff, {H:.0f}y",
              xs["econ_excess"] - bh_s, gap, 0.0002)
        if H == 30.0:
            check("inventory rise under the sticky correction",
                  xs["I"] / base["I"] - 1, 0.034, 0.003)
            check("cost-basis capital rise under the sticky correction",
                  xs["capital"] / base["capital"] - 1, 0.051, 0.004)
    # The correction has no stationary value: held lot-time thins like the
    # holding-time tail while the yield inflates faster.
    check("yield inflation rate sigma^2/2", STD.sigma**2 / 2, 0.0200, 0.0001)
    nu_p = crit_p["nu"]
    check("held-time thinning rate nu^2/(2 sigma^2)",
          nu_p**2 / (2 * STD.sigma**2), 0.0078, 0.0002)
    # A buy-and-hold anchor stands the whole horizon, so it inflates by more.
    a = STD.sigma**2 * 30.0 / 2
    check("buy-and-hold inflation factor at 30y", (exp(a) - 1) / a, 1.370, 0.002)
    # The depth past which a payout frozen in dollars outruns the drift.
    # (The censuses came out of the pmap in section 08.)
    for meas, xs_, (sh, _, _), xstar, below, beyond in [
            ("P", x_trap_p, trap_p, 0.693, 0.500, 0.164),
            ("Q", x_trap_q, trap_q, 0.182, 0.167, 0.692)]:
        check(f"sticky-dividend trap depth x* ({meas})", xs_, xstar, 0.001)
        check(f"x* as a fraction below the strike ({meas})", 1 - exp(-xs_),
              below, 0.001)
        check(f"30y census mass beyond x* ({meas})", sh[1], beyond, 0.006)
    # The rejected per-lot version, kept as a check that it is the cost-basis
    # capital in disguise -- an unfunded +1.24pp, which is why it is wrong.
    naive = e30["dividends"] * ((e30["capital"] - STD.gamma_p * e30["k"])
                                / e30["I"] - 1)
    check("unfunded return from per-lot dividend anchoring (rejected)",
          naive / e30["mv_capital"], 0.0122, 0.0003)

    # The Conservative regime.
    xc = economics(CON, "P", occ_c, horizon=30.0)
    check("Conservative: lots held", xc["I"], 5.50, 0.05)
    check("Conservative: market capital", xc["mv_capital"], 5.70, 0.05)
    check("Conservative: cost capital", xc["capital"], 8.90, 0.06)
    check("Conservative: Track A income", xc["income"], 0.3711, 0.0020)
    check("Conservative: true excess", xc["econ_excess"], 0.0149, 0.0005)
    check("Conservative: cash-on-cost-basis", xc["excess"], -0.0083, 0.0005)
    check("Conservative: buy-and-hold benchmark",
          buy_hold * xc["I"] / xc["mv_capital"], 0.0157, 0.0005)

    # The collateral footnote, and the regime comparison it explains. Track C
    # charges r on the put margin, which in fact earns approximately r at the
    # broker. The overcharge is the same absolute number in both regimes but a
    # different share of capital, because Conservative's inventory is half the
    # size -- and correcting it makes the two regimes agree, which is the point
    # of the table in section 09.
    for H, over, gap_s, gap_c in [(5.0, 0.00174, 0.0003, -0.0014),
                                  (10.0, 0.00129, 0.0001, -0.0011),
                                  (30.0, 0.00084, 0.0001, -0.0008)]:
        xs, xcv = (economics(STD, "P", occ_p, horizon=H),
                   economics(CON, "P", occ_c, horizon=H))
        o_s = STD.r * STD.gamma_p * xs["k"] / xs["mv_capital"]
        o_c = CON.r * CON.gamma_p * xcv["k"] / xcv["mv_capital"]
        g_s = xs["econ_excess"] - buy_hold * xs["I"] / xs["mv_capital"]
        g_c = xcv["econ_excess"] - buy_hold * xcv["I"] / xcv["mv_capital"]
        check(f"Track C overcharge on collateral at {H:.0f}y (Standard)",
              o_s, over, 5e-5)
        check(f"gap vs buy-and-hold at {H:.0f}y (Standard)", g_s, gap_s, 0.0005)
        check(f"gap vs buy-and-hold at {H:.0f}y (Conservative)",
              g_c, gap_c, 0.0005)
        check(f"the regimes agree once collateral earns r ({H:.0f}y)",
              (g_s + o_s) - (g_c + o_c), 0.0, 0.0001)
    # And the fully cash-secured convention, where collateral is k not gamma*k.
    check("cash-secured overcharge is ~4.5x the margin one (30y)",
          (e30["k"] / (e30["k"] + e30["I"]))
          / (STD.gamma_p * e30["k"] / e30["mv_capital"]), 4.7, 0.1)

    # ------------------------------------------------------------------
    print("--- Section 10: stability ---")
    check("tail exponent 2nu/sigma^2 (P)", crit_p["tail_exponent"], 1.25, 0.01)
    check("tail exponent 2nu/sigma^2 (Q)", crit_q["tail_exponent"], 0.25, 0.01)
    print(f"      P-world: count {'stable' if crit_p['count_ok'] else 'UNSTABLE'}, "
          f"capital {'stable' if crit_p['capital_ok'] else 'UNSTABLE'}")
    print(f"      Q-world: count {'stable' if crit_q['count_ok'] else 'UNSTABLE'}, "
          f"capital {'stable' if crit_q['capital_ok'] else 'UNSTABLE'}")
    if crit_p["capital_ok"] and not crit_q["capital_ok"]:
        print("PASS  the two measures disagree on capital stability (the "
              "article's sharpest comparison)")
    else:
        FAILURES.append("measure disagreement on capital stability")
    # Where the two boundaries sit, in each parameter.
    check("volatility at which lot count destabilizes (sqrt(2(mu-delta)))",
          sqrt(2 * (STD.mu - STD.delta)), 0.300, 0.001)
    check("volatility at which capital destabilizes (sqrt(mu-delta))",
          sqrt(STD.mu - STD.delta), 0.2121, 0.001)
    check("dividend yield at which lot count destabilizes (mu - sigma^2/2)",
          STD.mu - STD.sigma**2 / 2, 0.050, 1e-9)
    check("dividend yield at which capital destabilizes (mu - sigma^2)",
          STD.mu - STD.sigma**2, 0.030, 1e-9)
    hi_vol = Config(sigma=0.40)
    check("nu at sigma=40% (both criteria fail)",
          criteria(hi_vol, "P")["nu"], -0.035, 1e-9)
    check("trapped-forever fraction per assignment at sigma=40%",
          trapped_fraction(hi_vol, "P"), 0.0409, 0.002)
    # Independent cross-check of that closed form: integrate the escape
    # probability against the entry density directly.
    _, _, _, dens = entry_law(hi_vol, "P")
    m_h, s_h = hi_vol.world("P")
    th = 2 * abs(m_h - s_h**2 / 2) / s_h**2
    sc_h = s_h * sqrt(hi_vol.tau_c)
    step = 0.0005
    num = sum(dens((i + .5) * step) * step * exp(-th * ((i + .5) * step + BETA * sc_h))
              for i in range(20000))
    den = sum(dens((i + .5) * step) * step for i in range(20000))
    check("trapped fraction: closed form vs numerical integration",
          trapped_fraction(hi_vol, "P"), 1 - num / den, 1e-4)
    check("trapped lots accumulate per year at sigma=40%",
          (STD.p_star / STD.cadence) * trapped_fraction(hi_vol, "P"), 0.43, 0.02)

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
    for g in (0.50, 0.25, 0.15):
        check(f"f* = 1 at the broker's ceiling L = 1/{g:g}",
              liquidation_barrier(1.0 / g, g), 1.0, 1e-12)
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
    for g, l1, l10 in LMAX:
        Cg = Config(p_star=0.20, gamma_s=g)
        got1, got10 = max_leverage(Cg, "P", 0.01), max_leverage(Cg, "P", 0.10)
        print(f"      {g:>8.2f} {1 / g:>8.2f} {got1:>10.4f} {got10:>11.4f}"
              f" {got10 * g:>12.1%}")
        check(f"L_max at gamma_s = {g:.2f}, eps = 1%", got1, l1, 0.0005)
        check(f"L_max at gamma_s = {g:.2f}, eps = 10%", got10, l10, 0.0005)
        for eps, L in ((0.01, got1), (0.10, got10)):
            if L > 1.0:                     # gamma_s = 1 has nothing to invert
                check(f"round trip at gamma_s = {g:.2f}: P at L_max = eps",
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
    # Capacity needs the stationary survival curve -- the transient inverse
    # runs centuries into the tail, where a single grid's O(h^2) bias has
    # accumulated -- so the extrapolated pair is solved here rather than under
    # --full, and --full reuses it.
    (far_p, f, t90), (far_q, g, _) = pmap(
        _stationary_job, [(STD, "P"), (STD, "Q")])

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
    for A, want in ((11.59, 18.5), (15.0, 44.4), (5.0, 2.4)):
        check(f"T_sat at A = {A} lots, years",
              saturation(G25, "P", far_p, 0.10, equity=A, econ=f)["T_sat"],
              want, 0.1)

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
    check("the leverage an untended account drifts to at A = 11.59",
          L_reach, 1.883, 0.001)
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
    print(f"      {'H':>4} {'paths':>6} {'closed':>8} {'frozen':>8} {'live':>8}"
          f" {'live-frozen':>12} {'frozen-closed':>16}")
    for H, n, cl, st, dy, co, er in rows:
        print(f"      {H:>3.0f}y {n:>6} {cl[0]:>8.4f} {st[0]:>8.4f} {dy[0]:>8.4f}"
              f" {co[0]:>+8.4f} +-{co[1]:.4f} {er[0]:>+11.4f} +-{er[1]:.4f}")
        if abs(er[0]) > 3 * er[1] + 1e-12:
            FAILURES.append(f"frozen barrier disagrees with the closed form at {H}y")
    print("PASS  the frozen barrier matches liquidation_prob within 3 s.e. "
          "at every horizon")

    # And the answer the item exists to produce: the live account is sold out
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
    check("live-account liquidation by 20y at L = 2", rows[2][4][0], 0.6236,
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

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
