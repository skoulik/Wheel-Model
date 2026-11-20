"""BXM's published betas, reproduced from the index's own history.

    python code/bxm_real.py                         # the three tables
    python code/bxm_real.py --fetch-sp500tr         # get the S&P 500 series from Yahoo
    python code/bxm_real.py --from-yahoo-page F.mht # ...or from a saved Yahoo page

The model-side half of the comparison is `bxm_beta.py`: the index's
construction run through the model.  This is the other half, on the real
series, and it answers three questions the model cannot:

1. **Is the published figure an estimator artefact?**  Israelov and Nielsen
   (2015, Table 6) give BXM 0.46 up / 0.85 down, plain 0.62, over 1996-2014 on
   21-day overlapping returns, and no paper says how the split is fitted.  The
   real index reproduces it with section 09's own estimator -- least squares
   with an intercept on each side of a zero index return -- and a fit forced
   through the origin misses the down side.  So the up-beta is a property of
   the index, not of how it was measured.
2. **Is it the options or the path?**  A synthetic BXM on the real S&P 500
   path, rolled on the real third Fridays and priced by Black-Scholes,
   reproduces the real index's betas when each option is priced at the
   volatility of its month (trailing 21-day realized), and does not at a
   constant volatility.  Nothing beyond Black-Scholes is needed, given a
   volatility that moves.
3. **How much does the index's volatility move?**  Monthly realized
   volatility from 21-day blocks: the standard deviation of its log, its
   month-to-month autocorrelation, and a month's return's correlation with its
   change.  These are the figures `wheel_sim.SV_*` borrows (TODO II-38).

**The data are not in the repository**: the series are Cboe's, S&P's and
FRED's, and the repository is public.  Put them in `data/market/` (gitignored):

    BXM_History.csv   Cboe's daily BXM history, from 2002-03-22:
                      https://cdn.cboe.com/api/global/us_indices/daily_prices/BXM_History.csv
    DTB3.csv          FRED's 3-month T-bill, daily, as CSV:
                      https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3
    SP500TR.csv       the S&P 500 total-return index, daily, as date,close:
                      --fetch-sp500tr reads it from Yahoo's chart endpoint
                      (prices.py's source) where that is reachable; where it is
                      not, save https://finance.yahoo.com/quote/%5ESP500TR/history/
                      with the range set to Max as a single-file page (.mht) and
                      pass it to --from-yahoo-page.

Windows are fixed by date, so a longer download reproduces the same figures.
`verify_examples.py` runs this when the three files are present and says SKIP
when they are not.  Stdlib only.
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime, timedelta
from math import erf, exp, log, sqrt

DATA_DIR = os.path.join("data", "market")
FILES = {"bxm": "BXM_History.csv", "spx": "SP500TR.csv", "tbill": "DTB3.csv"}
DAYS = 21
WINDOWS = ((date(2002, 3, 22), date(2014, 12, 31)),     # overlaps the published sample
           (date(2002, 3, 22), date(2026, 11, 19)))     # everything to 2026-11-19
SWING_WINDOW = (date(1988, 1, 4), date(2026, 11, 19))
PUBLISHED = (0.46, 0.85, 0.62)


def _path(name, root):
    return os.path.join(root, DATA_DIR, FILES[name])


def available(root="."):
    return all(os.path.exists(_path(k, root)) for k in FILES)


def _read(path, fmt, col):
    out = {}
    with open(path, newline="") as fh:
        rows = csv.reader(fh)
        head = next(rows)
        i = head.index(col)
        for row in rows:
            v = row[i].strip()
            if v and v != ".":
                out[datetime.strptime(row[0], fmt).date()] = float(v)
    return out


def load(root="."):
    """{'bxm': {date: level}, 'spx': {...}, 'tbill': {date: annual %}}."""
    return {"bxm": _read(_path("bxm", root), "%m/%d/%Y", "BXM"),
            "spx": _read(_path("spx", root), "%Y-%m-%d", "close"),
            "tbill": _read(_path("tbill", root), "%Y-%m-%d", "DTB3")}


# ----------------------------------------------------------------------
# Fits
# ----------------------------------------------------------------------

def _slopes(x, y, cut=0.0):
    """Least squares with an intercept on each side of `cut`: (up, down)."""
    out = []
    for keep in (lambda v: v > cut, lambda v: v < cut):
        px = [a for a in x if keep(a)]
        py = [b for a, b in zip(x, y) if keep(a)]
        n = len(px)
        mx, my = sum(px) / n, sum(py) / n
        cov = sum((a - mx) * (b - my) for a, b in zip(px, py)) / n
        var = sum((a - mx) ** 2 for a in px) / n
        out.append(cov / var)
    return tuple(out)


def _plain(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    return (sum((a - mx) * (b - my) for a, b in zip(x, y))
            / sum((a - mx) ** 2 for a in x))


def _origin(x, y):
    """Each side through the origin: the fit that misses the down side."""
    return tuple(sum(a * b for a, b in zip(x, y) if keep(a))
                 / sum(a * a for a in x if keep(a))
                 for keep in (lambda v: v > 0, lambda v: v < 0))


def _corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    return (sum((x - ma) * (y - mb) for x, y in zip(a, b))
            / sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)))


def _windows(days, series):
    """21-day returns starting on every trading day."""
    v = [series[d] for d in days]
    return [v[i + DAYS] / v[i] - 1 for i in range(len(v) - DAYS)]


def real_betas(D, start, end):
    """The real index's betas on 21-day overlapping returns, several ways."""
    days = sorted(d for d in set(D["bxm"]) & set(D["spx"]) if start <= d <= end)
    x, y = _windows(days, D["spx"]), _windows(days, D["bxm"])
    # Excess of the T-bill, compounded daily over each window; the last
    # observation carried forward over FRED's holidays.
    tb, last, j = [], None, 0
    tdays = sorted(D["tbill"])
    for d in days:
        while j < len(tdays) and tdays[j] <= d:
            last = D["tbill"][tdays[j]]
            j += 1
        tb.append(last / 100)
    rf = []
    for i in range(len(days) - DAYS):
        g = 1.0
        for k in range(i, i + DAYS):
            g *= 1 + tb[k] / 252
        rf.append(g - 1)
    xe = [a - c for a, c in zip(x, rf)]
    ye = [b - c for b, c in zip(y, rf)]
    return {"days": len(days), "windows": len(x),
            "total": _slopes(x, y) + (_plain(x, y),),
            "excess": _slopes(xe, ye) + (_plain(xe, ye),),
            "split at the mean": _slopes(x, y, sum(x) / len(x)),
            "through the origin": _origin(x, y)}


