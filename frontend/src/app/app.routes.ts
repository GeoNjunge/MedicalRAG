import { Routes } from '@angular/router';
import { UploadComponent } from './components/upload.component/upload.component';
import { SearchComponent } from './components/search.component/search.component';

export const routes: Routes = [
    { path: '', redirectTo: 'upload', pathMatch: 'full' },
    { path: 'upload', component: UploadComponent },
    { path: 'search', component: SearchComponent },
];
