# CLAUDE.md

QTI Maker turns Markdown-style plain text into IMS QTI quiz packages for Canvas and other LMSes. It is a fork of [text2qti](https://github.com/gpoore/text2qti) that adds a FastAPI web interface, AI-powered question generation (Google Gemini), and document ingestion (Docling). Python 3.10+; package name `qtimaker`, version in `qtimaker/version.py` (0.7.1).

## Architecture
- **Core engine (inherited from text2qti — BSD 3-Clause):** `qtimaker/quiz.py` (the big parser/model), `markdown.py`, `qti.py`, `export.py`, `config.py`, and the QTI XML writers `xml_assessment.py`, `xml_assessment_v2.py`, `xml_assessment_meta.py`, `xml_imsmanifest.py`, plus `pymd_pandoc_attr.py`, `fmtversion.py`, `err.py`. These produce the QTI `.zip` from parsed quiz text.
- **CLI:** entry point `qtimaker = qtimaker.cmdline:main` (`qtimaker/cmdline.py`) — reads a Markdown/plain-text quiz file and writes a QTI package.
- **Tk GUI:** entry point `qtimaker_tk = qtimaker.gui.tk:main`; `make_gui_exe/` builds a Windows `.exe`.
- **Web app (new in this fork):** `qtimaker/web/app.py` — FastAPI app (`title="QTI Maker Web Interface"`), CORS-guarded, serves `web/templates/index.html` and `web/static/`.
  - Routes: `web/routes/upload.py`, `web/routes/questions.py`, `web/routes/quiz_generation.py`.
  - Services: `web/services/docling_service.py` (document → text extraction via Docling).
  - AI generation uses `google-genai` (Gemini); config in `web/config.py` and `qtimaker/config.py`.
- Runtime uploads land in the git-ignored `/uploads/` directory.

## Commands
```bash
# Install (editable) — Python 3.10+
python3 -m pip install setuptools
python3 -m pip install docling          # may need extra system deps; see README
python3 -m pip install -e ".[dev]"      # [dev] adds ruff

# CLI: text -> QTI package
qtimaker path/to/quiz.txt

# Web interface (http://localhost:8000)
python3 -m qtimaker.web.app
uvicorn qtimaker.web.app:app --reload    # dev, auto-reload

# Lint
python3 -m ruff check .

# Container (production)
docker compose -f docker-compose.prod.yml up --build   # needs external `proxy` network + .env
```
(No automated test suite / test script found in the repo.)

## Conventions
- **Ruff** is the linter/formatter, `line-length = 120` (`[tool.ruff]` in `pyproject.toml`). Run `ruff check .` before finishing.
- `pyproject.toml` is the single source of truth for dependencies; the Dockerfile installs from it. Version is dynamic from `qtimaker.__version__`.
- Web content is user- and AI-generated: escape it in templates/UI (a prior fix removed unescaped output) — treat model and upload text as untrusted.
- Keep files ASCII/UTF-8 with the existing `# -*- coding: utf-8 -*-` headers where present.

## Gotchas & Constraints
- **Preserve attribution.** The core QTI engine derives from text2qti (Geoffrey M. Poore, Glenn Horton-Smith) under BSD 3-Clause. Keep existing copyright notices intact when editing `quiz.py`, `qti.py`, the `xml_*` writers, etc.
- **Never commit secrets or sample data.** `.env`, API keys, and everything under `/uploads/` are git-ignored — keep them that way. `GEMINI_API_KEY` and `ALLOWED_ORIGINS` come from `.env` (see `.env.example`).
- **CORS is credential-aware:** a wildcard origin is rejected when credentials are enabled. In production set `ALLOWED_ORIGINS` to explicit origin(s); local default is `http://localhost:8000` / `http://127.0.0.1:8000`.
- **Docling is heavy** and may need extra system dependencies to install (see README troubleshooting). The Docker image runs `uvicorn ... --workers 2` on port 8000 as an unprivileged `appuser`.
- Security vulnerabilities go through `SECURITY.md`, not public issues.
