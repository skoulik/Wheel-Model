"""Does the operator's stated entry rule show up in the trades?

The pre-registration is `drafts/2026-07-27-selection-rule-preregistration.md`,
written before any price data was fetched. It fixes the features, the
statistical form, and what counts as confirmation, so this module is a test of
a stated hypothesis rather than a search. Read it first; nothing here may
quietly redefine anything there.

**What is being tested.** Rules 1-3 (aristocrats, market cap, weekly expiries)
define the universe, and the choice set is reconstructed *from* names the
operator traded, so those rules cannot be tested against this data -- the
pre-registration says so in advance. What remains are the timing rules:

    rule 4  fallen angel     pct5y   price within its trailing 5-year range
    rule 5  not a knife      slope   OLS slope of log price over 250 days,
                                     and slope_r2, how linear that fall is
    rule 6  oversold         pctB    (S - MA30) / (2 * sigma30)

Confirmation, as pre-registered, is negative coefficients on `pct5y` and `pctB`
(a low price level and an oversold condition both make a sale more likely).

**The statistical form, and why it is not a logistic regression.** Rule 7 sells
in order of preference until margin runs out, so each week is a *ranked choice
under a budget*: the operator scores an eligible set and takes the top few.
Fitting independent per-name logistic regressions would attribute the weekly
budget -- how many were sold at all that week -- to the features. The
pre-registration rejects that in advance. What is fitted instead is a
conditional (multinomial) logit over the weekly choice set, with the number
chosen taken as given, so every parameter is identified purely by *which* names
were picked from that week's menu and never by *how many*.

**What this can and cannot establish.** It can say whether entries are timed to
drawdowns. It cannot say the timing earned anything: under GBM entry timing
cannot generate return by construction, so a return claim would be a claim of
mean reversion, and 29 lots in one bull market cannot carry it.

Stdlib only. Run:  python code/selection_fit.py
"""

import glob
import random
import sys
from collections import defaultdict
from datetime import timedelta
from math import exp, isfinite, log, sqrt

import prices
from analyze_statement import STATEMENTS_GLOB, junk_symbols, parse
from live_ledger import wheel_universe

LOOKBACK_5Y = 1250        # trading days
LOOKBACK_TREND = 250
LOOKBACK_BOLL = 30
PRIMARY = ["pct5y", "pctB", "slope", "slope_r2"]
SECONDARY = ["ret1m", "ret3m", "ret12m", "rvol", "off52w"]


# ----------------------------------------------------------------------
# Features, all computed from closes strictly BEFORE the week being scored
# ----------------------------------------------------------------------
def features(ser, day):
    """The pre-registered features for one name, as known on `day`."""
    # Adjusted throughout: every feature here is a ratio of prices.
    hist = [c for d, c in ser.window_adj(day - timedelta(days=2600), day)]
    if len(hist) < LOOKBACK_TREND + 10:
        return None
    s = hist[-1]
    win5 = hist[-LOOKBACK_5Y:]
    lo, hi = min(win5), max(win5)
    if hi <= lo or s <= 0:
        return None
    boll = hist[-LOOKBACK_BOLL:]
    mb = sum(boll) / len(boll)
    vb = sum((c - mb) ** 2 for c in boll) / (len(boll) - 1)
    sb = sqrt(vb)

    trend = hist[-LOOKBACK_TREND:]
    n = len(trend)
    xs = list(range(n))
    ys = [log(c) for c in trend]
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    slope = sxy / sxx if sxx else 0.0
    yhat = [my + slope * (a - mx) for a in xs]
    ssr = sum((b - h) ** 2 for b, h in zip(ys, yhat))
    sst = sum((b - my) ** 2 for b in ys)
    r2 = 1 - ssr / sst if sst > 0 else 0.0

    rets = [(y / x) - 1 for x, y in zip(hist[-61:], hist[-60:]) if x]
    m = sum(rets) / len(rets) if rets else 0.0
    rvol = sqrt(sum((z - m) ** 2 for z in rets) / max(len(rets) - 1, 1) * 252) \
        if len(rets) > 5 else 0.0

    def back(k):
        return hist[-k] if len(hist) >= k else hist[0]

    return {
        "pct5y": (s - lo) / (hi - lo),
        "pctB": (s - mb) / (2 * sb) if sb > 0 else 0.0,
        "slope": slope * 250,                     # per year, in logs
        "slope_r2": r2,
        "ret1m": log(s / back(21)),
        "ret3m": log(s / back(63)),
        "ret12m": log(s / back(252)),
        "rvol": rvol,
        "off52w": log(s / max(hist[-252:])),
    }


def build_choice_sets(positions, px, universe):
    """Per week: the menu of names, and which of them a put was sold on."""
    sold = defaultdict(set)
    for p in positions:
        if p["right"] == "P" and p["sym"] in universe:
            iso = p["open"].isocalendar()
            sold[(iso[0], iso[1])].add(p["sym"])
    weeks = sorted(sold)
    sets = []
    for wk in weeks:
        monday = _monday(wk)
        menu = []
        for sym in sorted(universe):
            ser = px.get(sym)
            if ser is None:
                continue
            f = features(ser, monday - timedelta(days=1))
            if f is None:
                continue
            menu.append((sym, f))
        chosen = [i for i, (s, _) in enumerate(menu) if s in sold[wk]]
        if chosen and len(menu) - len(chosen) >= 5:
            sets.append((wk, menu, chosen))
    return sets


def _monday(iso_week):
    from datetime import date
    return date.fromisocalendar(iso_week[0], iso_week[1], 1)


