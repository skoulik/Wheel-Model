# Moving volatility and jumps in the base model — plan

**Status: agreed 2026-11-21**, in conversation, before any code: the representation and the
eight choices under *Decided*. Steps 1 and 3 are coded and committed; step 2 has a lower
bound (TODO II-41 for the rest); **step 4 ended overnight 2026-11-21/22 in a fitted model**
(*The volatility fit — method* below, and step 4's records), chosen on Sergei's instruction
while he was away — "if the result is good or acceptable, please move on and finalize the
method" — and **approved by him on 2026-11-22** ("Perfect, that you've got the model
settle"). Takes up TODO II-40, and absorbs II-38 (the swing structure on single names, step 4) and II-39
(the excess return under changing volatility, step 5). Sergei, 2026-11-20: "Perhaps we still
need to incorporate sigma change with the stock movement into the base model … This would involve
reviewing all previous results but might be worth doing to better model the reality." On
2026-11-21 he asked for a way to represent σ_IV's movement before measuring the magnitude of
the effect on each of the model's results.

## Decided

1. **One volatility state drives the price, and σ_IV is derived from it** (Sergei, 2026-11-21,
   "A"). σ_IV is not given a process of its own. The walk runs on realized volatility and the
   premiums on implied; modelled separately, nothing would keep them consistent, and the exact
   tests (excess = −leak at m = r − δ; excess = Δ̄·(μ − r) − leak at m = μ − δ) would be the first
   casualty. This extends the present architecture — premiums are quotes at σ_IV, defaulting to
   σ — rather than replacing it. Rejected: σ_IV as a surface fitted directly to the trade log,
   f(trailing return, moneyness, tenor), which fits the data tighter and leaves the walk's
   volatility and the premiums' unconnected.
2. **Jumps are in, both directions** (Sergei, 2026-11-21). Unscheduled down jumps and up jumps,
   with separate rates and size laws and each with its own effect on the volatility state; off
   by default, as `iv_spread` is zero by default. The reasons are the wheel's own:
   - **d's tail.** d is the diffusion's overshoot at assignment, derived from x₀
     (`eq:fall-split`); the model has no jumps, and the live account's mean d has run about
     twice its median (the pre-registration's P5), the deep lots being gaps on news.
   - **Deep lots leave by up jumps.** A lot 30% under its strike almost never diffuses back
     within a call period; a beat or an upgrade lifts it over in one step.
   - **The far-OTM call wing.** A deep lot's call is priced by the upper tail; without up jumps
     the fair layer prices it near zero and the overlay carries all of σ_IV(x).
   - **The compensator.** m stays the mean, so jumps are compensated in the diffusion's drift;
     down jumps alone would make the stock climb faster between gaps and recover deep lots too
     smoothly.
3. **Earnings are scheduled jumps** (Sergei, 2026-11-21: he sells through earnings weeks, and
   "Even if I did not, better to model them anyway"). Known dates, two-sided, distinct from the
   unscheduled jumps. The size law takes the jumps' shape — separate up and down sides — and
   reduces to a symmetric one if the data say so.
4. **Fair prices only the stock's own diffusive risk** (Sergei, 2026-11-21, "A"). Volatility
   risk unrelated to the stock, jump risk and earnings risk carry no premium in the baseline:
   the pricing measure uses the real-world jump rates and sizes (Merton's 1976 assumption).
   Everything the market charges above that is edge, measured in the overlay — the article's
   "its only edge is the volatility risk premium", extended to the new risks — so the edge stays
   a measured quantity rather than a fitted one. The real-world test stays exact in continuous
   time: excess = Δ̄·(μ − r) − leak, Δ̄ now the price sensitivity plus vega times how far
   volatility moves with the price; its form on a daily lattice is to be derived. Rejected:
   pricing-measure jumps fitted to the market's skew, which makes the skew fair, the edge
   depend on the jump calibration, and the real-world test gain a jump-premium term.
5. **Takeovers are not modelled** (Sergei, 2026-11-21: "They are uncommon in our universe
   (worth confirming and, if true, stating in the article)"). A cash bid pins the stock and
   cashes a lot out wherever it stands — an exit the spine does not have, the mirror of the
   permanent impairment the outlook already lists. Bid days are cleaned out of the jump
   calibration, since a gap followed by a pinned price is unlike any other jump.
6. **Earnings dates come from a public source** (Sergei, 2026-11-21: "Ideally a public source
   if there is one"). Proposed: SEC EDGAR. A US filer announces results on an 8-K carrying Item
   2.02, *Results of Operations and Financial Condition*, and EDGAR's free submissions API lists
   each filing with its item codes. Foreign private issuers file 6-Ks, which carry none; no name
   in the calibration universe (decision 7) does. EDGAR's fair-access policy
   asks an automated client to declare a contact in its User-Agent: Claude's mailbox
   (Sergei, 2026-11-21: "use your address if the system permits, otherwise mine").
7. **The calibration universe is the Dividend Aristocrats, each counted while its cap is $10B
   or more** (Sergei, 2026-11-21: "Take the list from the NOBL index"). Not the names the
   account trades: those are its own data, and include foreign issuers EDGAR cannot date. The
   floor was first $20B, a margin over the live account's $10B, and was relaxed the same day:
   "Quite a few names that the live account trades were filtered because of the higher limit."
   The $10B rule is applied at each date, not to today's cap: a name's day counts only if its
   cap that day was $10B or more. A margin on today's cap could not keep out the years a name
   now large spent small; the rule applied by date does, and needs no margin. Cap on a day:
   EDGAR's latest share count on or before it, put on today's split basis, times Yahoo's
   split-adjusted close; before a name's first count (2009–2011, as XBRL arrived) that count
   stands in. Names reporting shares by class take the all-class weighted-average count, and
   ERIE its 10-K cover (Class A plus 2,400 per Class B share). NOBL's holdings file of
   2026-11-20 lists 68 names, and all enter: 1,131 eligible name-years from 2005, of which the
   18 names under $20B today carry 197. ALB, FRT and AOS, under $10B today, count for the 7.3,
   2.1 and 5.9 years they spent above it. The list is still today's members, so names that
   left the index on a dividend cut, usually after the kind of fall the jump calibration is
   looking for, are missing: a survivorship tilt, taken up with step 2.
8. **Jumps and the volatility state are fitted together, by simulation** (Sergei, 2026-11-21,
   "Let's go with option A"). Step 3 found no threshold at which daily moves separate into
   diffusion and jumps: the count beyond c local standard deviations halves with each half sd
   from 3 to 6, where a normal tail falls six- to ninefold. Fitted in sequence — the days
   beyond a chosen c flagged and removed, the state fitted on the rest — the jump rate would be
   a convention, and the rise in volatility after a large move would be split between a jump
   kick and γ by fiat. Instead the model, state and jumps together, is simulated, and its
   parameters are those whose simulated paths reproduce the statistics measured on the data,
   each computed the same way on both; a threshold is then only a statistic. Rejected: the
   sequential fit at c = 4, or at Lee and Mykland's 1% critical value, about 4.8 for one name's
   sixteen years. The article describes and explains the method in full (Sergei: "we will need
   to thoroughly describe and explain our methodology in the article's prose").

## The representation, as proposed

**The state.** h = ln(σ_t/σ̄), today's volatility relative to its usual level, stepped daily:

    h′ = φ·h + θ·z + γ·(|z| − √(2/π)) + η·ε  (+ a kick on a jump day)
    log return = drift + σ_t·√Δt·z  (+ a jump on a jump day)

θ < 0 is the direction of the leverage effect (volatility rises as the stock falls), γ > 0 its
size (a large move either way raises it); on a rise the two partly cancel. The simulator's
present process is γ = 0. *Hypothesis, untested:* γ is why §09's calibration needed a daily
correlation of −1.0 to reach a monthly −0.37 — a linear correlation saturating.

**Unscheduled jumps.** Rates λ↑, λ↓, sizes exponential by default (Kou's double-exponential
jump–diffusion), each with a kick to h — a profit warning raises volatility. The drift is compensated so that the mean stays m; the walk's log drift then becomes
m − σ²/2 − λ·E[e^J − 1 − J], so jumps of either sign enter the first stability boundary
through the same convexity as σ²/2. Step 3's measurement revises two parts of this: jump
sizes scale with the volatility state, down jumps' clearly and up jumps' less so, so they are
stated as a power β of σ_t (β = 1 in units of σ_t, β = 0 in fixed log terms) with a tail
heavier than exponential; and no kick beyond the state's own response to a move of that size
is visible, so whether jumps need one is left to the fit.

**Earnings.** A date every 13 weeks, shared by every lot — a time-dependent step, not a new
state variable. The walk becomes periodic, with a one-year cycle (13 weeks against the 4-week
call grid); results are averaged over the phase of the start. The event's variance s_E² sits in
every option spanning the date, which is the build-up of implied volatility, and leaves when the
date passes, which is the crush — neither needs a rule, and h need not move for either.

**The fair σ_IV.** Each option priced at state h by the 2-D lattice under the pricing measure,
by backward induction — the same machinery that walks the book. It delivers by itself the term
structure (mean reversion damps h by (1 − e^(−κτ))/(κτ): 0.96 for the weekly put, 0.85 for the
four-week call at a 1.9-month half-life), the skew (θ < 0, down jumps) and the smile (h's swings,
both jump wings).

**The quote overlay.** What the market charges beyond fair, each term defaulting to zero: a
level spread v, multiplicative (σ_quote = (1 + v)·σ_fair); a put/call split; a residual smile
S(z_K) = 1 + s·z_K + c·z_K² in standardized moneyness z_K = ln(K/F)/(σ_fair·√τ). At a fixed p\*
the put's z_K is fixed (≈ −0.84 Standard, −1.28 Conservative), so the put skew is one number per
regime; the call's z_K = x/(σ√τ_c) moves with depth, so the residual smile is σ_IV(x).

## Calibration, as proposed

- **Earnings first, then jumps and the state together**: an earnings day left in is counted as
  a jump and again as a volatility swing, and its date is known, so it is removed first; jumps
  and the state cannot be told apart by any threshold, so they are fitted jointly, by
  simulation (decision 8).
- **The state:** realized-volatility statistics on the calibration universe (decision 7),
  daily from 2005, and the S&P series, on a jump-robust realized variance (bipower variation).
- **Unscheduled jumps:** the statistics of the days the bipower yardstick flags, outside
  earnings dates, split by sign (step 3), as targets for the joint fit. The index's jumps are
  mostly down and cannot be borrowed for a single name.
- **Earnings:** EDGAR's dates (decision 6, step 1); the two sessions from each date are its
  move, and the size law is fitted by sector if the utilities' and REITs' small moves hold up.
- **The overlay:** the trade-log IV panel, re-measured against the fair layer at the same state.
  Two cautions on the panel as it stands: the shallow-to-deep rise in σ_IV(x) is partly state —
  lots get deep in falls that raised volatility — and must be split before an overlay is set;
  and the put skew is absolute IV by percent moneyness across names, where at a fixed p\* a
  volatile name's put is struck further out (unchecked: likely much of the slope).
- **Better, if obtainable:** a daily implied-volatility series per name (IBKR's historical data
  offers OPTION_IMPLIED_VOLATILITY; its depth for single names unchecked), and Cboe's VIX for
  the index.

## The volatility fit — method, as it stands (night of 2026-11-21)

What the article must "thoroughly describe and explain" (decision 8). Code: `code/earnings.py`
(the universe and its dates), `code/volstats.py` (the statistics), `code/jumps.py` (their report
on the data), `code/volfit.py` (the model and the fit).

1. **The sample.** NOBL's 68 names of 2026-11-20, each day counted while the name's cap was
   $10B or more (decision 7); daily log returns of the split-adjusted close with dividends
   added back on ex-dates; the two sessions from each earnings date removed, and every quarter
   whose earnings date EDGAR does not give (decision 6). 1,040 name-years, 262,168 returns.
2. **The yardstick.** Each return over a local volatility from the 60 sessions before it,
   estimated by bipower variation — Lee and Mykland's daily jump test, with Barndorff-Nielsen
   and Shephard's estimator. It is not used to label days as jumps: no threshold separates
   them (step 3). It puts every statistic in units a name's own level cancels from.
3. **The statistics** (48, `volstats.stats`): the tail beyond 3 to 6 local sd on each side;
   the size beyond 4 sd by tercile of the volatility state, and its median-to-mean ratio; the
   rise in volatility over the next 20 sessions by size of move on each side (the kick table);
   II-38's three monthly statistics with the monthly persistence at 1, 3 and 6 months; the
   autocorrelation of |r| at 1 to 250 sessions; and the leverage function, the correlation of
   a day's return with the mean |r| over windows from 1 to 120 sessions ahead.
4. **The model** (`volfit.py`'s docstring): a day's move is a normal shock plus, on a jump
   day, a jump; log volatility is a fast factor plus a slow one, each mean-reverting at its own
   half-life; each responds to the day's move through its share of θ·x (the move's direction)
   and of γ·(|x| − √(2/π)) (its size), Nelson's EGARCH response; a jump adds a kick of its own;
   the fast factor's own noise may scale with its level (Chernov et al.'s feedback). Jumps come
   at a rate per side, with Weibull sizes in units of the day's volatility raised to a power β.
   **As fitted** (step 4), the data pinned down a smaller model, and that is the one carried
   forward: two factors with no shocks of their own (η = 0), moved by the day's direction (θ)
   and, on a down-jump day, by a kick; no size response (γ = 0), no feedback, no kick on an
   up jump; exponential jump sizes on both sides (Kou's law), one β for both — 11 parameters,
   in `data/aristocrats/volfit-final.json`.
5. **The fit.** The simulated method of moments (Duffie and Singleton): the model is
   simulated in eight replicas, each with the data's exact shape — a path per name, as long as
   its history, blank wherever the data is — so that every gap and short series biases the
   simulated statistics as it does the data's; the replicas' statistics are averaged and
   compared with the data's, Σ (simulated − data)² / variance. The draws are fixed, so the
   distance is smooth in the parameters; Nelder–Mead with Gao and Han's coefficients searches
   it, one pass from the start and one restart with a larger simplex, each ending when the
   best distance has gained less than 0.05 over 600 evaluations.
6. **The weights.** Each statistic's variance by the block jackknife over two-year calendar
   periods, every name deleted together (Künsch), floored at the larger of the names'
   bootstrap variance and the model's own sampling variance (the spread across the replicas
   at the starting parameters, each a sample of the data's shape), plus the simulation's own
   noise. Resampling names alone understated the variance thirteen times over, because the
   names share their episodes. The model floor exists for statistics resting on a handful of
   events: on the S&P, a single series with few moves beyond 6 sd, the jackknife variance of
   the kick after them came out near 10⁻²⁰ and took the distance to 10¹⁸.
7. **Checks.** A recovery test — data simulated from known parameters, fitted again on fresh
   fake samples — before any fit is believed (started at the truth: from far off, the search
   stalls, which says nothing about the model); standard errors by the simulated-moments
   sandwich (`volfit.py --se`), with the statistics' covariance taken as diagonal, checked
   against the recovery's spread; a distance near the number of statistics less the number
   of parameters as the sign of an adequate model; and a split of the sample in time, whose
   halves must not differ by more than the weights allow — the check that caught the weights.
8. **Choosing among models.** Nested models compared by distance on the same weights: a
   parameter goes when dropping it costs about its count or less (γ, the up-jump kick and
   shape and a second β: −2.2 for four; η: +0.6 for two; the down-jump shape: −0.4 for one;
   feedback: nothing for one), a factor
   stays when dropping it costs far more (one factor: +27 for the same 14 parameters).

## Sources, and where the article cites them

Sergei, 2026-11-21: "whatever ideas we'll harvest from the prior works should land in the
bibliography section with a reference from the article prose." Each is in
`sections/98-bibliography.md`, uncited until the prose exists; this is where each is owed.
An [A] source is opened before the prose quotes a number from it.

| idea | source | cited where the article |
|---|---|---|
| the response of log volatility to a move's sign and size, θ·x + γ·(\|x\| − √(2/π)) | Nelson 1991 (`nelson-1991`) | introduces θ and γ |
| two volatility factors; the fast one's feedback | Chernov, Gallant, Ghysels & Tauchen 2003 (`chernov-gallant-ghysels-tauchen-2003`) | explains why one factor is not enough |
| a single stock's leverage effect is slow (~69 days); the leverage function as a target | Bouchaud, Matacz & Potters 2001 (`bouchaud-matacz-potters-2001`) | introduces the leverage effect |
| volatility jumps with a down price jump (the kick κ↓) | Eraker, Johannes & Polson 2003; Todorov & Tauchen 2011 | introduces the kick |
| up and down jumps with separate rates and size laws | Kou 2002 (`kou-2002`) | introduces jumps |
| jump risk unpriced in the fair layer | Merton 1976 (`merton-1976`) | defines the fair layer |
| the jump test at daily frequency | Lee & Mykland 2008; Barndorff-Nielsen & Shephard 2004 | describes the jump measurement |
| the joint fit by simulated moments, searched by Nelder–Mead | Duffie & Singleton 1993; Nelder & Mead 1965; Gao & Han 2012 | describes the fit |
| the fit's weights: a calendar-block jackknife, since the names share episodes | Künsch 1989 (`kunsch-1989`), Petersen 2009 (`petersen-2009`) | describes how the distance is weighted |
| the down-jump kick, and none after up jumps | Patton & Sheppard 2015 (`patton-sheppard-2015`) | describes the kick |
| jump clustering, left out; jumps on earnings news | Maheu & McCurdy 2004 (`maheu-mccurdy-2004`) | states the constant jump rate as a limitation |
| the pricing tables' stratified draws and control variate | Glasserman 2003 (`glasserman-2003`) | describes the fair-price tables |
| the calibration universe and how members leave | ProShares holdings; S&P DJI methodology; SEC EDGAR; Yahoo prices | describes the universe |
| the takeover rate's lower bound | Valantasis & Watts 2025 (member-years); Wikipedia (the six exits, until II-41) | introduces jumps |

Read but not yet used, so not in the bibliography: jump intensities that rise with volatility
or with past jumps (Maheu & McCurdy 2004 for single stocks; Christoffersen, Jacobs &
Ornthanalai 2012; Aït-Sahalia, Cacho-Diaz & Laeven 2015), the next remedy if the fit still
falls short; single stocks' "rough" volatility (Zarhali et al. 2025; Bennedsen, Lunde &
Pakkanen 2022); common jumps across stocks (Bollerslev, Law & Tauchen 2008), for step 7.

## Where it lives in the article (settled 2026-11-22)

Sergei proposed an independent appendix, because the parameters come from fitting real-world
data and so should not be developed in Parts I and II. Claude agreed and proposed splitting
the material, which Sergei accepted ("Good, let's settle the plan this way"):
- **The model's structure goes in Part II**, a short section or subsection near §06, where the
  constant-σ assumption is stated. It covers what the process is and why: two volatility
  factors moved only by the stock's own moves, the kick after a down jump, jumps both ways,
  earnings as scheduled jumps, fair prices at the day's state. It is theory and intuition
  only, its numbers cited from the appendix as the running example's σ, μ and δ are cited.
- **The estimation goes in an appendix**, a new file before the derivations (e.g.
  `sections/96-volatility.md`, its anchor registered in §00). It covers the universe and the
  EDGAR dates, the statistics, weights, fit and tests, the earnings law, the Ederington–Lee
  result, and the literature: everything under *Owed to the article*. It is written as a
  self-contained unit, its own introduction, motivation and sources, relying on nothing but
  §00's notation, so that it can be lifted out as a standalone article (Sergei, 2026-11-22:
  "worth a big section in the article or even a standalone article"). Its numbers get checks
  in `verify_examples.py` and rows in the reproduction appendix, like everything else.
- **Not in Part IV.** Developing the process there would leave Part II's results resting on
  a later section, the forward conclusion CLAUDE.md rules out. An appendix is reference
  material any section may cite. Part IV still uses the process: the overlay (step 6) and the
  live-account comparison.
- **Then a full re-read.** Once the corrections are integrated, every section is re-read
  paragraph by paragraph (Sergei: "besides the individual corrections, we'll need to re-read
  all prior sections in full"). One section per session, as with §09's review. The signed
  claims flag what cites a changed formula or figure; sentences that assume constant σ
  without citing anything are found only by reading.
- **Decided on step 7's numbers (Sergei, 2026-11-22):** Part II carries the variable-σ
  model's results, side by side with the simplified constant-σ model's where practical and
  relevant. The gap at assignment is given prominence: "This is what brings 'pain' to the
  stakeholders." (Step 7 records the override of Claude's proposal to keep constant σ.)

## Owed to the article

What the prose must carry when Part II is revised or the difference is reported (Sergei,
2026-11-21: "we will need to thoroughly describe and explain our methodology in the article's
prose"; 2026-11-22, on the dropped earnings term: "make sure that the justification for the
parameter drop lands in the article's prose"). Each item points to where its numbers are.
1. **The method**, in full (decision 8; *The volatility fit — method*):
   - the 48 statistics, computed the same way on the data and the simulation;
   - the replicas on the data's own mask, and the fixed draws;
   - the weights: names share episodes, so resampling names understated the variance 13
     times. A calendar-block jackknife instead, after `kunsch-1989` and `petersen-2009`,
     with its floor. Eleven blocks is few: the errors move by about a fifth across 1-, 2-
     and 3-year blocks (step 5, (B));
   - the search, the at-truth recoveries, and the sandwich errors with their diagonal
     caveat.
2. **The model, and why each part** (step 4):
   - two factors, one rejected;
   - no shocks of the volatility's own;
   - θ, and the down-jump kick, whose precedent is `patton-sheppard-2015`;
   - Kou jumps in units of volatility^β;
   - γ and feedback dropped as undetermined.
3. **A constant jump rate**, a choice the data allow. Tail moves cluster, and the kicks
   reproduce it (step 5, (A), table). Maheu–McCurdy's clustering is the precedent.
4. **Earnings** (step 5(a), (C), the surprise table, and the dropped term):
   - the law: Kou, sizes nearly state-free, utilities and REITs half;
   - [`ederington-lee-1996`]'s decomposition holding in single stocks' realized
     volatility: the expected part of an earnings move leaves volatility alone, and the
     surprise raises it as any surprise does;
   - **the earnings term in h, measured and left out with its numbers**: excess 0.4bp,
     inventory 0.07%, betas 0.001. The expected part's fall and the surprise's rise offset
     for an option held for weeks;
   - `patell-wolfson-1981` and `dubinsky-et-al-2019` for scheduled jumps and the implied
     volatility's build-up and crush; their earnings premium is for the overlay;
   - `christensen-timmermann-veliyev-2024`: another firm's earnings can jump a name that
     announced nothing.
5. **Fair prices** (step 5(c)–(d)):
   - with no volatility shocks of its own, the pricing measure is one shift;
   - the tables and their accuracy (`glasserman-2003`);
   - both exact tests, with the vega channel: +0.006 on Δ̄, confirmed paired;
   - every excess read against its pricing-drift twin.
6. **II-38's answer and Merton's caveat**: a single stock's volatility against the index's
   (step 4); half the down jumps fall on market-wide days.
7. **What is left out, and why:** takeovers (decision 5), the index's leavers (step 2's
   lower bound), the constant jump rate (3), the earnings term (4).

## Sequence

1. **Earnings dates** (decision 6). `code/earnings.py`, in `prices.py`'s shape, with the
   dated universe pinned in it (Sergei agreed the design, 2026-11-21). EDGAR's filings and the
   universe's price histories are cached under `data/aristocrats/`, apart from the live
   account's `data/prices`, which every statement tranche refreshes; the EDGAR contact is read
   from an environment variable, so the repository carries no address; the predecessor CIKs,
   the by-date cap and the rule for undated quarters live in the script.

   **Probed 2026-11-21** (scratch, on the 50 names, prices from 2005 since Item 2.02 began in
   August 2004): keeping the last Item 2.02 within 60 days before each 10-Q or 10-K drops the
   extra ones a few filers make (AbbVie's at each quarter's start) and gives 4.0 a year for
   most names. On 37.5% of the two-session windows from those dates the stock moves more than
   3 robust standard deviations, against 4.8% of all other windows. Three things to fix: a
   reorganized company's history sits under its predecessor's CIK (XOM's new holding company
   from 2026, LIN from 2019, MDT from 2015); ED until about 2017 and TROW until about 2022
   announced most results outside Item 2.02; and a dozen names lose an occasional quarter to
   the 60-day rule. Earnings barely move the utilities and the REIT (z > 3 on 6–11% of ATO, ES,
   ED and O's dates, against 30–60% elsewhere), which the size law will have to carry.

   **Re-probed the same day** on the 68 names, each counted by date at $10B. Merging the
   predecessors' filings puts XOM, LIN and MDT at 4.0 dates a year. The obvious fallback for a
   quarter with no Item 2.02 — the last 8-K carrying Item 8.01 or 7.01 — lands on a gap only
   14% of the time (29 dates, mostly ED's and TROW's), so it mostly is not results. Proposed
   instead: a quarter whose date cannot be found is left out whole, its earnings and its other
   windows alike, rather than guessed. Size shows, modestly: on the names under $20B today the
   earnings windows move more than 3 robust standard deviations 44.1% of the time against
   37.2% above it (other windows 4.2% against 4.8%), and median robust volatility is 19.6%
   against 17.3%. Step 4 reports its fit for the two groups apart as well as together.

   **Coded 2026-11-21** (`code/earnings.py`). Of the 1,130 name-years the cap rule admits,
   1,101 are dated; 38.2% of the 4,449 earnings windows move more than 3 robust standard
   deviations, against 4.7% of the others. ED loses 33 quarters and TROW 53, most with no 8-K
   at all near the release: 1.7% of the name-years. Elsewhere a missing quarter is usually a
   release filed with no item but 9.01: the last such 8-K lands on a gap 44% of the time, close
   to Item 2.02's rate, but would recover only 9 quarters, so those quarters are left out with
   the rest, at 0.4%. The stretch after each name's last periodic report is left out too
   (0.5%), since no report in the window confirms its results.
2. **Takeovers' rarity** (decision 5). Count acquisitions among the S&P 500 Dividend
   Aristocrats from the index's published changes, against member-years, over as long a
   window as the changes are published for. The traded universe cannot answer it — an acquired
   name drops out of the price histories, so the names held are survivors by construction.
   If the rate is low, the article says so, with the rate, where it introduces jumps. The same
   changes name the members that left on a dividend cut (decision 7's survivorship tilt);
   whether to bring them into the calibration for their member years is decided here.

   **A lower bound, 2026-11-21** (Sergei: "let's go with the simpler option (lower bound) for
   now"; the full count is TODO II-41). S&P's own documents, saved in `literature/` — the
   20-years paper (May 2025), the research paper (March 2025) and the methodology (October
   2026) — give the counts but list no removals. The 20-years paper's Exhibit 8 charts the
   members each year, about 950 member-years over 2009–2025 read off the chart, and its Fact 2
   says 24 of the 57 founding members of May 2005 remained in March 2025. The methodology
   deletes a member between rebalancings for "mergers, takeovers, delistings, suspensions,
   spin-offs/demergers, or bankruptcies", and with its removal from the S&P 500 (p. 41); a
   monthly dividend review removes the cutters (p. 40). Wikipedia's table of changes names six
   takeover exits over 2009–2025 — Anheuser-Busch, Wrigley, Family Dollar, Sigma-Aldrich, the
   old Chubb, People's United — so the rate is at least 0.6% of members a year. A floor: the
   table starts in 2009 and gives most removals no reason. The leavers' decision waits for
   II-41's list.
3. **Unscheduled jumps: the measurement** (`code/jumps.py`). Lee and Mykland's test at daily
   frequency: each clean return — dividend added back, earnings windows out — over a bipower
   yardstick from the 60 sessions before it. Under decision 8 this step supplies statistics
   for the fit, not parameters.

   **Measured 2026-11-21** on 1,040 name-years, 262,168 returns. The tail, beyond c local sd:

   | c | 3.0 | 3.5 | 4.0 | 4.5 | 5.0 | 6.0 |
   |---|---|---|---|---|---|---|
   | observed | 4,319 | 2,304 | 1,349 | 836 | 536 | 236 |
   | normal tail | 708 | 122 | 17 | 1.8 | 0.2 | 0 |

   At c = 4, 0.44 up and 0.86 down jumps a name-year. In local sd the size beyond c is flat
   across the volatility state (down jumps 1.29, 1.31, 1.35 by tercile, low to high) and
   across names' levels, while in log return it more than doubles (1.05% to 2.48%): jump sizes
   scale with volatility. Their tail is heavier than exponential, the median 0.61 of the mean
   against 0.69. At c = 5 the rates and the kicks tell the same story and down jumps' sizes
   still scale with volatility, but up jumps' do not clearly (1.62, 1.18, 0.80 sd by tercile;
   1.19% to 1.49% in log return), so the fit carries the scaling as a parameter per side. The rise in volatility after a move, ln(sd of the 20 sessions after / the 20
   before), grows smoothly with the move, and jumps sit on the same curve:

   | move, local sd | 0–1 | 1–2 | 2–3 | 3–4 | > 4 |
   |---|---|---|---|---|---|
   | down | −0.01 | +0.06 | +0.15 | +0.25 | +0.43 |
   | up | −0.03 | 0.00 | +0.05 | +0.14 | +0.24 |

   That is the shape θ and γ give without a separate kick. 51% of down jumps and 31% of up
   ones fall on days the S&P moved beyond 3 sd. Among the largest are profit warnings filed
   under Item 2.02 that the date rule rightly leaves unscheduled (MDT 2006-08-02, ADM
   2024-01-22, SYY 2026-03-30). No up jump is followed by a collapse in volatility, the mark of
   a price pinned by a bid.
4. **The state and the jumps, fitted together** (decision 8) — II-38, widened. Agreed with
   Sergei 2026-11-21 ("The design is sound"):
   - **The estimator:** the simulated method of moments, on the names pooled — one parameter
     set for a typical Aristocrat. The distance weights each statistic by its sampling
     variance from resampling the names, so the spread between names counts. Each simulated
     replica copies the data's structure, a path per name as long as its history and blank
     where the data is, and the statistics are averaged over replicas, so the data's
     small-sample biases are reproduced rather than corrected for. The draws are fixed, which
     keeps the distance smooth; Nelder–Mead searches it. First a recovery test: data simulated
     from known parameters, fitted from elsewhere.
   - **The parameters:** the state's half-life, θ, γ and η; per side a rate, a Weibull size
     law (shape 1 is exponential, below 1 heavier) and the exponent β of its scaling with
     σ_t; per side a jump kick, held at zero unless freeing it improves the fit materially.
   - **The targets** (`code/volstats.py`): step 3's tails, sizes and kicks; II-38's three
     monthly statistics; the autocorrelation of |r| from 1 to 250 sessions. Every one is in
     units a series' own level cancels from, so σ̄ drops out.
   - **No market factor yet.** The base model is one stock; the shared-day shares are kept
     for step 7, where the account's many names matter.
   - **Groups:** the pool, and the two size groups apart; the S&P for comparison. Per name only
     the state's persistence, as a check on how far names differ — about 20 jumps a name at
     4 sd are too few for a jump law each.
   - **numpy is required** for the fit (Sergei: "numpy is fine, the stdlib only rule does not
     hold already as we use matplotlib"): an evaluation is eight simulations of the universe.

   This is where the γ hypothesis is tested.

   **First fit, 2026-11-21, one volatility factor, kicks at zero.** The recovery test passed
   (distance 30.6 over 43 statistics; the state recovered within 10–20%, the jump laws trading
   rate against size by about 10%, β weakly identified). On the data the model failed: distance
   202 where about 31 is expected. Two misfits are structural. Within names, volatility's
   monthly autocorrelation falls fast and then lingers — 0.53 at one month and 0.17 at six
   (per-name means), against the fit's 0.61 and 0.12 — the mark of a fast and a slow component,
   which one mean-reverting state cannot give; names differ only a little more than sampling
   explains (sd 0.12 across names at one month, 0.08 in simulation), so this is not pooling.
   And the jumps turned into a patch for thin daily tails: 21 up and 33 down a year at 1–4 sd,
   up-jump sizes shrinking as volatility rises (β↑ = −1.5). The rise in volatility after a
   4–6 sd fall also fell short (0.31 against 0.41). Sergei chose two factors ("Let's go with
   the option A"): h = h_fast + h_slow, each mean-reverting at its own half-life, the day's move
   split between them, and the jump kicks free. Rejected for now: a fat-tailed (Student-t)
   diffusion, which mends the tails but not the persistence; both, if two factors leave the
   tails short.

   **Second fit, two factors, one shared split, kicks free.** Distance 160 over 43 (one factor
   202; about 26 expected). The tails, II-38's monthly statistics (sd of log monthly volatility
   0.41 against 0.39, its correlation with the month's return −0.24 against −0.24) and
   persistence from a month out fit within 3 sd; the misfit moved to short horizons — the rise
   in volatility after 1–2 sd moves (z ≈ −5) and the autocorrelation of |r| at 5–20 sessions
   (z ≈ −3.5). Fast factor: half-life 5.2 sessions, 63% of the response; slow: 81 sessions.
   θ = −0.031, and **γ = −0.035**: once a fast factor is in, a large move does not raise
   volatility of itself — the rise after large moves in step 3's kick table is mostly a spike
   already under way, which the move reveals and the fast factor carries. The recovery test
   recovers γ's sign (0.053 against a true 0.060), so this is the data, not the fit. Jumps are
   rare and large again (1.1 up and 5.2 down a year), a down jump adding a kick of +0.69; but
   the recovery test trades their rate against their size (1 a year at 3 sd came back as 0.5
   at 5 sd), so only the combined tail beyond about 3 sd is pinned, and the slow factor's η is
   loose. Sergei asked for the literature first ("check whether anyone has faced the problem
   and suggested a remedy"); the sweep is under *Sources*. Taken from it: θ and γ split
   between the factors separately (a single stock's leverage effect is slow), the leverage
   function as five more targets, and feedback in the fast factor — fitted with and without
   the feedback, against a recovery test of the full model.

   **Third round, and the weights corrected (night of 2026-11-21).** Started cold with
   feedback 0.5, the full model and its recovery test both stalled (distances 205 and 98 after
   1,600 evaluations) and were stopped; without feedback the separate splits reached 150.5.
   Then the weights themselves turned out wrong. Split at 2016, the sample's two halves differ
   in the targets by far more than resampling the names allows — Σ z² = 645 over 48
   statistics, where about 48 is expected — most at the long lags (the autocorrelation of |r|
   at 60–250 sessions, the leverage function at 61–120, the six-month persistence): the
   names share their episodes, 2008 above all, and resampling them as if independent cannot
   see it. Every name's returns in a two-year calendar block deleted together — a block
   jackknife (Künsch 1989) — gives each statistic's sampling variance as a median **13
   times** the names' (geometric mean 11.5; 20 to 100 times at the long lags; below the
   names' for a few size statistics, so the weights use the larger of the two). Under those
   weights **the two-factor fit of the second round scores 18.2 over 48 statistics**, where a
   right model with 19 parameters would score about 29: the misfit was the weights', not the
   model's. `volfit.py` now weights this way by default (`--variance names` restores the old
   weights for comparison), the S&P included, whose one series the names could never
   resample. Refitting on these weights: the two-factor model, the one-factor model — which
   the old weights rejected, and which `model.py` would carry far more cheaply — and the
   two-factor model with feedback, all three started from the second round's fit.

   **Feedback is not needed.** On the block weights the feedback model settled at ζ = −0.02,
   distance 15.79 after 1,200 evaluations, against 15.63 for the same model without it; the
   run was stopped there (its best point is `data/aristocrats/volfit-all-fb-final-checkpoint.json`).
   Chernov et al. needed feedback for the Dow over 1953–1999, one index through 1987 with
   no jumps in their log-linear family; here the jumps and the down-jump kick do what their
   feedback did.

   **The two-factor model fits** (`data/aristocrats/volfit-all-nofeedback-warm-2f.json`,
   2,767 evaluations): distance **15.6 over 48 statistics** with 18 free parameters, every
   statistic within 1.6 of its standard error. Standard errors by the sandwich
   (`volfit.py --se`, approximate — the statistics' covariances are taken as zero):

   | parameter | estimate | s.e. |
   |---|---|---|
   | fast factor half-life, sessions | 5.1 | 2.3 |
   | slow factor half-life, sessions (slow/fast × fast) | 78 | — (ratio 15.3 ± 5.4) |
   | share of the direction response in the fast factor | 0.67 | 0.19 |
   | share of the size response in the fast factor | 0.64 | 0.10 |
   | θ, direction (leverage) | −0.0275 | 0.0095 |
   | γ, size | −0.018 | 0.037 |
   | η fast, η slow (own shocks) | 0.028, 0.006 | 0.040, 0.012 |
   | up jumps a year | 1.12 | 0.62 |
   | up-jump scale a, shape k, β | 2.2, 1.31, 0.47 | 3.6, 1.6, 1.4 |
   | down jumps a year | 5.6 | 1.5 |
   | down-jump scale a, shape k, β | 2.47, 1.26, 0.55 | 0.77, 0.27, 0.31 |
   | kick, up / down | 0.00 / +0.69 | 0.98 / 0.10 |

   Determined: leverage (θ, negative at three s.e.), two speeds (a week, about four months),
   five to six down jumps a year at about 2.5 local sd beyond the diffusion, sizes about
   exponential (k = 1 is within one s.e.) and scaling with volatility less than one-for-one
   (β ≈ 0.55), and a down jump doubling volatility (+0.69 in log), 64% of it into the fast
   factor. Not determined: γ (zero within half an s.e. — once the kick is in, a large move
   needs no extra response by its size), the own shocks η (volatility's variation is
   carried by its responses to moves), and the up-jump law beyond its rate (about one a
   year). The γ hypothesis — that a size effect is why §09 needed a daily correlation of −1.0
   — is **not supported**: what does the work is the down-jump kick. Next: the reduced model
   (γ = 0, up-jump sizes exponential, up-jump kick 0, one β for both sides) against this one,
   a recovery test of this fit from a perturbed start, and the one-factor model's final
   distance.

   **One factor is not enough, even on the honest weights** (`…-warm-1f.json`, 3,511
   evaluations): distance **40.7** with 14 free parameters — the same count as the reduced
   two-factor model — and the misses are where the wheel lives: persistence at six months
   (0.07 against 0.22, z = −2.3) and the leverage function at 21–60 sessions (−0.051 against
   −0.027, z = −3.5). A single state cannot be quick at a week and persistent at half a year
   at once, and its jumps again turn into a patch for thin daily tails (32 small down jumps a
   year, sizes 0.75 local sd). **The two-factor model stays.**

   **The weighting checked on fake data.** On a sample simulated from the two-factor fit —
   independent names, no shared episodes — the calendar-block jackknife gives about the
   names' variance (median ratio 1.11), so the thirteen-fold inflation on the real data is
   the shared episodes, not the jackknife. The distance at the true parameters on that sample
   is 30.5 over 48, where the fit with 18 parameters would expect about 30: the weights are
   calibrated. A recovery from 30% off the truth reached only 78 after 1,400 evaluations — the
   18-parameter surface, with its undetermined directions, is hard for Nelder–Mead — so
   identification is tested on the reduced model.

   **The reduced model is the model** (`volfit-all-nofeedback-warm-2f-reduced.json`,
   2,809 evaluations): γ = 0, up-jump sizes exponential, no kick on an up jump, one β for both
   sides — four parameters fewer, and the distance *fell*, to **13.4 over 48** with 14 free
   parameters, no statistic beyond 1.5 s.e.; the four were noise the search had to carry.
   Standard errors (sandwich, diagonal):

   | parameter | estimate | s.e. |
   |---|---|---|
   | fast half-life, sessions | 5.5 | 2.2 |
   | slow half-life, sessions | 86 (4.1 months) | ≈ 26 (ratio 15.9 ± 4.8) |
   | θ | −0.029 | 0.008 |
   | fast factor's share of θ / of the jump kick | 0.70 / 0.66 | 0.15 / 0.12 |
   | η fast / η slow | 0.037 / 0.006 | 0.038 / 0.012 |
   | up jumps a year; exponential scale, local sd | 1.12; 1.85 | 0.47; 0.62 |
   | down jumps a year; Weibull scale a, shape k | 6.2; 2.41, 1.19 | 1.5; 0.70, 0.22 |
   | β, sizes' scaling with volatility | 0.54 | 0.32 |
   | down-jump kick (log volatility) | +0.64 | 0.10 |

   Everything is determined but the own shocks η, which the responses to moves can stand in
   for; a variant with both η at zero (volatility moved only by the moves themselves, as in
   Nelson's EGARCH) is being fitted to see whether the data need them.

   **They do not: the final model** (`volfit-all-nofeedback-warm-reduced-noeta.json`, 1,945
   evaluations) holds η = 0 as well and scores **14.0 over 48 with 12 free parameters**, no
   statistic beyond 1.5 s.e. — 0.6 above the model with η free, for two parameters fewer.
   Volatility is moved only by the day's move: by its direction through θ, and on a jump day
   by the kick. Every parameter is now determined:

   | parameter | estimate | s.e. |
   |---|---|---|
   | fast half-life, sessions | 5.7 | 2.4 |
   | slow half-life, sessions | 88 (4.2 months) | ratio to the fast 15.4 ± 5.7 |
   | θ, log volatility per unit of the day's move | −0.026 | 0.007 |
   | fast factor's share of θ / of the kick | 0.71 / 0.67 | 0.17 / 0.10 |
   | up jumps a year; exponential scale, local sd | 1.2; 1.8 | 0.55; 0.50 |
   | down jumps a year; Weibull scale a, shape k | 6.5; 2.36, 1.18 | 1.8; 0.63, 0.21 |
   | β, jump sizes' scaling with volatility | 0.56 | 0.23 |
   | down-jump kick, log volatility | +0.645 | 0.058 |

   Read plainly: a day's fall of one local sd raises log volatility by 0.026, 71% of it in a
   factor that halves in about a week and the rest in one that halves in about four months; a
   down jump — six or seven a year, averaging about 2.2 local sd beyond the day's normal move —
   raises it by 0.645 (volatility × 1.9), two thirds of it gone within a few weeks; an up jump,
   about one a year, moves it only through θ. Jump sizes grow with volatility, but less than
   in proportion (β ≈ 0.56). The down-jump shape is within one s.e. of exponential; whether
   k↓ = 1 (both sides exponential, Kou's law, scaled by volatility) costs anything is tested
   next.

   **It costs nothing, and that is the model carried forward** (`data/aristocrats/volfit-final.json`,
   a copy of `…-final-kou.json`; errors in `volfit-final-se.json`): with down-jump sizes
   exponential too, the distance is **13.6 over 48 with 11 free parameters** — lower than with
   the shape free, the search having one direction fewer — and no statistic beyond 1.5 s.e.

   | parameter | estimate | s.e. |
   |---|---|---|
   | fast half-life, sessions | 6.1 | 2.4 |
   | slow half-life, sessions | 104 (4.9 months) | ratio to the fast 16.9 ± 5.4 |
   | θ, log volatility per unit of the day's move | −0.0288 | 0.0073 |
   | fast factor's share of θ / of the kick | 0.71 / 0.69 | 0.12 / 0.09 |
   | up jumps a year; mean size, local sd | 1.36; 1.77 | 0.55; 0.62 |
   | down jumps a year; mean size, local sd | 6.34; 2.02 | 1.07; 0.57 |
   | β, jump sizes' scaling with volatility | 0.58 | 0.32 |
   | down-jump kick, log volatility | +0.631 | 0.066 |

   In words: **a stock's log volatility is the sum of a factor that halves in about six
   sessions and one that halves in about five months; neither has shocks of its own — each
   day's move pushes them, a fall raising volatility by 0.029 a local sd (71% into the fast
   factor), and a down jump raising it by a further 0.63 (volatility × 1.9, 69% into the fast
   factor). Jumps are Kou's double exponential, in units of the day's volatility raised to
   0.58: about six or seven down a year averaging two local sd, and one or two up averaging
   1.8.** The group fits above used the shape free (k↓ ≈ 1.1–1.2), a difference the fits
   cannot see.

   **Identification** (`volfit-all-recover-…-attruth-seed{2,3,4}.json`, the 14-parameter
   model with η free; truth = its fit). Searches started from 30% off the truth stalled far
   above it (78, 150, 85, where the truth scores about 30) — the search, not the model:
   Nelder–Mead in 14–18 dimensions with flat directions does not find its way back from far.
   Started at the truth, on three fresh fake samples, every parameter came back near it,
   without visible bias, and with a spread across samples at or below the sandwich standard
   error computed on a fake sample: up jumps 0.15 against 0.16, k↓ 0.060 against 0.083,
   β 0.063 against 0.135, the kick 0.014 against 0.030, θ 0.0008 against 0.0026. Three samples
   are few and a start at the truth narrows the spread in flat directions, but the sandwich
   errors are not too small — if anything conservative. They are 3–4 times smaller on fake
   samples than on the data, the √13 of the shared episodes the fake names do not have: the
   errors to quote are the data's.

   **The final model by group** (`volfit-{all,big,small}-…final*.json`, `volfit-sp-…`; all
   with the final model's specification except the S&P, fitted earlier with η free):

   | | pooled (68) | over $20B (50) | $10–20B (18) | S&P 500 |
   |---|---|---|---|---|
   | distance over 48 | 14.0 | 10.5 | 25.5 | 14.0 |
   | fast / slow half-life, sessions | 5.7 / 88 | 6.3 / 102 | 5.8 / 109 | 6.0 / 114 |
   | θ | −0.026 ± 0.007 | −0.033 ± 0.008 | −0.012 ± 0.005 | −0.070 |
   | down jumps a year | 6.5 ± 1.8 | 6.1 ± 1.0 | 7.1 ± 1.3 | 6.8 |
   | down-jump kick | 0.645 ± 0.058 | 0.655 ± 0.072 | 0.512 ± 0.062 | 0.415 |
   | up jumps a year | 1.2 ± 0.55 | 1.35 ± 0.42 | 0.87 ± 0.20 | 0.9 |
   | β | 0.56 ± 0.23 | 0.61 ± 0.29 | 0.65 ± 0.27 | 0.67 |

   The two size groups share the model and nearly every parameter; the one difference near
   two standard errors is the leverage effect, weaker among the smaller names (−0.012 against
   −0.033, difference 0.021 ± 0.010), and their jump kick is a little smaller (1.5 s.e.). The
   pooled parameters stand for the live account's universe, which spans both; a size-dependent
   θ is a refinement to note, not to build in.

   **The S&P 500, for comparison — and II-38's answer** (`volfit-sp-…-reduced-floored.json`,
   the reduced model, distance 14.0 over 48, no statistic beyond 1.5 s.e.). Fast half-life
   6.0 sessions, slow 114 (5.4 months); θ = −0.070, two and a half times a single stock's;
   up jumps 0.9 a year, down 6.8; the down-jump kick +0.42, smaller than a stock's. On the
   statistics themselves, index against stocks: the sd of log monthly volatility 0.47 against
   0.39, its one-month autocorrelation 0.66 against 0.57, a month's return correlating with
   the change in its log volatility −0.42 against −0.24, and the leverage function 1.6 to 2
   times as deep at every lag. **The borrowing of II-38 does not hold**: a single
   Aristocrat's volatility swings less, forgets faster and answers the price about half as
   strongly as the index's — Bouchaud, Matacz and Potters' contrast between stocks and
   indices, on these names. §09's simulation ran the index's swings and a leverage
   correlation near the index's for a single stock, so it overstated both.

   **Where step 4 leaves the plan (2026-11-22).** What changes downstream:
   - **The γ hypothesis is not supported.** §09's need for a daily correlation of −1.0 is not
     a size effect: once a fast factor and a down-jump kick are in, γ is zero. What a single
     stock has is a modest direction effect (θ) and a large kick on down jumps.
   - **No own volatility shocks.** Volatility is moved by the day's move alone, so the state
     is a function of the price path — for the simulator, two filters of the moves already
     drawn; for `model.py` (step 7), a state that the depth walk itself drives.
   - **Two factors, not one.** The simulator carries both. Whether `model.py` can carry only
     the slow one, folding the fast factor and the jumps into a fatter-tailed period return
     over a four-week call period, is step 7's question.
   - **Jumps are Kou's law in units of volatility to the 0.58** — the representation's
     "sizes exponential by default" kept, with the scaling added; the compensator follows
     from it.
   - **The article** owes the reader the whole method (decision 8), the weighting finding
     with it, and its sources as the *Sources* table assigns them. Sergei (2026-11-22): the
     method is worth a big section of the article, or an article of its own.
   - **What is new, and what is not** (2026-11-22: first from a search, then corrected on
     reading the papers Sergei supplied the same day; the bibliography entries carry the
     pages).
     - **The down-jump kick** has one precedent, [`patton-sheppard-2015`]. On five-minute
       prices for 105 stocks they find negative jumps raise future volatility and positive
       ones lower it. Here the same holds in daily data, parametrically.
     - **Maheu and McCurdy are not that precedent**, as the first version of this bullet said
       [`maheu-mccurdy-2004`]. In their GARCH-jump model a jump feeds back into volatility
       *less* than an ordinary move, and the bad-news asymmetry mostly vanishes when a jump
       occurs. Their worked jumps are earnings surprises. What they do show is jump
       clustering, which the fitted model leaves out (a constant jump rate): a limitation to
       state.
     - **Earnings and unscheduled jumps: Ederington and Lee's decomposition, replicated —
       not a difference of kind** (searched three ways, then read, 2026-11-22; this bullet
       first said they "feed back differently", which the surprise-scaled test below
       withdraws). [`ederington-lee-1996`] showed scheduled releases resolve uncertainty and
       unscheduled ones create it, in implied volatility around macroeconomic news. Their
       decisive result is that implied volatility answers the day's *unexpected* volatility
       the same way whichever kind of day brought it. Measured against its kind's typical
       size, an earnings move here raises realized volatility as an ordinary move of the
       same surprise does (`earnmoves.kick_by_surprise`, under (C) below).
       Patell and Wolfson (1979, 1981) showed implied volatility rising into earnings and
       falling after [`patell-wolfson-1981`, read 2026-11-22]. Their realized variance is
       back near normal two days after the announcement (variance ratios 3.34 on the day,
       2.01 the day after, 1.24 the day after that, not significant). That is a partial
       precedent for the earnings jump leaving volatility where it was, over two days and on
       1976–77 data, with no comparison to unscheduled moves. [`dubinsky-et-al-2019`] model
       earnings as jumps at known dates whose
       variance leaves the options once the date passes, with the diffusive volatility
       unmoved. No study found compares the *realized* volatility after an earnings jump
       with that after an unscheduled jump of the same size in a single stock:
       - Maheu and McCurdy pool the two.
       - Patton and Sheppard's intraday data leave out the overnight returns, where
         [`christensen-timmermann-veliyev-2024`] put most earnings jumps.

       So the claim: Ederington and Lee's decomposition holds in single stocks' realized
       volatility, with the same answer — the expected part of a scheduled move leaves
       volatility alone, and the surprise raises it as any surprise does — measured with
       calendar-block errors and carried into the model. The principle and the decomposition
       are theirs.
     - **The weighting finding** is Petersen's panel lesson [`petersen-2009`] carried to
       simulated-moment weights. His bootstrap of firm clusters is our name bootstrap,
       and it assumes no correlation across firms. His clustering by time needs enough
       periods, and our eleven blocks are at the low end of that (13–19% understated at ten,
       in his simulations). The jackknife itself is [`kunsch-1989`]'s deletion on
       non-overlapping blocks (Carlstein's arrangement), carried to a panel.
     - **The rest:** two factors are Chernov et al.'s; single stocks' weaker leverage is
       Bouchaud, Matacz and Potters'; the tables' variance reductions are textbook
       [`glasserman-2003`].
     - **What the article can claim as its own:**
       - the population: the live account's universe, admitted by date;
       - the numbers;
       - the consequence for the wheel: §09's correlation of −1.0 is the down-jump kick,
         not a size effect;
       - the earnings split above, once checked.

       Open: whether volatility needing no shocks of its own is new. It is a statement about
       what these 48 statistics can see.
   - **Shared episodes** — half the down jumps on market-wide days, and the weights' factor of
     thirteen — are the account-level effect step 7 has to carry; one stock's model does not.
5. **The simulator.** `wheel_sim.py` carries the process — jumps and earnings included — and
   prices options fair at the state, which is II-39's proper pricing. One reading needs no
   calibration and can run first: how much of d's tail the present `--scenario stochvol`
   explains.

   **Run 2026-11-21** (scratch `d_tail.py`, wrapping `Lot.__init__`; `--scenario stochvol`'s
   three runs, 1,280 paths × 30 years each, seed 20260722): the acquisition gap g = 1 − S/K at
   assignment, the statistic `model_vs_live.py` reports as T2 and the pre-registration's P5
   tracks.

   | run | assignments | mean g | median g | mean/median | g > 5% | g > 10% |
   |---|---|---|---|---|---|---|
   | constant σ | 398,792 | 1.53% | 1.21% | 1.26 | 1.8% | 0.0% |
   | moving σ, no leverage | 402,863 | 1.36% | 0.92% | 1.48 | 3.0% | 0.2% |
   | moving σ, ρ = −0.9 | 390,461 | 1.60% | 1.05% | 1.52 | 5.0% | 0.5% |

   The live account reads 2.3× over 68 assigned lots (`model_vs_live.py`, rerun the same
   day). Moving volatility alone takes the ratio from the lognormal's 1.26 to about 1.5, a
   quarter of the way to the live figure. Two cautions before the remainder is put down to
   jumps: the live lots pool names of very different volatility, and mixing scales raises a
   mean/median ratio by itself, which one simulated stock does not do; and 68 lots is a ratio
   carried by a handful of deep ones. Step 3 compares like with like, each live gap measured in
   its own name's σ·√τ_p. The mean d against the sale price, 3.75% at constant σ, is
   eq:d-mean's 3.8%.

   **Design, proposed 2026-11-22** (awaiting Sergei's go-ahead). Four pieces, in order:
   - **(a) The earnings law, measured directly.** Earnings days are dated, so they need no
     simulation. Each date's two-session move, in units of the yardstick before it, is fitted
     by maximum likelihood as two days' diffusion plus one double-exponential jump, separate
     up and down sides (decision 3), its size scaling as σ^β_E. Two checks on the data decide
     the shape: whether the utilities' and REITs' moves are smaller (the sector split of
     *Calibration*), and whether volatility steps after the date. The fitted model has no
     earnings term in h, because earnings windows were masked out of the fit.
   - **(b) The process in `wheel_sim.py`.** The fitted model, stepped by session, five a
     week: two factors, θ, the down-jump kick, Kou jumps scaled by σ_t^0.58, and an earnings
     jump every 13 weeks at a phase drawn per path. The fit's statistics are scale-free, so σ̄
     is free; it is set so that the total variance (diffusion, jumps and earnings) averages
     σ², and the article's 20% stays the stock's whole volatility. The drift is compensated
     so the mean stays m. A new process beside the present one, which §09 quotes and keeps.
     `wheel_sim.py` stays stdlib.
   - **(c) Fair prices at the state.** Under decision 4 the pricing measure moves the
     diffusion's drift to r − δ and keeps the real-world law of the jumps and earnings. With no
     volatility shocks of its own (η = 0), the volatility risk decision 4 leaves unpriced is
     empty: every move of h is the stock's own, so "fair" has one meaning. Prices are read
     from tables built beforehand by Monte Carlo (numpy, a new `code/fairprice.py`, cached):
     implied volatility over a grid of the two factors and moneyness, for the put's five
     sessions and the call's twenty, under both measures. The pricing measure gives the
     premiums; the real-world one gives the strike for the dial p\*, now a quantile of the
     same table. Earnings enter by one quadrature over their law at a shifted strike, which
     holds if (a) finds the earnings move independent of the path; otherwise the sessions to
     the date become a table dimension. Rejected: a three-dimensional lattice (price and two
     factors) by backward induction, exact to its grid but much more code, where the tables'
     Monte Carlo error is controllable and (d)'s first test measures it.
   - **(d) The tests.** At m = r − δ the excess must be −leak to the tables' accuracy: the
     check that the tables price the simulator's own process. The real-world test, excess =
     Δ̄·(μ − r) − leak, takes Δ̄ as the sensitivity to the diffusive shock through both of its
     channels, the price and h (θ times the vega); its form on the session lattice, which
     decision 4 left to be derived, is derived here. Constant σ stays byte-identical.

   Then the d-tail reading again, on the fitted process, against the live 2.3. Sergei,
   2026-11-22: "Yes, please go ahead with both" (the tables, and the earnings law fitted
   directly).

   **(a) The earnings law, measured 2026-11-22** (`code/earnmoves.py`; `--recover` for the
   model's units). 4,322 dated windows on all 68 names. In yardstick units the two-session
   move has mean |s| 2.85, against 1.13 for two sessions of diffusion alone.
   - **The law** (yardstick units, block-jackknife errors): up with probability
     0.516 ± 0.017, mean size up 2.36 ± 0.13, down 2.63 ± 0.16, β_E 0.13 ± 0.12. Its tails
     match the data's: beyond 2, 3, 4, 6 and 8 local sd, 26.8, 18.0, 11.9, 4.9 and 2.0% of
     windows up against 25.4, 16.9, 11.1, 5.0 and 2.4% fitted; down 26.1, 18.8, 12.8, 5.6 and
     2.8% against 25.2, 17.4, 11.9, 5.8 and 2.9%.
   - **Size barely follows the state.** Mean |s| by tercile of h is 3.49, 2.85 and 2.19 — in
     local sd, so in log terms an earnings move is nearly the same size in a calm quarter as in
     a turbulent one. Sizes in units of today's volatility (β_E = 1) are rejected (likelihood
     ratio 249), and so are the unscheduled jumps' β = 0.58 (65).
   - **Sector.** Utilities and REITs move about half as much: mean |s| 1.74 and 1.57 against
     2.94, their law up 0.63, sizes 0.97 ± 0.20 and 1.60 ± 0.27. They are 325 of the 4,322
     windows, so the pooled law is the others' (2.46 and 2.70). The simulator carries the
     pooled law; the sector law is a variant.
   - **No kick.** After an earnings fall beyond 6 local sd, log volatility rises 0.16, against
     0.54 after an ordinary fall that size; after an earnings rise it moves −0.04 to +0.06,
     where ordinary rises raise it 0.14 to 0.42. The fitted model with the earnings jump kept
     out of h gives +0.12 and +0.06 on fake dates, within about 0.05 of the data at every band
     (the data lower after rises: a mild crush the model lacks). The earnings jump does not
     enter h; the resolution of the news is why. *Refined the same day under (C) of "Acting
     on the reading" below:* measured against an earnings day's typical move, the surprise
     raises volatility as an ordinary surprise does, and it is the expected part that leaves
     it alone; the model, leaving both out, misses a small crush and a small surprise
     response, each worth about 0.05 in log volatility.
   - **In the model's units** (a jump e^(β_E·H)·Y, H the model's log volatility, σ̄ at H = 0):
     up 0.523, sizes 4.73 and 5.22, β_E 0.25. Its fake fits on the data's mask and dates
     reproduce the data's estimates (2.31 and 2.59 against 2.36 and 2.63, β_E 0.13 against
     0.13). The sizes double because H = 0 is not the typical state: the fitted model's median
     H is 0.81 (5–95%: 0.30 to 1.58), and the yardstick's noise attenuates β_E from 0.25 to
     the measured 0.13, as an error in h must.

   **(b) and (c), built 2026-11-22.** `code/volprocess.py` pins the fitted process and the
   earnings law (stdlib) and steps it a session at a time; `code/fairprice.py` builds the
   fair-price tables (numpy, cached under `data/fair/`); `wheel_sim.py --scenario fittedvol`
   carries both.
   - **The scale.** σ̄ is set so that the year's variance averages σ²: at σ = 20%, 0.0039 a
     session. Of the variance, diffusion is 81%, unscheduled jumps 7% and earnings 12%, and
     the diffusive volatility at the median state is 14.2% a year. A simulated six years
     on 400 paths give 0.1994.
   - **The pricing measure.** With no volatility shocks of its own, the change of measure is
     one shift of z, κ_t = (μ − r)·Δt/σ_t, and h follows the shifted shocks.
   - **The tables.** 13 × 11 nodes of (h_fast, h_slow), 200,000 paths each, one set of draws
     for every node. Puts at the dial, calls at 111 depths and four tenors (20 sessions left
     for the premium, 15, 10 and 5 for an open call's delta and mark), every phase of the
     earnings cycle. The accuracy was found the hard way:
     - Plain draws left about 0.3% in implied volatility. One set of draws for every node
       makes that error a level common to the whole table rather than noise, so it would
       have been a few basis points of premium a year. Two changes took it to about 0.1%
       for a put and a near-the-money call (0.2% with earnings in the window):
       stratifying each path's total shock (a Brownian bridge), and the terminal price as
       a control variate with its regression coefficient. A control on realized variance
       gained nothing.
     - Linear interpolation in the state priced every option about 0.1% high, because log
       implied volatility is convex in the state; cubic takes that to 0.01% or less for
       puts and near calls (`fairprice --check`).
   - **The pricing-measure test passes.** At μ = r the excess plus the leak is
     −0.001% ± 0.012% on the fitted process, against +0.003% ± 0.013% at constant σ (640
     paths × 30 years each).
   - **First readings, real world** (640 × 30 years, against constant σ):

     | | constant σ | fitted process |
     |---|---|---|
     | economic excess | 1.493% | 1.493% |
     | E[I], lots | 11.4 | 10.8 |
     | up-beta / down-beta | 0.829 / 1.000 | 0.834 / 0.993 |
     | lots leaving at the first call expiry | 40.9% | 43.1% |
     | gap at assignment, mean / median | 1.26 | 1.54 |
     | gaps beyond 5% / 10% | 1.75% / 0.001% | 5.4% / 0.64% |

     The fitted process takes d's tail about as far as the borrowed index volatility with
     ρ = −0.9 did (1.52, 5.0%, 0.5%): about a quarter of the way to the live 2.3, with
     step 5's two cautions on that comparison still standing.

   **(d) Both exact tests pass on the fitted process** (`--scenario fittedvol`, 640 paths ×
   30 years a run):
   - **Pricing measure.** At μ = r, excess plus leak is −0.001% ± 0.012%.
   - **Real world.** Excess − (Δ̄·(μ − r) − leak) is −0.008% ± 0.017%, with Δ̄ = 0.934;
     constant σ gives −0.004% ± 0.016% at Δ̄ = 0.933.
   - **The delta on the session lattice.** An option's exposure to the shifted shock is
     ∂V/∂S + (share·θ·∂V/∂h_fast + share′·θ·∂V/∂h_slow)/(σ_t·S): the price's channel (with the
     smile, since depth moves with the price) plus the vega's, weighted by how far one sd of
     diffusive shock moves each factor per unit of the move it makes in the price. It is exact
     to first order in κ, about 0.009 a session at the median state.
   - **The volatility channel, measured and confirmed** (Sergei asked, 2026-11-22: "Do you think
     this is worth further digging?"). Read alone the test resolves 1.7bp, about the
     channel's whole size, so a run without it might have passed too. Two additions settle
     it:
     - **The split is exact.** The book's delta is recorded on the same dates through the
       price's channel alone, so the difference carries no noise of its own.
     - **The test is paired.** Each batch's pricing-drift run has the same draws (the drift
       moves no random number), and its excess plus leak is zero by no-arbitrage.
       Subtracting it, batch by batch, removes the noise the two share, along with any
       pricing error common to their tables.

     At 5,120 paths × 30 years (`--paths 5120`, about 35 minutes):

     | | Δ̄ | excess − (Δ̄·(μ − r) − leak), paired |
     |---|---|---|
     | constant σ, the reference | 0.932 | −0.4 ± 0.2bp |
     | fitted, both channels | 0.935 | −0.3 ± 0.2bp |
     | fitted, the price's channel alone | 0.929 | +0.7 ± 0.2bp |

     The volatility channel adds 0.006 to the book's delta, worth about 1.2bp a year at μ − r
     = 2%. With it the fitted process matches the constant-σ reference to 0.1 ± 0.3bp; without
     it, it misses by 1.1bp, about four standard errors. The test confirms the vega term
     decision 4 said it would gain. The reference's own −0.4bp is common to both (two
     standard errors, plausibly the delta's weekly sampling) and cancels in the comparison.
   - **The tables' level error shows at this resolution.** At μ = r the fitted process's
     excess plus leak is +1.1 ± 0.5bp at 5,120 paths (constant σ: −0.2 ± 0.4bp). That is the
     size the tables' 0.1% implied-volatility error predicts: options sold slightly rich, by
     a level common to the whole table. It is below everything step 7 will report except
     the excess return itself, and there it cancels if each excess is read against its own
     pricing-drift twin, as the paired test does. If step 7 needs the excess unpaired at
     the basis point, the remedy is more table paths: four times as many halves the error,
     for about twenty minutes a parameter set. Sergei, 2026-11-22: "Let's do both". So
     step 7 reads every excess paired, and the tables now pool four chunks of 200,000 draws
     a node (`fairprice.CHUNKS`). Rerun at 5,120 paths on those tables:
     - **The bias is gone.** At μ = r the fitted process reads +0.2 ± 0.5bp, against +1.1
       before. A put's implied volatility is good to 0.07% and a near-the-money call's to
       0.05%.
     - **The channel result holds.** Δ̄ is 0.935 with both channels and 0.930 through the
       price's alone. Paired, the reference reads −0.4 ± 0.2bp, both channels −0.5 ± 0.2bp
       and the price's alone +0.5 ± 0.2bp: 0.9bp off, about three standard errors.
     - **The build runs in parallel.** A row of nodes goes to each worker, eight at once.
       Each worker regenerates the same seeded draws, so the result is bit-identical to the
       serial build (checked): about five minutes against seventeen. Another session, asked
       by Sergei to look at the run's utilization, pointed out the idle cores. It also
       suggested reusing numpy buffers in the hot loop, which might save another 20–30%;
       that is left until a build is the bottleneck.
   - **Nothing else moved.** `--scenario dollars` and `stochvol` are byte-identical with the
     committed simulator, and `verify_examples.py` passes.

   **Where step 5 leaves the plan.** The simulator carries the fitted process with fair prices,
   so II-39's question can now be answered, and the magnitudes are step 7's. For the article's
   method section, one source to read and add: Glasserman (2003), *Monte Carlo Methods in
   Financial Engineering*, for stratification and control variates (not yet opened). (Since
   read; see the bibliography.)

   **Acting on the reading (2026-11-22).** Sergei: "Are we going to take action on the new
   findings? I think we should, rather than dismiss them." Three checks, each now in the
   code:
   - **(A) Jump clustering** (`volfit.py --clustering`, `volstats.clustering`). Maheu and
     McCurdy find jumps cluster, and the fitted model's jump rate is constant. The statistic
     is the count of moves beyond c local sd in the 20 sessions after one, over the same
     count after any day:

     | beyond | after a fall: data | model | after a rise: data | model |
     |---|---|---|---|---|
     | 3 sd | 2.80 ± 0.90 | 2.59 | 2.03 ± 0.70 | 1.68 |
     | 4 sd | 4.93 ± 2.47 | 3.54 | 3.14 ± 1.51 | 2.01 |
     | 5 sd | 6.17 ± 3.87 | 4.51 | 5.38 ± 2.16 | 2.02 |

     The data's errors are calendar-block jackknife; the model's figure is the mean of 8
     replicas. Tail moves do cluster, three to six times over. The model reproduces most of
     it through the volatility its kicks raise. The data sit above it at every threshold,
     within 1–1.6 errors each, and the six together add 3.7 to the distance, about what six
     well-fitted statistics should. So the data do not call for a self-exciting jump rate.
     The loosest point is after rises beyond 5 sd. The article states the constant rate as
     a choice the data allow, with this table, not as an omission.
   - **(B) The block length** (scratch `blocks_sensitivity.py`; the code's `BLOCK_YEARS`).
     Künsch and Petersen both say eleven blocks is few. Refitting nothing, the final model's
     distance and sandwich errors under each length:

     | blocks | distance over 48 | errors against two-year blocks |
     |---|---|---|
     | one-year, 22 of them | 9.8 | 1.08 to 1.20 times |
     | two-year, 11 | 13.5 | — |
     | three-year, 8 | 11.3 | 0.94 to 1.08 times |

     The fit holds at every length, and every parameter stays determined. The standard
     errors are uncertain by about a fifth, as Künsch's Theorem 3.3 says a jackknife on
     this few blocks must be. The article quotes the one-year errors, the larger, or states
     the fifth.
   - **(C) The earnings split, with errors** (`earnmoves.kick_split`): the kick after an
     earnings move beyond c against an ordinary day's, both sets' days in a calendar block
     deleted together.

     | | earnings | ordinary days | difference |
     |---|---|---|---|
     | fall beyond 3 sd | +0.087 ± 0.029 | +0.313 ± 0.077 | −0.226 ± 0.056 |
     | fall beyond 4 sd | +0.112 ± 0.029 | +0.431 ± 0.115 | −0.320 ± 0.096 |
     | fall beyond 6 sd | +0.158 ± 0.039 | +0.538 ± 0.153 | −0.380 ± 0.128 |
     | rise beyond 6 sd | +0.056 ± 0.034 | +0.418 ± 0.149 | −0.362 ± 0.123 |

     Three to four errors apart at every size and on both sides. The model with no
     earnings term gives +0.073, +0.088 and +0.122 for the falls on fake dates, within an
     error of the data.
   - **Earnings surprises** (Sergei: "What about earnings surprises?"). The first answer, that
     even a 6-sd earnings fall raises volatility only 0.16 against 0.54, measured both kinds
     of move in local sd. That is the wrong unit for a surprise: a typical earnings window
     moves 2.84 local sd against 0.81 on an ordinary day, so a 6-sd earnings move is a
     modest surprise for an earnings day. [`ederington-lee-1996`]'s test measures each move
     against what its kind of day was expected to bring. Run that way
     (`earnmoves.kick_by_surprise`; u is the move over its kind's mean |s|; calendar-block
     errors):

     | fall, u | earnings | ordinary | difference | model, fake dates |
     |---|---|---|---|---|
     | 1–1.5 | +0.013 ± 0.032 | +0.029 ± 0.007 | −0.016 ± 0.032 | +0.034 |
     | 1.5–2 | +0.077 ± 0.018 | +0.065 ± 0.010 | +0.011 ± 0.015 | +0.063 |
     | 2–3 | +0.162 ± 0.047 | +0.108 ± 0.016 | +0.054 ± 0.042 | +0.105 |
     | 3–5 | +0.200 ± 0.064 | +0.214 ± 0.045 | −0.014 ± 0.040 | +0.134 |

     | rise, u | earnings | ordinary | difference | model, fake dates |
     |---|---|---|---|---|
     | 0–1 | −0.061 ± 0.017 | −0.030 ± 0.008 | −0.030 ± 0.022 | −0.031 |
     | 1–1.5 | −0.051 ± 0.014 | −0.017 ± 0.009 | −0.034 ± 0.018 | −0.003 |
     | 3–5 | +0.156 ± 0.040 | +0.086 ± 0.031 | +0.069 ± 0.039 | +0.051 |

     Earnings and ordinary agree within an error at every band with enough events; only
     beyond five times (12 earnings falls) does a gap appear, at 1.7 errors. So Ederington
     and Lee hold here. The split in local sd is the expected part of a scheduled move,
     which leaves volatility alone; the surprise raises it as any surprise does. The model
     with no earnings term has neither part. It misses a small crush after mild earnings
     moves (−0.051 ± 0.014 against −0.003) and a small rise after big ones (+0.156 ± 0.040
     against +0.051), each about 0.05 in log volatility. A surprise against analysts'
     consensus would need I/B/E/S-type data, which EDGAR does not carry; the price's
     reaction is the measure used here.
   - **Open, for Sergei: an earnings term in h.** Feeding an earnings move to the factors
     at its surprise size would close the gap: as an ordinary move scaled by the ratio of
     typical sizes, with a small fall for the expected part. One or two parameters, fitted
     directly on the kick table as the earnings law was. It would mean rebuilding the
     tables. The effect is a few weeks of volatility about 5% off, four times a year:
     probably small for the wheel, which step 7 would measure. **Decided** (Sergei,
     2026-11-22): "if the contribution of the earnings to the wheel is small, to not include
     the parameter into the model, but explain why we simplify it in the article. We need to
     measure the effect first." So the term is measured before it is adopted, and left out
     with the reason stated if its effect on the wheel is small.

     **Measured the same day; left out.** The term is h falling c0 at each earnings session
     for the expected part and rising c1 per unit of surprise beyond the typical move.
     Fitted by indirect inference on the kicks after earnings by surprise band
     (`earnmoves.py --feedback`): c0 = 0.059 and c1 = 0.064, taking those ten bands'
     distance from 13.8 to 7.9. It was then run in the wheel, off and on, on the same draws
     (`wheel_sim.py --scenario earnterm`, 5,120 paths × 30 years):

     | on − off, paired | |
     |---|---|
     | excess, read against its μ = r twin | +0.4 ± 0.1bp |
     | E[I] | −0.008 ± 0.005 lots (−0.07%) |
     | up-beta, down-beta | −0.001, 0.000 |
     | gap mean/median | 1.535 → 1.539 |
     | gaps beyond 5%, 10% | +0.03, +0.015 points |

     For the article: the expected part's fall and the surprise's rise largely offset for
     the wheel, which holds options for weeks, not days. So the model keeps earnings out of h,
     and says so with these numbers. Two lessons from getting there:
     - On balance the term lowers volatility (total variance 4.6% less at the same σ̄). The
       term-on runs are therefore set at the σ whose tables give σ² a year once the term is
       in.
     - Re-matching σ̄ in the process alone, the tables unchanged, was tried first. It read
       the tables, not the term: options sold about 2.4% cheap in volatility and puts were
       struck too near. Inventory moved +2.5% that way, and −1.8% with no re-matching at
       all.
   - **To read when Sergei can get them:**
     - the published Petersen (2009), to check the draft's figures;
     - optionally Cornell (1978, *Financial Management* 7(1):54–59), events of predictable
       and unpredictable timing.

     Arrived the same day: Patell and Wolfson (1981) and Ederington and Lee (1996), as page
     images assembled into PDFs; the published Dubinsky et al. (2019), pp. 646–654 only.
6. **The overlay**, from the trade-log panel against the fair layer at the same state; the IBKR
   implied-volatility series if it can be had.
7. **Magnitudes**, result by result, from the simulator. Every excess return is read against
   its pricing-drift twin on the same draws, which removes the paths' shared noise and the
   tables' common pricing error (step 5(d)). Then `model.py` (h on 10–15 nodes, the
   depth walk modulated by them) and where in the article it lives — a revision of Part II, or
   the model kept and the difference reported where the assumption bites. Decided then, on the
   measurements.

   **Design, agreed 2026-11-22** (Sergei: "yes, please start the step 7 runs"):
   - **Four processes, each at total variance σ²:**
     - constant σ;
     - the fitted factors without jumps or earnings (θ alone moves h);
     - with the unscheduled jumps and their kick;
     - the full fitted process with earnings.
     Each step attributes its part of the difference, and each gets its own tables at its
     own σ̄ (the earnings-term lesson: tables must match the process's variance).
   - **Both regimes:** Standard p\* = 20% and Conservative 10%.
   - **Horizons:** 30 years for every result, and 5 and 10 years for inventory and the
     excess, which Part II quotes at those horizons. 5,120 paths each.
   - **The results, by section:**
     - **§05:** the assignment rate, and E[d] with its tail (mean/median, beyond 5% and
       10%).
     - **§07:** the median and mean holding time, the survival curve, the share leaving at
       the first expiry.
     - **§08:** E[I] at 5, 10 and 30 years, the census by depth, both capitals.
     - **§09:**
       - the economic excess, paired with its twin;
       - the book's delta, split by channel;
       - the up- and down-betas;
       - the excess's sensitivity to a volatility point of spread (σ_IV + 1 point,
         paired), the article's 45bp;
       - the Conservative regime's figures.
     - **§10:** the two boundaries. Where lots stop returning and capital stops returning,
       from the fitted process's long-run growth of log S and of 1/S, measured by
       simulation, set against μ − δ > σ²/2 and μ − δ > σ².
   - **Deferred: §11, the constrained account.** Its simulator monitors a barrier by
     Brownian bridge, which jumps break, and `wheel_sim` refuses the fitted process there.
     Carrying it means checking the barrier session by session. Taken up after these
     numbers, if they say Part II is revised.
   - **Output:** a `--scenario magnitudes` printing each result for the four processes and
     both regimes, with errors. The plan records the tables, and from them, the decision
     on `model.py` and where the change lives.
   - **Cost:** 16 sets of tables (four processes, two regimes, two drifts), about five
     minutes each in parallel. Then about 40 runs, a few hours in the background in all.

   **Started 2026-11-22** as `python code/wheel_sim.py --scenario magnitudes`: 64 runs at
   5,120 paths, and 12 new sets of tables (the constant-σ runs need none). Results go to
   `data/magnitudes.json`, each figure with its error across batches, and the log to
   `data/magnitudes.log`; both are gitignored and rebuilt by rerunning. **To pick up:** read
   the log's tables, which give each regime and horizon across the four processes, and
   record them here result by result. Then decide where the change lives, and carry the
   §10 boundaries (not in this scenario: the long-run growth of log S and of 1/S under each
   process, by simulation) and §11 as the design says.

   **Results, 2026-11-22** (rerun after the memory fixes and INF-9; about 15 minutes in all).
   Standard regime, 30 years, constant σ → the full fitted process, with the two steps
   between; errors in `data/magnitudes.json`.

   | result | constant | factors | +jumps | full |
   |---|---|---|---|---|
   | excess + leak, against its twin | 186.0bp | 186.8 | 186.1 | 186.1 (± 0.2–0.3) |
   | book delta (price channel alone) | 0.932 | 0.936 (0.931) | 0.934 (0.928) | 0.934 (0.928) |
   | one volatility point of spread (unpaired, same draws) | +45.4bp | +45.1 | +47.6 | +48.1 |
   | assignment rate | 0.200 | 0.199 | 0.200 | 0.200 |
   | gap at assignment: mean | 1.53% | 1.61% | 1.66% | 1.65% |
   | gap: mean/median | 1.26 | 1.29 | 1.51 | 1.54 |
   | gaps beyond 5% | 1.8% | 2.8% | 5.3% | 5.5% |
   | left at the first expiry | 40.7% | 42.0% | 43.3% | 42.8% |
   | E[I], 30 / 10 / 5 years | 11.34 / 7.29 / 5.26 | 11.03 / 7.11 / 5.19 | 10.64 / 6.82 / 4.99 | 10.66 / 6.92 / 5.11 |
   | mean holding E[I]/λ, years | 1.09 | 1.06 | 1.02 | 1.03 |
   | up-beta / down-beta | 0.827 / 1.000 | 0.842 / 1.001 | 0.840 / 0.993 | 0.834 / 0.993 |

   The median holding time is eight weeks in every process (two call periods; the grid sets
   it). The Conservative regime runs alike:
   - the excess 182.4 → 183.0bp;
   - a volatility point 50.7 → 54.0bp;
   - E[I] at 30 years 5.48 → 5.37;
   - gaps beyond 5% 0.85% → 5.4%, mean/median 1.29 → 1.61.

   A caution for reading the output: the spread runs' "against its twin" figure is not the
   spread's worth. The twin is sold at the spread too, so the pairing cancels the edge
   itself. The spread's worth is the unpaired difference above, same draws, spread against
   none.

   **What the numbers say.** Moving volatility, jumps and earnings, priced fair, leave Part
   II's central results standing within a few percent:
   - **The excess return is unchanged** (186.0 against 186.1bp). The book's delta moves
     +0.002, the volatility channel included.
   - **The assignment rate holds at the dial.**
   - **The median holding time holds at eight weeks.**
   - **Inventory and mean holding fall 3–6%** (5 to 30 years), as lots leave a little sooner.
   - **A volatility point is worth 6% more** (48 against 45bp), the jumps' part.
   - **The up-beta rises 0.007 and the down-beta falls 0.007.**

   What moves a lot is d's tail, the gap at assignment. Its mean/median goes from 1.26 to
   1.54 and gaps beyond 5% triple, almost all from the jumps; the live account reads 2.3.

   Claude proposed keeping the constant-σ model in Part II and reporting the difference where
   the assumption bites. **Sergei overrode it, 2026-11-22:** "The gaps at assignment are
   important. This is what brings 'pain' to the stakeholders and should not be dismissed
   lightly. Where practical and relevant, we can list both simplified model and
   variable-sigma model's results side by side." So:
   - **Part II carries the variable-σ model's results.** Wherever practical and relevant,
     they sit side by side with the simplified constant-σ model's: the closed forms stay,
     as the simplified model that explains the mechanism, and the fitted process's figures
     stand beside them.
   - **The gap at assignment gets prominence**, as the cost a stakeholder actually feels: its
     tail (mean/median 1.54 against 1.26, gaps beyond 5% tripled), set against the live
     account's 2.3 where Part IV compares.
   - **To be decided as each section is revised:** where the side-by-side form serves and
     where one figure is enough; and whether `model.py` carries h (the plan's step 7) or the
     variable-σ figures come from the simulator alone.

   §10's boundaries and §11 are not yet measured.
