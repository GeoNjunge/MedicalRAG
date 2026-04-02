import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, debounceTime, distinctUntilChanged, of, Subject } from 'rxjs';

interface SearchHit {
  _id: string;
  _score: number;
  _source: {
    patient_id: string;
    patient_name?: string;
    document_type?: string;
    summary_text?: string;
    diseases?: string[];
    lab_values?: any[];
    upload_date?: string;
    facility?: string;
  };
  highlight?: {
    summary_text?: string[];
    [key: string]: string[] | undefined;
  };
}


interface SearchResponse {
  hits: {
    total: { value: number };
    hits: SearchHit[];
  };
  took: number;
  aggregations?: any;
}

@Component({
  selector: 'app-search.component',
  imports: [CommonModule, FormsModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css',
})
export class SearchComponent {
    patientId = '';
  filterDocType = '';
  sortBy = 'relevance';
  pageSize = 10;


  loading = signal(false);
  results = signal<SearchHit[]>([]);
  searchMeta = signal<{ total: number; took: number } | null>(null);
  lastQuery = signal('');
  hasSearched = signal(false);
  currentPage = signal(0);
  totalHits = signal(0);
  selectedRecord = signal<SearchHit | null>(null);


  totalPages = computed(() => Math.ceil(this.totalHits() / this.pageSize));


  private readonly ES_URL = 'http://localhost:9200'; // direct ES or proxy
  private readonly API_BASE = 'http://localhost:8000';
  private searchSubject = new Subject<string>();


  constructor(private http: HttpClient) {
    this.searchSubject.pipe(
      debounceTime(400),
      distinctUntilChanged()
    ).subscribe(() => this.executeSearch());
  }


  onSearchChange(value: string) {
    if (value.length > 2) this.searchSubject.next(value);
  }


  triggerSearch() { this.executeSearch(); }


  quickSearch(id: string) {
    this.patientId = id;
    this.triggerSearch();
  }


  clearSearch() {
    this.patientId = '';
    this.results.set([]);
    this.searchMeta.set(null);
    this.hasSearched.set(false);
    this.currentPage.set(0);
  }


  executeSearch(page = 0) {
    if (!this.patientId.trim()) return;
    this.loading.set(true);
    this.lastQuery.set(this.patientId.trim());
    this.currentPage.set(page);


    // Build sort
    let sortClause: any = [{ '_score': { order: 'desc' } }];
    if (this.sortBy === 'date_desc') sortClause = [{ 'upload_date': { order: 'desc' } }];
    if (this.sortBy === 'date_asc') sortClause = [{ 'upload_date': { order: 'asc' } }];


    // Build query
    const mustClauses: any[] = [
      { match: { patient_id: this.patientId.trim() } }
    ];
    if (this.filterDocType) {
      mustClauses.push({ term: { document_type: this.filterDocType } });
    }


    const esQuery = {
      from: page * this.pageSize,
      size: this.pageSize,
      sort: sortClause,
      query: { bool: { must: mustClauses } },
      highlight: {
        fields: {
          summary_text: { number_of_fragments: 1, fragment_size: 180 }
        },
        pre_tags: ['<em>'],
        post_tags: ['</em>']
      }
    };


    // Try via backend proxy first (recommended), fall back to direct ES
    this.http.post<SearchResponse>(
      `${this.API_BASE}/search`, esQuery
    ).pipe(
      catchError(() =>
        // Fallback: direct Elasticsearch query
        this.http.post<any>(
          `${this.ES_URL}/medical_documents/_search`, esQuery
        ).pipe(catchError(() => of(null)))
      )
    ).subscribe({
      next: (res: any) => {
        this.loading.set(false);
        this.hasSearched.set(true);
        if (res) {
          this.results.set(res.hits.hits);
          this.totalHits.set(res.hits.total.value);
          this.searchMeta.set({ total: res.hits.total.value, took: res.took });
        } else {
          this.results.set([]);
          this.totalHits.set(0);
        }
      },
      error: () => {
        this.loading.set(false);
        this.hasSearched.set(true);
        this.results.set([]);
      }
    });
  }


  prevPage() {
    if (this.currentPage() > 0) this.executeSearch(this.currentPage() - 1);
  }


  nextPage() {
    if (this.currentPage() < this.totalPages() - 1) this.executeSearch(this.currentPage() + 1);
  }


  selectRecord(hit: SearchHit) {
    this.selectedRecord.set(this.selectedRecord()?._id === hit._id ? null : hit);
  }


  trackById(_: number, hit: SearchHit) { return hit._id; }


  docTypeClass(type?: string): string {
    if (!type) return 'default';
    if (type.includes('lab')) return 'lab';
    if (type.includes('discharge')) return 'discharge';
    if (type.includes('clinical') || type.includes('note')) return 'clinical';
    if (type.includes('radiology')) return 'radiology';
    return 'default';
  }


  formatDocType(type?: string): string {
    if (!type) return 'Document';
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }
}
