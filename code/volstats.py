"""Volatility and jump statistics of daily returns, for the data and the simulation alike.

Decision 8 of `drafts/2026-11-21-moving-volatility-plan.md` fits the volatility state and
the jumps together: the model is simulated, and its parameters are those whose simulated
paths reproduce the statistics measured on the data. That works only if each statistic is
computed the same way on both, so each is defined once, here, on one input: R, a 2-D array
of daily log returns, one series per row, NaN wherever a return is not clean (outside the
sample, in an earnings window, or past the end of a shorter series). `jumps.py` reports
them on the data; `volfit.py` fits them.

Every statistic is in units a series' own volatility level cancels from, so a model
simulated at any level answers for a name at any other:

- **tails**: returns beyond c local sd, per name-year, each side. The local sd -- the
  yardstick -- is bipower variation over the BV_WINDOW sessions before the return.
- **sizes**: beyond JUMP_C, the mean excess in local sd, by tercile of the volatility
  state h = ln(yardstick / the series' median yardstick), each side, and the
  median-to-mean ratio of the excess (0.69 for an exponential).
- **kicks**: ln(sd of the KICK_WINDOW returns after / those before), averaged over the
  returns in each band of the standardized move, each side.
- **monthly**: II-38's three -- the sd of log monthly volatility about the series' mean,
  its autocorrelation at 1, 3 and 6 months (the half-life), and the correlation of a
  month's return with the change in its log volatility. A month is MONTH consecutive
  sessions, so the data and a simulation cut it identically.
- **acf**: the autocorrelation of |r| at ACF_LAGS sessions, about each series' mean.
"""

from math import inf, log, pi

import numpy as np

BV_WINDOW = 60
MIN_PAIRS = 40
KICK_WINDOW = 20
MIN_KICK_PAIRS = 12
TAIL_C = (3.0, 3.5, 4.0, 4.5, 5.0, 6.0)
JUMP_C = 4.0
KICK_BANDS = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, inf))
MONTH = 21
MIN_MONTH = 17          # clean returns a month must hold
MONTH_LAGS = (1, 3, 6)
ACF_LAGS = (1, 5, 20, 60, 120, 250)
MU1_SQ = 2 / pi         # E|z|² for a standard normal z
SESSIONS = 252
SIDES = (("up", 1), ("down", -1))


def _pairs(R):
    """Running sums of |r_j|·|r_j+1| over clean adjacent pairs, and of their count."""
    n = R.shape[0]
    A = np.abs(R)
    P = A[:, :-1] * A[:, 1:]
    ok = ~np.isnan(P)
    zero = np.zeros((n, 1))
    return (np.concatenate([zero, np.cumsum(np.where(ok, P, 0.0), axis=1)], axis=1),
            np.concatenate([zero, np.cumsum(ok, axis=1)], axis=1))


def _window_bv(R, lo_off, hi_off, need, pairs=None):
    """Bipower sd for each return t from the adjacent pairs (j, j+1), j in
    [t + lo_off, t + hi_off]; NaN where fewer than `need` pairs are clean."""
    T = R.shape[1]
    cs, cc = pairs if pairs is not None else _pairs(R)
    t = np.arange(T)
    lo = np.clip(t + lo_off, 0, T - 1)
    hi = np.clip(t + hi_off, -1, T - 2)
    S = cs[:, hi + 1] - cs[:, lo]
    C = cc[:, hi + 1] - cc[:, lo]
    good = (hi >= lo)[None, :] & (C >= need)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(good, np.sqrt(S / C / MU1_SQ), np.nan)


def yardstick(R, pairs=None):
    """The local sd behind each return: returns t-BV_WINDOW .. t-1."""
    return _window_bv(R, -BV_WINDOW, -2, MIN_PAIRS, pairs)


def kicks(R, pairs=None):
    """ln(sd of returns t+1 .. t+KICK_WINDOW / sd of returns t-KICK_WINDOW .. t-1)."""
    pairs = pairs if pairs is not None else _pairs(R)
    before = _window_bv(R, -KICK_WINDOW, -2, MIN_KICK_PAIRS, pairs)
    after = _window_bv(R, 1, KICK_WINDOW - 1, MIN_KICK_PAIRS, pairs)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.log(after / before)


