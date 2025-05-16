import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdminViewComponent } from './admin-view.component';

const routes: Routes = [
  {
    path: '',
    component: AdminViewComponent,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'users',
        loadChildren: () => import('./components/users-management/users-management.module').then(m => m.UsersManagementModule)
      },
      {
        path: 'subjects',
        loadChildren: () => import('./components/subjects-management/subjects-management.module').then(m => m.SubjectsManagementModule)
      },
      {
        path: 'subjects/:id',
        loadChildren: () => import('./components/subjects-management/subject-edit/subject-edit.module').then(m => m.SubjectEditModule)
      },
      {
        path: 'documents',
        loadChildren: () => import('./components/documents-management/documents-management.module').then(m => m.DocumentsManagementModule)
      },
      {
        path: 'associations',
        loadChildren: () => import('./components/associations-management/associations-management.module').then(m => m.AssociationsManagementModule)
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./components/admin-dashboard/admin-dashboard.module').then(m => m.AdminDashboardModule)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminViewRoutingModule { }
