import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SubjectsComponent } from './subjects.component';

const routes: Routes = [
  {
    path: '',
    component: SubjectsComponent
  },
  {
    path: ':id',
    component: SubjectsComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ],
  declarations: [
    // Component is standalone, so no need to declare it here
  ]
})
export class SubjectsModule { }
