import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({ name: 'highlight', standalone: true })
export class HighlightPipe implements PipeTransform {
  constructor(private san: DomSanitizer) {}

  transform(value: string, term: string): SafeHtml {
    if (!term) return this.san.bypassSecurityTrustHtml(value);
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const html = value.replace(
      new RegExp(escaped, 'gi'),
      m => `<mark style="background:rgba(232,112,58,0.25);color:#ff8c52;border-radius:2px;padding:0 2px;">${m}</mark>`
    );
    return this.san.bypassSecurityTrustHtml(html);
  }
}
