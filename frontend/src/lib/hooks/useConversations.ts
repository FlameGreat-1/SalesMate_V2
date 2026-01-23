'use client';

import { useQuery } from '@tanstack/react-query';
import { historyAPI } from '@/lib/api/history';
import { useAuth } from './useAuth';

const QUERY_KEYS = {
  conversations: ['conversations'] as const,
  active: ['conversations', 'active'] as const,
  detail: (id: string) => ['conversations', id] as const,
};

export function useConversations() {
  const { isAuthenticated } = useAuth();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: QUERY_KEYS.conversations,
    queryFn: async () => {
      const response = await historyAPI.getConversations();
      return response;
    },
    enabled: isAuthenticated,
    staleTime: 2 * 60 * 1000,
    gcTime: 5 * 60 * 1000,
    refetchInterval: 30 * 1000,
  });

  return {
    conversations: data?.conversations || [],
    total: data?.total || 0,
    isLoading,
    error,
    refetch,
  };
}

export function useActiveConversation(enabled: boolean = true) {
  const { isAuthenticated } = useAuth();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: QUERY_KEYS.active,
    queryFn: async () => {
      const response = await historyAPI.getActiveConversation();
      return response;
    },
    enabled: isAuthenticated && enabled,
    staleTime: 1 * 60 * 1000,
    gcTime: 3 * 60 * 1000,
    retry: 1,
  });

  return {
    conversation: data?.conversation || null,
    messages: data?.messages || [],
    products: data?.products_discussed || [],
    isLoading,
    error,
    refetch,
  };
}

export function useConversationDetail(id: string | null) {
  const { isAuthenticated } = useAuth();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: QUERY_KEYS.detail(id || ''),
    queryFn: async () => {
      if (!id) throw new Error('No conversation ID');
      const response = await historyAPI.getConversationById(id);
      return response;
    },
    enabled: isAuthenticated && !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  return {
    conversation: data?.conversation || null,
    messages: data?.messages || [],
    products: data?.products_discussed || [],
    isLoading,
    error,
    refetch,
  };
}
