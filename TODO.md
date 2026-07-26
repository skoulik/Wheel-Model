# TODO

Open modeling and writing issues, from the 2026-07-10 review of the initial draft. Items are referenced from the sections as "TODO #n".

## Campaign: the restructure (agreed 2026-07-26)

The homogeneous approximation is excised from the article — not flagged, not caveated, deleted.
Sections that derived it or leaned on it are replaced by derivations from the depth process. The
article carries final results only; the road that led to them stays in `drafts/` and this file.

**Agreed structure — four parts, 16 files.**

| part | files |
|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability |
| III. Many assets | 11 portfolio · 12 correlation |
| IV. Reality | 13 verification · 14 live-account · 15 outlook |

**The spine.** A lot's state is its depth x = ln(K_c/S); on the call grid x is a Gaussian random
walk with per-period drift −ν·τ_c; exit is the first grid point with x ≤ 0. Everything follows:
entry law for x₀ → q(x) as the one-step exit probability → grid-sampled first passage for the
holding time → Little's law E[I] = λ·E[T] → the stationary depth census → income and capital as
integrals against that census → stability as conditions on ν.

**Settled decisions.**

1. *One chain in ν.* Every formula is the same formula with a drift argument m; everything
   downstream depends on it only through ν = m − σ²/2. A "measure" is a value of ν:
   Q-world = (r−δ, σ_IV), P-world = (μ−δ, σ_RV). Both are self-consistent worlds and both are
   reported wherever they differ materially; P leads for anything the operator lives through,
   Q for anything the market quotes, r for Track C. Resolves #4's first half by elimination.
