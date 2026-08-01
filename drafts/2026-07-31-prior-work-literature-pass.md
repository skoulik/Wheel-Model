# Prior-work literature pass

**Date:** 2026-07-31
**Purpose:** the reading pass owed by [TODO I-1](../TODO.md). Not a bibliography for
`sections/03-prior-work.md` — that comes later, and a skeleton for it is proposed at the end.
This document does three jobs: **harvest** ideas and methods from published work,
**cross-check** our own results against theirs, and **test the novelty claim** the article
currently asserts without evidence.
**Nothing in `sections/` was changed by this pass.**

---

## 0. How to read this, and what it is worth

### Source discipline

Preference went to peer-reviewed work with heavy citation counts (*Journal of Finance*, *Review
of Financial Studies*, *Financial Analysts Journal*, *Journal of Derivatives*, *Journal of
Financial Economics*, *Mathematical Finance*, *Operations Research*), plus a small number of
white papers that the academic literature itself cites (CBOE, AQR, Goldman). Practitioner blog
material was read only where it was the *primary* source for an index definition, and is
otherwise excluded.

Every citation below was re-found by search rather than quoted from memory, and each carries a
**read level** so that a later editor knows how much weight it can take:

| tag | meaning |
|---|---|
| **[F]** | full text read (PDF downloaded to `literature/`, extracted, and the relevant passages read) |
| **[P]** | partial — specific tables or sections read, not the whole paper |
| **[A]** | abstract, publisher summary or secondary description only — **do not quote a number from these without opening the paper** |

Downloaded PDFs live in `literature/`, which is **gitignored** (a line was added to
`.gitignore` by this pass). They are reference copies, not ours to redistribute.

### The one-paragraph verdict

