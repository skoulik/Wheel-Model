# Real Statement vs. Model: Observations from 14 Months of Live Wheel Trading

Source: statements/USD.csv + statements/USD1.csv (private, gitignored) — Interactive
Brokers cash-flow statements covering 2025-05 through 2026-07-10. Parser and
aggregate reports: code/analyze_statement.py. Parsed: 1,123 closed option positions
(75 still open), 161 stock transactions, 332 dividend-related cash flows (these
extend back to 2025-02, earlier than the option activity). A "junk" universe (~30 low-priced
legacy/meme/bankruptcy tickers: BLNK, FOSL, BYND, PLUG, NIO, MPW, CLOV, ...; plus
BEKE by operator judgment) is excluded — those are mostly covered calls liquidating
dead legacy stock plus bankruptcy remnants; interesting as a cautionary tale (see
#9) but not wheel data. The remaining "quality" universe is ~45 names (ABT, ACN,
ADP, BMY, CLX, CMCSA, CTSH, DPZ, ELV, GPC, HD, HPQ, INTU, JKHY, KMB, LOW, MDT, MRK,
MSFT, NVO, PFE, PYPL, SLB, TGT, UNH, ZTS, ...): 760 closed puts, 271 closed calls,
41 completed inventory lots, 27 lots still open.

Lot-attribution note: a share sale is matched to the open lot whose basis equals
the sale price (the wheel's default exit — the call was struck at that lot's
basis), falling back to FIFO only when no basis matches. Plain FIFO misreads
layered names as capitulations; see #4.

Headline: the model's *architecture* (queue of lots, put arrivals, call departures,
self-recycling) matches the practice well. The parameter conventions and several
simplifying assumptions do not. Numbered findings below, each with the model
implication.

---

## 1. The duty-cycle gap: option tenor ≠ cadence period  [biggest structural miss]

The model assumes one put always running: period = option lifetime τ_p. Reality: the
dominant pattern (525 of 760 puts) is a **2–4 day option sold on a weekly cadence** —
sold Tuesday (~70% of opens), expiring Friday. The stock is "covered" by a live put
only ~40–50% of calendar time.

Model implication: introduce two separate parameters — cadence period T (how often a
put is sold) and tenor τ_p ≤ T (how long it lives). Premium accrues once per T but is
priced off τ_p; assignment probability per cadence period is that of a τ_p-day option,
which for 3 days is far smaller than a weekly-tenor put. All annualizations change by
the factor τ_p/T. The current model is the special case τ_p = T.

## 2. Realized put assignment rate is ~9%, not ~18–20%

Across 760 quality puts: 66 assigned = 8.7% (weekly bucket 9.0%, monthly bucket
11.8%). The article's running example targets p ≈ 17.6%. The operator in practice
runs much further out of the money (median premium 0.26% of strike on 3-day puts) —
and the risk-neutral→real-world gap (p_rw < p) plus put skew push realized frequency
down further. Empirically validates the draft's conservatism claim, but the
*examples* should feature a low-p* regime (p* ≈ 5–10%) as the realistic base case,
with p* = 20% as the aggressive variant.

## 3. Recycling is much faster than the stress example — for lots that recycle

