import { Component, ElementRef, ViewChild, AfterViewChecked, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ChatMessage } from '../../interfaces/chat.interface';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { ChatInputComponent } from '../chat-input/chat-input.component';
import { DocumentsModalComponent } from '../documents-modal/documents-modal.component';

@Component({
  selector: 'app-chat-area',
  standalone: true,
  imports: [CommonModule, RouterModule, ChatMessageComponent, ChatInputComponent, DocumentsModalComponent],
  templateUrl: './chat-area.component.html',
  styleUrls: ['./chat-area.component.scss']
})
export class ChatAreaComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @Input() isDocumentsModalVisible = false;
  
  messages: ChatMessage[] = [
    {
      id: '1',
      content: '¡Hola! ¿En qué puedo ayudarte hoy?',
      isUser: false,
      timestamp: new Date()
    }
  ];

  constructor(private router: Router) {}

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
