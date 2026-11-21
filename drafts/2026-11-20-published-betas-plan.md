# §09's betas against the published ones — plan

**Status: agreed 2026-11-20**, in conversation, before any code: the direction (Sergei:
quantify this book's beta under changing volatility, and explain the sources of the mismatch to
the reader in detail) and the three choices under *Decided*. Opens TODO II-37; closes II-36.

## What was found

Reviewing §09's caution about comparing its split betas with published ones, the comparison
the box made could not be reproduced, and the published up-beta could not be explained.
Everything below is from scratch scripts run on cloud on 2026-11-20; none of it is in the
repository yet, and it is all to be recomputed by committed code before any of it is quoted.

**The published figures.** Israelov and Nielsen (2015, Table 6): the Cboe S&P 500 BuyWrite
Index over 1996-03-25 to 2014-12-31 has a plain beta of 0.62, an up-beta of 0.46 and a
down-beta of 0.85, "computed using 21-day overlapping returns", excess of 3-month LIBOR. No
paper states how the up/down split is fitted. The same authors (2014, Table 1) give 0.67 /
0.63 / 0.78 over 1986–2013; Israelov, Klein and Tummala (2018, Table 1(a), full samples to
September 2015) give up-betas of 0.35–0.60 and down-betas of 0.81–0.95 across eleven indexes,
averaging 0.46 / 0.84 (their 2006–2015 matched panel (b) runs to 0.96). The published up-beta
moves with the sample.

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

**Re-marking is not the mechanism** (2026-11-21, a scratch counterfactual on the same paths).
Marking each call through its life at the volatility it was sold at, rather than the day's,
leaves the per-life betas unchanged and moves the 21-day window betas by 0.01–0.02: up-beta
0.384 → 0.369 with the leverage effect, 0.253 → 0.242 without, 0.427 → 0.405 at implied 1.2×;
down-betas within 0.012. The window figures are the strike's blurring (0 → 0.17 at one
volatility) and the premium pairing, and the two do not add: 0.17 + 0.18 against 0.38 with
the leverage effect, 0.17 + 0.12 against 0.25 without.

**What turns this book's up-beta** (2026-11-21, scratch traces at 1,280 paths, seed 20260722;
the headline figures are in `--scenario stochvol`'s output since `c095869`). The premium adds
+0.020 / +0.021 with and without the leverage effect, so it does not decide the direction;
premium left out, the up-beta is 0.827 / 0.784 / 0.863 (constant σ / moving, no leverage /
moving, leverage). The cap at the strike decides it, through how far the rises reach — sd of a
four-week rise 0.036 / 0.041 / 0.034, rises over 20% 0.12% / 0.85% / 0.34% — and through the
depth mix. Within-depth pooling with the constant run's census gives 0.805 without the leverage
effect (so about half of its −0.043 is the rises, half the census, approximately) and 0.860
with it (nearly all of its +0.036 is the rises, the census −0.006).

