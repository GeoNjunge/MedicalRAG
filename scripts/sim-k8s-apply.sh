#!/usr/bin/env bash
# Apply KinD/K8s manifests with the same memory budget caps as sim-up.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# shellcheck source=../infra/scripts/lib/sim-memory.sh
source "${ROOT}/infra/scripts/lib/sim-memory.sh"

export SIM_MEMORY_ROOT="${ROOT}"

if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
fi

sim_print_plan

if [[ ! -f "${ROOT}/k8s/secret.yaml" ]]; then
  echo "Create k8s/secret.yaml from k8s/secret.example.yaml first." >&2
  exit 1
fi

kubectl apply -f k8s/secret.yaml
kubectl apply -k k8s/

kubectl patch configmap medicalrag-config -n medicalrag --type merge \
  -p "{\"data\":{\"SIM_BUDGET_GIB\":\"${SIM_BUDGET_GIB}\",\"SIM_MAX_RQ_WORKERS\":\"${SIM_MAX_RQ_WORKERS}\"}}"

kubectl scale deployment/api -n medicalrag --replicas="${SIM_API_REPLICAS}"
kubectl scale deployment/rq-worker -n medicalrag --replicas="${SIM_MAX_RQ_WORKERS}"

per_worker_mib="$(awk -v lim="${RQ_WORKER_MEM_LIMIT}" 'BEGIN {
  gsub(/g$/, "", lim); gsub(/G$/, "", lim);
  printf "%.0f", lim * 1024
}')"

kubectl set resources deployment/rq-worker -n medicalrag \
  --limits=memory="${per_worker_mib}Mi",cpu=2000m \
  --requests=memory="$(( per_worker_mib * 2 / 3 ))Mi",cpu=1000m

echo "K8s scaled to api=${SIM_API_REPLICAS}, rq-worker=${SIM_MAX_RQ_WORKERS}."
