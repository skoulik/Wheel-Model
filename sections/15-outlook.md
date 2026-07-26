# Outlook {#sec:outlook}

> **Status: stub.** To be written after Parts III and IV, since what belongs here depends on what those establish. The list below records what is deliberately outside the model, so that nothing on it can be mistaken for an oversight.

**The call-strike lever.** The model freezes each lot's call strike at its purchase price forever. Real operators move strikes down to force exits from stuck positions, trading a realized loss for released capital — and they use the lever asymmetrically, raising strikes freely and lowering them rarely. Whether that reluctance is optimal (the option value of waiting) or is loss aversion the model should argue against is a well-posed question the first-passage machinery could answer, since it prices the wait.

**Permanent impairment.** "Fundamentally sound" fails occasionally. A company that collapses permanently puts its lot into an absorbing state with no recovery, no premium and a near-total capital loss — a per-lot death hazard rather than a slow drift, and one whose expected cost can rival a year's premium income even at low rates.

**The entry filter.** The model sells a put every cadence period, unconditionally. Real operation waits for a price worth entering at — the "attractive price" half of [the strategy section](#sec:strategy)'s premise, which is left to the operator by design. The omission is not small: in the live account behind this article the weekly cadence is real, but only about twenty puts per name reach the market in a year rather than fifty-two, and the resulting arrival rate is several times below what the model predicts at the same strike dial. Everything downstream scales with the arrival rate, so this is the largest single gap between the model and the record — and closing it means modelling the operator's judgment, which is a different kind of project.

**Transaction costs.** Commissions are negligible on monthly options and material on short-tenor ones, which matters because a frictionless model has no reason not to prefer ever-shorter tenors — and this article's running example is now firmly in the frictional regime. On the live account, commissions eat a few percent of the premium on weekly puts against a fraction of a percent on monthly ones.

**Volatility skew.** The article's single implied-volatility number cannot express that the puts sold are richer than the calls sold. Since the strategy's whole edge lives in that richness, a two-sided treatment would sharpen the break-even estimate of [the returns section](#sec:returns).

**Volatility that moves.** σ is constant here and is the parameter most obviously not constant in practice — and it enters the stability boundaries quadratically.

**Depth-dependent drift.** The model assumes the expected return of a stock does not depend on how far it has fallen. Value investors assume the opposite, and if they are right, deep lots recover faster than the walk predicts and every result in Part II is conservative.
