"""Earnings dates for the calibration universe, from SEC EDGAR, cached locally.

Step 1 of `drafts/2026-11-21-moving-volatility-plan.md` (its decisions 3, 6 and 7).
The plan fits earnings, then unscheduled jumps, then the volatility state, each on
what the previous step leaves: an earnings day left in the sample is counted once
as a jump and again as a volatility swing. So the first thing the calibration needs
is the day each name announced each quarter's results, and a price history cannot
supply it -- a gap on results looks like a gap on any other news.

**The universe** (decision 7) is the S&P 500 Dividend Aristocrats as ProShares'
NOBL held them on 2026-11-20, pinned below with their EDGAR identifiers: index
membership changes, and a calibration that re-read it would move under its own
results. It is not the names the live account trades. Those are its own data, and
include foreign issuers EDGAR cannot date. A name's day is in the sample only
while its market cap that day was CAP_FLOOR or more, the live account's rule
applied at each date. A floor on today's cap would keep the years a name now large
spent small, whatever margin it carried. See `Name.cap()`.

**The dates** (decision 6). A US filer announces results on an 8-K carrying Item
2.02, *Results of Operations and Financial Condition*, which exists from
2004-08-23; EDGAR's submissions API lists every filing with its item codes. Some
filers make extra Item 2.02 filings -- AbbVie one at each quarter's start -- so the
date kept for a quarter is the **last** Item 2.02 filed within PICK_DAYS before
each 10-Q or 10-K. A quarter with none is **left out whole**, its earnings and its
other days alike, rather than guessed, and so is the stretch after a name's last
periodic report. ED until about 2017 and TROW until about 2022 announced most
results without one. The obvious stand-in, the last 8-K carrying Item 8.01 or
7.01, lands on a price gap only 14% of the time, against 38% for Item 2.02
dates; elsewhere a missing quarter is usually a release filed with no item but
9.01, too few to be worth a rule (the plan's step 1 records both probes).

**The caches** live under `data/aristocrats/` (gitignored): EDGAR's filings and
share counts, and the names' daily prices from Yahoo through `prices.fetch`. They
are kept apart from the live account's `data/prices`, which every statement
tranche refreshes, so that the two universes cannot mix. The window is fixed (HISTORY_START to WINDOW_END), so a
cache once written is the input and is never refreshed unless asked.

**The contact.** EDGAR's fair-access policy asks an automated client to declare a
contact in its User-Agent. It is read from the environment variable named by
CONTACT_ENV, so the repository carries no address; it is needed only when
something has to be fetched.

    python code/earnings.py             # fetch what is missing, report coverage
    python code/earnings.py ED TROW     # just these
    python code/earnings.py --refresh   # refetch everything
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from bisect import bisect_left, bisect_right
from datetime import date, timedelta
from math import log
from statistics import median

import prices

CACHE_DIR = os.path.join("data", "aristocrats")
EDGAR_DIR = os.path.join(CACHE_DIR, "edgar")
PRICE_DIR = os.path.join(CACHE_DIR, "prices")
CONTACT_ENV = "WHEEL_EDGAR_CONTACT"
EDGAR_PAUSE = 0.15          # seconds between requests; the policy's limit is 10 a second

# Prices from the first full year of Item 2.02, to the holdings file's date.
HISTORY_START = date(2005, 1, 1)
WINDOW_END = date(2026, 11, 20)
CAP_FLOOR = 10e9
PICK_DAYS = 60

# NOBL's holdings on 2026-11-20 (ProShares' daily holdings file), ticker -> CIK.
UNIVERSE = {
    "ABBV": "0001551152",   # AbbVie
    "ABT":  "0000001800",   # Abbott Laboratories
    "ADM":  "0000007084",   # Archer-Daniels-Midland
    "ADP":  "0000008670",   # Automatic Data Processing
    "AFL":  "0000004977",   # Aflac
    "ALB":  "0000915913",   # Albemarle
    "AMCR": "0001748790",   # Amcor
    "AOS":  "0000091142",   # A. O. Smith
    "APD":  "0000002969",   # Air Products & Chemicals
    "ATO":  "0000731802",   # Atmos Energy
    "BDX":  "0000010795",   # Becton Dickinson
    "BEN":  "0000038777",   # Franklin Templeton
    "BF-B": "0000014693",   # Brown-Forman, Class B
    "BRO":  "0000079282",   # Brown & Brown
    "CAH":  "0000721371",   # Cardinal Health
    "CAT":  "0000018230",   # Caterpillar
    "CB":   "0000896159",   # Chubb
    "CHD":  "0000313927",   # Church & Dwight
    "CHRW": "0001043277",   # C.H. Robinson Worldwide
    "CINF": "0000020286",   # Cincinnati Financial
    "CL":   "0000021665",   # Colgate-Palmolive
    "CLX":  "0000021076",   # Clorox
    "CTAS": "0000723254",   # Cintas
    "CVX":  "0000093410",   # Chevron
    "DOV":  "0000029905",   # Dover
    "ECL":  "0000031462",   # Ecolab
    "ED":   "0001047862",   # Consolidated Edison
    "EMR":  "0000032604",   # Emerson Electric
    "ERIE": "0000922621",   # Erie Indemnity, Class A
    "ES":   "0000072741",   # Eversource Energy
    "ESS":  "0000920522",   # Essex Property Trust
    "EXPD": "0000746515",   # Expeditors International
    "FAST": "0000815556",   # Fastenal
    "FDS":  "0001013237",   # FactSet Research Systems
    "FRT":  "0000034903",   # Federal Realty
    "GD":   "0000040533",   # General Dynamics
    "GPC":  "0000040987",   # Genuine Parts
    "GWW":  "0000277135",   # W.W. Grainger
    "HRL":  "0000048465",   # Hormel Foods
    "IBM":  "0000051143",   # IBM
    "ITW":  "0000049826",   # Illinois Tool Works
    "JNJ":  "0000200406",   # Johnson & Johnson
    "KMB":  "0000055785",   # Kimberly-Clark
    "KO":   "0000021344",   # Coca-Cola
    "LIN":  "0001707925",   # Linde plc
    "LOW":  "0000060667",   # Lowe's
    "MCD":  "0000063908",   # McDonald's
    "MDT":  "0001613103",   # Medtronic plc
    "MKC":  "0000063754",   # McCormick, non-voting
    "NDSN": "0000072331",   # Nordson
    "NEE":  "0000753308",   # NextEra Energy
    "NUE":  "0000073309",   # Nucor
    "O":    "0000726728",   # Realty Income
    "PEP":  "0000077476",   # PepsiCo
    "PG":   "0000080424",   # Procter & Gamble
    "PNR":  "0000077360",   # Pentair
    "PPG":  "0000079879",   # PPG Industries
    "ROP":  "0000882835",   # Roper Technologies
    "SHW":  "0000089800",   # Sherwin-Williams
    "SJM":  "0000091419",   # J.M. Smucker
    "SPGI": "0000064040",   # S&P Global
    "SWK":  "0000093556",   # Stanley Black & Decker
    "SYY":  "0000096021",   # Sysco
    "TGT":  "0000027419",   # Target
    "TROW": "0001113169",   # T. Rowe Price
    "WMT":  "0000104169",   # Walmart
    "WST":  "0000105770",   # West Pharmaceutical Services
    "XOM":  "0002115436",   # ExxonMobil Holdings
}

# A reorganized company files under a new CIK, and its history stays under the old
# one; Yahoo carries the price history through under the new ticker. The
# predecessor's filings and share counts are read as the name's own.
PREDECESSORS = {
    "LIN": ("0000884905",),   # Praxair (renamed Linde Inc), until the 2018 combination
    "MDT": ("0000064670",),   # Medtronic Inc, until Medtronic plc became the parent in 2015
    "XOM": ("0000034088",),   # Exxon Mobil Corp, until the 2026 holding company
}

# Names whose cover-page share count is reported per share class, so EDGAR's API
# carries no total under dei:EntityCommonStockSharesOutstanding (AOS's stops in
# 2015): their all-class basic weighted-average count stands in. ERIE reports
# neither, and its count is read off its latest 10-K cover -- see _erie_counts().
CLASS_REPORTERS = ("AOS", "BF-B", "HRL", "MKC")
ERIE_B_IN_A = 2400          # each ERIE Class B share converts into 2,400 Class A


def _fetch(url, path, refresh=False, raw=False):
    """EDGAR document at `url`, cached at `path`. A 404 is cached as null."""
    if refresh or not os.path.exists(path):
        contact = os.environ.get(CONTACT_ENV)
        if not contact:
            raise RuntimeError(
                f"{url} is not cached and {CONTACT_ENV} is not set. EDGAR asks an "
                f"automated client to declare a contact: set it to a name and an "
                f"e-mail address, e.g. 'Jane Doe jane@example.com'.")
        req = urllib.request.Request(
            url, headers={"User-Agent": contact, "Accept-Encoding": "identity"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            data = b"null"
        finally:
            time.sleep(EDGAR_PAUSE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "wb") as f:
            f.write(data)
        os.replace(path + ".tmp", path)
    with open(path, "rb") as f:
        data = f.read()
    if raw:
        return None if data == b"null" else data
    return json.loads(data)


def _filing_blocks(cik, refresh=False):
    """The CIK's filings, as EDGAR's column blocks (form, filingDate, items, ...).

    The submissions record carries the latest thousand filings; older ones are
    in paged files it names, fetched alongside.
    """
    sub = _fetch(f"https://data.sec.gov/submissions/CIK{cik}.json",
                 os.path.join(EDGAR_DIR, f"CIK{cik}.json"), refresh)
    blocks = [sub["filings"]["recent"]]
    for page in sub["filings"].get("files", []):
        blocks.append(_fetch(f"https://data.sec.gov/submissions/{page['name']}",
                             os.path.join(EDGAR_DIR, page["name"]), refresh))
    return blocks


def _submissions(cik, refresh=False):
    """The CIK's filings as (form, filed, items) rows."""
    rows = []
    for b in _filing_blocks(cik, refresh):
        rows += zip(b["form"], b["filingDate"], b.get("items", [""] * len(b["form"])))
    return [(f, date.fromisoformat(d), i) for f, d, i in rows]


