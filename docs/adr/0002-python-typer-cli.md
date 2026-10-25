# 0002. Python package with a Typer CLI over a library core, modelled on `bls` and `bea`

Date: 2026-10-25
Status: accepted

## Context

The requester already uses `bls` and `bea` and wants the same experience for
FRED: easy to install for researchers, callable from shell pipelines and
agent skills, Parquet output, identical global options and output flags.
Reusing the architecture lowers the learning curve and lets the three tools
evolve together.

## Decision

Implement `fred` as a Python 3.10+ package (`fred-cli` on PyPI, import name
`fred`) with the same structure as its siblings:

- a **library core** (`fred.client`, `fred.models`, `fred.records`, ...) that
  has no CLI concerns and is usable from notebooks and other programs;
- a **Typer** CLI (`fred.cli`) on top, one module per command group, each
  exposing `register(app)`; the same global options (`-v`, `-q`, `-V`), output
  options (`-f`, `-o`, `--columns`), panels and help conventions;
- `httpx` for HTTP, `rapidfuzz` for fuzzy matching, `pyarrow` for Parquet,
  `rich` (via Typer) for tables;
- `src/` layout, `hatchling` build backend, `uv` for development, the same
  Makefile, CI and release workflows.

Command names follow FRED's vocabulary: `data`, `latest`, `search`, `series`
(`info`, `search`, `vintages`, `updates`), `releases`, `categories`, plus
`config`, `doctor`, `cache` and `version` as in the siblings.

## Consequences

- Someone who knows `bls` or `bea` can use `fred` immediately; scripts and
  skills need only small changes between the three.
- The code bases are intentionally similar and should be kept that way;
  improvements to shared modules (`output`, `records`, `search`, `cache`) can
  be ported across.
- The same trade-offs apply: ~150 ms startup, ~40 MB for `pyarrow`.
