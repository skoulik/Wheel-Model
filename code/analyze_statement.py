"""Wheel-strategy statistics from Interactive Brokers cash-flow statements.

Reads every CSV under statements/ (private, gitignored — see .gitignore) and
prints the aggregates cited in drafts/2026-07-10-statement-vs-model-observations.md:
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
  DIVIDEND rows (Reference column empty)
    "TGT(US87612E1064) Cash Dividend USD 1.12 per Share (Ordinary Dividend)"
    "TLT(US4642874329) Payment in Lieu of Dividend (Ordinary Dividend)"   lent-out shares
    "SLB(...) Cash Dividend USD 0.285 per Share (Ordinary Div - NRA Withholding Exempt)"
    "EMLC(...) Cash Dividend USD 0.1206 per Share - US Tax"   withholding (both signs:
                                                   negative = withheld, positive = refund)
    "NVO(...) Cash Dividend USD 0.58432 per Share - FEE"      ADR/handling fee
  CORP rows — corporate actions, read only for the ticker map below
    "CMCSA(US20030N1019) Spinoff  1 for 25 (VSNT, VERSANT MEDIA GROUP INC-WI, ...)"

Two properties of the exports themselves, both of which cost a real figure
before they were found (TODO IV-6 and IV-7), and both handled in `_read_rows`:

  * The rows are NOT in date order, and open/close matching cannot assume they
    are. IBKR emitted one renamed close thirty-five rows ABOVE the open it
    belonged to, so the close was discarded as unmatched and the open stood
    forever. Rows are stably sorted by posting date before anything is matched.
  * Successive exports OVERLAP at the seam — USD.csv ends 2026-05-02 and
    USD1.csv starts 2026-05-01 — so nine rows are exported twice. A row
    repeated in a LATER file is one event seen twice and is dropped; a row
    repeated INSIDE one file is two genuine fills (there is such a pair) and is
    kept. Deduplicating the corpus as a whole would destroy the second kind.

Dates: the statement's Date column is the CASH POSTING date, not the trade
date. Trades post one business day later (options and equities both settle
T+1), and expiry/assignment processing posts one calendar day after expiry —
which is why 526 of 530 expiry rows land exactly one day after the contract's
expiry date, why 55 assignment stock rows are dated Saturday, and why opens
cluster on Tuesday for an operator who sells on Monday. Every date is shifted
back to its event date at parse time (`_trade_day` / `_expiry_day`), so a put
sold Monday and expiring Friday reads as the 4-calendar-day option it is, not
a 3-day one. Residual error: a holiday between trade and posting shifts the
inferred trade date one extra day back.

Caveats baked into the analysis:
  * Universe: defined by exclusion. Every out-of-universe name is listed
    explicitly in EXCLUDED_LIST below (see there) — there is no price rule or
    other heuristic. A price threshold was tried and dropped: it is a proxy
    for "not wheel-grade" that both over- and under-fires, and the operator's
    judgement is the thing actually being encoded. The list is applied in
    parse(), so an excluded name is absent from every figure below as though
    it had never been traded.
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
  * Corporate-action ticker variants are folded into their underlying before
    anything is keyed on the symbol — see `_variant_map`. A contract renamed
    mid-life otherwise loses both of its legs at once.

Stdlib only (Python 3.8+).
"""

import csv
import glob
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

# Model formulas: model.py is the single source (same directory).
from model import Config, assign_prob, bs_call, expected_drop, strike

