"""Wheel-strategy statistics from Interactive Brokers cash-flow statements.

Reads every CSV under statements/ (private, gitignored — see .gitignore) and
prints the aggregates cited in drafts/2026-07-10-statement-vs-model-observations.txt:
option outcome rates by tenor bucket, premium levels, inventory lot lifecycles,
aging open inventory, and assignment-date clustering.

Run:  python code/analyze_statement.py     (from the repo root)

Statement row format (columns: Date, Amount, Payee, Description, Reference):
  OPTION rows
    "-1 ABT 24APR26 94 P price: 0.2 comm: -1.05"   sell to open
    "+1 ABT 24APR26 94 P (expired)"                expired worthless
    "+1 ABT 24APR26 94 P (assigned)"               exercised (assignment/call-away)
    "+1 ABT 20FEB26 105 P price: 0.06 comm: -0.77" bought back early
  STOCK rows
    "+100 ABT (assigned) price: 94"                shares delivered by put assignment
    "-100 ACN (assigned) price: 240 comm: -0.02"   shares called away
    "-5 CHPT price: 6.02 comm: -0.3"               plain sale (legacy cleanup)

Caveats baked into the analysis:
  * "Junk" filter: any symbol that ever traded (stock or strike) below
    JUNK_PRICE_CUTOFF is excluded from the quality universe — these are legacy
    losers / bankruptcy remnants being liquidated, not wheel positions.
  * Lot matching: a sale is first matched to an open lot whose entry price
    equals the sale price (the wheel's default exit — the call struck at that
    lot's basis was exercised), then to remaining lots FIFO. Plain FIFO
    misreads layered names: ADP held lots at 240 and 217.5, and the exit at
    217.5 is the LOWER layer resolving at its own strike while the 240 layer
    stays held — not the 240 lot capitulating. Shares are fungible, so any
    attribution is a convention; this one matches the operator's intent.
  * Completed-lot statistics are right-censored: lots still open (often the
    oldest, highest-basis ones) never enter them. Read them as "fast lane"
    numbers, not unconditional averages.

Stdlib only (Python 3.8+).
"""

import csv
import glob
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime

STATEMENTS_GLOB = "statements/*.csv"
JUNK_PRICE_CUTOFF = 8.0  # USD; discretionary, see module docstring
# Manual additions to the junk universe: names the operator does not consider
# wheel-grade regardless of price (BEKE: speculative, not a hold-forever asset).
JUNK_EXTRA = {"BEKE"}

OPT_OPEN = re.compile(
    r"^-(\d+) (\S+) (\d{2}[A-Z]{3}\d{2}) ([\d.]+) ([PC]) price: ([\d.]+)(?: comm: (-?[\d.]+))?$")
OPT_CLOSE = re.compile(
    r"^\+(\d+) (\S+) (\d{2}[A-Z]{3}\d{2}) ([\d.]+) ([PC]) "
    r"(?:\((expired|assigned)\)|price: ([\d.]+)(?: comm: (-?[\d.]+))?)$")
STOCK = re.compile(
    r"^([+-])(\d+) (\S+)(?: \((assigned)\))? price: ([\d.]+)(?: comm: (-?[\d.]+))?$")


def parse(paths):
    """Return (option_positions, stock_transactions).

    Option positions are open/close pairs matched FIFO per contract
    (symbol, expiry, strike, right). Closes without a matching open (contract
    opened before the statement window) are dropped.
    """
    opens = {}
    positions = []
    stock_tx = []
    for path in paths:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)  # header
            for row in reader:
                if len(row) < 5:
                    continue
                day, desc, ref = row[0], row[3].strip(), row[4]
                if ref == "OPTION":
                    m = OPT_OPEN.match(desc)
                    if m:
                        key = (m[2], m[3], float(m[4]), m[5])
                        opens.setdefault(key, []).append(
                            (_d(day), float(m[6]), float(m[7] or 0)))
                        continue
                    m = OPT_CLOSE.match(desc)
                    if m:
                        key = (m[2], m[3], float(m[4]), m[5])
                        pending = opens.get(key, [])
                        if pending:
                            open_day, open_px, comm = pending.pop(0)
                            positions.append(dict(
                                sym=m[2], exp=_exp(m[3]), strike=float(m[4]),
                                right=m[5], open=open_day, close=_d(day),
                                open_px=open_px, comm=comm,
                                how=m[6] or "closed",
                                close_px=float(m[7]) if m[7] else 0.0))
                        continue
                    print("UNPARSED OPTION ROW:", desc, file=sys.stderr)
                elif ref == "STOCK":
                    m = STOCK.match(desc)
                    if m:
                        sign = 1 if m[1] == "+" else -1
                        stock_tx.append((_d(day), m[3], sign * int(m[2]),
                                         float(m[5]), m[4] == "assigned"))
                    else:
                        print("UNPARSED STOCK ROW:", desc, file=sys.stderr)
    still_open = sum(len(v) for v in opens.values())
    print(f"parsed: {len(positions)} closed option positions "
          f"({still_open} still open), {len(stock_tx)} stock transactions")
    return positions, stock_tx


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def _exp(s):
    return datetime.strptime(s, "%d%b%y").date()


def junk_symbols(positions, stock_tx):
    junk = {sym for _, sym, _, px, _ in stock_tx if px < JUNK_PRICE_CUTOFF}
    junk |= {p["sym"] for p in positions if p["strike"] < JUNK_PRICE_CUTOFF}
    junk |= JUNK_EXTRA
    return junk


