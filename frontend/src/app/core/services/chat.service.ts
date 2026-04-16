import { Injectable, signal } from '@angular/core';
import { ChatMessage, AnalysisResult } from '../models/mednlp.models';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private _messages = signal<ChatMessage[]>([
    { id: 0, role: 'ai', content: "Hello! I'm your MedNLP clinical assistant. Once a document is analyzed, I can help you interpret conditions, explain lab values, discuss treatment implications, or clarify medical terminology. What would you like to know?" }
  ]);
  private _open    = signal(false);
  private _hasDot  = signal(false);
  private _nextId  = 1;

  currentResults: AnalysisResult | null = null;

  readonly messages = this._messages.asReadonly();
  readonly isOpen   = this._open.asReadonly();
  readonly hasDot   = this._hasDot.asReadonly();

  open()  { this._open.set(true);  this._hasDot.set(false); }
  close() { this._open.set(false); }

  notifyNewResults(r: AnalysisResult) {
    this.currentResults = r;
    this._hasDot.set(true);
  }

  clear() {
    this._messages.set([
      { id: this._nextId++, role: 'ai', content: 'Chat cleared. How can I help you with the medical results?' }
    ]);
  }

  sendMessage(text: string): void {
    const userMsg: ChatMessage = { id: this._nextId++, role: 'user', content: text };
    const typingMsg: ChatMessage = { id: this._nextId++, role: 'ai', content: '', typing: true };

    this._messages.update(m => [...m, userMsg, typingMsg]);

    const delay = 1000 + Math.random() * 900;
    setTimeout(() => {
      const reply = this._generate(text);
      this._messages.update(msgs =>
        msgs.map(m => m.typing ? { ...m, content: reply, typing: false } : m)
      );
    }, delay);
  }

  private _generate(q: string): string {
    if (!this.currentResults) {
      return 'No analysis available yet. Please upload and process a medical document first, then I can provide detailed clinical interpretation.';
    }
    const ql = q.toLowerCase();
    const r  = this.currentResults;

    if (ql.includes('condition') || ql.includes('disease') || ql.includes('identif')) {
      const list = r.diseases_json.map(d => `<strong>${d.name}</strong> (${d.icd10? d.icd10 : null}, ${Math.round(d.confidence? d.confidence * 100 : 100)}%)`).join(', ');
      return `${r.diseases_json.length} conditions were identified: ${list}. The primary concern is ${r.diseases_json[0].name} with ${Math.round(r.diseases_json[0].confidence?r.diseases_json[0].confidence * 100 : 100)}% confidence.`;
    }
    if (ql.includes('lab') || ql.includes('abnormal') || ql.includes('result')) {
      const abn = r.labs_json.filter(l => l.status === 'abnormal');
      return `<strong>${abn.length} abnormal values</strong> detected: ${abn.map(l => `${l.test} at ${l.value} ${l.unit}`).join(', ')}. Glucose 300 mg/dL and HbA1c 9.8% reflect severely uncontrolled diabetes.`;
    }
    if (ql.includes('treatment') || ql.includes('implication') || ql.includes('manage')) {
      return `Key management priorities: <strong>1.</strong> Urgent glycemic control — HbA1c 9.8% requires intensified insulin or GLP-1 therapy. <strong>2.</strong> Nephroprotection — eGFR 38 warrants nephrology referral and RAAS inhibitor optimization. <strong>3.</strong> Statin therapy for LDL 178 mg/dL to reduce cardiovascular risk.`;
    }
    if (ql.includes('prognosis') || ql.includes('outlook')) {
      return `Prognosis depends on glycemic and renal control. CKD Stage 3 + uncontrolled diabetes carries significant progression risk. Aggressive intervention (HbA1c <7%, BP <130/80, statin) meaningfully improves 5-year renal outcomes.`;
    }
    if (ql.includes('kidney') || ql.includes('renal') || ql.includes('egfr')) {
      return `Creatinine elevated at <strong>2.1 mg/dL</strong>, eGFR <strong>38 mL/min/1.73m²</strong> — CKD Stage 3b, likely diabetic nephropathy. Avoid NSAIDs and contrast agents. ACE inhibitor or ARB therapy is first-line for renoprotection.`;
    }
    if (ql.includes('glucose') || ql.includes('sugar') || ql.includes('hba1c')) {
      return `Fasting glucose critically elevated at <strong>300 mg/dL</strong> (normal: 70–100), HbA1c <strong>9.8%</strong> reflects poor 3-month control. Immediate medication adjustment and dietary intervention required. Continuous glucose monitoring may be appropriate.`;
    }
    return `Based on the extracted findings — primarily <strong>${r.diseases_json[0].name}</strong> and associated complications — is there a specific aspect (labs, conditions, treatment, prognosis) you'd like me to elaborate on?`;
  }
}
