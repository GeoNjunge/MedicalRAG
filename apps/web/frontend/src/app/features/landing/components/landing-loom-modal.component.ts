import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-landing-loom-modal',
  standalone: true,
  template: `
    @if (open) {
      <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background:rgba(0,0,0,0.75); backdrop-filter:blur(4px);"
        (click)="close.emit()">
        <div
          style="background:#16181d; border:1px solid #2a2e38;"
          class="w-full max-w-3xl rounded-2xl overflow-hidden shadow-2xl"
          (click)="$event.stopPropagation()">
          <div class="flex items-center justify-between px-5 py-4 border-b" style="border-color:#2a2e38;">
            <div>
              <h3 class="font-[Syne] text-[16px] font-bold m-0">60s Local Video Demo</h3>
              <p style="color:#555b6b;" class="text-[12px] m-0 mt-1">
                Model execution logs on 2-core CPU hardware
              </p>
            </div>
            <button
              (click)="close.emit()"
              style="background:#1c1f26; border:1px solid #2a2e38; color:#8b909e;"
              class="w-8 h-8 rounded-lg cursor-pointer text-[18px] leading-none">
              ×
            </button>
          </div>
          <div class="relative w-full" style="padding-bottom:56.25%;">
            <iframe
              [src]="embedUrl"
              class="absolute inset-0 w-full h-full border-0"
              allow="autoplay; fullscreen"
              allowfullscreen>
            </iframe>
          </div>
          <p style="color:#555b6b;" class="text-[11px] m-0 px-5 py-3 font-mono">
            Replace LOOM_DEMO_URL in demo-samples.ts with your Loom embed link.
          </p>
        </div>
      </div>
    }
  `,
})
export class LandingLoomModalComponent {
  @Input({ required: true }) open = false;
  @Input({ required: true }) embedUrl!: SafeResourceUrl;
  @Output() close = new EventEmitter<void>();
}
