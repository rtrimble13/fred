# 0005. Offline fuzzy search over a curated catalog, the API's search for everything else

Date: 2026-10-25
Status: accepted

## Context

FRED, unlike BLS and BEA, has a good full-text search endpoint. But it costs
a request, returns hundreds of detailed series for plain queries ("inflation"
matches thousands), and ranks by its own relevance. Agents and people need to
turn "mortgage rates" into `MORTGAGE30US` instantly and deterministically,
and still reach the long tail.

## Decision

Two layers, mirroring `bls`/`bea` (ADR 0005) with the API in place of flat
files:

1. **`fred search`** - offline, zero-request fuzzy search over a *curated*
   JSON catalog of ~150 headline series (id, title, frequency, seasonal
   adjustment, units, source, tags, aliases). The scorer is the same per-token
   scheme as the siblings (exact tag 1.0, whole word 0.95, substring 0.75,
   RapidFuzz ratio >= 72 at 0.8 x ratio; exact id/tag/title/alias = 100),
   with one refinement: tokens shorter than five letters need a ratio of at
   least 85, so `gold` is not a typo of `sold`. Ties keep catalog order so
   headline series rank first.
2. **`fred series search`** - the API's full-text search over every series,
   with `--order-by popularity`, frequency/seasonal filters and tag filters,
   plus `releases`/`categories` browsing (ADR 0010).

## Consequences

- The curated catalog must be maintained by hand; wrong ids are the main risk,
  so contributors verify with `fred series info`.
- Search results are deterministic and explainable (score bands), which suits
  agents; the live search covers everything else at one request per query.
- The two layers are documented together so users know when to switch.
