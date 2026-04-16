import { Component, Input } from '@angular/core';
import { LabResult } from '../../../core/models/mednlp.models';

@Component({
  selector: 'app-results-labs',
  standalone: true,
  template: `
<div style="background:#16181d; border:1px solid #2a2e38;"
     class="rounded-2xl p-6 animate-[slideUp_0.4s_ease_forwards]">

  <div class="flex items-center gap-2 mb-3.5">
    <div style="background:rgba(62,207,142,0.1);"
         class="w-7 h-7 rounded-[7px] flex items-center justify-center">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v11m0
                 0H5a2 2 0 00-2 2v2a2 2 0 002 2h14a2 2 0 002-2v-2a2 2
                 0 00-2-2H9m0 0v-4"/>
      </svg>
    </div>
    <span style="color:#8b909e;"
          class="font-[Syne] text-[13px] font-bold uppercase tracking-[0.5px]">
      Laboratory Values
    </span>
  </div>

  <!-- Table -->
  <div style="border:1px solid #2a2e38;" class="overflow-hidden rounded-[10px]">

    <!-- Header -->
    <div class="grid px-3.5 py-2" style="grid-template-columns:1fr 110px 130px 80px;
               background:#0e0f11; border-bottom:1px solid #2a2e38;">
      @for (h of ['Test Name','Value','Reference','Flag']; track h) {
        <span style="color:#555b6b;"
              class="text-[10px] font-semibold uppercase tracking-[0.6px]">{{ h }}</span>
      }
    </div>

    <!-- Rows -->
    @for (lab of labs; track lab.test; let last = $last) {
      <div
        class="grid px-3.5 py-2.5 items-center transition-all duration-200"
        [style.gridTemplateColumns]="'1fr 110px 130px 80px'"
        [style.borderBottom]="last ? 'none' : '1px solid #2a2e38'"
        [style.borderLeft]="lab.status === 'abnormal' ? '3px solid #f87171' : '3px solid #3ecf8e'"
        (mouseenter)="$any($event.target).closest('div').style.background='rgba(232,112,58,0.03)'"
        (mouseleave)="$any($event.target).closest('div').style.background='transparent'">

        <span style="color:#e8eaf0;" class="text-[13px] font-medium">{{ lab.test }}</span>

        <span class="font-mono text-[13px]"
              [style.color]="lab.status === 'abnormal' ? '#f87171' : '#e8eaf0'"
              [style.fontWeight]="lab.status === 'abnormal' ? '600' : '400'">
          {{ lab.value }}
          <span style="color:#555b6b; font-size:10px;"> {{ lab.unit }}</span>
        </span>

        <span class="font-mono text-[11px]" style="color:#555b6b;">{{ lab.reference }}</span>

        <span
          class="inline-block px-2 py-0.5 rounded-[5px] text-[11px] font-medium capitalize"
          [style.color]="lab.status === 'abnormal' ? '#f87171' : '#3ecf8e'"
          [style.background]="lab.status === 'abnormal'
            ? 'rgba(248,113,113,0.1)' : 'rgba(62,207,142,0.1)'">
          {{ lab.status }}
        </span>

      </div>
    }
  </div>

</div>
  `,
})
export class ResultsLabsComponent {
  @Input() labs: LabResult[] = [];
}
