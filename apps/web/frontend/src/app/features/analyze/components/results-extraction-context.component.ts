import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { TokenMetrics } from '../../../core/models/mednlp.models';

@Component({
 selector: 'app-results-extraction-context',
 standalone: true,
 imports: [DecimalPipe],
 template: `
<div style="background:#16181d; border:1px solid #2a2e38;"
 class="rounded-2xl p-5 animate-[slideUp_0.4s_ease_forwards] min-w-0 max-w-full">

 <div class="flex items-start gap-3">
 <div style="background:rgba(79,158,248,0.1);"
 class="w-8 h-8 rounded-[8px] flex items-center justify-center flex-shrink-0 mt-0.5">
 <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4f9ef8"
 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
 <path d="M9 12l2 2 4-4"/>
 </svg>
 </div>
 <div class="min-w-0 flex-1">
 <p style="color:#e8eaf0;" class="font-[Syne] text-[14px] font-bold m-0 mb-1.5">
 Structured extraction before generation reduces hallucinations
 </p>
 <p style="color:#8b909e;" class="text-[13px] m-0 leading-[1.65]">
 The pipeline pulls diseases, lab values, and ICD-10 mappings from the document with
 rules and specialized NLP - then summarizes only that JSON. The clinical summary and
 validated output below reflect extracted facts, not a model reading raw PDF noise.
 </p>
 @if (metrics) {
 <p style="color:#555b6b;" class="font-mono text-[11px] m-0 mt-3 leading-[1.6]">
 Engineering note: summarizer input used
 {{ metrics.summarizer_input_tokens | number }} structured tokens vs
 {{ metrics.whole_document_tokens | number }} if the full document text were sent
 ({{ metrics.reduction_percent | number:'1.0-1' }}% fewer).
 </p>
 }
 </div>
 </div>

</div>
 `,
})
export class ResultsExtractionContextComponent {
 @Input() metrics: TokenMetrics | null = null;
}