The finance literature **strongly confirms the article's central economic claim** — that at fair
option prices the wheel is a repackaging of equity exposure and nothing more — and it confirms
it from three independent directions (Israelov & Nielsen's decomposition, Hill et al.'s
attribution, and the index record itself). The applied-probability literature **gives four of our
constructions proper names and better citations than the ones we currently use**, and one of them
(Brumelle's H = λG) is a stronger theorem than the derivation we wrote by hand.

Against that, the pass turned up **one substantive divergence that affects a headline sentence**
(§09 attributes an index-level volatility risk premium to single names, where the literature says
the single-name premium is between a third and zero of that), **one unexplained empirical fact
our model has no mechanism for** (weekly put-writing has historically underperformed monthly),
and **one claim that must be softened** (the novelty of applying Little's law to a portfolio of
assets — John Little himself gives that example).

### Disposition — what this pass turned into

Conversion into [`TODO.md`](../TODO.md) items ran 2026-07-31 to 2026-08-01, one finding at a
time, and is **complete**. This table is the map, and the inline markers below repeat it at each
finding. **Nothing here edits the findings themselves**: a converted finding keeps its original
text, and the TODO item is where the decisions, the corrections and any later amendments live.

| finding | became | |
|---|---|---|
| **D1** — index VRP quoted at a single-name model | **TODO II-18** | §03's citation half stays with I-1 |
| **D2** — the live account's +10 points | **TODO IV-5** | reshaped on conversion, see below |
| **D3** — weekly against monthly cadence | **TODO II-19** + **INF-6** + a line in **IV-3** | the test D3 asked for was run, see below |
| **D4** — the risk decomposition we cannot report | **TODO II-20** + **II-21** | H4's prescription contained a trap, see below |
| **D5** — Merton–Scholes–Gladstein unverified | **TODO I-5** — **closed 2026-08-01** | read in full; the summaries were wrong and both papers support us. Four items fell out |
| **D6** — Part III's diversification pricing problem | **TODO III-3**, with pointers in III-1 and III-2 | converted speculatively — it constrains sections not yet written |
| **N1–N3** — the novelty claim | **TODO I-1** | all three narrowings folded into the rewritten item |
| **H1** — Brumelle's H = λG | **TODO II-22** | the identity was checked numerically on conversion, see below |
| **H2, H3, H9** — the missing attributions | **TODO II-23** | grouped, then extended the same day to six citations — see below |
| **H4** — report a beta | **TODO II-20** (+ **II-21**) | converted with D4 on 2026-07-31; its prescription contains a trap |
| **H5** — the three-way decomposition | *inside* **II-20** | flagged adjacent, adopted only if it earns its space; no item of its own |
| **H6, H7** — Hill et al.; Broadie–Chernov–Johannes | folded into **IV-1**, with a line in **IV-2** | the section already owned the bullets these sharpen |
| **H8** — the disposition effect | **TODO II-24** | §08 rather than §16; the pass left the choice open |
| **H10** — Muravyev & Pearson on costs | folded into **IV-3** | with **tax**, which had no home anywhere |
| **H11** — Goyal & Saretto | folded into **IV-2** | converted as a *distinction*, not as support — see the marker |

Of §7's second-pass list, three items were converted with the harvest: **early exercise** became
**TODO II-25**, the **citation-graph pass** became **TODO I-6**, and **tax** went to **IV-3**.
The rest stay as written — they are waiting on Part III, on IV-5's re-cut, or on I-5.

**The cross-check's confirmations became an item of their own.** Rows **1, 3, 4 and 5** — where
independent work reaches *our* conclusion rather than lending us machinery — are **TODO II-26**,
converted 2026-08-01. The trigger was a count: §09 and §11 carry **no citations at all**, so the
section stating that at fair prices the wheel is indistinguishable from owning the stock reads as
though the question were untouched, when Israelov & Nielsen reach the same place from a
decomposition this article never uses. That is the strongest external support in this document and
it was, until the sweep, the least likely to reach a reader.

**Three things outside the findings were converted as well**, on 2026-08-01, because no item
carried them and each is an *instruction* rather than a reference. Strand F's "do not cite as
evidence" on **Kuang & Lin** went into **I-1** beside D5's prohibition, and is the likelier trap
of the two: it is the only recent paper on the wheel by name, so §03's author will find it while
looking for exactly this. Cross-check rows **2** (Goetzmann on Sharpe manipulation) and **13**
(Santa-Clara & Saretto on margin calls), together with Strand B's **Myth 8** — the "buy a good
company at a discount" slogan the article quotes in §02 and refutes in §09 without saying anyone
else has — extended **II-23** from three attributions to six, under a rule that item now states
explicitly: **the citation lands in the prose where the reader meets the claim**, not only in §03.

**The two unread downloads have owners.** `covering-the-world` (**unread**) belongs to **I-1**,
whose §03 subsection 2 is otherwise entirely US index data and would be generalising silently
without it; `li-zhang` (**skimmed**) belongs to **II-23**, whose autocallable pointer is a claim
about what that literature contains. Both are recorded as reads to be done before the *writing*,
not before the item.

**Four findings changed materially on conversion. The TODO items, not this document, carry the
corrected version.**

- **D2.** Most of the +10 points is a **clock mismatch**, not skew: `iv_panel.py` inverts with
  calendar τ while realised volatility is annualised over 252 sessions, which inflates only the
  short leg — about six of the ten points, and it reproduces the put-versus-call asymmetry on its
  own. D2's prescription also turned out to be *feasible*, which D2 doubted: the call strike is
  frozen at the lot's basis, so shallow lots write near-money calls by design, and the cross-tab
  can be built for free. It remains too thin to calibrate from.
- **D3.** Cadence-neutrality resolved as D3 expected (13 bp across a 13× range), but the mechanism
  is derivable from Bondarenko's own table: WPUT collected 1.68× PUT's premium where √-scaling
  predicts 2.08×, so weekly implied volatility ran at 0.81 of monthly. D3 also missed that §09's
  list of what the single σ_IV omits has **no tenor axis**, while the running example straddles
  one. Running the test surfaced an unrelated harness defect, hence INF-6.
- **D4 / H4.** The split beta was computed on conversion: **up 0.83, down exactly 1.000**, the
  asymmetry governed by n rather than by p\*. But **H4's prescription contains a trap**. Validated
  on a permanently at-the-money book it returns up 0.000 / down 1.000 against BXM's published
  0.63 / 0.78 — a terminal-payoff regression on an ATM call must, because the payoff is kinked at
  the strike, while BXM's figures come from calendar-monthly returns misaligned with the roll.
  Followed literally, H4 would have produced "the wheel's up-beta is 0.83 against BXM's 0.63" as
  though it were like-for-like. II-21 exists to keep that comparison a detour.
- **H1.** The H = λG mapping was checked numerically rather than asserted, and it is **exact** —
  per-arrival against census, agreeing to 0.000% on all four weightings. Two things this section
  did not know: **`model.py` already computes the H = λG side** (`occupation()` returns the
  per-arrival sums and `economics()` multiplies by λ), so only the prose derives anything by hand;
  and the theorem hands **§10** a better statement of the capital criterion than §08 gains from
  it — θ > 1 is exactly "G is finite at f = e^x". II-22 is therefore a §08 *and* §10 item.
- **Early exercise** (§7's list, now II-25). The pass flagged Bakshi & Kapadia's ~2 volatility
  points as "not nothing" against a caveat that merely asserts the omission is conservative. On
  conversion it turns out **not to bind, for a structural reason**: our calls are OTM on every
  date one is written, since the strike is frozen at the lot's basis and a lot survives only while
  x > 0, and 2 points is a *near-money* figure. The item carries the sizing of the one channel
  that could bite.

**One defect in this document, recorded rather than corrected.** Strand B cites
Merton–Scholes–Gladstein as "[A — unverified, see **D7**]"; the divergence is numbered **D5**, as
the reading list has it, so that pointer dangles. Left as written, since drafts are historical.

---

## 1. The literature, in six strands

### Strand A — What systematic option writing has actually returned

This is the empirical record against which any model of the wheel is eventually judged. The
canonical instruments are CBOE's strategy benchmark indices.

- **Whaley (2002)**, *Return and Risk of CBOE Buy Write Monthly Index*, J. Derivatives 10(2):35–42
  **[A]** — introduces BXM (long S&P 500, short ~ATM one-month SPX call). Over 1988–2001 the
  covered call earned nearly as much as the index with substantially lower risk. This is the
  paper that made "covered calls have a better Sharpe ratio" a stylised fact.

- **Israelov & Nielsen (2014)**, *Covered Call Strategies: One Fact and Eight Myths*, FAJ
  70(6):23–31 **[F]** — Table 1, 1 July 1986 – 31 December 2013, returns in excess of cash:

  | | S&P 500 | BXM |
  |---|---|---|
  | annualised excess return | 5.4% | 4.4% |
  | annualised volatility | 18.5% | 13.4% |
  | Sharpe | 0.29 | 0.33 |
  | worst drawdown | −61.7% | −43.0% |
  | beta | 1.00 | 0.67 |
  | *upside* beta | 1.00 | 0.63 |
  | *downside* beta | 1.00 | 0.78 |

  The split beta is the number to keep: the covered call is **more exposed on the way down than
  on the way up**, which is the payoff diagram restated as a risk statistic.

- **Bondarenko (2019)**, *Historical Performance of Put-Writing Strategies*, CBOE white paper
  **[F]** — PUT (monthly ATM SPX put-write, fully collateralised) against the S&P 500 over
  June 1986 – December 2018: compound return **9.54% vs 9.80%**, standard deviation **9.95% vs
  14.93%**, Sharpe **0.65 vs 0.49**. Volatility risk premium 1990–2018: average VIX **19.3%**
  against average realised **15.1%**, a spread of **4.2 points**. And the finding that matters
  most to us, over 2006–2018:

  | | PUT (monthly) | WPUT (weekly) | S&P 500 |
  |---|---|---|---|
  | compound return | 5.97% | **4.51%** | 7.59% |
  | Sharpe | 0.50 | **0.40** | 0.51 |
  | std dev | 10.69% | 9.48% | 14.32% |
  | max drawdown | −32.7% | −24.2% | −50.9% |
  | **gross premium collected /yr** | **22.1%** | **37.1%** | — |

  **The weekly programme collected 1.7× the premium and earned less, on both raw and
  risk-adjusted terms.** See divergence D3.

- **Hill, Balasubramanian, Gregory & Tierens (2006)**, *Finding Alpha via Covered Index Writing*,
  FAJ 62(5):29–46 **[P]** — 1990–2005, fixed-strike S&P 500 buy-writes. Two things we can use.
  First, against a *delta-adjusted* S&P benchmark (long 1 − Δ of the index, the rest at LIBOR)
  the ATM strategy outperformed by **5.5 pp**, 2% OTM by **4.5 pp**, 5% OTM by **2.2 pp** — i.e.
  they took the trouble to build an exposure-matched benchmark, exactly as our Track B ledger
  does. Second, their **four-way return attribution**: fair call premium / volatility premium /
  exercise cost / trading cost. Their conclusions, verbatim in substance:
  - "The bulk of the positive performance can be attributed to the fair call premium."
  - **"The cost of exercise ate away the largest proportion of the excess returns."**
  - "The volatility premium decreased as the strike moved farther out of the money."
  - Trading costs 3–6 bp/month at half an implied-volatility point of slippage.

- **CBOE CMBO** (S&P 500 Covered Combo Index), methodology document **[A]** — the closest
  published index to the wheel: short ATM monthly SPX put *and* short 2%-OTM monthly SPX call,
  with a long index position covering the call and T-bills covering the put. It is **not** the
  wheel: it holds both legs simultaneously and permanently, where the wheel alternates and its
  share count is a state variable. **No published index tracks the wheel.**

### Strand B — What the return *is*, once decomposed

- **Israelov & Nielsen (2014)** again **[F]** — the "one fact" is
  **ATM covered call = long equity (½ position) + short volatility (½ short straddle)**, so the
  strategy's expected return is the sum of an equity risk premium and a volatility risk premium
  and nothing else. Their stylised example (index at 100, one-month ATM call, index excess return
  6%, **IV 18%, realised 16%**): the option sells for $2.07, of which $0.23 (11%) is richness;
  delta 0.49 gives 2.94%/yr from equity, the richness gives 2.76%/yr, total **5.70%/yr**. And
  then the sentence that is our contribution 4 in someone else's words:

  > "If the option were instead priced such that its implied volatility is 16% — the same as
  > realized volatility — then even though the annual collected option premium is **22.1% of net
  > asset value**, there would be **zero compensation for shorting volatility** … the covered call
  > would simply earn the expected market excess return scaled by its exposure to its underlying
  > equity (2.94% per year), which is **no different from what would have been earned by simply
  > reducing the index position size by 51%**."

  The myths worth knowing by number, because four of them are the wheel's own marketing:
  **Myth 2** covered calls provide downside protection (they provide *very* limited support);
  **Myth 3** covered calls generate income ("income is revenue minus cost" — the zero-coupon
  bond analogy: cash from issuing a bond is not income); **Myth 4** high-volatility names and
  shorter tenors give higher yield ("price is not value" — 12 monthly ATM options generate ~3.5×
  the cash of one annual option and no more profit); **Myth 5** time decay works in your favour
  (only if IV exceeds *expected realised*); **Myth 7** you are paid for doing what you were going
  to do anyway ("an option is a contractual obligation, not a plan"); **Myth 8** covered calls
  (equivalently naked puts) let you buy a stock at a discount — which they demolish explicitly,
  and which is the wheel's central slogan.

  > **Three of the eight are converted; the rest are §03 material only.** Myth 2 → **II-20**,
  > where down-beta comes out exactly 1.000 in our own model; Myth 4 → **II-19**, cadence-
  > neutrality at fair prices; **Myth 8 → II-23**, landed at `eq:mark-loss`, which is where §09
  > already refutes the slogan §02 quotes — without saying anyone else has. Myth 3 is cross-check
  > row 2, and its *formal* half (Goetzmann on Sharpe manipulation) went to II-23 with it.

- **Israelov & Nielsen (2015)**, *Covered Calls Uncovered*, FAJ 71(6) **[P]** — a three-way
  attribution: passive equity, short volatility, and an **equity reversal (dynamic timing)**
  exposure that arises because the position's delta rises as the underlying falls. Results:
  passive equity carries most of the risk and return (Sharpe ≈ 0.41); short volatility has
  Sharpe ≈ 0.98 but **under 10% of the risk**; the reversal exposure carries **≈ 25% of the risk
  with Sharpe ≈ 0.10 — uncompensated**. Hedging it out lifts the strategy Sharpe (0.37 → higher)
  and cuts volatility 11.4% → 9.2%.

- **Goetzmann, Ingersoll, Spiegel & Welch (2007)**, *Portfolio Performance Manipulation and
  Manipulation-Proof Performance Measures*, RFS 20(5):1503–1546, and the companion
  *Sharpening Sharpe Ratios* (NBER w9116) **[A]** — Sharpe ratios can be manufactured by
  option-writing overlays; they characterise a manipulation-proof alternative. This is the formal
  version of §09's refusal to headline a cash yield.

- **Merton, Scholes & Gladstein (1978)**, J. Business 51:183–242, and **(1982)**, J. Business
  55:1–55 **[A — unverified, see D7]** — the original large-scale simulation studies of covered
  call and put-writing programmes. Secondary summaries describe the conclusion as the strategies
  "outperforming buy-and-hold", which I do not believe is the paper's actual claim and which
  would sit badly with everything else in this strand. **Flagged for full-text verification
  before it is cited anywhere.**

### Strand C — The volatility risk premium, and the index/single-name gap

This is the strand that produced the pass's most consequential finding.

- **Coval & Shumway (2001)**, *Expected Option Returns*, JF 56(3):983–1009 **[A]** — zero-beta
  at-the-money straddles on the index lose roughly **3% per week**; expected put returns are below
  the risk-free rate. Establishes that something beyond directional exposure is priced.

- **Bakshi & Kapadia (2003)**, *Delta-Hedged Gains and the Negative Market Volatility Risk
  Premium*, RFS 16(2):527–566 **[A]** — delta-hedged index option positions lose money on average,
  which identifies a negative *market* volatility risk premium.

- **Bakshi & Kapadia (2003)**, *Volatility Risk Premiums Embedded in Individual Equity Options:
  Some New Insights*, J. Derivatives, Fall 2003 **[F]** — **the key single-name paper.** 25 large
  US equities, 1991–1995, near-money short-dated calls:
  - average Black–Scholes implied volatility exceeds realised by **1.5 points** across the 25
    firms (all options), and by **1.07 points** once options with a dividend before expiry are
    dropped;
  - the same figure for **SPX is 3.3 points**;
  - delta-hedged gains lose **0.03% of the underlying** for single names against **0.07%** for
    the index;
  - **idiosyncratic volatility does not appear to be priced** — what little premium single-name
    options carry is the *market* volatility premium leaking through beta;
  - as an aside worth having: the American-exercise premium on their short-dated near-money calls
    is worth **about 2 volatility points**.

- **Carr & Wu (2009)**, *Variance Risk Premiums*, RFS 22(3):1311–1341 **[A]** — five indices and
  35 individual stocks. Index variance risk premia are strongly negative and robust to bid/mid/ask
  synthesis; for individual stocks the mean variance risk premium is **insignificant for all but
  three of the 35**.

- **Driessen, Maenhout & Vilkov (2009)**, *The Price of Correlation Risk: Evidence from Equity
  Options*, JF 64(3):1377–1406 **[A]** — the mechanism behind the gap: the index premium is
  substantially a **correlation** risk premium, not a variance premium that also exists on the
  components. They also report that the correlation premium **cannot be harvested once realistic
  frictions are imposed**. This is the single most important paper for the unwritten Part III.

- **Gârleanu, Pedersen & Poteshman (2009)**, *Demand-Based Option Pricing*, RFS 22(10):4259–4299
  **[A]** — demand pressure from end users explains both the overall expensiveness of index
  options and the shape of the skew, and it affects single-stock option expensiveness too. This is
  the reason the skew we descoped is not a market inefficiency waiting to be collected.

- **Goyal & Saretto (2009)**, *Cross-Section of Option Returns and Volatility*, JFE 94:310–326
  **[A]** — sorting stocks on implied-minus-historical volatility and trading straddles produces
  large, robust monthly returns. Relevant twice: it says the IV−RV spread is a real cross-sectional
  signal, and it is the published, options-based version of the "edge" the live account
  attributes to stock selection.

- **Muravyev & Pearson (2020)**, *Options Trading Costs Are Lower than You Think*, RFS
  33(11):4973–5014 **[A]** — traders who time executions pay effective spreads of **29.6%**
  (algorithmic) and **58.4%** (all traders) of the quoted half-spread. Conventional cost estimates
  roughly double the truth.

### Strand D — The probability machinery

This strand is where the harvest is largest, because it supplies names and pedigrees for
constructions the article currently derives from scratch.

- **Broadie, Glasserman & Kou (1997)**, *A Continuity Correction for Discrete Barrier Options*,
  Mathematical Finance 7(4):325–349 **[F]** — a discretely monitored barrier option is priced by
  the continuous formula with the barrier shifted by **exp(±β·σ·√Δt), β = −ζ(½)/√(2π) ≈ 0.5826**,
  where the sign depends on which side the barrier sits. They build on Siegmund's corrected
  diffusion approximation and Siegmund & Yuh (1982). **This is `eq:siegmund` exactly** — our
  call-grid tax is the Broadie–Glasserman–Kou barrier shift, in a setting where the "barrier" is
  the call strike and the "monitoring dates" are call expiries.

- **Siegmund (1979)**, *Corrected diffusion approximations in certain random walk problems*,
  Adv. Appl. Prob. 11(4) **[A]**; **Siegmund (1985)**, *Sequential Analysis* **[A]** — the origin
  of the correction, and what we currently cite.
- **Chang & Peres (1997)**, Ann. Probab. 25(2):787–802 **[A]** — the full asymptotic expansion in
  the Gaussian case, of which Siegmund's is the first term.
- **Janssen & van Leeuwaarden (2007)**, *On Lerch's Transcendent and the Gaussian Random Walk*,
  Ann. Appl. Probab. 17(2) **[P]** — exact expressions for the Gaussian random walk's
  all-time-maximum moments; the constant −ζ(½)/√(2π) drops out as the leading term.

- **Little (1961)** and **Little (2011)**, *OR Forum — Little's Law as Viewed on Its 50th
  Anniversary*, Operations Research 59(3):536–549 **[P]** — and this is the find of the pass.
  Little's retrospective presents the **generalised law H = λG** (due to **Brumelle 1971** and
  **Heyman & Stidham 1980**), in which each item carries an arbitrary weighting function
  *f<sub>i</sub>(t)* over its time in the system; L = λW is the special case f ≡ 1. Little's own
  worked example of a non-trivial weight is, verbatim, *"the dollar rate of return on the ith
  asset in a portfolio of assets"*, and he spells out that the finance application yields
  "the time average dollar return H and average dollar return per asset G, but also the average
  number of assets L and the average time of holding an asset, W."

  **Our income and capital integrals against the depth census are instances of H = λG.** See
  harvest H1 and novelty note N3.

- **Ladder heights and the Lundberg exponent [A]** — for Brownian motion with drift −ν and
  volatility σ, the all-time maximum is exponentially distributed with rate **2ν/σ²**. That is
  `eq:theta` — our census tail exponent θ = 2ν/σ² is the **Cramér–Lundberg adjustment
  coefficient** of classical ruin theory, and our capital criterion θ > 1 is a Cramér-type moment
  condition.

- **Dufresne's identity / exponential functionals of Brownian motion (Dufresne 1990; Yor 1992)**
  **[A]** — the perpetuity ∫₀^∞ exp(−2W_s^(μ)) ds is distributed as 1/(2γ_μ), and has a finite
  *m*-th moment **iff m < μ**. Structurally the same statement as ours (an exponential functional
  is finite exactly when a drift-to-variance ratio clears a threshold), but it is **not** literally
  our object; see the caution in H3.

- **M/G/∞ and infinite-server queues [A]** — the standard results are insensitivity of the
  stationary distribution to the service-time law, and Poisson occupancy/departures under Poisson
  arrivals. Directly relevant to III-1's promise about what is and is not Poisson.

- **Discretely monitored first passage / autocallables [A]** — a growing literature on pricing
  products that knock out only on scheduled observation dates (quadrature methods reaching
  O(1/N⁴) convergence; Hilbert-transform methods for the multi-asset case). **A wheel lot is an
  autocall**: it terminates at the first observation date on which the price is above a fixed
  level. This is the closest existing machinery to our holding-time problem.

### Strand E — The behavioural framing

- **Odean (1998)**, *Are Investors Reluctant to Realize Their Losses?*, JF 53:1775–1798 **[A]** —
  10,000 discount-brokerage accounts; investors are **1.5 to 2 times more likely to sell winners
  than losers**, not explained by rebalancing, transaction costs, taxes, or subsequent
  performance; for taxable accounts it is strictly harmful. With **Shefrin & Statman (1985)** this
  is the disposition effect.

  The wheel is a **contract that performs the disposition effect automatically and without
  discretion**: every winner is sold at the frozen call strike, and no loser is ever sold at all.
  Odean's investors do this 1.5–2× more often than chance; the wheel does it with probability one.

### Strand F — The wheel itself

Two arXiv papers exist and neither is a structural model. Both are recorded here for completeness
and for the novelty check.

> **→ TODO I-1**, converted 2026-08-01. The "do not cite as evidence" instruction below is now a
> **prohibition in I-1**, beside D5's, and is the likelier of the two to bite: this is the only
> recent paper on the wheel *by name*, so whoever writes §03 will find it while looking for
> exactly this. What I-1 permits is citing it **as existence** — two arXiv papers name the wheel,
> neither builds a structural model, which is N1's evidence — and nothing else.

- **Kuang & Lin (2025)**, *A Hybrid Architecture for Options Wheel Strategy Decisions:
  LLM-Generated Bayesian Networks for Transparent Trading*, arXiv:2512.01123 **[P]** — an LLM
  builds a per-trade Bayesian network from market context and populates it from an 18.75-year,
  8,919-trade dataset. Reported: **15.3% annualised, Sharpe 1.08 vs 0.62, max drawdown −8.2% vs
  −60%, and a 0% assignment rate maintained "through strategic option rolling."**
  **Treat with strong scepticism and do not cite as evidence.** A short-put programme that never
  takes assignment over nineteen years has not avoided the loss, it has rolled it forward; a
  −8.2% maximum drawdown for a short-put book spanning 2008 and 2020 is not credible on its face;
  and the backtest is in-sample with respect to the dataset the LLM selects from. It is listed
  because it is the only recent arXiv work on the wheel, not because it informs anything.

- **Svozil (2026)**, *Against a Universal Trading Strategy: No-Arbitrage, No-Free-Lunch, and
  Adversarial Cantor Diagonalization*, arXiv:2604.13334 **[P]** — three impossibility arguments
  (no-arbitrage, Wolpert–Macready, Turing diagonalisation) with the wheel as case study. The
  finance content is qualitative: strategies that succeed "for all practical purposes" depend on
  transient regime assumptions, so automating them amplifies tail risk. Consistent with our regime
  caveat, contributes no machinery.

---

## 2. Cross-check: our findings against theirs

Verdict key: **CONFIRMED** (independent work agrees), **CONFIRMS-US** (their result is evidence
for something we derived, not vice versa), **EXTENDS** (we say something they do not),
**DIVERGES** (flagged below), **UNTESTED** (nothing in the literature speaks to it).

> **Rows 1, 3, 4 and 5 → TODO II-26**, converted 2026-08-01 in the sweep that closed this
> conversion. The trigger was a count rather than a reading: **§09 and §11 carry no citations at
> all**, against three in §07 and one in §08 — so the section holding the article's headline
> result reads as though nothing had been written on the subject. Rows 2 and 13 went to **II-23**,
> row 14 to **IV-1**, row 15 to **II-18**, rows 16–20 are the divergences. Rows 6–9 are the
> machinery and are **II-22** and **II-23**; row 10 is **II-20** and **II-24**, the reversal
> exposure and the disposition effect. Only rows 11 and 12 need no citation, being EXTENDS —
> places where the article says something the literature does not.

| # | our finding | literature | verdict |
|---|---|---|---|
| 1 | At fair option prices the wheel is economically indistinguishable from owning the stock (§09, contribution 4) | Israelov & Nielsen (2014) stylised example: at IV = realised, a covered call earns *exactly* the delta-scaled equity premium despite collecting 22.1% of NAV in premium | **CONFIRMED**, in almost the same words |
| 2 | Cash income of 0.77 share prices/yr "is not a return at all" (§09 opening) | Israelov & Nielsen Myth 3 (income = revenue − cost; the zero-coupon-bond analogy); Goetzmann et al. on Sharpe manipulation by option overlays | **CONFIRMED** |
| 3 | Every point of σ_IV richness is worth ~45 bp of excess return; break-even is zero points | Same source: the entire volatility-premium contribution is the collected richness. Our 45 bp/point equals the extra premium (0.0531 share prices/point) divided by capital (11.59) = **45.8 bp** — a **100% pass-through**, which is also exactly what their example shows at a different notional-to-capital ratio ($0.23/month on $100 → 2.76%/yr) | **CONFIRMED**, and the two agree on the *mechanism*, not just the sign |
| 4 | The call-away giveaway is a first-class ledger term, and omitting it was a real error | Hill et al. (2006): "the cost of exercise ate away the largest proportion of the excess returns" | **CONFIRMS-US** — external confirmation that the term we nearly omitted is the dominant drag |
| 5 | Track B (exposure-matched, market-valued) is the right ledger, not Track A | Hill et al. benchmark against a *delta-adjusted* index; Israelov & Nielsen insist the comparison be made at matched equity exposure | **CONFIRMED** as standard practice |
| 6 | Call-grid tax β·σ·√τ_c, β = −ζ(½)/√(2π) ≈ 0.5826 (`eq:siegmund`) | Broadie, Glasserman & Kou (1997): identical constant, identical role — shift the barrier by exp(±βσ√Δt) | **CONFIRMED**, and we should be citing BGK |
| 7 | θ = 2ν/σ² as the census tail exponent; capital converges iff θ > 1 (`eq:theta`, `eq:capital-criterion`) | The maximum of Brownian motion with drift −ν is Exp(2ν/σ²); this is the Cramér–Lundberg adjustment coefficient | **CONFIRMED**, with a name we are not using |
| 8 | E[I] = λ·E[W] needs no independence assumption | Little (1961, 2011): the sample-path law needs only that the limits exist | **CONFIRMED** |
| 9 | Income and capital as integrals against the depth census | Brumelle's **H = λG**, of which Little's own example is a portfolio of assets | **CONFIRMED — and superseded**: there is a general theorem where we wrote a derivation (H1) |
| 10 | Inventory is dominated by deep, slow, unprofitable lots | Israelov & Nielsen (2015): the covered call's "equity reversal" exposure — you get longer as the price falls — carries ~25% of risk and is uncompensated. Odean (1998): the disposition effect, which the wheel automates | **CONFIRMED** from two directions; also **EXTENDS** — neither quantifies the standing census |
| 11 | Mean holding time 2.1 y against an 8-week median; exits only on the call grid | Nothing in the option-strategy literature computes the holding time of an assigned lot. The machinery exists (discretely monitored first passage / autocallables) but has not been pointed at this | **UNTESTED / EXTENDS** |
| 12 | Two stability boundaries, μ − δ > σ²/2 and μ − δ > σ² | Both are elementary GBM facts (log-drift sign; E[1/S] decay). No option-strategy paper states them as strategy stability conditions | **EXTENDS** |
| 13 | The finite account: survivable leverage 1.1–1.2×, ~19 share prices of equity per weekly put | Santa-Clara & Saretto (2009): margin calls "limit the notional amount of short positions and force investors out of trades precisely when they are losing money" | **CONFIRMED in kind**, not in magnitude — theirs is index puts on a margin schedule, ours is a wheel on one name; the two numbers are not comparable but the mechanism is the same |
| 14 | The overlay "earned nothing distinguishable from zero" over 14 months, 90% interval −19.8% to +7.6% | Broadie, Chernov & Johannes (2009): put returns carry such extreme sampling uncertainty that even deep-OTM put returns over 18 years are **insignificant** relative to Black–Scholes (p ≈ 8%), and CAPM alphas on option returns are *more* dispersed still | **CONFIRMED** — and it hands IV-1 exactly the citation it needs |
| 15 | σ_IV defaults to σ (no volatility risk premium assumed) | Bakshi & Kapadia (2003, JoD): single-name IV − RV is 1.07–1.5 points; Carr & Wu (2009): variance premium insignificant for 32 of 35 stocks; idiosyncratic volatility not priced | **CONFIRMED as a defensible default for single names** — arguably the *correct* default, which is a stronger statement than the article currently makes for it |
| 16 | "Implied volatility exceeds realised systematically, by 2–4 points on liquid equities" (§09:137) | That is the **index** number (SPX 3.3 points, VIX−realised 4.2 points). Single names: 1.07–1.5 points, and insignificant on a variance basis | **DIVERGES — D1** |
| 17 | The live account's put leg ran ~+10 IV points over subsequent realised | Literature single-name figure is ~1 point (near-money) | **DIVERGES — D2** |
| 18 | Cadence: weekly puts (τ_p = 1/52) as the running example | PUT (monthly) beat WPUT (weekly) 5.97% vs 4.51% and 0.50 vs 0.40 Sharpe, 2006–2018, despite 37.1% vs 22.1% gross premium | **DIVERGES — D3** |
| 19 | Diversification leaves expected return and capital unchanged (contribution 7, unwritten) | Little/Brumelle carry over directly, so the expectation half is safe. But Driessen–Maenhout–Vilkov means the *pricing* does not carry over: a basket of single-name wheels is not a wheel on the index, because the index option is dearer by the correlation premium | **UNTESTED — flagged for Part III (D6)** |
| 20 | Novelty of the inventory/queueing framing | See §4 | **PARTLY DIVERGES — N3** |

---

## 3. Divergences, in detail

Each carries what would settle it. **None of these was acted on; no section was edited.**

### D1 — §09 attributes an index-level volatility risk premium to single names

> **→ TODO II-18**, converted 2026-07-31. §03's citation half stays with I-1. The §09:152
> sentence is rewritten without printing a multiple, deferring the live account's own spread to
> §15 — the size of that gap is D2's measurement, not this one's.

**The claim.** `sections/09-returns.md:137` reads: *"implied volatility exceeds subsequently
realized volatility systematically, by 2–4 points on liquid equities, and this volatility risk
premium is the documented source of return in every put-write and covered-call study."*
Line 148 then says: *"against a documented premium of 2–4 points, the whole of it is edge."*

**The problem.** 2–4 points is the **index** figure — SPX 3.3 points (Bakshi & Kapadia), VIX minus
realised 4.2 points (Bondarenko). The single-name literature says something materially smaller:

- Bakshi & Kapadia (2003, JoD): **1.5 points** across 25 large caps, **1.07 points** excluding
  dividend-affected contracts, against **3.3** for SPX on the same measure;
- Carr & Wu (2009): variance risk premia **insignificant for 32 of 35 individual stocks** while
  strongly negative for every index;
- Driessen, Maenhout & Vilkov (2009): the reason — the index premium is largely a *correlation*
  premium, which by construction has no single-name counterpart;
- Bakshi & Kapadia (2003, JoD) again: **idiosyncratic volatility is not priced at all**.

The article's own model is a **single-name** model. Feeding it the index premium overstates the
edge by roughly a factor of two to three.

**What it costs us.** At our own 45 bp/point pass-through: 2–4 points → **0.9%–1.8%/yr** of
excess return, which is the number a reader will take away. The single-name literature supports
**0.5%–0.7%/yr** at 1.07–1.5 points, and something statistically indistinguishable from **zero**
on Carr & Wu's variance measure. The qualitative verdict — that the entire edge is the volatility
risk premium and there is no hurdle before it — is untouched. What changes is the size of the
prize, and it changes by enough to matter to a reader deciding whether to run this.

**A second-order sharpening.** Bakshi & Kapadia's single-name premium is what *leaks through beta*
from the market volatility premium. That predicts the single-name spread should scale with beta,
which is a testable structure the article could carry instead of a flat scalar.

**What would settle it:** a current (post-2010) single-name IV − RV estimate on the article's own
kind of universe — large-cap dividend payers — rather than a 1991–1995 sample of 25 names. The
live account's own `iv_panel.py` can produce one, but only after D2 is resolved, because it is
currently measuring a different object.

### D2 — The live account's +10 points against the literature's ~1

> **→ TODO IV-5**, converted 2026-07-31, **and materially reshaped** — read the item before this
> section. Explanations 1 and 2 below (moneyness, tenor) are joined by one this section missed:
> the panel measures implied and realised volatility on **two different clocks**, which inflates
> the short leg alone by about six of the ten points. The ATM-matched re-cut this section doubted
> is feasible on the call leg, whose strike is frozen at the lot's basis. IV-2's quotation of the
> +10 figure is withdrawn pending the re-cut; §09:162's "roughly twice" is affected too.

**The claim.** IV-2 records the put leg running **~+10 points** over subsequent realised
volatility, roughly double the call leg, with a within-name depth slope of +30–40% relative IV.
§09:152 already hedges this as "several points clear of the 2–4 the literature reports" and
attributes it to far-OTM puts being "not as far out of the money as they look".

**The problem.** Against the *correct* single-name baseline the gap is not "several points clear
of 2–4", it is roughly **tenfold**. That is too large to be left as an aside, because the article
uses it in two places at once: as evidence the premium is real, and as evidence the premium does
not arrive.

**The candidate explanations, none of which is currently distinguished:**
1. **Moneyness.** Bakshi & Kapadia measure *near-money* options. The live account sells OTM puts,
   where skew mechanically lifts implied volatility. Comparing an OTM put's IV to realised
   volatility is not measuring a risk premium; it is measuring skew plus a risk premium.
2. **Tenor.** Weekly options against their 30–60 day sample. Short-dated implied volatility is
   both higher and noisier.
3. **Measurement window.** A 14-month window's realised volatility is one draw.
4. **Era and universe.** 1991–1995 large caps vs a 2025–2026 retail book.
5. **A real effect.** Gârleanu–Pedersen–Poteshman's demand pressure is strongest exactly where
   retail sells: single-name OTM puts.

**What would settle it:** re-cut `iv_panel.py` to report an **ATM-matched, tenor-matched**
spread alongside the as-traded one. The difference between those two numbers *is* the skew
contribution, and only the ATM-matched number is comparable to the literature. This is a
measurement change, not a modelling one, and it should happen before §14 or §15 quote either
figure.

### D3 — Weekly put-writing has historically underperformed monthly, and our model has no mechanism for it

> **→ TODO II-19**, plus **INF-6** and a line in **IV-3**; converted 2026-07-31. Test (a) below
> was run: the model is cadence-neutral at fair prices to 13 bp across a 13× range, and its
> residual tilt at a flat premium favours weekly, the wrong way. So (b) applies — but not as an
> outlook item only. §09's list of what the single σ_IV omits has **no tenor axis** while the
> running example straddles one, so II-19 edits §09 as well. The term-structure slope this
> section calls "the sharper candidate" is quantified there from Bondarenko's own table.

**The fact.** 2006–2018: PUT (monthly ATM) compounded **5.97%** at Sharpe **0.50**; WPUT (weekly
ATM) compounded **4.51%** at Sharpe **0.40**, having collected **37.1%** of notional per year in
premium against PUT's **22.1%**. More premium, less money — 1.7× the gross for ~75% of the return.

**Why it matters to us.** Our running example writes **weekly** puts, and the article's cadence
result is the √n grid tax, which is about the *ratio* of call period to put period, not about the
absolute tenor. At fair prices our model is very nearly indifferent to absolute cadence: quotes
scale as √τ and nothing real changes. **The model therefore cannot produce the PUT-vs-WPUT
ordering at all**, in either direction.

**What the literature offers as the mechanism.** Two candidates, and they are not exclusive.
Israelov & Nielsen's Myth 4 is the general statement (more frequent writing multiplies cash, not
profit, and if anything reduces it). Israelov & Tummala (2017), *Which Index Options Should You
Sell?*, find the best-compensated options per unit of stress loss are **front-month, near-money**
— which is closer to PUT than to WPUT, but the comparison is on delta-hedged positions. The
sharper candidate is that the **term structure of the volatility risk premium is not flat**, so
premium per unit of √τ falls at very short tenors; our single scalar σ_IV assumes it is flat.

