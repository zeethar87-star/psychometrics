# Error Codes

| Code | Stage | User Message | Dev Details | Recovery |
|---|---|---|---|---|
| E-UPLOAD-404 | stage1 | Uploaded PDF is missing. | Input file path missing in job folder. | Re-upload PDF and retry job. |
| E-STAGE2-NOINPUT | stage2 | Preprocess input unavailable. | Stage1 did not produce PNG. | Resume from stage1 after fixing input. |
| E-STAGE7-NOINPUT | stage7 | Geometry input unavailable. | No preprocessed artifact found. | Re-run stage2 and resume. |
| E-STAGE8-NODXF | stage8 | DXF output not found. | Stage7 artifact missing. | Re-run stage7. |
| E-DXF-INVALID | stage8 | DXF failed validation. | Missing entities or EOF in file. | Inspect generator and rerun stage7/8. |
| E-UNEXPECTED | any | Unexpected processing error. | Unhandled exception captured as crash. | Check logs, fix issue, resume from checkpoint. |
