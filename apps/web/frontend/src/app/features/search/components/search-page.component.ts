import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ElasticsearchService } from '../../../core/services/elasticsearch.service';
import { EsPatientRecord, EsSearchParams } from '../../../core/models/mednlp.models';
import { SearchBarComponent }    from './search-bar.component';
import { SearchResultsComponent } from './search-results.component';

@Component({
  selector: 'app-search-page',
  standalone: true,
  imports: [FormsModule, SearchBarComponent, SearchResultsComponent],
  templateUrl: './search-page.component.html',
})
export class SearchPageComponent {
  private es = inject(ElasticsearchService);

  state    = signal<'idle' | 'searching' | 'done'>('idle');
  results  = signal<EsPatientRecord[]>([]);
  lastQuery = signal('');

  onSearch(params: EsSearchParams) {
    if (!params.query.trim()) return;
    this.lastQuery.set(params.query);
    this.state.set('searching');
    this.results.set([]);

    this.es.search(params).subscribe({
      next: res => { this.results.set(res); this.state.set('done'); },
      error: ()  => this.state.set('idle'),
    });
  }
}