# ----------------------------------------------------------------------
# Conditional logit, fitted by Newton-Raphson
# ----------------------------------------------------------------------
def standardize(sets, names):
    vals = defaultdict(list)
    for _, menu, _ in sets:
        for _, f in menu:
            for k in names:
                vals[k].append(f[k])
    stats = {}
    for k in names:
        v = vals[k]
        m = sum(v) / len(v)
        sd = sqrt(sum((z - m) ** 2 for z in v) / max(len(v) - 1, 1)) or 1.0
        stats[k] = (m, sd)
    return stats


def _design(sets, names, stats):
    out = []
    for wk, menu, chosen in sets:
        X = [[(f[k] - stats[k][0]) / stats[k][1] for k in names]
             for _, f in menu]
        out.append((X, chosen))
    return out


def fit_conditional_logit(data, p, iters=60, tol=1e-9):
    """Maximise sum_t sum_{i chosen} [eta_i - logsumexp_j eta_j]."""
    beta = [0.0] * p
    for _ in range(iters):
        grad = [0.0] * p
        hess = [[0.0] * p for _ in range(p)]
        ll = 0.0
        for X, chosen in data:
            eta = [sum(b * x for b, x in zip(beta, row)) for row in X]
            mx = max(eta)
            w = [exp(e - mx) for e in eta]
            Z = sum(w)
            pr = [x / Z for x in w]
            mean = [sum(pr[j] * X[j][a] for j in range(len(X)))
                    for a in range(p)]
            for i in chosen:
                ll += eta[i] - (mx + log(Z))
                for a in range(p):
                    grad[a] += X[i][a] - mean[a]
            k = len(chosen)
            for a in range(p):
                for b in range(a, p):
                    cov = sum(pr[j] * X[j][a] * X[j][b]
                              for j in range(len(X))) - mean[a] * mean[b]
                    hess[a][b] -= k * cov
                    if b != a:
                        hess[b][a] = hess[a][b]
        step = _solve(hess, [-g for g in grad])
        if step is None:
            break
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < tol:
            break
    se = _stderr(hess)
    return beta, se, ll


def _solve(A, b):
    """Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-12:
            return None
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r == c:
                continue
            fct = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= fct * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def _stderr(hess):
    n = len(hess)
    inv = []
    for i in range(n):
        e = [1.0 if j == i else 0.0 for j in range(n)]
        col = _solve([row[:] for row in hess], e)
        if col is None:
            return [float("nan")] * n
        inv.append(col[i])
    return [sqrt(-v) if v < 0 and isfinite(v) else float("nan") for v in inv]


# ----------------------------------------------------------------------
# Nonparametric check: where do the chosen names rank that week?
# ----------------------------------------------------------------------
def rank_test(sets, names, trials=2000, seed=11):
    rng = random.Random(seed)
    print(f"  {'feature':>10s} {'mean pct rank of chosen':>25s} {'p (permutation)':>17s}")
    for k in names:
        obs, per_week = [], []
        for _, menu, chosen in sets:
            vals = [f[k] for _, f in menu]
            order = sorted(range(len(vals)), key=lambda i: vals[i])
            rank = [0.0] * len(vals)
            for pos, i in enumerate(order):
                rank[i] = pos / max(len(vals) - 1, 1)
            obs += [rank[i] for i in chosen]
            per_week.append((rank, len(chosen)))
        mean_obs = sum(obs) / len(obs)
        hits = 0
        for _ in range(trials):
            tot = cnt = 0.0
            for rank, k_ch in per_week:
                for i in rng.sample(range(len(rank)), k_ch):
                    tot += rank[i]
                    cnt += 1
            if (tot / cnt) <= mean_obs:
                hits += 1
        p = min(hits, trials - hits) * 2 / trials
        print(f"  {k:>10s} {mean_obs:25.3f} {p:17.3f}")


def main():
    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB}")
    positions, stock_tx, divs, live = parse(paths)
    junk = junk_symbols(positions, stock_tx)
    universe = wheel_universe(positions, stock_tx, junk)
    px = prices.load_all(universe)

    sets = build_choice_sets(list(positions) + list(live), px, universe)
    n_obs = sum(len(m) for _, m, _ in sets)
    n_ch = sum(len(c) for _, _, c in sets)
    print(f"\nchoice sets: {len(sets)} weeks, {n_obs:,} name-weeks, "
          f"{n_ch} sales ({n_ch/len(sets):.1f} per week, "
          f"menu {n_obs/len(sets):.0f} names)")

    for label, names in (("PRIMARY (the stated rule)", PRIMARY),
                         ("SECONDARY (pre-committed generic set)", SECONDARY)):
        print(f"\n=== {label} ===")
        stats = standardize(sets, names)
        data = _design(sets, names, stats)
        beta, se, ll = fit_conditional_logit(data, len(names))
        null = sum(len(c) * -log(len(X)) for X, c in data)
        print(f"  conditional logit, coefficients per standard deviation")
        print(f"  {'feature':>10s} {'beta':>9s} {'se':>8s} {'z':>7s} "
              f"{'odds/sd':>9s}")
        for k, b, s in zip(names, beta, se):
            z = b / s if s and isfinite(s) else float("nan")
            print(f"  {k:>10s} {b:+9.3f} {s:8.3f} {z:+7.2f} {exp(b):9.2f}")
        print(f"  log-likelihood {ll:,.1f} vs null {null:,.1f}  "
              f"(pseudo-R2 {1 - ll/null:.3f})")
        print("  nonparametric check, same weeks:")
        rank_test(sets, names)


if __name__ == "__main__":
    main()
