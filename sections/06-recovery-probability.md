# The Recovery Probability

## Setup

Assignment has happened. The stock fell through the strike and the operator bought it at k·S₀; the market price now sits at

S′ = S₀ · (1 − d)

where d is the fractional drop from the pre-assignment reference price. The parameter d matters more than it first appears: assignment only tells us the stock finished *below* the strike, not how far below, and the depth of the overshoot is what the lot must climb back out of.

Per the strategy's rules, a covered call is now sold at the same strike the operator paid: K_c = k·S₀. The lot exits inventory if, within one call period τ_c, the stock climbs from S′ back to K_c. The probability of that event is the **recovery probability** q — the single most important quantity in the inventory model, because it sets the rate at which the warehouse empties.

## The formula

Under the same lognormal price model as before — but now using the real-world drift μ, since we are forecasting an actual price path rather than reading a probability out of option prices — the probability that the stock finishes at or above K_c after time τ_c is

q = N( [ (μ − σ²/2) · τ_c − ln( k / (1−d) ) ] / (σ·√τ_c) )

The term ln(k/(1−d)) is the log-distance the stock must travel: from its post-assignment level (1−d) up to the strike level k.

**Numerical verification.** For k = 0.95, d = 0.15 (a 15% drop caused assignment), μ = 7%, σ = 20%, quarterly calls (τ_c = 0.25): the stock must recover about 11.8% to reach the call strike, and q ≈ 16.2% — recovery within any given quarter happens roughly one time in six. Under normal drift that is intuitively reasonable for a 12% climb.

## Properties

Three monotonicities, all intuitive and all consequential:

- **q increases with τ_c.** More time, more chance to recover. This is the argument for longer calls — but we will see it cuts both ways, since longer calls also multiply inventory.
- **q increases with μ.** Stronger drift helps. This is where the "fundamentally sound asset" assumption does quantitative work: μ > 0 with confidence is exactly what that asset selection is meant to buy.
- **q decreases with d.** The deeper the assignment, the further the climb back. This is the strategy's soft spot, and the reason d must be handled carefully rather than assumed.

## How large is d, really?

In the verification above we used d = 0.15, and it is worth pausing on whether that is a typical assignment or a bad one. It is a bad one. The same lognormal model that gives us p also tells us how far below the strike the stock typically lands *given* that assignment occurred, and for the running example (k = 0.95, monthly, σ = 20%) the expected drop conditional on assignment is only about **7.9%** — roughly "just below the strike," as one would expect, not 15% below the reference price. A 15% monthly drop is roughly a 2.5-standard-deviation event.

The difference is not cosmetic. At d = 0.08, the required recovery shrinks to about 3%, and q jumps from 16% to about 42% — the lot typically exits within a couple of quarters instead of a year and a half. Every downstream quantity (inventory, capital, returns) moves substantially with this choice.

> **[Flagged for revision — see TODO #3]** d should not be a free input at all: its distribution conditional on assignment is derivable in closed form from the same model (a truncated-lognormal expectation, already implemented in `code/verify_examples.py`). The plan is to derive E[d | assignment] in the text and use it as the base case, retaining d = 0.15 as an explicitly labeled stress scenario.

## Heterogeneity: the shadow of tier 2

Everything above prices the recovery of a *single* lot against a *fixed* reference price S₀. But q is not constant across inventory: lots acquired at higher prices carry higher absolute strikes, and as the market falls further, those strikes become progressively harder to reach. A lot assigned near the top of a 30% decline may sit under a call strike the stock will not revisit for years, while a lot assigned near the bottom recycles in a quarter. This heterogeneity — old, slow layers pinned under fresh, fast ones — is the central concern of tier 2. For the remainder of tier 1 we adopt the **homogeneous approximation**: all lots share one q. Its cost is assessed in the stability section.