**What would settle it:** two things, in order. (a) Confirm that our model really is
cadence-neutral at fair prices by running the σ_IV = σ ledger at τ_p = 1/12 against 1/52 with n
held fixed — if it is not neutral, we have a prediction to compare and the sign matters. (b) If
it is neutral, this becomes an **outlook item**: a σ_IV(τ) term structure is the minimal
extension that would let the model speak to cadence, and it is the single most requested thing a
practitioner would ask of it.

### D4 — Our model cannot see a risk that the literature says is 25% of the total

> **→ TODO II-20**, plus **II-21**; converted 2026-07-31. §09 gains its first risk statistic:
> up-beta 0.83, **down-beta exactly 1.000**, which is Myth 2 disproved inside our own model, and
> above 1 once the put leg is in. The asymmetry turns out to be governed by **n**, not by p\* —
> the √n grid tax appearing in risk. **H4's prescription contains a trap** and II-21 is the
> quarantine for it; read that item before comparing anything to BXM. This section's pointer to
> H5 stands: the three-way mapping is still unconverted.

Israelov & Nielsen (2015) attribute ~25% of a covered call's *risk* to the dynamic equity
reversal exposure, with essentially no return. Under GBM that exposure cannot be compensated —
which is why our model, correctly, assigns it no return. But our model also does not **report**
it, because the article quotes expectations and capital, not a risk decomposition.

