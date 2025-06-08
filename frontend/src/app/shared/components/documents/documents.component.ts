import { Component, Input, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../../core/services/document.service';
import { Document } from '../../../core/models/document.model';
import { SubjectService } from '../../../core/services/subject.service';
import { Subject } from '../../../core/services/subject.service';
import { ChatService } from '../../../core/services/chat.service';
import { UploadDocumentModalComponent } from '../upload-document-modal/upload-document-modal.component';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule, FormsModule, UploadDocumentModalComponent],
  templateUrl: './documents.component.html',
  styleUrls: ['./documents.component.scss']
})
export class DocumentsComponent implements OnInit, OnDestroy {
  @Input() isAdminView = false;
  
  searchQuery: string = '';
  selectedSubject: string = 'Todas';
  documents: Document[] = [];
  isLoading = false;
  error: string | null = null;

  subjects: Subject[] = [];

  constructor(
    private documentService: DocumentService,
    private subjectService: SubjectService,
    private chatService: ChatService
  ) {}

  ngOnInit() {
    this.loadSubjects();
    this.loadDocuments();
    
    // Escuchar evento de documento subido para recargar la lista
    this.documentUploadedListener = () => {
      this.loadDocuments();
    };
    window.addEventListener('document-uploaded', this.documentUploadedListener);
  }
  
  ngOnDestroy(): void {
    // Limpiar el event listener al destruir el componente
    if (this.documentUploadedListener) {
      window.removeEventListener('document-uploaded', this.documentUploadedListener);
    }
  }

  loadDocuments() {
    this.isLoading = true;
    this.error = null;

    // Usamos directamente el DocumentService ya que apunta al endpoint correcto
    this.documentService.getDocuments().subscribe({
      next: (response) => {
        if (response.data) {
          this.documents = response.data.map(doc => ({
            ...doc,
            type: doc.type ? doc.type : 'pdf',
            uploadDate: doc.created_at ? new Date(doc.created_at) : new Date(),
            subject: this.getSubjectNameById(doc.subject_id),
            size: '1.2 MB', // Por defecto si no viene del API
            status: 'Procesado' // Por defecto si no viene del API
          }));
        }
        this.isLoading = false;
      },
      error: (error) => {
        this.error = 'Error al cargar los documentos. Por favor, intente nuevamente.';
        this.isLoading = false;
        console.error('Error loading documents:', error);
      }
    });
  }

  loadSubjects() {
    this.subjectService.getSubjects().subscribe({
      next: (response) => {
        if (response.data) {
          this.subjects = response.data;
        }
      },
      error: (error) => {
        console.error('Error loading subjects:', error);
      }
    });
  }

  getFileExtension(type: string | null | undefined): string {
    return type ? type.toUpperCase() : '';
  }

  getStatusClass(status: string): string {
    switch(status.toLowerCase()) {
      case 'procesado':
        return 'status-processed';
      case 'procesando':
        return 'status-processing';
      case 'error':
        return 'status-error';
      default:
        return '';
    }
  }

  @ViewChild(UploadDocumentModalComponent) uploadModal!: UploadDocumentModalComponent;
  private documentUploadedListener: any;

  openUploadModal(): void {
    this.uploadModal.open();
  }

  deleteDocument(id: number): void {
    if (confirm('¿Está seguro de que desea eliminar este documento?')) {
      this.documentService.deleteDocument(id).subscribe({
        next: () => {
          this.documents = this.documents.filter(doc => doc.id !== id);
        },
        error: (error) => {
          this.error = 'Error al eliminar el documento. Por favor, intente nuevamente.';
          console.error('Error deleting document:', error);
        }
      });
    }
  }

  getFilteredDocuments(): Document[] {
    return this.documents.filter(doc => {
      // Filtro por asignatura
      const matchesSubject = this.selectedSubject === 'Todas' || this.getSubjectNameById(doc.subject_id) === this.selectedSubject;
      
      // Filtro por búsqueda (título o asignatura)
      const matchesSearch = this.searchQuery === '' || 
        doc.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        doc.subject.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      return matchesSubject && matchesSearch;
    });
  }

  getSubjectNameById(subjectId: number | string): string {
    const subject = this.subjects.find(s => s.id == subjectId);
    return subject ? subject.name : '—';
  }

  async downloadDocument(documentId: number): Promise<void> {
    try {
      await this.documentService.downloadDocument(documentId);
      console.log('Document download initiated');
    } catch (error) {
      this.error = 'Error al descargar el documento. Por favor, intente nuevamente.';
      console.error('Error downloading document:', error);
    }
  }
}
