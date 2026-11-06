# Dollars per period — plan

**Status: draft, 2026-11-06.** The decision is agreed: the article measures return in dollars
per period. How to carry it through is not yet: the open questions at the end need Sergei's
calls before any code changes. Committed while still a draft, on his say-so, because a cloud
session does not keep uncommitted files. Closes TODO II-34 when done.

## The decision, and why

The economic ledger, eq:econ-pnl, measures each flow against the share price on the day the flow
happens. For premiums, dividends and the appreciation of held shares that is the same thing as
measuring them against the capital at the start of the period. For the two exit flows it is not:

| flow | measured now against | measured from now on against |
|---|---|---|
| mark loss at assignment, K − S′ | S′, the price at assignment | S, the price the put was sold at |
| upside surrendered at call-away, S_T − K | S_T, the price at expiry | S_w, the price the call was sold at |

Measuring against the exit price understates the upside surrendered and overstates the mark loss.
Over the thirty-year Standard book the net effect is that the ledger reads about 0.2 points high.
Three reasons settle the choice, recorded in TODO II-34:

1. **The verification test closes exactly.** At the pricing drift μ = r, no strategy beats the
   risk-free rate, so the excess must be minus the dividend leak and the collateral overcharge,
   −0.437%. In dollars the model gives −0.444% and the simulation −0.442% ± 0.005%. The current
   ledger gives −0.291%. The 8-basis-point residual CLAUDE.md quotes for this test, and the
   collateral footnote's "residual of opposite sign", are that gap netted against the overcharge.
2. **It is what an investor and a broker measure**: each period's dollar change over the dollars
   at the start of it, the time-weighted return. Part IV sets the model against a live account
   reported that way.
3. **It agrees with option-pricing theory and the literature.** Black–Scholes gives each
   instrument an expected excess return equal to its delta times the stock's. The dollar figures
   meet the book's delta × (μ − r) − leak − overcharge to within two basis points at every horizon
   and in both regimes. That is Israelov and Nielsen's framing: a covered call is a smaller stock
   position.

Two independent confirmations are in the repository: `code/ledger_dollar_check.py`, which
integrates the per-period difference against the census, and `python code/wheel_sim.py --scenario
dollars`, which books both conventions on the same simulated paths.

## What moves

The cash rows do not move: premiums, dividends, Track A income, capital at market value and at
cost, the equity row, cash on market value and cash on cost basis. Neither do holding times,
inventory, the census or the stability boundaries.

The economic rows do. First estimates, from the check script, to be recomputed by the changed
model and never quoted from here:

| Standard regime | 5 y | 10 y | 30 y | 100 y |
|---|---|---|---|---|
| mark loss at acquisition, a year | 0.1632 → 0.1553 | same | same | same |
| upside surrendered, a year | 0.3208 → 0.3491 | 0.3383 → 0.3682 | 0.3559 → 0.3876 | 0.3661 → 0.3986 |
| net of the three hidden terms | −0.240 → −0.261 | −0.169 → −0.191 | −0.006 → −0.030 | +0.203 → +0.178 |
| true excess return | 1.60% → 1.23% | 1.60% → 1.30% | 1.60% → 1.40% | 1.61% → 1.46% |
| book delta per unit of capital | 0.875 | 0.902 | 0.932 | 0.951 |

Conservative: 1.37/1.43/1.49% → 1.01/1.13/1.28% at 5/10/30 years.

**The true excess is no longer flat across horizons; it rises.** That reverses what `2799247`
and `bdc2d79` wrote on 2026-11-06 ("the same at every horizon", "barely moves"). The reason is
clean and checkable: the return follows the book's delta, and the fixed put margin's overcharge
thins as the book grows. A lot is a share less the call written against it, so its delta is
1 − Δ_call. As lots sink below their frozen strikes, those calls drift out of the money and stop
offsetting the shares, so each lot counts more nearly as a full share: 0.48 at its strike, 0.80
five log-points down, 0.96 at ten.

**Say it that way in the article.** "Their calls go out of the money, so the book behaves more like
stock" reads backwards to anyone who knows that an in-the-money call is the one that behaves like
stock (Sergei, 2026-11-06). The prose has to name the *short* call and say what it offsets.

The per-lot accounts change sign in substance: a lot collects 3.72% in call premiums and, in
dollars, surrenders about 3.9%, so the covered-call leg costs rather than washes. That is the
short call's delta times the stock's premium, as theory says it should be.

## Method

