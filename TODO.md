# TODO

Open work only. Everything finished, resolved or deliberately descoped lives in
[`DONE.md`](DONE.md), which also carries the map from the old flat numbering (#1–#25) to the
per-part numbering used here. Items are tagged `(was #n)` where a predecessor existed, so the
citations in `drafts/` stay traceable.

**Nothing resolved is kept in this file.** When an item closes its write-up goes to `DONE.md`, and
any figure a still-open item needs is folded into that item rather than left behind as a
hand-forward block. So every entry below is work someone still has to do. Numbers are never
recycled or closed up: the gaps — I-3, I-5, **all of Part II**, IV-5, IV-6, IV-7, INF-1, INF-6 —
mean those items are in `DONE.md`. (IV-6 and IV-7 were added to this list on 2026-08-01, when IV-8 was
numbered around them; they closed on 2026-07-28 and had been missing from it since. IV-5 closed
2026-08-05.)

Sections reference items as "TODO I-1", "TODO IV-2" — at present **no section body carries such a
flag** (checked 2026-08-05), and that is the intended steady state: an in-text flag is a promise to
a reader and should be added only when the text genuinely defers something. Twenty-one live in
`sections/98-bibliography.md`, in the internal field after an entry's anchor, which is stripped at
assembly and so never reaches a reader; they mark the one unread download, the sources that may be
cited for their existence only, and the entries the readings of 2026-08-04 and 2026-08-05 left
owing something to I-7, III-3, IV-3 or IV-9.

**The bibliography stands at 43 entries** — **16 [F]**, 17 [A], 6 [P] and 3 [R] textbooks — of
which **26 are cited, from 9 sections**. Three still carry `[cite unverified]`. Those counts move
most weeks and are printed by `python -m examples --references`, so **read them off the checker
rather than from here**; what is recorded here is only the shape, which is that the uncited
remainder is almost entirely §03's.

## Where things stand

Thirteen of the seventeen planned section files exist, plus two appendices: the bibliography
(`sections/98-bibliography.md`, hand-maintained, the only file that may declare a `{#ref:}`
anchor) and the generated reproduction table (`sections/99-reproduction.md`, produced by
`python -m examples --appendix`, never edited by hand). Part I is written bar two stubs; **Part II is closed** —
all thirty of its items are in `DONE.md`, the last thirteen having landed on 2026-08-04 and
2026-08-05;
**Part III and Part IV are unwritten**, and between
them they are still the bulk of what is left besides those stubs and the assembly work.

| part | files | state |
|---|---|---|
| I. Setup | 00 notation · 01 abstract · 02 introduction · 03 prior-work · 04 strategy | written, except 01 and 03 (stubs) |
| II. One asset | 05 entry · 06 depth-process · 07 holding-time · 08 inventory · 09 returns · 10 stability · 11 constrained | **written and closed** — no open items. Every section carries its citations; §09 went from none to eight on 2026-08-05 |
| III. Many assets | 12 portfolio · 13 correlation | **do not exist** |
| IV. Reality | 14 verification · 15 live-account · 16 outlook | **14 and 15 do not exist**; the outlook is a stub, on disk as `15-outlook.md` |

**This file uses the final numbering** — portfolio §12, correlation §13, verification §14, the
live account §15, the outlook §16 — as of 2026-07-30. It previously used the pre-§11 numbering
with a note saying so, which collided with the constrained section that actually occupies §11 on
disk: "write §11, the portfolio section" was an instruction to overwrite a finished section. The
*file* renames are still deferred to when Part III drafts — `15-outlook.md` becomes
`16-outlook.md` then — and nothing breaks in the meantime because anchors are name-based.

Six section files link to anchors in the missing files (recounted 2026-08-05, after II-18 added
two): `sec:verification` from 00, 07, 08 and 09; `sec:live` from 00, 04, 05 and 09;
`sec:portfolio` from 00, 08 and 09. Those cross-references are broken until Parts III and IV land,
and that is the assembly-time deadline. `sec:correlation` is referenced only from §00's own anchor
registry, so it is still promised by nothing but the list.

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
premium-sensitivity half of both papers was **II-27**, which closed on 2026-08-05 and put it in
§09 — both papers are now cited there for the slope, converted to volatility points. **So §03
inherits them already cited**, and its job is the pedigree: what the two simulations were, why
they are the earliest of their kind, and the insurance framing above. Do not restate §09's
conversion or its ~50 bp.

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
(added 2026-08-01). `sections/98-bibliography.md` is the live list — the pass's entries plus the
textbook and foundational sources the sections were already leaning on informally — each with a
`{#ref:...}` anchor, its read level and its local filename. The draft's §8 is the *historical*
list; keep read levels current in the bibliography, not there. Prose cites by anchor and never by
number (see §00's citation convention).

**The readiness measure for this item is the uncited count**, which `python -m examples
--references` prints every run: **an entry §03 never cites should be deleted from the bibliography
rather than shipped.** Read the number off the checker rather than from here — it has fallen
steadily as Part II landed its own citations, and what is left uncited is now almost exactly §03's
own working set.

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
  unchanged: no novelty may be claimed for the identity, and §08 must not imply otherwise. **§08
  already complies as of 2026-08-04** — its H = λG detour closes by conceding that Little's own
  illustration of a weighting is a portfolio of assets, and that what the article supplies is the
  holding time and the census to put into it. §03 must not contradict its own Part II. But the tone that follows from these two quotes is not defensive. The article
  is carrying out an application the field's own authority proposed and left open, on machinery
  fifty years of queueing theory has already stress-tested — which is *why* the results can be
  trusted without a new limit theorem behind them, and is a better sentence than any claim of
  priority would have been. What the article supplies is what Little could not: the specific W
  (a depth process and a first passage) and the specific weighting (the census). **Both quotes are
  short enough to use verbatim** and they are the cleanest way to make the point.
- **Its subsection 4 is the citation half of II-18**, the index/single-name volatility-premium gap.
  **II-18 closed on 2026-08-05 and §09 now carries that gap in prose**, with two citations of its
  own — [Bakshi & Kapadia](#ref:bakshi-kapadia-2003-jod) for the 3.3-against-1.5 measurement and
  [Carr & Wu](#ref:carr-wu-2009) for the mechanism, both **[F]**. So this subsection is no longer
  establishing the fact; it is supplying the pedigree behind a claim the reader has already met,
  which is the division of labour II-23 states. **Do not re-argue it and do not restate the
  numbers.** What §03 owes here is the shape of the literature — that the familiar 2-to-4-point
  figure is an index measurement, that the single-name work is thinner and later, and that
  [Driessen, Maenhout & Vilkov](#ref:driessen-maenhout-vilkov-2009) named the correlation mechanism
  §09 describes without naming. That last is **[A]**, so §03 may cite it for the result's existence
  and must quote no number from it.

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

**I-7. Bibliography entries carrying details nobody has checked against a copy — three open.**
(From building `sections/98-bibliography.md`, 2026-08-01. The count moves whenever an entry is
cleared; `python -m examples --references` prints it, and that is the number to trust.)

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

**Three are open**, and they are the residue after a run of clearings: janssen-vanleeuwaarden-2007
closed with II-29 on 2026-08-04, and li-linetsky on 2026-08-05 (below). Of the three, **one can be
finished** — israelov-covering-the-world, which only wants reading — and the other two are
Siegmund's, where the obstacle is a missing copy rather than a missing read.

- **israelov-covering-the-world** is downloaded but unread, and the title or author list is the
  guessed part. The read is owed by **I-1**; clearing the citation falls out of doing it.
- **li-linetsky** (the anchor was `li-zhang`) was read for II-23 on 2026-08-05 and **the tag
  stays**, which is the point of it. The read fixed a *guessed author* — the second author is
  **Linetsky**, not Zhang, so the anchor had been naming someone not on the paper — and put the
  title and affiliations on a copy. It could not fix the venue, because there is none: no journal
  header, no DOI, no arXiv id, in the text or in the PDF metadata. **The one field the copy
  yielded was a date**, off its own metadata — a MiKTeX typescript last written 2014-06-18, with
  references reaching 2014 — so the entry now says "2014 typescript" rather than guessing a year.
  This is the second instance of the Janssen pattern (a full read that cannot clear a citation),
  and the first where the *anchor itself* was wrong, which is worse than a wrong field: an anchor
  is what prose cites by.
- **siegmund-1985** has no copy, and it is a **book** — *Sequential Analysis: Tests and Confidence
  Intervals*, Springer — which is why it is the hardest of the three to source. Chang & Peres's
  reference list corroborates title, publisher and city; the edition and printing are unchecked.
- **siegmund-1979** was **never tagged, and was wrong in exactly the way this item says matters
  most**: the title had been silently truncated to "Corrected Diffusion Approximations" for
  "Corrected diffusion approximations in certain random walk problems". Completed, with pages
  701–719, from Chang & Peres's reference list — and then *tagged*, because that is not a copy
  either.

  **A copy arrived on 2026-08-05 (Sergei) and settled the field that mattered.** It is the Stanford
  Technical Report No. 4 of August 1978 — the preprint — and its cover reads "Corrected Diffusion
  Approximations in Certain Random Walk Problems". So the title is now off a source rather than a
  reference list, and it **adjudicates the transposition**: Chang & Peres had it right and
  **Janssen & van Leeuwaarden's list is the one that swapped this title with the 1985 book's**.
  That is the first time two disagreeing reference lists have been settled by a copy, and it went
  the way the *usage* pointed, as this item predicted it would. **The tag stays, narrowed**: a
  technical report cannot supply the journal, volume, issue, pages or the 1979 date, all of which
  are still Chang & Peres's. The level stays **[A]** — cover and front matter only — and §07 quotes
  no number from it.
**janssen-vanleeuwaarden-2007 was the fifth, and it was tagged and cleared within one day** — a
whole life cycle of this item, worth keeping as its worked example. It was tagged 2026-08-04 **by
having been read in full**: the copy is the authors' own typescript (`paperGRWdiffstyleFinal.dvi`,
dvips, March 2007) with no journal header, no volume, no pages and no DOI, so "*Annals of Applied
Probability* 17(2)" came from the pass and the page range was never there at all. **That is the
item's sharpest instance: reading a source cover to cover does not verify its citation, and can be
the thing that reveals the citation was never verified.** It was then cleared the same day, when
II-29 put one of its figures in §07 — and cleared by **the publisher**, since a second typescript
(January 2006) turned out to carry no journal header either. **So neither reading nor re-reading
could have closed it**, which is the strongest statement of the two-independent-checks point this
item has produced. Full details in [`DONE.md`](DONE.md).

The printed count has gone 10 → 3 → 5 → 6 → 5 → 4 → **3**. Every rise was this item working
rather than regressing, and every fall is an entry it has *closed*.

**One entry was born clear**, and it is the standard the remaining three are held to:
`glynn-whitt-1989-extensions` was added on 2026-08-04 *after* its copy had been obtained and read,
with every field taken off the JSTOR cover page and the article header. It is the first entry in
the bibliography that never needed the tag, and the first added in that order. It cost this item
nothing, which is the argument for obtaining a copy before writing an entry rather than after —
and `carr-wu-2009` and `bakshi-kapadia-2003-rfs` repeated the pattern on 2026-08-05, both clean in
every field on being read.

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

**Titles are the part to check first, and five for five now says so.** Every entry whose details
were put against a source on 2026-08-04 — chang-peres-1997 and chernoff-1965 against copies,
siegmund-1979 against two reference lists, janssen-vanleeuwaarden-2007 against the publisher —
turned out wrong in its title and right in everything else. Four different corruptions of the same
field: a truncation, a spurious comma, a singular for a plural, and a title-casing of a journal
that prints sentence case. Numbers get copied because they look like data; titles get retyped
because they look like prose.

**The fifth arrived on 2026-08-05 and it is a fifth distinct corruption: a dropped subtitle.**
`bakshi-kapadia-2003-jod` was carried as "Volatility Risk Premiums Embedded in Individual Equity
Options"; the copy reads "…**: Some New Insights**". The entry was **never tagged**, like
siegmund-1979 before it, and for the same reason — it came from the pass rather than from memory.
It also gained pages 45–54 off the copy, and its **volume and issue 11(1) remain uncopied**: they
are not printed on the article's pages and come from [Carr & Wu](#ref:carr-wu-2009)'s reference
list — which, in the same line, has the title wrong the other way, printing "Premium" singular
where the copy is plural. **A sixth reference list, and it is wrong about the paper we hold, in
the field this item says always goes first.** The two entries read that day and checked field by
**And a sixth check, later the same day, was the first to *confirm* a title rather than correct
one** — which is the outcome this item wants and had not yet seen. Sergei's copy of siegmund-1979
(the 1978 Stanford technical report) reads "Corrected Diffusion Approximations in Certain Random
Walk Problems", exactly the correction Chang & Peres's list had already supplied on 2026-08-04.
That is not a sixth corruption; it is the first *verification* of one, and it does a second job
besides: it **adjudicates between two disagreeing reference lists**, confirming Chang & Peres and
convicting Janssen & van Leeuwaarden of the transposition. The lesson is the one this item has been
circling — when two lists disagree, the one whose *usage* matches its list is the one to believe,
and a copy is what proves it.

field, `carr-wu-2009` and `bakshi-kapadia-2003-rfs`, were both **clean in every field** — the first
two [A]→[F] promotions to cost this item nothing.

**And the read-level rule caught a figure this item could never have seen** (2026-08-05). §09's
BXM detour quoted "up and down betas of roughly **0.63 and 0.78**" — carried from the literature
pass through II-21 into live prose, **with no citation attached at all**. A citation-based scan
misses that by construction: there is no anchor in the sentence to check a read level against. The
figures were pulled on read-level grounds (their source, [Whaley](#ref:whaley-2002), is **[A]** and
paywalled), and reading [Israelov & Nielsen (2015)](#ref:israelov-nielsen-2015) an hour later
showed **they were also wrong**: BXM's published split is **0.46 up and 0.85 down**, an asymmetry
of 0.39 against the recorded 0.15. **So the worst case is not an unverified entry — it is a number
with no entry at all**, and the check that would catch it is not a bibliography check but a scan
for digits in prose that no source is named for. Worth building before assembly.

**This is still a smaller worry than the read-level rule and a different one.** All four that
remain open are pointers for further reading and the article quotes no figure from any of them. The one number
that looked like an exception — β = 0.5826, attributed in §07 to siegmund-1979 — now rests on
**two [F] sources**: chang-peres-1997 prints it to seven digits, and chernoff-1965 supplies an
independent representation, Corollary 1(b)'s Wiener–Hopf integral, which evaluates to the same
−0.5825972. (The value *printed* beside that integral is −0.5824; the discrepancy is his
arithmetic, and §07 says so.) Broadie–Glasserman–Kou carries the constant too. A reader
following a wrong page range loses nothing but time; a reader following a wrong *title* is being
misled.

**And the one entry that *was* on a section's critical path is closed.** §07 now quotes
janssen-vanleeuwaarden-2007's 0.033838 zero-depth limit of [eq:trapped](#eq:trapped), and its tag
was cleared as II-29 was written rather than after — as this item asked, and it is the fourth
entry in the tally above.

**Deadline is assembly**, not §03: a bibliography goes out with the article, and this is the last
thing that should be discovered in proof. Clearing an entry means deleting its `[cite unverified]`
tag, which drops the count the checker prints.

## Part II — One asset

**Closed.** Part II closed on 2026-07-31, was reopened the same day by the literature pass, and was
reopened repeatedly through 2026-08-04 and 2026-08-05 as the sources that pass had only listed were
actually read. It is now closed again with every item written up in [`DONE.md`](DONE.md), and this
time the reopening mechanism is spent: **there are no unread sources left that Part II depends on.**

What the reopening was worth, since the file should record it once rather than leave it in thirty
entries. Four of its items rested on figures computed outside the model and recorded in this file;
**three of those four were wrong** — II-18's count of Carr & Wu, II-25's early-exercise threshold,
and the estimator behind II-20's betas, which turned out right only once its definition was
identified. Two sources listed at [A] said something other than what was recorded, one of them
close to the opposite. **The one item whose numbers were checked and confirmed unchanged was
II-19's**, and it was checked because the other three were not. The rule that caught all of it is
the read-level rule, and the pattern worth carrying into Parts III and IV is simpler than the rule:
*a number that has never been recomputed since it was first written down is not evidence, whoever
wrote it.*

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

  **Do not redeem it with the distributional Little's law.** (Added 2026-08-04; the statement is
  in [`DONE.md`](DONE.md) under II-30, and §08 now names the result and why it does not apply.) There *is* a distributional form — N distributed as Λ(W) — and it looks like exactly
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
  bullets up, which §12 has to *derive* before sizing is allowed to spend it. II-19 stated the
  same prohibition from §09's side, where the answer is simply not available.

  **II-19 closed on 2026-08-05 and §09 now makes the handoff explicitly**, so this bullet inherits
  a promise rather than an opportunity: the section's new cadence subsection states the invariance,
  gives the capital figures, and says in as many words that a given balance "runs a few names
  quickly or many names slowly, at the same return", pointing here for what an operator does with
  it. **All four rows are now frozen cases** in `returns_benchmark.py` and `returns_capital.py`
  rather than figures measured once outside the harness — and they were re-derived through the
  fixed harness (INF-6) and reproduce the table above exactly, so the numbers in this bullet are
  confirmed rather than merely inherited.
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

**This section's anchor is no longer an abstract** (2026-08-05). The paragraph above rested on DMV,
which is **[A]** and must stay that way, with the magnitudes borrowed from elsewhere — a weak
footing for Part III's central claim. [Carr & Wu (2009)](#ref:carr-wu-2009) is now **[F]** and
carries the same structure independently: index variance risk premiums are strongly negative and
highly significant on every index they measure (S&P 500, S&P 100, Dow), single-name premiums are
much smaller and far noisier, and the cross-section is organised by each name's **market-variance
beta** with an intercept indistinguishable from zero. They conclude there is "a systematic variance
risk factor in the stock market that asks for a highly negative risk premium" which individual
names carry only in proportion to their exposure to it. **That is "index-like risk, single-name
pay" derived rather than asserted**, and §13 can now make the argument from an [F] source and use
DMV only for the name of the mechanism. Their measured Sharpe ratios on shorting index variance —
**0.98 / 0.85 / 0.87** — are also the right order-of-magnitude counterweight to any suggestion that
the book should simply write index options instead, alongside DMV's frictions point below.

**Index-like risk, single-name pay.** That is one sentence and it is both halves of Part III.
§12's benefit and §13's vulnerability are not two subjects; they are one quantity with opposite
signs, and it is the same quantity II-18 corrected §09 for.

**§09 already says half of it, so Part III inherits a set-up rather than a blank page** (2026-08-05,
when II-18 closed). Its new premium subsection explains that an index option bundles in "the one
thing a single name cannot sell: the risk that everything falls together", and forwards explicitly
to [the portfolio section](#sec:portfolio) — *a book of single names is paid the single-name premium
and still carries the market's risk when correlations rise*. That forward reference is a promise
§12 and §13 now have to keep, and it fixes the framing: the reader meets the mechanism in Part II
as a fact about **pricing** and should meet it again in Part III as a fact about **risk**. Do not
re-derive it; extend it.

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

**The one thing blocking §15 has cleared**: IV-5 closed on 2026-08-05, so IV-2's withdrawn
implied-volatility level is restored and nothing else here is waiting on a measurement.

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

  **The machinery to fix it now exists, and the convention is settled** (IV-5, 2026-08-05). The
  same bug was live in `iv_panel.py` and was repaired there: `prices.Series.sessions_between()`
  and `session_on_or_before()` count the real calendar off the price series, and
  `iv_panel.session_tenor()` is the consumer to copy. **Take the convention rather than re-deciding
  it** — the count is inclusive of the trade's own session, which `iv_panel.report_clock` shows is
  the nearest of the candidate conventions to variance-true (an entry-day open→close move carries
  **0.65** of a close-to-close session, so a k-session option is worth k − 1 + 0.65) and the
  conservative one. Note this does *not* by itself resolve the bullet: T1's problem is that the
  wrong convention is the one that fits, and putting the tenor right will move the prediction from
  69.9 toward 88.7 against the 71 that occurred. Fixing the units and explaining the fit are two
  jobs, and IV-5 only supplies the first.
- **Three measurement traps**, worth a paragraph because all three were fallen into: reading
  depth on the day before exit discards nearly every exit; sampling lots on a synthetic τ_c grid
  scores periods at tenors never traded; and pricing an entry at the day's close when the
  operator writes in the first hour builds a look-ahead into every measured entry depth.
- **A fourth trap, and a free check, both from the finite-window law** (added 2026-08-04 from
  [Little (2011)](#ref:little-2011) §2.2, via **II-30**, closed 2026-08-04 — §08 now carries the
  window reading and `inventory_little.py` prints W(H)).

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
  be checked against it. The slope survived IV-5 unchanged, as predicted and for the stated
  reason — it divides within leg, name and tenor, so the clock cancels: **1.00 → 1.39** relative
  after against 0.94 → 1.29 before. It still rests on **9 contracts in the deepest bucket** of a
  column that is not monotone; quote it with that qualifier or not at all.

  **The level is restored, and it is less than half what this bullet used to carry** (IV-5 closed
  2026-08-05). The put leg runs **+4.5 points** over subsequently realised volatility and the call
  leg **+2.4**, against +10.7 and +7.0 as previously measured — so about six of the old ten points
  was the calendar/session mismatch, as D2 estimated.

  **Do not write "roughly double the call leg's" in any form.** IV-5 found the leg-level ratio is
  not a well-defined quantity: the legs occupy disjoint moneyness ranges by construction, and the
  ratio moves from 1.5× to 1.9× or from 4.3× to 2.3× depending purely on which cells are compared.
  What §15 should report instead is what the cross-tab shows, which is a cleaner finding than the
  one it replaces: **the spread is a function of distance from the money and barely of leg.**
  Near-money contracts on both legs sit within a fraction of a point of realised volatility (puts
  −5..−2% read −0.1% over 257 contracts, ATM calls −0.1% over 45), and the spread widens outward
  on both — puts +6.0% at 5–10% below spot and +13.2% beyond, calls +1.8% / +3.1% / +5.4%. §09:162
  already says this in prose; §15 is where the numbers go.

  **And it is the direct evidence for §09:156's existing caveat**, which was argued rather than
  measured: that the spread easiest to measure is the one on far-out-of-the-money puts, "and that
  one is quoted precisely because those puts are not as far out of the money as they look". The
  panel now shows exactly that shape. Worth landing the connection explicitly.
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
model's residual tilt even points the wrong way. It is also the first thing a practitioner would
ask for.

**§09 now says all of that itself, and names this section as where the extension belongs**
(II-19 closed 2026-08-05). Its new subsection, "The one dial the model says is free", gives the
sweep, sets Cboe's monthly-against-weekly record beside it, derives the ~3 volatility points of
term structure that would reconcile them, and closes by pointing here. **So this bullet is now a
commitment §09 has made to the reader, not a note to self** — the outlook has to carry it, and it
is the strongest of the four extensions listed here because it is the only one for which the
article has already shown a concrete empirical failure of its own model.

**One more of the same kind, from II-18** (which sends it here; recorded 2026-08-01 so the pointer
resolves): a **beta-scaled σ_IV**. Bakshi & Kapadia find that idiosyncratic volatility is not
priced at all, and that what premium single-name options do carry is the *market* volatility
premium leaking through beta — which predicts the single-name spread should scale with the name's
beta rather than being one flat scalar. That is a testable structure the model could carry, and it
is the natural companion to the term structure above: one gives σ_IV a tenor axis, the other a
cross-sectional one. Neither touches the spine.

**And it now has a published coefficient rather than only a direction** (2026-08-05, from reading
[Carr & Wu](#ref:carr-wu-2009) **[F]**). Their eq. (13) is the cross-sectional law this extension
would implement: mean log variance risk premium = **0.0061 − 0.3283·β^V**, R² 18.4%, across 35
single names and 5 indexes, where β^V is the name's *variance* beta against the index's — the
covariance of log realised variances, not the return beta. Two things that gives §16. The
**intercept is insignificant** (t = 0.09), so the functional form the model should carry is
proportional rather than affine: no market-variance beta, no premium. And the R² of 18.4% is the
honest ceiling — this explains a fifth of the cross-section, so a beta-scaled σ_IV would be a
better default than a flat scalar and still nothing like a calibration. Note the axis is variance
beta and not the CAPM beta a practitioner would reach for first; the two are related but the paper
is explicit that it estimates the former, and the distinction is the whole content of the
structure.

**Two more, from [the literature pass](drafts/2026-07-31-prior-work-literature-pass.md), folded in
2026-08-01.**

- **Transaction costs get a number** (harvest H10). The list currently says commissions "eat a few
  percent of the premium on weekly puts" — a live-account figure — and has nothing at all for the
  spread, which is the larger cost. **Muravyev & Pearson (2020) [A]**: traders who time their
  executions pay effective spreads of **29.6%** (algorithmic) to **58.4%** (all traders) of the
  quoted half-spread, so conventional estimates roughly double the truth. Hill et al.'s **3–6
  bp/month** at half an implied-volatility point of slippage is the covered-call-specific version.
  Both are quotable in a sentence and turn a descope into a bounded one.

  **One [F] figure joins them, and it says the cost is worse on single names** (2026-08-05, from
  [Carr & Wu](#ref:carr-wu-2009) Table 8). Their synthetic variance swap bid-ask spreads run
  **1.55 to 8.28 volatility points**, and "the spreads are larger for individual stocks than for
  stock indexes". Two useful things. It is a spread measured in the same units as the premium
  II-18 is sizing, so a reader can set it directly against a single-name premium of about a point —
  and on that comparison the friction is the same order as the prize. And it sharpens the descope's
  direction: every published spread the article cites is an *index* number, and the strategy this
  article models trades single names, where costs are larger and the premium is smaller. Both legs
  of that comparison point the same way and §16 should say so plainly.
- **Tax is missing from the list entirely**, which makes it read as an oversight rather than a
  decision. It is unexamined everywhere in this project and it is materially adverse for a wheel
  run in a taxable account: premium is short-term, repeated assignment on one name raises **wash
  sales**, and the **qualified-covered-call** rules suspend the holding period on the underlying,
  so writing the call can cost long-term treatment on the shares. §16 should say plainly that tax
  is out of scope and roughly which way the omission cuts. It also connects to **II-24**: the
  disposition effect's documented harm is largely a tax harm, and this article cannot price it —
  which is exactly why II-24's analogy must stay structural.

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
been carrying unbacked into a sourced one. The arithmetic of *our* version is sharper than it was
when this item was raised, and in the direction that helps it. II-18 put the single-name premium at
**about a point**, so the question a track record has to settle is not "two points against zero"
but roughly **50 bp/yr against zero** — half the resolution, on the same noisy quantity. And the
sensitivity MSG are warning about is now *measured* on our side too: II-27's conversion puts their
slope at ~50 bp per volatility point against our 45, so a modest error in the assumed premium moves
the reported level by more than the whole edge being claimed. **That is the sentence §14 wants**,
and it is theirs and ours saying the same thing.

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
does not depend on it. **II-20 and II-21 closed on 2026-08-05 and §09 now reports betas**, so this
item no longer sequences behind them — it inherits them. Two consequences. §09's risk subsection is
the model-side comparand §15's own beta should be set against, and §09 has already established the
house discipline for presenting one: state the estimator, and refuse the comparison with a
published figure computed another way. §15 should refuse it the same way rather than re-deriving
the reason.

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
**arithmetic** use is the free consistency check on the ledger that II-30 identified — exact, assumption-free, can
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
infrastructure landed 2026-07-30 — `code/examples/` with a harness, a module per formula, frozen
cases, a generated appendix (`sections/99-reproduction.md`), eleven compositions promoted into
`model.py`, and a coverage test wired into `verify_examples.py` that
asserts every displayed `{#eq:...}` has a registered example, every example is cited from the
prose, and every footnote names the script that actually backs its formula. The write-up, the
design decision behind it (a `Case` *is* a command line) and the three prose errors it surfaced
are in [`DONE.md`](DONE.md). The module, formula and case counts all grow with the article and are
printed by `verify_examples.py` on every run; do not record them here. **Two items of follow-up
remain, and both were re-checked on 2026-08-05 and are still live.**

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
