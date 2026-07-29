"""The live account restated in the article's ledgers.

The statements are a cash ledger, so unaided they can only produce Track A on a
cost basis -- the one number [the returns section](#sec:returns) warns is "too
flattering at the start, too damning later". This module marks the account to
market with `prices.py` and restates it in Track B, which is the only ledger in
which the live result and the model's prediction are the same kind of object.

The decomposition is the live analogue of eq:econ-pnl, and it is exact rather
than a fit. A wheel lot is a long equity position wrapped in a short option
overlay, so over any window

    wheel economic P&L  =  D + A - B - C

    A  option premium, net of commissions and buy-backs, on every contract
       written in the window (open contracts carry an offsetting mark)
    B  mark loss at acquisition: the operator pays the strike K while the
       market offers S(t0) < K, so (K - S(t0)) is lost the moment the put is
       assigned -- invisible to Track A, which books the purchase at K
    C  upside surrendered at call-away: shares leave at K_c while the market
       is at S(t1) > K_c -- also invisible to Track A, which sees a round trip
       at the same price
    D  equity P&L of the shares actually held while they were held: price
       change plus dividends received, open lots marked at the window's end

D is precisely what a buy-and-hold position in *the same names, bought at the
same moments, in the same size* would have earned. So

    excess over same-names buy-and-hold  =  A - B - C

with no capital weighting needed to get its sign, and dividends cancelling out
of it entirely (both sides receive them). That is the number the article's
verdict is about: at fair option prices A - B - C should be approximately zero,
and whatever it is instead is the live account's option-overlay edge.

Two benchmarks are reported, and the gap between them is the point:

  * **same names, same times** (D) neutralises entry selection, because its
    weights are the operator's own entries. Excess against it isolates the
    option overlay -- the volatility risk premium, the skew, and the
    assignment/call-away mechanics.
  * **the traded universe, equal weight** keeps selection in. The difference
    between the two excesses is the contribution of *which names, when* --
    TODO #14's "attractive price" lever, measured without fitting anything.

Capital is Track B capital of eq:capital: inventory at market value plus margin
on the live puts. The margin convention is the open question of TODO #6, so the
report gives capital with and without it.

Run:  python code/live_ledger.py              (from the repo root)
      python code/live_ledger.py --daily      (capital/exposure path)
      python code/live_ledger.py --bootstrap  (interval and concentration)
"""

import argparse
import glob
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

import prices
from analyze_statement import (STATEMENTS_GLOB, build_lots,
                               excluded_symbols, parse)
from model import bs_call, bs_put

MARGIN = 0.20          # Track B margin on a short put, matching Config.gamma_p
RF = 0.05              # risk-free rate, matching the article's r
MARK_SIGMA = 0.25      # implied vol for marking still-open short options


def wheel_universe(positions, stock_tx, excluded):
    """Symbols the wheel operated on.

    parse() has already dropped EXCLUDED_LIST, so `traded` is in-universe by
    construction and the subtraction below is a guard, not a filter.
    """
    traded = {p["sym"] for p in positions} | {t[1] for t in stock_tx}
    return traded - excluded


def realized_vol(series, end, days=60):
    """Annualised close-to-close volatility over the trailing `days` sessions."""
    # Adjusted: a ratio of two as-traded prices is meaningless across a split.
    hist = [c for d, c in series.window_adj(end - timedelta(days=days * 2), end)]
    if len(hist) < 10:
        return MARK_SIGMA
    rets = [(b / a) - 1 for a, b in zip(hist, hist[1:]) if a]
    if len(rets) < 5:
        return MARK_SIGMA
    mean = sum(rets) / len(rets)
    var = sum((x - mean) ** 2 for x in rets) / (len(rets) - 1)
    return (var * 252) ** 0.5


