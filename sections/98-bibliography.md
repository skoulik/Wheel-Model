# References {#sec:bibliography}

Every source the article cites, and the ones it intends to. Entries are ordered alphabetically by
first author; **the numbers a reader sees are assigned at assembly, not written here**, for the
same reason section and formula numbers are not: prose cites by name anchor, so inserting an entry
renumbers nothing. A citation in the text is a markdown link to an entry's `{#ref:...}` anchor —
`[Siegmund 1979](#ref:siegmund-1979)` — which becomes `\cite{siegmund-1979}` at assembly and
renders as a bracketed number.

**Everything after the anchor on a line is internal apparatus and is dropped at assembly**: the
read level, the local filename, and the link the copy came from. Read levels are the discipline
inherited from [the literature pass](../drafts/2026-07-31-prior-work-literature-pass.md) — **[F]**
full text read, **[P]** partial, **[A]** abstract or secondary description only. *Do not quote a
number from an [A] source without opening the paper.* That rule exists because it was broken once:
both Merton–Scholes–Gladstein papers were carried on secondary summaries that turned out to have
their conclusions backwards. A few entries also carry **[cite unverified]**, meaning the
bibliographic details — edition, title, pages — were reconstructed rather than read off a copy;
they need checking before assembly, and nothing in the article quotes them for a figure.

Downloaded copies live in `literature/`, which is gitignored: they are reference copies, not ours
to redistribute.

