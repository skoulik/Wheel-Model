# The account's cash, the window's edge, and the book's delta — plan

**Status: agreed 2026-11-13**, in conversation, before any code: the direction and the four
choices on how to carry it through, all under *Decided* below. Closes TODO II-35 when done,
and absorbs what was left of II-34 (steps 6–7 of `drafts/2026-11-06-dollars-per-period-plan.md`).

## What was found

Reviewing "The benchmark that matters", the model's true excess return disagreed with
Black–Scholes delta theory — the book's delta times μ − r, less the withholding leak and the
collateral overcharge — by a residual of +43bp at one year, +2.1 at five and −1.2 at thirty.
It traces to three parts and nothing else (Standard regime, real-world drift, model minus theory):

| | 1 y | 5 y | 10 y | 30 y |
|---|---|---|---|---|
| window edge | +50.8bp | +5.2 | +2.0 | +0.4 |
| premium float | −4.7 | −2.6 | −2.0 | −1.4 |
| delta taken at sale | −0.95 | −0.56 | −0.44 | −0.30 |

1. **The window's edge — a bug.** Over a finite horizon `economics()` spreads each call's premium
   across its four weeks (the occupancy weights of `_time_avg_weights`) but books the call's
   upside surrendered as a point at expiry. Calls still open at the horizon bring in premium and
   none of their cost. It fades as 1/horizon, which is why the pricing-drift check in
   `verify_examples.py` holds only from five years on.
2. **The premium float — an omission.** A premium is booked when the option is sold and set
   against a payout at expiry with no interest between, though the cash earns r meanwhile and the
   option was priced on that. It is the collateral overcharge's twin: account cash not credited r.
3. **Delta taken at sale — the comparison, not the model.** The model prices each option's payoff
   exactly. The comparison used each option's delta when sold, and an option's delta drifts over
   its life.

Removing (1) and (2) makes the pricing-drift identity exact, 0.00bp at every horizon, one year
included. With the collateral credited as well, and the delta averaged over each option's life,
the real-world identity is exact too: **true excess = Δ̄·(μ − r) − withholding leak**, 0.00bp at
5, 10 and 30 years in both regimes.

## Decided (Sergei, 2026-11-13)

1. **Fix the window edge and the premium float throughout the article** — every formula, result,
   figure and piece of supporting prose they reach.
2. **Both piles of cash get the same treatment.** The put's collateral and the premiums held until
   their options expire are cash at the broker earning r, and the ledger credits both. The
   collateral footnote's correction becomes part of the ledger.
3. **The book's delta is computed properly**, averaged over each option's life with its drift.
   The article then explains the usual shortcut — delta at the moment of sale, what a broker's
   screen shows — and what it does to the residual, citing Israelov and Nielsen where relevant.
4. **Track A gets the same interest.** A brokerage statement shows interest on the cash
   balance, and the same cash cannot earn r in one ledger and nothing in the other. Track A
   income gains one line; the cash rows move by 10–20bp. The point where cash on market value
   meets the economic return barely moves, 35.8 → 35.9 years, since the credit enters both.
5. **Every flow is booked on the day it happens, in that day's dollars, and the account's cash
   earns r from the day it arrives.** A premium earns interest from the day the option is sold;
   the upside surrendered is booked at call-away and the mark loss at assignment, undiscounted.
   The premium's interest is counted until its option expires, where the period's books close:
   after that it is income, withdrawn in the model, and kept in the account it would earn r and
   be charged r, adding nothing to the excess. The alternative — discounting each payout back
   to its sale date — was set aside: Track A books no payout to discount, and it would put the
   option flows alone in present-value dollars (it differs by 0.05–0.09bp weekly, 2–3bp at
   quarterly cadence). Withholding is taken at the dividend, at source, and carries no float.
6. **The edge is fixed two independent ways, and they must agree.** In `model.py` a call's
   premium and its upside surrendered carry the same weight, since both belong to one call
   period. In `wheel_sim.py` each option still open at the horizon is marked to market, at its
   Black–Scholes value for the tenor left. The two agree to first order by construction and
   differ only in how delta moves within the last weeks; they must agree within the
   simulation's standard error, or the work stops and is reported.
7. **`code/ledger_dollar_check.py` is deleted.** It has been stale since II-34's step 1, and the
   structural check below does its job exactly. II-34's `DONE.md` entry keeps the record of what
   it showed.

## What moves

First estimates, from scratch scripts. The changed model recomputes them, and they are never
quoted from here:

