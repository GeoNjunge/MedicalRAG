import { Component, Output, EventEmitter, Input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-upload-panel',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './upload-panel.component.html',
})
export class UploadPanelComponent {
  @Input()  disabled = false;
  @Output() fileSelected    = new EventEmitter<File>();
  @Output() patientIdChange = new EventEmitter<string>();
  @Output() docTypeChange   = new EventEmitter<string>();
  @Output() upload          = new EventEmitter<void>();

  file       = signal<File | null>(null);
  patientId  = '';
  docType    = 'clinical';
  isDragOver = false;

  docTypes = [
    { value: 'clinical',   label: 'Clinical Notes'     },
    { value: 'lab',        label: 'Lab Report'          },
    { value: 'discharge',  label: 'Discharge Summary'   },
    { value: 'other',      label: 'Other'               },
  ];

  onFileInput(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this._setFile(input.files[0]);
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    const f = event.dataTransfer?.files[0];
    if (f) this._setFile(f);
  }

  private _setFile(f: File) {
    this.file.set(f);
    this.fileSelected.emit(f);
  }

  formatBytes(b: number) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
  }

  onPatientId(v: string)  { this.patientIdChange.emit(v); }
  onDocType(v: string)    { this.docType = v; this.docTypeChange.emit(v); }
  triggerUpload()         { if (this.file() && !this.disabled) this.upload.emit(); }
}
