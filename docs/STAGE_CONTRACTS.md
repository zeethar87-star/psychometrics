# Stage Contracts

Gate levels: PASS / WARN / REJECT.

## Stage 1: PDF -> PNG
- Input: `input/*.pdf`.
- Output: `artifacts/page1.png`.
- Accept:
  - PASS: PNG exists and opens.
  - WARN: fallback placeholder generated.
  - REJECT: missing/invalid input PDF (`E-UPLOAD-404`).

## Stage 2: Preprocess
- Input: stage1 PNG.
- Output: `artifacts/preprocessed.png`.
- Accept:
  - PASS: output exists, readable image.
  - WARN: deskew skipped.
  - REJECT: stage1 artifact missing (`E-STAGE2-NOINPUT`).

## Stage 7: Build DXF
- Input: preprocessed image.
- Output: `artifacts/output.dxf`.
- Accept:
  - PASS: DXF generated with at least one entity.
  - WARN: naive geometry only.
  - REJECT: missing preprocess (`E-STAGE7-NOINPUT`).

## Stage 8: Validate DXF
- Input: generated DXF.
- Output: validation state + checkpoint.
- Accept:
  - PASS: contains entity tokens and EOF.
  - REJECT: invalid or missing DXF (`E-STAGE8-NODXF`, `E-DXF-INVALID`).

## Stage 9: Report
- Input: manifest + artifacts.
- Output: `artifacts/report.html`.
- Accept:
  - PASS: report exists and lists artifact links.
