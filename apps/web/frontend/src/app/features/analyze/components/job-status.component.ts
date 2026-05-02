import { Component, Input } from '@angular/core';
import { JobStep } from '../../../core/models/mednlp.models';

@Component({
  selector: 'app-job-status',
  standalone: true,
  templateUrl: './job-status.component.html',
})
export class JobStatusComponent {
  @Input() jobId!:     string;
  @Input() steps!:     JobStep[];
  @Input() pollCount!: number;
  @Input() done!:      boolean;

  stepBorder(s: JobStep): string {
    if (s.status === 'done')   return '1px solid rgba(62,207,142,0.35)';
    if (s.status === 'active') return '1px solid rgba(232,112,58,0.35)';
    return '1px solid #2a2e38';
  }
  stepBg(s: JobStep): string {
    if (s.status === 'done')   return 'rgba(62,207,142,0.05)';
    if (s.status === 'active') return 'rgba(232,112,58,0.05)';
    return '#0e0f11';
  }
  stepOpacity(s: JobStep): string {
    return s.status === 'idle' ? '0.4' : '1';
  }
  iconBg(s: JobStep): string {
    if (s.status === 'done')   return 'rgba(62,207,142,0.12)';
    if (s.status === 'active') return 'rgba(232,112,58,0.12)';
    return '#22262f';
  }
  iconStroke(s: JobStep): string {
    if (s.status === 'done')   return '#3ecf8e';
    if (s.status === 'active') return '#e8703a';
    return '#555b6b';
  }
}
