# The Wheel Strategy as a Stochastic Inventory System

> **⚠️ Working draft.** This is an article in active development. Formulas, numbers, and conclusions may change as open issues are resolved — see [TODO.md](TODO.md) for what is known to be incomplete. Nothing here is investment advice.

A mathematical model of the "wheel" options strategy — repeatedly selling cash-secured puts on fundamentally sound assets, taking assignment when it comes, and selling covered calls until the stock is called away — framed as a stochastic inventory system. Put assignments are arrivals into an inventory of stock lots; call-aways are departures; the machinery of queueing theory answers how much stock the strategy really holds, how much capital it consumes, and when it stops being self-recycling.

The end product will be a LaTeX article for a general, numerate audience.

## Layout

| Path | Contents |
|---|---|
| `sections/` | The article, one Markdown file per section, numbered in reading order. `00-notation.md` is the glossary and single source of truth for symbols. |
| `code/` | Supplementary scripts. `verify_examples.py` recomputes every worked numerical example quoted in the text. |
| `TODO.md` | Open modeling and writing issues, cross-referenced from the sections. |
| `drafts/` | Historical drafts. Superseded by `sections/` — the initial draft contains a since-corrected P&L formula. |

## Verifying the numbers

Every worked example in the article is machine-checked:

```
python code/verify_examples.py
```

Python 3.8+, standard library only.

## Status

Tier 1 (the homogeneous approximation — all inventory lots share one recovery rate) is drafted. Tier 2 — depth-dependent recovery rates, the true stability condition, and the stable/metastable/unstable phase diagram — is planned; see `sections/10-outlook.md`.