**Why the census tilts toward the strike** (same traces). Share of call periods begun within
2% of the strike 8.0% / 9.9% / 9.3%, for different reasons. *Without the leverage effect* lots
enter shallower: with E[σ²] held at 20%², 68% of assignments happen below 20% volatility (mean
at entry 17.8%), and entry depth scales with it (mean x₀ 0.0072 below 12%, 0.0309 above 32%),
so 77.4% of new lots enter within 2% against 70.6%; shallow call periods 13.8 a year against
11.7. *With it* entries are not shallower — assignments come in falls, as volatility rises
(mean at entry 22.3%), 72.3% enter within 2%, shallow periods 12.0 a year — and the share rises
because the book has 12% fewer call periods in all (128.6 a year against 146.9; at the constant
run's total the share would be 8.2%). Why the book shrinks under moving volatility is step 6's
open inventory question; §09's paragraph 6 states the larger share and leaves its reason until
that is answered (Sergei, 2026-11-21).

**Also found:** `bxm_beta.py`'s "calendar" case measures half-month periods marked to market,
not the calendar months §09 describes; `verify_examples.py`'s "a buy-write's down-beta exceeds
1" checks `< 1.0`; "BXM's published 0.63" there and in two docstrings is stale (0.46).

## What changes

1. **The simulator, under changing volatility.** `wheel_sim.py` gains a stochastic-volatility
   scenario: log-volatility mean-reverting with a leverage correlation, its swing structure
   taken from the S&P's measured statistics and its level the running example's σ = 20%, each
   option priced at the volatility of the day it is sold. Its defaults stay constant σ, so the
   other scenarios are byte-identical (diff checked, as for `--scenario constrained`). It
   reports the wheel book's plain and split betas, and its holding time and inventory, so it is
   known whether they move (decision 3).
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
   volatility changes. §09 carries the model's side and links forward to §14 for the
   real-index replication (decision 1); §14's part is drafted with it, parked until §14 is
   written.
5. **The bibliography**: the three data series as entries; Broadie–Chernov–Johannes cited
   where its parameters are used; the read levels of the four papers updated for what was read
   on 2026-11-20. Copies renamed into `literature/` on Windows.
6. **The limitation, stated where it bites.** The article already names constant σ in §06 (depth
   is self-contained "which leans on σ being a constant", with a pointer to §09), §10 (volatility
   rises in falling markets) and §15's outlook ("Volatility that moves"). Each is brought up to
   date with what the simulator measures — §06's pointer made true by §09's new paragraphs, §10's
   stress paragraph given the measured effect on the boundaries if step 1 finds one, §15's item
   narrowed to what is still open — and §07 gains a sentence if the holding time moves.
7. **TODO**: II-36 closed — Myth 2 is "Covered calls provide downside protection" (2014,
   Exhibit 1 p. 24, argued p. 28); II-37 opened for this, citing this plan; two more opened —
   the swing structure checked on representative NOBL holdings and on the index (decision 2),
   and the true excess return under changing volatility with proper pricing (decision 3).

## The model's assumptions and constants

**The constants are not challenged.** σ = 20%, μ = 7% and δ = 2.5% describe the running
example's single stock, and the index data neither confirm nor contradict them. For scale: the
S&P 500's realized volatility over 1988–2026 was 17.9% (monthly mean 14.9%), and its total
return grew 10.7% a year in log terms — one path, which estimates an expected return poorly.

**The constant-σ assumption is challenged — for risk statistics measured across periods.**
It is also the spine's foundation, and the obstacle to relaxing it is not a missing closed
form so much as what the model would stop being:

- **A second state variable.** With one σ, a lot's prospects depend on its depth alone, so a
  single function of x answers every question. With σ moving, they depend on depth *and* the
  current volatility, which every lot shares and which persists for months: the walk becomes
  two-dimensional, the census a joint density over (x, σ), and the lots no longer independent
  given the price.
- **The closed-form results are statements about one σ.** The call-grid tax β·σ·√τ_c, its √n
  law, the two stability boundaries μ − δ > σ²/2 and > σ², and the ~45bp a vol point are each
  exact for a constant σ; with σ moving, each becomes an average over the volatility path that
  has to be computed, and the boundaries become conditions on its distribution.
- **A second priced risk.** Option prices then depend on volatility as well as the price, so
  "one measure, two worlds" needs a volatility risk premium as a further free parameter, and
  the strongest test the model has — excess = Δ̄·(μ − r) − leak, exactly — acquires a vega term.

The expectations themselves (Little's law, the census integrals) are linear and would survive
on a two-dimensional grid; it is the analytic spine and the exact tests that would not. The
simulator carries changing volatility at no such cost, and step 1 measures whether the central
results move. If they move materially, that is a finding for the article to state where the
assumption bites — not a change of constants.

## Decided

1. **Where the explanation lives** (Sergei, 2026-11-20): §09 keeps the model's side — this
   book's betas under constant and changing volatility, and why a published beta reads
   differently — and the real-index replication goes to §14, which §09 points to by link (a
   promise until §14 exists). The project's rule keeps Parts I–II in the model's own voice.
2. **The stock's swing structure** (Sergei, 2026-11-20): borrow the index's measured swings —
   standard deviation of log volatility 0.50, half-life about two months — at the running
   example's σ = 20%, the leverage correlation run both at zero and at the index's, and say so.
   A new TODO item verifies the structure on representative stocks from NOBL's holdings (the
   S&P 500 Dividend Aristocrats) and on the index itself, which §14 measures anyway.
3. **The mean results** (Sergei, 2026-11-20): step 1's runs also report the median and mean
   holding time and the average inventory under changing volatility, which depend on the price
   path and the strikes but not on option prices. The true excess return waits: under moving
   volatility Black–Scholes at the current volatility misprices an option (a fair price uses
   the volatility expected over its life, plus a convexity term), so the ledger needs proper
   pricing first, and its exact test gains a vega term. That is its own TODO item.
4. **A lot's return includes its premium** (Sergei, 2026-11-20, after step 1): the beta is
   measured on the lot's whole return over a call period, premium included, as a published
   beta is. At one volatility this changes no figure — the premium is a level, uncorrelated
   with the period's return, so the slope is the same either way — but once volatility moves
   it is larger in turbulent months, and the down-beta reads 0.98–0.99 rather than exactly 1.
   Step 4 restates §09's definition of R, gives the cushion sentence its condition ("at one
   volatility"), and says why the down-beta drops; `model.split_beta`'s docstring says the
   premium is included and why it does not move the slope.

## Step 1's results (2026-11-20, `--scenario stochvol`, 1,280 paths × 30 years per run)

| | up | down | plain | E[I] | E[I]/λ, years | held at 3 months |
|---|---|---|---|---|---|---|
| constant σ (model.py 0.828 / 1.000 / 11.40 / 1.10) | 0.827 | 1.000 | 0.926 | 11.3 | 1.09 | 38% |
| changing σ, no leverage effect | 0.804 | 0.976 | 0.904 | 10.7 | 1.02 | 37% |
| changing σ, leverage ρ = −0.9 | 0.884 | 0.988 | 0.949 | 9.9 | 0.97 | 31% |

Standard errors ≈0.003 on the betas, ≈0.15 on E[I]; the median holding time is 8 weeks in all
three. The up-beta's direction depends on the leverage effect; the inventory falls 6–13%, its
mechanism not yet established; with the premium left out the down-beta is exactly 1.000 in
every run. ρ = −0.9 is a daily correlation, about −0.34 monthly against the index's −0.41.

## Where it stands (2026-11-21)

**Steps 1–4 are on `main`.** Step 4 is §09's subsection "Published betas come from a world
where volatility moves", after the clock-ratio paragraph, written paragraph by paragraph with
Sergei on 2026-11-21: what a beta measures (`1bc4e0c`); the published figures, checked against
the PDFs (`3749566`); the model's buy-write at one volatility (`c84d899`); the old caution box
and `[^bxm-beta]` deleted (`7937d84`); the premium's pairing and the leverage effect named
(`e0c80d4`); the S&P's swings closing most of the gap (`70df915`); this book under moving
volatility, two paragraphs, with the up-beta's direction explained by the cap at the strike
(`c095869` code and checks, `e251d36`, `fe14781`); why the model keeps one σ, its claim on
eq:delta-return signed (`bc41a26`). The §14 pointer sits under §09's existing promise on
`sec:verification`. §00 needed nothing new.

**Step 5, partly done.** The three data series are in the bibliography under a new **[D]**
level (`70df915`), and the copies are in `literature/` and `data/market/` on Windows. Left: the
read levels of the four papers for what was read on 2026-11-20 — the copies read on cloud were
the SSRN working paper of *Covered Calls Uncovered* and the May 2007 revision of
Broadie–Chernov–Johannes, now in `literature/` beside the held journal copy and January 2008
revision; BCJ's P-measure parameters are identical in both revisions (checked 2026-11-21), and
its entry should name the copy it rests on. BCJ is not cited in the prose — its parameters
were used only in a scratch run — so "cited where its parameters are used" has nothing to
attach to unless a later paragraph uses them.

**Step 6, next: the limitation where it bites.** §06's "[the returns section] prices what that
leaves out" now has the subsection to land on — reread the two together. §07/§08: inventory
falls under moving volatility (E[I] 11.3 → 10.7 without the leverage effect, 9.9 with), its
mechanism untraced; it is also why, with the leverage effect, a larger share of the book sits
near its strikes, which paragraph 6 states without a reason until this is answered. §10's
stress paragraph and §15's "Volatility that moves" narrowed to what is still open. Then the
rest of step 7 (II-37 to `DONE.md`).

