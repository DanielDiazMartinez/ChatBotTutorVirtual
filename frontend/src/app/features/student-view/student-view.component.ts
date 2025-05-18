import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { ChatAreaComponent } from './components/chat-area/chat-area.component';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';
import { DocumentsModalComponent } from './components/documents-modal/documents-modal.component';
import { SubjectService } from '../../services/subject.service';
import { Subject } from '../subject-selection/interfaces/subject.interface';
import { ChatService } from '../../core/services/chat.service';
import { Conversation, Message } from '../../core/models/chat.model';

@Component({
  selector: 'app-student-view',
  standalone: true,
  imports: [CommonModule, SidebarComponent, ChatAreaComponent, HeaderComponent, DocumentsModalComponent],
  templateUrl: './student-view.component.html',
  styleUrls: ['./student-view.component.scss']
})
export class StudentViewComponent implements OnInit { 
  @ViewChild(SidebarComponent) sidebarComponent!: SidebarComponent;
  
  isDocumentsModalVisible = false;
  currentSubject: Subject | null = null;
  isLoading = true;
  error: string | null = null;
  
  // Datos del usuario estudiante
  studentProfile: UserProfile = {
    name: 'Ana García',
    role: 'student',
    avatar: 'assets/images/student-avatar.svg'
  };

  // Conversación activa
  activeConversation: Conversation | null = null;
  conversationMessages: Message[] = [];

  // Lista de asignaturas disponibles
  availableSubjects: Subject[] = [];
  
  constructor(
    private subjectService: SubjectService,
    private chatService: ChatService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.loadSubjects();
  }

  private loadSubjects(): void {
    this.isLoading = true;
    this.error = null;

    this.subjectService.getAllSubjects().subscribe({
      next: (subjects) => {
        this.availableSubjects = subjects;
        this.isLoading = false;

        // Obtener la asignatura seleccionada
        const selectedSubjectIds = this.subjectService.getSelectedSubjects();
        
        if (selectedSubjectIds.length === 0) {
          // Si no hay asignatura seleccionada, redirigir a la página de selección
          this.router.navigate(['/subject-selection']);
          return;
        }
        
        // Buscar la asignatura seleccionada
        const selectedId = selectedSubjectIds[0];
        this.currentSubject = this.availableSubjects.find(subject => subject.id === selectedId) || null;
        
        if (!this.currentSubject) {
          // Si no se encuentra la asignatura, redirigir a la selección
          this.router.navigate(['/subject-selection']);
        }
      },
      error: (error) => {
        console.error('Error al cargar las asignaturas:', error);
        this.error = 'Error al cargar las asignaturas. Por favor, intenta de nuevo.';
        this.isLoading = false;
      }
    });
  }
  
  toggleDocumentsModal(): void {
    this.isDocumentsModalVisible = !this.isDocumentsModalVisible;
  }

  onConversationSelected(conversationId: number): void {
    if (!conversationId) return;
    
    this.chatService.getConversationById(conversationId).subscribe({
      next: (response) => {
        if (response.data) {
          this.activeConversation = response.data;
          this.loadConversationMessages(conversationId);
        }
      },
      error: (error) => {
        console.error('Error al cargar la conversación:', error);
      }
    });
  }

  private loadConversationMessages(conversationId: number): void {
    this.chatService.getConversationMessages(conversationId).subscribe({
      next: (response) => {
        if (response.data) {
          this.conversationMessages = response.data;
        }
      },
      error: (error) => {
        console.error('Error al cargar los mensajes:', error);
      }
    });
  }

  onSendNewMessage(data: {conversationId: number, text: string}): void {
    if (!data.conversationId || !data.text) return;
    
    this.chatService.sendMessage(data.conversationId, data.text).subscribe({
      next: (response) => {
        if (response.data) {
          // Añadir el nuevo mensaje a la lista de mensajes
          this.conversationMessages.push(response.data);
          
          // Actualizar el último mensaje en la barra lateral
          if (this.sidebarComponent) {
            this.sidebarComponent.updateConversationLastMessage(data.conversationId, data.text);
          }
          
          // Simular la respuesta del bot (en un entorno real, esto vendría del websocket o de polling)
          setTimeout(() => {
            this.loadConversationMessages(data.conversationId);
          }, 1000);
        }
      },
      error: (error) => {
        console.error('Error al enviar mensaje:', error);
      }
    });
  }
}