from __future__ import annotations

import os
import threading

from .pipeline import process_job


def enqueue_job(job_id: str) -> str:
    backend = os.getenv("JOB_BACKEND", "local")
    if backend == "rq":
        from redis import Redis
        from rq import Queue

        conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        q = Queue("dxf", connection=conn)
        q.enqueue(process_job, job_id)
        return "rq"

    thread = threading.Thread(target=process_job, args=(job_id,), daemon=True)
    thread.start()
    return "local-thread"
