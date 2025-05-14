import { Routes } from '@angular/router';
import { LoginComponent } from './features/login/login.component';
import { StudentViewComponent } from './features/student-view/student-view.component';
import { SubjectSelectionComponent } from './features/subject-selection/subject-selection.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'subject-selection',
    component: SubjectSelectionComponent,
  },
  {
    path: 'chat',
    component: StudentViewComponent,
  }
];
