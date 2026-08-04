from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from .config import DATA_DIR, PIPELINE_STAGES
from .models import JobState, now_iso


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def job_dir(job_id: str) -> Path:
    return DATA_DIR / job_id


def manifest_path(job_id: str) -> Path:
    return job_dir(job_id) / "manifest.json"


def events_path(job_id: str) -> Path:
    return job_dir(job_id) / "events.log"


def create_job(upload_filename: str) -> dict[str, Any]:
    ensure_dirs()
    job_id = str(uuid.uuid4())
    jdir = job_dir(job_id)
    (jdir / "input").mkdir(parents=True, exist_ok=True)
    (jdir / "artifacts" / "frames").mkdir(parents=True, exist_ok=True)
    manifest = {
        "job_id": job_id,
        "state": JobState.PENDING.value,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "progress": 0,
        "current_stage": "queued",
        "last_error_code": None,
        "what_is_happening": "Job queued",
        "files": {
            "input_pdf": f"input/{upload_filename}",
            "png": None,
            "preprocessed": None,
            "dxf": None,
            "report": None,
        },
        "stages": {stage: {"state": "Pending", "checkpoint": None} for stage in PIPELINE_STAGES},
    }
    write_manifest(job_id, manifest)
    append_event(
        job_id,
        {
            "type": "progress",
            "progress": 0,
            "stage": "queued",
            "message": "Job created",
            "last_error_code": None,
        },
    )
    return manifest


def read_manifest(job_id: str) -> dict[str, Any]:
    with manifest_path(job_id).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest(job_id: str, payload: dict[str, Any]) -> None:
    payload["updated_at"] = now_iso()
    with manifest_path(job_id).open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def append_event(job_id: str, event: dict[str, Any]) -> None:
    path = events_path(job_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**event, "ts": now_iso()}) + "\n")
