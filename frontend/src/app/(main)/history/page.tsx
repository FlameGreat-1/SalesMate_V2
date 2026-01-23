'use client';

import { ConversationList } from '@/components/history/ConversationList';
import { useConversations } from '@/lib/hooks/useConversations';
import { useChat } from '@/lib/hooks/useChat';
import { Button } from '@/components/ui/Button';
import { useRouter } from 'next/navigation';

export default function HistoryPage() {
  const { total } = useConversations();
  const { startConversation } = useChat();
  const router = useRouter();

  const handleNewChat = async () => {
    try {
      await startConversation();
      router.push('/chat');
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gradient mb-2">
              Conversation History
            </h1>
            <p className="text-text-secondary">
              {total > 0 ? `${total} conversation${total !== 1 ? 's' : ''}` : 'No conversations yet'}
            </p>
          </div>
          <Button variant="primary" onClick={handleNewChat}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New
          </Button>
        </div>

        <ConversationList />
      </div>
    </div>
  );
}
