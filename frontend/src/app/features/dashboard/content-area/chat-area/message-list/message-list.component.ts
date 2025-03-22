// src/app/features/dashboard/content-area/chat-area/message-list/message-list.component.ts
import { Component, Input, AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

interface Message {
  id: number;
  text: string;
  is_bot: boolean;
  created_at: string;
}

@Component({
  selector: 'app-message-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './message-list.component.html',
  styleUrls: ['./message-list.component.scss']
})
export class MessageListComponent implements AfterViewChecked {
  @Input() messages: Message[] = [];
  @Input() isLoading: boolean = false;
  
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  constructor() {}
  
  ngAfterViewChecked() {
    this.scrollToBottom();
  }
  
  scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }
}