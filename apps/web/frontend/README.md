# MedNLP – Medical Intelligence Platform
### Angular 18 · Tailwind CSS v3 · Standalone Components · Signals

---

## Project Structure

```
src/app/
├── core/
│   ├── models/
│   │   └── mednlp.models.ts          ← All TypeScript interfaces
│   └── services/
│       ├── mednlp-api.service.ts     ← Upload + polling (HttpClient)
│       ├── elasticsearch.service.ts  ← ES search (mock → real)
│       └── chat.service.ts           ← Chat state + response generation
│
├── shared/
│   ├── components/
│   │   └── navbar.component.ts/html  ← Sticky nav with router links
│   └── pipes/
│       └── highlight.pipe.ts         ← Highlights search term in results
│
├── features/
│   ├── analyze/components/
│   │   ├── analyze-page.component    ← Page orchestrator
│   │   ├── upload-panel.component    ← File picker + drag-drop
│   │   ├── job-status.component      ← Polling progress steps
│   │   ├── results-summary.component ← Clinical summary card
│   │   ├── results-diseases.component← Disease tags with ICD-10
│   │   └── results-labs.component    ← Lab table with flags
│   │
│   ├── search/components/
│   │   ├── search-page.component     ← Page orchestrator
│   │   ├── search-bar.component      ← Query + filters + quick chips
│   │   └── search-results.component  ← ES result cards with highlight
│   │
│   └── chat/components/
│       └── chat-modal.component      ← Slide-up AI chat panel
│
├── app.component.ts   ← Root shell (navbar + outlet + chat modal)
├── app.routes.ts      ← Lazy-loaded routes
└── app.config.ts      ← provideRouter + provideHttpClient
```

---

## Quick Start

```bash
cd /apps/web/frontend
npm install
npm start              # http://localhost:4200
```

---

## Wiring to Your Real Backend

### 1 — Upload & Get Job ID

In `analyze-page.component.ts`, replace the simulated block:

```typescript
// REAL — replace the simulated block in startUpload()
this.api.uploadDocument(file, this.patientId(), this.docType()).subscribe({
  next: res => { this.jobId.set(res.job_id); this._startPolling(res.job_id); },
  error: err => { this.uploading.set(false); console.error(err); }
});
```

Your backend must return:
```json
{ "job_id": "JOB-XXXXXXXX" }
```

### 2 — Poll for Status / Results

`_startPolling()` is already wired to `mednlp-api.service.ts → pollJob()`.  
Your backend must return one of:

**While processing:**
```json
{ "status": "Extracting entities" }
```

**When done:**
```json
{
  "diseases_json": [{ "name": "...", "icd10": "...", "confidence": 0.97 }],
  "labs_json":     [{ "test": "...", "value": "...", "unit": "...",
                      "reference": "...", "status": "abnormal" }],
  "summary_text":  "The patient has..."
}
```

The type guard `isAnalysisResult()` in `mednlp.models.ts` distinguishes between the two automatically.

### 3 — Elasticsearch Search

In `elasticsearch.service.ts`, uncomment the real HTTP call and remove the mock:

```typescript
search(params: EsSearchParams): Observable<EsPatientRecord[]> {
  const p = new HttpParams()
    .set('q',        params.query)
    .set('doc_type', params.docType)
    .set('range',    params.dateRange);
  return this.http.get<EsPatientRecord[]>(`${this.base}/search`, { params: p });
}
```

### 4 — API Base URL

Change `private base = '/api'` in each service to your real backend URL,  
or configure a proxy in `proxy.conf.json`:

```json
{
  "/api": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true
  }
}
```

Add to `angular.json` serve options: `"proxyConfig": "proxy.conf.json"`

---

## Tech Stack

| Layer        | Choice                                 |
|--------------|----------------------------------------|
| Framework    | Angular 18 (standalone components)     |
| State        | Angular Signals (`signal()`)           |
| Styling      | Tailwind CSS v3 (inline class + style) |
| HTTP         | Angular `HttpClient`                   |
| Routing      | Angular Router (lazy-loaded)           |
| Fonts        | Syne · DM Sans · DM Mono (Google)     |
| Animations   | CSS keyframes via Tailwind config      |
