# MedicalRAG local runbook (WSL2 + Docker Desktop + optional KinD)

Foolproof guide for the zero-copy Compose and Kubernetes stack. See also [LOCAL_CICD.md](./LOCAL_CICD.md).

> **WSL path rule:** Keep the repo under the Linux filesystem (e.g. `/home/ubuntu/projects/MedicalRAG`). Avoid bind-mounting from `/mnt/c/...` — slow I/O and permission pain.

---

## 1. Host prerequisites & installations

### Windows (host)

| Item | Purpose | Install |
|------|---------|---------|
| **WSL 2** | Linux runtime for Ubuntu | `wsl --install` or Microsoft Store “Ubuntu” |
| **Docker Desktop** | Docker engine + Compose from WSL | [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) |
| **Windows Terminal** (optional) | Easier WSL tabs | Microsoft Store |

You do **not** need kubectl/kind on Windows if you run all commands inside WSL Ubuntu.

### WSL Ubuntu (where you run MedicalRAG)

| Tool | Min version | Install (Ubuntu) | Verify |
|------|-------------|------------------|--------|
| **Docker CLI** | Compose v2 | Via Docker Desktop WSL integration (below) | `docker version` |
| **Docker Compose** | v2 | Bundled with Docker Desktop | `docker compose version` |
| **curl**, **git** | any | `sudo apt update && sudo apt install -y curl git ca-certificates` | `curl --version` |
| **Python 3.11+** | 3.11 | `sudo apt install -y python3 python3-venv python3-pip` | `python3 --version` |
| **kubectl** | 1.28+ | [kubectl install](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) | `kubectl version --client` |
| **kind** | 0.20+ | [kind install](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) | `kind version` |

Optional: **Redis CLI** on host for debugging (`sudo apt install -y redis-tools`).

### Enable Docker Desktop WSL 2 integration (fixes “docker could not be found”)

1. Start **Docker Desktop** on Windows and wait until it says “Engine running”.
2. Open **Settings → General** → enable **Use the WSL 2 based engine**.
3. Open **Settings → Resources → WSL Integration**:
   - Turn on **Enable integration with my default WSL distro**.
   - Turn **on** the toggle for your **Ubuntu** distro (the one where the repo lives).
4. Click **Apply & Restart**.
5. In **Windows Terminal**, open **Ubuntu** (not PowerShell) and run:

```bash
docker version
docker compose version
docker run --rm hello-world
```

**What this does:** Docker Desktop runs the engine on Windows but installs the `docker` client into WSL and sets `DOCKER_HOST` so the Ubuntu shell talks to that engine — without this, WSL has no daemon and you see “The command 'docker' could not be found”.

If `docker version` shows **Client** but **Server** errors:

- Confirm Docker Desktop is running on Windows.
- Re-enable WSL integration for your distro and restart Docker Desktop.
- From PowerShell: `wsl --list --verbose` — Ubuntu should be **VERSION 2**.

---

## 2. Path & environment customization

### Recommended layout (WSL)

| Asset | WSL path (example) | Mounted in container at |
|-------|--------------------|-------------------------|
| Repo | `/home/ubuntu/projects/MedicalRAG` | `/app` |
| Virtualenv | `/home/ubuntu/projects/MedicalRAG/venv` | `/app/venv` |
| HF / disease models | `/home/ubuntu/projects/MedicalRAG/ml_core/src/ml_core/models` | `/app/ml_core/src/ml_core/models` |
| Ollama blobs | `/home/ubuntu/.ollama/models` | `/home/ubuntu/.ollama/models` |

`ml_core/src/ml_core/pipeline/resources.py` expects Ollama blobs under `/home/ubuntu/.ollama/models/...` inside the container — the Compose mount target must stay that path.

### Docker Compose — configure paths

**Option A — defaults (repo cloned at `~/projects/MedicalRAG`, venv at `./venv`):**  
No changes needed; see `docker-compose.yml` lines 27–35.

**Option B — override via repo-root `.env` or shell** (Compose substitutes `${VAR}` in the compose file):

