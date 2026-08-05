"""Daily price history for the names in the statements, cached locally.

The statements (see `analyze_statement.py`) are a *cash* ledger: they record
what was paid and received, never what anything was worth. That is enough for
Track A and nothing else. Marking open inventory, reconstructing the depth
x = ln(K_c/S) of a live lot, inverting an option premium for its implied
volatility, and scoring the operator's entry timing all need one more input:
the share price on a given day. This module supplies it.

Source: the public Yahoo Finance chart endpoint, which returns daily OHLC plus
split and dividend events as JSON. Chosen after stooq — the original plan —
put a JavaScript proof-of-work challenge in front of its CSV endpoint. No API
key, no package: stdlib `urllib` only, so the project's stdlib-only guarantee
survives. The endpoint is unofficial and could change; everything fetched is
cached under `data/` (gitignored, like `statements/`) so that an analysis run
is reproducible offline and a change upstream cannot silently move a published
number. The cache refreshes itself when it falls behind the calendar -- see
`is_stale()` -- so adding statements that run past the cached range fetches the
missing days instead of quietly dropping those dates from the marks.

    python code/prices.py            # fetch/refresh every symbol in statements/
    python code/prices.py ABT ACN    # just these
    python code/prices.py --refresh  # force, ignoring cache freshness

**As-traded vs. adjusted, which matters here.** Yahoo returns closes that are
retroactively *split-adjusted*: after a 2:1 split every earlier close is halved.
The statements are not adjusted — a strike is whatever it was on the day it was
written. Comparing the two directly would misprice every option written before a
split. `Series.close()` therefore returns the **as-traded** price, undoing the
adjustment with the cumulative forward split factor, and `adj_close()` is kept
separately for return calculations where the adjusted series is the correct one.

Inside the statement window the only such event on a quality name is Comcast's
Versant spin-off (2026-01-03), which Yahoo models as a 1067:1000 split; the rest
(NVO 2:1, TRI 963:1000) predate the window and CHPT's 1:20 reverse split is on
an excluded name. The correction is general rather than a special case for
those.

**Open vs. close.** Each row carries both. The close is the right mark for
anything that happens at the end of a session — an expiry, an assignment, an
inventory mark — and is what every consumer uses by default. The *open* is used
for one thing: the spot facing a position at the moment it was sold. The
operator writes on Monday mornings, within the hour after the bell, so pricing
that entry off the same day's close would compare a premium received at ~10am
with the 4pm mark: a look-ahead the trade never had. See `Series.open()`.

Dividends are *not* removed from either series: depth is a price ratio and the
model carries dividends explicitly through delta, so a price series is what is
wanted, not a total-return one.

**The session calendar.** The series also knows which days were sessions,
which is the only place in this project that does. Anything measuring a tenor
against a volatility has to count on that calendar rather than on the wall
clock -- see `Series.sessions_between()` for why, and `iv_panel.session_tenor`
for the consumer. The article's own formulas are unaffected: its tau_p = 1/52
is 4.85 sessions, so its week is already a trading week.
"""

import bisect
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta

CACHE_DIR = os.path.join("data", "prices")
CHART_URL = ("https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
             "?period1={p1}&period2={p2}&interval=1d&events=div%7Csplit")
UA = {"User-Agent": "Mozilla/5.0"}

# Five years of lookback before the earliest statement activity (2025-02), so
# that the trailing 5-year range of the pre-registered `pct5y` feature is
# defined on the first day of the window rather than growing into existence.
HISTORY_START = date(2019, 1, 1)

# A cache whose last row is older than this many days is refetched. Sized for
# a long weekend plus a holiday; see is_stale().
STALE_AFTER_DAYS = 4

# Cache format. Bump when the shape of a row changes: an entry written by an
# older version is treated as stale and refetched, so the upgrade happens by
# itself rather than needing a manual --refresh.
#   1: rows are [day, close]
#   2: rows are [day, close, open]  -- the open is needed to price an entry at
#      the moment it was actually made, see Series.open().
CACHE_VERSION = 2

# Symbols the statement knows under a name Yahoo does not. Renames and ticker
# changes, not aliases of convenience.
SYMBOL_ALIASES = {
    "MPT": "MPW",      # Medical Properties Trust: statement carries both
}

