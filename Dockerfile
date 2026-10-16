# Local / CI image — "no-copy" for heavy assets.
# Source code, venv, HF/Ollama models, and ml_core model weights are bind-mounted at runtime.
# Build only caches lightweight production Python dependencies (optional layer).

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="MedicalRAG-local" \
      org.opencontainers.image.description="Runtime shell for bind-mounted MedicalRAG repo (no model COPY)"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    MEDICALRAG_ROOT=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Optional dependency layer: requirements file only (no apps/, ml_core/, models/, or venv/).
ARG PREINSTALL_DEPS=0
COPY requirements-prod.txt /tmp/requirements-prod.txt
RUN if [ "$PREINSTALL_DEPS" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends \
        build-essential libffi-dev libssl-dev \
      && pip install --upgrade pip \
      && pip install -r /tmp/requirements-prod.txt \
      && apt-get purge -y build-essential \
      && apt-get autoremove -y \
      && rm -rf /var/lib/apt/lists/* ; \
    fi

COPY infra/scripts/entrypoint-api.sh infra/scripts/entrypoint-worker.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint-api.sh /usr/local/bin/entrypoint-worker.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/entrypoint-api.sh"]
