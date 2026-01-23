'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { ChatProvider, useChat } from '@/context/ChatContext';
import { Spinner } from '@/components/ui/Spinner';

function Navigation() {
  const { closeConversation, currentConversation } = useChat();
  const router = useRouter();
  const pathname = usePathname();

  const handleHistoryClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (currentConversation) {
      await closeConversation();
    }
    router.push('/history');
  };

  return (
    <nav className="flex items-center gap-6">
      <a
        href="/chat"
        className={`transition-colors duration-200 ${
          pathname === '/chat'
            ? 'text-text-primary'
            : 'text-text-secondary hover:text-text-primary'
        }`}
      >
        Chat
      </a>
      <a
        href="/history"
        onClick={handleHistoryClick}
        className={`transition-colors duration-200 ${
          pathname === '/history'
            ? 'text-text-primary'
            : 'text-text-secondary hover:text-text-primary'
        }`}
      >
        History
      </a>
    </nav>
  );
}

function LayoutContent({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-purple-structural backdrop-blur-md bg-black/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-structural flex items-center justify-center">
                <span className="text-white font-bold text-lg leading-none">S</span>
              </div>
            </div>

            <Navigation />
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>
    </div>
  );
}

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <ChatProvider>
      <LayoutContent>{children}</LayoutContent>
    </ChatProvider>
  );
}
