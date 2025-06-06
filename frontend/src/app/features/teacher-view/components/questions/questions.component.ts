import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SubjectService } from '../../../../core/services/subject.service';
import { ChatService } from '../../../../core/services/chat.service';
import { Subject } from '../../../../core/services/subject.service';

interface Question {
  id: string;
  text: string;
  subject: string;
  topic: string;
  userId: string;
  userName: string;
  userEmail?: string;
}

interface QuestionStats {
  totalQuestions: number;
  uniqueUsers?: number;
  questionsBySubject?: { [key: string]: number };
}

interface Topic {
  id: string;
  name: string;
  description: string;
  subject_id: number;
}

@Component({
  selector: 'app-questions',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './questions.component.html',
  styleUrls: ['./questions.component.scss']
})
export class QuestionsComponent implements OnInit {
  selectedSubject: string = 'Todas';
  selectedTopic: string = 'Todos';
  
  stats: QuestionStats = {
    totalQuestions: 0,
    uniqueUsers: 0,
    questionsBySubject: {}
  };

  questions: Question[] = [];
  subjects: Subject[] = [];
  topics: Topic[] = [];
  allTopics: Topic[] = []; // Para almacenar todos los temas

  constructor(
    private subjectService: SubjectService,
    private chatService: ChatService
  ) {}

  ngOnInit(): void {
    this.loadSubjects();
    this.loadAllTopics();
    this.loadQuestions();
    this.loadStatistics();
  }

  loadSubjects(): void {
    this.subjectService.getSubjects().subscribe({
      next: (response) => {
        if (response.data) {
          this.subjects = response.data;
          console.log('Asignaturas cargadas:', this.subjects);
        }
      },
      error: (error) => {
        console.error('Error al cargar asignaturas:', error);
      }
    });
  }

  loadAllTopics(): void {
    // Por ahora cargaremos todos los temas disponibles
    // En el futuro podrías implementar un endpoint específico para obtener todos los temas
    this.allTopics = [];
    this.topics = [];
  }

  loadTopicsForSubject(subjectId: string): void {
    if (!subjectId || subjectId === 'Todas') {
      this.topics = this.allTopics;
      return;
    }

    this.subjectService.getTopicsBySubject(subjectId).subscribe({
      next: (response) => {
        if (response.data) {
          this.topics = response.data.map((topic: any) => ({
            id: topic.id.toString(),
            name: topic.name,
            description: topic.description || '',
            subject_id: topic.subject_id
          }));
          console.log('Temas cargados para la asignatura:', this.topics);
        }
      },
      error: (error) => {
        console.error('Error al cargar temas:', error);
        this.topics = [];
      }
    });
  }

  loadQuestions(subjectId?: number, topicId?: number): void {
    this.chatService.getUserMessages(subjectId, topicId).subscribe({
      next: (response) => {
        if (response.data) {
          this.questions = response.data;
          console.log('Mensajes cargados:', this.questions);
        }
      },
      error: (error) => {
        console.error('Error al cargar mensajes:', error);
        this.questions = [];
      }
    });
  }

  loadStatistics(subjectId?: number, topicId?: number): void {
    this.chatService.getMessagesStatistics(subjectId, topicId).subscribe({
      next: (response) => {
        if (response.data) {
          this.stats = {
            totalQuestions: response.data.total_messages || 0,
            uniqueUsers: response.data.unique_users || 0,
            questionsBySubject: response.data.messages_by_subject || {}
          };
          console.log('Estadísticas cargadas:', this.stats);
        }
      },
      error: (error) => {
        console.error('Error al cargar estadísticas:', error);
        this.stats = {
          totalQuestions: 0,
          uniqueUsers: 0,
          questionsBySubject: {}
        };
      }
    });
  }

  onSubjectChange(event: Event): void {
    this.selectedSubject = (event.target as HTMLSelectElement).value;
    this.selectedTopic = 'Todos'; // Reset topic selection
    
    if (this.selectedSubject === 'Todas') {
      this.topics = this.allTopics;
      this.loadQuestions(); // Cargar todas las preguntas
      this.loadStatistics(); // Cargar todas las estadísticas
    } else {
      const selectedSubjectData = this.subjects.find(s => s.name === this.selectedSubject);
      if (selectedSubjectData) {
        this.loadTopicsForSubject(selectedSubjectData.id);
        const subjectId = Number(selectedSubjectData.id);
        this.loadQuestions(subjectId); // Cargar preguntas filtradas por asignatura
        this.loadStatistics(subjectId); // Cargar estadísticas filtradas por asignatura
      }
    }
  }

  onTopicChange(event: Event): void {
    this.selectedTopic = (event.target as HTMLSelectElement).value;
    
    // Cargar preguntas y estadísticas filtradas por asignatura y tema
    const selectedSubjectData = this.subjects.find(s => s.name === this.selectedSubject);
    const selectedTopicData = this.topics.find(t => t.name === this.selectedTopic);
    
    const subjectId = selectedSubjectData && this.selectedSubject !== 'Todas' ? Number(selectedSubjectData.id) : undefined;
    const topicId = selectedTopicData && this.selectedTopic !== 'Todos' ? Number(selectedTopicData.id) : undefined;
    
    this.loadQuestions(subjectId, topicId);
    this.loadStatistics(subjectId, topicId);
  }

  getFilteredQuestions(): Question[] {
    // Ya no necesitamos filtrar aquí porque el filtrado se hace en el backend
    return this.questions;
  }

  getSubjectNames(): string[] {
    const names = ['Todas', ...this.subjects.map(s => s.name)];
    return names;
  }

  getTopicNames(): string[] {
    const names = ['Todos', ...this.topics.map(t => t.name)];
    return names;
  }
}
