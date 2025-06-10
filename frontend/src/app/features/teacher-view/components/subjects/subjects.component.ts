import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, ParamMap, RouterModule } from '@angular/router';
import { SubjectService as CoreSubjectService, StudentAnalysisRequest } from '../../../../core/services/subject.service';
import { SubjectService } from '../../../../services/subject.service';
import { AuthService } from '../../../../services/auth.service';
import { DocumentService } from '../../../../core/services/document.service';
import { UploadDocumentModalComponent } from '../../../../shared/components/upload-document-modal/upload-document-modal.component';

interface Student {
  id: string;
  name: string;
  email: string;
}

interface Topic {
  id: string;
  name: string;
  description: string;
  documentCount: number;
}

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: Date;
  topicId: string;
}

@Component({
  selector: 'app-subjects',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule, UploadDocumentModalComponent],
  templateUrl: './subjects.component.html',
  styleUrl: './subjects.component.scss'
})
export class SubjectsComponent implements OnInit {
  // ViewChild para el modal de subir documentos
  @ViewChild(UploadDocumentModalComponent) uploadModal!: UploadDocumentModalComponent;
  
  // Asignatura seleccionada actualmente
  subject: any = null;
  
  // Lista de asignaturas del profesor
  teacherSubjects: any[] = [];
  
  // Estado de carga
  isLoadingSubjects: boolean = false;
  isLoadingStudents: boolean = false;
  isLoadingDocuments: boolean = false;
  
  // Estado para gestión de resúmenes
  showSummaryEditor: boolean = false;
  isGeneratingSummary: boolean = false;
  isUpdatingSummary: boolean = false;
  subjectSummary: string = '';
  originalSummary: string = '';
  
  // Estado para análisis de estudiantes
  studentAnalysis: any = null;
  isGeneratingAnalysis: boolean = false;
  showAnalysisSection: boolean = false;
  analysisSettings: StudentAnalysisRequest = {
    days_back: 30,
    min_participation: 1
  };
  
  constructor(
    private route: ActivatedRoute,
    private coreSubjectService: CoreSubjectService,
    private subjectService: SubjectService,
    private authService: AuthService,
    private documentService: DocumentService
  ) {}
  
  ngOnInit(): void {
    this.loadTeacherSubjects();
    
    this.route.paramMap.subscribe((params: ParamMap) => {
      const subjectId = params.get('id');
      if (subjectId) {
        this.loadSubjectDetails(subjectId);
      } else {
        // Si no hay ID en la ruta, cargar la primera asignatura disponible
        if (this.teacherSubjects.length > 0) {
          this.loadSubjectDetails(this.teacherSubjects[0].id);
        }
      }
    });

    // Listener para recargar temas cuando se suba un documento
    window.addEventListener('document-uploaded', () => {
      if (this.subject?.id) {
        this.loadSubjectTopics(this.subject.id);
      }
    });
  }
  
