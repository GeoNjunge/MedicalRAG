import { Component, EventEmitter, Input, Output } from '@angular/core';
import { JsonPipe } from '@angular/common';
import { AnalysisResult } from '../../../core/models/mednlp.models';
import { DemoSample, DemoSampleId } from '../../../core/constants/demo-samples';
import { ResultsSummaryComponent } from '../../analyze/components/results-summary.component';
import { ResultsDiseasesComponent } from '../../analyze/components/results-diseases.component';
import { ResultsLabsComponent } from '../../analyze/components/results-labs.component';
import { ResultsTokenMetricsComponent } from '../../analyze/components/results-token-metrics.component';

@Component({
  selector: 'app-landing-sample-panel',
  standalone: true,
  imports: [
    JsonPipe,
    ResultsSummaryComponent,
    ResultsDiseasesComponent,
    ResultsLabsComponent,
    ResultsTokenMetricsComponent,
  ],
  template: `
    <section class="px-6 pb-20">
      <div class="max-w-6xl mx-auto">
        <div class="mb-6">
          <h2 class="font-[Syne] text-[24px] font-bold m-0 mb-2">Interactive Demo Samples</h2>
          <p style="color:#8b909e;" class="text-[14px] m-0">
            Load pre-calculated pipeline outputs instantly — no backend inference required.
          </p>
        </div>

        <div class="flex flex-wrap gap-3 mb-6">
          @for (sample of samples; track sample.id) {
            <button
              (click)="selectSample.emit(sample.id)"
              [style.border]="activeId === sample.id ? '1px solid #e8703a' : '1px solid #2a2e38'"
              [style.background]="activeId === sample.id ? 'rgba(232,112,58,0.08)' : '#16181d'"
              class="px-4 py-3 rounded-xl cursor-pointer text-left transition-all duration-200
                     hover:border-[#e8703a] min-w-[220px]">
              <span style="color:#e8eaf0;" class="font-[Syne] text-[13px] font-bold block mb-1">
                {{ sample.label }}
              </span>
              <span style="color:#555b6b;" class="text-[11px] leading-[1.5]">
                {{ sample.description }}
              </span>
            </button>
          }
        </div>

        @if (activeResult) {
          <div class="grid gap-4 lg:grid-cols-2">
            <div class="flex flex-col gap-4">
              @if (activeResult.token_metrics) {
                <app-results-token-metrics [metrics]="activeResult.token_metrics" />
              }
              <app-results-summary [summaryText]="activeResult.summary_text" />
              <app-results-diseases [diseases]="activeResult.diseases_json" />
              <app-results-labs [labs]="activeResult.labs_json" />
              <button
                (click)="openInAnalyzer.emit()"
                style="background:linear-gradient(135deg,#c45e2a,#e8703a);"
                class="w-full py-3 rounded-xl text-white font-[Syne] text-[13px] font-bold
                       cursor-pointer border-none">
                Open Sample in Live Analyzer
              </button>
            </div>

            <div
              style="background:#0e0f11; border:1px solid #2a2e38;"
              class="rounded-2xl p-4 overflow-hidden">
              <div class="flex items-center justify-between mb-3">
                <span style="color:#8b909e;" class="font-mono text-[11px] uppercase tracking-[0.15em]">
                  Validated JSON Output Schema
                </span>
                <span style="color:#3ecf8e;" class="font-mono text-[10px]">200 OK · cached</span>
              </div>
              <pre
                style="color:#8b909e; background:#16181d; border:1px solid #2a2e38;"
                class="text-[11px] leading-[1.6] m-0 p-4 rounded-xl overflow-auto max-h-[640px] font-mono">{{ activeResult | json }}</pre>
            </div>
          </div>
        } @else {
          <div
            style="background:#16181d; border:1px dashed #2a2e38; color:#555b6b;"
            class="rounded-2xl px-8 py-16 text-center text-[14px]">
            Select a sample clinical document above to preview structured output.
          </div>
        }
      </div>
    </section>
  `,
})
export class LandingSamplePanelComponent {
  @Input({ required: true }) samples: DemoSample[] = [];
  @Input() activeId: DemoSampleId | null = null;
  @Input() activeResult: AnalysisResult | null = null;
  @Output() selectSample = new EventEmitter<DemoSampleId>();
  @Output() openInAnalyzer = new EventEmitter<void>();
}
