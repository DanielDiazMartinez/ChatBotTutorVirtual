import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SubjectEditComponent } from './subject-edit.component';

const routes: Routes = [
  {
    path: '',
    component: SubjectEditComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class SubjectEditModule { }
