# TODO

Open modeling and writing issues, from the 2026-07-10 review of the initial draft. Items are referenced from the sections as "TODO #n".

## Done

- ✅ **P&L formula corrected.** The draft's E[Π]/S = c_p(1+p) + p·c_c/q − p(k−1+d) double-counted the put premium (once as income at entry, once as the "recycled capital gain" at exit under the net-basis convention) and booked a mark-to-market drag into Track A. Corrected Track A run rate: **E[Π]/S = c_p + p·c_c/q** per put period. See `sections/08-returns-and-capital.md`, including the "pitfall worth naming" box documenting the error class.

## Open

1. **Correlated exits vs. the Poisson independence assumption.** On a single underlying, all lots share one price path: a recovery through a strike level calls away every lot at or below it simultaneously. The mean I\* survives (rate balance only), but the distribution is burstier than Poisson — P(I=0) and the ±√I\* fluctuation claims are idealized. Decide the framing: (a) Poisson claims apply across a diversified portfolio of names, (b) single-name idealization with means-only trust, or both. Affects sections 07 and 09.

2. **Dividends.** The strategy targets dividend payers, yet dividends are absent. Three effects: (a) dividend yield δ belongs in the probability formulas (d₂ uses r − δ − σ²/2; the price drift in q is total-return μ minus δ); (b) dividends collected on held inventory are a material Track A income stream (I\* lots × yield); (c) dividends drive early exercise of ITM covered calls (see #5) — which actually helps by recycling lots sooner. Affects sections 05, 06, 08.

3. **Derive d instead of assuming it.** Conditional on assignment, the drop d has a distribution implied by the same lognormal model. E[d | assignment] ≈ 7.9% for the monthly k=0.95, σ=20% example — versus the draft's assumed 0.15, a ~2.5σ event. Closed form is a standard truncated-lognormal expectation (implemented in `code/verify_examples.py`). Plan: derive E[d | assignment] in section 06, use it as base case, keep d = 0.15 as a labeled stress scenario. Materially moves q, I\*, c_c, and the excess return (−0.1%/yr vs +9.9%/yr in the section 08 example).

4. **State the measure-mixing policy explicitly.** p is risk-neutral (conservative-high), q is real-world (realistic). Defensible, but must be presented once as a deliberate design decision — "conservatism on the entry side, realism on the exit side." Also distinguish σ_IV (enters p, quoted by the market) from σ_RV (governs real dynamics, enters q and p_rw); IV > RV systematically is the strategy's documented edge and deserves its own general-audience discussion. Affects section 05 (flag already placed) and 06.

5. **American vs. European exercise.** Both p and q are terminal (European) probabilities; listed equity options are American. For short puts the approximation is good (early exercise rare, slightly raises effective p). For covered calls on dividend payers it is not negligible: deep-ITM calls are exercised the day before ex-dividend, which shortens holding periods — favorable for the strategy. Also note terminal-vs-path distinction (stock may cross the strike intra-period and come back). A caveat paragraph in sections 05/06 suffices.

6. **Smaller items.**
   - Delta vs. ITM probability: N(−d₁) ≈ 16% vs N(−d₂) ≈ 18% in the running example; section 05 now notes the conflation — keep the distinction consistent everywhere.
   - Exit-timing granularity: exits occur only on the call grid (every n put periods); q_p smoothing is means-exact, dynamics-approximate. Footnoted in section 07.
   - Track C overcharges: cash collateral securing short puts itself earns ~risk-free at the broker; only the stock-inventory component truly forgoes the rate. Flagged in section 08; needs a clean corrected Track C definition.
   - Position sizing: the model sells exactly one put per period regardless of capital. A practitioner-facing subsection on sizing against total capital (and how the capital bound interacts with m) is needed.
   - Premium-example consistency: keep c_p/c_c examples derived from the same Black–Scholes parameters as the probability examples (script enforces c_p ≈ 0.005 for the monthly k=0.95 put; the old draft's c_p = 0.02 belonged to a different implicit horizon).

## Writing / infrastructure

- Prior-work section (`sections/03-prior-work.md`) is a stub; do a real literature pass before assembly (PUT/BXM indices, volatility risk premium, Whaley, Israelov & Nielsen; verify novelty claim for the queueing framing).
- Abstract to be rewritten last.
- LaTeX assembly pipeline (Unicode-math → LaTeX conversion) — decide tooling when sections stabilize.
