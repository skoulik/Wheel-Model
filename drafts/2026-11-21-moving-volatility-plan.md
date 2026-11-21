# Moving volatility and jumps in the base model — plan

**Status: agreed 2026-11-21**, in conversation, before any code: the representation and the six
choices under *Decided*. Nothing is measured or coded yet. Takes up TODO II-40, and absorbs
II-38 (the swing structure on single names, step 4) and II-39 (the excess return under
changing volatility, step 5). Sergei, 2026-11-20: "Perhaps we still need
to incorporate sigma change with the stock movement into the base model … This would involve
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
   each filing with its item codes. Foreign private issuers file 6-Ks, which carry none — NVO,
   ATHM and BEKE among the names in `data/prices` — so their dates are detected as gaps a
   quarter apart, or the names are left out of the earnings fit. EDGAR's fair-access policy
   asks an automated client to declare a contact in its User-Agent.

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
through the same convexity as σ²/2.

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

- **Earnings first, then jumps, then the state**, each fitted on what the previous step leaves:
  otherwise an earnings day is counted as a jump and again as a volatility swing.
- **The state:** realized-volatility statistics from `data/prices` (171 names, daily, up to
  2018–2026) and the S&P series, on a jump-robust realized variance (bipower variation).
- **Unscheduled jumps:** the days that variance flags, outside earnings dates, split by sign.
  The index's jumps are mostly down and cannot be borrowed for a single name.
- **Earnings:** the dates are not in `data/prices` (the fetch takes dividends and splits only).
- **The overlay:** the trade-log IV panel, re-measured against the fair layer at the same state.
  Two cautions on the panel as it stands: the shallow-to-deep rise in σ_IV(x) is partly state —
  lots get deep in falls that raised volatility — and must be split before an overlay is set;
  and the put skew is absolute IV by percent moneyness across names, where at a fixed p\* a
  volatile name's put is struck further out (unchecked: likely much of the slope).
- **Better, if obtainable:** a daily implied-volatility series per name (IBKR's historical data
  offers OPTION_IMPLIED_VOLATILITY; its depth for single names unchecked), and Cboe's VIX for
  the index.

## Sequence

1. **Earnings dates** (decision 6). Fetch and cache them beside `data/prices`; check on the
   first fetch that the item codes reach back to 2018 and that the filing day is the day of
   the gap. The fair-access contact is settled with Sergei first.
2. **Takeovers' rarity** (decision 5). Count acquisitions among the S&P 500 Dividend
   Aristocrats from the index's published changes, against member-years, over as long a
   window as the changes are published for. The traded universe cannot answer it — an acquired
   name drops out of the price histories, so the names held are survivors by construction.
   If the rate is low, the article says so, with the rate, where it introduces jumps.
3. **Unscheduled jumps.** The days the jump-robust variance flags, outside earnings dates and
   takeover bids, split by sign: λ↑, λ↓, the two size laws and each side's kick to h.
4. **The state — II-38, widened.** σ̄, half-life, θ, γ and η per name and across names, on what
   steps 1–3 leave, with the S&P for comparison; II-38's three statistics fall out of it. This
   is where the γ hypothesis is tested.
5. **The simulator.** `wheel_sim.py` carries the process — jumps and earnings included — and
   prices options fair at the state, which is II-39's proper pricing. One reading needs no
   calibration and can run first: how much of d's tail the present `--scenario stochvol`
   explains.
6. **The overlay**, from the trade-log panel against the fair layer at the same state; the IBKR
   implied-volatility series if it can be had.
7. **Magnitudes**, result by result, from the simulator; then `model.py` (h on 10–15 nodes, the
   depth walk modulated by them) and where in the article it lives — a revision of Part II, or
   the model kept and the difference reported where the assumption bites. Decided then, on the
   measurements.
