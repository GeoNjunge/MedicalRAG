import { Component, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EsSearchParams } from '../../../core/models/mednlp.models';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './search-bar.component.html',
})
export class SearchBarComponent {
  @Output() search = new EventEmitter<EsSearchParams>();

  query     = '';
  docType   = '';
  dateRange = 'all';

  quickFilters = ['Diabetes', 'Hypertension', 'Cardiac', 'Renal Failure', 'Sepsis', 'PAT-004xx'];

  emit() {
    if (!this.query.trim()) return;
    this.search.emit({ query: this.query, docType: this.docType, dateRange: this.dateRange });
  }

  quickSearch(term: string) {
    this.query = term;
    this.emit();
  }

  onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') this.emit();
  }
}
