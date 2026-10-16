#!/usr/bin/env bash
# One-shot KinD cluster for MedicalRAG hostPath zero-copy (WSL2 + Docker Desktop).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="${KIND_CLUSTER_NAME:-medicalrag}"

cd "$ROOT"

if ! command -v kind >/dev/null 2>&1; then
  echo "Install kind first: https://kind.sigs.k8s.io/docs/user/quick-start/#installation" >&2
  exit 1
fi

if [[ ! -d "$ROOT/venv/bin" && ! -d "$ROOT/.venv/bin" ]]; then
  echo "Warning: no ./venv (or .venv) on host — create one before API/worker pods can start." >&2
fi

if [[ ! -f "$ROOT/k8s/secret.yaml" ]]; then
  echo "Create k8s/secret.yaml from k8s/secret.example.yaml (GROQ_API_KEY required)." >&2
  exit 1
fi

# Patch kind extraMounts if repo is not the default path.
CONFIG="$ROOT/infra/kind/kind-config.yaml"
if [[ "$ROOT" != "/home/ubuntu/projects/MedicalRAG" ]]; then
  echo "Repo is at $ROOT — update infra/kind/kind-config.yaml extraMounts hostPath values to match."
fi

kind delete cluster --name "$CLUSTER_NAME" 2>/dev/null || true
kind create cluster --name "$CLUSTER_NAME" --config "$CONFIG"

docker compose build
kind load docker-image medicalrag-local:runtime --name "$CLUSTER_NAME"

kubectl config use-context "kind-${CLUSTER_NAME}"
kubectl apply -f k8s/secret.yaml
kubectl apply -k k8s/

echo "Waiting for API..."
kubectl rollout status deployment/api -n medicalrag --timeout=300s
kubectl rollout status deployment/loadbalancer -n medicalrag --timeout=120s

echo "Try: curl -sf http://localhost:8080/healthz"
