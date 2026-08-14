# Derivations {#sec:derivations}

The article states its formulas where they are needed and puts the algebra here, so that a reader following the argument is not made to follow the arithmetic at the same time. Nothing in this appendix is new: every result below is quoted in some section, and the entries are reached from there by link. Nothing here is required in order to use the model, and a reader willing to take the formulas on trust can skip the whole appendix without losing the thread.

Two conventions. Displayed steps inside a derivation carry no numbers of their own — only the article's own formulas are numbered, and a derivation refers to them by their number like any other part of the text. And every derivation ends where the section that needed it begins, at the formula as that section states it, so the two can be compared symbol for symbol.

## Two Gaussian integrals {#drv:partial-expectation}

Two of the derivations below — the mean entry depth and the mean fall from the price the put was sold at — are the same integral wearing different clothes, and so are the mark loss and the call-away giveaway that [the returns section](#sec:returns) books later. It is worth doing once.

Throughout, Z is a draw from the standard normal distribution of [eq:phi](#eq:phi), φ is its bell curve and N its running total, as [the entry section](#sec:entry) defines them. Both results below concern a **partial** expectation: an average taken not over every outcome but only over those below some cut-off a, with the rest of the outcomes contributing nothing. Written with an indicator — 1{Z < a}, a quantity that is 1 when the condition holds and 0 when it does not — an average over the whole line with that factor inside it *is* an average over the part below a.

**The exponential one.** For any constants c and a,

E[ e^(c·Z) · 1{Z < a} ]  =  e^(c²/2) · N(a − c)

The proof is one algebraic step, **completing the square**. Write the expectation as an integral against the bell curve and collect the two exponents:

E[ e^(c·Z) · 1{Z < a} ]  =  ∫_(−∞)^a e^(c·z) · φ(z) dz  =  ∫_(−∞)^a e^(c·z − z²/2) dz / √(2π)

The exponent c·z − z²/2 is a quadratic in z, and any quadratic can be written as a perfect square plus a constant:

c·z − z²/2  =  −(z − c)²/2  +  c²/2

The constant c²/2 carries no z, so it leaves the integral as a factor. What remains is the same bell curve shifted along by c — that is what −(z − c)²/2 is — so substituting u = z − c turns it back into an ordinary standard normal, with the cut-off carried along to a − c:

E[ e^(c·Z) · 1{Z < a} ]  =  e^(c²/2) · ∫_(−∞)^(a−c) φ(u) du  =  e^(c²/2) · N(a − c)

Read it in words: multiplying by e^(c·Z) before averaging tilts the weight toward large Z, and the identity says that tilt does exactly two things — it scales the answer by e^(c²/2) and it shifts the cut-off by c. Both effects come from the same completed square. Setting a = ∞ gives N(∞) = 1 and the familiar E[e^(c·Z)] = e^(c²/2), which is where the σ²/2 in [eq:lognormal](#eq:lognormal) comes from.

**The linear one.** For any a,

E[ Z · 1{Z < a} ]  =  −φ(a)

This one needs no integration at all, only the observation that the bell curve is its own derivative up to a factor of −z:

φ′(z)  =  −z · φ(z),   so that   z · φ(z)  =  −φ′(z)

The integrand is therefore already a derivative, and the integral is the thing it is the derivative of, evaluated at the ends:

E[ Z · 1{Z < a} ]  =  ∫_(−∞)^a z · φ(z) dz  =  [ −φ(z) ]_(−∞)^a  =  −φ(a)

the lower end contributing nothing because φ dies away to zero. The minus sign is worth a moment: averaging Z over only its lower tail must give something negative, and −φ(a) is negative for every a. It is largest in size at a = 0, where the whole lower half is included and the cut-off sits where the curve is tallest.

## Why the option formulas look unlike a textbook's {#drv:bs-convention}

[eq:bs-put](#eq:bs-put) and [eq:bs-call](#eq:bs-call) will not match the Black–Scholes formulas in [Hull](#ref:hull) or anywhere else on sight, and a reader who checks them against a textbook should know why before concluding one of them is wrong. Nothing has been approximated; the article is quoting prices in different units.

The textbook writes the price of a European put on a dividend-paying stock in **dollars**, as a function of the spot price S₀ and the strike K:

p  =  K·e^(−r·τ)·N(−d₂)  −  S₀·e^(−δ·τ)·N(−d₁),   d₁ = [ ln(S₀/K) + (r − δ + σ²/2)·τ ] / (σ·√τ)

This article quotes every price and strike as a **fraction of the share price**, as [the notation section](#sec:notation) sets out: k = K/S₀ is the strike as a fraction of spot, and a premium of 0.005 means half a percent of the share price. Converting is division by S₀, and it goes through cleanly because every dollar amount above is proportional to one of S₀ or K:

p/S₀  =  (K/S₀)·e^(−r·τ)·N(−d₂)  −  e^(−δ·τ)·N(−d₁)  =  k·e^(−r·τ)·N(−d₂)  −  e^(−δ·τ)·N(−d₁)

which is [eq:bs-put](#eq:bs-put). The arguments convert too, and this is the step that changes a formula's appearance most: ln(S₀/K) is the logarithm of the reciprocal of k, so it becomes −ln k, and

d₁  =  [ −ln k + (r − δ + σ²/2)·τ ] / (σ·√τ)

as the article writes it. The call is the same division applied to the same textbook formula.

**Why this is exact rather than a convenience.** The Black–Scholes price is **homogeneous of degree one** in spot and strike: double both the share price and the strike and every price doubles with them, because the whole problem has simply been restated in units half the size. A quantity with that property loses nothing when it is divided through by one of its two arguments — the remaining ratio carries all the information the pair did. So a strike is fully described by k and a premium by its fraction of spot, and S₀ never has to appear. This is the reason the model can be stated without ever naming a share price or an account size, and why every figure in the article is a percentage.

## The strike dial: strike out of probability, and back {#drv:kstar}

[The entry section](#sec:entry) turns one dial, a target assignment probability p\*, and reads a strike off it. That is [eq:kstar](#eq:kstar). Read the other way — strike in, probability out — the same algebra gives [eq:p-screen](#eq:p-screen).

**Setting up the event.** By [eq:lognormal](#eq:lognormal), the price after one put tenor is

S_τ  =  S₀ · exp( (m − σ²/2)·τ_p  +  σ·√τ_p·Z )

with Z a single standard normal draw. The put assigns when the stock finishes below its strike, S_τ < k·S₀. Divide through by S₀, take logarithms of both sides — legitimate in the same direction because the logarithm is increasing — and the event becomes a statement about Z alone:

(m − σ²/2)·τ_p  +  σ·√τ_p·Z  <  ln k

Z  <  [ ln k − (m − σ²/2)·τ_p ] / (σ·√τ_p)

Everything the model knows about assignment is in that one threshold. Give it a name: writing it as −d₂ makes it the same d₂ that appears in [eq:bs-put](#eq:bs-put), and the assignment probability is then the area below it,

P(assignment)  =  N(−d₂),   −d₂ = [ ln k − (m − σ²/2)·τ_p ] / (σ·√τ_p)

The threshold carries the drift m, so it is a different number in the article's two worlds — that is the whole of [the entry section](#sec:entry)'s "one measure, two worlds", written out. Reading it at the market's drift m = r − δ gives [eq:p-screen](#eq:p-screen) exactly.

**Inverting it.** The dial runs the other way: p\* is chosen and k must follow. Since N is increasing it has an inverse, so applying N⁻¹ to both sides of N(−d₂) = p\* strips the N away and leaves an ordinary equation in ln k:

[ ln k − (m − σ²/2)·τ_p ] / (σ·√τ_p)  =  N⁻¹(p\*)

Multiply up and move the drift across:

ln k  =  N⁻¹(p\*)·σ·√τ_p  +  (m − σ²/2)·τ_p

Exponentiating both sides gives [eq:kstar](#eq:kstar). The shape is worth reading off it: the strike sits N⁻¹(p\*) one-period moves away from where the drift alone would have carried the price. Since p\* is below a half, N⁻¹(p\*) is negative and the strike sits below — one-in-five is 0.84 of a move down, one-in-ten is 1.28.

**The gap between the two worlds.** Because only the drift differs between them, the threshold's dependence on m is a single subtraction, and the distance in threshold units follows by inspection: changing m by μ − r changes −d₂ by (μ − r)·τ_p/(σ·√τ_p), which is [eq:screen-gap](#eq:screen-gap). Converting that to a gap in *probability* is where [eq:gap-prob](#eq:gap-prob) comes from — since the real world's threshold is N⁻¹(p\*) by construction of the dial, the market's is N⁻¹(p\*) + Δd₂, and the difference of the two areas is the formula as stated.

The approximation quoted beside it is the first term of a Taylor expansion. For a small step h, N(x + h) ≈ N(x) + N′(x)·h, and N′ is φ, so

Δp  =  N(N⁻¹(p\*) + Δd₂) − p\*  ≈  φ(N⁻¹(p\*)) · Δd₂

This is why the probability gap depends on the strike while the threshold gap does not: the conversion factor is the height of the bell curve at the threshold, which is 0.28 at Standard and 0.18 at Conservative. At the running parameters it gives 0.0039 against the exact 0.0039 — the two agree to four decimals because Δd₂ is small enough that the curvature never gets a chance to matter.

## The entry-depth density {#drv:x0-law}

[eq:x0-law](#eq:x0-law) is the truncated-normal density of the depth a lot enters at. Two things happen to the ordinary bell curve on the way to it — a change of variable and a conditioning — and the compact result hides which factor came from which.

**The starting quantity.** Let R = ln(S_τ/S₀) be the put's own log return over its tenor. By [eq:lognormal](#eq:lognormal) it is normal, with mean (m − σ²/2)·τ_p and spread σ·√τ_p, so by [eq:phi](#eq:phi) its density is the standard bell curve standardized and rescaled:

f_R(ρ)  =  φ( (ρ − (m − σ²/2)·τ_p) / (σ·√τ_p) ) / (σ·√τ_p)

**The change of variable.** A lot's call strike is frozen at what it cost, K_c = k·S₀, so the depth of [eq:x0-def](#eq:x0-def) is

x₀  =  ln(K_c/S_τ)  =  ln(k·S₀/S_τ)  =  ln k − R

Depth is the log return reflected and shifted. When a density is carried through a change of variable it must be multiplied by the derivative of the old variable with respect to the new — the factor that keeps areas equal when the axis is stretched. Here the map is a reflection and a shift, with no stretch at all:

dρ/dx₀  =  −1,   so   |dρ/dx₀|  =  1

so no factor appears. **That absence is the point**: every 1/(σ·√τ_p) in the final formula came from standardizing R, and none of it from the change of variable. Substituting ρ = ln k − x₀ into f_R and taking the absolute value of the derivative gives the density of x₀ before any conditioning:

φ( (ln k − x₀ − (m − σ²/2)·τ_p) / (σ·√τ_p) ) / (σ·√τ_p)

**The conditioning.** This density is not yet the one the article wants, because the model only ever sees a depth when the put assigned. Assignment is R < ln k, which in the new variable is exactly x₀ > 0 — a lot that entered has, by definition, positive depth. So the truncation point is at zero, which is why [eq:x0-law](#eq:x0-law) is stated for x₀ > 0 and is silent below it.

Discarding everything below zero leaves an area of P(assignment) rather than one, and the detour in [the entry section](#sec:entry) is the repair: divide by that probability. By construction of the strike dial it is p\*, and that is the whole of the p\* in the denominator. Applying it gives [eq:x0-law](#eq:x0-law) as stated.

**A reading of the result.** Evaluate the density at the truncation point itself, x₀ = 0. The argument of φ becomes (ln k − (m − σ²/2)·τ_p)/(σ·√τ_p), which the derivation above identified as N⁻¹(p\*) exactly. So

f(0)  =  φ(N⁻¹(p\*)) / (σ·√τ_p · p\*)

The density is at its highest right at the strike and falls away from there: most assignments are shallow. That combination φ(N⁻¹(p\*))/p\* is the one that reappears in [eq:x0-mean](#eq:x0-mean), and this is where it comes from.

## The mean entry depth {#drv:x0-mean}

[eq:x0-mean](#eq:x0-mean) is the mean of the density just derived. It uses the second Gaussian integral of [the lemma above](#drv:partial-expectation), and the drift disappears from it along the way — which the article makes something of, so it is worth seeing exactly where it goes.

Write a = N⁻¹(p\*) throughout. The strike-dial derivation established that

(ln k − (m − σ²/2)·τ_p) / (σ·√τ_p)  =  a

which lets the argument of φ in [eq:x0-law](#eq:x0-law) be written as a − x₀/(σ·√τ_p). **The drift has already been absorbed into a at this step**, and it never reappears; this single substitution is the whole reason [eq:x0-mean](#eq:x0-mean) carries no m. The density becomes

f(x₀)  =  φ( a − x₀/(σ·√τ_p) ) / (σ·√τ_p · p\*),   x₀ > 0

**Measuring depth in one-period moves.** Substitute t = x₀/(σ·√τ_p), so x₀ = σ·√τ_p·t and dx₀ = σ·√τ_p·dt, with t running from 0 to ∞. One factor of σ·√τ_p comes down from x₀ and one from dx₀, and one cancels against the density's own:

E[x₀]  =  ∫_0^∞ x₀·f(x₀) dx₀  =  (σ·√τ_p / p\*) · ∫_0^∞ t·φ(a − t) dt

Everything left is a pure number set by the dial, times one period's move out front — which is the article's reading of the result.

**The remaining integral.** Substitute w = a − t, so t = a − w and dt = −dw; as t runs from 0 up to ∞, w runs from a down to −∞, and the reversed direction cancels the minus sign. Splitting the integrand in two:

∫_0^∞ t·φ(a − t) dt  =  ∫_(−∞)^a (a − w)·φ(w) dw  =  a·∫_(−∞)^a φ(w) dw  −  ∫_(−∞)^a w·φ(w) dw

The first integral is N(a) = p\*, by the definition of a. The second is the linear integral of [the lemma](#drv:partial-expectation), equal to −φ(a), and it enters with a minus sign in front, so it arrives as +φ(a):

∫_0^∞ t·φ(a − t) dt  =  a·p\*  +  φ(a)

**Putting it back.** Multiplying by the σ·√τ_p/p\* set aside earlier, the p\* cancels against the first term and divides the second:

E[x₀]  =  σ·√τ_p · ( a  +  φ(a)/p\* )

which is [eq:x0-mean](#eq:x0-mean). The two terms are worth separating: a = N⁻¹(p\*) is negative and is where the strike sits, while φ(a)/p\* is positive, larger, and is the overshoot beyond it. Their sum is positive because a lot that assigned has finished below the strike by definition — the second term is the mean of the truncated tail, known in statistics as the **inverse Mills ratio**, and the fact that it exceeds the first in size is the whole content of "assignment lands below the strike, not at it".

## The mean fall from S₀ {#drv:d-mean}

[eq:d-mean](#eq:d-mean) is the average fall from the price the put was sold at, given that the put assigned. It follows from the exponential integral of [the lemma above](#drv:partial-expectation) in three lines, and the article's remark that one takes the expectation of e^(−x₀) is this derivation compressed.

The fall is d = 1 − S_τ/S₀, so its conditional mean is one minus the conditional mean of the price ratio, and that ratio is [eq:lognormal](#eq:lognormal) divided through by S₀. Keeping a = N⁻¹(p\*) as above, the strike-dial derivation showed that assignment is exactly the event Z < a. So

E[ S_τ/S₀ | assignment ]  =  E[ e^( (m − σ²/2)·τ_p + σ·√τ_p·Z ) · 1{Z < a} ] / p\*

the division by p\* being the same renormalization as before: a conditional average is the partial average divided by the probability of the condition. The drift term carries no Z, so it comes out as a factor, and what is left is precisely the lemma's exponential integral with c = σ·√τ_p:

E[ e^(σ·√τ_p·Z) · 1{Z < a} ]  =  e^(σ²·τ_p/2) · N(a − σ·√τ_p)

Multiplying the two exponentials together is where the σ²/2 cancels — the −σ²/2 in the drift of [eq:lognormal](#eq:lognormal) against the +σ²/2 the lemma's tilt produces:

e^( (m − σ²/2)·τ_p ) · e^( σ²·τ_p/2 )  =  e^( m·τ_p )

**That cancellation is the reason [eq:d-mean](#eq:d-mean) carries m and not m − σ²/2**, and it is the same cancellation that makes a lognormal's mean grow at m while its median grows at m − σ²/2. Collecting:

E[ S_τ/S₀ | assignment ]  =  e^(m·τ_p) · N(a − σ·√τ_p) / p\*

**Back into the article's notation.** The strike-dial derivation named the threshold −d₂, so a = −d₂ and p\* = N(−d₂). The shifted cut-off is then a − σ·√τ_p = −(d₂ + σ·√τ_p) = −d₁, which is the article's d₁ = d₂ + σ·√τ_p. Substituting both:

E[ S_τ/S₀ | assignment ]  =  e^(m·τ_p) · N(−d₁) / N(−d₂)

and subtracting from one gives [eq:d-mean](#eq:d-mean). The d₁ that appears in it is the same d₁ as in the option formulas, and for the same reason: the lemma's shift by c is what turns a probability into a stock-weighted one, which is exactly the difference between d₂ and d₁ that [the entry section](#sec:entry)'s detour describes.
