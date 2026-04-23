---
name: new-cloud-run-job
description: Use this skill when creating a new Cloud Run Job, modifying deployment structure, or understanding conventions for legacy vs new BigQuery-based jobs.
---

# Skill: Adding a New Cloud Run Job

## When to use
Use this skill when creating a new Cloud Run Job or modifying the deployment structure.

## Steps to create a new job

1. **Create directory:** `jobs/<job-name>/`
2. **Create files:**
   - `main.py` — Entry point
   - `requirements.txt` — Python dependencies
   - `Procfile` — `web: python main.py` (for Cloud Run)
3. **Virtual environment:** `python3 -m venv virt && source virt/bin/activate && pip install -r requirements.txt`
4. **Do NOT commit** `virt/`, `__pycache__/`, `.env`

## Conventions for new jobs (BigQuery-based)
- Use `python-dotenv` + `os.getenv()` for all config
- Use `logging` module (not `print()`)
- Use `click` for CLI interfaces
- Use parameterized BigQuery queries
- Use Python 3.13+ type hints (`list[str]`, `X | None`)
- Each job is fully self-contained (no shared imports across jobs except `volume-1/` for legacy)

## Legacy jobs (pickle-based)
- Legacy jobs import from `volume-1/common/` via `sys.path.append`
- They use `pickle` for data serialization
- They use Pub/Sub to trigger downstream jobs
- Do not modify legacy jobs unless specifically asked — they are production and stable

## Makefile
The root `Makefile` handles `make setup` (creates all venvs) and `make clean` (removes them).