STATEMENTS_GLOB = "statements/*.csv"
# Symbols outside the universe the article claims to trade. Every name is
# listed explicitly -- there is no price rule or other heuristic -- and the
# list is enforced in parse(): a row naming one of these is dropped as it is
# read, so nothing here reaches any analysis. The position was never opened,
# the shares were never assigned, the dividend was never received.
#
# Anything appearing in the statements and NOT listed here is the universe the
# model is verified against, so a new symbol counts as in-universe by default
# and must be ruled out by hand.
#
# What is in here, roughly in the order the groups below are written:
#
#   * Legacy losers and bankruptcy remnants -- penny-priced positions being
#     liquidated, the residue of strategies that predate the wheel.
#   * Speculative single names -- high-beta growth, China ADRs, pre-profit
#     story stocks, spin-offs and renamings. They trade at normal prices but
#     are not hold-forever assets, and the wheel's premise (assignment is an
#     acceptable outcome) does not hold for them.
#   * Non-equity or non-single-name instruments -- ETFs, bond funds and
#     preferreds. Wheel-able, but their return process is not the lognormal
#     single-stock walk the model is built on, so they cannot verify it. STRF
#     is the wheeled preferred already noted as an out-of-scope outlier.
#   * Corporate-action ticker variants. IBKR appends a digit to the symbol of
#     an option whose deliverable a corporate action has changed, so an
#     excluded name reappears under a name the list does not hold. CHPT1 and
#     KYNB1 are the two observed, from a 1-for-20 reverse split and a merger.
#     These now resolve to their underlying in `_variant_map` and would be
#     excluded through it, but they stay listed: the map is inferred from what
#     the statements happen to mention, and an exclusion should not depend on
#     an inference. The hit is recorded under the name the statement wrote, so
#     these go on reporting as traded rather than as stale list entries.
#
# ALT and BEKE were once carried as exceptions, the wheel having entered them
# by assignment inside the window; they were the only empirical handle on the
# permanent-impairment hazard (TODO #13). They are now excluded like the rest:
# neither is a name the strategy would knowingly enter, so measuring the hazard
# from them would measure a universe the article does not claim. That leaves no
# impairment observations at all -- the honest state, pending a genuine
# in-universe assignment that goes against us.
#
# EMLC and 9988 were found missing on 2026-07-28 (TODO IV-5) by enumerating
# every symbol the statements mention rather than every symbol the analysis
# reaches. Both are legacy holdings the wheel never traded -- an EM local
# currency bond ETF and an HK listing -- and both were in universe by this
# list's own default rule while being invisible to universe_report(), which
# is built from closed option positions and stock rows and so cannot see a
# name that only pays dividends.
EXCLUDED_LIST = {
    "ALT", "API", "BB", "BLNK", "BTBT", "BYND", "BZUN", "CHPT", "CLNE",
    "CLOV", "CRON", "FOSL", "FUBO", "GOTU", "HYLN", "KNDI", "KODK", "LAZR",
    "MPT", "MPW", "NIO", "NNDM", "NNOX", "PLUG", "QS", "RLX", "TLRY", "TPIC",
    "VIR",

    "9988", "ATHM", "BEKE", "CLSK", "D", "DQ", "EH", "FOLD", "GDS", "JKS",
    "JOYY", "KVUE", "KYNB", "MCRB", "MOMO", "NBIS", "RBLX", "RIVN", "RSI",
    "SCLX", "SHLS", "TAL", "TME", "VSNT", "WBA", "XPEV", "ZYME",

    "AMLP", "EMLC", "EWM", "EWY", "KWEB", "LTPZ", "STRF", "TLT",

    "CHPT1", "KYNB1",
}

# Excluded symbols actually encountered while parsing, and how many rows each
# cost. Populated by parse(); read by universe_report() to show what was
# dropped and to flag entries that no longer appear in the statements at all.
EXCLUDED_SEEN = Counter()

# Every symbol the raw rows mention, folded onto its underlying, counted by
# row kind: {symbol: Counter({"OPTION": n, "STOCK": n, "DIVIDEND": n, ...})}.
# Populated by parse(); read by universe_report() to name the symbols the
# analysis never reaches. That report is the one that could have caught TODO
# IV-5 and did not, because it was built from what the analysis had already
# consumed rather than from what the statements say.
SYMBOLS_SEEN = {}

# Corporate-action ticker variant -> the underlying it belongs to, inferred by
# `_variant_map` from the corpus. Populated by parse(), reported by
# universe_report().
VARIANT_PARENT = {}

OPT_OPEN = re.compile(
    r"^-(\d+) (\S+) (\d{2}[A-Z]{3}\d{2}) ([\d.]+) ([PC]) price: ([\d.]+)(?: comm: (-?[\d.]+))?$")
OPT_CLOSE = re.compile(
    r"^\+(\d+) (\S+) (\d{2}[A-Z]{3}\d{2}) ([\d.]+) ([PC]) "
    r"(?:\((expired|assigned)\)|price: ([\d.]+)(?: comm: (-?[\d.]+))?)$")
STOCK = re.compile(
    r"^([+-])(\d+) (\S+)(?: \((assigned)\))? price: ([\d.]+)(?: comm: (-?[\d.]+))?$")
DIV = re.compile(r"^(\S+?) ?\((\S+)\) (.*)$")  # optional space: "TRI (CA...)"
DIV_PER_SHARE = re.compile(r"USD ([\d.]+) per Share")
DIV_TAX = re.compile(r"- ([A-Z]{2}) Tax$")
# An adjusted option's symbol: a letters-only root with one digit appended.
# The digit-only tickers in the statements (9988, an HK listing) are not this
# shape, and would find no parent even if they were.
VARIANT = re.compile(r"^([A-Z][A-Z.]*)(\d)$")


def _excluded(sym, parent=None):
    """True if `sym` is out of universe; records the hit for the report.

    `parent` is the underlying `sym` was renamed from, if any: an excluded
    name must stay excluded when a corporate action renames its options. The
    hit is recorded under the symbol the statement actually wrote, so a list
    entry covering a variant (CHPT1, KYNB1) goes on showing as traded rather
    than as an entry that no longer matches anything.
    """
    if sym not in EXCLUDED_LIST and (parent or sym) not in EXCLUDED_LIST:
        return False
    EXCLUDED_SEEN[sym] += 1
    return True


