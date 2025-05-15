import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { QuestionsManagementComponent } from './questions-management.component';

const routes: Routes = [
  {
    path: '',
    component: QuestionsManagementComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class QuestionsManagementModule { }
