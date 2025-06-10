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
  students: any[];
  teachers: any[];
  student_count: number;
  teacher_count: number;
  total_users: number;
  subject_id: number;
  subject_name: string;
  subject_code: string;
}

// Interfaces para análisis de estudiantes
export interface StudentAnalysisStatistics {
  total_messages: number;
  unique_students: number;
  participation_rate: number;
  most_active_students: Array<{
    student_id: number;
    student_name: string;
    message_count: number;
  }>;
}

export interface StudentAnalysisSummary {
  subject_id: number;
  subject_name: string;
  analysis_summary: string;
  statistics: StudentAnalysisStatistics;
  sample_questions: string[];
  analysis_date: string;
}

export interface StudentAnalysisRequest {
  days_back?: number;
  min_participation?: number;
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

  removeUsersFromSubject(subjectId: number, userIds: number[]): Observable<ApiResponse<any>> {
    return this.api.delete<any>(`subjects/${subjectId}/users`, { user_ids: userIds });
  }

  // Método para obtener temas de una asignatura
  getTopicsBySubject(subjectId: string): Observable<ApiResponse<any[]>> {
    return this.api.get<any[]>(`topics/subject/${subjectId}`);
  }

  // Método para crear un nuevo tema
  createTopic(topic: { name: string; description: string; subject_id: number }): Observable<ApiResponse<any>> {
    return this.api.post<any>('topics', topic);
  }

  // Método para editar un tema
  updateTopic(topicId: number, topic: { name: string; description: string }): Observable<ApiResponse<any>> {
    return this.api.put<any>(`topics/${topicId}`, topic);
  }

  // Método para eliminar un tema
  deleteTopic(topicId: number): Observable<ApiResponse<any>> {
    return this.api.delete<any>(`topics/${topicId}`);
  }

  // Métodos para análisis de estudiantes
  generateStudentAnalysis(
    subjectId: number, 
    request: StudentAnalysisRequest = {}
  ): Observable<ApiResponse<StudentAnalysisSummary>> {
    return this.api.post<StudentAnalysisSummary>(`subjects/${subjectId}/analysis`, request);
  }

  getStudentStatistics(
    subjectId: number,
    daysBack: number = 30
  ): Observable<ApiResponse<StudentAnalysisStatistics>> {
    return this.api.get<StudentAnalysisStatistics>(`subjects/${subjectId}/analysis/statistics`, { days_back: daysBack });
  }
}
