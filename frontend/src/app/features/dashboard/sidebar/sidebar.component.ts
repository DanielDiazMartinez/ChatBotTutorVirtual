// src/app/features/dashboard/sidebar/sidebar.component.ts
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

// Interfaces
interface Document {
  id: number;
  title: string;
  description: string;
  file_path: string;
}

interface Conversation {
  id: number;
  document_id: number;
  created_at: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  @Input() documents: Document[] = [];
  @Input() conversations: Conversation[] = [];
  @Input() currentDocumentId: number | null = null;
  @Input() currentConversationId: number | null = null;
  @Input() isLoading: boolean = false;
  
  @Output() documentSelected = new EventEmitter<number>();
  @Output() conversationSelected = new EventEmitter<number>();
  @Output() newConversation = new EventEmitter<void>();
  
  onSelectDocument(id: number): void {
    this.documentSelected.emit(id);
  }
  
  onSelectConversation(id: number): void {
    this.conversationSelected.emit(id);
  }
  
  onCreateNewConversation(): void {
    this.newConversation.emit();
  }
}