import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminDashboardComponent } from './admin-dashboard.component';
import { AdminDashboardRoutingModule } from './admin-dashboard-routing.module';

@NgModule({
  imports: [
    CommonModule,
    AdminDashboardRoutingModule,
    AdminDashboardComponent
  ]
})
export class AdminDashboardModule {}