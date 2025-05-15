import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { UsersManagementComponent } from './users-management.component';

const routes: Routes = [
  {
    path: '',
    component: UsersManagementComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class UsersManagementModule { }
