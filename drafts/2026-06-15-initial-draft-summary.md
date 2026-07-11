## Summary of the Model: The Wheel Strategy as a Stochastic Inventory System

### What the Strategy Is

The strategy sells put options repeatedly on assets considered fundamentally sound — large, dividend-paying companies unlikely to collapse permanently. Selling a put means accepting an obligation: if the stock falls below a chosen level (the strike price) by expiration, you must buy it at that strike. In exchange, you collect a cash payment upfront (the premium).

If no assignment happens, you collect the premium and sell another put. If assignment does happen, you now own the stock. You then sell a covered call against it — the opposite obligation, promising to sell the stock back at the same strike price you paid if it recovers there. Again you collect a premium. You repeat until the stock recovers and you are "called away," then start again.

Two period lengths govern the strategy: τ_p is how long each put option runs, and τ_c is how long each covered call runs, with τ_c ≥ τ_p. You can use weekly puts with monthly calls, or monthly puts with quarterly calls, and so on. The ratio n = τ_c / τ_p ≥ 1 turns out to matter considerably.

Three accounting tracks run in parallel throughout, answering three different questions. Track A records only realized cash flows — premiums received and capital gains when called away — and treats assignment as inventory acquisition, not a loss. Track B tracks capital committed at current market prices, because brokers compute margin requirements on live prices regardless of the operator's accounting philosophy. Track C charges the risk-free rate against committed capital, capturing the opportunity cost of money that could be earning interest elsewhere. True excess return is (Track A minus Track C) divided by Track B, annualized.

---

### The Assignment Probability

*A brief aside for those unfamiliar with probability distributions:* When something either happens or doesn't — a coin flip, a die roll checking for a six, a put option either assigning or not — and each trial is independent of the others, statisticians call this a Bernoulli event. The only parameter is p, the probability it happens. When you sell a put option, you are running one Bernoulli trial.

The probability of assignment p is computed from the Black-Scholes model. The corrected formula (the previous version had a sign reversal in the logarithm) is:

p = N(−d₂),    d₂ = [−ln(k) + (r − σ²/2) × τ_p] / (σ√τ_p)

where k = K/S₀ is the strike expressed as a fraction of current price (so k = 0.95 means a 5% out-of-the-money put), r is the risk-free rate, σ is implied volatility, and N(·) is the standard normal cumulative distribution — a lookup that converts a standardized score into a probability.

Numerical verification: for k = 0.95, monthly put (τ_p = 1/12 of a year), σ = 20%, r = 5%, this gives d₂ ≈ 0.93 and p ≈ 18%. This matches market convention for what is called a "20-delta put," confirming the sign is now correct. The previous version gave d₂ ≈ −0.84 and p ≈ 80%, which is obviously wrong for a mildly out-of-the-money option.

To find the strike that hits a target assignment probability p\*, invert the formula:

k\*(τ_p) = exp(N⁻¹(p\*) × σ√τ_p + (r − σ²/2) × τ_p)

For a 20% target (N⁻¹(0.20) ≈ −0.842) with the same parameters, this gives k\* ≈ 0.955, confirming that a 20% assignment probability corresponds to a strike about 4.5% below current price on a monthly option.

This formula uses the risk-neutral probability — the one consistent with option prices — which overestimates how often assignment actually occurs in practice, because stocks tend to drift upward over time. The real-world assignment frequency is lower by a factor controlled by the Sharpe ratio of the asset and the square root of the period length:

p_rw = N(−d₂ + (r − μ) × √τ_p / σ)

Since μ > r for equities, the correction term is negative, making p_rw < p. Using the risk-neutral p throughout the model is therefore conservative — it assumes a harder environment than reality for a fundamentally sound asset. The gap grows with √τ_p, so longer-dated puts are more conservatively modeled relative to reality.

---

### The Recovery Probability

The call-away probability q is what determines how quickly inventory unwinds. After assignment at price S' = S₀(1−d) — where d is the fractional drop that caused assignment — the covered call strike sits at K_c = k × S₀. The stock must climb from S' back to K_c within τ_c for the call to be exercised. The corrected formula (again, the previous sign was inverted) is:

q = N([(μ − σ²/2) × τ_c − ln(k / (1−d))] / (σ√τ_c))

Numerical verification: for k = 0.95, d = 0.15 (15% drop caused assignment), μ = 7%, σ = 20%, quarterly calls (τ_c = 0.25 years), this gives q ≈ 16%. The stock must recover about 12% from the assignment price to reach the call strike — occurring roughly one in six quarters under normal drift, which is intuitively reasonable.

Key properties: q increases with τ_c (more time means more chance of recovery), increases with μ (stronger positive drift helps), and decreases with d (the deeper the assignment, the further the stock must climb back). Critically, q is not constant across inventory layers — lots acquired at higher prices have higher absolute strikes, which become progressively harder to reach as prices fall further. This heterogeneity is the central concern of tier 2.

---

### The Inventory Queue: Many Periods, Many Layers

*An analogy:* Imagine running a storage warehouse. Each week, a delivery truck arrives with a new pallet with probability p (the put assigns) or doesn't (probability 1−p). Each pallet already in the warehouse independently has a chance q_p of being picked up and removed that same week (the covered call is exercised for that lot). When deliveries outpace pickups, inventory grows. When pickups outpace deliveries, the warehouse empties. Eventually, if the rates are stable, the warehouse reaches an average occupancy.

Here q_p is the per-put-period probability of call-away for each lot, derived from the per-call-period probability q by:

