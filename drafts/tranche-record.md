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

Two things a row's difference cannot tell you. **An entry-law move is not the tranche's own**:
every put is priced at the whole window's drift, so a tranche that moves the drift re-prices
every contract already counted, and only matching contracts across the two corpora separates the
new contracts' expectation from the re-pricing (2026-11-05 note under the spine). And **a figure
that reproduces is not thereby right**: the misdated price cache reproduced perfectly at every
ingest before this one. A Saturday among the cached dates is the check for that one.

## What arrived

| as-of | statements through | new lots done | lots done / open | universe over the tranche | regime |
|---|---|---|---|---|---|
| 2026-07-02 | 2026-07-09 (`USD`, `USD1`) | — (baseline) | 36 / 19 | +8.96%/yr (whole window) | rally |
| 2026-07-24 | 2026-07-30 (`USD2`) | 4, no assignments | 40 / 15 | +19.50%/yr | rally |
| 2026-08-21 | 2026-09-01 (`USD3`) | 7, no assignments | 47 / 8 | +55.25%/yr | rally |
| 2026-10-01 | 2026-09-29 (`USD4`) | 1, nine assignments | 48 / 16 | −86.8%/yr | drawdown; market rule flat |
| 2026-11-05 | 2026-10-31 (`USD5`) | 1, one assignment | 49 / 16 | +95.9%/yr | rally; market rule drawdown |

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

### 2026-11-05: September in reverse

The sixth tranche is the fifth turned inside out, and `USD2` again: a drawdown for the S&P 500 and
a rally for the traded universe. The aristocrats took back September's fall and more (NOBL
+8.30%) while the index slipped. All figures are on corrected price dates (see the 2026-11-05
restatement below); the earlier rows' corrected values are there too.

| window | days | S&P 500 | market rule | universe, matched | book rule |
|---|---|---|---|---|---|
| `USD` 2025-02-07 .. 2026-05-02 | 449 | +19.95% (+16.2%/yr) | rally | +9.78% (+8.0%/yr) | flat |
| `USD1` 2026-05-02 .. 2026-07-09 | 68 | +4.31% (+23.2%/yr) | rally | +1.72% (+9.3%/yr) | rally |
| `USD2` 2026-07-09 .. 2026-07-30 | 21 | −1.33% (−23.2%/yr) | drawdown | +2.73% (+47.5%/yr) | rally |
| `USD3` 2026-07-30 .. 2026-09-01 | 33 | +2.71% (+30.0%/yr) | rally | +3.12% (+34.5%/yr) | rally |
| `USD4` 2026-09-01 .. 2026-09-29 | 28 | +0.32% (+4.1%/yr) | flat | −6.83% (−89.0%/yr) | drawdown |
| `USD5` 2026-09-29 .. 2026-10-31 | 32 | **−1.11% (−12.7%/yr)** | **drawdown** | **+8.40% (+95.9%/yr)** | **rally** |
| **all to date** | 631 | +25.79% (+14.9%/yr) | rally | +26.75% (+15.5%/yr) | **rally** |

The earlier windows' book-rule figures move by up to 0.89 points against the corrected 10-01
table, because the universe grew to 107 names (see the universe note below). No label changes,
but one comes close: the `USD` window's book rule reads +7.96%/yr, a hair under the +8% rally
line. It is recorded and never scored, so nothing turns on it.

**The accumulated window's book rule returns from flat to rally**, +4.5%/yr (corrected) to
+15.5%/yr — the same mechanism as September's fall, run the other way: October's average
exposure was nearly two and a half times the window's, so its gain carries that much weight.
The market rule stays rally at +14.9%/yr, and **the two rules agree on the accumulated row
again**. Appendix C item 8 made September's disagreement the finding; what October adds is that
the book rule's accumulated label has now changed twice in two months on single months of
exposure-weighted movement, which says how much weight it can bear at freeze. Nothing is scored.

## The ledger

