# Local CI/CD & orchestration

Lightweight end-to-end stack for verifying MedicalRAG with **zero-copy bind mounts** (repo, host `venv`, HF/Ollama model weights). API startup matches [`run_prod.sh`](../run_prod.sh).

## Architecture

```text
Client → Nginx (edge) → FastAPI replicas (APP_ENV=production, uvicorn)
                              ↓
                         Postgres (shared state when scaling API)
Redis ← RQ workers (APP_ENV=dev, local NLP pipeline)
```

| Tier | Compose network | K8s label `tier` | Components |
|------|-----------------|------------------|------------|
| Edge | `vpc-edge` | `edge` | Nginx load balancer |
| App | `vpc-app` | `application` | API (`entrypoint-api.sh`) |
| Data | `vpc-data` | `data` | Redis, Postgres |
| Workers | `vpc-workers` | `workers` | RQ (`entrypoint-worker.sh`) |

**Note:** Production API jobs run **in-process** (Groq). RQ workers serve the **dev** pipeline for local/CI NLP testing; scale workers with `APP_ENV=dev` independently of prod API replicas.

## Prerequisites

- Docker Compose v2 and (optional) kind/minikube for Kubernetes
- Repo root `.env` from `.env.example` with **`GROQ_API_KEY`** set (required by `run_prod.sh`)
- Host virtualenv at `./venv` with dependencies installed (`pip install -r requirements-prod.txt` minimum; workers need `requirements-dev.txt`)
- Model bind mounts (optional for prod-only smoke tests; required for RQ workers):
  - `ml_core/src/ml_core/models/`
  - `~/.ollama/models/` (llama.cpp GGUF paths in `resources.py`)

## Step-by-step — Docker Compose

1. **Build the slim runtime image** (no model COPY):
   ```bash
   cd /home/ubuntu/projects/MedicalRAG
   docker compose build
   ```

2. **Configure environment** — copy and edit `.env`; ensure Postgres URL when using the default stack:
   ```bash
   cp .env.example .env
   # Set GROQ_API_KEY, and optionally:
   # DATABASE_URL=postgresql+psycopg://medicalrag:medicalrag@postgres:5432/medicalrag
   ```

3. **Start the full stack** (LB + API + Redis + Postgres + workers):
   ```bash
   docker compose up -d
   ```

4. **Scale API and workers** (Compose DNS round-robins `api` for Nginx):
   ```bash
   docker compose up -d --scale api=3 --scale rq-worker=4
   ```

5. **Verify**:
   ```bash
   curl -sf http://localhost:8080/healthz
   curl -sf http://localhost:8080/
   ```

6. **Logs / teardown**:
   ```bash
   docker compose logs -f api rq-worker loadbalancer
   docker compose down
   ```

### Compose tuning

| Variable | Default | Purpose |
|----------|---------|---------|
| `LB_PORT` | `8080` | Published load balancer port |
| `WORKERS` | `1` | Uvicorn workers per API container (`run_prod.sh`) |
| `PREINSTALL_DEPS` | `0` | Set `1` at build time to bake `requirements-prod.txt` when no host `venv` |
| `MEDICALRAG_VENV` | `./venv` | Host path mounted to `/app/venv` |
| `MEDICALRAG_MODELS` | `./ml_core/src/ml_core/models` | HF / disease model weights |
| `OLLAMA_MODELS` | `$HOME/.ollama/models` | GGUF blobs for local summarizer |

See [`infra/network/vpc-subnets.env`](../infra/network/vpc-subnets.env) for the simulated VPC layout.

## Step-by-step — Kubernetes (local cluster)

1. **Build image into the cluster** (kind example):
   ```bash
   docker compose build
   kind load docker-image medicalrag-local:runtime
   ```

2. **Adjust host paths** in `k8s/api-deployment.yaml` and `k8s/worker-deployment.yaml` if your repo is not `/home/ubuntu/projects/MedicalRAG`.

3. **Create secrets** (never commit):
   ```bash
   cp k8s/secret.example.yaml k8s/secret.yaml
   # edit GROQ_API_KEY, then:
   kubectl apply -f k8s/secret.yaml
   ```

4. **Apply manifests**:
   ```bash
   kubectl apply -k k8s/
   ```

5. **Scale replicas**:
   ```bash
   kubectl scale deployment/api -n medicalrag --replicas=3
   kubectl scale deployment/rq-worker -n medicalrag --replicas=4
   ```

6. **Access** via NodePort `30080` or port-forward:
   ```bash
   kubectl port-forward -n medicalrag svc/loadbalancer 8080:8080
   curl -sf http://127.0.0.1:8080/
   ```

Network policies in `k8s/network-policies.yaml` mirror Compose tier isolation (requires a CNI that enforces `NetworkPolicy`).

## CI hook (optional)

After unit tests, validate the image and compose config:

```bash
docker compose config --quiet
docker compose build
docker compose up -d --scale api=2 --scale rq-worker=2
curl -sf http://localhost:8080/healthz
docker compose down -v
```

## Files reference

| File | Role |
|------|------|
| [`Dockerfile`](../Dockerfile) | Slim runtime; optional `PREINSTALL_DEPS`; no model COPY |
| [`docker-compose.yml`](../docker-compose.yml) | Local orchestration + VPC-style networks |
| [`infra/scripts/entrypoint-api.sh`](../infra/scripts/entrypoint-api.sh) | Production uvicorn (`run_prod.sh` parity) |
| [`infra/scripts/entrypoint-worker.sh`](../infra/scripts/entrypoint-worker.sh) | RQ worker with shared env bootstrap |
| [`infra/nginx/nginx.conf`](../infra/nginx/nginx.conf) | Edge load balancing to `api:10000` |
| [`k8s/`](../k8s/) | Deployments, Services, ConfigMaps, NetworkPolicies |
