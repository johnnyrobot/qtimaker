FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies extracted from pyproject.toml
RUN pip install --no-cache-dir \
    'bespon>=0.7.0' \
    'markdown>=3.4.4' \
    'fastapi>=0.104.0' \
    'uvicorn[standard]>=0.24.0' \
    'python-multipart>=0.0.6' \
    'jinja2>=3.1.2' \
    'python-dotenv>=1.0.0' \
    'google-generativeai>=0.3.0' \
    'pydantic>=2.5.0' \
    'docling>=1.0.0'

# Copy application code
COPY . .

RUN mkdir -p /app/uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "qtimaker.web.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
