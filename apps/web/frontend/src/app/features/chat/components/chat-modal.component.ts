import { Component, inject, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../../core/services/chat.service';

@Component({
  selector: 'app-chat-modal',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat-modal.component.html',
})
export class ChatModalComponent implements AfterViewChecked {
  chat    = inject(ChatService);
  inputText = '';

  @ViewChild('msgScroll') private msgScroll!: ElementRef<HTMLDivElement>;

  ngAfterViewChecked() {
    if (this.msgScroll) {
      this.msgScroll.nativeElement.scrollTop = this.msgScroll.nativeElement.scrollHeight;
    }
  }

  send() {
    const t = this.inputText.trim();
    if (!t) return;
    this.inputText = '';
    this.chat.sendMessage(t);
  }

  sendSuggestion(text: string) {
    this.chat.sendMessage(text);
  }

  onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') this.send();
  }

  suggestions = [
    'What conditions were identified?',
    'Explain the abnormal lab results',
    'What are the treatment implications?',
    'What is the patient prognosis?',
  ];
}
