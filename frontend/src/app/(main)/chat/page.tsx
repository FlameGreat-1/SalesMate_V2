'use client';

import { useState } from 'react';
import { useChat } from '@/lib/hooks/useChat';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { Button } from '@/components/ui/Button';

export default function ChatPage() {
  const { currentConversation, startConversation } = useChat();
  const [isStarting, setIsStarting] = useState(false);

  const handleStartNewConversation = async () => {
    setIsStarting(true);
    try {
      await startConversation();
    } catch (error) {
      console.error('Failed to start conversation:', error);
    } finally {
      setIsStarting(false);
    }
  };

  if (currentConversation) {
    return (
      <div className="h-[calc(100vh-4rem)]">
        <ChatWindow />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-glass border border-purple-structural flex items-center justify-center">
          <svg className="w-10 h-10 text-purple-structural" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-text-primary mb-3">
          Start a New Conversation
        </h2>
        <p className="text-text-secondary mb-6">
          Ask me anything about products, and I'll help you find exactly what you need.
        </p>
        <Button
          variant="primary"
          size="lg"
          onClick={handleStartNewConversation}
          isLoading={isStarting}
        >
          Start
        </Button>
      </div>
    </div>
  );
}