This is not a contradiction; it is a **gap in what we report**. A reader coming from the covered-call
literature will ask what the wheel's beta is, and whether it is asymmetric the way BXM's is
(0.63 up, 0.78 down). We can answer that — the machinery is there — and we currently do not.
See harvest H5.

### D5 — Merton–Scholes–Gladstein, unverified

> **→ TODO I-5**, converted 2026-07-31; the prohibition itself lives in **I-1** and stands until
> I-5 closes. **Explicitly low priority**: nothing in `sections/` cites these papers, so I-5 may
> be closed either by reading them *or* by deciding §03 will not mention the early simulation
> literature — provided that decision is written down. One instruction the item adds: **do not
> close it by searching**, since more secondary description is the evidence class this finding
> exists to reject.
>
> **Closed 2026-08-01, by option 1 — reading them.** The expectation recorded below was correct:
> both papers price at Black–Scholes with trailing realised variance and report *distributional*
> differences at that price, which makes them a **supporting** citation. What it did not
> anticipate is 1982's uncovered put writing beating covered call writing in all six pairings and
> beating the DJ stock portfolio outright at E/S = 1.1 — so §03 may not cite them as "option
> writing underperforms". [`DONE.md`](../DONE.md) carries the verdict; the read also raised
> **II-27**, **II-28**, **III-4** and **IV-8**, and a bullet in **II-18**.