def _concept(cik, taxonomy, name, refresh=False):
    """One XBRL concept's facts for a CIK, or None when the CIK reports none."""
    return _fetch(
        f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{name}.json",
        os.path.join(EDGAR_DIR, f"{cik}-{taxonomy}-{name}.json"), refresh)


def _latest_per_date(facts):
    """One count per date: the latest filing's, and the shortest period's.

    A 10-Q reports the quarter's weighted-average count and the year-to-date's
    with the same end date; the quarter's is the one for that date. Filings are
    ordered by date, not accession number, whose leading part names the agent
    that filed it.
    """
    best = {}
    for f in facts:
        if date.fromisoformat(f["filed"]) > WINDOW_END:
            continue
        key = (f["filed"], f["accn"], f.get("start", ""))
        if f["end"] not in best or key > best[f["end"]][0]:
            best[f["end"]] = (key, f["val"])
    return [(date.fromisoformat(d), v) for d, (_, v) in sorted(best.items())]


def _erie_counts(refresh=False):
    """ERIE's Class A shares plus its Class B on conversion, off each 10-K's cover.

    One count a year, dated at its filing; a cover the pattern cannot read is
    skipped and reported, and the latest must be read.
    """
    cik = UNIVERSE["ERIE"]
    filings = []
    for b in _filing_blocks(cik, refresh):
        filings += zip(b["form"], b["filingDate"], b["accessionNumber"],
                       b["primaryDocument"])
    counts = []
    for f, d, acc, doc in filings:
        filed = date.fromisoformat(d)
        if f != "10-K" or not HISTORY_START <= filed <= WINDOW_END:
            continue
        acc = acc.replace("-", "")
        page = _fetch(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}",
                      os.path.join(EDGAR_DIR, f"{cik}-10-K-{acc}.htm"), refresh, raw=True)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|&#?\w+;", " ",
                                          (page or b"").decode("utf-8", "replace")))
        a = re.search(r"([\d,]{6,}) shares of Class A common stock", text, re.I)
        b = re.search(r"([\d,]{3,}) shares of Class B common stock", text, re.I)
        if a and b:
            na, nb = (int(m.group(1).replace(",", "")) for m in (a, b))
            counts.append((filed, na + ERIE_B_IN_A * nb))
        else:
            print(f"  ERIE: no share counts read off the 10-K cover of {d}", file=sys.stderr)
    counts.sort()
    if not counts or counts[-1][0] < WINDOW_END - timedelta(days=400):
        raise ValueError("ERIE: the latest 10-K cover was not read")
    return counts


