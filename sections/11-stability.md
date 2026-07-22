# Stability: When Does the System Stay Bounded? {#sec:stability}

## The homogeneous case is always stable — which should worry you

Under the homogeneous approximation with constant q, the system cannot run away: whenever q > 0, the equilibrium I\* = p·n/q of [eq:istar](#eq:istar) is finite, and inventory mean-reverts toward it. Departures scale with inventory (q_p per lot), so the fuller the warehouse, the faster it drains. On paper, the wheel cannot be buried.

A result this comforting, derived from an approximation this strong, should be treated as a description of the approximation rather than of the world. The interesting — and dangerous — behavior appears exactly where the approximation breaks.

## Heterogeneity: dead strata

Recall the caveat from [the recovery section](#sec:recovery): q is not actually uniform across inventory. A lot's call strike is frozen at the price level where it was assigned. In a falling market, old lots carry strikes far above the current price; their individual recovery probabilities q_i are much smaller than the q of a freshly assigned lot. The homogeneous model averages this away. Reality does not.

The failure mode: if q_i declines fast enough with the layer's depth — the gap between its strike and the current price — the *effective* average exit rate across the standing inventory can fall below the arrival rate p. Then old layers stop unwinding on any relevant horizon while new lots keep arriving on top. Capital becomes trapped in **dead strata**: lots that are technically still in the conveyor but whose exit dates have receded toward infinity. Track A still shows premium income; Track B quietly ratchets up; the self-recycling property — which held layer-by-layer in the homogeneous model — fails in aggregate.

Whether this happens is not a matter of temperament but of a computable condition: how fast q_i decays with depth, against the rate p at which new layers arrive. Deriving that condition requires specifying q_i as a function of layer depth — precisely tier 2's task.

## Reflexivity: the parameters move against you together

The second danger is that p and q are treated as constants but are functions of market conditions — and in stress they move *simultaneously and in the harmful direction*:

- Falling markets raise implied volatility, which (at a fixed strike) raises the assignment probability p: more puts land in the money.
- The same falling market deepens d and depresses the recovery odds q.

Both movements push I\* = p·n/q the same way, and their effect compounds multiplicatively: a market that doubles p and halves q *quadruples* equilibrium inventory. The system's response to stress is therefore convex — mild stress looks comfortably absorbed, severe stress deteriorates much faster than a linear extrapolation from mild stress suggests. An operator calibrated on calm markets will systematically underestimate how quickly the warehouse fills in a storm.

Note also what reflexivity does to the operator's chosen strike policy: if strikes are set by target probability p\* (the inversion formula [eq:kstar](#eq:kstar) of [the assignment section](#sec:assignment)), rising volatility pushes the strike k\* lower rather than letting p rise — trading assignment frequency for deeper out-of-the-money entries. The model as stated holds k fixed; the strike-policy feedback belongs to the parameter studies of tier 2.

## Summary of tier 1's verdict

Within its assumptions, the wheel is a stable, self-recycling inventory system with computable equilibrium inventory, income, and capital. The assumptions that carry the load, in order of fragility:

1. **Uniform q across layers** — fails in sustained declines; produces dead strata (tier 2's subject).
2. **Constant p and q over time** — fails reflexively in stress, with multiplicative effect on I\*.
3. **Geometric price decline** in the capital bound — fails in crash-then-flatline markets, which stall the convergence.
4. **Independent lot exits** — fails on a single name (common price path); repaired by diversification across names or demoted to a means-only claim.
