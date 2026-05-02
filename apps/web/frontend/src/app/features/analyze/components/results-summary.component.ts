import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-results-summary',
  standalone: true,
  template: `
<div style="background:#16181d; border:1px solid #2a2e38;"
     class="rounded-2xl p-6 animate-[slideUp_0.4s_ease_forwards]">

  <div class="flex items-center gap-2 mb-3.5">
    <div style="background:rgba(79,158,248,0.1);"
         class="w-7 h-7 rounded-[7px] flex items-center justify-center">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4f9ef8"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    </div>
    <span style="color:#8b909e;"
          class="font-[Syne] text-[13px] font-bold uppercase tracking-[0.5px]">
      Clinical Summary
    </span>
    <button
      (click)="openChat.emit()"
      style="background:rgba(232,112,58,0.08); border:1px solid rgba(232,112,58,0.25); color:#e8703a;"
      class="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-[7px] text-[11px]
             font-[DM_Sans] cursor-pointer transition-all duration-200
             hover:bg-[rgba(232,112,58,0.18)]">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
      Chat about this
    </button>
  </div>

  <p style="color:#e8eaf0; border-left:3px solid #4f9ef8; background:#0e0f11;"
     class="text-[14px] leading-[1.75] m-0 p-4 rounded-[10px]">
    {{ summaryText }}
  </p>

</div>
  `,
})
export class ResultsSummaryComponent {
  @Input()  summaryText = '';
  @Output() openChat = new EventEmitter<void>();
}
