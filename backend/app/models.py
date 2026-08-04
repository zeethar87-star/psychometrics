from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class JobState(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    DONE = "Done"
    FAILED = "Failed"
    CRASH = "Crash"


@dataclass
class StageResult:
    state: str
    error_code: str | None = None
    message: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
