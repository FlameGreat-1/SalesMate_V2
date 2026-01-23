'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { chatAPI } from '@/lib/api/chat';
import { storage } from '@/lib/utils/storage';
import type { Conversation, Message, ChatState } from '@/types';

interface ChatContextType extends ChatState {
  startConversation: () => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  streamMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  setConversation: (conversation: Conversation, messages: Message[]) => void;
  closeConversation: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ChatState>({
    currentConversation: null,
    messages: [],
    isStreaming: false,
    isLoading: false,
  });

  const closeConversation = async () => {
    if (!state.currentConversation) return;

    const conversationId = state.currentConversation.id;

    try {
      const token = storage.getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/${conversationId}/close`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to close conversation');
      }

      setState({
        currentConversation: null,
        messages: [],
        isStreaming: false,
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to close conversation:', error);
      setState({
        currentConversation: null,
        messages: [],
        isStreaming: false,
        isLoading: false,
      });
    }
  };

  const startConversation = async () => {
    if (state.currentConversation) {
      await closeConversation();
    }

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await chatAPI.startConversation();

      setState({
        currentConversation: response.conversation,
        messages: response.messages,
        isStreaming: false,
        isLoading: false,
      });
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const sendMessage = async (message: string) => {
    if (!state.currentConversation) {
      throw new Error('No active conversation');
    }

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: state.currentConversation.id,
      role: 'user',
      content: message,
      intent: null,
      metadata: {},
      created_at: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    try {
      const response = await chatAPI.sendMessage({
        message,
        conversation_id: state.currentConversation.id,
      });

      setState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages.filter((m) => m.id !== userMessage.id),
          response.user_message,
          response.assistant_message,
        ],
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        messages: prev.messages.filter((m) => m.id !== userMessage.id),
        isLoading: false,
      }));
      throw error;
    }
  };

  const streamMessage = async (message: string) => {
    if (!state.currentConversation) {
      throw new Error('No active conversation');
    }

    const userMessage: Message = {
      id: `temp-user-${Date.now()}`,
      conversation_id: state.currentConversation.id,
      role: 'user',
      content: message,
      intent: null,
      metadata: {},
      created_at: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      conversation_id: state.currentConversation.id,
      role: 'assistant',
      content: '',
      intent: null,
      metadata: { products: [] },
      created_at: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage, assistantMessage],
      isStreaming: true,
    }));

    try {
      await chatAPI.streamMessage(
        {
          message,
          conversation_id: state.currentConversation.id,
        },
        (chunk: string) => {
          setState((prev) => ({
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === assistantMessage.id
                ? { ...m, content: m.content + chunk }
                : m
            ),
          }));
        },
        (product: any) => {
          setState((prev) => ({
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === assistantMessage.id
                ? {
                    ...m,
                    metadata: {
                      ...m.metadata,
                      products: [...(m.metadata.products || []), product],
                    },
                  }
                : m
            ),
          }));
        },
        (error: string) => {
          console.error('Stream error:', error);
          setState((prev) => ({ ...prev, isStreaming: false }));
        },
        () => {
          setState((prev) => ({ ...prev, isStreaming: false }));
        }
      );
    } catch (error) {
      setState((prev) => ({
        ...prev,
        messages: prev.messages.filter(
          (m) => m.id !== userMessage.id && m.id !== assistantMessage.id
        ),
        isStreaming: false,
      }));
      throw error;
    }
  };

  const clearChat = () => {
    setState({
      currentConversation: null,
      messages: [],
      isStreaming: false,
      isLoading: false,
    });
  };

  const setConversation = (conversation: Conversation, messages: Message[]) => {
    setState({
      currentConversation: conversation,
      messages,
      isStreaming: false,
      isLoading: false,
    });
  };

  return (
    <ChatContext.Provider
      value={{
        ...state,
        startConversation,
        sendMessage,
        streamMessage,
        clearChat,
        setConversation,
        closeConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
}
