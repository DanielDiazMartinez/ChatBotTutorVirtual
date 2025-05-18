export interface Message {
  id: number;
  conversation_id: number;
  text: string;
  is_bot: boolean;
  created_at?: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  user_role: string;
  document_id: number;
  subject_id?: number;
  messages: Message[];
}

export interface ConversationResponse {
  data: Conversation[];
  message: string;
  status: number;
}

export interface SingleConversationResponse {
  data: Conversation;
  message: string;
  status: number;
}

export interface ConversationWithBotResponse {
  data: {
    conversation: Conversation;
    bot_response: string;
  };
  message: string;
  status: number;
}

export interface MessagePair {
  user_message: Message;
  bot_message: Message;
}

export interface MessagePairResponse {
  data: MessagePair;
  message: string;
  status: number;
}
