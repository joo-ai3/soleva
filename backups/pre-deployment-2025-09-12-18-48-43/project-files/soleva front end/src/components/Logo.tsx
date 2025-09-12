import React from 'react';
import { Link } from 'react-router-dom';

interface LogoProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
}

export default function Logo({ className = '', size = 'medium' }: LogoProps) {
  const sizeClasses = {
    small: 'h-8 sm:h-10',
    medium: 'h-10 sm:h-12', 
    large: 'h-12 sm:h-16'
  };

  return (
    <Link to="/" className={`flex items-center ${className}`}>
      <div className="logo-container flex items-center">
        <img 
          src="/logo.png" 
          alt="Soleva - Premium Egyptian Footwear Store Logo" 
          className={`${sizeClasses[size]} w-auto transition-all duration-300 hover:scale-105 drop-shadow-sm object-contain`}
          loading="eager"
          decoding="async"
          width="auto"
          height={size === 'small' ? '40' : size === 'medium' ? '48' : '64'}
        />
      </div>
    </Link>
  );
}