- **`model.py`, the mark loss.** λ·(E[e^x₀] − 1) becomes (1/T)·E[(k − R′)⁺], R′ the price
  relative over the put's tenor under drift m: an undiscounted Black–Scholes put at the real-world
  drift, in closed form. `entry_basis_ratio` stays for what else uses it.
- **`model.py`, the upside surrendered.** `occupation()` accumulates, per call period j,
  Σ_x u_j(x)·g(x) with g(x) = E[(R − e^x)⁺] over one call tenor at drift m, again in closed form,
  where u_j is the depth density at the period's sale. This replaces the exit-price giveaway in
  `economics()`. `stationary()` carries the new field through its Richardson extrapolation.
  `DepthWalk.step()` is untouched, so its two paths stay as they are.
- **One convention in `model.py`.** The exit-price version is deleted, not kept beside the new
  one: sections carry only final results. `wheel_sim.py --scenario dollars` and TODO II-34 →
  `DONE.md` are the record of why.
- **The verification test becomes exact**: a check that at μ = r the true excess equals
  −leak − overcharge to a basis point. That replaces the 8bp tolerance.

## Order of work

Each step is one commit, reviewed before it lands, with `verify_examples.py` green, the appendix
regenerated, the affected figures redrawn and the claims re-signed after rereading.

1. **The model and its checks.** `model.py` as above; every example case that quotes an economic
   figure updated to the new value; the exact μ = r check added. No prose yet — the sections are
   then knowingly stale for one commit, which the checks will show.
2. **§04.** `eq:excess-return` says what each flow is measured against. Its gloss of economic
   profit gains the upside surrendered, which it has been missing.
3. **§09, "What Track A leaves out".** eq:mark-loss, eq:giveaway and their prose; the slogan
   paragraph's 1.6% overpayment, restated per unit of the sale price; the hidden-terms account,
   replaced by the delta account (decision 1), and fig:hidden-terms; eq:econ-pnl, eq:excess; the closing paragraph, which
   now says the return rises with the horizon and why.
4. **§09, "The two ledgers, side by side".** The economic rows of both regimes, fig:two-ledgers
   and its meeting point, the paragraph after the table and the subsection's close.
5. **§09, "The benchmark that matters"**, capital-share first (decision 2), then the per-lot accounts, the
   "third of a share price" sentence, the collateral footnote, and the Israelov–Nielsen
   paragraph once II-33's PDF check is done.
6. **§09, the rest:** leverage (its break-even is the excess), the volatility-premium conversion
   (~45bp a point), dividends, the Conservative regime, "What this section produced".
7. **Outside §09:** §11's return-on-equity row and stationary draw; §02's answer on returns;
   CLAUDE.md's central results and its strongest test; TODO's "Where things stand"; II-34 to
   `DONE.md`.

## Decided

1. **The hidden-terms account is replaced** (Sergei, 2026-11-06). §09 explained why the three
   hidden terms meet near thirty years as a lift of σ²/2 on the lots held against the drag of the
   book still standing, a decomposition that exists only when exits are measured at the exit
   price. In its place: the cash yield falls as the book deepens (deep lots' calls pay little, and
   the one put a week is spread over more lots) while the economic return rises with the book's
   delta, and the two cross. fig:hidden-terms stays. `model.hidden_terms` and
   `hidden_terms_balance`'s lift/drag/second-order split go with it; the balance horizon itself
   stays, as the point where cash on market value meets the economic return.

2. **The benchmark leads with the capital-share comparison and mentions the delta-scaled one**
   (Sergei, 2026-11-06). The capital-share comparison answers the operator's own question: run the
   wheel, or put the same money in the stock? The delta-scaled one explains the answer. First
   estimates, Standard regime, wheel minus the benchmark:

   | benchmark | 5 y | 30 y | collateral credited at r, 5 y / 30 y |
   |---|---|---|---|
   | the same capital in the stock | −0.34 | −0.20 | −0.16 / −0.11 |
   | the stock scaled to the book's delta | −0.19 | −0.12 | −0.02 / −0.03 |

   Per unit of the exposure it carries the wheel earns what the stock does, less the withheld
   dividend on the shares whose exposure the calls have sold. The options are fairly priced; the
   shortfall against the stock is the exposure the calls give away (Israelov and Nielsen's point,
   once II-33 has checked their words).

## Open questions

3. **When.** Do steps 1–4 now, since they rewrite text already reviewed, and resume the review at
   the benchmark on the new numbers? Lean: yes.
