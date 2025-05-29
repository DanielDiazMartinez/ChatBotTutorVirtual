import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, ParamMap, RouterModule } from '@angular/router';
import { SubjectService as CoreSubjectService } from '../../../../core/services/subject.service';
import { SubjectService } from '../../../../services/subject.service';
import { AuthService } from '../../../../services/auth.service';

interface Student {
  id: string;
  name: string;
  email: string;
}

interface Topic {
  id: string;
  name: string;
  description: string;
  documentCount: number;
}

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: Date;
  topicId: string;
}

@Component({
  selector: 'app-subjects',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './subjects.component.html',
  styleUrl: './subjects.component.scss'
})
export class SubjectsComponent implements OnInit {
  // Asignatura seleccionada actualmente
  subject: any = null;
  
  // Lista de asignaturas del profesor
  teacherSubjects: any[] = [];
  
  // Estado de carga
  isLoadingSubjects: boolean = false;
  isLoadingStudents: boolean = false;
  
  constructor(
    private route: ActivatedRoute,
    private coreSubjectService: CoreSubjectService,
    private subjectService: SubjectService,
    private authService: AuthService
  ) {}
  
  ngOnInit(): void {
    this.loadTeacherSubjects();
    
    this.route.paramMap.subscribe((params: ParamMap) => {
      const subjectId = params.get('id');
      if (subjectId) {
        this.loadSubjectDetails(subjectId);
      } else {
        // Si no hay ID en la ruta, cargar la primera asignatura disponible
        if (this.teacherSubjects.length > 0) {
          this.loadSubjectDetails(this.teacherSubjects[0].id);
        }
      }
    });
  }
  
  // Cargar las asignaturas del profesor actual
  private loadTeacherSubjects(): void {
    this.isLoadingSubjects = true;
    
    this.authService.getCurrentUserFromBackend().subscribe({
      next: (user: any) => {
        const userId = user.data.id;
        this.subjectService.getSubjectsByUserId(userId.toString()).subscribe({
          next: (response) => {
            this.teacherSubjects = response.data || [];
            this.isLoadingSubjects = false;
            
            // Si hay un ID en la ruta, cargar esa asignatura
            const subjectId = this.route.snapshot.paramMap.get('id');
            if (subjectId) {
              this.loadSubjectDetails(subjectId);
            } else if (this.teacherSubjects.length > 0) {
              // Si no hay ID específico, cargar la primera asignatura
              this.loadSubjectDetails(this.teacherSubjects[0].id);
            }
          },
          error: (error) => {
            console.error('Error al cargar asignaturas del profesor:', error);
            this.isLoadingSubjects = false;
          }
        });
      },
      error: (error) => {
        console.error('Error al obtener usuario actual:', error);
        this.isLoadingSubjects = false;
      }
    });
  }
  
  loadSubjectDetails(subjectId: string): void {
    // Buscar la asignatura en la lista del profesor
    const foundSubject = this.teacherSubjects.find(s => s.id === subjectId);
    if (foundSubject) {
      this.subject = {
        ...foundSubject,
        description: foundSubject.description || 'Sin descripción disponible'
      };
      
      // Cargar estudiantes de la asignatura desde el backend
      this.loadSubjectStudents(subjectId);
      
      // Cargar temas específicos de la asignatura desde el backend
      this.loadSubjectTopics(subjectId);
      
      // Resetear estados
      this.selectedTopicId = null;
      this.searchTerm = '';
    }
  }

  // Cargar temas de una asignatura específica
  private loadSubjectTopics(subjectId: string): void {
    console.log('Cargando temas para la asignatura:', subjectId);
    
    this.coreSubjectService.getTopicsBySubject(subjectId).subscribe({
      next: (response) => {
        console.log('Respuesta del servicio de temas:', response);
        
        if (response.data) {
          this.topics = response.data.map((topic: any) => ({
            id: topic.id.toString(),
            name: topic.name,
            description: topic.description || 'Sin descripción',
            documentCount: topic.documentCount || 0
          }));
          console.log('Temas cargados:', this.topics);
        } else {
          console.log('No se encontraron temas en la respuesta');
          this.topics = [];
        }
      },
      error: (error) => {
        console.error('Error al cargar temas de la asignatura:', error);
        this.topics = [];
      }
    });
  }
  
  // Cargar estudiantes de una asignatura específica
  private loadSubjectStudents(subjectId: string): void {
    this.isLoadingStudents = true;
    console.log('Cargando estudiantes para la asignatura:', subjectId);
    
    this.coreSubjectService.getSubjectUsers(subjectId).subscribe({
      next: (response) => {
        console.log('Respuesta del servicio de usuarios de asignatura:', response);
        
        // La respuesta del backend tiene la estructura: response.data.students
        if (response.data && response.data.students) {
          console.log('Estudiantes encontrados:', response.data.students);
          this.students = response.data.students.map((user: any) => ({
            id: user.id.toString(),
            name: user.full_name,
            email: user.email
          }));
          console.log('Estudiantes filtrados:', this.students);
        } else {
          console.log('No se encontraron estudiantes en la respuesta');
          this.students = [];
        }
        this.isLoadingStudents = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes de la asignatura:', error);
        this.students = [];
        this.isLoadingStudents = false;
      }
    });  }

