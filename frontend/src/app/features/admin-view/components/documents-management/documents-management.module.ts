import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DocumentsManagementComponent } from './documents-management.component';

const routes: Routes = [
  {
    path: '',
    component: DocumentsManagementComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    RouterModule.forChild(routes)
  ]
})
export class DocumentsManagementModule { }
