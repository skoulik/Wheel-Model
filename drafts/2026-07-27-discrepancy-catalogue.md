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
    selection contribution          +6.11% /yr    which names, when

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
the wheel's own inventory earned +20.07%/yr against +13.96%/yr for the same
dollars, on the same days, spread equally across every name the operator ever
traded. The +6.11% gap is what "attractive price" bought — and it is the lever
[the strategy section](#sec:strategy) declares out of scope.

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
| S1 | name and entry selection | **+6.11%/yr** | measured, exposure-matched |
| S2 | skipped weeks | 257 of 651 gaps exactly 7d; mean gap 21.7d | measured |
| S3 | the operator's stated rule | pre-registered 2026-07-27 | awaiting fit |

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

## What this changes

* The mechanical wheel model is **not** contradicted by the live account. Its
  central prediction — that the overlay earns approximately nothing at fair
  prices — is what the data shows, within a wide interval.
* The gap that motivated this exercise is mostly M1 (accounting) and S1
  (selection), in that order of size.
* Only S1 needs new modelling. It is TODO #14's "attractive price" lever, and
  it is now measured rather than conjectured.
* M4 amends a Done item; M3 amends published draft numbers.
