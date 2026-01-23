'use client';

import { useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { Spinner } from '@/components/ui/Spinner';
import { useChat } from '@/lib/hooks/useChat';

export function ChatWindow() {
  const { messages, isStreaming, isLoading, streamMessage, currentConversation } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    try {
      await streamMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  if (!currentConversation) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-text-secondary">Starting conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-hide">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-glass border border-purple-structural flex items-center justify-center">
                <svg className="w-8 h-8 text-purple-structural" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Welcome to SalesMate AI
              </h3>
              <p className="text-text-secondary">
                Ask me anything about products, and I'll help you find the perfect match!
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatBubble key={message.id} message={message} />
            ))}
            {isStreaming && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="border-t border-purple-structural p-4">
        <ChatInput
          onSend={handleSendMessage}
          disabled={isStreaming || isLoading}
          placeholder="Ask about products..."
        />
      </div>
    </div>
  );
}
