import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { ChatAreaComponent } from './components/chat-area/chat-area.component';

@Component({
  selector: 'app-student-view',
  standalone: true,
  imports: [CommonModule, SidebarComponent, ChatAreaComponent],
  templateUrl: './student-view.component.html',
  styleUrls: ['./student-view.component.scss']
})
export class StudentViewComponent { }