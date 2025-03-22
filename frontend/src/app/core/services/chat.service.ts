import { Injectable } from '@angular/core';
import { Observable, of, switchMap, delay } from 'rxjs';
import { DummyDataService, Message, Conversation } from './dummy-data.service';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/chat'; // Cambiar por tu URL real
  private useDummyData = true; // Cambiar a false para usar la API real

  constructor(
    private http: HttpClient,
    private dummyDataService: DummyDataService
  ) { }

  getConversations(studentId?: number): Observable<Conversation[]> {
    if (this.useDummyData) {
      return this.dummyDataService.getConversations(studentId);
    }
    
    const url = studentId 
      ? `${this.apiUrl}/conversations/student/${studentId}`
      : `${this.apiUrl}/conversations`;
      
    return this.http.get<Conversation[]>(url);
  }

  getConversation(id: number): Observable<Conversation | undefined> {
    if (this.useDummyData) {
      return this.dummyDataService.getConversation(id);
    }
    
    return this.http.get<Conversation>(`${this.apiUrl}/conversation/${id}`);
  }

  createConversation(studentId: number, documentId: number, initialMessage: string): Observable<Conversation> {
    if (this.useDummyData) {
      // Simular creación de conversación
      const newId = Math.floor(Math.random() * 1000) + 100;
      const newConversation: Conversation = {
        id: newId,
        student_id: studentId,
        document_id: documentId,
        created_at: new Date().toISOString()
      };
      
      return of(newConversation).pipe(
        delay(500),
        switchMap(conv => {
          // Añadir mensaje inicial
          return this.dummyDataService.addMessage(conv.id, initialMessage, false).pipe(
            switchMap(() => {
              // Simular respuesta del bot
              const botResponse = this.dummyDataService.generateBotResponse(initialMessage);
              return this.dummyDataService.addMessage(conv.id, botResponse, true);
            }),
            switchMap(() => of(conv))
          );
        })
      );
    }
    
    return this.http.post<Conversation>(`${this.apiUrl}/conversation`, {
      student_id: studentId,
      document_id: documentId,
      text: initialMessage
    });
  }

  sendMessage(conversationId: number, text: string): Observable<Message> {
    if (this.useDummyData) {
      return this.dummyDataService.addMessage(conversationId, text, false).pipe(
        switchMap(() => {
          // Simular respuesta del bot después de un segundo
          return of(null).pipe(
            delay(1000),
            switchMap(() => {
              const botResponse = this.dummyDataService.generateBotResponse(text);
              return this.dummyDataService.addMessage(conversationId, botResponse, true);
            })
          );
        })
      );
    }
    
    return this.http.post<Message>(`${this.apiUrl}/${conversationId}/message`, {
      text,
      is_bot: false
    });
  }

  deleteConversation(id: number): Observable<any> {
    if (this.useDummyData) {
      return of({ success: true }).pipe(delay(300));
    }
    
    return this.http.delete(`${this.apiUrl}/conversation/${id}`);
  }
}