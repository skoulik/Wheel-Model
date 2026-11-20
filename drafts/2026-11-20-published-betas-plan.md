# §09's betas against the published ones — plan

**Status: DRAFT, 2026-11-20** — written in conversation; the direction is agreed (Sergei:
quantify this book's beta under changing volatility, and explain the sources of the mismatch to
the reader in detail), the open questions at the end are not. Opens TODO II-37; closes II-36.

## What was found

Reviewing §09's caution about comparing its split betas with published ones, the comparison
the box made could not be reproduced, and the published up-beta could not be explained.
Everything below is from scratch scripts run on cloud on 2026-11-20; none of it is in the
repository yet, and it is all to be recomputed by committed code before any of it is quoted.

**The published figures.** Israelov and Nielsen (2015, Table 6): the Cboe S&P 500 BuyWrite
Index over 1996-03-25 to 2014-12-31 has a plain beta of 0.62, an up-beta of 0.46 and a
down-beta of 0.85, "computed using 21-day overlapping returns", excess of 3-month LIBOR. No
paper states how the up/down split is fitted. The same authors (2014, Table 1) give 0.67 /
0.63 / 0.78 over 1986–2013; Israelov, Klein and Tummala (2018) give up-betas of 0.35–0.60 and
down-betas of 0.81–0.96 across eleven indexes. The published up-beta moves with the sample.

**The real index reproduces them with the article's estimator** (least squares with an
intercept, split at a zero stock return), on Cboe's BXM history, Yahoo's S&P 500 total-return
index and FRED's 3-month T-bill (DTB3):

| BXM, 21-day overlapping | plain | up | down |
|---|---|---|---|
| 2002-03-22 to 2014-12-31 | 0.65 | 0.54 | 0.82 |
| 2002-03-22 to 2026-11-19 | 0.63 | 0.45 | 0.87 |
| the same, through the origin | | 0.53–0.58 | 0.71–0.74 |

