---
name: fred-data
description: Fetch U.S. and international economic time series (GDP, unemployment, inflation, interest rates, money supply, exchange rates, housing, government debt) from FRED, the Federal Reserve Bank of St. Louis database, with the `fred` CLI. Use when a task needs an official economic indicator, its latest reading, its history or a past vintage, or a CSV/Parquet extract of FRED data.
---

# FRED data via the `fred` CLI

`fred` is a command-line client for the FRED API. It is installed
(`fred --version` works) and reads the API key from `FRED_API_KEY`; every live
request needs that key (exit 7 without it).

## Rules

1. Always pass `--format json` (or `jsonl`/`csv`/`parquet` for files). Parse
   **stdout** only; stderr holds warnings.
2. Resolve series ids before fetching data:
   - `fred search "<plain words>" --limit 5 --format json` (offline, free).
     Use the top `id` if its `score` >= 90, otherwise show the user the
     candidates.
   - For something not in the curated catalog:
     `fred series search "<words>" --order-by popularity -n 10 --format json`
     (live, one request); add `--frequency m`, `--seasonal sa` or
     `--tag usa` to narrow, `--exclude-tag discontinued` to drop dead series.
   - Confirm what an id measures: `fred series info ID --format json`
     (title, frequency, units, seasonal adjustment, last update).
3. Fetch with one call for all ids you need:
   - latest: `fred latest ID1 ID2 --meta --format json --strict`
   - range: `fred data ID1 ID2 --start YYYY-MM --end YYYY-MM --format json`
   - changes: add `--units pc1` (percent change from a year ago), `pch`
     (from the previous observation), `chg` (difference), `pca` (annualized)
   - lower frequency: add `--frequency m|q|a` (`--aggregation eop` for rates
     and stocks, the default `avg` for flows and indexes)
   - as first published: add `--as-of YYYY-MM-DD`
4. Interpret exit codes: `0` ok; `2` your flags were wrong (read stderr, fix);
   `3` bad id, units or frequency; `4` rate limit (wait a minute); `5` network
   (retry once after a pause); `6` a series had no data; `7` key missing or
   rejected.
5. Budget: 120 requests per minute; each `fred data` call costs one request
   per series (two with `--meta`). Batch ids into one call; do not loop over
   ids one at a time.

## Output schema

Each JSON row: `series_id, date (YYYY-MM-DD; first day of the period for
monthly/quarterly/annual series), value (number or null)`, plus
`realtime_start`/`realtime_end` with `--as-of` and `title, units, frequency,
seasonal_adjustment, last_updated` with `--meta`. With `--units pc1`/`pch`
the value is a percent change; with `chg`/`ch1` a difference in the series'
units.

## Worked example

User: "What's the unemployment rate, and how does it compare to a year ago?"

```bash
fred search "unemployment rate" --limit 3 --format json      # -> UNRATE, score 100
fred data UNRATE --years 2 --meta --format json              # levels; the last row is the latest
fred latest UNRATE --units ch1 --format json                 # change from a year ago, in points
```

Report the latest `date`, `value` and `units`, and the year-ago change in
percentage points (rates change by points, not percent). Say that the value
is the current vintage.

## Reference

For anything beyond a single lookup (real values, yield-curve questions,
vintages and revisions, choosing between candidate series, the answer
template), follow
[`docs/practitioners-guide.md`](../../docs/practitioners-guide.md), especially
section 7 (agent protocol) and section 8 (question playbook).