def median(sorted_vals):
    return sorted_vals[len(sorted_vals) // 2] if sorted_vals else float("nan")


def option_report(positions, junk):
    buckets = {"P": [(1, 5, "weekly(2-4d)"), (6, 14, "1-2wk"),
                     (15, 27, "2-4wk"), (28, 45, "monthly")],
               "C": [(1, 7, "<=1wk"), (8, 21, "1-3wk"),
                     (22, 45, "~monthly"), (46, 400, "long")]}
    for right in "PC":
        ps = [p for p in positions
              if p["right"] == right and p["sym"] not in junk]
        outcomes = Counter(p["how"] for p in ps)
        premium = sorted(p["open_px"] / p["strike"] for p in ps)
        print(f"\n=== {right} options, quality universe: {len(ps)} closed ===")
        print(f"outcomes: {dict(outcomes)}  "
              f"assign rate: {outcomes['assigned'] / len(ps):.3f}  "
              f"premium/strike median: {median(premium) * 100:.2f}%")
        for lo, hi, name in buckets[right]:
            sub = [p for p in ps if lo <= (p["exp"] - p["open"]).days <= hi]
            if not sub:
                continue
            assigned = sum(1 for p in sub if p["how"] == "assigned")
            prem = sorted(p["open_px"] / p["strike"] for p in sub)
            comm = sorted(-p["comm"] / (p["open_px"] * 100)
                          for p in sub if p["open_px"])
            print(f"  {name:12s} n={len(sub):4d}  assign rate={assigned / len(sub):.3f}  "
                  f"premium median={median(prem) * 100:.2f}%  "
                  f"comm/premium median={median(comm) * 100:.1f}%")
        early = [p for p in ps if p["how"] == "closed" and p["open_px"]]
        if early:
            frac = sorted(p["close_px"] / p["open_px"] for p in early)
            print(f"  early buy-backs: {len(early)} ({len(early) / len(ps):.0%}), "
                  f"repurchased at median {median(frac):.0%} of premium received")
    total = {r: sum(p["open_px"] * 100 for p in positions
                    if p["right"] == r and p["sym"] not in junk) for r in "PC"}
    print(f"\ngross premium (quality, closed): puts ${total['P']:,.0f}, "
          f"calls ${total['C']:,.0f}, calls/puts = {total['C'] / total['P']:.2f}")


def inventory_report(stock_tx, junk, today):
    buys = defaultdict(list)
    completed = []
    for day, sym, qty, px, _ in sorted(stock_tx):
        if sym in junk:
            continue
        if qty > 0:
            buys[sym].append([day, qty, px])
        else:
            remaining = -qty
            # Price-match first, then FIFO — see docstring caveat.
            while remaining > 0 and buys[sym]:
                lot = next((l for l in buys[sym] if abs(l[2] - px) < 1e-9),
                           buys[sym][0])
                b_day, b_qty, b_px = lot
                take = min(remaining, b_qty)
                completed.append(dict(sym=sym, in_day=b_day, out_day=day,
                                      in_px=b_px, out_px=px, qty=take))
                lot[1] -= take
                remaining -= take
                if lot[1] == 0:
                    buys[sym].remove(lot)
            # remaining > 0 here means legacy shares bought before the
            # statement window were sold; not a wheel lot, ignore.
    hold = sorted((l["out_day"] - l["in_day"]).days for l in completed)
    same = sum(1 for l in completed if abs(l["out_px"] - l["in_px"]) < 1e-9)
    above = sum(1 for l in completed if l["out_px"] > l["in_px"] + 1e-9)
    below = sum(1 for l in completed if l["out_px"] < l["in_px"] - 1e-9)
    print(f"\n=== inventory lots (quality universe, price-match-then-FIFO) ===")
    below_lots = [l for l in completed if l["out_px"] < l["in_px"] - 1e-9]
    for l in below_lots:
        print(f"  below-basis exit: {l['sym']} {l['qty']} in @{l['in_px']} "
              f"{l['in_day']} -> out @{l['out_px']} {l['out_day']}")
    print(f"completed: {len(completed)}  holding days median {median(hold)}, "
          f"max {hold[-1] if hold else '-'}  "
          f"exit vs entry strike same/above/below: {same}/{above}/{below}")
    print("open lots (right-censored — the aging tail):")
    open_lots = [(sym, d, q, px) for sym, lst in buys.items()
                 for d, q, px in lst]
    for sym, d, q, px in sorted(open_lots, key=lambda x: x[1]):
        print(f"  {sym:6s} {q:5d} @ {px:8.2f}  since {d}  ({(today - d).days}d)")


def cluster_report(stock_tx, junk):
    clusters = Counter(day for day, sym, qty, _, assigned in stock_tx
                       if qty > 0 and assigned and sym not in junk)
    top = [(str(d), c) for d, c in clusters.most_common(6) if c > 1]
    print(f"\nassignment-day clusters (common shocks): {top}")


def main():
    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB} "
                 "(they are private and not in the repository)")
    print("reading:", ", ".join(paths))
    positions, stock_tx = parse(paths)
    junk = junk_symbols(positions, stock_tx)
    print(f"junk universe (excluded, price < {JUNK_PRICE_CUTOFF}): {sorted(junk)}")
    option_report(positions, junk)
    inventory_report(stock_tx, junk, date.today())
    cluster_report(stock_tx, junk)


if __name__ == "__main__":
    main()
