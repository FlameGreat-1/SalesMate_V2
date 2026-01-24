'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { Spinner } from '@/components/ui/Spinner';

export default function HomePage() {
  const { isAuthenticated, isLoading, profile } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else if (!profile?.budget_min || !profile?.budget_max || profile.preferred_categories.length === 0) {
        router.push('/preferences');
      } else {
        router.push('/chat');
      }
    }
  }, [isAuthenticated, isLoading, profile, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Spinner size="lg" />
    </div>
  );
}
