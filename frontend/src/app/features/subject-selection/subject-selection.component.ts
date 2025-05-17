import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SubjectCardComponent } from './components/subject-card/subject-card.component';
import { SubjectService } from '../../services/subject.service';
import { Subject } from './interfaces/subject.interface';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { AuthService, UserMe } from '../../services/auth.service';

@Component({
  selector: 'app-subject-selection',
  templateUrl: './subject-selection.component.html',
  styleUrls: ['./subject-selection.component.scss'],
  standalone: true,
  imports: [CommonModule, SubjectCardComponent, HeaderComponent]
})
export class SubjectSelectionComponent implements OnInit {
  subjects: Subject[] = [];
  selectedSubject: Subject | null = null;
  isLoading = true;
  error: string | null = null;

  constructor(
    private router: Router,
    private subjectService: SubjectService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.subjectService.setSelectedSubjects([]);
    this.loadSubjectsForCurrentUser();
  }

  loadSubjectsForCurrentUser(): void {
    this.isLoading = true;
    this.error = null;
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        const userId = user.data.id;
        this.subjectService.getSubjectsByUserId(userId).subscribe({
          next: (subjectsResponse) => {
            // Asignar iconos predeterminados
            const iconMap: { [key: string]: string } = {
              'matemáticas': '📐',
              'matematicas': '📐',
              'física': '⚡',
              'fisica': '⚡',
              'química': '🧪',
              'quimica': '🧪',
              'biología': '🧬',
              'biologia': '🧬',
              'historia': '📚',
              'literatura': '📖',
              'geología': '🪨',
              'geologia': '🪨',
            };
            this.subjects = (subjectsResponse.data || []).map((subject: any) => {
              const key = subject.name?.toLowerCase() || '';
              return {
                ...subject,
                icon: iconMap[key] || '🎓'
              };
            });
            this.isLoading = false;
          },
          error: (error) => {
            this.error = 'Error al cargar las asignaturas del usuario.';
            this.isLoading = false;
          }
        });
      },
      error: (error) => {
        this.error = 'No se pudo obtener la información del usuario autenticado.';
        this.isLoading = false;
      }
    });
  }

  onSubjectSelect(subject: Subject): void {
    if (this.selectedSubject?.id === subject.id) {
      this.selectedSubject = null;
      this.subjectService.setSelectedSubjects([]);
    } else {
      this.selectedSubject = subject;
      this.subjectService.setSelectedSubjects([subject.id]);
      this.router.navigate(['/chat']);
    }
  }
}
