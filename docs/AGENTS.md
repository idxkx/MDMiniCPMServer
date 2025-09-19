# Repository Guidelines

## Project Structure & Module Organization
- src/: FastAPI application code (entry: src/main.py).
- docker/: Dockerfile and compose setup; mounts models/ read-only to /app/models.
- models/: local model folders; treated as data, not code.
- docs/: scaffold notes (see docs/SCAFFOLD.md).
- REQUIREMENTS.TXT, .env(.example): runtime deps and configuration.

## Build, Test, and Development Commands
- Install: `pip install -r REQUIREMENTS.TXT`
- Run (local): `PYTHONPATH=src python -m uvicorn main:app --host 0.0.0.0 --port 8207`
  - Health: `curl -f http://127.0.0.1:8207/health`; Models: `curl -s http://127.0.0.1:8207/models`
- Docker: `docker compose -f docker/docker-compose.yml up -d --build`
  - Logs: `docker compose -f docker/docker-compose.yml logs -f`; Down: `... down`
  - Host port override: `HOST_PORT=8207 ... up -d`

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indent; use type hints; line length <= 100.
- Modules/files: lower_snake_case; constants UPPER_SNAKE_CASE; functions lower_snake_case.
- Group imports: stdlib, third-party, local.
- No formatter configured; keep consistent. If used locally, prefer black + ruff (do not change deps).

## Testing Guidelines
- Framework: pytest (suggested; not bundled). Layout: tests/test_*.py.
- Add FastAPI endpoint tests with httpx TestClient.
- Run: `pytest -q`. Target basic coverage for changed code; include happy-path and failure cases.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise summary; prefer Conventional Commits (feat, fix, docs, chore, refactor).
- PRs must include: purpose, linked issues, what changed, how to validate (e.g., curl health/models), and any Docker rebuild steps.
- For API changes, include example requests/responses; for Docker changes, include image size / run notes.

## Security & Configuration Tips
- Never commit secrets; use `.env` (already gitignored). Keep large model weights out of Git when possible-mount via compose.
- Honor env vars: SERVER_HOST, SERVER_PORT, MODEL_PATH. Read-only mount of models protects runtime.
- If adding caches/temp, write under a mounted path (e.g., /app/temp) to avoid bloating images.
