export interface LastMessage {
  text: string;
  is_bot: boolean;
  created_at: string;
}

export interface Conversation {
  id: number;
  student_id: number;
  document_id: number;
  created_at: string;
  title?: string;
  pinned?: boolean;
  last_message?: string | LastMessage;
}

export interface Message {
  id: number;
  conversation_id: number;
  text: string;
  is_bot: boolean;
  created_at: string;
}
