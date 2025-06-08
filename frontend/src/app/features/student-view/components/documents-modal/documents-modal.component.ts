import { Component, Input, OnChanges, SimpleChanges, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentTopic, DocumentUI, DocumentAdapter } from '../../interfaces/document.interface';
import { ChatService } from '../../../../core/services/chat.service';
import { DocumentService } from '../../../../core/services/document.service';

@Component({
  selector: 'app-documents-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="documents-drawer" [class.show]="isVisible">
      <div class="drawer-content">
        <div class="drawer-header">
          <h2>Documentos</h2>
        </div>
        
        <div class="topics-container">
          <div *ngIf="filteredTopics.length > 0; else noDocuments">
            <div *ngFor="let topic of filteredTopics" class="topic-section">
              <h3>{{topic.name}}</h3>
              <div class="documents-list">
                <div *ngFor="let doc of topic.documents" class="document-card">
                  <div class="document-icon" [class]="doc.type">
                    <svg *ngIf="doc.type === 'pdf'" width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M20 2H8C6.9 2 6 2.9 6 4V16C6 17.1 6.9 18 8 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H8V4H20V16ZM4 6H2V20C2 21.1 2.9 22 4 22H18V20H4V6ZM16 12V9C16 8.45 15.55 8 15 8H13V13H15C15.55 13 16 12.55 16 12ZM14 9H15V12H14V9ZM18 11H19V10H18V9H19V8H17V13H18V11ZM10 11H11C11.55 11 12 10.55 12 10V9C12 8.45 11.55 8 11 8H9V13H10V11ZM10 9H11V10H10V9Z" fill="currentColor"/>
                    </svg>
                    <svg *ngIf="doc.type === 'image'" width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="currentColor"/>
                    </svg>
                  </div>
                  <div class="document-info">
                    <span class="document-title">{{doc.title}}</span>
                    <span class="document-date">{{doc.uploadDate | date:'mediumDate'}}</span>
                  </div>
                  <button class="download-btn" (click)="downloadDocument(doc)">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <ng-template #noDocuments>
            <div class="no-documents">
              <p>No hay documentos disponibles para esta asignatura</p>
            </div>
          </ng-template>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .documents-drawer {
      position: fixed;
      top: 64px; // Altura del header
      right: -350px;
      width: 350px;
      height: calc(100vh - 64px); // Restar la altura del header
      background: white;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      z-index: 100; // Reducido para estar debajo del header

      &.show {
        right: 0;
      }

      .drawer-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        background-color: #ffffff;
        border-left: 1px solid #e0e0e0;
      }

      .drawer-header {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        padding: 1rem;
        background-color: #c5e99b;
        border-bottom: 1px solid #8FBC94;

        h2 {
          color: #3f6464;
          margin: 0;
          font-size: 1.2rem;
          font-weight: 500;
          text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
        }
      }

      .topics-container {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;

        .topic-section {
          margin-bottom: 1.5rem;

          h3 {
            color: #3f6464;
            margin: 0 0 0.75rem 0;
            font-size: 1.1rem;
            font-weight: 500;
            padding: 0 0.5rem;
          }
        }

        .documents-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .document-card {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 0.5rem;
          transition: all 0.2s ease;
          cursor: pointer;

          &:hover {
            border-color: #c5e99b;
            background-color: #f8fff8;
            transform: translateX(-4px);
          }

          .document-icon {
            width: 36px;
            height: 36px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.75rem;
            flex-shrink: 0;

            &.pdf {
              color: #e74c3c;
              background-color: #fde9e7;
            }

            &.image {
              color: #3498db;
              background-color: #e8f4fc;
            }
          }

          .document-info {
            flex: 1;
            min-width: 0;

            .document-title {
              display: block;
              font-weight: 500;
              color: #3f6464;
              margin-bottom: 0.25rem;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .document-date {
              font-size: 0.8rem;
              color: #666;
            }
          }

          .download-btn {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: none;
            background-color: rgba(143, 188, 148, 0.1);
            color: #3f6464;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            margin-left: 0.5rem;
            flex-shrink: 0;

            &:hover {
              background-color: #c5e99b;
              transform: translateY(-2px);
            }

            &:active {
              transform: translateY(0);
            }
          }
        }
      }
    }
    
    .no-documents {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 200px;
      color: #666;
      font-size: 0.9rem;
      text-align: center;
      
      p {
        margin: 0;
      }
    }
  `]
})
export class DocumentsModalComponent implements OnChanges, OnInit {
  @Input() isVisible = false;
  @Input() currentSubjectId: string | undefined;
  
  private chatService = inject(ChatService);
  private documentService = inject(DocumentService);
  
  // Documentos filtrados según la asignatura actual
  filteredTopics: DocumentTopic[] = [];
  documentTopics: DocumentTopic[] = [];
  loading = false;
  error: string | null = null;

  ngOnInit(): void {
    // Cargar todos los documentos al inicio
    this.loadAllDocuments();
  }

  ngOnChanges(changes: SimpleChanges): void {
    // Si cambia el subject_id y está definido, cargar documentos específicos
    if (changes['currentSubjectId'] && this.currentSubjectId) {
      this.loadSubjectDocuments(Number(this.currentSubjectId));
    } else {
      // Si no hay ID de asignatura, filtrar con los datos existentes
      this.filterDocuments();
    }
  }

  // Método para cargar todos los documentos al inicio
  private loadAllDocuments(): void {
    // Por ahora, si no tenemos una forma de obtener todos los documentos,
    // podemos usar los datos de ejemplo hasta que se seleccione una asignatura
    this.documentTopics = this.getExampleDocuments();
    this.filterDocuments();
  }

  // Método para cargar documentos de una asignatura específica
  loadSubjectDocuments(subjectId: number): void {
    this.loading = true;
    this.error = null;
    
    this.chatService.getSubjectDocuments(subjectId).subscribe({
      next: (response) => {
        if (response.data && Array.isArray(response.data)) {
          // Convertir los documentos de la API al formato de la UI
          const documents = response.data.map(doc => DocumentAdapter.toDocumentUI(doc));
          
          // Agrupar por asignatura
          const subjectName = documents.length > 0 ? documents[0].topic : 'Sin asignatura';
          
          // Crear un único tema con todos los documentos de la asignatura
          this.documentTopics = [{
            name: subjectName,
            documents: documents
          }];
          
          this.filteredTopics = [...this.documentTopics];
        } else {
          this.documentTopics = [];
          this.filteredTopics = [];
        }
        
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar documentos:', error);
        this.error = 'Error al cargar los documentos';
        this.loading = false;
        this.filteredTopics = [];
      }
    });
  }

  // Método para filtrar documentos según la asignatura actual
  filterDocuments(): void {
    // Si no hay asignatura seleccionada, mostrar todos los documentos
    if (!this.currentSubjectId) {
      this.filteredTopics = [...this.documentTopics];
      return;
    }

    const subjectId = Number(this.currentSubjectId);
    
    // En lugar de filtrar localmente, cargamos desde el servidor
    this.loadSubjectDocuments(subjectId);
  }

  // Datos de ejemplo para mostrar antes de cargar desde la API
  private getExampleDocuments(): DocumentTopic[] {
    return [
      {
        name: 'Documentos',
        documents: [
          {
            id: '1',
            title: 'Selecciona una asignatura para ver sus documentos',
            topic: 'Instrucciones',
            type: 'pdf',
            url: '',
            uploadDate: new Date()
          }
        ]
      }
    ];
  }

  async downloadDocument(doc: DocumentUI): Promise<void> {
    // Use the DocumentService to download the document by ID
    if (doc.id) {
      try {
        await this.documentService.downloadDocument(Number(doc.id));
        console.log('Document download initiated for:', doc.title);
      } catch (error) {
        console.error('Error downloading document:', error);
      }
    } else {
      console.log('Document ID not available for download:', doc.title);
    }
  }
}
