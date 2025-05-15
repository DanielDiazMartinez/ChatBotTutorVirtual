import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'profesor' | 'estudiante';
  subjects?: string[];
  active: boolean;
}

@Component({
  selector: 'app-users-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './users-management.component.html',
  styleUrls: ['./users-management.component.scss']
})
export class UsersManagementComponent implements OnInit {
  users: User[] = [];
  searchTerm: string = '';
  showNewUserForm: boolean = false;
  roleFilter: string = 'todos';

  // Datos de prueba
  mockUsers: User[] = [
    { id: '1', name: 'Ana García', email: 'ana.garcia@profesor.edu', role: 'profesor', active: true },
    { id: '2', name: 'Carlos López', email: 'carlos.lopez@profesor.edu', role: 'profesor', active: true },
    { id: '3', name: 'María Rodríguez', email: 'maria@estudiante.edu', role: 'estudiante', subjects: ['Matemáticas', 'Física'], active: true },
    { id: '4', name: 'Pedro Sánchez', email: 'pedro@estudiante.edu', role: 'estudiante', subjects: ['Física', 'Biología'], active: true },
    { id: '5', name: 'Laura Martínez', email: 'laura@estudiante.edu', role: 'estudiante', subjects: ['Biología', 'Literatura'], active: true },
    { id: '6', name: 'Javier Fernández', email: 'javier@profesor.edu', role: 'profesor', active: false },
  ];

  newUser = {
    name: '',
    email: '',
    role: 'estudiante' as 'profesor' | 'estudiante',
    password: '',
    confirmPassword: ''
  };

  constructor() {}

  ngOnInit(): void {
    this.users = this.mockUsers;
  }

  getFilteredUsers(): User[] {
    return this.users.filter(user => {
      const matchesTerm = 
        user.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesRole = 
        this.roleFilter === 'todos' || 
        user.role === this.roleFilter;

      return matchesTerm && matchesRole;
    });
  }

  toggleNewUserForm(): void {
    this.showNewUserForm = !this.showNewUserForm;
    if (!this.showNewUserForm) {
      this.resetNewUserForm();
    }
  }

  resetNewUserForm(): void {
    this.newUser = {
      name: '',
      email: '',
      role: 'estudiante',
      password: '',
      confirmPassword: ''
    };
  }

  addNewUser(): void {
    if (this.validateNewUser()) {
      // En un caso real, aquí enviaríamos los datos a un servicio
      const newUserId = (this.users.length + 1).toString();
      const newUserObj: User = {
        id: newUserId,
        name: this.newUser.name,
        email: this.newUser.email,
        role: this.newUser.role,
        active: true
      };
      
      if (this.newUser.role === 'estudiante') {
        newUserObj.subjects = [];
      }

      this.users.push(newUserObj);
      this.toggleNewUserForm();
    }
  }

  validateNewUser(): boolean {
    // Esta validación es básica, en un caso real sería más exhaustiva
    return (
      this.newUser.name.length > 0 &&
      this.newUser.email.length > 0 &&
      this.newUser.password.length >= 6 &&
      this.newUser.password === this.newUser.confirmPassword
    );
  }

  toggleUserStatus(user: User): void {
    user.active = !user.active;
    // En un caso real, aquí actualizaríamos el estado en el servidor
  }

  editUser(userId: string): void {
    // En un caso real, aquí navegaríamos a una vista de edición detallada
    console.log(`Editar usuario con ID: ${userId}`);
  }

  deleteUser(userId: string): void {
    // En un caso real, aquí mostraríamos un diálogo de confirmación
    // y luego eliminaríamos al usuario
    this.users = this.users.filter(user => user.id !== userId);
  }
}
