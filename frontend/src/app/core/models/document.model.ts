export interface Document {
  id: number;
  title: string;
  subject: string;
  subject_id: number;
  type: 'pdf' | 'image';
  size: string;
  uploadDate: Date;
  created_at: string;
  status: 'Procesado' | 'Procesando' | 'Error';
  description?: string;
  url?: string;
}
