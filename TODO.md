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
to a reader and should be added only when the text genuinely defers something. Thirteen live in
`sections/98-bibliography.md` (recounted 2026-08-04, after the queueing reads), in the internal
field after an entry's anchor, which is stripped at assembly and so never reaches a reader; they
mark the two unread downloads, the one source that may be cited for its existence only, and the
ten entries the reading of 2026-08-04 left owing something to I-7, II-22, II-23, II-29, II-30 or
IV-9. The bibliography stands at **43 entries**, five of them added that day.

## Where things stand

Thirteen of the seventeen planned section files exist, plus two appendices: the bibliography
(`sections/98-bibliography.md`, hand-maintained, the only file that may declare a `{#ref:}`
anchor) and the generated reproduction table (`sections/99-reproduction.md`, produced by
`python -m examples --appendix`, never edited by hand). Part I is written bar two stubs; **Part II is written, with thirteen items outstanding**
(II-18 through II-30 — nine from the literature pass of 2026-07-31, which reopened Part II the
day it closed, two more from the Merton–Scholes–Gladstein read of 2026-08-01 that closed I-5, and
two from the reads of 2026-08-04, Chang–Peres and Little; none of them changes a formula or a
verdict, only II-29 moves a number and only II-30 adds one); **Part III and Part IV are unwritten**, and between
them they are still the bulk of what is left besides those stubs and the assembly work.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · 11 constrained | written; **thirteen open items** (II-18 – II-30) — six in §09, the rest in §05, §07, §08 and §10; II-23 also touches §00, §02 and §11, and II-29 §00 and `code/` |
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

  **Checked against the copy on 2026-08-04, and it is worse than recorded — which is the good
  news.** [Little (2011)](#ref:little-2011) §3.2.2 does not merely offer a portfolio as an
  illustration of the weighting; it names the entire four-quantity assembly this article is built
  out of: in the financial-assets example "we would know not only the time average dollar return H
  and average dollar return per asset G, but also the average number of assets L and the average
  time of holding an asset, W". That is §08 and §09 in one sentence, published in 2011. His
  closing section then leaves it unclaimed — H = λG "seems full of potential … The applications
  await someone's imagination" (§4.3.2).

  **So §03 writes this as leverage, not as a concession.** The prohibition stands and is
  unchanged: no novelty may be claimed for the identity, and §08 must not imply otherwise (II-22's
  second caution). But the tone that follows from these two quotes is not defensive. The article
  is carrying out an application the field's own authority proposed and left open, on machinery
  fifty years of queueing theory has already stress-tested — which is *why* the results can be
  trusted without a new limit theorem behind them, and is a better sentence than any claim of
  priority would have been. What the article supplies is what Little could not: the specific W
  (a depth process and a first passage) and the specific weighting (the census). **Both quotes are
  short enough to use verbatim** and they are the cleanest way to make the point.
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

**I-7. Bibliography entries carrying details nobody has checked against a copy — eight cleared,
five open.** (From building `sections/98-bibliography.md`, 2026-08-01; recounted 2026-08-04, three
times.)

Every entry the pass supplied came with its bibliographic details; the ones added to cover what
the sections were already citing informally did not, and were reconstructed rather than read off
a copy. Ten were tagged **[cite unverified]**, and `python -m examples --references` lists
whatever carries the tag every run.

**Eight are cleared**, by obtaining copies and reading the details off them: black-scholes-1973,
hull (2021 → **2022**, and it is the Global Edition), little-1961, merton-1973, ross-first-course
(**2018**, 10th ed.), ross-probability-models (**2010**, 10th ed.), chang-peres-1997 and
chernoff-1965. The last two were both cleared on 2026-08-04 and **both had a wrong title and
nothing else wrong** — which is the strongest evidence this item has produced for its own closing
sentence. Chang & Peres carried a serial comma the paper does not have ("Gaussian Random Walks,
and the Riemann"); authors, year, volume, issue and pages were all correct. Chernoff was carried as
"Sequential **Test** for the Mean…", singular, against the printed "Sequential **Tests** for the
Mean of a Normal Distribution IV (Discrete Case)"; journal and pages read off the scan agree, and
volume and year are settled from inside the copy by his own reference [4] — part III of the same
series, *Ann. Math. Statist.* **36** 28–54, 1965, the article immediately preceding this one in the
same volume.

**Five are open, and two of them are new to the list rather than left over from it.**

- **israelov-covering-the-world** and **li-zhang** are downloaded but unread, and a title or
  author list is the guessed part in both. The reads are owed by **I-1** and **II-23**; clearing
  the citation falls out of doing them.
- **siegmund-1985** has no copy. Chang & Peres's reference list corroborates title, publisher and
  city — better than memory, not a copy; the edition and printing are unchecked.
- **siegmund-1979** was **never tagged, and was wrong in exactly the way this item says matters
  most**: the title had been silently truncated to "Corrected Diffusion Approximations" for
  "Corrected diffusion approximations in certain random walk problems". Completed, with pages
  701–719, from Chang & Peres's reference list — and now *tagged*, because that is not a copy
  either.
- **janssen-vanleeuwaarden-2007** is the newest, tagged 2026-08-04 **by having been read in full**.
  The copy is the authors' own typescript — `paperGRWdiffstyleFinal.dvi`, dvips, March 2007 — with
  no journal header, no volume, no pages and no DOI, so "*Annals of Applied Probability* 17(2)"
  came from the pass and the page range was never there at all. Nothing else about the entry
  moved; the read raised it to **[F]**. **This is the item's sharpest instance yet: reading a
  source cover to cover does not verify its citation, and can be the thing that reveals the
  citation was never verified.** The two are independent checks and the F/P/A ladder does not
  imply the other one.

The printed count therefore went 10 → 3 → 5 → 6 → 5. Every rise was this item working rather than
regressing, and the one fall is the first entry it has *closed* since 2026-08-01.

**One entry was born clear**, and it is the standard the other five are being held to:
`glynn-whitt-1989` was added on 2026-08-04 *after* its copy had been obtained and read, with every
field taken off the JSTOR cover page and the article header. It is the first entry in the
bibliography that never needed the tag, and the first added in that order. The 40th entry costs
this item nothing, which is the argument for obtaining a copy before writing an entry rather than
after.

**A fourth reference list, and it is wrong about the one paper we now hold.** (2026-08-04, from
[Glynn & Whitt (1989)](#ref:glynn-whitt-1989-extensions), read in full the same day.) Their list gives
Little's paper as "A Proof **of** the **Queueing** Formula: L = λW" — two departures from the copy
in front of us, which prints "A PROOF FOR THE QUEUING FORMULA". Everything else in their list that
we can check is right, including Brumelle and Heyman & Stidham, whose details agree with Little's
own list field for field. This instance is the cleanest of the four sampled lists, because we hold
the disputed paper and can simply look. Little's own list, by contrast, was right about Glynn &
Whitt on every field: title, journal, volume, issue and pages.

**Correction, the same day: "volumes have never been wrong" lasted about an hour.** This item
carried, until the Whitt and Glynn–Whitt copies arrived, the generalisation that across the
sampled lists *titles* keep being wrong while volumes, issues and page ranges never had been.
**Glynn & Whitt's list breaks it**, and in the least forgivable place: their citation of *their own
earlier paper* gives "Queueing Syst. Theory Appl. **1**, 191-215", where the copy's page header
reads **Queueing Systems 2 (1986) 191–215**. Pages right, volume wrong, in a self-citation. So the
tally is now five lists, with **titles wrong in three and a volume wrong in one**, and the
generalisation that survives is only the weak one this item started with: *a reference list is a
source with its own error rate, and no field is exempt*. Authors are not more reliable about their
own work — [Little's](#ref:little-1961) own 2011 list is so far the only one with nothing wrong in
it, and that is a sample of one.

**The converse of the Janssen instance arrived the same day, and the count did not move for it.**
Both Little papers were read in full on 2026-08-04. `little-1961` was already among the eight
cleared and had never been tagged; the read confirmed it from inside the copy — title and pages
off the printed article, the journal off its own INFORMS copyright page — and identified the one
field that is *not* from a copy: volume and issue, 9(3), which come from Little's own 2011
reference list. That is the best corroboration this item will ever be offered, an author citing
his own paper, and it is still a reference list. `little-2011` was never tagged either, and needed
nothing: every field is printed on its p. 536 along with the DOI. **So the two independent checks
can pass in either order.** Janssen showed a full read revealing that the citation had never been
verified; Little shows a citation cleared *before* the read and confirmed by it. Neither implies
the other, which is the whole of what this item is about.

**A second reference list is not a second opinion.** Janssen & van Leeuwaarden's list was read on
2026-08-04 and it corroborated chernoff-1965 outright (journal, volume, pages) — but it
**transposes the titles of siegmund-1979 and siegmund-1985**, giving the 1979 *Adv. Appl. Prob.*
paper the book's title and the 1985 Springer book the paper's, while its own body text cites the
two correctly. Both entries above are unchanged, because Chang & Peres and Janssen & van
Leeuwaarden's *usage* agree and only the latter's list dissents. The lesson for the remaining
clearing work: a reference list is a source with its own error rate, and two of them agreeing on
details while disagreeing on which title belongs to which work is exactly the failure a copy
would settle in one look.

**And the copy, obtained the same day, settled it in one look — the other way.** Both lists were
right about chernoff-1965 on every field they carried, and the entry was wrong anyway, on the one
field neither list had been asked about because it had been *paraphrased* rather than copied. So
the two failure modes are independent: corroborating lists catch a field taken from the wrong
place, and only a copy catches a field taken from the right place and mistyped. **Two lists
agreeing is evidence about the fields they agree on and about nothing else.**

**The lesson is that the tag list was not the risk surface.** The one entry actually misleading a
reader carried no tag, because it came from the pass rather than from memory and so was never
suspected. Before assembly every entry needs a copy or a named corroborating source, tagged or
not.

**Titles are the part to check first, and three for three now says so.** Every entry whose details
were put against a source on 2026-08-04 — chang-peres-1997 and chernoff-1965 against copies,
siegmund-1979 against two reference lists — turned out wrong in its title and right in everything
else. Three different corruptions of the same field: a truncation, a spurious comma, a singular
for a plural. Numbers get copied because they look like data; titles get retyped because they look
like prose.

**This is still a smaller worry than the read-level rule and a different one.** Four of the five
are pointers for further reading and the article quotes no figure from any of them. The one number
that looked like an exception — β = 0.5826, attributed in §07 to siegmund-1979 — now rests on
**two [F] sources**: chang-peres-1997 prints it to seven digits, and chernoff-1965 supplies an
independent representation, Corollary 1(b)'s Wiener–Hopf integral, which evaluates to the same
−0.5825972. (The value *printed* beside that integral is −0.5824; the discrepancy is his
arithmetic and II-23 carries it.) Broadie–Glasserman–Kou carries the constant too. A reader
following a wrong page range loses nothing but time; a reader following a wrong *title* is being
misled.

**janssen-vanleeuwaarden-2007 is the fifth and it is not in that class**, because II-29 may put
one of its figures in §07 — the 0.033838 zero-depth limit of [eq:trapped](#eq:trapped). The read
level supports that (**[F]**, and the theorem was reproduced against its own Spitzer counterpart
before it was quoted); the *citation* does not yet, and it is the only open entry where clearing
the tag is on the critical path of a section edit rather than of assembly. Do it when II-29 is
written, not after.

**Deadline is assembly**, not §03: a bibliography goes out with the article, and this is the last
thing that should be discovered in proof. Clearing an entry means deleting its `[cite unverified]`
tag, which drops the count the checker prints.

## Part II — One asset

Part II closed on 2026-07-31, was reopened the same day by the literature pass, and has been
reopened three times since by reading the sources that pass had only listed. **Thirteen items are
open**, they divide in three, and **none of them changes a formula or a verdict** — II-29 is the
only one that moves a number at all, and II-30 the only one that adds one.

**Six land in §09**, and IV-5 edits it a seventh time, so read them together before touching the
section. Two are corrections to what the section already says — **II-18** the level of the
volatility premium, **II-19** its missing tenor axis — two are additions the section never
attempted: **II-20** the first risk statistic anywhere in the article, and **II-21** the detour
that keeps II-20 from being read as a comparison it is not — **II-26** is the citations §09
owes for results it argues out unaided, and **II-27** the two published precedents for its 45 bp
slope. II-19 and II-20 add frozen cases; neither adds model machinery beyond what `model.py`
already has.

**Four came from the pass's harvest** (and **II-26** from its cross-check, in the sweep that
closed the conversion), converted 2026-08-01, and none of them moves a number anywhere:
**II-22** replaces §08's hand-derived census integrals with the theorem they are
instances of, and hands §10 a cleaner statement of its own capital criterion; **II-23** cites seven
borrowed things where the reader meets them, and reaches outside Part II to do it (§00, §02, §11);
**II-24** gives §08's census its second analogy; **II-25** puts a size behind §05's early-exercise
caveat. All four depend on §03 (**I-1**) for the citations themselves — **§03 carries the
pedigree, the section carries the pointer**, and neither should be written twice.

**Four came from actually reading what the pass had only listed at [A] or [P]**, and they are the
ones carrying measurements: **II-27** and **II-28** from Merton–Scholes–Gladstein (2026-08-01),
**II-29** from Chang & Peres, then Janssen & van Leeuwaarden, then Chernoff, and **II-30** from
Little's own two papers (all 2026-08-04). II-27 and II-28 land in §09 and §05 and move nothing.
**II-29 lands in §07 and moves two figures** — the trapped fraction from 4.1% to 4.4%, the grid
tax's multiple from 2.1× to 2.4× — because the constant β is a far-barrier limit and §07 applies
it at 0.28 of one step. It also corrects the pedigree in II-23's first bullet, so **read the two
together**. **II-30 lands in §08**, adds one figure the section never had, and corrects what the
article says a source assumes rather than what it computes.

**Every read that has promoted a source off [A] or [P] so far has found the record wrong in some
way that mattered** — four of four now — **but the fourth moved where the wrongness lives**. Chang
& Peres, Chernoff and Janssen & van Leeuwaarden each turned up a defective bibliography entry;
Little's two entries were clean, and what the read caught instead was §08's prose crediting the
1961 paper with a freedom from assumptions that paper does not have. The record being checked is
the article as much as the bibliography, and only one of the two has a checker. That is the
argument for doing the ones still owed.

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
in Little's own 50th-anniversary paper ([2011](#ref:little-2011), §3.2.2) **[F] since 2026-08-04**
— says that for **any** weighting f<sub>i</sub>(t) applied over each item's time in the system, the
time-average H equals λ times the per-item total G. L = λW is the case f ≡ 1.

**The statement in full, off the copy** (2011 §3.2.1), because the hypotheses are the half of it
this item cares about. For each item i take f<sub>i</sub>(t) with ∫|f<sub>i</sub>| dt < ∞ and
f<sub>i</sub> = 0 outside [t<sub>i</sub>, t<sub>i</sub> + l<sub>i</sub>] for some finite
l<sub>i</sub> > 0 — usually l<sub>i</sub> = W<sub>i</sub>, the item's own time in the system.
Set G<sub>i</sub> = ∫f<sub>i</sub>, H(t) = Σ<sub>i</sub> f<sub>i</sub>(t), and let G and H be the
long-run averages of the G<sub>i</sub> and of H(t). **Then: if λ and G exist and are finite, and
the technical condition l<sub>i</sub>/t<sub>i</sub> → 0 holds, H exists and H = λG.** Two things
follow for us and both are gains, not obstacles — see the §10 paragraph below for the first, and
§08 does not need the second, because [eq:little-finite](#eq:little-finite) turns out not to be a
limit statement at all (**II-30**).

**Whose theorem, exactly.** Little credits it to **Brumelle, S. (1971). On the relation between
customer and time averages in queues. *J. Appl. Probab.* 8:508–520** and **Heyman, D. P. &
Stidham, S. Jr. (1980). The relation between customer and time averages in queues. *Oper. Res.*
28(4):983–994** — details from his reference list and **not from copies**, so an entry built from
them ships tagged under I-7 until someone opens the papers. Neither is in
`sections/98-bibliography.md` yet, and neither should be until §08 cites it.

**The lump-cost extension is not an aside, it is which citation our income needs — and the copy is
now read.** A weighting that is a *rate* over the lot's life — the basis e^x, the dividend on
market value — is Brumelle's f<sub>i</sub>(t) directly. The call premium and the call-away
giveaway are not: they are point flows at period ends, and `model.py` already treats the giveaway
that way (`economics()` gives `exitcost` its own weights, "a point flow at the end of period j, not
an occupancy"). A sum of point masses is not a function with ∫|f| dt < ∞, so the theorem as Little
states it does not literally cover them. **[Glynn & Whitt (1989)](#ref:glynn-whitt-1989-extensions) [F]** is
the reference that does, read 2026-08-04, and it is a better fit than the second-hand description
suggested:

- **§1.4 is our case, named.** "Lump Costs Plus Cost Rate" — a cost rate over the customer's stay
  *plus* a lump incurred at an instant — and the authors state that this example "is not covered by
  any of the previous versions of H = λG because F<sub>k</sub>(t) … is not absolutely continuous
  with respect to the Lebesgue measure". That is our premium and our giveaway beside our basis and
  dividends, in one weighting.
- **§1.5 is the sharper fit still**, and it is the one to cite if only one is: a general cumulative
  cost process C<sub>k</sub>(t) accrued while customer k is in the system, with their Example 1 —
  shoppers whose purchases accumulate as they shop — noting that the exit time and the accumulated
  cost "might be highly dependent". Ours are *maximally* dependent: the same depth path decides
  both what a lot earns and when it leaves. The theorem does not care, and that is worth one clause
  in §08, because a reader's instinct is that such dependence must break something.
- **One condition covers all four weightings.** §4.3: for both nonintegral formulations, conditions
  (17) and (18) hold as soon as **W<sub>n</sub>/T<sub>n</sub> → 0**. That is the same
  residence-does-not-grow condition as Little's l<sub>i</sub>/t<sub>i</sub> → 0 above. So the honest
  summary for the detour is one sentence: *rates and lumps alike are covered, under the single
  condition that holding times do not grow with the book's age* — which is E[W] < ∞ in practice,
  and is §10's first boundary again.
- **Do not overstate the gap, because they do not.** Their Remark 1 says the lump form can be
  transformed into the integral form by a change of variables, so this "should not be
  overemphasize[d]" — what is gained is that the analysis is not "significantly complicate[d]".
  Cite Glynn & Whitt for the weighting we actually use; do not build a paragraph out of the fact
  that Brumelle's statement is narrower.

**And §4.2 hands §10 something the narrower statement cannot.** In the plain H = λG of Heyman &
Stidham, G < ∞ is a hypothesis. Glynn & Whitt drop it — "in contrast to Theorem 1 of Heyman and
Stidham, we do not require that G < ∞ or ∫₀^∞ f<sub>k</sub>(t) dt < ∞" (checked against the page
image, not the OCR). So the divergent regime is inside their theorem rather than outside it: with
W finite and G infinite at f = e^x, their Theorem 4a(i) gives H = ∞ as a *conclusion*. §10's
capital boundary is then a result of the same theorem that produces the income, not a place where
the theorem stops. Verify the exact route through Theorem 4 when §10 is actually written — the
statement above is read off the hypotheses, not reproduced.

**Cite [Whitt (1991)](#ref:whitt-1991) theorem 6.3, not the original.** (Added 2026-08-04 on
reading the review **[F]**.) Whitt restates the Glynn–Whitt extension in the elementary framework
of his §2, and the result is the version §08 should carry, because a general-audience detour can
state it in two lines. Let A<sub>k</sub> and D<sub>k</sub> be the kth item's arrival and departure,
and let F<sub>k</sub>(t) be **any** nondecreasing cumulative cost for item k. Suppose

- **(6.1)** k⁻¹A<sub>k</sub> → λ⁻¹ *and* k⁻¹D<sub>k</sub> → λ⁻¹ — arrivals and departures share
  one limiting rate; and
- **(6.8)** F<sub>k</sub>(t) = 0 before A<sub>k</sub> and F<sub>k</sub>(t) = F<sub>k</sub>(D<sub>k</sub>)
  after D<sub>k</sub> — cost accrues only while the item is in the system.

**Then G<sub>k</sub> → G if and only if H<sub>t</sub> → H, and H = λG.**

Three reasons that is the better citation. It is an **iff**, which the caution above hedged
against and no longer needs to: under (6.1) and (6.8) the per-lot total converges exactly when the
time-average does, so §10's "capital returns iff G is finite at f = e^x" is the theorem's own
biconditional rather than our inference from its hypotheses. Its (6.1) is **§08's own
self-recycling sentence** — 10.4 lots in, 10.4 out — so the article has already told the reader
the condition before it needs it, and the *transient* is exactly the regime where the two rates
have not yet met. And "any nondecreasing cumulative cost" covers rates, lumps and mixtures in one
clause, with no measure-theoretic aside about absolute continuity.

**One caution from the review's remark 6.2.** Decomposing G into its rate part and its lump part,
"it is possible for H<sub>t</sub> → H without having the two components converge". Ours both
converge, but a detour that presents the decomposition as if convergence were componentwise would
be asserting more than the theorem gives. Whitt's **theorem 6.4** (Y = λX, "a sample path version
of the renewal reward theorem") is the companion worth knowing about: t⁻¹Y(t) → Y iff
k⁻¹Y(A<sub>k</sub>) → X, and then Y = λX.

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

**And the copy makes that gain sharper than the item first claimed** (2026-08-04). Those are not
two conditions the article imposes on the theorem from outside; they are **the theorem's own
hypotheses**, read back. H = λG asks for λ and G finite, plus l<sub>i</sub>/t<sub>i</sub> → 0 —
residence times that do not grow with the index, which is what E[W] < ∞ delivers. So §10's two
boundaries are the two ways the identity's preconditions can fail: below μ − δ = σ²/2 the
holding times themselves diverge and the count law goes with them; between σ²/2 and σ² the count
law survives and G at f = e^x is what diverges. **The stability section is the failure analysis of
the inventory section's theorem**, which is a cleaner joint than "two integrals, two convergence
conditions". ~~Do not overstate it into an iff~~ — **that hedge is withdrawn**: Whitt's theorem
6.3, below, *is* an iff under conditions §08 has already stated, so the equivalence can be written
plainly.

**Two cautions.** (There were three. The first is withdrawn — see II-30.)

- **Do not claim novelty** — N3, and **I-1** carries the prohibition. Little's own worked example
  of a non-trivial weight is "the dollar rate of return on the ith asset in a portfolio of
  assets", and the 2011 copy is more explicit still: he names H, G, L and W together for a
  portfolio of assets and leaves the application open. §08 must not contradict what §03 is
  required to concede — but I-1 now also says how to write it, which is as leverage rather than as
  an apology, so this caution costs the section no confidence.
- **One detour, not two.** The value here is that a single detour covers the income and the
  capital results together, where the article currently justifies them separately. If it becomes
  two detours it has not paid for itself and the hand-derivation was better.

**Incidental, and not a defect in `code/`.** Re-integrating a *re-binned* census misprices the
steep weightings badly: call income read off 0.01-wide bins from an h = 0.02 walk comes out **15%
low**, while E[I] on the same bins is exact, because the call premium does nearly all its work in
the few cells nearest x = 0. Nothing in `code/` does this — `depth_census()` accumulates mean
depth and weighted q on the cells and only the printed table is binned — but §08's table invites a
reader to try it, and any check ever written against that table has to match bin width to h.

**II-23. Seven borrowed things, none of them cited where the reader meets it.** (Harvest H2, H3
and H9 of [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), converted
2026-08-01; **extended the same day** with cross-check rows 2 and 13 and Israelov & Nielsen's
Myth 8, which the harvest did not claim and no other item carries; a seventh added 2026-08-04
from Little's 1961 copy.)

Seven edits of a sentence or a clause each. No number moves and no formula changes — that is the
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
  barrier, their framing is closer to what we do than Siegmund's sequential-analysis one, and the
  paper carries an order of magnitude more citations in finance.

  **The pedigree this bullet first gave is wrong, corrected 2026-08-04 by reading
  [Chang & Peres](#ref:chang-peres-1997) in full.** Siegmund is not the origin. The constant and
  the shift are **[Chernoff (1965)](#ref:chernoff-1965)**, who showed that the optimal boundary
  for a diffusion observed only at 0, δ, 2δ, … stands ẑ·√δ away from the continuous one with
  ẑ = −β; the closed form −ζ(½)/√(2π) was supplied to him by Gordon Latta, and Hogan (1986)
  identified ẑ with the limiting expected overshoot. Siegmund (1979) is the corrected diffusion
  approximation built on that, and Hardy (1905) did the analysis the expansion rests on. So:
  **Chernoff (1965) as the origin, Siegmund (1979) as the approximation, BGK (1997) as the use we
  are making of it, Chang & Peres (1997) [F] for the expansion.**

  **Checked against Chernoff's own copy the same day, and the pedigree survives verbatim** — his
  (1.1) is the ẑ·√δ displacement, his Summary names Latta, and his §1 is explicit that the
  observation times are t₀, t₀ + δ, t₀ + 2δ, …. **Two refinements, both worth carrying into the
  prose.**

  *The −0.5824 is an arithmetic slip, not a rival constant, and that changes what to tell a
  reader.* Chernoff prints −.5824 twice — in the Summary and in Corollary 1(b) — but the object
  printed is Latta's ζ(½)/√(2π), which is −0.5825972, and Corollary 1(b)'s own Wiener–Hopf integral
  **−(1/2π)∫λ⁻² log[λ²/2(1−e^(−λ²/2))] dλ evaluates to −0.582597157939**, agreeing with the closed
  form to 25 digits (checked while reading). So the origin paper and §07 hold the *same* constant
  and differ only in a fourth-decimal evaluation. Still quote 0.5826 and still cite Chang & Peres
  for the digits, but the footnote a careful reader deserves is "the value printed there is the
  same number, rounded wrongly", not "the sources disagree".

  *He did not know it was an overshoot, and that is the better story.* The constant reached him as
  a **Spitzer–Wiener–Hopf integral** (his refs [6], [7] — Spitzer, *Duke Math. J.* 24:327–343 and
  27:363–372), Latta recognised the integral as a zeta value, and Hogan identified it as a mean
  overshoot **twenty-one years later**. So II-29's "what β *is*" sentence is not Chernoff's
  reading of his own number: it was computed before anyone knew what it measured. One clause of
  that in §07's detour is the kind of thing a general audience remembers, and it costs nothing.

  **One caution the copy adds: his object is not a barrier.** Chernoff is displacing the
  *Bayes-optimal stopping boundary* of a sequential test, not the knock-out level of a
  discretely-monitored option — the √δ displacement is shared, the problem is not. §07 should say
  the constant and the √δ shift *first appear* there, not that he solved our problem; BGK is still
  the citation for the use we make of it. His Theorem 5.1 also carries a uniformity restriction —
  the shift is asymptotic in δ and uniform only for t in an interval bounded away from 0 and ∞ —
  which is a *different* limit from the one that actually bites us. **His framing has no
  barrier-distance axis in it at all**, so it cannot see the b → ∞ problem II-29 raises, and
  Chang & Peres remains the only source for the size of that error.

  **The error statement is II-29, not this bullet, and the axis guessed at here is the wrong
  one.** "Asymptotic in the monitoring frequency" is the one axis on which the article is safe:
  in the Gaussian case the expansion in drift-per-step *converges* out to |θ| < 2√π and we sit at
  θ = 0.035. What is asymptotic is the *barrier distance*, where the article sits at 0.28 of one
  period's step, and two of §07's numbers are low because of it.
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
- **[eq:lambda-eff](#eq:lambda-eff) is Little's own handling of blocked arrivals, and §11 presents
  it as our inversion.** (Added 2026-08-04 from [Little (1961)](#ref:little-1961) **[F]**, p. 387.)
  §11 says Little's law "runs the other way" when capacity binds, which reads as an improvisation
  on a law that was not built for it. It was: the origin paper's Discussion takes up exactly the
  case where "arrivals come with rate λ but not all arrivals join the system", says flatly that
  L = λW then "does not hold", and gives the two repairs — redefine λ "to include only those
  arrivals that join the system", or give the refused ones a zero waiting time and keep them in W.
  **§11 does the first**, and a clause saying so converts the section's most useful idea from a
  liberty into a citation. The same page also leaves "what constitutes the 'system'" deliberately
  flexible, requiring only "consistency of meaning" across *number in the system*, *time spent in
  the system* and *arrival to the system* — which is the licence for calling a warehouse of stock
  a queue, and belongs beside §08's detour rather than here.

  **Cite the definition and nothing further.** Little's remark makes λ_eff the right *bookkeeping*;
  it says nothing about whether E[W] survives the blocking unchanged, which is the assumption
  [eq:lambda-eff](#eq:lambda-eff) actually rests on and which §11 measures itself (the thinning
  table, under 1% on everything count-like). Do not let the citation appear to underwrite the
  approximation — the measurement is the better evidence and it is already there.

  **The direction §11 runs the law is the one that is not automatic, and someone proved what it
  costs.** (Added 2026-08-04 from [Glynn & Whitt (1989)](#ref:glynn-whitt-1989-extensions) **[F]** §4.1.)
  Every standard statement of Little's law runs λ and W to L; §11 runs the other way, and Glynn &
  Whitt open by saying that reverse implication is their own contribution — "all previous versions
  show that the existence of limits for λ and W imply the existence of a limit for L. We show how
  to go the other way". Their **Theorem 5** is the price: from the time averages alone you get an
  *inequality*, lim sup of the customer-average wait ≤ λ⁻¹L, and equality needs one of two extra
  conditions — that the system **empties infinitely often**, or that W<sub>n</sub>/n → 0. Their
  Remark 6 exhibits a case where the inequality is strict, 2 > 1, so this is not a technicality.

  **What §11 should take from it is one clause, not a derivation.** The wheel does empty
  infinitely often — that is [the inventory section](#sec:inventory)'s own arrivals-equal-departures
  picture, and on one name P(I = 0) ≈ 14% — so the inversion is legitimate, and it is legitimate
  for a *stated reason* rather than by symmetry of an equals sign. Sequence with the bullet above:
  Little supplies the bookkeeping for refused arrivals, Glynn & Whitt supplies the licence to read
  the identity backwards, and §11's thinning table remains the evidence for the modelling
  assumption neither of them addresses.

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
BGK is **[F]**, Israelov & Nielsen is **[F]**, and Chang & Peres and **chernoff-1965** are both
**[F]** since 2026-08-04 — the latter was judged desirable and not owed, since it is cited for
priority alone, and reading it anyway repaid the hour with a wrong title, a settled −0.5824 and
the two refinements above. The remaining **two [A]** sources are cited for the existence of a
result rather than for a figure, which is what **I-1**'s read-level rule permits.

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

**II-29. β is a far-barrier constant, the article applies it at 0.28 of one step, and two of §07's
numbers are low because of it.** (From reading [Chang & Peres](#ref:chang-peres-1997) in full,
2026-08-04 — II-23 had it listed as a pointer for higher-order terms, and it turned out to carry
the meaning of the constant and the size of the error as well. **Extended the same day from
[Janssen & van Leeuwaarden](#ref:janssen-vanleeuwaarden-2007)** — parts Seventh to Twelfth, which
name eq:trapped's object, give one value of it in closed form, and add a third confirming route —
**and again from [Chernoff](#ref:chernoff-1965)**, parts Thirteenth to Fifteenth, which date the
constant's meaning, confirm its digits by a fourth route and rule the origin paper out as a source
of a sharper error bound.
Everything below was measured while raising the item and **outside the model**: the trapped
fraction by three independent routes that agree, the overshoot by a Monte Carlo whose implied
E[W] reproduces §07's own 2.10. Nothing in `code/` computes any of it yet.)

**First, what β *is*, which the article never says.** §00's symbol table calls β "Siegmund's
overshoot constant" and §07 calls [eq:siegmund](#eq:siegmund) "a classical correction"; neither
says overshoot *of what*, so the reader is asked to accept 0.5826 on authority. It is the
**limiting expected overshoot** of a Gaussian random walk — E₀R_∞ = E₀(S_τ²)/(2·E₀S_τ), the mean
amount by which the walk stands *past* a level when first observed beyond it, in units of one
period's step σ·√τ_c. That is the right general-audience account of the call-grid tax and it is
one sentence: the grid does not merely delay a lot's exit, it *records the exit late*, and a
barrier crossed between two expiries behaves as though it sat 0.58 steps deeper. The paper's
companion constant is the other end of the same story — **E₀S_τ = 1/√2 = 0.7071**, the mean first
ladder height, which is the overshoot of a barrier the walk starts on.

**Second, the limit is in the wrong place for us.** β is the b → ∞ value, and the barrier
distance the article actually applies it at is

    b  =  E[x₀] / (σ·√τ_c)  =  0.5582/√n  =  **0.279 step sds** at n = 4

— **independent of σ**, because E[x₀] and the step both scale with it. In the Conservative regime
it is 0.237, which is *further* inside the small-b region rather than further out. Chang & Peres's
Corollary 3.1 states its error as O(e^(−rb)) *as b → ∞*, so the article stands where that term is
largest, and **b ∝ 1/√n means it gets worse as calls outrun puts** — the same lever that creates
the tax in the first place.

**Third, the good news: the drift axis is free**, which is where II-23 guessed the error was. In
the Gaussian case the expansion in drift-per-step is a *convergent* series for |θ| < 2√π = 3.545
(Theorem 1.1), where θ = (ν/σ)·√τ_c = **0.0347** at the running parameters. Its first drift
coefficient is ρ′(0) = ¼, so the drift correction to the shift is exactly **ν·τ_c/4 — a quarter of
one call period's drift**, worth +0.00048 on a tax of 0.0323 (+1.5%), and the next term
(ρ″(0) = ζ(3/2)/(2(2π)^(3/2)) = 0.08293) is four orders of magnitude smaller. Cadence is not the
problem; barrier distance is.

**Fourth, [eq:holding-siegmund](#eq:holding-siegmund) is not an approximation at all — it is an
identity with the wrong constant in it.** Wald's identity gives

    E[W]  =  ( E[x₀] + E[overshoot] ) / ν      exactly,

so §07's "lands 9% below the exact 2.10" is *entirely* the constant and nothing else. The measured
mean exit overshoot is **0.669 ± 0.001 step sds** against β's 0.583, and Chang & Peres bracket it
from both ends:

| overshoot constant | value at the running example | E[W] it gives |
|---|---|---|
| ρ(θ) = β + θ/4 + …, the b → ∞ end | 0.5913 | 1.93 y |
| **measured, at b = 0.279** | **0.669** | **2.10 y** |
| E_θS_τ = (1/√2)·e^(βθ), the b → 0 end | 0.7215 | 2.22 y |

The exact 2.104 sits inside a bracket whose two ends are both published constants — and the
measured mean overshoot falls off with barrier distance exactly as the theory says, from the one
limit to the other:

| b (step sds) | 0 | 0.279 | 0.5 | 1 | 2 | 4 | 8 |
|---|---|---|---|---|---|---|---|
| mean overshoot | 0.723 | 0.660 | 0.627 | 0.596 | 0.592 | 0.592 | 0.591 |

Both ends land on their closed forms to within the noise, and the whole correction is spent by one
full step. The 0.660 at fixed b = 0.279 and the 0.669 averaged over the entry law do not conflict:
the overshoot is convex in b, so spreading x₀ over the entry law raises the average above its
value at the mean.

**§07 can therefore say why its closed form runs light, in which direction, and between what two
numbers the truth must lie** — which is strictly better than the bare "9%" it reports now, and
costs a sentence and a bracket.

**Fifth, and this one moves a printed figure: [eq:trapped](#eq:trapped) is 7.8% low.** §07 quotes
"**4.1%** of every assignment permanently trapped" and a stratum growing at "λ × 4.1% ≈ **0.43**
lots a year" at σ = 40%. eq:trapped is Corollary 3.1 truncated at its first term, evaluated at the
same b = 0.279, and the exact discrete-walk answer is:

| σ = 40%, ν = −3.5% | trapped fraction | λ·P, lots/yr |
|---|---|---|
| eq:trapped as printed | 0.0409 | 0.426 |
| exact, via the paper's Wald identity (22) | **0.04436 ± 0.00002** | **0.461** |
| exact, brute-force walk with an analytic tail credit at 100 steps | 0.04451 ± 0.00032 | 0.463 |

So **4.1% should be about 4.4%, and 0.43 about 0.46.** The two routes have almost nothing in
common — the first never runs a walk to absorption at all — and they agree to within the second
one's noise. Note the direction is *against* the operator, so §07's conclusion is reinforced and
its number is the flattering one.

**This is the one place in Part II where an approximation is quoted as a result.**
eq:holding-siegmund is the other β formula and §07 presents it as an approximation with its error
attached; `grid_tax()` is a definition the article names. That is exactly the difference. `trapped_fraction()` is a
closed form all the way down, and `verify_examples.py:214` checks it against *numerical
integration of the same closed form*, which tests the truncated-normal expectation and cannot see
the approximation being made. It was booked as a cross-check between two independent routes; it is
not one. (`DONE.md`'s INF-5 entry carries a dated `**Amended:**` note to that effect as of
2026-08-04.)

**Sixth, §07's headline multiple undersells its own argument.** "2.1 times the typical entry
depth" is the ratio of β·σ·√τ_c to E[x₀], and it is arithmetically right for the tax *as defined*
— but what the grid actually charges is 0.669·σ·√τ_c = 0.0371, so the honest multiple is **2.40×**,
and the Wald decomposition splits the hole a lot must climb **29% entry, 71% grid**. The
qualitative claim — "the exit grid, not the entry overshoot, is what keeps lots in inventory" — is
*strengthened*, and the √n scaling argument beside it is untouched, since both quantities still
scale with σ·√τ_c.

### Extended 2026-08-04 by reading [Janssen & van Leeuwaarden](#ref:janssen-vanleeuwaarden-2007) in full

The pass had this listed as a pointer for "moments of the all-time maximum". It is the other half
of the same item: **the quantity [eq:trapped](#eq:trapped) computes is that maximum's
distribution**, and the paper supplies one exact value of it in closed form. Everything below was
again measured outside the model, and their Theorems 1–3 were each reproduced against their own
elementary Spitzer counterparts to ten digits before anything was quoted from them.

**Seventh, the trapped fraction has a name and it is theirs.** Measure a lot's *recovery* from its
entry depth in units of one period's step: S_j = (x₀ − x_j)/(σ·√τ_c). That is exactly their
Gaussian random walk, whose drift per step is θ = ν·√τ_c/σ — negative in the unstable regime,
which is their −β with β = |θ| — and a lot escapes iff S ever reaches b = x₀/(σ·√τ_c). So

    trapped  =  P( M < b ),   M = the all-time maximum of the Gaussian random walk

with no approximation anywhere in the statement. §07's grid tax is the *mean* of that same
maximum and eq:trapped is its *lower tail*, which is why one constant governs both. Below, θ at
σ = 40% means |θ| = 0.024268.

**Eighth, and this is the find: the b → 0 end of eq:trapped is exact and published.** Their
Theorem 1 gives P(M = 0) = √2·θ·exp{ (θ/√(2π))·Σ ζ(½−r)(−θ²/2)^r / (r!(2r+1)) } — the fraction
trapped when the strike is set so far out that assignment lands at no depth at all. At σ = 40%
(θ = 0.024268) it is **0.033838**, against eq:trapped's zero-depth limit of
1 − exp(−2β·θ) = **0.027880**. The closed form is **17.6% low there**, and the shortfall factor is

    (2β·θ) / (√2·θ)  =  √2·β  =  **0.8239**,   with no parameters left in it

so the relative error is a universal constant at that end. **It is worst exactly where an operator
would go to escape the problem** — further out of the money — and §07 should not be read as
promising otherwise.

**Ninth, this pins the diagnosis down at both ends: the formula's shape is right and only its
constant is wrong.** Substituting the two published overshoot constants into eq:trapped, against
the exact 0.0444 at the entry law:

| overshoot constant used in the shift | trapped, at the entry law | at x₀ → 0 |
|---|---|---|
| β = 0.5826, **as printed** | 0.0409 | 0.02788 |
| measured 0.660 at b = 0.279 (above) | 0.0445 | — |
| ladder height 1/√2 = 0.7071 | 0.0467 | **0.03374** |
| E_θS_τ = 0.7215, the b → 0 end | 0.0473 | — |
| **exact** | **0.0444** | **0.033838** |

At x₀ → 0 the ladder-height constant makes the closed form right to **0.3%**, the residual being
the O(θ²) term their series carries — a formula that is wrong by 17.6% with one constant and by
0.3% with another is not the wrong formula. The same two ends that bracket E[W] above bracket the
trapped fraction, so **§07 can give eq:trapped the identical treatment**, which is worth more than
requoting a number.

**Tenth, a third route agrees.** A plain walk simulation over the entry law — 600k paths, no
analytic tail credit, truncated where Lundberg's inequality bounds the neglected mass at 4e−9 —
gives **0.04460 ± 0.00027**, against the Wald identity's 0.04436 ± 0.00002 and the brute force's
0.04451. Three routes sharing almost nothing now put the printed 4.1% at 4.4%.

**Eleventh, what β *does*, in one line, from their Theorem 2.** E M = 1/(2θ) + ζ(½)/√(2π) + θ/4 +
O(θ²): the grid-sampled all-time maximum keeps the continuous exponential's rate 2ν/σ² and, to
this order, its standard deviation, and loses **exactly the call-grid tax from its mean**. At the
running example, in depth units, mean 0.76816 against the continuous 0.8000 — a deficit of
0.031844 against β·σ·√τ_c − ν·τ_c/4 = 0.031836 predicted — while the standard deviation is
0.799524, short by 0.000476 ≈ ν·τ_c/4. **The mean moves by 0.58 of a step and the spread by 0.009
of one.** That is the sharpest available statement of what sampling costs, and §07 may use it as
one — but **not as a result about our lots**: their M runs forever and a lot's walk is killed at
zero, so the two coincide only in the trapped case above.

**Twelfth, the constant has a family and a queueing pedigree.** Their §1 lists where
−ζ(½)/√(2π) turns up: sequential testing ([Chernoff](#ref:chernoff-1965)), corrected diffusion
approximations ([Siegmund](#ref:siegmund-1979)), the discretization error in *simulating* Brownian
motion (Asmussen, Glynn & Pitman 1995, *Ann. Appl. Probab.* 5:875–896; Calvin 1995, *JMAA*
191:608–617), option pricing ([Broadie, Glasserman & Kou](#ref:broadie-glasserman-kou-1997)), and
the thermodynamics of a polymer chain (Comtet & Majumdar 2005, *J. Stat. Mech.* P06013) — because
"these applications have in common that a Brownian motion is observed only at equidistant sampling
points". Separately, 1/(2θ) is **Kingman's** upper bound on E M, tight in heavy traffic, and the
c ≈ 0.58 gap he reported in 1965 *is* this constant — he wrote it as a series he did not evaluate,
so he had the zeta function in hand without saying so. One sentence of that turns 0.5826 from a
number quoted on authority into
a member of a family, and the Kingman half connects §07's grid tax to §08's queueing frame. Any of
those citations arrives **[cite unverified]** — the details above are off their reference list, not
off copies, the one exception being Chernoff, whose own copy was obtained the same day (see
Thirteenth) — and the general-audience pick is the polymer.

**No numerical hazard.** Their series converge for |θ| < 2√π = 3.545 and the article's θ is 0.035
at the running example and 0.024 at σ = 40%; θ = |ν|·√τ_c/σ cannot approach the radius at any
parameters a reader would try. Their §7 gives alternative representations if it ever did.

### Extended 2026-08-04 by reading [Chernoff](#ref:chernoff-1965) in full

The origin paper, read the same day off a JSTOR scan of pp. 55–68. **It moves no figure** — the
attribution corrections it carries belong to II-23, which owns them — but it settles two things
this item asserts and closes off a third line of enquiry before anyone spends an afternoon on it.

**Thirteenth, β was an integral for twenty-one years before it was an overshoot, and the First
point above is not Chernoff's reading of his own number.** He reached ẑ through Spitzer's solution
of the Wiener–Hopf equation (his refs [6] and [7]: F. Spitzer, *The Wiener–Hopf equation whose
kernel is a probability density*, *Duke Math. J.* **24**:327–343, 1957, and II, **27**:363–372,
1960), Gordon Latta recognised the resulting integral as ζ(½)/√(2π), and Hogan identified it with
the limiting expected overshoot only in **1986**. Nothing in the 1965 paper says the word. **This
is a gain for §07's detour, not a caveat**: the general-audience sentence First proposes — *a
barrier crossed between two expiries behaves as though it sat 0.58 steps deeper* — can be
introduced as the meaning the number turned out to have, twenty-one years after it was first
computed as a definite integral in a problem about sequential testing. That is a better opening
than "the constant is the limiting expected overshoot", and it is the same length.

**Fourteenth, a fourth route confirms the digits, and it is his own.** Corollary 1(b) prints ẑ as
−(1/2π)∫λ⁻² log[λ²/2(1−e^(−λ²/2))] dλ. Evaluated while reading, that integral is
**−0.582597157939**, matching −ζ(½)/√(2π) to 25 digits. So the four routes now on record — Latta's
zeta closed form, Chernoff's Wiener–Hopf integral, Chang & Peres's ladder-height expansion, and
Janssen & van Leeuwaarden's series — all land on the same 0.5825972, which is the strongest
possible support for **Do not change `BETA`** below. The **−0.5824** printed twice in his paper is
an arithmetic slip in evaluating his own formula, not a rival value; II-23 carries what to tell a
reader about it.

**Fifteenth, the origin cannot help with Second, and this closes that line off.** Chernoff's object
is the **Bayes-optimal stopping boundary of a sequential test**, not a knock-out barrier, and his
asymptotics run in δ: (1.1) is x̃_δ(t) = x̃(t) + ẑ√δ + o(√δ), with Theorem 5.1 making the o(1)
uniform only for t in an interval bounded away from 0 and ∞. **There is no barrier-distance axis in
the paper at all** — the boundary *is* where the process stops, so the small-b regime the article
sits in does not arise for him and no error term of his can be re-read as bounding ours. Chang &
Peres stays the sole source for the size of the b = 0.279 error, and nobody should go back to the
origin looking for a sharper one.

**Two places this correction does not reach**, measured and recorded so nobody re-derives them.

*(In both, θ is §00's census exponent 2ν/σ² = 1.25, not the drift-per-step θ = 0.0347 this item
borrows from Chang & Peres above. The two letters collide and the article's meaning wins.)*

- **§10's [eq:theta](#eq:theta) is exact on the grid**, not corrected. Solve the Lundberg equation
  for a Gaussian step: E[e^(γ·Δ)] = 1 with Δ ~ N(−ν·τ_c, σ²·τ_c) is γ·τ_c·(−ν + γ·σ²/2) = 0, and
  τ_c cancels identically, so γ = 2ν/σ² on *any* call grid and the capital boundary is
  cadence-free. §10 already reaches that from [eq:basis-multiplier](#eq:basis-multiplier); this is
  the census side of the same fact, and it is the answer to the question a reader will have on
  arriving from §07 — *did the grid move the boundaries too?*
- **§11's [eq:survive](#eq:survive) needs no shift.** Its barrier is continuously monitored, in
  the formula and in `wheel_sim`, which crosses with a Brownian bridge. Were a discretely
  monitored version ever wanted — a broker checking at the close — the shift is
  β·σ·√(1/252) = 0.0073 in log price, multiplying P(sold out, ever) by e^(−1.25 × 0.0073) = 0.991,
  so §11's 1.01% would read 1.00%. The contrast is the point: the same correction is 2.1× the
  entry depth on a four-week call grid and a rounding error on a daily one, because it scales with
  the square root of the monitoring interval.

**What to do.**

- **§00's symbol table**: β gains its meaning (limiting expected overshoot) and its far-barrier
  caveat, in the same line.
- **§07, [eq:siegmund](#eq:siegmund)**: say what the overshoot is, that 0.5826 is the far-barrier
  limit, and that at the article's own barrier distance the grid charges 0.669 — then quote 2.40×
  or quote both. Attribution follows **II-23**'s corrected pedigree, with
  [Janssen & van Leeuwaarden](#ref:janssen-vanleeuwaarden-2007) beside Chang & Peres for the
  meaning: they are the ones who say in as many words that the constant is what a grid costs a
  *maximum*, and their application list is the optional second sentence (Twelfth above). **If the
  detour wants one memorable sentence rather than two dutiful ones**, Thirteenth is the candidate —
  the number was computed as a definite integral in 1965 and only understood as an overshoot in
  1986 — and it can carry the meaning and the pedigree together.
- **§07, [eq:holding-siegmund](#eq:holding-siegmund)**: replace the one-sided "9% below" with
  Wald's identity and the two-sided bracket.
- **§07, [eq:trapped](#eq:trapped)**: requote from the walk — 4.4% and 0.46 — and keep the closed
  form as the reasoning aid it is, with its bias named. **Give it the same bracket treatment as
  eq:holding-siegmund** (Ninth above): the two ends are the same two published constants, so the
  two β formulas in the section end up presented alike instead of one being corrected and the
  other requoted. If one extra sentence can be afforded, the zero-depth limit is the one to spend
  it on — the closed form is 17.6% low there, worst where the strikes are furthest out.
  **Precondition: `code/` has to be able to compute it.** The cheap route is Chang & Peres's
  identity (22): trapped = 1 − E[exp(−θ·(x₀ + R))] with R the overshoot law of the walk, which
  needs a few periods per path rather than the 12,700 the brute force ran. Whatever route is
  chosen, it needs a frozen case, and `holding_trapped.py`'s `--sigma 0.40` expectations
  (0.041, 0.43) move with it. **Use Janssen & van Leeuwaarden's Theorem 1 as the second frozen
  case**: at x₀ → 0 it gives 0.033838 in closed form with no walk to run and no Monte Carlo error
  to argue about, it is the one point where the exact answer is *published* rather than measured,
  and any route that reproduces the entry-law figure while missing that endpoint has the shape
  wrong rather than the constant.
- **Do not change `BETA`.** 0.5826 is correct to four decimals for what it is
  (−ζ(½)/√(2π) = 0.5825972); the defect is the *application*, not the constant, and `grid_tax()`
  is a definition the article names. If a corrected shift is wanted in code it belongs beside
  `grid_tax()` under its own name, not inside it.

**One gain outside Part II, recorded and not converted.** `model.py:565`'s converger uses
"Siegmund's E[T] ≈ (E[x₀] + βσ√τ_c)/ν" as an independent read on cells it cannot converge, noting
that converged cells sit **5–12% above it** and truncated ones below. That band is now explained
and, better, *bounded*: the excess is (E[overshoot] − β)·σ·√τ_c/ν, and the overshoot is largest at
b = 0 — the ladder height's CV² is 0.65, below 1, so its mean residual life falls with distance,
which is what the table above shows — so the ceiling is
(E_θS_τ − ρ(θ))·σ·√τ_c / (E[x₀] + ρ(θ)·σ·√τ_c) ≈ **15%** at the running example, against a measured
10%. A one-sided heuristic becomes a two-sided test, which is worth an INF item if anyone extends
the sweep. (The monotonicity is an argument and a measurement here, not a theorem quoted from the
paper.)

**Sequence with II-23**, which owns the attribution of the same equation and now carries the
corrected pedigree. **II-23 changes no number and this one changes two**, so if they are written
together, keep that distinction visible in the commit rather than merging them.

**II-30. §08's detour describes a Little's law that is not the one it cites, and the finite-horizon
row it calls an approximation is the theorem itself.** (From reading both
[Little (1961)](#ref:little-1961) and [Little (2011)](#ref:little-2011) in full, 2026-08-04. The
first was **[A]** — a scan with no text layer, read off page images — and the second **[P]**.
Withdraws II-22's first caution; adds one figure and moves none.)

Three edits, all in §08, and they are one idea seen three times: **the law is stronger than the
article thinks, in exactly the direction the article needs.**

**1. The finite window is not a truncation. It is the theorem.** II-22's first caution said
"H = λG is a stationary identity and the article reports finite horizons —
[eq:little-finite](#eq:little-finite) is a truncation of it, not the theorem". That is wrong, and
the copy is emphatic about it. Little (2011) **§2 is new material written for the retrospective**,
and its whole argument is that practice happens in finite windows: he proves **LL.1** (system empty
at 0 and T) and **LL.2** (nonzero starting and ending queues, with λ = S(T)/T counting everything
that was ever in the system), and states as his reason that "all observations of practice take
place in a finite time interval" and that "the finite time interval guarantees that the
relationship L = λW is numerically exact". §2.1.4 adds that LL.1 needs no stationarity: it "holds
under nonstationary conditions", his own example being a supermarket whose arrival rate peaks
after noon.

**Which is our transient exactly, and this is the sharp end of the item.** A filling wheel starts
empty and is still filling when the horizon arrives, so **LL.2** is the case that fits — the one
that permits a non-empty ending queue. It is also the only one that *can* fit: 1961's Theorems 1
and 2 require {n<sub>t</sub>} itself to be strictly stationary, and ours is not, by ninety years.
So the article cites 1961 for [eq:little](#eq:little), where it holds, and then applies the law
over a window that 1961's hypotheses do not reach — while calling the result an approximation of
the thing that *is* covered. Both halves of that are backwards. **Checked on our own numbers, and
it is exact to machine precision.** Reading W(H) as the mean residence *inside the window*,
W(H) = (1/H)∫₀^H (H−s)·S(s) ds, against `economics(horizon=H)["I"]` computed the census way:

    horizon H                          5 y     10 y     30 y
    E[I] averaged over [0,H]          5.41    7.39    11.40      (§08's second row, unchanged)
    W(H), in-window residence         0.520   0.711    1.096
    lambda * W(H)                     5.41    7.39    11.40      (agrees to 1.3e-15)

and it is exact for a structural reason, not a numerical accident: `_time_avg_weights` gives period
j the weight τ_c·(H − (j+½)τ_c)/H, which *is* the expected in-window occupancy of that period for
a lot arriving uniformly in the window. So **every** horizon-indexed figure in Part II — the
inventory, the premiums, the basis — is already λ·G read over the window, for its own weighting.
The extension of LL.1 from f ≡ 1 to general f is ours by the same two-line argument and is not in
Little; say "the same reading" rather than citing him for it.

**It has a name, an older lineage, and a warning attached** (added 2026-08-04 from
[Whitt (1991)](#ref:whitt-1991) §5 **[F]**). The finite-window reading is the **operational
analysis** version of Buzen and of Denning & Buzen, textbook material in computer performance
analysis (Lazowska et al., ch. 3), and Whitt calls it "primarily a rediscovery of the fact that,
for each sample path, ∫₀^t Q(s) ds = Σ<sub>k=1</sub>^{A(t)} W<sub>k</sub> whenever Q(t) = 0". So
Little's LL.1/LL.2 are a restatement of something with its own literature, and **§08 should not
present the window reading as exotic**. Two further gifts. When the system is *not* empty at the
window's end — our case — Whitt records the standard convention as **defining W to be L/λ**, which
is precisely the W(H) computed above, so the quantity is not ours and needs no apology. And the
warning, which II-30 must carry into the section: the finite-time "measurement" version "leaves
open the question of how the finite-time averages are related to the limits (e.g., prediction)".
That is the exact seam this article walks — it reports 11.40 *and* 21.82 — so the window law
licenses the measurement and says nothing about the extrapolation. The 90-year approach is still
what connects them, and it is not a corollary of the identity.

**What §08 gains is a sentence it currently cannot write.** The section's best line is that the
operator-relevant number is 11.40 and not 21.82, and it explains the gap by the slowness of the
tail. The window law explains it in one figure instead: **over a thirty-year window a lot spends
1.10 years inside the window against a full life of 2.10** — the window sees about half of each
lot, so it holds about half the equilibrium inventory. Same law, honestly applied, no
approximation anywhere. **Trap when quoting the fraction**: 11.40 is a near-grid number and 2.10 is
the extrapolated one, so the ratio reads 52% or 54% depending on which E[W] a reader divides by
(near-grid E[W] = 2.046). Quote **W(H) = 1.10 y** — which follows from two figures §08 already
prints — and say "about half", not a percentage.

**2. The detour credits the 1961 paper with assumptions it does not make.** The detour says the law
requires "nothing about the arrival pattern, nothing about the order of service, nothing about
whether items are independent, nothing about the shape of any distribution. Only that the system is
in a steady state and that the averages exist", and then names Little (1961) as the original.
**Little (1961)'s Theorems 1 and 2 assume strict stationarity of all three processes** — the queue
length, the waits and the interarrival times — **and metric transitivity of the arrival process**,
an ergodicity condition that "the averages exist" does not cover. He flags the first himself: "a
requirement is made for strict stationarity (although this is probably not the weakest requirement
possible)". The assumption-free statement is the later **sample-path version** (Stidham 1974,
restated at 2011 §3.1.1: if λ and W exist and are finite, L exists and equals λW) and LL.1/LL.2,
which assume nothing whatever. Note also that the form the article uses is his **Theorem 2**, the
one about expectations (W = TL, "the principal result for applications"); Theorem 1 is the
sample-path statement that holds with probability one.

**The repair is small and improves the detour.** Keep 1961 as the origin; hang the freedom on the
finite-window theorems, which are in the same author's voice, published in the same journal, and
assume less than anything else available. Two clauses are also now citable that the detour
currently asserts: order of service, from 1961's own Fig. 1 caption — "the figure is drawn for the
case of departure in order of arrival, but this is not required for the proofs" — and the
flexibility of what counts as "the system", from p. 387, which requires only "consistency of
meaning" across *number in the system*, *time spent in the system* and *arrival to the system*.
That is the licence for treating a warehouse of stock as a queue, and it is worth one clause
because a reader's first objection to §08 is that this is not a queue.

**3. §08's closing hedge on the distribution can name the theorem it is declining.** The section
says the distribution of I is not the "tidy bell-shaped thing a queueing course would suggest" and
defers to §12. There is a **distributional Little's law** (2011 §3.3, due to Haji & Newell 1971):
N has the same distribution as Λ(W) — but only under (a) **FIFO** departures, (b) stationary
{W<sub>i</sub>}, and (c) each W<sub>i</sub> independent of the arrival process after item i
arrived. Little calls the conditions "quite restrictive". **The wheel fails (a) outright**: lots
leave in order of depth, not order of arrival, so a lot assigned last week can be called away
years before one assigned in a drawdown. That is the precise reason only the mean carries, and it
is a better sentence than the current appeal to a shared price path — which is the reason (c) also
fails, and can stay beside it.

**4. Optional, and the best pedagogy in the whole item: the ordinal version.** (Halfin & Whitt,
via [Whitt (1991)](#ref:whitt-1991) §8(3), theorem 8.1.) Measure time in *arrival indices* instead
of years, so that a customer's waiting time becomes the number of arrivals during its stay. The
conclusion: **the long-run average number in the system at an arrival epoch equals the long-run
average number of arrivals during one customer's sojourn**. In wheel terms, with no clock at all:
*while you hold one lot, about twenty-two more are assigned* — which is E[I] = 21.8 restated
without years, without λ, and without the reader having to multiply anything. It is the same
number §08 already prints, and it may be the version a general audience actually keeps. Optional
because §08's argument does not need it; if the section is already long, drop it rather than the
window reading.

**Where it goes, and it may want its own subsection.** The detour is a general-audience explainer
and these are four different jobs: fixing what it claims a source assumes, adding the window
reading, naming the distributional result, and optionally restating E[I] ordinally. **Prefer a
short subsection after "Applying it"** — the window law belongs next to [eq:little-finite](#eq:little-finite) and the table it
introduces, not inside a general-audience detour that is doing a different job — with edits 2 and 3
staying as clauses where they already are. Sequence **after II-22**, which owns the same section's
census integrals and now points here for the finite-horizon half.

**What this owes `code/`.** W(H) is a new quoted figure, so under INF-5 it needs a field and a
frozen case: add `W(H) = I(H)/λ` to `code/examples/inventory_little.py` beside the two rows it
already prints, and assert the three values above. Nothing in `model.py` changes — the quantity is
a ratio of two things it already computes.

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

  **Do not redeem it with the distributional Little's law.** (Added 2026-08-04; II-30 has the
  statement.) There *is* a distributional form — N distributed as Λ(W) — and it looks like exactly
  the tool for this bullet, which is why it is worth naming the reason it is not: it requires
  **FIFO departures**, and a wheel violates that on one name and on a book, since lots leave by
  depth and never by seniority. The Poisson result §12 owes comes from the infinite-server
  structure with independent arrival streams, which is a different argument with different
  hypotheses, and the derivation has to be that one.

  **Two leads, and the review settles both without the paywalled original** (2026-08-04).
  **Brumelle, S. L. (1972). A Generalization of L = λW to Moments of Queue Length and Waiting
  Times. *Opns. Res.* 20:1127–1136** is, by its title, the second-moment extension — the object
  this bullet needs, since §12 must produce a variance and not a mean. It is paywalled and nobody
  has opened it, and **it does not need opening**: [Whitt (1991)](#ref:whitt-1991) §6(4) **[F]**
  describes it as relating "the higher moments of the time-stationary number in queue **in a
  G/G/s model** to the higher moments of the customer-stationary waiting time". That description
  is enough to close the lead rather than pursue it — the moment relation is a *model-specific*
  application, not an assumption-free identity like H = λG, and the wheel is not G/G/s. Cite
  Whitt for the existence of the result if §12 wants to note that moments have been done; do not
  reach for it as machinery. The same paragraph gives Brumelle's better-known product, the
  workload formula EV = λ[E(SW) + E(S²)/2].

  And **Glynn & Whitt's §5 CLT** is worth knowing exists but is **not** this bullet's tool either:
  it describes the fluctuation of long-run *averages* around their limits, not the marginal
  distribution of I at a point in time. Confusing the two would produce a confident wrong answer.
  Whitt §8(4) also pins down the distributional version precisely — Q′(0) =<sup>d</sup> Π(λW₀) for
  a rate-one Poisson process Π independent of W₀ — and says it "seems most useful when the arrival
  process is a Poisson process", with FCFS required for the underlying equivalence. So the
  distributional law delivers a *mixed* Poisson under conditions the wheel fails, while the
  infinite-server argument delivers a plain Poisson under conditions it can meet. Two different
  results; §12 needs the second.
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

**And it is a named corollary, not an appeal to linearity** (added 2026-08-04 from
[Little (2011)](#ref:little-2011) **[F]**, §2.2.3 Corollary (3); the 1961 paper has the same
result for priority classes on p. 387). For mutually exclusive classes k — one per name, for us —
L<sub>k</sub> = λ<sub>k</sub>W<sub>k</sub> holds class by class, and the aggregates are
λ = Σλ<sub>k</sub>, L = ΣL<sub>k</sub>, **W = Σ(λ<sub>k</sub>/λ)·W<sub>k</sub>**. Two things §12
should take from that. The book-level law is a *theorem* about a decomposition rather than a
restatement of "expectations add, so it must be fine" — worth a clause where the diversification
claim is first made. And **the book's mean holding time is the arrival-weighted average of the
names', not the plain average**: a book that runs a fast name at high cadence and a slow one at
low cadence has a book-level W nearer the fast name's. §12 does not currently quote such a number,
and this is the rule if it starts to — including in §11's capacity formula, where E[W] is the
denominator and a mis-weighted book average would propagate straight into λ_eff.

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
write-ups, with one exception: **IV-9 is a constraint on how §14 measures**, added 2026-08-04, and
it should be read before either section is drafted rather than after.

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
- **A fourth trap, and a free check, both from the finite-window law** (added 2026-08-04 from
  [Little (2011)](#ref:little-2011) §2.2, via **II-30**).

  *The trap: a window cannot see E[W], and comparing a live holding time to 2.10 years is a
  category error.* What a window of length H measures is the **in-window** residence — a lot
  assigned in month 12 of a 15-month record contributes three months and is still open. II-30
  gives the model-side comparand, W(H) = E[I over [0,H]]/λ, and at the running example's parameters
  it reads **13.5 weeks at H = 1.25 y** against E[W] = 2.10 years, a factor of **eight**. So the
  quantity to put beside a live mean holding time is W(H) at the live window's own length and the
  live parameters, computed the same way — not 2.10, and not the median either. This bites nothing
  today only because no bullet above quotes a live mean holding time; it bites the moment §14
  does, which is exactly the shape of the calendar/session trap two bullets up.

  *The check: L = λW is an arithmetic identity on the ledger, so it tests the data.* LL.2 holds
  exactly over any finite window with a non-empty start and end, which is every live window we will
  ever have. The account's mean inventory, its assignment count and its mean in-window residence
  must satisfy it to the digit — and in `live_ledger.py` those three come from different places in
  the statements (positions against transactions), so a disagreement is a **data** fault, not a
  model result. That is Little's own advertised use: Lovejoy's report in the same paper is that
  "Little's Law provides a reality check" on hospital data that "do not add up". Cheap to add
  beside the 4,204 lot-days already measured, and it belongs with the two internal checks above
  rather than in the model comparison, because it can only ever pass or reveal a bug.
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

**IV-9. Which quantity §14 should measure, and the one the live book cannot measure at all.**
(From [Whitt (1991)](#ref:whitt-1991) §7 and §8(1) **[F]**, with
[Glynn & Whitt (1986)](#ref:glynn-whitt-1986) **[A]** and
[(1989, indirect)](#ref:glynn-whitt-1989-indirect) **[P]** behind it; 2026-08-04. Constrains IV-1
and IV-2 rather than adding a section.)

Little's law is assumption-free as an identity, and this item is about the fact that *estimating*
its terms from a finite record is not. Whitt puts it in one sentence: "the probability structure
underlying L = λW becomes crucial when we want to compare finite averages to their limits". §14
does exactly that comparison, on 55 lots.

**1. The indirect estimator is the better one, and we are in the case where it wins.** With λ
known, estimating L indirectly as λ·Ŵ is *more asymptotically efficient* than estimating L
directly from the inventory path — "provided that the interarrival and waiting times are
negatively correlated", which Whitt notes is the typical situation and is emphatically ours:
assignments cluster in drawdowns (III-2's common-shock arrivals), and lots assigned in a drawdown
are the deep, slow ones. So shorter gaps between arrivals go with longer holding times, which is
the sign the result wants. Glynn & Whitt go further — a linear control estimator, λŴ +
â(λ̂⁻¹ − λ⁻¹), is better still — and note that L = λW "does not change the asymptotic efficiency
when the arrival rate λ needs to be estimated as well".

**2. The estimator counts departures, not arrivals, and the reason is our censoring.** Whitt is
explicit that one works with the completed lots, D(t), and not with A(t), "because the time spent
in the system by customers still present at time t is typically not known". That is the live
book's 55-lots-40-resolved problem stated as an estimation convention. IV-1 already handles it
with Kaplan–Meier, which is the stronger treatment; the point here is that the naive alternative
has a name and a known bias direction, and §14 should say which it used.

**3. And the one that actually bites: the wheel is a partially observable system in Whitt's
sense.** §8(1) describes the case where L is cheap to observe and W is expensive — "in many
manufacturing settings it is much easier to count the work in process than it is to measure
production intervals … thus we may want to apply L = λW to estimate W using L, **even though the
statistical precision would be better using W**". That is the live account exactly: inventory
comes off the positions file continuously (4,204 lot-days), holding times need lots to have
finished. **But the difficulty he then raises is one this article has already quantified.** The
observed WIP includes items that will never become good product, so "what we want to observe … is
only the WIP that will eventually be good, but this eventually good WIP is not directly
observable". Our analogue is [eq:trapped](#eq:trapped): a fraction of lots never return at all.
So **L/λ is not an estimate of the mean holding time of lots that get called away** — it is
contaminated by exactly the population §10 says never leaves, and it is contaminated upward.
Nozari & Whitt is the reference for the repair; nobody has read it and §14 may not need it, but
the trap must not be walked into silently.

**What to do, and it is a paragraph in §14 plus a check.** State which estimator each live figure
uses; do not compare a live L/λ against the model's E[W] without saying what the trapped fraction
does to it; and keep the two uses of the identity apart, because they are different in kind. The
**arithmetic** use is II-30's free consistency check on the ledger — exact, assumption-free, can
only pass or reveal a bug. The **statistical** use is comparing a window's measured value to the
model's, which needs the probability structure and has confidence intervals. IV-2 already owes
intervals (Broadie–Chernov–Johannes); this is the same discipline reaching the quantity side.

**One thing worth knowing and not worth using.** [Glynn & Whitt (1986)](#ref:glynn-whitt-1986)
prove the CLTs are locked together the way the means are: the customer-average wait obeys a
central limit theorem **iff** the time-average queue length does, jointly, with simply related
limits. It is a satisfying fact and it is not a tool for us — our single-name book violates the
stationarity these CLTs assume, which is III-1's whole problem, and the honest route to intervals
on live figures stays the empirical one.

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
