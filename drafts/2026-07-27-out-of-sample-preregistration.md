# Pre-registration: what the next tranche of live data should show

**Written 2026-07-27, before any statement data beyond 2026-07-09 exists.** The
operator will keep supplying statements as time passes. That makes every future
tranche a genuine out-of-sample test — but only if the expectations are on
paper first. Written afterwards, the same sentences would be a story fitted to
the answer.

This file may not be edited once new data has been examined. Corrections go in
a dated appendix, and a failed prediction is recorded as a failure, not retuned.
It is the companion to
`drafts/2026-07-27-selection-rule-preregistration.md`, which fixed the entry-rule
hypothesis under the same discipline.

## The baseline being predicted from

Everything below is measured over 2025-05-02 .. 2026-07-02: 1.17 years, 129
names, 70 lots acquired, 41 exited, 29 open. The window rose — the traded
universe returned +9.48%/yr equal-weighted and the names actually held +20.07%.
**One regime, one direction.** That is the limitation the new data exists to fix.

    Track A on cost basis          +34.40% /yr
    Track B economic, on market    +15.43% /yr
    same-names buy-and-hold        +17.62% /yr
    option-overlay excess           -2.19% /yr   (90% CI -15.6% .. +8.5%)
    selection contribution         +10.59% /yr

## Group 1: mechanical predictions, regime-independent

These follow from the model's structure and should hold in *any* regime. They
are the strongest tests, because a failure here is a failure of the model rather
than of a parameter choice.

**P1. The entry law stays calibrated.** Over any tranche with at least 200 put
contracts, the number of assignments predicted by N(−d₂) — evaluated at the
strike actually written, the spot on the trade date, and a trailing volatility
known at the time — should land within **±15%** of the realised count. Baseline:
94.6 predicted against 97 assigned, an error of 2.5%.

**P2. The depth census stays calibrated.** Mean depth over lot-days, model
against live, within **±15%**. Baseline: 0.139 against 0.146, an error of 5%.
This is the sharpest test in the set, because the census carries income and
capital.

**P3. q(x) stays monotone in depth**, and the aggregate predicted exercise rate
stays within **±40%** of realised. Baseline: 19.9% predicted against 15.6%. The
loose band is deliberate — the model runs mildly aggressive and that is expected
to persist, see P4.

**P4. The model keeps exiting lots slightly too fast.** Live survival S(t) should
remain **above** the model's at every horizon out to a year. This is *not*
censoring — the baseline comparison already uses Kaplan-Meier — so if the gap
closes as more lots resolve, the current reading was an artifact and P4 is the
prediction that fails.

**P5. The jump tail persists.** The mean acquisition gap should stay at least
**1.5×** the median. Baseline: 4.4% against 2.2%, a ratio of 2.0. This is the
lognormal's known missing piece and it should not go away.

**P6. The call-grid tax stays visible.** The share of lot-days spent above the
lot's own call strike should stay in the **10–25%** band. Baseline: 16.7%.

## Group 2: the regime test, which is the point of waiting

**P7. The overlay excess is concave in the market return.** This is the central
prediction and the one the current data structurally cannot test.

The overlay's economic result is `premium − B − C`: premium collected, less the
mark loss at assignment, less the upside surrendered at call-away. Those two
costs are driven by *opposite* market conditions:

  * **a strong rally** — few assignments, so B is small; many call-aways with
    large overshoot, so C is large. Excess **negative**. This is the baseline
    window, and it is why −2.19% should not be read as the unconditional figure.
  * **a flat market** — few assignments and few call-aways; premium is kept
    against small B and small C. Excess **positive**, and this should be the
    overlay's best regime.
  * **a sharp drawdown** — many assignments landing deep, so B is large; few
    call-aways, so C is small. Excess **negative again**.

So the prediction is not "the excess rises as the market falls". It is that
excess peaks near zero market return and is negative at both extremes, while
averaging to approximately zero across regimes, which is what no-arbitrage
requires. **A monotone relationship in either direction falsifies this.**

Reporting rule fixed now: the excess is quoted with its bootstrap interval, never
as a point estimate, and a tranche is scored against the *sign pattern* above,
not against a target number.

**P8. Selection shrinks, and may go negative, when drawdowns stop mean-reverting.**
The +10.59% was earned buying dips in a market that kept recovering. Rules 4 and
6 are dip-buying rules and the falling-knife filter of rule 5 is **absent from
the trades** — that is the fitted result, not a supposition. So in a regime where
cheap keeps getting cheaper, the same behaviour should underperform.

This is the sharpest available test of whether the live account's advantage was
skill or regime, and it is the prediction most likely to be uncomfortable.

**P9. The operator's behaviour stays stable even if its payoff does not.** The
conditional-logit coefficients on `pct5y` and `pctB` should stay negative and
significant. P8 and P9 are independent: P9 says the operator keeps doing the same
thing, P8 says it stops working. If P9 fails, the process changed, and that must
be **recorded as a change of process** rather than absorbed into the model.

**P10. The volatility risk premium compresses when realised volatility spikes.**
Put-leg IV minus subsequent realised volatility should stay positive on average
but narrow materially in any high-volatility tranche. Baseline: +5 to +10 points
in a calm, rising market.

## Group 3: what improves by waiting alone

No new trades needed; these sharpen as the existing book ages.

**P11.** The 29 open lots resolve, filling in the censored tail. The
Kaplan-Meier median should **rise** above the current 63 days as the slow lots
report. The mean remains unestimable — its tail is measured in decades.

**P12.** The impairment hazard gains observations. Baseline: 2 in-window entries
into names since judged un-wheelable, across ~45 names over 1.17 years. No rate
is predicted; the point is that it accumulates toward one.

## Procedure, fixed in advance

1. **Minimum tranche before re-running:** six months of new statements, or 20
   new completed lots, whichever comes first. Re-running on every new week would
   invite reading noise as signal.
2. **No new features** in `selection_fit.py` without a dated amendment to the
   entry-rule pre-registration. The five-feature secondary set stays five.
3. **Refit, do not re-specify.** The same code, the same parameters, the same
   bins. Any change to a definition invalidates the comparison and must be
   applied to the baseline as well, with both figures reported.
4. **Report failures as failures.** A prediction that misses is recorded in the
   appendix with the number that missed it. The value of this file is entirely in
   its being falsifiable.
5. **Regime is classified before the results are computed** — by the traded
   universe's equal-weighted return over the tranche, into rally (> +8%/yr),
   flat (−8% to +8%), or drawdown (< −8%/yr) — so that P7 cannot be scored after
   seeing which way it went.

## What would count as the model being wrong

Not a single missed prediction; several, in a pattern. Specifically: P1 and P2
failing together would mean the entry law and the depth process disagree with
reality in the same direction, which is the spine and not a detail. P7 coming out
monotone would mean the overlay has a directional exposure the decomposition
says it cannot have. Either would be a finding worth more than anything currently
in the article, and neither should be explained away.
