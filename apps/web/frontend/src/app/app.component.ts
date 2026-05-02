import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent }    from './shared/components/navbar.component';
import { ChatModalComponent } from './features/chat/components/chat-modal.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, ChatModalComponent],
  template: `
    <app-navbar></app-navbar>
    <router-outlet></router-outlet>
    <app-chat-modal></app-chat-modal>
  `,
})
export class AppComponent {}
