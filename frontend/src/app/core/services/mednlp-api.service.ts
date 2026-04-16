import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, switchMap, takeUntil, filter, Subject, timer, catchError, takeWhile } from 'rxjs';
import { JobResponse, PollResponse, AnalysisResult, isAnalysisResult } from '../models/mednlp.models';

@Injectable({ providedIn: 'root' })
export class MednlpApiService {
  private base = 'http://127.0.0.1:8000/api/v1';   // ← swap to your real API base URL

  constructor(private http: HttpClient) {}

  uploadDocument(file: File, patientId: string, docType: string): Observable<JobResponse> {
    const fd = new FormData();
    fd.append('file', file);
    if (patientId) fd.append('patient_id', patientId);
    // fd.append('doc_type', docType);
    return this.http.post<JobResponse>(`${this.base}/upload`, fd);
  }

  /** Polls /status/:jobId every 2 s; completes when backend returns an AnalysisResult */
  pollJob(jobId: string, stop$: Subject<void>): Observable<PollResponse> {
    return timer(0, 2000).pipe(
      switchMap(() => this.http.get<PollResponse>(`${this.base}/status/${jobId}`)),
      takeWhile((res) => !isAnalysisResult(res), true),
      takeUntil(stop$),

      catchError((err) => {
        console.error(err);
        return []
      })
    );
  }
}