def excess_units(positions, live, universe, px, end, b_rows, c_rows):
    """The excess A - B - C, split into name-attributable pieces.

    Every component of A, B and C carries a symbol, so the whole of the excess
    can be attributed without residue -- which the caller checks. The pieces
    are what the bootstrap resamples and what the concentration report ranks.

    Returned as (units, by_name): `units` is the finer split -- option cash
    aggregated per name, but B and C one row per lot -- and `by_name` sums
    everything to the symbol.
    """
    opt = defaultdict(float)
    for p in positions:
        if p["sym"] not in universe:
            continue
        opt[p["sym"]] += (p["qty"] * p["open_px"] * 100 + p["comm"]
                          + p.get("close_comm", 0.0)
                          - (p["qty"] * p["close_px"] * 100
                             if p["how"] == "closed" else 0.0))
    for o in live:
        if o["sym"] not in universe:
            continue
        opt[o["sym"]] += o["qty"] * o["open_px"] * 100 + o["comm"]
        ser = px.get(o["sym"])
        s = ser.close_on_or_before(end) if ser else None
        tau = (o["exp"] - end).days / 365
        if s is None or tau <= 0:
            continue
        k = o["strike"]
        val = (bs_put(k / s, tau, realized_vol(ser, end), RF) * s
               if o["right"] == "P"
               else bs_call(s / k, 1.0, tau, realized_vol(ser, end), RF) * k)
        opt[o["sym"]] -= o["qty"] * val * 100

    units = [(sym, v) for sym, v in opt.items()]
    units += [(sym, -loss) for sym, _d, _k, _s, loss in b_rows]
    units += [(sym, -give) for sym, _d, _k, _s, give in c_rows]
    by_name = defaultdict(float)
    for sym, v in units:
        by_name[sym] += v
    return units, dict(by_name)


def bootstrap_excess(units, capital, years, n_iter=20000, seed=20260727):
    """Resampling interval for the annualised excess.

    Drawn with replacement from `units`, which the caller chooses: the lot-level
    split, or the same values clustered by symbol. Clustering is the honest
    default -- a name's contracts and lots are the same bet repeated, so
    treating them as independent draws understates the interval -- and both are
    reported because the article's earlier figure used the finer split.

    Capital and the window length are held at their full-sample values. They are
    not properties of the resampled positions, and letting them move would mix a
    wobble in the capital base into an interval about the overlay.
    """
    rng = random.Random(seed)
    k = len(units)
    draws = sorted(sum(units[rng.randrange(k)][1] for _ in range(k))
                   / capital / years for _ in range(n_iter))
    return (draws[int(0.05 * n_iter)], draws[int(0.95 * n_iter)],
            sum(1 for v in draws if v < 0) / n_iter)


def option_cash(positions, live, universe, end, px):
    """A: net option cash, plus the mark on contracts still open at `end`.

    Premium received is cash in hand even on a contract that has not expired,
    but such a contract is also a live liability. Both are reported so the
    reader can see how much of A is unsettled.
    """
    received = commissions = bought_back = 0.0
    by_leg = defaultdict(float)
    for p in positions:
        if p["sym"] not in universe:
            continue
        received += p["qty"] * p["open_px"] * 100
        commissions += p["comm"] + p.get("close_comm", 0.0)
        by_leg[p["right"]] += p["qty"] * p["open_px"] * 100
        if p["how"] == "closed":
            bought_back -= p["qty"] * p["close_px"] * 100
    live_prem = live_mark = 0.0
    unmarked = []
    for o in live:
        if o["sym"] not in universe:
            continue
        live_prem += o["qty"] * o["open_px"] * 100
        commissions += o["comm"]
        by_leg[o["right"]] += o["qty"] * o["open_px"] * 100
        ser = px.get(o["sym"])
        s = ser.close_on_or_before(end) if ser else None
        tau = (o["exp"] - end).days / 365
        if s is None or tau <= 0:
            unmarked.append(o["sym"])
            continue
        sigma = realized_vol(ser, end)
        k = o["strike"]
        val = (bs_put(k / s, tau, sigma, RF) * s if o["right"] == "P"
               else bs_call(s / k, 1.0, tau, sigma, RF) * k)
        live_mark -= o["qty"] * val * 100     # short: a liability
    return dict(received=received, live_prem=live_prem, commissions=commissions,
                bought_back=bought_back, live_mark=live_mark, by_leg=dict(by_leg),
                unmarked=unmarked,
                total=received + live_prem + commissions + bought_back + live_mark)


