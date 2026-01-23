import apiClient from './client';
import { API_ENDPOINTS } from './config';
import type {
  ConversationListResponse,
  ConversationDetailResponse,
} from '@/types';

export const historyAPI = {
  async getConversations(): Promise<ConversationListResponse> {
    const response = await apiClient.get<ConversationListResponse>(
      API_ENDPOINTS.HISTORY.CONVERSATIONS
    );
    return response.data;
  },

  async getActiveConversation(): Promise<ConversationDetailResponse> {
    const response = await apiClient.get<ConversationDetailResponse>(
      API_ENDPOINTS.HISTORY.ACTIVE
    );
    return response.data;
  },

  async getConversationById(id: string): Promise<ConversationDetailResponse> {
    const response = await apiClient.get<ConversationDetailResponse>(
      API_ENDPOINTS.HISTORY.DETAIL(id)
    );
    return response.data;
  },
};
