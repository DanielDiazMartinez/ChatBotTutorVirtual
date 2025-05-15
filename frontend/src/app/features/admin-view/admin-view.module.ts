import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminViewRoutingModule } from './admin-view-routing.module';
import { AdminViewComponent } from './admin-view.component';
import { RouterModule } from '@angular/router';

// Componente principal que se carga de forma independiente
// y usa una arquitectura de lazy loading para los subcomponentes

@NgModule({
  imports: [
    CommonModule,
    AdminViewRoutingModule
  ]
})
export class AdminViewModule { }
