import { Component, OnInit } from '@angular/core';
import { UserService } from '../../../../core/services/user.service';
import { SubjectService } from '../../../../core/services/subject.service';
import { DocumentService } from '../../../../core/services/document.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  totalUsuarios = 0;
  totalProfesores = 0;
  totalEstudiantes = 0;
  totalAdministradores = 0;
  totalAsignaturas = 0;
  totalDocumentos = 0;

  constructor(
    private userService: UserService,
    private subjectService: SubjectService,
    private documentService: DocumentService
  ) {}

  ngOnInit(): void {
    this.userService.getAllUsers().subscribe({
      next: (response) => {
        if (response.data) {
          this.totalUsuarios = response.data.length;
          this.totalProfesores = response.data.filter(u => u.role === 'teacher').length;
          this.totalEstudiantes = response.data.filter(u => u.role === 'student').length;
          this.totalAdministradores = response.data.filter(u => u.role === 'admin').length;
        }
      },
      error: () => {
        this.totalUsuarios = 0;
        this.totalProfesores = 0;
        this.totalEstudiantes = 0;
        this.totalAdministradores = 0;
      }
    });

    this.subjectService.getSubjects().subscribe({
      next: (response) => {
        if (response.data) {
          this.totalAsignaturas = response.data.length;
        }
      },
      error: () => {
        this.totalAsignaturas = 0;
      }
    });

    // Cargar total de documentos
    this.documentService.getDocuments().subscribe({
      next: (response) => {
        if (response.data) {
          this.totalDocumentos = response.data.length;
        }
      },
      error: () => {
        this.totalDocumentos = 0;
      }
    });
  }
} 