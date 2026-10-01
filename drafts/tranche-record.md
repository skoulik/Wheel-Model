# The tranche record

The live account behind this article keeps trading, and its brokerage statements arrive roughly
monthly. Each one is ingested as it comes and every live figure in the article is recomputed on
the whole corpus to date — see [the out-of-sample pre-registration](2026-07-27-out-of-sample-preregistration.md),
Appendix B, for why the earlier "wait for six months or twenty lots" trigger was retired.

This file is that record — and unlike everything else in `drafts/` it is **not** historical, which
is why it carries no date in its name: it is appended to as long as the account keeps trading, and
it closes only when the article is frozen for release.

**The window is never chosen**: it is always everything to date, and
every intermediate state is on the table below, so no favourable sub-window can be selected
afterwards and any sub-window a reader wants is computable from the rows. The path of the
estimates is itself a result — it shows how much a live wheel record moves as it accumulates,
which is [the holding-time section](../sections/07-holding-time.md)'s argument in the account's
own numbers.

**Rows are append-only.** A row records what the figures were, computed with the code of the day;
it is never edited afterwards. If a later change to the code moves an earlier figure, that is
recorded as a new dated note under the tables, not by rewriting the row — the Kaplan–Meier note
below is the first such case.

## Adding a row

From the repo root, with the new CSV dropped into `statements/`:

```
python code/prices.py                    # extend the cache to the new dates
python code/market_regime.py             # the regime, both rules — run this FIRST
python code/analyze_statement.py         # sanity: seam, dedupe, new symbols
python code/live_ledger.py --bootstrap   # the ledger, the intervals, concentration
python code/model_vs_live.py             # the spine, link by link
python code/selection_fit.py             # the entry-rule coefficients
python code/iv_panel.py                  # the volatility panel
```

Copy the previous corpus into a scratch `statements/` and run the same set against it, so every
restated figure arrives with a verified before/after rather than as a bare new number. Classify
the regime **before** reading anything else off the refresh — `market_regime.py` prints both
rules, and **both labels are recorded**: the market rule (the S&P 500's plain return over the
tranche) and the book rule (the traded universe, exposure-matched), per the pre-registration's
Appendix C. Then append one row to each table, and carry every moved figure into the sections and
into TODO IV-1/IV-2.

## What arrived

| as-of | statements through | new lots done | lots done / open | universe over the tranche | regime |
|---|---|---|---|---|---|
| 2026-07-02 | 2026-07-09 (`USD`, `USD1`) | — (baseline) | 36 / 19 | +8.96%/yr (whole window) | rally |
| 2026-07-24 | 2026-07-30 (`USD2`) | 4, no assignments | 40 / 15 | +19.50%/yr | rally |
| 2026-08-21 | 2026-09-01 (`USD3`) | 7, no assignments | 47 / 8 | +55.25%/yr | rally |
| 2026-10-01 | 2026-09-29 (`USD4`) | 1, nine assignments | 48 / 16 | −86.8%/yr | drawdown; market rule flat |

The regime rule is Appendix B's item 3, applied mechanically: the traded universe's
equal-weighted return over the tranche alone, exposure-matched exactly as `live_ledger`'s
benchmark is. Annualising three weeks is noisy by construction — +19.5%/yr is +1.2% of actual
movement — and the label is kept anyway, because a rule that is adjusted for plausibility is not
a rule. The third row is noisier still in the same direction: +55.25%/yr is +4.24% of actual
movement over 28 days, and it is by some distance the strongest tranche so far. It is also the
first tranche whose *lots* moved rather than its quotes — seven called away, no new assignments —
so the ledger below moves more between rows two and three than it did between one and two.

### 2026-09-07: the regime column was measuring the operator, and a second rule joins it

The rows above are untouched, as rows here always are. What follows is the restatement, and the
reason for it is in the pre-registration's [Appendix C](2026-07-27-out-of-sample-preregistration.md).

The regime column classifies from the **traded universe**, which is a basket the operator chose —
daily, it regresses on NOBL at beta 0.951 with R² 0.888 against 0.571 / 0.471 on SPY, so it *is* a
dividend-aristocrat basket, and a rotation into that style reads on this rule as a market move.
Exposure-matching compounds it: weighting days by the book's own inventory asks what these names
did on the days we were long, which is a question about the book. From now on both rules are
recorded, and `code/market_regime.py` computes them.

