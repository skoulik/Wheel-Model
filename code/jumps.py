"""Unscheduled jumps on the calibration universe, step 3 of the moving-volatility plan.

`drafts/2026-11-21-moving-volatility-plan.md` takes earnings days out first, then fits the
volatility state and the jumps together, by simulation (decision 8). This is the
measurement: on the days `earnings.py` puts in the sample, with the two sessions from each
earnings date taken out, how the daily moves too large for a normal diffusion behave on
each side. The statistics themselves are defined once, in `volstats.py`, which the fit
(`volfit.py`) computes on its simulated paths the same way; this script reports them on
the data with what only the data has -- dates, names, the market on the day.

**The returns** are daily log returns of the split-adjusted close with the dividend added
back on its ex-date (Yahoo states both on the same split basis): an ex-dividend drop is a
known payment, not a jump. A return counts when both its sessions are in the sample and
neither is in an earnings window.

**The test** is Lee and Mykland's (2008) at daily frequency: each return over a yardstick
from the sessions before it, estimated by bipower variation -- the mean of |r_j|·|r_j+1|
over adjacent pairs, divided by E|z|² = 2/π -- which a single large move barely moves,
since it enters only multiplied by its ordinary neighbours. The day itself is never in its
own yardstick. With intraday data the same estimator would split a day's variance into its
diffusive and jump parts; with daily closes it can only supply the yardstick. No
threshold separates the two (the tail table shows why), so a threshold here is only the
place a statistic is read.

Beyond the shared statistics this reports, at the threshold c: the size beyond c in log
return as well as in local sd, by the volatility state and by the name's own level --
which of the two is flat says whether jump sizes scale with volatility; the same by the
two size groups; how many jumps fall on days the S&P also moved beyond MARKET_C, or
COJUMP names jumped together; the largest jumps; and up jumps after which volatility
collapsed, the mark of a price pinned by a takeover bid.

    python code/jumps.py            # at volstats.JUMP_C
    python code/jumps.py --c 5      # the jump diagnostics at another threshold
"""

import csv
import os
import sys
from bisect import bisect_left
from collections import Counter
from datetime import date
from math import erfc, log, sqrt

import numpy as np

import earnings
import volstats as V

MARKET_FILE = os.path.join("data", "market", "SP500TR.csv")
MARKET_C = 3.0
COJUMP = 5
TOP = 10


def name_returns(n):
    """(days, r) for an `earnings.Name`: clean log returns, NaN elsewhere."""
    days = n.series.days
    px = np.array([n.series.adj_close(d) for d in days], dtype=float)
    div = dict(n.series.divs)
    add = np.array([div.get(d, 0.0) for d in days])
    r = np.full(len(days), np.nan)
    r[1:] = np.log((px[1:] + add[1:]) / px[:-1])
    window = set()
    for d in n.dates:
        i = bisect_left(days, d)
        window.update((i, i + 1))
    ok = np.array([n.in_sample(d) for d in days])
    clean = np.zeros(len(days), dtype=bool)
    clean[1:] = ok[1:] & ok[:-1]
    clean[[i for i in window if i < len(days)]] = False
    return days, np.where(clean, r, np.nan)


def market_returns():
    """(days, r) for the S&P 500 total-return index, every return clean."""
    with open(MARKET_FILE, newline="") as f:
        rows = [(date.fromisoformat(row["date"]), float(row["close"]))
                for row in csv.DictReader(f)]
    px = np.array([c for _, c in rows])
    r = np.full(len(rows), np.nan)
    r[1:] = np.log(px[1:] / px[:-1])
    return [d for d, _ in rows], r


def universe_returns():
    """(syms, days per row, R) over the whole universe."""
    names = earnings.load_universe()
    syms, days, rows = [], [], []
    for sym, n in names.items():
        d, r = name_returns(n)
        syms.append(sym)
        days.append(d)
        rows.append(r)
    return names, syms, days, V.pad(rows)