- Bakshi, G. & Kapadia, N. (2003). Volatility Risk Premiums Embedded in Individual Equity Options. *Journal of Derivatives*, Fall. {#ref:bakshi-kapadia-2003-jod} — **[F]** · `bakshi-kapadia-2003-jod-individual-equity-vrp.pdf`
- Bakshi, G. & Kapadia, N. (2003). Delta-Hedged Gains and the Negative Market Volatility Risk Premium. *Review of Financial Studies* 16(2):527–566. {#ref:bakshi-kapadia-2003-rfs} — **[A]** · `bakshi-kapadia-2003-rfs-delta-hedged-gains.pdf`
- Black, F. & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. *Journal of Political Economy* 81(3):637–654. {#ref:black-scholes-1973} — **[A]** · [cite unverified]
- Bondarenko, O. (2019). Historical Performance of Put-Writing Strategies. Cboe. {#ref:bondarenko-2019} — **[F]** · `bondarenko-2019-put-writing-strategies.pdf` · https://cdn.cboe.com/resources/education/research_publications/PutWriteCBOE19_v14_by_Prof_Oleg_Bondarenko_as_of_June_14.pdf
- Broadie, M., Chernov, M. & Johannes, M. (2009). Understanding Index Option Returns. *Review of Financial Studies* 22(11):4493–4529. {#ref:broadie-chernov-johannes-2009} — **[P]** · `broadie-chernov-johannes-2009-index-option-returns.pdf`
- Broadie, M., Glasserman, P. & Kou, S. (1997). A Continuity Correction for Discrete Barrier Options. *Mathematical Finance* 7(4):325–349. {#ref:broadie-glasserman-kou-1997} — **[F]** · `broadie-glasserman-kou-1997-continuity-correction.pdf`
- Carr, P. & Wu, L. (2009). Variance Risk Premiums. *Review of Financial Studies* 22(3):1311–1341. {#ref:carr-wu-2009} — **[A]**
- Cboe Global Markets. Cboe S&P 500 Covered Combo Index (CMBO) Methodology. {#ref:cboe-cmbo} — **[A]** · https://cdn.cboe.com/api/global/us_indices/governance/CMBO_Methodology.pdf
- Chang, J. T. & Peres, Y. (1997). Ladder Heights, Gaussian Random Walks, and the Riemann Zeta Function. *Annals of Probability* 25(2):787–802. {#ref:chang-peres-1997} — **[A]** · [cite unverified]
- Coval, J. & Shumway, T. (2001). Expected Option Returns. *Journal of Finance* 56(3):983–1009. {#ref:coval-shumway-2001} — **[A]**
- Driessen, J., Maenhout, P. & Vilkov, G. (2009). The Price of Correlation Risk: Evidence from Equity Options. *Journal of Finance* 64(3):1377–1406. {#ref:driessen-maenhout-vilkov-2009} — **[A]**
- Gârleanu, N., Pedersen, L. H. & Poteshman, A. (2009). Demand-Based Option Pricing. *Review of Financial Studies* 22(10):4259–4299. {#ref:garleanu-pedersen-poteshman-2009} — **[A]**
- Goetzmann, W., Ingersoll, J., Spiegel, M. & Welch, I. (2007). Portfolio Performance Manipulation and Manipulation-Proof Performance Measures. *Review of Financial Studies* 20(5):1503–1546. {#ref:goetzmann-et-al-2007} — **[A]**
- Goyal, A. & Saretto, A. (2009). Cross-Section of Option Returns and Volatility. *Journal of Financial Economics* 94:310–326. {#ref:goyal-saretto-2009} — **[A]**
- Hill, J., Balasubramanian, V., Gregory, K. & Tierens, I. (2006). Finding Alpha via Covered Index Writing. *Financial Analysts Journal* 62(5):29–46. {#ref:hill-et-al-2006} — **[P]** · `hill-et-al-2006-finding-alpha-covered-index-writing.pdf` · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=935138
- Hull, J. C. (2021). *Options, Futures, and Other Derivatives*. 11th ed. Pearson. {#ref:hull} — **[A]** · [cite unverified]
- Israelov, R. & Nielsen, L. N. (2014). Covered Call Strategies: One Fact and Eight Myths. *Financial Analysts Journal* 70(6):23–31. {#ref:israelov-nielsen-2014} — **[F]** · `israelov-nielsen-2014-covered-call-one-fact-eight-myths.pdf` · https://www.aqr.com/Insights/Research/Journal-Article/Covered-Call-Strategies-One-Fact-and-Eight-Myths
- Israelov, R. & Nielsen, L. N. (2015). Covered Calls Uncovered. *Financial Analysts Journal* 71(6). {#ref:israelov-nielsen-2015} — **[P]** · `israelov-nielsen-2015-covered-calls-uncovered.pdf` · https://www.aqr.com/library/journal-articles/covered-calls-uncovered
- Israelov, R. & Tummala, H. (2017). Which Index Options Should You Sell? *Journal of Investment Strategies*. {#ref:israelov-tummala-2017} — **[A]** · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2990542
- Israelov, R. et al. Covering the World: Global Evidence on Covered Calls. AQR. {#ref:israelov-covering-the-world} — **[downloaded, unread]** · `israelov-et-al-covering-the-world-global-covered-calls.pdf` · [cite unverified] · *read owed by TODO I-1, before §03's subsection 2, which is otherwise all US index data*
- Janssen, A. J. E. M. & van Leeuwaarden, J. S. H. (2007). On Lerch's Transcendent and the Gaussian Random Walk. *Annals of Applied Probability* 17(2). {#ref:janssen-vanleeuwaarden-2007} — **[P]** · `janssen-vanleeuwaarden-2007-lerch-gaussian-random-walk.pdf`
- Kuang, X. & Lin, B. (2025). arXiv:2512.01123. {#ref:kuang-lin-2025} — **[P]** · `arxiv-2512.01123-wheel-bayesian-networks.pdf` · *cite as existence only — see TODO I-1; do not cite its figures as evidence*
- Li, ... & Zhang, ... Discretely Monitored First Passage Problems and Barrier Options. {#ref:li-zhang} — **[downloaded, skimmed]** · `li-zhang-discretely-monitored-first-passage-barrier-options.pdf` · [cite unverified] · *read owed by TODO II-23, before §07's autocallable pointer is written*
- Little, J. D. C. (1961). A Proof for the Queuing Formula: L = λW. *Operations Research* 9(3):383–387. {#ref:little-1961} — **[A]** · [cite unverified]
- Little, J. D. C. (2011). OR Forum — Little's Law as Viewed on Its 50th Anniversary. *Operations Research* 59(3):536–549. {#ref:little-2011} — **[P]** · `little-2011-littles-law-50th-anniversary.pdf`
- Merton, R. C. (1973). Theory of Rational Option Pricing. *Bell Journal of Economics and Management Science* 4(1):141–183. {#ref:merton-1973} — **[A]** · [cite unverified]
- Merton, R. C., Scholes, M. S. & Gladstein, M. L. (1978). The Returns and Risk of Alternative Call Option Portfolio Investment Strategies. *Journal of Business* 51(2):183–242. {#ref:merton-scholes-gladstein-1978} — **[F]** · `merton-scholes-gladstein-1978-call-option-portfolio-strategies.pdf`
- Merton, R. C., Scholes, M. S. & Gladstein, M. L. (1982). The Returns and Risks of Alternative Put-Option Portfolio Investment Strategies. *Journal of Business* 55(1):1–55. {#ref:merton-scholes-gladstein-1982} — **[F]** · `merton-scholes-gladstein-1982-put-option-portfolio-strategies.pdf`
- Muravyev, D. & Pearson, N. D. (2020). Options Trading Costs Are Lower than You Think. *Review of Financial Studies* 33(11):4973–5014. {#ref:muravyev-pearson-2020} — **[A]**
- Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance* 53:1775–1798. {#ref:odean-1998} — **[A]**
- Ross, S. M. *A First Course in Probability*. Pearson. {#ref:ross-first-course} — **[A]** · [cite unverified]
- Ross, S. M. *Introduction to Probability Models*. Academic Press. {#ref:ross-probability-models} — **[A]** · [cite unverified]
- Santa-Clara, P. & Saretto, A. (2009). Option Strategies: Good Deals and Margin Calls. *Journal of Financial Markets* 12:391–417. {#ref:santa-clara-saretto-2009} — **[A]** · `santa-clara-saretto-wp-good-deals.pdf` (working-paper version)
- Shefrin, H. & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance* 40(3). {#ref:shefrin-statman-1985} — **[A]**
- Siegmund, D. (1979). Corrected Diffusion Approximations. *Advances in Applied Probability* 11(4). {#ref:siegmund-1979} — **[A]**
- Siegmund, D. (1985). *Sequential Analysis: Tests and Confidence Intervals*. Springer. {#ref:siegmund-1985} — **[A]** · [cite unverified]
- Svozil, K. (2026). arXiv:2604.13334. {#ref:svozil-2026} — **[P]** · `arxiv-2604.13334-against-universal-trading-strategy.pdf`
- Whaley, R. E. (2002). Return and Risk of CBOE Buy Write Monthly Index. *Journal of Derivatives* 10(2):35–42. {#ref:whaley-2002} — **[A]** · https://www.pm-research.com/content/iijderiv/10/2/35
