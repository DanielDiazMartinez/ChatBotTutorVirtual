import { Component, Input, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../../core/services/document.service';
import { Document } from '../../../core/models/document.model';
import { SubjectService } from '../../../core/services/subject.service';
import { Subject } from '../../../core/services/subject.service';
import { ChatService } from '../../../core/services/chat.service';
import { UserService } from '../../../core/services/user.service';
import { User } from '../../../core/models/user.model';
import { AuthService } from '../../../services/auth.service';
import { SubjectService as TeacherSubjectService } from '../../../services/subject.service';
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
  selectedUser: string = 'Todos'; // Nuevo filtro de usuario
  documents: Document[] = [];
  isLoading = false;
  error: string | null = null;

  subjects: Subject[] = [];
  users: User[] = []; // Lista de usuarios para el filtro

  constructor(
    private documentService: DocumentService,
    private subjectService: SubjectService,
    private chatService: ChatService,
    private userService: UserService,
    private authService: AuthService,
    private teacherSubjectService: TeacherSubjectService
  ) {}

  ngOnInit() {
    this.loadSubjects();
    if (this.isAdminView) {
      this.loadUsers(); // Cargar usuarios solo en vista de administrador
    }
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
            status: 'Procesado', // Por defecto si no viene del API
            user_id: doc.user_id // Asegurar que tenemos el user_id
          }));
        }
        this.isLoading = false;
      },
      error: (error) => {
        if (error.status === 403) {
          this.error = 'No tienes permisos para acceder a estos documentos.';
        } else {
          this.error = 'Error al cargar los documentos. Por favor, intente nuevamente.';
        }
        this.isLoading = false;
        console.error('Error loading documents:', error);
      }
    });
  }

  loadSubjects() {
    if (this.isAdminView) {
      // En vista de administrador, cargar todas las asignaturas
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
    } else {
      // En vista de profesor, cargar solo las asignaturas del profesor actual
      this.authService.getCurrentUserFromBackend().subscribe({
        next: (user: any) => {
          const userId = user.data.id;
          this.teacherSubjectService.getSubjectsByUserId(userId.toString()).subscribe({
            next: (response) => {
              if (response.data) {
                // Mapear los datos para que coincidan con la interfaz Subject esperada
                this.subjects = response.data.map(subject => ({
                  id: subject.id,
                  name: subject.name,
                  code: '', // La interfaz del teacher service no tiene code
                  description: subject.description || '',
                  teacherCount: 0,
                  studentCount: 0
                }));
              }
            },
            error: (error) => {
              console.error('Error loading teacher subjects:', error);
            }
          });
        },
        error: (error) => {
          console.error('Error al obtener usuario actual:', error);
        }
      });
    }
  }

  loadUsers() {
    this.userService.getAllUsers().subscribe({
      next: (response) => {
        if (response.data) {
          this.users = response.data;
        }
      },
      error: (error) => {
        console.error('Error loading users:', error);
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
      
      // Filtro por usuario (solo en vista de administrador)
      const matchesUser = !this.isAdminView || this.selectedUser === 'Todos' || this.getUserNameById(doc.user_id) === this.selectedUser;
      
      // Filtro por búsqueda (título, asignatura o usuario en vista admin)
      const matchesSearch = this.searchQuery === '' || 
        doc.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        doc.subject.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (this.isAdminView && this.getUserNameById(doc.user_id).toLowerCase().includes(this.searchQuery.toLowerCase()));
      
      return matchesSubject && matchesUser && matchesSearch;
    });
  }

  getSubjectNameById(subjectId: number | string): string {
    const subject = this.subjects.find(s => s.id == subjectId);
    return subject ? subject.name : '—';
  }

  getUserNameById(userId: number | string): string {
    const user = this.users.find(u => u.id == userId);
    return user ? user.full_name : '—';
  }

  async downloadDocument(documentId: number): Promise<void> {
    try {
      await this.documentService.downloadDocument(documentId);
      console.log('Document download initiated');
    } catch (error: any) {
      if (error.message && error.message.includes('403')) {
        this.error = 'No tienes permisos para descargar este documento.';
      } else {
        this.error = 'Error al descargar el documento. Por favor, intente nuevamente.';
      }
      console.error('Error downloading document:', error);
    }
  }

  async previewDocument(documentId: number): Promise<void> {
    try {
      const previewUrl = await this.documentService.previewDocument(documentId);
      // Abrir el PDF en una nueva ventana/tab para previsualización
      window.open(previewUrl, '_blank');
    } catch (error: any) {
      if (error.message && error.message.includes('403')) {
        this.error = 'No tienes permisos para previsualizar este documento.';
      } else {
        this.error = 'Error al previsualizar el documento. Por favor, intente nuevamente.';
      }
      console.error('Error previewing document:', error);
    }
  }
}