def standardize(R, pairs=None):
    """(s, sd, h): each return over its yardstick, the yardstick, and the state
    h = ln(yardstick / the series' median yardstick); NaN where undefined."""
    sd = yardstick(R, pairs)
    with np.errstate(invalid="ignore"):
        s = R / sd
    sd = np.where(np.isnan(s), np.nan, sd)
    with np.errstate(invalid="ignore", divide="ignore"):
        h = np.log(sd / np.nanmedian(sd, axis=1, keepdims=True))
    return s, sd, h


def _pooled_corr(x, y):
    """Correlation over the pairs where both are defined, x and y already centred."""
    xy = x * y
    ok = ~np.isnan(xy)
    d = np.sqrt(np.where(ok, x * x, 0.0).sum() * np.where(ok, y * y, 0.0).sum())
    return float(np.where(ok, xy, 0.0).sum() / d) if d > 0 else np.nan


def _centred(X):
    """Each row less its own mean, NaN kept."""
    return X - np.nanmean(X, axis=1, keepdims=True)


def _lagged_corr(X, lag):
    """Pooled within-series autocorrelation of an already centred X at `lag`."""
    return _pooled_corr(X[:, :-lag], X[:, lag:])


def months(R):
    """(log monthly volatility, monthly return) per MONTH-session block, NaN for a
    block with fewer than MIN_MONTH clean returns."""
    n, T = R.shape
    B = R[:, : T // MONTH * MONTH].reshape(n, T // MONTH, MONTH)
    k = (~np.isnan(B)).sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        lv = 0.5 * np.log(np.nansum(B * B, axis=2) * MONTH / k)
        ret = np.nansum(B, axis=2) * MONTH / k
    bad = k < MIN_MONTH
    return np.where(bad, np.nan, lv), np.where(bad, np.nan, ret)


def stats(R):
    """Every statistic, as an ordered {name: value}."""
    pairs = _pairs(R)
    s, sd, h = standardize(R, pairs)
    kk = kicks(R, pairs)
    ok = ~np.isnan(s)
    s1, h1, k1 = s[ok], h[ok], kk[ok]       # the defined returns, flattened once
    years = s1.size / SESSIONS
    out = {}
    for name, sign in SIDES:
        x = s1 * sign
        for c in TAIL_C:
            out[f"tail {name} {c:g}"] = np.count_nonzero(x > c) / years
    for name, sign in SIDES:
        m = s1 * sign > JUMP_C
        ex, hh = np.abs(s1[m]) - JUMP_C, h1[m]
        ex = ex[np.argsort(hh, kind="stable")]
        cut = (0, ex.size // 3, 2 * ex.size // 3, ex.size)
        for k in range(3):
            part = ex[cut[k]:cut[k + 1]]
            out[f"size {name} h{k + 1}"] = float(part.mean()) if part.size else np.nan
        out[f"size {name} median/mean"] = (float(np.median(ex) / ex.mean())
                                          if ex.size else np.nan)
    has_kick = ~np.isnan(k1)
    sk, kd = s1[has_kick], k1[has_kick]
    for name, sign in SIDES:
        x = sk * sign
        for a, b in KICK_BANDS:
            m = (x >= a) & (x < b)
            label = f"{a:g}-{b:g}" if b < inf else f">{a:g}"
            out[f"kick {name} {label}"] = float(kd[m].mean()) if m.any() else np.nan
    lv, ret = months(R)
    c = _centred(lv)
    out["month sd log vol"] = float(np.sqrt(np.nanmean(c * c)))
    for lag in MONTH_LAGS:
        out[f"month acf {lag}"] = _lagged_corr(c, lag)
    dlv = lv[:, 1:] - lv[:, :-1]
    rs = _centred(ret[:, 1:])
    rs = rs / np.sqrt(np.nanmean(rs * rs, axis=1, keepdims=True))
    out["month corr(return, dlogvol)"] = _pooled_corr(rs, _centred(dlv))
    a = _centred(np.abs(R))
    for lag in ACF_LAGS:
        out[f"acf |r| {lag}"] = _lagged_corr(a, lag)
    return out


def pad(rows):
    """Stack 1-D arrays of unequal length into a 2-D array, NaN past each end."""
    T = max(len(r) for r in rows)
    out = np.full((len(rows), T), np.nan)
    for i, r in enumerate(rows):
        out[i, : len(r)] = r
    return out


def half_life(rho):
    """Periods for a first-order autocorrelation rho to halve."""
    return log(0.5) / log(rho) if 0 < rho < 1 else np.nan