```bash
# Append to /home/ubuntu/projects/MedicalRAG/.env (or export before compose)
MEDICALRAG_VENV=/home/ubuntu/projects/MedicalRAG/venv
MEDICALRAG_MODELS=/home/ubuntu/projects/MedicalRAG/ml_core/src/ml_core/models
OLLAMA_MODELS=/home/ubuntu/.ollama/models
```

**Lines that must stay consistent:**

| Compose `source` (host) | Compose `target` (container) | File:lines |
|-------------------------|------------------------------|------------|
| `.` or repo root | `/app` | `docker-compose.yml` 23–25 |
| `${MEDICALRAG_VENV:-./venv}` | `/app/venv` | 26–28 |
| `${MEDICALRAG_MODELS:-./ml_core/...}` | `/app/ml_core/src/ml_core/models` | 29–32 |
| `${OLLAMA_MODELS:-${HOME}/.ollama/models}` | `/home/ubuntu/.ollama/models` | 33–36 |

**Do not use** `/mnt/c/Users/...` for these mounts unless you accept slower mounts and fix permissions; prefer cloning the repo into `~/projects/MedicalRAG` inside WSL.

### Kubernetes — configure paths

Edit **hostPath.path** on both files (keep **mountPath** unchanged):

- `k8s/api-deployment.yaml` — volumes `repo`, `venv`, `ml-models`, `ollama-models` (lines 58–72)
- `k8s/worker-deployment.yaml` — same block (lines 51–65)

Example if your repo is `/home/ubuntu/projects/MedicalRAG`:

```yaml
path: /home/ubuntu/projects/MedicalRAG          # repo
path: /home/ubuntu/projects/MedicalRAG/venv     # venv
path: /home/ubuntu/projects/MedicalRAG/ml_core/src/ml_core/models
path: /home/ubuntu/.ollama/models
```

**KinD on WSL:** The KinD node is a container; `hostPath` is resolved **inside that node**. Use `infra/kind/kind-config.yaml` `extraMounts` so the same paths exist on the node (see Path B step 2).

---

## 3. Step-by-step execution

### Path A — Docker Compose

Run every command from WSL, repo root: `cd /home/ubuntu/projects/MedicalRAG`

1. **Copy environment template**

   ```bash
   cp .env.example .env
   ```

   Creates `.env` from the template so Compose `env_file: .env` and the API config loader can read secrets and URLs.

2. **Edit `.env` (required fields)**

   ```bash
   nano .env   # or code .env
   ```

   Set at minimum `GROQ_API_KEY=...` (required by `entrypoint-api.sh`). For the default Compose stack, set:

   ```env
   DATABASE_URL=postgresql+psycopg://medicalrag:medicalrag@postgres:5432/medicalrag
   ```

   Empty strings for unused S3 fields are fine if `.env.example` already provides them.