| window | days | S&P 500 | market rule | universe, matched | book rule |
|---|---|---|---|---|---|
| `USD` 2025-02-07 .. 2026-05-02 | 449 | +18.86% (+15.3%/yr) | rally | +7.58% (+6.2%/yr) | flat |
| `USD1` 2026-05-02 .. 2026-07-09 | 68 | +4.31% (+23.2%/yr) | rally | +1.95% (+10.5%/yr) | rally |
| `USD2` 2026-07-09 .. 2026-07-30 | 21 | **−1.33% (−23.2%/yr)** | **drawdown** | +3.14% (+54.6%/yr) | rally |
| `USD3` 2026-07-30 .. 2026-09-01 | 33 | +2.71% (+30.0%/yr) | rally | +3.35% (+37.1%/yr) | rally |
| **all to date** | 571 | +25.64% (+16.4%/yr) | rally | +18.83% (+12.0%/yr) | rally |

**These book-rule figures are not the ones in the rows above and are not a correction to them.**
Each row above was computed on the corpus available that month over a hand-typed window, and the
first is a whole-window figure where the other two are tranche-only; the table here is one rule
applied to every window on today's corpus, with windows contiguous — each running from the
previous tranche's last statement date to its own. The windows also do not line up: the record's
baseline row spans `USD` and `USD1` together.

**`USD2` flips.** Three weeks the record labels a rally were a **−1.33% month for the S&P 500**.
The basket outran the index and the old rule read that as the market rising.

**The accumulated window is a rally on both rules**, +16.4%/yr and +12.0%/yr, so nothing about
§15's regime caveat softens: everything this account has measured, it measured in a rising market.
One down month inside sixteen is not the drawdown P7 and P8 are waiting for.

### 2026-10-01: the first drawdown, and it is the book's alone

The fifth tranche's two labels disagree, the mirror image of `USD2`: a flat month for the S&P 500
and a drawdown for the traded universe. Dividend aristocrats fell (NOBL −5.27%) while the index
held, and the basket the operator trades fell with them. It is the first window the book rule
labels a drawdown.

| window | days | S&P 500 | market rule | universe, matched | book rule |
|---|---|---|---|---|---|
| `USD` 2025-02-07 .. 2026-05-02 | 449 | +18.86% (+15.3%/yr) | rally | +7.56% (+6.1%/yr) | flat |
| `USD1` 2026-05-02 .. 2026-07-09 | 68 | +4.31% (+23.2%/yr) | rally | +1.85% (+9.9%/yr) | rally |
| `USD2` 2026-07-09 .. 2026-07-30 | 21 | −1.33% (−23.2%/yr) | drawdown | +2.80% (+48.7%/yr) | rally |
| `USD3` 2026-07-30 .. 2026-09-01 | 33 | +2.71% (+30.0%/yr) | rally | +3.13% (+34.6%/yr) | rally |
| `USD4` 2026-09-01 .. 2026-09-29 | 28 | **+0.32% (+4.1%/yr)** | **flat** | **−6.65% (−86.8%/yr)** | **drawdown** |
| **all to date** | 599 | +26.04% (+15.9%/yr) | rally | +6.60% (+4.0%/yr) | **flat** |

One rule per column on today's corpus, as before. The earlier windows' book-rule figures differ
from the 09-07 table by up to 0.34 points because the universe grew to 103 names (see the
universe note below); no earlier label changes.

**The accumulated window's book rule falls from rally to flat**, +12.0%/yr to +4.0%/yr. One
month moves it that far because exposure-matching weights each day by the book's inventory, and
September's loss fell on inventory well above the window's average. **The market rule does not
move** — the window is +15.9%/yr on the S&P 500 — so §15's caveat stands as written: everything
this account has measured, it measured in a rising market.

What changes is P7's classification, which is the book rule's by Appendix C item 7: the
accumulated window P7 will be scored against now reads flat. This is the first time the two rules
have disagreed on the accumulated row, and Appendix C item 8 makes that disagreement the finding
rather than either label. Nothing is scored here — a one-month drawdown is a tranche label, which
item 9 says is recorded and never scored — and a single month at −6.65% is not the sustained
drawdown P8 was written for.

## The ledger

