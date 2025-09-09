import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  loading?: boolean;
  modern?: boolean;
}

export default function GlassButton({ 
  children, 
  variant = 'secondary',
  size = 'md',
  className = '', 
  loading = false,
  disabled,
  modern = false,
  ...props 
}: GlassButtonProps) {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm min-h-[40px]',
    md: 'px-6 py-3 text-base min-h-[44px]',
    lg: 'px-8 py-4 text-lg min-h-[48px]'
  };

  const variantClasses = {
    primary: 'btn-primary text-[#000000]',
    secondary: modern ? 'modern-glass-button' : 'btn-secondary', 
    ghost: 'btn-ghost'
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
      transition={{ duration: 0.15 }}
      className={clsx(
        'btn',
        variantClasses[variant],
        sizeClasses[size],
        {
          'opacity-50 cursor-not-allowed': disabled || loading,
          'cursor-wait': loading
        },
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </motion.button>
  );
}