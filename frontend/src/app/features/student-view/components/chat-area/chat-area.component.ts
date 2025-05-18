import { Component, ElementRef, ViewChild, AfterViewChecked, Input, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ChatMessage } from '../../interfaces/chat.interface';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { ChatInputComponent } from '../chat-input/chat-input.component';
import { DocumentsModalComponent } from '../documents-modal/documents-modal.component';
import { Subject } from '../../../subject-selection/interfaces/subject.interface';
import { Conversation, Message } from '../../../../core/models/chat.model';

@Component({
  selector: 'app-chat-area',
  standalone: true,
  imports: [CommonModule, RouterModule, ChatMessageComponent, ChatInputComponent, DocumentsModalComponent],
  templateUrl: './chat-area.component.html',
  styleUrls: ['./chat-area.component.scss']
})
export class ChatAreaComponent implements AfterViewChecked, OnChanges {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @Input() isDocumentsModalVisible = false;
  @Input() currentSubject: Subject | null = null;
  @Input() activeConversation: Conversation | null = null;
  @Input() set apiMessages(value: Message[]) {
    this._apiMessages = value || [];
    this.updateDisplayMessages();
  }
  
  get apiMessages(): Message[] {
    return this._apiMessages;
  }
  
  @Output() sendMessage = new EventEmitter<{conversationId: number, text: string}>();
  
  _apiMessages: Message[] = [];
  displayMessages: ChatMessage[] = [
    {
      id: '1',
      content: '¡Hola! ¿En qué puedo ayudarte hoy?',
      isUser: false,
      timestamp: new Date()
    }
  ];
  
  // Método getter para obtener un mensaje de bienvenida personalizado con la asignatura
  get welcomeMessage(): string {
    return this.currentSubject 
      ? `Estás en la asignatura de ${this.currentSubject.name}. ¿En qué puedo ayudarte?` 
      : '¡Hola! ¿En qué puedo ayudarte hoy?';
  }

  constructor(private router: Router) {
    // Actualizar el primer mensaje de bienvenida cuando se cargue el componente
    setTimeout(() => {
      if (this.displayMessages.length > 0 && !this.displayMessages[0].isUser) {
        this.displayMessages[0].content = this.welcomeMessage;
      }
    }, 0);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['currentSubject'] && !changes['currentSubject'].firstChange) {
      // Actualizar el mensaje de bienvenida si cambia la asignatura
      if (this.displayMessages.length > 0 && !this.displayMessages[0].isUser) {
        this.displayMessages[0].content = this.welcomeMessage;
      }
    }
    
    if (changes['activeConversation'] && changes['activeConversation'].currentValue) {
      // Si hay una nueva conversación activa, actualizamos los mensajes
      this.updateDisplayMessages();
    }
  }

  private updateDisplayMessages(): void {
    // Si hay mensajes de la API, los convertimos al formato que utiliza el componente
    if (this._apiMessages && this._apiMessages.length > 0) {
      this.displayMessages = this._apiMessages.map(apiMsg => ({
        id: apiMsg.id.toString(),
        content: apiMsg.text,
        isUser: !apiMsg.is_bot,
        timestamp: new Date(apiMsg.created_at)
      }));
    } else if (this.activeConversation) {
      // Si hay una conversación activa pero no hay mensajes, mostrar un estado vacío
      this.displayMessages = [];
    } else {
      // Si no hay conversación activa ni mensajes, mostramos el mensaje de bienvenida
      this.displayMessages = [{
        id: '1',
        content: this.welcomeMessage,
        isUser: false,
        timestamp: new Date()
      }];
    }
    
    // Asegurar que después de actualizar los mensajes, hacemos scroll al final
    setTimeout(() => this.scrollToBottom(), 100);
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  onSendMessage(content: string): void {
    if (!content.trim()) return;
    
    // Si hay una conversación activa, enviamos el mensaje a través del Output
    if (this.activeConversation) {
      this.sendMessage.emit({
        conversationId: this.activeConversation.id,
        text: content
      });
    }
    
    // Añadimos el mensaje del usuario a la UI inmediatamente (optimistic update)
    this.displayMessages.push({
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    });
    
    // Simulamos una respuesta si no hay conversación activa (modo desarrollo)
    if (!this.activeConversation) {
      setTimeout(() => {
        this.displayMessages.push({
          id: (Date.now() + 1).toString(),
          content: 'Esta es una respuesta simulada del tutor virtual.',
          isUser: false,
          timestamp: new Date()
        });
      }, 1000);
    }
  }

  goToLogin(): void {
    this.router.navigate(['/login'], { replaceUrl: true });
  }
}
