import { Component } from '@angular/core';
import { LANDING_METRICS, LandingMetric } from '../data/landing.constants';

@Component({
  selector: 'app-landing-metrics',
  standalone: true,
  template: `
    <section class="px-6 pb-12">
      <div class="max-w-6xl mx-auto grid gap-4 md:grid-cols-3">
        @for (metric of metrics; track metric.title) {
          <article
            style="background:#16181d; border:1px solid #2a2e38;"
            class="rounded-2xl p-6 animate-[slideUp_0.4s_ease_forwards]">
            <p style="color:#555b6b;"
               class="font-mono text-[11px] uppercase tracking-[0.18em] m-0 mb-3">
              {{ metric.title }}
            </p>
            <p
              [style.color]="accentColor(metric.accent)"
              class="font-arial text-[36px] font-extrabold m-0 mb-2 leading-none">
              {{ metric.value }}
            </p>
            <p style="color:#8b909e;" class="text-[13px] m-0 leading-[1.6]">
              {{ metric.highlight }}
            </p>
          </article>
        }
      </div>
    </section>
  `,
})
export class LandingMetricsComponent {
  readonly metrics = LANDING_METRICS;

  accentColor(accent: LandingMetric['accent']): string {
    const map = { orange: '#e8703a', green: '#3ecf8e', blue: '#4f9ef8' };
    return map[accent];
  }
}
