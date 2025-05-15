import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { ManageUsersDialogComponent } from './manage-users-dialog/manage-users-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SubjectService, Subject } from '../../../../core/services/subject.service';

@Component({
  selector: 'app-subjects-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule, MatDialogModule],
  templateUrl: './subjects-management.component.html',
  styleUrls: ['./subjects-management.component.scss']
})
export class SubjectsManagementComponent implements OnInit {
  subjects: Subject[] = [];
  searchTerm: string = '';
  showNewSubjectForm: boolean = false;

  newSubject = {
    name: '',
    description: ''
  };
  
  selectedSubject: Subject | null = null;
  showManageUsersDialog: boolean = false;
  isLoading: boolean = false;

  constructor(
    private dialog: MatDialog,
    private subjectService: SubjectService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadSubjects();
  }
  
  loadSubjects(): void {
    this.isLoading = true;
    this.subjectService.getSubjects().subscribe({
      next: (subjects) => {
        this.subjects = subjects;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar asignaturas:', error);
        this.isLoading = false;
      }
    });
  }

  getFilteredSubjects(): Subject[] {
    return this.subjects.filter(subject => 
      subject.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      subject.description.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  toggleNewSubjectForm(): void {
    this.showNewSubjectForm = !this.showNewSubjectForm;
    if (!this.showNewSubjectForm) {
      this.resetNewSubjectForm();
    }
  }

  resetNewSubjectForm(): void {
    this.newSubject = {
      name: '',
      description: ''
    };
  }

  addNewSubject(): void {
    if (this.validateNewSubject()) {
      this.isLoading = true;
      this.subjectService.createSubject({
        name: this.newSubject.name,
        description: this.newSubject.description
      }).subscribe({
        next: (newSubject) => {
          this.subjects.push(newSubject);
          this.toggleNewSubjectForm();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear asignatura:', error);
          this.isLoading = false;
        }
      });
    }
  }

  validateNewSubject(): boolean {
    return (
      this.newSubject.name.length > 0 &&
      this.newSubject.description.length > 0
    );
  }

  toggleSubjectStatus(subject: Subject): void {
    this.isLoading = true;
    this.subjectService.toggleSubjectStatus(subject.id).subscribe({
      next: (updatedSubject) => {
        const index = this.subjects.findIndex(s => s.id === updatedSubject.id);
        if (index !== -1) {
          this.subjects[index] = updatedSubject;
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cambiar el estado de la asignatura:', error);
        // Revertir el cambio en la interfaz
        subject.active = !subject.active;
        this.isLoading = false;
      }
    });
  }

  editSubject(subjectId: string): void {
    // Ahora navegamos a la vista de edición
    // El botón de edición en el HTML ya tiene el RouterLink configurado,
    // pero mantenemos este método por si se quiere llamar programáticamente
    this.router.navigate(['/admin/subjects', subjectId]);
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
    this.selectedSubject = subject;
    const dialogRef = this.dialog.open(ManageUsersDialogComponent, {
      width: '900px',
      data: { subject: subject, subjectService: this.subjectService }
    });
    
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Actualizar la asignatura con los datos recibidos del diálogo
        console.log('Usuarios actualizados:', result);
        
        // Actualizar los contadores en la interfaz
        const index = this.subjects.findIndex(s => s.id === subject.id);
        if (index !== -1) {
          this.subjects[index].teacherCount = result.filter((u: any) => u.role === 'teacher').length;
          this.subjects[index].studentCount = result.filter((u: any) => u.role === 'student').length;
        }
      }
    });
  }
}
