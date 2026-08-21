import { AnalysisResult } from '../models/mednlp.models';

export type DemoSampleId = 'lab-report' | 'discharge-summary' | 'ehr-report';

export interface DemoSample {
  id: DemoSampleId;
  label: string;
  description: string;
  result: AnalysisResult;
}

export const DEMO_SAMPLES: DemoSample[] = [
  {
    id: 'lab-report',
    label: 'Sample Lab Report',
    description: 'Metabolic panel with critical potassium flag and lipid profile.',
    result: {
      diseases_json: [],
      labs_json: [
        { test: 'GLUCOSE, FASTING', value: '104', unit: 'mg/dL', status: 'abnormal' },
        { test: 'HEMOGLOBIN A1C', value: '5.8', unit: '%', status: 'abnormal' },
        { test: 'CREATININE', value: '1.25', unit: 'mg/dL', status: 'normal' },
        { test: 'POTASSIUM', value: '5.6', unit: 'mEq/L', status: 'abnormal' },
        { test: 'SODIUM', value: '140', unit: 'mmol/L', status: 'normal' },
        { test: 'WBC COUNT', value: '11.2', unit: 'x10^3/uL', status: 'abnormal' },
        { test: 'TOTAL CHOLESTEROL', value: '215', unit: 'mg/dL', status: 'abnormal' },
        { test: 'LDL', value: '145', unit: 'mg/dL', status: 'abnormal' },
        { test: 'HDL', value: '42', unit: 'mg/dL', status: 'normal' },
      ],
      summary_text:
        'The patient shows mildly elevated fasting glucose (104 mg/dL) and HbA1c (5.8%), suggesting early dysglycemia. Potassium is critically high at 5.6 mEq/L with a hemolysis note — redraw is recommended. WBC is slightly elevated. Lipid panel shows borderline total cholesterol (215 mg/dL) and elevated LDL (145 mg/dL).',
      token_metrics: {
        whole_document_tokens: 1842,
        summarizer_input_tokens: 312,
        tokens_saved: 1530,
        reduction_percent: 83.06,
      },
    },
  },
  {
    id: 'discharge-summary',
    label: 'Sample Discharge Summary',
    description: 'Multi-morbidity discharge with ICD-10 mapped conditions.',
    result: {
      diseases_json: [
        { name: 'Type 2 Diabetes Mellitus', icd10: 'E11', confidence: 0.97 },
        { name: 'Hypertension', icd10: 'I10', confidence: 0.95 },
        { name: 'Chronic Kidney Disease Stage 3', icd10: 'N18.3', confidence: 0.88 },
        { name: 'Peripheral Neuropathy', icd10: 'G62.9', confidence: 0.76 },
        { name: 'Hyperlipidemia', icd10: 'E78.5', confidence: 0.91 },
      ],
      labs_json: [
        { test: 'FASTING GLUCOSE', value: '300', unit: 'mg/dL', status: 'abnormal' },
        { test: 'HBA1C', value: '9.8', unit: '%', status: 'abnormal' },
        { test: 'EGFR', value: '38', unit: 'mL/min/1.73m²', status: 'abnormal' },
        { test: 'LDL CHOLESTEROL', value: '178', unit: 'mg/dL', status: 'abnormal' },
      ],
      summary_text:
        'The patient is a 58-year-old male with poorly controlled Type 2 Diabetes Mellitus (HbA1c 9.8%, fasting glucose 300 mg/dL), Chronic Kidney Disease Stage 3 (eGFR 38), hypertension, hyperlipidemia, and peripheral neuropathy. Urgent glycemic optimization and nephrology follow-up are warranted.',
      token_metrics: {
        whole_document_tokens: 3210,
        summarizer_input_tokens: 428,
        tokens_saved: 2782,
        reduction_percent: 86.67,
      },
    },
  },
  {
    id: 'ehr-report',
    label: 'Sample EHR Report',
    description: 'Emergency visit with chest pain workup and mixed lab flags.',
    result: {
      diseases_json: [
        { name: 'Acute Chest Pain', icd10: 'R07.9', confidence: 0.92 },
        { name: 'Atrial Fibrillation', icd10: 'I48.91', confidence: 0.84 },
        { name: 'Anemia', icd10: 'D64.9', confidence: 0.79 },
      ],
      labs_json: [
        { test: 'TROPONIN I', value: '0.08', unit: 'ng/mL', status: 'abnormal' },
        { test: 'BNP', value: '420', unit: 'pg/mL', status: 'abnormal' },
        { test: 'HEMOGLOBIN', value: '10.1', unit: 'g/dL', status: 'abnormal' },
        { test: 'INR', value: '2.4', unit: '', status: 'abnormal' },
        { test: 'CREATININE', value: '1.6', unit: 'mg/dL', status: 'abnormal' },
      ],
      summary_text:
        'Emergency presentation for acute chest pain with mildly elevated troponin and BNP, raising concern for cardiac ischemia versus demand ischemia in the setting of atrial fibrillation. Anemia (Hb 10.1 g/dL) and supratherapeutic INR (2.4) are noted. Creatinine is elevated at 1.6 mg/dL.',
      token_metrics: {
        whole_document_tokens: 2650,
        summarizer_input_tokens: 356,
        tokens_saved: 2294,
        reduction_percent: 86.57,
      },
    },
  },
];

export const LOOM_DEMO_URL =
  'https://www.loom.com/embed/00000000000000000000000000000000?hide_owner=true&hide_share=true&hide_title=true&hideEmbedTopBar=true';
