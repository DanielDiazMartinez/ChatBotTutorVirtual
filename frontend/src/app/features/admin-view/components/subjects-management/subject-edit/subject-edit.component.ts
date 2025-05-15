import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { SubjectService, Subject } from '../../../../../core/services/subject.service';

@Component({
  selector: 'app-subject-edit',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './subject-edit.component.html',
  styleUrls: ['./subject-edit.component.scss']
})
export class SubjectEditComponent implements OnInit {
  subject: Subject | null = null;
  isLoading: boolean = false;
  error: string | null = null;
  successMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private subjectService: SubjectService
  ) {}

  ngOnInit(): void {
    this.loadSubject();
  }

  loadSubject(): void {
    const subjectId = this.route.snapshot.paramMap.get('id');
    if (!subjectId) {
      this.error = 'No se proporcionó un ID de asignatura válido';
      return;
    }

    this.isLoading = true;
    
    // Obtener los detalles de la asignatura
    this.subjectService.getSubjects().subscribe({
      next: (subjects) => {
        const subject = subjects.find(s => s.id === subjectId);
        if (subject) {
          this.subject = { ...subject }; // Crear una copia para no modificar directamente el original
        } else {
          this.error = 'No se encontró la asignatura especificada';
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar la asignatura:', error);
        this.error = 'Error al cargar la asignatura';
        this.isLoading = false;
      }
    });
  }

  saveChanges(): void {
    if (!this.subject) return;
    
    this.isLoading = true;
    this.error = null;
    this.successMessage = null;
    
    this.subjectService.updateSubject(this.subject.id, {
      name: this.subject.name,
      description: this.subject.description
    }).subscribe({
      next: (updatedSubject) => {
        this.subject = updatedSubject;
        this.isLoading = false;
        this.successMessage = 'Asignatura actualizada correctamente';
        
        // Mostrar mensaje de éxito por un tiempo limitado
        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (error) => {
        console.error('Error al actualizar la asignatura:', error);
        this.error = 'Error al guardar los cambios';
        this.isLoading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/admin/subjects']);
  }

  toggleStatus(): void {
    if (!this.subject) return;
    
    this.isLoading = true;
    this.subjectService.toggleSubjectStatus(this.subject.id).subscribe({
      next: (updatedSubject) => {
        this.subject = updatedSubject;
        this.isLoading = false;
        this.successMessage = `Estado cambiado a ${this.subject.active ? 'activo' : 'inactivo'} correctamente`;
        
        // Mostrar mensaje de éxito por un tiempo limitado
        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (error) => {
        console.error('Error al cambiar el estado de la asignatura:', error);
        this.error = 'Error al cambiar el estado';
        this.isLoading = false;
      }
    });
  }
}
