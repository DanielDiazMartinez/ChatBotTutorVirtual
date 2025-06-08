import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
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
  returnTo: string | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private subjectService: SubjectService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.subjectService.setSelectedSubjects([]);
    // Obtener el parámetro returnTo si existe
    this.route.queryParams.subscribe(params => {
      this.returnTo = params['returnTo'] || null;
    });
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
      
      // Si viene de un profesor, mantiene en el mismo flujo de chat
      // Si viene de un estudiante, navega al chat normal
      this.router.navigate(['/chat']);
    }
  }
}
