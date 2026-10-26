# 0004. Tidy `series_id, date, value` records; JSON, JSONL, CSV, Parquet, table

Date: 2026-10-25
Status: accepted

## Context

The observations endpoint returns, per series, a list of
`{realtime_start, realtime_end, date, value}` objects with string values and
`.` for missing data. Consumers want spreadsheets, dataframes, `jq` pipelines
and data lakes, and the same output flags as `bls` and `bea`.

## Decision

Normalise every observation into a flat **record** with a fixed core column
order (`series_id, date, value`), typed values (`date` as a real date,
`value` as float or null), chronological order, and optional columns appended
in a defined order: `realtime_start`/`realtime_end` with `--as-of`, and the
series metadata (`title, units, frequency, seasonal_adjustment,
last_updated`) with `--meta`. The core is smaller than in `bls`/`bea` because
FRED observations carry no period code, frequency or footnotes of their own;
those are series attributes, available through `--meta`. All formats
serialise the same records:

| format | purpose |
| --- | --- |
| `json` | default for pipes; array of objects |
| `jsonl` | streaming / append-friendly |
| `csv` | spreadsheets, pandas |
| `parquet` | typed columnar storage (pyarrow, snappy) |
| `table` | humans; default on a TTY |

A `--layout wide` pivot (one row per date) and a `--raw` escape hatch (the
request parameters plus each series' observations with original string
values, key removed) are provided; `--columns` projects identically in every
format. The serialisers are the same as in the siblings.

## Consequences

- Core column names and order are part of the contract; adding columns is a
  minor change, renaming or reordering core columns is major.
- `date` is FRED's observation date: the *first day* of the period for
  monthly, quarterly and annual series, the actual day for daily and weekly
  series (weekly series carry their week-ending convention).
- Transformations (`--units`) change what `value` means without changing the
  column name; the parameters are visible in `--raw` and documented.
