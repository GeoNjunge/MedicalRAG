import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, delay } from 'rxjs';
import { EsPatientRecord, EsSearchParams } from '../models/mednlp.models';

const MOCK_RECORDS: EsPatientRecord[] = [
  { patientId:'PAT-00482', name:'James Mwangi',  dob:'1966-03-14', date:'2024-01-14', type:'Discharge Summary', conditions:['Type 2 Diabetes','Hypertension','CKD Stage 3'], summary:'Patient discharged after glycemic management. HbA1c improved from 11.2% to 9.8%. Nephrology follow-up arranged. Renal function monitoring and ACE inhibitor dosage adjustment advised.', score:0.98 },
  { patientId:'PAT-00391', name:'Amina Ochieng', dob:'1978-07-22', date:'2024-01-09', type:'Clinical Notes',    conditions:['Hypertension','Coronary Artery Disease'],          summary:'Follow-up visit for hypertension management. BP 150/90 mmHg despite current therapy. Medication dosage adjusted. Cardiac stress test ordered for next appointment.', score:0.85 },
  { patientId:'PAT-00577', name:'David Kamau',   dob:'1990-11-05', date:'2023-12-28', type:'Lab Report',        conditions:['Hyperlipidemia','Pre-diabetes'],                  summary:'Lipid panel reveals elevated LDL at 220 mg/dL. Fasting glucose 108 mg/dL indicating pre-diabetic state. Lifestyle counseling and repeat labs in 3 months recommended.', score:0.79 },
  { patientId:'PAT-00203', name:'Grace Njeri',   dob:'1954-02-19', date:'2023-12-12', type:'Clinical Notes',    conditions:['Type 1 Diabetes','Hypothyroidism'],               summary:'Patient presents with poorly controlled T1DM. Thyroid function tests abnormal — TSH elevated at 9.2 mIU/L. Endocrinology referral made. Insulin regimen reviewed.', score:0.71 },
  { patientId:'PAT-00629', name:'Samuel Otieno', dob:'1985-09-30', date:'2023-11-28', type:'Discharge Summary', conditions:['Sepsis','Acute Kidney Injury'],                   summary:'ICU admission for Gram-negative sepsis with secondary acute kidney injury. Creatinine peaked at 4.8 mg/dL. Recovered with IV antibiotics and supportive care.', score:0.63 },
];

@Injectable({ providedIn: 'root' })
export class ElasticsearchService {
  private base = '/api/es';

  constructor(private http: HttpClient) {}

  /** In production: hits your ES proxy endpoint. Currently returns mock data. */
  search(params: EsSearchParams): Observable<EsPatientRecord[]> {
    // ── Real call (uncomment when backend is ready) ──────────────
    // const p = new HttpParams()
    //   .set('q',         params.query)
    //   .set('doc_type',  params.docType)
    //   .set('range',     params.dateRange);
    // return this.http.get<EsPatientRecord[]>(`${this.base}/search`, { params: p });

    // ── Mock (remove when wiring real API) ───────────────────────
    return of(MOCK_RECORDS).pipe(delay(1400 + Math.random() * 600));
  }
}