| | 5 y | 10 y | 30 y |
|---|---|---|---|
| true excess, Standard | 1.23% → 1.38% | 1.31% → 1.44% | 1.40% → 1.49% |
| true excess, Conservative | 1.01% → 1.33% | 1.14% → 1.39% | 1.28% → 1.46% |
| book delta, at sale → over its life (Standard) | 0.875 → 0.872 | 0.902 → 0.900 | 0.932 → 0.931 |
| gap to the same capital in the stock | −0.33 → −0.19 | −0.28 → −0.15 | −0.20 → −0.10 |
| gap to the stock scaled to Δ̄ | −0.19 → −0.035 | −0.16 → −0.028 | −0.12 → −0.020 |
| Track A income, a year | 0.610 → 0.621 | | 0.772 → 0.783 |

**The gap to the stock becomes the exposure the calls sell, exactly**: (shares − Δ̄)·(μ − r),
and against the Δ̄-scaled stock it is exactly the withholding on those shares. Standard and
Conservative then agree to a basis point on both gaps — which is a finding about the regimes,
not a coincidence of the fix, and the Conservative block has to say why.

**The cadence table moves most**, because the float and the collateral both grow with the call
period. At thirty years: weekly 1.40 → 1.49%, biweekly 1.30 → 1.44%, monthly 1.14 → 1.35%,
quarterly 0.77 → 1.16%. The weekly-to-quarterly gap halves, from 63bp to 34bp, and what II-34's
step 6 said about the Bondarenko conflict has to be re-derived, not carried over.

**Stationary figures** (§10, §11) have no window edge; they move by the float and, where the
collateral is counted, by its credit. §11's ledger already leaves the collateral out of the
account (`model.saturation`), so there only the float moves.

## Method

- **`model.py`, the edge.** In `economics()` the upside surrendered takes the call premium's
  occupancy weights. The point weights go.
- **`model.py`, the cash.** `economics()` books interest on the account's cash: r·γ_p·k on the
  collateral, and premium·(e^(rτ) − 1) on each leg's premiums. It enters Track A income and the
  economic ledger alike. `overcharge` goes from the dict; `leak` stays.
- **`model.py`, the delta.** A new `book_delta_life()` beside `book_delta()`: each option's dollar
  delta averaged over its life under the world's drift, discounted at r and stated per unit of
  the price at sale, so that E_P[payoff] − E_Q[payoff] = Δ̄·(μ − r)·τ holds exactly. Closed form
  inside (E[e^X·N(α + βX)] for normal X), Gauss–Legendre over the life. `book_delta()` stays: it
  is the shortcut the article explains, and the beta and shock tables use it.
- **`wheel_sim.py`**, independently: interest credited on the collateral and on each premium until
  its option expires, and options open at the horizon marked to market. `--scenario validate`
  compares component by component again; `--scenario dollars` is retired with the check script,
  or kept as the record of II-34 — Sergei's call.
- **Two exact structural checks in `verify_examples.py`**, replacing the 3bp one that stops at
  five years: at the pricing drift, true excess = −leak at 1, 5, 10 and 30 years; at the
  real-world drift, true excess = Δ̄·(μ − r) − leak at the same horizons, both regimes, to 0.1bp.
- **The carry-through** goes as II-34's did: independent evidence for the new values first,
  crashes before failures, hand-written checks by hand, case literals by script, the appendix as
  CRLF bytes, then only the figures that move.
- **Figures.** `hidden-terms` and `two-ledgers` move and were drawn on cloud, so they are
  redrawn here with matplotlib 3.11.2 installed. Anything else that moves is listed in step 1's
  commit, and its drawing machine is Sergei's call.

## Order of work

Each step is one commit, reviewed before it lands, with `verify_examples.py` green. From step 3
on the review is paragraph by paragraph with Sergei, as §09's has been.

1. **The model and its checks.** Everything under *Method*, CLAUDE.md's central results and its
   strongest test, and the comments over each changed `CASES` list saying the prose lags.
   The sections are knowingly stale for this one commit.
2. **§00 and §04.** The tracks, defined once: Track C charges r on the capital and the account's
   cash earns r; §00's γ_p row, which says the overcharge is "measured in the verification
   section"; eq:excess-return's gloss.
3. **§09, "What comes in" and "What Track A leaves out".** The interest line in eq:income,
   eq:giveaway, eq:econ-pnl and eq:excess.
4. **§09, "The two ledgers, side by side"**, and fig:two-ledgers.
5. **§09, "The benchmark that matters"**, resuming the paragraph review on the new numbers: the
   three-way split of the shortfall becomes two (exposure sold and withholding); the delta detour
   gets its formula, the replication reason, Δ̄, the shortcut and its effect, and a link back to
   §05; the collateral footnote dissolves into the ledger; the closing paragraphs stop arguing
   "identical". Israelov and Nielsen's quotes still wait on II-33, and whether their 51% is a
   delta at sale is part of that check.
6. **§09, the rest:** leverage, the σ_IV table, the cadence table, the dividends, the Conservative
   regime, "What this section produced".
7. **Outside §09:** §02's answer, §05–§08's pointers, §10, §11; TODO's "Where things stand"; II-34
   and II-35 to `DONE.md`.