Secondary sources describe the 1978/1982 simulation studies as showing option strategies
outperforming buy-and-hold. If that is the actual claim it sits awkwardly against contribution 4
and against everything in Strand B, and it is old enough and famous enough that a reader may raise
it. I could not obtain the full text in this pass. **Do not cite it either way until someone has
read it.** My expectation is that the papers report *distributional* differences under fair
Black–Scholes pricing rather than risk-adjusted outperformance, in which case they are a
supporting citation rather than a contradicting one.

### D6 — Part III's diversification promise has a pricing problem the literature identifies

> **→ TODO III-3**, with pointers added to III-1 and III-2; converted 2026-07-31. Converted
> **speculatively and on purpose**: it constrains how §12 and §13 are written, so waiting for
> them would be waiting until it is too late to apply. The conversion also sharpened it —
> II-18's magnitudes make the gap concrete (SPX 3.3 points against 1.07–1.5 single-name, and
> **that gap is the correlation premium**), which compresses this finding to **"index-like risk,
> single-name pay."** DMV's caveat that the correlation premium is unharvestable net of frictions
> is carried too, so the item cannot be read as "write index options instead". Separately, II-19
> hands III-1 an unrelated sizing result on the same subsection.

Not a divergence yet, because §12 does not exist. Recorded so it is not discovered late.

