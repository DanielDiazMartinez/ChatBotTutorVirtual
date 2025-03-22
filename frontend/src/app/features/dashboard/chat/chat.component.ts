import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../../core/services/chat.service';
import { Message, Conversation } from '../../../core/services/dummy-data.service';
import { Subscription } from 'rxjs';
// import { ChatInputComponent } from '../dashboard/chat-input/chat-input.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy {
  conversationId: number = 0;
  conversation: Conversation | null = null;
  messages: Message[] = [];
  newMessage: string = '';
  loading: boolean = true;
  error: string | null = null;
  private subscriptions: Subscription = new Subscription();
  
  constructor(
    private route: ActivatedRoute,
    private chatService: ChatService
  ) {}

  ngOnInit(): void {
    this.subscriptions.add(
      this.route.params.subscribe(params => {
        this.conversationId = +params['id'] || 1;
        this.loadConversation();
      })
    );
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadConversation(): void {
    this.loading = true;
    this.error = null;
    
    this.subscriptions.add(
      this.chatService.getConversation(this.conversationId).subscribe({
        next: (conversation) => {
          if (conversation) {
            this.conversation = conversation;
            this.messages = conversation.messages || [];
          } else {
            this.error = "No se encontró la conversación";
          }
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading conversation:', err);
          this.error = "Error al cargar la conversación";
          this.loading = false;
        }
      })
    );
  }

  sendMessage(): void {
    if (!this.newMessage.trim()) return;
    
    // Optimistic UI update
    const tempMessage: Message = {
      id: -1, // Temporal ID
      conversation_id: this.conversationId,
      text: this.newMessage,
      is_bot: false,
      created_at: new Date().toISOString()
    };
    
    this.messages.push(tempMessage);
    const messageText = this.newMessage;
    this.newMessage = ''; // Clear input
    
    this.subscriptions.add(
      this.chatService.sendMessage(this.conversationId, messageText).subscribe({
        next: (response) => {
          // La respuesta ya incluye el mensaje del bot gracias a
          // la lógica en el servicio
          console.log('Message sent successfully', response);
          // Actualizar toda la conversación para asegurar sincronización
          this.loadConversation();
        },
        error: (err) => {
          console.error('Error sending message:', err);
          // Remover mensaje optimista en caso de error
          this.messages = this.messages.filter(m => m !== tempMessage);
          this.error = "Error al enviar el mensaje";
        }
      })
    );
  }

  
  handleNewMessage(text: string): void {
    if (!text.trim()) return;
    
    // Luego puedes llamar a tu método sendMessage() existente
    this.newMessage = text;
    this.sendMessage();
  }
}

