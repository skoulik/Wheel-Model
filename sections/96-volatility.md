# Estimating the Volatility Process {#sec:volatility}

Part II's model holds the stock's volatility σ constant: one number for every price and every date. That is what lets a lot's depth describe its prospects completely, and it is a simplification. Real volatility moves, rises when prices fall, and is broken by jumps — days whose moves no normal distribution at the day's volatility would produce. The article carries a second model beside the constant one, in which volatility moves and the price jumps, and this appendix measures that model's process: which stocks, which data, what is measured on them, what the model is, how its parameters are found, how far they can be trusted, and what was left out.

The appendix relies on nothing but the notation of [the notation section](#sec:notation), and the rest of the article only uses what it finds. Every figure below is computed from public data by scripts in the article's repository; the last subsection says how to obtain the data and rebuild them.

## The stocks and the data

**The stocks.** The process is fitted to one kind of stock, the kind a covered-call operator writes on: large US companies with a long record of paying and raising dividends. The universe is the S&P 500 Dividend Aristocrats, the members of the S&P 500 that have raised their dividend for at least twenty-five consecutive years ([S&P Dow Jones Indices](#ref:spdji-aristocrats-methodology)), taken as the 68 names [ProShares' NOBL fund](#ref:proshares-nobl-holdings) held on 20 November 2026 and fixed there, so that the sample does not move as the index changes.

**The size rule.** A name's day counts only if its market capitalization that day was $10 billion or more. The rule is applied at each date rather than to today's size, because a company large now may have spent years small, and its small years behave like a small company's. A day's capitalization is the latest share count the company filed with the SEC on or before that day, put on today's split basis, times the day's split-adjusted close; before a company's first electronically filed count, about 2009 to 2011, its first count stands in.

**The prices.** Daily closes, dividends and splits come from [Yahoo Finance](#ref:yahoo-aristocrat-prices), from January 2005 to 20 November 2026. A day's return is the log of the close plus any dividend paid that day over the previous close,

r_t  =  ln( (P_t + D_t) / P_(t−1) )

so that the drop on an ex-dividend day, a known payment rather than news, is not counted as a move.

**The earnings dates.** A quarterly results announcement moves a stock for a known reason on a known day, and the model treats it as a scheduled event of its own, measured apart from everything else. Its dates come from [the SEC's EDGAR filings](#ref:sec-edgar): a US company announces results on a Form 8-K carrying Item 2.02, *Results of Operations and Financial Condition*, which exists from 23 August 2004. Some companies file more than one in a quarter, so the date kept is the last Item 2.02 filing in the sixty days before each quarterly or annual report. A quarter with none is left out whole — its announcement and its other days alike — rather than guessed, and so is the stretch after a company's last periodic report. A company reorganized under a new holding company keeps its predecessor's filings. The returns of the filing day and the day after are taken out of the sample, since a release can come before the open or after the close: 4,449 such windows, of which 38.2% move more than three robust standard deviations, against 4.7% of all other two-day windows.

**The sample.** What is left is 262,168 daily returns on the 68 names, about 1,040 name-years. Not every name contributes throughout: a company that crossed $10 billion recently counts only from then, and three that are below it today count for the years they spent above it.

**What the sample cannot contain.** The list is the index's members today. A company that left it — on a takeover, or on cutting its dividend, usually after a fall of exactly the kind this appendix measures — has no history here. Takeovers are rare: [Wikipedia's table of changes](#ref:wikipedia-aristocrats) names six over 2009–2025 against about 950 member-years in [S&P's own account of the index](#ref:valantasis-watts-2025), at least 0.6% of members a year. The dividend cutters are the larger omission, and the sample is tilted toward calmer histories by them; the last subsection returns to both.

## The yardstick, and why no day is called a jump

**Measuring a move against its own day.** A 3% fall means something different on a calm stock in a calm month and on a volatile one in a crisis. So every return is measured in units of its own local volatility — the typical size of a day's move just before it — and every statistic in this appendix is read in those units. That makes them comparable across names whose volatility differs, and across a simulated stock and a real one, since a name's own level cancels.

> **Detour: bipower variation.** The obvious local volatility is the standard deviation of the returns before the day. One large move in that window inflates it, and a later move measured against it looks smaller than it was. [Barndorff-Nielsen and Shephard](#ref:barndorff-nielsen-shephard-2004) replace the squared return with the product of two neighbouring absolute returns:
>
> σ̂²  =  (π/2) · mean over j of  |r_j| · |r_(j+1)|
>
> A single large move enters only multiplied by the ordinary moves beside it, so it barely moves the estimate, and for normal moves the factor π/2 — one over E|z|² for a standard normal z — makes it an estimate of the variance. Here the window is the sixty sessions before the return, the day itself never in it, with at least forty clean pairs.

This is [Lee and Mykland's](#ref:lee-mykland-2008) jump test run on daily closes: with no jump, a return over its bipower yardstick is standard normal. They admit windows of anything from √252 to 252 days for daily data; sixty is inside that range.

**What the tails show.** Counting the returns beyond c local standard deviations, on each side, against what a normal distribution would give on the same number of returns:

| c | 3.0 | 3.5 | 4.0 | 4.5 | 5.0 | 6.0 |
|---|---|---|---|---|---|---|
| up | 1,683 | 838 | 457 | 272 | 162 | 64 |
| down | 2,636 | 1,466 | 892 | 564 | 374 | 172 |
| normal, both sides | 708 | 122 | 16.6 | 1.8 | 0.2 | 0.0 |

There are far too many large moves, and more down than up. What there is not is a place where they change character. Each half standard deviation further out, the observed count falls by a factor of 1.6 to 1.9, where a normal tail falls by six to nine: the large moves thin out smoothly, with no threshold beyond which they become a different population. The conventional cut — Lee and Mykland's 1% critical value, 4.8 local standard deviations for one name's sixteen years of returns — would call 0.4 up and 0.9 down jumps a name-year at c = 4 and fewer at 4.8, and the jump rate would be whatever the threshold made it.

**So no day is labelled.** A sequential fit — flag the days beyond a threshold as jumps, fit the volatility on the rest — would make the jump rate a convention, and would split the rise in volatility after a large move between the jump and the ordinary response by fiat. Instead the volatility and the jumps are fitted together, by simulation: the model is run, and its parameters are those whose simulated returns reproduce what is measured on the data, each statistic computed identically on both. A threshold is then only the place a statistic is read. The next subsection says which statistics.

## What the data show

The fit asks a model to reproduce 48 statistics of the 262,168 returns, in six groups. Each is computed by the same code on the data and on a simulated sample of the same shape, and each is in local standard deviations or is a correlation, so no name's own level enters. Together they describe what a lot's owner meets: how often a large move comes, how large it is, what it does to the volatility that follows, and how long that lasts.

**The tails** (twelve statistics): the counts beyond 3, 3.5, 4, 4.5, 5 and 6 local standard deviations, a name-year, each side — the table above.

**The size of a large move, by the volatility of the day** (eight). Beyond 4 local standard deviations, the mean excess over the threshold, in each third of the volatility state — h = ln(local sd / the name's median local sd), so a calm day has h below zero and a turbulent one above — and the median excess over the mean, which is 0.69 for an exponential law. On the down side the excess is flat in local units, 1.29, 1.31 and 1.35 standard deviations from the calmest third to the most turbulent, while in log return it more than doubles, from 1.05% to 2.48%: a large fall scales with the volatility it falls in. The median is 0.61 of the mean on the down side and 0.62 on the up, so the excess has a heavier tail than an exponential's.

**What a move does to the volatility after it** (twelve). For each return, the log ratio of the volatility over the twenty sessions after it to that over the twenty before, averaged by the size of the day's move:

| the day's move, local sd | 0–1 | 1–2 | 2–3 | 3–4 | 4–6 | beyond 6 |
|---|---|---|---|---|---|---|
| up | −0.03 | 0.00 | +0.05 | +0.14 | +0.21 | +0.42 |
| down | −0.01 | +0.06 | +0.15 | +0.25 | +0.41 | +0.54 |

The rise grows smoothly with the move, and the largest moves sit on the same curve as the ordinary ones. A fall raises volatility more than a rise of the same size: a fall of four to six standard deviations multiplies the next month's volatility by e^0.41 = 1.5.

**Volatility month by month** (five). The standard deviation of a month's log volatility about the name's mean, 0.39; its autocorrelation from one month to the next, 0.57, and at three and six months 0.34 and 0.22; and the correlation of a month's return with the change in its log volatility, −0.24. A turbulent month tends to be followed by another, and a falling month tends to be a turbulent one.

**How long volatility remembers** (six). The autocorrelation of the size of a day's move, |r|, at 1, 5, 20, 60, 120 and 250 sessions: 0.25, 0.22, 0.15, 0.07, 0.05 and 0.02. A large move makes large moves more likely for months, and the memory fades slowly rather than at one rate.

**The leverage effect** (five). The correlation of a day's return with the mean size of the moves over windows after it — 1, 2 to 5, 6 to 20, 21 to 60 and 61 to 120 sessions ahead — which [Bouchaud, Matacz and Potters](#ref:bouchaud-matacz-potters-2001) introduced as the leverage function and found to decay over about 69 days for US stocks. Here it is −0.060, −0.076, −0.059, −0.027 and −0.019: a fall today predicts turbulence over the next weeks and, more weakly, months. It is measured with |r| rather than their r², so that a single crash cannot carry it.

One fact the fit does not use, because a model of one stock at a time cannot reproduce it: about half the large falls are shared. Of the moves beyond four standard deviations, 51% of the falls and 31% of the rises came on a day the S&P 500 itself moved beyond three.

## The model, and why each part

The model steps one stock a session at a time. Its log volatility is the sum of two factors, H = h_f + h_s, a fast one and a slow one, and the session's volatility is σ_t = σ̄·e^H, with σ̄ a scale set below. A session's log return is

r_t  =  c_t  +  σ_t · z_t  +  σ̄ · e^(β·H_t) · J_t

with z_t a standard normal shock and J_t a jump: up jumps arrive at a rate of λ↑ a year, each exponential in size with mean a↑, and down jumps at λ↓ a year with mean a↓, at most one a session. Each factor decays toward zero and is pushed by the session's move:

h_f′  =  φ_f · h_f  +  w_θ · θ · x_t  +  w_κ · κ↓ · [down jump]
h_s′  =  φ_s · h_s  +  (1 − w_θ) · θ · x_t  +  (1 − w_κ) · κ↓ · [down jump]

where x_t is the whole move in local standard deviations, its jump included, and [down jump] is one on a down-jump session and zero otherwise. The parameters, all fitted:

- **φ_f and φ_s**, each factor's daily persistence, quoted as half-lives: the number of sessions in which a factor's distance from zero halves.
- **θ**, how far one local standard deviation of the day's move pushes log volatility; negative, so a fall raises volatility and a rise lowers it. w_θ is the fast factor's share of that push.
- **κ↓**, the further rise in log volatility on the day of a down jump, the kick; w_κ is the fast factor's share of it.
- **λ↑, λ↓, a↑, a↓**: how often each kind of jump comes and how large it is on average, in units of σ̄·e^(β·H).
- **β**, how a jump's size grows with the volatility it arrives in: β = 1 would keep it a fixed number of local standard deviations, β = 0 a fixed log return. Measured in local standard deviations, a jump is e^((β − 1)·H) times its size in the model's units.

Two things are set rather than fitted. c_t is the drift that makes each session's expected gross return exactly e^(m·Δt), whatever the state, so the price drift is the article's m and the jumps only redistribute around it. And σ̄ is the scale at which the year's total variance — diffusion, jumps and earnings together — averages σ², so the article's σ remains the stock's whole volatility.

**Where each part comes from, and what each is up against.** The response of log volatility to the day's move is [Nelson's](#ref:nelson-1991): θ·z + γ·(|z| − E|z|), a direction term and a size term. Two factors at different speeds are [Chernov, Gallant, Ghysels and Tauchen's](#ref:chernov-gallant-ghysels-tauchen-2003), who rejected every one-factor model of the Dow. A volatility that jumps with the price is [Eraker, Johannes and Polson's](#ref:eraker-johannes-polson-2003) on the S&P 500, and [Todorov and Tauchen](#ref:todorov-tauchen-2011) found price and volatility jumps arriving together; that the kick follows only the falls is [Patton and Sheppard's](#ref:patton-sheppard-2015) finding on the S&P 100's stocks, negative jumps raising future volatility and positive ones lowering it. The jump law is [Kou's](#ref:kou-2002) double exponential. The model began larger than the one above — a size term γ, shocks of each factor's own, a feedback of a factor on its own volatility as Chernov and colleagues have it, a kick after up jumps, a heavier-tailed size law on each side, a β for each — and each part was kept only if the data asked for it. The test is the fit's distance, the sum over the 48 statistics of each squared miss over its variance (the next subsection), which for an adequate model is about 48 less the number of parameters: a part stays when removing it raises the distance by clearly more than one for each parameter it removes.

| change | parameters | distance |
|---|---|---|
| one factor instead of two | the same 14 | +27 |
| γ, the up-jump kick, the up-jump shape and a second β removed | −4 | −2.2 |
| each factor's own shocks removed | −2 | +0.6 |
| the down-jump shape made exponential | −1 | −0.4 |
| the fast factor's feedback added | +1 | +0.2 |

One factor fails where the wheel lives. A single state cannot be quick over a week and persistent over half a year at once: its fit read the six-month persistence at 0.07 against the data's 0.22, and the leverage function at 21 to 60 sessions at −0.051 against −0.027, each more than two standard errors out. Everything else removed cost no more than its count. γ in particular is not needed once the kick is in: the rise after a large fall is the kick's, not a size effect's. And no factor needs shocks of its own — volatility here moves only when the price does. Chernov and colleagues needed feedback for one index over 1953 to 1999 with no jumps in their model; here the jumps and the kick do its work.

## The fit

The parameters are found by the simulated method of moments of [Duffie and Singleton](#ref:duffie-singleton-1993): for a candidate set, simulate the model, compute the 48 statistics on the simulated returns exactly as on the data, and choose the set that brings the two closest.

> **Detour: the simulated method of moments.** When a model's statistics have no formula — and these, read through a yardstick, on series with gaps, do not — they can still be computed on the model's own output. The method makes that the estimator: the distance between data and model is a weighted sum of squared misses,
>
> D(parameters)  =  Σ over the statistics of  ( simulated − data )² / variance
>
> each statistic's miss measured against how precisely the data determine it, and the estimate is the parameter set that minimizes D. If the model is right and the variances are right, D at the true parameters is a sum of squared standard normal misses, about one for each statistic less one for each parameter fitted; a value far above that says the model cannot reproduce the data, whatever its parameters.

**The simulated sample has the data's shape.** Each evaluation simulates eight replicas of the whole universe, and each replica copies the data's structure exactly: a path for every name, as long as that name's history, blank wherever its data is — the earnings windows, the undated quarters, the years below $10 billion. A short series estimates a slow autocorrelation with a bias, and a gap breaks the windows a statistic is read over; since the simulation has the same short series and the same gaps, it is biased the same way, and the comparison is like for like with nothing to correct. The eight replicas' statistics are averaged before they are compared.

**The draws are fixed.** Every evaluation uses the same random numbers, so a small change in the parameters makes a small change in D, and the search is not chasing noise.

**The search** is the simplex method of [Nelder and Mead](#ref:nelder-mead-1965), which needs no derivatives: a simplex of one more point than there are parameters moves across the surface by reflecting its worst point through the others, stretching when that helps and shrinking when it does not. In a dozen dimensions the standard method spends nearly all its steps on reflections, and [Gao and Han's](#ref:gao-han-2012) coefficients, which depend on the dimension, are used instead. A search runs from the start and once more from its own end with a larger simplex, each pass ending when the best D has improved by less than 0.05 over 600 evaluations.

## The weights

A distance is only as honest as the variances it divides by, and getting them right was the hardest part of the fit.

**The obvious variance is wrong by a factor of thirteen.** The natural way to say how precisely the data determine a statistic is to resample the names — draw 68 from the 68 with replacement, recompute, repeat — which treats each name's history as an independent draw. They are not independent. The names live through the same years: 2008 is in every series at once, and so is March 2020. Resampling names cannot see that, and it understated each statistic's variance by a median factor of 13, and by 20 to 100 at the long lags, where the shared episodes dominate. It was caught by splitting the sample in time: with names resampled, the halves before and after 2016 differed by a distance of 645 over the 48 statistics, where honest variances would put it near 48.

**A calendar-block jackknife instead.** Each statistic's variance is estimated by deleting every name's returns in one two-year calendar block together, recomputing, and repeating for each block — a block jackknife, after [Künsch](#ref:kunsch-1989), with the blocks cut by calendar so that a shared episode leaves the sample whole. [Petersen](#ref:petersen-2009) makes the same point for panels in finance: when observations share a time effect, clustering by time is what keeps the standard errors honest. The variance used is the larger of the jackknife's and the names' — the names' is the larger for a few size statistics — and it is floored by the model's own sampling variance, the spread of each statistic across the replicas, plus the simulation's noise. The floor matters where a statistic rests on a handful of events: on the S&P 500, a single series with few moves beyond six standard deviations, the jackknife put the variance of the rise after them near 10⁻²⁰, and one statistic would otherwise have carried the whole distance.

**Checked on a sample where the answer is known.** On returns simulated from a fitted model, with the names independent by construction, the calendar jackknife gives about the names' variance (a median ratio of 1.11), so the thirteenfold inflation on the real data is the shared episodes, not the method. And the distance at the true parameters on that sample is 30.5 over 48 statistics, where a model with 18 parameters should score about 30: the weights are calibrated.

**Eleven blocks is few.** Two-year blocks over twenty-two years give eleven, and both Künsch and Petersen warn that a variance from so few clusters is itself uncertain. Re-weighted with one-year blocks or three-year ones, without refitting, the final model's distance is 9.8 or 11.3 against 13.5, every parameter stays determined, and its standard errors move by up to a fifth — 1.08 to 1.20 times the two-year blocks' with one-year blocks, 0.94 to 1.08 with three. The errors quoted below should be read as uncertain by about that much.

## The fitted process

The final model has eleven parameters. Its distance is 13.6 over the 48 statistics, where an adequate model with eleven would score about 37, and no statistic misses by more than 1.3 of its standard errors. The standard errors are the simulated-moments sandwich, with the statistics' covariance taken as diagonal, so they are approximate in a second way as well as the first:

| parameter | estimate | standard error |
|---|---|---|
| fast factor's half-life | 6.1 sessions | 2.4 |
| slow factor's half-life | 104 sessions, about five months | its ratio to the fast, 16.9 ± 5.4 |
| θ, log volatility per local sd of the day's move | −0.0288 | 0.0073 |
| w_θ, the fast factor's share of θ | 0.71 | 0.12 |
| κ↓, the kick after a down jump, in log volatility | +0.631 | 0.066 |
| w_κ, the fast factor's share of the kick | 0.69 | 0.09 |
| λ↑, up jumps a year | 1.36 | 0.55 |
| a↑, their mean size, units of σ̄·e^(β·H) | 1.77 | 0.62 |
| λ↓, down jumps a year | 6.34 | 1.07 |
| a↓, their mean size, units of σ̄·e^(β·H) | 2.02 | 0.57 |
| β, jump sizes' growth with volatility | 0.58 | 0.32 |

**Read plainly.** A stock's log volatility is the sum of a part that halves in about six sessions and a part that halves in about five months. Neither moves on its own: each session's move pushes them, a fall of one local standard deviation raising log volatility by 0.029 — seven tenths of it into the fast part — and a rise lowering it by as much. A down jump, six or seven a year, raises it by a further 0.63, multiplying volatility by e^0.63 = 1.9, and two thirds of that is gone within a few weeks. An up jump, one or two a year, moves volatility only through θ. Jumps grow with the volatility they arrive in, but less than in proportion, so in local terms they are largest in calm months: at the fitted model's median state, H = 0.82, a down jump averages 1.4 local standard deviations beyond the day's ordinary move and an up jump 1.3; in the calmest twentieth of sessions 1.8 and 1.6, in the most turbulent twentieth 1.0 and 0.9. (H = 0 is not the typical state: σ̄ is a scale, and the stationary H sits above zero because falls and their kicks push it up more often than rises pull it down.)

**Are the parameters identified?** A fit is believed only if it can find parameters it already knows. Returns were simulated from a fitted model — the final one with each factor's own shocks still free, fourteen parameters — and fitted again, on three fresh samples, the search started at the truth. Every parameter came back near it without visible bias, and with a spread across the samples at or below the sandwich standard error computed on a simulated sample — so those errors are not too small, if anything conservative. On a simulated sample they are three to four times smaller than on the data, which is the factor of √13 the shared episodes put on the real names and the simulated ones do not have; the errors to quote are the data's. Started instead 30% away from the truth, the search stalled well above it. That is a statement about Nelder and Mead's method in a dozen dimensions with nearly flat directions, not about the model, and it is why every fit here was started from the previous one's end.

**Large names and smaller ones.** Fitted apart — the 50 names above $20 billion today and the 18 between $10 and $20 billion, with the down-jump size law left free in both — the two groups share the model and nearly every parameter:

| | all 68 | over $20 billion | $10–20 billion |
|---|---|---|---|
| distance over 48 | 14.0 | 10.5 | 25.5 |
| fast / slow half-life, sessions | 5.7 / 88 | 6.3 / 102 | 5.8 / 109 |
| θ | −0.026 ± 0.007 | −0.033 ± 0.008 | −0.012 ± 0.005 |
| down jumps a year | 6.5 ± 1.8 | 6.1 ± 1.0 | 7.1 ± 1.3 |
| the down-jump kick | 0.645 ± 0.058 | 0.655 ± 0.072 | 0.512 ± 0.062 |
| up jumps a year | 1.2 ± 0.55 | 1.35 ± 0.42 | 0.87 ± 0.20 |
| β | 0.56 ± 0.23 | 0.61 ± 0.29 | 0.65 ± 0.27 |

The one difference near two standard errors is the leverage effect, weaker among the smaller names (−0.012 against −0.033, a difference of 0.021 ± 0.010), and their kick is a little smaller. The pooled parameters stand for the whole universe.

**A single stock is not the index.** The same model fitted to the S&P 500's own returns, each factor's own shocks left free, scores 14.0 over 48 and has half-lives of 6.0 and 114 sessions, θ = −0.070 — two and a half times a single stock's — and a smaller kick, 0.42. The statistics say the same directly. The index's monthly log volatility swings with a standard deviation of 0.47 against the stocks' 0.39, keeps 0.66 of a month's level into the next against 0.57, and moves against the month's return with a correlation of −0.42 against −0.24; its leverage function is 1.6 to 2 times as deep at every lag. A single Aristocrat's volatility swings less, forgets faster, and answers its price about half as strongly as the index's — the contrast [Bouchaud, Matacz and Potters](#ref:bouchaud-matacz-potters-2001) drew between stocks and indices, found again on these names. A volatility process borrowed from the index would overstate all three for the stocks the wheel is run on.

## Earnings

**A scheduled jump.** An earnings release is a jump whose date is known, and it needs no simulation to be found: each date's move is measured and its law fitted directly. The move is the log return over the two sessions from each EDGAR date — the filing day and the next, so that results released before the open and after the close are both caught — with any dividend added back, in units of the yardstick of the sixty clean sessions before it. On the 4,322 dated windows whose three closes are all in the sample, its mean absolute size is 2.85 local standard deviations, where two sessions of ordinary moves alone would give 1.13.

**Its law** is Kou's again: two sessions of diffusion and one jump, up with probability p and exponential in size with mean a_E↑, down otherwise with mean a_E↓, its size growing with the volatility state h as e^((β_E − 1)·h) in local units:

s  =  √2 · z  +  e^((β_E − 1)·h) · Y

A normal plus an exponential has a density in closed form, so the law is fitted by maximum likelihood, its standard errors by the same calendar-block jackknife as the fit's weights, since an earnings season is shared too. Up with probability 0.516 ± 0.017, the mean up size 2.36 ± 0.13 local standard deviations and the mean down size 2.63 ± 0.16, β_E = 0.13 ± 0.12. Its tails match the data's:

| beyond, local sd | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|
| windows up, data / fitted | 26.8 / 25.4% | 18.0 / 16.9% | 11.9 / 11.1% | 4.9 / 5.0% | 2.0 / 2.4% |
| windows down, data / fitted | 26.1 / 25.2% | 18.8 / 17.4% | 12.8 / 11.9% | 5.6 / 5.8% | 2.8 / 2.9% |

**Its size barely follows the volatility.** By the calm, middle and turbulent third of the state, the mean absolute move is 3.49, 2.85 and 2.19 local standard deviations — falling in local units, so in log return an earnings move is nearly the same size in a calm quarter as in a turbulent one. A law that scales with volatility as the unscheduled jumps do (β_E = 0.58) is rejected by a likelihood ratio of 65, one that scales in proportion (β_E = 1) by 249. Utilities and REITs move about half as much as the rest, a mean of 1.74 and 1.57 local standard deviations against 2.94; they are 325 of the 4,322 windows, and the model carries the pooled law.

**In the model's own units.** The model scales the earnings jump by e^(β_E·H), H its own log volatility, not by a yardstick estimated from sixty noisy sessions. The law it carries is the one that, put into simulated samples of the fitted model with the data's dates and gaps and fitted exactly as the data are, gives back the data's estimates: up with probability 0.523, mean sizes 4.73 and 5.22 in units of σ̄·e^(β_E·H), β_E = 0.25. The sizes are about double the yardstick's because H = 0 is not the typical state, and β_E comes out larger because the yardstick's noise attenuates a slope measured against it.

**No kick, and why.** After an ordinary fall beyond six local standard deviations log volatility rises by 0.54; after an earnings fall that size, by 0.16. After ordinary rises it climbs 0.14 to 0.42 as the rise grows; after earnings rises it moves between −0.04 and +0.06. Measured that way, an earnings move looks unlike any other. But a six-sd move is a large surprise on an ordinary day and a modest one on an earnings day, whose typical move is 2.84 local standard deviations against 0.81. [Ederington and Lee](#ref:ederington-lee-1996), studying implied volatility around scheduled macroeconomic releases, found that scheduled news resolves uncertainty where unscheduled news creates it, and that volatility answers the *unexpected* part of a day's move the same way whichever kind of day brought it. Measured against its own kind's typical size, the same holds here:

| fall, times its kind's typical move | 1–1.5 | 1.5–2 | 2–3 | 3–5 |
|---|---|---|---|---|
| rise in log volatility after an earnings fall | +0.013 ± 0.032 | +0.077 ± 0.018 | +0.162 ± 0.047 | +0.200 ± 0.064 |
| after an ordinary fall | +0.029 ± 0.007 | +0.065 ± 0.010 | +0.108 ± 0.016 | +0.214 ± 0.045 |

Earnings and ordinary moves agree within an error at every size with enough events, falls and rises alike. So the expected part of a scheduled move leaves volatility where it was, and the surprise raises it as any surprise does; the principle and the decomposition are Ederington and Lee's, here in a single stock's realized volatility. That the build-up and the resolution are the rule is old: [Patell and Wolfson](#ref:patell-wolfson-1981) saw implied volatility rise into earnings and fall after, with realized variance back near normal two days later, and [Dubinsky, Johannes, Kaeck and Seeger](#ref:dubinsky-et-al-2019) price earnings as jumps at known dates whose variance leaves the options once the date has passed. A surprise against analysts' forecasts would need data EDGAR does not carry; the price's own reaction is the measure used here. And not all of a release's effect stays with the firm that released it: [Christensen, Timmermann and Veliyev](#ref:christensen-timmermann-veliyev-2024) find that announcements raise the chance of jumps in firms that announced nothing, which a model of one stock at a time leaves out.

**An earnings term, measured and left out.** The model does not feed an earnings move to its volatility factors at all, and so misses both halves of that decomposition: a small fall in volatility after mild earnings moves (−0.051 ± 0.014 in log volatility, against the model's −0.003) and a small rise after large ones (+0.156 ± 0.040 against +0.051). A term that would close the gap — log volatility falling by c₀ at each release, for the uncertainty resolved, and rising by c₁ for each unit of surprise beyond the typical move — fits at c₀ = 0.059 and c₁ = 0.064. Run in the article's wheel with the term on and off, on the same simulated paths, over thirty years:

| on less off | |
|---|---|
| true excess return | +0.4 ± 0.1 basis points |
| lots held | −0.008 ± 0.005, or −0.07% |
| up-beta, down-beta | −0.001, 0.000 |
| gaps at assignment beyond 5%, beyond 10% | +0.03, +0.015 points |

For a strategy that holds its options for weeks, the fall at the release and the rise after a surprise very nearly cancel. The model leaves the term out, and this table is why.

## Fair prices on the fitted process

A process for the stock is half of what an option model needs; the other half is a price for every option at every state. Here "fair" means priced as if the market charged only for the stock's own diffusive risk. The drift of the ordinary shock z is moved from the real world's to the risk-free rate's, and nothing else changes: jumps arrive at their real-world rates and sizes, and earnings at their real-world law, which is [Merton's](#ref:merton-1976) assumption for jumps that carry news specific to one firm. Whatever the market charges beyond that, for volatility, for jumps or for earnings, is then an edge to be measured — the question [the returns section](#sec:returns) asks of the volatility risk premium — rather than something the model assumes.

**One shift prices everything.** Because neither volatility factor has shocks of its own, the only source of diffusive risk is z, and moving the drift from μ to r takes a single shift of its mean, (μ − r)·Δt/σ_t each session. The factors are functions of the price path and follow the shifted shocks; the jumps keep their real-world law, and the drift c_t keeps the expected return at the measure's.

**The prices are tabulated.** An option's fair value depends on the two factors, the strike's distance from the price, the time left and where the earnings calendar stands, and has no formula, so it is computed once by simulation from every node of a grid in the two factors and tabulated, with values between nodes interpolated. Two variance reductions from [Glasserman](#ref:glasserman-2003) do most of the work: each path's total shock is stratified, so that the draws cover its distribution evenly, and the terminal price serves as a control variate with its regression coefficient. Together they bring a put's price to within 0.07% in implied volatility, and a near-the-money call's to within 0.05%. The interpolation is cubic: log implied volatility is convex in the state, and a linear one priced every option about 0.1% high.

**Two exact tests.** The article tests its model by two identities that hold at fair prices whatever the strategy does. Under the pricing measure the wheel earns the risk-free rate, less only the tax withheld on its dividends; under the real-world measure it earns, beyond the risk-free rate, the stock's excess return times the book's delta averaged over each option's life, less the same tax (the identity of [eq:delta-return](#eq:delta-return)). On the fitted process the delta gains a second channel. An option's value moves with volatility as well as with the price, and here volatility moves with the price, so an option's exposure to the stock is its price delta plus its vega times how far a unit of the price's move moves the factors. Both identities hold on the fitted process within the simulations' errors, the second only once the volatility channel is counted.

## What is left out, and why

Four things a fuller process would have, each left out on evidence rather than for convenience.

**Takeovers.** A cash bid pins a stock's price and pays out a position wherever it stands — an exit no part of this process has. Among these companies takeovers are rare, at least 0.6% of members a year by the count above; and none of the data's large up jumps is followed by the collapse in volatility that marks a price pinned by a bid, so none has been cleaned from the sample.

**The companies that left.** The universe is today's members. Those that left on a dividend cut, usually after the kind of fall the jumps measure, are missing, and the process is fitted to the survivors' histories. Bringing them back for their member years needs S&P's own record of the index's removals, which its published documents count but do not list; until then the jump rates here are best read as a floor.

**A constant jump rate.** Large moves cluster: after a move beyond three, four or five local standard deviations, another follows within twenty sessions three to six times as often as after an ordinary day. [Maheu and McCurdy](#ref:maheu-mccurdy-2004), fitting eleven US stocks, made the jump rate itself depend on its own past for that reason. Here the rate is constant, and the fitted model reproduces most of the clustering anyway, through the volatility its kicks raise:

| another move beyond c within 20 sessions, against an ordinary day's | after a fall: data | model | after a rise: data | model |
|---|---|---|---|---|
| c = 3 | 2.80 ± 0.90 | 2.59 | 2.03 ± 0.70 | 1.68 |
| c = 4 | 4.93 ± 2.47 | 3.54 | 3.14 ± 1.51 | 2.01 |
| c = 5 | 6.17 ± 3.87 | 4.51 | 5.38 ± 2.16 | 2.02 |

The data sit above the model at every threshold, each within 1 to 1.6 standard errors, and the six together would add 3.7 to the distance, about what six well-fitted statistics should. The data do not call for a self-exciting rate; the loosest point is after rises beyond five. (Maheu and McCurdy also found a jump feeding volatility less than an ordinary move of the same size, which runs against the kick here. Their volatility is a GARCH variance fed by the whole day's innovation, a different construction from this one's, and the two findings are not directly comparable; the kick here is what the data's own statistics ask for.)

**Jumps shared across stocks.** About half the large falls came on days the index itself moved beyond three standard deviations. [Merton](#ref:merton-1976) assumed a jump carries news specific to one firm, and a model of one stock at a time can only make that assumption. For one stock it costs nothing; for a book of several it is the first thing to revisit, since the falls that arrive together are the ones a diversified book cannot spread.

The earnings term is the fifth, and the subsection on earnings measured what leaving it out costs.

## Rebuilding the data

The scripts that produced this appendix will not run forever; the data they read will stay obtainable. So what follows describes first what to obtain and what is done to it, in terms independent of any script, and then the commands that do it today.

**What to obtain.**

1. **The companies.** The 68 names ProShares' NOBL fund held on 20 November 2026, each identified by its SEC central index key, with its predecessor's for the three reorganized under a new holding company (Exxon Mobil, Linde, Medtronic).
2. **Each company's filing history** from EDGAR: every filing's form, date and, for an 8-K, its item codes. The earnings date of a quarter is the last 8-K carrying Item 2.02 in the sixty days before the quarter's 10-Q or 10-K; a quarter with none, and the stretch after the last periodic report, are left out.
3. **Each company's shares outstanding** over time, from EDGAR's XBRL filings: the cover-page count (`dei:EntityCommonStockSharesOutstanding`), or the basic weighted-average count for companies that report shares by class.
4. **Daily prices** from January 2005 to 20 November 2026: the close, each dividend on its ex-date, and each split, from any vendor that gives all three on one split basis.
5. **The S&P 500's total-return index** over the same days, for the shared-jump count and the index's fit.

**What is done to them.** Each day's market capitalization is the latest share count on or before it, put on the current split basis, times the split-adjusted close; a day counts if that is $10 billion or more. Returns are r = ln((P_t + D_t)/P_(t−1)) on split-adjusted closes, kept when both sessions count and neither is in an earnings window — the date's session and the next. The yardstick is bipower variation over the sixty sessions before, with at least forty clean pairs; the 48 statistics are read in its units; the weights are the calendar-block jackknife over two-year blocks.

**The commands today**, from the repository's root, in order:

    WHEEL_EDGAR_CONTACT="Name email@example.com" python code/earnings.py
    python code/jumps.py
    python code/earnmoves.py --recover --feedback
    python code/volfit.py --no-feedback --start data/aristocrats/volfit-final.json \
        --fix gamma=0 --fix "k up=1" --fix "k down=1" --fix "kick up=0" \
        --fix "eta fast=0" --fix "eta slow=0" --tie "beta up=beta down" --tag final
    python code/volfit.py --se FILE      # FILE: the fit the line above wrote

The first fetches the filings and the prices into `data/aristocrats/` — EDGAR asks an automated client to name a contact — and reports each company's coverage; the second prints the data's statistics and jumps; the third the earnings law; the fourth refits the model, which takes some hours; the fifth gives its standard errors. With the data present, `python code/verify_examples.py` checks every figure in this appendix against them.

**What a rebuild can and cannot change.** Vendors revise their histories and change how they present them, so a rebuild months later may move the last digit of a statistic. The fit's parameters, which the rest of the article uses, are pinned in the code and do not move with the data; the checks on the data's statistics are set at the precision quoted here. A difference beyond that is a question about the data or the scripts, and the fundamentals above are what to check them against.
