# Pre-registration: the operator's entry-selection rule

**Written 2026-07-27, before any price data was fetched and before any model was
fitted to the selection decision.** That ordering is the whole point of this
document: the rule below is what the operator says they do, recorded so that a
later fit reads as a test of a stated hypothesis rather than a story
reconstructed to match whatever the regression found. Nothing in this file may
be edited after the first fit is run; corrections go in a dated appendix.

Context: TODO #14. The live account sells ~1.70 lots per name-year against the
model's 10.4 (p\* = 20%) or 5.2 (p\* = 10%), and per-name put opens have a modal
gap of exactly 7 days but a mean gap of 21.7 days. The operator skips weeks. The
model's step 1 never waits, and has no filter that could. The question is what
the skipping rule is, and whether it explains any part of the gap between the
mechanical model's predicted economics and the live account's realized ones.

## The rule as stated by the operator

Reproduced as given, including the operator's own caveat that it is "very vague,
not always followed systematically."

1. **Universe.** Dividend aristocrats with market capitalisation above $10B.
2. **Weeklies preferred.** Names with weekly option expiries are preferred over
   names offering only monthlies.
3. **Size preferred.** Higher market capitalisation preferred over lower.
4. **Fallen angels preferred.** The prevailing price level is near the bottom of
   its 5-year range.
5. **But avoid falling knives.** Exclude names that keep trending linearly lower.
6. **Oversold on 30 days.** Of the survivors, pick those near the bottom of the
   2σ Bollinger band on a 30-day window.
7. **Budget.** Sell puts in order of preference until the margin-less-safety-
   buffer allows no more.

## Mapping to computable features

Every rule maps onto something derivable from daily closes plus static name
attributes. Feature definitions are fixed here so they cannot be tuned later.

| rule | feature | definition |
|---|---|---|
| 1 | `aristocrat`, `mcap` | static universe attributes (external; see caveat) |
| 2 | `weeklies` | name offers weekly expiries — inferred from the observed expiry grid across the whole statement, not from the trades of the name in question on the week being scored |
| 3 | `log_mcap` | log market capitalisation |
| 4 | `pct5y` | (S − min₅y) / (max₅y − min₅y), on trailing 5-year daily closes, as-traded |
| 5 | `slope`, `slope_r2` | OLS slope of log price on time over a trailing 250 trading days, and its R². "Falling knife" = slope strongly negative **and** R² high |
| 6 | `pctB` | (S − MA₃₀) / (2·σ₃₀), where MA₃₀ and σ₃₀ are the 30-trading-day mean and standard deviation of the close. Rule 6 says the operator prefers `pctB` near −1 |
| 7 | budget | the weekly count of new puts is taken as given; the model conditions on it |

Rule 4 is a *level* signal and rule 5 is a *slope* signal, and they point in
opposite directions by construction — the operator wants a low price that is not
still falling. The interaction is therefore part of the hypothesis, not a
refinement of it.

## Statistical form

Rule 7 makes this a **ranked choice under a budget**, not a set of independent
per-name coin flips: in week *t* the operator scores an eligible set and takes the
top few until margin runs out. The correct likelihood is conditional-logit /
discrete-choice over the weekly choice set, with the number chosen taken as
given. Fitting independent per-name logistic regressions would misattribute the
weekly budget constraint to the features, and is pre-emptively rejected here.

Choice set per week: the names the operator was plausibly willing to trade —
operationalised as every symbol that appears anywhere in the statement's quality
universe, which is itself an outcome of rules 1–3 and therefore cannot be used to
test them. **Rules 1–3 are consequently not testable from this data**; only rules
4–6, which discriminate *within* the already-selected universe *across weeks*,
are. This is stated now so that a later inability to test rules 1–3 is not
mistaken for a negative result.

## What would confirm and what would disconfirm

Confirmation: `pct5y` and `pctB` carry negative coefficients (low price level,
oversold) that are significant against the weekly choice set, and the falling-
knife interaction shows a positive coefficient on `slope` conditional on low
`pct5y` (a low price is preferred only when it has stopped falling).

Disconfirmation: coefficients indistinguishable from zero, or of the wrong sign,
would mean the skipping pattern is driven by something not in the stated rule —
capital availability, attention, or noise.

**Neither outcome is a claim about return.** Establishing that entries are timed
to drawdowns is a claim about *behaviour*. Establishing that the timing *earned*
anything is a claim about the price process, and the sample cannot carry it:
41 completed lots, ~45 correlated names, one market regime. Under GBM, entry
timing cannot generate return by construction, so a positive return finding
would be a claim of mean reversion and must be argued as one.

## Pre-committed secondary fit

Alongside the stated rule, a small generic feature set (trailing return over
1/3/12 months, realised volatility, distance from the 52-week high) will be fitted
on the same choice sets, and both reported. The generic set is fixed here at five
features to bound the search: with ~651 observed entries, fishing across a wide
feature space would overfit long before it informed anything.

## Caveats fixed in advance

* Market capitalisation and aristocrat status are *current* attributes; using
  them as if they held throughout the window is a mild look-ahead. Rules 1–3 are
  untestable here anyway (see above), so this is recorded, not corrected.
* The choice set is reconstructed from names the operator actually traded at some
  point, which understates the true eligible universe and biases rules 4–6 toward
  looking weaker than they are.
* Weeks where margin was already exhausted are not observable from the cash
  statement. Rule 7's budget is proxied by the realised weekly count.

## Appendix A, 2026-07-27: the choice set changed, and the fit was re-run

Nothing above has been edited. This appendix records a change to the *data* the
fit runs on, made after the first fit and before any new tranche of statements.

The weekly menu was previously every name that ever appeared in the statements —
126 names, including speculative growth names, China ADRs, ETFs and a preferred.
It is now the 96 names of `EXCLUDED_LIST`'s complement, which is what **rule 1
said the universe was all along**. The third caveat above ("the choice set is
reconstructed from names the operator actually traded, which understates the true
eligible universe") is unchanged in kind but smaller in degree: the menu is still
reconstructed, but it no longer contains names rule 1 excludes by definition.

Sample: 54 weeks, 5,184 name-weeks, 644 sales (was 55 / 6,914 / 716).

Results are in Appendix 3 of `drafts/2026-07-27-discrepancy-catalogue.md`. In
summary, against the hypotheses fixed above:

* **Rules 4 and 6 confirmed, more strongly than on the old menu.** `pct5y`
  β = −0.723 (z = −11.4), `pctB` β = −0.462 (z = −9.5); chosen names sit at the
  27th and 35th percentiles. Pseudo-R² rose 0.07 → 0.094.
* **Rule 5 rejected outright.** The pre-registered positive `slope` coefficient
  is negative and larger than before (β = −0.306, z = −4.9). Both props of the
  earlier partial rescue are gone: `slope_r2` went from +0.136 (z = +3.3) to
  −0.071 (z = −1.3), and the secondary set's `off52w` from +0.352 (z = +3.4) to
  −0.080 (z = −0.7). The reading that rule 5 survived as "prefer the ones that
  have started to come back" is **withdrawn** — it was an artifact of the old
  menu.
* The stale context figures in the header and the caveats above restate as: 36
  completed lots (was 41), 34 names carrying inventory (was ~45), and **1.41**
  lots per name-year against the model's 10.4 at p\* = 20% (was 1.70).

The disconfirmation clause above is satisfied for rule 5 and only rule 5, which
is what a pre-registration is for.