def _share_counts(sym, refresh=False):
    """[(date, shares as counted that day)], and where they came from."""
    if sym == "ERIE":
        return _erie_counts(refresh), "10-K cover"
    if sym in CLASS_REPORTERS:
        d = _concept(UNIVERSE[sym], "us-gaap",
                     "WeightedAverageNumberOfSharesOutstandingBasic", refresh)
        return _latest_per_date(d["units"]["shares"]), "weighted-average"
    counts = {}
    for cik in PREDECESSORS.get(sym, ()) + (UNIVERSE[sym],):
        d = _concept(cik, "dei", "EntityCommonStockSharesOutstanding", refresh)
        if d:
            counts.update(_latest_per_date(d["units"]["shares"]))
    counts = sorted(counts.items())
    if not counts or counts[-1][0] < WINDOW_END - timedelta(days=400):
        raise ValueError(f"{sym}: cover-page share count missing or stale "
                         f"(last {counts[-1][0] if counts else 'none'}); "
                         f"does it belong in CLASS_REPORTERS?")
    return counts, "cover page"


def _prices(sym, refresh=False):
    """The name's daily history over the window, as a `prices.Series`."""
    path = os.path.join(PRICE_DIR, f"{sym}.json")
    if refresh or not os.path.exists(path):
        payload = prices.fetch(sym, start=HISTORY_START,
                               end=WINDOW_END + timedelta(days=1))
        os.makedirs(PRICE_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f)
    with open(path) as f:
        payload = json.load(f)
    rows = [(date.fromisoformat(r[0]),) + tuple(r[1:]) for r in payload["rows"]
            if date.fromisoformat(r[0]) <= WINDOW_END]
    return prices.Series(
        sym, rows,
        [(date.fromisoformat(d), x) for d, x in payload["splits"]],
        [(date.fromisoformat(d), x) for d, x in payload["dividends"]])


