// ─── Job & Polling ───────────────────────────────────────────────
export interface JobResponse {
  job_id: string;
}

export interface PollStatusResponse {
  status: string;         // e.g. "Extracting entities"
}

export interface AnalysisResult {
  diseases_json: Disease[];
  labs_json:     LabResult[];
  summary_text:  string;
}

export type PollResponse = PollStatusResponse | AnalysisResult;

export function isAnalysisResult(r: PollResponse): r is AnalysisResult {
  return (r as AnalysisResult).summary_text != null;
}

export interface JobProgressEvent {
  type: 'progress';
  job_id: string;
  stage: string;
  status: string;
  timestamp: string;
}

export interface JobCompletedEvent {
  type: 'completed';
  job_id: string;
  stage: string;
  status: string;
  timestamp: string;
  result: AnalysisResult;
}

export interface JobFailedEvent {
  type: 'failed';
  job_id: string;
  stage: string;
  status: string;
  timestamp: string;
}

export type JobEvent = JobProgressEvent | JobCompletedEvent | JobFailedEvent;

// ─── Domain ──────────────────────────────────────────────────────
export interface Disease {
  name:       string;
  icd10?:      string;
  confidence?: number;
}

export interface LabResult {
  test:      string;
  value:     string;
  unit:      string;
  reference?: string;
  status:    'normal' | 'abnormal';
}

// ─── Job Status Steps ─────────────────────────────────────────────
export type StepStatus = 'idle' | 'active' | 'done';

export interface JobStep {
  id:     string;
  label:  string;
  detail: string;
  status: StepStatus;
}

// ─── Elasticsearch ────────────────────────────────────────────────
export interface EsPatientRecord {
  patientId:  string;
  name:       string;
  dob:        string;
  date:       string;
  type:       'Discharge Summary' | 'Clinical Notes' | 'Lab Report';
  conditions: string[];
  summary:    string;
  score:      number;
}

export interface EsSearchParams {
  query:     string;
  docType:   string;
  dateRange: string;
}

// ─── Chat ────────────────────────────────────────────────────────
export interface ChatMessage {
  id:      number;
  role:    'user' | 'ai';
  content: string;
  typing?: boolean;
}
