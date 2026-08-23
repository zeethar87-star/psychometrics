from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR, THROTTLE_SECONDS
from .job_store import append_event, create_job, events_path, job_dir, read_manifest, write_manifest
from .worker import enqueue_job

app = FastAPI(title="PDF to Smart DXF MVP")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/job/{job_id}", response_class=HTMLResponse)
def progress_page(job_id: str) -> str:
    html = (STATIC_DIR / "progress.html").read_text(encoding="utf-8")
    return html.replace("__JOB_ID__", job_id)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF only")
    manifest = create_job(file.filename)
    out_pdf = job_dir(manifest["job_id"]) / manifest["files"]["input_pdf"]
    out_pdf.write_bytes(await file.read())
    backend = enqueue_job(manifest["job_id"])
    append_event(manifest["job_id"], {"type": "log", "stage": "queue", "message": f"enqueued via {backend}"})
    return {"job_id": manifest["job_id"]}


@app.get("/api/job/{job_id}")
def job_status(job_id: str) -> dict:
    try:
        return read_manifest(job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@app.get("/api/job/{job_id}/events")
async def stream(job_id: str) -> StreamingResponse:
    path = events_path(job_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="job not found")

    async def event_generator():
        sent = 0
        while True:
            if path.exists():
                lines = path.read_text(encoding="utf-8").splitlines()
                for i in range(sent, len(lines)):
                    payload = lines[i]
                    yield f"data: {payload}\n\n"
                sent = len(lines)
                manifest = read_manifest(job_id)
                if manifest["state"] in {"Done", "Failed", "Crash"} and sent == len(lines):
                    break
            await asyncio.sleep(THROTTLE_SECONDS)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/job/{job_id}/download")
def download(job_id: str):
    manifest = read_manifest(job_id)
    dxf = manifest["files"].get("dxf")
    report = manifest["files"].get("report")
    if dxf and (job_dir(job_id) / dxf).exists():
        return FileResponse(job_dir(job_id) / dxf, media_type="application/dxf", filename=f"{job_id}.dxf")
    if report and (job_dir(job_id) / report).exists():
        return FileResponse(job_dir(job_id) / report, media_type="text/html", filename=f"{job_id}-report.html")
    raise HTTPException(status_code=404, detail="artifact not ready")


@app.get("/api/job/{job_id}/frames")
def frames(job_id: str) -> dict[str, list[str]]:
    frames_dir = job_dir(job_id) / "artifacts" / "frames"
    if not frames_dir.exists():
        return {"frames": []}
    names = sorted([f"/jobs/{job_id}/artifacts/frames/{p.name}" for p in frames_dir.glob("*.png")])
    return {"frames": names}


app.mount("/jobs", StaticFiles(directory=Path("data/jobs")), name="jobs")
