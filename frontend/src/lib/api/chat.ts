import apiClient from './client';
import { API_CONFIG, API_ENDPOINTS } from './config';
import { storage } from '../utils/storage';
import type {
  StartConversationResponse,
  SendMessageRequest,
  SendMessageResponse,
  StreamChunk,
} from '@/types';

export const chatAPI = {
  async startConversation(): Promise<StartConversationResponse> {
    const response = await apiClient.post<StartConversationResponse>(
      API_ENDPOINTS.CHAT.START
    );
    return response.data;
  },

  async sendMessage(data: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await apiClient.post<SendMessageResponse>(
      API_ENDPOINTS.CHAT.MESSAGE,
      data
    );
    return response.data;
  },

  async streamMessage(
    data: SendMessageRequest,
    onChunk: (chunk: string) => void,
    onProduct?: (product: any) => void,
    onError?: (error: string) => void,
    onComplete?: () => void
  ): Promise<void> {
    const token = storage.getToken();
    
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.CHAT.STREAM}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamChunk = JSON.parse(line.slice(6));

              if (data.type === 'chunk' && data.content) {
                onChunk(data.content);
              } else if (data.type === 'product' && data.product && onProduct) {
                onProduct(data.product);
              } else if (data.type === 'complete' && onComplete) {
                onComplete();
              } else if (data.type === 'error' && data.error && onError) {
                onError(data.error);
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', parseError);
            }
          }
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Stream failed';
      if (onError) {
        onError(errorMessage);
      }
      throw error;
    }
  },
};
