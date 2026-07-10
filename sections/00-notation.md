# Notation and Conventions

This file is the single source of truth for every symbol used in the article. When a section introduces a new symbol, it must be added here. When two sections disagree with this table, this table wins and the sections are wrong.

## Conventions

- All times are measured in **years** (a month is 1/12, a quarter is 0.25).
- Prices of options and strikes are expressed as **fractions of the underlying price** at the moment of reference, so they are dimensionless. A premium c_p = 0.005 means the put sells for 0.5% of the stock price.
- Rates (r, μ) and volatility (σ) are **annualized**.
- Probabilities named p refer to the put leg; probabilities named q refer to the call leg.
- Math is written in Unicode plain text in these drafts; conversion to LaTeX happens at assembly time.
- Every worked numerical example in the text is recomputed by `code/verify_examples.py`. If you change a formula or an example, update and re-run the script.

## Market and asset parameters

| Symbol | Meaning |
|---|---|
| S₀ | Price of the underlying stock at the moment of reference |
| μ | Real-world (expected) annual drift of the stock's return |
| r | Risk-free interest rate, annualized |
| σ | Volatility of the stock's returns, annualized (currently a single number; see TODO on distinguishing implied vs realized) |

## Strategy parameters (chosen by the operator)

| Symbol | Meaning |
|---|---|
| τ_p | Lifetime of each put option sold (e.g., 1/12 for monthly puts) |
| τ_c | Lifetime of each covered call sold; τ_c ≥ τ_p |
| n | The clock ratio τ_c / τ_p ≥ 1 (e.g., monthly puts with quarterly calls give n = 3) |
| k | Put strike as a fraction of current price, k = K/S₀ (k = 0.95 is a 5% out-of-the-money put) |
| p\* | Target assignment probability, when the strike is chosen by inverting for it |
| m | Margin fraction the broker requires on a short put position |

## Derived quantities

| Symbol | Meaning |
|---|---|
| d₂, d₁ | The standard Black–Scholes intermediate quantities (defined where first used) |
| p | Risk-neutral probability the put is assigned at expiration, p = N(−d₂) |
| p_rw | Real-world assignment probability (uses μ instead of r); p_rw < p for equities |
| d | Fractional price drop at the moment of assignment: the stock sits at S′ = S₀(1−d) |
| S′ | Stock price just after assignment, S′ = S₀(1−d) |
| K_c | Covered call strike; in the base model K_c equals the put strike, K_c = k·S₀ |
| q | Probability the covered call finishes in the money within one call period τ_c |
| q_p | The same exit probability converted to the put-period clock: q_p = 1 − (1−q)^(1/n) ≈ q/n |
| c_p | Put premium received, as a fraction of S₀ |
| c_c | Call premium received, as a fraction of S₀ |
| I | Number of inventory lots (assigned stock positions) currently held — a random variable |
| I\* | Steady-state mean of I: I\* = p/q_p ≈ p·n/q |
| B_j | Cost basis of the j-th inventory lot |

## Probability notation

| Symbol | Meaning |
|---|---|
| N(·) | Standard normal cumulative distribution function |
| N⁻¹(·) | Its inverse (quantile function) |
| P(·), E[·] | Probability and expectation |

## The three accounting tracks

| Track | Question it answers |
|---|---|
| A | Realized cash flows only: premiums received plus capital gains at call-away. Assignment is inventory acquisition, not a loss. |
| B | Capital committed at current market prices — what the broker margins, regardless of the operator's accounting philosophy. |
| C | Opportunity cost: the risk-free rate charged against committed capital. |

True excess return = (Track A − Track C) / Track B, annualized.
