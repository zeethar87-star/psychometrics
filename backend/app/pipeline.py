from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from .config import PIPELINE_STAGES
from .job_store import append_event, job_dir, read_manifest, write_manifest
from .models import JobState


class StageError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _update(job_id: str, stage: str, progress: int, msg: str, state: JobState = JobState.PROCESSING) -> None:
    manifest = read_manifest(job_id)
    manifest["state"] = state.value
    manifest["current_stage"] = stage
    manifest["progress"] = progress
    manifest["what_is_happening"] = msg
    write_manifest(job_id, manifest)
    append_event(
        job_id,
        {
            "type": "progress",
            "progress": progress,
            "stage": stage,
            "message": msg,
            "last_error_code": manifest.get("last_error_code"),
        },
    )


def _checkpoint(job_id: str, stage: str, checkpoint_file: str | None) -> None:
    manifest = read_manifest(job_id)
    manifest["stages"][stage]["state"] = "Done"
    manifest["stages"][stage]["checkpoint"] = checkpoint_file
    write_manifest(job_id, manifest)


def _write_frame(job_id: str, name: str, image: Image.Image) -> None:
    frame_rel = f"artifacts/frames/{name}.png"
    image.save(job_dir(job_id) / frame_rel, format="PNG")
    append_event(
        job_id,
        {
            "type": "frame",
            "frame": frame_rel,
            "stage": name,
            "message": f"Frame ready: {name}",
        },
    )


