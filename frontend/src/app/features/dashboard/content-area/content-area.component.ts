import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatAreaComponent } from './chat-area/chat-area.component';

@Component({
  selector: 'app-content-area',
  standalone: true,
  imports: [CommonModule, ChatAreaComponent],
  templateUrl: './content-area.component.html',
  styleUrls: ['./content-area.component.scss']
})
export class ContentAreaComponent {
  @Input() documentId: number | null = null;
  @Input() conversationId: number | null = null;
  
  showPdfViewer: boolean = false;
  
  togglePdfViewer(): void {
    this.showPdfViewer = !this.showPdfViewer;
  }
}