# Known-dead: no history obtainable, for a reason we understand. Recorded so a
# failed fetch is a deliberate omission rather than a silent hole, and so these
# do not re-attempt on every run. Between them they carry $83 of the $60,059 of
# in-universe premium, so nothing here is material.
KNOWN_MISSING = {
    "FGEN": "FibroGen — 1:25 reverse split then delisted",
    "MPW": "Medical Properties Trust — gone under either ticker",
    "MPT": "the pre-rename ticker for MPW; the statement carries both",
    "WBA": "Walgreens — taken private 2025-08, history withdrawn",
    "FOLD": "renamed, and judged not wheel-grade (see EXCLUDED_LIST)",
    # Corporate-action placeholder tickers. These appear only in CORP rows,
    # never as positions, and are not securities Yahoo would know.
    "CHPT1": "adjusted-contract placeholder after the CHPT reverse split",
    "CMCS1": "adjusted-contract placeholder after the Versant spin-off",
    "KYNB1": "adjusted-contract placeholder after the KYNB reverse split",
    "TRI1": "adjusted-contract placeholder from the TRI tender",
}


class Series:
    """One symbol's daily history, with split handling."""

    def __init__(self, sym, rows, splits, divs):
        self.sym = sym
        self.days = [r[0] for r in rows]
        self._close = {r[0]: r[1] for r in rows}
        # Rows from a version-1 cache have no open; those days simply have
        # none, and the entry falls back to the close (see open_on_or_before).
        self._open = {r[0]: r[2] for r in rows if len(r) > 2 and r[2] is not None}
        self.splits = splits          # [(date, factor)], factor = num/den
        self.divs = divs              # [(date, amount_per_share)]
        self._factor = self._forward_factors()

    def _forward_factors(self):
        """Cumulative factor converting an adjusted close to an as-traded one.

        Yahoo divides every close before a split by the split factor. To undo
        that, a close on day d is multiplied by the product of the factors of
        all splits occurring strictly after d.
        """
        factor = {}
        running = 1.0
        for d in reversed(self.days):
            factor[d] = running
            for s_day, f in self.splits:
                if s_day == d:
                    running *= f
        return factor

    def adj_close(self, day):
        """Split-adjusted close, as Yahoo returns it. For return series."""
        return self._close.get(day)

    def close(self, day):
        """As-traded close — comparable with a statement strike."""
        c = self._close.get(day)
        return None if c is None else c * self._factor[day]

    def close_on_or_before(self, day, limit=7):
        """Last as-traded close at or before `day` (holidays, weekends)."""
        for back in range(limit + 1):
            c = self.close(day - timedelta(days=back))
            if c is not None:
                return c
        return None

    def open(self, day):
        """As-traded opening print — comparable with a statement strike.

        Yahoo adjusts the open for splits exactly as it adjusts the close, so
        the same forward factor undoes it.
        """
        o = self._open.get(day)
        return None if o is None else o * self._factor[day]

    def open_on_or_before(self, day, limit=7):
        """Last as-traded open at or before `day`.

        For a position opened intraday: the operator trades within the first
        hour after the bell, so the session's opening print is a far better
        proxy for the spot he faced than that afternoon's close. Using the
        close instead prices a premium received at ~10am against the 4pm mark
        — a look-ahead the entry never had.

        The trade day itself is *inferred* (the statement posts an event a day
        or more later, see `analyze_statement`), and the open is more exposed
        to an off-by-one there than the close is, because overnight gaps are
        where news lands. That error is occasional and unsigned; the bias it
        replaces was systematic.

        Falls back to the close of the same day when no open is recorded, so a
        stale version-1 cache degrades to the old behaviour rather than
        dropping the position out of the analysis entirely.
        """
        for back in range(limit + 1):
            d = day - timedelta(days=back)
            o = self.open(d)
            if o is not None:
                return o
            c = self.close(d)
            if c is not None:
                return c
        return None

    def session_on_or_before(self, day, limit=7):
        """The last session date at or before `day`, or None.

        The *date* behind `open_on_or_before`'s price. A caller that needs
        both the spot an entry faced and the tenor from that entry to its
        expiry must measure the two from the same session: the trade day is
        inferred (see `analyze_statement`), and a day counted one out shifts
        the spot and the tenor independently. Returns the same session
        `open_on_or_before` prices against, including its close fallback,
        because both search the days that carry a row.
        """
        for back in range(limit + 1):
            d = day - timedelta(days=back)
            if d in self._close:
                return d
        return None

    def sessions_between(self, start, end):
        """Number of trading sessions in [start, end], both inclusive.

        **The clock every tenor in this project should be counted on.**
        Realised volatility here is annualised over 252 sessions
        (`iv_panel.forward_vol`), and Black-Scholes takes sigma and tau on one
        clock or it returns nonsense. A put written at Monday's open for
        Friday's close spans five sessions -- 5/252 of a year -- against four
        calendar days, 4/365. Reading the second while annualising the first
        understates sigma*sqrt(tau) by a factor of 1.35, and inverting a
        premium under it hands back that much too much volatility.

        The error vanishes at long tenors, where the two conventions differ
        only by the holiday count, and is worst exactly at the weekly tenor
        the live account trades. See `iv_panel.session_tenor`.
        """
        return (bisect.bisect_right(self.days, end)
                - bisect.bisect_left(self.days, start))

    def adj_on_or_before(self, day, limit=7):
        """Last split-adjusted close at or before `day`."""
        for back in range(limit + 1):
            c = self.adj_close(day - timedelta(days=back))
            if c is not None:
                return c
        return None

    def window(self, start, end):
        """As-traded closes in [start, end], chronological."""
        return [(d, self.close(d)) for d in self.days if start <= d <= end]

    def window_adj(self, start, end):
        """Split-adjusted closes in [start, end], chronological.

        **Use this for anything that takes a ratio of two prices** -- returns,
        volatility, trends, 5-year ranges. The as-traded series is deliberately
        discontinuous at a split, because the traded price really did jump: a
        1:20 reverse split multiplies it by twenty overnight. That is the right
        number to compare with a strike and a catastrophic one to difference.
        SCLX, KYNB and MCRB each reverse-split inside the window and produced
        annualised volatilities of 4,300-7,300% before this was separated out.
        """
        return [(d, self.adj_close(d)) for d in self.days if start <= d <= end]

    def __len__(self):
        return len(self.days)


