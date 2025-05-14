import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  // Datos simulados para el tablero
  teacherName: string = 'Profesor Martínez';
  currentDate: Date = new Date();
  
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
  
  recentQuestions = [
    { id: '1', text: '¿Cómo se calcula la derivada de una función compuesta?', date: new Date('2025-05-13'), student: 'Ana García', subject: 'Matemáticas' },
    { id: '2', text: '¿Qué es la fuerza electromotriz?', date: new Date('2025-05-12'), student: 'Carlos Ruiz', subject: 'Física' },
    { id: '3', text: '¿Cuáles son las fases de la mitosis?', date: new Date('2025-05-11'), student: 'Elena Martín', subject: 'Biología' },
    { id: '4', text: '¿Podría explicar el concepto de momento de una fuerza?', date: new Date('2025-05-11'), student: 'David López', subject: 'Física' }
  ];
  
  getTotalStudents(): number {
    return this.subjects.reduce((sum, subject) => sum + subject.students, 0);
  }
  
  getTotalDocuments(): number {
    return this.subjects.reduce((sum, subject) => sum + subject.documents, 0);
  }
}
