import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { ApiResponse } from '../models/api-response.model';
import { Conversation, Message } from '../models/chat.model';
import { Document } from '../models/document.model';

// Interface para la respuesta específica de creación de conversación
interface ConversationWithResponse {
  conversation: Conversation;
  bot_response?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private api = inject(ApiService);

  createConversation(subjectId: number): Observable<ApiResponse<ConversationWithResponse>> {
    const payload: any = {
      subject_id: subjectId,
      text: null
    };
    
    
  return this.api.post<ConversationWithResponse>('chat/conversation', payload);
  }

  getConversationById(conversationId: number): Observable<ApiResponse<Conversation>> {
        return this.api.get<Conversation>(`conversation/${conversationId}`);
  }

  sendMessage(conversationId: number, text: string, file?: File): Observable<ApiResponse<Message>> {
    // Si hay un archivo, usamos FormData para enviar los datos
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      
      // El texto debe ser enviado como un string JSON en el campo message_data
      const messageData = JSON.stringify({ text });
      formData.append('message_data', messageData);
      
      return this.api.postFormData<Message>(`chat/c/${conversationId}`, formData);
    } else {
      // Si no hay archivo, enviamos solo el texto como message_data
      const formData = new FormData();
      formData.append('message_data', JSON.stringify({ text }));
      
      return this.api.postFormData<Message>(`chat/c/${conversationId}`, formData);
    }
  }

  getConversationMessages(conversationId: number): Observable<ApiResponse<Message[]>> {
    return this.api.get<Message[]>(`chat/conversation/${conversationId}/messages`);
  }

  getUserConversations(subjectId?: number): Observable<ApiResponse<Conversation[]>> {
    const url = subjectId 
      ? `chat/me/conversations?subject_id=${subjectId}` 
      : 'chat/me/conversations';
    return this.api.get<Conversation[]>(url);
  }
  
  deleteConversation(conversationId: number): Observable<ApiResponse<void>> {
    return this.api.delete<void>(`chat/conversation/${conversationId}`);
  }

  getSubjectDocuments(subjectId: number): Observable<ApiResponse<Document[]>> {
    return this.api.get<Document[]>(`subjects/${subjectId}/documents`);
  }
  
  getTeacherDocuments(): Observable<ApiResponse<Document[]>> {
    return this.api.get<Document[]>('documents/list');
  }
}
