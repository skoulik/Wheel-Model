"""The model's own predictions, tested against the live account.

`live_ledger.py` compares the live account with the *market* — buy-and-hold of
the same names. This module compares it with the *model*: it feeds `model.py`
the live account's measured parameters and checks the spine link by link.

    entry law  ->  survival  ->  E[W]  ->  Little's law  ->  depth census

Every one of these tests needs the spot price on a particular day, which is why
none of them was possible from the cash statement alone.

    T1  the entry law      does the strike policy actually run produce the
                           assignment rate N(-d2) says it should?
    T2  the entry depth    is E[d | assignment] the depth assignments land at?
    T3  the depth census   is standing inventory distributed over depth the way
                           the killed walk says? -- the sharpest test, because
                           the census is what carries income and capital
    T4  q(x)               does the exit rate rise with shallowness as the
                           one-step exit probability predicts?
    T5  survival           does the holding-time distribution match first
                           passage, with the censoring handled properly?
                           (the open empirical half of TODO #9)

A note on drift, because it decides how to read T3 and T4. The window's realised
price drift was far above the article's mu = 7%, so the model is run twice: at
the article's assumption, which tests the *parameterisation*, and at the
realised drift, which tests the *mechanism*. Only the second is a fair test of
the depth process itself.

Run:  python code/model_vs_live.py            (from the repo root)
"""

import glob
import sys
from collections import defaultdict
from datetime import timedelta
from math import exp, log, sqrt

import prices
from analyze_statement import (STATEMENTS_GLOB, WHEEL_DESPITE_JUNK, build_lots,
                               junk_symbols, parse)
from live_ledger import realized_vol, wheel_universe
from model import (N, Config, assign_prob, depth_census, expected_drop,
                   occupation)

TRADING_DAYS = 252


