# Where the live account and the mechanical model disagree

Source: `statements/` restated through `code/live_ledger.py`, which marks the
account to market using `code/prices.py` (Yahoo chart endpoint, cached under
`data/`). Window 2025-05-02 .. 2026-07-02, 1.17 years, **96 names, 56 lots
acquired, 36 exited, 20 still open**.

This is the first measurement of the live account in **Track B**. Everything
before it — the 2026-07-10 observations draft, all of TODO items #7–#14 — was
computed from a cash ledger, which can only produce Track A on a cost basis.

> **Restated 2026-07-27 (second revision), after two definition changes.** Every
> figure in this file moved. The universe is now an explicit list of names the
> strategy claims to trade (`EXCLUDED_LIST` in `analyze_statement.py`), replacing
> a price threshold that admitted speculative growth names, China ADRs, ETFs and
> a preferred; and an entry is now priced at the session's **open** rather than
> its close, because the operator writes within the hour after the bell. The
> figures under the previous definitions are kept in the margin as `(was …)` so
> the two are never confused. Re-running the old definition reproduces the old
> numbers exactly, so every change below is attributable to the redefinition and
> nothing else. Discipline for this restatement is fixed by procedure item 3 of
> the out-of-sample pre-registration: apply the change to the baseline too, and
> report both.
>
> The cleanup cost 43% of the option contracts (2,112 → 1,204) and 39% of the
> lot-days (6,351 → 3,870). It bought relevance at the price of power, and the
> intervals below are correspondingly wider.

## The headline

    Track A on cost basis          +37.97% /yr    what the brokerage shows   (was +34.40%)
    Track B economic, on market    +19.52% /yr                               (was +15.43%)
    same-names buy-and-hold        +24.29% /yr                               (was +17.62%)
    EXCESS over same names          -4.77% /yr    the option overlay         (was  -2.19%)
    selection contribution         +25.01% /yr    which names, when          (was +10.59%)

Three findings. Their order of size *changed* with the restatement — selection
is now the largest at +25.0 points, ahead of accounting's 18.5 — but they are
kept in their original order below so the two revisions can be read against each
other.

