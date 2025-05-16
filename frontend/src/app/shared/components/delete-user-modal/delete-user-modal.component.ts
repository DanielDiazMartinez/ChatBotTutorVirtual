import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-delete-user-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-overlay" *ngIf="isVisible" (click)="onOverlayClick($event)">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Confirmar eliminación</h2>
        </div>
        <div class="modal-content">
          <div class="warning-icon">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
            </svg>
          </div>
          <p>¿Estás seguro que deseas eliminar al usuario <strong>{{userName}}</strong>?</p>
          <p class="warning-text">Esta acción no se puede deshacer.</p>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" (click)="onCancel()">Cancelar</button>
          <button class="delete-btn" (click)="onConfirm()">Eliminar</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal-container {
      background-color: white;
      border-radius: 8px;
      width: 90%;
      max-width: 400px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      overflow: hidden;
    }

    .modal-header {
      padding: 1.25rem;
      background-color: #3f6464;
      color: white;
      
      h2 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 500;
      }
    }

    .modal-content {
      padding: 1.5rem;
      text-align: center;

      .warning-icon {
        color: #dc3545;
        margin-bottom: 1rem;
      }

      p {
        margin: 0.5rem 0;
        color: #333;
        font-size: 1rem;
        line-height: 1.5;

        &.warning-text {
          color: #dc3545;
          font-size: 0.9rem;
          margin-top: 1rem;
        }
      }
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      padding: 1rem 1.5rem;
      border-top: 1px solid #eee;

      button {
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .cancel-btn {
        background: none;
        border: 1px solid #e0e0e0;
        color: #666;
        
        &:hover {
          background-color: #f5f5f5;
        }
      }

      .delete-btn {
        background-color: #dc3545;
        border: none;
        color: white;
        
        &:hover {
          background-color: #c82333;
        }
      }
    }
  `]
})
export class DeleteUserModalComponent {
  @Input() isVisible = false;
  @Input() userName = '';
  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  onConfirm(): void {
    this.confirm.emit();
  }

  onCancel(): void {
    this.cancel.emit();
  }

  onOverlayClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal-overlay')) {
      this.cancel.emit();
    }
  }
} 