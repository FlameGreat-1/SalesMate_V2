import { formatRelativeTime } from '@/lib/utils/formatters';
import { ProductCard } from './ProductCard';
import type { Message } from '@/types';

interface ChatBubbleProps {
  message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user';
  const products = message.metadata?.products || [];

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-slide-up`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-purple-structural text-white'
              : 'glass-card text-text-primary'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {!isUser && products.length > 0 && (
          <div className="mt-3 space-y-2">
            {products.map((product: any, index: number) => (
              <ProductCard key={product.id || index} product={product} />
            ))}
          </div>
        )}

        <div className={`mt-1 px-2 ${isUser ? 'text-right' : 'text-left'}`}>
          <span className="text-xs text-text-muted">
            {formatRelativeTime(message.created_at)}
          </span>
        </div>
      </div>
    </div>
  );
}
