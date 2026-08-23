# Local Runbook

## Prerequisites
- Python 3.11+

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (single command)
```bash
make run
```
Then open `http://localhost:8000`.

## Optional RQ+Redis mode
```bash
export JOB_BACKEND=rq
redis-server
python -m backend.rq_worker
python -m backend.run_local
```

## Demo sample
- Use `tests/assets/sample_plan.pdf` from upload page.
