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
}
