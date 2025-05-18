import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { ApiResponse } from '../models/api-response.model';
import { Conversation, Message } from '../models/chat.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private api = inject(ApiService);

  createConversation(documentId: number, text: string): Observable<ApiResponse<Conversation>> {
    return this.api.post<Conversation>('conversation', {
      document_id: documentId,
      text
    });
  }

  getConversationById(conversationId: number): Observable<ApiResponse<Conversation>> {
    return this.api.get<Conversation>(`conversation/${conversationId}`);
  }

  sendMessage(conversationId: number, text: string): Observable<ApiResponse<Message>> {
    return this.api.post<Message>(`conversation/${conversationId}/message`, {
      text
    });
  }

  getConversationMessages(conversationId: number): Observable<ApiResponse<Message[]>> {
    return this.api.get<Message[]>(`conversation/${conversationId}/messages`);
  }

  getUserConversations(): Observable<ApiResponse<Conversation[]>> {
    return this.api.get<Conversation[]>('chat/me/conversations');
  }
}