def _row_symbol(row):
    """(kind, symbol) named by a raw row; symbol None if the row parses no name."""
    desc, ref = row[3].strip(), row[4]
    if ref == "OPTION":
        m = OPT_OPEN.match(desc) or OPT_CLOSE.match(desc)
        return "OPTION", m[2] if m else None
    if ref == "STOCK":
        m = STOCK.match(desc)
        return "STOCK", m[3] if m else None
    if ref == "CORP":
        m = DIV.match(desc)          # same "SYM(ISIN) ..." shape as a dividend
        return "CORP", m[1] if m else None
    if ref == "" and "ividend" in desc:
        m = DIV.match(desc)
        return "DIVIDEND", m[1] if m else None
    return None, None


def _read_rows(paths):
    """Every data row from every file, in event order and without re-exports.

    Returns (rows, n_duplicates). Two properties of the exports are handled
    here rather than left for the matching to trip over — see the module
    docstring for what each one cost.

    ORDER. Rows are stably sorted by posting date, so an open always precedes
    the close it belongs to. The files are not ordered, and the case that
    matters is not hypothetical: the close of the renamed CMCSA contract sits
    thirty-five rows above its own open. The sort is stable, so file order
    survives within a day and the read order of everything already contiguous
    is untouched — no in-universe contract has an open and a close posted on
    the same day, so nothing can be re-paired by this.

    OVERLAP. Successive exports repeat the days at the seam. A row already
    carried by an EARLIER file is dropped, at most as many times as that file
    carried it; repeats INSIDE one file are genuine repeat fills and are kept.
    Headers are skipped per file, so the whole-corpus dedupe that would eat
    the second file's header — and the data row behind it — cannot happen.
    """
    seen = Counter()
    rows = []
    n_dup = 0
    for path in paths:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)  # header, one per file
            body = [r for r in reader if len(r) >= 5]
        budget = Counter(seen)     # how many of each row earlier files carried
        kept = []
        for r in body:
            t = tuple(r)
            if budget[t]:
                budget[t] -= 1
                n_dup += 1
                continue
            kept.append(r)
        seen.update(tuple(r) for r in kept)
        rows.extend(kept)
    rows.sort(key=lambda r: r[0])
    return rows, n_dup


def _variant_map(census):
    """Corporate-action ticker variants, mapped back to their underlying.

    IBKR renames an option whose deliverable a corporate action has changed:
    by the OCC convention the root is truncated to four characters and a
    sequence digit appended, so CMCSA -> CMCS1 and TRI -> TRI1. Nothing else
    about the contract changes, so the two legs of one position end up keyed
    under two different symbols — the close matches no open and is discarded,
    and the open is never closed and stands as a short position forever. Three
    contracts in the window (TODO IV-6).

    `census` is {symbol: Counter(row kind)} over the raw rows. A candidate is
    a symbol of the adjusted shape whose stem is the four-character root of
    another symbol the statements mention. CORP rows are the corroborating
    authority — they name the underlying whose deliverable changed — but they
    are NOT sufficient alone: KYNB1 appears with no CORP row in the window,
    its merger having posted outside it. So a mapping the CORP rows do not
    confirm is applied and reported rather than silently trusted or silently
    dropped, and an ambiguous one is refused.
    """
    corp = {s for s, kinds in census.items() if kinds["CORP"]}
    parent, unconfirmed = {}, []
    for sym in sorted(census):
        m = VARIANT.match(sym)
        if not m:
            continue
        cands = [s for s in census if s != sym and s[:4] == m[1]]
        if not cands:
            continue
        backed = [s for s in cands if s in corp]
        if len(backed) == 1:
            parent[sym] = backed[0]
        elif len(cands) == 1:
            parent[sym] = cands[0]
            unconfirmed.append(sym)
        else:
            print(f"AMBIGUOUS TICKER VARIANT: {sym} -> {sorted(cands)}, "
                  "not resolved", file=sys.stderr)
    for sym in unconfirmed:
        print(f"TICKER VARIANT {sym} -> {parent[sym]}: no CORP row confirms it "
              "(the corporate action posted outside the window)", file=sys.stderr)
    return parent