def _cache_path(sym):
    return os.path.join(CACHE_DIR, f"{sym}.json")


def fetch(sym, start=HISTORY_START, end=None, pause=0.25):
    """Download one symbol. Returns the parsed payload or raises."""
    end = end or (date.today() + timedelta(days=1))
    url = CHART_URL.format(
        sym=SYMBOL_ALIASES.get(sym, sym),
        p1=int(datetime(start.year, start.month, start.day).timestamp()),
        p2=int(datetime(end.year, end.month, end.day).timestamp()))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())
    time.sleep(pause)                  # be a polite client
    res = payload["chart"]["result"][0]
    ts = res["timestamp"]
    quote = res["indicators"]["quote"][0]
    closes = quote["close"]
    opens = quote.get("open") or [None] * len(closes)
    events = res.get("events", {})
    rows = [[date.fromtimestamp(t).isoformat(), c, o]
            for t, c, o in zip(ts, closes, opens) if c is not None]
    splits = [[date.fromtimestamp(int(e["date"])).isoformat(),
               e["numerator"] / e["denominator"]]
              for e in events.get("splits", {}).values()]
    divs = [[date.fromtimestamp(int(e["date"])).isoformat(), e["amount"]]
            for e in events.get("dividends", {}).values()]
    return {"symbol": sym, "version": CACHE_VERSION,
            "fetched": date.today().isoformat(),
            "rows": rows, "splits": sorted(splits), "dividends": sorted(divs)}


def is_stale(payload, today=None):
    """Should this cache entry be refetched?

    True when its last row predates the most recent plausible trading day.
    Without this the cache is permanent: a statement extending past the cached
    range would find no price for its new dates, and the failure is quiet
    rather than loud — `close_on_or_before` searches back a week, finds
    nothing, returns None, and the affected lots drop out of the marks. The
    numbers would move without anything reporting an error.

    True also when the entry predates the current CACHE_VERSION, whatever its
    date: an old row is missing fields the analysis now needs. This check comes
    first, ahead of the attempted-today shortcut, so a format bump refetches
    even a cache written moments ago.

    A symbol already attempted today is not retried, so a delisted name costs
    one request per day rather than one per call.
    """
    today = today or date.today()
    if payload.get("attempted") == today.isoformat():
        return False       # today's fetch already failed; see load()
    if payload.get("version", 1) < CACHE_VERSION:
        return True
    if payload.get("fetched") == today.isoformat():
        return False
    if not payload.get("rows"):
        return True
    last = date.fromisoformat(payload["rows"][-1][0])
    return last < today - timedelta(days=STALE_AFTER_DAYS)


