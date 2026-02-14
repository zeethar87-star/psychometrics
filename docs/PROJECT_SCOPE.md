# Project Scope

## Core Scope (MVP)
- Upload one architectural PDF and create one processing job.
- Run deterministic pipeline stages: Stage 1 (PDF→PNG placeholder), Stage 2 (preprocess), Stage 7 (minimal DXF), Stage 8 (DXF validate), Stage 9 (report).
- Persist manifest/checkpoints per stage for resumable execution.
- Show live job progress and frame previews through SSE (throttled at 500ms).
- Allow artifact download (DXF preferred, HTML report fallback).

## Non-goals (MVP)
- Full OCR/vision semantic extraction.
- Multi-page auto selection.
- High-precision CAD reconstruction.
- Multi-tenant auth and cloud object storage.