def acquisition_and_exit(completed, open_lots, px, end):
    """B and C: the two economic events Track A cannot see.

    B is measured at the put's expiry, when assignment happens and the shares
    arrive at the strike. C is measured at the call's expiry. Both use the
    as-traded close on the event day, which is the price the exercise decision
    was made against.
    """
    B = C = 0.0
    b_rows, c_rows, missing = [], [], []
    for lot in completed + open_lots:
        ser = px.get(lot["sym"])
        s = ser.close_on_or_before(lot["in_day"]) if ser else None
        if s is None:
            missing.append((lot["sym"], lot["in_day"]))
            continue
        loss = (lot["in_px"] - s) * lot["qty"]
        B += loss
        b_rows.append((lot["sym"], lot["in_day"], lot["in_px"], s, loss))
    for lot in completed:
        ser = px.get(lot["sym"])
        s = ser.close_on_or_before(lot["out_day"]) if ser else None
        if s is None:
            missing.append((lot["sym"], lot["out_day"]))
            continue
        give = (s - lot["out_px"]) * lot["qty"]
        C += give
        c_rows.append((lot["sym"], lot["out_day"], lot["out_px"], s, give))
    return B, C, b_rows, c_rows, missing


def equity_pnl(completed, open_lots, px, end, div_by_sym):
    """D: what the shares themselves did while they were held."""
    price_pnl = 0.0
    rows = []
    for lot in completed:
        ser = px.get(lot["sym"])
        if ser is None:
            continue
        s0 = ser.close_on_or_before(lot["in_day"])
        s1 = ser.close_on_or_before(lot["out_day"])
        if s0 is None or s1 is None:
            continue
        price_pnl += (s1 - s0) * lot["qty"]
        rows.append((lot["sym"], "closed", (s1 - s0) * lot["qty"]))
    for lot in open_lots:
        ser = px.get(lot["sym"])
        if ser is None:
            continue
        s0 = ser.close_on_or_before(lot["in_day"])
        s1 = ser.close_on_or_before(end)
        if s0 is None or s1 is None:
            continue
        price_pnl += (s1 - s0) * lot["qty"]
        rows.append((lot["sym"], "open", (s1 - s0) * lot["qty"]))
    return price_pnl, sum(div_by_sym.values()), rows


def wheel_dividends(divs, stock_tx, universe):
    """Net dividend cash on reconstructed wheel inventory (receipts, tax, fees)."""
    events = defaultdict(list)
    for day, sym, qty, _, _ in sorted(stock_tx):
        events[sym].append((day, qty))

    def held(sym, day):
        return sum(q for d, q in events[sym] if d <= day)

    out = defaultdict(float)
    for r in divs:
        if r["sym"] not in universe or held(r["sym"], r["day"]) <= 0:
            continue
        out[r["sym"]] += r["amount"]     # receipts positive, tax/fees negative
    return dict(out)


def capital_path(completed, open_lots, positions, live, universe, px,
                 start, end):
    """Daily Track B capital: inventory at market + margin on live puts."""
    lots = [(l["sym"], l["in_day"], l["out_day"], l["qty"]
             , l["in_px"]) for l in completed]
    lots += [(l["sym"], l["in_day"], None, l["qty"], l["in_px"])
             for l in open_lots]
    puts = [(p["sym"], p["open"], p["close"], p["qty"], p["strike"])
            for p in positions
            if p["right"] == "P" and p["sym"] in universe]
    puts += [(o["sym"], o["open"], min(o["exp"], end), o["qty"], o["strike"])
             for o in live if o["right"] == "P" and o["sym"] in universe]
    rows = []
    day = start
    while day <= end:
        mv = cost = margin = 0.0
        for sym, d0, d1, qty, basis in lots:
            if d0 <= day and (d1 is None or day < d1):
                ser = px.get(sym)
                s = ser.close_on_or_before(day) if ser else None
                if s is not None:
                    mv += s * qty
                    cost += basis * qty
        for sym, d0, d1, qty, k in puts:
            if d0 <= day <= d1:
                margin += MARGIN * k * 100 * qty
        rows.append((day, mv, cost, margin))
        day += timedelta(days=1)
    return rows


