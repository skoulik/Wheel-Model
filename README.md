# The Wheel Strategy as a Stochastic Inventory System

*Sergei Kulik*

> **⚠️ Working draft.** This is an article in active development. Formulas, numbers, and conclusions may change as open issues are resolved — see [TODO.md](TODO.md) for what is known to be incomplete. Nothing here is investment advice.

A mathematical model of the "wheel" options strategy — repeatedly selling cash-secured puts on fundamentally sound assets, taking assignment when it comes, and selling covered calls until the stock is called away — framed as a stochastic inventory system. Put assignments are arrivals into an inventory of stock lots; call-aways are departures; the machinery of queueing theory answers how much stock the strategy really holds, how much capital it consumes, and when it stops being self-recycling.

The end product will be a LaTeX article for a general, numerate audience.

## Layout

| Path | Contents |
|---|---|
| `sections/` | The article, one Markdown file per section, numbered in reading order. `00-notation.md` is the glossary and single source of truth for symbols, and `98-bibliography.md` the same for references. `97-derivations.md` holds the longer derivations; `99-reproduction.md` is generated, listing every figure the text quotes with the command that reproduces it. |
| `figures/` | The article's graphs, as SVG, drawn by the same code that computes their numbers and regenerated rather than edited. |
| `code/` | `model.py`, the analytic model and the only place a formula is defined. `wheel_sim.py`, an independent Monte Carlo simulation of the strategy that shares none of the model's machinery, so that agreement between them is evidence rather than arithmetic. `verify_examples.py`, which recomputes every worked example in the text. `lattice.py`, which carries the moving volatility into `model.py` (see *Status*). And the scripts behind the volatility calibration. |
| `TODO.md` | Open modeling and writing issues, grouped by article part. |
| `DONE.md` | Completed work, resolved questions, and what is deliberately out of scope. |
| `drafts/` | Historical drafts and plans, superseded by `sections/` — the initial draft contains a since-corrected P&L formula. Three files there are still growing: `tranche-record.md`, the live account's statements as they arrive and the path of every headline figure across them; and `2026-11-21-moving-volatility-plan.md` and `2026-11-22-model-moving-volatility-plan.md`, the modelling work now under way. |

## Verifying the numbers

Every worked example in the article is machine-checked, and so is the apparatus around it — citations, cross-references, the figures against a fresh drawing, and the reproduction appendix:

```
python code/verify_examples.py
```

It takes about five minutes. Python 3.8+. The model itself needs only the standard library, and uses numpy when it is installed; the figures need matplotlib, and are reported as skipped without it. The volatility calibration requires numpy, and on its first run fetches its data from SEC EDGAR and Yahoo Finance; EDGAR asks automated clients to identify themselves, so set `WHEEL_EDGAR_CONTACT` to a name and an e-mail address. The model with moving volatility requires numpy too, and reads lattices simulated once per set of parameters and cached under `data/lattice/`: `python code/lattice.py` builds the running example's in about twenty minutes, and until then its checks are reported as skipped.

## License

The article text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the code under `code/` is licensed under MIT. See [LICENSE.md](LICENSE.md).

## Status

The article is in four parts. **Part I (setup)** and **Part II (one asset)** are written: the model has a single state variable — a lot's *depth* below its own frozen call strike — and the entry law, holding time, standing inventory, returns, three stability boundaries and the capacity of an account with a finite balance all follow from that one random walk. **Part III (portfolios and correlation)** and **Part IV (verification, the live account, outlook)** are not yet written, and the abstract and prior-work survey are written last; see [TODO.md](TODO.md).

**Under way: volatility that moves, and jumps** (TODO II-40, planned in [`drafts/2026-11-21-moving-volatility-plan.md`](drafts/2026-11-21-moving-volatility-plan.md)). Part II assumes one constant volatility, and that assumption is what lets a lot's depth describe its prospects completely. Real volatility moves, and moves with the price, and that is most of why published covered-call indices show an up-market beta of 0.46 where the model, at one volatility, gives 0.17: with volatility moving as the S&P 500's does, it reaches 0.38. So the model is being extended:

- **Calibrated on the kind of stock the strategy trades.** The universe is the S&P 500 Dividend Aristocrats, each name counted only on days its market capitalization was $10 billion or more, with earnings dates taken from SEC filings.
- **Fitted by simulation.** Daily moves show no threshold at which ordinary moves give way to jumps, so the volatility and the jumps are fitted together, by the simulated method of moments: the model is simulated, and its parameters are those whose simulated paths reproduce 48 statistics measured on the data in exactly the same way. One finding on the way: weighting those statistics by resampling the stocks understated their noise thirteen-fold, because the stocks share their bad years (2008, 2020), and made a good model look rejected.
- **The fitted model.** Volatility has two parts, one fading over about a week and one over about five months. It is moved only by the stock's own moves: a fall raises it, and a downward jump nearly doubles it. Jumps go both ways, and earnings bring a move of their own every quarter, which raises volatility no further. A single stock's volatility swings less, forgets faster and responds to the price about half as strongly as the S&P 500's, so the article's earlier borrowing of the index's figures overstated the effect.
- **What moves.** Measured in the simulator with every option priced fair at the volatility of the day, most of Part II's results hold within a few percent: the excess return, the assignment rate, the median holding time. What moves is the tail of the gap at assignment — the loss a lot is born with, the cost an operator feels — whose share beyond 5% triples, and the boundary at which the strategy's capital stops coming back, which tightens. So Part II will carry both: the constant-volatility model, which explains the mechanism, and the moving one's figures beside it.
- **The model carries it.** `model.py` now runs the moving volatility on a lattice: a lot's depth, the two volatility factors and the week of the earnings calendar, its transitions and prices simulated once from every volatility state (`code/lattice.py`), and each put's sale and its lot's first call period simulated exactly. It agrees with the simulator's figures within both models' errors, and on the way it found six shortcomings in the simulator: four now fixed (the volatility scale σ̄, the capital boundary's Jensen term, the order of its same-day events, and the units of its sampled delta) and two traced and awaiting a decision (its fair-price tables' grid, and how it samples the delta's volatility channel).
- **Next.** Part II's sections are revised to carry both models' figures, with the estimation described in an appendix of its own, and every section re-read in full.