Contribution 7 promises that diversification leaves expected return and expected capital
*completely unchanged*. Little/Brumelle make that safe on the **quantity** side: the law is
additive across independent streams and needs no independence assumption anyway. But
Driessen–Maenhout–Vilkov means it is **not** safe on the **price** side: a portfolio of
single-name wheels and a wheel on the index are not the same trade, because the index option
embeds a correlation risk premium that the components do not. A diversified book of single-name
wheels collects the *smaller* premium, and the reason is exactly the correlation exposure that
III-2 is about to identify as the strategy's main vulnerability. **The two halves of Part III are
the same fact seen twice**, and the section should say so rather than treating diversification and
correlation as separate topics.

---

## 4. The novelty claim

`sections/03-prior-work.md` currently asserts: *"We are not aware of prior work treating the wheel
specifically as an inventory/queueing system with layered, depth-dependent exit rates and deriving
stability conditions for it."*

> **→ TODO I-1**, converted 2026-07-31. All three narrowings are folded into the rewritten item,
> which now reads "the reading is done, the section is not". I-1 also carries the read-level rule
> and D5's prohibition, and **cannot close until §03 is written**.

**Verdict: the claim survives, but it must be narrowed in three places.**

**N1 — No published index or academic study tracks the wheel as a strategy.** CBOE's suite covers
BXM (buy-write), PUT/WPUT (put-write), PPUT (protective put), CLL (collar) and CMBO (covered
combo). CMBO is the nearest and is **not** the wheel: it holds a short put and a short call
simultaneously and permanently against a permanent long index position, where the wheel alternates
between the two states and the number of shares held is the state variable. Searches across arXiv,
SSRN and the journal publishers surfaced exactly two academic items on the wheel by name
(Strand F), neither of which builds a structural model. **This half of the claim is safe.**

**N2 — The individual ingredients are all standard, and we should say so.** Nothing in the spine
is new mathematics: the barrier shift is Broadie–Glasserman–Kou, the tail exponent is the Lundberg
coefficient, the first-passage machinery is Siegmund's, the infinite-server analogy is textbook,
and grid-monitored knockouts are the autocallable literature's daily business. The contribution is
the **assembly** — that these particular pieces compose into a single-state-variable account of a
strategy nobody had modelled — not any one piece. The current phrasing already implies this, but
§03 should make it explicit, because a referee will.

**N3 — "Little's law applied to a portfolio of positions" cannot be claimed at all.** John Little's
own 50th-anniversary paper offers *"the dollar rate of return on the ith asset in a portfolio of
assets"* as the canonical illustration of the generalised law H = λG. Applying L = λW to holdings
is not novel; it is the textbook example. What is ours is the **depth process that supplies W**,
and the census that supplies the weighting function. §03 must not claim otherwise, and §08 should
probably cite Brumelle rather than deriving the weighted version by hand (H1).

**One caveat on the search itself.** Negative results from web search are weak evidence. I searched
for the wheel by name, for covered-call/put-write holding-time models, for queueing and
inventory-theoretic treatments of option positions, for infinite-server applications in finance,
and for averaging-down/accumulation models — across arXiv, SSRN and the major publishers. That is
reasonable coverage of what is *findable*, but it is not a systematic review, and a
citation-graph pass outward from Whaley (2002), Israelov & Nielsen (2014) and Broadie–Glasserman–
Kou (1997) would be a stronger test. Recommend doing that before publication, not before assembly.

---

## 5. Harvest — what to actually take

> **H1–H11 were converted on 2026-08-01**, after the divergences. Four became items of their own
> — **H1 → II-22**, **H2/H3/H9 → II-23**, **H8 → II-24** — and the rest were folded into items
> that already owned the section they touch: **H6** and **H7** into **IV-1** (with a line of H7 in
> **IV-2**), **H10** into **IV-3**, **H11** into **IV-2**. **H4** went into **II-20** with D4 the
> day before — *and its prescribed BXM comparison is the trap II-21 quarantines, so do not follow
> H4's last paragraph as written*; **H5** stays flagged as adjacent inside II-20 and was
> deliberately not promoted. Each marker below says where its item is and what changed.

Ordered by how much they change the article.

**H1 — Replace §08's hand-derivation with Brumelle's H = λG.** *(highest value)*

> **→ TODO II-22**, converted 2026-08-01. The identity was **checked numerically and holds
> exactly** (0.000% across all four weightings), and two things this section did not know came out
> of the check: `model.py` already computes the H = λG side, so only the prose derives anything by
> hand; and **§10 gains more than §08 does** — the capital criterion θ > 1 *is* the statement that
> G is finite at f = e^x. The item also carries a caution this section does not: H = λG is a
> stationary identity while the article reports finite horizons.
Our income and capital results are currently derived as integrals against the census, justified in
prose. They are instances of a named theorem — the generalised Little's law, H = λG (Brumelle
1971; Heyman & Stidham 1980; restated in Little 2011 §3.2.2) — which says that for **any**
weighting f<sub>i</sub>(t) applied over each item's time in system, the time-average H equals λ
times the per-item total G. Setting f to the lot's carrying value gives our capital result; setting
it to the lot's income rate gives our income result. This is worth doing for three reasons: it is a
theorem rather than a construction, it inherits Little's freedom from independence assumptions
(which the article already leans on hard), and it gives the general reader a single detour that
covers both results instead of two.

**H2 — Cite Broadie–Glasserman–Kou for the call-grid tax, alongside Siegmund.**

> **→ TODO II-23**, converted 2026-08-01, **grouped with H3 and H9** — three one-sentence
> attributions that are one editing sitting and share one constraint: §03 carries the pedigree,
> Part II carries the pointer. The item adds a target this section misses, §00's symbol table,
> which also calls β "Siegmund's overshoot constant".
`eq:siegmund` is currently attributed to Siegmund alone. The constant and its use are
Broadie–Glasserman–Kou (1997) — a Mathematical Finance paper with an order of magnitude more
citations in finance, and one whose framing ("shift the barrier by exp(±βσ√Δt)") is *closer to what
we do* than Siegmund's sequential-analysis framing. It also supplies the honest error statement:
the correction is asymptotic in the monitoring frequency. Keep Siegmund (1979, 1985) as the
origin and Chang & Peres (1997) as the pointer for anyone wanting the higher-order terms.

**H3 — Name θ = 2ν/σ² as the Lundberg adjustment coefficient.**

> **→ TODO II-23** with H2 and H9, converted 2026-08-01. The Dufresne/Yor caution below is carried
> into the item verbatim in substance — cite as analogy or not at all, never as an identity.
§10 introduces θ as "the tail exponent" and calls it "the single most informative number about a
configuration of this strategy". It is the **Cramér–Lundberg adjustment coefficient** from ruin
theory, the exponential rate of the all-time maximum of a Brownian motion with drift −ν, and the
condition θ > 1 is a Cramér-type moment condition. Naming it costs one sentence, buys a
detour-worthy pointer (an actuary reading the article will recognise the whole structure), and
tells the reader that our second boundary is a known kind of object rather than an ad-hoc
threshold.
*Caution:* the Dufresne/Yor exponential-functional results are **structurally analogous, not
literally applicable** — their object is ∫e^{−2W} ds, ours is E[e^x] under an occupation measure.
Cite them as "the same phenomenon appears as…", or not at all. Do not assert an identity.

