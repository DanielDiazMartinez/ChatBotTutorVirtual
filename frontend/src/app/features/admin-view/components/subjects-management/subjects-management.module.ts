import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SubjectsManagementComponent } from './subjects-management.component';

const routes: Routes = [
  {
    path: '',
    component: SubjectsManagementComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class SubjectsManagementModule { }
