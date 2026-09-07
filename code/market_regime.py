"""What the market did over each tranche, and what the account's own names did.

The out-of-sample pre-registration classifies every statement tranche into a
regime -- rally, flat, drawdown -- before anything else is read off the
refresh. Appendix B fixed the rule as *the traded universe's equal-weighted
return over the tranche, exposure-matched*, and said it would be "computed
mechanically as part of the refresh". Until this module there was no script:
the figure was reconstructed by hand each time, and the windows were typed in.

Two things are wrong with classifying by the universe alone, and both are the
reason this module exists rather than a preference about benchmarks.

  * **The universe is selected.** It is the names the operator judged
    wheel-grade -- a quality-dividend basket -- so its return over a window
    mixes what the world did with what the operator chose. Over the corpus to
    date the account's universe regresses on NOBL at beta 0.95, R^2 0.89,
    against 0.57 / 0.47 on SPY: it is a dividend-aristocrat basket to two
    decimal places, and a rotation into or out of that style reads on this
    rule as a market move.
  * **Exposure-matching puts the book inside its own classifier.** Weighting
    days by the wheel's inventory market value answers "what did these names
    do on the days we were long", which is the right question for attribution
    (see `live_ledger.universe_benchmark`) and the wrong one for a regime: the
    quantity meant to describe the world the book faced is then partly the
    book's own timing. Over the full corpus the same basket reads -1.61% total
    unmatched against +12.87%/yr exposure-matched.

So this module reports **both rules, side by side, and replaces neither**:

    market rule   the S&P 500's plain price return over the tranche's calendar
                  window. Exogenous to the operator entirely. This is the rule
                  for P8 ("the selection edge shrinks when dips stop
                  mean-reverting") and for the caveat section 15 owes the
                  reader, both of which are claims about the world.
    book rule     the pre-registered universe figure, unchanged. This is the
                  rule for P7's concavity, whose drivers -- the mark loss B and
                  the surrendered upside C -- are mechanically set by what the
                  *held names* did, not by what the index did.

**A tranche label is recorded and never scored.** Appendix B already scores the
predictions once, at freeze, against the accumulated record; the per-tranche
labels exist so the path is on the table. At three weeks a +/-8%/yr band is
about +/-0.5% of actual movement, and the classification is correspondingly
fragile -- which the diagnostic columns make visible rather than hide: over the
same tranche the three references disagree outright. The accumulated-window row
is the one that carries meaning.

    python code/market_regime.py
    python code/market_regime.py --matched   # add the exposure-matched index
"""

import argparse
import glob
import sys
from datetime import date

import prices
from analyze_statement import STATEMENTS_GLOB, build_lots, excluded_symbols, parse
from live_ledger import universe_benchmark, wheel_universe

# Appendix B's thresholds, in annualised simple return. Not a free parameter:
# changing one needs a dated amendment to the pre-registration.
RALLY, DRAWDOWN = 0.08, -0.08

# The classifier. The other references are printed beside it as diagnostics,
# because the label's sensitivity to this choice is itself a finding.
CLASSIFIER = "SPY"
DIAGNOSTICS = ("NOBL", "RSP")


def classify(annualised):
    if annualised > RALLY:
        return "rally"
    if annualised < DRAWDOWN:
        return "drawdown"
    return "flat"


def statement_windows(paths):
    """[(name, start, end)] -- one contiguous window per statement tranche.

    A tranche's window runs from the *previous* tranche's last statement date
    to its own, so the windows tile the corpus with no gaps and no overlaps and
    every day of market history is counted exactly once. The first tranche runs
    from the first statement date; files that overlap at the seam (USD/USD1)
    collapse into one window, which is what makes this the tranche list rather
    than the file list.

    Derived from the files rather than typed in: the windows in
    `drafts/tranche-record.md` were hand-entered, and a window that is retyped
    each refresh is a window that can drift.
    """
    import csv
    spans = []
    for path in sorted(paths):
        with open(path, newline="") as f:
            rows = [r for r in csv.reader(f)][1:]
        days = [r[0] for r in rows if len(r) > 4 and r[0][:2] == "20"]
        if days:
            spans.append((path, date.fromisoformat(min(days)),
                          date.fromisoformat(max(days))))
    windows, cursor = [], None
    for path, lo, hi in spans:
        name = path.replace("\\", "/").rsplit("/", 1)[-1]
        # A file adding no new dates is a seam re-export, not a tranche of its
        # own; fold its name onto the row already covering that range.
        if cursor is not None and hi <= cursor:
            windows[-1] = (windows[-1][0] + "+" + name,) + windows[-1][1:]
            continue
        windows.append((name, cursor if cursor is not None else lo, hi))
        cursor = hi
    return windows


