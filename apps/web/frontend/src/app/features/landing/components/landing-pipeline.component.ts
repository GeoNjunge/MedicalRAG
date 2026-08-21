import { Component } from '@angular/core';
import { PIPELINE_STEPS, PipelineStep } from '../data/landing.constants';

@Component({
  selector: 'app-landing-pipeline',
  standalone: true,
  template: `
    <section id="architecture" class="px-6 pb-14">
      <div class="max-w-6xl mx-auto">
        <div class="mb-8 text-center">
          <h2 class="font-[Syne] text-[28px] font-bold m-0 mb-2">End-to-End Pipeline</h2>
          <p style="color:#8b909e;" class="text-[14px] m-0">
            From PDF upload to validated clinical JSON — built for constrained CPU environments.
          </p>
        </div>

        <div class="grid gap-3 md:grid-cols-5">
          @for (step of steps; track step.step; let last = $last) {
            <div class="relative flex flex-col items-center text-center">
              <div
                style="background:#1c1f26; border:1px solid #2a2e38;"
                class="w-full rounded-2xl p-4 min-h-[160px] flex flex-col items-center justify-start gap-3">
                <div
                  style="background:rgba(232,112,58,0.1); border:1px solid rgba(232,112,58,0.25);"
                  class="w-10 h-10 rounded-xl flex items-center justify-center">
                  <span [innerHTML]="iconSvg(step.icon)"></span>
                </div>
                <span style="color:#555b6b;" class="font-mono text-[10px]">STEP {{ step.step }}</span>
                <h3 class="font-[Syne] text-[14px] font-bold m-0">{{ step.title }}</h3>
                <p style="color:#8b909e;" class="text-[12px] m-0 leading-[1.5]">{{ step.subtitle }}</p>
              </div>
              @if (!last) {
                <div
                  class="hidden md:block absolute top-1/2 -right-2 w-4 h-px"
                  style="background:#3a3f4d;">
                </div>
              }
            </div>
          }
        </div>
      </div>
    </section>
  `,
})
export class LandingPipelineComponent {
  readonly steps = PIPELINE_STEPS;

  iconSvg(icon: PipelineStep['icon']): string {
    const stroke = '#e8703a';
    const common = `fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`;
    const icons: Record<PipelineStep['icon'], string> = {
      upload: `<svg width="18" height="18" viewBox="0 0 24 24" ${common}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`,
      parse: `<svg width="18" height="18" viewBox="0 0 24 24" ${common}><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>`,
      infer: `<svg width="18" height="18" viewBox="0 0 24 24" ${common}><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>`,
      optimize: `<svg width="18" height="18" viewBox="0 0 24 24" ${common}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
      output: `<svg width="18" height="18" viewBox="0 0 24 24" ${common}><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
    };
    return icons[icon];
  }
}
