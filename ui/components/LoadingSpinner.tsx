"use client";

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
  className?: string;
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  className = '',
  text
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'text-blue-500',
    secondary: 'text-gray-500',
    white: 'text-white'
  };

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <Loader2 
        className={`animate-spin ${sizeClasses[size]} ${colorClasses[variant]}`}
      />
      {text && (
        <span className={`text-sm ${colorClasses[variant]}`}>
          {text}
        </span>
      )}
    </div>
  );
};

export default LoadingSpinner; 