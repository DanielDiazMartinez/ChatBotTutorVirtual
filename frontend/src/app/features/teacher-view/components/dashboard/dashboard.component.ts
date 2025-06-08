import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ChatService } from '../../../../core/services/chat.service';
import { AuthService } from '../../../../services/auth.service';
import { SubjectService } from '../../../../services/subject.service';
import { SubjectService as CoreSubjectService } from '../../../../core/services/subject.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // Datos del profesor
  teacherName: string = 'Profesor';
  currentDate: Date = new Date();
  
  // Datos reales de mensajes
  recentQuestions: any[] = [];
  isLoadingMessages: boolean = false;
  
  // Datos reales de asignaturas
  subjects: any[] = [];
  isLoadingSubjects: boolean = false;
  
  constructor(
    private chatService: ChatService,
    private authService: AuthService,
    private subjectService: SubjectService,
    private coreSubjectService: CoreSubjectService
  ) {}

  ngOnInit(): void {
    this.loadRecentMessages();
    this.loadTeacherSubjects();
  }

  private loadTeacherSubjects(): void {
    this.isLoadingSubjects = true;
    
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        const userId = user.data.id;
        
        // Actualizar nombre del profesor
        if (user.data.name) {
          this.teacherName = user.data.name;
        }
        
        this.subjectService.getSubjectsByUserId(userId.toString()).subscribe({
          next: (response) => {
            if (response.data && response.data.length > 0) {
              this.loadSubjectsWithStatistics(response.data);
            } else {
              this.subjects = [];
              this.isLoadingSubjects = false;
            }
          },
          error: (error) => {
            console.error('Error al cargar asignaturas del profesor:', error);
            this.subjects = [];
            this.isLoadingSubjects = false;
          }
        });
      },
      error: (error) => {
        console.error('Error al obtener usuario actual:', error);
        this.subjects = [];
        this.isLoadingSubjects = false;
      }
    });
  }

  private loadSubjectsWithStatistics(teacherSubjects: any[]): void {
    // Crear observables para obtener las estadísticas de cada asignatura
    const subjectRequests = teacherSubjects.map(subject => 
      this.coreSubjectService.getSubjectUsers(subject.id.toString())
    );

    forkJoin(subjectRequests).subscribe({
      next: (responses) => {
        this.subjects = teacherSubjects.map((subject, index) => {
          const userStats = responses[index].data;
          return {
            id: subject.id,
            name: subject.name,
            students: userStats?.student_count || 0,
            documents: subject.document_count || 0 // Usar el conteo del backend
          };
        });
        this.isLoadingSubjects = false;
      },
      error: (error) => {
        console.error('Error al cargar estadísticas de asignaturas:', error);
        // En caso de error, usar los datos básicos sin estadísticas
        this.subjects = teacherSubjects.map(subject => ({
          id: subject.id,
          name: subject.name,
          students: 0,
          documents: subject.document_count || 0 // Usar el conteo del backend aunque haya error
        }));
        this.isLoadingSubjects = false;
      }
    });
  }

  private loadRecentMessages(): void {
    this.isLoadingMessages = true;
    this.chatService.getRecentMessages(10).subscribe({
      next: (response) => {
        if (response.data) {
          this.recentQuestions = response.data;
          console.log('Mensajes recientes cargados:', this.recentQuestions);
        }
        this.isLoadingMessages = false;
      },
      error: (error) => {
        console.error('Error al cargar mensajes recientes:', error);
        this.recentQuestions = [];
        this.isLoadingMessages = false;
      }
    });
  }
  
  getTotalStudents(): number {
    return this.subjects.reduce((sum, subject) => sum + subject.students, 0);
  }
  
  getTotalDocuments(): number {
    return this.subjects.reduce((sum, subject) => sum + subject.documents, 0);
  }
}