**1. Eighteen percentage points a year of the apparent result is accounting.**
The cash view says +38.0%; the economic view says +19.5%. This is exactly the
failure [the returns section](#sec:returns) predicts and quantifies for the
model — cost basis inflates relative to market value as deep lots accumulate —
except that in a 1.17-year-old account the effect runs the *other* way round and
is far larger than the model's +4.11% at five years, because the book is young,
the losers are all still held, and 20 of 56 lots have never been marked.

**2. The option overlay earned nothing, and probably less than nothing.** The
excess over holding the same shares is −4.77%/yr. Resampling puts the 90%
interval at **−26.0% to +14.1%** by lot and **−20.0% to +7.4%** clustered by
name, with P(excess < 0) = 63% and 70% respectively: the overlay's contribution
is *statistically indistinguishable from zero*, and the point estimate sits on
the negative side of it. That is the model's prediction, confirmed — not
contradicted — by the live account. The interval is now half again as wide as it
was, because the account being measured is half the size.

**3. The live account's advantage is stock selection, not the wheel.** Holding
the wheel's own inventory earned +34.01%/yr against +9.00%/yr for the same
dollars, on the same days, spread equally across every name the operator trades.
The +25.01% gap is what "attractive price" bought — and it is the lever
[the strategy section](#sec:strategy) declares out of scope.

> **Correction, applied 2026-07-27 to the first revision and still in force.**
> This gap once read +6.11%, against a universe benchmark of +13.96%. Both were
> wrong. Returns were being taken as ratios of *as-traded* prices, which are
> deliberately discontinuous at a split: SCLX, KYNB and MCRB each reverse-split
> inside the window, so a 1:20 split entered the equal-weight universe average as
> a +1,900% daily return. `prices.Series.window_adj`/`adj_on_or_before` now serve
> every return, volatility and trend calculation, and the as-traded series is
> reserved for what it is for — comparing a price with a strike. The overlay
> excess was unaffected, since it never touches universe returns. All three of
> those names are now out of universe as well, so the bug can no longer bite
> here; the fix stays because the next reverse split will not announce itself.

So the perceived outperformance is real, but it is **not** the wheel
outperforming. It is good stock selection, measured through a cash ledger that
flatters it further, with an option overlay that gave part of it back.

## Both headlines are the same few positions, and that is the finding

`live_ledger.py --bootstrap` ranks each name by its footprint in *both*
decompositions at once:

    name       excess    w/o it  selection    w/o it
    UNH    $  -11,019    +2.08% $   13,961   +12.35%
    ELV    $   -3,352    -2.68% $    7,898   +17.85%
    MSFT   $   -3,652    -2.50% $    5,354   +20.15%
    INTU   $     -957    -4.17% $   -5,229   +29.75%
    ZTS    $      176    -4.88% $   -4,642   +29.21%

UNH alone is 51% of the selection gap and, on its own, the difference between a
negative and a positive overlay. The first three rows share a sign pattern:
**negative excess, positive selection, the same name.** That is not a coincidence
to be apologised for, it is the mechanism stated in the ledger's own arithmetic.
A lot that runs far enough to dominate the selection column is a lot whose
covered call gave that run away, and it appears in the excess column with the
opposite sign and comparable size.

The concentration is therefore evidence, not noise. The lognormal has no room
for a lot that goes from 260 to 394 in seven weeks; the live account has three
of them in fourteen months. It is the same tail T2 measures from the other side
as a right-skewed entry depth, and the same tail that makes the mean and the
median disagree everywhere in this data. Averaging it away would be discarding
the one feature of reality the model is known to lack.

The honest reading of both headlines is that each is a statement about a
fourteen-month window in which a handful of positions did the work — which is
what the wide intervals already say, and what the out-of-sample pre-registration
exists to fix.

**The clearest single illustration.** UNH was assigned at 260 on 2026-03-27.
Three days later the operator wrote a four-week call at the same 260 basis for
$18.10 — the frozen-strike policy the model assumes. UNH then ran from 277 to
393.85 by the 2026-05-15 expiry and was called away at 260. Collected $1,810;
surrendered $13,385. The covered call capped precisely the recovery that would
have repaid the lot, which is the model's central mechanism arriving in the most
expensive available form.

## What the universe change did, name by name

Fourteen lots left the measurement. Their equity P&L over the window:

    STRF   5 lots   -$9,976     the wheeled preferred, already out of scope
    KWEB   2 lots   -$2,294     China ETF
    KVUE   2 lots     +$810
    DQ     1 lot      +$678
    RIVN   1 lot      +$238
    AMLP   1 lot      +$190
    BEKE   1 lot      -$370
    ALT    1 lot      -$315

The jump in measured selection is almost entirely **STRF and KWEB**, which are
excluded on a structural criterion — a preferred and an index fund are not the
lognormal single-stock walk the model is built on — decided before the question
of how they performed arose. The speculative single names contributed *positive*
P&L totalling ~+$1.9k, so removing them slightly *lowers* measured selection. The
redefinition is not self-flattering; STRF was simply suppressing the number
before, and it was −$6,880 of the old +$17,179 gap.

**The overlay went the other way.** The excluded names contributed exactly
**+$2,921** to the old excess: $8,369 of call premium against only $1,395 of
surrendered upside — cheap calls written on names that kept falling. Strip them
and the covered-call leg's result gets substantially worse (below). The universe
cleanup made the overlay look worse and selection look better, which is the
pattern to expect when the names removed were ones that fell.

## The catalogue

Organised by the only three places excess return can come from.

### (iii) Measurement — the largest single source

| # | source | magnitude | status |
|---|---|---|---|
| M1 | Track A vs Track B ledger | **18.5 pp/yr** | measured |
| M2 | right-censoring: 20 open lots never marked | inside M1 | measured |
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
over 56 lots has **median +2.0%** — which confirms finding #12 — but **mean
+3.6%**, and 11% of lots do land deeper than 10%: +25% (NVO, assigned at 67 into
a 50.03 close after the July 2025 profit warning), +21% (TRI), +15% (ACN), +12%
(CTSH), +11% (ELV). The inversion could only see
assignments that got an at-basis call written within 21 days, and those are
exactly the shallow ones; deep lots wait, or get a call struck below basis. The
derived E[d | assignment] survives as a description of the *median*; it
understates the *mean* because the real process has jumps and the lognormal
model does not.

### (i) Options sold dear — the put leg keeps a fifth, the call leg loses a third

    put premium                    $33,721                       (was $36,225)
    less mark loss at acquisition  -26,768                       (was -32,306)
    PUT LEG                        $ 6,953     20.6% of premium kept  (was 10.8%)
    call premium                   $29,074                       (was $37,443)
    less upside surrendered        -38,643                       (was -40,038)
    CALL LEG                       $-9,569    -32.9% of premium kept  (was -6.9%)
    frictions                      $-5,054     commissions, buy-backs, open marks
    EXCESS                         $-7,670                       (was -$4,749)

This is the largest qualitative change in the restatement, and it goes the
article's way. Under the old universe both legs were very nearly a wash. On the
names the strategy actually claims, they are not symmetric at all: **the put leg
keeps a fifth of its premium and the call leg gives back a third of its own.**

The reason is the previous section's arithmetic. The excluded names were falling
names, and a call written on a falling name expires worthless — $8,369 of call
premium against $1,395 of surrendered upside. That flattered the call leg by
enough to disguise what the covered call does on a name that recovers, which is
exactly the mechanism [the returns section](#sec:returns) is about. Removing them
does not create the effect; it stops hiding it.

Frictions are not negligible: $653 of commissions, $745 of buy-backs, and $3,656
of mark on the 68 contracts still open at the window's end.

Decomposed into volatility risk premium versus skew in Appendix 2.

### (ii) Not-GBM — where the live advantage actually is

| # | source | magnitude | status |
|---|---|---|---|
| S1 | name and entry selection | **+25.01%/yr** | measured, exposure-matched |
| S2 | skipped weeks | 240 of 598 gaps exactly 7d; mean gap 21.6d | measured |
| S3 | the operator's stated rule | rules 4 and 6 confirmed, rule 5 rejected outright | fitted, see Appendix 3 |

S1 is measured with the size and duration of the exposure held fixed — the same
dollars, on the same days — so it is not the artifact of comparing a
time-varying position against a buy-at-the-start index. It is still one window,
one regime, and — see above — a handful of positions, and it should not be
quoted as an estimate of skill.

S2 is the statistic least disturbed by the restatement: the modal gap is still
exactly 7 days (40% of gaps, was 39%) and the mean is still 21.6 days (was 21.7).
While a name is in rotation the operator writes a median of **18.1 puts a year**
against a weekly cadence's 52, and acquires **1.41 lots per wheeled name-year**
(was 1.70) against the model's 10.4 at p\* = 20%.

### Structural differences that are not edge, but must be controlled

| # | difference | measured |
|---|---|---|
| X1 | the put book is *wide*: puts on 95 names, put margin $43.4k = **31% of capital** against the single-name model's 1.6% | yes |
| X2 | deep lots are often left uncovered: 29 calls struck below the *top* layer's basis | yes |
| X3 | K_c policy: 116 at basis / 23 above / 29 below (of 168 matched) — frozen-K_c holds **69%** of the time (was ~80%) | yes |
| X4 | impairment: **no observations.** ALT and BEKE were the only two, and both are now out of universe | none |
| X5 | coverage: calls-live per lot-held is >1 early (legacy shares) and settles at ≈1.0 from Feb 2026 | yes |

X1 is the one that matters most for comparability: the model is a single-name
wheel whose capital is inventory plus one put's margin, while the live account
sells puts across 95 names and holds inventory on 34. Premium per unit of
inventory capital is therefore structurally far higher live than in the model,
and any direct comparison of Track A yields between them is meaningless without
this adjustment.

X3 weakened. The frozen-K_c assumption held ~80% of the time under the old
universe and 69% under the new one, because the calls that came out were
disproportionately the at-basis ones. The model still describes the modal
policy, but "roughly seven times in ten" is the honest figure.

X4 is now empty by construction, and that is a loss worth recording rather than
a tidying-up. ALT and BEKE were the only two lots the wheel ever entered on a
name it would later disown, and they were the sole empirical handle on the
permanent-impairment hazard of TODO #13. Excluding them is right — neither is a
name the strategy would knowingly enter, so a hazard estimated from them would
describe a universe the article does not claim — but it leaves **the impairment
channel untested**, and no rate can be quoted until an in-universe name goes
against the account and stays there.

## The regime caveat, which bounds all of the above

The universe returned +9.00%/yr over the window and the held names +34.01%/yr.
**A covered-call overlay must underperform in a strong up-market** — that is
mechanical, not evidence, and the held names ran far harder than the universe
did. The −4.77% is a regime-conditional number, and the resampling interval
already says the sample cannot distinguish it from the model's predicted zero.
Neither the overlay result nor the selection result should be read as an
unconditional estimate: 1.17 years, 34 correlated names carrying inventory, one
direction of market, and a handful of positions doing most of the work in both
directions.

## Appendix: the model's own predictions, tested (`code/model_vs_live.py`)

The comparison above is against the *market*. This one is against the *model*:
`model.py` fed the live account's measured parameters — σ = 34.3%
(inventory-weighted realised), exposure-weighted drift +34.1%, median put tenor
4 d, median call tenor 14 d — and checked link by link. Every one of these tests
needs a spot price, which is why none was possible before.

The call/put tenor ratio is now **n = 4**, exactly the article's running example,
though at half its absolute tenors (4 d / 14 d against 7 d / 28 d). The longer
calls that pushed the old median to 25 d were disproportionately on excluded
names.

**T1, the entry law — passes sharply on aggregate.** Over 920 put contracts
written against a known spot, the model expects **71.6** assignments, **72**
contracts finished below the strike, and **71** were assigned. That is a **0.8%**
error on the model's own event, sharper than the old 2.5%.

*Bucket-level calibration, however, does not survive the change of spot
convention, and should no longer be claimed.* Priced at the session open, the
highest-probability bucket predicts 27.4% and realises 8.0% (n = 75); priced at
the close, the same bucket predicts 25.9% and realises 24.3%. The far-OTM
anomaly is robust to the convention — puts predicted at 0.7% finish ITM 8.5% of
the time either way, which is the jump tail — but the middle of the distribution
is not. The likely cause is real and systematic rather than noise: the operator
sells into intraday weakness that partly reverts by the close, so the opening
print overstates entry-time moneyness for exactly the puts written nearest the
money, while the close understates it. The truth is between the two, and the
statement the data supports is the aggregate one.

**T2, the entry depth — the model brackets reality but is skewed wrong.** Live
d = 1 − S(expiry)/K over 58 assigned lots has median **+2.2%**, mean **+3.8%**;
the model's E[d | assignment] at these clocks is **+6.0%**. The live mean is 1.8×
the live median, so the distribution is far more right-skewed than the lognormal
conditional, which is the same jump tail T1 sees from the other side.

**T3, the depth census — the sharpest test, and it holds.** Mean depth over
3,870 lot-days is **0.145** live against **0.151** from the killed walk at the
article's μ = 7%: a 4% error on the quantity that carries income and capital.
The error changed sign — the model now runs marginally *deep* rather than
marginally shallow — but stayed the same size, which is about as much as this
sample can resolve.

The drift comparison sharpened considerably. At the article's μ = 7% the model
gives 0.151 against 0.145 live; at the window's realised drift it gives **0.101**,
a 30% miss (the old gap was 23%). A bull-market drift would have emptied the book
far faster than it actually emptied, and the account behaved as though its names
drift at something much closer to 7% than to the 34% they in fact delivered. The
shape still differs consistently: live is thinner right at the strike (11.5% vs
19.7% in 0–2%) and fatter in the middle (38.6% vs 29.4% in 5–20%).

**And the call-grid tax: 19.0% of all lot-days are spent above the lot's own
call strike** (was 16.7%), held only because the call has not expired yet. The
model kills those states by construction; this is the empirical size of the
effect [eq:siegmund](#eq:siegmund) corrects for.

**T4, q(x) — validated, with the model running aggressive.** Against the 284 call
contracts actually written, the model expects **26.1%** exercised and **19.7%**
were. The shape is monotone in depth and tracked throughout:

    depth at write     n    model q   realised
       ITM (x<-2%)     5      0.736      0.600
            -2..0%    20      0.626      0.500
              0-2%    42      0.421      0.357
              2-5%    70      0.335      0.300
             5-10%    57      0.170      0.105
            10-20%    70      0.094      0.014
              >20%    20      0.020      0.000

The two deepest bins are now thin (n = 70 and 20) and read 0.014 and 0.000
against predictions of 0.094 and 0.020; the direction is the old one but the
sample no longer supports a claim about the deep tail of q.

Two wrong constructions were tried first and are recorded in the module so they
are not retried: reading depth on the day before exit (throws away nearly every
exit, since a called-away lot is above its strike that day), and sampling each
lot every τ_c days from its own entry (scores periods at tenors the operator
never traded, and made the model look 2× too aggressive when the fault was the
sampling). Neither the call-coverage rate (87.5% of lot-days) nor post-entry
volatility drift (36.2% at entry against 34.8% at exit, i.e. slightly *down*)
explains any part of the gap; both were measured and rejected.

**A confirmation that was previously thought untestable.** 56 calls were assigned
against only 55 that finished above the strike. The excess is early exercise —
the dividend-capture channel that draft finding #11 recorded as invisible to a
cash statement ("payment dates, not ex-dates, are recorded"). The margin is now
one contract rather than eleven, so this survives as a *demonstration* that the
channel is visible with prices, not as a measurement of its size.

**T5, holding time — the model exits too fast, and censoring is large.**

    days     live S(t)   model S(t)
      30        65.6%       52.4%
      90        43.5%       20.6%
     365        21.1%        5.2%

Kaplan-Meier median holding time is **56 days against the 30 days that completed
lots alone report** — a 1.9× understatement (was 2.3×), which is TODO #9's
censoring warning quantified. The survival gap is T4's per-period overstatement
compounded over many periods. With 36 exits and 20 censored the curve flattens at
21.1% from day 180 onward, so nothing beyond six months is estimated here.

**Verdict.** The spine is confirmed empirically at every link that the sample can
resolve: the entry law to within 0.8% in aggregate, the depth census to within 4%
on the mean, q(x) monotone and tracked in the bins that carry the mass. Where it
errs it errs in one direction — the lognormal lacks the jump tail, which makes
assignments deeper than predicted in the tail and exits slightly faster than
observed. What the restatement removed is the *bucket-level* claims: T1's
calibration curve and q(x)'s deepest bins are no longer supported at this sample
size, and the aggregate statements are what the data carries.

## Appendix 2: the implied-volatility panel (`code/iv_panel.py`)

899 of 909 contracts inverted for implied volatility. This is what the article
currently assumes rather than measures.

**Accuracy bound, first.** The spot is now the session's **open** rather than its
close, because the operator writes within the hour after the bell — but the trade
was not at the opening auction either, so a band remains. Re-running the whole
panel at the close moves the put-leg spreads by under a point but the call-leg
weeklies by more than four (+9.0 against +4.6), so **call-leg numbers are the
convention-sensitive ones** and should be read as a band. Sensitivity to the spot
itself is unchanged: ±1% moves median IV by ∓5.5 points on the 4-day puts, ∓2 on
monthlies, and ±2.5 on calls.

**The volatility risk premium is real and large on the put leg.**

    leg      tenor      n   median IV   med fwd RV   IV - RV
    puts     <=1wk    493       37.1%        26.7%    +10.5%
    puts     1-3wk     61       44.3%        29.0%    +15.3%
    puts     ~monthly 142       35.6%        26.0%     +9.6%
    calls    <=1wk     70       36.1%        27.1%     +9.0%
    calls    1-3wk     38       35.2%        33.6%     +1.6%
    calls    ~monthly  78       34.8%        31.0%     +3.8%
    calls    longer    17       43.5%        36.4%     +7.2%

Weighted by contract count the put leg averages **+10.7 points** and the call leg
**+5.5**, so TODO #4's conjecture stands: the put spread is roughly double the
call spread. But the call leg is now spread across four thin, disagreeing buckets
rather than two, and the per-bucket call figures should not be quoted.

Against the article's break-even of **zero**, with every point worth ~45bp, the
put-leg spread is the entire edge and then some.

**The skew is textbook and steep.** Put IV rises monotonically as the strike
falls — 18.1% at the money, 29.9% at 2–5% out, 45.7% at 5–10% out, 47.6% beyond
— while calls trace a smile, 30.8% at the money, 30.6% just out, and 44.5%
beyond 10%. A single scalar `iv_spread` cannot represent this.

**σ_IV(x) is increasing in depth, and the effect is bigger than it was.**

    lot depth      n   median IV   relative to the name's own median
      0-2%        24       33.0%                                0.93x
      2-5%        37       33.4%                                0.99x
      5-10%       26       36.1%                                0.84x
     10-20%       30       41.6%                                0.92x
     20-35%       13       53.6%                                1.07x
      >35%         8       60.6%                                1.29x

The far-OTM smile wins over the "shallow lots sit at the money" effect: a deep
lot's call is quoted at a *higher* implied volatility, so deep lots earn richer
call premiums than a constant σ_IV books. **But the relative column is the one to
model.** In absolute terms IV nearly doubles across the depth range; after
dividing by each name's own median IV it rises from 0.93× to 1.29×. Most of the
absolute rise is still selection — deep lots sit on intrinsically volatile names
— but the genuine within-name depth effect is now about **+30 to +40% relative
IV from shallow to deep**, against the +20% measured before, and the column is no
longer monotone in the middle. The deepest bin holds 8 contracts, so the size is
not firm; the sign is.

This matters for the decision to leave σ_IV(x) out of the model. The omission is
larger than the article currently claims, and its sign is favourable — the model
is pessimistic about deep inventory by more than it says.

**The leverage effect is confirmed, modest, and asymmetric as predicted.**

    trailing 20d       n   median IV   relative
    fell >15%         78       50.8%      1.06x
    fell 7-15%       149       37.3%      1.00x
    fell 2-7%        233       35.6%      0.99x
    flat             221       33.5%      1.00x
    rose 2-7%        107       36.2%      1.00x
    rose >7%          43       41.3%      0.93x

Relative IV rises after falls and drops after rises. But *absolute* IV is
elevated on **both** tails — 50.8% after a big fall and 41.3% after a big rise —
which is exactly the operator's own observation that a surge raises implied
volatility too, just not relative to the name's own level.

**The tension worth naming, because it is the sharpest result here.** The put leg
harvests a spread of about +10 volatility points, and yet Appendix 1 shows it
kept only **20.6% of its premium** economically, because the mark loss at
assignment consumed four fifths of it. The volatility risk premium is real and it
is very largely cancelled by the cost of the inventory it creates. The
restatement moved this from "very nearly cancelled" to "four fifths cancelled",
which is a weaker version of the same statement — and the slack it opens on the
put leg is more than taken back by the call leg, which now loses a third of its
own premium.

## Appendix 3: the selection rule, fitted (`code/selection_fit.py`)

The pre-registration was written before any price data was fetched. What it
predicted, and what the trades say. 54 weeks, 5,184 name-weeks, 644 sales — a
menu of 96 names a week from which ~12 were picked. Conditional logit over the
weekly choice set, so the weekly budget (rule 7) is absorbed and every
coefficient is identified by *which* names were picked, never how many.

The choice set is now the operator's *stated* universe rather than everything
that ever appeared in the statements, which is what rule 1 always said it should
be. That is a fairer test of rules 4–6 than the old one, and it changes two
conclusions.

    feature      beta/sd      z    odds/sd    mean pct rank of chosen   (was)
    pct5y         -0.723  -11.4      0.49                      0.269   (0.318)
    pctB          -0.462   -9.5      0.63                      0.351   (0.361)
    slope         -0.306   -4.9      0.74                      0.320   (0.326)
    slope_r2      -0.071   -1.3      0.93                      0.581   (0.569)

**Rule 4 (fallen angels) and rule 6 (oversold): confirmed, decisively, and more
strongly than before.** Both coefficients carry the pre-registered negative sign
at z ≈ −10, and the nonparametric check agrees without any model at all — the
names picked sit at the **27th percentile** of their own 5-year range (was 32nd)
and the **35th percentile** of their 30-day Bollinger position, against 50 under
random selection, at p < 0.001 by permutation. Restricting the menu to the stated
universe sharpened rule 4 rather than diluting it: within the aristocrats, the
operator goes further down the 5-year range than the old figure suggested.
Pseudo-R² also rose, 0.07 → 0.094.

**Rule 5 (avoid falling knives): rejected outright, and the earlier consolation
is withdrawn.** The pre-registration predicted a *positive* slope coefficient — a
low price preferred only once it has stopped falling. The fitted sign is negative
and stronger than before (β = −0.306, z = −4.9): steeper decliners are picked
*more* often, and the picked names sit at the 32nd percentile by trend slope. Two
props the earlier reading leaned on have now gone:

  * `slope_r2` has flipped from **+0.136 (z = +3.3)** to **−0.071 (z = −1.3)**,
    i.e. from significant to nothing. The pre-registered "falling knife = steep
    decline *and* a high R²" needs both legs; the second leg is not there.
  * `off52w` has flipped from **+0.352 (z = +3.4)** to **−0.080 (z = −0.7)**, and
    nonparametrically the chosen names sit at the **26th** percentile of distance
    from their 52-week high. The old draft read the positive coefficient as rule
    5 surviving in a different coordinate — "not avoid steep trends but prefer
    the ones that have started to come back". **That reading is withdrawn.** It
    was an artifact of a choice set stuffed with speculative names whose 52-week
    behaviour has nothing to do with the operator's decision.

The generic secondary set is otherwise unchanged in character: 3-month and
12-month returns both strongly negative (z = −6.8, −4.9) — dip buying, at
somewhat lower significance than before.

One honesty note, restated. `rvol` still carries a significant negative
conditional coefficient (z = −5.9), but its mean percentile rank is now **0.580
at p < 0.001** — the chosen names are *more* volatile than the menu average, not
less. Under the old universe this was 0.520 at p = 0.044 and was called
"essentially no marginal effect"; it is now significant and pointing the opposite
way from the coefficient. It remains a suppression/collinearity artifact and must
not be reported as "the operator avoids volatile names" — if anything the raw
tendency is the reverse, which is what one expects once the genuinely wild names
are out of the menu and the remaining variation is aristocrats under stress.

**What this does not show.** That the timing earned anything. The fit says
entries are timed to drawdowns; whether those drawdowns mean-revert is a claim
about the price process that 20 lots in a single bull market cannot support.

## What this changes

* The mechanical wheel model is **not** contradicted by the live account. Its
  central prediction — that the overlay earns approximately nothing at fair
  prices — is what the data shows, within a wide interval, and the point
  estimate moved further onto the negative side of zero.
* The gap that motivated this exercise is now mostly S1 (selection) and M1
  (accounting), **in that order** — the restatement reversed their ranking.
* Only S1 needs new modelling. It is TODO #14's "attractive price" lever, and
  it is now measured rather than conjectured.
* M4 amends a Done item; M3 amends published draft numbers.

## What the restatement changed, in one place

Kept, and mostly sharpened:

* the spine, link by link — entry law to 0.8% in aggregate, census to 4%, q(x)
  monotone, survival above the model at every horizon;
* the overlay verdict, indistinguishable from zero and now more negative;
* selection as the account's advantage — larger, and still the excluded lever;
* rules 4 and 6 confirmed, rule 5 rejected;
* the put-leg volatility risk premium, ~+10 points, roughly double the call leg;
* the skipped-week cadence, essentially untouched.

Changed materially:

* the call leg went from a near-wash to **−32.9% of premium**, and the put leg
  from 10.8% kept to 20.6%. The old symmetry was an artifact of cheap calls on
  falling names;
* selection +10.59% → +25.01%, almost all of it the removal of STRF and KWEB;
* the σ_IV(x) depth effect roughly doubled, from +20% to +30–40% relative;
* frozen-K_c from ~80% to 69% of calls.

Withdrawn:

* T1's bucket-level calibration — convention-sensitive, aggregate only;
* q(x)'s deepest two bins — n = 70 and 20, no longer supported;
* the early-exercise *magnitude* — a one-contract margin now, not eleven;
* "rule 5 survives as prefer-the-ones-recovering" — `off52w` flipped and lost
  significance;
* the impairment hazard — no in-universe observations exist.