def pick_dates(rows, end=WINDOW_END):
    """Earnings dates and undated quarters from a filer's (form, filed, items) rows.

    Returns (dates, undated): `dates` the last Item 2.02 8-K within PICK_DAYS
    before each 10-Q or 10-K, sorted; `undated` the (start, end) spans, both
    inclusive, of the quarters that have none -- each from the day after the
    previous periodic report to the day of its own. The stretch after the last
    periodic report is undated too: its results, if out, are confirmed by a
    report the window does not hold. Filings after `end` are ignored, so a
    cache fetched later gives the same answer.
    """
    rows = [(f, d, i) for f, d, i in rows if d <= end]
    results = sorted({d for f, d, i in rows if f == "8-K" and "2.02" in i.split(",")})
    periodic = sorted({d for f, d, _ in rows if f in ("10-Q", "10-K")})
    dates, undated = set(), []
    for k, p in enumerate(periodic):
        j = bisect_right(results, p) - 1
        if j >= 0 and results[j] >= p - timedelta(days=PICK_DAYS):
            dates.add(results[j])
        else:
            start = periodic[k - 1] + timedelta(days=1) if k else date.min
            undated.append((start, p))
    undated.append((periodic[-1] + timedelta(days=1) if periodic else date.min, date.max))
    return sorted(dates), undated


class Name:
    """One name of the universe: its prices, its share counts and its dates."""

    def __init__(self, sym, series, counts, source, dates, undated):
        self.sym = sym
        self.series = series
        self.source = source          # where the share counts came from
        self.dates = dates
        self.undated = undated
        # Counts are as filed; the closes are split-adjusted to the last day of
        # the window, so each count is put on that basis -- multiplied by every
        # split after it, the convention of `prices.Series._forward_factors`.
        self._count_days = [d for d, _ in counts]
        self._counts = [n * self._splits_after(d) for d, n in counts]
        self._undated_ends = [e for _, e in undated]

    def _splits_after(self, day):
        k = 1.0
        for d, f in self.series.splits:
            if d > day:
                k *= f
        return k

    def cap(self, day):
        """Market cap on a session: the latest count dated on or before it, times
        the close. Before the first count (2009-2011 for most names, as XBRL
        arrived) the first count stands in."""
        px = self.series.adj_close(day)
        if px is None:
            return None
        j = max(bisect_right(self._count_days, day) - 1, 0)
        return self._counts[j] * px

    def dated(self, day):
        """False inside a quarter whose results date could not be found."""
        k = bisect_left(self._undated_ends, day)
        return not (k < len(self.undated) and self.undated[k][0] <= day)

    def in_sample(self, day):
        """The day counts: the cap was CAP_FLOOR or more, and its quarter is dated."""
        cap = self.cap(day)
        return cap is not None and cap >= CAP_FLOOR and self.dated(day)


