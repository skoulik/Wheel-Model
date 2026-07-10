# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A quantitative finance modeling project: a mathematical model of the "wheel" options strategy (selling cash-secured puts, taking assignment, selling covered calls until called away), framed as a stochastic inventory system. The end product is a **LaTeX article for a general audience** describing the model in full. Supplementary artifacts (simulators, verification code) are added on a per-need basis.

## Repository Layout

- `sections/` — the article, one `.md` file per section, numbered in reading order. `sections/00-notation.md` is the **single source of truth for all symbols and conventions**; update it whenever a symbol is introduced or changed.
- `code/` — all scripts. `code/verify_examples.py` recomputes every worked numerical example quoted in the sections. **Run it after touching any formula or example**: `python code/verify_examples.py` (stdlib only). When adding a worked example to the text, add a corresponding check.
- `TODO.md` — open modeling/writing issues; sections reference them as "TODO #n". Resolve an item by fixing the sections, moving it to the Done list, and removing the in-text flag.
- `drafts/` — historical drafts, named `YYYY-MM-DD-<description>.txt`. The initial draft summarizes a prior modeling discussion; it contains a known-wrong P&L formula (see TODO.md Done list) — the sections, not the draft, are authoritative.

## Writing Workflow

- Article sections are developed in Markdown, one file per section — not directly in `.tex`. Conversion to LaTeX happens at assembly time.
- Math is written in **Unicode plain text** (τ, σ, N(−d₂)), not LaTeX markup — a deliberate decision for raw readability.
- Target audience is the general public. Every modeling assumption must be justified in plain terms, not just stated.
- Every parameter gets a proper explanation when first introduced (what it means, typical values, why it matters).
- Before using a mathematical construct, include a short self-contained detour (blockquote style, see existing sections) explaining what it is with a pointer for further reading.
- Accounting-track discipline: label every P&L/capital formula with its track (A = realized cash, B = market-priced capital, C = opportunity cost). Mixing tracks caused the one substantive error found so far.

## The Model (big picture)

- **Notation:** see `sections/00-notation.md`. Core symbols: τ_p/τ_c put/call periods, n = τ_c/τ_p; k = K/S₀; p = assignment probability (risk-neutral, deliberately conservative); q = per-call-period recovery probability (real-world drift μ — the measure mixing is a deliberate policy, TODO #4); q_p ≈ q/n on the put clock; d = drop at assignment.
- **Central result:** inventory of assigned lots is an M/M/∞-style queue, ~Poisson steady state with mean I\* = p·n/q; in equilibrium arrival rate = departure rate ("self-recycling"). Track A run rate per put period: E[Π]/S = c_p + p·c_c/q.
- **Tier structure:** Tier 1 (current sections) uses the homogeneous approximation — uniform q across inventory layers. Tier 2 (planned, `sections/10-outlook.md`) makes q_i depth-dependent, derives the true stability condition, and maps the stable/metastable/unstable phase diagram. Failure modes motivating it: dead strata of trapped capital, p↑/q↓ reflexivity in stress, crash-then-flatline breaking the capital-convergence bound.

## Cautions

- **Sign errors have happened before** (both d₂ and the q formula had inverted signs in early drafts; the P&L formula double-counted the put premium). The defense is `code/verify_examples.py` — keep it in sync with the text and re-run it after any formula change.
- The known-correct anchor example: k=0.95, τ_p=1/12, σ=20%, r=5% ⇒ d₂ ≈ 0.93, p ≈ 17.6%.
- Branch note: the current branch is `master`, but the configured main branch for PRs is `main`.