| as-of | Track A, cost basis | Track B, economic | same-names B&H | overlay excess | 90% CI, clustered | selection |
|---|---|---|---|---|---|---|
| 2026-07-02 | +38.11% | +19.73% | +24.50% | −4.77% | −19.8% .. +7.6% | +25.39% |
| 2026-07-24 | +38.36% | +24.34% | +28.71% | −4.37% | −18.1% .. +6.9% | +29.63% |
| 2026-08-21 | +36.96% | +32.11% | +37.71% | −5.61% | −18.7% .. +5.1% | +38.71% |
| 2026-10-01 | +37.36% | +25.69% | +29.65% | −3.96% | −16.0% .. +6.1% | +34.69% |
| 2026-11-05 | +36.69% | +31.09% | +38.49% | −7.40% | −19.8% .. +2.9% | +36.15% |

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

**2026-11-05.** Every figure in this section up to here, bar the 2026-11-05 row, was measured on
misdated prices and flatters the overlay by 2.2 to 2.8 points; the corrected rows are in the
2026-11-05 section below. The 2026-11-05 row and everything after this note are on corrected
dates, and comparisons with the fourth row are with its corrected values.

P(excess < 0) reads **86%** on the fifth row, and the interval's upper end, +2.9%, is the nearest
zero has come; on corrected prices the five intervals are thirty, twenty-seven, twenty-six,
twenty-four and twenty-three points wide. UNH is 25% of the selection gap and nearly all of the
shortfall (−7.40% → −2.06% without it). INTU, called away this month, rises to second in both
decompositions, and the positions negative on the overlay and positive on selection at once are
UNH, INTU, ELV, MSFT and ACN.

**What moved the fifth row: the third row again, with most of its call-aways still to come.** The
traded universe rose 8.40% while the S&P 500 fell; one lot was called away and one assigned. The
one exit — INTU at 282.5, on a stock that closed at 325.15 — raised C by a twelfth. The rest of
the rally sits in the calls still open: sixteen lots carry calls written before it, and their mark,
what it would cost to buy them back, rose from 12% of call premium to 26%. The call leg went from
−42.8% to −53.1% and moved the excess 1.6 times as far as the excess moved in total, from −6.17%
to −7.40%; the put leg, its new premium written with only KMB assigned against it, went from
+14.8% to +20.0% and gave back 38% of that. Track A fell seven tenths of a point while Track B rose
five and a half: the statement sees an ordinary month of premium, the economic ledger sees held
names rising through the strikes that cap them. The open-call mark is upside surrendered but not
yet booked as C — most of it becomes C at call-away if prices hold, and it vanishes only if they
fall back.

## The spine

| as-of | entry law, predicted / assigned | contracts | mean depth, model / live | q(x), model / realised | KM median | lot-days above strike |
|---|---|---|---|---|---|---|
| 2026-07-02 | 71.5 / 71 | 921 | 0.151 / 0.146 | 26.3% / 19.6% | 49 d † | 19.4% |
| 2026-07-24 | 69.9 / 71 | 956 | 0.157 / 0.148 | 27.6% / 19.6% | 56 d | 18.7% |
| 2026-08-21 | 66.4 / 71 | 1011 | 0.165 / 0.149 | 30.5% / 21.6% | 56 d | 20.1% |
| 2026-10-01 | 74.9 / 80 | 1042 | 0.168 / 0.152 | 28.3% / 21.3% | 57 d | 19.2% |
| 2026-11-05 | 70.0 / 81 | 1111 | 0.166 / 0.156 | 31.4% / 20.8% | 63 d | 19.2% |

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

**2026-11-05.** Every row above bar the 2026-11-05 row, and every note before this one, was
measured on misdated prices; the corrected rows are in the 2026-11-05 section below. The entry
law moves most.

**2026-11-05: the entry-law notes on the third and fourth rows read a difference of totals.** Both
attribute their row's move to the tranche's own contracts — "55 new put contracts … none of them
was assigned", "expected 8.5 of the 31 new put contracts". But every contract is priced at the
drift measured over the whole window, so a tranche that moves the drift re-prices the thousand
contracts already counted, and the difference between two rows' totals mixes the two. Matched
contract by contract: the third row's 55 new contracts expected 2.3 assignments and got none,
while the drift's rise took the rest from 69.9 to 64.0 — so the error's widening was the drift,
and the 55 contracts narrowed it; the fourth row's 31 expected **2.6**, not 8.5, and got 9, while
the drift's fall took the rest from 66.4 to 72.2. The tranche figures, 2.3 and 2.6, are the same
on corrected prices; the drift's share is not.