def _terciles(values, key):
    order = np.argsort(key, kind="stable")
    v, k = values[order], values.size
    return [v[a:b] for a, b in ((0, k // 3), (k // 3, 2 * k // 3), (2 * k // 3, k))]


def main():
    args = sys.argv[1:]
    c = float(args[args.index("--c") + 1]) if "--c" in args else V.JUMP_C
    names, syms, days, R = universe_returns()
    s, sd, h = V.standardize(R)
    st = V.stats(R)
    valid = ~np.isnan(s)
    years = np.count_nonzero(valid) / V.SESSIONS
    row_years = np.count_nonzero(valid, axis=1) / V.SESSIONS
    big = np.array([names[x].cap(names[x].series.days[-1]) >= 20e9 for x in syms])

    print(f"{len(syms)} names, {years:.0f} name-years of clean returns "
          f"({np.count_nonzero(valid)}), yardstick {V.BV_WINDOW} sessions of bipower "
          f"variation\n")
    print("the tail: returns beyond c local sd, against a normal tail")
    print(f"  {'c':>4} {'up':>6} {'down':>6} {'normal':>9} {'ratio':>7}")
    for x in V.TAIL_C:
        up = round(st[f"tail up {x:g}"] * years)
        dn = round(st[f"tail down {x:g}"] * years)
        g = erfc(x / sqrt(2)) * np.count_nonzero(valid)
        print(f"  {x:4.1f} {up:6} {dn:6} {g:9.1f} {(up + dn) / g:7.1f}")

    sbar = np.nanmedian(sd, axis=1, keepdims=True) * np.ones_like(sd)
    print(f"\njumps at c = {c:g}")
    for side, sign in V.SIDES:
        m = s * sign > c
        ex_s = np.abs(s[m]) - c
        ex_r = np.abs(R[m]) - c * sd[m]
        print(f"  {side:4}: {m.sum():5} jumps, {m.sum() / years:.3f} a name-year; "
              f"beyond c: {ex_s.mean():.2f} sd (median/mean "
              f"{np.median(ex_s) / ex_s.mean():.2f}, exponential 0.69), "
              f"{ex_r.mean():.2%} in log return")
        for label, key in (("state h", h[m]), ("name's level", sbar[m])):
            cells = [f"{a.mean():4.2f} sd / {b.mean():6.2%}" for a, b in
                     zip(_terciles(ex_s, key), _terciles(ex_r, key))]
            print(f"        by {label} tercile, low to high: " + "   ".join(cells))
        for grp, flag in (("over $20B today", True), ("$10-20B today", False)):
            g = m & big[:, None] if flag else m & ~big[:, None]
            print(f"        {grp}: {g.sum() / row_years[big == flag].sum():.3f} a name-year, "
                  f"beyond c {(np.abs(s[g]) - c).mean():.2f} sd")

    print(f"\nthe kick: ln(sd after / sd before), {V.KICK_WINDOW} sessions each side, "
          f"by the day's move in local sd")
    labels = [f"{a:g}-{b:g}" if b < float("inf") else f">{a:g}" for a, b in V.KICK_BANDS]
    print("      " + "".join(f"{x:>9}" for x in labels))
    for side, _ in V.SIDES:
        print(f"  {side:4}" + "".join(f"{st[f'kick {side} {x}']:+9.3f}" for x in labels))

    print("\nII-38's monthly statistics, and the persistence of |r|")
    print(f"  sd of log monthly volatility {st['month sd log vol']:.3f}; autocorrelation "
          + ", ".join(f"{st[f'month acf {k}']:.3f} at {k}" for k in V.MONTH_LAGS)
          + f" months (half-life {V.half_life(st['month acf 1']):.1f} months); "
          f"corr(month's return, change in log vol) {st['month corr(return, dlogvol)']:+.3f}")
    print("  acf |r|: " + ", ".join(f"{st[f'acf |r| {k}']:.3f} at {k}" for k in V.ACF_LAGS))
    print("  leverage, corr(r, mean |r| ahead): " + ", ".join(
        f"{st[k]:+.3f} over {k.split()[1]}" for k in st if k.startswith("leverage")))

    md, mr = market_returns()
    ms = V.standardize(mr[None, :])[0][0]
    mkt_s = {d: x for d, x in zip(md, ms) if not np.isnan(x)}
    kk = V.kicks(R)
    jumps = [(i, t) for i, t in zip(*np.nonzero(np.abs(s) > c))]
    together = Counter((days[i][t], s[i, t] > 0) for i, t in jumps)
    print("\nshared jump days")
    for side, sign in V.SIDES:
        js = [(i, t) for i, t in jumps if s[i, t] * sign > 0]
        m = sum(1 for i, t in js if abs(mkt_s.get(days[i][t], 0)) > MARKET_C)
        k = sum(1 for i, t in js if together[days[i][t], sign > 0] >= COJUMP)
        print(f"  {side:4}: {m / len(js):.0%} on a day the S&P moved beyond {MARKET_C:g} sd; "
              f"{k / len(js):.0%} on a day {COJUMP} or more names jumped {side}")

    def line(i, t):
        k = f"{kk[i, t]:+.2f}" if not np.isnan(kk[i, t]) else "  - "
        return (f"{syms[i]:5} {days[i][t]} {R[i, t]:+7.1%} {s[i, t]:+6.1f} sd, kick {k}, "
                f"S&P {mkt_s.get(days[i][t], float('nan')):+5.1f} sd, "
                f"{together[days[i][t], s[i, t] > 0]} names")

    print("\nlargest jumps")
    for side, sign in V.SIDES:
        js = sorted((p for p in jumps if s[p] * sign > 0), key=lambda p: -abs(s[p]))
        for p in js[:TOP]:
            print(f"  {side:4} " + line(*p))
    print("\nup jumps after which volatility collapsed (kick < -1): bid candidates")
    for p in sorted((p for p in jumps if s[p] > 0 and kk[p] < -1), key=lambda p: kk[p]):
        print("  " + line(*p))


if __name__ == "__main__":
    main()
