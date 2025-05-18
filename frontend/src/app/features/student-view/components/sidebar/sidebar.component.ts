import { Component, OnInit, ViewEncapsulation, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { ChatService } from '../../../../core/services/chat.service';
import { Conversation } from '../../../../core/models/chat.model';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SidebarComponent implements OnInit {
  @Output() conversationSelected = new EventEmitter<number>();
  
  conversations: Conversation[] = [];
  activeConversationId: string | null = null;
  isLoading = false;
  error: string | null = null;

  constructor(private chatService: ChatService) { }

  ngOnInit(): void {
    this.loadConversations();
  }

  loadConversations(): void {
    this.isLoading = true;
    this.chatService.getUserConversations().subscribe({
      next: (response) => {
        if (response.data) {
          this.conversations = response.data.map(conv => ({
            ...conv,
            title: this.formatConversationTitle(conv),
            pinned: conv.pinned || false
          }));
          this.sortConversations();
          if (this.conversations.length > 0 && !this.activeConversationId) {
            this.selectConversation(String(this.conversations[0].id));
          }
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error al cargar conversaciones:', err);
        this.error = 'Error al cargar las conversaciones';
        this.isLoading = false;
      }
    });
  }
  
  /**
   * Formatea el título de la conversación usando el último mensaje o un título predeterminado
   */
  formatConversationTitle(conversation: Conversation): string {
    if (conversation.last_message) {
      // Extraer el texto del mensaje dependiendo de si es string u objeto
      let message: string;
      if (typeof conversation.last_message === 'string') {
        message = conversation.last_message;
      } else if (typeof conversation.last_message === 'object' && 'text' in conversation.last_message) {
        message = conversation.last_message.text;
      } else {
        message = 'Nuevo mensaje';
      }
      
      // Truncar el último mensaje si es más largo de 50 caracteres
      return message.length > 50 
        ? `${message.substring(0, 47)}...` 
        : message;
    }
    
    return conversation.title || `Conversación ${conversation.id}`;
  }

  onNewConversation(): void {
    // Esta funcionalidad se mantendrá en el componente padre ya que requiere
    // información del documento y la asignatura
    const newConversation: Conversation = {
      id: Date.now(),
      student_id: 0, // Esto se llenará en el backend
      document_id: 0, // Esto se llenará cuando se seleccione un documento
      created_at: new Date().toISOString(),
      title: 'Nueva Conversación',
      last_message: {
        text: 'Nueva conversación iniciada',
        is_bot: false,
        created_at: new Date().toISOString()
      },
      pinned: false
    };
    this.conversations.unshift(newConversation);
    this.selectConversation(String(newConversation.id));
  }

  selectConversation(conversationId: string): void {
    this.activeConversationId = conversationId;
    this.conversationSelected.emit(Number(conversationId));
  }

  onPinConversation(conversationId: string, event: MouseEvent): void {
    event.stopPropagation();
    const conversation = this.conversations.find(c => String(c.id) === conversationId);
    if (conversation) {
      conversation.pinned = !conversation.pinned;
      this.sortConversations();
      // Aquí se podría implementar una actualización en el backend
    }
  }

  onDeleteConversation(conversationId: string, event: MouseEvent): void {
    event.stopPropagation();
    this.conversations = this.conversations.filter(c => String(c.id) !== conversationId);
    
    if (this.activeConversationId === conversationId) {
      this.activeConversationId = this.conversations.length > 0 ? String(this.conversations[0].id) : null;
      if (this.activeConversationId) {
        this.conversationSelected.emit(Number(this.activeConversationId));
      }
    }
    // Aquí se podría implementar una eliminación en el backend
  }

  private sortConversations(): void {
    this.conversations.sort((a, b) => {
      if (a.pinned === b.pinned) {
        // Si ambas están fijadas o ambas no están fijadas, ordenar por fecha de creación (más reciente primero)
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      return a.pinned ? -1 : 1;
    });
  }

  /**
   * Actualiza el último mensaje de una conversación específica
   * Este método debería ser llamado cuando se reciben nuevos mensajes
   */
  updateConversationLastMessage(conversationId: number, lastMessage: string): void {
    const conversation = this.conversations.find(c => c.id === conversationId);
    if (conversation) {
      // Crear un objeto LastMessage con el texto actualizado
      conversation.last_message = {
        text: lastMessage,
        is_bot: false,
        created_at: new Date().toISOString()
      };
      conversation.title = this.formatConversationTitle(conversation);
    }
  }

  showOptionsModal(conversation: Conversation, event: MouseEvent): void {
    event.stopPropagation();
    
    // Cerrar modal existente si hay uno
    const existingModal = document.querySelector('.options-modal');
    existingModal?.remove();

    const modalDiv = document.createElement('div');
    modalDiv.className = 'options-modal';
    
    const pinButton = document.createElement('button');
    pinButton.className = 'modal-option';
    pinButton.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z" fill="currentColor" />
      </svg>
      <span>${conversation.pinned ? 'Desfijar' : 'Fijar'} conversación</span>
    `;
    pinButton.onclick = () => {
      modalDiv.remove();
      this.onPinConversation(String(conversation.id), event);
    };

    const deleteButton = document.createElement('button');
    deleteButton.className = 'modal-option delete';
    deleteButton.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" fill="currentColor" />
      </svg>
      <span>Eliminar conversación</span>
    `;
    deleteButton.onclick = () => {
      modalDiv.remove();
      this.onDeleteConversation(String(conversation.id), event);
    };

    modalDiv.appendChild(pinButton);
    modalDiv.appendChild(deleteButton);

    document.body.appendChild(modalDiv);

    const buttonRect = (event.target as HTMLElement).getBoundingClientRect();
    
    // Calcular posición para que aparezca al lado del botón
    let left = buttonRect.right + 5;
    let top = buttonRect.top;

    // Asegurarse de que no se salga de la ventana
    if (left + 180 > window.innerWidth) { // 180px es el min-width del modal
      left = buttonRect.left - 180 - 5;
    }

    Object.assign(modalDiv.style, {
      position: 'fixed',
      top: top + 'px',
      left: left + 'px',
      display: 'block'
    });

    // Cerrar el modal al hacer clic fuera
    document.addEventListener('click', (e) => {
      if (modalDiv && !modalDiv.contains(e.target as Node)) {
        modalDiv.remove();
      }
    }, { once: true });
  }
}