q_p = 1 − (1−q)^(1/n) ≈ q/n    for small q

The approximation q/n is accurate when q is not too large, which holds comfortably for n ≥ 2 or for modest q values.

**The Poisson steady-state distribution.** A Poisson distribution describes the count of independent random events occurring at a constant average rate — the number of phone calls arriving at a switchboard per hour, the number of bus passengers boarding per stop, or in our case, the number of inventory lots held at equilibrium. It is characterized entirely by one number, its mean, and has the distinctive property that variance equals mean: if the average is four lots, the typical swing around that average is roughly ±2 lots (the square root of four).

For the inventory system with constant arrival rate p and state-proportional departure rate q_p × i, the steady-state distribution is well approximated by a Poisson with mean:

I\* = p / q_p = p × n / q = p × (τ_c / τ_p) / q

Full distribution: P(I = i) = e^(−I\*) × (I\*)^i / i!

This approximation is exact in the continuous-time limit and very accurate for the discrete-time model when q_p is small, which is ensured whenever n is not too small or q is moderate. For n = 1 and large q simultaneously, the approximation degrades somewhat, but the equilibrium mean I\* remains exact regardless.

From the Poisson distribution:
- Average inventory held: E[I] = I\*
- Probability of holding no inventory at all: P(I = 0) = e^(−I\*). For I\* = 1, this is about 37%; for I\* = 2, about 14%; for I\* = 3, about 5%.
- The ratio τ_c/τ_p acts as a direct multiplier on I\*: doubling the call period for the same p and q doubles the average inventory. Longer calls are more expensive in terms of capital lockup.

---

### The Self-Recycling Result

One of the cleanest results of the model is what happens in steady state. The average number of new assignments per period is p (one put sold, assigns with probability p). The average number of call-aways per period is E[I] × q_p = I\* × q_p = (pn/q) × (q/n) = p. The two rates are identical.

In plain terms: in the long run, the system is returning inventory at exactly the rate it acquires it. New lots arrive, old lots depart, and the warehouse hums at its equilibrium occupancy. Each departed lot realizes a capital gain equal to the original put premium for that lot — so the system is continuously recycling: put premiums earned on entry are recovered again on exit, while call premiums accumulate in between.

---

### Expected Returns and Capital Commitment

In the homogeneous approximation — valid when price levels are roughly stable and all layers share similar characteristics — the per-period P&L normalized by current price S is:

E[Π / period] / S = c_p(1 + p) + p × c_c/q − p × (k − 1 + d)

The three terms decompose cleanly. The term c_p(1+p) captures all put-derived income: the premium c_p collected when each new put is sold, plus the average capital gain p × c_p recycled from call-aways (the original put premium recovered at exit, since capital gain at call-away equals the original put premium by construction). The term p × c_c/q is call premium income — the average of I\* = pn/q lots each contributing c_c/n per put period, which telescopes to p × c_c/q. The final term p × (k−1+d) is the assignment drag, the average cost of acquiring inventory above its immediate post-assignment market price.

Annualizing by dividing through by τ_p gives the expected annual return per unit of asset price. Capital committed in steady state is approximately:

E[Capital] / S₀ ≈ m × k + I\* × (k − c_p)

the first term being margin on the current put, the second the average cost basis across inventory lots.

**Capital convergence in stress.** If price falls geometrically — every assignment occurs at price S_j = S₀(1−d)^j — then cost bases shrink geometrically too: B_j = (k−c_p) × S_j. Even summing infinitely many lots, the total converges:

Σ B_j = (k − c_p) × S₀ / d

For k = 0.95, c_p = 0.02, d = 0.15, this bound is (0.93/0.15) × S₀ ≈ 6.2 × S₀ in total cost basis regardless of how many lots accumulate. With margin fraction m = 0.20, maximum margin consumed by put-selling stays bounded. This is reassuring, but it depends entirely on the geometric structure of price decline — equal percentage drops each assignment. Real markets often drop sharply and then flatline, which stalls the geometric compression and allows capital to accumulate at similar price levels without convergence. This is the primary practical failure mode, addressed in tier 2.

---

### Stability: When Does the System Stay Bounded?

Under the homogeneous approximation with constant q, the system is always stable in the sense that I\* is finite whenever q > 0. The real instability emerges in the heterogeneous case: old lots acquired at higher prices have strikes further from the current depressed price, making their q_i smaller than that of newer lots. If q_i declines fast enough with layer depth, the effective average exit rate falls below p — old layers accumulate permanently while new ones keep arriving on top. Capital becomes trapped in dead strata that never unwind.

The secondary danger is reflexivity: in falling markets, implied volatility rises, pushing p upward (more puts land in the money), while recovery becomes harder, pushing q downward. Both move I\* = pn/q upward simultaneously and nonlinearly. A market that doubles p and halves q produces a fourfold increase in equilibrium inventory. The system can appear comfortable in mild stress and deteriorate rapidly in severe stress.

---

### What Tier 2 Addresses

The homogeneous approximation — uniform q across all layers — is both the model's greatest simplification and its most important limitation. Tier 2 will specify q_i as an explicit function of the layer's depth relative to current price, incorporating the valuation-gravity effect observed in high-quality equities (where deep drawdowns attract institutional dip-buying). From there the true stability condition — not just I\* finite, but the distribution of q_i weighted by layer depth — can be derived, and the phase diagram mapping the strategy's parameter space into stable, metastable, and unstable regions can be constructed.