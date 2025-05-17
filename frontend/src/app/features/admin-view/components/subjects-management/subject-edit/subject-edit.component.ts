import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
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
  isLoading = false;
  error: string | null = null;
  successMessage: string | null = null;

  constructor(
    private subjectService: SubjectService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const subjectId = this.route.snapshot.paramMap.get('id');
    if (subjectId) {
      this.loadSubject(subjectId);
    } else {
      this.error = 'ID de asignatura no proporcionado';
    }
    }

  loadSubject(subjectId: string): void {
    this.isLoading = true;
    this.error = null;
    
    this.subjectService.getSubject(subjectId).subscribe({
      next: (response) => {
        if (response.data) {
          this.subject = response.data;
        } else {
          this.error = 'Asignatura no encontrada';
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
      code: this.subject.code,
      description: this.subject.description
    }).subscribe({
      next: (response) => {
        if (response.data) {
          this.subject = response.data;
          this.successMessage = 'Asignatura actualizada correctamente';
          
          // Mostrar mensaje de éxito por un tiempo limitado
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        }
        this.isLoading = false;
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
}
