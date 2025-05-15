import { Component, ElementRef, ViewChild, AfterViewChecked, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ChatMessage } from '../../interfaces/chat.interface';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { ChatInputComponent } from '../chat-input/chat-input.component';
import { DocumentsModalComponent } from '../documents-modal/documents-modal.component';
import { Subject } from '../../../subject-selection/interfaces/subject.interface';

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
  
  messages: ChatMessage[] = [
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
      if (this.messages.length > 0 && !this.messages[0].isUser) {
        this.messages[0].content = this.welcomeMessage;
      }
    }, 0);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['currentSubject'] && !changes['currentSubject'].firstChange) {
      // Actualizar el mensaje de bienvenida si cambia la asignatura
      if (this.messages.length > 0 && !this.messages[0].isUser) {
        this.messages[0].content = this.welcomeMessage;
      }
    }
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  onSendMessage(content: string): void {
    if (!content.trim()) return;
    
    this.messages.push({
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    });

    setTimeout(() => {
      this.messages.push({
        id: (Date.now() + 1).toString(),
        content: 'Esta es una respuesta simulada del tutor virtual.',
        isUser: false,
        timestamp: new Date()
      });
    }, 1000);
  }

  goToLogin(): void {
    this.router.navigate(['/login'], { replaceUrl: true });
  }
}
