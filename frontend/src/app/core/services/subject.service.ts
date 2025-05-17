import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';
import { User } from '../models/user.model';
import { map } from 'rxjs/operators';

export interface Subject {
  id: string;
  name: string;
  code: string;
  description: string;
  teacherCount: number;
  studentCount: number;
  teachers?: any[];
  students?: any[];
}

export interface SubjectUsersResponse {
  assignedUsers: User[];
  availableUsers: User[];
}

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private api = inject(ApiService);

  // Métodos para manejo de asignaturas
  getSubjects(): Observable<ApiResponse<Subject[]>> {
    return this.api.get<any>('subjects').pipe(
      map(response => ({
        ...response,
        data: response.data.map((subject: any) => ({
          ...subject,
          teacherCount: subject.teacher_count,
          studentCount: subject.student_count
        }))
      }))
    );
  }

  getSubject(id: string): Observable<ApiResponse<Subject>> {
    return this.api.get<any>(`subjects/${id}`).pipe(
      map(response => ({
        ...response,
        data: response.data ? {
          ...response.data,
          teacherCount: response.data.teacher_count,
          studentCount: response.data.student_count
        } : response.data
      }))
    );
  }

  createSubject(subject: Partial<Subject>): Observable<ApiResponse<Subject>> {
    return this.api.post<Subject>('subjects', subject);
  }

  updateSubject(id: string, changes: Partial<Subject>): Observable<ApiResponse<Subject>> {
    return this.api.put<Subject>(`subjects/${id}`, changes);
  }

  deleteSubject(id: string): Observable<ApiResponse<void>> {
    return this.api.delete<void>(`subjects/${id}`);
  }

  // Métodos para manejo de usuarios en asignaturas
  getSubjectUsers(subjectId: string): Observable<ApiResponse<SubjectUsersResponse>> {
    return this.api.get<SubjectUsersResponse>(`subjects/${subjectId}/users`);
  }

  updateSubjectUsers(subjectId: string, assignedUsers: User[]): Observable<ApiResponse<User[]>> {
    return this.api.put<User[]>(`subjects/${subjectId}/users`, assignedUsers);
  }

  createUser(user: Partial<User>): Observable<ApiResponse<User>> {
    return this.api.post<User>('users', user);
  }

  addUsersToSubject(subjectId: number, userIds: number[]): Observable<ApiResponse<any>> {
    return this.api.post<any>(`subjects/${subjectId}/users`, { user_ids: userIds });
  }
}