**H4 — Report a beta, and an asymmetric one.** *(new result, cheap)*
BXM's up-beta 0.63 against down-beta 0.78 is the single most quoted risk fact about covered calls,
and our model can produce the wheel's analogue directly — regress the ledger's period returns on
the underlying's, split by sign. It would (a) let §09 speak to the covered-call literature in its
own units, (b) give §12 a natural place to say what diversification does and does not remove, and
(c) probably show the wheel's asymmetry is *worse* than BXM's, because the wheel's inventory is
concentrated in exactly the states where the stock has already fallen. If that comes out, it is a
genuine result and it is currently missing.

**H5 — Adopt the three-way decomposition as a presentation layer for §09.**
Israelov & Nielsen (2015): passive equity + short volatility + equity reversal. Our Track B ledger
already contains all three; we present it as premium/mark-loss/giveaway/dividends instead. Adding
a short table that maps our terms onto theirs would let a reader arriving from the covered-call
literature locate themselves immediately, and it makes the "reversal exposure is uncompensated"
point — which we get for free from GBM — legible as a *result* rather than an assumption.

**H6 — Use Hill et al.'s four-way attribution as an external check on our ledger.**

> **→ folded into TODO IV-1**, 2026-08-01, rather than made an item: §14 already owns the ledger's
> verification and the bullet this sharpens. The framing carried across is that it validates the
> ledger's *structure* where the Monte Carlo validates only its arithmetic. This section says §14;
> IV-1 is that section.
Fair call premium / volatility premium / exercise cost / trading cost. Their finding that the
exercise cost is the largest single drag is precisely our call-away giveaway, and it is the term
our first economic ledger omitted. A paragraph in §14 comparing our attribution's shape to theirs
is a cheap external validation of the ledger's *structure*, independent of the Monte Carlo, which
only validates its arithmetic.

**H7 — Take Broadie–Chernov–Johannes as the method for IV-1's "what a career cannot test".**

> **→ folded into TODO IV-1**, with its second consequence in **IV-2**, 2026-08-01. Both halves
> survive as written: the overlay-excess statistic is defended as the right *kind* of measurement,
> and IV-2's interval is presented as a known property of option returns rather than as an apology
> for fourteen months.
They make the argument we need and make it better than we currently can: put returns are so noisy
that even 18 years of monthly data cannot reject Black–Scholes for deep-OTM puts (p ≈ 8%), and
**CAPM alphas and Sharpe ratios on option returns are noisier still than raw average returns** —
so the natural-looking regression is the *worst* test available. Their prescription is to test
market-neutral or delta-hedged component portfolios rather than strategy returns. Two consequences
for us: our overlay-excess measurement (wheel minus same-names buy-and-hold) is already the right
*kind* of statistic and should be defended as such, and the wide bootstrap interval in IV-2 should
be presented as **the expected consequence of a known property of option returns**, not as an
apology for a short sample.

**H8 — The disposition-effect framing for the census.**

> **→ TODO II-24**, converted 2026-08-01. The §08-or-§16 choice this section leaves open is
> **decided for §08**: §16's list is what the model leaves out, and this describes what the model
> already produces. The item adds two limits — the analogy is structural and does not transfer
> Odean's cost estimate, since that cost is largely tax and the article models none (IV-3).
§08's hospital-beds analogy is good; Odean gives it a second, sharper one. The wheel is a
contract that sells every winner and holds every loser — the disposition effect with the
discretion removed. Odean's investors do it 1.5–2× more than chance and it costs them; the wheel
does it always. This is a one-paragraph detour in §08 or §16 and it is the most intuitive possible
statement of why standing inventory is dominated by deep lots.

**H9 — Autocallables as the machinery pointer for §07.**

> **→ TODO II-23** with H2 and H3, converted 2026-08-01. The INF possibility this section raises
> is recorded in the item and **not** converted: an autocallable-quadrature check on
> `occupation()` would be a third independent method family, and nothing needs it today.
A wheel lot is an autocall: it terminates on the first scheduled observation date at which the
underlying is above a fixed level. Saying so gives §07's first-passage detour a real-world anchor
readers may know, and points anyone wanting sharper numerics at a literature (quadrature methods,
Hilbert transforms) built for exactly our grid problem. Possible use for INF work: an independent
numerical check on `occupation()` from a completely different method family.

**H10 — Muravyev & Pearson for the transaction-cost descope.**

> **→ folded into TODO IV-3**, 2026-08-01, together with **tax** from §7's second-pass list, which
> had no home anywhere. §16 is the outlook, and IV-3 is the item that rewrites it.
§16 lists transaction costs as deliberately out of scope. If it wants a defensible sentence about
what including them would cost, the modern estimate is that effective spreads are **29.6%
(algorithmic) to 58.4% (all traders) of the quoted half-spread** — conventional estimates roughly
double the truth. Hill et al.'s 3–6 bp/month at half a volatility point is the covered-call-specific
version.

**H11 — Goyal & Saretto for IV-2's selection discussion.**

> **→ folded into TODO IV-2**, 2026-08-01, and sharpened on the way. This section already notes
> that it is an options signal rather than a stock-selection one; the item makes that the *whole*
> reason to cite it, and adds the account's own confirmation — the published edge lives in the
> overlay, which is the leg that earned −4.37%.
IV-2 must say what modelling the selection result would commit us to. Goyal & Saretto (2009) is
the published, pre-existing version of "the operator has an edge picking what to sell": sorting on
implied-minus-historical volatility predicts option returns cross-sectionally, robustly. It is
worth noting that this is an **options** signal, not a stock-selection signal — so it is *not* what
the live account's rules 4 and 6 (fallen angels, oversold) claim, and citing it makes the
distinction sharp rather than muddy.

---

## 6. Proposed skeleton for §03 (not written, for discussion)

Six short subsections, each ending in what the article takes from it:

1. **The strategy has a benchmark family but not a benchmark.** BXM, PUT/WPUT, CMBO; what each
   is, and why none of them is the wheel. *Take: the wheel has never been indexed, so there is no
   published return series to calibrate against — which is why Part IV builds one from a
   statement.*
2. **What the record says.** Whaley (2002), Bondarenko (2019), Hill et al. (2006), Israelov &
   Nielsen (2014). Lower volatility, similar or slightly better Sharpe, asymmetric beta, and a
   worse return in strong up-markets. *Take: the regime caveat in §15 is a documented mechanical
   fact, not a hedge.*
3. **Where the return comes from.** The equity + short-volatility decomposition; the reversal
   exposure; income vs revenue. *Take: contribution 4 is not our discovery, it is the consensus —
   what is ours is deriving it inside a model that also produces the inventory.*
4. **The volatility risk premium, and the index/single-name gap.** Coval & Shumway, Bakshi &
   Kapadia (both), Carr & Wu, Driessen–Maenhout–Vilkov, Gârleanu–Pedersen–Poteshman.
   *Take: σ_IV = σ is the right default for a single-name model, and the honest number for the
   edge is smaller than the index literature suggests.* **This subsection is the fix for D1.**
5. **The mathematical toolkit.** Little (1961, 2011) and Brumelle; Siegmund and
   Broadie–Glasserman–Kou; ruin theory's adjustment coefficient; the infinite-server queue; the
   discretely monitored barrier / autocallable literature. Each with one sentence on where it
   enters. *Take: the machinery is standard and old; the assembly is not.*
6. **What is new here.** Narrowed per N1–N3: no prior structural model of the wheel; the
   ingredients are standard; the application of Little's law to holdings is explicitly *not*
   claimed. What is claimed: one state variable, the entry law it induces, the grid-sampled
   first-passage holding time, the depth census, and the two stability boundaries.

Length target: shorter than it looks — the article is for a general audience, so most of these
should be two or three sentences with the citation carrying the weight.

---

## 7. What a second pass should cover

Deliberately not done here, either because Part III does not exist yet or because it needs a
different kind of search.

