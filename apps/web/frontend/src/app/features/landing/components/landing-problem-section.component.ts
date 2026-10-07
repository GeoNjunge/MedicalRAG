import { Component } from '@angular/core';
import { LANDING_TRUST_POINTS } from '../data/landing.constants';

@Component({
 selector: 'app-landing-problem-section',
 standalone: true,
 template: `
 <section class="px-6 pb-10">
 <div
 style="background:#16181d; border:1px solid #2a2e38;"
 class="max-w-5xl mx-auto rounded-2xl p-8 md:p-10 text-center">
 <p style="color:#555b6b;"
 class="font-mono text-[11px] uppercase tracking-[0.2em] m-0 mb-4">
 The problem
 </p>
 <h2 class="font-[Syne] text-[clamp(1.35rem,3vw,1.75rem)] font-bold m-0 mb-4 leading-[1.25]">
 Reliable Medical Document Analysis for Constrained Environments
 </h2>
 <p style="color:#8b909e;"
 class="text-[15px] m-0 mb-8 max-w-3xl mx-auto leading-[1.75]">
 Most tools send entire PDFs to a model and hope the summary is accurate. In clinical
 workflows that invites missed facts and hallucinations. MedicalRAG extracts structured
 diseases, labs, and findings first - then generates a summary only from those facts - 
 so output stays grounded, explainable, and reviewable.
 </p>

 <div class="grid gap-3 sm:grid-cols-3 text-left">
 @for (point of trustPoints; track point.label) {
 <div
 style="background:#0e0f11; border:1px solid #2a2e38;"
 class="rounded-xl px-4 py-4">
 <p style="color:#e8eaf0;" class="font-[Syne] text-[13px] font-bold m-0 mb-1.5">
 {{ point.label }}
 </p>
 <p style="color:#8b909e;" class="text-[12px] m-0 leading-[1.6]">
 {{ point.detail }}
 </p>
 </div>
 }
 </div>
 </div>
 </section>
 `,
})
export class LandingProblemSectionComponent {
 readonly trustPoints = LANDING_TRUST_POINTS;
}
