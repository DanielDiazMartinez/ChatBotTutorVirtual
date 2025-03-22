import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';

// Interfaces
export interface Message {
  id: number;
  text: string;
  is_bot: boolean;
  created_at: string;
  conversation_id: number;
}

export interface Conversation {
  id: number;
  student_id: number;
  document_id: number;
  created_at: string;
  messages?: Message[];
}

export interface Document {
  id: number;
  title: string;
  description: string;
  file_path: string;
  teacher_id: number;
  created_at: string;
}

export interface Student {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface Teacher {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DummyDataService {
  private documents: Document[] = [
    {
      id: 1,
      title: 'Introducción a la Inteligencia Artificial',
      description: 'Conceptos básicos y fundamentos de la IA',
      file_path: '/uploads/1/intro_ia.pdf',
      teacher_id: 1,
      created_at: '2025-01-15T09:30:00Z'
    },
    {
      id: 2,
      title: 'Machine Learning Avanzado',
      description: 'Técnicas y algoritmos avanzados de ML',
      file_path: '/uploads/1/ml_avanzado.pdf',
      teacher_id: 1,
      created_at: '2025-01-20T14:45:00Z'
    },
    {
      id: 3,
      title: 'Procesamiento de Lenguaje Natural',
      description: 'Fundamentos y aplicaciones de NLP',
      file_path: '/uploads/2/nlp_fundamentos.pdf',
      teacher_id: 2,
      created_at: '2025-02-05T11:20:00Z'
    }
  ];

  private conversations: Conversation[] = [
    {
      id: 1,
      student_id: 1,
      document_id: 1,
      created_at: '2025-03-10T08:30:00Z'
    },
    {
      id: 2,
      student_id: 1,
      document_id: 2,
      created_at: '2025-03-12T10:15:00Z'
    },
    {
      id: 3,
      student_id: 2,
      document_id: 1,
      created_at: '2025-03-15T14:20:00Z'
    }
  ];

  private messages: Message[] = [
    {
      id: 1,
      conversation_id: 1,
      text: '¿Qué es exactamente la inteligencia artificial?',
      is_bot: false,
      created_at: '2025-03-10T08:31:00Z'
    },
    {
      id: 2,
      conversation_id: 1,
      text: 'La inteligencia artificial (IA) es la simulación de procesos de inteligencia humana por parte de máquinas, especialmente sistemas informáticos. Estos procesos incluyen el aprendizaje (la adquisición de información y reglas para usar la información), el razonamiento (usar las reglas para llegar a conclusiones aproximadas o definitivas) y la autocorrección.',
      is_bot: true,
      created_at: '2025-03-10T08:31:30Z'
    },
    {
      id: 3,
      conversation_id: 1,
      text: '¿Cuáles son las principales áreas de la IA?',
      is_bot: false,
      created_at: '2025-03-10T08:32:45Z'
    },
    {
      id: 4,
      conversation_id: 1,
      text: 'Las principales áreas de la IA incluyen: Machine Learning (aprendizaje automático), Neural Networks (redes neuronales), Natural Language Processing (procesamiento del lenguaje natural), Robotics (robótica), Expert Systems (sistemas expertos), y Computer Vision (visión por computadora). Cada una de estas áreas tiene aplicaciones específicas y métodos de implementación.',
      is_bot: true,
      created_at: '2025-03-10T08:33:15Z'
    }
    // Puedes añadir más mensajes para otras conversaciones
  ];

  private students: Student[] = [
    {
      id: 1,
      email: 'estudiante1@example.com',
      full_name: 'Ana García',
      created_at: '2025-01-05T10:00:00Z'
    },
    {
      id: 2,
      email: 'estudiante2@example.com',
      full_name: 'Carlos López',
      created_at: '2025-01-07T11:30:00Z'
    }
  ];

  private teachers: Teacher[] = [
    {
      id: 1,
      email: 'profesor1@example.com',
      full_name: 'Dr. Martínez',
      created_at: '2024-12-15T09:00:00Z'
    },
    {
      id: 2,
      email: 'profesor2@example.com',
      full_name: 'Dra. Rodríguez',
      created_at: '2024-12-20T14:30:00Z'
    }
  ];

  constructor() { }

  // Métodos para obtener datos simulando llamadas API
  getDocuments(): Observable<Document[]> {
    return of(this.documents).pipe(delay(800)); // Simular latencia de red
  }

  getDocument(id: number): Observable<Document | undefined> {
    const document = this.documents.find(doc => doc.id === id);
    return of(document).pipe(delay(500));
  }

  getConversations(studentId?: number): Observable<Conversation[]> {
    let filteredConversations = this.conversations;
    if (studentId) {
      filteredConversations = this.conversations.filter(conv => conv.student_id === studentId);
    }
    return of(filteredConversations).pipe(delay(700));
  }

  getConversation(id: number): Observable<Conversation | undefined> {
    const conversation = this.conversations.find(conv => conv.id === id);
    if (conversation) {
      // Clonar para no modificar el original
      const result = {...conversation};
      // Añadir mensajes
      result.messages = this.messages.filter(msg => msg.conversation_id === id);
      return of(result).pipe(delay(600));
    }
    return of(undefined).pipe(delay(500));
  }

  getStudents(): Observable<Student[]> {
    return of(this.students).pipe(delay(500));
  }

  getStudent(id: number): Observable<Student | undefined> {
    const student = this.students.find(s => s.id === id);
    return of(student).pipe(delay(400));
  }

  getTeachers(): Observable<Teacher[]> {
    return of(this.teachers).pipe(delay(500));
  }

  getTeacher(id: number): Observable<Teacher | undefined> {
    const teacher = this.teachers.find(t => t.id === id);
    return of(teacher).pipe(delay(400));
  }

  // Método para agregar un mensaje (simula post a la API)
  addMessage(conversationId: number, text: string, isBot: boolean): Observable<Message> {
    const newMessage: Message = {
      id: Math.max(...this.messages.map(m => m.id)) + 1,
      conversation_id: conversationId,
      text: text,
      is_bot: isBot,
      created_at: new Date().toISOString()
    };
    
    this.messages.push(newMessage);
    return of(newMessage).pipe(delay(300));
  }

  // Método para simular respuesta del bot
  generateBotResponse(question: string): string {
    const responses = [
      "Según los documentos disponibles, este concepto se refiere principalmente a...",
      "La literatura académica sugiere varias interpretaciones para esta pregunta. Lo más aceptado es...",
      "Esta es una pregunta importante en el campo. Basándonos en el material, podemos decir que...",
      "De acuerdo con el documento, hay varios factores que influyen en este fenómeno...",
      "Los expertos en esta área generalmente coinciden en que...",
      "Este es un tema complejo con múltiples dimensiones. En resumen, podemos destacar que..."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }
}