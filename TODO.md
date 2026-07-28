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

**Progress.** Stage 1 done (commit "Stage 1: the analytic core, one chain in nu"). Stage 2 done:
sections 00, 04, 05–10 written, 02 contributions rewritten, 01/15 reduced to honest stubs, the
superseded 06/07/09 deleted. Stage 3 (portfolio, correlation) and Stage 4 (verification,
live account, outlook) remain, along with the code cleanup they carry: retire `first_passage.py`
and `legacy_homogeneous.py`, and delete `homogeneous_predictions`/`check_quoted` from the
simulator when the verification section replaces what they were checking.

## Done

- ✅ **The scripts are fast now** (2026-07-27). `verify_examples.py` went from **434 s to 3.3 s** (`--full`: ~12 min to 4.3 s), `model.py` from 9.3 s to 6.3 s, and `wheel_sim.py --scenario sweep` from 50.9 s to 12.0 s. Two changes, in that order of importance. **(1) The convolution.** `DepthWalk.step()` — a 400-cell density against a 69-point kernel, run for up to 8000 periods — was the runtime of everything, and it is one `numpy.convolve` call. `model.py` now uses numpy when it is importable and falls back to the original Python loop when it is not, so the stdlib-only guarantee survives as a real, tested path rather than a claim: a new structural check in `verify_examples.py` runs both and asserts they agree (they match to 1e-16, and no article number moved by so much as a last digit). That alone was **114x** on a single `occupation()` call. **(2) The sweeps**, as planned below: `model.pmap()` is a thin `ProcessPoolExecutor` wrapper, and the volatility-risk-premium, dividend, sticky-dividend, census, base-walk and stationary batches in `verify_examples.py`, both grid checks in `model.py`, and the dividend sweep in `wheel_sim.py` now go through it. `WHEEL_WORKERS=1` forces the serial path; parallel and serial output was diffed byte-for-byte on every script. Worth recording that the *second* change is the one the original note predicted and it turned out to be the smaller of the two (~1.5x, once numpy had removed the work it was distributing) — Amdahl, not a surprise, but the note assumed the convolution was untouchable and it was not. **GPU was evaluated and rejected**: torch with CUDA is installed here, but the walk is 8000 *sequential* 400-element steps, so it is launch-latency bound, and numpy already runs it in 0.2 s. Not practical, and it would have cost the stdlib fallback. The remaining runtime is Monte Carlo (`wheel_sim.py`), which is a different job: `simulate()` is embarrassingly parallel over paths, but splitting it means merging `Agg` and re-thinking seeding, so it was left alone.
- ✅ **Stationary figures were grid-biased; fixed by extrapolation** (2026-07-26). Found while moving the working example to a weekly cadence. `occupation()` puts the absorbing boundary on cell centres, so the first live cell sits at h/2 instead of 0+ and lots are held marginally too long. The bias is O(h²) and positive, and it accumulates over the whole heavy tail, so it hit only the *stationary* figures — the finite-horizon numbers, which is most of the article, were never affected. At the far grid the article had been using (h = 0.05) it inflated the mean holding time by **5% at the old monthly cadence and 23% at the weekly one**. Under the old parameters the published 4.18 y / 10.04 lots / 94 y should have read **3.98 / 9.54 / 92**. Fixed by `model.stationary()`, which Richardson-extrapolates two grids; three-point refinement confirms the O(h²) order at both cadences, and `code/mc_holding.py` — a grid-free Monte Carlo of the same walk, new in this change — agrees within its sampling error. Also raised the near-grid default from h = 0.02 to h = 0.01, since the resolution that matters is h relative to one period's step σ·√τ_c, which the shorter call period cut by half.
- ✅ **The homogeneous approximation, excised** (was #18; 2026-07-26). Not flagged or caveated — deleted. Sections 06/07/09 of the old numbering are gone; the depth process, first passage, Little's law and the depth census replace them. Every number the article quotes was regenerated from `code/model.py` and is checked by `verify_examples.py`.
- ✅ **First-passage core** (was #19; 2026-07-26). Built, validated and written: entry law → grid-sampled first passage → Little's law → census → economics → two stability criteria. Validated three ways — a no-arbitrage identity that holds to 5bp, agreement with the wheel simulator component by component, and grid-refinement checks. The results that came out of it: mean holding time 4.2y against a 6-month median; the call-grid tax exceeding the entry overshoot by 1.8×; a 94-year approach to equilibrium; and the finding that at fair option prices the wheel is economically indistinguishable from owning the stock.
- ✅ **The measure policy, resolved by elimination** (was #4, first half; 2026-07-26). There is one chain of formulas parameterized by the price drift m, and a "measure" is a value of m. Prices are never computed from either world — they are quotes, market data. What remains of #4 is the volatility skew (see the narrowed item below).
- ✅ **American vs. European exercise** (was #5; 2026-07-26). Caveat paragraph written at the end of [the entry section](#sec:entry): early put exercise is rare and raises effective assignment slightly; dividend-driven early call exercise shortens holding periods and therefore helps, so omitting it is conservative; the terminal-vs-path distinction is promoted from caveat to result as the call-grid tax of [eq:siegmund](#eq:siegmund).
- ✅ **Correlated exits vs. the Poisson independence assumption** (was #1; 2026-07-22). Decided by data rather than by framing choice: the layered simulation (section 09, finding five) shows the single-name inventory is nothing like Poisson (Var/Mean ≈ 4.8, P(I=0) ≈ 14% vs Poisson 0.9%), and the section commits to the honest combined framing — on one name only the rate-balance logic survives; the distributional claims (±√I\*, e^(−I\*)) belong to a diversified portfolio of independent wheels. Exit clustering itself proved modest (14% of exit dates); the real single-name tail risk is depth, not batch exits. Residue: section 07's caveat flag gets rewired to sec:layered in the #18 pass; portfolio-level modeling continues as #11.
- ✅ **Dividend carry in the cost of patience** (was #16; 2026-07-22). Quantified end to end (draft findings 9–10): carry is large (a third of income at δ = 2.5%), concentrates on deep lots exactly as conjectured (3.7× the homogeneous prediction — same length-bias factor as inventory), and finances patience only *partially* — excess return declines monotonically in δ under the total-return convention. δ entered the model core (was #2) and the stability boundary ν = μ − δ − σ²/2 (to be written into the stability section under #19). The STRF outlier is no longer a footnote but a *derived* phase: a ~9% yielder has ν < 0, structurally trapped, held for carry. Securities-lending income remains an honesty note for the outlook.
- ✅ **Three smaller items from #6** (2026-07-22 sweep): delta-vs-ITM-probability consistency (section 05 states the distinction; kept consistent since), exit-timing granularity (footnoted in section 07 — and now *quantified*: the call-grid tax of the first-passage analysis is the same effect, promoted from footnote to result), premium-example consistency (enforced by `verify_examples.py` since the script exists).
- ✅ **Dividends in the model** (was #2, parts a–b; 2026-07-22). The article now carries a dividend yield throughout under the total-return convention: μ is total return, the price drifts at μ − δ; d₂, k\*, the partial expectation, E[d|assignment], and q all gained δ (sections 05/06, formulas promoted into `code/verify_examples.py`); dividends on held inventory entered eq:run-rate as p·δ_net·τ_c/q with δ_net = δ(1−w) and w = 15% withholding introduced in section 08; the running example now uses δ = 2.5% (p ≈ 18.5%, q ≈ 0.40/0.147, I\* ≈ 1.40/3.78, excess +10.9%/+1.6%). The δ = 0 anchor is kept as a labeled historical check. Part (c), dividend-driven early exercise, remains under #5. Empirics context preserved: carry ran at ~4% of gross premium; withholding is country-dependent (15% US treaty, 27% Denmark, 6.4% blended observed).
- ✅ **Formula numbering and cross-references** (was #17). Every displayed (non-inline) formula now carries a pandoc-style anchor on its display line (`... {#eq:name}`), and prose references cite the formula directly as a markdown link (`[eq:name](#eq:name)`) instead of pointing at the containing section; at assembly the anchors become numbered `equation` environments and the links become `\eqref` — a literal "(N)". The convention and the anchor registry (15 anchors across sections 04–08) live in `sections/00-notation.md` Conventions.
- ✅ **Symmetry of CC and CSP** (was #14). The introduction now introduces *cash-secured put* and glosses "covered", and a detour presents the payoff diagrams of both legs, states their payoff equivalence at the same strike (put–call parity, Hull pointer), recasts the wheel's two phases as one trade with alternating collateral, and notes the volatility skew as the pricing asymmetry we set aside. See `sections/02-introduction.md`.
- ✅ **Attractive price disclaimer** (was #15). The asset qualifier now reads "fundamentally sound *and* entered at an attractive price" in both places it appears; the definition of "attractive" is explicitly declared out of scope (valuation is the operator's job, the model takes the entry level as given). See `sections/02-introduction.md` and `sections/04-strategy.md`.
- ✅ **d derived, not assumed** (was #3). The recovery section now derives E[d | assignment] = 1 − e^(r·τ_p)·N(−d₁)/N(−d₂) ≈ 7.9% for the running example via the lognormal partial-expectation identity (with a conditional-expectation detour), fixes the article-wide convention — base case d ≈ 0.08, stress case d = 0.15 explicitly labeled as a ~2.5σ event — and sections 07/08 now lead with the base case. The closed form is cross-checked against direct numerical integration in `code/verify_examples.py`; computing under μ instead of r moves the figure by <0.1pp, so the risk-neutral convention is immaterial here. *Empirically confirmed* against the live statements (draft finding #12, `assignment_depth_report` in `code/analyze_statement.py`): implied assignment depths recovered from at-basis call premiums are of order 1% below the strike — matching the formula's prediction for the operator's short-tenor regime — and cleanly reject d = 0.15 as typical (zero implied gaps beyond 10% at σ = 20%).
- ✅ **P&L formula corrected.** The draft's E[Π]/S = c_p(1+p) + p·c_c/q − p(k−1+d) double-counted the put premium (once as income at entry, once as the "recycled capital gain" at exit under the net-basis convention) and booked a mark-to-market drag into Track A. Corrected Track A run rate: **E[Π]/S = c_p + p·c_c/q** per put period. See `sections/08-returns-and-capital.md`, including the "pitfall worth naming" box documenting the error class.

## Part IV, from the live-account measurement (2026-07-27)

Source: `drafts/2026-07-27-discrepancy-catalogue.md`, and the four scripts behind
it — `prices.py`, `live_ledger.py`, `model_vs_live.py`, `iv_panel.py`,
`selection_fit.py`. Parts I and II now carry brief supporting references to this
work; the material itself belongs here. **Everything below is measured**, so
these are writing tasks, not modelling ones.

20. **§14 the live account** ({#sec:live}) — the ledger and its verdict. Track A
    on cost basis +37.97%/yr against Track B +19.52%; same-names buy-and-hold
    +24.29%; option-overlay excess **−4.77%/yr**; selection **+25.01%/yr**,
    exposure-matched. Lead with the ledger gap, not the return.

    **This section owes the reader the intervals, and it is the only section
    that does.** Parts I and II assert three times that the overlay "earned
    nothing distinguishable from zero" (`02-introduction`, `04-strategy`,
    `09-returns`) without a number anywhere behind it — that is deliberate, the
    statistics belong to the reality-check sections, but it means §14 must
    actually deliver them or the claim is unsupported in the whole article.
    Required here: the point estimate, the 90% resampling interval **−20.0% to
    +7.4%** clustered by name (quote the clustered one; −26.0% to +14.1% by lot
    is the looser alternative), P(excess < 0) = 70%, and the sample it rests on.
    A reader meeting only "earned nothing" would not guess the point estimate is
    negative and the interval twenty points wide. `live_ledger.py --bootstrap`
    produces all of it.

    The **UNH lot is the worked example** and was deliberately kept out of Part
    II so it lands here: assigned at 260, a four-week call written at the same
    260 basis for $18.10, called away at 260 with the stock at 393.85 —
    collected $1,810, surrendered $13,385. It is also, on its own, the
    difference between a negative and a positive overlay excess (−4.77% →
    +2.08%) *and* 51% of the selection gap — the same position carrying both
    verdicts, which is the point rather than a caveat: a lot that runs far
    enough to dominate selection is a lot whose call gave the run away. Do not
    present it as an outlier to be set aside.

    Include the by-leg decomposition — **put leg keeps 20.6% of premium, call
    leg −32.9%**, frictions −$5,054 — which is where the restatement bites: the
    old near-symmetry between the legs was cheap calls on falling names, and on
    the universe the strategy actually claims the call leg gives back a third of
    its own premium. And the regime caveat: the universe rose over the window
    and a covered-call overlay *must* lag in a strong up-market.

21. **§13 verification** ({#sec:verification}) — the spine tested against live
    data, not only simulation. Entry law: 71.6 assignments expected, 72 finished
    below the strike, 71 assigned, over 920 contracts. Depth census: mean depth
    0.151 model against 0.145 live over 3,870 lot-days — and notably the model
    fits at the article's μ = 7% (0.151) far better than at the window's realised
    drift (0.101), which is worth its own paragraph. q(x): 26.1% of calls
    expected exercised against 19.7%, monotone in depth. Survival: model exits
    faster than observed, the compounding of that per-period gap. Also carries
    the grid-free Monte Carlo check and the Q-world no-arbitrage identity.

    **Claim only the aggregates.** The restatement withdrew two bin-level
    results: T1's calibration curve is sensitive to whether entry is priced at
    the session open or close (top bucket 27.4% predicted vs 8.0% realised at the
    open, 25.9% vs 24.3% at the close), and q(x)'s two deepest bins now hold 70
    and 20 contracts. The aggregate statements are what the sample carries.

    Three measurement traps are worth a paragraph because all three were fallen
    into: reading depth on the day before exit discards nearly every exit;
    sampling lots on a synthetic τ_c grid scores periods at tenors never traded;
    and pricing an entry at the day's close when the operator writes in the first
    hour builds a look-ahead into every measured entry depth.

22. **Selection as a model extension** — the honest form of TODO #14. The
    pre-registered rule (`drafts/2026-07-27-selection-rule-preregistration.md`)
    is fitted: rules 4 and 6 (fallen angels, oversold) confirmed at z ≈ −10 with
    a permutation check agreeing, rule 5 (avoid falling knives) **rejected** in
    both its simple and its interaction form. If this becomes a modelled
    mechanism rather than a reported measurement, the minimal form is a
    state-dependent thinning of the arrival process. **Note what it commits to**:
    under GBM entry timing cannot generate return by construction, so modelling
    selection as profitable is a claim of mean reversion and must be argued as
    one. 20 lots in one bull market cannot support it. Rule 5's partial rescue
    ("prefers the ones that have started to come back") was **withdrawn** on the
    restated choice set — see Appendix A of the selection-rule pre-registration —
    so the rule is rejected without qualification.

23. **σ_IV, if it is ever carried properly** (supersedes the modelling half of
    #4). Measured: the put leg's spread over realized volatility runs ~2× the
    call leg's, and the within-name depth slope is ≈ +20% relative IV from
    shallow to deep (the apparent doubling is mostly name selection). [The
    returns section](#sec:returns) now names both as deliberate simplifications
    and states the sign of the bias. Splitting `Config.iv_spread` into put and
    call legs is small; a strike- and depth-dependent surface is a
    renumber-every-figure job through Parts II–III and was judged not worth it.

24. **Part III inputs from the live book.** The live account's put book spans 129
    names while inventory sits on 29, so put margin is ~25% of Track B capital
    against the single-name model's 1.6%: premium is generated across a far
    wider book than the inventory it creates. That is a portfolio fact, and
    [the portfolio section](#sec:portfolio) is where sizing against bursty,
    heavy-tailed capital demand belongs (see #6). Assignment clustering on
    market-wide drawdown dates (#11) is measured and waiting there too.

25. **Impairment gets its first data point** (feeds #13). Two in-window entries
    into names since judged un-wheelable (ALT, BEKE) across ~45 names over 1.17
    years. Thin, but it is an observed hazard rate rather than a free parameter,
    and it pairs with the x\* boundary already derived under #13.

## Open

4. **Volatility skew** (all that remains of the old #4). *Modelling half
   superseded by #23; what remains here is the article-side decision, now taken:
   [the returns section](#sec:returns) names the omission and its cost.* The article carries one implied volatility σ_IV and one spread over realized. Skew means the puts sold are systematically richer than the calls sold, so the edge concentrates in the put leg and in shallow lots — which matters more since the 2026-07-26 recompute, not less: at the weekly cadence the break-even spread computed in [the returns section](#sec:returns) is essentially **zero**, so the whole of the edge is the spread and *where* the spread sits decides who earns it. `model.Config` carries `iv_spread` as a single scalar; splitting it into put and call legs is a small change, and the honest version would also make the spread strike-dependent.

6. **Smaller items.** (Three resolved sub-items moved to Done, 2026-07-22.)
   - Track C on put collateral: cash securing a short put earns ~risk-free at the broker, so charging r against it may overcharge. Now *measured* rather than argued — the Q-world identity puts it at 15–19bp/yr, since market-value capital is dominated by the shares (5.08 against 0.19 of margin). Small enough to state as a footnote in [the returns section](#sec:returns) rather than restructure Track C for; decide when Part IV lands.
   - Position sizing: the model sells exactly one put per period regardless of capital. A practitioner-facing subsection on sizing against total capital is needed, and [the portfolio section](#sec:portfolio) is where it belongs: capital demand is bursty and heavy-tailed, so sizing against *mean* capital is precisely the mistake to warn against.

## From comparison with live trading records (2026-07-10)

Source: `drafts/2026-07-10-statement-vs-model-observations.md`, an analysis of a year of real wheel operation against the tier-1 model. The queue architecture matched practice well; the following did not.

7. **Duty cycle: split cadence from tenor.** *Demoted 2026-07-26 — the gap that motivated this item was a reporting artifact, not a real duty cycle.* The model assumes one put always running (period = option lifetime τ_p), and the source draft recorded a "3-day put sold weekly", covered only ~40–50% of calendar time, as the biggest structural miss found. Wrong: the statement's Date column is the **cash posting date**, not the trade date, and every date in it runs one day late (options settle T+1; expiry/assignment processing posts the calendar day after expiry). Evidence: 526 of 530 expiry rows are dated exactly one day after the contract's expiry, 55 assignment stock rows are dated *Saturday*, and 7 put opens are dated Saturday — impossible as trade dates. Corrected, the dominant put is sold **Monday at the open for Friday's close**: 4 calendar days, live 5 of the week's 7 days, and essentially continuous in trading time. The recorded "3-day" tenor was Tuesday-posted minus Friday-expiry. So T and τ_p do come apart, but only across the weekend, when nothing trades — τ_p = T is a good approximation, not a concession. The mechanism stays in the model (premium accrues per T, prices off τ_p, annualizations carry τ_p/T; `wheel_sim.py` supports T ≥ τ_p), and the article-side treatment for the live-account section is now a minor calibration point rather than a structural repair. `code/analyze_statement.py` shifts every date back to its event date as of this fix; the numbers in the source draft's findings #1–#3 are one day short throughout and should be re-derived from the script, not quoted from the draft.

8. **Realistic base-case parameters.** Observed assignment rates run ~8–9% per put, not the article's ~18% running example; observed recycling (for lots that recycle) is ~16%/month, not the stress example's 16%/quarter. Re-run the economics with a low-p\* regime (p\* ≈ 5–10%, weekly cadence, monthly-ish calls), keeping p\* = 20% as the aggressive variant. The companion change — derived d, not d = 0.15, as base — is done (was #3, see Done list) and directly validated by the statement data in exactly this low-p\* regime (draft finding #12). Plan update 2026-07-22: lands as a "realistic regime" subsection of the rewritten stability section (#19 campaign) using #7's cadence split; the running example keeps p\* = 20% for continuity of the pedagogical thread. **Half-done 2026-07-26**: the clocks are now the live account's — a put every week, calls for four weeks (n = 4) — throughout Parts II and III, and every quoted number was regenerated. What remains is only the strike dial. At the weekly cadence the *existing* Conservative regime (p\* = 10%, λ = 5.2 lots/yr) already sits on the observed 8.7% per-put assignment rate, so the realistic case is in the article already; the open decision is whether to promote it to the lead, which is a prose choice, not a modelling one. Note that neither regime reproduces the observed *arrival* rate — that gap is #14, and it is not p\*'s to close.

9. **Censoring-aware calibration; three holding-time regimes.** Completed lots recycle fast (median ~1 month), but the extended 14-month window resolves the tail into three empirical regimes: a *fast lane* (exit at entry strike within ~a month), a *metastable* class (resolves at entry strike after months of limbo), and a *trapped* class (ages past 200+ days). Trapped layers are not abandoned or force-exited: they are held while fresh layers cycle beneath them, so strata resolve bottom-up — exactly the qualitative behavior depth-dependent q_i predicts; genuine below-basis exits are rare (2 of 41 completed lots). Statistics on completed lots alone wildly overstate the exit rate (survivorship/right-censoring); calibration needs survival analysis. The modeling half of this item is *decided* (2026-07-22, draft findings 3/10): the mixture **emerges from** depth dependence plus the common path — no mixture parameterization needed, a single q(x) generates all three regimes. What remains is the empirical half: fit the first-passage model (entry law, ν, σ, call grid) to the live statements' holding-time data with censoring-aware survival methods, and see whether the observed fast/metastable/trapped proportions match the model's or demand depth-dependent μ(x).

10. **DESCOPED (2026-07-26).** Call strike K_c as a policy variable — deliberately outside the model, by decision, not oversight. K_c stays frozen at entry, [the strategy section](#sec:strategy) says so explicitly, and the article's verdict is therefore about the *mechanical* wheel. Recorded in [the outlook](#sec:outlook) as the most consequential thing the model does not do. The original entry, kept because the reasoning still stands if it is ever revisited: The model fixes K_c at the entry strike; in practice the operator moves the call strike down to exit stuck lots (buying q at a realized-loss cost) or up in recoveries (extra gain, lower q). "Call strike vs. basis" is the operator's main tool against dead strata and the natural control knob of the tier-2 phase diagram. Empirically the lever is used asymmetrically — strikes move up freely, down only rarely — which poses a genuinely interesting model question: is that reluctance optimal (the option value of waiting for recovery), or loss-aversion the model should advise against? Priority upgrade 2026-07-22: the layered results make this the single most consequential open item — without the strike-down lever the base-case excess return is ≈ 0, so this policy *is* where the strategy's edge lives or dies. And the question is now tractable: the first-passage machinery prices the wait (expected time and carry at depth x vs. the realized loss of striking down), so "optimal reluctance" is a computable threshold, not a philosophical stance.

11. **Common-shock arrivals.** Assignments across a portfolio of wheels cluster on market-wide drawdown dates. Exits diversify across names; arrivals do not. A portfolio-level model needs a systematic component in p — bursts arrive exactly when capital is scarcest (direct evidence for section 09's reflexivity).

12. **Transaction-cost haircut as a function of tenor.** Commissions eat a few percent of premium on short-tenor cheap options (vs. negligible on monthly). Without a friction term the model has no reason not to prefer ever-shorter tenors; the haircut belongs in any τ_p/T optimization.

13. **Permanent-impairment hazard.** "Fundamentally sound" fails occasionally in real portfolios (bankruptcies, permanent collapses): the lot enters an absorbing state with q = 0, premium ≈ 0, capital loss ≈ 100%. Even a small per-year hazard adds an expected cost that can rival annual premium income. Model it as an explicit per-lot death hazard in tier 2, not a verbal disclaimer.

    **Now has a derived entry point** (2026-07-26, from the dividend-stickiness review). The article's asset is a dividend aristocrat — a payout that rises and never falls — and [the strategy section](#sec:strategy) now says so explicitly, because that clause is what licenses a constant δ. Push the clause to its limit and it names its own failure boundary. With the payout frozen in dollars and the total return held fixed, a lot at depth x faces a yield of δ·e^x on the market value of its shares, so the drag grows with depth and

        nu(x)  =  nu − δ·(e^x − 1),      zero at   x\* = ln(1 + nu/δ)

    changing sign at x\* and growing more negative beyond it — a runaway region, not a slow one, and the same object as the Gordon-model price at which a fixed payout stops being payable. At the running parameters x\* = 0.693 (**50% below the strike**), with 16% of the thirty-year census already past it; under the pricing drift x\* = 0.182 (**17% below**), with 69% of the census beyond. So the never-cut assumption is not merely optimistic in the deep tail, it is *inconsistent with option prices* there, and the impairment hazard is the mechanism that resolves the contradiction. `model.sticky_dividend_trap()` computes the boundary; `model.sticky_dividend_yield()` computes the bounded version of the correction that the article does adopt (four basis points at thirty years, see [the returns section](#sec:returns)). Two consequences for whoever picks this up: the hazard is naturally *depth-dependent* rather than a flat per-lot rate, and x\* gives it a scale to be calibrated against instead of a free parameter.

    **The empirical handle is gone** (2026-07-27, with the universe restatement). The live account's only two entries into names it would later disown, ALT and BEKE, were the sole observations of this hazard; both are now out of universe, and rightly so — neither is a name the strategy would knowingly enter, so a rate estimated from them would describe a universe the article does not claim. The consequence is that **the impairment channel is untested and no rate can be quoted**, and the out-of-sample pre-registration's P12 has been retired rather than passed. Calibrating this needs an in-universe name that falls and stays down, which is a slower experiment than the rest of Part IV. Until then x\* above is the only scale available, and it is theoretical.

    Rejected along the way, recorded so it is not re-invented: crediting a lot's dividend income by its own realized depth (income ∝ δ·e^x per lot). It is internally inconsistent — all shares of one company pay the same cash on the same day, so identical shares would receive different dividends — and the tell is that E[e^x] over the census *is* the cost-basis capital, so the correction is worth +1.22pp of pure unfunded return at 30y and breaks the no-arbitrage identity immediately. Any dividend correction must move the drift and the income together.

14. **RESOLVED as a measurement (2026-07-27), see #22 for what remains.** The
    missing mechanism was correctly identified below as "attractive price"
    selection, and it is now quantified rather than conjectured: exposure-matched,
    it contributed **+25.01%/yr** (restated 2026-07-27 from +10.59%, the change
    being almost entirely STRF and KWEB leaving the universe) against the option
    overlay's zero, and the stated rule behind it has been fitted and partly
    rejected. The original entry follows, since its reasoning about why p\* cannot
    absorb the gap still stands — with its arrival figures restated as **18.1
    puts per name-year** while in rotation and **1.41 lots per name-year** (was
    ~19.6 and 1.70), the modal gap still exactly 7 days.

    **The operator skips weeks, and that is the entry discipline, not a defect.** Measured 2026-07-26 when the working example moved to a weekly cadence: per name the median gap between consecutive put opens is exactly 7 days (248 of 610 gaps), so the weekly cadence is genuinely per-name and not a portfolio aggregate — but the *mean* gap is far longer, ~19.6 puts per name-year against the 52 an unconditional weekly cadence would sell, with a long tail of 14/21/28/60-day gaps. Consequently observed arrivals are 1.70 lots per name-year while the model at T = 1 week, p\* = 20% predicts 10.4 (p\* = 10%: 5.2). The gap is *not* p\*'s to absorb: the operator's strikes sit at ≈8.7% assignment probability per put, which is what p\* is defined to measure, and bending p\* down to ≈3.3% to match arrivals would put the model's strikes far outside the real ones and wreck premium and entry depth together. The missing mechanism is the **"attractive price" selection** of [the strategy section](#sec:strategy) — the operator sells a put only when the price is worth entering at, and the model's step 1, which never waits, has no such filter. Deliberately out of scope (valuation is the operator's discipline, and the article says so), but recorded here because it is the single largest unexplained ratio between the model and the statements, and calibrating arrival rates against live data will keep hitting it. If it ever must be modelled, the natural minimal form is a state-dependent thinning of the arrival process rather than a change to the strike dial.

## From the layered simulation (2026-07-22)

Source: `drafts/2026-07-22-layered-simulation-findings.md`, first results from `code/wheel_sim.py` — the article's exact mechanics on a common GBM path with per-lot frozen strikes (no homogeneous-q approximation). Validation: assignment rate, E[d], and depth-binned exit rates all match the formulas; the deviations below are emergent, not bugs.

18. **The homogeneous base case understates inventory ~3.5× and its excess return is an artifact.** At the article's running parameters (δ = 2.5% since the retrofit), simulated mean inventory is 4.7 lots vs I\* ≈ 1.3, capital 7.7·S₀ vs 1.5·S₀, collapsing the base-case excess return from +10.9%/yr to −0.9%. Track A income survives. Progress 2026-07-22: **section 09 (sec:layered) now presents all of this in the article**; what remains of this item is the rewiring pass — turn the temporary flags in 07/08 into forward references to sec:layered, update section 02's contributions list, sweep remaining tier vocabulary from 06/08/11/12, remove this item's in-text flags, and update CLAUDE.md (tier language is internal-only; refresh the anchor example and central-result line).

19. **First-passage core: Little's law + grid-sampled passage times.** A lot's depth x = ln(K_c/S) is ABM with drift −ν (ν = μ − δ − σ²/2), sampled on the call grid; exit = first grid point with x ≤ 0; E[I] = arrival rate × E[holding time] (Little); depth-dependent q_i is a derived object, not the primitive. *Analytics built and validated* (draft finding 10, `code/first_passage.py`): integral-equation solver cross-checked against the wheel MC (3 decimals) and a pure-walk MC (4 decimals); Siegmund closed form within ~10% with the call-grid-tax decomposition; stationary I\* = 9.1 at the running parameters; E[I(t)] takes 88y to reach 90% of stationary, so the transient integral is the operator-relevant number; stability condition ν > 0 (at μ = 7%: unstable in calm markets at σ = 40%, or at σ = 20% with δ = 5%), replacing the old "always stable whenever q > 0"; trapped-forever fraction ≈ 2.2% per assignment at σ = 40%. *Section 09 (sec:layered) is written.* Remaining writing: section 10 ({#sec:first-passage}) with the Little's-law and first-passage detours (Ross pointer for both); section 11 rewrite (stability absorbed from the old section: ν-criterion, phase picture with δ as an axis, crash-then-flatline ratchet, trapped fraction, corrected economics, #8's realistic-regime subsection); `verify_examples.py` extended with the quoted first-passage numbers.

## Writing / infrastructure

- Prior-work section (`sections/03-prior-work.md`) is a stub; do a real literature pass before assembly (PUT/BXM indices, volatility risk premium, Whaley, Israelov & Nielsen; verify novelty claim for the queueing framing).
- Abstract to be rewritten last.
- LaTeX assembly pipeline (Unicode-math → LaTeX conversion) — decide tooling when sections stabilize.
- Figures: the ASCII payoff diagrams in the section 02 detour are placeholders — redraw as proper vector figures (TikZ or similar) at assembly time.
