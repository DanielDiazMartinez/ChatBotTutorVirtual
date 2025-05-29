import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';
import { SubjectService } from '../../services/subject.service';
import { AuthService } from '../../services/auth.service';
import { Subject } from '../subject-selection/interfaces/subject.interface';

@Component({
  selector: 'app-teacher-view',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent],
  templateUrl: './teacher-view.component.html',
  styleUrls: ['./teacher-view.component.scss']
})
export class TeacherViewComponent implements OnInit {
  // Navegación activa
  activeNav: string = 'dashboard';
  
  // Estado de expansión de la sección de asignaturas
  subjectsExpanded: boolean = false;
  
  // Lista de asignaturas del profesor
  teacherSubjects: Subject[] = [];
  isLoadingSubjects: boolean = false;
  
  // Datos del usuario profesor
  teacherProfile: UserProfile = {
    name: 'Profesor Martínez',
    role: 'teacher',
    avatar: 'assets/images/teacher-avatar.svg'
  };

  constructor(
    private subjectService: SubjectService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadTeacherSubjects();
  }

  setActive(navItem: string) {
    this.activeNav = navItem;
  }
  
  toggleSubjects() {
    this.subjectsExpanded = !this.subjectsExpanded;
  }
  
  // Método para verificar si la URL actual contiene una ruta específica
  isActiveRoute(route: string): boolean {
    return window.location.href.includes(route);
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
}
