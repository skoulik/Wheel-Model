"""The trade log as an option-price panel: implied volatility, measured.

Every contract the operator wrote is a quote. With the spot price known
(`prices.py`) each one becomes an implied-volatility observation at a known
moneyness and tenor, so 2,112 contracts turn into an IV panel covering 14
months and ~130 names. Three things the article currently assumes then become
measurements:

  * **the volatility risk premium.** `Config.iv_spread` defaults to 0 -- the
    article deliberately strips the strategy's documented edge out of its
    headline results and reports the break-even spread instead (essentially
    zero, with every volatility point worth ~45bp). What spread the operator
    actually harvests is an empirical question, answered here by comparing IV
    at the moment of sale with the volatility subsequently realised.
  * **the skew.** The article carries a single sigma_IV, and TODO #4 records
    that the puts sold are systematically richer than the calls sold. Measured
    here per leg and per moneyness.
  * **sigma_IV as a function of depth.** The open question behind all of this:
    implied vol rises when a stock falls, and a wheel lot is deep precisely
    because its stock fell -- so deep lots might earn richer call premiums than
    the constant-sigma model books. But the call on a deep lot is far out of
    the money, and far-OTM calls sit LOWER on the smile. The two effects fight
    and the sign is not obvious a priori. The operator's own deep-lot call
    sales settle it, which is why this is measured before any functional form
    for sigma_IV(x) is written into the model.

**Accuracy warning, stated up front.** The statement records no market prices,
so the spot used is the day's CLOSE while the trade happened at some unknown
moment intraday. For the 25-day calls this is minor. For the 4-day puts written
3% out of the money at 0.26% of strike it is not: vega is tiny there, so a 1%
error in the spot moves implied vol by a lot. Per-contract IVs in the short-put
bucket should be read as noisy; medians over hundreds of contracts survive,
individual values do not. Failures to invert are counted and reported rather
than dropped silently.

Run:  python code/iv_panel.py            (from the repo root)
"""

import glob
import sys
from collections import defaultdict
from math import log, sqrt

import prices
from analyze_statement import (STATEMENTS_GLOB, WHEEL_DESPITE_JUNK, build_lots,
                               junk_symbols, parse)
from live_ledger import RF, wheel_universe
from model import bs_call, bs_put

IV_LO, IV_HI = 0.01, 3.0
MIN_PREMIUM = 0.02          # dollars per share; below this the quote is a tick


def implied_vol(right, spot, strike, tau, premium, r=RF, delta=0.0):
    """Invert Black-Scholes for sigma by bisection. None if out of range."""
    def price(sig):
        if right == "P":
            return bs_put(strike / spot, tau, sig, r, delta) * spot
        return bs_call(spot, strike, tau, sig, r, delta)

    lo, hi = IV_LO, IV_HI
    if not (price(lo) <= premium <= price(hi)):
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if price(mid) < premium:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def forward_vol(ser, a, b, min_obs=6):
    """Annualised close-to-close volatility realised over [a, b]."""
    h = [c for d, c in ser.window(a, b)]
    if len(h) < min_obs:
        return None
    rets = [(y / x) - 1 for x, y in zip(h, h[1:]) if x]
    if len(rets) < min_obs - 1:
        return None
    m = sum(rets) / len(rets)
    v = sum((z - m) ** 2 for z in rets) / (len(rets) - 1)
    return (v * 252) ** 0.5


def trailing_return(ser, day, days=20):
    """Log return of the name over the `days` calendar days before `day`."""
    from datetime import timedelta
    a = ser.close_on_or_before(day - timedelta(days=days))
    b = ser.close_on_or_before(day)
    return log(b / a) if a and b else None


