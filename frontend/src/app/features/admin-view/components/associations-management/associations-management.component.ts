import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'profesor' | 'estudiante';
  subjects: string[];
  active: boolean;
}

interface Subject {
  id: string;
  name: string;
  description: string;
  active: boolean;
}

@Component({
  selector: 'app-associations-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './associations-management.component.html',
  styleUrls: ['./associations-management.component.scss']
})
export class AssociationsManagementComponent implements OnInit {
  // Lista de usuarios y asignaturas
  users: User[] = [];
  subjects: Subject[] = [];
  
  // Filtros
  selectedSubject: string = '';
  selectedRole: string = 'todos';
  searchTerm: string = '';
  
  // Asignaciones
  showAssignForm: boolean = false;
  selectedUserId: string = '';
  selectedSubjectId: string = '';
  
  // Modos de visualización
  viewMode: 'subjects' | 'users' = 'subjects';
  
  // Datos de prueba
  mockSubjects: Subject[] = [
    { id: '1', name: 'Matemáticas', description: 'Álgebra, Cálculo y Geometría', active: true },
    { id: '2', name: 'Física', description: 'Mecánica, Electricidad y Termodinámica', active: true },
    { id: '3', name: 'Biología', description: 'Genética, Ecología y Evolución', active: true },
    { id: '4', name: 'Literatura', description: 'Narrativa, Poesía y Teatro', active: true },
    { id: '5', name: 'Historia', description: 'Historia antigua, medieval y moderna', active: false }
  ];
  
  mockUsers: User[] = [
    { id: '1', name: 'Ana García', email: 'ana.garcia@profesor.edu', role: 'profesor', subjects: ['1', '2'], active: true },
    { id: '2', name: 'Carlos López', email: 'carlos.lopez@profesor.edu', role: 'profesor', subjects: ['3'], active: true },
    { id: '3', name: 'María Rodríguez', email: 'maria@estudiante.edu', role: 'estudiante', subjects: ['1', '2'], active: true },
    { id: '4', name: 'Pedro Sánchez', email: 'pedro@estudiante.edu', role: 'estudiante', subjects: ['2', '3'], active: true },
    { id: '5', name: 'Laura Martínez', email: 'laura@estudiante.edu', role: 'estudiante', subjects: ['3', '4'], active: true },
    { id: '6', name: 'Javier Fernández', email: 'javier@profesor.edu', role: 'profesor', subjects: ['4', '5'], active: false },
  ];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.users = this.mockUsers;
    this.subjects = this.mockSubjects;
    
    this.route.queryParamMap.subscribe(params => {
      const subjectId = params.get('subject');
      if (subjectId) {
        this.selectedSubject = subjectId;
        this.viewMode = 'subjects';
      }
    });
  }
  
  getSubjectById(id: string): Subject | undefined {
    return this.subjects.find(subject => subject.id === id);
  }
  
  getUsersBySubject(subjectId: string): User[] {
    return this.users.filter(user => 
      user.subjects.includes(subjectId) &&
      (this.selectedRole === 'todos' || user.role === this.selectedRole) &&
      (this.searchTerm === '' || 
       user.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
       user.email.toLowerCase().includes(this.searchTerm.toLowerCase()))
    );
  }
  
  // Método para filtrar profesores por asignatura
  getProfessorsBySubject(subjectId: string): User[] {
    return this.getUsersBySubject(subjectId).filter(user => user.role === 'profesor');
  }
  
  // Método para filtrar estudiantes por asignatura
  getStudentsBySubject(subjectId: string): User[] {
    return this.getUsersBySubject(subjectId).filter(user => user.role === 'estudiante');
  }
  
  // Método para contar profesores por asignatura
  getProfessorCountBySubject(subjectId: string): number {
    return this.getProfessorsBySubject(subjectId).length;
  }
  
  // Método para contar estudiantes por asignatura
  getStudentCountBySubject(subjectId: string): number {
    return this.getStudentsBySubject(subjectId).length;
  }
  
  getSubjectsByUser(userId: string): Subject[] {
    const user = this.users.find(u => u.id === userId);
    if (!user) return [];
    
    return this.subjects.filter(subject => 
      user.subjects.includes(subject.id) &&
      (this.searchTerm === '' || 
       subject.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
       subject.description.toLowerCase().includes(this.searchTerm.toLowerCase()))
    );
  }
  
  getUsersNotInSubject(subjectId: string): User[] {
    return this.users.filter(user => 
      !user.subjects.includes(subjectId) && 
      user.active && 
      (this.selectedRole === 'todos' || user.role === this.selectedRole)
    );
  }
  
  getSubjectsNotAssignedToUser(userId: string): Subject[] {
    const user = this.users.find(u => u.id === userId);
    if (!user) return [];
    
    return this.subjects.filter(subject => 
      !user.subjects.includes(subject.id) && 
      subject.active
    );
  }
  
  // Método para obtener usuarios filtrados por rol
  getFilteredUsers(role: string | null = null): User[] {
    return this.users.filter(user =>
      (role === null || user.role === role) &&
      (this.selectedRole === 'todos' || user.role === this.selectedRole)
    );
  }
  
  toggleAssignForm(): void {
    this.showAssignForm = !this.showAssignForm;
    if (!this.showAssignForm) {
      this.selectedUserId = '';
      this.selectedSubjectId = '';
    }
  }
  
  assignUserToSubject(): void {
    if (!this.selectedUserId || !this.selectedSubjectId) return;
    
    // En un caso real, aquí enviaríamos los datos a un servicio
    const user = this.users.find(u => u.id === this.selectedUserId);
    if (user && !user.subjects.includes(this.selectedSubjectId)) {
      user.subjects.push(this.selectedSubjectId);
    }
    
    this.toggleAssignForm();
  }
  
  removeUserFromSubject(userId: string, subjectId: string): void {
    // En un caso real, aquí mostraríamos un diálogo de confirmación
    const user = this.users.find(u => u.id === userId);
    if (user) {
      user.subjects = user.subjects.filter(id => id !== subjectId);
    }
  }
  
  switchViewMode(mode: 'subjects' | 'users'): void {
    this.viewMode = mode;
    // Resetear filtros al cambiar de vista
    if (mode === 'subjects') {
      this.selectedSubject = '';
    } else {
      this.selectedUserId = '';
    }
    this.searchTerm = '';
  }

  // Método para obtener el usuario seleccionado
  getSelectedUser(): User | undefined {
    return this.users.find(u => u.id === this.selectedUserId);
  }
  
  // Método para obtener el nombre del usuario seleccionado
  getSelectedUserName(): string {
    return this.getSelectedUser()?.name || '';
  }
  
  // Método para obtener el email del usuario seleccionado
  getSelectedUserEmail(): string {
    return this.getSelectedUser()?.email || '';
  }
  
  // Método para obtener el rol del usuario seleccionado
  getSelectedUserRole(): string {
    return this.getSelectedUser()?.role === 'profesor' ? 'Profesor' : 'Estudiante';
  }
  
  // Método para obtener la inicial del usuario seleccionado
  getSelectedUserInitial(): string {
    const name = this.getSelectedUserName();
    return name ? name.charAt(0) : '';
  }
}
