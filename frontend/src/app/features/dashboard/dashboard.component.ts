// src/app/features/dashboard/dashboard.component.ts (actualizar con la nueva importación)
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './sidebar/sidebar.component';
import { ContentAreaComponent } from './content-area/content-area.component';

// Interfaces (puedes moverlas a archivos separados después)
interface Document {
  id: number;
  title: string;
  description: string;
  file_path: string;
}

interface Conversation {
  id: number;
  document_id: number;
  created_at: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, SidebarComponent, ContentAreaComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  documents: Document[] = [];
  conversations: Conversation[] = [];
  currentDocumentId: number | null = null;
  currentConversationId: number | null = null;
  isLoading: boolean = false;

  // Datos dummy para desarrollo
  dummyDocuments: Document[] = [
    { 
      id: 1, 
      title: 'Introducción a la Inteligencia Artificial', 
      description: 'Conceptos básicos de IA',
      file_path: '/assets/docs/ia_intro.pdf'
    },
    { 
      id: 2, 
      title: 'Machine Learning Fundamentos', 
      description: 'Principios básicos de ML',
      file_path: '/assets/docs/ml_basics.pdf'
    },
    { 
      id: 3, 
      title: 'Redes Neuronales', 
      description: 'Arquitecturas de redes neuronales',
      file_path: '/assets/docs/neural_networks.pdf'
    }
  ];

  constructor() {}

  ngOnInit(): void {
    // Cargar datos iniciales
    this.loadInitialData();
  }

  loadInitialData(): void {
    // Simulando carga de datos
    this.isLoading = true;
    setTimeout(() => {
      this.documents = this.dummyDocuments;
      this.isLoading = false;
    }, 1000);
  }

  onDocumentSelected(documentId: number): void {
    this.currentDocumentId = documentId;
    // Aquí cargarías las conversaciones relacionadas con este documento
    console.log(`Documento seleccionado: ${documentId}`);
    
    // Simular carga de conversaciones
    this.conversations = this.dummyDocuments
      .filter(doc => doc.id === documentId)
      .map((_, index) => ({
        id: 100 + index,
        document_id: documentId,
        created_at: new Date(Date.now() - index * 86400000).toISOString() // Fechas diferentes
      }));
  }

  onConversationSelected(conversationId: number): void {
    this.currentConversationId = conversationId;
    console.log(`Conversación seleccionada: ${conversationId}`);
  }

  onNewConversation(): void {
    if (!this.currentDocumentId) {
      console.error('No hay documento seleccionado');
      return;
    }
    
    // Simulando creación de conversación
    const newConversation: Conversation = {
      id: Math.floor(Math.random() * 1000) + 100, // ID aleatorio
      document_id: this.currentDocumentId,
      created_at: new Date().toISOString()
    };
    
    this.conversations = [...this.conversations, newConversation];
    this.currentConversationId = newConversation.id;
    console.log(`Nueva conversación creada: ${newConversation.id}`);
  }
}