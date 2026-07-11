# Expected Returns and Capital Commitment {#sec:returns}

Throughout this section we work in the homogeneous approximation — price levels roughly stable, all lots alike — and we are strict about accounting tracks. All quantities are per unit of underlying price (per S₀).

## The lifecycle of a lot, in cash

The cleanest way to get the income run rate is to follow one put through its life and count only cash (Track A):

- **Sell the put:** collect c_p.
- **If it expires worthless** (probability 1−p): done. Total: c_p.
- **If assigned** (probability p): pay k for the stock. Sell covered calls at strike k, collecting c_c per call period; the number of call periods until recovery is geometric with success probability q, so 1/q periods and c_c/q of call premium in expectation. At call-away, deliver the stock at k — the same strike paid at entry. The purchase and the sale cancel *exactly*. Total: c_p + c_c/q in expectation.

Notice what the cancellation means: passage through inventory costs nothing at the price level (in this stable-price approximation) and earns call premium the whole way through. The put premium is earned exactly **once** per put sold, assigned or not.

## The steady-state run rate (Track A)

In equilibrium, one put is sold per period and lots complete their lifecycle at rate p per period (the self-recycling property). The expected realized income per put period is therefore

**E[Π] / S = c_p + p · c_c / q**

The second term can be read two equivalent ways, and the equivalence is a useful consistency check: *by lifecycle*, completions at rate p each carrying c_c/q of accumulated call premium; or *by standing inventory*, I\* = pn/q lots each yielding c_c/n per put period, and (pn/q)·(c_c/n) = p·c_c/q. Annualizing: divide by τ_p.

> **A pitfall worth naming.** There is a tempting alternative derivation that goes wrong. Under the popular "net cost basis" convention, an assigned lot is booked at basis k − c_p (strike paid minus premium received), so the exit at strike k shows a *capital gain of exactly c_p* — the put premium recovered again at the exit door. The recycling image is correct and appealing. But under that convention the premium was folded into the basis rather than booked as income at entry — counting c_p at entry *and* the c_p gain at exit counts the same cash twice. Similarly, the "assignment drag" — paying k for stock currently worth 1−d — is a real mark-to-market loss but not a Track A entry: Track A defines assignment as acquisition. Booking the drag without also booking the offsetting recovery gain at call-away (from 1−d back up to k, which cancels it exactly for every lot that completes) understates income by mixing half of Track B's ledger into Track A. Either convention, applied consistently, lands on the same formula above.

> **[Flagged for revision — see TODO #2]** For the dividend-paying assets this strategy targets, dividends collected while holding inventory are a genuine Track A income stream — at I\* lots and a 2–3% yield, a material one — currently absent from the run rate, as dividends are absent from the model generally.

## The mark-to-market view (Track B's ledger)

Track A's serenity has a cost, and honesty requires displaying it. At any moment the standing inventory carries **unrealized losses**: each lot was bought at k against a market at 1−d, roughly (k − 1 + d) per lot at acquisition, healing as the stock climbs toward the strike. In steady state this pool of paper losses is a *level*, not a flow — of rough size I\* · (k−1+d) at its worst — and it never touches the realized run rate as long as lots eventually complete. But it is exactly what a mark-to-market observer (a broker, a nervous spouse) sees during the holding period, and it is what becomes real if the operator is ever forced to liquidate mid-cycle. [The stability section](#sec:stability) is about when "lots eventually complete" fails.

## Capital committed (Track B)

The capital tied up in steady state is margin on the live short put plus the cost basis of the standing inventory:

E[Capital] / S₀ ≈ m·k + I\* · (k − c_p)

with m the broker's margin fraction on the put.

## A worked example, end to end

Running parameters: k = 0.95, monthly puts (τ_p = 1/12), quarterly calls (n = 3), σ = 20%, r = 5%, μ = 7%, m = 0.20. Black–Scholes prices the monthly put at c_p ≈ 0.005.

**Base case (d ≈ 0.08, the conditional expectation derived in [the recovery section](#sec:recovery)):** q ≈ 0.42, I\* ≈ 1.25 lots, and the call — struck only ~3% above the market — is worth c_c ≈ 0.029. Run rate: 0.005 + 0.176·0.029/0.42 ≈ 0.0170 per month ≈ **20.4% of S₀ per year** (Track A) on capital ≈ **1.37·S₀** (Track B), for a true excess return of roughly **+9.9% per year**.

**Stress case (d = 0.15, the ~2.5σ assignment):** q ≈ 0.162, so I\* ≈ 3.3 lots. The quarterly call on the depressed stock is worth only c_c ≈ 0.008. Run rate: 0.005 + 0.176·0.008/0.162 ≈ 0.0133 per month ≈ **16.0% of S₀ per year** (Track A). Capital: 0.20·0.95 + 3.26·0.945 ≈ **3.27·S₀** (Track B). Charging r on that capital (Track C ≈ 0.163·S₀/yr) leaves a true excess return of roughly **−0.1% per year**. Read that again: with assignments always landing 15% deep, the wheel works furiously to approximately match T-bills.

The pair of numbers is the honest summary of the strategy: its economics live and die on how deep assignments land and how fast lots recycle. The base case says the machine works; the stress case says a regime of persistently deep assignments erases the edge entirely — which is exactly why d had to be derived rather than assumed, and why modeling depth-dependent q (tier 2) is not a refinement but the heart of the matter. (One further Track C caveat, flagged as TODO #6: cash collateral securing short puts typically itself earns near the risk-free rate at the broker, so Track C as computed here overcharges the put-margin component; the correction improves the excess return.)

## Capital convergence under geometric decline

How bad can Track B get in a sustained fall? Suppose the price falls geometrically — every assignment occurs at S_j = S₀·(1−d)^j, each drop a constant fraction d. Then cost bases shrink geometrically too, B_j = (k − c_p)·S_j, and even summing infinitely many lots the total converges:

Σ_j B_j = (k − c_p) · S₀ / d

> **Detour: geometric series.** A sum a + a·x + a·x² + … with |x| < 1 converges to a/(1−x): each term is a fixed fraction of the last, so the tail shrinks fast enough to add up to something finite. Here each successive lot's basis is (1−d) times the previous one's.

For k = 0.95, c_p = 0.005, d = 0.15 (the stress value is the appropriate one here — the bound is about sustained decline) the total cost basis is bounded by about **6.3·S₀**, no matter how many lots accumulate; with margin fraction m = 0.20, margin consumed by put-selling stays bounded as well. This is reassuring — but the reassurance leans entirely on the *geometric* structure: equal percentage drops each assignment, so that later lots are ever cheaper. Real markets often drop sharply and then **flatline**. A flatline stalls the geometric compression: assignments keep arriving near the same price level, cost bases stop shrinking, and capital accumulates without the convergence mechanism. This — not the smooth decline — is the primary practical failure mode, and it belongs to tier 2's agenda.
