# Production API image (lightweight — no local LLM stack)
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/apps/api:/app/ml_core/src \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements-prod.txt requirements-prod.txt
COPY apps ./apps
COPY ml_core ./ml_core

RUN pip install --no-cache-dir -r requirements-prod.txt

RUN mkdir -p /app/apps/api/files /app/logs

WORKDIR /app/apps/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
