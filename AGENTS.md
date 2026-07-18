# AGENTS.md

QTI Maker is a Python 3.10+ tool that converts Markdown-based plain text into IMS QTI quiz packages for LMSes like Canvas. It is a fork of [text2qti](https://github.com/gpoore/text2qti) that adds a **FastAPI web interface**, **AI question generation** (Google Gemini via `google-genai`), and **document ingestion** (Docling). The QTI engine lives in `qtimaker/` (`quiz.py`, `qti.py`, `markdown.py`, the `xml_*.py` writers); the web layer lives in `qtimaker/web/` (`app.py`, `routes/`, `services/`).

## Setup
Requires Python 3.10 or newer.
```bash
python3 -m pip install setuptools
python3 -m pip install docling          # may pull extra system deps — see README
python3 -m pip install -e ".[dev]"      # editable install + ruff (dev extra)
cp .env.example .env                     # add GEMINI_API_KEY for AI generation
```
On Windows, use `python -m pip …` (or the `py` launcher). Docling can require additional OS-level packages; the README's install section documents platform specifics and troubleshooting.

## Build & Run
- **CLI:** `qtimaker path/to/quiz.txt` → writes a QTI `.zip`. (Console script `qtimaker = qtimaker.cmdline:main`.)
- **Tk GUI:** `qtimaker_tk`; a Windows `.exe` can be built from `make_gui_exe/`.
- **Web (development):**
  ```bash
  python3 -m qtimaker.web.app          # or: uvicorn qtimaker.web.app:app --reload
  # serves http://localhost:8000
  ```
- **Web (production, container):**
  ```bash
  docker compose -f docker-compose.prod.yml up --build
  ```
  The image is `python:3.11-slim`, installs from `pyproject.toml`, runs `uvicorn qtimaker.web.app:app --host 0.0.0.0 --port 8000 --workers 2` as an unprivileged user, and mounts a `qtimaker_uploads` volume. It expects an external Docker network named `proxy` and an `.env` file.

## Testing
No automated test suite or test runner is configured in this repo (no `tests/` directory, no pytest/tox config). Before considering a change done: run the linter (below), exercise the CLI on a sample quiz file, and — for web changes — start the server and hit the affected route manually.

## Code Style
- **Ruff** is the linter (dev extra), configured with `line-length = 120` in `pyproject.toml`:
  ```bash
  python3 -m ruff check .
  ```
- Keep changes focused (one logical change per PR) and match the surrounding style; several modules carry `# -*- coding: utf-8 -*-` headers.
- **Preserve attribution:** the core engine derives from text2qti under the BSD 3-Clause License. Keep existing copyright notices intact.

## Commit & PR Conventions
- Branch `main`. Commit subjects follow a light Conventional-Commits style seen in history: `feat(web): …`, `fix(web): …`, `docs: …`, `deps: …`, `chore: …`.
- Keep pull requests focused and lint-clean. Use the templates in `.github/` (`PULL_REQUEST_TEMPLATE.md`, issue templates).
- Report **security vulnerabilities** privately via `SECURITY.md` — do not open a public issue.

## Security & Data
- **Never commit secrets or uploads.** `.env`, API keys, and everything under `/uploads/` are git-ignored — keep it that way.
- Configuration via env (`.env.example`): `GEMINI_API_KEY` (Gemini access) and `ALLOWED_ORIGINS` (comma-separated CORS allowlist). CORS is credential-aware — a `*` wildcard is rejected when credentials are enabled, so set explicit origins in production; the local default is `http://localhost:8000` / `http://127.0.0.1:8000`.
- Treat AI-generated and user-uploaded content as untrusted: escape it in templates/UI (a prior fix hardened this) to avoid injection in the browser.
