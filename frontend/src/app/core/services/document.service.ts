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

  getDocumentById(documentId: number): Observable<ApiResponse<Document>> {
    return this.api.get<Document>(`documents/${documentId}`);
  }

  uploadDocument(title: string, description: string, file: File): Observable<ApiResponse<Document>> {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('pdf_file', file);
    
    return this.api.upload<Document>('documents/upload', formData);
  }

  deleteDocument(documentId: number): Observable<ApiResponse<any>> {
    return this.api.delete(`documents/${documentId}`);
  }
}