On the fifth row, all on corrected prices, the entry law reads 70.0 predicted against 81 assigned,
−13.6%. The tranche's own 69 contracts expected 4.9 and got 1, in a month the traded universe
rose 8.40%, while the drift's rise (+43.4% → +51.7%) took the rest from 69.3 to 65.1. Priced at
today's drift, **the last three tranches' 155 contracts expect 9.6 assignments and got 10**: the
whole shortfall sits on the 956 contracts counted by the second row (60.3 against 71). The model's
mean depth at the realised drift (μ = 54.2%) is 0.078 against a live 0.156, from 0.094 against
0.153 at the fourth row's corrected 45.9% — the gap widening again as the drift rose. Live
survival stays above the model's at every horizon. The KM median moves 57 d → 63 d as September's
nine assignments aged a month, and the curve sits flat at 14.0% from 180 d with 16 lots censored.
The model's mean holding time at the account's measured parameters is 0.17 y (64 d, E[J] 3.18),
from a corrected 0.19 y (69 d, E[J] 4.33) — a model output, not a measurement.

## The selection fit

Not tabulated until now, because until now no tranche moved it. The third does, on one
pre-registered coefficient, so it is recorded here rather than left to be noticed at freeze.

| as-of | pct5y (rule 4) | pctB (rule 6) | slope (rule 5) | slope_r2 (rule 5) | pseudo-R² | choice sets |
|---|---|---|---|---|---|---|
| 2026-07-24 | −0.726 (z −11.6) | −0.486 (z −10.2) | −0.332 (z −5.3) | −0.101 (z −1.8) | 0.097 | 57 wk, 672 sales, menu 96 |
| 2026-08-21 | −0.778 (z −12.7) | −0.483 (z −10.4) | −0.328 (z −5.2) | −0.132 (z −2.4) | 0.100 | 61 wk, 697 sales, menu 100 |
| 2026-10-01 | −0.825 (z −13.8) | −0.489 (z −10.6) | −0.319 (z −5.2) | −0.148 (z −2.8) | 0.105 | 65 wk, 730 sales, menu 103 |
| 2026-11-05 | −0.866 (z −14.9) | −0.485 (z −10.6) | −0.316 (z −5.3) | −0.152 (z −2.9) | 0.109 | 68 wk, 761 sales, menu 107 |

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

The fifth row again: rule 4 firmer (z −14.9), rule 6 where it was, and `slope_r2` to z = −2.9.
`off52w` is −0.004 (z −0.0). The date fix does not move this fit at all — every row reproduces to
the third decimal on corrected prices — so the table needs no restatement.

## A note on the universe, 2026-11-05

The traded universe grew **103 → 107 names**: BX and KKR, last tranche's mentioned-only names,
now carry closed contracts, and APO and DKS are new. NTR and OZK, one option row each, and FGEN and
TRI.TN, corporate actions, are still mentioned without reaching an analysis. The earlier windows'
book-rule figures move by up to 0.89 points against the corrected 10-01 table with it, and no
label changes.

Puts are now sold across **106 names while inventory sits in 37**, and put margin is **27.6% of
Track B capital**, falling again on the inventory mark rather than a narrower book. Counted from
`live_ledger.py`'s own parse as before, which reproduces the 102 and 37 on the fourth row's corpus.

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

## 2026-11-05: every row restates, because half of every year's prices were a day late

`prices.py` dated each Yahoo bar by the machine's own calendar. Yahoo stamps a daily bar at the US
open, and from the first Sunday of October to the first Sunday of April that moment falls after
midnight in Adelaide — so every bar in that half of the year was filed under the next day:
Saturday rows, no Mondays, Thanksgiving and Christmas 2025 each a day late. Any price looked up by
date in those months was the previous session's; April to September was right. Fixed in
`prices._trading_day()`, cache version 3. A fresh fetch through the old code reproduces the first
four rows of each table above to the digit, so what follows is the date fix alone. Those rows
stay as they are; each is restated here on its own corpus.

