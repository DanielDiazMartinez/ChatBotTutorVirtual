// src/app/features/dashboard/content-area/chat-area/chat-area.component.ts
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MessageListComponent } from './message-list/message-list.component';
import { MessageInputComponent } from './message-input/message-input.component';

interface Message {
  id: number;
  text: string;
  is_bot: boolean;
  created_at: string;
}

@Component({
  selector: 'app-chat-area',
  standalone: true,
  imports: [CommonModule, MessageListComponent, MessageInputComponent],
  templateUrl: './chat-area.component.html',
  styleUrls: ['./chat-area.component.scss']
})
export class ChatAreaComponent implements OnChanges {
  @Input() conversationId: number | null = null;
  @Input() documentId: number | null = null;
  
  messages: Message[] = [];
  isLoading: boolean = false;
  
  // Datos dummy para pruebas
  dummyMessages: Message[] = [
    {
      id: 1,
      text: "Hola, tengo una pregunta sobre este documento.",
      is_bot: false,
      created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString() // 5 minutos antes
    },
    {
      id: 2,
      text: "¡Claro! Estoy aquí para ayudarte con cualquier duda sobre el material. ¿Qué te gustaría saber?",
      is_bot: true,
      created_at: new Date(Date.now() - 1000 * 60 * 4).toISOString() // 4 minutos antes
    },
    {
      id: 3,
      text: "¿Puedes explicarme mejor el concepto principal de la sección 2?",
      is_bot: false,
      created_at: new Date(Date.now() - 1000 * 60 * 3).toISOString() // 3 minutos antes
    },
    {
      id: 4,
      text: "Por supuesto. El concepto principal de la sección 2 trata sobre los fundamentos del aprendizaje automático. En esencia, es una técnica que permite a las computadoras aprender de los datos sin ser programadas explícitamente. El proceso generalmente implica: 1) recopilar datos, 2) preparar los datos, 3) elegir un modelo, 4) entrenar el modelo, 5) evaluar el modelo, y 6) ajustar el modelo según sea necesario.",
      is_bot: true,
      created_at: new Date(Date.now() - 1000 * 60 * 2).toISOString() // 2 minutos antes
    }
  ];
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['conversationId'] && this.conversationId) {
      this.loadMessages();
    }
  }
  
  loadMessages(): void {
    this.isLoading = true;
    
    // Simular carga de mensajes
    setTimeout(() => {
      this.messages = this.dummyMessages;
      this.isLoading = false;
    }, 800);
  }
  
  handleNewMessage(text: string): void {
    if (!text.trim()) return;
    
    // Añadir mensaje del usuario
    const userMessage: Message = {
      id: this.messages.length + 1,
      text: text,
      is_bot: false,
      created_at: new Date().toISOString()
    };
    
    this.messages = [...this.messages, userMessage];
    
    // Simular respuesta del bot
    setTimeout(() => {
      const botResponse: Message = {
        id: this.messages.length + 1,
        text: this.generateBotResponse(text),
        is_bot: true,
        created_at: new Date().toISOString()
      };
      
      this.messages = [...this.messages, botResponse];
    }, 1500);
  }
  
  // Genera respuestas dummy para pruebas
  generateBotResponse(question: string): string {
    const responses = [
      "Basado en el documento, puedo decir que este concepto se refiere principalmente a los fundamentos del aprendizaje automático y cómo se aplican en contextos prácticos.",
      "Según la información disponible, este tema es una parte fundamental de la inteligencia artificial moderna. El documento explica varios enfoques y metodologías relacionadas.",
      "El documento detalla este concepto en la sección 3.2. En resumen, se trata de cómo los algoritmos pueden aprender patrones a partir de datos históricos para hacer predicciones sobre nuevos datos.",
      "Esta es una pregunta interesante. El documento aborda este tema desde múltiples perspectivas, pero la idea central es que los sistemas de IA pueden mejorar su rendimiento con la experiencia.",
      "De acuerdo con el material presentado, este es un área en constante evolución. Los avances recientes han permitido aplicaciones más sofisticadas en diversos campos."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }
}