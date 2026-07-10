# The Inventory Queue

## The warehouse analogy

Imagine running a storage warehouse. Each week a delivery truck arrives with a new pallet with probability p, or doesn't (probability 1−p). Each pallet already in the warehouse has, that same week, a chance q_p of being picked up and removed. When deliveries outpace pickups, inventory grows; when pickups outpace deliveries, the warehouse empties. If the rates are stable, occupancy settles around an equilibrium level, fluctuating but mean-reverting.

That is the wheel: deliveries are put assignments, pallets are stock lots, pickups are call-aways. The one bookkeeping wrinkle is that arrivals and departures run on different clocks — puts on the τ_p clock, calls on the τ_c clock — so we first convert everything to put periods.

## Converting the exit rate to the put-period clock

The recovery probability q is per *call* period. A lot surviving one call period has survived n put periods, so the per-put-period exit probability q_p satisfies (1−q_p)ⁿ = 1−q:

q_p = 1 − (1−q)^(1/n) ≈ q/n    (accurate when q is not large)

For n ≥ 2 or modest q the approximation q/n is comfortably accurate. (A pedantic footnote: real exits can only happen at call expirations, every n-th put period, so treating q_p as available every period smooths the timing. Means are unaffected; only the fine-grained dynamics are slightly idealized.)

## Detour: the Poisson distribution

> A **Poisson distribution** describes the count of independent random events occurring at a stable average rate — phone calls arriving at a switchboard per hour, typos per page, or here, inventory lots held at equilibrium. It has a single parameter, its mean, and one distinctive fingerprint: its **variance equals its mean**. If the average count is 4, typical fluctuation around it is about ±2 (the square root of 4). Poisson distributions arise universally as the steady state of systems where arrivals come at a constant rate and each item present departs independently — in queueing theory this is the M/M/∞ ("infinite-server") queue. See Ross, *Introduction to Probability Models*, for both the distribution and the queue.

## The steady state

Our inventory is a birth–death process: arrivals at constant rate p, departures at rate q_p per lot held, so total departure rate q_p·i when i lots are held. Departures accelerate as inventory grows — more pallets, more pickups — which is what pulls the system toward equilibrium. The equilibrium level is where the rates balance:

p = q_p · I\*    ⟹    I\* = p / q_p ≈ p·n / q = p · (τ_c/τ_p) / q

and the full steady-state distribution is well approximated by a Poisson with that mean:

P(I = i) = e^(−I\*) · (I\*)^i / i!

The approximation is exact in the continuous-time limit and very accurate whenever q_p is small (ensured by n not too small or q moderate). For n = 1 with large q it degrades somewhat — but the equilibrium *mean* I\* = p/q_p is exact regardless, since it needs only the rate balance, not the distributional shape.

Consequences worth staring at:

- **Average inventory: E[I] = I\*.** For the running stress example (p ≈ 0.176, n = 3, q ≈ 0.162): I\* ≈ 3.3 lots. With the more typical d ≈ 0.08 (so q ≈ 0.42): I\* ≈ 1.25 lots.
- **The strategy is usually holding stock.** The probability of an empty warehouse is P(I=0) = e^(−I\*): about 37% for I\* = 1, 14% for I\* = 2, 5% for I\* = 3. The comfortable picture of "mostly selling puts, occasionally stuck with shares" is wrong at equilibrium — inventory is the normal condition, not the exception.
- **The clock ratio is a direct multiplier.** Doubling τ_c at fixed p and q doubles I\*. Longer calls buy more premium per contract and higher per-call recovery odds, but pay for it linearly in average capital lockup. This is the quantitative form of the trade-off from the strategy section.

## The self-recycling property

In steady state, the average number of new assignments per put period is p. The average number of call-aways per put period is E[I] · q_p = (p/q_p) · q_p = p. **The two rates are identical** — not approximately, exactly, by the definition of equilibrium.

In plain terms: in the long run the system returns inventory at precisely the rate it acquires it. New lots arrive, old lots depart, and the warehouse hums at its equilibrium occupancy. Moreover — as the returns section makes precise — each departing lot exits at the same strike at which it entered, so the round trip through inventory costs nothing at the price level and earns call premiums the whole way through. The wheel, at equilibrium, is a conveyor: stock in, stock out, premiums accumulating on both legs.

## An honest caveat: the independence assumption

> **[Flagged for revision — see TODO #1]** The warehouse analogy has each pallet picked up *independently*. On a single underlying this is substantially false: all lots ride the same price path, and when the stock recovers through a strike level, every lot struck at or below it is called away *at once*. The equilibrium mean I\* survives (it needs only rate balance), but the fluctuations are burstier than Poisson — long accumulations punctuated by mass exits — so quantities like P(I=0) and the ±√I\* typical swing are idealized. The clean interpretations available: (a) read the Poisson claims as applying across a diversified portfolio of wheels on many names, where paths are roughly independent; or (b) read them as a single-name idealization whose means are trustworthy and whose tails are not. The article must commit to one framing.
