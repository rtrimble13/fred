# 0012. Everyday-phrase aliases and small-word skipping in catalog search

Date: 2026-10-25
Status: accepted

## Context

`fred search` (ADR 0005) scores each query word against series titles and
tags and averages the credits. People and agents phrase questions in everyday
language ("mortgage rates", "jobs report", "fed balance sheet", "price of
gas"), and a word that appears in no title or tag, such as "rates", "report"
or "of", scores 0 and halves the result. Many natural queries would return
nothing or rank the wrong series first.

Adding such phrases as ordinary tags fixes the phrase itself but leaks its
words: every word of a tag earns credit on its own. With a `mortgage rates`
tag, the lone word `rates` would match the mortgage series at 95, above the 90
that agents treat as a confident match. `bls` met the same problem and solved
it with aliases (its ADR 0012); `fred` adopts the solution unchanged.

## Decision

1. **Single-word synonyms are tags** (`jobs` on payroll employment series,
   `grocery`, `pay`, `hiring`, `salary`). One word leaks nothing but itself.
2. **Multi-word everyday phrases are `aliases`**, a new optional catalog
   field. An alias matches only the query as a whole and then scores 100. Both
   sides are normalised with `phrase_key`: case, punctuation, word order,
   simple plurals and the small words `a an the of in for us u s` are ignored,
   so `price of eggs` matches the alias `egg prices`. Alias words earn no
   per-word credit. Matching is exact after normalisation, not fuzzy: a fuzzy
   threshold let `bar prices` match `car prices` at 90.
3. **The same small words are skipped in per-word scoring** unless the query
   consists of nothing else, so `unemployment in texas` scores like
   `unemployment texas`.
4. An alias shared by several series is allowed where the phrase is genuinely
   ambiguous (`fed funds rate` on the monthly and daily series) or names a
   seasonally adjusted/unadjusted pair. Catalog order still breaks ties.
5. A tag that should decide a query (`money supply`, `house prices`,
   `recession indicator`) is given to one series only; related series carry
   narrower tags.

## Consequences

- Common phrasings resolve offline with scores agents can trust; queries for
  data the catalog does not hold (`bitcoin price`, `gold price`) still return
  nothing, and tests pin both.
- Score bands are unchanged in meaning: 100 is still an exact match (now also
  to a normalised alias).
- Small words no longer give incidental credit, so ties they used to break are
  decided by catalog order; the catalog is ordered accordingly (headline
  series before their daily, unadjusted or component variants).
- Contributors choose between a tag and an alias; `docs/development.md` and a
  catalog test (aliases must have at least two significant words, no
  duplicates per series) enforce the split.

Ported from `bls` (ADR 0012) unchanged in mechanism; `fred`'s catalog uses the
same `tags`/`aliases` split (`mortgage rates`, `jobs report`, `yield curve`, `fed
balance sheet`), and its test suite pins both the phrases that must resolve and
the ones that must not (`bitcoin price`, `gold price`).
