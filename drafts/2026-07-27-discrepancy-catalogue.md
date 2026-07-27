# Where the live account and the mechanical model disagree

Source: `statements/` restated through `code/live_ledger.py`, which marks the
account to market using `code/prices.py` (daily closes, Yahoo chart endpoint,
cached under `data/`). Window 2025-05-02 .. 2026-07-02, 1.17 years, 129 names,
70 lots acquired, 41 exited, 29 still open.

This is the first measurement of the live account in **Track B**. Everything
before it — the 2026-07-10 observations draft, all of TODO items #7–#14 — was
computed from a cash ledger, which can only produce Track A on a cost basis.

## The headline

    Track A on cost basis          +34.40% /yr    what the brokerage shows
    Track B economic, on market    +15.43% /yr
    same-names buy-and-hold        +17.62% /yr
    EXCESS over same names          -2.19% /yr    the option overlay
    selection contribution         +10.59% /yr    which names, when

Three findings, in order of size.

**1. Nineteen percentage points a year of the apparent result is accounting.**
The cash view says +34.4%; the economic view says +15.4%. This is exactly the
failure [the returns section](#sec:returns) predicts and quantifies for the
model — cost basis inflates relative to market value as deep lots accumulate —
except that in a 1.17-year-old account the effect runs the *other* way round and
is far larger than the model's +4.11% at five years, because the book is young,
the losers are all still held, and 29 of 70 lots have never been marked.

**2. The option overlay earned nothing, and possibly less than nothing.** The
excess over holding the same shares is −2.19%/yr. But a bootstrap over lots puts
the 90% interval at **−15.6% to +8.5%**, with P(excess < 0) = 59%: the overlay's
contribution is *statistically indistinguishable from zero*. That is the model's
prediction, confirmed — not contradicted — by the live account. A single lot
moves it: dropping the UNH call-away flips −2.19% to +3.97%.

**3. The live account's advantage is stock selection, not the wheel.** Holding
the wheel's own inventory earned +20.07%/yr against +9.48%/yr for the same
dollars, on the same days, spread equally across every name the operator ever
traded. The +10.59% gap is what "attractive price" bought — and it is the lever
[the strategy section](#sec:strategy) declares out of scope.

> **Correction, applied 2026-07-27 after first publication of this draft.** That
> gap first read +6.11%, against a universe benchmark of +13.96%. Both were
> wrong. Returns were being taken as ratios of *as-traded* prices, which are
> deliberately discontinuous at a split: SCLX, KYNB and MCRB each reverse-split
> inside the window, so a 1:20 split entered the equal-weight universe average
> as a +1,900% daily return. `prices.Series.window_adj`/`adj_on_or_before` now
> serve every return, volatility and trend calculation, and the as-traded series
> is reserved for what it is for — comparing a price with a strike. The overlay
> excess is unaffected, since it never touches universe returns.

So the perceived outperformance is real, but it is **not** the wheel
outperforming. It is good stock selection, measured through a cash ledger that
flatters it further, with an option overlay that gave part of it back.

## The catalogue

Organised by the only three places excess return can come from.

### (iii) Measurement — the largest single source

| # | source | magnitude | status |
|---|---|---|---|
| M1 | Track A vs Track B ledger | **19.0 pp/yr** | measured |
| M2 | right-censoring: 29 open lots never marked | inside M1 | measured |
| M3 | contract-count parsing bug | call premium understated **30%**, put **14%** | fixed |
| M4 | finding #12's inversion was selection-biased | see below | measured |

**M3.** `analyze_statement.py` matched option opens to closes row by row and
ignored the contract count, but 322 of 1,198 open rows carry more than one
contract (up to 60). Gross premium was understated by 1.14× on puts and 1.30× on
calls, which flips the draft's headline calls/puts income ratio from **0.90 to
1.03** — calls now *out-earn* puts, strengthening rather than weakening the
model's prediction that the call leg dominates as inventory builds. Fixed by
matching on contract quantity; positions now carry `qty` and prorated cash.

**M4.** Draft finding #12 inverted at-basis call premiums to conclude "NOT ONE
assignment implies a gap deeper than 10%". With real prices, the acquisition gap
has **median +1.4%** — which confirms finding #12 — but **mean +3.9%**, with a
tail reaching +25% (NVO, assigned at 67 into a 50.03 close after the July 2025
profit warning), +21% (TRI), +15% (ACN, STRF). The inversion could only see
assignments that got an at-basis call written within 21 days, and those are
exactly the shallow ones; deep lots wait, or get a call struck below basis. The
derived E[d | assignment] survives as a description of the *median*; it
understates the *mean* because the real process has jumps and the lognormal
model does not.

### (i) Options sold dear — currently a wash

    put premium                    $36,225
    less mark loss at acquisition  -32,306
    PUT LEG                        $ 3,919     10.8% of premium kept
    call premium                   $37,443
    less upside surrendered        -40,038
    CALL LEG                       $-2,595     -6.9% of premium kept
    frictions                      $-6,073     commissions, buy-backs, open marks
    EXCESS                         $-4,749

Each leg is very nearly a wash, exactly as [the returns section](#sec:returns)
argues it must be at fair prices, and frictions then tip the total negative.
Frictions are not negligible: $819 of commissions, $839 of buy-backs, and $4,415
of mark on the 177 contracts still open at the window's end — that last item is
alone 93% of the excess, so the point estimate is fragile in both directions.

Not yet decomposed into volatility risk premium versus skew. That needs the
implied-volatility panel (Stage 2): every one of the 2,112 contracts becomes an
IV observation now that spot is known.

**The clearest single illustration in the data.** UNH was assigned at 260 on
2026-03-27. Three days later the operator wrote a four-week call at the same 260
basis for $18.10 — the frozen-strike policy the model assumes. UNH then ran from
277 to 393.85 by the 2026-05-15 expiry and was called away at 260. Collected
$1,810; surrendered $13,385. The covered call capped precisely the recovery that
would have repaid the lot, which is the model's central mechanism arriving in
the most expensive available form.

### (ii) Not-GBM — where the live advantage actually is

| # | source | magnitude | status |
|---|---|---|---|
| S1 | name and entry selection | **+10.59%/yr** | measured, exposure-matched |
| S2 | skipped weeks | 257 of 651 gaps exactly 7d; mean gap 21.7d | measured |
| S3 | the operator's stated rule | rules 4 and 6 confirmed, rule 5 rejected | fitted, see Appendix 3 |

S1 is measured with the size and duration of the exposure held fixed — the same
dollars, on the same days — so it is not the artifact of comparing a
time-varying position against a buy-at-the-start index. It is still one window
and one regime, and it should not be quoted as an estimate of skill.

### Structural differences that are not edge, but must be controlled

| # | difference | measured |
|---|---|---|
| X1 | the put book is *wide*: 129 names, put margin $46.6k = **25% of capital** against the single-name model's 1.6% | yes |
| X2 | deep lots are often left uncovered: 35 calls struck below the *top* layer's basis | yes |
| X3 | K_c policy: 138 at basis / 24 above / 11 below (of 173 matched) — frozen-K_c holds ~80% of the time | yes |
| X4 | impairment: 2 in-window entries into names since judged junk (ALT, BEKE) — the first empirical handle on TODO #13 | yes |
| X5 | coverage: calls-live per lot-held is >1 early (legacy shares) and settles at ≈1.0 from Feb 2026 | yes |

X1 is the one that matters most for comparability: the model is a single-name
wheel whose capital is inventory plus one put's margin, while the live account
sells puts across 129 names and holds inventory on 29. Premium per unit of
inventory capital is therefore structurally far higher live than in the model,
and any direct comparison of Track A yields between them is meaningless without
this adjustment.

## The regime caveat, which bounds all of the above

The universe returned +13.96%/yr over the window and the held names +20.07%/yr.
**A covered-call overlay must underperform in a strong up-market** — that is
mechanical, not evidence. The −2.19% is a regime-conditional number, and the
bootstrap interval already says the sample cannot distinguish it from the
model's predicted zero. Neither the overlay result nor the selection result
should be read as an unconditional estimate: 1.17 years, ~45 correlated names,
one direction of market.

## Appendix: the model's own predictions, tested (`code/model_vs_live.py`)

The comparison above is against the *market*. This one is against the *model*:
`model.py` fed the live account's measured parameters — σ = 33.9%
(inventory-weighted realised), exposure-weighted drift +19.4%, median put tenor
4 d, median call tenor 25 d — and checked link by link. Every one of these tests
needs a spot price, which is why none was possible before.

**T1, the entry law — passes sharply.** Over 1,083 put contracts written against
a known spot, the model expects **94.6** assignments, **94** contracts finished
below the strike, and **97** were assigned. That is a 0.6% error on the model's
own event. Calibration by predicted probability tracks well except in the
far-OTM bucket, where puts predicted at 0.7% finished ITM 9.2% of the time — the
lognormal has no jumps and the market does.

**T2, the entry depth — the model brackets reality but is skewed wrong.** Live
d = 1 − S(expiry)/K has median **+2.2%**, mean **+4.4%**; the model's
E[d | assignment] at these clocks is **+6.1%**. The live mean is 2.0× the live
median, so the distribution is far more right-skewed than the lognormal
conditional, which is the same jump tail T1 sees from the other side.

**T3, the depth census — the sharpest test, and it holds.** Mean depth over
6,351 lot-days is **0.146** live against **0.139** from the killed walk at the
article's μ = 7%: a 5% error on the quantity that carries income and capital.
Notably the census matches *better* at the article's assumed drift than at the
realised +19.4% — a bull-market drift would have emptied the book faster than it
actually emptied. The shape differs in a consistent way: live is thinner right
at the strike (10.1% vs 23.6% in 0–2%) and fatter in the middle (52.1% vs 38.6%
in 5–20%).

**And the call-grid tax, measured directly for the first time: 16.7% of all
lot-days are spent above the lot's own call strike**, held only because the
call has not expired yet. The model kills those states by construction; this is
the empirical size of the effect [eq:siegmund](#eq:siegmund) corrects for.

**T4, q(x) — validated.** Against the 556 call contracts actually written, the
model expects **19.9%** exercised and **15.6%** were. The shape is monotone in
depth and tracked throughout, the model running modestly aggressive:

    depth at write     n    model q   realised
       ITM (x<-2%)     6      0.752      0.667
            -2..0%    10      0.588      0.600
              0-2%    69      0.447      0.406
              2-5%   121      0.314      0.215
             5-10%    81      0.175      0.185
            10-20%   138      0.092      0.051
              >20%   131      0.036      0.008

Two wrong constructions were tried first and are recorded in the module so they
are not retried: reading depth on the day before exit (throws away nearly every
exit, since a called-away lot is above its strike that day), and sampling each
lot every τ_c days from its own entry (scores periods at tenors the operator
never traded, and made the model look 2× too aggressive when the fault was the
sampling). Neither the call-coverage rate (90.8%, highest in the shallow bins)
nor post-entry volatility drift (30.4% at entry vs 32.8% while held) explains
any part of the gap; both were measured and rejected.

**A confirmation that was previously thought untestable.** 87 calls were
assigned against only 76 that finished above the strike. The excess is early
exercise — the dividend-capture channel that draft finding #11 recorded as
invisible to a cash statement ("payment dates, not ex-dates, are recorded").
With prices it is visible after all, and it is direct evidence for the early-
exercise caveat of TODO #2c/#5.

**T5, holding time — the model exits too fast, and censoring is huge.**

    days     live S(t)   model S(t)
      30        68.2%       53.5%
      90        49.3%       31.6%
     365        31.8%       10.9%

Kaplan-Meier median holding time is **63 days against the 28 days that
completed lots alone report** — a 2.3× understatement, which is TODO #9's
censoring warning quantified. The survival gap is T4's modest per-period
overstatement compounded over many periods.

**Verdict.** The spine is confirmed empirically at every link that the sample can
resolve: the entry law to within 0.6%, the depth census to within 5% on the mean,
q(x) monotone and tracked. Where it errs it errs in one direction — the lognormal
lacks the jump tail, which makes assignments deeper than predicted in the tail
and exits slightly faster than observed.

## Appendix 2: the implied-volatility panel (`code/iv_panel.py`)

1,097 of 1,109 contracts inverted for implied volatility. This is what the
article currently assumes rather than measures.

**Accuracy bound, first.** The spot used is the day's close; the trade happened
intraday. Perturbing the assumed spot by ±1% moves median IV by ∓5.5 points on
the 4-day puts, ∓2 points on monthlies, and ±2.5 points on calls (the opposite
sign, since a call is long the spot). Worse, the bias is not obviously random:
rule 6 sells puts into weakness, so if the operator trades below the close the
true put IV is nearer the low end. Every put number below should be read as a
band, not a point.

**The volatility risk premium is real and large on the put leg.**

    leg      tenor      n   median IV   med fwd RV   IV - RV
    puts     <=1wk    541       37.8%        27.3%    +10.5%
    puts     ~monthly 161       35.1%        25.4%     +9.7%
    calls    <=1wk     86       33.1%        28.5%     +4.7%
    calls    ~monthly 137       37.3%        32.4%     +4.9%

Against the article's break-even of **zero**, with every point worth ~45bp, a
put-leg spread of +5 to +10 points (the band the sensitivity above allows) is
the entire edge and then some. TODO #4's conjecture that the edge concentrates
in the put leg is confirmed: the put spread is roughly double the call spread.

**The skew is textbook and steep.** Put IV rises monotonically as the strike
falls — 16.3% at the money, 29.7% at 2–5% out, 45.7% at 5–10% out, 48.6% beyond
— while calls trace a smile, 31.1% at the money, 26.3% just out, and 48.9%
beyond 10%. A single scalar `iv_spread` cannot represent this.

**σ_IV(x) is increasing in depth — the sign question is settled.**

    lot depth      n   median IV   relative to the name's own median
      0-2%        46       31.7%                                0.93x
      2-5%        47       31.3%                                0.92x
      5-10%       33       35.8%                                0.96x
     10-20%       38       37.3%                                0.95x
     20-35%       20       65.9%                                1.09x
      >35%        11       57.5%                                1.13x

The far-OTM smile wins over the "shallow lots sit at the money" effect: a deep
lot's call is quoted at a *higher* implied volatility, so deep lots earn richer
call premiums than a constant σ_IV books. **But the relative column is the one
to model.** In absolute terms IV roughly doubles across the depth range; after
dividing by each name's own median IV it rises only from 0.92× to 1.13×. Most
of the absolute rise is selection — deep lots sit on intrinsically volatile
names — and the genuine within-name depth effect is about **+20% relative IV
from shallow to deep**. That, not the doubling, is what belongs in σ_IV(x).

**The leverage effect is confirmed, modest, and asymmetric as predicted.**

    trailing 20d       n   median IV   relative
    fell >15%         93       52.3%      1.06x
    fell 7-15%       184       36.4%      1.00x
    flat             258       33.0%      1.00x
    rose 2-7%        136       37.9%      0.98x
    rose >7%          60       44.3%      0.94x

Relative IV rises after falls and drops after rises. But *absolute* IV is
elevated on **both** tails — 52.3% after a big fall and 44.3% after a big rise —
which is exactly the operator's own observation that a surge raises implied
volatility too, just not relative to the name's own level.

**The tension worth naming, because it is the sharpest result here.** The put
leg harvests a spread of +5 to +10 volatility points, and yet Appendix 1 shows
it kept only **10.8% of its premium** economically, because the mark loss at
assignment consumed the rest. The volatility risk premium is real and it is
very nearly cancelled by the cost of the inventory it creates. That is a
cleaner statement of why the wheel's edge is so much smaller than its premium
income suggests than anything the model derived a priori — and it is the live
account's version of the article's "each leg is very nearly a wash."

## Appendix 3: the selection rule, fitted (`code/selection_fit.py`)

The pre-registration was written before any price data was fetched. What it
predicted, and what the trades say. 55 weeks, 6,914 name-weeks, 716 sales — a
menu of ~126 names a week from which ~13 were picked. Conditional logit over the
weekly choice set, so the weekly budget (rule 7) is absorbed and every
coefficient is identified by *which* names were picked, never how many.

    feature      beta/sd      z    odds/sd    mean pct rank of chosen
    pct5y         -0.564  -10.5      0.57                      0.318
    pctB          -0.467  -10.6      0.63                      0.361
    slope         -0.196   -5.5      0.82                      0.326
    slope_r2      +0.136   +3.3      1.15                      0.569

**Rule 4 (fallen angels) and rule 6 (oversold): confirmed, decisively.** Both
coefficients carry the pre-registered negative sign at z ≈ −10, and the
nonparametric check agrees without any model at all — the names picked sit at
the **32nd percentile** of their own 5-year range and the **36th percentile** of
their 30-day Bollinger position, against 50 under random selection, at p < 0.001
by permutation. The operator does what the operator says.

**Rule 5 (avoid falling knives): rejected, in both forms.** The pre-registration
predicted a *positive* slope coefficient — a low price preferred only once it
has stopped falling. The fitted sign is negative (z = −5.5): steeper decliners
are picked *more* often, and the picked names sit at the 33rd percentile by
trend slope. Adding the pre-registered interaction does not rescue it; `pct5y ×
slope` also comes out negative (z = −5.1), so the preference for decline is
*stronger* among already-cheap names, not weaker. Whatever the operator does to
avoid value traps, it is not visible as trend-slope avoidance in the trades.

The generic secondary set tells the same story from another angle: 3-month and
12-month returns both strongly negative (z = −8.6, −9.0) — dip buying — while
`off52w` is *positive* (z = +3.4). Conditional on being cheap over the long
haul, names nearer their 52-week high are preferred. That is arguably rule 5
surviving in a different coordinate: not "avoid steep trends" but "prefer the
ones that have started to come back".

Two honesty notes. Pseudo-R² is 0.07 — this explains a modest slice of a noisy
decision, which is what one should expect from a rule the operator describes as
"not always followed systematically". And `rvol` carries a significant
conditional coefficient (z = −6.7) but a mean percentile rank of 0.520 at
p = 0.044, i.e. essentially no marginal effect; it is a suppression/collinearity
artifact and should not be reported as "the operator avoids volatile names".

**What this does not show.** That the timing earned anything. The fit says
entries are timed to drawdowns; whether those drawdowns mean-revert is a claim
about the price process that 29 lots in a single bull market cannot support.

## What this changes

* The mechanical wheel model is **not** contradicted by the live account. Its
  central prediction — that the overlay earns approximately nothing at fair
  prices — is what the data shows, within a wide interval.
* The gap that motivated this exercise is mostly M1 (accounting) and S1
  (selection), in that order of size.
* Only S1 needs new modelling. It is TODO #14's "attractive price" lever, and
  it is now measured rather than conjectured.
* M4 amends a Done item; M3 amends published draft numbers.