def load(sym, refresh=False):
    """Cached history for one symbol, refetching when absent or stale."""
    path = _cache_path(sym)
    cached = None
    if os.path.exists(path):
        with open(path) as f:
            cached = json.load(f)
    if cached is not None and not refresh and not is_stale(cached):
        payload = cached
    else:
        if sym in KNOWN_MISSING and cached is None:
            return None
        try:
            payload = fetch(sym)
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError,
                IndexError, TypeError) as e:
            if cached is not None:
                # Keep serving what we have rather than losing the history to
                # a transient network failure; stamp the attempt so the retry
                # happens tomorrow, not on the next call.
                print(f"  {sym}: refresh failed ({type(e).__name__}), "
                      f"using cache through {cached['rows'][-1][0]}",
                      file=sys.stderr)
                # `attempted`, not `fetched`: the entry may be stale in format
                # as well as in date, and only `attempted` suppresses both.
                cached["attempted"] = date.today().isoformat()
                with open(path, "w") as f:
                    json.dump(cached, f)
                payload = cached
            else:
                print(f"  {sym}: fetch failed ({type(e).__name__}) — skipped",
                      file=sys.stderr)
                return None
        else:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(path, "w") as f:
                json.dump(payload, f)
    return Series(
        sym,
        # Rows are [day, close] in a version-1 cache and [day, close, open] in
        # a version-2 one; both shapes are accepted, so a serve-the-stale-cache
        # fallback still works after the bump.
        [(date.fromisoformat(r[0]), r[1]) + tuple(r[2:])
         for r in payload["rows"]],
        [(date.fromisoformat(d), f) for d, f in payload["splits"]],
        [(date.fromisoformat(d), a) for d, a in payload["dividends"]])


def load_all(syms, refresh=False):
    """Load many symbols; returns {sym: Series} omitting the unavailable."""
    out = {}
    for s in sorted(set(syms)):
        ser = load(s, refresh=refresh)
        if ser is not None and len(ser):
            out[s] = ser
    return out


def statement_symbols(pattern="statements/*.csv"):
    """Every symbol appearing in an option or stock row of the statements.

    Parsed with deliberately loose patterns rather than by importing
    analyze_statement: this is the *superset* of names to fetch, including the
    excluded and the legacy, and it should not inherit that module's filters.
    """
    opt = re.compile(r"^[+-]\d+ (\S+) \d{2}[A-Z]{3}\d{2} ")
    stk = re.compile(r"^[+-]\d+ (\S+?)(?: \(assigned\))? price: ")
    syms = set()
    import csv
    for path in sorted(glob.glob(pattern)):
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) < 5 or row[4] not in ("OPTION", "STOCK"):
                    continue
                m = opt.match(row[3].strip()) or stk.match(row[3].strip())
                if m:
                    syms.add(m[1])
    return sorted(syms)


def main():
    args = sys.argv[1:]
    refresh = "--refresh" in args
    want = [a for a in args if not a.startswith("-")] or statement_symbols()
    print(f"symbols: {len(want)}  cache: {CACHE_DIR}/"
          f"{'  (forced refresh)' if refresh else ''}")
    got, missing = {}, []
    for s in want:
        ser = load(s, refresh=refresh)
        if ser is None or not len(ser):
            missing.append(s)
        else:
            got[s] = ser
    print(f"loaded {len(got)}; unavailable {len(missing)}: {missing}")
    span = [(s.days[0], s.days[-1]) for s in got.values()]
    print(f"earliest history {min(a for a, _ in span)}, "
          f"latest close {max(b for _, b in span)}")
    short = [(s, ser.days[0]) for s, ser in got.items()
             if ser.days[0] > date(2020, 1, 1)]
    if short:
        print("short histories (5-year lookback incomplete at window start):")
        for s, d in sorted(short, key=lambda x: -x[1].toordinal()):
            print(f"  {s:6s} starts {d}")
    with_splits = {s: ser.splits for s, ser in got.items() if ser.splits}
    print("split events on record:")
    for s, sp in sorted(with_splits.items()):
        print(f"  {s:6s} " + ", ".join(f"{d} x{f:.4f}" for d, f in sp))


if __name__ == "__main__":
    main()
