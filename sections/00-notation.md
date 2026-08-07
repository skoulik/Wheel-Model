# Notation and Conventions {#sec:notation}

This file is the single source of truth for every symbol used in the article. When a section introduces a new symbol, it must be added here. When two sections disagree with this table, this table wins and the sections are wrong.

## Conventions

- All times are measured in **years** (a week is 1/52, four weeks 1/13, a month 1/12, a quarter 0.25).
- Prices of options and strikes are expressed as **fractions of the underlying price** at the moment of reference, so they are dimensionless. A premium c_p = 0.005 means the put sells for 0.5% of the stock price. Capital is quoted the same way: "capital of 5.1" means five times the current share price.
- Rates (r, μ) and volatility (σ) are **annualized**.
- Math is written in Unicode plain text in these drafts; conversion to LaTeX happens at assembly time.
- **One measure, two worlds.** Every probability and expectation in this article is computed under a single price drift m, and the whole model is one chain of formulas parameterized by it. Setting m = μ − δ gives the **real-world** reading (what actually happens); setting m = r − δ gives the **risk-neutral** reading (what the option market's prices imply). Both are self-consistent, and where they differ materially the article reports both. Option premiums are never computed from either: they are **quotes**, market data, read off the screen and parameterized in the market's own convention (Black–Scholes at implied volatility). See [the entry section](#sec:entry).
- **Cross-references:** every section's H1 carries a pandoc-style anchor (`# Title {#sec:name}`), and in-prose references are written as markdown links to those anchors — e.g. `[the holding-time section](#sec:holding)`. At assembly time these become `\label`/`\ref` pairs. Never refer to another section by bare prose or by number; always link. Current anchors: sec:notation, sec:abstract, sec:introduction, sec:prior-work, sec:strategy, sec:entry, sec:depth, sec:holding, sec:inventory, sec:returns, sec:stability, sec:constrained, sec:portfolio, sec:correlation, sec:verification, sec:live, sec:outlook, sec:bibliography.
- **Formula numbering:** every displayed (non-inline) formula carries a pandoc-style anchor at the end of its display line — `E[I] = λ · E[W]    {#eq:little}`. In-prose references are markdown links to those anchors, e.g. `formula [eq:little](#eq:little)`. At assembly time the display becomes a numbered `equation` environment with `\label{eq:name}`, and each reference link is replaced wholesale by `\eqref{eq:name}` — a literal "(N)" — so phrase references to read naturally with a bare number in the link's place ("formula (7)"). Never refer to a displayed formula by paraphrase or by its section alone; cite its anchor. Current anchors, in reading order within each section: eq:n, eq:excess-return (section 04); eq:wait, eq:normal, eq:phi, eq:lognormal, eq:bs-put, eq:bs-call, eq:iv, eq:kstar, eq:p-screen, eq:screen-gap, eq:x0-def, eq:x0-law, eq:d-mean (05); eq:depth-def, eq:depth-walk, eq:nu, eq:qx, eq:ccx (06); eq:siegmund, eq:survival, eq:holding, eq:holding-siegmund, eq:trapped (07); eq:lambda, eq:little, eq:little-finite, eq:census (08); eq:income, eq:capital, eq:mark-loss, eq:giveaway, eq:econ-pnl, eq:excess, eq:levered-excess (09); eq:count-criterion, eq:basis-multiplier, eq:capital-criterion, eq:theta, eq:account-criterion (10); eq:leverage, eq:barrier, eq:first-passage, eq:survive, eq:lmax, eq:capacity, eq:lambda-eff, eq:income-capacity, eq:astar, eq:debit-growth, eq:theta-eff, eq:gmax, eq:draw, eq:capacity-lots (11).
- **Citations:** the bibliography ([the references section](#sec:bibliography)) is the only file that may declare a `{#ref:...}` anchor, and it is the anchor list — unlike sections and formulas, there is no register to keep here. A citation in prose is a markdown link to one, written so the sentence still reads with the link's text in place — `a correction due to [Siegmund](#ref:siegmund-1979)`. At assembly the whole link becomes `\cite{key}` — a bracketed number. **Never write a citation number in the source**, for the same reason no section or formula number is written there: the numbers are assigned at assembly from the bibliography's order, so inserting an entry renumbers nothing and cannot silently mis-cite. Cite at the first place a reader meets the claim, not only where the source is described.
- Every worked numerical example in the text is recomputed by `code/verify_examples.py`, which is organized section by section. If you change a formula or an example, update and re-run the script.

## Market and asset parameters

| Symbol | Meaning |
|---|---|
| S, S₀ | Price of the underlying stock; S₀ when a fixed reference moment matters |
| μ | Real-world expected annual **total return** of the stock — price appreciation plus dividend yield |
| r | Risk-free interest rate, annualized |
| σ | Volatility of the stock's returns, annualized — the **realized** volatility, which governs the actual price path |
| σ_IV | Implied volatility: the number the market quotes option prices in. The article's results assume σ_IV = σ (no volatility risk premium) unless stated, and [the returns section](#sec:returns) computes what spread would be needed to change the verdict. **A single scalar**: one value for both legs, every strike and every lot depth. Real surfaces are flat in neither direction, and [the returns section](#sec:returns) names what that costs and why it is not carried |
| δ | Continuous dividend yield, annualized, gross of withholding (running example: 2.5%). Held **constant**, which assumes the payout tracks the price's *trend* — a company raising its dividend at the price's log drift ν has, by construction, a constant yield. It does **not** assume the payout is cut when the price dips; see [the depth section](#sec:depth) |
| w | Withholding tax fraction on dividends (running example: 15%, the common treaty rate) |
| δ_net | Net dividend yield retained by the operator: δ_net = δ·(1−w) (running example: ≈ 2.1%) |
| δ_eff | Sensitivity device, not a parameter: the yield to run the model at if the payout is fixed in dollars between raises rather than tracking the price continuously. Used once, in [the returns section](#sec:returns), to bound that assumption at 2.78% over thirty years |
| **m** | **The price drift of the world being computed in**: m = μ − δ in the real world, m = r − δ under the market's pricing measure. The dividend is subtracted because it is paid out of the price |

## Strategy parameters (chosen by the operator)

| Symbol | Meaning |
|---|---|
| T | **Cadence**: how often a new put is sold (running example: weekly) |
| τ_p | **Tenor**: how long each put runs, τ_p ≤ T. The article's examples use τ_p = T; the two come apart in real operation, see [the live-account section](#sec:live) |
| τ_c | Lifetime of each covered call sold; τ_c ≥ τ_p (running example: four weeks) |
| n | The clock ratio τ_c / τ_p ≥ 1 (weekly puts with four-week calls give n = 4) |
| k | Put strike as a fraction of the current price, k = K/S (k = 0.95 is a 5% out-of-the-money put) |
| p\* | **The strike dial**: the assignment probability the operator targets, from which the strike k\* follows by [eq:kstar](#eq:kstar). Two regimes are carried throughout — **Standard** p\* = 20%, which leads the worked examples as the conventional setting to pair with a stylized 20%-volatility market, and **Conservative** p\* = 10%, which is the setting the live account is measured to run at. See [the entry section](#sec:entry) for the measurement and for why the stylized value leads |
| γ_p | Margin fraction the broker requires on a short **put** position (running example: 0.20). Track C charges r on γ_p·k although the collateral behind it earns approximately r at the broker; the resulting overcharge is footnoted in [the returns section](#sec:returns) and measured in [the verification section](#sec:verification). Its counterpart against held shares is γ_s, in the working-capital table below |
| K_c | Covered call strike, frozen at the price the lot was bought at: K_c = k·S at the moment of assignment |

## The depth process and its statistics

| Symbol | Meaning |
|---|---|
| x | **Depth** of a lot: x = ln(K_c/S) ([eq:depth-def](#eq:depth-def)), how far its frozen call strike sits above the current price. The state variable of the whole model |
| x₀ | Depth at the moment of assignment ([eq:x0-def](#eq:x0-def)), distributed by [eq:x0-law](#eq:x0-law) |
| ν | Drift of the depth process, ν = m − σ²/2 — the rate at which depth is worked off ([eq:nu](#eq:nu)) |
| q(x) | Probability that a lot at depth x is called away at the end of the current call period ([eq:qx](#eq:qx)) |
| c_p | Put premium received, as a fraction of the price at the sale. A quote |
| c_c(x) | Call premium received on a lot at depth x, as a fraction of the current price. A quote ([eq:ccx](#eq:ccx)) |
| J | Number of call periods a lot lives through before being called away |
| W | Holding time of a lot, W = J·τ_c |
| S_j | Survival sequence, S_j = P(J > j) ([eq:survival](#eq:survival)) |
| β | the overshoot constant, β = −ζ(1/2)/√(2π) ≈ 0.5826, the size of the call-grid tax ([eq:siegmund](#eq:siegmund)). It is the *limiting expected overshoot* — how far past a level a sampled walk stands when first observed beyond it — for a barrier infinitely far away; this article's barrier sits 0.28 of a step off, where the true overshoot is 0.667. Usually attributed to Siegmund; it originates with [Chernoff](#ref:chernoff-1965) and reaches this article's use of it through [Broadie, Glasserman & Kou](#ref:broadie-glasserman-kou-1997). See [the holding-time section](#sec:holding) |
| θ | Tail exponent of the standing inventory's depth distribution, θ = 2ν/σ² ([eq:theta](#eq:theta)); it is also the exponent governing a levered account's survival, see [eq:survive](#eq:survive) |
| λ | Arrival rate of new lots per year, λ = p\*/T ([eq:lambda](#eq:lambda)) |
| I, I(t) | Number of inventory lots held — a random variable; I(t) when the time path matters |
| ρ(x) | Stationary depth census: how the standing inventory is distributed over depth ([eq:census](#eq:census)) |
| d | Fractional price drop at the moment of assignment, S → S(1−d). Not a free input: it follows from x₀, and its average is [eq:d-mean](#eq:d-mean) (≈ 3.8% for the running example) |

## Working capital and the finite account

Everything above describes an operator who buys whatever the puts assign. A real account has a finite balance and a broker with an opinion about it, and [the constrained section](#sec:constrained) is where that operator appears. These symbols are used there and nowhere earlier, with two exceptions. [The stability section](#sec:stability) states the third stability boundary as ν > g ([eq:account-criterion](#eq:account-criterion)), because that is where the three boundaries are set beside each other, and leaves g's derivation to the constrained section. And [the returns section](#sec:returns) reads γ_s, L and the financing spread once, to price what borrowing does to the excess return ([eq:levered-excess](#eq:levered-excess)) — the cost of leverage being a return calculation, while the amount of it an account can carry is capacity and stays here.

| Symbol | Meaning |
|---|---|
| A | **Account equity**, measured in share prices — one unit is one share at today's spot, so an account of A = 11.59 could pay for eleven and a half lots outright. The unconstrained model is A = ∞. (Unrelated to the accounting tracks below, which are always written out as "Track A") |
| γ_s | Equity fraction the broker requires against **held shares**: 1.00 shares paid for in full, 0.50 under Reg T, 0.25 under portfolio margin, 0.15 the most aggressive available. A property of the account type, not a dial the operator turns |
| u, u\* | **Utilization**: margin posted as a fraction of equity. u\* is the operator's **stopping rule** — the utilization at which they stop selling new puts. u\* = 1 runs to the broker's own limit; a survival tolerance instead fixes u\* = γ_s·L_max |
| L | **Leverage**: gross exposure per unit of equity, L = u/γ_s ([eq:leverage](#eq:leverage)), so the broker's ceiling u\* = 1 is L = 1/γ_s. The leverage an account *realizes* is E[I]/A, which is generally far below what it is permitted. What carrying it costs is priced in [the returns section](#sec:returns) ([eq:levered-excess](#eq:levered-excess)) |
| f\* | **Liquidation barrier**: the fraction of today's price at which equity falls to γ_s of market value and the book is sold out ([eq:barrier](#eq:barrier)). f\* ≤ 0 is an unlevered book, which is never called; f\* ≥ 1 is a position in violation the day it is put on |
| ε | **Survival tolerance**: the eventual-liquidation probability the operator is willing to accept (running example: 10%). The dial that L_max and g_max are inversions of. It is a statement about **unbounded** time, so any liquidation probability quoted from it carries a horizon |
| L_max | Largest leverage whose eventual liquidation probability is at most ε ([eq:lmax](#eq:lmax)) — 1.13 at γ_s = 0.25 and ε = 10%, against a broker's ceiling of 4 |
| I_max | **Capacity**: the largest inventory the equity can carry, I_max = L_max·A ([eq:capacity](#eq:capacity)). A put whose assignment would breach it is not sold |
| A\* | **The equity a wheel needs**: A\* = E[I(∞)]/L_max ([eq:astar](#eq:astar)), the account size above which the constraint never binds. A function of the stock, not a number |
| λ_eff | Arrival rate actually achieved once blocking starts, λ_eff = I_max/E[W] ([eq:lambda-eff](#eq:lambda-eff)) — Little's law run backwards. The ratio λ_eff/λ = min(1, A/A\*) is the **throughput retention**: the fraction of the strategy the account is running |
| T_sat | **Saturation time**: the first time E[I(t)] reaches capacity. Emergent rather than assumed — it is what replaces the unconstrained model's arbitrary "90% of the asymptote" convention |
| D | **Debit balance**: cash borrowed from the broker, D = max(0, I − A) for an account at capacity |
| r_b | Rate charged on the debit, r_b = r + the **financing spread**. The spread is 0 in the article's base case, so that leverage is priced at no worse than fair; retail brokers charge 1–3% |
| draw | Cash withdrawn from the account per year, in share prices. Negative is a deposit |
| g | Growth rate of the debit under the operator's cash policy, g = r_b + (draw − income)/D ([eq:debit-growth](#eq:debit-growth)). The default g = 0 is a policy and not the absence of one: the operator services the interest and withdraws the rest. The third stability boundary is a race between it and ν: the account survives iff ν > g ([eq:account-criterion](#eq:account-criterion)) |
| θ_eff | The tail exponent θ with the cash policy in it, θ_eff = 2(ν − g)/σ² ([eq:theta-eff](#eq:theta-eff)). A cash policy enters survival in exactly one way, by displacing the drift, so every survival formula reads ν − g where it would read ν |
| g_max | Fastest a debit may grow while liquidation risk stays within ε ([eq:gmax](#eq:gmax)) |
| draw_max | **Maximum sustainable draw**: the cash per year that may be taken out at that same tolerance ([eq:draw](#eq:draw)). A constraint, not an optimum — it says what a chosen leverage costs in spendable cash, and it goes negative, becoming a demand for deposits, well below the leverage a broker permits |

Three conventions govern this block.

**The defaults are the unconstrained operator.** γ_s = 1, A = ∞, financing spread 0 and g = 0 describe someone who pays for shares in full, never runs out of money and never gets a margin call — which is exactly the operator every figure in Parts I and II reports. So the constrained model is a departure from the unconstrained one and recovers it exactly, and that equivalence is checked rather than asserted.

**Initial and maintenance requirements are deliberately not distinguished.** Brokers demand more equity to open a position than to keep one, and γ_s is one number covering both. The difference is a few percentage points; the question this part asks is whether the account survives at all, and that question is not sensitive to it.

**The put collateral is excluded from capacity, from the barrier and from the financing ledger alike** — one exclusion, applied uniformly. Capacity is a statement about shares. The margin standing behind the single open put is γ_p·k\* ≈ 0.196 share prices, which is **1.5%** of a saturated running example's capacity, and carrying it through three formulas costs more in clutter than naming it once here.

## Probability notation

| Symbol | Meaning |
|---|---|
| N(·) | Standard normal cumulative distribution function |
| N⁻¹(·) | Its inverse (quantile function) |
| φ(·) | Its density: the standard normal bell curve ([eq:phi](#eq:phi)) |
| d₁, d₂ | The two arguments of the Black–Scholes formula ([eq:bs-put](#eq:bs-put)), d₁ = d₂ + σ·√τ. N(−d₂) is the probability a put finishes in the money; the put's delta is e^(−δ·τ)·N(−d₁), and **not** N(−d₁), which is the no-dividend shorthand. See [the entry section](#sec:entry) |
| P(·), E[·] | Probability and expectation |

## The three accounting tracks

| Track | Question it answers |
|---|---|
| A | Realized cash flows only: premiums received, dividends collected, and cash exchanged when lots are bought and sold. Assignment is inventory acquisition, not a loss. This is what a brokerage statement shows |
| B | Capital committed, valued at market: broker margin on the live short put plus the **market value** of the shares held, before any borrowing against them. A put has bought nothing and ties up only collateral; shares have been bought and tie up what they are worth |
| C | Opportunity cost: the risk-free rate charged against the capital in Track B |

The headline number is the **true excess return** — [eq:excess](#eq:excess) in [the returns section](#sec:returns) — which values inventory at market, books the mark loss at acquisition and the upside surrendered at call-away, and charges r on Track B. It is the only convention that satisfies no-arbitrage, and that fact is used as a test in [the verification section](#sec:verification). The Track A cash view is reported next to it because it is what operators actually see, and because the gap between the two is instructive.

None of the three is displaced by the finite account. Track B remains **exposure** — what the position is worth at market — while the constraint of [the constrained section](#sec:constrained) runs on a different quantity, the **equity required** to hold that exposure, which is smaller by whatever the broker lends. Equity required is a second ledger line beside the three tracks, never a replacement for one; [the returns section](#sec:returns) makes the distinction where the quantity first appears, and tabulates it — γ_p·k + γ_s·E[I], the broker lending against held shares but not against the put collateral — as a row beside the two capitals rather than as a denominator.
