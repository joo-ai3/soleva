import React from 'react';

interface SectionTitleProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
  role?: string;
  'aria-level'?: number;
}

export default function SectionTitle({ children, className = "", id, role = "heading", ...props }: SectionTitleProps) {
  return (
    <h2 
      id={id}
      role={role}
      aria-level={props['aria-level'] || 2}
      className={`text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-6 sm:mb-8 md:mb-10 tracking-tight text-text-primary leading-tight text-center ${className}`}
    >
      {children}
    </h2>
  );
}