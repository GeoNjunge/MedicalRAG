import { Component, EventEmitter, Output } from '@angular/core';
import { LANDING_BADGES } from '../data/landing.constants';

@Component({
  selector: 'app-landing-hero',
  standalone: true,
  template: `
    <section class="relative px-6 pt-16 pb-10 overflow-hidden">
      <div
        class="absolute inset-0 pointer-events-none"
        style="background:radial-gradient(ellipse 80% 60% at 50% -10%, rgba(232,112,58,0.15), transparent);">
      </div>

      <div class="relative max-w-5xl mx-auto text-center">
        <p style="color:#555b6b;"
           class="font-mono text-[11px] uppercase tracking-[0.22em] mb-4">
          Medical RAG Document Processing System
        </p>

        <h1 class="font-[Syne] text-[clamp(2rem,5vw,3.5rem)] font-extrabold tracking-tight m-0 mb-5 leading-[1.08]">
          Constrained Clinical
          <span style="background:linear-gradient(135deg,#ff8c52,#ffb347);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                       background-clip:text;">
            Document Engine
          </span>
        </h1>

        <p style="color:#8b909e;"
           class="text-[clamp(15px,2vw,18px)] max-w-2xl mx-auto m-0 mb-8 leading-[1.7]">
          Asynchronous PDF ingestion and clinical text extraction optimized for low-resource hardware.
        </p>

        <div class="flex flex-wrap items-center justify-center gap-3 mb-8">
          <button
            (click)="tryDemo.emit()"
            style="background:linear-gradient(135deg,#c45e2a,#e8703a);"
            class="px-6 py-3 rounded-xl text-white font-[Syne] text-[14px] font-bold
                   cursor-pointer border-none transition-transform duration-200 hover:scale-[1.02]">
            Try Live Demo
          </button>
          <button
            (click)="exploreArchitecture.emit()"
            style="background:#1c1f26; border:1px solid #2a2e38; color:#e8eaf0;"
            class="px-6 py-3 rounded-xl font-[Syne] text-[14px] font-semibold
                   cursor-pointer transition-all duration-200 hover:border-[#e8703a]">
            Explore System Architecture
          </button>
          <button
            (click)="openVideo.emit()"
            style="background:rgba(79,158,248,0.08); border:1px solid rgba(79,158,248,0.25); color:#4f9ef8;"
            class="px-5 py-3 rounded-xl font-[DM_Sans] text-[13px] font-medium
                   cursor-pointer transition-all duration-200 hover:bg-[rgba(79,158,248,0.15)]">
            View 60s Local Video Demo
          </button>
        </div>

        <div class="flex flex-wrap items-center justify-center gap-2.5">
          @for (badge of badges; track badge.label) {
            <span
              style="background:#16181d; border:1px solid #2a2e38; color:#8b909e;"
              class="font-mono text-[11px] px-3 py-1.5 rounded-full">
              {{ badge.label }}
            </span>
          }
        </div>
      </div>
    </section>
  `,
})
export class LandingHeroComponent {
  readonly badges = LANDING_BADGES;
  @Output() tryDemo = new EventEmitter<void>();
  @Output() exploreArchitecture = new EventEmitter<void>();
  @Output() openVideo = new EventEmitter<void>();
}
