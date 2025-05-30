import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '../../interfaces/chat.interface';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-chat-message',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chat-message.component.html',
  styleUrls: ['./chat-message.component.scss']
})
export class ChatMessageComponent {
  @Input() message!: ChatMessage;
  @Output() imageClick = new EventEmitter<number>();
  
  private apiUrl = environment.apiUrl;
  
  getImageUrl(imageId: number): string {
    return `${this.apiUrl}/images/${imageId}/file`;
  }
  
  onImageClick(imageId: number): void {
    this.imageClick.emit(imageId);
  }

  // Formatea el contenido del mensaje para mostrar correctamente listas y otros elementos
  formatMessageContent(content: string): string {
    return content
      // Convertir listas numeradas (1. texto) en formato HTML
      .replace(/(\d+)\.\s+\*\*(.*?)\*\*/g, '<div class="numbered-item"><span class="number">$1.</span> <strong>$2</strong></div>')
      .replace(/(\d+)\.\s+(.*?)(?=\n|$)/g, '<div class="numbered-item"><span class="number">$1.</span> <span class="content">$2</span></div>')
      // Convertir texto en negrita **texto** a <strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Convertir saltos de línea en <br>
      .replace(/\n/g, '<br>')
      // Limpiar espacios extra
      .trim();
  }
}
