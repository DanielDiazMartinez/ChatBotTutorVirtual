import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { UserService } from '../../../../core/services/user.service';
import { User, UserCreate } from '../../../../core/models/user.model';
import { finalize } from 'rxjs';
import { DeleteUserModalComponent } from '../../../../shared/components/delete-user-modal/delete-user-modal.component';
import { EditUserComponent } from './edit-user.component';

// Interfaz para la gestión local de usuarios con campos adicionales
export interface UserViewModel {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  subjects: string[];
}

@Component({
  selector: 'app-users-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule, DeleteUserModalComponent, EditUserComponent],
  templateUrl: './users-management.component.html',
  styleUrls: ['./users-management.component.scss']
})
export class UsersManagementComponent implements OnInit {
  users: UserViewModel[] = [];
  searchTerm: string = '';
  showNewUserForm: boolean = false;
  roleFilter: string = '';
  loading: boolean = false;
  error: string | null = null;
  filteredUsers: UserViewModel[] = [];
  showDeleteModal: boolean = false;
  selectedUser: UserViewModel | null = null;
  editingUser: UserViewModel | null = null;

  // Aquí van las variables de touched
  nameTouched = false;
  emailTouched = false;
  passwordTouched = false;
  confirmPasswordTouched = false;

  newUser = {
    name: '',
    email: '',
    role: 'student' as 'admin' | 'teacher' | 'student',
    password: '',
    confirmPassword: ''
  };

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.loadUsers();
  }
  
  loadUsers(): void {
    this.loading = true;
    console.log('1. Iniciando carga de usuarios...');
    this.userService.getAllUsers()
      .pipe(finalize(() => {
        this.loading = false;
        console.log('2. Finalizada la carga de usuarios');
      }))
      .subscribe({
        next: (response) => {
          console.log('3. Respuesta del servidor:', response);
          if (response.data) {
            this.users = response.data.map((user: User) => ({
              id: user.id,
              name: user.full_name || '',
              email: user.email,
              role: user.role,
              subjects: []
            }));
            console.log('4. Usuarios cargados en this.users:', this.users);
            this.applyFilters();
          } else {
            console.log('5. No hay datos en la respuesta');
          }
        },
        error: (error) => {
          console.error('6. Error en la carga:', error);
          this.error = error.error?.detail || error.message || 'Error al cargar los usuarios';
        }
      });
  }
  
  applyFilters(): void {
    this.filteredUsers = this.users.filter(user => {
      const matchesSearch = user.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                          user.email.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchesRole = !this.roleFilter || user.role === this.roleFilter;
      return matchesSearch && matchesRole;
    });
  }

  getRoleInSpanish(role: string): string {
    switch (role) {
      case 'admin':
        return 'administrador';
      case 'teacher':
        return 'profesor';
      case 'student':
        return 'estudiante';
      default:
        return role;
    }
  }
  
  toggleNewUserForm(): void {
    this.showNewUserForm = !this.showNewUserForm;
    if (!this.showNewUserForm) {
      this.newUser = {
        name: '',
        email: '',
        role: 'student',
        password: '',
        confirmPassword: ''
      };
    }
  }

  validateNewUser(): boolean {
    // No setea error, solo retorna si es válido
    return !!this.newUser.name && !!this.newUser.email && !!this.newUser.password && !!this.newUser.confirmPassword &&
      this.newUser.password === this.newUser.confirmPassword &&
      this.newUser.password.length >= 6;
  }
  getNameError(): string | null {
    if (!this.newUser.name && this.nameTouched) return 'El nombre es obligatorio';
    return null;
  }
  getEmailError(): string | null {
    if (!this.newUser.email && this.emailTouched) return 'El correo es obligatorio';
    return null;
  }
  getPasswordError(): string | null {
    if (!this.newUser.password && this.passwordTouched) return 'La contraseña es obligatoria';
    if (this.newUser.password.length > 0 && this.newUser.password.length < 6 && this.passwordTouched) return 'La contraseña debe tener al menos 6 caracteres';
    return null;
  }
  getConfirmPasswordError(): string | null {
    if (!this.newUser.confirmPassword && this.confirmPasswordTouched) return 'La confirmación es obligatoria';
    if (this.newUser.password !== this.newUser.confirmPassword && this.confirmPasswordTouched) return 'Las contraseñas no coinciden';
    return null;
  }
  addNewUser(): void {
    // Limpiar error global
    this.error = null;
    if (this.validateNewUser()) {
      this.loading = true;
      const userData: UserCreate = {
        email: this.newUser.email,
        password: this.newUser.password,
        full_name: this.newUser.name,
        role: this.newUser.role
      };
      this.userService.createUser(userData)
        .pipe(finalize(() => this.loading = false))
        .subscribe({
          next: (response) => {
            if (response.data) {
              const newUser: UserViewModel = {
                id: response.data.id,
                name: response.data.full_name,
                email: response.data.email,
                role: response.data.role,
                subjects: []
              };
              this.users.push(newUser);
              this.applyFilters();
              this.toggleNewUserForm(); // Oculta el formulario y muestra la lista
              // Limpiar los touched
              this.nameTouched = false;
              this.emailTouched = false;
              this.passwordTouched = false;
              this.confirmPasswordTouched = false;
            }
          },
          error: (error) => {
            this.error = error.error?.detail || error.message || 'Error al crear el usuario';
            console.error('Error creating user:', error);
          }
        });
    }
  }

  editUser(userId: number): void {
    const user = this.users.find(u => u.id === userId);
    if (user) {
      // Hacemos una copia para no modificar el original hasta guardar
      this.editingUser = { ...user };
    }
  }

  onEditUserSave(editedUser: UserViewModel): void {
    this.loading = true;
    this.userService.updateUser(editedUser.id, {
      full_name: editedUser.name,
      email: editedUser.email,
      role: editedUser.role
    }).pipe(finalize(() => this.loading = false))
      .subscribe({
        next: (response) => {
          // Actualizar en la lista local
          const idx = this.users.findIndex(u => u.id === editedUser.id);
          if (idx !== -1 && response.data) {
            this.users[idx] = {
              ...this.users[idx],
              name: response.data.full_name,
              email: response.data.email,
              role: response.data.role
            };
            this.applyFilters();
          }
          this.editingUser = null;
        },
        error: (error) => {
          this.error = error.error?.detail || error.message || 'Error al actualizar el usuario';
        }
      });
  }

  onEditUserCancel(): void {
    this.editingUser = null;
  }

  deleteUser(userId: number): void {
    this.selectedUser = this.users.find(user => user.id === userId) || null;
    if (this.selectedUser) {
      this.showDeleteModal = true;
    }
  }

  onDeleteConfirm(): void {
    if (this.selectedUser) {
      this.loading = true;
      this.userService.deleteUser(this.selectedUser.id).subscribe({
        next: () => {
          this.users = this.users.filter(user => user.id !== this.selectedUser?.id);
          this.applyFilters();
          this.showDeleteModal = false;
          this.selectedUser = null;
          this.loading = false;
        },
        error: (error) => {
          this.error = error.error?.detail || error.message || 'Error al eliminar el usuario';
          this.loading = false;
        }
      });
    }
  }

  onDeleteCancel(): void {
    this.showDeleteModal = false;
    this.selectedUser = null;
  }
}
