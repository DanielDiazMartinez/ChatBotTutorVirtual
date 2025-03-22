// src/app/features/dashboard/content-area/chat-area/message-input/message-input.component.ts
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-message-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './message-input.component.html',
  styleUrls: ['./message-input.component.scss']
})
export class MessageInputComponent {
  @Input() isDisabled: boolean = false;
  @Output() messageSent = new EventEmitter<string>();
  
  message: string = '';
  
  onKeyDown(event: KeyboardEvent): void {
    // Enviar mensaje al presionar Enter sin Shift
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
  
  sendMessage(): void {
    if (!this.message.trim() || this.isDisabled) return;
    
    this.messageSent.emit(this.message);
    this.message = '';
  }
}