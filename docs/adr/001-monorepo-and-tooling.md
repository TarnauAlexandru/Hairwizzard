# 001. Monorepo with a uv workspace and a shared `strand_core` package

- **Status:** Accepted
- **Date:** 2026-10-23

## Context

Strand has a phone app (Flet), a backend (FastAPI), training code and docs. The phone and the
backend need the same domain model and recommendation logic. Keeping two copies would drift.

## Decision

One repository. The domain, ports and recommendation logic live in `packages/strand_core`, a
pure-Python package with no third-party dependencies, imported by both the backend and the app.
Python dependencies are managed with a [uv](https://docs.astral.sh/uv/) workspace; quality checks
are ruff (lint + format), mypy (strict on `strand_core`), pytest, bandit and pip-audit, run by
pre-commit locally and by GitHub Actions on every push.

## Alternatives considered

- **Separate repositories per part:** cleaner boundaries, but sharing `strand_core` would need a
  published package and versioning overhead for a single developer.
- **Poetry instead of uv:** mature, but slower and without first-class workspaces.

## Consequences

- One `uv sync` sets up everything; one CI run checks everything.
- `strand_core` must never import third-party libraries, or it stops working on the phone.
  This is enforced with import-linter in Phase 2.3.
- The mobile app is packaged by `flet build`, outside the workspace; how it bundles
  `strand_core` is decided in Phase 0.2.
