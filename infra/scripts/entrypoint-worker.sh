#!/usr/bin/env bash
# RQ worker bootstrap — same env loading and PYTHONPATH as run_prod.sh / entrypoint-api.sh.
set -euo pipefail

ROOT="${MEDICALRAG_ROOT:-/app}"
API_DIR="${ROOT}/apps/api"

cd "${API_DIR}"

# Workers run the dev NLP pipeline (Redis queue). Override only if explicitly set.
export APP_ENV="${WORKER_APP_ENV:-dev}"
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

# Re-apply worker mode after .env (which may set APP_ENV=production).
export APP_ENV="${WORKER_APP_ENV:-dev}"

mkdir -p "${API_DIR}/files"

PYTHON="${ROOT}/venv/bin/python3"
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON=python3
fi

echo "Starting MedicalRAG RQ worker (APP_ENV=${APP_ENV}, queue=ai_queue)"
exec "${PYTHON}" -m app.worker.worker
