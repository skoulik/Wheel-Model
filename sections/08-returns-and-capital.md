# Expected Returns and Capital Commitment {#sec:returns}

Throughout this section we work in the homogeneous approximation — price levels roughly stable, all lots alike — and we are strict about accounting tracks. All quantities are per unit of underlying price (per S₀).

## The lifecycle of a lot, in cash

The cleanest way to get the income run rate is to follow one put through its life and count only cash (Track A):

- **Sell the put:** collect c_p.
- **If it expires worthless** (probability 1−p): done. Total: c_p.
- **If assigned** (probability p): pay k for the stock. Sell covered calls at strike k, collecting c_c per call period — and, because the asset pays a dividend, collect δ_net·τ_c of dividend per call period held. Here **δ_net = δ·(1−w)** is the yield the operator actually keeps: dividends arrive net of a withholding tax w (15% is the common treaty rate for foreign holders of US stock, and our running value), so δ = 2.5% gross becomes δ_net ≈ 2.1%. The number of call periods until recovery is geometric with success probability q, so 1/q periods and (c_c + δ_net·τ_c)/q of premium-plus-carry in expectation. At call-away, deliver the stock at k — the same strike paid at entry. The purchase and the sale cancel *exactly*. Total: c_p + (c_c + δ_net·τ_c)/q in expectation.

Notice what the cancellation means: passage through inventory costs nothing at the price level (in this stable-price approximation) and earns call premium and dividends the whole way through. The put premium is earned exactly **once** per put sold, assigned or not.

## The steady-state run rate (Track A)

In equilibrium, one put is sold per period and lots complete their lifecycle at rate p per period (the self-recycling property). The expected realized income per put period is therefore

