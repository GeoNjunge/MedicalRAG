import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule, FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { form } from '@angular/forms/signals';

@Component({
  selector: 'app-upload-form-component',
  imports: [ReactiveFormsModule],
  templateUrl: './upload-form-component.html',
  styleUrl: './upload-form-component.css',
})
export class UploadFormComponent {
  uploadForm!: FormGroup
  filetoUpload: File | null = null
  constructor(private formBuilder: FormBuilder, private http: HttpClient) {}

  ngOnInit() {
    this.uploadForm = this.formBuilder.group({
      file: ['', Validators.required],
      patient_id: ['', Validators.required],
      model_version: [''],
      priority: [''],
    });
  }

  onFileChange(event: any) {
    if (event.target.files && event.target.files.length > 0) {
      this.filetoUpload = event.target.files[0] as File;
      this.uploadForm.patchValue({
        file: this.filetoUpload.name
      })
      this.uploadForm.get('file')?.updateValueAndValidity();
    } else {
      this.filetoUpload = null;
    }
  }

  onSubmit() {
    if (this.uploadForm.valid && this.filetoUpload) {
      const formData: FormData = new FormData();
      formData.append('patient_id', this.uploadForm.get('patient_id')?.value);
      formData.append('model_version', this.uploadForm.get('model_version')?.value);
      formData.append('priority', this.uploadForm.get('priority')?.value);
      formData.append('file', this.filetoUpload);

      this.http.post('http://127.0.0.1:8000/api/v1/upload', formData).subscribe({
        next: value => {
          console.log('File uploaded successfully', value);
        },
        error: error => {
          console.error('Error uploading file', error);
        },
        complete: () => {console.log('Upload request completed');
          this.uploadForm.reset();
          this.filetoUpload = null;
        }
    });
      
    }
  }
 

}