def universe_benchmark(px, universe, completed, open_lots, start, end):
    """Exposure-matched selection benchmark.

    A buy-at-the-start, hold-to-the-end index return is not comparable with the
    wheel's equity P&L: the wheel's exposure is time-varying, its lots are held
    for weeks rather than the whole window, and they are entered *after* falls,
    which is the very thing being measured. The benchmark must therefore hold
    the same dollars on the same days.

    So on each trading day the benchmark holds exactly the wheel's inventory
    market value, invested in an equal-weighted basket of every name the
    operator ever traded, and earns that basket's daily return:

        benchmark P&L  =  sum_d  MV(d-1) * r_universe(d)
        wheel equity   =  sum_d  MV(d-1) * r_held(d)      ( = D's price part)

    The difference is the contribution of *which names, when* -- selection and
    entry timing -- with the size and duration of the exposure held fixed.
    """
    # Trading days: the union of every series' days, restricted to the window.
    days = sorted({d for ser in px.values() for d in ser.days
                   if start <= d <= end})
    lots = [(l["sym"], l["in_day"], l["out_day"], l["qty"]) for l in completed]
    lots += [(l["sym"], l["in_day"], None, l["qty"]) for l in open_lots]

    bench_pnl = wheel_pnl = 0.0
    exposure_days = 0.0
    gap_by_name = defaultdict(float)
    for prev, day in zip(days, days[1:]):
        held = [(s, q) for s, d0, d1, q in lots
                if d0 <= prev and (d1 is None or prev < d1)]
        if not held:
            continue
        mv_prev = 0.0
        mv_now = 0.0
        contrib = []
        for sym, qty in held:
            ser = px.get(sym)
            if ser is None:
                continue
            a, b = ser.close_on_or_before(prev), ser.close_on_or_before(day)
            if a is None or b is None:
                continue
            mv_prev += a * qty
            mv_now += b * qty
            contrib.append((sym, a * qty, (b - a) * qty))
        if mv_prev <= 0:
            continue
        rets = []
        for sym in universe:
            ser = px.get(sym)
            if ser is None:
                continue
            # Adjusted: three names reverse-split inside the window, and an
            # as-traded return across a 1:20 split is a 1,900% daily move.
            a, b = ser.adj_on_or_before(prev), ser.adj_on_or_before(day)
            if a and b:
                rets.append(b / a - 1)
        if not rets:
            continue
        r_uni = sum(rets) / len(rets)
        bench_pnl += mv_prev * r_uni
        wheel_pnl += mv_now - mv_prev
        exposure_days += mv_prev
        for sym, mv, pnl in contrib:
            gap_by_name[sym] += pnl - mv * r_uni
    return (bench_pnl, wheel_pnl, exposure_days / max(len(days) - 1, 1),
            dict(gap_by_name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daily", action="store_true",
                    help="print the monthly capital and exposure path")
    ap.add_argument("--bootstrap", action="store_true",
                    help="resampling interval for the excess, and what "
                         "concentration the point estimate rests on")
    args = ap.parse_args()

    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB}")
    positions, stock_tx, divs, live = parse(paths)
    excluded = excluded_symbols()
    universe = wheel_universe(positions, stock_tx, excluded)
    completed, open_lots = build_lots(stock_tx, excluded)

    end = max(max(p["close"] for p in positions),
              max(d for d, *_ in stock_tx))
    start = min(min(p["open"] for p in positions),
                min(d for d, *_ in stock_tx))
    years = (end - start).days / 365.25

    px = prices.load_all(universe)
    print(f"\nwindow {start} .. {end}  ({years:.2f} y)  "
          f"universe {len(universe)} names, prices for {len(px)}")

    A = option_cash(positions, live, universe, end, px)
    B, C, b_rows, c_rows, missing = acquisition_and_exit(
        completed, open_lots, px, end)
    div_by_sym = wheel_dividends(divs, stock_tx, universe)
    D_price, D_div, _ = equity_pnl(completed, open_lots, px, end, div_by_sym)

    cap = capital_path(completed, open_lots, positions, live, universe, px,
                       start, end)
    n = len(cap)
    avg_mv = sum(r[1] for r in cap) / n
    avg_cost = sum(r[2] for r in cap) / n
    avg_margin = sum(r[3] for r in cap) / n
    avg_capB = avg_mv + avg_margin

    print("\n=== A: option cash ===")
    print(f"  premium received (closed)      ${A['received']:12,.0f}")
    print(f"  premium received (still open)  ${A['live_prem']:12,.0f}")
    print(f"  commissions                    ${A['commissions']:12,.0f}")
    print(f"  buy-backs                      ${A['bought_back']:12,.0f}")
    print(f"  mark on open contracts         ${A['live_mark']:12,.0f}"
          f"   (sigma = trailing realised)")
    print(f"  {'-'*48}")
    print(f"  A = net option cash            ${A['total']:12,.0f}")
    print(f"      by leg: puts ${A['by_leg'].get('P', 0):,.0f}, "
          f"calls ${A['by_leg'].get('C', 0):,.0f}, "
          f"calls/puts = {A['by_leg'].get('C',0)/A['by_leg'].get('P',1):.2f}")
    if A["unmarked"]:
        print(f"      unmarked open contracts: {sorted(set(A['unmarked']))}")

    print("\n=== B and C: what Track A cannot see ===")
    print(f"  B = mark loss at acquisition   ${B:12,.0f}"
          f"   ({len(b_rows)} lots)")
    print(f"  C = upside surrendered at exit ${C:12,.0f}"
          f"   ({len(c_rows)} exits)")
    if missing:
        print(f"      unpriced events: {missing}")

    print("\n=== D: the shares themselves ===")
    print(f"  price change on lots held      ${D_price:12,.0f}")
    print(f"  dividends, net of tax and fees ${D_div:12,.0f}")
    print(f"  D = same-names buy-and-hold    ${D_price + D_div:12,.0f}")

    econ = D_price + D_div + A["total"] - B - C
    excess = A["total"] - B - C

    # Where the excess comes from. A put's economic result is its premium less
    # the mark loss if it is assigned; a call's is its premium less the upside
    # surrendered if it is exercised. Everything else is friction. This is the
    # live version of the article's claim that each leg is very nearly a wash.
    put_prem = A["by_leg"].get("P", 0.0)
    call_prem = A["by_leg"].get("C", 0.0)
    friction = A["commissions"] + A["bought_back"] + A["live_mark"]
    print("\n=== where the excess comes from, by leg ===")
    print(f"  put premium                    ${put_prem:12,.0f}")
    print(f"  less mark loss at acquisition  ${-B:12,.0f}")
    print(f"  {'-'*48}")
    print(f"  PUT LEG                        ${put_prem - B:12,.0f}"
          f"   ({(put_prem-B)/put_prem:+.1%} of premium kept)")
    print(f"  call premium                   ${call_prem:12,.0f}")
    print(f"  less upside surrendered        ${-C:12,.0f}")
    print(f"  {'-'*48}")
    print(f"  CALL LEG                       ${call_prem - C:12,.0f}"
          f"   ({(call_prem-C)/call_prem:+.1%} of premium kept)")
    print(f"  frictions (comm, buy-backs,    ${friction:12,.0f}")
    print(f"    marks on open contracts)")
    print(f"  {'='*48}")
    print(f"  EXCESS = A - B - C             ${excess:12,.0f}")
    print("\n=== the two ledgers ===")
    trackA = A["received"] + A["live_prem"] + A["commissions"] \
        + A["bought_back"] + D_div
    realized_stock = sum((l["out_px"] - l["in_px"]) * l["qty"]
                         for l in completed)
    print(f"  Track A cash income            ${trackA:12,.0f}"
          f"   (premium + dividends)")
    print(f"  realized stock P&L             ${realized_stock:12,.0f}")
    print(f"  Track A total, realized cash   ${trackA + realized_stock:12,.0f}")
    print(f"  Track B economic P&L           ${econ:12,.0f}"
          f"   (= D + A - B - C)")
    print(f"\n  average capital, market value  ${avg_capB:12,.0f}"
          f"   (inventory {avg_mv:,.0f} + put margin {avg_margin:,.0f})")
    print(f"  average capital, cost basis    ${avg_cost + avg_margin:12,.0f}")

    print("\n=== returns, annualised ===")
    print(f"  Track A on cost basis          "
          f"{(trackA + realized_stock)/(avg_cost+avg_margin)/years:+11.2%}"
          f"   <- what a brokerage statement shows")
    print(f"  Track B economic, on market    {econ/avg_capB/years:+11.2%}")
    print(f"  same-names buy-and-hold (D)    "
          f"{(D_price+D_div)/avg_capB/years:+11.2%}")
    print(f"  EXCESS over same names (A-B-C) "
          f"{excess/avg_capB/years:+11.2%}"
          f"   <- the option overlay's edge")

    bench_pnl, wheel_eq, avg_exposure, sel_by_name = universe_benchmark(
        px, universe, completed, open_lots, start, end)
    print("\n=== selection: the same dollars, on the same days ===")
    print(f"  wheel's own inventory earned   ${wheel_eq:12,.0f}"
          f"   ({wheel_eq/avg_exposure/years:+.2%} on ${avg_exposure:,.0f})")
    print(f"  same dollars in the universe   ${bench_pnl:12,.0f}"
          f"   ({bench_pnl/avg_exposure/years:+.2%}, equal weight)")
    print(f"  selection contribution         ${wheel_eq - bench_pnl:12,.0f}"
          f"   ({(wheel_eq-bench_pnl)/avg_exposure/years:+.2%})"
          f"   <- which names, when")
    print(f"  (reconciliation: the daily walk gives ${wheel_eq:,.0f} against "
          f"D's ${D_price:,.0f}, a {abs(wheel_eq-D_price)/abs(D_price):.1%} "
          f"residual from entry/exit day alignment)")

    if args.bootstrap:
        units, by_name = excess_units(positions, live, universe, px, end,
                                      b_rows, c_rows)
        resid = sum(v for _, v in units) - excess
        assert abs(resid) < 1.0, f"excess not fully attributed: {resid:,.2f}"
        print("\n=== how firm is the excess? ===")
        print(f"  point estimate                 "
              f"{excess/avg_capB/years:+11.2%}")
        for label, u in (("by lot ", units),
                         ("by name", list(by_name.items()))):
            lo, hi, p_neg = bootstrap_excess(u, avg_capB, years)
            print(f"  {label}  n={len(u):4d}   90% CI {lo:+.2%} .. {hi:+.2%}"
                  f"   P(excess < 0) = {p_neg:.0%}")
        sel_total = sum(sel_by_name.values())
        print("  largest single positions, in both decompositions:")
        print(f"    {'name':6s} {'excess':>10s} {'w/o it':>9s} "
              f"{'selection':>10s} {'w/o it':>9s}")
        # Rank on total footprint, not the net: a name whose two contributions
        # cancel is the most interesting one here, not the least.
        rank = sorted(sel_by_name, key=lambda s: -(abs(by_name.get(s, 0.0))
                                                   + abs(sel_by_name[s])))[:5]
        for sym in rank:
            e, g = by_name.get(sym, 0.0), sel_by_name[sym]
            print(f"    {sym:6s} ${e:9,.0f} {(excess-e)/avg_capB/years:+9.2%} "
                  f"${g:9,.0f} {(sel_total-g)/avg_exposure/years:+9.2%}")
        print("  The concentration is not noise to be averaged away. A lot that"
              "\n  runs far enough to matter is the jump tail the lognormal"
              "\n  lacks, arriving in the ledger -- the same tail T2 sees as a"
              "\n  right-skewed entry depth. It cuts both ways by construction:"
              "\n  a name that rises far enough to dominate selection is a name"
              "\n  whose call gave that rise away.")

    if args.daily:
        print("\n=== capital path (month ends) ===")
        seen = set()
        for day, mv, cost, margin in cap:
            key = (day.year, day.month)
            nxt = day + timedelta(days=1)
            if (nxt.year, nxt.month) != key and key not in seen:
                seen.add(key)
                print(f"  {day}  inventory MV ${mv:10,.0f}  "
                      f"cost ${cost:10,.0f}  put margin ${margin:8,.0f}  "
                      f"MV/cost {mv/cost if cost else 0:.3f}")


if __name__ == "__main__":
    main()