def measure_parameters(positions, completed, open_lots, px, start, end):
    """The live account's parameters, measured rather than assumed."""
    # Volatility: inventory-weighted realised vol of the names actually held.
    lots = completed + open_lots
    wsum = vsum = 0.0
    for l in lots:
        ser = px.get(l["sym"])
        if ser is None:
            continue
        s = ser.close_on_or_before(l["in_day"])
        if not s:
            continue
        w = s * l["qty"]
        vsum += w * realized_vol(ser, min(end, l.get("out_day") or end), days=120)
        wsum += w
    sigma = vsum / wsum if wsum else 0.20

    # Realised drift, exposure-weighted over the days inventory was actually
    # held. Measuring it from the window's start instead would answer a
    # different question -- what the held names did over the whole window,
    # including the falls that caused the assignments in the first place --
    # and would feed the depth process a drift the lots never experienced.
    spans = [(l["sym"], l["in_day"], l.get("out_day") or end, l["qty"])
             for l in lots]
    num = den = 0.0
    for sym, d0, d1, qty in spans:
        ser = px.get(sym)
        if ser is None:
            continue
        day = d0
        while day < d1:
            nxt = day + timedelta(days=1)
            a, b = ser.close_on_or_before(day), ser.close_on_or_before(nxt)
            if a and b:
                num += a * qty * (b / a - 1)
                den += a * qty
            day = nxt
    # num/den is a per-calendar-day return over held days.
    drift = (num / den) * 365 if den else 0.0

    # Tenors: the medians the operator actually trades.
    def med(vals):
        vals = sorted(vals)
        return vals[len(vals) // 2] if vals else 0

    tau_p = med([(p["exp"] - p["open"]).days for p in positions
                 if p["right"] == "P"]) / 365
    tau_c = med([(p["exp"] - p["open"]).days for p in positions
                 if p["right"] == "C"]) / 365
    return sigma, drift, tau_p, tau_c


def live_config(sigma, tau_p, tau_c, mu, delta):
    """A Config carrying the live account's clocks and market."""
    n = max(1, round(tau_c / tau_p))
    return Config(p_star=0.09, tau_p=tau_p, n=n, sigma=sigma, mu=mu,
                  delta=delta, label="live")


# ----------------------------------------------------------------------
# T1: the entry law
# ----------------------------------------------------------------------
def test_entry_law(positions, px, universe, sigma_by_sym, drift):
    """Predicted assignment probability per put vs. what actually happened.

    For each put the model says P(assigned) = N(-d2) at the strike fraction
    k = K/S actually written. Summing those probabilities gives the number of
    assignments the model expects; the statement gives the number that
    occurred. This is the entry law tested directly, and it could not be done
    before because k needs the spot on the trade date.
    """
    rows = []
    for p in positions:
        if p["right"] != "P" or p["sym"] not in universe:
            continue
        ser = px.get(p["sym"])
        if ser is None:
            continue
        s0 = ser.close_on_or_before(p["open"])
        s1 = ser.close_on_or_before(p["exp"])
        tau = (p["exp"] - p["open"]).days / 365
        if not s0 or not s1 or tau <= 0:
            continue
        # Volatility as known ON THE TRADE DATE. Using a vol measured at the
        # end of the window would leak the outcome into the prediction.
        sig = realized_vol(ser, p["open"], days=120)
        k = p["strike"] / s0
        rows.append(dict(
            sym=p["sym"], qty=p["qty"], k=k, tau=tau, sigma=sig,
            p_pred=assign_prob(k, tau, sig, drift),
            itm=s1 < p["strike"],
            assigned=p["how"] == "assigned"))
    n = sum(r["qty"] for r in rows)
    pred = sum(r["p_pred"] * r["qty"] for r in rows)
    itm = sum(r["qty"] for r in rows if r["itm"])
    asg = sum(r["qty"] for r in rows if r["assigned"])
    print("\n=== T1: the entry law ===")
    print(f"  puts priced against a known spot: {len(rows)} positions, "
          f"{n} contracts")
    print(f"  model expects assigned          {pred:8.1f} contracts "
          f"({pred/n:.1%})")
    print(f"  finished below the strike       {itm:8.0f} contracts "
          f"({itm/n:.1%})   <- the model's own event")
    print(f"  actually assigned               {asg:8.0f} contracts "
          f"({asg/n:.1%})")
    # Calibration: does the predicted probability track the realised rate?
    print("  calibration by predicted probability:")
    buckets = [(0, .02), (.02, .05), (.05, .10), (.10, .20), (.20, 1.01)]
    for lo, hi in buckets:
        sub = [r for r in rows if lo <= r["p_pred"] < hi]
        if not sub:
            continue
        m = sum(r["qty"] for r in sub)
        print(f"    p_pred {lo:.0%}-{hi:.0%}: n={m:5.0f}  "
              f"mean predicted {sum(r['p_pred']*r['qty'] for r in sub)/m:.1%}  "
              f"realised ITM {sum(r['qty'] for r in sub if r['itm'])/m:.1%}  "
              f"assigned {sum(r['qty'] for r in sub if r['assigned'])/m:.1%}")
    return rows


# ----------------------------------------------------------------------
# T2: the entry depth
# ----------------------------------------------------------------------
def test_entry_depth(rows, C, drift):
    """E[d | assignment]: how far below the strike assignments actually land."""
    ds = sorted((1 - r["k_exit"]) for r in rows if r.get("k_exit"))
    print("\n=== T2: the entry depth ===")
    if not ds:
        print("  no priced assignments")
        return
    n = len(ds)
    print(f"  realised d = 1 - S(expiry)/K over {n} assigned lots:")
    print(f"    quartiles {ds[n//4]:+.3f} / {ds[n//2]:+.3f} / {ds[3*n//4]:+.3f}"
          f"   mean {sum(ds)/n:+.3f}")
    print(f"  model E[d | assignment] at the live clocks: "
          f"{expected_drop(C, 'P'):+.3f}")
    print(f"  live mean/median ratio {(sum(ds)/n)/max(ds[n//2],1e-9):.1f}x "
          f"-- the distribution is right-skewed, so the mean is carried by a "
          f"tail of crash assignments the lognormal has little room for")


# ----------------------------------------------------------------------
# T3: the depth census
# ----------------------------------------------------------------------
def lot_day_depths(completed, open_lots, px, end):
    """x = ln(K_c/S) for every lot on every day it was held.

    K_c is the lot's frozen basis, exactly the model's call strike. Depth is
    the model's one state variable, so this is the empirical census.
    """
    out = []
    lots = [(l["sym"], l["in_day"], l["out_day"], l["in_px"], l["qty"])
            for l in completed]
    lots += [(l["sym"], l["in_day"], None, l["in_px"], l["qty"])
             for l in open_lots]
    for sym, d0, d1, basis, qty in lots:
        ser = px.get(sym)
        if ser is None:
            continue
        day = d0
        stop = d1 or end
        while day <= stop:
            s = ser.close_on_or_before(day)
            if s:
                out.append((sym, day, log(basis / s), qty))
            day += timedelta(days=1)
    return out


def test_census(depths, C, horizon):
    """The empirical depth census against the killed walk's."""
    edges = [-9.0, 0.0, 0.02, 0.05, 0.10, 0.20, 0.35, 0.60, 9.0]
    labels = ["above strike", "0-2%", "2-5%", "5-10%", "10-20%",
              "20-35%", "35-60%", ">60%"]
    emp = [0.0] * (len(edges) - 1)
    for _, _, x, _ in depths:
        b = min(len(emp) - 1, max(0, sum(1 for e in edges[1:] if x >= e)))
        emp[b] += 1
    tot = sum(emp)
    emp = [e / tot for e in emp]

    # The model's census excludes x <= 0 by construction (the walk is killed
    # there), so compare on the live part and report the killed mass separately.
    model_edges = [0.0, 0.02, 0.05, 0.10, 0.20, 0.35, 0.60, 9.0]
    shares, mean_x, mean_q = depth_census(C, "P", model_edges, horizon=horizon)
    print("\n=== T3: the depth census ===")
    print(f"  {tot:,.0f} lot-days over {len({d for _, d, _, _ in depths})} "
          f"calendar days")
    print(f"  {'bin':>14s}  {'live':>8s}  {'model':>8s}")
    print(f"  {'above strike':>14s}  {emp[0]:7.1%}  {'(killed)':>8s}"
          f"   <- the call-grid tax: lots above their strike, not yet called")
    live_rest = sum(emp[1:])
    for lab, e, m in zip(labels[1:], emp[1:], shares):
        print(f"  {lab:>14s}  {e/live_rest:7.1%}  {m:7.1%}")
    emp_mean = sum(x for _, _, x, _ in depths if x > 0) / \
        max(sum(1 for _, _, x, _ in depths if x > 0), 1)
    print(f"  {'mean depth':>14s}  {emp_mean:7.3f}  {mean_x:7.3f}")
    return emp[0]


# ----------------------------------------------------------------------
# T4: q(x)
# ----------------------------------------------------------------------
def test_q_of_x(positions, px, universe, C, drift):
    """q(x) against the operator's actual calls.

    q(x) is the probability that a call written on a lot at depth x is
    exercised at its expiry, so the empirical analogue is one observation per
    call actually written: read x = ln(K_c/S) at the moment the call was sold,
    and score whether it was assigned.

    Two wrong ways were tried first and are recorded so they are not retried.
    Reading the depth on the day before the exit throws away almost every exit,
    because a lot that is called away is by definition ABOVE its strike that
    day. Sampling each lot every tau_c days from its own entry date is better
    but still wrong: it scores lot-periods the operator never wrote a call
    against, at tenors they never traded, and it made the model look 2x too
    aggressive when the fault was in the sampling.
    """
    rows = []
    for p in positions:
        if p["right"] != "C" or p["sym"] not in universe:
            continue
        ser = px.get(p["sym"])
        if ser is None:
            continue
        s0 = ser.close_on_or_before(p["open"])
        s1 = ser.close_on_or_before(p["exp"])
        tau = (p["exp"] - p["open"]).days / 365
        if not s0 or not s1 or tau <= 0:
            continue
        sig = realized_vol(ser, p["open"], days=120)
        x = log(p["strike"] / s0)
        nu = drift - sig * sig / 2
        rows.append(dict(x=x, qty=p["qty"], tau=tau,
                         q_pred=N((nu * tau - x) / (sig * sqrt(tau))),
                         assigned=p["how"] == "assigned",
                         itm=s1 > p["strike"]))
    n = sum(r["qty"] for r in rows)
    print("\n=== T4: q(x), against the calls actually written ===")
    print(f"  calls priced against a known spot: {len(rows)} positions, "
          f"{n} contracts (median tenor "
          f"{sorted(r['tau'] for r in rows)[len(rows)//2]*365:.0f} d)")
    print(f"  model expects exercised   {sum(r['q_pred']*r['qty'] for r in rows):7.1f}"
          f"  ({sum(r['q_pred']*r['qty'] for r in rows)/n:.1%})")
    print(f"  finished above the strike {sum(r['qty'] for r in rows if r['itm']):7.0f}"
          f"  ({sum(r['qty'] for r in rows if r['itm'])/n:.1%})")
    print(f"  actually assigned         {sum(r['qty'] for r in rows if r['assigned']):7.0f}"
          f"  ({sum(r['qty'] for r in rows if r['assigned'])/n:.1%})")
    edges = [-9, -0.02, 0.0, 0.02, 0.05, 0.10, 0.20, 9]
    labels = ["ITM (x<-2%)", "-2..0%", "0-2%", "2-5%", "5-10%", "10-20%", ">20%"]
    print(f"  {'depth at write':>14s}  {'n':>5s}  {'model q':>8s}  "
          f"{'realised':>9s}")
    for i, lab in enumerate(labels):
        sub = [r for r in rows if edges[i] <= r["x"] < edges[i + 1]]
        if not sub:
            continue
        m = sum(r["qty"] for r in sub)
        print(f"  {lab:>14s}  {m:5.0f}  "
              f"{sum(r['q_pred']*r['qty'] for r in sub)/m:8.3f}  "
              f"{sum(r['qty'] for r in sub if r['assigned'])/m:9.3f}")



# ----------------------------------------------------------------------
# T5: survival
# ----------------------------------------------------------------------
def test_survival(completed, open_lots, C, end):
    """Kaplan-Meier holding-time survival against the model's first passage."""
    events = sorted([((l["out_day"] - l["in_day"]).days, 1) for l in completed] +
                    [((end - l["in_day"]).days, 0) for l in open_lots])
    n_at_risk = len(events)
    surv, curve = 1.0, []
    i = 0
    while i < len(events):
        t = events[i][0]
        d = sum(1 for tt, e in events[i:] if tt == t and e == 1)
        c = sum(1 for tt, e in events[i:] if tt == t)
        if d:
            surv *= (1 - d / n_at_risk)
        curve.append((t, surv))
        n_at_risk -= c
        i += c
    occ = occupation(C, "P")
    S = occ["surv"]
    print("\n=== T5: holding-time survival ===")
    print(f"  {len(completed)} exits, {len(open_lots)} still held (censored)")
    print(f"  {'days':>6s}  {'live S(t)':>10s}  {'model S(t)':>11s}")
    for target in (30, 60, 90, 120, 180, 270, 365):
        live = next((s for t, s in reversed(curve) if t <= target), 1.0)
        j = int(target / 365 / C.tau_c)
        mod = S[j] if j < len(S) else S[-1]
        print(f"  {target:6d}  {live:10.1%}  {mod:11.1%}")
    naive = sorted((l["out_day"] - l["in_day"]).days for l in completed)
    km_med = next((t for t, s in curve if s <= 0.5), None)
    print(f"  median holding time: completed-lots-only "
          f"{naive[len(naive)//2]}d, Kaplan-Meier "
          f"{km_med if km_med is not None else 'not reached'}"
          f"{'d' if km_med is not None else ' (S never falls to 50%)'}")
    ET = occ["E[J]"] * C.tau_c
    print(f"  model mean holding time {ET:.2f} y ({ET*365:.0f} d), "
          f"E[J] = {occ['E[J]']:.2f} call periods")


def main():
    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB}")
    positions, stock_tx, divs, live = parse(paths)
    junk = junk_symbols(positions, stock_tx)
    universe = wheel_universe(positions, stock_tx, junk)
    completed, open_lots = build_lots(stock_tx, junk - WHEEL_DESPITE_JUNK)
    end = max(max(p["close"] for p in positions),
              max(d for d, *_ in stock_tx))
    start = min(min(p["open"] for p in positions),
                min(d for d, *_ in stock_tx))
    horizon = (end - start).days / 365.25
    px = prices.load_all(universe)

    sigma, drift, tau_p, tau_c = measure_parameters(
        positions, completed, open_lots, px, start, end)
    sigma_by_sym = {s: realized_vol(ser, end, days=120)
                    for s, ser in px.items()}
    delta = 0.025

    print(f"\nmeasured live parameters over {start} .. {end} ({horizon:.2f} y):")
    print(f"  sigma (inventory-weighted realised)   {sigma:.1%}")
    print(f"  realised price drift of held names    {drift:+.1%}")
    print(f"  median put tenor                      {tau_p*365:.0f} d")
    print(f"  median call tenor                     {tau_c*365:.0f} d  "
          f"(n = {max(1, round(tau_c/tau_p))})")

    # Two worlds: the article's assumption, and what actually happened.
    C_art = live_config(sigma, tau_p, tau_c, mu=0.07, delta=delta)
    C_real = live_config(sigma, tau_p, tau_c, mu=drift + delta, delta=delta)

    rows = test_entry_law(positions, px, universe, sigma_by_sym,
                          C_real.mu - delta)

    # Attach the realised exit ratio to assigned puts for T2.
    assigned_rows = []
    for p in positions:
        if p["right"] != "P" or p["how"] != "assigned" or p["sym"] not in universe:
            continue
        ser = px.get(p["sym"])
        s1 = ser.close_on_or_before(p["exp"]) if ser else None
        if s1:
            assigned_rows.append({"k_exit": s1 / p["strike"]})
    test_entry_depth(assigned_rows, C_real, drift)

    depths = lot_day_depths(completed, open_lots, px, end)
    print("\n--- run at the ARTICLE's mu = 7% (tests the parameterisation) ---")
    test_census(depths, C_art, horizon)
    print(f"\n--- run at the REALISED drift mu = {C_real.mu:.1%} "
          f"(tests the mechanism) ---")
    test_census(depths, C_real, horizon)
    test_q_of_x(positions, px, universe, C_real, C_real.mu - delta)
    test_survival(completed, open_lots, C_real, end)


if __name__ == "__main__":
    main()
