import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface Document {
  id: string;
  title: string;
  subject: string;
  type: 'pdf' | 'image';
  size: string;
  uploadDate: Date;
  status: 'Procesado' | 'Procesando' | 'Error';
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './documents.component.html',
  styleUrls: ['./documents.component.scss']
})
export class DocumentsComponent {
  @Input() isAdminView = false;
  
  searchQuery: string = '';
  selectedSubject: string = 'Todas';

  documents: Document[] = [
    {
      id: '1',
      title: 'Guía de Álgebra',
      subject: 'Matemáticas',
      type: 'pdf',
      size: '2.4 MB',
      uploadDate: new Date('2025-05-10'),
      status: 'Procesado'
    },
    {
      id: '2',
      title: 'Presentación de Circuitos',
      subject: 'Física',
      type: 'pdf',
      size: '4.7 MB',
      uploadDate: new Date('2025-05-11'),
      status: 'Procesado'
    },
    {
      id: '3',
      title: 'Ejercicios resueltos de derivadas',
      subject: 'Matemáticas',
      type: 'pdf',
      size: '1.2 MB',
      uploadDate: new Date('2025-05-12'),
      status: 'Procesado'
    },
    {
      id: '4',
      title: 'Esquemas de química orgánica',
      subject: 'Química',
      type: 'image',
      size: '0.8 MB',
      uploadDate: new Date('2025-05-14'),
      status: 'Procesando'
    },
    {
      id: '5',
      title: 'Diagrama del sistema circulatorio',
      subject: 'Biología',
      type: 'image',
      size: '3.5 MB',
      uploadDate: new Date('2025-05-15'),
      status: 'Error'
    }
  ];

  subjects = ['Todas', 'Matemáticas', 'Física', 'Química', 'Biología', 'Literatura'];
  
  getIconForType(type: string): string {
    switch(type) {
      case 'pdf': return 'description';
      case 'docx': return 'article';
      case 'ppt': return 'slideshow';
      case 'xlsx': return 'table_chart';
      case 'image': return 'image';
      default: return 'insert_drive_file';
    }
  }

  getStatusClass(status: string): string {
    switch(status) {
      case 'Procesado': return 'processed';
      case 'Procesando': return 'processing';
      case 'Error': return 'error';
      default: return '';
    }
  }

  getFileExtension(type: string): string {
    return `.${type}`;
  }

  uploadDocument(): void {
    console.log('Abrir diálogo para subir documento');
    // Aquí se implementaría la lógica para subir un documento
  }

  deleteDocument(id: string): void {
    this.documents = this.documents.filter(doc => doc.id !== id);
  }

  getFilteredDocuments(): Document[] {
    return this.documents.filter(doc => {
      // Filtro por asignatura
      const matchesSubject = this.selectedSubject === 'Todas' || doc.subject === this.selectedSubject;
      
      // Filtro por búsqueda (título o asignatura)
      const matchesSearch = this.searchQuery === '' || 
        doc.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        doc.subject.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      return matchesSubject && matchesSearch;
    });
  }
}
