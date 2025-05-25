export interface LastMessage {
  text: string;
  is_bot: boolean;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id?: number; 
  subject_id?: number;
  user_role?: string;
  created_at: string;
  title?: string;
  pinned?: boolean;
  last_message?: string | LastMessage;
  messages?: Message[]; // Opcional, para mantener compatibilidad con el código existente
}

export interface Message {
  id: number;
  conversation_id: number;
  text: string;
  is_bot: boolean;
  created_at: string;
}
