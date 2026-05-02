import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '',        redirectTo: 'analyze', pathMatch: 'full' },
  {
    path: 'analyze',
    loadComponent: () =>
      import('./features/analyze/components/analyze-page.component')
        .then(m => m.AnalyzePageComponent),
  },
  {
    path: 'search',
    loadComponent: () =>
      import('./features/search/components/search-page.component')
        .then(m => m.SearchPageComponent),
  },
  { path: '**', redirectTo: 'analyze' },
];