def parse(paths):
    """Return (option_positions, stock_transactions, dividend_rows).

    Option positions are open/close pairs matched FIFO per contract
    (symbol, expiry, strike, right). Closes without a matching open (contract
    opened before the statement window) are dropped. Dividend rows keep every
    dividend-related cash flow (receipt, payment in lieu, withholding tax,
    fee) tagged by kind.

    Matching is by CONTRACT COUNT, not by row: a row can carry any number of
    contracts (1 is the mode, but 2, 3, 6 and even 60 all occur), and an open
    of six can be closed by two rows of three. Each emitted position therefore
    carries `qty`, and its cash is prorated to that quantity. Ignoring the
    count understates gross premium by 14% on the put leg and 30% on the call
    leg, which is enough to flip the calls/puts income ratio from 0.90 to 1.03.
    Every option row's Amount reconciles to qty*price*100 + commission exactly
    (1198 of 1198 rows), so the count is real and Amount is authoritative.

    Rows naming a symbol in EXCLUDED_LIST are dropped here, at the point of
    reading, rather than filtered downstream. That is the whole enforcement:
    an excluded name cannot reach an analysis by being forgotten in one call
    site, because it never enters the data. Both legs of an excluded option go
    together, so the open/close matching below never sees a half pair.

    Every symbol is folded onto its underlying before it is used as a key --
    see `_variant_map` -- and the corpus itself is de-overlapped and put in
    event order by `_read_rows`. Neither is cosmetic: without the first the
    two legs of a renamed contract never meet, and without the second they
    still do not, because the rename also moves the close in the file.
    """
    opens = {}
    positions = []
    stock_tx = []
    divs = []
    EXCLUDED_SEEN.clear()          # parse() may be called more than once
    SYMBOLS_SEEN.clear()
    VARIANT_PARENT.clear()

    rows, n_dup = _read_rows(paths)
    census = defaultdict(Counter)
    for row in rows:
        kind, sym = _row_symbol(row)
        if sym:
            census[sym][kind] += 1
    VARIANT_PARENT.update(_variant_map(census))
    for sym, kinds in census.items():          # the census, folded on parents
        SYMBOLS_SEEN.setdefault(VARIANT_PARENT.get(sym, sym), Counter()).update(kinds)

    for row in rows:
        day, desc, ref = row[0], row[3].strip(), row[4]
        if ref == "OPTION":
            m = OPT_OPEN.match(desc)
            if m:
                sym = VARIANT_PARENT.get(m[2], m[2])
                if _excluded(m[2], sym):
                    continue
                key = (sym, m[3], float(m[4]), m[5])
                n = int(m[1])
                opens.setdefault(key, []).append(dict(
                    day=_trade_day(day), qty=n, px=float(m[6]),
                    comm_per=float(m[7] or 0) / n))
                continue
            m = OPT_CLOSE.match(desc)
            if m:
                sym = VARIANT_PARENT.get(m[2], m[2])
                if _excluded(m[2], sym):
                    continue
                key = (sym, m[3], float(m[4]), m[5])
                pending = opens.get(key, [])
                # Expiry/assignment posts +1 calendar day; a buy-back
                # is a trade and posts +1 business day.
                close_day = (_expiry_day(day) if m[6]
                             else _trade_day(day))
                close_px = float(m[7]) if m[7] else 0.0
                close_comm_per = float(m[8] or 0) / int(m[1])
                remaining = int(m[1])
                while remaining > 0 and pending:
                    o = pending[0]
                    take = min(remaining, o["qty"])
                    positions.append(dict(
                        sym=sym, exp=_exp(m[3]), strike=float(m[4]),
                        right=m[5], open=o["day"], close=close_day,
                        qty=take, open_px=o["px"],
                        comm=o["comm_per"] * take,
                        close_comm=close_comm_per * take,
                        how=m[6] or "closed", close_px=close_px))
                    o["qty"] -= take
                    remaining -= take
                    if o["qty"] == 0:
                        pending.pop(0)
                continue
            print("UNPARSED OPTION ROW:", desc, file=sys.stderr)
        elif ref == "STOCK":
            m = STOCK.match(desc)
            if m:
                sym = VARIANT_PARENT.get(m[3], m[3])
                if _excluded(m[3], sym):
                    continue
                sign = 1 if m[1] == "+" else -1
                assigned = m[4] == "assigned"
                d_ev = _expiry_day(day) if assigned else _trade_day(day)
                stock_tx.append((d_ev, sym, sign * int(m[2]),
                                 float(m[5]), assigned))
            else:
                print("UNPARSED STOCK ROW:", desc, file=sys.stderr)
        elif ref == "" and "ividend" in desc:
            m = DIV.match(desc)
            if not m:
                print("UNPARSED DIVIDEND ROW:", desc, file=sys.stderr)
                continue
            sym, rest = VARIANT_PARENT.get(m[1], m[1]), m[3]
            if _excluded(m[1], sym):
                continue
            tax = DIV_TAX.search(rest)
            per_share = DIV_PER_SHARE.search(rest)
            divs.append(dict(
                day=_d(day), sym=sym, amount=float(row[1]),
                kind=("fee" if rest.endswith("FEE")
                      else "tax" if tax else "recv"),
                country=tax[1] if tax else None,
                pil="in Lieu" in rest or "IN LIEU" in rest,
                per_share=float(per_share[1]) if per_share else None))
    live = [dict(sym=k[0], exp=_exp(k[1]), strike=k[2], right=k[3],
                 open=o["day"], qty=o["qty"], open_px=o["px"],
                 comm=o["comm_per"] * o["qty"])
            for k, v in opens.items() for o in v if o["qty"]]
    still_open = sum(o["qty"] for o in live)
    n_contracts = sum(p["qty"] for p in positions)
    print(f"parsed: {len(positions)} closed option positions "
          f"({n_contracts} contracts; {still_open} contracts still open), "
          f"{len(stock_tx)} stock transactions, "
          f"{len(divs)} dividend-related cash flows")
    print(f"        ({sum(EXCLUDED_SEEN.values())} rows in "
          f"{len(EXCLUDED_SEEN)} excluded symbols dropped at read; "
          f"see EXCLUDED_LIST)")
    if n_dup:
        print(f"        ({n_dup} rows dropped as re-exports of a row an "
              f"earlier file already carried)")
    if VARIANT_PARENT:
        print("        (corporate-action renames folded onto the underlying: "
              + " ".join(f"{v}->{p}" for v, p in sorted(VARIANT_PARENT.items()))
              + ")")
    _check_live(live, _d(max(r[0] for r in rows)) if rows else None)
    return positions, stock_tx, divs, live


