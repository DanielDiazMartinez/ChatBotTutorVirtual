import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';

interface Student {
  id: string;
  name: string;
  email: string;
  subjects: string[];
  avatarUrl?: string;
  performance?: {
    participationRate: number;
    questionsAsked: number;
    documentAccess: number;
  };
}

@Component({
  selector: 'app-student-profile',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './student-profile.component.html',
  styleUrls: ['./student-profile.component.scss']
})
export class StudentProfileComponent implements OnInit {
  studentId: string | null = null;
  studentName: string | null = null;
  student: Student | null = null;
  isLoading = true;

  // Datos simulados (en un caso real, esto vendría de un servicio)
  mockStudents: Student[] = [
    {
      id: '1',
      name: 'Ana García',
      email: 'ana.garcia@estudiante.edu',
      subjects: ['Matemáticas', 'Física'],
      avatarUrl: 'assets/images/student-avatar-1.png',
      performance: {
        participationRate: 85,
        questionsAsked: 12,
        documentAccess: 78
      }
    },
    {
      id: '2',
      name: 'Carlos Ruiz',
      email: 'carlos.ruiz@estudiante.edu',
      subjects: ['Física', 'Biología'],
      avatarUrl: 'assets/images/student-avatar-2.png',
      performance: {
        participationRate: 70,
        questionsAsked: 8,
        documentAccess: 62
      }
    },
    {
      id: '3',
      name: 'Elena Martín',
      email: 'elena.martin@estudiante.edu',
      subjects: ['Biología', 'Literatura'],
      avatarUrl: 'assets/images/student-avatar-3.png',
      performance: {
        participationRate: 92,
        questionsAsked: 15,
        documentAccess: 90
      }
    },
    {
      id: '4',
      name: 'David López',
      email: 'david.lopez@estudiante.edu',
      subjects: ['Física', 'Matemáticas'],
      avatarUrl: 'assets/images/student-avatar-4.png',
      performance: {
        participationRate: 65,
        questionsAsked: 6,
        documentAccess: 55
      }
    }
  ];

  // Actividades recientes simuladas
  recentActivities = [
    { 
      id: '1',
      type: 'question', 
      content: '¿Cómo se calcula la derivada de una función compuesta?', 
      date: new Date('2025-05-13'), 
      subject: 'Matemáticas' 
    },
    { 
      id: '2',
      type: 'document',
      content: 'Accedió al documento: Ecuaciones diferenciales', 
      date: new Date('2025-05-12'), 
      subject: 'Matemáticas' 
    },
    { 
      id: '3',
      type: 'question',
      content: '¿Cuáles son las principales leyes de Newton?', 
      date: new Date('2025-05-10'), 
      subject: 'Física' 
    }
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Obtener el ID y/o nombre del estudiante de los parámetros de la URL
    this.route.paramMap.subscribe(params => {
      this.studentId = params.get('id');
      
      // Si tenemos un ID, buscar el estudiante
      if (this.studentId) {
        this.loadStudentById(this.studentId);
      } else {
        // Si no tenemos ID, verificamos si hay un parámetro de nombre
        this.route.queryParamMap.subscribe(queryParams => {
          this.studentName = queryParams.get('name');
          if (this.studentName) {
            this.loadStudentByName(this.studentName);
          } else {
            // Si no hay ID ni nombre, redirigir al dashboard
            this.router.navigate(['/teacher/dashboard']);
          }
        });
      }
    });
  }

  private loadStudentById(id: string): void {
    // Simulación de carga de datos (reemplazar por llamada a API en caso real)
    setTimeout(() => {
      this.student = this.mockStudents.find(s => s.id === id) || null;
      this.isLoading = false;
      
      if (!this.student) {
        // Si no se encuentra el estudiante, redirigir al dashboard
        this.router.navigate(['/teacher/dashboard']);
      }
    }, 500); // Simulamos un retraso de carga
  }

  private loadStudentByName(name: string): void {
    // Simulación de carga de datos (reemplazar por llamada a API en caso real)
    setTimeout(() => {
      this.student = this.mockStudents.find(s => s.name === name) || null;
      this.isLoading = false;
      
      if (!this.student) {
        // Si no se encuentra el estudiante, redirigir al dashboard
        this.router.navigate(['/teacher/dashboard']);
      }
    }, 500); // Simulamos un retraso de carga
  }

  getProgressBarClass(value: number): string {
    if (value >= 80) return 'high';
    if (value >= 60) return 'medium';
    return 'low';
  }

  onBack(): void {
    // Si tenemos una página anterior en el historial, volvemos atrás
    // Esto permite volver al punto de origen (dashboard, materias, etc.)
    if (window.history.length > 1) {
      window.history.back();
    } else {
      // Si no hay historial, volvemos al dashboard como fallback
      this.router.navigate(['/teacher/dashboard']);
    }
  }
}
