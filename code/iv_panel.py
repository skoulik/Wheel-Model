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

**Two clocks, and the panel reports both.** Implied volatility is inverted on a
**session** tenor -- trading days spanned over 252, counted off the real price
calendar -- because `forward_vol` annualises realised volatility over 252
sessions and the two have to meet on one clock. Reading a calendar tenor
against a session-annualised realised volatility is a units error, and it is
not a small one at the tenor this account trades: a four-calendar-day put is
five sessions, so `sigma*sqrt(tau)` differs between the readings by 1.35 and
the inversion hands back that much too much volatility. The error decays with
tenor, so it inflates **only the short leg** -- which is the shape of the
finding this panel was built to report, and the reason the correction was
worth making before the finding was quoted. The as-quoted **calendar** IV is
printed beside it, because that is the number that was on the broker's screen.

**Accuracy warning, stated up front.** The statement records no market prices,
so the spot used is the day's OPENING print while the trade happened at some
unknown moment intraday -- the operator writes within the hour after the bell,
which makes the open the closest available proxy and avoids pricing a morning
sale against that afternoon's close. Residual error remains: the trade was not
at the opening auction either. For the 25-day calls this is minor. For the
4-day puts written
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
from analyze_statement import (STATEMENTS_GLOB, build_lots,
                               excluded_symbols, parse)
from live_ledger import RF, wheel_universe
from model import bs_call, bs_put

IV_LO, IV_HI = 0.01, 3.0
MIN_PREMIUM = 0.02          # dollars per share; below this the quote is a tick
SESSIONS, CALENDAR = 252, 365
MIN_CELL = 5                # rows below this are reported as '-', never as a median

# Bucket edges, defined once because three reports cross them against each
# other. Tenor is bucketed on *calendar* days even though it is priced on
# sessions: "<=1wk" should mean what a reader thinks it means.
TENORS = ((0, 8, "<=1wk"), (8, 21, "1-3wk"),
          (21, 45, "~monthly"), (45, 400, "longer"))
MONEY = ((-9, -.10, "x < -10%"), (-.10, -.05, "-10..-5%"),
         (-.05, -.02, "-5..-2%"), (-.02, .02, "at the money"),
         (.02, .05, "+2..5%"), (.05, .10, "+5..10%"), (.10, 9, "x > +10%"))


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


def session_tenor(ser, a, exp):
    """Tenor in years on the session clock. Returns (tau, extrapolated).

    `a` is the session the entry was priced against, so the count spans the
    trade's own session through the expiry inclusive -- an option written at
    Monday's open and expiring Friday sees five sessions of diffusion.

    The count is **inclusive** of the trade's own session, and that is the one
    judgement call in the whole correction: sqrt(5/4) = 1.12 of implied
    volatility sits between an inclusive reading and an exclusive one on a
    weekly put, which is the same order as the finding being measured. It is
    settled from the data rather than by taste -- see `report_clock`, which
    measures what the entry day is actually worth: **0.65** of a
    close-to-close session over the cached history, because the contract is
    written at the open and so misses that day's overnight gap. The
    variance-true count is k - 1 + 0.65, so on a five-session put the
    inclusive k reads 29.0% against a variance-true 30.1% and the exclusive
    k - 1 reads 32.6%. Inclusive is both the nearer of the two conventions
    and the conservative one, since buying the contract more diffusion than
    it gets reports the account's premium as *less* rich than it was.

    `extrapolated` flags the one case the price history cannot answer: a
    contract still open at the last statement date can expire after the last
    cached session, and its tail is estimated at 252/365 sessions per calendar
    day. Counted and reported by the caller rather than silently absorbed.
    """
    last = ser.days[-1]
    if exp <= last:
        return ser.sessions_between(a, exp) / SESSIONS, False
    n = ser.sessions_between(a, last) + (exp - last).days * SESSIONS / CALENDAR
    return n / SESSIONS, True