| as-of | Track A, cost basis | Track B, economic | same-names B&H | overlay excess | 90% CI, clustered | selection |
|---|---|---|---|---|---|---|
| 2026-07-02 | +38.11% | +19.73% | +24.50% | −4.77% | −19.8% .. +7.6% | +25.39% |
| 2026-07-24 | +38.36% | +24.34% | +28.71% | −4.37% | −18.1% .. +6.9% | +29.63% |
| 2026-08-21 | +36.96% | +32.11% | +37.71% | −5.61% | −18.7% .. +5.1% | +38.71% |
| 2026-10-01 | +37.36% | +25.69% | +29.65% | −3.96% | −16.0% .. +6.1% | +34.69% |

P(excess < 0) reads 69% on the first two rows and **77%** on the third. UNH remains the single
largest position in both decompositions; on the second row it is 39% of the selection gap and, on
its own, the difference between −4.37% and +1.99%, and on the third 27% of the gap and the
difference between −5.61% and +0.20%. ACN joins UNH, ELV and MSFT on the third row's list of
positions that are negative on the overlay and positive on selection at once.

**What moved the third row, since it moved more than the second.** Seven lots were called away in
a 4.24% month and none were replaced, so inventory fell from fifteen open lots to eight. Every
call-away books its surrendered upside into C, which rose by a fifth against a call premium that
rose by a twentieth: the call leg went from giving back 28.9% of its own premium to giving back
**47.6%**. The call leg alone moved the excess **2.2 times** as far as the excess moved in total;
the put leg (25.2% → 28.4% of premium kept) and lower frictions gave 55% of that back. Track A
*fell* while Track B rose by eight points, which is the ledger gap this record exists to show — a
brokerage statement sees a quiet month of premium, the economic ledger sees a book cashing in its
unrealised gains at strikes fixed months earlier.

P(excess < 0) reads **70%** on the fourth row, and the interval is twenty-two points wide against
twenty-seven, twenty-five and twenty-four before it. UNH is 28% of the selection gap and, on its
own, the difference between −3.96% and +1.43%. INTU joins UNH, ELV, MSFT and ACN on the list of
positions negative on the overlay and positive on selection at once; ZTS leaves the top five.

**What moved the fourth row: the third row turned over.** Nine puts were assigned in a month the
traded universe fell 6.65%, one lot was called away, and inventory doubled from eight open lots to
sixteen. The mark loss at acquisition rose from 71.6% of put premium to 74.7%, which the put
leg's new premium only just covered — its result barely moved. C did not move at all: the one
call-away, ACN, came on a spike above its 185 strike that had reversed by the close, so at the
as-traded close its surrendered upside is slightly negative. The month's call premium, less the
mark on calls still open, therefore went into the ledger with nothing surrendered against it, and
the call leg accounts for all of the excess's move from −5.61% to −3.96%. Track A rose four tenths
of a point while Track B fell six and a half, the ledger gap running the other way: a brokerage
statement sees a busy month of premium, the economic ledger sees the held names marked down.

**2026-10-01: the by-leg split is restated.** Until today `live_ledger.py` credited the premium on
a contract still open to its leg and put that contract's mark — what it would cost to close —
into frictions, so every freshly written contract counted as premium kept in full. The fifth
tranche left sixteen lots carrying fresh calls, and as printed the call leg would have read
−27.3%. Each mark now sits in its own leg, and frictions are commissions and buy-backs alone.
The excess and every column of the table above are unchanged; the leg figures quoted in prose,
here and in `TODO.md`, restate as follows on each row's own corpus:

| as-of | put leg kept, as quoted | restated | call leg kept, as quoted | restated |
|---|---|---|---|---|
| 2026-07-02 | +20.7% | +18.8% | −32.9% | −43.3% |
| 2026-07-24 | +25.2% | +20.1% | −28.9% | −40.7% |
| 2026-08-21 | +28.4% | +24.4% | −47.6% | −53.4% |
| 2026-10-01 | | +23.3% | | −39.7% |

The third row's account above survives at a smaller scale: on the restated split its call leg
went −40.7% → −53.4% and moved the excess 1.6 times as far as the excess moved in total, with the
put leg giving back 38% of that and frictions nothing.

## The spine

