import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-results-token-metrics',
  standalone: true,
  imports: [DecimalPipe],
  template: `
<div style="background:#16181d; border:1px solid #2a2e38;"
     class="rounded-2xl p-6 animate-[slideUp_0.4s_ease_forwards]">

  <div class="flex items-center gap-2 mb-4">
    <div style="background:rgba(62,207,142,0.1);"
         class="w-7 h-7 rounded-[7px] flex items-center justify-center">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 20V10"/>
        <path d="M18 20V4"/>
        <path d="M6 20v-6"/>
      </svg>
    </div>
    <span style="color:#8b909e;"
          class="font-[Syne] text-[13px] font-bold uppercase tracking-[0.5px]">
      Summarizer Token Savings
    </span>
  </div>

  <div class="grid gap-3" style="grid-template-columns: repeat(2, minmax(0, 1fr));">
    <div style="background:#0e0f11; border:1px solid #2a2e38;"
         class="rounded-xl p-4">
      <p style="color:#555b6b;" class="text-[11px] uppercase tracking-[0.4px] m-0 mb-1">
        Whole document (baseline)
      </p>
      <p style="color:#e8eaf0;" class="font-[Syne] text-[24px] font-bold m-0">
        {{ metrics.whole_document_tokens | number }}
      </p>
      <p style="color:#8b909e;" class="text-[12px] m-0 mt-1">
        Tokens if the full PDF text was sent to the summarizer
      </p>
    </div>

    <div style="background:#0e0f11; border:1px solid rgba(62,207,142,0.25);"
         class="rounded-xl p-4">
      <p style="color:#555b6b;" class="text-[11px] uppercase tracking-[0.4px] m-0 mb-1">
        Structured input (actual)
      </p>
      <p style="color:#3ecf8e;" class="font-[Syne] text-[24px] font-bold m-0">
        {{ metrics.summarizer_input_tokens | number }}
      </p>
      <p style="color:#8b909e;" class="text-[12px] m-0 mt-1">
        Tokens sent as diseases + labs JSON
      </p>
    </div>
  </div>

  <div style="background:rgba(62,207,142,0.06); border:1px solid rgba(62,207,142,0.18);"
       class="rounded-xl px-4 py-3 mt-3 flex items-center justify-between gap-3">
    <span style="color:#8b909e;" class="text-[13px]">
      Saved <strong style="color:#3ecf8e;">{{ metrics.tokens_saved | number }}</strong> tokens
    </span>
    <span style="color:#3ecf8e; background:rgba(62,207,142,0.12);"
          class="text-[12px] font-bold px-2.5 py-1 rounded-full">
      {{ metrics.reduction_percent | number:'1.0-1' }}% reduction
    </span>
  </div>

</div>
  `,
})
export class ResultsTokenMetricsComponent {
  @Input({ required: true }) metrics!: {
    whole_document_tokens: number;
    summarizer_input_tokens: number;
    tokens_saved: number;
    reduction_percent: number;
  };
}