def intraday_share(px, min_obs=200):
    """Var(open->close) / Var(close->close): what the entry day is worth.

    `sessions_between` counts the trade's own session as a whole one, but the
    contract is written at that session's *open*, so it collects only the
    day's intraday variance -- while `forward_vol` measures close-to-close,
    which also carries the overnight gap. The entry day is therefore worth
    less than a full session. Returns the median ratio across the panel's own
    names, so the correction is measured on the universe it is applied to.
    """
    out = []
    for ser in px.values():
        intraday, c2c = [], []
        prev = None
        for d in ser.days:
            o, c, a = ser.open(d), ser.close(d), ser.adj_close(d)
            if o and c:
                intraday.append(log(c / o))
            if prev and a:
                c2c.append(log(a / prev))
            if a:
                prev = a
        if len(intraday) < min_obs or len(c2c) < min_obs:
            continue

        def var(xs):
            m = sum(xs) / len(xs)
            return sum((z - m) ** 2 for z in xs) / (len(xs) - 1)

        vc = var(c2c)
        if vc > 0:
            out.append(var(intraday) / vc)
    return med(out), len(out)


def forward_vol(ser, a, b, min_obs=6):
    """Annualised close-to-close volatility realised over [a, b]."""
    h = [c for d, c in ser.window_adj(a, b)]
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
    a = ser.adj_on_or_before(day - timedelta(days=days))
    b = ser.adj_on_or_before(day)
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
        # Open, not close: the position was sold in the first hour of the
        # session, so that day's opening print is the spot it was written
        # against. See prices.Series.open().
        s0 = ser.open_on_or_before(p["open"])
        # The spot and the tenor come off the same session, or a trade day
        # inferred one out moves them independently -- on a five-session
        # option, by 20% of the tenor.
        a = ser.session_on_or_before(p["open"])
        tau_cal = (p["exp"] - p["open"]).days / CALENDAR
        prem = p["open_px"]
        if not s0 or a is None or tau_cal <= 0:
            failed["no spot / zero tenor"] += 1
            continue
        tau, extrapolated = session_tenor(ser, a, p["exp"])
        if tau <= 0:
            failed["no spot / zero tenor"] += 1
            continue
        if prem < MIN_PREMIUM:
            failed["premium below a tick"] += 1
            continue
        iv = implied_vol(p["right"], s0, p["strike"], tau, prem)
        if iv is None:
            failed["outside 1%-300%"] += 1
            continue
        if extrapolated:
            failed["(kept) expiry past the price history, tail estimated"] += 1
        # The as-quoted reading, kept beside the priced one so the panel still
        # ties to what the broker's screen showed. It inverts a shorter tenor
        # and so runs higher; it may fail the 300% ceiling where the session
        # reading does not, which is itself the size of the mismatch.
        iv_cal = implied_vol(p["right"], s0, p["strike"], tau_cal, prem)
        if iv_cal is None:
            failed["(kept) calendar reading above 300%"] += 1
        rows.append(dict(
            sym=p["sym"], right=p["right"], qty=p["qty"], day=p["open"],
            tau=tau, tau_cal=tau_cal, iv=iv, iv_cal=iv_cal,
            sessions=tau * SESSIONS, prem=prem,
            spot=s0, strike=p["strike"],
            moneyness=log(p["strike"] / s0),
            fwd_vol=forward_vol(ser, p["open"], p["exp"]),
            fwd21=forward_vol(ser, p["open"], p["open"] + timedelta(days=21)),
            ret20=trailing_return(ser, p["open"])))
    return rows, failed


