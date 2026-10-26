# fred

[![CI](https://github.com/rtrimble13/fred/actions/workflows/ci.yml/badge.svg)](https://github.com/rtrimble13/fred/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A command-line client (and small Python library) for
[FRED](https://fred.stlouisfed.org/), the Federal Reserve Bank of St. Louis
economic database: 800,000+ U.S. and international time series on growth,
jobs, prices, interest rates, money, markets, housing, trade and government,
plus ALFRED, the archive of what each series looked like on any past date. It
is the sibling of [`bls`](https://github.com/rtrimble13/bls) and
[`bea`](https://github.com/rtrimble13/bea) and shares their design: one tool
for people doing ad-hoc research in a terminal, and for automations or AI
agents that need predictable, scriptable access to official time series.

```console
$ export FRED_API_KEY=...            # free 32-character key from https://fred.stlouisfed.org/docs/api/api_key.html
$ fred data UNRATE CPIAUCSL --start 2024-01 --end 2024-03 --units pc1 --format csv
series_id,date,value
UNRATE,2024-01-01,8.1
UNRATE,2024-02-01,8.3
UNRATE,2024-03-01,8.6
CPIAUCSL,2024-01-01,3.1
CPIAUCSL,2024-02-01,3.2
CPIAUCSL,2024-03-01,3.5
```

## Features

- **The whole database**: `fred data` fetches any series by id, one request
  each, paginated automatically; `--units pc1` and friends apply FRED's own
  transformations (changes, percent changes, logs); `--frequency q
  --aggregation eop` aggregates to a lower frequency; `--as-of 2020-03-15`
  returns the values as they were published on that day (ALFRED vintages).
- **Normalised records**: every series becomes the same tidy shape
  (`series_id`, `date`, `value`), with vintage columns and series metadata
  (`--meta`) appended on request; `.` becomes `null`.
- **Filters the API lacks**: inclusive date ranges in friendly forms
  (`--start 2020-03 --end 2024-Q2`), `--years N`, `--latest`, `--series-file`;
  transient failures are retried with back-off.
- **Output for humans and machines**: `table`, `json`, `jsonl`, `csv`,
  `parquet`; long (tidy) or wide layouts; `--columns` to pick columns;
  `--raw` for the API-shaped JSON.
- **Discovery, offline and live**: `fred search "mortgage rates"` works
  offline against a curated catalog of ~150 widely used series and
  understands everyday phrases ("jobs report", "yield curve", "fed balance
  sheet"); `fred series search` is the API's full-text search over every
  series, with frequency, seasonal-adjustment and tag filters; `fred series
  info`, `fred series vintages`, `fred series updates`, `fred releases`
  (including the upcoming release calendar) and `fred categories` round it
  out.
- **Automation friendly**: API key from the environment only, stable exit
  codes, warnings on stderr and data on stdout, `--strict`, `--quiet`,
  `--series-file -` to read ids from stdin, JSON by default when piped.
- **Linux CI, tag-driven releases**: versions are derived from `vX.Y.Z` git
  tags; a one-click workflow bumps, tags and publishes.

## Installation

Requires Python 3.10+.

```bash
# with uv (recommended)
uv tool install git+https://github.com/rtrimble13/fred
# or with pipx
pipx install git+https://github.com/rtrimble13/fred
# or into the current environment
pip install git+https://github.com/rtrimble13/fred
```

For development:

```bash
git clone https://github.com/rtrimble13/fred && cd fred
make install        # uv venv + editable install with dev extras
make check          # ruff, mypy, pytest
```

## Configuration

Set your key once; everything else has sensible defaults.

| Variable | Purpose | Default |
| --- | --- | --- |
| `FRED_API_KEY` | Your 32-character API key. **Required for every live request**; FRED has no anonymous access. | unset |
| `FRED_FORMAT` | Default `--format` (`json`, `jsonl`, `csv`, `parquet`, `table`). | `table` on a TTY, `json` otherwise |
| `FRED_CACHE_DIR` | Where the release list and category tree are cached. | `$XDG_CACHE_HOME/fred` or `~/.cache/fred` |
| `FRED_TIMEOUT` | HTTP timeout in seconds. | `30` |
| `FRED_MAX_RETRIES` | Retries for 429/5xx/network errors. | `3` |
| `FRED_USER_AGENT` | User-Agent header. | `fred-cli/<version> (+repo url)` |
| `FRED_API_BASE_URL` | Override the API endpoint (testing, proxies). | `https://api.stlouisfed.org/fred` |
| `NO_COLOR` | Disable colour in table output. | unset |

The key is deliberately **not** accepted as a flag (see
[ADR 0003](docs/adr/0003-api-key-from-environment.md)). `fred config` prints
the effective configuration with the key masked; `fred doctor` additionally
checks connectivity.

## Usage

```text
fred data        Fetch observations for one or more series
fred latest      Newest observation per series (alias for data --latest)
fred search      Fuzzy-search the curated series catalog (offline)
fred series      info ID... | search QUERY (live, all of FRED) | vintages ID | updates
fred releases    List releases; `releases show ID`, `releases series ID`, `releases dates`
fred categories  Browse the category tree; `categories children ID`, `categories series ID`
fred config      Effective configuration (key masked)
fred doctor      Configuration + connectivity check
fred cache       info | clear
fred version     Print the version
```

Run `fred <command> --help` for all options. Highlights:

```bash
# 10-year and 2-year Treasury yields, monthly averages since 2019, one column per series
fred data DGS10 DGS2 --frequency m --start 2019 --layout wide -f csv -o yields.csv

# Year-over-year CPI and core CPI inflation for the last 5 years (the API computes pc1)
fred data CPIAUCSL CPILFESL --units pc1 --years 5

# Latest readings with titles, units and when they were last updated
fred latest UNRATE PAYEMS FEDFUNDS MORTGAGE30US --meta

# Nonfarm payrolls as first published on 2 February 2024, from ALFRED
fred data PAYEMS --as-of 2024-02-02 --years 1

# Real GDP growth at an annual rate, directly from the pre-computed series
fred data A191RL1Q225SBEA --years 3

# Ids from a file (or stdin with "-"); fail if any series has no data
fred data --series-file ids.txt --years 2 --strict -f jsonl

# Find series without knowing the id
fred search "mortgage rates"                 # offline, typo-tolerant, everyday phrases
fred series search "median home price" --order-by popularity -n 10   # live, all of FRED
fred series search "unemployment rate" --frequency m --tag usa  # with filters
fred series info UNRATE CPIAUCSL             # title, frequency, units, coverage, last update
fred releases dates --days 7                 # what is coming out this week
fred releases series 53                      # every series in the GDP release

# Exactly what the API returned (key removed)
fred data UNRATE --latest --raw
```

### Dates, frequencies and units

`--start`/`--end` accept `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, `YYYY-Qn` and
`YYYY-Hn`. Both bounds are inclusive and are sent to the API as
`observation_start`/`observation_end`, so only the rows you asked for are
transferred. Without a date flag the full history is returned; `--years N`
covers the last N calendar years and `--latest` asks for the newest value
only.

`--frequency` (`d`, `w`, `bw`, `m`, `q`, `sa`, `a`) aggregates a series to a
lower frequency on the server, by average unless `--aggregation sum` or
`eop` is given. `--units` applies a transformation: `lin` (levels, the
default), `chg`, `ch1` (change from a year ago), `pch`, `pc1` (percent change
from a year ago), `pca`, `cch`, `cca`, `log`. `--as-of DATE` fetches the
vintage known on that date and adds `realtime_start`/`realtime_end` columns.

### Output

Long layout columns, always in this order:

```
series_id, date, value
```

followed by `realtime_start`, `realtime_end` (with `--as-of`) and `title`,
`units`, `frequency`, `seasonal_adjustment`, `last_updated` (with `--meta`).
`date` is the observation date (the first day of the period for monthly,
quarterly and annual series; ISO 8601 in text formats, `date32` in Parquet);
`value` is a float, `null` where FRED reports `.`.

The wide layout has one row per date and one column per series id. See
[docs/output-formats.md](docs/output-formats.md) for schemas and examples.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | success |
| 1 | unexpected error |
| 2 | usage error (bad flag, bad date, unknown column) |
| 3 | the API rejected the request (unknown series, bad parameter) or returned an HTTP error |
| 4 | rate limit exceeded (120 requests per minute) |
| 5 | network problem (DNS, timeout, connection reset) |
| 6 | `--strict` and at least one series returned no data |
| 7 | configuration error (no or rejected `FRED_API_KEY`) |

Warnings (unknown series, empty results) go to **stderr**; data goes to
**stdout**. `--quiet` silences the warnings.

## Python API

```python
from fred import FREDClient, Settings

with FREDClient.from_settings(Settings.from_env()) as client:  # or FREDClient(api_key="...")
    resp = client.fetch(["UNRATE", "CPIAUCSL"], start=date(2015, 1, 1), units="pc1", meta=True)
    for series in resp.series:
        for obs in series.data:
            print(series.series_id, series.title, obs.date, obs.value)
```

See [docs/python-api.md](docs/python-api.md).

## For agents and automations

`fred` is designed to be called from scripts, cron jobs, GitHub Actions and
agent skills. [docs/agents.md](docs/agents.md) is a compact contract
(commands, flags, output schema, exit codes, rate-limit guidance) that a
skill can reference, and [examples/skill/SKILL.md](examples/skill/SKILL.md) is
a ready-made skill. [docs/practitioners-guide.md](docs/practitioners-guide.md)
is the companion reference for turning questions into series, fetches and
sourced answers. [examples/github-actions/](examples/github-actions/)
contains a scheduled data-pull workflow.

## Documentation

- [docs/practitioners-guide.md](docs/practitioners-guide.md) - what you can answer with `fred`: research workflow, recipes, reading FRED data, agent protocol
- [docs/usage.md](docs/usage.md) - full command reference
- [docs/configuration.md](docs/configuration.md) - environment variables, limits, caching
- [docs/output-formats.md](docs/output-formats.md) - record schema per format
- [docs/series-ids.md](docs/series-ids.md) - how to find and read FRED series ids
- [docs/agents.md](docs/agents.md) - the contract for agentic workflows
- [docs/python-api.md](docs/python-api.md) - using the library
- [docs/development.md](docs/development.md) - contributing, tests, tooling
- [docs/releasing.md](docs/releasing.md) - versioning and the release workflow
- [docs/adr/](docs/adr/) - architecture decision records
- [CHANGELOG.md](CHANGELOG.md)

## Versioning

Versions are `vMAJOR.MINOR.PATCH` git tags; the package version is derived from
them at build time (hatch-vcs). Releases are produced by the **Bump version**
workflow in the Actions tab (choose patch/minor/major), which updates
`CHANGELOG.md`, tags, builds, verifies, and publishes a GitHub release
([docs/releasing.md](docs/releasing.md)).

## Data notes

- FRED aggregates series from many sources (BLS, BEA, the Federal Reserve
  Board, Census, Treasury, and others) under their respective terms; see the
  [FRED API terms of use](https://fred.stlouisfed.org/docs/api/terms_of_use.html).
  Some series (for example S&P 500, Dow Jones) are available only for the
  most recent years because of licensing.
- The API limits each key to 120 requests per minute and 100,000
  observations per request; `fred` paginates and exits with code 4 when rate
  limited.
- Values are the *current* vintage unless `--as-of` is given; revised series
  change over time.

## License

MIT - see [LICENSE](LICENSE).
