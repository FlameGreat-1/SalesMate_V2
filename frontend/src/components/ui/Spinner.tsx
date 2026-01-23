interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const containerSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-10 h-10',
  };

  const textSizes = {
    sm: 'text-[8px]',
    md: 'text-xs',
    lg: 'text-base',
  };

  const roundedSizes = {
    sm: 'rounded-sm',
    md: 'rounded',
    lg: 'rounded-md',
  };

  return (
    <div
      className={`inline-flex ${className}`}
      role="status"
      aria-label="Loading"
    >
      <div 
        className={`
          ${containerSizes[size]} 
          ${roundedSizes[size]} 
          bg-purple-structural 
          flex items-center justify-center
          animate-zoom
        `}
      >
        <span className={`text-white font-bold ${textSizes[size]} leading-none`}>
          S
        </span>
      </div>
      <span className="sr-only">Loading...</span>
    </div>
  );
}
