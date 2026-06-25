# -*- coding: utf-8 -*-
#
# FastAPI application for QTI Maker web interface
#

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from .routes import upload, questions, quiz_generation

app = FastAPI(title="QTI Maker Web Interface", version=__version__)

# CORS middleware.
# Restrict origins via the ALLOWED_ORIGINS env var (comma-separated). A
# wildcard "*" is rejected when credentials are enabled, so credentials are
# only allowed when an explicit origin allowlist is configured.
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    # Safe local default; override in production via ALLOWED_ORIGINS.
    allowed_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(upload.router)
app.include_router(questions.router)
app.include_router(quiz_generation.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

