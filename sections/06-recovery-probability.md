# The Recovery Probability {#sec:recovery}

## Setup

Assignment has happened. The stock fell through the strike and the operator bought it at k·S₀; the market price now sits at

S′ = S₀ · (1 − d)

where d is the fractional drop from the pre-assignment reference price. The parameter d matters more than it first appears: assignment only tells us the stock finished *below* the strike, not how far below, and the depth of the overshoot is what the lot must climb back out of.

Per the strategy's rules, a covered call is now sold at the same strike the operator paid: K_c = k·S₀. The lot exits inventory if, within one call period τ_c, the stock climbs from S′ back to K_c. The probability of that event is the **recovery probability** q — the single most important quantity in the inventory model, because it sets the rate at which the warehouse empties.

## How deep does an assignment land? Deriving d

Before q can be computed we need d, and it is tempting to simply pick a scary-looking number — the article's own first draft assumed d = 0.15 and moved on. But d is not a free parameter. The same lognormal model that produced the assignment probability also says how far below the strike the stock typically finishes *given* that it finished below at all, and deriving that number rather than guessing it turns out to move the strategy's headline economics more than any other single choice in this article.

> **Detour: conditional (truncated) expectation.** An ordinary expectation averages over all scenarios. A **conditional expectation** averages only over the scenarios in which some event happened — "the average size of an insurance claim, *given* that a claim was filed." Computing one means cutting the distribution at the event's boundary and averaging what remains; the piece that remains is called a *truncated* distribution. For the lognormal, these truncated averages (also called *partial expectations*) have closed forms built from the same N(·) function used everywhere else in this article. Any text that derives the Black–Scholes formula computes one along the way; Hull's *Options, Futures, and Other Derivatives* covers it.

Assignment is the event S_T < k·S₀. The lognormal partial-expectation identity gives the average terminal price over exactly those scenarios:

E[S_T | S_T < k·S₀] = S₀ · e^(r·τ_p) · N(−d₁) / N(−d₂)

where d₁ = d₂ + σ·√τ_p — the same pair of quantities from [the assignment section](#sec:assignment): N(−d₂) is the assignment probability itself, and N(−d₁) is the number that appeared there as the put's delta. Since the post-assignment price is S′ = S₀·(1−d), the expected drop conditional on assignment is

**E[d | assignment] = 1 − e^(r·τ_p) · N(−d₁) / N(−d₂)**

**Numerical verification.** For the running example (k = 0.95, τ_p = 1/12, σ = 20%, r = 5%): d₂ ≈ 0.93, d₁ ≈ 0.99, and E[d | assignment] ≈ **7.9%**. The typical assignment lands just under the strike — about 3% below the strike level k = 0.95 — not deep below the reference price. (The formula inherits the risk-neutral convention adopted for p; recomputing with the real-world drift μ = 7% moves the figure by less than 0.1 percentage point. Conditioning on assignment does all the work — one month of drift is noise beside it.)

This fixes the convention for the rest of the article:

- **Base case: d ≈ 0.08**, the derived conditional expectation, rounded.
- **Stress case: d = 0.15**, retained deliberately. A 15% monthly drop is roughly a 2.5-standard-deviation event, and keeping it on the books is honest for two reasons: an average never tells the whole story — conditional on assignment, d has a *distribution*, and gap-downs through the strike (earnings surprises, sector shocks) land in its deep tail; and the stress case previews the regime where the strategy's economics genuinely change, which [the returns section](#sec:returns) will make quantitative.

## The formula

Under the same lognormal price model as before — but now using the real-world drift μ, since we are forecasting an actual price path rather than reading a probability out of option prices — the probability that the stock finishes at or above K_c after time τ_c is

q = N( [ (μ − σ²/2) · τ_c − ln( k / (1−d) ) ] / (σ·√τ_c) )

The term ln(k/(1−d)) is the log-distance the stock must travel: from its post-assignment level (1−d) up to the strike level k.

**Numerical verification.** For k = 0.95, μ = 7%, σ = 20%, quarterly calls (τ_c = 0.25). In the base case d = 0.08, the stock must climb about 3.3% to reach the call strike, and q ≈ 42% — recovery within any given quarter is nearly a coin flip. In the stress case d = 0.15, the required climb is 11.8% and q ≈ 16.2% — one quarter in six. The gap between those two numbers propagates into everything downstream: inventory, capital, returns.

## Properties

Three monotonicities, all intuitive and all consequential:

- **q increases with τ_c.** More time, more chance to recover. This is the argument for longer calls — but we will see it cuts both ways, since longer calls also multiply inventory.
- **q increases with μ.** Stronger drift helps. This is where the "fundamentally sound asset" assumption does quantitative work: μ > 0 with confidence is exactly what that asset selection is meant to buy.
- **q decreases with d.** The deeper the assignment, the further the climb back. This is the strategy's soft spot, and the reason d was derived above rather than guessed — and why the stress case stays on the books next to the base case.

## Heterogeneity: the shadow of tier 2

Everything above prices the recovery of a *single* lot against a *fixed* reference price S₀. But q is not constant across inventory: lots acquired at higher prices carry higher absolute strikes, and as the market falls further, those strikes become progressively harder to reach. A lot assigned near the top of a 30% decline may sit under a call strike the stock will not revisit for years, while a lot assigned near the bottom recycles in a quarter. This heterogeneity — old, slow layers pinned under fresh, fast ones — is the central concern of tier 2. For the remainder of tier 1 we adopt the **homogeneous approximation**: all lots share one q. Its cost is assessed in [the stability section](#sec:stability).