| as-of | entry law, predicted / assigned | contracts | mean depth, model / live | q(x), model / realised | KM median | lot-days above strike |
|---|---|---|---|---|---|---|
| 2026-07-02 | 71.5 / 71 | 921 | 0.151 / 0.146 | 26.3% / 19.6% | 49 d † | 19.4% |
| 2026-07-24 | 69.9 / 71 | 956 | 0.157 / 0.148 | 27.6% / 19.6% | 56 d | 18.7% |
| 2026-08-21 | 66.4 / 71 | 1011 | 0.165 / 0.149 | 30.5% / 21.6% | 56 d | 20.1% |
| 2026-10-01 | 74.9 / 80 | 1042 | 0.168 / 0.152 | 28.3% / 21.3% | 57 d | 19.2% |

Mean depth is at the article's μ = 7%; at the window's realised drift the model reads 0.097
against the same 0.148 on the second row, and 0.085 against 0.149 on the third — the realised
drift having risen to +54.3% — which is the comparison that says which parameter the census is
sensitive to, and it says it more loudly each tranche. Live survival stays above the model's at
every horizon on all three rows.

The third row's entry law drifts the other way from the first two: 66.4 predicted against the same
71 assigned, because 55 new put contracts were written and none of them was assigned. The KM
median holds at 56 d across a tranche that resolved seven lots, which is the first row where that
figure has been tested by exits rather than by censoring — the curve is now flat at 12.9% from
180 d with 8 lots censored, against 15.8% with 15. The model's own mean holding time at the
account's measured parameters fell 0.21 y → 0.16 y (77 d → 59 d, E[J] 4.79 → 3.68) on the higher
realised drift; that is a model output at live parameters, not a live measurement, and the two
must not be quoted as though they were the same kind of object.

On the fourth row the realised drift fell back to +42.8% from +54.3%, and the model's mean depth
at that drift rose to 0.098 against a live 0.152 — the first row on which that gap narrowed, which
is the same sensitivity read from the other side. Live survival stays above the model's at every
horizon. It is also the first tranche since the baseline in which puts were assigned: the model
expected 8.5 of the 31 new put contracts to be assigned and 9 were, so the aggregate error holds at −6.4%. The KM
median moves 56 d → 57 d, and the curve sits flat at 12.6% from 180 d with 16 lots censored, nine
of them under four weeks old. The model's mean holding time at the account's measured parameters
rose back to 0.21 y (75 d, E[J] 4.69) on the lower drift — again a model output, not a
measurement.

**† 2026-08-01.** The pre-registration's Appendix A prints 56 d for this baseline, and today's
code gives 49 d on the same corpus. Changes landed after that appendix was written — the seam
dedupe that removed a phantom TSCO lot (`8d6b592`) and the exclusion of EMLC and 9988
(`6aaf681`) are the candidates. The row above carries what is reproducible now; P11 is scored
against 49 d, with the discrepancy stated.

**2026-10-01.** On the third row's corpus today's code reads model mean depth **0.164** at μ = 7%
and **0.084** at the realised drift, where that row and its note carry 0.165 and 0.085. Bisected
to `7758fac` (2026-09-15), the fix for the census grid artifact; every other figure in the row
reproduces. The fourth row is on the fixed grid.

## The selection fit

Not tabulated until now, because until now no tranche moved it. The third does, on one
pre-registered coefficient, so it is recorded here rather than left to be noticed at freeze.

| as-of | pct5y (rule 4) | pctB (rule 6) | slope (rule 5) | slope_r2 (rule 5) | pseudo-R² | choice sets |
|---|---|---|---|---|---|---|
| 2026-07-24 | −0.726 (z −11.6) | −0.486 (z −10.2) | −0.332 (z −5.3) | −0.101 (z −1.8) | 0.097 | 57 wk, 672 sales, menu 96 |
| 2026-08-21 | −0.778 (z −12.7) | −0.483 (z −10.4) | −0.328 (z −5.2) | −0.132 (z −2.4) | 0.100 | 61 wk, 697 sales, menu 100 |
| 2026-10-01 | −0.825 (z −13.8) | −0.489 (z −10.6) | −0.319 (z −5.2) | −0.148 (z −2.8) | 0.105 | 65 wk, 730 sales, menu 103 |

