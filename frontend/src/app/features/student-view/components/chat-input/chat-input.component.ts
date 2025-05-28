import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface ChatMessageInput {
  text: string;
  file?: File;
}

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-input.component.html',
  styleUrls: ['./chat-input.component.scss']
})
export class ChatInputComponent {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  @Output() sendMessage = new EventEmitter<ChatMessageInput>();
  
  message: string = '';
  selectedFile: File | null = null;
  selectedFileName: string = '';

  onSubmit(): void {
    if (this.message.trim() || this.selectedFile) {
      this.sendMessage.emit({
        text: this.message.trim(),
        file: this.selectedFile || undefined
      });
      this.message = '';
      this.clearSelectedFile();
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSubmit();
    }
  }
  
  openFileSelector(): void {
    this.fileInput.nativeElement.click();
  }
  
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.selectedFileName = this.selectedFile.name;
    }
  }
  
  clearSelectedFile(): void {
    this.selectedFile = null;
    this.selectedFileName = '';
    if (this.fileInput?.nativeElement) {
      this.fileInput.nativeElement.value = '';
    }
  }
}
