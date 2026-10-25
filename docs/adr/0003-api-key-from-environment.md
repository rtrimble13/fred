# 0003. API key only from the environment; no anonymous mode

Date: 2026-10-25
Status: accepted

## Context

FRED issues free 32-character API keys and requires one on every request;
there is no anonymous tier. Keys are rate limited (120 requests per minute).
The tool runs in shells, cron, CI and agent sandboxes, where a `--api-key`
flag would leak into history, process listings and transcripts.

## Decision

Read the key exclusively from `FRED_API_KEY` (inherited from `bls` and `bea`,
ADR 0003). Provide no flag and no config file. Every live command fails
*before* making a request when the key is unset, with exit code 7 and a hint
pointing at the key page. When the API rejects the key (its error message
names `api_key`), that error is also mapped to exit code 7 so scripts can
tell "fix the key" from "fix the request". `fred config` and `fred doctor`
print the key masked; `doctor` additionally checks that the key has FRED's
shape (32 lower-case alphanumerics). The key is sent only as the `api_key`
query parameter, never logged, and never echoed in `--raw` output.

## Consequences

- Secrets management is delegated to the environment, where it belongs.
- Offline commands (`search`, `config`, `cache`, `version`) work without a
  key; everything else needs one.
- Tests never need a real key: the fake API accepts a test key, and the client
  can be constructed with `api_key=None`.
