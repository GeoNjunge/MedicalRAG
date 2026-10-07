import { Component } from '@angular/core';

@Component({
  selector: 'app-landing-demo-banner',
  standalone: true,
  template: `
    <div
      style="background:rgba(251,191,36,0.08); border-bottom:1px solid rgba(251,191,36,0.22);"
      class="px-6 py-2.5 text-center">
      <p style="color:#fbbf24;" class="text-[12px] m-0 leading-[1.6] max-w-4xl mx-auto">
        <strong>Prototype notice:</strong> This hosted demo uses cached sample outputs so you can
        explore the UI without running the full local pipeline. Clinical use requires human review.
      </p>
    </div>
  `,
})
export class LandingDemoBannerComponent {}
