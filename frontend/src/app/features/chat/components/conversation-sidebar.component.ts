import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ConversationService } from '../services/conversation.service';
import { Conversation } from '../interfaces/conversation.interface';

@Component({
  selector: 'app-conversation-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="conversation-sidebar">
      <h3 class="sidebar-title">Mis conversaciones</h3>
      
      <div *ngIf="loading" class="loading-spinner">
        Cargando...
      </div>
      
      <div *ngIf="error" class="error-message">
        {{ error }}
      </div>

      <ng-container *ngIf="!loading && !error">
        <div *ngIf="conversations.length === 0" class="no-conversations">
          No tienes conversaciones activas
        </div>
        
        <ul class="conversation-list">
          <li *ngFor="let conversation of conversations" 
              class="conversation-item"
              [class.active]="selectedConversationId === conversation.id"
              (click)="selectConversation(conversation)">
            <div class="conversation-title">
              Conversación {{ conversation.id }}
            </div>
            <div class="conversation-preview" *ngIf="conversation.messages.length > 0">
              {{ getLastMessage(conversation) }}
            </div>
          </li>
        </ul>
      </ng-container>
    </div>
  `,
  styles: [`
    .conversation-sidebar {
      width: 100%;
      height: 100%;
      padding: 1rem;
      background-color: #f5f5f5;
      border-right: 1px solid #e0e0e0;
      overflow-y: auto;
    }
    
    .sidebar-title {
      margin-bottom: 1.5rem;
      font-size: 1.2rem;
      font-weight: 500;
    }
    
    .conversation-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .conversation-item {
      padding: 0.75rem;
      border-radius: 4px;
      margin-bottom: 0.5rem;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    
    .conversation-item:hover {
      background-color: #e9e9e9;
    }
    
    .conversation-item.active {
      background-color: #e1e1e1;
    }
    
    .conversation-title {
      font-weight: 500;
      margin-bottom: 0.25rem;
    }
    
    .conversation-preview {
      font-size: 0.85rem;
      color: #666;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }
    
    .loading-spinner {
      text-align: center;
      padding: 1rem;
      color: #666;
    }
    
    .error-message {
      color: #d32f2f;
      padding: 0.5rem;
      text-align: center;
    }
    
    .no-conversations {
      text-align: center;
      color: #666;
      padding: 1rem;
    }
  `]
})
export class ConversationSidebarComponent implements OnInit {
  conversations: Conversation[] = [];
  loading: boolean = true;
  error: string | null = null;
  selectedConversationId: number | null = null;

  constructor(
    private conversationService: ConversationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadConversations();
  }

  /**
   * Carga las conversaciones del usuario actual
   */
  loadConversations(): void {
    this.loading = true;
    this.error = null;

    this.conversationService.getUserConversations().subscribe({
      next: (response) => {
        this.conversations = response.data;
        this.loading = false;
        
        // Extraer el ID de la conversación de la URL actual si existe
        const urlParts = this.router.url.split('/');
        const conversationIdFromUrl = Number(urlParts[urlParts.length - 1]);
        
        if (!isNaN(conversationIdFromUrl)) {
          this.selectedConversationId = conversationIdFromUrl;
        }
      },
      error: (err) => {
        console.error('Error al cargar las conversaciones:', err);
        this.error = 'Error al cargar las conversaciones. Por favor, intenta de nuevo.';
        this.loading = false;
      }
    });
  }

  /**
   * Selecciona una conversación y navega a su vista detallada
   */
  selectConversation(conversation: Conversation): void {
    this.selectedConversationId = conversation.id;
    this.router.navigate(['/chat', conversation.id]);
  }

  /**
   * Obtiene el último mensaje de una conversación para mostrar en la vista previa
   */
  getLastMessage(conversation: Conversation): string {
    if (!conversation.messages || conversation.messages.length === 0) {
      return 'No hay mensajes';
    }
    
    // Ordenar los mensajes por fecha y obtener el último
    const messages = [...conversation.messages].sort((a, b) => {
      return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
    });
    
    const lastMessage = messages[0];
    return lastMessage.text.length > 50 
      ? lastMessage.text.substring(0, 50) + '...' 
      : lastMessage.text;
  }
}