def load(sym, refresh=False):
    """One name of UNIVERSE, fetching whatever is not cached."""
    rows = []
    for cik in PREDECESSORS.get(sym, ()) + (UNIVERSE[sym],):
        rows += _submissions(cik, refresh)
    dates, undated = pick_dates(rows)
    counts, source = _share_counts(sym, refresh)
    return Name(sym, _prices(sym, refresh), counts, source, dates, undated)


def load_universe(refresh=False):
    """{sym: Name} for every name in UNIVERSE."""
    return {s: load(s, refresh) for s in sorted(UNIVERSE)}


def _robust_z(closes):
    """|log return| over a robust sd of the 60 sessions before it (median |r| / 0.6745).

    On split-adjusted closes, dividends not added back: an ex-dividend drop is
    about one robust sd on a utility and less elsewhere, small beside the 3 sd
    the report counts."""
    r = [None] + [log(b / a) if a and b else None for a, b in zip(closes, closes[1:])]
    z = [None] * len(r)
    for i in range(61, len(r)):
        past = [abs(x) for x in r[i - 60:i] if x is not None]
        sd = median(past) / 0.6745 if past else 0
        if r[i] is not None and sd > 0:
            z[i] = abs(r[i]) / sd
    return z


def report(names):
    """Per name: sample years, dates a year, undated quarters, and how often the
    two sessions from a date move more than 3 robust sd -- then the same pooled,
    against every other two-session window in the sample. A wrong date shows as
    a hit rate near the other windows'."""
    hits, other = [], []
    print(f"{'name':5} {'cap':>7}  {'counts':16} {'in sample':>18} {'dates':>6} "
          f"{'a year':>6} {'undated':>7} {'z>3':>5}")
    for sym, n in names.items():
        days = n.series.days
        z = _robust_z([n.series.adj_close(d) for d in days])
        ok = [n.in_sample(d) for d in days]
        marks, own = set(), []
        for d in n.dates:
            i = bisect_left(days, d)
            if i + 1 >= len(days) or not ok[i]:
                continue
            w = [x for x in (z[i], z[i + 1]) if x is not None]
            if w:
                own.append(max(w))
                marks.update((i, i + 1))
        other += [max(z[i], z[i + 1]) for i in range(61, len(days) - 1)
                  if ok[i] and z[i] is not None and z[i + 1] is not None
                  and i not in marks]
        hits += own
        years = sum(ok[61:]) / 252
        first = next((d for d, o in zip(days[61:], ok[61:]) if o), None)
        lost = sum(1 for _, e in n.undated if HISTORY_START <= e <= WINDOW_END)
        print(f"{sym:5} {n.cap(days[-1]) / 1e9:6.1f}B  {n.source:16} "
              f"{years:5.1f}y from {str(first or '-'):10} {len(own):6} "
              f"{len(own) / years if years else 0:6.1f} {lost:7} "
              f"{sum(1 for h in own if h > 3) / max(len(own), 1):5.0%}")
    share = lambda xs: sum(1 for x in xs if x > 3) / len(xs)
    print(f"\nmoves over 3 robust sd: {share(hits):.1%} of {len(hits)} earnings windows, "
          f"{share(other):.1%} of {len(other)} others")


def main():
    args = sys.argv[1:]
    refresh = "--refresh" in args
    named = [a for a in args if not a.startswith("-")]
    unknown = [s for s in named if s not in UNIVERSE]
    if unknown:
        sys.exit(f"not in the universe: {' '.join(unknown)}")
    syms = named or sorted(UNIVERSE)
    print(f"{len(syms)} names, cache {CACHE_DIR}/, window {HISTORY_START} to {WINDOW_END}"
          f"{', refetching' if refresh else ''}\n")
    report({s: load(s, refresh) for s in syms})


if __name__ == "__main__":
    main()
