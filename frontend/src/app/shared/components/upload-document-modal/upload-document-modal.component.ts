import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject } from '../../../core/services/subject.service';
import { SubjectService } from '../../../core/services/subject.service';
import { DocumentService } from '../../../core/services/document.service';

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

  isVisible = false;
  isLoading = false;
  uploadError: string | null = null;
  subjects: Subject[] = [];
  uploadForm!: FormGroup;
  selectedFile: File | null = null;
  fileMaxSize = 10; // MB
  currentTopicId: string | null = null;
  hideSubjectSelector = false;

  ngOnInit(): void {
    this.initForm();
    this.loadSubjects();
  }

  initForm(): void {
    this.uploadForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      subjectId: ['', Validators.required],
      file: [null, Validators.required]
    });
  }

  loadSubjects(): void {
    this.subjectService.getSubjects().subscribe({
      next: (response) => {
        if (response.data) {
          this.subjects = response.data;
        }
      },
      error: (error) => {
        console.error('Error cargando asignaturas:', error);
      }
    });
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
    this.resetForm();
    
    // Si se proporciona subjectId, preseleccionarlo y deshabilitar el selector
    if (subjectId) {
      this.uploadForm.patchValue({ subjectId: subjectId });
      this.uploadForm.get('subjectId')?.disable();
    } else {
      this.uploadForm.get('subjectId')?.enable();
    }
  }

  close(): void {
    this.isVisible = false;
    this.resetForm();
  }

  resetForm(): void {
    this.uploadForm.reset();
    this.uploadForm.get('subjectId')?.enable(); // Habilitar el selector por defecto
    this.selectedFile = null;
    this.uploadError = null;
    this.currentTopicId = null;
    this.hideSubjectSelector = false;
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
    
    this.documentService.uploadDocument(
      formData.title,
      formData.description,
      this.selectedFile,
      subjectId,
      this.currentTopicId || undefined
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
