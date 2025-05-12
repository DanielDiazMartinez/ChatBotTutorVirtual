import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common'; 

interface Conversation {
  id: string;
  title: string;
  pinned: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SidebarComponent implements OnInit {
  conversations: Conversation[] = [
    { id: '1', title: 'Introducción a Angular', pinned: false },
    { id: '2', title: 'Componentes y Módulos', pinned: true },
    { id: '3', title: 'Servicios e Inyección de Dependencias', pinned: false },
  ];
  activeConversationId: string | null = null;

  constructor() { }

  ngOnInit(): void {
    if (this.conversations.length > 0) {
      this.activeConversationId = this.conversations[0].id;
    }
  }

  onNewConversation(): void {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'Nueva Conversación',
      pinned: false
    };
    this.conversations.unshift(newConversation);
    this.activeConversationId = newConversation.id;
  }

  selectConversation(conversationId: string): void {
    this.activeConversationId = conversationId;
  }

  onPinConversation(conversationId: string, event: MouseEvent): void {
    event.stopPropagation();
    const conversation = this.conversations.find(c => c.id === conversationId);
    if (conversation) {
      conversation.pinned = !conversation.pinned;
      this.sortConversations();
    }
  }

  onDeleteConversation(conversationId: string, event: MouseEvent): void {
    event.stopPropagation();
    this.conversations = this.conversations.filter(c => c.id !== conversationId);
    
    if (this.activeConversationId === conversationId) {
      this.activeConversationId = this.conversations.length > 0 ? this.conversations[0].id : null;
    }
  }

  private sortConversations(): void {
    this.conversations.sort((a, b) => {
      return a.pinned ? -1 : 1;
    });
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
      this.onPinConversation(conversation.id, event);
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
      this.onDeleteConversation(conversation.id, event);
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