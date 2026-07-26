"""Numerical verification of every worked example quoted in the sections.

Run:  python code/verify_examples.py          (analytic, ~15 s)
      python code/verify_examples.py --full   (adds the far-grid stationary
                                               figures, ~2 min)

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
                   k_star_drift, occupation, put_premium, q_exit, strike,
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
    check("k* (Standard, P-world)", k_p, 0.9546, 0.0005)
    check("k* (Standard, Q-world)", k_q, 0.9530, 0.0005)
    check("realized assignment rate = p* by construction", p_p, 0.20, 1e-9)
    check("E[x0] (Standard)", x0_p, 0.0322, 0.0005)
    check("E[d | assignment] (Standard, P)", expected_drop(STD, "P"), 0.0754, 0.001)
    check("E[d | assignment] (Standard, Q)", expected_drop(STD, "Q"), 0.0770, 0.001)
    # What the broker screen shows at the same strike: the risk-neutral number.
    m_q, _ = STD.world("Q")
    check("screen (risk-neutral) p at the P-strike",
          assign_prob(k_p, STD.tau_p, STD.sigma, m_q), 0.2075, 0.001)
    check("what the screen usually shows instead: delta N(-d1)",
          N(-(d2(k_p, STD.tau_p, STD.sigma, m_q) + STD.sigma * sqrt(STD.tau_p))),
          0.192, 0.002)
    check("c_p, the put quote (Standard)", put_premium(STD, "P"), 0.00628, 0.0002)
    check("k* (Conservative, P-world)", strike(CON, "P"), 0.9306, 0.0005)
    check("E[x0] (Conservative)", entry_law(CON, "P")[2], 0.0273, 0.0005)
    check("E[d | assignment] (Conservative, P)", expected_drop(CON, "P"), 0.0942, 0.001)
    check("E[d | assignment] (Conservative, Q)", expected_drop(CON, "Q"), 0.0958, 0.001)

    # ------------------------------------------------------------------
    print("--- Section 06: the depth process ---")
    crit_p, crit_q = criteria(STD, "P"), criteria(STD, "Q")
    check("nu (P-world)", crit_p["nu"], 0.025, 1e-9)
    check("nu (Q-world)", crit_q["nu"], 0.005, 1e-9)
    # The two tables of section 06: exit odds and premium, both against depth.
    for x, q_want, cc_want in [(x0_p, 0.398, 0.0284), (0.05, 0.331, 0.0221),
                               (0.10, 0.174, 0.0098), (0.15, 0.075, 0.0036),
                               (0.20, 0.026, 0.0011), (0.30, 0.002, 0.0001)]:
        check(f"q at depth {x:.3f}", q_exit(STD, "P", x), q_want, 0.001)
        check(f"call quote at depth {x:.3f}",
              bs_call(1.0, exp(x), STD.tau_c, STD.sigma_iv, STD.r, STD.delta),
              cc_want, 0.0002)
    check("one period's jostle, sigma*sqrt(tau_c)",
          STD.sigma * sqrt(STD.tau_c), 0.10, 1e-9)
    check("one period's drift, nu*tau_c", crit_p["nu"] * STD.tau_c, 0.00625, 1e-9)
    check("volatility at which nu vanishes", sqrt(2 * (STD.mu - STD.delta)),
          0.30, 0.001)

    # ------------------------------------------------------------------
    print("--- Section 07: holding time ---")
    occ_p = occupation(STD, "P")
    occ_q = occupation(STD, "Q")
    sc = STD.sigma * sqrt(STD.tau_c)
    check("call-grid tax beta*sigma*sqrt(tau_c)", BETA * sc, 0.0583, 0.0005)
    check("grid tax as a multiple of the entry depth", BETA * sc / x0_p, 1.81, 0.05)
    check("first-period exit probability (P)", occ_p["q(x0)"], 0.400, 0.005)
    check("the naive 1/q answer, in call periods", 1 / occ_p["q(x0)"], 2.50, 0.02)
    check("every lot eventually exits when nu > 0", occ_p["P[exit]"], 1.0, 0.002)
    check("call premiums collected per lot (P)", occ_p["E[prem]"], 0.0678, 0.001)
    check("upside given away per lot (P)", occ_p["E[exitcost]"], 0.0634, 0.001)
    # The survival curve quoted in section 07, by call period.
    for months, want in [(3, 0.60), (6, 0.46), (12, 0.33), (24, 0.22),
                         (36, 0.18), (60, 0.13), (120, 0.08), (240, 0.04)]:
        check(f"still held after {months} months",
              occ_p["surv"][months // 3], want, 0.005)
    median_j = next(j for j, s in enumerate(occ_p["surv"]) if s < 0.5)
    check("median holding time, in call periods", median_j, 2, 0)

    # ------------------------------------------------------------------
    print("--- Section 08: inventory ---")
    e30 = economics(STD, "P", occ_p, horizon=30.0)
    check("arrival rate lambda (Standard)", e30["lambda"], 2.40, 0.01)
    check("E[I] over 30 years (Standard, P)", e30["I"], 4.89, 0.05)
    check("E[I] over 30 years (Standard, Q)",
          economics(STD, "Q", occ_q, horizon=30.0)["I"], 6.13, 0.06)
    occ_c = occupation(CON, "P")
    check("E[I] over 30 years (Conservative, P)",
          economics(CON, "P", occ_c, horizon=30.0)["I"], 2.35, 0.03)
    # The depth census: what the standing inventory is made of.
    EDGES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, float("inf")]
    shares, mean_x, mean_q = depth_census(STD, "P", EDGES, horizon=30.0)
    for i, want in enumerate([0.08, 0.06, 0.13, 0.07, 0.09, 0.13, 0.18, 0.27]):
        check(f"census share, bin {i + 1} of 8", shares[i], want, 0.006)
    check("inventory-weighted mean depth (30y)", mean_x, 0.367, 0.005)
    check("inventory-weighted exit probability (30y)", mean_q, 0.112, 0.003)
    check("share of held time deeper than 30%", shares[6] + shares[7], 0.45, 0.01)
    s_st, mx_st, mq_st = depth_census(STD, "P", EDGES)
    check("stationary inventory-weighted mean depth", mx_st, 0.775, 0.01)
    check("stationary inventory-weighted exit probability", mq_st, 0.062, 0.003)
    check("stationary share of held time deeper than 50%", s_st[7], 0.52, 0.01)
    check("capital per share of a lot 50% down in log terms", exp(0.5), 1.65, 0.01)

    # ------------------------------------------------------------------
    print("--- Section 09: returns and capital ---")
    for H, inv, mv, cost, econ, cash in [(5.0, 2.22, 2.41, 2.82, 0.0139, 0.0373),
                                         (10.0, 3.10, 3.29, 4.18, 0.0143, 0.0164),
                                         (30.0, 4.89, 5.08, 7.82, 0.0149, -0.0080)]:
        x = economics(STD, "P", occ_p, horizon=H)
        check(f"E[I] at {H:.0f}y", x["I"], inv, 0.02)
        check(f"market-value capital at {H:.0f}y", x["mv_capital"], mv, 0.02)
        check(f"cost-basis capital at {H:.0f}y", x["capital"], cost, 0.03)
        check(f"economic excess at {H:.0f}y", x["econ_excess"], econ, 0.0005)
        check(f"cash-view excess at {H:.0f}y", x["excess"], cash, 0.0005)
    # The wheel against simply owning the stock, on the same capital.
    m_p, _ = STD.world("P")
    buy_hold = m_p + STD.delta_net - STD.r
    check("buy-and-hold excess return", buy_hold, 0.01625, 1e-6)
    equity_frac = e30["I"] / e30["mv_capital"]
    check("wheel's equity fraction of capital", equity_frac, 0.963, 0.005)
    check("gap: wheel minus equity-adjusted buy-and-hold",
          e30["econ_excess"] - buy_hold * equity_frac, -0.0007, 0.0005)
    # The income decomposition quoted at the top of the section.
    cp_yr = e30["c_p"] / STD.cadence
    check("put premiums per year", cp_yr, 0.0753, 0.0005)
    check("call premiums per year", e30["premiums"] - cp_yr, 0.1495, 0.0010)
    check("dividends per year", e30["dividends"], 0.1038, 0.0005)
    check("Track A income per year", e30["income"], 0.3287, 0.0010)
    m_price, _ = STD.world("P")
    apprec = e30["I"] * m_price
    check("appreciation of held shares per year", apprec, 0.2199, 0.0010)
    check("mark loss at acquisition per year", e30["acq_loss"], 0.0795, 0.0005)
    check("upside surrendered per year", e30["call_away_loss"], 0.1393, 0.0010)
    check("the three nearly cancel",
          apprec - e30["acq_loss"] - e30["call_away_loss"], 0.0011, 0.0010)

    # The volatility-risk-premium sweep: how much edge is needed, and what it buys.
    for spread, prem, exc, gap in [(0.000, 0.2249, 0.0149, -0.0007),
                                   (0.005, 0.2358, 0.0171, 0.0015),
                                   (0.010, 0.2470, 0.0193, 0.0037),
                                   (0.020, 0.2699, 0.0238, 0.0082)]:
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
    for d, inv, mv, cost, exc in [(0.000, 3.72, 3.91, 5.32, 0.0185),
                                  (0.010, 4.14, 4.33, 6.15, 0.0171),
                                  (0.025, 4.89, 5.08, 7.82, 0.0149),
                                  (0.040, 5.79, 5.98, 10.14, 0.0128),
                                  (0.060, 7.23, 7.42, 14.68, 0.0100)]:
        cfg = Config(p_star=0.20, delta=d)
        xd = economics(cfg, "P", occupation(cfg, "P"), horizon=30.0)
        check(f"E[I] at delta = {d:.3f}", xd["I"], inv, 0.02)
        check(f"market capital at delta = {d:.3f}", xd["mv_capital"], mv, 0.02)
        check(f"cost capital at delta = {d:.3f}", xd["capital"], cost, 0.04)
        check(f"true excess at delta = {d:.3f}", xd["econ_excess"], exc, 0.0005)
        bh_d = (cfg.mu - cfg.r - cfg.withhold * d) * xd["I"] / xd["mv_capital"]
        check(f"gap vs buy-and-hold at delta = {d:.3f}",
              xd["econ_excess"] - bh_d, -0.0006, 0.0003)

    # The Conservative regime.
    xc = economics(CON, "P", occ_c, horizon=30.0)
    check("Conservative: lots held", xc["I"], 2.35, 0.02)
    check("Conservative: market capital", xc["mv_capital"], 2.54, 0.02)
    check("Conservative: cost capital", xc["capital"], 3.86, 0.03)
    check("Conservative: Track A income", xc["income"], 0.1573, 0.0010)
    check("Conservative: true excess", xc["econ_excess"], 0.0126, 0.0005)
    check("Conservative: cash-on-cost-basis", xc["excess"], -0.0093, 0.0005)
    check("Conservative: buy-and-hold benchmark",
          buy_hold * xc["I"] / xc["mv_capital"], 0.0151, 0.0005)

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
          trapped_fraction(hi_vol, "P"), 0.0759, 0.002)
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
          (STD.p_star / STD.cadence) * trapped_fraction(hi_vol, "P"), 0.18, 0.01)

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
        print("--- Far-grid stationary figures (slow) ---")
        far = dict(h=0.05, x_max=50.0, eps=1e-7)
        fp = occupation(STD, "P", **far)
        f = economics(STD, "P", fp)
        check("stationary E[T] (Standard, P), years", f["E[T]"], 4.18, 0.05)
        check("Siegmund closed form for E[T]", f["E[T]_siegmund"], 3.62, 0.05)
        check("stationary E[I] (Standard, P)", f["I"], 10.04, 0.10)
        check("years to reach 90% of stationary E[I]",
              time_to_fraction(STD, fp, 0.9), 94.0, 1.0)
        fq = occupation(STD, "Q", **far)
        g = economics(STD, "Q", fq)
        check("stationary E[T] (Standard, Q), years", g["E[T]"], 20.08, 0.20)
        check("stationary E[I] (Standard, Q)", g["I"], 48.20, 0.50)

    print()
    if FAILURES:
        raise SystemExit(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