def build_panel(positions, live, px, universe):
    """One row per contract: implied vol, moneyness, tenor, context."""
    rows, failed = [], defaultdict(int)
    from datetime import timedelta
    for p in list(positions) + list(live):
        if p["sym"] not in universe:
            continue
        ser = px.get(p["sym"])
        if ser is None:
            continue
        s0 = ser.close_on_or_before(p["open"])
        tau = (p["exp"] - p["open"]).days / 365
        prem = p["open_px"]
        if not s0 or tau <= 0:
            failed["no spot / zero tenor"] += 1
            continue
        if prem < MIN_PREMIUM:
            failed["premium below a tick"] += 1
            continue
        iv = implied_vol(p["right"], s0, p["strike"], tau, prem)
        if iv is None:
            failed["outside 1%-300%"] += 1
            continue
        rows.append(dict(
            sym=p["sym"], right=p["right"], qty=p["qty"], day=p["open"],
            tau=tau, iv=iv, spot=s0, strike=p["strike"],
            moneyness=log(p["strike"] / s0),
            fwd_vol=forward_vol(ser, p["open"], p["exp"]),
            fwd21=forward_vol(ser, p["open"], p["open"] + timedelta(days=21)),
            ret20=trailing_return(ser, p["open"])))
    return rows, failed


