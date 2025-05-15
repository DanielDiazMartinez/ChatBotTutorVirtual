// filepath: /home/dani/Proyectos/ChatBotTutorVirtual/frontend/src/app/app.routes.ts
import { Routes } from '@angular/router';
import { LoginComponent } from './features/login/login.component';
import { StudentViewComponent } from './features/student-view/student-view.component';
import { SubjectSelectionComponent } from './features/subject-selection/subject-selection.component';
import { TeacherViewComponent } from './features/teacher-view/teacher-view.component';
import { authGuard, teacherGuard, studentGuard, adminGuard } from './guards/auth.guard';

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
    canActivate: [authGuard]
  },
  {
    path: 'chat',
    component: StudentViewComponent,
    canActivate: [studentGuard]
  },
  {
    path: 'admin',
    canActivate: [adminGuard],
    loadChildren: () => import('./features/admin-view/admin-view.module').then(m => m.AdminViewModule)
  },
  {
    path: 'teacher',
    component: TeacherViewComponent,
    canActivate: [teacherGuard],
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./features/teacher-view/components/dashboard/dashboard.module').then(m => m.DashboardModule)
      },
      {
        path: 'questions',
        loadChildren: () => import('./features/teacher-view/components/questions/questions.module').then(m => m.QuestionsModule)
      },
      {
        path: 'documents',
        loadChildren: () => import('./features/teacher-view/components/documents/documents.module').then(m => m.DocumentsModule)
      },
      {
        path: 'subjects',
        loadChildren: () => import('./features/teacher-view/components/subjects/subjects.module').then(m => m.SubjectsModule)
      },
      {
        path: 'student-profile',
        loadChildren: () => import('./features/teacher-view/components/student-profile/student-profile.module').then(m => m.StudentProfileModule)
      }
    ]
  }
];