> **Conversion status, 2026-08-01.** Three of these became items — early exercise is **II-25**,
> the citation-graph pass is **I-6**, tax is folded into **IV-3**. Part III's reading is recorded
> inside **III-3**, deliberately as a precondition on §12/§13 rather than as a task of its own.
> The remaining three already had homes: **I-5**, **II-18**/**IV-5**, and **IV-3**.

- **Part III's literature is largely unread.** Driessen–Maenhout–Vilkov is the anchor and I have
  only its abstract. Also wanted: the correlation risk premium literature more broadly, the
  crisis-correlation literature, and whatever exists on diversification of short-option books.
  This should be done *with* §12 and §13, not before. → **III-3**, which also records that its own
  magnitudes come from II-18's sources and not from DMV, precisely because DMV is **[A]**.
- **A citation-graph pass** outward from Whaley (2002), Israelov & Nielsen (2014) and
  Broadie–Glasserman–Kou (1997), to firm up the novelty claim (N1 caveat). → **I-6**, kept out of
  I-1 so that §03 is not held behind a release gate.
- **Merton–Scholes–Gladstein (1978, 1982)** in full text (D5). → **I-5**.
- **A modern single-name IV − RV estimate** (D1) — either from the literature or from our own data
  once D2's measurement is fixed. → **II-18** takes the published route; **IV-5** decides what our
  own data can support, and finds it is one nine-contract cell.
- **Early exercise.** Bakshi & Kapadia note an American-exercise premium worth ~2 volatility points
  on short-dated near-money calls. Our model is European and `DONE.md` argues the omission is
  conservative. Two points is not nothing, and the argument deserves a citation rather than an
  assertion. → **II-25**, where the two points turns out **not to bind**: our calls are OTM by
  construction on every date one is written, and near-money is where the American premium lives.
- **The term structure of the volatility risk premium** (D3), if we decide the cadence question
  is worth answering. → **IV-3**, as the minimal extension that would let the model speak to
  cadence; II-19 carries the slope the record implies.
- **Tax.** Entirely unexamined here and materially adverse for a wheel run in a taxable account
  (short-term treatment of premium, wash sales on repeated assignment, and the qualified-covered-call
  rules that suspend holding periods). The article does not claim to cover it; §16 should probably
  say so explicitly. → **IV-3**, with the observation that it is not currently even on §16's list
  of deliberate omissions, which makes it look like an oversight.

---

## 8. Reading list

Downloaded copies are in `literature/` (gitignored). Read levels as defined in §0.

**Strategy performance and decomposition**
- Whaley, R. (2002). Return and Risk of CBOE Buy Write Monthly Index. *J. Derivatives* 10(2):35–42. **[A]** — https://www.pm-research.com/content/iijderiv/10/2/35
- Israelov, R. & Nielsen, L. N. (2014). Covered Call Strategies: One Fact and Eight Myths. *FAJ* 70(6):23–31. **[F]** — https://www.aqr.com/Insights/Research/Journal-Article/Covered-Call-Strategies-One-Fact-and-Eight-Myths · `israelov-nielsen-2014-covered-call-one-fact-eight-myths.pdf`
- Israelov, R. & Nielsen, L. N. (2015). Covered Calls Uncovered. *FAJ* 71(6). **[P]** — https://www.aqr.com/library/journal-articles/covered-calls-uncovered · `israelov-nielsen-2015-covered-calls-uncovered.pdf`
- Hill, J., Balasubramanian, V., Gregory, K. & Tierens, I. (2006). Finding Alpha via Covered Index Writing. *FAJ* 62(5):29–46. **[P]** — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=935138 · `hill-et-al-2006-finding-alpha-covered-index-writing.pdf`
- Bondarenko, O. (2019). Historical Performance of Put-Writing Strategies. CBOE. **[F]** — https://cdn.cboe.com/resources/education/research_publications/PutWriteCBOE19_v14_by_Prof_Oleg_Bondarenko_as_of_June_14.pdf · `bondarenko-2019-put-writing-strategies.pdf`
- Israelov, R. et al. Covering the World: Global Evidence on Covered Calls. AQR. **[downloaded, unread]** — `israelov-et-al-covering-the-world-global-covered-calls.pdf` — *read owed by **I-1**, before §03's subsection 2, which is otherwise all US index data*
- Israelov, R. & Tummala, H. (2017). Which Index Options Should You Sell? *J. Investment Strategies*. **[A]** — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2990542
- **Merton, R., Scholes, M. & Gladstein, M. (1978). The Returns and Risk of Alternative *Call* Option Portfolio Investment Strategies. *J. Business* 51(2):183–242. [F]** — `merton-scholes-gladstein-1978-call-option-portfolio-strategies.pdf` — *covered writing below the underlying in all eight comparisons; the premium-sensitivity experiment (II-27); the portfolio-dispersion result (III-4); Appendix C's market-vs-model premiums (II-18)*
- **Merton, R., Scholes, M. & Gladstein, M. (1982). The Returns and Risks of Alternative *Put*-Option Portfolio Investment Strategies. *J. Business* 55(1):1–55. [F]** — `merton-scholes-gladstein-1982-put-option-portfolio-strategies.pdf` — *the wheel's own leg: uncovered put writing, put early-exercise frequencies and the stop-loss that does not transfer (II-28), the conversion strategy as an empirical no-arbitrage test (IV-8)*
- Cboe S&P 500 Covered Combo Index (CMBO) methodology. **[A]** — https://cdn.cboe.com/api/global/us_indices/governance/CMBO_Methodology.pdf

**Volatility risk premium**
- Coval, J. & Shumway, T. (2001). Expected Option Returns. *JF* 56(3):983–1009. **[A]**
- Bakshi, G. & Kapadia, N. (2003). Delta-Hedged Gains and the Negative Market Volatility Risk Premium. *RFS* 16(2):527–566. **[A]** — `bakshi-kapadia-2003-rfs-delta-hedged-gains.pdf`
- **Bakshi, G. & Kapadia, N. (2003). Volatility Risk Premiums Embedded in Individual Equity Options. *J. Derivatives*, Fall. [F]** — `bakshi-kapadia-2003-jod-individual-equity-vrp.pdf` — *the single most important source for D1*
- Carr, P. & Wu, L. (2009). Variance Risk Premiums. *RFS* 22(3):1311–1341. **[A]**
- Driessen, J., Maenhout, P. & Vilkov, G. (2009). The Price of Correlation Risk. *JF* 64(3):1377–1406. **[A]**
- Gârleanu, N., Pedersen, L. H. & Poteshman, A. (2009). Demand-Based Option Pricing. *RFS* 22(10):4259–4299. **[A]**
- Goyal, A. & Saretto, A. (2009). Cross-Section of Option Returns and Volatility. *JFE* 94:310–326. **[A]**

**Statistics, frictions, measurement**
- Broadie, M., Chernov, M. & Johannes, M. (2009). Understanding Index Option Returns. *RFS* 22(11):4493–4529. **[P]** — `broadie-chernov-johannes-2009-index-option-returns.pdf`
- Santa-Clara, P. & Saretto, A. (2009). Option Strategies: Good Deals and Margin Calls. *JFM* 12:391–417. **[A]** — `santa-clara-saretto-wp-good-deals.pdf` (working-paper version)
- Goetzmann, W., Ingersoll, J., Spiegel, M. & Welch, I. (2007). Portfolio Performance Manipulation and Manipulation-Proof Performance Measures. *RFS* 20(5):1503–1546. **[A]**
- Muravyev, D. & Pearson, N. (2020). Options Trading Costs Are Lower than You Think. *RFS* 33(11):4973–5014. **[A]**

**Probability**
- **Broadie, M., Glasserman, P. & Kou, S. (1997). A Continuity Correction for Discrete Barrier Options. *Mathematical Finance* 7(4):325–349. [F]** — `broadie-glasserman-kou-1997-continuity-correction.pdf`
- Siegmund, D. (1979). Corrected Diffusion Approximations. *Adv. Appl. Prob.* 11(4). **[A]**; Siegmund (1985), *Sequential Analysis*. **[A]**
- Chang, J. & Peres, Y. (1997). *Ann. Probab.* 25(2):787–802. **[A]**
- Janssen, A. & van Leeuwaarden, J. (2007). On Lerch's Transcendent and the Gaussian Random Walk. *Ann. Appl. Probab.* 17(2). **[P]** — `janssen-vanleeuwaarden-2007-lerch-gaussian-random-walk.pdf`
- **Little, J. (2011). OR Forum — Little's Law as Viewed on Its 50th Anniversary. *Operations Research* 59(3):536–549. [P]** — `little-2011-littles-law-50th-anniversary.pdf` — *source for H1 and N3*; cites Brumelle (1971) and Heyman & Stidham (1980) for H = λG
- Li & Zhang. Discretely Monitored First Passage Problems and Barrier Options. **[downloaded, skimmed]** — `li-zhang-discretely-monitored-first-passage-barrier-options.pdf` — *read owed by **II-23**, before §07's autocallable pointer is written*

**Behavioural**
- Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *JF* 53:1775–1798. **[A]**
- Shefrin, H. & Statman, M. (1985). The Disposition to Sell Winners Too Early. *JF* 40(3). **[A]**

**On the wheel specifically (both weak)**
- Kuang, X. & Lin, B. (2025). arXiv:2512.01123. **[P]** — `arxiv-2512.01123-wheel-bayesian-networks.pdf` — *do not cite as evidence*
- Svozil, K. (2026). arXiv:2604.13334. **[P]** — `arxiv-2604.13334-against-universal-trading-strategy.pdf`