def med(vals):
    vals = sorted(v for v in vals if v is not None)
    return vals[len(vals) // 2] if vals else None


def bucket(rows, right, tlo=0, thi=400, mlo=-9, mhi=9):
    """Rows for one leg, tenor band and moneyness band.

    Tenor is selected on the *calendar* day count even though it is priced on
    sessions: "<=1wk" has to mean the week a reader means, and moving the
    bucket edges as well as the pricing would make the before/after
    incomparable for two reasons at once.
    """
    return [r for r in rows if r["right"] == right
            and tlo <= r["tau_cal"] * CALENDAR < thi
            and mlo <= r["moneyness"] < mhi]


def spread(sub):
    """(n, median IV, median RV, IV - RV) for a cell, or None if too thin."""
    iv, rv = med([r["iv"] for r in sub]), med([r["fwd21"] for r in sub])
    if len(sub) < MIN_CELL or iv is None or rv is None:
        return None
    return len(sub), iv, rv, iv - rv


def report_levels(rows):
    print("\n=== implied volatility by leg and tenor ===")
    print(f"  {'leg':>5s} {'tenor':>10s} {'n':>5s} {'IV':>8s} "
          f"{'as quoted':>10s} {'median |x|':>11s} {'med fwd RV':>11s} "
          f"{'IV - RV':>9s}")
    for right, label in (("P", "puts"), ("C", "calls")):
        for lo, hi, name in TENORS + ((0, 400, "ALL TENORS"),):
            sub = bucket(rows, right, lo, hi)
            got = spread(sub)
            if got is None:
                continue
            n, iv, rv, gap = got
            cal = med([r["iv_cal"] for r in sub])
            print(f"  {label:>5s} {name:>10s} {n:5d} {iv:8.1%} "
                  f"{f'{cal:.1%}' if cal else '-':>10s} "
                  f"{med([abs(r['moneyness']) for r in sub]):11.1%} "
                  f"{rv:11.1%} {gap:+9.1%}")
    print("  IV is inverted on the session clock (trading days spanned / 252),"
          "\n  which is the clock fwd RV is annualised on. 'as quoted' is the "
          "same\n  premium read on a calendar tenor: what the screen showed, "
          "and what\n  this panel reported before the clock was fixed.")
    print("  fwd RV is realised over the 21 days after the sale, a stable "
          "window;\n  matching each option's own tenor is too short to "
          "estimate for the 4-day puts.")


def report_skew(rows):
    """IV against moneyness, the asymmetry the single sigma_IV hides."""
    print("\n=== the skew: IV against moneyness ===")
    print("  moneyness x = ln(K/S); x < 0 is a strike below spot")
    print(f"  {'bucket':>14s} {'puts n':>7s} {'put IV':>8s} "
          f"{'calls n':>8s} {'call IV':>8s}")
    for lo, hi, name in MONEY:
        ps = bucket(rows, "P", mlo=lo, mhi=hi)
        cs = bucket(rows, "C", mlo=lo, mhi=hi)
        if not ps and not cs:
            continue
        pi = med([r["iv"] for r in ps])
        ci = med([r["iv"] for r in cs])
        print(f"  {name:>14s} {len(ps):7d} "
              f"{f'{pi:.1%}' if pi else '-':>8s} {len(cs):8d} "
              f"{f'{ci:.1%}' if ci else '-':>8s}")
    print("  Levels only, and the legs sit at different tenors -- so this "
          "table\n  cannot separate skew from tenor. That is what the "
          "cross-tab below is\n  for, and it is why the put/call gap here is "
          "not a skew measurement.")


def report_cross(rows):
    """IV - RV by leg, moneyness and tenor: the cross the panel never took.

    The two tables above report IV - RV by tenor and IV by moneyness and never
    cross them, so a skew effect and a tenor effect cannot be told apart --
    which is exactly how a clock artefact that scales with tenor survived
    being read as a skew finding.

    The **call leg** is the one that separates, and by construction: the call
    strike is frozen at the lot's basis, so a shallow lot writes a near-money
    call and a deep one writes a far one, and one leg populates the whole
    moneyness range at a roughly common tenor. The **put leg** has no
    at-the-money cell by design and never will -- the operator sells puts out
    of the money -- so the near-money puts that do appear are accidents and
    should be read as such.
    """
    print("\n=== IV - RV by leg, moneyness and tenor (session clock) ===")
    print("  cells are n and median IV - median RV; '-' where n < "
          f"{MIN_CELL}")
    cols = TENORS + ((0, 400, "all"),)
    print(f"  {'moneyness':>15s}" + "".join(f"{c[2]:>13s}" for c in cols))
    for right, label in (("P", "puts"), ("C", "calls")):
        print(f"  {label}:")
        for mlo, mhi, mname in MONEY:
            cells = []
            for tlo, thi, _ in cols:
                got = spread(bucket(rows, right, tlo, thi, mlo, mhi))
                cells.append(f"{got[0]:5d}{got[3]:+8.1%}" if got
                             else f"{'-':>13s}")
            if all(c.strip() == "-" for c in cells):
                continue
            print(f"  {mname:>15s}" + "".join(cells))


def report_clock(rows, px):
    """The session count's own error bar, on the leg where it bites.

    Everything the panel now reports rests on counting sessions inclusively,
    and a weekly put has only five of them -- so a reader is entitled to ask
    what the next-door convention would have said. This prices the shortest
    put bucket under all three counts. The spread between them is the honest
    uncertainty on the headline number, and it is smaller than the correction
    it is qualifying.
    """
    r, n_names = intraday_share(px)
    sub = bucket(rows, "P", 0, 8)
    rv = med([x["fwd21"] for x in sub])
    print("\n=== what the session count is worth ===")
    if r is None or rv is None or len(sub) < MIN_CELL:
        print("  too few names or contracts to measure; skipped")
        return
    print(f"  an entry-day open->close move carries {r:.2f} of a "
          f"close-to-close session's\n  variance, measured across {n_names} "
          "names -- the contract is written at the\n  open, so it misses that "
          "day's overnight gap. A k-session option is worth\n  k - 1 + "
          f"{r:.2f} sessions of diffusion.")
    print(f"\n  puts <=1wk (n={len(sub)}), median RV {rv:.1%}, priced four ways:")
    print(f"  {'session count':>24s} {'median IV':>10s} {'IV - RV':>9s}")
    for label, k_of in (("exclusive, k - 1", lambda k: k - 1),
                        (f"variance-true, k-1+{r:.2f}", lambda k: k - 1 + r),
                        ("inclusive, k  <- used", lambda k: k),
                        ("calendar days / 365", None)):
        if k_of is None:
            iv = med([x["iv_cal"] for x in sub])
        else:
            ivs = []
            for x in sub:
                tau = k_of(x["sessions"]) / SESSIONS
                if tau > 0:
                    ivs.append(implied_vol(x["right"], x["spot"], x["strike"],
                                           tau, x["prem"]))
            iv = med(ivs)
        if iv is None:
            continue
        print(f"  {label:>24s} {iv:10.1%} {iv - rv:+9.1%}")
    print("  The inclusive count is the nearest of the three to variance-true "
          "and\n  errs the conservative way: it buys the contract more "
          "diffusion than it\n  gets, so it reports the account's premium as "
          "less rich than it was.")


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
    excluded = excluded_symbols()
    universe = wheel_universe(positions, stock_tx, excluded)
    completed, open_lots = build_lots(stock_tx, excluded)
    px = prices.load_all(universe)

    rows, failed = build_panel(positions, live, px, universe)
    n = sum(r["qty"] for r in rows)
    print(f"\nIV panel: {len(rows)} contracts inverted ({n} counting "
          f"multiplicity)")
    for k, v in sorted(failed.items(), key=lambda kv: -kv[1]):
        print(f"  not inverted, {k}: {v}")

    report_clock(rows, px)
    report_levels(rows)
    report_skew(rows)
    report_cross(rows)
    report_depth(rows, completed + open_lots, px)
    report_leverage(rows)


if __name__ == "__main__":
    main()
