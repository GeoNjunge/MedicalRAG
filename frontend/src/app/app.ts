import { Component, signal } from '@angular/core';
import { UploadFormComponent } from "./Components/upload-form-component/upload-form-component";

@Component({
  selector: 'app-root',
  imports: [UploadFormComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
