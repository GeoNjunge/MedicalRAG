import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { DemoModeService } from '../../../core/services/demo-mode.service';
import { LOOM_DEMO_URL, DemoSampleId } from '../../../core/constants/demo-samples';
import { LandingDemoBannerComponent } from './landing-demo-banner.component';
import { LandingHeroComponent } from './landing-hero.component';
import { LandingMetricsComponent } from './landing-metrics.component';
import { LandingArchitectureComparisonComponent } from './landing-architecture-comparison.component';
import { LandingPipelineComponent } from './landing-pipeline.component';
import { LandingStackBarComponent } from './landing-stack-bar.component';
import { LandingSamplePanelComponent } from './landing-sample-panel.component';
import { LandingLoomModalComponent } from './landing-loom-modal.component';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [
    LandingDemoBannerComponent,
    LandingHeroComponent,
    LandingMetricsComponent,
    LandingArchitectureComparisonComponent,
    LandingPipelineComponent,
    LandingStackBarComponent,
    LandingSamplePanelComponent,
    LandingLoomModalComponent,
  ],
  template: `
    <app-landing-demo-banner />

    <app-landing-hero
      (tryDemo)="goToAnalyzer()"
      (exploreArchitecture)="scrollToArchitecture()"
      (openVideo)="videoOpen.set(true)" />

    <app-landing-metrics />

    <app-landing-architecture-comparison />

    <app-landing-pipeline />

    <app-landing-stack-bar />

    <app-landing-sample-panel
      [samples]="demo.samples"
      [activeId]="demo.activeSampleId()"
      [activeResult]="demo.activeResult()"
      (selectSample)="loadSample($event)"
      (openInAnalyzer)="goToAnalyzer()" />

    <app-landing-loom-modal
      [open]="videoOpen()"
      [embedUrl]="loomEmbedUrl()"
      (close)="videoOpen.set(false)" />
  `,
})
export class LandingPageComponent implements OnInit {
  private router = inject(Router);
  private sanitizer = inject(DomSanitizer);
  readonly demo = inject(DemoModeService);

  videoOpen = signal(false);
  loomEmbedUrl = computed(() =>
    this.sanitizer.bypassSecurityTrustResourceUrl(LOOM_DEMO_URL)
  );

  ngOnInit(): void {
    if (!this.demo.activeResult()) {
      this.demo.loadSample('lab-report');
    }
  }

  loadSample(id: DemoSampleId): void {
    this.demo.loadSample(id);
  }

  goToAnalyzer(): void {
    this.router.navigate(['/analyze']);
  }

  scrollToArchitecture(): void {
    document.getElementById('architecture-comparison')?.scrollIntoView({ behavior: 'smooth' });
  }
}
