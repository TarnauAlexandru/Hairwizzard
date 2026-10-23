# Strand

[![CI](https://github.com/TarnauAlexandru/Hairwizzard/actions/workflows/ci.yml/badge.svg)](https://github.com/TarnauAlexandru/Hairwizzard/actions/workflows/ci.yml)

Strand is an Android app, written in Python with [Flet](https://flet.dev), that analyses your face
shape and hair from a few photos, recommends haircuts, lets you edit the cut zone by zone in 3D,
and produces a card to show your barber, plus the styling products to match.

**All image processing and machine learning run on the phone. Photos never leave the device.**
The backend only stores accounts, the haircut and product catalog, reviews and saved looks.

> Status: early development. Phase 0 (setup and on-device spike) of 13.

## Planned features

- Guided capture: front, left, right, back, top, plus a hair close-up, with automatic checks
- Face shape and hair profile (texture, thickness, density) analysis, on device
- Ranked haircut recommendations with the reason for each
- Zone-by-zone editor (top, crown, fringe, sides, back, fade, neckline, part)
- 360° 3D preview and the cut overlaid on your own photos
- Barber card with lengths and clipper guard numbers, exported as PNG or PDF
- Styling routine (prep, style, finish) and product reviews filtered by hair type

## Repository layout

```
packages/strand_core/   domain model, ports, recommendation logic (pure Python, shared)
backend/                FastAPI API: accounts, catalog, reviews, saved looks (no ML)
mobile/                 Flet Android app, WebView with MediaPipe JS and three.js
ml/                     model training and ONNX export
docs/                   architecture decisions (ADRs), threat model, model cards
```

## Architecture

Clean Architecture with dependencies pointing inwards:
`presentation → application → domain ← infrastructure`.
Decisions are recorded in [docs/adr](docs/adr/README.md).

## Development

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-packages          # install everything
uv run pre-commit install       # run checks before every commit
uv run pytest                   # tests
uv run ruff check . && uv run ruff format --check .
uv run mypy packages/strand_core/src backend/app
```

CI runs the same checks, plus bandit and pip-audit, on every push.

## License

[MIT](LICENSE)