| as-of | same-names B&H | overlay excess | 90% CI, clustered | P(excess < 0) | selection | put leg kept | call leg kept |
|---|---|---|---|---|---|---|---|
| 2026-07-02 | +24.50% → +27.32% | −4.77% → −7.61% | → −23.9% .. +5.7% | 69% → 79% | +25.39% → +28.55% | +18.8% → +9.0% | −43.3% → −47.6% |
| 2026-07-24 | +28.71% → +31.32% | −4.37% → −7.01% | → −21.9% .. +5.2% | 69% → 79% | +29.63% → +32.50% | +20.1% → +10.9% | −40.7% → −44.6% |
| 2026-08-21 | +37.71% → +40.10% | −5.61% → −7.99% | → −22.1% .. +3.5% | 77% → 84% | +38.71% → +41.32% | +24.4% → +15.6% | −53.4% → −57.0% |
| 2026-10-01 | +29.65% → +31.86% | −3.96% → −6.17% | → −19.2% .. +4.6% | 70% → 79% | +34.69% → +37.12% | +23.3% → +14.8% | −39.7% → −42.8% |

Track A does not move on any row, being cash, and Track B moves by at most 0.03 points.

| as-of | entry law, predicted / assigned | mean depth, model / live | q(x), model / realised | lot-days above strike |
|---|---|---|---|---|
| 2026-07-02 | 71.5 → 65.5 / 71 | 0.150 / 0.146 | 26.3% → 27.5% / 19.6% | 19.4% → 19.5% |
| 2026-07-24 | 69.9 → 64.2 / 71 | 0.156 / 0.148 → 0.149 | 27.6% → 28.7% / 19.6% | 18.7% → 18.8% |
| 2026-08-21 | 66.4 → 61.1 / 71 | 0.164 / 0.149 → 0.150 | 30.5% → 31.6% / 21.6% | 20.1% → 20.2% |
| 2026-10-01 | 74.9 → 69.3 / 80 | 0.168 / 0.152 → 0.153 | 28.3% → 29.3% / 21.3% | 19.2% → 19.3% |

Contracts, the KM medians and the realised exercise rates do not move. The first two rows' model
mean depth reads 0.150 and 0.156 where they carry 0.151 and 0.157 even before the fix: that is
`7758fac`'s grid fix again, the one bisected for the third row below, confirmed by running
`7758fac~1` and `7758fac` on both corpora.

**The overlay was flattered by 2.2 to 2.8 points on every row, and the reason is a selection on
the last day.** A put is assigned because the stock closed below its strike on expiry Friday; the
misdated cache marked the new lot at Thursday's close, which on such a day sits above Friday's,
so the mark loss B was understated. A call is exercised because the stock closed above the strike,
where Thursday's close sits below Friday's, so the upside surrendered C was understated too. Both
prices enter the shares' own return with the opposite sign, which is why same-names buy-and-hold
rises by what the overlay loses and Track B stays put. B is now 80–89% of put premium on the four
rows, against 72–79% as recorded. **The verdict survives with a firmer lean**: every interval still
contains zero, and P(excess < 0) reads 79–84% where it read 69–77%.

**The entry law loses five or six expected assignments on every row**, and the aggregate error
becomes −7.7%, −9.6%, −13.9% and −13.4% where it read +0.7%, −1.5%, −6.5% and −6.4%: inside P1's
±15%, and near its edge. Two things moved it together, which no run here separates: every entry in
those months is now priced at its own session's open rather than the previous session's, and the
measured drift the contracts are priced at rose with the corrected shares (+43.4% against +40.3%
on the fourth row). "Finished below the strike" now equals "assigned" on every row; the
one-contract gap between them was the bug.

**Two findings that rested on the misdated cache are withdrawn.**

- *The top probability bucket's miscalibration.* Appendix A of the pre-registration narrowed P1 to
  the aggregate because the bucket above 20% predicted 27.4% and realised 8.0% at the open, against
  25.9% and 24.3% at the close, and TODO IV-1 read that as the operator selling into intraday
  weakness that partly reverts. On corrected dates it predicts 26.2% and realises 20.3% at the open
  on the first row, and 26.1% against 21.7% on the fourth: most of the gap was the misdated prices.
  P1 stays an aggregate test as written; whether any reversion remains is not established either
  way.
