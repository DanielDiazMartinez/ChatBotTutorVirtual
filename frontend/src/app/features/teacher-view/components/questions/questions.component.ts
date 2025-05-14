import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface Question {
  id: string;
  text: string;
  subject: string;
  topic: string;
  difficulty: 'Fácil' | 'Media' | 'Difícil';
  correctPercentage: number;
  attempts: number;
}

interface QuestionStats {
  totalQuestions: number;
  averageSuccess: number;
  byDifficulty: {
    easy: number;
    medium: number;
    hard: number;
  };
}

@Component({
  selector: 'app-questions',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './questions.component.html',
  styleUrls: ['./questions.component.scss']
})
export class QuestionsComponent {
  selectedSubject: string = 'Todas';
  selectedTopic: string = 'Todos';
  
  stats: QuestionStats = {
    totalQuestions: 125,
    averageSuccess: 68.4,
    byDifficulty: {
      easy: 85.2,
      medium: 62.7,
      hard: 41.3
    }
  };

  questions: Question[] = [
    {
      id: '1',
      text: '¿Cuál es la fórmula del área de un círculo?',
      subject: 'Matemáticas',
      topic: 'Geometría',
      difficulty: 'Fácil',
      correctPercentage: 92.5,
      attempts: 240
    },
    {
      id: '2',
      text: 'Explique la ley de Ohm y su aplicación en circuitos eléctricos.',
      subject: 'Física',
      topic: 'Electricidad',
      difficulty: 'Media',
      correctPercentage: 67.8,
      attempts: 185
    },
    {
      id: '3',
      text: 'Analice la estructura molecular del ADN y explique su función.',
      subject: 'Biología',
      topic: 'Genética',
      difficulty: 'Difícil',
      correctPercentage: 38.2,
      attempts: 156
    },
    {
      id: '4',
      text: 'Describa las principales características del Romanticismo en la literatura.',
      subject: 'Literatura',
      topic: 'Movimientos Literarios',
      difficulty: 'Media',
      correctPercentage: 71.5,
      attempts: 128
    },
    {
      id: '5',
      text: 'Resuelva la siguiente ecuación diferencial: dy/dx = 2xy',
      subject: 'Matemáticas',
      topic: 'Cálculo',
      difficulty: 'Difícil',
      correctPercentage: 45.3,
      attempts: 112
    }
  ];

  subjects = ['Todas', 'Matemáticas', 'Física', 'Biología', 'Literatura'];
  topics = ['Todos', 'Geometría', 'Cálculo', 'Electricidad', 'Genética', 'Movimientos Literarios'];

  onSubjectChange(event: Event): void {
    this.selectedSubject = (event.target as HTMLSelectElement).value;
    // Aquí filtrarías los temas según la asignatura seleccionada
    // Y después filtrarías las preguntas
  }

  onTopicChange(event: Event): void {
    this.selectedTopic = (event.target as HTMLSelectElement).value;
    // Aquí filtrarías las preguntas por tema
  }

  getFilteredQuestions(): Question[] {
    return this.questions
      .filter(q => this.selectedSubject === 'Todas' || q.subject === this.selectedSubject)
      .filter(q => this.selectedTopic === 'Todos' || q.topic === this.selectedTopic);
  }

  getDifficultyClass(difficulty: string): string {
    switch(difficulty) {
      case 'Fácil': return 'easy';
      case 'Media': return 'medium';
      case 'Difícil': return 'hard';
      default: return '';
    }
  }

  getSuccessRateClass(rate: number): string {
    if (rate >= 75) return 'high';
    if (rate >= 50) return 'medium';
    return 'low';
  }
}