def window_return(ser, a, b):
    """(total, annualised simple) price return of one series over [a, b].

    Split-adjusted, like every other ratio of two prices in this project --
    NOBL split 2:1 on 2026-05-28, inside the window.

    Plain buy-and-hold, deliberately: this is the *market*, not a position in
    it, so no exposure weighting is applied. Annualised the same way the
    tranche record annualises, simple rather than geometric, so the figures are
    comparable with the rows already on it.
    """
    pa, pb = ser.adj_on_or_before(a), ser.adj_on_or_before(b)
    if not (pa and pb):
        return None, None
    total = pb / pa - 1
    years = max((b - a).days, 1) / 365.25
    return total, total / years


def _ols(x, y):
    """(beta, R^2) of y on x, no intercept term needed at daily frequency."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / n
    vx = sum((a - mx) ** 2 for a in x) / n
    vy = sum((b - my) ** 2 for b in y) / n
    return cov / vx, (cov / (vx * vy) ** 0.5) ** 2


def _vol(rets):
    m = sum(rets) / len(rets)
    return (sum((r - m) ** 2 for r in rets) / len(rets) * 252) ** 0.5


def basket_report(px, idx, start, end):
    """What the traded universe is, measured against the public baskets.

    This is the evidence behind the pre-registration's Appendix C -- that the
    universe is a dividend-aristocrat basket rather than a market one -- and
    behind the two claims section 04 makes when it names the index: that the
    index's *yield* transfers to the single name the model describes, because a
    basket's yield is the weighted mean of its members', and that its
    *volatility* does not, because diversification cancels whatever the members
    do not share while the model's sigma stays a single lot's -- it is what
    carries one name away from one frozen strike, however many lots are held.
    """
    days = sorted({d for ser in px.values() for d in ser.days
                   if start <= d <= end})
    U, I = [], {s: [] for s in idx}
    for prev, day in zip(days, days[1:]):
        rs = []
        for ser in px.values():
            a, b = ser.adj_on_or_before(prev), ser.adj_on_or_before(day)
            if a and b:
                rs.append(b / a - 1)
        ir = {}
        for s, ser in idx.items():
            a, b = ser.adj_on_or_before(prev), ser.adj_on_or_before(day)
            ir[s] = (b / a - 1) if (a and b) else None
        if not rs or any(v is None for v in ir.values()):
            continue
        U.append(sum(rs) / len(rs))
        for s in idx:
            I[s].append(ir[s])

    print(f"\n=== what the traded universe is, {len(U)} sessions ===")
    print(f"{'basket':<10}{'beta':>8}{'R^2':>8}{'ann.vol':>10}{'yield':>9}")
    for s in (CLASSIFIER,) + DIAGNOSTICS:
        if s not in idx:
            continue
        beta, r2 = _ols(I[s], U)
        ser = idx[s]
        last = ser.adj_on_or_before(end)
        ttm = sum(a for d, a in ser.divs
                  if (end - d).days < 365 and d <= end)
        print(f"{s:<10}{beta:>8.3f}{r2:>8.3f}{_vol(I[s]):>10.1%}"
              f"{ttm / last:>9.2%}")
    print(f"{'universe':<10}{'':>8}{'':>8}{_vol(U):>10.1%}"
          f"{'--':>9}   equal weight, {len(px)} names")
    print("   beta and R^2 are the universe regressed on that basket. The "
          "universe is a\n   dividend-aristocrat basket, which is why the "
          "regime cannot be read off it.")
    print("   The volatility column is a BASKET volatility and is not the "
          "model's sigma, which\n   belongs to a single lot however many lots "
          "are held. The yield column is a\n   weighted mean and does "
          "transfer -- see section 04.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched", action="store_true",
                    help="also print the indices exposure-matched to the "
                         "book, which is an attribution figure and not a "
                         "regime one -- see the module docstring")
    args = ap.parse_args()

    paths = sorted(glob.glob(STATEMENTS_GLOB))
    if not paths:
        sys.exit(f"no statement files found at {STATEMENTS_GLOB}")
    positions, stock_tx, _divs, _live = parse(paths)
    excluded = excluded_symbols()
    universe = wheel_universe(positions, stock_tx, excluded)
    completed, open_lots = build_lots(stock_tx, excluded)
    px = prices.load_all(universe)
    idx = prices.load_indices()

    windows = statement_windows(paths)
    corpus = (windows[0][1], windows[-1][2])
    rows = windows + [("ALL to date", corpus[0], corpus[1])]

    refs = (CLASSIFIER,) + DIAGNOSTICS
    print(f"\nwindows derived from {len(paths)} statement files; "
          f"corpus {corpus[0]} .. {corpus[1]}")
    print(f"thresholds: rally > {RALLY:+.0%}/yr, drawdown < {DRAWDOWN:+.0%}/yr, "
          f"annualised simple\n")

    print("=== the market rule: plain index return over the tranche "
          "(the classifier is " + CLASSIFIER + ") ===")
    head = f"{'tranche':<22}{'window':<26}{'days':>5}"
    for s in refs:
        head += f"{s:>10}{'/yr':>9}{'':>3}"
    print(head)
    for name, a, b in rows:
        line = f"{name:<22}{str(a) + ' .. ' + str(b):<26}{(b - a).days:>5}"
        for s in refs:
            tot, ann = window_return(idx[s], a, b) if s in idx else (None, None)
            if tot is None:
                line += f"{'--':>10}{'--':>9}{'':>3}"
            else:
                line += f"{tot:>+10.2%}{ann:>+9.1%}{classify(ann)[0]:>3}"
        print(line)
    print("   r = rally, f = flat, d = drawdown.  The classifier is the first "
          "column;\n   the others are diagnostics, and where they disagree the "
          "label is noise, not signal.")

    print("\n=== the book rule: traded universe, equal weight, "
          "exposure-matched (pre-registered) ===")
    print(f"{'tranche':<22}{'window':<26}{'days':>5}"
          f"{'universe':>12}{'/yr':>9}{'':>3}{'exposure':>12}")
    for name, a, b in rows:
        bench, wheel_eq, avg_exp, _, _, _ = universe_benchmark(
            px, universe, completed, open_lots, a, b)
        years = max((b - a).days, 1) / 365.25
        if avg_exp <= 0:
            print(f"{name:<22}{str(a) + ' .. ' + str(b):<26}"
                  f"{(b - a).days:>5}{'no exposure':>12}")
            continue
        ann = bench / avg_exp / years
        print(f"{name:<22}{str(a) + ' .. ' + str(b):<26}{(b - a).days:>5}"
              f"{bench / avg_exp:>+12.2%}{ann:>+9.1%}{classify(ann)[0]:>3}"
              f"{avg_exp:>12,.0f}")
    print("   Unchanged from Appendix B and still the rule for P7, whose "
          "drivers are\n   what the HELD names did. It is not a market "
          "measurement and is not read as one.")
    print("   These do NOT reproduce the hand-computed figures on the tranche "
          "record's rows:\n   each of those was computed on the corpus "
          "available that month, over a window\n   typed in by hand, and the "
          "first is a whole-window figure where the rest are\n   tranche-only. "
          "This is one rule applied to every window on today's corpus.")

    if args.matched:
        print("\n=== diagnostic: the indices exposure-matched to the book ===")
        print(f"{'tranche':<22}" + "".join(f"{s:>12}" for s in refs))
        for name, a, b in rows:
            _, _, avg_exp, _, idx_pnl, _ = universe_benchmark(
                px, universe, completed, open_lots, a, b, indices=idx)
            years = max((b - a).days, 1) / 365.25
            if avg_exp <= 0:
                print(f"{name:<22}{'no exposure':>12}")
                continue
            print(f"{name:<22}" + "".join(
                f"{idx_pnl[s] / avg_exp / years:>+12.2%}" for s in refs))
        print("   These are the ladder's rungs (`live_ledger.py`), NOT regime "
              "figures: weighting\n   days by the book's own inventory answers "
              "a question about the book, not the market.")

    basket_report(px, idx, corpus[0], corpus[1])

    print("\nA tranche label is recorded, never scored. Scoring happens once, "
          "at freeze,\nagainst the accumulated record -- the ALL row above. At "
          "three weeks a +/-8%/yr\nband is about +/-0.5% of actual movement.")


if __name__ == "__main__":
    main()
