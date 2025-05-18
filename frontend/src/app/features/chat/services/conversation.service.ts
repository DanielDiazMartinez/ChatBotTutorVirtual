import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { 
  Conversation, 
  ConversationResponse,
  SingleConversationResponse,
  ConversationWithBotResponse,
  MessagePairResponse
} from '../interfaces/conversation.interface';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  constructor(private http: HttpClient) {}

  /**
   * Obtiene todas las conversaciones del usuario autenticado
   */
  getUserConversations(): Observable<ConversationResponse> {
    return this.http.get<ConversationResponse>(`${environment.apiUrl}/me/conversations`);
  }

  /**
   * Obtiene una conversación específica por su ID
   */
  getConversationById(conversationId: number): Observable<SingleConversationResponse> {
    return this.http.get<SingleConversationResponse>(`${environment.apiUrl}/conversation/${conversationId}`);
  }

  /**
   * Crea una nueva conversación
   */
  createConversation(documentId: number, text: string, topicId?: number): Observable<ConversationWithBotResponse> {
    const payload = {
      document_id: documentId,
      text,
      ...(topicId && { topic_id: topicId })
    };
    return this.http.post<ConversationWithBotResponse>(`${environment.apiUrl}/conversation`, payload);
  }

  /**
   * Añade un mensaje a una conversación existente
   */
  addMessageToConversation(conversationId: number, text: string): Observable<MessagePairResponse> {
    return this.http.post<MessagePairResponse>(
      `${environment.apiUrl}/c/${conversationId}`, 
      { text }
    );
  }

  /**
   * Elimina una conversación
   */
  deleteConversation(conversationId: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/conversation/${conversationId}`);
  }
}
