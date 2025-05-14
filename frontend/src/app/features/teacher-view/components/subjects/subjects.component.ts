import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, ParamMap, RouterModule } from '@angular/router';

interface Student {
  id: string;
  name: string;
  email: string;
  progress: number;
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
  // Datos de muestra de asignaturas
  subjects = [
    { id: '1', name: 'Matemáticas', description: 'Álgebra, Cálculo y Geometría' },
    { id: '2', name: 'Física', description: 'Mecánica, Electricidad y Termodinámica' },
    { id: '3', name: 'Biología', description: 'Genética, Ecología y Evolución' },
    { id: '4', name: 'Literatura', description: 'Narrativa, Poesía y Teatro' }
  ];
  
  // Asignatura seleccionada actualmente
  subject = {
    id: '1',
    name: 'Matemáticas',
    description: 'Álgebra, Cálculo y Geometría'
  };
  
  constructor(private route: ActivatedRoute) {}
  
  ngOnInit(): void {
    // Si no hay ID en la ruta, cargar la primera asignatura por defecto
    this.students = this.studentsMap['1'] || [];
    this.topics = this.topicsMap['1'] || [];
    
    this.route.paramMap.subscribe((params: ParamMap) => {
      const subjectId = params.get('id');
      if (subjectId) {
        this.loadSubjectDetails(subjectId);
      } else {
        // Si no hay ID en la ruta, intentamos obtener del queryParams
        this.route.queryParamMap.subscribe(queryParams => {
          const subjectName = queryParams.get('name');
          if (subjectName) {
            // Buscar por nombre si está disponible
            const foundSubject = this.subjects.find(s => s.name === subjectName);
            if (foundSubject) {
              this.loadSubjectDetails(foundSubject.id);
            }
          }
        });
      }
    });
  }
  
  loadSubjectDetails(subjectId: string): void {
    // Aquí se cargarían los detalles de la asignatura desde un servicio
    // Por ahora, usamos datos de muestra
    const foundSubject = this.subjects.find(s => s.id === subjectId);
    if (foundSubject) {
      this.subject = foundSubject;
      
      // Cargar estudiantes y temas específicos de la asignatura
      this.students = this.studentsMap[subjectId] || [];
      this.topics = this.topicsMap[subjectId] || [];
      
      // Resetear estados
      this.selectedTopicId = null;
      this.searchTerm = '';
    }
  }
  
  // Datos de muestra de estudiantes por asignatura
  studentsMap: { [key: string]: Student[] } = {
    '1': [
      { id: '1', name: 'Ana García', email: 'ana@example.com', progress: 85 },
      { id: '2', name: 'Carlos López', email: 'carlos@example.com', progress: 72 },
      { id: '3', name: 'María Rodríguez', email: 'maria@example.com', progress: 94 },
      { id: '4', name: 'Pedro Sánchez', email: 'pedro@example.com', progress: 65 },
      { id: '5', name: 'Laura Martínez', email: 'laura@example.com', progress: 88 }
    ],
    '2': [
      { id: '6', name: 'Javier Ruiz', email: 'javier@example.com', progress: 79 },
      { id: '7', name: 'Elena Gómez', email: 'elena@example.com', progress: 88 },
      { id: '8', name: 'Miguel Torres', email: 'miguel@example.com', progress: 62 },
      { id: '9', name: 'Sofía Navarro', email: 'sofia@example.com', progress: 95 }
    ],
    '3': [
      { id: '10', name: 'Daniel Pérez', email: 'daniel@example.com', progress: 77 },
      { id: '11', name: 'Lucía Fernández', email: 'lucia@example.com', progress: 91 },
      { id: '12', name: 'Roberto Díaz', email: 'roberto@example.com', progress: 84 }
    ],
    '4': [
      { id: '13', name: 'Carmen Vega', email: 'carmen@example.com', progress: 82 },
      { id: '14', name: 'Jorge Medina', email: 'jorge@example.com', progress: 75 },
      { id: '15', name: 'Alicia Ramos', email: 'alicia@example.com', progress: 89 },
      { id: '16', name: 'Pablo Ortiz', email: 'pablo@example.com', progress: 71 }
    ]
  };
  
  // Datos de muestra de temas por asignatura
  topicsMap: { [key: string]: Topic[] } = {
    '1': [
      { id: '1', name: 'Álgebra Lineal', description: 'Sistemas de ecuaciones y matrices', documentCount: 3 },
      { id: '2', name: 'Cálculo Diferencial', description: 'Derivadas y aplicaciones', documentCount: 5 },
      { id: '3', name: 'Geometría Analítica', description: 'Coordenadas y vectores', documentCount: 2 }
    ],
    '2': [
      { id: '4', name: 'Mecánica Clásica', description: 'Leyes de Newton y aplicaciones', documentCount: 4 },
      { id: '5', name: 'Electromagnetismo', description: 'Campo eléctrico y magnético', documentCount: 3 },
      { id: '6', name: 'Termodinámica', description: 'Energía y entropía', documentCount: 2 }
    ],
    '3': [
      { id: '7', name: 'Genética', description: 'Leyes de Mendel y herencia', documentCount: 5 },
      { id: '8', name: 'Ecología', description: 'Ecosistemas y biodiversidad', documentCount: 4 },
      { id: '9', name: 'Evolución', description: 'Selección natural y adaptación', documentCount: 3 }
    ],
    '4': [
      { id: '10', name: 'Narrativa', description: 'Análisis de novelas y cuentos', documentCount: 6 },
      { id: '11', name: 'Poesía', description: 'Métrica y recursos literarios', documentCount: 4 },
      { id: '12', name: 'Teatro', description: 'Obras dramáticas y representación', documentCount: 5 }
    ]
  };
  
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
    // Cargar documentos para el tema seleccionado
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
    if (this.newTopicName.trim()) {
      const newTopic: Topic = {
        id: Date.now().toString(),
        name: this.newTopicName,
        description: this.newTopicDescription || 'Sin descripción',
        documentCount: 0
      };
      this.topics.push(newTopic);
      this.toggleNewTopicForm();
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
