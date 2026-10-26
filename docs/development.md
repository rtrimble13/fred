# Development

## Setup

```bash
git clone https://github.com/rtrimble13/fred && cd fred
make install          # creates .venv with uv and installs -e ".[dev]"
source .venv/bin/activate
fred --help
```

Without `make`: `uv venv && uv pip install -e ".[dev]"`.

## Everyday commands

| Command | What it does |
| --- | --- |
| `make check` | ruff lint + format check, mypy (strict), pytest with coverage. Same as CI. |
| `make format` | ruff format + autofix |
| `make test` | pytest |
| `make build` | sdist and wheel into `dist/` |
| `pre-commit install` | optional git hooks (ruff, whitespace, yaml/json checks) |

## Layout

```
src/fred/
  cli/            Typer app: _common (plumbing), data, discover, meta
  client.py       HTTP client: endpoints, pagination, retries, error mapping
  config.py       Settings from environment variables
  periods.py      Date-spec parsing; frequency, units and aggregation vocabularies
  models.py       Observation / Series / SeriesInfo / DataResponse / Release / Category / Source
  records.py      Flatten to records; wide pivot
  output.py       json / jsonl / csv / parquet / table writers
  search.py       Fuzzy scoring, aliases and search
  catalog.py      Bundled curated series catalog loader
  cache.py        Small file cache
  errors.py       Exceptions and exit codes
  data/           series_catalog.json
tests/            pytest suite with a fake FRED API (httpx.MockTransport)
docs/             user docs and ADRs
examples/         scripts, a GitHub Actions workflow, an agent skill
scripts/          release helpers (next_version, changelog_*)
```

## Testing philosophy

The FRED API is never called in tests. `tests/conftest.py` contains
`FakeFRED`, a small in-memory implementation of the endpoints the client uses
(series, observations with pagination, units, frequency aggregation and
vintages, search with filters and tags, vintage dates, updates, releases and
release dates, categories, sources) for a handful of series, served through
`httpx.MockTransport`. CLI tests inject it via `State(transport=...)` passed
as the Typer context object; client tests pass it to
`FREDClient(transport=...)`. The fake generates deterministic observations
(including `.` for holidays in daily series) so tests can assert on counts,
ordering and request parameters.

To exercise the real API locally:

```bash
export FRED_API_KEY=...
fred doctor
fred latest UNRATE -v
```

## Adding a series to the curated catalog

Edit `src/fred/data/series_catalog.json`. Each entry needs `id`, `title`,
`frequency` (`daily`, `weekly`, `biweekly`, `monthly`, `quarterly`, `annual`),
`seasonal` (`SA`/`NSA`), `units`, `source` (the publishing agency) and
`tags`; `aliases` is optional. Keep headline series before variants: ties in
search score keep file order. Verify the id with `fred series info ID` before
committing.

Everyday wording goes in one of two places ([ADR 0012](adr/0012-catalog-aliases.md)):

- **`tags`** for single words and established terms (`jobs`, `cpi`, `vix`,
  `yield curve`). Each word of a tag earns credit on its own, so avoid
  multi-word tags whose words could pair with unrelated titles, and give a
  tag to one series only when a query should have one clear winner.
- **`aliases`** (optional) for everyday phrases people type whole
  (`mortgage rates`, `jobs report`, `fed balance sheet`). An alias matches
  only the entire query, ignoring case, word order, plurals and small words
  such as "of" and "in", and lends no credit to its individual words. An
  alias must contain at least two significant words (a test enforces it).

Check a new phrase with `fred search "<phrase>"`, and check that it does not
create matches for unrelated queries (`tests/test_search_catalog.py` pins
both kinds).

## Style

- Python 3.10+, `from __future__ import annotations`, type hints everywhere
  (mypy strict).
- Ruff for lint and formatting, line length 100.
- CLI commands live in `src/fred/cli/*.py` and register themselves via
  `register(app)`; shared behaviour goes in `_common.py`.
- Errors raised from library code are `FREDError` subclasses; the CLI maps them
  to exit codes in `handle_errors`.
- Decisions with lasting consequences get an ADR in `docs/adr/`.
