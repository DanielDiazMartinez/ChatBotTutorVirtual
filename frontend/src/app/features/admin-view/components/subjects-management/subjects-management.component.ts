import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { SubjectService, Subject } from '../../../../core/services/subject.service';
import { ManageUsersDialogComponent } from './manage-users-dialog/manage-users-dialog.component';

@Component({
  selector: 'app-subjects-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule, MatDialogModule],
  templateUrl: './subjects-management.component.html',
  styleUrls: ['./subjects-management.component.scss']
})
export class SubjectsManagementComponent implements OnInit {
  subjects: Subject[] = [];
  isLoading = false;
  searchTerm = '';
  showNewSubjectForm = false;
  newSubject = {
    name: '',
    code: '',
    description: ''
  };

  constructor(
    private subjectService: SubjectService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadSubjects();
  }
  
  loadSubjects(): void {
    this.isLoading = true;
    this.subjectService.getSubjects().subscribe({
      next: (response) => {
        if (response.data) {
          this.subjects = response.data;
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar asignaturas:', error);
        this.isLoading = false;
      }
    });
  }

  getFilteredSubjects(): Subject[] {
    if (!this.searchTerm) return this.subjects;
    const searchLower = this.searchTerm.toLowerCase();
    return this.subjects.filter(subject => 
      subject.name.toLowerCase().includes(searchLower) ||
      subject.description.toLowerCase().includes(searchLower)
    );
  }

  toggleNewSubjectForm(): void {
    this.showNewSubjectForm = !this.showNewSubjectForm;
    if (!this.showNewSubjectForm) {
      this.newSubject = { name: '', code: '', description: '' };
    }
  }

  validateNewSubject(): boolean {
    return this.newSubject.name.trim().length > 0 && this.newSubject.code.trim().length > 0;
  }

  addNewSubject(): void {
    if (this.validateNewSubject()) {
      this.isLoading = true;
      this.subjectService.createSubject({
        name: this.newSubject.name,
        code: this.newSubject.code,
        description: this.newSubject.description
      }).subscribe({
        next: (response) => {
          if (response.data) {
            this.subjects.push(response.data);
          this.toggleNewSubjectForm();
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear asignatura:', error);
          this.isLoading = false;
        }
      });
    }
  }

  deleteSubject(subjectId: string): void {
    if (confirm('¿Está seguro de que desea eliminar esta asignatura? Esta acción no se puede deshacer.')) {
      this.isLoading = true;
      this.subjectService.deleteSubject(subjectId).subscribe({
        next: () => {
          this.subjects = this.subjects.filter(subject => subject.id !== subjectId);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al eliminar la asignatura:', error);
          this.isLoading = false;
        }
      });
    }
  }
  
  openManageUsersDialog(subject: Subject): void {
    const dialogRef = this.dialog.open(ManageUsersDialogComponent, {
      width: '900px',
      data: { subject: subject, subjectService: this.subjectService }
    });
    
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Recargar la lista de asignaturas para obtener los contadores actualizados del backend
        this.loadSubjects();
      }
    });
  }
}
