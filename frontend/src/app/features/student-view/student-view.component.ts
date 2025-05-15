import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { ChatAreaComponent } from './components/chat-area/chat-area.component';
import { HeaderComponent, UserProfile } from '../../shared/components/header/header.component';
import { DocumentsModalComponent } from './components/documents-modal/documents-modal.component';
import { SubjectService } from '../../services/subject.service';
import { Subject } from '../subject-selection/interfaces/subject.interface';

@Component({
  selector: 'app-student-view',
  standalone: true,
  imports: [CommonModule, SidebarComponent, ChatAreaComponent, HeaderComponent, DocumentsModalComponent],
  templateUrl: './student-view.component.html',
  styleUrls: ['./student-view.component.scss']
})
export class StudentViewComponent implements OnInit { 
  isDocumentsModalVisible = false;
  currentSubject: Subject | null = null;
  
  // Datos del usuario estudiante
  studentProfile: UserProfile = {
    name: 'Ana García',
    role: 'student',
    avatar: 'assets/images/student-avatar.svg'
  };

  // Lista de asignaturas disponibles
  availableSubjects: Subject[] = [
    { id: '1', name: 'Matemáticas', icon: '📐', description: 'Álgebra, geometría y cálculo' },
    { id: '2', name: 'Física', icon: '⚡', description: 'Mecánica, electricidad y termodinámica' },
    { id: '3', name: 'Química', icon: '🧪', description: 'Química orgánica e inorgánica' },
    { id: '4', name: 'Biología', icon: '🧬', description: 'Genética, ecología y evolución' },
    { id: '5', name: 'Historia', icon: '📚', description: 'Historia mundial y local' },
    { id: '6', name: 'Literatura', icon: '📖', description: 'Análisis literario y escritura' }
  ];
  
  constructor(private subjectService: SubjectService, private router: Router) {}
  
  ngOnInit(): void {
    // Obtener la asignatura seleccionada
    const selectedSubjectIds = this.subjectService.getSelectedSubjects();
    if (selectedSubjectIds.length === 0) {
      // Si no hay asignatura seleccionada, redirigir a la página de selección
      this.router.navigate(['/subject-selection']);
      return;
    }
    
    // Buscar la asignatura seleccionada
    this.currentSubject = this.availableSubjects.find(subject => subject.id === selectedSubjectIds[0]) || null;
  }
  
  toggleDocumentsModal(): void {
    this.isDocumentsModalVisible = !this.isDocumentsModalVisible;
  }
}