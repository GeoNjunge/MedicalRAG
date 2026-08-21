#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="${ROOT}/apps/api"

cd "${API_DIR}"

export APP_ENV=production
export PYTHONPATH="${ROOT}:${API_DIR}:${ROOT}/ml_core/src"

if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
elif [[ -f "${API_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${API_DIR}/.env"
  set +a
fi

if [[ -z "${GROQ_API_KEY:-}" ]]; then
  echo "Error: GROQ_API_KEY must be set for production." >&2
  exit 1
fi

mkdir -p "${API_DIR}/files"

PYTHON="${ROOT}/venv/bin/python3"
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON=python3
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"

echo "Starting MedicalRAG API (production) on ${HOST}:${PORT}"
exec "${PYTHON}" -m uvicorn app.main:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --workers "${WORKERS}"