Realized call-away rate per call position: 29% for ≤1-week calls, 18% for monthly
calls. The model's *stress* example (d = 0.15) gives q ≈ 16% per QUARTER; reality
shows ~18% per MONTH. Median completed-lot holding time: 28 days. Median call tenor
~2.5 weeks, so realized n = τ_c/τ_p ≈ 3–6 against weekly puts. Consistent with the
derived E[d | assignment] ≈ 8% picture (TODO #3, since resolved), not with d = 0.15
as base case — see #12 for the direct measurement.

## 4. Holding times come in three regimes, and naive statistics only see the first
   [tier 2 in the flesh — updated with the May–July 2026 window]

The extended window is a natural experiment: several lots flagged as "stuck" in May
resolved by July, and HOW they resolved matters. Three regimes are now visible:

  * **Fast lane** (most lots): recycle in ~2–6 weeks at entry strike. Median
    completed-lot holding: 28 days. HD did a full cycle (assigned @300 May 16,
    called away @300 Jun 19) in 34 days.
  * **Metastable**: months-long limbo that DOES resolve at entry strike. MSFT @370
    and UNH @260 exited at strike after ~49 days; HPQ (600 sh @22) after 151 days;
    max completed holding 168 days. Patience worked — these are the lots the
    homogeneous model averages into the fast lane, wrongly but not fatally.
  * **Trapped**: old high-basis layers that neither recycle nor get abandoned —
    the operator holds them while cycling fresh layers beneath (see #6): ADP @240
    (153d) held while its 217.5 layer resolved at strike; ZTS @130 (231d) held
    while a 75 layer cycled underneath. Still open and aging: NVO 344d, STRF ×5
    (230–324d), HRL@26 314d, PYPL 237d, TRI 142d — a third of open lots are older
    than 200 days. Genuine capitulation (exit below basis) is RARE: 2 of 41
    completed lots (KVUE 20→18, a −10% realized exit; NVO 74→71, a scratch).

Model implications:
  a) **Censoring**: statistics on completed lots overstate q — the aging tail never
     enters them. Empirical calibration needs survival analysis, not sample means.
  b) A single q cannot generate this mixture. Tier 2's depth-dependent q_i is one
     way; an explicit three-regime mixture (fast / metastable / trapped) may be the
     cleaner parameterization and maps directly onto what the data shows.

## 5. The call-strike policy is an active lever, not a constant

