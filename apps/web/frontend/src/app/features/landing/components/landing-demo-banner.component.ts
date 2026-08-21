import { Component } from '@angular/core';

@Component({
  selector: 'app-landing-demo-banner',
  standalone: true,
  template: `
    <div
      style="background:rgba(251,191,36,0.08); border-bottom:1px solid rgba(251,191,36,0.22);"
      class="px-6 py-2.5 text-center">
      <p style="color:#fbbf24;" class="text-[12px] m-0 leading-[1.6] max-w-4xl mx-auto">
        <strong>Notice:</strong> Demonstrating system UI and pre-calculated inference metrics.
        Backend runs via static cached outputs to minimize free-tier resource limits.
      </p>
    </div>
  `,
})
export class LandingDemoBannerComponent {}