  // Referencias a los arrays activos según la asignatura seleccionada
  students: Student[] = [];
  topics: Topic[] = [];
  
  // Datos de muestra de documentos por tema
  documentsMap: { [key: string]: Document[] } = {
    // Temas de Matemáticas
    '1': [
      { id: '1', name: 'Introducción a Matrices', type: 'pdf', size: '2.4 MB', uploadDate: new Date('2025-02-15'), topicId: '1' },
      { id: '2', name: 'Ejercicios de Ecuaciones', type: 'docx', size: '1.8 MB', uploadDate: new Date('2025-03-10'), topicId: '1' },
      { id: '3', name: 'Examen Parcial Resuelto', type: 'pdf', size: '3.2 MB', uploadDate: new Date('2025-04-05'), topicId: '1' }
    ],
    '2': [
      { id: '4', name: 'Guía de Derivadas', type: 'pdf', size: '4.1 MB', uploadDate: new Date('2025-01-20'), topicId: '2' },
      { id: '5', name: 'Presentación de Aplicaciones', type: 'ppt', size: '5.7 MB', uploadDate: new Date('2025-02-28'), topicId: '2' }
    ],
    '3': [
      { id: '6', name: 'Ejercicios Vectores', type: 'pdf', size: '1.5 MB', uploadDate: new Date('2025-03-15'), topicId: '3' }
    ],
    // Temas de Física
    '4': [
      { id: '7', name: 'Problemas de Cinemática', type: 'pdf', size: '3.5 MB', uploadDate: new Date('2025-03-05'), topicId: '4' },
      { id: '8', name: 'Leyes de Newton', type: 'docx', size: '1.9 MB', uploadDate: new Date('2025-02-20'), topicId: '4' }
    ],
    '5': [
      { id: '9', name: 'Campo Eléctrico', type: 'pdf', size: '2.7 MB', uploadDate: new Date('2025-03-18'), topicId: '5' },
      { id: '10', name: 'Experimentos de Magnetismo', type: 'ppt', size: '4.3 MB', uploadDate: new Date('2025-04-02'), topicId: '5' }
    ],
    // Y así con otros temas...
  };
  
  // Referencia actual a los documentos del tema seleccionado
  documents: Document[] = [];
  
  // Estado de la UI
  selectedTopicId: string | null = null;
  searchTerm: string = '';
  newTopicName: string = '';
  newTopicDescription: string = '';
  showNewTopicForm: boolean = false;
  showUploadForm: boolean = false;
  
  // Métodos de la UI
  getFilteredDocumentsByTopic(topicId: string): Document[] {
    if (!topicId) return [];
    return this.documentsMap[topicId] || [];
  }
  
  selectTopic(topicId: string): void {
    this.selectedTopicId = topicId;
    this.documents = this.getFilteredDocumentsByTopic(topicId);
  }
  
  toggleNewTopicForm(): void {
    this.showNewTopicForm = !this.showNewTopicForm;
    if (!this.showNewTopicForm) {
      this.newTopicName = '';
      this.newTopicDescription = '';
    }
  }
  
  addNewTopic(): void {
    if (this.newTopicName.trim() && this.subject?.id) {
      const topicData = {
        name: this.newTopicName,
        description: this.newTopicDescription || '',
        subject_id: parseInt(this.subject.id)
      };

      this.coreSubjectService.createTopic(topicData).subscribe({
        next: (response) => {
          console.log('Tema creado exitosamente:', response);
          
          // Recargar la lista de temas
          this.loadSubjectTopics(this.subject.id);
          
          // Cerrar el formulario
          this.toggleNewTopicForm();
        },
        error: (error) => {
          console.error('Error al crear el tema:', error);
        }
      });
    }
  }
  
  toggleUploadForm(): void {
    this.showUploadForm = !this.showUploadForm;
  }
  
  uploadDocument(topicId: string): void {
    // Aquí iría la lógica para subir documentos
    // Por ahora, simularemos que se agregó un nuevo documento
    const newDoc: Document = {
      id: Date.now().toString(),
      name: 'Nuevo Documento',
      type: 'pdf',
      size: '1.2 MB',
      uploadDate: new Date(),
      topicId: topicId
    };
    
    // Inicializar el array de documentos para el tema si no existe
    if (!this.documentsMap[topicId]) {
      this.documentsMap[topicId] = [];
    }
    
    // Agregar el documento al mapa y actualizar la lista actual
    this.documentsMap[topicId].push(newDoc);
    if (this.selectedTopicId === topicId) {
      this.documents = this.documentsMap[topicId];
    }
    
    // Actualizar el contador de documentos del tema
    const topic = this.topics.find(t => t.id === topicId);
    if (topic) {
      topic.documentCount++;
    }
  }
  
  getFilteredStudents(): Student[] {
    if (!this.searchTerm.trim()) return this.students;
    const term = this.searchTerm.toLowerCase();
    return this.students.filter(student => 
      student.name.toLowerCase().includes(term) || 
      student.email.toLowerCase().includes(term)
    );
  }
}