def stage1_pdf_to_png(job_id: str) -> None:
    manifest = read_manifest(job_id)
    pdf_path = job_dir(job_id) / manifest["files"]["input_pdf"]
    if not pdf_path.exists():
        raise StageError("E-UPLOAD-404", "Input PDF missing")
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]
    img = Image.new("RGB", (900, 700), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((80, 80, 820, 620), outline="black", width=3)
    draw.line((120, 120, 780, 120), fill="black", width=2)
    draw.line((120, 620, 780, 620), fill="black", width=2)
    draw.text((120, 300), f"PDF page 1 placeholder\nsource hash: {pdf_hash}", fill="black")
    out_rel = "artifacts/page1.png"
    img.save(job_dir(job_id) / out_rel, format="PNG")
    _write_frame(job_id, "stage1", img.resize((450, 350)))
    manifest = read_manifest(job_id)
    manifest["files"]["png"] = out_rel
    write_manifest(job_id, manifest)
    _checkpoint(job_id, "stage1_pdf_to_png", out_rel)


def stage2_preprocess(job_id: str) -> None:
    manifest = read_manifest(job_id)
    png_rel = manifest["files"]["png"]
    if not png_rel:
        raise StageError("E-STAGE2-NOINPUT", "No PNG artifact from stage1")
    img = Image.open(job_dir(job_id) / png_rel)
    gray = ImageOps.grayscale(img)
    bw = gray.point(lambda x: 255 if x > 180 else 0, mode="1").convert("L")
    out_rel = "artifacts/preprocessed.png"
    bw.save(job_dir(job_id) / out_rel, format="PNG")
    _write_frame(job_id, "stage2", bw.resize((450, 350)))
    manifest = read_manifest(job_id)
    manifest["files"]["preprocessed"] = out_rel
    write_manifest(job_id, manifest)
    _checkpoint(job_id, "stage2_preprocess", out_rel)


def stage7_build_dxf(job_id: str) -> None:
    manifest = read_manifest(job_id)
    if not manifest["files"]["preprocessed"]:
        raise StageError("E-STAGE7-NOINPUT", "Preprocessed image missing")
    dxf = """0
SECTION
2
ENTITIES
0
LINE
8
A-WALL
10
0.0
20
0.0
11
100.0
21
0.0
0
LINE
8
A-WALL
10
100.0
20
0.0
11
100.0
21
50.0
0
ENDSEC
0
EOF
"""
    out_rel = "artifacts/output.dxf"
    (job_dir(job_id) / out_rel).write_text(dxf, encoding="utf-8")
    frame = Image.new("RGB", (450, 350), "white")
    draw = ImageDraw.Draw(frame)
    draw.line((20, 300, 400, 300), fill="blue", width=3)
    draw.line((400, 300, 400, 120), fill="blue", width=3)
    draw.text((20, 20), "DXF entities created: 2 lines", fill="black")
    _write_frame(job_id, "stage7", frame)
    manifest = read_manifest(job_id)
    manifest["files"]["dxf"] = out_rel
    write_manifest(job_id, manifest)
    _checkpoint(job_id, "stage7_build_dxf", out_rel)


def stage8_validate_dxf(job_id: str) -> None:
    manifest = read_manifest(job_id)
    dxf_rel = manifest["files"]["dxf"]
    if not dxf_rel:
        raise StageError("E-STAGE8-NODXF", "DXF output is missing")
    content = (job_dir(job_id) / dxf_rel).read_text(encoding="utf-8")
    if "LINE" not in content or "EOF" not in content:
        raise StageError("E-DXF-INVALID", "DXF does not include expected entities")
    _checkpoint(job_id, "stage8_validate_dxf", dxf_rel)


def stage9_report(job_id: str) -> None:
    report_rel = "artifacts/report.html"
    report = """
    <html><body>
    <h1>Job Report</h1>
    <p>MVP report generated.</p>
    <ul>
      <li>stage1: page1.png</li>
      <li>stage2: preprocessed.png</li>
      <li>stage7: output.dxf</li>
    </ul>
    </body></html>
    """
    (job_dir(job_id) / report_rel).write_text(report, encoding="utf-8")
    manifest = read_manifest(job_id)
    manifest["files"]["report"] = report_rel
    write_manifest(job_id, manifest)
    _checkpoint(job_id, "stage9_report", report_rel)


def process_job(job_id: str) -> None:
    stages = [
        ("stage1_pdf_to_png", stage1_pdf_to_png, 20),
        ("stage2_preprocess", stage2_preprocess, 45),
        ("stage7_build_dxf", stage7_build_dxf, 75),
        ("stage8_validate_dxf", stage8_validate_dxf, 90),
        ("stage9_report", stage9_report, 100),
    ]
    manifest = read_manifest(job_id)
    manifest["state"] = JobState.PROCESSING.value
    write_manifest(job_id, manifest)
    try:
        for stage_name, fn, pct in stages:
            if manifest["stages"][stage_name]["state"] == "Done":
                continue
            _update(job_id, stage_name, max(1, pct - 10), f"Running {stage_name}")
            fn(job_id)
            _update(job_id, stage_name, pct, f"Completed {stage_name}")
            manifest = read_manifest(job_id)
        manifest["state"] = JobState.DONE.value
        manifest["current_stage"] = "completed"
        manifest["what_is_happening"] = "Job complete"
        manifest["progress"] = 100
        write_manifest(job_id, manifest)
        append_event(job_id, {"type": "done", "progress": 100, "stage": "completed", "message": "Job completed", "last_error_code": None})
    except StageError as exc:
        manifest = read_manifest(job_id)
        manifest["state"] = JobState.FAILED.value
        manifest["last_error_code"] = exc.code
        manifest["what_is_happening"] = str(exc)
        write_manifest(job_id, manifest)
        append_event(job_id, {"type": "error", "progress": manifest.get("progress", 0), "stage": manifest.get("current_stage"), "message": str(exc), "last_error_code": exc.code})
    except Exception as exc:  # noqa: BLE001
        manifest = read_manifest(job_id)
        manifest["state"] = JobState.CRASH.value
        manifest["last_error_code"] = "E-UNEXPECTED"
        manifest["what_is_happening"] = str(exc)
        write_manifest(job_id, manifest)
        append_event(job_id, {"type": "error", "progress": manifest.get("progress", 0), "stage": manifest.get("current_stage"), "message": str(exc), "last_error_code": "E-UNEXPECTED"})
