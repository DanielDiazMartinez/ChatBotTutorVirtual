import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { ChatAreaComponent } from './components/chat-area/chat-area.component';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';
import { DocumentsModalComponent } from './components/documents-modal/documents-modal.component';

@Component({
  selector: 'app-student-view',
  standalone: true,
  imports: [CommonModule, SidebarComponent, ChatAreaComponent, HeaderComponent, DocumentsModalComponent],
  templateUrl: './student-view.component.html',
  styleUrls: ['./student-view.component.scss']
})
export class StudentViewComponent { 
  isDocumentsModalVisible = false;
  
  // Datos del usuario estudiante
  studentProfile: UserProfile = {
    name: 'Ana García',
    role: 'student',
    avatar: 'assets/images/student-avatar.svg'
  };
  
  toggleDocumentsModal(): void {
    this.isDocumentsModalVisible = !this.isDocumentsModalVisible;
  }
}