**E[Π] / S = c_p + p · (c_c + δ_net·τ_c) / q**    {#eq:run-rate}

The second term can be read two equivalent ways, and the equivalence is a useful consistency check: *by lifecycle*, completions at rate p each carrying (c_c + δ_net·τ_c)/q of accumulated call premium and dividend carry; or *by standing inventory*, I\* = pn/q lots each yielding c_c/n of premium plus δ_net·τ_p of dividends per put period, and the products agree. Annualizing: divide by τ_p.

> **A pitfall worth naming.** There is a tempting alternative derivation that goes wrong. Under the popular "net cost basis" convention, an assigned lot is booked at basis k − c_p (strike paid minus premium received), so the exit at strike k shows a *capital gain of exactly c_p* — the put premium recovered again at the exit door. The recycling image is correct and appealing. But under that convention the premium was folded into the basis rather than booked as income at entry — counting c_p at entry *and* the c_p gain at exit counts the same cash twice. Similarly, the "assignment drag" — paying k for stock currently worth 1−d — is a real mark-to-market loss but not a Track A entry: Track A defines assignment as acquisition. Booking the drag without also booking the offsetting recovery gain at call-away (from 1−d back up to k, which cancels it exactly for every lot that completes) understates income by mixing half of Track B's ledger into Track A. Either convention, applied consistently, lands on the same formula above.

## The mark-to-market view (Track B's ledger)

Track A's serenity has a cost, and honesty requires displaying it. At any moment the standing inventory carries **unrealized losses**: each lot was bought at k against a market at 1−d, roughly (k − 1 + d) per lot at acquisition, healing as the stock climbs toward the strike. In steady state this pool of paper losses is a *level*, not a flow — of rough size I\* · (k−1+d) at its worst — and it never touches the realized run rate as long as lots eventually complete. But it is exactly what a mark-to-market observer (a broker, a nervous spouse) sees during the holding period, and it is what becomes real if the operator is ever forced to liquidate mid-cycle. [The stability section](#sec:stability) is about when "lots eventually complete" fails.

## Capital committed (Track B)

The capital tied up in steady state is margin on the live short put plus the cost basis of the standing inventory:

E[Capital] / S₀ ≈ m·k + I\* · (k − c_p)    {#eq:capital}

with m the broker's margin fraction on the put.

## A worked example, end to end

Running parameters: k = 0.95, monthly puts (τ_p = 1/12), quarterly calls (n = 3), σ = 20%, r = 5%, μ = 7% total return, δ = 2.5% gross with w = 15% withholding (δ_net ≈ 2.1%), m = 0.20. Black–Scholes prices the monthly put at c_p ≈ 0.0054.

**Base case (d ≈ 0.08, the conditional expectation [eq:d-mean](#eq:d-mean) derived in [the recovery section](#sec:recovery)):** q ≈ 0.40, I\* ≈ 1.40 lots, and the call — struck only ~3% above the market — is worth c_c ≈ 0.026. Run rate: 0.0054 + 0.185·(0.026 + 0.0053)/0.40 ≈ 0.0200 per month ≈ **24.0% of S₀ per year** (Track A, of which ≈ 3.0% is dividend carry) on capital ≈ **1.51·S₀** (Track B), for a true excess return of roughly **+10.9% per year**.

**Stress case (d = 0.15, the ~2.5σ assignment):** q ≈ 0.147, so I\* ≈ 3.8 lots. The quarterly call on the depressed stock is worth only c_c ≈ 0.007. Run rate: 0.0054 + 0.185·(0.007 + 0.0053)/0.147 ≈ 0.0206 per month ≈ **24.7% of S₀ per year** (Track A — now *more* than the base case, because a warehouse of 3.8 lots throws off δ_net each on top of its meager call premiums). Capital: 0.20·0.95 + 3.78·0.945 ≈ **3.76·S₀** (Track B). Charging r on that capital (Track C ≈ 0.188·S₀/yr) leaves a true excess return of roughly **+1.6% per year**: the wheel works furiously to barely beat T-bills, and the thin margin it keeps is mostly dividend carry on depressed stock. Note what the homogeneous accounting just did, though — it credited full dividend carry on every lot at no extra cost, as if a large inventory were merely a larger dividend portfolio. Whether that flatters the strategy is exactly the kind of question this approximation cannot answer.

> **[Flagged for revision — see TODO #18]** The layered simulation (`code/wheel_sim.py`, `drafts/2026-07-22-layered-simulation-findings.md`) shows the base case above is far too kind: the run rate [eq:run-rate](#eq:run-rate) survives layering, but average capital comes out ≈ 7.7·S₀, not 1.51·S₀, because standing inventory is dominated by deep lots whose calls are nearly worthless — collapsing the base-case excess return from +10.9%/yr to below zero. The correction is the first-passage treatment (TODO #19); until then, read the base-case excess return as an upper bound of the homogeneous approximation.

The pair of numbers is the honest summary of the strategy: its economics live and die on how deep assignments land and how fast lots recycle. The base case says the machine works; the stress case says a regime of persistently deep assignments grinds the edge from +10.9% down to +1.6% — and even that remainder is mostly dividend carry credited on terms this approximation is too generous about. This is exactly why d had to be derived rather than assumed, and why modeling depth-dependent recovery is not a refinement but the heart of the matter. (One further Track C caveat, flagged as TODO #6: cash collateral securing short puts typically itself earns near the risk-free rate at the broker, so Track C as computed here overcharges the put-margin component; the correction improves the excess return.)

## Capital convergence under geometric decline

How bad can Track B get in a sustained fall? Suppose the price falls geometrically — every assignment occurs at S_j = S₀·(1−d)^j, each drop a constant fraction d. Then cost bases shrink geometrically too, B_j = (k − c_p)·S_j, and even summing infinitely many lots the total converges:

Σ_j B_j = (k − c_p) · S₀ / d    {#eq:capital-bound}

> **Detour: geometric series.** A sum a + a·x + a·x² + … with |x| < 1 converges to a/(1−x): each term is a fixed fraction of the last, so the tail shrinks fast enough to add up to something finite. Here each successive lot's basis is (1−d) times the previous one's.

For k = 0.95, c_p ≈ 0.0054, d = 0.15 (the stress value is the appropriate one here — the bound is about sustained decline) the total cost basis is bounded by about **6.3·S₀**, no matter how many lots accumulate; with margin fraction m = 0.20, margin consumed by put-selling stays bounded as well. This is reassuring — but the reassurance leans entirely on the *geometric* structure: equal percentage drops each assignment, so that later lots are ever cheaper. Real markets often drop sharply and then **flatline**. A flatline stalls the geometric compression: assignments keep arriving near the same price level, cost bases stop shrinking, and capital accumulates without the convergence mechanism. This — not the smooth decline — is the primary practical failure mode, and it belongs to tier 2's agenda.
