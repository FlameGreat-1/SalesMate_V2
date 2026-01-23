import { formatRelativeTime } from '@/lib/utils/formatters';
import { Badge } from '@/components/ui/Badge';
import type { Conversation } from '@/types';

interface ConversationItemProps {
  conversation: Conversation;
  isActive?: boolean;
  onClick: () => void;
}

export function ConversationItem({
  conversation,
  isActive = false,
  onClick,
}: ConversationItemProps) {
  const statusVariant = {
    active: 'success' as const,
    completed: 'default' as const,
    abandoned: 'error' as const,
  };

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
        isActive
          ? 'glass-card border-purple-structural-light shadow-glow'
          : 'glass-card hover:border-purple-structural-light hover:shadow-glow-sm'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-sm font-medium text-text-primary truncate">
              Conversation
            </h4>
            <Badge variant={statusVariant[conversation.status as keyof typeof statusVariant]} size="sm">
              {conversation.status}
            </Badge>
          </div>
          <p className="text-xs text-text-muted">
            {formatRelativeTime(conversation.last_activity_at)}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-text-secondary">
        <span>{conversation.message_count} messages</span>
        {conversation.products_discussed.length > 0 && (
          <span>{conversation.products_discussed.length} products</span>
        )}
      </div>

      {conversation.stage && (
        <div className="mt-2 pt-2 border-t border-purple-structural/30">
          <span className="text-xs text-text-muted capitalize">
            Stage: {conversation.stage.replace('_', ' ')}
          </span>
        </div>
      )}
    </div>
  );
}