2. *Two criteria, not one.* Lot count is stable iff ν > 0; expected capital is stable iff
   m > σ² (a lot's basis relative to current spot is e^x, and E[1/S_t] must decay). At the
   running parameters the verdict flips between measures — the article's sharpest result.
3. *Two regimes, side by side.* Standard p\* = 20% (the prose thread), Conservative p\* = 10%.
   Neither is fitted to the live account, which falls between them.
4. *Three clocks.* Cadence T ≥ tenor τ_p, call τ_c. Little's law wants an arrival rate anyway
   (λ = p/T), so #7 costs one symbol; Parts II–III set T = τ_p, Part IV calibrates it.
5. *Volatility risk premium off by default* (σ_IV = σ_RV): headline results describe the
   inventory machine with the strategy's documented edge stripped out. The break-even IV−RV
   spread is a computed result instead. Skew (put spread > call spread) stays a named limitation.
6. *No strike-down lever* (#10 descoped): K_c frozen at entry. The article's verdict is therefore
   a statement about the mechanical wheel, stated as such.
7. *The d = 0.15 stress case dies* — depth is a process, not a parameter; the stress axis is σ.
8. *Q gives the verification section a theorem*: run at ν_Q with Q-priced premiums, expected
   excess return over r must vanish, up to the dividend-withholding leak (≈ w·δ on the stock
   component) and any Track C overcharge — which measures #6's open accounting question.

**Staging.** (1) analytic core + numbers, reviewed before prose; (2) Part II prose; (3) Part III;
(4) Part IV. Each stage: `verify_examples.py` green, summary, review, then commit.

## Done

- ✅ **Correlated exits vs. the Poisson independence assumption** (was #1; 2026-07-22). Decided by data rather than by framing choice: the layered simulation (section 09, finding five) shows the single-name inventory is nothing like Poisson (Var/Mean ≈ 4.8, P(I=0) ≈ 14% vs Poisson 0.9%), and the section commits to the honest combined framing — on one name only the rate-balance logic survives; the distributional claims (±√I\*, e^(−I\*)) belong to a diversified portfolio of independent wheels. Exit clustering itself proved modest (14% of exit dates); the real single-name tail risk is depth, not batch exits. Residue: section 07's caveat flag gets rewired to sec:layered in the #18 pass; portfolio-level modeling continues as #11.
- ✅ **Dividend carry in the cost of patience** (was #16; 2026-07-22). Quantified end to end (draft findings 9–10): carry is large (a third of income at δ = 2.5%), concentrates on deep lots exactly as conjectured (3.7× the homogeneous prediction — same length-bias factor as inventory), and finances patience only *partially* — excess return declines monotonically in δ under the total-return convention. δ entered the model core (was #2) and the stability boundary ν = μ − δ − σ²/2 (to be written into the stability section under #19). The STRF outlier is no longer a footnote but a *derived* phase: a ~9% yielder has ν < 0, structurally trapped, held for carry. Securities-lending income remains an honesty note for the outlook.
- ✅ **Three smaller items from #6** (2026-07-22 sweep): delta-vs-ITM-probability consistency (section 05 states the distinction; kept consistent since), exit-timing granularity (footnoted in section 07 — and now *quantified*: the call-grid tax of the first-passage analysis is the same effect, promoted from footnote to result), premium-example consistency (enforced by `verify_examples.py` since the script exists).
- ✅ **Dividends in the model** (was #2, parts a–b; 2026-07-22). The article now carries a dividend yield throughout under the total-return convention: μ is total return, the price drifts at μ − δ; d₂, k\*, the partial expectation, E[d|assignment], and q all gained δ (sections 05/06, formulas promoted into `code/verify_examples.py`); dividends on held inventory entered eq:run-rate as p·δ_net·τ_c/q with δ_net = δ(1−w) and w = 15% withholding introduced in section 08; the running example now uses δ = 2.5% (p ≈ 18.5%, q ≈ 0.40/0.147, I\* ≈ 1.40/3.78, excess +10.9%/+1.6%). The δ = 0 anchor is kept as a labeled historical check. Part (c), dividend-driven early exercise, remains under #5. Empirics context preserved: carry ran at ~4% of gross premium; withholding is country-dependent (15% US treaty, 27% Denmark, 6.4% blended observed).
- ✅ **Formula numbering and cross-references** (was #17). Every displayed (non-inline) formula now carries a pandoc-style anchor on its display line (`... {#eq:name}`), and prose references cite the formula directly as a markdown link (`[eq:name](#eq:name)`) instead of pointing at the containing section; at assembly the anchors become numbered `equation` environments and the links become `\eqref` — a literal "(N)". The convention and the anchor registry (15 anchors across sections 04–08) live in `sections/00-notation.md` Conventions.
- ✅ **Symmetry of CC and CSP** (was #14). The introduction now introduces *cash-secured put* and glosses "covered", and a detour presents the payoff diagrams of both legs, states their payoff equivalence at the same strike (put–call parity, Hull pointer), recasts the wheel's two phases as one trade with alternating collateral, and notes the volatility skew as the pricing asymmetry we set aside. See `sections/02-introduction.md`.
- ✅ **Attractive price disclaimer** (was #15). The asset qualifier now reads "fundamentally sound *and* entered at an attractive price" in both places it appears; the definition of "attractive" is explicitly declared out of scope (valuation is the operator's job, the model takes the entry level as given). See `sections/02-introduction.md` and `sections/04-strategy.md`.
- ✅ **d derived, not assumed** (was #3). The recovery section now derives E[d | assignment] = 1 − e^(r·τ_p)·N(−d₁)/N(−d₂) ≈ 7.9% for the running example via the lognormal partial-expectation identity (with a conditional-expectation detour), fixes the article-wide convention — base case d ≈ 0.08, stress case d = 0.15 explicitly labeled as a ~2.5σ event — and sections 07/08 now lead with the base case. The closed form is cross-checked against direct numerical integration in `code/verify_examples.py`; computing under μ instead of r moves the figure by <0.1pp, so the risk-neutral convention is immaterial here. *Empirically confirmed* against the live statements (draft finding #12, `assignment_depth_report` in `code/analyze_statement.py`): implied assignment depths recovered from at-basis call premiums are of order 1% below the strike — matching the formula's prediction for the operator's short-tenor regime — and cleanly reject d = 0.15 as typical (zero implied gaps beyond 10% at σ = 20%).
- ✅ **P&L formula corrected.** The draft's E[Π]/S = c_p(1+p) + p·c_c/q − p(k−1+d) double-counted the put premium (once as income at entry, once as the "recycled capital gain" at exit under the net-basis convention) and booked a mark-to-market drag into Track A. Corrected Track A run rate: **E[Π]/S = c_p + p·c_c/q** per put period. See `sections/08-returns-and-capital.md`, including the "pitfall worth naming" box documenting the error class.

## Open

4. **State the measure-mixing policy explicitly.** p is risk-neutral (conservative-high), q is real-world (realistic). Defensible, but must be presented once as a deliberate design decision — "conservatism on the entry side, realism on the exit side." Also distinguish σ_IV (enters p, quoted by the market) from σ_RV (governs real dynamics, enters q and p_rw); IV > RV systematically is the strategy's documented edge and deserves its own general-audience discussion. Affects section 05 (flag already placed) and 06. Update 2026-07-22: the conservatism margin is now *displayed in data* — the layered simulation's realized assignment rate is exactly p_rw (19.2% vs risk-neutral 20%), quoted in section 09 — and the simulator carries an `iv_spread` hook ready for the IV > RV discussion.

5. **American vs. European exercise.** Both p and q are terminal (European) probabilities; listed equity options are American. For short puts the approximation is good (early exercise rare, slightly raises effective p). For covered calls on dividend payers it is not negligible: deep-ITM calls are exercised the day before ex-dividend, which shortens holding periods — favorable for the strategy. Also note terminal-vs-path distinction (stock may cross the strike intra-period and come back). A caveat paragraph in sections 05/06 suffices.

6. **Smaller items.** (Three resolved sub-items moved to Done, 2026-07-22.)
   - Track C overcharges: cash collateral securing short puts itself earns ~risk-free at the broker; only the stock-inventory component truly forgoes the rate. Flagged in section 08; needs a clean corrected Track C definition. Now *more* material, not less: the layered capital numbers (7.7·S₀) make the put-margin share small, so the correction mostly concerns whether idle cash between assignments is charged.
   - Position sizing: the model sells exactly one put per period regardless of capital. A practitioner-facing subsection on sizing against total capital is needed — and the layered results sharpen it: capital demand is bursty and heavy-tailed (Var/Mean ≈ 5), so sizing against *mean* capital is exactly the mistake the homogeneous model invites.

## From comparison with live trading records (2026-07-10)

Source: `drafts/2026-07-10-statement-vs-model-observations.md`, an analysis of a year of real wheel operation against the tier-1 model. The queue architecture matched practice well; the following did not.

7. **Duty cycle: split cadence from tenor.** The model assumes one put always running (period = option lifetime τ_p). In practice the operator sells short-tenor options on a longer cadence (e.g., a 3-day put sold weekly), so the stock is covered by a live put only ~40–50% of calendar time. Introduce cadence period T and tenor τ_p ≤ T; premium accrues per T but prices off τ_p; annualizations change by τ_p/T. The current model is the special case τ_p = T. Biggest structural miss found. Update 2026-07-22: `wheel_sim.py` supports T ≥ τ_p already; what remains is the article-side treatment, paired with #8.

8. **Realistic base-case parameters.** Observed assignment rates run ~8–9% per put, not the article's ~18% running example; observed recycling (for lots that recycle) is ~16%/month, not the stress example's 16%/quarter. Re-run the economics with a low-p\* regime (p\* ≈ 5–10%, weekly cadence, monthly-ish calls), keeping p\* = 20% as the aggressive variant. The companion change — derived d, not d = 0.15, as base — is done (was #3, see Done list) and directly validated by the statement data in exactly this low-p\* regime (draft finding #12). Plan update 2026-07-22: lands as a "realistic regime" subsection of the rewritten stability section (#19 campaign) using #7's cadence split; the running example keeps p\* = 20% for continuity of the pedagogical thread.

9. **Censoring-aware calibration; three holding-time regimes.** Completed lots recycle fast (median ~1 month), but the extended 14-month window resolves the tail into three empirical regimes: a *fast lane* (exit at entry strike within ~a month), a *metastable* class (resolves at entry strike after months of limbo), and a *trapped* class (ages past 200+ days). Trapped layers are not abandoned or force-exited: they are held while fresh layers cycle beneath them, so strata resolve bottom-up — exactly the qualitative behavior depth-dependent q_i predicts; genuine below-basis exits are rare (2 of 41 completed lots). Statistics on completed lots alone wildly overstate the exit rate (survivorship/right-censoring); calibration needs survival analysis. The modeling half of this item is *decided* (2026-07-22, draft findings 3/10): the mixture **emerges from** depth dependence plus the common path — no mixture parameterization needed, a single q(x) generates all three regimes. What remains is the empirical half: fit the first-passage model (entry law, ν, σ, call grid) to the live statements' holding-time data with censoring-aware survival methods, and see whether the observed fast/metastable/trapped proportions match the model's or demand depth-dependent μ(x).

10. **Call strike K_c as a policy variable.** The model fixes K_c at the entry strike; in practice the operator moves the call strike down to exit stuck lots (buying q at a realized-loss cost) or up in recoveries (extra gain, lower q). "Call strike vs. basis" is the operator's main tool against dead strata and the natural control knob of the tier-2 phase diagram. Empirically the lever is used asymmetrically — strikes move up freely, down only rarely — which poses a genuinely interesting model question: is that reluctance optimal (the option value of waiting for recovery), or loss-aversion the model should advise against? Priority upgrade 2026-07-22: the layered results make this the single most consequential open item — without the strike-down lever the base-case excess return is ≈ 0, so this policy *is* where the strategy's edge lives or dies. And the question is now tractable: the first-passage machinery prices the wait (expected time and carry at depth x vs. the realized loss of striking down), so "optimal reluctance" is a computable threshold, not a philosophical stance.

11. **Common-shock arrivals.** Assignments across a portfolio of wheels cluster on market-wide drawdown dates. Exits diversify across names; arrivals do not. A portfolio-level model needs a systematic component in p — bursts arrive exactly when capital is scarcest (direct evidence for section 09's reflexivity).

12. **Transaction-cost haircut as a function of tenor.** Commissions eat a few percent of premium on short-tenor cheap options (vs. negligible on monthly). Without a friction term the model has no reason not to prefer ever-shorter tenors; the haircut belongs in any τ_p/T optimization.

13. **Permanent-impairment hazard.** "Fundamentally sound" fails occasionally in real portfolios (bankruptcies, permanent collapses): the lot enters an absorbing state with q = 0, premium ≈ 0, capital loss ≈ 100%. Even a small per-year hazard adds an expected cost that can rival annual premium income. Model it as an explicit per-lot death hazard in tier 2, not a verbal disclaimer.

## From the layered simulation (2026-07-22)

Source: `drafts/2026-07-22-layered-simulation-findings.md`, first results from `code/wheel_sim.py` — the article's exact mechanics on a common GBM path with per-lot frozen strikes (no homogeneous-q approximation). Validation: assignment rate, E[d], and depth-binned exit rates all match the formulas; the deviations below are emergent, not bugs.

18. **The homogeneous base case understates inventory ~3.5× and its excess return is an artifact.** At the article's running parameters (δ = 2.5% since the retrofit), simulated mean inventory is 4.7 lots vs I\* ≈ 1.3, capital 7.7·S₀ vs 1.5·S₀, collapsing the base-case excess return from +10.9%/yr to −0.9%. Track A income survives. Progress 2026-07-22: **section 09 (sec:layered) now presents all of this in the article**; what remains of this item is the rewiring pass — turn the temporary flags in 07/08 into forward references to sec:layered, update section 02's contributions list, sweep remaining tier vocabulary from 06/08/11/12, remove this item's in-text flags, and update CLAUDE.md (tier language is internal-only; refresh the anchor example and central-result line).

19. **First-passage core: Little's law + grid-sampled passage times.** A lot's depth x = ln(K_c/S) is ABM with drift −ν (ν = μ − δ − σ²/2), sampled on the call grid; exit = first grid point with x ≤ 0; E[I] = arrival rate × E[holding time] (Little); depth-dependent q_i is a derived object, not the primitive. *Analytics built and validated* (draft finding 10, `code/first_passage.py`): integral-equation solver cross-checked against the wheel MC (3 decimals) and a pure-walk MC (4 decimals); Siegmund closed form within ~10% with the call-grid-tax decomposition; stationary I\* = 9.1 at the running parameters; E[I(t)] takes 88y to reach 90% of stationary, so the transient integral is the operator-relevant number; stability condition ν > 0 (at μ = 7%: unstable in calm markets at σ = 40%, or at σ = 20% with δ = 5%), replacing the old "always stable whenever q > 0"; trapped-forever fraction ≈ 2.2% per assignment at σ = 40%. *Section 09 (sec:layered) is written.* Remaining writing: section 10 ({#sec:first-passage}) with the Little's-law and first-passage detours (Ross pointer for both); section 11 rewrite (stability absorbed from the old section: ν-criterion, phase picture with δ as an axis, crash-then-flatline ratchet, trapped fraction, corrected economics, #8's realistic-regime subsection); `verify_examples.py` extended with the quoted first-passage numbers.

## Writing / infrastructure

- Prior-work section (`sections/03-prior-work.md`) is a stub; do a real literature pass before assembly (PUT/BXM indices, volatility risk premium, Whaley, Israelov & Nielsen; verify novelty claim for the queueing framing).
- Abstract to be rewritten last.
- LaTeX assembly pipeline (Unicode-math → LaTeX conversion) — decide tooling when sections stabilize.
- Figures: the ASCII payoff diagrams in the section 02 detour are placeholders — redraw as proper vector figures (TikZ or similar) at assembly time.
