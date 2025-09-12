import React from 'react';
import clsx from 'clsx';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'compact' | 'spacious';
  hover?: boolean;
  modern?: boolean;
}

export default function GlassCard({ 
  children, 
  className = '',
  variant = 'default',
  hover = true,
  modern = false
}: GlassCardProps) {
  const variantClasses = {
    default: 'card',
    compact: 'card card-compact',
    spacious: 'card card-spacious'
  };

  return (
    <div 
      className={clsx(
        modern ? 'modern-glass-card' : variantClasses[variant],
        {
          'hover:transform hover:scale-[1.02]': hover
        },
        className
      )}
    >
      {children}
    </div>
  );
}