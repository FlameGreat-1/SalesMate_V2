export function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-3 max-w-fit glass-card">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-purple-structural rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-purple-structural rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-purple-structural rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm text-text-secondary">Thinking...</span>
    </div>
  );
}
