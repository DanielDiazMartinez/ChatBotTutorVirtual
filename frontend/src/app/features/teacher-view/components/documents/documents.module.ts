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
    RouterModule.forChild(routes),
    DocumentsComponent // Importar el componente standalone
  ]
})
export class DocumentsModule { }
