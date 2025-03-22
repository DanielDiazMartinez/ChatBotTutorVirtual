import { Routes } from '@angular/router';
import { ChatComponent } from './features/dashboard/chat/chat.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'chat/:id', component: ChatComponent },
  
];