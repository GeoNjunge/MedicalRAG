import { Component, Input } from '@angular/core';
import { Disease } from '../../../core/models/mednlp.models';

@Component({
  selector: 'app-results-diseases',
  standalone: true,
  template: `
<div style="background:#16181d; border:1px solid #2a2e38;"
     class="rounded-2xl p-6 animate-[slideUp_0.4s_ease_forwards]">

  <div class="flex items-center gap-2 mb-3.5">
    <div style="background:rgba(248,113,113,0.1);"
         class="w-7 h-7 rounded-[7px] flex items-center justify-center">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f87171"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2
                 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      </svg>
    </div>
    <span style="color:#8b909e;"
          class="font-[Syne] text-[13px] font-bold uppercase tracking-[0.5px]">
      Identified Conditions
    </span>
    <span class="font-mono text-[11px] ml-auto" style="color:#555b6b;">
      {{ diseases.length }} identified
    </span>
  </div>

  <div class="flex flex-wrap gap-2">
    @for (d of diseases; track d.icd10) {
      <span
        style="background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.25);
               color:#fca5a5;"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[6px]
               font-mono text-[12px]">
        {{ d.name }}
        <span style="opacity:0.4;">|</span>
        <span style="color:#555b6b; font-size:11px;">{{ d.icd10 }}</span>
        <span class="text-[10px] ml-0.5"
              [style.color]="d.confidence ?? 1 >= 0.9 ? '#3ecf8e' : d.confidence ?? 1 >= 0.75 ? '#fbbf24' : '#555b6b'">
          {{ (d.confidence ?? 1 * 100).toFixed(0) }}%
        </span>
      </span>
    }
  </div>

</div>
  `,
})
export class ResultsDiseasesComponent {
  @Input() diseases: Disease[] = [];
}
