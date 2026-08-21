import { Component } from '@angular/core';
import { STACK_TAGS } from '../data/landing.constants';

@Component({
  selector: 'app-landing-stack-bar',
  standalone: true,
  template: `
    <section class="px-6 pb-14">
      <div
        style="background:#16181d; border:1px solid #2a2e38;"
        class="max-w-6xl mx-auto rounded-2xl px-6 py-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex flex-wrap gap-2">
          @for (tag of tags; track tag) {
            <span
              style="background:#0e0f11; border:1px solid #2a2e38; color:#8b909e;"
              class="font-mono text-[11px] px-2.5 py-1 rounded-md">
              {{ tag }}
            </span>
          }
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <span
            class="w-2.5 h-2.5 rounded-full animate-pulse"
            style="background:#3ecf8e; box-shadow:0 0 0 4px rgba(62,207,142,0.18);">
          </span>
          <span style="color:#3ecf8e;" class="font-mono text-[12px]">
            Runtime Ready (Inference Cache Active)
          </span>
        </div>
      </div>
    </section>
  `,
})
export class LandingStackBarComponent {
  readonly tags = STACK_TAGS;
}
