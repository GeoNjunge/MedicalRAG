import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, ElementRef, OnDestroy, signal, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, interval, of, Subscription, switchMap, takeWhile } from 'rxjs';

interface ProcessingResult {
  diseases_json: any[];
  labs_json: any[];
  summary_text: string;
}


interface PollingStatus {
  status?: string;
  diseases_json?: any[];
  labs_json?: any[];
  summary_text?: string;
}


interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-upload.component',
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.css',
})

export class UploadComponent implements OnDestroy {
  @ViewChild('chatScroll') chatScroll!: ElementRef;


  selectedFile: File | null = null;
  isDragging = false;
  chatInputText = '';


  phase = signal<'idle' | 'uploading' | 'processing' | 'done'>('idle');
  jobId = signal<string>('');
  currentStatus = signal<string>('');
  pollCount = signal<number>(0);
  result = signal<ProcessingResult | null>(null);
  errorMessage = signal<string>('');
  chatOpen = signal(false);
  chatMessages = signal<ChatMessage[]>([]);
  chatLoading = signal(false);


  private pollSub?: Subscription;
  private readonly API_BASE = 'http://localhost:8000'; // adjust to your backend


  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}


  onDragOver(e: DragEvent) {
    e.preventDefault();
    this.isDragging = true;
  }


  onDrop(e: DragEvent) {
    e.preventDefault();
    this.isDragging = false;
    const file = e.dataTransfer?.files[0];
    if (file) this.selectedFile = file;
  }


  onFileSelected(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files?.[0]) this.selectedFile = input.files[0];
  }


  uploadDocument() {
    if (!this.selectedFile) return;
    this.phase.set('uploading');
    this.errorMessage.set('');


    const formData = new FormData();
    formData.append('file', this.selectedFile);


    this.http.post<{ job_id: string }>(`${this.API_BASE}/upload`, formData).subscribe({
      next: (res: { job_id: string; }) => {
        this.jobId.set(res.job_id);
        this.phase.set('processing');
        this.startPolling(res.job_id);
      },
      error: (err: { error: { message: any; }; }) => {
        this.phase.set('idle');
        this.errorMessage.set(err?.error?.message || 'Upload failed. Please try again.');
      }
    });
  }


  startPolling(jobId: string) {
    this.pollCount.set(0);
    this.pollSub = interval(2000).pipe(
      switchMap(() =>
        this.http.get<any>(`${this.API_BASE}/status/${jobId}`).pipe(
          catchError(() => of({ status: 'Checking...' }))
        )
      ),
      takeWhile((res: { diseases_json: any; }) => !res.diseases_json, true)
    ).subscribe({
      next: (res:any) => {
        this.pollCount.update((n: number) => n + 1);
        if (res.diseases_json) {
          this.result.set({
            diseases_json: res.diseases_json ?? [],
            labs_json: res.labs_json ?? [],
            summary_text: res.summary_text ?? ''
          });
          this.phase.set('done');
          this.pollSub?.unsubscribe();
        } else {
          this.currentStatus.set(res.status || '');
        }
      },
      error: () => {
        this.phase.set('idle');
        this.errorMessage.set('Lost connection to processing server.');
        this.pollSub?.unsubscribe();
      }
    });
  }


  reset() {
    this.pollSub?.unsubscribe();
    this.selectedFile = null;
    this.phase.set('idle');
    this.jobId.set('');
    this.currentStatus.set('');
    this.pollCount.set(0);
    this.result.set(null);
    this.errorMessage.set('');
    this.chatMessages.set([]);
  }


  openChat() { this.chatOpen.set(true); }


  closeChat(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('modal-backdrop')) {
      this.chatOpen.set(false);
    }
  }


  sendSuggestion(text: string) {
    this.chatInputText = text;
    this.sendMessage();
  }


  onChatEnter(e: any) {
    if (!e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }


  autoResize(e: Event) {
    const el = e.target as HTMLTextAreaElement;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }


  async sendMessage() {
    const text = this.chatInputText.trim();
    if (!text || this.chatLoading()) return;


    this.chatInputText = '';
    this.chatMessages.update((msgs: any) => [...msgs, { role: 'user', content: text, timestamp: new Date() }]);
    this.chatLoading.set(true);


    setTimeout(() => {
      const scroll = this.chatScroll?.nativeElement;
      if (scroll) scroll.scrollTop = scroll.scrollHeight;
    }, 50);


    const context = this.result()
      ? `Medical document analysis results:\n
Summary: ${this.result()!.summary_text}\n
Conditions: ${JSON.stringify(this.result()!.diseases_json)}\n
Lab Results: ${JSON.stringify(this.result()!.labs_json)}\n\n`
      : '';


    const systemPrompt = `You are MedNLP, a medical AI assistant. You have been provided with structured analysis of a patient's medical document. Help clinicians and patients understand the findings clearly and compassionately. Be concise, accurate, and flag anything critical. Do not diagnose — interpret and explain. ${context}`;


    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1000,
          system: systemPrompt,
          messages: [
            ...this.chatMessages().slice(0, -1).map((m: { role: any; content: any; }) => ({ role: m.role, content: m.content })),
            { role: 'user', content: text }
          ]
        })
      });
      const data = await response.json();
      const reply = data.content?.map((b: any) => b.text || '').join('') || 'No response received.';
      this.chatMessages.update((msgs: any) => [...msgs, { role: 'assistant', content: reply, timestamp: new Date() }]);
    } catch {
      this.chatMessages.update((msgs: any) => [...msgs, { role: 'assistant', content: 'Connection error. Please try again.', timestamp: new Date() }]);
    }


    this.chatLoading.set(false);
    setTimeout(() => {
      const scroll = this.chatScroll?.nativeElement;
      if (scroll) scroll.scrollTop = scroll.scrollHeight;
    }, 50);
  }


  formatMessage(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }


  isString(val: any): boolean { return typeof val === 'string'; }


  ngOnDestroy() { this.pollSub?.unsubscribe(); }
}
