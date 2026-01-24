'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ConversationItem } from './ConversationItem';
import { Spinner } from '@/components/ui/Spinner';
import { useConversations, useConversationDetail } from '@/lib/hooks/useConversations';
import { useChat } from '@/lib/hooks/useChat';

export function ConversationList() {
  const { conversations, isLoading, error, hasMore, loadMore, reset } = useConversations();
  const { currentConversation, setConversation } = useChat();
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const hasNavigated = useRef(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const topRef = useRef<HTMLDivElement>(null);
  
  const { conversation: detailConversation, messages, isLoading: isLoadingDetail } = useConversationDetail(selectedId);

  // Reset to 10 when scrolling back to top
  useEffect(() => {
    const handleScroll = () => {
      if (!topRef.current) return;
      
      const rect = topRef.current.getBoundingClientRect();
      
      // If top element is visible (back at top), reset to 10
      if (rect.top >= 0 && rect.top <= 100) {
        reset();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [reset]);

  // Auto-load more when scrolling down
  useEffect(() => {
    if (!hasMore || isLoading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading, loadMore]);

  useEffect(() => {
    if (detailConversation && messages && !isLoadingDetail && !hasNavigated.current) {
      setConversation(detailConversation, messages);
      hasNavigated.current = true;
      router.push('/chat');
    }
  }, [detailConversation, messages, isLoadingDetail, setConversation, router]);

  const handleConversationClick = (conversationId: string) => {
    hasNavigated.current = false;
    setSelectedId(conversationId);
  };

  if (isLoading && conversations.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-400">Failed to load conversations</p>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-glass border border-purple-structural flex items-center justify-center">
          <svg className="w-8 h-8 text-purple-structural" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          No conversations yet
        </h3>
        <p className="text-text-secondary">
          Start a new conversation to see your history here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div ref={topRef} className="h-0" />
      {conversations.map((conversation) => (
        <ConversationItem
          key={conversation.id}
          conversation={conversation}
          isActive={currentConversation?.id === conversation.id}
          onClick={() => handleConversationClick(conversation.id)}
        />
      ))}
      
      {hasMore && (
        <div ref={loadMoreRef} className="flex justify-center py-4">
          <Spinner size="sm" />
        </div>
      )}
    </div>
  );
}
