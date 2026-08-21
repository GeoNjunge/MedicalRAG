import { Injectable, signal } from '@angular/core';
import { AnalysisResult } from '../models/mednlp.models';
import { DEMO_SAMPLES, DemoSample, DemoSampleId } from '../constants/demo-samples';

@Injectable({ providedIn: 'root' })
export class DemoModeService {
  readonly activeSampleId = signal<DemoSampleId | null>(null);
  readonly activeResult = signal<AnalysisResult | null>(null);
  readonly isDemoMode = signal(false);

  get samples(): DemoSample[] {
    return DEMO_SAMPLES;
  }

  loadSample(id: DemoSampleId): AnalysisResult {
    const sample = DEMO_SAMPLES.find(s => s.id === id);
    if (!sample) {
      throw new Error(`Unknown demo sample: ${id}`);
    }
    this.activeSampleId.set(id);
    this.activeResult.set(sample.result);
    this.isDemoMode.set(true);
    return sample.result;
  }

  clear(): void {
    this.activeSampleId.set(null);
    this.activeResult.set(null);
    this.isDemoMode.set(false);
  }
}
