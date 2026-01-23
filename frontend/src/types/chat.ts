export interface Conversation {
  id: string;
  user_id: string;
  status: string;
  stage: string;
  context: Record<string, any>;
  products_discussed: string[];
  started_at: string;
  ended_at: string | null;
  last_activity_at: string;
  message_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  intent: string | null;
  metadata: Record<string, any>;
  created_at: string;
}

export interface StartConversationResponse {
  conversation: Conversation;
  messages: Message[];
  products_discussed: string[];
}

export interface SendMessageRequest {
  message: string;
  conversation_id: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  user_message: Message;
  assistant_message: Message;
  products: any[];
  intent: string;
  stage: string;
}

export interface StreamChunk {
  type: 'chunk' | 'product' | 'complete' | 'error';
  content?: string;
  product?: any;
  error?: string;
  conversation_id?: string;
  message_id?: string;
  intent?: string;
  stage?: string;
  products?: string[];
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

export interface ConversationDetailResponse {
  conversation: Conversation;
  messages: Message[];
  products_discussed: any[];
}

export interface ChatState {
  currentConversation: Conversation | null;
  messages: Message[];
  isStreaming: boolean;
  isLoading: boolean;
}
