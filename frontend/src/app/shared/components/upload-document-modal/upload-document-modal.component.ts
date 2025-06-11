import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject } from '../../../core/services/subject.service';
import { SubjectService } from '../../../core/services/subject.service';
import { DocumentService } from '../../../core/services/document.service';
import { AuthService } from '../../../services/auth.service';
import { SubjectService as TeacherSubjectService } from '../../../services/subject.service';

@Component({
  selector: 'app-upload-document-modal',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './upload-document-modal.component.html',
  styleUrls: ['./upload-document-modal.component.scss']
})
export class UploadDocumentModalComponent implements OnInit {
  private fb = inject(FormBuilder);
  private subjectService = inject(SubjectService);
  private documentService = inject(DocumentService);
  private authService = inject(AuthService);
  private teacherSubjectService = inject(TeacherSubjectService);

  isVisible = false;
  isLoading = false;
  uploadError: string | null = null;
  subjects: Subject[] = [];
  topics: any[] = [];
  uploadForm!: FormGroup;
  selectedFile: File | null = null;
  fileMaxSize = 10; // MB
  currentTopicId: string | null = null;
  hideSubjectSelector = false;
  hideTopicSelector = false;

  ngOnInit(): void {
    this.initForm();
    this.loadSubjects();
  }

  initForm(): void {
    this.uploadForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      subjectId: ['', Validators.required],
      topicId: [''],
      file: [null, Validators.required]
    });
  }

  loadSubjects(): void {
    // Cargar solo las asignaturas del profesor actual
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        const userId = user.data.id;
        this.teacherSubjectService.getSubjectsByUserId(userId.toString()).subscribe({
          next: (response) => {
            if (response.data) {
              // Mapear los datos para que coincidan con la interfaz Subject esperada
              this.subjects = response.data.map((subject: any) => ({
                id: subject.id,
                name: subject.name,
                code: subject.code || '',
                description: subject.description || '',
                teacherCount: 0,
                studentCount: 0
              }));
            }
          },
          error: (error) => {
            console.error('Error cargando asignaturas del profesor:', error);
          }
        });
      },
      error: (error) => {
        console.error('Error al obtener usuario actual:', error);
      }
    });
  }

  loadTopics(subjectId: string): void {
    this.subjectService.getTopicsBySubject(subjectId).subscribe({
      next: (response) => {
        if (response.data) {
          this.topics = response.data;
        }
      },
      error: (error) => {
        console.error('Error cargando temas:', error);
      }
    });
  }

  onSubjectChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    const subjectId = selectElement.value;
    
    if (subjectId) {
      this.loadTopics(subjectId);
      // Limpiar la selección de tema cuando cambia la asignatura
      this.uploadForm.patchValue({ topicId: '' });
    } else {
      this.topics = [];
    }
  }

  onFileSelected(event: Event): void {
    const fileInput = event.target as HTMLInputElement;
    if (fileInput.files && fileInput.files.length > 0) {
      const file = fileInput.files[0];
      
      // Validar tipo de archivo (PDF)
      if (file.type !== 'application/pdf') {
        this.uploadError = 'Solo se permiten archivos PDF.';
        this.selectedFile = null;
        this.uploadForm.get('file')?.reset();
        return;
      }
      
      // Validar tamaño de archivo (máx 10MB)
      if (file.size > this.fileMaxSize * 1024 * 1024) {
        this.uploadError = `El archivo es demasiado grande. El tamaño máximo permitido es ${this.fileMaxSize}MB.`;
        this.selectedFile = null;
        this.uploadForm.get('file')?.reset();
        return;
      }
      
      this.selectedFile = file;
      this.uploadError = null;
      this.uploadForm.get('file')?.setValue(file);
    }
  }

  open(topicId?: string, subjectId?: string): void {
    this.isVisible = true;
    this.currentTopicId = topicId || null;
    this.hideSubjectSelector = !!subjectId;
    this.hideTopicSelector = !!topicId;
    this.resetForm();
    
    // Si se proporciona subjectId, preseleccionarlo y deshabilitar el selector
    if (subjectId) {
      this.uploadForm.patchValue({ subjectId: subjectId });
      this.uploadForm.get('subjectId')?.disable();
      this.loadTopics(subjectId);
    } else {
      this.uploadForm.get('subjectId')?.enable();
    }
    
    // Si se proporciona topicId, preseleccionarlo y deshabilitar el selector
    if (topicId) {
      this.uploadForm.patchValue({ topicId: topicId });
      this.uploadForm.get('topicId')?.disable();
    } else {
      this.uploadForm.get('topicId')?.enable();
    }
  }

  close(): void {
    this.isVisible = false;
    this.resetForm();
  }

  resetForm(): void {
    this.uploadForm.reset();
    this.uploadForm.get('subjectId')?.enable(); // Habilitar el selector por defecto
    this.uploadForm.get('topicId')?.enable(); // Habilitar el selector por defecto
    this.selectedFile = null;
    this.uploadError = null;
    this.currentTopicId = null;
    this.hideSubjectSelector = false;
    this.hideTopicSelector = false;
    this.topics = [];
  }

  submit(): void {
    if (this.uploadForm.invalid || !this.selectedFile) {
      this.uploadForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.uploadError = null;

    const formData = this.uploadForm.value;
    // Obtener el subjectId correcto, incluso si el campo está deshabilitado
    const subjectId = this.uploadForm.get('subjectId')?.value || this.uploadForm.getRawValue().subjectId;
    // Obtener el topicId correcto, incluso si el campo está deshabilitado
    const topicId = this.uploadForm.get('topicId')?.value || this.uploadForm.getRawValue().topicId;
    
    this.documentService.uploadDocument(
      formData.title,
      formData.description,
      this.selectedFile,
      subjectId,
      topicId || undefined
    ).subscribe({
      next: () => {
        this.isLoading = false;
        this.close();
        // Emitir evento para recargar documentos
        window.dispatchEvent(new CustomEvent('document-uploaded'));
      },
      error: (error) => {
        this.isLoading = false;
        this.uploadError = 'Error al subir el documento. Por favor, inténtelo de nuevo.';
        console.error('Error uploading document:', error);
      }
    });
  }
}
