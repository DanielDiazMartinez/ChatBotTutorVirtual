import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; 

interface Conversation {
  id: string;
  title: string;
  date: string;
  pinned: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  conversations: Conversation[] = [
    { id: '1', title: 'Introducción a Angular', date: '09/05/2025', pinned: false },
    { id: '2', title: 'Componentes y Módulos', date: '08/05/2025', pinned: true },
    { id: '3', title: 'Servicios e Inyección de Dependencias', date: '07/05/2025', pinned: false },
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
      date: new Date().toLocaleDateString(),
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
      if (a.pinned === b.pinned) {
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      }
      return a.pinned ? -1 : 1;
    });
  }
}