# ----------------------------------------------------------------------
# A synthetic BXM on the real path
# ----------------------------------------------------------------------

def _call(s, k, tau, iv, r=0.03):
    """Black-Scholes call on the total-return index (no dividend: it is paid in)."""
    if tau <= 0:
        return max(s - k, 0.0)
    d1 = (log(s / k) + (r + iv * iv / 2) * tau) / (iv * sqrt(tau))
    d2 = d1 - iv * sqrt(tau)
    n = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
    return s * n(d1) - k * exp(-r * tau) * n(d2)


def _third_friday(y, m):
    d = date(y, m, 15)
    return d + timedelta((4 - d.weekday()) % 7)


def synthetic(D, start, end, iv_rule):
    """A buy-write on the real S&P 500 path: an at-the-money call written on
    each monthly expiry (the third Friday, or the session before it), held to
    the next, marked daily at the implied volatility `iv_rule` gives.  Returns
    its betas and the correlation of its 21-day returns with the real BXM's."""
    days = sorted(d for d in set(D["bxm"]) & set(D["spx"]) if start <= d <= end)
    S = [D["spx"][d] for d in days]
    rolls = []
    for y in range(start.year, end.year + 1):
        for m in range(1, 13):
            tf = _third_friday(y, m)
            cand = [d for d in days if tf - timedelta(7) < d <= tf]
            if cand:
                rolls.append(cand[-1])
    roll_set = set(rolls)
    V = [1.0]
    k = expiry = units = None
    for i, d in enumerate(days):
        if i > 0:
            tau = max((expiry - d).days, 0) / 365
            V.append(units * (S[i] - _call(S[i], k, tau, iv_rule(i, S))))
        if d in roll_set or k is None:
            k = S[i]
            nxt = [x for x in rolls if x > d]
            expiry = nxt[0] if nxt else d + timedelta(28)
            units = V[i] / (S[i] - _call(S[i], k, (expiry - d).days / 365, iv_rule(i, S)))
    xs = [S[i + DAYS] / S[i] - 1 for i in range(len(S) - DAYS)]
    ys = [V[i + DAYS] / V[i] - 1 for i in range(len(V) - DAYS)]
    real = _windows(days, D["bxm"])
    return {"betas": _slopes(xs, ys) + (_plain(xs, ys),), "corr": _corr(ys, real)}


def constant_iv(level):
    return lambda i, S: level


def trailing_iv(mult=1.0, window=DAYS, floor=0.08):
    def rule(i, S):
        lo = max(1, i - window)
        lr = [log(S[j] / S[j - 1]) for j in range(lo, i + 1)]
        if len(lr) < 6:
            return 0.18 * mult
        m = sum(lr) / len(lr)
        return max(sqrt(sum((v - m) ** 2 for v in lr) / len(lr) * 252) * mult, floor)
    return rule


# ----------------------------------------------------------------------
# The index's own volatility
# ----------------------------------------------------------------------

