export interface Document {
  id: string;
  title: string;
  topic: string;
  type: 'pdf' | 'image';
  url: string;
  uploadDate: Date;
}

export interface DocumentTopic {
  name: string;
  documents: Document[];
}
