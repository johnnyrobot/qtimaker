FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code and install from pyproject.toml (single source of
# truth for dependencies) so the image matches the tested dependency set.
COPY . .
RUN pip install --no-cache-dir .

# Run as an unprivileged user; give it ownership of the writable upload dir.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/uploads \
    && chown -R appuser:appuser /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

USER appuser

CMD ["uvicorn", "qtimaker.web.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
