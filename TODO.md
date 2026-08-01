# TODO

Open work only. Everything finished, resolved or deliberately descoped lives in
[`DONE.md`](DONE.md), which also carries the map from the old flat numbering (#1–#25) to the
per-part numbering used here. Items are tagged `(was #n)` where a predecessor existed, so the
citations in `drafts/` stay traceable.

**Nothing resolved is kept in this file.** When an item closes its write-up goes to `DONE.md`, and
any figure a still-open item needs is folded into that item rather than left behind as a
hand-forward block. So every entry below is work someone still has to do. Numbers are never
recycled or closed up: the gaps — I-3, I-5, II-1 through II-17, IV-6, IV-7, INF-1 — mean those
items are in `DONE.md`. (IV-6 and IV-7 were added to this list on 2026-08-01, when IV-8 was
numbered around them; they closed on 2026-07-28 and had been missing from it since.)

Sections reference items as "TODO I-1", "TODO IV-2" — at present **no section body carries such a
flag** (checked 2026-08-01), and that is the intended steady state: an in-text flag is a promise
to a reader and should be added only when the text genuinely defers something. Three live in
`sections/98-bibliography.md`, in the internal field after an entry's anchor, which is stripped at
assembly and so never reaches a reader; they mark the two unread downloads and the one source
that may be cited for its existence only.

## Where things stand

Thirteen of the seventeen planned section files exist, plus two appendices: the bibliography
(`sections/98-bibliography.md`, hand-maintained, the only file that may declare a `{#ref:}`
anchor) and the generated reproduction table (`sections/99-reproduction.md`, produced by
`python -m examples --appendix`, never edited by hand). Part I is written bar two stubs; **Part II is written, with eleven items outstanding**
(II-18 through II-28 — nine from the literature pass of 2026-07-31, which reopened Part II the
day it closed, and two more from the Merton–Scholes–Gladstein read of 2026-08-01 that closed I-5;
none of them changes a formula or a verdict); **Part III and Part IV are unwritten**, and between
them they are still the bulk of what is left besides those stubs and the assembly work.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · 11 constrained | written; **eleven open items** (II-18 – II-28) — six in §09, the rest in §05, §07, §08 and §10, and II-23 also touches §00, §02 and §11 |
| III. Many assets | 12 portfolio · 13 correlation | **do not exist** |
| IV. Reality | 14 verification · 15 live-account · 16 outlook | **14 and 15 do not exist**; the outlook is a stub, on disk as `15-outlook.md` |

**This file uses the final numbering** — portfolio §12, correlation §13, verification §14, the
live account §15, the outlook §16 — as of 2026-07-30. It previously used the pre-§11 numbering
with a note saying so, which collided with the constrained section that actually occupies §11 on
disk: "write §11, the portfolio section" was an instruction to overwrite a finished section. The
*file* renames are still deferred to when Part III drafts — `15-outlook.md` becomes
`16-outlook.md` then — and nothing breaks in the meantime because anchors are name-based.

Six section files link to anchors in the missing files: `sec:verification` from 00, 07, 08 and 09;
`sec:live` from 00, 04 and 05; `sec:portfolio` from 08. Those cross-references are broken until
Parts III and IV land, and that is the assembly-time deadline. `sec:correlation` is so far
referenced from nowhere.

The two missing Part IV sections are **writing tasks, not modelling ones**: everything they report
is already measured, in `drafts/2026-07-27-discrepancy-catalogue.md` and the five scripts behind
it (`prices.py`, `live_ledger.py`, `model_vs_live.py`, `iv_panel.py`, `selection_fit.py`).

---

## Part I — Setup

**I-1. Prior work is a stub — the reading is done, the section is not.** The literature pass this
item asked for happened on 2026-07-31 and is written up in
[`drafts/2026-07-31-prior-work-literature-pass.md`](drafts/2026-07-31-prior-work-literature-pass.md):
six strands, a twenty-row cross-check of our findings against theirs, eleven harvest items and a
reading list. Nothing in `sections/` was changed by it. Downloaded PDFs are in `literature/`,
which is gitignored — reference copies, not ours to redistribute.

**Read levels bind.** Every source in that list carries **[F]** (full text read), **[P]**
(partial) or **[A]** (abstract or secondary description only). *Do not quote a number from an
`[A]` source without opening the paper.* Merton–Scholes–Gladstein was the live case and **the
prohibition is lifted**: both papers were read in full on 2026-08-01 and the secondary summaries
were wrong, in the direction that helps — [`DONE.md`](DONE.md) records what they actually
concluded. They are the reason the rule exists, and the rule stands for everything else.

**What §03 owes them, stated carefully.** These are the earliest large-scale simulations of
these strategies and a reader may raise them, so §03 should cite them — but **not** as "option
writing underperforms". 1978 has fully covered call writing below the underlying in all eight
strike-by-universe comparisons; 1982 has *uncovered put writing above covered call writing in
all six*, and above the DJ stock portfolio outright at E/S = 1.1 (5.1% against 4.6% semiannual,
at less than half the standard deviation). What both papers actually support is contribution 4:
at model prices these strategies trade expected return for risk, and whether they beat the
underlying ex post depends on the underlying's realised run — which is what MSG say each time,
in almost those words. Two further things §03 can use. Their **insurance framing** (1982 §VI:
the uncovered put writer "is supplying the service of providing insurance … he expects to be
compensated for this service, and the form of the compensation is an expected return in excess
of the return on riskless fixed-income securities") is the clearest general-audience statement
of why a volatility risk premium should exist at all, and it is by Merton and Scholes. And 1982
**restates the 1978 call results over the full 14 years** unchanged — Table 5's covered-call
columns against 1978's Table 7 — so the 1978 conclusion is not an artefact of its window. The
premium-sensitivity half of both papers is **II-27** and belongs in §09, not here.

**A second prohibition, and it is likelier to bite than the first** (added 2026-08-01). **Kuang &
Lin (2025)**, arXiv:2512.01123 **[P]**, is the *only* recent academic item on the wheel by name,
so whoever writes §03 will find it and will want to use it — the section needs something to say
about prior work on its own subject. It reports **15.3% annualised, Sharpe 1.08 against 0.62, a
−8.2% maximum drawdown, and a 0% assignment rate** maintained "through strategic option rolling"
over 18.75 years. **Do not cite any of those numbers as evidence.** A short-put programme that
never takes assignment across 2008 and 2020 has not avoided the loss, it has rolled it forward; a
−8.2% maximum drawdown on a short-put book spanning those years is not credible on its face; and
the backtest is in-sample with respect to the dataset its LLM selects from. §03 may cite it **as
existence** — that two arXiv papers name the wheel and neither builds a structural model, which is
N1's evidence — and for nothing else. Svozil (2026), arXiv:2604.13334 **[P]**, is the other; it is
qualitative, contributes no machinery, and is consistent with our regime caveat.

**One unread download belongs to this item** (planned 2026-08-01).
`literature/israelov-et-al-covering-the-world-global-covered-calls.pdf` is downloaded and **not
read**. It is global evidence on covered calls, and its natural home is §03's subsection 2 — "what
the record says" — which is otherwise entirely US index data (BXM, PUT/WPUT, CMBO). Read it before
writing that subsection, **or** state there that the record cited is US-only and why. Either is
acceptable; silently generalising from US indices to "what systematic option writing returns" is
not.

**The reading list now has a live counterpart, and §03 writes into it rather than beside it**
(added 2026-08-01). `sections/98-bibliography.md` holds all thirty-eight entries — the pass's
thirty-two plus the six textbook and foundational sources the sections were already leaning on
informally — each with a `{#ref:...}` anchor, its read level and its local filename. The draft's
§8 is now the *historical* list and the bibliography is the live one; keep read levels current in
the bibliography, not there. Prose cites by anchor and never by number (see §00's citation
convention), and `python -m examples --references` prints how many entries are still uncited —
**thirty-two of them, essentially all of §03's**. That count is the readiness measure for this
item: an entry §03 never cites should be deleted from the bibliography rather than shipped.

What remains is writing `sections/03-prior-work.md`, for which §6 of the draft proposes a
six-subsection skeleton. Two things it must carry:

- **The novelty claim is now verified, and it survives narrowed in three places.** No published
  index or academic study tracks the wheel — CBOE's CMBO is the nearest and is *not* it, holding
  a short put and a short call simultaneously and permanently where the wheel alternates and the
  share count is the state variable. But **the ingredients are all standard and §03 should say
  so**: the barrier shift is Broadie–Glasserman–Kou, the tail exponent is the Lundberg
  adjustment coefficient, the first-passage machinery is Siegmund's, grid-monitored knockouts are
  the autocallable literature's daily business. And **"Little's law applied to a portfolio of
  positions" cannot be claimed at all** — Little's own 50th-anniversary paper offers "the dollar
  rate of return on the ith asset in a portfolio of assets" as the canonical illustration of the
  generalised law. What is ours is the *assembly*: the depth process that supplies W, and the
  census that supplies the weighting function.
- **Its subsection 4 is the citation half of II-18**, the index/single-name volatility-premium gap.

The pass's findings finished converting on 2026-08-01, so nothing further is expected to land
here from that document. **This item cannot close until §03 is written.** The citation-graph pass
that would strengthen the novelty claim is **I-6** and deliberately does *not* block this item.

**I-2. The abstract is written last.** `sections/01-abstract.md` is a stub by design; it cannot
be honest until Parts III and IV fix what the article concludes.

**I-4. §02 promises things Parts III and IV must actually deliver.** The contributions list
commits the article to five results that do not yet exist anywhere:

- diversification leaves expected return and expected capital **completely unchanged** while
  removing only the noise around them (contribution 7 → III-1);
- correlations rising toward one in a crisis is **the mechanism the strategy is most exposed
  to**, not a tail scenario (contribution 7 → III-2);
- the live comparison confirms the model **link by link** — entry law to within a percent, the
  depth census to within five (contribution 8 → IV-1);
- the account's advantage came entirely from the excluded lever while the option machinery
  earned nothing distinguishable from zero (contribution 8 → IV-2);
- the article shows **which of the model's predictions a career-length track record has no
  power to test** (contribution 8 → IV-1). *Nothing currently delivers this one* — see IV-1.

Either the sections deliver these or §02 is rewritten. Check the list against the finished
Parts III and IV before assembly. **This is now a check, not a rewrite**: II-16 made the other
editing pass over §02 on 2026-07-31, which added the finite account as contribution 6 and pushed
portfolios to 7 and the live comparison to 8 — hence the numbering above. Items 1 through 6 are
delivered and were re-read for stale figures in that pass; only 7 and 8 are still promises.

**I-6. A citation-graph pass on the novelty claim, before release.** (From §4's own caveat and
the second-pass list of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md);
converted 2026-08-01. **Deliberately not folded into I-1** — see below.)

The novelty claim rests on **negative results from web search**, which is weak evidence, and the
pass says so about itself. It searched for the wheel by name, for covered-call and put-write
holding-time models, for queueing and inventory-theoretic treatments of option positions, for
infinite-server applications in finance, and for averaging-down and accumulation models, across
arXiv, SSRN and the major publishers. That is reasonable coverage of what is *findable* by
keyword; it is not a systematic review, and keyword search is exactly the method that misses a
paper which builds our object under someone else's vocabulary.

**The stronger test is a citation-graph pass** — forward citations outward from the three
anchors, Whaley (2002), Israelov & Nielsen (2014) and Broadie–Glasserman–Kou (1997), on the
reasoning that a prior structural model of the wheel would almost certainly cite at least one of
them and might well match none of our search terms.

**Why it is separate from I-1.** I-1 closes when §03 is written, which is an assembly-time
deadline; this is a **release** gate, and the pass recommends it "before publication, not before
assembly". Folding it in would hold a section that is otherwise ready to close behind a search
that can happen at any time before release. §03 can be written on the evidence in hand provided
it is phrased as N2 requires — the ingredients are standard, the assembly is not — which is a
claim a later pass can only strengthen.

**If it finds something**, the repair is confined to §03's subsection 6. No result in the article
depends on being first, and that is worth saying inside §03 rather than only here.

**I-7. Ten bibliography entries carry details nobody has checked against a copy.** (From building
`sections/98-bibliography.md`, 2026-08-01.)

Every entry the pass supplied came with its bibliographic details; the ones added to cover what
the sections were already citing informally did not, and were reconstructed rather than read off
a copy. Those ten are tagged **[cite unverified]** in the entry line, and
`python -m examples --references` lists them every run: black-scholes-1973, chang-peres-1997,
hull, israelov-covering-the-world, li-zhang, little-1961, merton-1973, ross-first-course,
ross-probability-models, siegmund-1985.

**This is a smaller worry than the read-level rule and a different one.** Nothing in the article
quotes a figure from any of them — they are pointers for further reading, plus the two 1973
pricing papers, which the article cites for the existence of a formula it derives itself. What is
unverified is the *citation*: Hull's edition and year, the Ross titles' publishers, page ranges,
and in four cases (chang-peres-1997, israelov-covering-the-world, li-zhang, and the Li–Zhang
initials) a title or author list filled in from memory. A reader following a wrong page range
loses nothing but time; a reader following a wrong *title* is being misled, so the four matter
more than the six.

**Deadline is assembly**, not §03: a bibliography goes out with the article, and this is the last
thing that should be discovered in proof. Clearing an entry means deleting its `[cite unverified]`
tag, which drops the count the checker prints.

## Part II — One asset

Part II closed on 2026-07-31 and was reopened the same day by the literature pass. Nine items are
open, they divide cleanly in two, and **none of them changes a formula or a verdict**.

**Five land in §09**, and IV-5 edits it a sixth time, so read them together before touching the
section. Two are corrections to what the section already says — **II-18** the level of the
volatility premium, **II-19** its missing tenor axis — two are additions the section never
attempted: **II-20** the first risk statistic anywhere in the article, and **II-21** the detour
that keeps II-20 from being read as a comparison it is not — and **II-26** is the citations §09
owes for results it argues out unaided. II-19 and II-20 add frozen cases; neither adds model
machinery beyond what `model.py` already has.

**Four came from the pass's harvest** (and **II-26** from its cross-check, in the sweep that
closed the conversion), converted 2026-08-01, and none of them moves a number anywhere:
**II-22** replaces §08's hand-derived census integrals with the theorem they are
instances of, and hands §10 a cleaner statement of its own capital criterion; **II-23** cites six
borrowed things where the reader meets them, and reaches outside Part II to do it (§00, §02, §11);
**II-24** gives §08's census its second analogy; **II-25** puts a size behind §05's early-exercise
caveat. All four depend on §03 (**I-1**) for the citations themselves — **§03 carries the
pedigree, the section carries the pointer**, and neither should be written twice.