- *"The wrong clock is the one that fits."* Priced on the inclusive session count `iv_panel` uses,
  the fourth row's puts predict 95.9 assignments against 80, and on the calendar count 69.3: one
  overshoots by a fifth and the other falls short by a seventh, so neither fits. The 88.7 that
  `model_vs_live`'s T1 docstring and TODO quoted does not reproduce at today's count even on the
  misdated cache (94.2 on the second row's corpus), so it was a different count.
- *UNH as the sign of the overlay.* The ledger notes above, and Appendix A, say UNH alone is the
  difference between a negative and a positive excess. On corrected prices the excess without it
  is −0.13%, −0.09%, −1.67% and −0.31% on the four rows: UNH is nearly all of the shortfall, never
  the sign. It is still the largest position in both decompositions, at 47%, 38%, 27% and 28% of
  the selection gap.

**The ledger's reconciliation residual**, printed as a residual "from entry/exit day alignment"
and 0.5–1.0% on the four rows, is 0.0% on every corrected row: it was this bug.
The acquisition gap's mean/median ratio, P5's statistic, reads 2.4× on the first row where it read
1.8×, a heavier jump tail than recorded.

**Unchanged:** the selection fit, to the third decimal on every row. The IV panel moves by about a
point; the prose list below quotes corrected figures from the sixth row on. In the regime tables only the `USD`
window and the accumulated row move, and no label changes. On the 2026-10-01 table the market rule's `USD` window reads +19.95% (+16.2%/yr) for
+18.86%, and the accumulated window +27.20% (+16.6%/yr) for +26.04%; the book rule's `USD` window
reads +8.89% (+7.2%/yr, still flat) for +7.56%, and the accumulated window +7.45% (+4.5%/yr, still
flat) for +6.60%.

**Scoring.** Appendix A's baselines and every figure on the rows above were measured on the
misdated cache. At freeze the predictions are scored against the corrected figures — the first
rows of the two tables here for the baselines — as P11 is already scored against the 49 d that
reproduces rather than the 56 d printed.

## Section prose that moves with the ledger

These sentences in the written sections quote the live account either in words rather than digits,
or in digits that do not look like live figures, so a grep for a moved number will not find them.
Check each by hand at every refresh; this list is kept current rather than appended to.

- **§09, the put leg.** "the mark loss taken at assignment consumed about **four fifths**", and
  then "the **fifth** that survives on the put leg" — B / put premium and the put leg's kept
  share, 79.2% and +20.0% at the sixth tranche, on corrected prices. It read three quarters and a
  quarter at the fifth on misdated ones (74.7%, +23.3%); the date fix alone moves it by eight or
  nine points, and a tranche by a point or a few.
- **§09, the call leg.** "which finished behind by about **half** of the premium it collected" —
  the call leg's kept share, −53.1% at the sixth tranche. The fastest mover: a month of call-aways,
  or of rally against open calls, moves it ten points (corrected, −42.8% → −53.1% over the last
  two rows).
- **§09, the skew.** "about **five** points on puts 5–10% below spot against **under one** on calls
  the same distance above", and "at matched distance it still runs **three to five** points above
  the call leg's" — `iv_panel.py`'s cross-tab, all-tenor column: puts +5.2% at 5–10% and +8.9%
  beyond, calls +0.6% and +5.9%, at the sixth tranche. The calls cell at 5–10% holds 42 contracts
  and moved two points on two new ones in October, so this sentence is the noisiest on the list;
  at the corrected fifth tranche it read +5.0% against +2.6%, which is where the old "roughly
  twice" came from.
- **§09, the window.** "within the precision **eighteen** months can support" — the ledger's
  window in months, 1.48 y at the sixth tranche.
- **§09, the tenor.** "weekly puts near **29%** implied against roughly **33%** on its four-week
  calls" — `iv_panel.py`'s session-clock IV for puts ≤ 1 wk and calls ~monthly, 29.3% / 33.0%.
- **§04, the aristocrat footnote.** The index's yield and volatility against the S&P 500's, from
  `market_regime.py` — 1.98% at 14.3% against 1.00% at 17.0% at the sixth tranche.

And one figure in **§16 (outlook)** cannot be checked at all: "only about **twenty** puts per name
reach the market in a year rather than fifty-two" is the discrepancy catalogue's 18.1, which has no
script behind it (INF-2) and is measured over a window five tranches out of date. It is left
standing only because there is nothing to replace it with; give it a script before the freeze.
