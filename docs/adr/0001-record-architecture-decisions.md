# 0001. Record architecture decisions

Date: 2026-10-25
Status: accepted

## Context

`fred` is meant to be used for years by people and by automations whose
authors will not have the original design discussions available. Decisions
about output shape, exit codes and limits become contracts once scripts depend
on them. The project is the third of a family (`bls`, `bea`, `fred`), so it
also needs a record of where it follows its siblings and where the FRED API
forced a different choice.

## Decision

Keep Architecture Decision Records in `docs/adr/`, one Markdown file per
decision, in the MADR short form (context, decision, consequences), indexed in
`docs/adr/README.md`. A decision is recorded when it affects the CLI contract,
the data shape, dependencies, security or the release process. ADRs inherited
from `bls` or `bea` say so explicitly.

## Consequences

- Changes to contracts must come with a new ADR (or a superseding one), which
  slows down casual breaking changes - intentionally.
- Newcomers and agents can read the "why" without digging through history, and
  people who know the sibling tools can see the differences at a glance.
