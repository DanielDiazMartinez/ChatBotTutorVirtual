import { Routes } from '@angular/router';
import { LoginComponent } from './features/login/login.component';
import { StudentViewComponent } from './features/student-view/student-view.component';

export const routes: Routes = [
  { path: '', redirectTo: '/chat', pathMatch: 'full' },
  { 
    path: 'login', 
    component: LoginComponent,
    // Esto asegura que el componente se carga de forma independiente
    data: { standalone: true } 
  },
  { path: 'chat', component: StudentViewComponent }
];