def med(vals):
    vals = sorted(v for v in vals if v is not None)
    return vals[len(vals) // 2] if vals else None


def report_levels(rows):
    print("\n=== implied volatility by leg and tenor ===")
    print(f"  {'leg':>4s} {'tenor':>10s} {'n':>5s} {'median IV':>10s} "
          f"{'median |x|':>11s} {'med fwd RV':>11s} {'IV - RV':>9s}")
    for right, label in (("P", "puts"), ("C", "calls")):
        for lo, hi, name in ((0, 8, "<=1wk"), (8, 21, "1-3wk"),
                             (21, 45, "~monthly"), (45, 400, "longer")):
            sub = [r for r in rows if r["right"] == right
                   and lo <= r["tau"] * 365 < hi]
            if len(sub) < 5:
                continue
            iv, rv = med([r["iv"] for r in sub]), med([r["fwd21"] for r in sub])
            print(f"  {label:>4s} {name:>10s} {len(sub):5d} {iv:10.1%} "
                  f"{med([abs(r['moneyness']) for r in sub]):11.1%} "
                  f"{rv:11.1%} {iv - rv:+9.1%}")
    print("  fwd RV is realised over the 21 days after the sale, a stable "
          "window;\n  matching each option's own tenor is too short to "
          "estimate for the 4-day puts.")


def report_skew(rows):
    """IV against moneyness, the asymmetry the single sigma_IV hides."""
    print("\n=== the skew: IV against moneyness ===")
    print("  moneyness x = ln(K/S); x < 0 is a strike below spot")
    print(f"  {'bucket':>14s} {'puts n':>7s} {'put IV':>8s} "
          f"{'calls n':>8s} {'call IV':>8s}")
    edges = [(-9, -.10, "x < -10%"), (-.10, -.05, "-10..-5%"),
             (-.05, -.02, "-5..-2%"), (-.02, .02, "at the money"),
             (.02, .05, "+2..5%"), (.05, .10, "+5..10%"), (.10, 9, "x > +10%")]
    for lo, hi, name in edges:
        ps = [r for r in rows if r["right"] == "P" and lo <= r["moneyness"] < hi]
        cs = [r for r in rows if r["right"] == "C" and lo <= r["moneyness"] < hi]
        if not ps and not cs:
            continue
        pi = med([r["iv"] for r in ps])
        ci = med([r["iv"] for r in cs])
        print(f"  {name:>14s} {len(ps):7d} "
              f"{f'{pi:.1%}' if pi else '-':>8s} {len(cs):8d} "
              f"{f'{ci:.1%}' if ci else '-':>8s}")


def report_depth(rows, lots, px):
    """IV on calls written against a held lot, by the lot's depth.

    The question the model needs answered: as a lot gets deeper, does the call
    it sells get quoted at a higher or a lower implied volatility?
    """
    by_sym = defaultdict(list)
    for l in lots:
        by_sym[l["sym"]].append(l)
    print("\n=== sigma_IV against lot depth (calls on held inventory) ===")
    print(f"  {'depth x':>12s} {'n':>5s} {'median IV':>10s} "
          f"{'rel. to name':>13s}")
    name_med = {}
    for sym in {r["sym"] for r in rows}:
        vals = [r["iv"] for r in rows if r["sym"] == sym]
        if len(vals) >= 4:
            name_med[sym] = med(vals)
    buckets = defaultdict(list)
    edges = [(0, .02, "0-2%"), (.02, .05, "2-5%"), (.05, .10, "5-10%"),
             (.10, .20, "10-20%"), (.20, .35, "20-35%"), (.35, 9, ">35%")]
    for r in rows:
        if r["right"] != "C":
            continue
        held = [l for l in by_sym.get(r["sym"], [])
                if l["in_day"] <= r["day"] and
                (l.get("out_day") is None or r["day"] < l["out_day"])]
        if not held:
            continue
        # Depth of the lot this call is covering: nearest basis to the strike.
        lot = min(held, key=lambda l: abs(l["in_px"] - r["strike"]))
        x = log(lot["in_px"] / r["spot"])
        if x <= 0:
            continue
        for lo, hi, name in edges:
            if lo <= x < hi:
                buckets[name].append(r)
                break
    for _, _, name in edges:
        sub = buckets.get(name, [])
        if len(sub) < 4:
            continue
        rel = [r["iv"] / name_med[r["sym"]] for r in sub if r["sym"] in name_med]
        print(f"  {name:>12s} {len(sub):5d} {med([r['iv'] for r in sub]):10.1%} "
              f"{f'{med(rel):.2f}x' if rel else '-':>13s}")
    print("  'rel. to name' divides by that name's own median IV, so the "
          "column\n  isolates the depth effect from the fact that volatile "
          "names get assigned.")


def report_leverage(rows):
    """Does IV rise when the stock has just fallen? The leverage effect."""
    name_med = {}
    for sym in {r["sym"] for r in rows}:
        vals = [r["iv"] for r in rows if r["sym"] == sym]
        if len(vals) >= 4:
            name_med[sym] = med(vals)
    print("\n=== the leverage effect: IV against the last 20 days' return ===")
    print(f"  {'trailing return':>16s} {'n':>5s} {'median IV':>10s} "
          f"{'rel. to name':>13s}")
    edges = [(-9, -.15, "fell >15%"), (-.15, -.07, "fell 7-15%"),
             (-.07, -.02, "fell 2-7%"), (-.02, .02, "flat"),
             (.02, .07, "rose 2-7%"), (.07, 9, "rose >7%")]
    for lo, hi, name in edges:
        sub = [r for r in rows if r["ret20"] is not None
               and lo <= r["ret20"] < hi and r["sym"] in name_med]
        if len(sub) < 5:
            continue
        print(f"  {name:>16s} {len(sub):5d} {med([r['iv'] for r in sub]):10.1%} "
              f"{med([r['iv']/name_med[r['sym']] for r in sub]):12.2f}x")


def main():
    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB}")
    positions, stock_tx, divs, live = parse(paths)
    junk = junk_symbols(positions, stock_tx)
    universe = wheel_universe(positions, stock_tx, junk)
    completed, open_lots = build_lots(stock_tx, junk - WHEEL_DESPITE_JUNK)
    px = prices.load_all(universe)

    rows, failed = build_panel(positions, live, px, universe)
    n = sum(r["qty"] for r in rows)
    print(f"\nIV panel: {len(rows)} contracts inverted ({n} counting "
          f"multiplicity)")
    for k, v in sorted(failed.items(), key=lambda kv: -kv[1]):
        print(f"  not inverted, {k}: {v}")

    report_levels(rows)
    report_skew(rows)
    report_depth(rows, completed + open_lots, px)
    report_leverage(rows)


if __name__ == "__main__":
    main()
