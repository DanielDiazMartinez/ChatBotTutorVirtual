import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-image-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-modal.component.html',
  styleUrls: ['./image-modal.component.scss']
})
export class ImageModalComponent {
  @Input() isVisible = false;
  @Input() imageId: number | null = null;
  @Output() closeModal = new EventEmitter<void>();

  private apiUrl = environment.apiUrl;

  get imageUrl(): string {
    return this.imageId ? `${this.apiUrl}/images/${this.imageId}/file` : '';
  }

  onClose(): void {
    this.closeModal.emit();
  }

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }
}