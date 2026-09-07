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
python code/analyze_statement.py         # sanity: seam, dedupe, new symbols
python code/live_ledger.py --bootstrap   # the ledger, the intervals, concentration
python code/model_vs_live.py             # the spine, link by link
python code/selection_fit.py             # the entry-rule coefficients
python code/iv_panel.py                  # the volatility panel
```

Copy the previous corpus into a scratch `statements/` and run the same set against it, so every
restated figure arrives with a verified before/after rather than as a bare new number. Classify
the regime from the tranche's own universe return **before** reading anything else off the
refresh. Then append one row to each table, and carry every moved figure into the sections and
into TODO IV-1/IV-2.

## What arrived

| as-of | statements through | new lots done | lots done / open | universe over the tranche | regime |
|---|---|---|---|---|---|
| 2026-07-02 | 2026-07-09 (`USD`, `USD1`) | — (baseline) | 36 / 19 | +8.96%/yr (whole window) | rally |
| 2026-07-24 | 2026-07-30 (`USD2`) | 4, no assignments | 40 / 15 | +19.50%/yr | rally |
| 2026-08-21 | 2026-09-01 (`USD3`) | 7, no assignments | 47 / 8 | +55.25%/yr | rally |

The regime rule is Appendix B's item 3, applied mechanically: the traded universe's
equal-weighted return over the tranche alone, exposure-matched exactly as `live_ledger`'s
benchmark is. Annualising three weeks is noisy by construction — +19.5%/yr is +1.2% of actual
movement — and the label is kept anyway, because a rule that is adjusted for plausibility is not
a rule. The third row is noisier still in the same direction: +55.25%/yr is +4.24% of actual
movement over 28 days, and it is by some distance the strongest tranche so far. It is also the
first tranche whose *lots* moved rather than its quotes — seven called away, no new assignments —
so the ledger below moves more between rows two and three than it did between one and two.

## The ledger

| as-of | Track A, cost basis | Track B, economic | same-names B&H | overlay excess | 90% CI, clustered | selection |
|---|---|---|---|---|---|---|
| 2026-07-02 | +38.11% | +19.73% | +24.50% | −4.77% | −19.8% .. +7.6% | +25.39% |
| 2026-07-24 | +38.36% | +24.34% | +28.71% | −4.37% | −18.1% .. +6.9% | +29.63% |
| 2026-08-21 | +36.96% | +32.11% | +37.71% | −5.61% | −18.7% .. +5.1% | +38.71% |

P(excess < 0) reads 69% on the first two rows and **77%** on the third. UNH remains the single
largest position in both decompositions; on the second row it is 39% of the selection gap and, on
its own, the difference between −4.37% and +1.99%, and on the third 27% of the gap and the
difference between −5.61% and +0.20%. ACN joins UNH, ELV and MSFT on the third row's list of
positions that are negative on the overlay and positive on selection at once.

**What moved the third row, since it moved more than the second.** Seven lots were called away in
a 4.24% month and none were replaced, so inventory fell from fifteen open lots to eight. Every
call-away books its surrendered upside into C, which rose $42.3k → $50.7k against a call premium
that rose only $32.8k → $34.4k: the call leg went from giving back 28.9% of its own premium to
giving back **47.6%**. In dollars the call leg moved the excess by **−$6,870**, which is more than
the whole of its −$3,072 net move; the put leg (+$1,565, 25.2% → 28.4% of premium kept) and lower
frictions (+$2,233) gave $3,798 of it back. Track A *fell* while Track B
rose by eight points, which is the ledger gap this record exists to show — a brokerage statement
sees a quiet month of premium, the economic ledger sees a book cashing in its unrealised gains at
strikes fixed months earlier.

## The spine

| as-of | entry law, predicted / assigned | contracts | mean depth, model / live | q(x), model / realised | KM median | lot-days above strike |
|---|---|---|---|---|---|---|
| 2026-07-02 | 71.5 / 71 | 921 | 0.151 / 0.146 | 26.3% / 19.6% | 49 d † | 19.4% |
| 2026-07-24 | 69.9 / 71 | 956 | 0.157 / 0.148 | 27.6% / 19.6% | 56 d | 18.7% |
| 2026-08-21 | 66.4 / 71 | 1011 | 0.165 / 0.149 | 30.5% / 21.6% | 56 d | 20.1% |

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

**† 2026-08-01.** The pre-registration's Appendix A prints 56 d for this baseline, and today's
code gives 49 d on the same corpus. Changes landed after that appendix was written — the seam
dedupe that removed a phantom TSCO lot (`8d6b592`) and the exclusion of EMLC and 9988
(`6aaf681`) are the candidates. The row above carries what is reproducible now; P11 is scored
against 49 d, with the discrepancy stated.

## The selection fit

Not tabulated until now, because until now no tranche moved it. The third does, on one
pre-registered coefficient, so it is recorded here rather than left to be noticed at freeze.

| as-of | pct5y (rule 4) | pctB (rule 6) | slope (rule 5) | slope_r2 (rule 5) | pseudo-R² | choice sets |
|---|---|---|---|---|---|---|
| 2026-07-24 | −0.726 (z −11.6) | −0.486 (z −10.2) | −0.332 (z −5.3) | −0.101 (z −1.8) | 0.097 | 57 wk, 672 sales, menu 96 |
| 2026-08-21 | −0.778 (z −12.7) | −0.483 (z −10.4) | −0.328 (z −5.2) | −0.132 (z −2.4) | 0.100 | 61 wk, 697 sales, menu 100 |

Rules 4 and 6 are unmoved and stay confirmed. **Rule 5's rejection hardened**: `slope_r2` was the
last prop of the withdrawn "prefer the ones that have started to come back" reading, which needed
it positive, and it has now crossed from indistinguishable from zero to significantly the *wrong*
sign at z = −2.4. The operator prefers falls that are less linear, not more — which is what rules 4
and 6 already say, a dislocation rather than a trend. This is a pre-registered rule moving further
against itself on new data, which is the outcome the pre-registration's disconfirmation clause was
written to make reportable; nothing about the specification changes, and it is refit, not
re-specified. The secondary set's `off52w` likewise stays insignificant (−0.042, z = −0.4).

## A note on the universe, third tranche

The traded universe grew **96 → 100 names**: HLI, OTIS, ROL and WSO had been mentioned in the raw
rows without ever reaching an analysis and now carry contracts, and KR, LII and XYL took their
place on that list. The menu in the selection fit and the denominator of the equal-weight benchmark
both move with it, so the third row's universe return is not computed against quite the same basket
as the second's. The effect is small at four names in a hundred and it is recorded rather than
corrected for, because the universe is defined by what was traded and revising it backwards would
be choosing a basket.

The put book's width moved with it: puts are now sold across **99 names while inventory sits in
34**, and put margin is **$43.0k = 29.5% of Track B capital** against the single-name model's 1.6%.
That is III-1's book-width caveat at the new corpus; the ratio fell from 31% because Track B
capital rose on the inventory mark, not because the book narrowed.

## Section prose that moves with the ledger

Three sentences in the written sections quote the live account in words rather than digits, so they
do not show up in a grep for a moved number and have to be checked by hand at every refresh. They
are listed here because the next refresh will not find them otherwise.

- **§09, the put leg.** "the mark loss taken at assignment consumed about **three quarters**" was
  restated to "about **seven tenths**" on 2026-09-07 (74.8% → 71.6%), and the following clause from
  "the **quarter** that survives" to "the **three tenths** that survive". It drifts a point or two
  per tranche in the same direction; re-check the ratio B / put premium each time.
- **§09, the call leg.** "surrendered **nearly a third** more at call-away than it collected in
  premium" was wrong at the fourth tranche and is now "**nearly half again** more" (28.9% → 47.6%).
  This is the fastest-moving of the three, because a single call-away month moves it several points.
- **§09, the skew.** "about **six** points on puts 5–10% below spot against about **three** on calls
  the same distance above" still holds (+6.0% / +2.7%), but the call figure is drifting down and
  will need "about two and a half" or a rewrite before long.

And one figure in **§16 (outlook)** cannot be checked at all: "only about **twenty** puts per name
reach the market in a year rather than fifty-two" is the discrepancy catalogue's 18.1, which has no
script behind it (INF-2) and is measured over a window three tranches out of date. It is left
standing only because there is nothing to replace it with; give it a script before the freeze.
