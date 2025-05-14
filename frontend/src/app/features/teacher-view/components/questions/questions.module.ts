import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { QuestionsComponent } from './questions.component';

const routes: Routes = [
  {
    path: '',
    component: QuestionsComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ],
  declarations: [
    // The component is standalone, so no need to declare it here
  ]
})
export class QuestionsModule { }