Model: call strike = original put strike, always. Reality: of 41 completed lots, 34
exited at entry strike, 5 above (strike improvement — extra capital gain), 2 below
(realized-loss exits: KVUE 20→18 the clear case). Calls are also observed struck
below a deep layer's basis while it waits (a standing offer to exit at a loss), but
executed capitulation is rare — the dominant response to a trapped layer is
patience plus layering new entries beneath it (#6), not forcing the exit.

Model implication: K_c is a policy variable, and the phase-diagram lever works in
both directions — strike-up harvests recoveries, strike-down buys q at a
quantifiable realized-loss cost. The observed policy uses it asymmetrically:
freely upward, reluctantly downward. Tier 2 should model K_c policy explicitly and
ask whether the observed reluctance is optimal or a behavioral artifact
(loss-realization aversion) — a genuinely interesting question the model can answer.

## 6. New layers form under old ones, exactly as tier 2 assumes

The extended window shows explicit layering on half a dozen names — a second lot
assigned well below the first while the first is still held: NVO 67→52, PYPL 63→53,
HRL 26→20, KWEB 29→27, TSCO 41→34, ACN 185→148, ZTS 130→75, ADP 240→217.5. Lower
layers demonstrably recycle while upper ones wait (ADP's 217.5 layer completed at
strike in 120 days; the 240 layer is still held). The strike ladder that tier 2
models (deep old strata under fresh shallow ones, with depth-dependent exit rates)
is not hypothetical; it is the normal operating condition of the live account, and
the bottom-up order of resolution is exactly what depth-dependent q_i predicts.

## 7. Arrivals are cross-sectionally clustered (common shocks)

Assignments cluster on dates: 2025-06-21 assigned five quality names at once;
2026-04-25 four (ABT, ACN, MDT, TSCO); 2026-05-15/16 six across two days (CTSH, DPZ,
JKHY, HD, HRL, ZTS). Running ~45 concurrent wheels diversifies idiosyncratic exits
(supporting the "portfolio" resolution of TODO #1), but arrivals are driven by
market-wide drawdowns and land in bursts — precisely when capital is scarcest
(reflexivity, section 09, now with direct evidence). A portfolio model should give p
a common systematic component.

## 8. Transaction costs and early management (minor but real)

Commission: median 3.5% of premium on weekly puts (cheap options, fixed per-contract
fees) vs ~0.1–0.2% on monthlies — a friction haircut that grows as tenor shrinks and
belongs in any τ_p optimization (the frictionless model has no reason not to prefer
ever-shorter tenors). Early buy-backs: ~4% of puts (repurchased at median 11% of
premium received) and ~3% of calls — profit-locking behavior; a refinement, not a
structural gap.

## 9. The "fundamentally sound" assumption fails in the field — and has an absorbing state

The junk universe is a graveyard: covered calls at $1–$3 strikes grinding out exits
from collapsed legacy positions, bankruptcy remnants (FibroGen contra rights,
Walgreens tender odd lots, reverse-split fragments). Once a stock collapses
permanently, its lot exits the wheel mathematics entirely: q = 0 forever, premium
≈ 0, capital loss ~100%. Even a small per-year probability of permanent impairment
adds a non-recycling absorbing state whose expected cost can rival annual premium
income. Worth an explicit per-lot "death" hazard in tier 2 rather than a verbal
disclaimer — real portfolios demonstrably accumulate these.

## 10. Encouraging confirmations

- Call premium now contributes 90% as much gross income as put premium ($28.5k vs
  $31.6k) — and the ratio ROSE from 0.62 to 0.90 as inventory accumulated over the
  extra months, consistent with the model's call-income term scaling with I*.
- Median monthly-put premium 0.72% of strike vs. the model's Black–Scholes 0.5% at
  k = 0.95 — right ballpark, gap consistent with IV > RV plus skew (TODO #4).
- Exit-at-entry-strike is the dominant mode (34 of 41) — the self-recycling
  accounting (gain = original premium) describes the large majority of completed
  cycles.
- The operator sells puts continuously while holding inventory, including on the
  same names (layering), exactly as the queue model assumes.

## 11. Dividends: minor income on ordinary names, structural carry for the aging
    tail  [added 2026-07-11; dividend/withholding parsing in analyze_statement.py]

The statements carry 332 dividend-related cash flows (receipts, payments in lieu,
withholding tax, fees) over 2025-02 .. 2026-07. Matching receipts to the
reconstructed wheel position on the payment date (caveat: entitlement fixes on the
earlier record date, so lots that turned over in between can be mis-bucketed):

  * Wheel inventory collected **$7,104 gross — 11.8% of the $60.1k gross option
    premium**. But $4,750 of that is a single name, STRF; ex-STRF the ordinary
    equity names contributed ~$2,350 ≈ **3.9% of premium** — real, second-order.
    (Another $6,254 landed on legacy shares of quality names held from before the
    window, and $6,023 on non-wheel holdings; both excluded from wheel economics.)
  * **Carry concentrates on the aging tail.** Dividends accrue per unit holding
    time, so the trapped/metastable lots of finding #4 collect disproportionately:
    HRL (315d open) 5 receipts, ADP $510, and NVO, PYPL, ZTS, TRI, DPZ all paid
    while stuck. The patience policy of findings #4/#5 is partly carry-financed:
    a trapped lot's annual cost is opportunity + impairment hazard MINUS net
    dividend yield, which for a 2–4.5% payer meaningfully softens the trap and for
    a high-yielder can erase it. This feeds the #5/#10 optimality question — for
    dividend payers, the option value of waiting comes with positive carry, so the
    observed reluctance to strike down is more rational than it first looks.
  * **STRF is a remarkable outlier, not a category to model**: a fixed-coupon
    preferred ($2.50/quarter, ~9%/yr on the ~110 basis) deliberately wheeled. Its
    five aged lots (230–325d) are the draft's biggest "trapped" block, yet they
    out-earn most fast-lane equity lots while waiting — bond-like securities break
    the "trapped = dead capital" reading. Out of scope for the model (the article
    is about equity wheels); worth keeping in mind when reading the aging-tail
    statistics, since STRF alone is 5 of the 27 open lots and 2/3 of the wheel
    dividend flow.
  * **Withholding is a real, country-dependent haircut**: 15% on US names (treaty
    rate), 27% on NVO (Denmark), 0% on SLB (NRA-exempt) and effectively 0% on STRF
    (withheld then refunded; one payment reclassified Return of Capital). Blended:
    6.4% of gross. Any dividend term in the model (δ in the formulas, income on
    I* lots) should be net-of-withholding for Track A.
  * **Two-thirds of the quality flow arrived as Payment in Lieu** — the broker
    lends out the inventory. Gross-equivalent economically, different tax
    mechanics, and it flags an unmodeled side-channel: wheel inventory earns
    securities-lending income precisely on the hard-to-borrow names. Even the junk
    graveyard drips: $2.1k of PIL, mostly the collapsed REIT MPW — finding #9's
    absorbing state has q = 0 but not always yield = 0.
  * What the cash statement CANNOT test: the dividend-capture early-exercise
    channel (TODO #2c/#5) — payment dates, not ex-dates, are recorded, so
    "call assigned the day before ex-div" is invisible here.

Model implication: TODO #2's three dividend effects get empirical magnitudes —
(a) δ in the probability formulas: typical wheel-name yields 1.5–4.5%;
(b) income on held inventory: ~4% of premium for ordinary names — worth a term,
not a rewrite; (c) untestable from this data. New: net-of-withholding δ, and
dividend carry as an offset in the trapped-lot economics (tier 2's
cost-of-patience). Bond-like names (STRF) are excluded outliers, noted only as
a caveat on the aging-tail statistics.

## 12. Assignments land just under the strike — the derived E[d | assignment]
    checks out  [added 2026-07-11; assignment_depth_report in analyze_statement.py]

Direct empirical test of the article's newly derived E[d | assignment] (TODO #3).
The statements record no market prices, but 57 of the 66 assigned quality puts had
a covered call sold at the lot's basis within days (median lag 3 days), and an
at-basis call's premium prices the market's distance below the strike. Inverting
Black–Scholes on each call's premium/strike/tenor:

  * Implied gap below strike: median −0.6% (σ = 20%) to +0.7% (σ = 30%), IQR
    roughly −1.5% to +3%. NOT ONE assignment implies a gap deeper than 10% at
    σ = 20% (9% of them do at σ = 30%).
  * The model, fed the operator's actual regime (2–4 day puts, ~9% assignment
    rate), predicts E[gap] ≈ +1.0% to +1.5% — inside the empirical band. The
    d = 0.15 assumption would predict ≈ +11%: cleanly rejected. The shallow-
    landing picture behind the derived base case (d ≈ 0.08 for the article's
    monthly example, scaling with σ·√τ_p) is what the account actually shows.
  * The σ = 30% tail (a few implied gaps past 10%) matches the article's framing
    of d = 0.15 as the distribution's tail, kept as a labeled stress case.
  * Caveats: the ~3-day lag between Friday-expiry assignment and the call sale
    lets the market bounce (hence implied spots slightly above strike in ~half
    the cases — some calls were sold after partial recovery), and the inversion
    assumes a flat σ. Read it as "overshoot is of order 1%, bounded far away
    from 15%," not a precise estimate.

Model implication: none needed — this one is a confirmation. The derivation that
replaced the assumed d (TODO #3) survives contact with 14 months of live data in
a regime far from the one it was calibrated on.

---

## Suggested additions to TODO.md (for the main session to fold in)

  7.  Duty cycle: split cadence period T from option tenor τ_p (finding #1).
  8.  Realistic base-case parameters: p* ≈ 5–10%, weekly cadence, ~monthly calls;
      re-run section 08 economics (findings #2, #3).
  9.  Censoring-aware calibration; holding-time mixture — fast / metastable /
      trapped regimes — as an alternative or complement to depth-dependent q_i
      (finding #4).
  10. Call-strike policy K_c as a control variable (strike-down = buying q with
      realized loss); the operator lever in the tier-2 phase diagram. Include the
      optimality question: is the observed reluctance to strike down rational or
      loss-aversion? (finding #5).
  11. Common-shock arrivals across a portfolio of wheels (finding #7).
  12. Transaction-cost haircut as a function of tenor (finding #8).
  13. Permanent-impairment hazard: absorbing "dead lot" state (finding #9).
  16. [added 2026-07-11] Dividend carry in the cost of patience: a held lot's
      waiting cost is opportunity + impairment − net dividend yield; carry
      partially rationalizes the strike-down reluctance of #10. Bond-like
      outliers (STRF) noted but out of scope. Also fold finding #11's empirics
      into existing TODO #2: δ net of withholding (0–27% by country, 15%
      typical), inventory dividend income ≈ 4% of premium for ordinary names.
  (Finding #12 adds no new item — it empirically confirms resolved TODO #3 and is
  recorded in that item's Done entry.)

Note on privacy: this file summarizes aggregates from private statements. The raw
statements are gitignored; the parser (code/analyze_statement.py) contains no data.
