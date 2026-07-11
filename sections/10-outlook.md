# Outlook: What Tier 2 Addresses {#sec:outlook}

The homogeneous approximation — one q for every inventory layer — is simultaneously the model's greatest simplification and its most consequential one. Tier 2 replaces it.

**Depth-dependent exit rates.** Specify q_i as an explicit function of layer i's depth: the gap between the layer's frozen strike and the current price. The functional form should incorporate the *valuation-gravity* effect observed in high-quality equities — deep drawdowns in fundamentally sound names attract institutional dip-buying, so recovery drift is not constant in depth. This is where the "fundamentally sound asset" assumption stops being a slogan and becomes a curve.

**The true stability condition.** With q_i specified, derive the actual criterion for boundedness — not merely "I\* is finite," but whether the depth-weighted distribution of exit rates keeps the aggregate departure rate above the arrival rate as layers accumulate. The homogeneous model cannot even pose this question.

**The phase diagram.** Map the strategy's parameter space (p\*, n, σ, μ, and the q_i profile) into regions: **stable** (inventory mean-reverts, self-recycling holds in aggregate), **metastable** (stable in calm regimes, tips into accumulation under stress via the reflexivity channel), and **unstable** (dead strata form under ordinary conditions). The practical payoff of the whole modeling effort is knowing which region a given configuration of the wheel actually occupies.

Alongside tier 2, the open items in `TODO.md` — dividends, the derived distribution of d, the measure policy, exercise-style caveats, and the accounting refinements — are to be folded into the tier 1 sections.
