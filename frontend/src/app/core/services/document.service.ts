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

  async downloadDocument(documentId: number): Promise<void> {
    const url = `${this.api['apiUrl']}/documents/${documentId}/download`;
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      throw new Error('Authentication token not found');
    }

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error downloading file: ${response.status} ${response.statusText}`);
      }

      // Try to get filename from Content-Disposition header
      const disposition = response.headers.get('Content-Disposition');
      let filename = `document_${documentId}.pdf`;
      if (disposition) {
        const filenameMatch = disposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error downloading document:', error);
      throw error;
    }
  }

  async previewDocument(documentId: number): Promise<string> {
    const url = `${this.api['apiUrl']}/documents/${documentId}/preview`;
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      throw new Error('Authentication token not found');
    }

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error previewing file: ${response.status} ${response.statusText}`);
      }

      const blob = await response.blob();
      return window.URL.createObjectURL(blob);
    } catch (error) {
      console.error('Error previewing document:', error);
      throw error;
    }
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
