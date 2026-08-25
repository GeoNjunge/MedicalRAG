import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { JobResponse, JobEvent } from '../models/mednlp.models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class MednlpApiService {
  private base = environment.apiBaseUrl;
  private apiKey = environment.apiKey;
  private readonly maxReconnectAttempts = 5;
  private readonly reconnectBaseDelayMs = 1000;
  private readonly reconnectMaxDelayMs = 10000;

  constructor(private http: HttpClient) {}

  uploadDocument(file: File, patientId: string, docType: string): Observable<JobResponse> {
    const fd = new FormData();
    fd.append('file', file);
    if (patientId) fd.append('patient_id', patientId);
    const headers = this.apiKey
      ? new HttpHeaders({ 'X-API-Key': this.apiKey })
      : undefined;
    return this.http.post<JobResponse>(`${this.base}/upload`, fd, { headers });
  }

  streamJob(jobId: string): Observable<JobEvent> {
    return new Observable<JobEvent>((observer) => {
      let source: EventSource | null = null;
      let reconnectAttempt = 0;
      let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
      let closedByClient = false;
      let terminalEventReceived = false;

      const clearReconnectTimer = () => {
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
      };

      const cleanupSource = () => {
        if (source) {
          source.removeEventListener('progress', onEvent);
          source.removeEventListener('completed', onEvent);
          source.removeEventListener('failed', onEvent);
          source.close();
          source = null;
        }
      };

      const scheduleReconnect = () => {
        if (closedByClient || terminalEventReceived) {
          return;
        }

        if (reconnectAttempt >= this.maxReconnectAttempts) {
          observer.error(new Error('SSE reconnect attempts exhausted'));
          return;
        }

        const delay = Math.min(
          this.reconnectBaseDelayMs * Math.pow(2, reconnectAttempt),
          this.reconnectMaxDelayMs
        );
        reconnectAttempt += 1;
        clearReconnectTimer();
        reconnectTimer = setTimeout(() => {
          connect();
        }, delay);
      };

      const onEvent = (event: MessageEvent) => {
        try {
          const payload = JSON.parse(event.data) as JobEvent;
          reconnectAttempt = 0;
          observer.next(payload);

          if (payload.type === 'completed' || payload.type === 'failed') {
            terminalEventReceived = true;
            clearReconnectTimer();
            cleanupSource();
            observer.complete();
          }
        } catch (error) {
          clearReconnectTimer();
          cleanupSource();
          observer.error(error);
        }
      };

      const connect = () => {
        cleanupSource();
        clearReconnectTimer();

        const sseUrl = this.apiKey
          ? `${this.base}/jobs/${jobId}/events?api_key=${encodeURIComponent(this.apiKey)}`
          : `${this.base}/jobs/${jobId}/events`;

        source = new EventSource(sseUrl);

        source.onopen = () => {
          reconnectAttempt = 0;
        };

        source.addEventListener('progress', onEvent);
        source.addEventListener('completed', onEvent);
        source.addEventListener('failed', onEvent);

        source.onerror = () => {
          cleanupSource();
          scheduleReconnect();
        };
      };

      connect();

      return () => {
        closedByClient = true;
        clearReconnectTimer();
        cleanupSource();
      };
    });
  }
}
