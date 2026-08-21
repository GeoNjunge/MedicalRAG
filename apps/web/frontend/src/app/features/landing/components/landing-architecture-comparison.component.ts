import { Component } from '@angular/core';
import {
  ARCHITECTURE_COMPARISON,
  ArchitectureCard,
  DUAL_APPROACH_CALLOUT,
} from '../data/landing.constants';

@Component({
  selector: 'app-landing-architecture-comparison',
  standalone: true,
  template: `
    <section id="architecture-comparison" class="px-6 pb-14">
      <div class="max-w-6xl mx-auto">
        <div class="mb-8 text-center">
          <h2 class="font-[Syne] text-[28px] font-bold m-0 mb-2">
            Architecture Comparison
          </h2>
          <p style="color:#8b909e;" class="text-[14px] m-0 max-w-2xl mx-auto leading-[1.7]">
            Two deployment paths — same clinical output schema, different engineering trade-offs.
          </p>
        </div>

        <div class="grid gap-5 lg:grid-cols-2">
          @for (card of cards; track card.id) {
            <article
              [style.border]="borderStyle(card.accent)"
              style="background:#16181d;"
              class="rounded-2xl p-6 flex flex-col gap-5 animate-[slideUp_0.4s_ease_forwards]">

              <!-- Card header -->
              <div>
                <span
                  [style.background]="tagBg(card.accent)"
                  [style.border]="tagBorder(card.accent)"
                  [style.color]="accentColor(card.accent)"
                  class="inline-block font-mono text-[10px] uppercase tracking-[0.14em]
                         px-2.5 py-1 rounded-full mb-3">
                  {{ card.highlightTag }}
                </span>
                <h3 class="font-[Syne] text-[17px] font-bold m-0 leading-[1.35]">
                  {{ card.title }}
                </h3>
              </div>

              <!-- Pipeline steps -->
              <ol class="m-0 p-0 list-none flex flex-col gap-2.5">
                @for (step of card.steps; track step.order) {
                  <li
                    style="background:#0e0f11; border:1px solid #2a2e38;"
                    class="rounded-xl px-4 py-3 flex items-start gap-3">
                    <span
                      [style.background]="tagBg(card.accent)"
                      [style.color]="accentColor(card.accent)"
                      [style.border]="tagBorder(card.accent)"
                      class="flex-shrink-0 w-6 h-6 rounded-lg flex items-center justify-center
                             font-mono text-[11px] font-bold border">
                      {{ step.order }}
                    </span>
                    <div class="min-w-0">
                      <p style="color:#e8eaf0;" class="text-[13px] font-semibold m-0 mb-0.5">
                        {{ step.label }}
                      </p>
                      <p style="color:#555b6b;" class="font-mono text-[11px] m-0 leading-[1.5]">
                        {{ step.detail }}
                      </p>
                    </div>
                  </li>
                }
              </ol>

              <!-- Engineering focus -->
              <div
                [style.borderLeft]="'3px solid ' + accentColor(card.accent)"
                style="background:#0e0f11;"
                class="rounded-r-xl px-4 py-3 mt-auto">
                <p style="color:#555b6b;" class="font-mono text-[10px] uppercase tracking-[0.12em] m-0 mb-1.5">
                  Engineering Focus
                </p>
                <p style="color:#8b909e;" class="text-[13px] m-0 leading-[1.65]">
                  {{ card.engineeringFocus }}
                </p>
              </div>
            </article>
          }
        </div>

        <!-- Dual approach callout -->
        <div
          style="background:rgba(79,158,248,0.06); border:1px solid rgba(79,158,248,0.22);"
          class="mt-6 rounded-2xl px-5 py-4 flex items-start gap-3">
          <span
            style="background:rgba(79,158,248,0.12); color:#4f9ef8; border:1px solid rgba(79,158,248,0.25);"
            class="flex-shrink-0 font-mono text-[10px] uppercase tracking-[0.1em]
                   px-2 py-1 rounded-md whitespace-nowrap mt-0.5">
            Dual Approach
          </span>
          <p style="color:#8b909e;" class="text-[13px] m-0 leading-[1.7]">
            {{ callout }}
          </p>
        </div>
      </div>
    </section>
  `,
})
export class LandingArchitectureComparisonComponent {
  readonly cards = ARCHITECTURE_COMPARISON;
  readonly callout = DUAL_APPROACH_CALLOUT;

  accentColor(accent: ArchitectureCard['accent']): string {
    return accent === 'orange' ? '#e8703a' : '#4f9ef8';
  }

  tagBg(accent: ArchitectureCard['accent']): string {
    return accent === 'orange' ? 'rgba(232,112,58,0.1)' : 'rgba(79,158,248,0.1)';
  }

  tagBorder(accent: ArchitectureCard['accent']): string {
    return accent === 'orange'
      ? '1px solid rgba(232,112,58,0.25)'
      : '1px solid rgba(79,158,248,0.25)';
  }

  borderStyle(accent: ArchitectureCard['accent']): string {
    return accent === 'orange'
      ? '1px solid rgba(232,112,58,0.2)'
      : '1px solid rgba(79,158,248,0.2)';
  }
}
