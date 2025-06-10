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
import { AuthService } from '../../services/auth.service';

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
  
  // Datos del usuario (puede ser estudiante o profesor)
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
    private router: Router,
    private authService: AuthService
  ) {}
  
  ngOnInit(): void {
    this.loadUserProfile();
    this.loadSubjects();
    this.warmupModels(); // Calentar modelos al cargar la vista
  }

  private loadUserProfile(): void {
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        if (user && user.data) {
          this.studentProfile = {
            name: user.data.name || user.data.username,
            role: user.data.role,
            avatar: user.data.role === 'teacher' ? 'assets/images/teacher-avatar.svg' : 'assets/images/student-avatar.svg'
          };
        }
      },
      error: (error) => {
        console.error('Error al cargar el perfil del usuario:', error);
      }
    });
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
    
    // Establecer la conversación activa
    // Creamos un objeto de conversación básico con el ID
    this.activeConversation = {
      id: conversationId,
      created_at: new Date().toISOString()
    };
    
    // Limpiamos los mensajes anteriores
    this.conversationMessages = [];
    
    // Cargamos directamente los mensajes de esta conversación
    this.loadConversationMessages(conversationId);
  }

  private loadConversationMessages(conversationId: number): void {
    // Indicamos que estamos cargando
    const temporalLoadingElement = document.querySelector('.chat-messages-container');
    if (temporalLoadingElement) {
      temporalLoadingElement.classList.add('loading');
    }
    
    this.chatService.getConversationMessages(conversationId).subscribe({
      next: (response) => {
        if (response.data && response.data.length > 0) {
          console.log('Mensajes cargados:', response.data);
          this.conversationMessages = response.data;
        } else {
          this.conversationMessages = [];
          console.warn('No se encontraron mensajes para la conversación');
        }
        
        if (temporalLoadingElement) {
          temporalLoadingElement.classList.remove('loading');
        }
      },
      error: (error) => {
        console.error('Error al cargar los mensajes:', error);
        this.conversationMessages = [];
        
        if (temporalLoadingElement) {
          temporalLoadingElement.classList.remove('loading');
        }
      }
    });
  }

  onSendNewMessage(data: {conversationId: number, text: string, file?: File}): void {
    if (!data.conversationId || (!data.text && !data.file)) return;
    
    // Agregamos directamente el mensaje del usuario para mostrar feedback inmediato (optimistic update)
    const userMessage: Message = {
      id: Date.now(), // ID temporal, será reemplazado con la respuesta del servidor
      conversation_id: data.conversationId,
      text: data.text,
      is_bot: false,
      created_at: new Date().toISOString()
    };
    
    this.conversationMessages.push(userMessage);
    
    // Actualizamos la barra lateral
    if (this.sidebarComponent) {
      this.sidebarComponent.updateConversationLastMessage(data.conversationId, data.text);
    }
    
    // Enviamos el mensaje al servidor
    this.chatService.sendMessage(data.conversationId, data.text, data.file).subscribe({
      next: (response) => {
        if (response.data) {
          // Reemplazamos el mensaje temporal con el real (si es necesario)
          // O simplemente recargamos todos los mensajes
          this.loadConversationMessages(data.conversationId);
        }
      },
      error: (error) => {
        console.error('Error al enviar mensaje:', error);
        // Opcional: Mostrar un mensaje de error en la UI
        // O marcar el mensaje como no enviado
      }
    });
  }

  private warmupModels(): void {
    // Calentar los modelos del backend de forma silenciosa
    this.chatService.warmupModels().subscribe({
      next: (response) => {
        console.log('Modelos calentados exitosamente:', response);
      },
      error: (error) => {
        console.warn('Error al calentar modelos (no crítico):', error);
      }
    });
  }
}