So the published figure is a real property of the index, and not an estimator difference: the
through-origin fit misses the down-beta. (Cboe's file starts in 2002.)

**The model's buy-write does not**, with constant volatility: 0.47 / 0.17 / 0.83 on BXM's
construction. Ruled out as the cause, each tried in the model: every intercept-bearing variant
of the fit (0.16–0.18); implied vol falling as the index rises (0.18); a volatility risk
premium, realized 12% against implied 20% (0.20); a strike ½–2% above spot (0.20–0.30); and
Broadie, Chernov and Johannes's estimated S&P dynamics, stochastic volatility with jumps (0.18).

**A synthetic BXM on the real S&P path**, priced by Black–Scholes, rolled on third Fridays,
21-day returns correlating 0.95 with the real index's:

| implied vol of the written call | plain | up | down |
|---|---|---|---|
| constant 18% | 0.61 | 0.24 | 0.96 |
| the market's trailing 21-day realized vol | 0.63 | 0.47 | 0.85 |
| real BXM, same window (2002–2026) | 0.63 | 0.45 | 0.87 |

Nothing beyond Black–Scholes is needed — provided each month's option is priced at that
month's volatility.

**The S&P's own volatility**, measured from the same series (1988–2026): monthly realized vol
median 12.6%, mean 14.9%; standard deviation of its log 0.48–0.51; half-life 1.6–2.2 months;
a month's return correlates −0.35 to −0.43 with that month's change in log vol. Broadie et
al.'s diffusive part swings about a quarter as much; their jumps carry the crashes instead.

**The model with those swings** (log-vol mean-reverting, calibrated to the four statistics;
daily return–vol correlation −1.0 needed to reach a monthly −0.37): 0.61 / 0.40 / 0.83 —
about 80% of the gap closed. The remainder is within what a strike above spot and a volatility
premium add, +0.02–0.03 each.

**The mechanism.** Within one month the premium is a level: it lifts the fitted line without
tilting it, which is why constant σ gives an up-beta near 0.17. Pooled over months, calm ones
bring small moves and small premiums, turbulent ones large moves and large premiums, so large
moves arrive with large premiums and the fitted line steepens; falls tend to bring rising
volatility, so the pairing is strongest on the way up.

**Also found:** `bxm_beta.py`'s "calendar" case measures half-month periods marked to market,
not the calendar months §09 describes; `verify_examples.py`'s "a buy-write's down-beta exceeds
1" checks `< 1.0`; "BXM's published 0.63" there and in two docstrings is stale (0.46).

## What changes

1. **The simulator, under changing volatility.** `wheel_sim.py` gains a stochastic-volatility
   scenario: log-volatility mean-reverting with a leverage correlation, its swing structure
   taken from the S&P's measured statistics and its level the running example's σ = 20%, each
   option priced at the volatility of the day it is sold. Its defaults stay constant σ, so the
   other scenarios are byte-identical (diff checked, as for `--scenario constrained`). It
   reports the wheel book's plain and split betas — and, for the question below, its central
   mean results, so it is known whether they move.
2. **The buy-write replica.** `bxm_beta.py` reworked to daily steps, with the conventions the
   prose describes (each option's life; 21-day overlapping), under constant σ and under the
   calibrated swings; its checks fixed and the figures pinned.
3. **The real-data replication.** A script that reads the three series from files the reader
   downloads (sources and steps in its docstring and the bibliography), and computes the real
   index's betas under each fit, the synthetic index on the real path, and the S&P's volatility
   statistics. The data are not committed: the repository is public and the series are Cboe's,
   S&P's and FRED's. `verify_examples.py` runs it when the files are present and says SKIP
   otherwise, as it does for matplotlib.
4. **The prose**, in plain paragraphs: what is measured, what the model produces, what is
   published, why they differ, what makes them agree — and what this book's betas become when
   volatility changes. Where it lives is the first open question.
5. **The bibliography**: the three data series as entries; Broadie–Chernov–Johannes cited
   where its parameters are used; the read levels of the four papers updated for what was read
   on 2026-11-20. Copies renamed into `literature/` on Windows.
6. **TODO**: II-36 closed — Myth 2 is "Covered calls provide downside protection" (2014,
   Exhibit 1 p. 24, argued p. 28); II-37 opened for this, citing this plan.

## The model's assumptions and constants

**The constants are not challenged.** σ = 20%, μ = 7% and δ = 2.5% describe the running
example's single stock, and the index data neither confirm nor contradict them. For scale: the
S&P 500's realized volatility over 1988–2026 was 17.9% (monthly mean 14.9%), and its total
return grew 10.7% a year in log terms — one path, which estimates an expected return poorly.

**The constant-σ assumption is challenged — for risk statistics measured across periods.**
It is also the spine's foundation: with one σ, depth is a self-contained state, and that is
what lets the census, the holding time and the ledger be computed rather than simulated. So
the analytic model cannot carry changing volatility without losing what it is. The simulator
can, and step 1 measures whether the central results move. If they move materially, that is a
finding for the article to state — most likely in §10 or §14 — not a change of constants.

## Open questions

1. **Where the explanation lives.** The project's rule keeps Parts I–II in the model's own
   voice, with the extended treatment of data in Part IV. Real index data in §09 is outside the
   model, if not the live account. Options: (a) all of it in §09, as a subsection after the
   betas; (b) §09 keeps the model's side — its betas under constant and changing volatility,
   and why a published beta differs — and the real-index replication goes to §14 with a
   pointer; (c) all of it to §14, §09 keeping one sentence and a pointer.
2. **The stock's swing structure.** The index's measured swings, applied to a single stock at
   σ = 20%: a stock's volatility swings at least as much, with a weaker leverage effect. Borrow
   the index's numbers and say so, or find a single-stock source.
3. **The mean results.** Run the central results under changing volatility now, as part of
   step 1, or open it as its own TODO item once the betas are done.
