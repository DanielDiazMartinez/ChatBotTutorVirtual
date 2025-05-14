import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StudentProfileRoutingModule } from './student-profile-routing.module';

@NgModule({
  imports: [
    CommonModule,
    StudentProfileRoutingModule
  ],
  declarations: [
    // Component is standalone, so no need to declare it here
  ]
})
export class StudentProfileModule { }
