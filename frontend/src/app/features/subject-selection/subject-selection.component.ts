import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SubjectCardComponent } from './components/subject-card/subject-card.component';
import { SubjectService } from '../../services/subject.service';
import { Subject } from './interfaces/subject.interface';
import { HeaderComponent } from '../../shared/components/header/header.component';

@Component({
  selector: 'app-subject-selection',
  templateUrl: './subject-selection.component.html',
  styleUrls: ['./subject-selection.component.scss'],
  standalone: true,
  imports: [CommonModule, SubjectCardComponent, HeaderComponent]
})
export class SubjectSelectionComponent implements OnInit {
  subjects: Subject[] = [
    { id: '1', name: 'Matemáticas', icon: '📐', description: 'Álgebra, geometría y cálculo' },
    { id: '2', name: 'Física', icon: '⚡', description: 'Mecánica, electricidad y termodinámica' },
    { id: '3', name: 'Química', icon: '🧪', description: 'Química orgánica e inorgánica' },
    { id: '4', name: 'Biología', icon: '🧬', description: 'Genética, ecología y evolución' },
    { id: '5', name: 'Historia', icon: '📚', description: 'Historia mundial y local' },
    { id: '6', name: 'Literatura', icon: '📖', description: 'Análisis literario y escritura' }
  ];

  selectedSubject: Subject | null = null;

  constructor(
    private router: Router,
    private subjectService: SubjectService
  ) {}

  ngOnInit(): void {
    // Clear any previous selection when entering this view
    this.subjectService.setSelectedSubjects([]);
  }

  onSubjectSelect(subject: Subject): void {
    if (this.selectedSubject?.id === subject.id) {
      // Deselect if clicking the same subject
      this.selectedSubject = null;
      this.subjectService.setSelectedSubjects([]);
    } else {
      // Select new subject and navigate to chat
      this.selectedSubject = subject;
      this.subjectService.setSelectedSubjects([subject.id]);
      this.router.navigate(['/chat']);
    }
  }
}