def swings(D, start, end):
    """Monthly realized volatility from 21-day blocks: (median, sd of its log,
    month-to-month autocorrelation of its log, a month's return's correlation
    with its change in log)."""
    days = sorted(d for d in D["spx"] if start <= d <= end)
    lr = [log(D["spx"][b] / D["spx"][a]) for a, b in zip(days, days[1:])]
    vols, rets = [], []
    for j in range(len(lr) // DAYS):
        blk = lr[j * DAYS:(j + 1) * DAYS]
        m = sum(blk) / DAYS
        vols.append(sqrt(sum((v - m) ** 2 for v in blk) / DAYS * 252))
        rets.append(sum(blk))
    lv = [log(v) for v in vols]
    ml = sum(lv) / len(lv)
    srt = sorted(vols)
    return (srt[len(srt) // 2], sqrt(sum((v - ml) ** 2 for v in lv) / len(lv)),
            _corr(lv[:-1], lv[1:]), _corr(rets[1:], [b - a for a, b in zip(lv, lv[1:])]))


# ----------------------------------------------------------------------
# Getting the S&P 500 series
# ----------------------------------------------------------------------

def fetch_sp500tr(root="."):
    """From Yahoo's chart endpoint, prices.py's source, where it is reachable."""
    import prices
    payload = prices.fetch("^SP500TR", start=date(1988, 1, 1))
    _write_closes(root, [(r[0], r[1]) for r in payload["rows"]])


def from_yahoo_page(path, root="."):
    """From a history page saved whole (.mht) with the range set to Max."""
    import email
    import html
    import re
    msg = email.message_from_bytes(open(path, "rb").read())
    doc = max((p.get_payload(decode=True) or b"" for p in msg.walk()
               if p.get_content_type() == "text/html"), key=len).decode("utf-8", "replace")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, flags=re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        if len(cells) >= 6:
            try:
                rows.append((datetime.strptime(cells[0], "%b %d, %Y").date().isoformat(),
                             float(cells[4].replace(",", ""))))
            except ValueError:
                continue
    _write_closes(root, rows)


def _write_closes(root, rows):
    rows = sorted(set(rows))
    os.makedirs(os.path.join(root, DATA_DIR), exist_ok=True)
    with open(_path("spx", root), "w", newline="") as fh:
        fh.write("date,close\n")
        for d, c in rows:
            fh.write(f"{d},{c}\n")
    print(f"wrote {len(rows)} days, {rows[0][0]} to {rows[-1][0]}, to {_path('spx', root)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch-sp500tr", action="store_true")
    ap.add_argument("--from-yahoo-page", metavar="MHT")
    a = ap.parse_args()
    if a.fetch_sp500tr:
        return fetch_sp500tr()
    if a.from_yahoo_page:
        return from_yahoo_page(a.from_yahoo_page)
    if not available():
        missing = [FILES[k] for k in FILES if not os.path.exists(_path(k, "."))]
        print(f"missing in {DATA_DIR}/: {', '.join(missing)} -- see this script's docstring")
        return 2
    D = load()
    pu, pd, pp = PUBLISHED
    print("1. The real BXM, 21-day overlapping returns            up    down   plain")
    for start, end in WINDOWS:
        r = real_betas(D, start, end)
        print(f"   {start} to {end} ({r['windows']} windows)")
        for key in ("total", "excess"):
            u, d, p = r[key]
            print(f"     intercept, split at zero, {key:<7} returns        {u:.3f}  {d:.3f}  {p:.3f}")
        u, d = r["split at the mean"]
        print(f"     intercept, split at the mean                    {u:.3f}  {d:.3f}")
        u, d = r["through the origin"]
        print(f"     through the origin                              {u:.3f}  {d:.3f}")
    print(f"   published, 1996-2014                                 {pu:.2f}   {pd:.2f}    {pp:.2f}")
    print("\n2. A synthetic BXM on the real path                    up    down   plain   corr")
    for start, end in WINDOWS:
        print(f"   {start} to {end}")
        for label, rule in (("implied vol constant 18%", constant_iv(0.18)),
                            ("implied = trailing 21-day realized", trailing_iv()),
                            ("implied = 1.2x trailing realized", trailing_iv(1.2))):
            s = synthetic(D, start, end, rule)
            u, d, p = s["betas"]
            print(f"     {label:<44}  {u:.3f}  {d:.3f}  {p:.3f}  {s['corr']:.3f}")
    med, sd, ac, co = swings(D, *SWING_WINDOW)
    print(f"\n3. The S&P 500's volatility, {SWING_WINDOW[0]} to {SWING_WINDOW[1]}:")
    print(f"   monthly realized vol: median {med:.1%}; sd of its log {sd:.2f}; "
          f"month-to-month autocorrelation {ac:.2f};\n   a month's return against "
          f"its change in log vol {co:+.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
