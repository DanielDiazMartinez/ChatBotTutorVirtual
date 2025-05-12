import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '../../interfaces/chat.interface';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { ChatInputComponent } from '../chat-input/chat-input.component';

@Component({
  selector: 'app-chat-area',
  standalone: true,
  imports: [CommonModule, ChatMessageComponent, ChatInputComponent],
  templateUrl: './chat-area.component.html',
  styleUrls: ['./chat-area.component.scss']
})
export class ChatAreaComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  messages: ChatMessage[] = [
    {
      id: '1',
      content: '¡Hola! ¿En qué puedo ayudarte hoy?',
      isUser: false,
      timestamp: new Date()
    }
  ];

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  onSendMessage(content: string): void {
    // Agregar mensaje del usuario
    this.messages.push({
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    });

    // Simular respuesta del bot (esto se reemplazará con la llamada real al backend)
    setTimeout(() => {
      this.messages.push({
        id: (Date.now() + 1).toString(),
        content: 'Esta es una respuesta simulada del tutor virtual.',
        isUser: false,
        timestamp: new Date()
      });
    }, 1000);
  }
}