3. **Create and populate the host virtualenv (zero-copy dependency source)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements-prod.txt
   pip install -r requirements-dev.txt   # required for RQ workers (rq, torch, etc.)
   deactivate
   ```

   Installs packages on the **host** into `./venv`; containers use `/app/venv/bin/python3` via bind mount — no heavy COPY in the image.

4. **Validate Compose syntax**

   ```bash
   docker compose config --quiet
   ```

   Renders the final compose model (env substitution, merges) and exits non-zero if YAML or references are invalid.

5. **Build the slim runtime image**

   ```bash
   docker compose build
   ```

   Builds `medicalrag-local:runtime` from the root `Dockerfile` (entrypoints + optional deps only; no models).

6. **Start base stack**

   ```bash
   docker compose up -d
   ```

   Creates VPC-style networks, starts Redis/Postgres (health waits), then API + worker + Nginx LB; API uses production uvicorn on port 10000 inside the network.

7. **Scale API and workers**

   ```bash
   docker compose up -d --scale api=3
   # rq-worker: default 1; each extra replica adds ~4–6 GiB (full NLP stack per process)
   # docker compose up -d --scale rq-worker=2
   ```

   Adds more containers for services `api` and `rq-worker`; Compose DNS returns multiple backends for `api`, and Nginx `least_conn` balances across them.

8. **Health checks through Nginx (host port 8080 by default)**

   ```bash
   curl -sf http://localhost:8080/healthz && echo "LB health OK"
   ```

   Hits Nginx `/healthz` (direct 200 from edge tier, no upstream).

   ```bash
   curl -sf http://localhost:8080/ | head -c 500 && echo
   ```

   Proxies to an `api` upstream; success means LB → FastAPI → JSON health payload from `app.main`.

   ```bash
   curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8080/
   ```

   Prints only HTTP status — quick pass/fail without dumping body.

9. **Optional: direct API container (bypass LB)**

   ```bash
   docker compose ps api
   docker compose exec api curl -sf http://127.0.0.1:10000/
   ```

   Lists API tasks and curls uvicorn inside one container (sanity check without Nginx).

10. **Teardown**

    ```bash
    docker compose down
    ```

    Stops and removes containers/networks; named volume `postgres-data` persists unless you add `-v`.

---

### Docker Desktop Kubernetes vs KinD (read this if pods stick in `ContainerCreating`)

**Symptom:** `api` / `rq-worker` stay `ContainerCreating` for many minutes; `kubectl describe pod` shows:

```text
FailedMount ... hostPath type check failed: /home/ubuntu/projects/MedicalRAG/venv is not a directory
```

**Cause:** Docker Desktop’s built-in Kubernetes (`desktop-worker`, `desktop-worker2`) is **not** the same filesystem as your WSL Ubuntu home. A stub path may exist on the node (often only `ml_core/` from `DirectoryOrCreate`), but **not** your full repo or `venv`. Zero-copy `hostPath` **does not work** on bundled Docker Desktop K8s without custom node mounts.

**Fix:** Use **KinD** with [`infra/kind/kind-config.yaml`](../infra/kind/kind-config.yaml) `extraMounts`, or use **Docker Compose** for local verification.

Quick reset to KinD:

```bash
kubectl config use-context kind-medicalrag   # after setup-kind script
# or: ./scripts/setup-kind-medicalrag.sh
```

Disable Docker Desktop Kubernetes (Settings → Kubernetes → untick Enable) if you only want KinD, to avoid applying manifests to the wrong cluster.

### Path B — Kubernetes (KinD)

Assumes repo at `/home/ubuntu/projects/MedicalRAG` and paths in manifests match. Adjust `infra/kind/kind-config.yaml` `extraMounts` if your paths differ.

1. **Create KinD cluster with host mounts and NodePort 8080**

   ```bash
   kind delete cluster --name medicalrag 2>/dev/null || true
   kind create cluster --name medicalrag --config infra/kind/kind-config.yaml
   ```

   Provisions a single-node cluster; `extraMounts` mirror WSL repo/Ollama paths into the node; `extraPortMappings` maps NodePort 30080 to host 8080.

2. **Build image and load into KinD**

   ```bash
   cd /home/ubuntu/projects/MedicalRAG
   docker compose build
   kind load docker-image medicalrag-local:runtime --name medicalrag
   ```

   Builds on Docker Desktop engine, then imports the image tarball into the KinD node’s containerd (no registry pull).

3. **Point kubectl at the cluster**

   ```bash
   kubectl cluster-info --context kind-medicalrag
   ```

   Confirms API server reachability for context `kind-medicalrag`.

4. **Create secrets (Groq + optional keys)**

   ```bash
   cp k8s/secret.example.yaml k8s/secret.yaml
   nano k8s/secret.yaml   # set GROQ_API_KEY at minimum
   kubectl apply -f k8s/secret.yaml
   ```

   Creates `medicalrag-secrets` in namespace `medicalrag` (namespace created by kustomize or apply order — secret yaml includes namespace).

5. **Apply manifests**

   ```bash
   kubectl apply -k k8s/
   ```

   Applies namespace, ConfigMaps, Redis, Postgres, API, workers, Nginx LB, and NetworkPolicies via Kustomize.

6. **Wait for rollouts**

   ```bash
   kubectl rollout status deployment/api -n medicalrag --timeout=300s
   kubectl rollout status deployment/rq-worker -n medicalrag --timeout=300s
   kubectl rollout status deployment/loadbalancer -n medicalrag --timeout=120s
   ```

   Blocks until Deployments report minimum available replicas (readiness probes passing).

7. **Scale replicas**

   ```bash
   kubectl scale deployment/api -n medicalrag --replicas=3
   kubectl scale deployment/rq-worker -n medicalrag --replicas=1
   ```

   Patches Deployment `spec.replicas`; controllers create/destroy Pods to match.

8. **Access via mapped host port or port-forward**

   ```bash
   curl -sf http://localhost:8080/healthz && echo "KinD LB OK"
   curl -sf http://localhost:8080/
   ```

   Uses `kind-config.yaml` hostPort 8080 → NodePort 30080 → `loadbalancer` Service when mapping works.

   If 8080 is busy or mapping fails:

   ```bash
   kubectl port-forward -n medicalrag svc/loadbalancer 8080:8080
   ```

   Opens a local TCP tunnel from your WSL shell to the Nginx Service (run in a separate terminal, then curl `localhost:8080`).

9. **Inspect**

   ```bash
   kubectl get pods,svc -n medicalrag
   kubectl logs -n medicalrag deployment/api --tail=50
   ```

   Lists workload state and recent API logs from one Pod in the Deployment.

10. **Delete cluster**

    ```bash
    kind delete cluster --name medicalrag
    ```

    Removes the KinD container and cluster kubeconfig context.

---

## 4. Troubleshooting & verification

### 1) Confirm bind mounts (Compose)

```bash
docker compose exec api ls -la /app/venv/bin/python3
docker compose exec api /app/venv/bin/python3 -c "import sys; print(sys.executable)"
```

**Expect:** `python3` exists and prints `/app/venv/bin/python3` — proves the host venv is mounted, not image-only Python.

### 2) Confirm repo + models mount (Compose)

```bash
docker compose exec api test -f /app/run_prod.sh && echo "repo mount OK"
docker compose exec api ls /app/ml_core/src/ml_core/models 2>/dev/null | head
docker compose exec rq-worker ls /home/ubuntu/.ollama/models 2>/dev/null | head
```

**Expect:** `run_prod.sh` visible at `/app`; model/Ollama dirs list host content (may be empty if you have not downloaded models yet).

### 3) API / worker logs (Compose)

```bash
docker compose logs --tail=80 api
docker compose logs --tail=80 rq-worker
```

**Expect:** API log line `Starting MedicalRAG API (production) on 0.0.0.0:10000`; worker `Starting MedicalRAG RQ worker`. Errors like `GROQ_API_KEY must be set` or `No module named ...` point to `.env` or incomplete `venv`.

### 4) KinD mount + venv (Kubernetes)

```bash
POD=$(kubectl get pod -n medicalrag -l app=api -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n medicalrag "$POD" -- ls -la /app/venv/bin/python3
kubectl exec -n medicalrag "$POD" -- /app/venv/bin/python3 -c "import fastapi; print('venv OK')"
kubectl describe pod -n medicalrag "$POD" | sed -n '/Mounts:/,/Conditions:/p'
```

**Expect:** Same venv path as Compose; `Mounts` shows `repo`, `venv`, `ml-models`, `ollama-models` from hostPath. If `ls` fails inside Pod but works on WSL host, fix `infra/kind/kind-config.yaml` extraMounts paths.

### Common failures

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `docker: not found` in WSL | Docker Desktop integration off | Section 1 integration steps |
| Compose fails: `.env` missing | No env file | `cp .env.example .env` |
| API exits immediately | Missing `GROQ_API_KEY` | Set in `.env` |
| Worker restart loop | Empty venv or missing `rq` | `pip install -r requirements-dev.txt` in host `venv` |
| KinD Pod `CrashLoopBackOff`, empty `/app` | hostPath not on KinD node | Recreate cluster with `infra/kind/kind-config.yaml` |
| LB 502 | API not healthy | `docker compose logs api` or `kubectl logs deployment/api -n medicalrag` |
