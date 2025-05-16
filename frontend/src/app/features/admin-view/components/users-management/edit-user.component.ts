import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserViewModel } from './users-management.component';

@Component({
  selector: 'app-edit-user',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="edit-user-form new-user-form">
      <h2>Editar usuario</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre completo</label>
          <input type="text" [(ngModel)]="user.name" placeholder="Nombre del usuario" />
        </div>
        <div class="form-group">
          <label>Correo electrónico</label>
          <input type="email" [(ngModel)]="user.email" placeholder="correo@ejemplo.com" />
        </div>
        <div class="form-group">
          <label>Rol</label>
          <select [(ngModel)]="user.role">
            <option value="admin">Administrador</option>
            <option value="teacher">Profesor</option>
            <option value="student">Estudiante</option>
          </select>
        </div>
      </div>
      <div class="form-actions">
        <button class="save-btn" (click)="save()">Guardar</button>
        <button class="cancel-btn" (click)="cancel.emit()">Cancelar</button>
      </div>
    </div>
  `,
  styleUrls: ['./users-management.component.scss']
})
export class EditUserComponent {
  @Input() user!: UserViewModel;
  @Output() saveUser = new EventEmitter<UserViewModel>();
  @Output() cancel = new EventEmitter<void>();

  save() {
    this.saveUser.emit(this.user);
  }
} 