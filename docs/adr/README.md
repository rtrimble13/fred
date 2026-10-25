# Architecture Decision Records

Decisions that shape `fred` and would be costly to reverse. One file per
decision, numbered in order of acceptance, following the
[MADR](https://adr.github.io/madr/) short form: context, decision, consequences.
`fred` deliberately mirrors the design of [`bls`](https://github.com/rtrimble13/bls)
and [`bea`](https://github.com/rtrimble13/bea); where a decision is inherited
unchanged the ADR says so.

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | accepted |
| [0002](0002-python-typer-cli.md) | Python package with a Typer CLI over a library core, modelled on `bls` and `bea` | accepted |
| [0003](0003-api-key-from-environment.md) | API key only from the environment; no anonymous mode | accepted |
| [0004](0004-tidy-records-and-output-formats.md) | Tidy `series_id, date, value` records; JSON, JSONL, CSV, Parquet, table | accepted |
| [0005](0005-fuzzy-search.md) | Offline fuzzy search over a curated catalog, the API's search for everything else | accepted |
| [0006](0006-version-from-git-tags.md) | Version derived from `vX.Y.Z` git tags; workflow-driven releases | accepted |
| [0007](0007-server-side-windows-transformations-vintages.md) | Date windows, transformations, aggregation and vintages are the API's job | accepted |
| [0008](0008-per-series-requests-pagination-retries.md) | One request per series, pagination, retries, rate-limit mapping | accepted |
| [0009](0009-linux-only-ci.md) | Linux-only GitHub Actions | accepted |
| [0010](0010-discovery-through-the-api.md) | Discovery through search, releases and categories, with cached metadata | accepted |
| [0011](0011-stable-exit-codes-and-streams.md) | Stable exit codes; data on stdout, diagnostics on stderr | accepted |
| [0012](0012-catalog-aliases.md) | Everyday-phrase aliases and small-word skipping in catalog search | accepted |

To add one: copy the template below to `NNNN-short-title.md`, add a row here.

```markdown
# NNNN. Title

Date: YYYY-MM-DD
Status: proposed | accepted | superseded by NNNN

## Context
## Decision
## Consequences
```