Rules 4 and 6 are unmoved and stay confirmed. **Rule 5's rejection hardened**: `slope_r2` was the
last prop of the withdrawn "prefer the ones that have started to come back" reading, which needed
it positive, and it has now crossed from indistinguishable from zero to significantly the *wrong*
sign at z = −2.4. The operator prefers falls that are less linear, not more — which is what rules 4
and 6 already say, a dislocation rather than a trend. This is a pre-registered rule moving further
against itself on new data, which is the outcome the pre-registration's disconfirmation clause was
written to make reportable; nothing about the specification changes, and it is refit, not
re-specified. The secondary set's `off52w` likewise stays insignificant (−0.042, z = −0.4).

The fourth row moves the same way and further: rules 4 and 6 firmer (z −13.8 and −10.6), and
`slope_r2` further to the wrong sign at z = −2.8. `off52w` is now −0.009 (z −0.1).

## A note on the universe, third tranche

The traded universe grew **96 → 100 names**: HLI, OTIS, ROL and WSO had been mentioned in the raw
rows without ever reaching an analysis and now carry contracts, and KR, LII and XYL took their
place on that list. The menu in the selection fit and the denominator of the equal-weight benchmark
both move with it, so the third row's universe return is not computed against quite the same basket
as the second's. The effect is small at four names in a hundred and it is recorded rather than
corrected for, because the universe is defined by what was traded and revising it backwards would
be choosing a basket.

The put book's width moved with it: puts are now sold across **99 names while inventory sits in
34**, and put margin is **29.5% of Track B capital** against the single-name model's 1.6%.
That is III-1's book-width caveat at the new corpus; the ratio fell from 31% because Track B
capital rose on the inventory mark, not because the book narrowed.

## A note on the universe, fourth tranche

The traded universe grew **100 → 103 names**: KR, LII and XYL, last tranche's mentioned-only
names, now carry closed contracts, and BX and KKR take their place on that list with one put
each, written on the statement's last day. The earlier windows' book-rule figures move by up to
0.34 points with it, and no earlier label changes.

Puts are now sold across **102 names while inventory sits in 37**, and put margin is **29.2% of
Track B capital**. No script prints the two name counts; they were counted from
`live_ledger.py`'s own parse, which reproduces the third tranche's 99 and 34.

## Section prose that moves with the ledger

These sentences in the written sections quote the live account either in words rather than digits,
or in digits that do not look like live figures, so a grep for a moved number will not find them.
Check each by hand at every refresh; this list is kept current rather than appended to.

- **§09, the put leg.** "the mark loss taken at assignment consumed about **three quarters**", and
  then "the **quarter** that survives on the put leg" — B / put premium and the put leg's kept
  share, 74.7% and +23.3% at the fifth tranche. It read seven tenths and three tenths at the fourth
  (71.6%, and +28.4% on the old split); it moves a point or two each tranche.
- **§09, the call leg.** "which finished behind by about **two fifths** of the premium it
  collected" — the call leg's kept share, −39.7% on the split restated 2026-10-01. The fastest
  mover: a call-away month moves it several points (−40.7% → −53.4% → −39.7% over the last three
  rows). It used to compare C with premium directly ("nearly half again more"), which stopped
  being the leg's result once the marks on open calls joined the leg.
- **§09, the skew.** "about **six** points on puts 5–10% below spot against about **three** on calls
  the same distance above" — `iv_panel.py`'s cross-tab, +6.2% / +2.7% at the fifth tranche.
- **§09, the window.** "within the precision **seventeen** months can support" — the ledger's
  window in months, 1.40 y at the fifth tranche.
- **§09, the tenor.** "weekly puts near **28%** implied against roughly **33%** on its four-week
  calls" — `iv_panel.py`'s session-clock IV for puts ≤ 1 wk and calls ~monthly, 28.2% / 33.4%.
- **§04, the aristocrat footnote.** The index's yield and volatility against the S&P 500's, from
  `market_regime.py` — 2.15% at 14.3% against 0.99% at 17.3% at the fifth tranche.

And one figure in **§16 (outlook)** cannot be checked at all: "only about **twenty** puts per name
reach the market in a year rather than fifty-two" is the discrepancy catalogue's 18.1, which has no
script behind it (INF-2) and is measured over a window four tranches out of date. It is left
standing only because there is nothing to replace it with; give it a script before the freeze.
