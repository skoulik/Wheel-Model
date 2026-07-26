# Notation and Conventions {#sec:notation}

This file is the single source of truth for every symbol used in the article. When a section introduces a new symbol, it must be added here. When two sections disagree with this table, this table wins and the sections are wrong.

## Conventions

- All times are measured in **years** (a week is 1/52, four weeks 1/13, a month 1/12, a quarter 0.25).
- Prices of options and strikes are expressed as **fractions of the underlying price** at the moment of reference, so they are dimensionless. A premium c_p = 0.005 means the put sells for 0.5% of the stock price. Capital is quoted the same way: "capital of 5.1" means five times the current share price.
- Rates (r, μ) and volatility (σ) are **annualized**.
- Math is written in Unicode plain text in these drafts; conversion to LaTeX happens at assembly time.
- **One measure, two worlds.** Every probability and expectation in this article is computed under a single price drift m, and the whole model is one chain of formulas parameterized by it. Setting m = μ − δ gives the **real-world** reading (what actually happens); setting m = r − δ gives the **risk-neutral** reading (what the option market's prices imply). Both are self-consistent, and where they differ materially the article reports both. Option premiums are never computed from either: they are **quotes**, market data, read off the screen and parameterized in the market's own convention (Black–Scholes at implied volatility). See [the entry section](#sec:entry).
- **Cross-references:** every section's H1 carries a pandoc-style anchor (`# Title {#sec:name}`), and in-prose references are written as markdown links to those anchors — e.g. `[the holding-time section](#sec:holding)`. At assembly time these become `\label`/`\ref` pairs. Never refer to another section by bare prose or by number; always link. Current anchors: sec:notation, sec:abstract, sec:introduction, sec:prior-work, sec:strategy, sec:entry, sec:depth, sec:holding, sec:inventory, sec:returns, sec:stability, sec:portfolio, sec:correlation, sec:verification, sec:live, sec:outlook.
- **Formula numbering:** every displayed (non-inline) formula carries a pandoc-style anchor at the end of its display line — `E[I] = λ · E[W]    {#eq:little}`. In-prose references are markdown links to those anchors, e.g. `formula [eq:little](#eq:little)`. At assembly time the display becomes a numbered `equation` environment with `\label{eq:name}`, and each reference link is replaced wholesale by `\eqref{eq:name}` — a literal "(N)" — so phrase references to read naturally with a bare number in the link's place ("formula (7)"). Never refer to a displayed formula by paraphrase or by its section alone; cite its anchor. Current anchors: eq:n, eq:excess-return (section 04); eq:kstar, eq:p-screen, eq:x0-law, eq:d-mean (05); eq:depth-walk, eq:nu, eq:qx, eq:ccx (06); eq:siegmund, eq:survival, eq:holding, eq:trapped (07); eq:little, eq:census (08); eq:income, eq:capital, eq:econ-pnl, eq:excess (09); eq:count-criterion, eq:capital-criterion (10).
- Every worked numerical example in the text is recomputed by `code/verify_examples.py`, which is organized section by section. If you change a formula or an example, update and re-run the script.

## Market and asset parameters

| Symbol | Meaning |
|---|---|
| S, S₀ | Price of the underlying stock; S₀ when a fixed reference moment matters |
| μ | Real-world expected annual **total return** of the stock — price appreciation plus dividend yield |
| r | Risk-free interest rate, annualized |
| σ | Volatility of the stock's returns, annualized — the **realized** volatility, which governs the actual price path |
| σ_IV | Implied volatility: the number the market quotes option prices in. The article's results assume σ_IV = σ (no volatility risk premium) unless stated, and [the returns section](#sec:returns) computes what spread would be needed to change the verdict |
| δ | Continuous dividend yield, annualized, gross of withholding (running example: 2.5%) |
| w | Withholding tax fraction on dividends (running example: 15%, the common treaty rate) |
| δ_net | Net dividend yield retained by the operator: δ_net = δ·(1−w) (running example: ≈ 2.1%) |
| **m** | **The price drift of the world being computed in**: m = μ − δ in the real world, m = r − δ under the market's pricing measure. The dividend is subtracted because it is paid out of the price |

## Strategy parameters (chosen by the operator)

| Symbol | Meaning |
|---|---|
| T | **Cadence**: how often a new put is sold (running example: weekly) |
| τ_p | **Tenor**: how long each put runs, τ_p ≤ T. The article's examples use τ_p = T; the two come apart in real operation, see [the live-account section](#sec:live) |
| τ_c | Lifetime of each covered call sold; τ_c ≥ τ_p (running example: four weeks) |
| n | The clock ratio τ_c / τ_p ≥ 1 (weekly puts with four-week calls give n = 4) |
| k | Put strike as a fraction of the current price, k = K/S (k = 0.95 is a 5% out-of-the-money put) |
| p\* | **The strike dial**: the assignment probability the operator targets, from which the strike k\* follows by [eq:kstar](#eq:kstar). Two regimes are carried throughout — **Standard** p\* = 20% and **Conservative** p\* = 10% |
| γ | Margin fraction the broker requires on a short put position (running example: 0.20) |
| K_c | Covered call strike, frozen at the price the lot was bought at: K_c = k·S at the moment of assignment |

## The depth process and its statistics

| Symbol | Meaning |
|---|---|
| x | **Depth** of a lot: x = ln(K_c/S), how far its frozen call strike sits above the current price. The state variable of the whole model |
| x₀ | Depth at the moment of assignment, distributed by [eq:x0-law](#eq:x0-law) |
| ν | Drift of the depth process, ν = m − σ²/2 — the rate at which depth is worked off ([eq:nu](#eq:nu)) |
| q(x) | Probability that a lot at depth x is called away at the end of the current call period ([eq:qx](#eq:qx)) |
| c_p | Put premium received, as a fraction of the price at the sale. A quote |
| c_c(x) | Call premium received on a lot at depth x, as a fraction of the current price. A quote ([eq:ccx](#eq:ccx)) |
| J | Number of call periods a lot lives through before being called away |
| W | Holding time of a lot, W = J·τ_c |
| S_j | Survival sequence, S_j = P(J > j) ([eq:survival](#eq:survival)) |
| β | Siegmund's overshoot constant, β = −ζ(1/2)/√(2π) ≈ 0.5826, the size of the call-grid tax ([eq:siegmund](#eq:siegmund)) |
| θ | Tail exponent of the standing inventory's depth distribution, θ = 2ν/σ² ([eq:capital-criterion](#eq:capital-criterion)) |
| λ | Arrival rate of new lots per year, λ = p\*/T |
| I, I(t) | Number of inventory lots held — a random variable; I(t) when the time path matters |
| ρ(x) | Stationary depth census: how the standing inventory is distributed over depth ([eq:census](#eq:census)) |
| d | Fractional price drop at the moment of assignment, S → S(1−d). Not a free input: it follows from x₀, and its average is [eq:d-mean](#eq:d-mean) (≈ 3.8% for the running example) |

## Probability notation

| Symbol | Meaning |
|---|---|
| N(·) | Standard normal cumulative distribution function |
| N⁻¹(·) | Its inverse (quantile function) |
| P(·), E[·] | Probability and expectation |

## The three accounting tracks

| Track | Question it answers |
|---|---|
| A | Realized cash flows only: premiums received, dividends collected, and cash exchanged when lots are bought and sold. Assignment is inventory acquisition, not a loss. This is what a brokerage statement shows |
| B | Capital committed, valued at market: broker margin on the live short put plus the **market value** of the shares held. What could be redeployed if the position were closed |
| C | Opportunity cost: the risk-free rate charged against the capital in Track B |

The headline number is the **true excess return** — [eq:excess](#eq:excess) in [the returns section](#sec:returns) — which values inventory at market, books the mark loss at acquisition and the upside surrendered at call-away, and charges r on Track B. It is the only convention that satisfies no-arbitrage, and that fact is used as a test in [the verification section](#sec:verification). The Track A cash view is reported next to it because it is what operators actually see, and because the gap between the two is instructive.
