from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "jobs"
STATIC_DIR = BASE_DIR / "frontend"
THROTTLE_SECONDS = 0.5
PIPELINE_STAGES = [
    "stage1_pdf_to_png",
    "stage2_preprocess",
    "stage7_build_dxf",
    "stage8_validate_dxf",
    "stage9_report",
]
