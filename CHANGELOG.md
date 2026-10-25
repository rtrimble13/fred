# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/) as `vMAJOR.MINOR.PATCH` git tags.

Releases are cut by the **Bump version** GitHub Actions workflow, which moves the
*Unreleased* section below under the new version heading.

## [Unreleased]
### Added

- `fred data` / `fred latest`: fetch observations for any number of FRED
  series (one request each, paginated when needed) with date ranges
  (`--start/--end/--years`), server-side frequency aggregation
  (`--frequency`, `--aggregation`), unit transformations (`--units pch`,
  `pc1`, ...), ALFRED vintages (`--as-of`), series metadata (`--meta`), long
  and wide layouts, and `--strict` for automations.
- Output formats: `json`, `jsonl`, `csv`, `parquet` and a rich `table`;
  `--columns` to select and order columns; `--output` to write files.
- Discovery: `fred search` (offline fuzzy search over a curated catalog of
  ~130 widely used series, with everyday-phrase aliases), `fred series
  search` (the API's full-text search with filters and tags), `fred series
  info`, `fred series vintages`, `fred series updates`, `fred releases`
  (list, show, series, upcoming dates) and `fred categories`.
- Maintenance: `fred config`, `fred doctor`, `fred cache`, `fred version`.
- Python API (`fred.FREDClient`) with retries, pagination and typed models.
- Documentation (including a practitioner's guide), ADRs, examples, GitHub
  Actions CI and tag-driven releases.