  // Cargar las asignaturas del profesor actual
  private loadTeacherSubjects(): void {
    this.isLoadingSubjects = true;
    
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        const userId = user.data.id;
        this.subjectService.getSubjectsByUserId(userId.toString()).subscribe({
          next: (response) => {
            this.teacherSubjects = response.data || [];
            this.isLoadingSubjects = false;
            
            // Si hay un ID en la ruta, cargar esa asignatura
            const subjectId = this.route.snapshot.paramMap.get('id');
            if (subjectId) {
              this.loadSubjectDetails(subjectId);
            } else if (this.teacherSubjects.length > 0) {
              // Si no hay ID específico, cargar la primera asignatura
              this.loadSubjectDetails(this.teacherSubjects[0].id);
            }
          },
          error: (error) => {
            console.error('Error al cargar asignaturas del profesor:', error);
            this.isLoadingSubjects = false;
          }
        });
      },
      error: (error) => {
        console.error('Error al obtener usuario actual:', error);
        this.isLoadingSubjects = false;
      }
    });
  }
  
  loadSubjectDetails(subjectId: string): void {
    // Buscar la asignatura en la lista del profesor
    const foundSubject = this.teacherSubjects.find(s => s.id === subjectId);
    if (foundSubject) {
      this.subject = {
        ...foundSubject,
        description: foundSubject.description || 'Sin descripción disponible'
      };
      
      // Cargar estudiantes de la asignatura desde el backend
      this.loadSubjectStudents(subjectId);
      
      // Cargar temas específicos de la asignatura desde el backend
      this.loadSubjectTopics(subjectId);
      
      // Resetear estados
      this.selectedTopicId = null;
      this.searchTerm = '';
    }
  }

  // Cargar temas de una asignatura específica
  private loadSubjectTopics(subjectId: string): void {
    console.log('Cargando temas para la asignatura:', subjectId);
    
    this.coreSubjectService.getTopicsBySubject(subjectId).subscribe({
      next: (response) => {
        console.log('Respuesta del servicio de temas:', response);
        
        if (response.data) {
          this.topics = response.data.map((topic: any) => ({
            id: topic.id.toString(),
            name: topic.name,
            description: topic.description || 'Sin descripción',
            documentCount: topic.documentCount || 0
          }));
          console.log('Temas cargados:', this.topics);
        } else {
          console.log('No se encontraron temas en la respuesta');
          this.topics = [];
        }
      },
      error: (error) => {
        console.error('Error al cargar temas de la asignatura:', error);
        this.topics = [];
      }
    });
  }
  
  // Cargar estudiantes de una asignatura específica
  private loadSubjectStudents(subjectId: string): void {
    this.isLoadingStudents = true;
    console.log('Cargando estudiantes para la asignatura:', subjectId);
    
    this.coreSubjectService.getSubjectUsers(subjectId).subscribe({
      next: (response) => {
        console.log('Respuesta del servicio de usuarios de asignatura:', response);
        
        // La respuesta del backend tiene la estructura: response.data.students
        if (response.data && response.data.students) {
          console.log('Estudiantes encontrados:', response.data.students);
          this.students = response.data.students.map((user: any) => ({
            id: user.id.toString(),
            name: user.full_name,
            email: user.email
          }));
          console.log('Estudiantes filtrados:', this.students);
        } else {
          console.log('No se encontraron estudiantes en la respuesta');
          this.students = [];
        }
        this.isLoadingStudents = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes de la asignatura:', error);
        this.students = [];
        this.isLoadingStudents = false;
      }
    });  }

  // Cargar documentos de un tema específico
  private loadDocumentsByTopic(topicId: number): void {
    this.isLoadingDocuments = true;
    console.log('Cargando documentos para el tema:', topicId);
    
    this.documentService.getDocumentsByTopic(topicId).subscribe({
      next: (response) => {
        console.log('Respuesta del servicio de documentos por tema:', response);
        
        if (response.data) {
          this.documents = response.data.map((doc: any) => ({
            id: doc.id.toString(),
            name: doc.title,
            type: 'PDF',
            size: 'N/A', // El backend no devuelve el tamaño
            uploadDate: new Date(doc.created_at || Date.now()),
            topicId: doc.topic_id?.toString() || ''
          }));
          console.log('Documentos cargados:', this.documents);
        } else {
          console.log('No se encontraron documentos en la respuesta');
          this.documents = [];
        }
        this.isLoadingDocuments = false;
      },
      error: (error) => {
        console.error('Error al cargar documentos del tema:', error);
        this.documents = [];
        this.isLoadingDocuments = false;
      }
    });
  }

  // Referencias a los arrays activos según la asignatura seleccionada
  students: Student[] = [];
  topics: Topic[] = [];
  
  // Referencia actual a los documentos del tema seleccionado
  documents: Document[] = [];
  
  // Estado de la UI
  selectedTopicId: string | null = null;
  searchTerm: string = '';
  newTopicName: string = '';
  newTopicDescription: string = '';
  showNewTopicForm: boolean = false;
  showUploadForm: boolean = false;
  
  // Variables para edición de temas
  editingTopicId: string | null = null;
  editTopicName: string = '';
  editTopicDescription: string = '';
  
  // ID del tema seleccionado para subir documentos
  selectedTopicForUpload: string | null = null;
  
  // Métodos de la UI
  selectTopic(topicId: string): void {
    this.selectedTopicId = topicId;
    this.loadDocumentsByTopic(parseInt(topicId));
  }
  
  toggleNewTopicForm(): void {
    this.showNewTopicForm = !this.showNewTopicForm;
    if (!this.showNewTopicForm) {
      this.newTopicName = '';
      this.newTopicDescription = '';
    }
  }
  
  addNewTopic(): void {
    if (this.newTopicName.trim() && this.subject?.id) {
      const topicData = {
        name: this.newTopicName,
        description: this.newTopicDescription || '',
        subject_id: parseInt(this.subject.id)
      };

      this.coreSubjectService.createTopic(topicData).subscribe({
        next: (response) => {
          console.log('Tema creado exitosamente:', response);
          
          // Recargar la lista de temas
          this.loadSubjectTopics(this.subject.id);
          
          // Cerrar el formulario
          this.toggleNewTopicForm();
        },
        error: (error) => {
          console.error('Error al crear el tema:', error);
        }
      });
    }
  }

  // Métodos para editar tema
  startEditTopic(topic: Topic): void {
    this.editingTopicId = topic.id;
    this.editTopicName = topic.name;
    this.editTopicDescription = topic.description;
  }

  cancelEditTopic(): void {
    this.editingTopicId = null;
    this.editTopicName = '';
    this.editTopicDescription = '';
  }

  saveEditTopic(): void {
    if (this.editingTopicId && this.editTopicName.trim()) {
      const topicData = {
        name: this.editTopicName,
        description: this.editTopicDescription || ''
      };

      this.coreSubjectService.updateTopic(parseInt(this.editingTopicId), topicData).subscribe({
        next: (response) => {
          console.log('Tema editado exitosamente:', response);
          
          // Recargar la lista de temas
          this.loadSubjectTopics(this.subject.id);
          
          // Cerrar el formulario de edición
          this.cancelEditTopic();
        },
        error: (error) => {
          console.error('Error al editar el tema:', error);
        }
      });
    }
  }

  // Método para eliminar tema
  deleteTopic(topic: Topic): void {
    if (confirm(`¿Está seguro de que desea eliminar el tema "${topic.name}"? Esta acción no se puede deshacer.`)) {
      this.coreSubjectService.deleteTopic(parseInt(topic.id)).subscribe({
        next: (response) => {
          console.log('Tema eliminado exitosamente:', response);
          
          // Si el tema eliminado era el seleccionado, limpiar selección
          if (this.selectedTopicId === topic.id) {
            this.selectedTopicId = null;
            this.documents = [];
          }
          
          // Recargar la lista de temas
          this.loadSubjectTopics(this.subject.id);
        },
        error: (error) => {
          console.error('Error al eliminar el tema:', error);
        }
      });
    }
  }
  
  toggleUploadForm(): void {
    this.showUploadForm = !this.showUploadForm;
  }
  
  uploadDocument(topicId: string): void {
    // Guardar el ID del tema seleccionado
    this.selectedTopicForUpload = topicId;
    
    // Abrir el modal de subir documentos
    this.openUploadModal();
  }

  // Método para abrir el modal de subir documentos
  openUploadModal(): void {
    if (this.uploadModal && this.subject?.id) {
      this.uploadModal.open(this.selectedTopicForUpload || undefined, this.subject.id);
    }
  }
  
  getFilteredStudents(): Student[] {
    if (!this.searchTerm.trim()) return this.students;
    
    return this.students.filter(student => 
      student.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      student.email.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  // Métodos para gestión de resúmenes de asignatura
  toggleSummaryEditor(): void {
    this.showSummaryEditor = !this.showSummaryEditor;
    if (this.showSummaryEditor) {
      this.originalSummary = this.subject?.summary || '';
      this.subjectSummary = this.originalSummary;
    }
  }

  generateSummary(): void {
    if (!this.subject?.id) return;
    
    this.isGeneratingSummary = true;
    this.documentService.generateSubjectSummary(parseInt(this.subject.id)).subscribe({
      next: (response) => {
        if (response.data?.summary) {
          this.subjectSummary = response.data.summary;
          this.subject.summary = response.data.summary;
          // NO actualizar originalSummary para que el botón "Guardar" se active
        }
        this.isGeneratingSummary = false;
      },
      error: (error) => {
        console.error('Error generando resumen:', error);
        this.isGeneratingSummary = false;
      }
    });
  }

  saveSummary(): void {
    if (!this.subject?.id || !this.subjectSummary.trim()) return;
    
    this.isUpdatingSummary = true;
    this.documentService.updateSubjectSummary(parseInt(this.subject.id), this.subjectSummary).subscribe({
      next: (response) => {
        if (response.data?.updated) {
          this.subject.summary = this.subjectSummary;
          this.originalSummary = this.subjectSummary;
          this.showSummaryEditor = false;
        }
        this.isUpdatingSummary = false;
      },
      error: (error) => {
        console.error('Error actualizando resumen:', error);
        this.isUpdatingSummary = false;
      }
    });
  }

  cancelSummaryEdit(): void {
    this.subjectSummary = this.originalSummary;
    this.showSummaryEditor = false;
  }

  hasSummaryChanged(): boolean {
    return this.subjectSummary !== this.originalSummary;
  }

  // Métodos para análisis de estudiantes
  toggleAnalysisSection(): void {
    this.showAnalysisSection = !this.showAnalysisSection;
    if (this.showAnalysisSection && !this.studentAnalysis) {
      this.generateStudentAnalysis();
    }
  }

  generateStudentAnalysis(): void {
    if (!this.subject?.id) return;

    this.isGeneratingAnalysis = true;
    this.coreSubjectService.generateStudentAnalysis(
      parseInt(this.subject.id), 
      this.analysisSettings
    ).subscribe({
      next: (response) => {
        this.studentAnalysis = response.data;
        this.isGeneratingAnalysis = false;
      },
      error: (error) => {
        console.error('Error al generar análisis de estudiantes:', error);
        this.isGeneratingAnalysis = false;
        
        // Mostrar mensaje específico dependiendo del tipo de error
        let errorMessage = 'Error al generar el análisis. Por favor, inténtelo de nuevo.';
        
        if (error.status === 404) {
          errorMessage = 'No se encontraron mensajes de estudiantes para analizar en el período especificado. Intente ampliar el rango de días o verificar que los estudiantes estén participando.';
        } else if (error.status === 500) {
          errorMessage = 'Error interno del servidor al generar el análisis. Por favor, contacte al administrador si el problema persiste.';
        }
        
        alert(errorMessage);
      }
    });
  }

  refreshAnalysis(): void {
    this.studentAnalysis = null;
    this.generateStudentAnalysis();
  }

  updateAnalysisSettings(): void {
    if (this.studentAnalysis) {
      this.refreshAnalysis();
    }
  }

  formatParticipationRate(rate: number): string {
    return `${(rate * 100).toFixed(1)}%`;
  }

  formatAnalysisDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
