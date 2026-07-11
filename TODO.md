# TODO

Open modeling and writing issues, from the 2026-07-10 review of the initial draft. Items are referenced from the sections as "TODO #n".

## Done

- ✅ **Symmetry of CC and CSP** (was #14). The introduction now introduces *cash-secured put* and glosses "covered", and a detour presents the payoff diagrams of both legs, states their payoff equivalence at the same strike (put–call parity, Hull pointer), recasts the wheel's two phases as one trade with alternating collateral, and notes the volatility skew as the pricing asymmetry we set aside. See `sections/02-introduction.md`.
- ✅ **Attractive price disclaimer** (was #15). The asset qualifier now reads "fundamentally sound *and* entered at an attractive price" in both places it appears; the definition of "attractive" is explicitly declared out of scope (valuation is the operator's job, the model takes the entry level as given). See `sections/02-introduction.md` and `sections/04-strategy.md`.
- ✅ **P&L formula corrected.** The draft's E[Π]/S = c_p(1+p) + p·c_c/q − p(k−1+d) double-counted the put premium (once as income at entry, once as the "recycled capital gain" at exit under the net-basis convention) and booked a mark-to-market drag into Track A. Corrected Track A run rate: **E[Π]/S = c_p + p·c_c/q** per put period. See `sections/08-returns-and-capital.md`, including the "pitfall worth naming" box documenting the error class.

## Open

1. **Correlated exits vs. the Poisson independence assumption.** On a single underlying, all lots share one price path: a recovery through a strike level calls away every lot at or below it simultaneously. The mean I\* survives (rate balance only), but the distribution is burstier than Poisson — P(I=0) and the ±√I\* fluctuation claims are idealized. Decide the framing: (a) Poisson claims apply across a diversified portfolio of names, (b) single-name idealization with means-only trust, or both. Affects sections 07 and 09.

2. **Dividends.** The strategy targets dividend payers, yet dividends are absent. Three effects: (a) dividend yield δ belongs in the probability formulas (d₂ uses r − δ − σ²/2; the price drift in q is total-return μ minus δ); (b) dividends collected on held inventory are a material Track A income stream (I\* lots × yield); (c) dividends drive early exercise of ITM covered calls (see #5) — which actually helps by recycling lots sooner. Affects sections 05, 06, 08. *Empirics from the statements (draft finding #11):* (b) ran at ~4% of gross premium for ordinary equity names (typical yields 1.5–4.5%); δ must be net of withholding, which is country-dependent (15% US treaty, 27% Denmark, 0% exempt cases — 6.4% blended); (c) is untestable from cash statements (payment dates, not ex-dates). See also #16 for the carry side.

3. **Derive d instead of assuming it.** Conditional on assignment, the drop d has a distribution implied by the same lognormal model. E[d | assignment] ≈ 7.9% for the monthly k=0.95, σ=20% example — versus the draft's assumed 0.15, a ~2.5σ event. Closed form is a standard truncated-lognormal expectation (implemented in `code/verify_examples.py`). Plan: derive E[d | assignment] in section 06, use it as base case, keep d = 0.15 as a labeled stress scenario. Materially moves q, I\*, c_c, and the excess return (−0.1%/yr vs +9.9%/yr in the section 08 example).

4. **State the measure-mixing policy explicitly.** p is risk-neutral (conservative-high), q is real-world (realistic). Defensible, but must be presented once as a deliberate design decision — "conservatism on the entry side, realism on the exit side." Also distinguish σ_IV (enters p, quoted by the market) from σ_RV (governs real dynamics, enters q and p_rw); IV > RV systematically is the strategy's documented edge and deserves its own general-audience discussion. Affects section 05 (flag already placed) and 06.

5. **American vs. European exercise.** Both p and q are terminal (European) probabilities; listed equity options are American. For short puts the approximation is good (early exercise rare, slightly raises effective p). For covered calls on dividend payers it is not negligible: deep-ITM calls are exercised the day before ex-dividend, which shortens holding periods — favorable for the strategy. Also note terminal-vs-path distinction (stock may cross the strike intra-period and come back). A caveat paragraph in sections 05/06 suffices.

6. **Smaller items.**
   - Delta vs. ITM probability: N(−d₁) ≈ 16% vs N(−d₂) ≈ 18% in the running example; section 05 now notes the conflation — keep the distinction consistent everywhere.
   - Exit-timing granularity: exits occur only on the call grid (every n put periods); q_p smoothing is means-exact, dynamics-approximate. Footnoted in section 07.
   - Track C overcharges: cash collateral securing short puts itself earns ~risk-free at the broker; only the stock-inventory component truly forgoes the rate. Flagged in section 08; needs a clean corrected Track C definition.
   - Position sizing: the model sells exactly one put per period regardless of capital. A practitioner-facing subsection on sizing against total capital (and how the capital bound interacts with m) is needed.
   - Premium-example consistency: keep c_p/c_c examples derived from the same Black–Scholes parameters as the probability examples (script enforces c_p ≈ 0.005 for the monthly k=0.95 put; the old draft's c_p = 0.02 belonged to a different implicit horizon).

## From comparison with live trading records (2026-07-10)

Source: `drafts/2026-07-10-statement-vs-model-observations.md`, an analysis of a year of real wheel operation against the tier-1 model. The queue architecture matched practice well; the following did not.

7. **Duty cycle: split cadence from tenor.** The model assumes one put always running (period = option lifetime τ_p). In practice the operator sells short-tenor options on a longer cadence (e.g., a 3-day put sold weekly), so the stock is covered by a live put only ~40–50% of calendar time. Introduce cadence period T and tenor τ_p ≤ T; premium accrues per T but prices off τ_p; annualizations change by τ_p/T. The current model is the special case τ_p = T. Biggest structural miss found.

8. **Realistic base-case parameters.** Observed assignment rates run ~8–9% per put, not the article's ~18% running example; observed recycling (for lots that recycle) is ~16%/month, not the stress example's 16%/quarter. Re-run the section 08 economics with a low-p\* regime (p\* ≈ 5–10%, weekly cadence, monthly-ish calls) as base case, keeping p\* = 20% as the aggressive variant. Reinforces #3 (derived d, not d = 0.15, as base).

9. **Censoring-aware calibration; three holding-time regimes.** Completed lots recycle fast (median ~1 month), but the extended 14-month window resolves the tail into three empirical regimes: a *fast lane* (exit at entry strike within ~a month), a *metastable* class (resolves at entry strike after months of limbo), and a *trapped* class (ages past 200+ days). Trapped layers are not abandoned or force-exited: they are held while fresh layers cycle beneath them, so strata resolve bottom-up — exactly the qualitative behavior depth-dependent q_i predicts; genuine below-basis exits are rare (2 of 41 completed lots). Statistics on completed lots alone wildly overstate the exit rate (survivorship/right-censoring); calibration of q needs survival analysis. A single q cannot produce this — a fast/metastable/trapped mixture may be a cleaner tier-2 parameterization than depth-dependent q_i, or the mixture may *emerge from* depth dependence; deciding which is part of tier 2's job.

10. **Call strike K_c as a policy variable.** The model fixes K_c at the entry strike; in practice the operator moves the call strike down to exit stuck lots (buying q at a realized-loss cost) or up in recoveries (extra gain, lower q). "Call strike vs. basis" is the operator's main tool against dead strata and the natural control knob of the tier-2 phase diagram. Empirically the lever is used asymmetrically — strikes move up freely, down only rarely — which poses a genuinely interesting model question: is that reluctance optimal (the option value of waiting for recovery), or loss-aversion the model should advise against?

11. **Common-shock arrivals.** Assignments across a portfolio of wheels cluster on market-wide drawdown dates. Exits diversify across names; arrivals do not. A portfolio-level model needs a systematic component in p — bursts arrive exactly when capital is scarcest (direct evidence for section 09's reflexivity).

12. **Transaction-cost haircut as a function of tenor.** Commissions eat a few percent of premium on short-tenor cheap options (vs. negligible on monthly). Without a friction term the model has no reason not to prefer ever-shorter tenors; the haircut belongs in any τ_p/T optimization.

13. **Permanent-impairment hazard.** "Fundamentally sound" fails occasionally in real portfolios (bankruptcies, permanent collapses): the lot enters an absorbing state with q = 0, premium ≈ 0, capital loss ≈ 100%. Even a small per-year hazard adds an expected cost that can rival annual premium income. Model it as an explicit per-lot death hazard in tier 2, not a verbal disclaimer.

16. **Dividend carry in the cost of patience.** (Draft finding #11, added 2026-07-11.) A held lot's annual waiting cost is opportunity cost + impairment hazard − net dividend yield. Carry accrues per unit holding time, so it concentrates exactly on the metastable/trapped lots of #9 — the observed patience policy is partly carry-financed, which makes the strike-down reluctance of #10 more rational than loss-aversion alone. Tier 2's phase diagram should carry δ_net per lot. Out-of-scope outliers, noted for honesty rather than modeled: bond-like securities deliberately wheeled (the live account's STRF preferred, ~9%/yr on basis, its five oldest "trapped" lots — they skew any aging-tail statistic they enter), and securities-lending income on lent-out inventory (two-thirds of observed dividend flow arrived as payments in lieu).

## Writing / infrastructure

- Prior-work section (`sections/03-prior-work.md`) is a stub; do a real literature pass before assembly (PUT/BXM indices, volatility risk premium, Whaley, Israelov & Nielsen; verify novelty claim for the queueing framing).
- Abstract to be rewritten last.
- LaTeX assembly pipeline (Unicode-math → LaTeX conversion) — decide tooling when sections stabilize.
- Figures: the ASCII payoff diagrams in the section 02 detour are placeholders — redraw as proper vector figures (TikZ or similar) at assembly time.