**II-18. §09 quotes the *index* volatility risk premium at a single-name model.** (Divergence D1
of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md); raised 2026-07-31.)

[The returns section](#sec:returns) says implied volatility exceeds subsequently realised
volatility "by **2–4 points on liquid equities**" (§09:137), and then "against a documented
premium of 2–4 points, the whole of it is edge" (§09:148). **2–4 points is the index figure** —
SPX 3.3 points, VIX minus realised 4.2. The single-name literature, which is the one a
single-name model is entitled to, says materially less:

- **Bakshi & Kapadia (2003, *J. Derivatives*)** — 25 large US caps, 1991–1995: implied exceeds
  realised by **1.5 points** across all options, **1.07** once contracts with a dividend before
  expiry are dropped, against **3.3 for SPX on the same measure**. Delta-hedged gains lose 0.03%
  of the underlying for single names against 0.07% for the index. **[F]**
- **Carr & Wu (2009)** — variance risk premia are **insignificant for 32 of 35 individual
  stocks**, and strongly negative for every index. **[A]**
- **Driessen, Maenhout & Vilkov (2009)** — the mechanism: the index premium is substantially a
  **correlation** risk premium, which by construction has no single-name counterpart. **[A]**
- **Bakshi & Kapadia again — idiosyncratic volatility is not priced at all.** What little premium
  single-name options carry is the *market* volatility premium leaking through beta.
- **Merton–Scholes–Gladstein (1978), Appendix C [F]** — the earliest measurement of this gap that
  exists, and it is ~zero. 694 six-month single-name contracts, April 1973 – November 1975.
  Pooled, market premiums do run richer than Black–Scholes at trailing realised variance: ATM
  **11.7% of spot against 11.2%** (138 observations), OTM **7.5% against 7.1%** (96). But
  weighting each of the 14 dates equally the gap disappears — ATM **11.7% against 11.6%**,
  average difference **−0.1%**, which they call insignificant; OTM difference **0.0%**. Added
  2026-08-01 with the MSG read. **Caveat-grade and it cannot carry a number**: fourteen dates
  over 2.5 years, on *calls*, in the first years of the listed market. It earns a clause because
  it is the only pre-1990 single-name evidence anyone has and it points the same way as the rest
  of this list.

**What it costs.** At §09's own ~45 bp of edge per volatility point, 2–4 points reads as
**90–180 bp/yr** over buy-and-hold. The single-name range supports **48–68 bp**, and something
statistically indistinguishable from **zero** on a variance basis. The qualitative verdict is
untouched — break-even is still zero, every point is still worth about 45 bp, the edge is still
the whole of the volatility risk premium and nothing else. What moves is **the size of the
prize**, by a factor of two to three, and that is the number a reader deciding whether to run
this will take away.

**The item is a gain, not only a correction, and should be written as one.** σ_IV = σ is
currently presented (§00, §05) as an assumption made to strip the machinery bare. The single-name
literature makes it **the correct default for a single-name model**, not merely a conservative
one — which is a stronger statement than the article makes for it anywhere. §09 should say so.

**Three edits to §09.**

- **§09:137** — replace the flat 2–4 with the index/single-name split, and make the gap itself the
  point: why every study a reader has heard of quotes 2–4, and why none of it is theirs.
- **§09:148** — restate "against a documented premium of 2–4 points, the whole of it is edge" at
  the single-name figure. The σ_IV sweep is already frozen at 0.5, 1.0 and 2.0 points of richness
  in `examples/returns_benchmark.py`, which brackets the single-name range; **add one case at
  `--iv-spread 0.015`** so the top of that range is quoted from a check rather than interpolated.
- **§09:152** — "several points clear of the 2–4 the literature reports" measures the live
  account's put leg against a baseline that is now wrong. **Strip the baseline, and do not print
  the multiple.** Say the account's puts were dear by somewhat more than the single-name
  literature would predict and leave the size to [the live section](#sec:live): how much of that
  gap is skew rather than premium is a measurement question (D2 of the pass, not yet converted),
  and §09 must not brag about the live account's spread ahead of it.

**No formula, code or frozen case changes** beyond that one new sweep case. Nothing recomputes.

**Deliberately not touched** (decided with Sergei, 2026-07-31 — do not re-litigate):
[the introduction](#sec:introduction)'s contribution 4 and [the entry section](#sec:entry)'s
forward reference both carry the claim without digits — "the entire edge of the strategy is the
volatility risk premium", "implied volatility is *systematically higher*" — and both survive at
one point. §05 explicitly forwards the quantitative statement to §09, so §09 carries the whole of
it and is the only place the numbers need to be right.

**Related, and not this item.** The citations belong in §03 (**I-1**, whose subsection 4 is this
item's other half). The live account's own spread wants an ATM-matched, tenor-matched re-cut of
`iv_panel.py` before §15 quotes either figure — D2 of the pass, now **IV-5**, which also edits
§09 three lines away from this item and should be sequenced with it. And the structure Bakshi &
Kapadia imply, a single-name premium scaling with beta rather than a flat scalar, is outlook
material (**IV-3**), not a change to the spine.

**II-19. §09's single σ_IV has no tenor axis, and the model's cadence-neutrality is not honest
without one.** (Divergence D3 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md); the neutrality test D3
asked for was run on 2026-07-31 and is reported here.)

**The fact the model cannot produce.** Bondarenko (2019), 2006–2018: PUT, the monthly ATM SPX
put-write, compounded **5.97%** at Sharpe **0.50**; WPUT, the weekly programme, compounded
**4.51%** at Sharpe **0.40** — having collected **37.1%** of notional a year against PUT's
**22.1%**. More premium, less money.

**The test, run.** Holding n = 4 and sweeping absolute cadence over a 13× range at fair prices
(σ_IV = σ, 30y horizon):

| cadence | τ_c | lots/yr | E[I] | capital | excess | vs buy-and-hold |
|---|---|---|---|---|---|---|
| weekly 1/52 | 0.0769 | 10.40 | 11.40 | 11.59 | +1.60% | +0.01% |
| biweekly 1/26 | 0.1538 | 5.20 | 8.02 | 8.21 | +1.59% | +0.00% |
| monthly 1/12 | 0.3333 | 2.40 | 5.42 | 5.61 | +1.56% | −0.01% |
| quarterly 1/4 | 1.0000 | 0.80 | 3.09 | 3.28 | +1.47% | −0.07% |

**The excess moves 13 bp across a 13× change in cadence, against an empirical gap of 146 bp.**
So the model is cadence-neutral at fair prices, as D3 expected — and it is worse than silent: at
a *flat* volatility premium it harvests **45.0 bp per point weekly against 42.0 monthly**, because
premium volume scales as 1/√τ and a flat spread pays on volume. **The model's residual tilt
favours weekly; the record favours monthly.** At fair prices the two collapse to ±1 bp, which is
Israelov & Nielsen's Myth 4 confirmed — more frequent writing multiplies cash, not profit. The
Q-world identity holds at every cadence (7.9 / 10.3 / 13.1 / 14.5 bp), so this is the model
behaving correctly rather than a bug.

**The mechanism, derivable from Bondarenko's own table.** An ATM premium is ≈ 0.4·σ_IV·√τ, so a
programme writing 1/τ contracts a year collects ≈ 0.4·σ_IV/√τ. Pure √-scaling predicts WPUT
should collect √(52/12) = **2.08×** PUT's premium; it collected **1.68×**. So the weekly
programme's implied volatility ran at **1.68/2.08 = 0.81 of the monthly's** — roughly **3
volatility points lower** at those levels. The name a reader will recognise is the **VIX term
structure in contango**: VIX9D normally sits below VIX, so short-dated options are quoted cheaper
in volatility terms and a weekly programme harvests a smaller spread against the same realised
volatility. At §09's own ~45 bp per point, three points is the right order to close a 146 bp gap.
*Indicative arithmetic on published aggregates: the ratio is robust, the absolute levels depend
on that 0.4.*

**What §09 is missing.** "What the single σ_IV leaves out" names **Across strikes** and **With
depth**, and closes on premium volume. **It does not name tenor** — and the article's own running
example straddles that axis, writing weekly puts against four-week calls. If the term structure
is real, the flat σ_IV **flatters the put leg** relative to the call leg by something like three
points, a first-order bias in the leg the strategy leans on. IV-5's corrected panel points the
same way: puts ≤1wk at 30.8% against calls ~monthly at 33.6% on a session clock — weekly below
monthly, as contango predicts, though confounded by moneyness.

**Two edits to §09.**

- **A cadence sweep**, formatted like the dividend sweep it sits beside and carrying the same
  shape of conclusion — this dial barely moves the return per unit of capital and greatly moves
  how much capital the position needs. Three rows is enough.
- **"Across tenor"**, as a third bolded axis in "What the single σ_IV leaves out", with the sign
  stated and the magnitude sourced to Bondarenko's ratio. **This is what makes the sweep
  honest**: without it §09 reports cadence-neutrality as a result while the literature holds a
  146 bp counterexample the model cannot see.

**Precondition: INF-6.** The frozen cases this needs — `--tau-p` variants in
`returns_benchmark.py` for the excess and the difference, `returns_capital.py` for lots, E[I] and
capital — are *wrong* until the harness stops overriding `cadence`. `--tau-p 0.08333` currently
reports +1.74% against the correct +1.56%, because it sells a monthly put every week.

**Handed forward to III-1, not claimed here.** Capital per name is 11.59 weekly against 3.28
quarterly, so a 100-share-price account carries **8.6 names doing 89.7 lots/yr, or 30.5 names
doing 24.4 lots/yr, at the same ~1.5% return on capital** — cadence buys names by giving up
throughput. That is a sizing statement and III-1 owns sizing; §09 states the invariance and
points there. **Do not let §09 claim the extra names reduce variance**: that is §12's question and
nothing answers it yet. And it is *not* a capital-efficiency gain — capital per lot of throughput
**rises** 3.7× as cadence slows, from 1.11 to 4.10.

**II-20. The article reports no risk statistic anywhere, and the two it is missing cost a line
each.** (Divergence D4 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), with harvest H4;
converted 2026-07-31, and the betas below were computed while converting it.)

**The gap.** Israelov & Nielsen (2015) attribute **~25% of a covered call's risk** to a dynamic
*equity reversal* exposure — the position lengthens as the underlying falls — carrying Sharpe
≈ 0.10, essentially uncompensated. Under GBM that exposure *cannot* be compensated, so the model
is right to assign it no return. But the article never **reports** it, because it quotes
expectations and capital and no risk statistic anywhere. A reader arriving from the covered-call
literature will ask what the wheel's beta is and whether it is asymmetric the way BXM's is, and
the machinery to answer already exists.

**Computed 2026-07-31** — terminal payoff over one call period against the depth census,
inventory only, P-measure, 30y census. Indicative, done outside the model:

| configuration | up-beta | down-beta | gap |
|---|---|---|---|
| Standard p\* = 20%, n = 4 | 0.828 | **1.000** | 0.172 |
| Conservative p\* = 10%, n = 4 | 0.823 | **1.000** | 0.177 |
| n = 1, calls on the put clock | 0.927 | **1.000** | 0.073 |
| n = 13, quarterly calls | 0.683 | **1.000** | 0.317 |
| σ = 30% | 0.870 | **1.000** | 0.130 |

**Two results, neither of them anywhere in the article.**

- **Down-beta is exactly 1.000 in every configuration.** Below its strike a lot is pure stock, so
  the wheel absorbs the whole decline. That is Israelov & Nielsen's **Myth 2** — covered calls
  provide downside protection — disproved inside our own model, and Myth 2 is the wheel's own
  marketing. **With the put leg included it exceeds 1**: the operator holds the shares *and* is
  short a put that is losing. Say it that way; the wheel is more than fully exposed on the
  downside, and that is the sentence a reader will remember.
- **The asymmetry is governed by n** — 0.073 / 0.172 / 0.317 at n = 1, 4, 13 — and barely by p\*
  (0.828 against 0.823). That is [the holding-time section](#sec:holding)'s √n grid tax showing up
  in *risk* rather than in holding time: one lever, a second consequence, and the article
  currently draws only the first. Higher volatility *reduces* the asymmetry (0.870 up at σ = 30%)
  because lots run deeper and their calls sit further out of the money.

**What the subsection must carry.**

- **Include the put leg.** Everything above is inventory only, and the put is exactly what carries
  down-beta past 1.
- **Keep the delta-against-price framing beside the betas**, not instead of them: book delta rises
  toward 1 per lot as the price falls and toward 0 as it rises, which is analytic from `bs_call`
  and exhibits the reversal directly rather than as a regression coefficient. **Cross-reference
  Israelov & Nielsen's "equity reversal exposure" explicitly and consider adopting their term** —
  the article has no name for this at all, and theirs is the one a reader will recognise (agreed
  with Sergei, 2026-07-31).
- **Do not claim comparability with BXM's 0.63 / 0.78.** Ours is a different estimator, and
  **II-21** is where that comparison is made and where it stays a detour.
- Harvest **H5** — mapping our premium / mark-loss / giveaway / dividends onto their passive
  equity + short volatility + equity reversal — is adjacent, unconverted, and would sit naturally
  in the same subsection if it earns its space.

**No new machinery**: the census and `bs_call` are both in `model.py`. It needs an example module
and frozen cases under INF-5's policy.

**II-21. Replicate BXM's beta estimator against ours — a detour, deliberately not load-bearing.**
(Scoped with Sergei, 2026-07-31, out of II-20.)

**Why it exists.** Validating II-20's estimator on a degenerate census — a book permanently at the
money, which is a plain ATM covered call — returns **up-beta 0.000, down-beta 1.000** against
BXM's published **0.63 / 0.78**. That is not an error. A terminal-payoff regression on a truly
at-the-money call *must* return exactly 0 and 1, because the payoff is kinked precisely at the
strike. The published figures come from **calendar-monthly** returns misaligned with the
third-Friday roll, with strikes set at the first listing above spot; the misalignment smears the
kink and pulls the two numbers toward each other.

**The trap it closes.** H4 prescribes "regress the ledger's period returns on the underlying's,
split by sign" and compare with BXM. Followed literally, that yields a number which *looks*
comparable to 0.63 / 0.78 and is not: "the wheel's up-beta is 0.83 against BXM's 0.63" would read
as a like-for-like risk comparison and would be wrong.

**What to do.** On `wheel_sim.py` paths — this needs paths, because the analytic core cannot see
calendar misalignment — compute the split beta BXM's way: calendar-monthly returns, strike at the
first listing above spot, roll on expiry. Then put the two estimators side by side on the same
book. Two questions worth answering: how much of the gap is *misalignment* against how much is
the *strike offset*, and whether the two estimators agree once both are run on the same
simulated account.

**Keep it a detour.** A blockquote detour in §09 in the article's established style, or a
footnote. **§09's headline risk numbers stay ours**, and no conclusion in the article may depend
on this comparison landing any particular way.

**II-22. §08 derives by hand a theorem that has a name, and §10 inherits a better statement of
its own criterion.** (Harvest H1 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), its highest-value item;
converted 2026-08-01, and the identity was checked numerically while converting.)

The **generalised Little's law, H = λG** — Brumelle (1971) and Heyman & Stidham (1980), restated
in Little's own 50th-anniversary paper (2011, §3.2.2) **[P]** — says that for **any** weighting
f<sub>i</sub>(t) applied over each item's time in the system, the time-average H equals λ times
the per-item total G. L = λW is the case f ≡ 1.

**Every census integral in Part II is an instance of it**, and the article derives each in prose:

| weighting f | gives | where |
|---|---|---|
| 1 | E[I] = 11.40 lots | [eq:little](#eq:little) |
| e^x | cost-basis capital 18.23 | §09, "what is tied up" |
| the call premium at depth x | call income 0.3706/yr | [eq:income](#eq:income) |
| δ_net × market value | dividends 0.2422/yr | [eq:income](#eq:income) |

**Checked 2026-08-01, and it is exact.** Computed both ways at Standard/P/30y — the per-arrival
route (λ times the per-lot sum over its life) against the census route (E[I] times the
depth-census average) — the two agree to **0.000% on all four** when the census is read on the
walk's own cells. `model.py` already computes the H = λG side: `occupation()` returns exactly the
per-arrival sums `E[J]`, `E[prem]`, `E[basis]`, and `economics()` multiplies them by λ. **Only the
prose derives them by hand.** And `wheel_sim.py --scenario validate` already checks all four end
to end against machinery that shares nothing with `model.py` (E[I] +5.8%, cost capital +11.7%,
premiums +1.2%, dividends +5.5% at 200 paths).

**What §10 gains, which is the better half of this item.** The capital criterion is currently
derived as "the integral of e^x against the census converges". Under H = λG that is precisely the
statement that **G is finite for f = e^x** — the per-lot integral of carrying value over the
lot's life. The two boundaries then read as one sentence with two weightings: lots return iff W
is finite, their capital returns iff G is finite at f = e^x. That is a real gain in exposition and
it costs nothing.

**Three cautions.**

- **H = λG is a stationary identity and the article reports finite horizons.**
  [eq:little-finite](#eq:little-finite) is a truncation of it, not the theorem, and so is every
  horizon-indexed figure downstream. Whatever §08 says must keep that distinction as sharply as it
  currently keeps [eq:little](#eq:little) apart from [eq:little-finite](#eq:little-finite).
- **Do not claim novelty** — N3, and **I-1** carries the prohibition. Little's own worked example
  of a non-trivial weight is "the dollar rate of return on the ith asset in a portfolio of
  assets". §08 must not contradict what §03 is required to concede.
- **One detour, not two.** The value here is that a single detour covers the income and the
  capital results together, where the article currently justifies them separately. If it becomes
  two detours it has not paid for itself and the hand-derivation was better.

**Incidental, and not a defect in `code/`.** Re-integrating a *re-binned* census misprices the
steep weightings badly: call income read off 0.01-wide bins from an h = 0.02 walk comes out **15%
low**, while E[I] on the same bins is exact, because the call premium does nearly all its work in
the few cells nearest x = 0. Nothing in `code/` does this — `depth_census()` accumulates mean
depth and weighted q on the cells and only the printed table is binned — but §08's table invites a
reader to try it, and any check ever written against that table has to match bin width to h.

**II-23. Six borrowed things, none of them cited where the reader meets it.** (Harvest H2, H3 and
H9 of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), converted
2026-08-01; **extended the same day** with cross-check rows 2 and 13 and Israelov & Nielsen's
Myth 8, which the harvest did not claim and no other item carries.)

Six edits of a sentence or a clause each. No number moves and no formula changes — that is the
point of the item, since **N2 requires §03 to say the ingredients are standard** and the article
should not be quietly implying otherwise.

**The rule this item enforces: the citation lands in the prose, not only in §03.** §03 carries the
pedigree — what each source is, what it says, where it enters — but a reader meeting
[eq:siegmund](#eq:siegmund) in §07, or the mark loss in §09, has to be able to see *there* that
the claim is someone else's and where to check it. A name in a list at the front of the article
does not do that job. Every bullet below names the line it lands on.

*The machinery — three constructions the article derives as if they were its own:*

- **[eq:siegmund](#eq:siegmund) is Broadie–Glasserman–Kou.** §07 attributes the barrier shift to
  "a classical correction due to Siegmund" and §00's symbol table calls β "Siegmund's overshoot
  constant". The constant *and its use* are **Broadie, Glasserman & Kou (1997)**, *Mathematical
  Finance* 7(4):325–349 **[F]**: price a discretely monitored barrier option with the continuous
  formula and the barrier shifted by exp(±β·σ·√Δt). That is our call grid with the strike as the
  barrier, their framing is closer to what we do than Siegmund's sequential-analysis one, the
  paper carries an order of magnitude more citations in finance — and it supplies an honest error
  statement the section currently lacks: **the correction is asymptotic in the monitoring
  frequency**. Keep Siegmund (1979, 1985) as the origin, add Chang & Peres (1997) as the pointer
  for the higher-order terms.
- **θ = 2ν/σ² is the Cramér–Lundberg adjustment coefficient.** §10 calls it "the tail exponent …
  the single most informative number about a configuration of this strategy" and leaves it
  unnamed. It is the exponential rate of the all-time maximum of a Brownian motion with drift −ν,
  which is ruin theory's adjustment coefficient, and θ > 1 is a Cramér-type moment condition.
  Naming it costs a sentence, hands an actuary the entire structure at a glance, and tells every
  other reader that the second boundary is a known kind of object rather than a threshold we
  invented. **Caution: do not assert an identity with Dufresne/Yor.** Their exponential functional
  ∫e^(−2W)ds is the same *phenomenon* — an exponential functional finite exactly when a
  drift-to-variance ratio clears a threshold — and is **not** our object, which is E[e^x] under an
  occupation measure. Cite as "the same phenomenon appears as…", or not at all.
- **A wheel lot is an autocall.** §07's first-passage detour is pure theory and has no real-world
  anchor. An autocallable terminates at the first scheduled observation date on which the
  underlying is above a fixed level, which is a wheel lot exactly, and it is a product many
  readers will have heard of. Worth a pointer in the detour.

*The results — three places where the article argues from first principles something that is
already published, and would be stronger for saying so:*

- **§09's "it is not a return" has a formal version.** §09 opens the Track A critique with "cash
  accounting is internally consistent but it is not a return", and argues it unaided — which is
  right for a general audience and should stay. **Goetzmann, Ingersoll, Spiegel & Welch (2007)**,
  *RFS* 20(5):1503–1546 **[A]**, is the formal statement: Sharpe ratios can be *manufactured* by
  option-writing overlays, and they characterise a manipulation-proof alternative. One clause
  pointing at it tells a sceptical reader that §09's refusal to headline a cash yield is not our
  private preference. **[A] — cite the existence of the result, quote no number from it.**
- **§11's margin call has a published counterpart.** §11 derives it from the barrier — *the margin
  call is the moment capacity falls to meet the book* — and **Santa-Clara & Saretto (2009) [A]**
  report the same mechanism empirically: margin calls "limit the notional amount of short
  positions and force investors out of trades precisely when they are losing money". The
  cross-check marks this **CONFIRMED in kind, not in magnitude** — theirs is index puts on a
  margin schedule, ours is a wheel on one name, and the two sets of numbers are not comparable.
  **Cite the mechanism; never the magnitude.**
- **Myth 8 is this article's own opening slogan, and §09 already refutes it.** §02 quotes
  practitioners — *"assignment just means buying a good company at a discount"* — and answers that
  the slogans "contain truth, but they are not a model", deferring the argument. §09's mark loss
  *is* that argument: each arrival pays K for something worth S′, so the discount is a loss of
  e^(x₀) − 1 booked the moment it happens ([eq:mark-loss](#eq:mark-loss), 0.1632/yr). Israelov &
  Nielsen's **Myth 8 [F]** demolishes the same slogan directly, for covered calls and equivalently
  for naked puts, and §04's Track A framing ("assignment is *inventory acquisition, not a loss*")
  is the same claim stated as accounting. **Land it at [eq:mark-loss](#eq:mark-loss)**, where the
  article has earned it, plus at most a clause at §02 noting the slogan has been formally answered
  and pointing forward. **Do not turn §02 into an argument** — the deferral there is deliberate,
  and the refutation belongs where the number is.

**One read this item owes** (planned 2026-08-01).
`literature/li-zhang-discretely-monitored-first-passage-barrier-options.pdf` is downloaded and
**skimmed only**. It is the machinery behind the autocallable bullet, and a pointer to a
literature is a claim about what that literature contains — skim level does not support one. Read
it before writing that sentence. Everything else here is already at the level its bullet needs:
BGK is **[F]**, Israelov & Nielsen is **[F]**, and the two **[A]** sources are cited for the
existence of a result rather than for a figure, which is what **I-1**'s read-level rule permits.

**One INF possibility, recorded and not converted.** The discretely-monitored-barrier literature
has numerics built for our grid problem (quadrature reaching O(1/N⁴), Hilbert-transform methods
for the multi-asset case) from a method family that shares nothing with either `model.py` or
`wheel_sim.py` — so it would be a third independent check on `occupation()`. That is a larger job
than this item and nothing currently needs it.

**II-24. §08's census has a second, sharper analogy the article is not using.** (Harvest H8 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md); converted 2026-08-01, and
the §08-versus-§16 question the pass left open is decided here.)

§08 explains the census with **length bias** — the hospital-beds detour — which is right and
stays. Odean (1998) **[A]** offers a second one that is about this strategy rather than about
sampling: the **disposition effect**. In 10,000 discount-brokerage accounts investors are **1.5 to
2 times more likely to sell winners than losers**, unexplained by rebalancing, transaction costs,
taxes or subsequent performance, and strictly harmful in a taxable account; with Shefrin & Statman
(1985) it is one of the most robust findings in behavioural finance.

**The wheel performs the disposition effect by contract, with the discretion removed.** Every
winner is sold at the frozen call strike; no loser is ever sold at all. Odean's investors do it
1.5–2× more often than chance and it costs them; the wheel does it with probability one. That is
the most intuitive statement available of why standing inventory is dominated by deep lots, and it
costs one blockquote detour in the article's established style.

**§08, not §16** (the pass offered either). §16's list is what the model leaves *out*; this
describes what the model already produces, and it belongs beside the census it explains.

**Two things keep it honest.** The disposition effect is a finding about *discretionary* selling
and its measured harm is largely tax, which this article does not model at all (IV-3 now carries
the tax descope) — the analogy is structural, not a transfer of Odean's cost estimate. And the
detour must not be allowed to carry an argument: the result is already established by §08's length
bias and [the holding-time section](#sec:holding)'s first passage, and the analogy only makes it
memorable.

**II-25. §05's exercise-style caveat asserts a conclusion that can be cited and sized.** (From the
second-pass list of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md);
converted 2026-08-01, with the threshold computed while converting.)

§05's "caveat on exercise style" says early call exercise on dividend payers "shortens holding
periods and therefore *helps* the strategy, so omitting it is conservative". That is an
assertion, and `DONE.md`'s American-vs-European entry resolved the question on it. The pass
supplies a figure the resolution did not have: **Bakshi & Kapadia (2003, JoD) [F]** measure the
American-exercise premium at **about 2 volatility points** on short-dated near-money calls. At
§09's ~45 bp of edge per volatility point that would be ~90 bp/yr if it bound — the size of the
entire claimed edge — so it is worth knowing why it does not.

**It does not bind, and the reason is structural rather than empirical.** Our calls are **out of
the money on every date one is written**: the strike is frozen at the lot's basis and a lot
survives only while x > 0, which is S < K_c. Bakshi & Kapadia's 2 points is a *near-money* figure,
and near-money is exactly where the American premium concentrates. It is an upper bound on an
object this strategy never sells.

**The one channel that could bite, sized 2026-08-01.** A lot can rise above its strike
*mid-period* — §07 reports a fifth of the live book's inventory-time was spent above its own call
strikes — so a dividend-driven early exercise is available if an ex-dividend date falls inside the
call period. It needs the call's remaining time value below the quarterly payout of δ/4 = 0.625%
of the price. At σ = 20%, that requires the stock to be above the strike by:

| days to expiry | 28 | 21 | 14 | 7 | 3 |
|---|---|---|---|---|---|
| stock above strike by | 6.8% | 4.9% | 3.1% | 1.3% | 0.3% |

An ex-dividend date falls inside a given four-week call with probability ≈ 4/13. **The threshold
is self-defeating in both directions.** Early in the period, where an exercise would actually
shorten the wait, it demands 6.8% — more than a typical period's entire move of σ·√τ_c = 5.5%,
starting from a lot that was *below* its strike at the last grid point. Late in the period the
threshold collapses toward zero, but so does what is gained: exercise three days early instead of
at expiry changes nothing, because the lot leaves either way. **And a lot that far above its
strike was leaving at expiry in any case** — that is what q(x) says at negative depth. Early
exercise accelerates exits that were already going to happen, which is the direction §05 claims;
what is new is that the claim now has a size rather than a hand-wave.

**What to do, and it is small.** Add the citation and the reason to §05's caveat, so that "is
conservative" becomes "is conservative, and this is the size of what is omitted". Append a dated
`**Amended:**` note to `DONE.md`'s American-vs-European entry recording that the literature pass
reopened it and it closed the same way with a number behind it. **This does not reopen the
descope** — nothing in the model changes, and the European treatment stands.

**II-26. §09 states the article's central result and cites nobody, while the literature reaches it
independently.** (Cross-check rows 1, 3, 4 and 5 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md); converted 2026-08-01, out
of the sweep that closed the conversion.)

**The gap is structural rather than incidental.** §07 carries three citations and §08 one;
**§09 and §11 carry none at all**. The section holding the article's headline economic result —
that at fair option prices the wheel is indistinguishable from owning the stock — reads as though
nothing had ever been written on the subject. **II-23 is the case where §09 borrows; this is the
opposite case and it is the stronger one.** Where the article argues its way to a conclusion the
literature already holds, saying so costs a clause and turns a contrarian-sounding result into a
consensus one.

**Four, in descending order of value.**

- **Contribution 4 is confirmed in almost the same words** (row 1). Israelov & Nielsen (2014)
  **[F]**, stylised example — index at 100, one-month ATM call, IV 18% against realised 16%.
  Priced at IV = realised: *"even though the annual collected option premium is 22.1% of net asset
  value, there would be zero compensation for shorting volatility … no different from what would
  have been earned by simply reducing the index position size by 51%."* That is §09's result,
  reached from a decomposition — equity plus short volatility — that this article never uses,
  which is exactly what makes it **evidence** rather than agreement. Land it where §09 concludes
  the wheel is economically indistinguishable from owning the stock.
- **The 45 bp slope agrees on the mechanism, not merely the sign** (row 3). Our own extra premium
  per volatility point (0.0531 share prices) over capital (11.59) is **45.8 bp — a 100%
  pass-through** — and their example shows the same at a different notional-to-capital ratio
  ($0.23/month on $100 → 2.76%/yr). Two unrelated parameterisations agreeing that *all* of the
  richness arrives is worth a sentence, because the reader's natural objection to "every point is
  worth about 45 bp" is that surely something eats part of it. **Same source as the bullet above:
  one citation, two uses.**
- **The call-away giveaway is the dominant drag in published attributions too** (row 4). Hill et
  al. (2006) **[P]**: *"the cost of exercise ate away the largest proportion of the excess
  returns."* Ours is 0.3559/yr, the largest negative term in the ledger, and the first economic
  ledger omitted it entirely — so this is external confirmation that the term nearly lost is the
  one that matters most. A clause at [eq:giveaway](#eq:giveaway). **IV-1 owns the full four-way
  comparison** (harvest H6); this is a pointer to it, not a second copy of it.
- **Track B is standard practice, not a convenient choice** (row 5). §09 argues for market value
  from first principles — capital committed is what selling would release — and is right, but it
  reads as *our* argument for *our* preferred number. Hill et al. benchmark against a
  **delta-adjusted** index (long 1 − Δ, the remainder at LIBOR) and Israelov & Nielsen insist
  throughout on matched equity exposure. One clause noting that the exposure-matched ledger is
  what this literature does answers the reader who suspects Track B was chosen because it
  flatters. **Weakest of the four and the first to cut** if §09 gets crowded.

**§11's zero is left alone.** Santa-Clara & Saretto (II-23) is the one citation that section is
getting; the rest of it is derivation, and there is nothing published to corroborate a barrier
formula.

**Keep the density honest.** This is a general-audience article, and four citations in one section
is about the most §09 can absorb without becoming a survey — hence the fourth marked cuttable and
the third reduced to a clause. **§03 (I-1) carries all of these sources properly.** II-26 is the
pointer, on the rule II-23 states: the reader should meet the claim and its attribution in the
same place.

**II-27 competes for the same space and outranks bullets 3 and 4** (noted 2026-08-01). It brings
§09 a measured *slope* rather than a matching conclusion, which is a closer fit to the claim the
section is defending. If the two items are written together and §09 cannot hold both, cut Track B
(row 5) first and Hill et al. (row 4) second; bullets 1 and 2 are one citation and stay.

**II-27. §09's 45 bp slope has two independent precedents, and converting them to volatility
points is the work.** (From the Merton–Scholes–Gladstein read of 2026-08-01, which closed I-5.
The conversion below was done while raising the item and is **indicative, not a result**.)

[The returns section](#sec:returns) says every point of volatility richness is worth about **45
basis points** of excess return a year, and that break-even sits at **zero** points. That is the
article's central quantitative claim about where the edge comes from, and §09 supports it with
nothing outside our own sweep. **Both MSG papers ran the same experiment**: price the options at
model value, then re-run the entire simulation with the premium scaled from 70% to 130% of it.

| % of model premium | 70 | 80 | 90 | **100** | 110 | 120 | 130 |
|---|---|---|---|---|---|---|---|
| 1978, ATM covered calls, 136-stock (Table 8) | 0.8 | 1.8 | 2.7 | **3.7** | 4.7 | 5.7 | 6.8 |
| — its standard deviation | 6.8 | 6.8 | 7.0 | **7.1** | 7.2 | 7.3 | 7.5 |
| 1982, ATM uncovered puts, 136-stock (Table 7) | 1.7 | 2.5 | 3.3 | **4.1** | 4.9 | 5.7 | 6.5 |
| — its standard deviation | 5.2 | 5.3 | 5.4 | **5.6** | 5.7 | 5.9 | 6.1 |

Semiannual percentages. Their own summaries: a 10% rise in premium is worth "roughly an
additional 100 basis points" of semiannual average return on the 1978 calls and **80 bp** on the
1982 puts (70 bp for the DJ universe in both), while the standard deviation is "virtually
unaffected". **Return moves and risk does not** — precisely the shape of §09's claim, found
twice, on both legs, on real price paths, by authors with no stake in our conclusion.

**Why this is an item and not a citation.** Their axis is *percent of model premium*, ours is
*volatility points*, and the bridge has to be built. Indicatively, on the 1982 puts: their ATM
six-month put premium runs about **8.5%** of spot (1978 fn. 11 puts the ATM six-month *call* at
10% of stock price for the 136-stock sample in H1 1973; 1982 p. 8 gives an average put/call price
ratio of **84.9%** at E/S = 1.0); net investment is 100·E − P, about 91.5% of spot; and
Black–Scholes vega at T = 0.5 makes one volatility point worth roughly **3.2%** of that premium
at σ = 30%. Ten percent of premium is then ≈ 3.1 points, and 80 bp per half-year becomes
**≈ 50 bp per point per year, against our 45**.

**Treat that as a sketch.** σ = 30% is assumed rather than read — they report premium *levels* in
figures and never tabulate the variance rates behind them — the capital bases differ (they post
100·E in commercial paper per put; we carry inventory at market plus collateral), and the 1978
call leg needs its own conversion. Doing it properly *is* the item, and it is worth doing even if
the answer lands further from 45 than this sketch: an independent estimate of the same slope off
1963–77 data is a stronger thing to set beside §09's finite difference than any of II-26's four,
and a material disagreement would itself be a finding.

**Where it lands.** §09, beside the volatility-premium slope, as the answer to the reader's
natural objection that surely something eats part of each point. **Sequence with II-26 and
II-18** — all three edit the same subsection, II-18 moves the size of the prize, and II-26 is
choosing which citations survive; see its density note for what this displaces.

**II-28. The put leg's early exercise, where MSG 1982 supplies a number and a warning — and one
headline result that must not be imported.** (From the same read; **the put-side twin of II-25**,
which sized this question for calls and found it did not bind. This one binds differently.)

II-25 established that early exercise does not reach our *calls*: they are out of the money on
every date one is written, and the American premium lives near the money. **The put leg has had
no equivalent treatment.**

**The frequencies.** Six-month puts, 136-stock sample, July 1963 – June 1977 (Table 1), percent
exercised early / at expiration / never:

| | early | at expiry | never |
|---|---|---|---|
| OTM, E = 0.9·S | 24.7 | 3.0 | 72.3 |
| ATM, E = 1.0·S | 43.7 | 3.1 | 53.2 |
| ITM, E = 1.1·S | 65.4 | 3.2 | 31.4 |

DJ never-exercised: 73.7 / 52.3 / 25.2. Ours are OTM by construction, which is the top row — but
these are *six-month* puts under 1970s rates and dividend yields against our weekly ones, so the
window in which early exercise can pay is a fraction of theirs. Quote 24.7% with the tenor
attached or it will read as a claim about us.

**The warning is theirs** (p. 23): *"any simulation of put-option strategies that assumes all put
positions are held until the expiration date will systematically understate the returns to the
buyers of puts and overstate the returns to the writers of puts."* Our model is European; that
sentence is aimed at what we do.

**What it costs is the tail, not the mean**, and their own tables measure it. Table 6 re-runs the
simulation with the same premiums and early exercise switched off:

| 136-stock, ATM | with early exercise | held to expiry |
|---|---|---|
| average return % | 4.1 | 4.1 |
| standard deviation % | 5.6 | 6.6 |
| lowest return % | −6.4 | −13.2 |
| skewness | +0.44 | −0.44 |

The mean does not move. The left tail roughly doubles and the skew changes sign.

**The result that must not be imported, and the item's reason to exist.** In Table 5 uncovered
put writing beats fully covered call writing on every axis in all six strike-by-universe
pairings — higher return, lower standard deviation, positive skew, smaller worst loss — and beats
the DJ stock portfolio outright at E/S = 1.1. A reader who has met MSG will expect the wheel's
put leg to inherit that. **It does not.** The advantage is early exercise acting as a
*stop-loss*: when the stock falls far enough MSG repurchase the put at intrinsic value and the
proceeds sit in commercial paper for the balance of the period, so the position is closed and the
loss truncated. **The wheel has no such exit.** Assignment does not end our exposure; it converts
the short put into a lot that then rides the depth process to its own barrier, which is the whole
of Part II. So the wheel's put leg should be expected to resemble their Table 6 rather than their
Table 5 — and the European treatment is the *right* model of it for a reason unrelated to the
American premium being small.

**What to do.** Extend §05's caveat on exercise style — calls-only after II-25 — with one
paragraph for puts: the observed frequency at OTM strikes and six-month tenor, why a weekly tenor
sees far less of it, and the structural point that assignment in the wheel is an *entry* and not
an exit, so MSG's stop-loss is absent by construction. **This does not reopen the descope**, no
formula changes, and like II-25 it turns an assertion into a sized one. Append the dated
`**Amended:**` note to `DONE.md`'s American-vs-European entry alongside II-25's.

**One smaller thing, folded in here rather than given an item.** 1982 pp. 9–11 finds the put–call
parity model systematically understates American put values, worst in high-rate periods (1969,
1974), concluding that "for all but the 'roughest' of evaluations, the parity model is not an
appropriate put-pricing model". **We are not exposed today** — `model.py:120`'s `bs_put` is a
direct European formula and does not go through `bs_call` — but parity is the natural shortcut
for anyone extending the pricing, and §05's caveat is the place to spend a clause on it.

## Part III — Many assets

Neither file exists. This is Stage 3 of the restructure and the largest single block of
remaining work. Both sections have their inputs already measured or already derived; what is
missing is the derivation and the prose. **III-3 is not a third section** — it is a constraint on
how the other two are written, and it is recorded now precisely because it must bind before they
are drafted rather than be discovered afterwards.

**III-1. Write §12, the portfolio section** (`{#sec:portfolio}`). It owes four things:

- **The diversification result** §02 promises: expected return and expected capital are
  unchanged by diversification, which removes only the variance around them. Little's law needs
  no independence assumption and so carries over directly; the statement to be careful with is
  what *does* change. **III-3 names one thing that does, and the literature quantifies it**: the
  premium, which is a single-name price and not an index one.
- **The distributional claims the single-name analysis handed forward** (was #1). The article
  states that ±√I\* and e^(−I\*) belong to a diversified portfolio of independent wheels, not to
  one name — on one name the inventory is nothing like Poisson (Var/Mean ≈ 4.8, P(I = 0) ≈ 14%
  against Poisson's 0.9%). §12 is where that promise is redeemed.
- **Position sizing** (was #6). The model sells exactly one put per period regardless of
  capital. A practitioner-facing subsection on sizing against total capital belongs here, and
  the warning it must carry is that capital demand is bursty and heavy-tailed, so **sizing
  against mean capital is precisely the mistake**.

  **Quantified 2026-07-29 (II-7), and the warning has a second half that is worse than the
  first.** The mistake is not only that demand is bursty *around* its mean: the mean itself is a
  near-singular function of two parameters nobody knows exactly. A\* runs **7.97 / 19.23 / 48.97
  / >126** across σ = 15/20/25/28% and diverges at 30%, a local elasticity of **3.5** rising to a
  4.2 secant by σ = 25% — a 1% relative error in the volatility estimate is a 3.5% error in the
  equity required, and the sensitivity worsens as volatility rises — while the dials the
  operator actually chooses (p\*, the cadence, n) move it proportionally and predictably. Sized
  for the running example and run on a σ = 25% stock, an account retains **39.3% throughput**.
  Both halves belong in this subsection: the distribution around the mean, and the fragility of
  the mean. Anything quoting the elasticity must say which of 3.5 and 4.2 it means.

  **Cadence is the third sizing dial, handed here by II-19** (measured 2026-07-31, recorded in
  this item 2026-08-01 so the figures sit where the work is). Capital per name is **11.59** share
  prices at weekly cadence against **3.28** at quarterly, at the same ~1.5% return on capital — so
  a 100-share-price account carries **8.6 names doing 89.7 lots/yr, or 30.5 names doing 24.4
  lots/yr**. **Cadence buys names by giving up throughput.** It is *not* a capital-efficiency gain:
  capital per lot of throughput **rises 3.7×** as cadence slows, from 1.11 to 4.10. §09 states the
  invariance and points here; this subsection owns what an operator does with it. **The sizing
  argument may not assume the extra names reduce variance** — that is the distributional claim two
  bullets up, which §12 has to *derive* before sizing is allowed to spend it. II-19 states the
  same prohibition from §09's side, where the answer is simply not available.
- **The live book's width** (was #24, figures restated 2026-07-27). The account sells puts
  across **95 names while holding inventory in 34**, so put margin is **$43.4k = 31% of Track B
  capital** against the single-name model's 1.6%. Premium is generated across a far wider book
  than the inventory it creates. This is the structural difference that most damages
  comparability: **any direct comparison of Track A yields between model and live account is
  meaningless without it**, which makes it §12's business and a caveat §14 must reference.

**III-2. Write §13, the correlation section** (`{#sec:correlation}`). Two results:

- **Common-shock arrivals** (was #11). Assignments across a portfolio of wheels cluster on
  market-wide drawdown dates. Exits diversify across names; **arrivals do not**. A
  portfolio-level model needs a systematic component in p, and the sting is the timing: bursts
  arrive exactly when capital is scarcest. Clustering is measured in the live book and waiting
  to be used.
- **Correlation → 1 in a crisis**, framed as §02 promises it: the mechanism the strategy is
  most exposed to, not a tail scenario. Every diversification benefit claimed in §12 is a
  benefit that fails in exactly the state that matters — **and the premium never paid for it**,
  which is III-3 and is the sentence that joins this section to §12.

**III-3. §12 and §13 are the same fact seen twice, and Part III has to be written that way.**
(Divergence D6 of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md);
converted **speculatively** on 2026-07-31, before either section exists, because it constrains how
they are written — recording it afterwards would be recording it too late.)

**The promise.** §02's contribution 7: diversification "leave[s] the expected return and expected
capital *completely unchanged* while removing only the noise around them — and … correlations
rising toward one in a crisis is not a tail scenario but the mechanism the strategy is most
exposed to." One sentence, two clauses, currently reading as two topics.

**The quantity side is safe.** Little's law is additive across streams and needs no independence
assumption, so E[I] = λ·E[W] carries to a book of N names directly, and H = λG with it. Nothing
about the expectation half of contribution 7 is in danger.

**The price side is not, and the literature names the mechanism.** Driessen, Maenhout & Vilkov
(2009): the index variance risk premium is substantially a **correlation** risk premium, and the
components do not carry it. II-18 supplies the magnitudes — SPX **3.3 points** against
**1.07–1.5** for single names — and **that gap is the correlation premium**. So a diversified book
of single-name wheels collects the **single-name** premium, the small one, while in a crisis, as
correlations rise toward one, it carries **index-like** risk.

**Index-like risk, single-name pay.** That is one sentence and it is both halves of Part III.
§12's benefit and §13's vulnerability are not two subjects; they are one quantity with opposite
signs, and it is the same quantity II-18 is correcting §09 for.

**One counterweight the section must carry, or the argument misleads.** DMV also find the
correlation premium **cannot be harvested once realistic frictions are imposed**. So the
conclusion is *not* "write index options instead" — it is that the diversification benefit is
smaller than it looks, and that the compensation for the risk left over was never actually
available to anyone.

**What this constrains in III-1 and III-2.**

- **Say which comparison is being made.** "Diversification leaves the expectation unchanged" is a
  statement about going from one name to N names, and as such it is true. It is **not** the
  statement that a basket of single-name wheels equals a wheel on the index — different trades at
  different prices. A reader will run the two together unless stopped, and contribution 7's
  wording does nothing to stop them.
- **Write the two sections as one argument**, or at minimum have §12 end where §13 begins.
  Contribution 7 already puts them in a single sentence; the sections should earn it.

**Part III's literature is unread, and this item is the whole of what has been read.** (Second-
pass list of the same document; folded in 2026-08-01.) The pass deliberately stopped here, on the
ground that the reading should happen *with* §12 and §13 rather than before them — so before
either drafts, read Driessen–Maenhout–Vilkov in full and read around it: the correlation risk
premium literature more broadly, the crisis-correlation literature, and whatever exists on
diversifying short-option books. **The read levels bind** (I-1): DMV is **[A]** — an abstract —
which is why this item states its mechanism qualitatively and takes its *magnitudes* from II-18's
Bakshi & Kapadia and Carr & Wu instead. Nothing here may be upgraded to a quoted DMV number until
someone opens the paper, and §13 must not lean on it further than the item already does.

**III-4. A portfolio of nonlinear positions is not the nonlinear position on the portfolio, and
contribution 7's wording invites the confusion.** (From the Merton–Scholes–Gladstein read of
2026-08-01. **Sits under III-3's constraint** rather than beside it: III-3 says §12 and §13 are
one argument, and this is a second way that argument can be got wrong.)

**The mechanism, in their worked example** (1978 fn. 14). Two at-the-money fully covered
positions: 100 shares of each stock at $100, one call written on each for $1,000, net investment
$18,000, semiannual dividend yield 1.5% on both. Let the ex post average price appreciation
across the two names be zero. If both end at $100 the covered portfolio earns **+12.8%**. If one
ends at $70 and the other at $130 — same average, identical stock-portfolio return — the covered
portfolio **loses 4.7%**. The intrinsic value of one call is $3,000 in the second case and zero
in the first, and the average conceals it entirely.

**It is not a constructed case.** Appendix C.II gives the real one: DJ sample, second half of
1973. The equally weighted stock portfolio returned **+0.9%** with dividends. The average
percentage premium was **8.3%**, so the single-position analogy predicts about **+9.0%**. The
portfolio of fully covered positions returned **+0.5%** — because 11 of the 30 names rose and 19
fell, and seven of the eleven rose more than 20%. Their own warning (p. 206) is that using one
covered position on a stock portfolio as a surrogate for a portfolio of covered positions "will
be biased high if the premium received for the single option is assumed equal to the average
premium received in the writing portfolio".

**What this does and does not do to contribution 7.** The promise is that diversification "leaves
the expected return and expected capital *completely unchanged* while removing only the noise
around them". **The expectation half is safe, and III-3 already says why** — expectation is
linear, so E[portfolio] is the average of E[position] whatever the dependence structure, and
Little's law carries across streams with no independence assumption. MSG's point is about the *ex
post* relation between a book's realised return and its constituents' average realised return,
which is a different object and is not a counterexample to the promise. **But "removing only the
noise" is the phrase that will mislead.** It invites the reader to picture a distribution
narrowing around a fixed centre. What actually happens to a book of concave positions is that
cross-sectional dispersion is a cost which does not average away: every lot's upside is capped
against *its own* frozen strike, so spread among the names converts into forgone gains no matter
how many there are. Diversification shrinks the noise and leaves that intact — and on our own
ledger the forgone gain is [eq:giveaway](#eq:giveaway), already the largest negative term.

**Why it belongs to Part III and not to §02.** The contributions list is not wrong and does not
need rewriting; the claim is true as stated. What is missing is the sentence §12 has to carry so
a reader does not over-read it — the same shape as III-3's "say which comparison is being made",
and a constraint on how §12 is written rather than a correction to §02. Only if §12 cannot say it
cleanly should contribution 7's wording be revisited, under I-4's standing "check, not a rewrite".

**It is also the one piece of hard evidence Part III has on its own subject.** III-3 records that
the literature on diversifying short-option books is the thinnest we have, and that DMV — the
anchor — is **[A]**, an abstract. MSG 1978 is **[F]**, is precisely on this question, and comes
with both a worked example and a dated real portfolio. Use it in §12 where the diversification
benefit is first claimed.

## Part IV — Reality

Neither §14 nor §15 exists; the outlook is a stub. Everything below is measured — these are
write-ups.

**IV-1. Write §14, verification** (`{#sec:verification}`, was #21). The spine tested against
live data, not only simulation.

- **Entry law:** 69.9 assignments expected, 72 finished below the strike, 71 assigned, over 956
  contracts — an aggregate error of −1.5%.
- **Depth census:** mean depth 0.157 model against 0.148 live over 4,204 lot-days. The model
  fits at the article's **μ = 7% far better than at the window's realised drift** (0.157 against
  0.097) — that deserves its own paragraph, since it is a statement about which parameter the
  census is actually sensitive to.
- **q(x):** 27.6% of calls expected exercised against 19.6% realised, monotone in depth.
- **Survival:** the model exits lots faster than observed at every horizon, and the comparison
  is Kaplan–Meier, so **this is not censoring** (was #9). Show the compounding of the
  per-period gap.
- **The two internal checks:** the grid-free Monte Carlo (`mc_holding.py`) that proves the
  extrapolated stationary figures, and the **Q-world no-arbitrage identity** — run at ν_Q with
  Q-priced premiums, expected excess return over r must vanish up to the dividend-withholding
  leak; it holds to 8 bp at 30y and under 20 bp at every horizon, and it has already caught one
  real omission. This is the settled decision the restructure owed the article a theorem for.
  **What the leftover residual is, is open** (from II-2, 2026-07-28). It is *not* the Track C
  overcharge on collateral, which was this item's previous claim: the residual is positive
  (+17.5/+12.6/+7.9 bp at Standard's 5/10/30y) where that argument predicts negative
  (−16.0/−11.3/−6.7), and at Conservative it reads +2.3 bp against a predicted −31.5. The clue
  worth chasing is that Q-world `econ_pnl` exceeds r·E[I] − leak by ≈ **0.0020 per arrival** in
  both regimes at every horizon — a per-lot term, not a capital-proportional one. Either
  identify it or state the residual as numerical tolerance and say so; do not attribute it to
  the collateral.
- **Claim only the aggregates.** The restatement withdrew two bin-level results: T1's
  calibration curve is sensitive to whether entry is priced at the session open or close (top
  bucket 27.0% predicted against 8.1% realised at the open, 26.1% against 27.0% at the close —
  the operator sells into intraday weakness that partly reverts, so the truth is between), and
  q(x)'s two deepest bins now hold 70 and 20 contracts. No bucket-level claim should be
  reintroduced.
- **The calendar/session mismatch, found 2026-07-28 and deliberately not fixed.** Every τ in the
  live tests is in *calendar* years while every σ is annualised over **252 sessions**, so a put
  written Monday at the open for Friday's close — five sessions — is priced with four days of
  diffusion. The units are wrong and the understatement is large: σ·√τ is short by a factor
  √((5/252)/(4/365)) = **1.35** at the median put. **And the wrong convention is the one that
  fits.** At the window's drift, pricing each put on its own session count predicts **88.7**
  assignments against the **71** that occurred; the calendar reading predicts **69.9**. So either
  the operator's entries partly revert — which is T1's own bucket finding, the opening print
  overstating moneyness on puts written nearest the money — or session-annualised realised
  volatility overstates the volatility relevant to a five-session option, or both. Resolve it
  before claiming T1 as a clean pass, and note that the aggregate agreement currently rests on
  a cancellation rather than on each side being right. Nothing was changed in the code; the
  decision and its evidence are in `model_vs_live.py`'s T1 docstring. Note the article itself is
  unaffected: its τ_p = 1/52 is 4.85 sessions, so its own week is already a trading week.
- **Three measurement traps**, worth a paragraph because all three were fallen into: reading
  depth on the day before exit discards nearly every exit; sampling lots on a synthetic τ_c grid
  scores periods at tenors never traded; and pricing an entry at the day's close when the
  operator writes in the first hour builds a look-ahead into every measured entry depth.
- **What a career-length record cannot test** — owed to §02 (I-4) and not yet written anywhere.
  The natural material is already in Part II: equilibrium is approached over ~90 years and the
  mean holding time is 2.1 years against an 8-week median, so the stationary results are
  structurally untestable by any operator, and the 15-month window resolves 40 of 55 lots. State
  which predictions the data *can* discriminate and which it provably cannot.

  **The method for this bullet is Broadie, Chernov & Johannes (2009) [P]** (harvest H7, folded in
  2026-08-01), and it says the thing we need better than we can say it unaided: put returns are so
  noisy that **18 years of monthly data cannot reject Black–Scholes even for deep-OTM puts**
  (p ≈ 8%), and **CAPM alphas and Sharpe ratios on option returns are noisier still than raw
  average returns** — so the natural-looking regression is the *worst* test available. Their
  prescription is to test market-neutral or delta-hedged *component* portfolios rather than
  strategy returns, which means our overlay-excess statistic (wheel minus same-names buy-and-hold)
  is already the right *kind* of measurement and should be defended as such. IV-2 uses the same
  citation for its intervals.
- **An external check on the ledger's *structure*** (harvest H6, folded in 2026-08-01). Hill,
  Balasubramanian, Gregory & Tierens (2006) **[P]** attribute a fixed-strike buy-write's return
  four ways — fair call premium, volatility premium, exercise cost, trading cost — and conclude
  that **"the cost of exercise ate away the largest proportion of the excess returns"**. That is
  our call-away giveaway, which the first economic ledger omitted. A paragraph comparing the
  *shape* of our attribution to theirs is a validation the Monte Carlo cannot supply:
  `wheel_sim.py` checks that the ledger adds up, not that its terms are the right terms. They also
  benchmark against a **delta-adjusted** index (long 1 − Δ, the remainder at LIBOR), which is
  Track B's logic arrived at independently and is worth saying beside it.

**IV-2. Write §15, the live account** (`{#sec:live}`, was #20). The ledger and its verdict.
**Lead with the ledger gap, not the return.**

- **The ledger:** Track A on cost basis **+38.36%/yr** against Track B **+24.34%**; same-names
  buy-and-hold +28.71%; option-overlay excess **−4.37%/yr**; selection **+29.63%/yr**,
  exposure-matched.
- **This section owes the reader the intervals, and it is the only section that does.** Parts I
  and II assert three times — in `02-introduction`, `04-strategy` and `09-returns` — that the
  overlay "earned nothing distinguishable from zero", with no number anywhere behind it. That is
  deliberate, the statistics belong here, but it means §15 must actually deliver them or the
  claim is unsupported across the whole article. Required: the point estimate, the 90%
  resampling interval **−18.1% to +6.9% clustered by name** (quote the clustered one; −24.0% to
  +13.4% by lot is the looser alternative), P(excess < 0) = 69%, and the sample it rests on.
  `live_ledger.py --bootstrap` produces all of it.

  **Present the width as a property of the object, not of the sample** (harvest H7, folded in
  2026-08-01). A twenty-five-point interval over fourteen months reads as an apology for a short
  record; Broadie–Chernov–Johannes make it the *expected* consequence of a known property of
  option returns, which eighteen years does not fix. IV-1 carries the citation and the fuller
  statement — use it here rather than restating it.
- **The UNH lot is the worked example**, deliberately kept out of Part II so it lands here:
  assigned at 260, a four-week call written at the same 260 basis for $18.10, called away at 260
  with the stock at 393.85 — collected $1,810, surrendered $13,385. It is also, on its own, the
  difference between a negative and a positive overlay excess (−4.37% → +1.99%) **and** 39% of
  the selection gap. The same position carries both verdicts, and that is the point rather than
  a caveat: a lot that runs far enough to dominate selection is a lot whose call gave the run
  away. **Do not present it as an outlier to be set aside.** UNH, ELV and MSFT all show negative
  excess and positive selection together.
- **The by-leg decomposition**, which is where the restatement bites: the **put leg keeps 25.2%
  of premium, the call leg −28.9%**, frictions −$7,107. The old near-symmetry between the legs
  was cheap calls on falling names; on the universe the strategy actually claims, the call leg
  gives back nearly a third of its own premium. Removing those names did not create the effect, it
  stopped hiding it.
- **Selection, reported not modelled** (was #22 and #14). The pre-registered rule
  (`drafts/2026-07-27-selection-rule-preregistration.md`) is fitted: rules 4 and 6 (fallen
  angels, oversold) confirmed at z ≈ −10 with a permutation check agreeing; rule 5 (avoid
  falling knives) **rejected outright** in both its simple and its interaction form — its
  partial rescue was withdrawn on the restated choice set. **Name what modelling it would
  commit to:** under GBM, entry timing cannot generate return by construction, so treating
  selection as profitable is a claim of mean reversion and must be argued as one. 20 lots in one
  bull market cannot support it. If it is ever modelled, the minimal form is a state-dependent
  thinning of the arrival process.

  **Goyal & Saretto (2009) [A] is the published version of this claim — and it is not the claim
  the account is making** (harvest H11, folded in 2026-08-01). Sorting stocks on
  implied-minus-historical volatility and trading straddles produces large, robust cross-sectional
  returns. That is an **options** signal: it says the *contracts* on some names are mispriced.
  Rules 4 and 6 (fallen angels, oversold) are **stock-selection** signals — a claim about the
  shares — and the account's own ledger agrees, since the overlay earned −4.37% while the
  selection earned +29.63%. Cite it to make that distinction sharp, which is the opposite of using
  it as support; the honest reading is that the published edge lives in the leg this account did
  *not* profit from.
- **The cadence calibration** (was #7). τ_p = T is a good approximation because the dominant put
  is sold Monday at the open for Friday's close — live 5 of the week's 7 days, continuous in
  trading time. What the account does instead of selling every week is skip weeks: **18.1 puts
  per name-year while in rotation** against 52, **1.41 lots per name-year** against the model's
  10.4 at p\* = 20%, modal gap exactly 7 days (40% of gaps). Both rates are the discrepancy
  catalogue's and have no script behind them (INF-2); the lot count under the second moved
  56 → 55 on 2026-07-28, so re-measure before quoting rather than copying the digits.
  [The entry section](#sec:entry) now defers the arrival gap to here, deliberately without
  digits, so this is the only place they appear. When they are re-measured, **check the identity
  that closes the gap**: puts per name-year × the per-put assignment rate should reproduce lots
  per name-year, which at the current digits it does (18.1 × 7.7% ≈ 1.4). If it stops doing so,
  one of the three is measured over the wrong denominator.
- **The implied-volatility panel** (was #23). The within-name depth slope is **+30–40% relative
  IV** from shallow to deep. This is the measurement behind the article's decision to carry one
  scalar σ_IV; report it here and let [the returns section](#sec:returns)'s stated bias direction
  be checked against it. **The level is withdrawn pending IV-5**: the panel's "~+10 points,
  roughly double the call leg's" is measured on a calendar clock against a session-annualised
  realised volatility, and about six of those ten points is that mismatch. Do not write §15 from
  the old figure — re-run the panel once IV-5 lands and quote what it says then. The depth slope
  is unaffected (within-leg, within-name and within-tenor, so the clock cancels), but it rests on
  **9 contracts in the deepest bucket** of a column that is not monotone; quote it with that
  qualifier or not at all.
- **The regime caveat, which bounds everything above:** the universe returned +9.96%/yr over the
  window and the held names +39.59%/yr, and **a covered-call overlay must lag in a strong
  up-market**. That is mechanical, not evidence. Neither the overlay nor the selection result is
  an unconditional estimate.
- Reference III-1's book-width caveat rather than restating it: Track A yields are not
  comparable between a 95-name put book and a single-name model.

**IV-3. Rewrite §16, the outlook.** Currently a stub whose standing content is the list of
things deliberately outside the model — the call-strike lever, permanent impairment and the
dividend cut, the entry filter, transaction costs, skew, moving volatility, depth-dependent
drift. That list is accurate and should survive. What it cannot be written around until Parts
III and IV land is the forward-looking half: what the model should become, given what the live
comparison actually showed. Write last, and rename the file to `16-outlook.md` when Part III
takes §12 and §13.

**One addition to that list, from II-19:** a **σ_IV(τ) term structure** is the minimal extension
that would let the model speak to cadence at all. Cadence is currently the one dial the model
reports as nearly free — 13 bp across a 13× range — where the record says it is not, and the
model's residual tilt even points the wrong way. II-19 carries the size of the slope the record
implies. It is also the first thing a practitioner would ask for.

**One more of the same kind, from II-18** (which sends it here; recorded 2026-08-01 so the pointer
resolves): a **beta-scaled σ_IV**. Bakshi & Kapadia find that idiosyncratic volatility is not
priced at all, and that what premium single-name options do carry is the *market* volatility
premium leaking through beta — which predicts the single-name spread should scale with the name's
beta rather than being one flat scalar. That is a testable structure the model could carry, and it
is the natural companion to the term structure above: one gives σ_IV a tenor axis, the other a
cross-sectional one. Neither touches the spine.

**Two more, from [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), folded in
2026-08-01.**

- **Transaction costs get a number** (harvest H10). The list currently says commissions "eat a few
  percent of the premium on weekly puts" — a live-account figure — and has nothing at all for the
  spread, which is the larger cost. **Muravyev & Pearson (2020) [A]**: traders who time their
  executions pay effective spreads of **29.6%** (algorithmic) to **58.4%** (all traders) of the
  quoted half-spread, so conventional estimates roughly double the truth. Hill et al.'s **3–6
  bp/month** at half an implied-volatility point of slippage is the covered-call-specific version.
  Both are quotable in a sentence and turn a descope into a bounded one.
- **Tax is missing from the list entirely**, which makes it read as an oversight rather than a
  decision. It is unexamined everywhere in this project and it is materially adverse for a wheel
  run in a taxable account: premium is short-term, repeated assignment on one name raises **wash
  sales**, and the **qualified-covered-call** rules suspend the holding period on the underlying,
  so writing the call can cost long-term treatment on the shares. §16 should say plainly that tax
  is out of scope and roughly which way the omission cuts. It also connects to **II-24**: the
  disposition effect's documented harm is largely a tax harm, and this article cannot price it —
  which is exactly why II-24's analogy must stay structural.

**IV-5. `iv_panel.py` measures implied against realised volatility on two different clocks, and
the article quotes the difference.** (Divergence D2 of
[the literature pass](drafts/2026-07-31-prior-work-literature-pass.md); the clock half was found
while converting it, 2026-07-31. **Must land before §15 is written**, and it edits §09.)

**The claim at issue.** IV-2 records the put leg running **~+10 points** over subsequent realised
volatility, roughly double the call leg. Against the *index* premium of 2–4 points that reads as
"several points clear"; against the single-name baseline II-18 installs (1.07–1.5 points) it
would be tenfold, which is too large to leave as an aside — the article uses it in two places at
once, as evidence the premium is real and as evidence the premium does not arrive.

**Most of it is a units mismatch.** `iv_panel.py` inverts Black–Scholes with
`tau = (exp - open).days / 365` — calendar time — while `forward_vol` annualises realised
volatility over **252 sessions**. The two coincide at monthly tenors and diverge badly at weekly
ones: a four-day put is priced with too little diffusion, so the inversion hands back too much
volatility to match the premium. Priced on session time at a true 20% and inverted on calendar
time, a weekly put reads **26.6%**; the same test on a 25-day call reads **19.8%**. **An artifact
that inflates only the short leg is exactly the shape of the reported finding.**

Measured per contract against the real session calendar, the inflation factor is **1.204** at
≤1wk, 1.089 at 1–3wk, ~1.04 at monthly and 1.016 at longer. Indicative effect on the panel's own
medians (computed outside the script, 2026-07-31 — the re-cut must redo it per contract):

| leg / tenor | as measured | on a session clock | RV | spread |
|---|---|---|---|---|
| puts ≤1wk (n=493) | 37.1% | 30.8% | 26.7% | **+10.5 → ~+4.1** |
| calls ~monthly (n=78) | 34.8% | 33.6% | 31.0% | **+3.8 → ~+2.6** |

So roughly **six of the ten points is the clock**, and the put/call asymmetry falls from ~2.8× to
~1.6×. This is the same mismatch IV-1 documents for `model_vs_live.py` — the 1.35 factor at the
median put — which nobody had connected to `iv_panel.py`. **The article's own
formulas are unaffected**: τ_p = 1/52 is 4.85 sessions, so its week is already a trading week.

**The skew half is measurable after all, and cheaply.** The pass prescribed an ATM-matched
re-cut and doubted the data supported one. It does, on the call leg only, and *by design*: the
call strike is frozen at the lot's basis, so a shallow lot writes a near-money call. Cross-tabbing
the call leg by moneyness on a session clock gives a clean monotone skew signature —
**+1.6 (ATM, n=43) / +3.1 / +4.1 / +6.7 (>+10%, n=65)**. The put leg has no ATM cell by design and
never will; the 35 near-money puts in the current skew table are accidents and behave like one
(median IV 18.1% against 45.7% two buckets out).

**What to do, in order, with an early exit.**

1. **Fix the clock.** Put the comparison on session time (τ = sessions spanned / 252, counted
   from the price series, which knows the real calendar) and print the as-quoted calendar IV
   beside it so the panel still ties to what the broker screen showed. This is a measurement
   change, not a modelling one.
2. **Add the missing cross-tab**: IV − RV by leg × moneyness × tenor. The panel currently reports
   IV − RV by tenor and IV by moneyness and never crosses them, which is why the skew confound
   was invisible.
3. **Read the residual and stop.** If it lands near the single-name literature, the remaining
   work is a confirmation, not a rescue.

**Do not buy option-chain data for this.** Historical chains on ~500 name-days would be needed to
match ATM on the put leg, and `prices.py` fetches underlying OHLC only — that is a paid-data
question (OptionMetrics/ORATS/CBOE DataShop), not a scripting one. The ATM call cell already
exists for free, and **it can characterise but not calibrate**: split by tenor it is 28 / 6 / 9
contracts reading −3.0 / +2.0 / +9.1, so the cell that actually matches Bakshi & Kapadia's
near-money short-dated object rests on nine contracts. That is why II-18 calibrates §09 from
published figures and not from ours. If a fallback is ever wanted for the put leg, fitting a smile
per name-date from the operator's own cross-section and evaluating at x = 0 is interpolation
rather than new data — model-dependent, and it must be reported as such.

**Two consequences, one of them in live text.**

- **§09:162 says "the put leg's spread over realised volatility ran to roughly twice the call
  leg's."** That rests on the uncorrected panel and is ~1.6× after the fix. Whoever runs this item
  edits that sentence; it is the only Part II text IV-5 touches, and II-18 is working three lines
  away in the same section.
- **IV-2's "~+10 points, roughly double the call leg" is withdrawn pending this item** — see the
  note on that bullet. **The depth slope survives**: it divides by each name's own median IV
  within one leg at one tenor, so the clock cancels, and §09:164's "roughly a third" is untouched.

**IV-8. MSG's two methodological cautions, one of which delivers a promise nothing currently
delivers.** (From the Merton–Scholes–Gladstein read of 2026-08-01. Numbered **IV-8** and not IV-6: IV-6 and
IV-7 both closed on 2026-07-28 and are in `DONE.md`.)

**First, and this is the valuable half.** I-4 records that §02's contribution 8 promises the
article will show **which of the model's predictions a career-length track record has no power to
test**, and that *nothing currently delivers it*. MSG 1982 p. 33 is the precedent, and it is
about as authoritative as one gets:

> "The observed sensitivity of the average returns to the level of premiums should also serve as
> a further warning against placing great significance on the levels of measured average return
> even over a 14-year period."

1978 p. 214 says it of its own results too — the levels "reported in this or any other similar
study are rather sensitive to the assumed premiums". **Fourteen years, 136 stocks, 28 semiannual
observations, and the authors decline to read the levels.** Our record is shorter, narrower and
overlapping. That is not an argument for reporting nothing; it is the citation that lets §14 say
what the record cannot settle without sounding like an excuse, and it turns a promise §02 has
been carrying unbacked into a sourced one. The arithmetic of *our* version is II-27's: if a point
of volatility is worth 45 bp, then telling a two-point edge from a zero-point one asks a track
record to resolve 90 bp/yr.

**Second, the presentation discipline for a selection-driven result.** IV-2's verdict is that the
account's advantage came entirely from the excluded lever while the option machinery earned
nothing distinguishable from zero. MSG 1978 had the same problem — their 136 CBOE-listed names
were chosen by the exchanges partly on past performance — and solved it by **running everything
twice and reporting both**: the biased universe (beta 1.17, semiannual alpha **4.2%**) beside the
DJ 30 (beta 0.98, alpha **0.5%**), with the statement that the truth for a broadly diversified
holding lies somewhere between. 1982 fn. 25 repeats it over the extended window — S&P 500
semiannual 3.87%, sd 13.09%; 136-stock beta 1.17, alpha 3.68%; DJ beta 1.00, alpha 0.71%. **They
name the bias, in the direction that hurts them, before reporting a single strategy result.** §15
makes a claim of the same kind about one account with no control universe at all, and the honest
form of it is theirs: name the bias, size it where possible, and lead with the comparison that
does not depend on it. **Sequence with II-20 and II-21**, which want a beta reported and have no
precedent to point at for how one should be presented.

**And a pointer into IV-1.** MSG 1982 §III simulates the put/call **conversion** — long stock,
long put, short call at one strike and expiry, riskless under parity — against rolling commercial
paper. Average excess return: **−0.051 / −0.059 / −0.095%** per half-year across the three
strikes on the 136-stock sample and **−0.061 / −0.119 / −0.209%** on the DJ (Table 3). Small,
negative, and *explained* rather than shrugged at: converters pay above the parity price for an
American put, and the position is slightly bearish, so a return a little below r is what theory
asks for. **That is the empirical ancestor of the free test** — run at m = r − δ and the economic
excess must vanish — which IV-1 carries in its "two internal checks" bullet as a check we run on
ourselves. One sentence noting the same test was run on real 1963–77 price paths, landing 5–21 bp
per half-year from zero with the residual accounted for, tells the reader both that the test is
the standard one and that a small non-zero residual is the expected outcome rather than a
failure. **Do not present the two as numerically comparable**: different construction, capital
base and measure. It is the shape of the check that transfers, not the size.

**IV-4. Live data keeps arriving — standing.** Statements land roughly monthly and will keep
landing until the article is frozen for release. **Every tranche is ingested when it arrives and
every live figure is recomputed on the whole corpus to date**; the procedure is
[`drafts/tranche-record.md`](drafts/tranche-record.md), which also holds the running record and
the exact command list.
The out-of-sample pre-registration
(`drafts/2026-07-27-out-of-sample-preregistration.md`) fixes twelve predictions and a procedure;
**Appendix B, 2026-08-01, retired the trigger** and replaced it with that record, for the reason
the article should keep in view — the pre-registration bound estimation and inference with one
rule, and only the second needed protecting.

What still binds, and is not negotiable per tranche: refit, do not re-specify; no new features in
`selection_fit.py` without a dated amendment; classify the regime from the tranche's own universe
return *before* reading anything else off the refresh; report failures as failures, in a dated
appendix. P12 (impairment) is retired rather than pending.

**Scoring happens once, at freeze, against the accumulated record** — never tranche by tranche,
because a month is three or four lots against an excess whose interval is twenty-five points
wide. And the wording is fixed now, so it is not decided by whoever writes §14: the predictions
were **recorded before the data existed and checked afterwards, with the data examined
continuously in between**. They are not an out-of-sample test and the phrase must not appear.
P7's blind was partly opened on 2026-08-01 — the extended-window excess was seen before Appendix
B was drafted — and the scoring appendix says so.

**What P8 and P7's concavity are waiting for is a regime, not a tranche.** No quantity of monthly
data in a rising market tests "the selection edge shrinks when dips stop recovering". Both rows
of the record so far are labelled rally. That is the limitation the record exists to outlast.

**One thing to know before scoring.** Appendix A's restated P11 baseline of 56 d cannot be
reproduced by today's code: the same pre-tranche corpus now gives a Kaplan–Meier median of
**49 d**. Changes landed after that appendix was written on 2026-07-27 — the seam dedupe that
removed a phantom TSCO lot (56 → 55 lots, `8d6b592`) and the exclusion of EMLC and 9988
(`6aaf681`) are the candidates. Score P11 against a baseline re-measured with the code of the
day, and say so. (With tranche 3 the figure reads 56 d again — two different corpora agreeing by
coincidence, not the prediction landing.)

## Infrastructure and assembly

One standing discipline, inherited from Part II's code half and closing with no item: **every
number a section quotes gets a check under that section's heading.** For anything with a formula
behind it that is now enforced mechanically by INF-5's coverage test; INF-2 carries the rest into
Parts III and IV. Prose figures with no formula behind them are the residue it cannot reach —
II-16's stale "four years" survived the weekly-cadence change of 2026-07-26 for exactly that
reason — so a section's narrative numbers still have to be re-read by hand when a running
parameter moves.

**INF-2. Extend `verify_examples.py` to Parts III and IV — and decide about the live figures.**
Every number in §12–§15 needs a check, on the same section-by-section discipline as the rest, and
every formula they display needs an example module under INF-5's policy. Two open questions:
whether the portfolio results get their own Monte Carlo cross-check the way the single-name spine
did, and — the real gap — that **no check reproduces the live-account figures at all**. §15 will
quote a ledger produced by `live_ledger.py` against statement data; if those numbers move, nothing
tells us. At minimum, pin the headline ledger figures in a regression check so a change in
`analyze_statement.py` cannot silently restate the article.

The withdrawal of I-3 sharpened this: a figure that lives only in a draft, with **no script
behind it**, survived into TODO as a finding and was wrong about what it measured. The concrete
piece of that episode worth keeping is the **per-lot call-strike classification** — every call
scored against the layers actually held when it was written, not against one basis per name.
It exists nowhere in `code/`; the reconstruction that withdrew I-3 was ad hoc. Put it in
`analyze_statement.py` beside the lot lifecycle, where it can be re-run.

**INF-3. The LaTeX assembly pipeline.** Unicode-math → LaTeX conversion, `{#sec:...}` anchors →
`\label`/`\ref`, `{#eq:...}` → numbered `equation` environments with `\eqref`. Tooling decision
deferred until the sections stabilise, which is now close: pick it once Part IV drafts. The
generated appendix (`sections/99-reproduction.md`) needs a place in that pipeline too.

**INF-4. Figures.** The ASCII payoff diagrams in the §02 detour are placeholders and must be
redrawn as proper vector figures (TikZ or similar) at assembly. Worth reviewing at the same time
whether Parts II–IV want figures they currently do without — the depth census, the survival
curve and the live-versus-model comparisons are all natural candidates and none is drawn.
**One more joined the list on 2026-07-29:** II-7's (σ, μ) plane, where both stability boundaries
are curves rather than points and the band between them — lot count stationary, capital integral
divergent — is visible as an area. `sensitivity()` prints it as a text grid; it wants to be drawn.

**INF-5. Every quoted number gets a formula, a runnable script and a footnote.** The
infrastructure landed 2026-07-30 — `code/examples/` with a harness, 19 modules covering all 46
numbered formulas, 96 frozen cases, a generated appendix (`sections/99-reproduction.md`), eleven
compositions promoted into `model.py`, and a coverage test wired into `verify_examples.py` that
asserts every displayed `{#eq:...}` has a registered example, every example is cited from the
prose, and every footnote names the script that actually backs its formula. The write-up, the
design decision behind it (a `Case` *is* a command line) and the three prose errors it surfaced
are in [`DONE.md`](DONE.md). **Two items of follow-up remain.**

- **Five lower-value formula gaps**, all of them numbers quoted without a displayed formula: the
  census moments (§08's mean depth 38% and weighted q 0.066), the cost-basis capital of §09
  (18.23, where `eq:capital` gives market value only), the volatility-premium slope ("about 45
  basis points" per point, a finite difference over the sweep), the sticky-dividend fixed point
  (§09:151, described in prose but never displayed), and x\* = ln(1 + ν/δ) (§09, displayed inline
  but unnumbered). Each is backed by a script and a footnote already; what is missing is only the
  display in the prose.
- **§00's anchor registry has drifted from the sections, and the coverage test cannot see it**
  (found 2026-07-30, during the TODO cleanup; halved the same day). `sections/00-notation.md`
  Conventions is declared the single source of truth for anchors, and it **omits** `eq:screen-gap`
  (05), `eq:little-finite` (08), `eq:mark-loss` and `eq:giveaway` (09) — the four formulas INF-5
  itself added. It was also wrong in the other direction, listing `eq:account-criterion` under §10
  where no section displayed it; **II-12 displayed it on 2026-07-30**, so that half is closed and
  the registry is now only incomplete rather than also false. `coverage()` reads
  `declared_anchors()` off the displays themselves, so a registry that disagrees with them is
  invisible to it. Fix the list, and add the missing guard: parse §00's registry and assert it
  matches the displayed set exactly, per section. That closes the one remaining way a numbered
  formula can be promised and not exist — and it is the guard that would have caught
  `eq:account-criterion` sitting promised-but-absent for a day.

**INF-6. The example harness overrides `cadence`, so any `--tau-p` case is silently wrong.**
(Found 2026-07-31, while running II-19's cadence test.)

`build_parser` in `code/examples/_harness.py` takes each flag's default from a **post-init**
reference `Config()`. By then `__post_init__` has already resolved `cadence` from `None` to
`tau_p`, so the parser's default for `--cadence` is 1/52 and every CLI-built Config passes it
explicitly — the `if self.cadence is None` branch never fires. Passing `--tau-p 0.08333`
therefore builds a book that **sells a monthly put every week**: 52 arrivals a year instead of
12, and `returns_benchmark.py` reports **+1.74%** excess against the correct **+1.56%**.

**Nothing is wrong today and the trap is live.** `cadence` is the only field whose declared
default differs from its post-init value, and no existing Case varies `--tau-p` or `--cadence`,
so **no frozen number is currently affected**. It bites the first time someone adds one, which is
exactly what II-19 does.

**The fix is one line**: take each default from the dataclass field, `default=f.default`, rather
than `getattr(ref, f.name)`. Every other init field's declared default already equals its
post-init value, so nothing else moves and `ref` becomes unused. Add a case that varies `--tau-p`
and asserts the arrival rate, so the trap cannot reopen.

**INF-7. Pin the live-figure window before release.** (Raised 2026-08-01, when tranche 3
arrived; deferred to release by the operator, who wants the figures tracking the data until
then.)

Every script that reads the statements derives its own window from the data — `live_ledger.main`
takes `end = max(close dates)`, and `model_vs_live`, `selection_fit` and `iv_panel` follow it.
None of them has a cutoff. So **dropping a file into `statements/` silently restates every live
figure the article quotes**, in §02, §05, §07, §09 and §15, with nothing recording which window
a sentence was measured on. That is INF-2's "no check reproduces the live-account figures at
all", arriving as a fact rather than a risk: the 2026-08-01 refresh moved seven prose figures
and every bullet of IV-1 and IV-2.

The fix is an as-of cut applied at read time in `analyze_statement._read_rows`, so every
consumer inherits it, plus `--as-of` on each script. Cutting on the **posting** date reproduces
an earlier corpus exactly — verified 2026-08-01, where the pre-tranche cut reproduced the whole
of the previous ledger, T1's 71.5/90.3 pair and the 27.4%/8.0% bucket to the digit. At release,
freeze the default at whatever date the article is measured on and print the window in the
banner, so a later tranche cannot restate a published number without someone typing the flag.
