# The Wheel Strategy as a Stochastic Inventory System

*Sergei Kulik*

> **⚠️ Working draft.** This is an article in active development. Formulas, numbers, and conclusions may change as open issues are resolved — see [TODO.md](TODO.md) for what is known to be incomplete. Nothing here is investment advice.

A mathematical model of the "wheel" options strategy — repeatedly selling cash-secured puts on fundamentally sound assets, taking assignment when it comes, and selling covered calls until the stock is called away — framed as a stochastic inventory system. Put assignments are arrivals into an inventory of stock lots; call-aways are departures; the machinery of queueing theory answers how much stock the strategy really holds, how much capital it consumes, and when it stops being self-recycling.

The end product will be a LaTeX article for a general, numerate audience.

## Layout

| Path | Contents |
|---|---|
| `sections/` | The article, one Markdown file per section, numbered in reading order. `00-notation.md` is the glossary and single source of truth for symbols; `98-bibliography.md` is the same for references. |
| `code/` | Supplementary scripts. `verify_examples.py` recomputes every worked numerical example quoted in the text. |
| `TODO.md` | Open modeling and writing issues, grouped by article part. |
| `DONE.md` | Completed work, resolved questions, and what is deliberately out of scope. |
| `drafts/` | Historical drafts, superseded by `sections/` — the initial draft contains a since-corrected P&L formula. Also `tranche-record.md`, the one living file there: the account's statements as they arrive, and the path of every headline figure across them. |

## Verifying the numbers

Every worked example in the article is machine-checked:

```
python code/verify_examples.py
```

Python 3.8+, standard library only.

## License

The article text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the code under `code/` is licensed under MIT. See [LICENSE.md](LICENSE.md).

## Status

The article is in four parts. **Part I (setup)** and **Part II (one asset)** are written: the model has a single state variable — a lot's *depth* below its own frozen call strike — and the entry law, holding time, standing inventory, returns, three stability boundaries and the capacity of an account with a finite balance all follow from that one random walk. **Part III (portfolios and correlation)** and **Part IV (verification, the live account, outlook)** are not yet written, and the abstract and prior-work survey are written last; see [TODO.md](TODO.md).

A prior-work literature pass on 2026-07-31 confirmed the article's central economic claim from three independent directions, and reopened Part II with four outstanding items, all of them in the returns section. Two are corrections: the volatility risk premium is currently quoted at its **index** level where this model is single-name, and the one implied volatility the article carries has no tenor axis. Two are additions, including the article's first risk statistic. Until those close, treat the returns section's volatility-premium figures as under revision.
