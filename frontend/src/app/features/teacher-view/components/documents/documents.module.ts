import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { DocumentsComponent } from './documents.component';
import { FormsModule } from '@angular/forms';

const routes: Routes = [
  {
    path: '',
    component: DocumentsComponent
  }
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    RouterModule.forChild(routes)
  ],
  declarations: [
    // The component is standalone, so no need to declare it here
  ]
})
export class DocumentsModule { }
