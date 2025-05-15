import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface Subject {
  id: string;
  name: string;
  description: string;
  teacherCount: number;
  studentCount: number;
  active: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'student' | 'teacher' | 'admin';
  avatar?: string;
}

export interface SubjectUsersResponse {
  assignedUsers: User[];
  availableUsers: User[];
}

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private apiUrl = environment.apiUrl;

  // Datos mock para pruebas
  private mockSubjects: Subject[] = [
    { id: '1', name: 'Matemáticas', description: 'Álgebra, Cálculo y Geometría', teacherCount: 2, studentCount: 35, active: true },
    { id: '2', name: 'Física', description: 'Mecánica, Electricidad y Termodinámica', teacherCount: 1, studentCount: 28, active: true },
    { id: '3', name: 'Biología', description: 'Genética, Ecología y Evolución', teacherCount: 2, studentCount: 32, active: true },
    { id: '4', name: 'Literatura', description: 'Narrativa, Poesía y Teatro', teacherCount: 1, studentCount: 25, active: true },
    { id: '5', name: 'Historia', description: 'Historia antigua, medieval y moderna', teacherCount: 1, studentCount: 30, active: false }
  ];
  
  private mockUsers: {[key: string]: SubjectUsersResponse} = {
    '1': {
      assignedUsers: [
        { id: '1', name: 'Ana García', email: 'ana@example.com', role: 'student' },
        { id: '2', name: 'Carlos López', email: 'carlos@example.com', role: 'student' },
        { id: '3', name: 'Profesor Martínez', email: 'martinez@example.com', role: 'teacher' }
      ],
      availableUsers: [
        { id: '4', name: 'Laura Pérez', email: 'laura@example.com', role: 'student' },
        { id: '5', name: 'David Sánchez', email: 'david@example.com', role: 'student' },
        { id: '6', name: 'Profesora Rodríguez', email: 'rodriguez@example.com', role: 'teacher' },
        { id: '7', name: 'Profesor Gómez', email: 'gomez@example.com', role: 'teacher' }
      ]
    }
  };

  constructor(private http: HttpClient) { }

  // Métodos para manejo de asignaturas

  getSubjects(): Observable<Subject[]> {
    // En un entorno real: return this.http.get<Subject[]>(`${this.apiUrl}/subjects`);
    return of(this.mockSubjects);
  }

  createSubject(subject: Partial<Subject>): Observable<Subject> {
    // En un entorno real: return this.http.post<Subject>(`${this.apiUrl}/subjects`, subject);
    const newSubject: Subject = {
      id: (this.mockSubjects.length + 1).toString(),
      name: subject.name || '',
      description: subject.description || '',
      teacherCount: 0,
      studentCount: 0,
      active: true
    };
    
    this.mockSubjects.push(newSubject);
    return of(newSubject);
  }

  updateSubject(id: string, changes: Partial<Subject>): Observable<Subject> {
    // En un entorno real: return this.http.put<Subject>(`${this.apiUrl}/subjects/${id}`, changes);
    const index = this.mockSubjects.findIndex(s => s.id === id);
    if (index !== -1) {
      this.mockSubjects[index] = { ...this.mockSubjects[index], ...changes };
      return of(this.mockSubjects[index]);
    }
    throw new Error('Asignatura no encontrada');
  }

  deleteSubject(id: string): Observable<void> {
    // En un entorno real: return this.http.delete<void>(`${this.apiUrl}/subjects/${id}`);
    this.mockSubjects = this.mockSubjects.filter(s => s.id !== id);
    return of(void 0);
  }

  toggleSubjectStatus(id: string): Observable<Subject> {
    const index = this.mockSubjects.findIndex(s => s.id === id);
    if (index !== -1) {
      this.mockSubjects[index].active = !this.mockSubjects[index].active;
      return of(this.mockSubjects[index]);
    }
    throw new Error('Asignatura no encontrada');
  }

  // Métodos para manejo de usuarios en asignaturas

  getSubjectUsers(subjectId: string): Observable<SubjectUsersResponse> {
    // En un entorno real: return this.http.get<SubjectUsersResponse>(`${this.apiUrl}/subjects/${subjectId}/users`);
    if (this.mockUsers[subjectId]) {
      return of(this.mockUsers[subjectId]);
    }
    
    // Si no existe, crear una entrada vacía para esta asignatura
    this.mockUsers[subjectId] = {
      assignedUsers: [],
      availableUsers: [
        { id: '4', name: 'Laura Pérez', email: 'laura@example.com', role: 'student' },
        { id: '5', name: 'David Sánchez', email: 'david@example.com', role: 'student' },
        { id: '6', name: 'Profesora Rodríguez', email: 'rodriguez@example.com', role: 'teacher' },
        { id: '7', name: 'Profesor Gómez', email: 'gomez@example.com', role: 'teacher' }
      ]
    };
    
    return of(this.mockUsers[subjectId]);
  }

  updateSubjectUsers(subjectId: string, assignedUsers: User[]): Observable<User[]> {
    // En un entorno real: return this.http.put<User[]>(`${this.apiUrl}/subjects/${subjectId}/users`, assignedUsers);
    
    // Actualizar la lista de usuarios asignados en los datos mock
    if (this.mockUsers[subjectId]) {
      this.mockUsers[subjectId].assignedUsers = [...assignedUsers];
      
      // Actualizar los contadores de la asignatura
      const index = this.mockSubjects.findIndex(s => s.id === subjectId);
      if (index !== -1) {
        this.mockSubjects[index].teacherCount = assignedUsers.filter(u => u.role === 'teacher').length;
        this.mockSubjects[index].studentCount = assignedUsers.filter(u => u.role === 'student').length;
      }
      
      return of(assignedUsers);
    }
    
    throw new Error('Asignatura no encontrada');
  }

  createUser(user: Partial<User>): Observable<User> {
    // En un entorno real: return this.http.post<User>(`${this.apiUrl}/users`, user);
    const newUser: User = {
      id: Date.now().toString(),
      name: user.name || '',
      email: user.email || '',
      role: user.role || 'student'
    };
    
    // Agregar el nuevo usuario a la lista de disponibles para todas las asignaturas
    Object.keys(this.mockUsers).forEach(subjectId => {
      this.mockUsers[subjectId].availableUsers.push({ ...newUser });
    });
    
    return of(newUser);
  }
}
