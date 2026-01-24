'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { historyAPI } from '@/lib/api/history';
import { useAuth } from './useAuth';

const QUERY_KEYS = {
  conversations: ['conversations'] as const,
  active: ['conversations', 'active'] as const,
  detail: (id: string) => ['conversations', id] as const,
};

const CONVERSATIONS_PER_PAGE = 10;

export function useConversations() {
  const { isAuthenticated } = useAuth();
  const [displayCount, setDisplayCount] = useState(CONVERSATIONS_PER_PAGE);

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

  const allConversations = data?.conversations || [];
  
  const displayedConversations = useMemo(() => {
    return allConversations.slice(0, displayCount);
  }, [allConversations, displayCount]);

  const hasMore = displayCount < allConversations.length;

  const loadMore = () => {
    setDisplayCount(prev => prev + CONVERSATIONS_PER_PAGE);
  };

  const reset = () => {
    setDisplayCount(CONVERSATIONS_PER_PAGE);
  };

  return {
    conversations: displayedConversations,
    total: allConversations.length,
    isLoading,
    error,
    refetch,
    hasMore,
    loadMore,
    reset,
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
