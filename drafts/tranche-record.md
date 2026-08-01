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

The regime rule is Appendix B's item 3, applied mechanically: the traded universe's
equal-weighted return over the tranche alone, exposure-matched exactly as `live_ledger`'s
benchmark is. Annualising three weeks is noisy by construction — +19.5%/yr is +1.2% of actual
movement — and the label is kept anyway, because a rule that is adjusted for plausibility is not
a rule.

## The ledger

| as-of | Track A, cost basis | Track B, economic | same-names B&H | overlay excess | 90% CI, clustered | selection |
|---|---|---|---|---|---|---|
| 2026-07-02 | +38.11% | +19.73% | +24.50% | −4.77% | −19.8% .. +7.6% | +25.39% |
| 2026-07-24 | +38.36% | +24.34% | +28.71% | −4.37% | −18.1% .. +6.9% | +29.63% |

P(excess < 0) reads 69% on both rows. UNH remains the single largest position in both
decompositions; on the second row it is 39% of the selection gap and, on its own, the difference
between −4.37% and +1.99%.

## The spine

| as-of | entry law, predicted / assigned | contracts | mean depth, model / live | q(x), model / realised | KM median | lot-days above strike |
|---|---|---|---|---|---|---|
| 2026-07-02 | 71.5 / 71 | 921 | 0.151 / 0.146 | 26.3% / 19.6% | 49 d † | 19.4% |
| 2026-07-24 | 69.9 / 71 | 956 | 0.157 / 0.148 | 27.6% / 19.6% | 56 d | 18.7% |

Mean depth is at the article's μ = 7%; at the window's realised drift the model reads 0.097
against the same 0.148, which is the comparison that says which parameter the census is
sensitive to. Live survival stays above the model's at every horizon on both rows.

**† 2026-08-01.** The pre-registration's Appendix A prints 56 d for this baseline, and today's
code gives 49 d on the same corpus. Changes landed after that appendix was written — the seam
dedupe that removed a phantom TSCO lot (`8d6b592`) and the exclusion of EMLC and 9988
(`6aaf681`) are the candidates. The row above carries what is reproducible now; P11 is scored
against 49 d, with the discrepancy stated.
