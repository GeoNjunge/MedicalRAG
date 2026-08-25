# MedicalRAG Remediation Backlog

Prioritized from the enterprise engineering audit. **P0 = ship-blocking**, **P1 = production-hardening**, **P2 = quality & scale**.

---

## P0 — Critical (implemented)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| P0-1 | Fix job state machine: failed jobs must not become `completed` | ✅ Done | `apps/api/app/worker/tasks.py` |
| P0-2 | Guard `db` in worker exception handlers | ✅ Done | `tasks.py` |
| P0-3 | Remove `ml_core` → `apps.api` dependency inversion | ✅ Done | `ml_core/logging_utils.py` |
| P0-4 | API key auth on upload + SSE; job existence check on SSE | ✅ Done | `app/core/auth.py`, routes |
| P0-5 | Redis Pub/Sub for job events (multi-worker safe) | ✅ Done | `app/services/job_events.py` |
| P0-6 | Fix silent SSE failures; unify event stream path | ✅ Done | `upload.py`, `ai_pipeline.py` |
| P0-7 | Honor `DATABASE_URL` in SQLAlchemy engine | ✅ Done | `database/session.py` |
| P0-8 | Fix pytest fixtures (`conftest.py`) and upload test | ✅ Done | `app/tests/` |
| P0-9 | Validate `patient_id` / filename on upload | ✅ Done | `upload_services.py` |
| P0-10 | Disable `/docs` in production | ✅ Done | `main.py` |
| P0-11 | Frontend API key support (header + SSE query param) | ✅ Done | `mednlp-api.service.ts` |

---

## P1 — Production hardening

| ID | Item | Status | Notes |
|----|------|--------|-------|
| P1-1 | Wire S3 upload/download (remove local `files/` as source of truth) | ⏳ Pending | Dead code path; PHI on app disk |
| P1-2 | Durable job queue (outbox pattern) — rollback DB if Redis enqueue fails | ⏳ Pending | Prevents orphaned pending jobs |
| P1-3 | Delete uploaded PDFs after processing + startup orphan purge | ✅ Done | `file_cleanup.py`, workers, `main.py` lifespan |
| P1-4 | Postgres instead of SQLite in production | ⏳ Pending | Concurrent writes, encryption options |
| P1-5 | Groq client timeouts, retries, structured failure | ✅ Done | `summarizer_client.py`, `prod_pipeline.py` |
| P1-6 | Structured audit log (actor, patient_id, job_id, action) | ⏳ Pending | HIPAA / SOC2 |
| P1-7 | Field-level encryption or KMS for PHI columns | ⏳ Pending | Data at rest |
| P1-8 | Rate limiting on `/upload` (per IP / API key) | ⏳ Pending | Abuse prevention |
| P1-9 | OAuth2 / JWT with patient-scoped RBAC (replace shared API key) | ⏳ Pending | Real authorization |
| P1-10 | Fix Dockerfile + add `docker build` to CI | ✅ Done | `infra/docker/Dockerfile`, `.github/workflows/ci.yml` |
| P1-11 | `/health/ready` probing DB, Redis, Groq config | ⏳ Pending | Load balancer safety |
| P1-12 | Unify dev/prod summarization (structured JSON input only) | ⏳ Pending | Env parity |
| P1-13 | Restore pipeline resource init in FastAPI lifespan | ⏳ Pending | Cold-start races |
| P1-14 | Enforce `max_retries`; dead-letter queue for failed jobs | ⏳ Pending | Operational recovery |
| P1-15 | Remove hardcoded credentials from `start_script.sh` | ⏳ Pending | Secret hygiene |

---

## P2 — Quality, scale & compliance maturity

| ID | Item | Rationale |
|----|------|-----------|
| P2-1 | Golden-set extraction metrics in CI (precision/recall thresholds) | ML regression gates |
| P2-2 | Groq API contract tests (mock HTTP) | External dependency safety |
| P2-3 | E2E test: upload → SSE → results (Playwright + docker-compose) | User journey |
| P2-4 | Angular unit + component tests | Frontend coverage |
| P2-5 | Standardize imports (`ml_core.pipeline.*` only) | Repo hygiene |
| P2-6 | Remove committed `*.egg-info/` artifacts | Packaging cleanliness |
| P2-7 | Replace in-browser mock chat with backend or disable in prod | Clinical liability |
| P2-8 | Elasticsearch integration (replace mock search service) | Feature completeness |
| P2-9 | HIPAA controls doc + subprocessor/BAA tracking | Compliance accuracy |
| P2-10 | Lazy imports to fix pytest collection hang | Developer velocity |
| P2-11 | `uv.lock` / single lockfile in CI | Dependency reproducibility |
| P2-12 | docker-compose for local Redis + API + worker + frontend | Onboarding |

---

## Implementation order (recommended)

1. **Week 1:** P0 verification (CI green, manual prod smoke test) — **complete**
2. **Week 2–3:** P1-1 → P1-4 (S3 wiring, queue durability, Postgres)
3. **Week 4:** P1-6 → P1-9, P1-11 (audit, auth upgrade, health probes)
4. **Ongoing:** P2 items tied to release milestones
