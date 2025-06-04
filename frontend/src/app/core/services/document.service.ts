import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { Document } from '../models/document.model';
import { ApiResponse } from '../models/api-response.model';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private api = inject(ApiService);

  getDocuments(): Observable<ApiResponse<Document[]>> {
    return this.api.get<Document[]>('documents/list');
  }

  getDocumentById(documentId: number): Observable<ApiResponse<Document>> {
    return this.api.get<Document>(`documents/${documentId}`);
  }

  uploadDocument(title: string, description: string, file: File, subjectId: string, topicId?: string): Observable<ApiResponse<Document>> {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('pdf_file', file);
    formData.append('subject_id', subjectId);
    
    if (topicId) {
      formData.append('topic_id', topicId);
    }
    
    return this.api.upload<Document>('documents/upload', formData);
  }

  deleteDocument(documentId: number): Observable<ApiResponse<any>> {
    return this.api.delete(`documents/${documentId}`);
  }

  // Métodos para gestión de resúmenes de asignaturas
  generateSubjectSummary(subjectId: number): Observable<ApiResponse<{summary: string}>> {
    return this.api.post<{summary: string}>(`documents/subjects/${subjectId}/summary`, {});
  }

  updateSubjectSummary(subjectId: number, summary: string): Observable<ApiResponse<{updated: boolean}>> {
    const formData = new FormData();
    formData.append('new_summary', summary);
    return this.api.put<{updated: boolean}>(`documents/subjects/${subjectId}/summary`, formData);
  }

  getDocumentsByTopic(topicId: number): Observable<ApiResponse<Document[]>> {
    return this.api.get<Document[]>(`documents/topic/${topicId}`);
  }
}
