"""Numerical verification of every worked example quoted in the sections.

Run:  python code/verify_examples.py          (analytic, ~4 min)
      python code/verify_examples.py --full   (adds the extrapolated
                                               stationary figures, ~12 min)

The weekly cadence costs time: the call grid is 4 weeks, so covering the same
span of calendar years takes 4.3x more periods than the old quarterly grid,
and resolving a period's step (sigma*sqrt(tau_c) = 0.055) needs h = 0.01
rather than 0.02.

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

from model import (BETA, Config, DepthWalk, N, assign_prob, bs_call, criteria,
                   d2, depth_census, economics, entry_law, expected_drop,
                   k_star_drift, occupation, put_premium, q_exit, stationary,
                   sticky_dividend_trap, sticky_dividend_yield, strike,
                   time_to_fraction, trapped_fraction)

FAILURES = []


def check(label, got, expected, tol):
    ok = abs(got - expected) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got:.4f}, expected ~{expected}")
    if not ok:
        FAILURES.append(label)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--full", action="store_true",
                    help="also check the far-grid stationary figures (slow)")
    args = ap.parse_args()

    STD = Config(p_star=0.20, label="Standard")
    CON = Config(p_star=0.10, label="Conservative")

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
    occ_p = occupation(STD, "P")
    occ_q = occupation(STD, "Q")
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
    occ_c = occupation(CON, "P")
    check("E[I] over 30 years (Conservative, P)",
          economics(CON, "P", occ_c, horizon=30.0)["I"], 5.50, 0.06)
    # The depth census: what the standing inventory is made of.
    EDGES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, float("inf")]
    shares, mean_x, mean_q = depth_census(STD, "P", EDGES, horizon=30.0)
    for i, want in enumerate([0.08, 0.05, 0.11, 0.07, 0.09, 0.13, 0.18, 0.28]):
        check(f"census share, bin {i + 1} of 8", shares[i], want, 0.006)
    check("inventory-weighted mean depth (30y)", mean_x, 0.380, 0.005)
    check("inventory-weighted exit probability (30y)", mean_q, 0.066, 0.003)
    check("share of held time deeper than 30%", shares[6] + shares[7], 0.46, 0.01)
    s_st, mx_st, mq_st = depth_census(STD, "P", EDGES)
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

    # The volatility-risk-premium sweep: how much edge is needed, and what it buys.
    for spread, prem, exc, gap in [(0.000, 0.5297, 0.0160, 0.0001),
                                   (0.005, 0.5555, 0.0183, 0.0023),
                                   (0.010, 0.5818, 0.0205, 0.0046),
                                   (0.020, 0.6358, 0.0252, 0.0092)]:
        cfg = Config(p_star=0.20, iv_spread=spread)
        xs = economics(cfg, "P", occupation(cfg, "P"), horizon=30.0)
        check(f"premiums/yr at sigma_IV = {cfg.sigma_iv:.3f}",
              xs["premiums"], prem, 0.0010)
        check(f"excess at sigma_IV = {cfg.sigma_iv:.3f}", xs["econ_excess"],
              exc, 0.0005)
        check(f"gap vs buy-and-hold at sigma_IV = {cfg.sigma_iv:.3f}",
              xs["econ_excess"] - buy_hold * (xs["I"] / xs["mv_capital"]),
              gap, 0.0005)

    # The dividend sweep.
    for d, inv, mv, cost, exc in [(0.000, 8.54, 8.74, 12.11, 0.0198),
                                  (0.010, 9.56, 9.75, 14.15, 0.0183),
                                  (0.025, 11.40, 11.59, 18.23, 0.0160),
                                  (0.040, 13.65, 13.84, 24.00, 0.0138),
                                  (0.060, 17.31, 17.51, 35.50, 0.0108)]:
        cfg = Config(p_star=0.20, delta=d)
        xd = economics(cfg, "P", occupation(cfg, "P"), horizon=30.0)
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
    for H, F, d_eff, exc, shift, gap in [
            (5.0, 1.020, 0.02550, 0.01588, -0.00008, 0.00027),
            (10.0, 1.039, 0.02597, 0.01581, -0.00015, 0.00012),
            (30.0, 1.113, 0.02782, 0.01562, -0.00042, 0.00006)]:
        d_got, F_got = sticky_dividend_yield(STD, "P", H)
        check(f"sticky-dividend inflation factor at {H:.0f}y", F_got, F, 0.001)
        check(f"delta_eff at {H:.0f}y", d_got, d_eff, 0.0001)
        cfg = Config(p_star=0.20, delta=d_got)
        xs = economics(cfg, "P", occupation(cfg, "P"), horizon=H)
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
    for meas, xstar, below, beyond in [("P", 0.693, 0.500, 0.164),
                                       ("Q", 0.182, 0.167, 0.692)]:
        xs_ = sticky_dividend_trap(STD, meas)
        check(f"sticky-dividend trap depth x* ({meas})", xs_, xstar, 0.001)
        check(f"x* as a fraction below the strike ({meas})", 1 - exp(-xs_),
              below, 0.001)
        sh, _, _ = depth_census(STD, meas, [0.0, xs_, float("inf")],
                                horizon=30.0)
        check(f"30y census mass beyond x* ({meas})", sh[1], beyond, 0.006)
    # The rejected per-lot version, kept as a check that it is the cost-basis
    # capital in disguise -- an unfunded +1.24pp, which is why it is wrong.
    naive = e30["dividends"] * ((e30["capital"] - STD.margin * e30["k"])
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
    print("--- Structural: no-arbitrage in the Q-world ---")
    for label, cfg in (("Standard", STD), ("Conservative", CON)):
        occ = occupation(cfg, "Q")
        for H in (5.0, 10.0, 30.0):
            x = economics(cfg, "Q", occ, horizon=H)
            resid = x["econ_excess"] + x["leak"] / x["mv_capital"]
            check(f"{label} @ {H:.0f}y: Q-world excess = -(withholding leak)",
                  resid, 0.0, 0.003)

    # ------------------------------------------------------------------
    if args.full:
        print("--- Stationary figures, Richardson-extrapolated (slow) ---")
        fp = stationary(STD, "P")
        f = economics(STD, "P", fp)
        check("stationary E[T] (Standard, P), years", f["E[T]"], 2.10, 0.03)
        check("Siegmund closed form for E[T]", f["E[T]_siegmund"], 1.91, 0.03)
        check("stationary E[I] (Standard, P)", f["I"], 21.82, 0.30)
        check("years to reach 90% of stationary E[I]",
              time_to_fraction(STD, fp, 0.9), 90.4, 1.0)
        # The Q-world stationary figures are quoted as round numbers in the
        # text: at nu = 0.5% the mean is carried by the far tail, so the
        # tolerances here are what the article actually claims, not more.
        fq = stationary(STD, "Q")
        g = economics(STD, "Q", fq)
        check("stationary E[T] (Standard, Q), years", g["E[T]"], 9.0, 0.4)
        check("stationary E[I] (Standard, Q)", g["I"], 93.7, 4.0)

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
