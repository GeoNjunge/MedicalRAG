import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EsPatientRecord } from '../../../core/models/mednlp.models';
import { HighlightPipe } from '../../../shared/pipes/highlight.pipe';

@Component({
  selector: 'app-search-results',
  standalone: true,
  imports: [FormsModule, HighlightPipe],
  templateUrl: './search-results.component.html',
})
export class SearchResultsComponent {
  @Input() state: 'idle' | 'searching' | 'done' = 'idle';
  @Input() results: EsPatientRecord[] = [];
  @Input() query = '';

  sortOrder = 'Relevance';
  sortOptions = ['Relevance', 'Date (newest)', 'Date (oldest)'];

  typeColor(type: string): string {
    const map: Record<string, string> = {
      'Discharge Summary': '#4f9ef8',
      'Clinical Notes':    '#3ecf8e',
      'Lab Report':        '#fbbf24',
    };
    return map[type] ?? '#e8703a';
  }

  scoreColor(score: number): string {
    const pct = score * 100;
    if (pct >= 90) return '#3ecf8e';
    if (pct >= 75) return '#e8703a';
    return '#fbbf24';
  }

  get esQuery(): string {
    return `GET /medical-records/_search?q=${encodeURIComponent(this.query)}&size=10`;
  }
}
