# Reader's flow report — Parts I–II

I read as the article's stated target reader: comfortable with algebra, normal
distributions, logs and exponentials, one long-ago probability course, no queueing
theory, no measure-theoretic finance, only a lay grasp of puts and calls. I read
`00`→`02`→`04`→`05`→`06`→`07`→`08`→`09`→`10`→`11` once, forward, at reading speed,
skimming `00` like a glossary and never reading ahead. I looked nothing up. Everything
below is my reaction on first contact, not an audit.

## Overall reading experience

The article is genuinely well-written sentence by sentence, and several of its hardest
ideas land cleanly (the σ²/2 drag, the mean-vs-median holding time, "economically
identical to owning the stock", the margin-call detour). But the difficulty curve is not
a curve — it is a wall in the middle. Sections **06 and 10** are the easiest and best.
Section **07** is where I first stopped understanding and started nodding, and it never
fully let me back in. Section **09** is where I drifted from exhaustion rather than
difficulty: it is enormous, sweep after sweep, and each individual part is clear while
the whole is punishing. Section **11** is long but recovers the clarity of 06/10.

Two structural things hurt the reading before any individual sentence did:

1. **The Introduction's "Contributions" list spoils every result before I can hold any
   of them.** Eight dense numbered items throw "1.6%", "two years", "ninety years",
   "the volatility risk premium", "the equity risk premium", "nineteen share prices",
   "a factor of twenty-five" at me before I have met the model. I could not absorb them
   and stopped trying around item 4.

2. **A cloud of similar capital numbers — 11.59, 18.23, 19.04, 19.23, 21.82 — never
   fully separates in my head.** Which one is "what the strategy consumes", which is
   "the equity the wheel needs", which is "equilibrium lots"? I confused them
   repeatedly from §08 onward.

The five passages I would rewrite first, by ID:

- **R-07-1** — the β / expected-overshoot / Wald derivation (§07). My single biggest
  comprehension failure.
- **R-02-1** — the Contributions spoiler-dump (§02).
- **R-09-1** — the sheer length of §09; it needs to be broken up or thinned.
- **R-08-2** — the "window law" two-rows / time-in-window passage (§08).
- **R-04-2** — the "Exposure is not the same as equity required" digression (§04),
  which argues a fine point about a denominator before I know what the return even is.

## Section verdicts

| section | did I follow it | where it got hard |
|---|---|---|
| 00 notation | skim only | fine as a glossary; too much forward-referenced detail to absorb |
| 02 introduction | mostly | the Contributions list buried me; two undefined "premiums" |
| 04 strategy | yes | the equity-required digression arrived too early; "√tenor" asserted |
| 05 entry | mostly | risk-neutral drift nodded-along; the "where the operator sits" digression |
| 06 depth | yes, well | the clearest section in the article |
| 07 holding time | **partly lost** | β, expected overshoot, Wald run backwards — nodded without understanding |
| 08 inventory | with rereads | three flavours of Little's law; the window-law rows |
| 09 returns | drifted | not hard so much as endless; the BXM beta detour lost me |
| 10 stability | yes, well | strong and well-ordered |
| 11 constrained | yes | long, but clear |

## Findings, in reading order

### §02 — Introduction

**R-02-1 — The Contributions list dumps every conclusion before I can hold one**
- **Severity:** lost me
- **Kind:** wrong order
- **Where:** the eight-item "Contributions" list, "1. **Entry** … about 1.6% below the
  strike" through "8. **A comparison against fifteen months of a real wheel account**".
- **What happened when I read it:** I expected a roadmap and got the destination. Each
  item is a compressed result with its punchline attached — "a true median of eight",
  "some ninety years to approach", "nineteen share prices", "a factor of twenty-five".
  I have no model yet, so none of these mean anything; they are just numbers asserting
  importance. By item 4 I was skimming, and I arrived at §04 having retained none of it
  except a vague sense that the answer is "the wheel is like owning the stock".
- **What would have fixed it:** cut each item to the *question* it answers and defer the
  number ("How long does a lot stay? Not what the obvious calculation says — and the gap
  turns out to be a first-passage effect."). Let the sections deliver the numbers.

**R-02-2 — "volatility risk premium" and "equity risk premium" used as if known**
- **Severity:** slowed me
- **Kind:** unexplained term
- **Where:** item 4, "the entire edge of the strategy is the volatility risk premium";
  item 5, "is exactly the equity risk premium".
- **What happened when I read it:** these are offered as the payoff of two of the eight
  contributions, but I do not yet know what either premium is. I nodded at "the edge is
  the volatility risk premium" as though it were an answer, when it was a term I could
  not define. (It is defined later, in §05 and properly in §09 — but here it is load-
  bearing and undefined.)
- **What would have fixed it:** one half-sentence gloss at first use, or phrase the
  contribution without leaning on the named premium.

**R-02-3 — the margin/capacity item is unreadable this early**
- **Severity:** had to reread
- **Kind:** overloaded sentence
- **Where:** item 6, "needs about **nineteen share prices** of the operator's own money
  … against the 5.5 a portfolio-margin ceiling implies, and 5.8 times what the most
  aggressive margin available implies."
- **What happened when I read it:** three different capital figures (19, 5.5, 5.8×) in
  one breath, none of which I can anchor because I do not know what a "share price" of
  capital means yet or what portfolio margin is. I reread it twice and gave up.
- **What would have fixed it:** this is the item that most needs to become a question
  rather than a spreadsheet row.

### §04 — The Strategy and Its Accounting

**R-04-1 — "premium scales with the square root of the tenor" asserted, never justified**
- **Severity:** slowed me
- **Kind:** hidden assumption
- **Where:** "premium scales roughly with the square root of the tenor while assignments
  scale with the cadence."
- **What happened when I read it:** I stopped, because this is clearly doing real work
  (it is the reason separating the two clocks "changes the economics"), and I have no
  idea *why* premium goes as √tenor. It reads as something the author knows and I am
  expected to nod at. I nodded.
- **What would have fixed it:** a five-word pointer — "premium grows with volatility ×
  √time, the same √ that governs how far a price wanders" — would have connected it to
  the σ·√τ language the rest of the article uses.

**R-04-2 — the "equity required" digression argues a denominator I don't have yet**
- **Severity:** had to reread
- **Kind:** wrong order
- **Where:** the subsection "**Exposure is not the same as equity required.**" and the
  paragraph after it, "The temptation to divide by it instead is worth naming…"
- **What happened when I read it:** this is a careful, two-paragraph argument about why
  you should *not* divide the return by equity-required, complete with "close to four
  times the excess return". But I have not yet been shown any return, any excess return,
  or any division. I am being warned off a mistake in a calculation I have never seen.
  I reread it, decided I would have to take it on faith, and moved on slightly rattled.
- **What would have fixed it:** compress it to a one-line flag here ("a fourth quantity,
  equity required, will appear in §11; it is never a return denominator, for reasons
  given there") and let §09/§11 carry the actual argument where the return exists.

**R-04-3 — the tenor separation is argued twice and half-retracted**
- **Severity:** mild friction
- **Kind:** lost thread
- **Where:** "Real operation separates them, though usually by less than it first
  appears — a put sold Monday … live five of the week's seven days …" then "The
  separation still changes the economics…"
- **What happened when I read it:** I was told the separation matters, then told it
  barely matters (Monday–Friday is "very nearly the truth"), then told it changes the
  economics anyway. I finished the paragraph unsure whether I should care about τ_p ≠ T
  or not. The honest answer ("not in Parts II–III; see the live section") is buried at
  the end.
- **What would have fixed it:** lead with the verdict — "in every example here T = τ_p;
  the gap only matters in the live account" — then give the reassurance.

### §05 — Entry

**R-05-1 — the risk-neutral drift is asserted, and I nodded**
- **Severity:** had to reread
- **Kind:** unanswered "why"
- **Where:** "The **risk-neutral** drift is what option *prices* behave as if the stock
  will do: the risk-free rate r … It is an artifact of how options are priced."
- **What happened when I read it:** this is the concept the whole "one measure, two
  worlds" apparatus rests on, and the text tells me option prices "behave as if" the
  drift were r without saying *why* they do. I could paraphrase the words — "for pricing,
  pretend the stock only earns r" — but I could not have explained to a friend why that
  is legitimate rather than a mistake. I nodded and kept going, which is exactly the
  failure the reader is meant to catch.
- **What would have fixed it:** one sentence of intuition — that an option can be
  replicated by continuously trading the stock and cash, so its price cannot depend on
  the stock's real growth rate, only on r and σ. Even a gesture at replication would let
  me stop taking it on pure authority.

**R-05-2 — "Sharpe ratio" used without definition**
- **Severity:** slowed me
- **Kind:** unexplained term
- **Where:** "the argument of N(·) shifts by the asset's Sharpe ratio times the square
  root of the tenor."
- **What happened when I read it:** I have a hazy memory that Sharpe ratio is
  return-over-risk, but the article has been scrupulous about defining everything else
  in a detour, so its bare appearance here made me distrust my memory and reread.
- **What would have fixed it:** "(μ − r)/σ, the asset's Sharpe ratio" inline.

**R-05-3 — "the two differ by a factor of four here" — which two?**
- **Severity:** had to reread
- **Kind:** lost thread
- **Where:** "That is a shift in d₂, not in probability, and the distinction is worth
  keeping because the two differ by a factor of four here."
- **What happened when I read it:** I stopped to work out which two quantities differ by
  four. The shift in d₂ (0.0139) versus the probability shift (0.4 pp = 0.004)? I think
  so, but I had to reconstruct it from the numbers two sentences apart. The pronoun "the
  two" pointed at nothing nearby.
- **What would have fixed it:** name them — "the d₂ shift (0.0139) and the probability
  shift (0.004) differ by a factor of four."

**R-05-4 — "Where a real operator sits on the dial" is a long forward-referenced detour**
- **Severity:** slowed me
- **Kind:** wrong order
- **Where:** the whole subsection, "Over fifteen months, 956 of its put contracts …"
  through "… Conservative is where a real book sits."
- **What happened when I read it:** having just learned the strike formula, I was pulled
  into a multi-step reconciliation of a live account I have not been introduced to —
  7.4%, corrected to 10.8%, cross-checked via 5.5%→5.1% at 30% vol. Each step is fine in
  isolation; together they are a detour into evidence for a choice (Standard vs
  Conservative) that I did not yet know was contested. I recovered at "So the two regimes
  bracket practice", but I had drifted for three paragraphs.
- **What would have fixed it:** this may simply belong later, or compressed to its
  conclusion ("measured on the live account, real practice is the Conservative regime;
  see §live") with the reconciliation deferred.

**R-05-5 — the exercise-style caveat is where I first started skimming**
- **Severity:** slowed me
- **Kind:** lost thread
- **Where:** "## A caveat on exercise style" through the Merton–Scholes–Gladstein put
  discussion.
- **What happened when I read it:** this is thorough and clearly conscientious, but it is
  a long two-leg caveat (American vs European, call leg then put leg, a table of
  early-exercise thresholds, a borrowed simulation result about tail vs mean) placed
  right after the section's real payoff. I started skimming at the days-to-expiry table
  and skimmed to the end of the section. I recovered at §06.
- **What would have fixed it:** it reads like an appendix. If it must stay inline, a
  one-line summary at the top ("early exercise is negligible on the call leg and does not
  help the put leg; details follow") would let a reader skip with confidence rather than
  drift.

### §06 — The Depth Process

*(This section I followed completely and enjoyed. Findings are minor; the praise is in
the final section.)*

**R-06-1 — "ζ(1/2)" will land later, but the constant's provenance is invisible here**
- **Severity:** mild friction
- **Kind:** unexplained term
- **Where:** (actually first appears in §07, but I flag it against my expectation set in
  §06's clean treatment of ν) — noting only that §06 sets a standard of "every term
  explained" that §07 then breaks.
- **What happened when I read it:** n/a here; see R-07-2.

### §07 — How Long a Lot Stays

**R-07-1 — the β / expected-overshoot / Wald-run-backwards derivation lost me**
- **Severity:** lost me
- **Kind:** logical jump
- **Where:** "## Exits happen on a grid, and the grid is expensive", specifically from
  "What β measures is an **expected overshoot**" through "the overshoot the model is
  really paying is **0.667** steps, not 0.583."
- **What happened when I read it:** I followed that discrete sampling makes the barrier
  effectively deeper, and I accepted β·σ·√τ_c as a correction. Then it came apart. "β is
  the overshoot for a barrier infinitely far away" and "a fresh lot sits 0.28 of a step
  below its barrier" — so β is the *wrong* value here. Then Wald's identity appears
  (E[W] = hole / rate), and the text says "Run that backwards from the exact 2.10 years
  computed below" to *recover* the true overshoot 0.667. That is: it uses a holding-time
  answer that has not been computed yet (it is "below") to back out the overshoot that
  the same section then uses to explain the holding time. On first read this felt
  circular, and I could not tell whether 0.667 was derived, measured, or assumed. I
  nodded at "roughly 30% is the entry and 70% is the grid" — a striking claim — without
  being able to reconstruct where 70% came from.
- **What would have fixed it:** separate the *concept* (sampling deepens the barrier;
  here is the textbook constant β) from the *correction to the concept* (β is a
  far-barrier limit, ours is a near barrier, so the real overshoot is larger). And do
  not derive the overshoot from a number that appears "below" — either compute E[W]
  first and present this as a diagnostic, or state 0.667 as the measured overshoot and
  drop the run-it-backwards framing. The 30/70 split is worth its own clean sentence.

**R-07-2 — β = −ζ(1/2)/√(2π): the Riemann zeta is dropped without a word**
- **Severity:** had to reread
- **Kind:** unexplained term
- **Where:** "β = −ζ(1/2)/√(2π) ≈ 0.5826".
- **What happened when I read it:** ζ(1/2) is alien notation to me, and it arrives with
  no gloss — the article that carefully explained N(·) and truncated distributions
  suddenly assumes the Riemann zeta function. I could take 0.5826 on faith, but the
  symbol made me feel I had missed a prerequisite.
- **What would have fixed it:** either "(ζ is the Riemann zeta function; the value is
  just a fixed constant ≈ 0.5826)" or lead with the number and put the closed form in
  the footnote where the history already lives.

**R-07-3 — the history paragraph is a detour I did not need mid-derivation**
- **Severity:** slowed me
- **Kind:** wrong order
- **Where:** "Nobody knew that when the number was first computed … Chernoff (1965) …
  Gordon Latta … Siegmund … Chang & Peres … Broadie, Glasserman & Kou … a slip in his
  arithmetic and not a second constant."
- **What happened when I read it:** I was still trying to understand what β *does*, and
  the text pivoted into a paragraph of attribution history — four names, a −0.5824
  vs −0.5826 arithmetic-slip aside. It is charming, but it landed exactly when I needed
  to keep hold of the mechanism, and I lost the thread of the argument across it.
- **What would have fixed it:** move the provenance to a footnote. The mechanism and its
  history are competing for the same attention, and the mechanism is losing.

**R-07-4 — "the exact 2.10 years computed below" is a forward reference to its own result**
- **Severity:** had to reread
- **Kind:** broken promise (forward ref used before delivered)
- **Where:** "Run that backwards from the exact 2.10 years computed below".
- **What happened when I read it:** the section computes the tax using a number the same
  section will not produce for another two subsections. I flipped my attention forward
  looking for it, found the survival table and eq:holding only later, and had to hold an
  IOU in the meantime. Coupled with R-07-1 this made the grid argument feel like it
  assumed its own conclusion.
- **What would have fixed it:** present the exact E[W] first (survival curve → 2.10),
  *then* diagnose the overshoot from it. Order the section effect-then-cause instead of
  cause-then-effect-then-cause.

### §08 — The Inventory

**R-08-1 — three flavours of Little's law, and I lost track of which was in force**
- **Severity:** slowed me
- **Kind:** shifting ground
- **Where:** the 1961 detour with its "One qualification" (stationary vs sample-path vs
  2011 finite-window), then "## The equilibrium…" invoking "Little's own finite-window
  form", then the "H = λG" weighted-law detour.
- **What happened when I read it:** the core result (E[I] = 21.8) is crisp. But around it
  the section keeps refining *which* Little's law it means — the 1961 stationary one, the
  assumption-free sample-path one, the 2011 window one, and finally the H = λG weighted
  one. By the third variant I had stopped tracking the distinctions and was taking "it's
  some version of Little's law" on faith. The qualifications may all be necessary, but
  cumulatively they eroded my confidence rather than building it.
- **What would have fixed it:** a single sentence up front — "we use Little's law three
  times: to count lots, to read it over a finite window, and to weight lots by capital;
  each needs slightly different hypotheses, flagged as they arise" — so the refinements
  feel like a plan rather than a series of corrections.

**R-08-2 — the window law: two rows and "time a lot spends in-window" needed rereading**
- **Severity:** had to reread
- **Kind:** overloaded sentence
- **Where:** "## The equilibrium the unconstrained operator will never see", the two-row
  table (holdings at H vs average over [0,H]) and "**Over a thirty-year window a lot
  spends 1.10 years inside it, against a full life of 2.10.**"
- **What happened when I read it:** the distinction between "what you hold at H" and
  "the average across [0,H]" is genuinely important — the second is what the rest of Part
  II uses — but I had to read the passage twice to see that they are different questions,
  not two estimates of one thing. Then "time a lot spends in-window" divides the average
  inventory by λ to get 1.10 years, which is a third quantity, and I needed a third pass
  to see it was a *consistency* reading rather than a new result. Individually clear;
  together they overloaded me.
- **What would have fixed it:** slow it down and label the three quantities explicitly
  as (a) holdings at the horizon, (b) capital committed on average, (c) a cross-check.
  One sentence naming why (b) is the one that matters would carry the whole passage.

**R-08-3 — a block of §11's numbers is airlifted in early**
- **Severity:** slowed me
- **Kind:** wrong order
- **Where:** "[The constrained section] computes it: **0.9 years** for an account of
  three share prices, 2.4 for five, **18.5** for the 11.59 … 270 for 19.04 — and never
  for an account of 19.23 or more."
- **What happened when I read it:** five account sizes and five saturation times, all
  forward-referenced to a section I have not reached, appear mid-argument about the
  90-year approach. It is a preview of §11's central table, and it is too much detail to
  absorb as a preview — I could not hold "18.5 for 11.59" against "270 for 19.04" without
  the context that §11 later supplies.
- **What would have fixed it:** keep the qualitative point (a finite account reaches
  equilibrium far sooner, and the smaller the account the sooner) and drop the specific
  five-number list to §11.

**R-08-4 — "capital of 11.59" arrives before I know what it is**
- **Severity:** mild friction
- **Kind:** unexplained term
- **Where:** "the 11.59 that the rest of Part II reports this strategy as consuming".
- **What happened when I read it:** 11.59 is quoted as a known quantity ("this
  strategy's capital") but §09, which derives it, has not been read yet. It is one more
  member of the 11.59 / 18.23 / 19.23 / 21.82 family that I cannot yet tell apart. See
  the overall-experience note; this is the first place the confusion bit.

### §09 — Returns and Capital

**R-09-1 — the section is exhausting by sheer accumulation**
- **Severity:** lost me
- **Kind:** lost thread
- **Where:** the whole section, but the drift began at "## What the single σ_IV leaves
  out" and worsened through the cadence sweep, "## Dividends, resolved", "## What if the
  dividend never falls", and "## The Conservative regime".
- **What happened when I read it:** the central result — at fair prices the wheel equals
  owning the stock, and every vol point is worth ~45 bp — is delivered well and early and
  I understood it. Then the section keeps going: benchmark, collateral footnote, split
  betas, BXM caution, leverage, single-name premium, three surface omissions, cadence
  sweep, dividend sweep, sticky-dividend fixed point, Conservative regime. Each is a
  self-contained mini-paper with its own table. By the dividend sweeps I was reading
  words without building understanding — I could see "four basis points at thirty years"
  but had stopped asking why. This is the longest section by far and it reads like three
  sections wearing one heading.
- **What would have fixed it:** split it. The mean result (income, capital, benchmark) is
  one section; the risk decomposition (betas, reversal) is another; the sensitivity
  sweeps (cadence, dividend, sticky dividend, Conservative) are a third. Each would then
  have room to breathe and a reader could rest between them.

**R-09-2 — the BXM split-beta detour lost me completely**
- **Severity:** lost me
- **Kind:** lost thread
- **Where:** "> **A caution about comparing this with published numbers.**" — the
  0.46-vs-0.83, up-beta-0.00, "three conventions span nearly half a unit of beta"
  passage.
- **What happened when I read it:** this is a defensive digression about why *not* to
  compare the article's 0.83 with a published 0.46, and it is dense with measurement
  conventions (calendar months vs mid-month expiry, strike-above-spot, overlapping
  21-day returns) that mean nothing to me. I understood the conclusion ("not comparable")
  before the paragraph started and then could not follow the evidence for it. I skimmed
  to the end of the blockquote.
- **What would have fixed it:** the conclusion is enough for my level; the convention
  arithmetic belongs in a footnote for the specialist who would actually make the
  comparison.

**R-09-3 — "the volatility risk premium" is properly explained only here, long after use**
- **Severity:** slowed me
- **Kind:** unexplained term (explained too late)
- **Where:** "## So where could an edge come from?" and "This **volatility risk
  premium**" — with the index-vs-single-name split (3 points vs ~1 point).
- **What happened when I read it:** this is the first place I felt I *understood* the
  volatility risk premium — implied exceeds realized, systematically, and that gap is the
  only possible edge. But the term has been doing headline work since §02 (contribution
  4) and appeared again in §05. By the time it is explained I had already nodded at it
  three times. The explanation is good; it is just three sections downstream of where I
  first needed it.
- **What would have fixed it:** a one-line definition at the first genuine use in §05
  (which nearly does this already) with an explicit "priced in full in §returns" pointer,
  so this section reads as the promised payoff rather than a first introduction.

**R-09-4 — undefined finance terms in the dividend subsections**
- **Severity:** mild friction
- **Kind:** unexplained term
- **Where:** "the **Gordon-model price** at which a fixed payout stops being payable";
  "the shape a reader may recognize as the **VIX term structure in contango**".
- **What happened when I read it:** both are dropped as if familiar. I do not know the
  Gordon model, and while I have heard "VIX", "term structure in contango" is a phrase I
  can only half-parse. Each made me feel the intended reader was more specialist than me.
- **What would have fixed it:** a three-word gloss apiece, or drop the name and keep the
  plain description ("short-dated options are normally quoted cheaper than longer-dated
  ones").

**R-09-5 — the collateral footnote is a full argument masquerading as a footnote**
- **Severity:** slowed me
- **Kind:** wrong order
- **Where:** "> **A footnote on the collateral, which Track C overcharges.**" — 17/13/8
  bps, the 4.5× posting-full-cash case, "arithmetic, not a measurement".
- **What happened when I read it:** it is called a footnote but it is a dense paragraph
  that then *recurs* as the whole explanation of the Conservative regime's 8-bp deficit
  much later. I did not retain it, so when "the collateral footnote above" was invoked in
  the Conservative subsection I had to hunt back for it. A genuine footnote would not be
  load-bearing twice.
- **What would have fixed it:** if it is going to explain a later result, promote it to a
  short named subsection so the later callback lands.

### §10 — Stability

*(Strong section, well-ordered; I followed all of it. Findings are minor.)*

**R-10-1 — "the exponential martingale of one drifting walk" assumes a term I don't have**
- **Severity:** mild friction
- **Kind:** unexplained term
- **Where:** (the phrase recurs in §11 eq:survive's "read twice" passage) "the same
  number because they are the same object, the exponential martingale of one drifting
  walk."
- **What happened when I read it:** "martingale" is not a word this article has taught
  me, and it is used at the moment of a satisfying unification (θ is one object read
  twice). I got the intuition from the surrounding prose, so the term was decorative
  rather than necessary — but it briefly made me feel I was missing the real reason.
- **What would have fixed it:** either a one-line detour on martingale or, since the
  prose already carries the point, drop the term.

**R-10-2 — "reflection principle" invoked without explanation**
- **Severity:** mild friction
- **Kind:** unexplained term
- **Where:** §11, "the reflection principle gives P(sold out by H) = …" (flagging here
  as it is the same class as R-10-1).
- **What happened when I read it:** the formula is given, so I could use it, but "the
  reflection principle" is named as though I would recognise it, and I do not. It is
  cited to Ross, so a reader could look it up — but the article's own standard is a
  detour, and this got none.
- **What would have fixed it:** a one-sentence detour, or "(a classical trick for
  counting barrier-crossing paths; see [Ross])".

### §11 — The Finite Account

*(Long but clear; the margin detour is one of the best explanations in the article.)*

**R-11-1 — the capital-figure family finally collides here**
- **Severity:** had to reread
- **Kind:** shifting ground
- **Where:** A\* = 19.23, capacity 21.82, A = 11.59, 19.04, and the T_sat table
  spanning A = 1.00 … 19.23.
- **What happened when I read it:** by this section I am juggling A\* (19.23, "the equity
  a wheel needs"), E[I(∞)] (21.82, equilibrium lots), the 30-year capital (11.59, "what
  the strategy consumes"), and 19.04 (a T_sat row). These are all "about nineteen to
  twenty-two share prices" and I kept having to stop and ask which was which. The section
  is careful, but the numbers are close enough that carefulness in the prose does not
  rescue them in my memory.
- **What would have fixed it:** a tiny recurring gloss on each figure's *role* at each
  use ("A\* = 19.23, the equity above which the account never blocks"), or a one-line
  "three numbers to keep apart" box, would stop me confusing the thing the strategy
  *consumes* with the thing it *needs*.

**R-11-2 — Glynn–Whitt and the "run the law backwards" caveat is heavy for its payoff**
- **Severity:** slowed me
- **Kind:** logical jump
- **Where:** "running the law *backwards* … [Glynn and Whitt] proved what it costs: from
  the time averages alone one gets an inequality rather than an equation, and equality
  needs an extra condition, the simplest being that the system empties infinitely often."
- **What happened when I read it:** the conclusion (the inversion is legitimate because a
  single-name book empties ~14% of the time) is clear. The route to it — an inequality
  that becomes an equality under an emptying condition — is a real mathematical subtlety
  that I could not evaluate and had to accept. It is honest, but it briefly raised a
  doubt ("is the whole λ_eff inversion shaky?") that the surrounding confidence did not
  quite settle.
- **What would have fixed it:** lead with the reassurance ("the inversion is valid here,
  and here is the one condition it needs") rather than with the cost.

## Where the prose is genuinely good

These did their job on first read and should be preserved and imitated:

- **§02 payoff-diagram detour.** The ASCII diagrams plus "two names for one trade" made
  put–call parity intuitive to me without a single formula. This is exactly the right
  level for the target reader.
- **§06, the whole section.** The clearest writing in the article. The three-term
  unpacking of ν = μ − δ − σ²/2 is a model of exposition, and the σ²/2 explanation —
  "gain 20% then lose 20% and you are down 4%" — is the best single sentence in Parts
  I–II. The paired q(x) and c_c(x) tables landing on "**Depth simultaneously destroys a
  lot's chance of leaving and its ability to earn while it waits**" is a genuinely
  satisfying click.
- **§07, the framing of the failure.** "The survivors are not a random sample of the
  original lots; they are the unlucky ones, selected for exactly the property that keeps
  them from leaving." I understood length-selection immediately from this, even though
  the β mechanics later lost me.
- **§07/§08, mean vs median.** "two years against eight weeks, a factor of thirteen" and
  the hospital-beds length-bias detour made a counterintuitive result feel inevitable.
- **§08, the disposition-effect detour.** "The wheel is the disposition effect written
  into a contract, with the discretion removed and the frequency raised to certainty."
  Memorable and clarifying, and honest about not pushing the analogy too far.
- **§09, the central verdict.** "**At fair option prices the wheel is economically
  identical to owning the stock**" with the cancellation table (appreciation ≈ mark loss
  + upside surrendered) is the payoff the whole article promised, and it lands. The
  "cash-on-cost-basis" explanation of why an operator's own records will mislead them
  (flattering early, damning late, nothing changed) is excellent.
- **§10, the risk-neutral reading.** "It is a leveraged bet that stocks go up, wearing
  the costume of an income machine" is the sharpest sentence in the back half, and the
  two-boundaries structure (lots come back / capital comes back) is beautifully clear.
- **§11, the margin-call detour.** The concrete walk-through — buy 10 with 5 of your own
  at γ_s = 0.25, price falls a third, equity meets requirement, book is sold — taught me
  what a forced liquidation is better than any definition would have. "The margin call is
  the moment capacity falls to meet the book" is a genuinely illuminating reframing.