def _check_live(live, last_day):
    """Warn about contracts left standing that the statements say are gone.

    A contract still in `live` at the end of the read has no close anywhere in
    the corpus. If it expired BEFORE the last statement date, that is not a
    live position — it is a lost close, and the open will be carried as a
    standing short for the rest of time. Today's cost is a misclassification;
    the expensive version is a ledger whose window ends before such an expiry,
    which marks a Black-Scholes liability against a contract that no longer
    exists.

    A warning rather than a hard failure: the next tranche of statements can
    bring a corporate action this map has never seen, and that is exactly when
    the output is wanted rather than a traceback.
    """
    stale = sorted((o for o in live if last_day and o["exp"] < last_day),
                   key=lambda o: o["exp"])
    for o in stale:
        print(f"STALE OPEN CONTRACT: {o['sym']} {o['exp']} {o['strike']:g}"
              f"{o['right']} x{o['qty']} opened {o['open']} — expired before "
              f"the last statement date {last_day} and was never closed; its "
              "close is probably keyed under a renamed symbol (TODO IV-6)",
              file=sys.stderr)


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def _trade_day(s):
    """Trade date behind a T+1 cash posting: the previous business day."""
    d = _d(s) - timedelta(days=1)
    while d.weekday() >= 5:          # posted Mon or Sat -> traded Friday
        d -= timedelta(days=1)
    return d


def _expiry_day(s):
    """Event date behind an expiry/assignment posting: one calendar day back.

    Not a business-day shift: the OCC processes Friday expiries over the
    weekend, so these rows are dated Saturday.
    """
    return _d(s) - timedelta(days=1)


def _exp(s):
    return datetime.strptime(s, "%d%b%y").date()


def excluded_symbols():
    """Symbols outside the universe — a copy of the fixed EXCLUDED_LIST.

    Kept as a function so callers read it the same way they always did, but it
    no longer filters anything by itself: parse() has already dropped these
    rows. Downstream uses are belt-and-braces on data that cannot contain
    them.
    """
    return set(EXCLUDED_LIST)


def all_symbols(positions, stock_tx):
    return {p["sym"] for p in positions} | {sym for _, sym, _, _, _ in stock_tx}


