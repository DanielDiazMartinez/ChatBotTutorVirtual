import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ChatService } from '../../../../core/services/chat.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // Datos simulados para el tablero
  teacherName: string = 'Profesor Martínez';
  currentDate: Date = new Date();
  
  // Datos reales de mensajes
  recentQuestions: any[] = [];
  isLoadingMessages: boolean = false;
  
  subjects = [
    { 
      id: '1', 
      name: 'Matemáticas', 
      students: 125, 
      documents: 15,
      topStudents: [
        { id: '1', name: 'Ana García' },
        { id: '2', name: 'David López' }
      ]
    },
    { 
      id: '2', 
      name: 'Física', 
      students: 98, 
      documents: 12,
      topStudents: [
        { id: '2', name: 'Carlos Ruiz' },
        { id: '4', name: 'David López' }
      ]
    },
    { 
      id: '3', 
      name: 'Biología', 
      students: 110, 
      documents: 9,
      topStudents: [
        { id: '3', name: 'Elena Martín' }
      ]
    },
    { 
      id: '4', 
      name: 'Literatura', 
      students: 85, 
      documents: 8,
      topStudents: [
        { id: '3', name: 'Elena Martín' }
      ]
    }
  ];
  
  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.loadRecentMessages();
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
