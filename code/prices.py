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
number.

    python code/prices.py            # fetch/refresh every symbol in statements/
    python code/prices.py ABT ACN    # just these

**As-traded vs. adjusted, which matters here.** Yahoo returns closes that are
retroactively *split-adjusted*: after a 2:1 split every earlier close is halved.
The statements are not adjusted — a strike is whatever it was on the day it was
written. Comparing the two directly would misprice every option written before a
split. `Series.close()` therefore returns the **as-traded** price, undoing the
adjustment with the cumulative forward split factor, and `adj_close()` is kept
separately for return calculations where the adjusted series is the correct one.

Inside the statement window the only such event on a quality name is Comcast's
Versant spin-off (2026-01-03), which Yahoo models as a 1067:1000 split; the rest
(NVO 2:1, TRI 963:1000) predate the window and CHPT's 1:20 reverse split is a
junk name. The correction is general rather than a special case for those.

Dividends are *not* removed from either series: depth is a price ratio and the
model carries dividends explicitly through delta, so a price series is what is
wanted, not a total-return one.
"""

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

# Symbols the statement knows under a name Yahoo does not. Renames and ticker
# changes, not aliases of convenience.
SYMBOL_ALIASES = {
    "MPT": "MPW",      # Medical Properties Trust: statement carries both
}

# Known-dead: delisted or renamed beyond recovery. Recorded so a failed fetch
# is a deliberate omission rather than a silent hole. Both are junk-universe
# names and neither is one of the two junk lots the analysis counts (ALT, BEKE).
KNOWN_MISSING = {
    "FGEN": "FibroGen — 1:25 reverse split then delisted; no Yahoo history",
    "MPW": "Medical Properties Trust — no history under either ticker",
}


class Series:
    """One symbol's daily history, with split handling."""

    def __init__(self, sym, rows, splits, divs):
        self.sym = sym
        self.days = [r[0] for r in rows]
        self._close = {r[0]: r[1] for r in rows}
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

    def window(self, start, end):
        """As-traded closes in [start, end], chronological."""
        return [(d, self.close(d)) for d in self.days if start <= d <= end]

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
    closes = res["indicators"]["quote"][0]["close"]
    events = res.get("events", {})
    rows = [[date.fromtimestamp(t).isoformat(), c]
            for t, c in zip(ts, closes) if c is not None]
    splits = [[date.fromtimestamp(int(e["date"])).isoformat(),
               e["numerator"] / e["denominator"]]
              for e in events.get("splits", {}).values()]
    divs = [[date.fromtimestamp(int(e["date"])).isoformat(), e["amount"]]
            for e in events.get("dividends", {}).values()]
    return {"symbol": sym, "fetched": date.today().isoformat(),
            "rows": rows, "splits": sorted(splits), "dividends": sorted(divs)}


def load(sym, refresh=False):
    """Cached history for one symbol, fetching if absent. None if unavailable."""
    path = _cache_path(sym)
    if not refresh and os.path.exists(path):
        with open(path) as f:
            payload = json.load(f)
    else:
        if sym in KNOWN_MISSING:
            return None
        try:
            payload = fetch(sym)
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError,
                IndexError, TypeError) as e:
            print(f"  {sym}: fetch failed ({type(e).__name__}) — skipped",
                  file=sys.stderr)
            return None
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f)
    return Series(
        sym,
        [(date.fromisoformat(d), c) for d, c in payload["rows"]],
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
    analyze_statement: this is the *superset* of names to fetch, including junk
    and legacy, and it should not inherit that module's filters.
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
    want = sys.argv[1:] or statement_symbols()
    print(f"symbols: {len(want)}  cache: {CACHE_DIR}/")
    got, missing = {}, []
    for s in want:
        ser = load(s)
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
