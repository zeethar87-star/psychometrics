# Architecture

## Stack
- Backend API: FastAPI.
- Queue choice: **RQ + Redis** (simple Python-first queue, low operational overhead). MVP includes local-thread fallback for no-Redis local demos.
- Storage: local filesystem (`data/jobs/<job_id>`).

## Services
- API service: upload, status, SSE events, download.
- Worker: consumes job IDs and processes stage-by-stage.
- Frontend: static HTML/CSS/JS pages served by FastAPI.

## Job Folder Layout
- `manifest.json`: canonical state (state, stage, progress, files, stage checkpoints).
- `events.log`: append-only SSE event source.
- `input/`: uploaded file.
- `artifacts/`: generated PNG/preprocessed image/DXF/report.
- `artifacts/frames/`: lightweight preview frames.

## Resumability
- Manifest tracks per-stage state (`Pending/Done`) and checkpoints.
- On restart/re-run, worker skips stages already marked Done.
- Crash recorded as `Crash` with error code.

## Plugin Architecture (design)
Hooks (future):
- `pre_geometry`
- `post_geometry`
- `pre_architecture`
- `post_architecture`
- `post_core`

Plugins receive immutable input and return **new** output objects. Core pipeline never mutates plugin inputs in place.

Example future plugins:
- Column plugin: inject column candidates in `post_geometry`.
- Grid removal plugin: remove grid lines in `pre_architecture`.
