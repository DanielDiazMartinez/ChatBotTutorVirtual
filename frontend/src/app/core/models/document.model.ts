export interface Document {
  id: number;
  title: string;
  subject: string;
  subject_id: number;
  user_id: number; // Usuario que subió el documento
  type: 'pdf' | 'image';
  size: string;
  uploadDate: Date;
  created_at: string;
  status: 'Procesado' | 'Procesando' | 'Error';
  description?: string;
  url?: string;
}
