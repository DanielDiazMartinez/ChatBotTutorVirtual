import { Document as ApiDocument } from '../../../core/models/document.model';

export interface DocumentUI {
  id: string;
  title: string;
  topic: string;
  type: 'pdf' | 'image';
  url: string;
  uploadDate: Date;
}

export interface DocumentTopic {
  name: string;
  documents: DocumentUI[];
}

// Clase adaptadora para convertir documentos del API al formato de la UI
export class DocumentAdapter {
  static toDocumentUI(apiDocument: ApiDocument): DocumentUI {
    return {
      id: apiDocument.id.toString(),
      title: apiDocument.title,
      topic: apiDocument.subject,
      type: apiDocument.type || 'pdf',
      url: apiDocument.url || '',
      uploadDate: new Date(apiDocument.created_at)
    };
  }
}