def median(sorted_vals):
    return sorted_vals[len(sorted_vals) // 2] if sorted_vals else float("nan")


def option_report(positions, excluded):
    # Calendar days between trade and expiry, after the posting-date shift.
    # The dominant pattern is Mon-open/Fri-close = 4d; a put sold the previous
    # Friday for the same expiry is a true 7d weekly, hence the split at 6-8.
    buckets = {"P": [(1, 5, "intraweek(<=5d)"), (6, 8, "weekly(7d)"),
                     (9, 14, "~2wk"), (15, 27, "2-4wk"), (28, 45, "monthly")],
               "C": [(1, 7, "<=1wk"), (8, 21, "1-3wk"),
                     (22, 45, "~monthly"), (46, 400, "long")]}
    for right in "PC":
        ps = [p for p in positions
              if p["right"] == right and p["sym"] not in excluded]
        outcomes = Counter(p["how"] for p in ps)
        premium = sorted(p["open_px"] / p["strike"] for p in ps)
        print(f"\n=== {right} options: {len(ps)} closed ===")
        print(f"outcomes: {dict(outcomes)}  "
              f"assign rate: {outcomes['assigned'] / len(ps):.3f}  "
              f"premium/strike median: {median(premium) * 100:.2f}%")
        for lo, hi, name in buckets[right]:
            sub = [p for p in ps if lo <= (p["exp"] - p["open"]).days <= hi]
            if not sub:
                continue
            assigned = sum(1 for p in sub if p["how"] == "assigned")
            prem = sorted(p["open_px"] / p["strike"] for p in sub)
            comm = sorted(-p["comm"] / (p["open_px"] * 100 * p["qty"])
                          for p in sub if p["open_px"])
            print(f"  {name:12s} n={len(sub):4d}  assign rate={assigned / len(sub):.3f}  "
                  f"premium median={median(prem) * 100:.2f}%  "
                  f"comm/premium median={median(comm) * 100:.1f}%")
        early = [p for p in ps if p["how"] == "closed" and p["open_px"]]
        if early:
            frac = sorted(p["close_px"] / p["open_px"] for p in early)
            print(f"  early buy-backs: {len(early)} ({len(early) / len(ps):.0%}), "
                  f"repurchased at median {median(frac):.0%} of premium received")
    # Gross premium counts contracts, not rows -- see the parse() docstring.
    total = {r: sum(p["open_px"] * 100 * p["qty"] for p in positions
                    if p["right"] == r and p["sym"] not in excluded) for r in "PC"}
    print(f"\ngross premium (closed): puts ${total['P']:,.0f}, "
          f"calls ${total['C']:,.0f}, calls/puts = {total['C'] / total['P']:.2f}")


def build_lots(stock_tx, excluded):
    """Reconstruct inventory lots from stock rows.

    Returns (completed, open_lots). A lot is a parcel of shares acquired on one
    day at one price; `completed` records its exit, `open_lots` the parcels
    still held at the end of the statement. Sales that match no open lot are
    legacy shares bought before the window and are dropped.

    Matching is price-first, then FIFO -- see the module docstring. `excluded`
    is the set of symbols to skip; parse() has already dropped EXCLUDED_LIST,
    so this is normally redundant and kept only as an explicit guard.
    """
    buys = defaultdict(list)
    completed = []
    for day, sym, qty, px, _ in sorted(stock_tx):
        if sym in excluded:
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
    open_lots = [dict(sym=sym, in_day=d, in_px=px, qty=q)
                 for sym, lst in buys.items() for d, q, px in lst]
    return completed, sorted(open_lots, key=lambda l: l["in_day"])


def inventory_report(stock_tx, excluded, today):
    completed, open_lots = build_lots(stock_tx, excluded)
    hold = sorted((l["out_day"] - l["in_day"]).days for l in completed)
    same = sum(1 for l in completed if abs(l["out_px"] - l["in_px"]) < 1e-9)
    above = sum(1 for l in completed if l["out_px"] > l["in_px"] + 1e-9)
    below = sum(1 for l in completed if l["out_px"] < l["in_px"] - 1e-9)
    print(f"\n=== inventory lots (price-match-then-FIFO) ===")
    below_lots = [l for l in completed if l["out_px"] < l["in_px"] - 1e-9]
    for l in below_lots:
        print(f"  below-basis exit: {l['sym']} {l['qty']} in @{l['in_px']} "
              f"{l['in_day']} -> out @{l['out_px']} {l['out_day']}")
    print(f"completed: {len(completed)}  holding days median {median(hold)}, "
          f"max {hold[-1] if hold else '-'}  "
          f"exit vs entry strike same/above/below: {same}/{above}/{below}")
    print("open lots (right-censored — the aging tail):")
    for l in open_lots:
        print(f"  {l['sym']:6s} {l['qty']:5d} @ {l['in_px']:8.2f}  "
              f"since {l['in_day']}  ({(today - l['in_day']).days}d)")


def _implied_spot(c_over_k, tau, sigma, r):
    """Invert the Black-Scholes call price (strike = 1) for spot, by bisection."""
    lo, hi = 0.3, 1.5
    for _ in range(60):
        mid = (lo + hi) / 2
        if bs_call(mid, 1.0, tau, sigma, r) < c_over_k:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def assignment_depth_report(positions, excluded, r=0.05):
    """How deep below the strike do assignments land? (draft finding #12)

    Empirical check of the article's derived E[d | assignment]. The statements
    record no market prices, but the first covered call sold at the lot's
    basis prices the gap: inverting Black-Scholes on its premium/strike/tenor
    implies the spot at the moment the call was sold. Caveats: a few days pass
    between expiry-assignment and the call sale (the market can bounce, so
    implied spots slightly ABOVE the strike are common and expected), and a
    volatility must be assumed - results are bracketed with sigma 20%/30%.
    """
    in_universe = [p for p in positions if p["sym"] not in excluded]
    assigned = [p for p in in_universe
                if p["right"] == "P" and p["how"] == "assigned"]
    calls = [p for p in in_universe if p["right"] == "C"]
    rows = []
    for ap in assigned:
        cands = [c for c in calls
                 if c["sym"] == ap["sym"]
                 and abs(c["strike"] - ap["strike"]) < 1e-9
                 and 0 <= (c["open"] - ap["close"]).days <= 21]
        if not cands:
            continue
        c = min(cands, key=lambda c: (c["open"] - ap["close"]).days)
        tau = (c["exp"] - c["open"]).days / 365
        if tau > 0 and c["open_px"]:
            rows.append((ap, c, tau))
    lags = sorted((c["open"] - ap["close"]).days for ap, c, _ in rows)
    print(f"\n=== assignment depth via first at-basis call "
          f"(assigned puts: {len(assigned)}, usable: {len(rows)}, "
          f"median lag {median(lags)}d) ===")
    for sigma in (0.20, 0.30):
        gaps = sorted(1 - _implied_spot(c["open_px"] / c["strike"], tau, sigma, r)
                      for _, c, tau in rows)
        m = len(gaps)
        deep = sum(1 for g in gaps if g > 0.10)
        neg = sum(1 for g in gaps if g < 0)
        print(f"  implied gap below strike (sigma={sigma:.0%}): quartiles "
              f"{gaps[m // 4]:+.3f} / {gaps[m // 2]:+.3f} / {gaps[3 * m // 4]:+.3f}  "
              f"mean {sum(gaps) / m:+.3f}  >10% deep: {deep / m:.0%}  "
              f"above strike: {neg / m:.0%}")
    print("  model-predicted E[gap] = 1 - (1 - E[d|A])/k at the observed "
          "assignment rates (finding #2):")
    # The weekly put runs Monday open to Friday close. That is 5 sessions of
    # trading time but only 4 calendar days, and at this tenor the convention
    # nearly doubles tau_p, so both ends of the bracket are reported.
    for label, tau_p, p_emp in (("Mon-Fri puts (5/252 trading)", 5 / 252, 0.09),
                                ("Mon-Fri puts (4/365 calendar)", 4 / 365, 0.09),
                                ("monthly puts", 1 / 12, 0.118)):
        for sigma in (0.20, 0.30):
            # delta=0, no IV spread: measure "Q" is then the plain drift r,
            # matching the convention this diagnostic has always used.
            C = Config(p_star=p_emp, tau_p=tau_p, sigma=sigma, r=r, delta=0.0)
            k = strike(C, "Q")
            ed = expected_drop(C, "Q")
            print(f"    {label:30s} sigma={sigma:.0%}: k*={k:.3f}  E[d|A]={ed:.3f}  "
                  f"E[gap]={1 - (1 - ed) / k:+.3f}")
    # Config is parameterized by p*, so reach k = 0.95 through the p* that
    # produces it rather than re-deriving the formula outside model.py.
    C = Config(p_star=assign_prob(0.95, 1 / 12, 0.20, r), tau_p=1 / 12,
               sigma=0.20, r=r, delta=0.0)
    ed = expected_drop(C, "Q")
    print(f"    article example (k=0.95, monthly, sigma=20%): E[d|A]={ed:.3f}  "
          f"E[gap]={1 - (1 - ed) / 0.95:+.3f}  (d=0.15 would put E[gap] near +0.11)")


def dividend_report(divs, positions, stock_tx, excluded):
    """Dividend flows, with withholding and wheel attribution.

    Attribution caveat: a receipt is credited to wheel inventory when the
    reconstructed wheel position (from statement stock rows) is > 0 on the
    PAYMENT date; the entitlement actually fixes on the record date a few
    days to weeks earlier, so lots assigned or called away in between can be
    mis-bucketed. Receipts on wheel names with zero reconstructed position
    are legacy shares held from before the statement window.
    """
    wheel = {p["sym"] for p in positions} | {t[1] for t in stock_tx}

    def bucket(sym):
        return "wheel" if sym in wheel else "non-wheel"

    agg = defaultdict(lambda: defaultdict(float))
    for r in divs:
        kind = ("pil" if r["kind"] == "recv" and r["pil"]
                else "cash" if r["kind"] == "recv" else r["kind"])
        agg[bucket(r["sym"])][kind] += r["amount"]
    print(f"\n=== dividend flows ({min(r['day'] for r in divs)} .. "
          f"{max(r['day'] for r in divs)}) ===")
    for b in ("wheel", "non-wheel"):
        a = agg[b]
        gross = a["cash"] + a["pil"]
        if not gross:
            continue
        print(f"  {b:13s} gross ${gross:8,.0f} (cash {a['cash']:,.0f} "
              f"+ in-lieu {a['pil']:,.0f})  net tax {a['tax']:,.0f} "
              f"({-a['tax'] / gross:.1%})  fees {a['fee']:,.0f}  "
              f"net ${gross + a['tax'] + a['fee']:,.0f}")

    # Wheel-inventory attribution: reconstructed position on payment date.
    events = defaultdict(list)
    for day, sym, qty, _, _ in sorted(stock_tx):
        events[sym].append((day, qty))

    def held(sym, day):
        return sum(q for d, q in events[sym] if d <= day)

    per_sym = defaultdict(lambda: defaultdict(float))
    for r in divs:
        if r["sym"] not in wheel:
            continue
        key = "recv" if r["kind"] == "recv" else r["kind"]
        on_wheel = held(r["sym"], r["day"]) > 0
        per_sym[r["sym"]][key] += r["amount"]
        per_sym[r["sym"]]["recv_wheel" if on_wheel else "recv_legacy"] += (
            r["amount"] if r["kind"] == "recv" else 0)
        if r["kind"] == "recv" and on_wheel:
            per_sym[r["sym"]]["n_wheel"] += 1
    tot_wheel = sum(s["recv_wheel"] for s in per_sym.values())
    tot_legacy = sum(s["recv_legacy"] for s in per_sym.values())
    print(f"in-universe receipts on wheel inventory ${tot_wheel:,.0f} vs "
          f"legacy shares ${tot_legacy:,.0f}; by symbol (wheel part only):")
    for sym in sorted(per_sym, key=lambda s: -per_sym[s]["recv_wheel"]):
        s = per_sym[sym]
        if not s["recv_wheel"]:
            continue
        rate = -s["tax"] / s["recv"] if s["recv"] else 0
        print(f"  {sym:6s} {s['n_wheel']:2.0f} receipt rows  "
              f"gross ${s['recv_wheel']:7,.0f}  "
              f"(symbol-level tax rate {rate:.1%})")
    premium = {r: sum(p["open_px"] * 100 * p["qty"] for p in positions
                      if p["right"] == r and p["sym"] not in excluded)
               for r in "PC"}
    print(f"wheel-inventory dividends vs gross premium: "
          f"${tot_wheel:,.0f} / ${premium['P'] + premium['C']:,.0f} = "
          f"{tot_wheel / (premium['P'] + premium['C']):.1%}")


def universe_report(positions, stock_tx, excluded):
    """Print what was excluded, what remains as the universe, and what neither.

    The last part is the one that matters. `all_symbols` sees only what the
    analysis consumed — closed option positions and stock rows — so a name
    that only pays dividends, or only carries a contract that never closed, is
    in universe by EXCLUDED_LIST's default rule and invisible to the only
    report that could say so. Two such names went unnoticed for months (TODO
    IV-5) and finding them took enumerating the raw rows by hand. SYMBOLS_SEEN
    is that enumeration, kept: every symbol the statements mention, against
    every symbol the analysis reaches.
    """
    seen = all_symbols(positions, stock_tx)      # already excluded-free
    dropped = sorted(EXCLUDED_SEEN)
    print(f"\nexcluded, dropped at read ({len(dropped)} symbols, "
          f"{sum(EXCLUDED_SEEN.values())} rows): {' '.join(dropped)}")
    stale = sorted(excluded - set(EXCLUDED_SEEN))
    if stale:  # listed by hand but absent from the statements
        print(f"  listed but not traded in-window ({len(stale)}): "
              f"{' '.join(stale)}")
    unreached = sorted(set(SYMBOLS_SEEN) - seen - excluded - set(EXCLUDED_SEEN))
    detail = " ".join(
        f"{s}({','.join(f'{k}:{n}' for k, n in sorted(SYMBOLS_SEEN[s].items()))})"
        for s in unreached)
    print(f"mentioned in the raw rows ({len(SYMBOLS_SEEN)}), of which never "
          f"reached by any analysis and not excluded ({len(unreached)})"
          + (f": {detail}" if detail else ""))
    print(f"universe ({len(seen)}): {' '.join(sorted(seen))}")


def cluster_report(stock_tx, excluded):
    clusters = Counter(day for day, sym, qty, _, assigned in stock_tx
                       if qty > 0 and assigned and sym not in excluded)
    top = [(str(d), c) for d, c in clusters.most_common(6) if c > 1]
    print(f"\nassignment-day clusters (common shocks): {top}")


def main():
    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB} "
                 "(they are private and not in the repository)")
    print("reading:", ", ".join(paths))
    positions, stock_tx, divs, _live = parse(paths)
    excluded = excluded_symbols()
    universe_report(positions, stock_tx, excluded)
    option_report(positions, excluded)
    inventory_report(stock_tx, excluded, date.today())
    cluster_report(stock_tx, excluded)
    dividend_report(divs, positions, stock_tx, excluded)
    assignment_depth_report(positions, excluded)


if __name__ == "__main__":
    main()
