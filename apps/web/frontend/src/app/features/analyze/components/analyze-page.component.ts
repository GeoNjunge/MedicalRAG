import { Component, inject, signal, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { MednlpApiService } from '../../../core/services/mednlp-api.service';
import { ChatService } from '../../../core/services/chat.service';
import {
  AnalysisResult, Disease, LabResult, JobStep, isAnalysisResult
} from '../../../core/models/mednlp.models';
import { UploadPanelComponent }  from './upload-panel.component';
import { JobStatusComponent }    from './job-status.component';
import { ResultsSummaryComponent } from './results-summary.component';
import { ResultsDiseasesComponent } from './results-diseases.component';
import { ResultsLabsComponent }   from './results-labs.component';

@Component({
  selector: 'app-analyze-page',
  standalone: true,
  imports: [
    FormsModule,
    UploadPanelComponent,
    JobStatusComponent,
    ResultsSummaryComponent,
    ResultsDiseasesComponent,
    ResultsLabsComponent,
  ],
  templateUrl: './analyze-page.component.html',
})
export class AnalyzePageComponent implements OnDestroy {
  private api  = inject(MednlpApiService);
  private chat = inject(ChatService);
  private stop$ = new Subject<void>();

  // ── Upload state ───────────────────────────────────────────
  selectedFile   = signal<File | null>(null);
  patientId      = signal('');
  docType        = signal('clinical');
  uploading      = signal(false);

  // ── Job state ──────────────────────────────────────────────
  jobId          = signal<string | null>(null);
  pollCount      = signal(0);
  pollDone       = signal(false);
  nlpStatusText  = signal('Waiting...');

  steps = signal<JobStep[]>([
    { id: 'upload',     label: 'Uploading & Queuing',  detail: 'Sending to worker pool...', status: 'idle' },
    { id: 'processing', label: 'NLP Processing',        detail: 'Waiting...',                status: 'idle' },
    { id: 'done',       label: 'Results Ready',         detail: '—',                         status: 'idle' },
  ]);

  // ── Results ────────────────────────────────────────────────
  results = signal<AnalysisResult | null>(null);

  // ─── Simulated poll stages (replace with real API call) ───
  private pollStages = [
    'Extracting document text...',
    'Running NLP tokenization...',
    'Extracting named entities...',
    'Identifying lab values...',
    'Mapping to ICD-10 codes...',
    'Generating clinical summary...',
  ];

  onFileSelected(file: File) { this.selectedFile.set(file); }

  startUpload() {
    const file = this.selectedFile();
    if (!file) return;
    this.uploading.set(true);
    this.pollCount.set(0);
    this.pollDone.set(false);
    this.results.set(null);

    this._setStep('upload', 'active');

    // ── REAL API: uncomment below ────────────────────────────
    this.api.uploadDocument(file, this.patientId(), this.docType()).subscribe({
      next: res => { this.jobId.set(res.job_id); this._startPolling(res.job_id); },
      error: err => { this.uploading.set(false); console.error(err); }
    });

    // ── SIMULATED: remove when backend is ready ──────────────
    // const fakeId = 'JOB-' + Math.random().toString(36).substr(2, 8).toUpperCase();
    // this.jobId.set(fakeId);
    // this._simulatePolling();
  }

  // private _simulatePolling() {
  //   let si = 0;
  //   setTimeout(() => this._setStep('processing', 'active'), 2000);

  //   const iv = setInterval(() => {
  //     this.pollCount.update(n => n + 1);
  //     if (si < this.pollStages.length) {
  //       this.nlpStatusText.set(this.pollStages[si++]);
  //       this._updateStepDetail('processing', this.pollStages[si - 1]);
  //     }
  //     if (si >= this.pollStages.length) {
  //       clearInterval(iv);
  //       setTimeout(() => this._onJobComplete(), 800);
  //     }
  //   }, 2000);
  // }

  /** Wire this to real pollJob() observable in production */
  private _startPolling(jobId: string) {
    this.api.pollJob(jobId, this.stop$).subscribe({
      next: res => {
        console.log(res)
        this.pollCount.update(n => n + 1);
        if (isAnalysisResult(res)) {
          this.stop$.next();
          this._onJobComplete(res);
        } else {
          this.nlpStatusText.set(res.status);
          this._updateStepDetail('processing', res.status);
          this._setStep('processing', 'active');
        }
      },
      error: err => console.error(err),
    });
  }

  private _onJobComplete(res?: AnalysisResult) {
    this._setStep('upload', 'done');
    this._setStep('processing', 'done');
    this._setStep('done', 'done');
    this.pollDone.set(true);
    this.uploading.set(false);

    const result = res ?? MOCK_RESULT;
    this.results.set(result);
    this.chat.notifyNewResults(result);
  }

  private _setStep(id: string, status: JobStep['status']) {
    this.steps.update(steps =>
      steps.map(s => s.id === id ? { ...s, status } : s)
    );
  }

  private _updateStepDetail(id: string, detail: string) {
    this.steps.update(steps =>
      steps.map(s => s.id === id ? { ...s, detail } : s)
    );
  }

  openChat() { this.chat.open(); }

  ngOnDestroy() { this.stop$.next(); this.stop$.complete(); }
}

// ─── Mock result (remove when using real API) ───────────────────
const MOCK_RESULT: AnalysisResult = {
  diseases_json: [
    { name:'Type 2 Diabetes Mellitus',      icd10:'E11',    confidence:0.97 },
    { name:'Hypertension',                  icd10:'I10',    confidence:0.95 },
    { name:'Chronic Kidney Disease Stage 3',icd10:'N18.3',  confidence:0.88 },
    { name:'Peripheral Neuropathy',         icd10:'G62.9',  confidence:0.76 },
    { name:'Hyperlipidemia',                icd10:'E78.5',  confidence:0.91 },
    { name:'Diabetic Retinopathy',          icd10:'E11.31', confidence:0.69 },
  ],
  labs_json: [
    { test:'Fasting Glucose',  value:'300', unit:'mg/dL',          reference:'70–100',  status:'abnormal' },
    { test:'HbA1c',            value:'9.8', unit:'%',               reference:'<5.7',    status:'abnormal' },
    { test:'Creatinine',       value:'2.1', unit:'mg/dL',          reference:'0.7–1.2', status:'abnormal' },
    { test:'eGFR',             value:'38',  unit:'mL/min/1.73m²',  reference:'>60',     status:'abnormal' },
    { test:'LDL Cholesterol',  value:'178', unit:'mg/dL',          reference:'<100',    status:'abnormal' },
    { test:'Hemoglobin',       value:'12.4',unit:'g/dL',           reference:'12–17',   status:'normal'   },
    { test:'Sodium',           value:'138', unit:'mEq/L',          reference:'136–145', status:'normal'   },
    { test:'Potassium',        value:'4.2', unit:'mEq/L',          reference:'3.5–5.0', status:'normal'   },
    { test:'ALT',              value:'42',  unit:'U/L',             reference:'7–56',    status:'normal'   },
  ],
  summary_text: 'The patient is a 58-year-old male presenting with poorly controlled Type 2 Diabetes Mellitus (HbA1c 9.8%) complicated by Chronic Kidney Disease Stage 3 (eGFR 38 mL/min/1.73m²) and peripheral neuropathy. Significant hyperglycemia is present with a fasting glucose of 300 mg/dL. Concurrent hypertension and hyperlipidemia (LDL 178 mg/dL) represent additional major cardiovascular risk factors. Evidence of early diabetic retinopathy was noted. Renal function indices suggest progressive nephropathy; urgent nephrology referral and RAAS inhibitor therapy optimization are warranted.',
};

