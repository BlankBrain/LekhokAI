"use client";

import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  variant?: 'text' | 'card' | 'image' | 'button' | 'avatar';
  lines?: number;
  width?: string;
  height?: string;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  variant = 'text',
  lines = 1,
  width,
  height
}) => {
  const baseClasses = 'animate-pulse bg-gradient-to-r from-gray-300/20 via-gray-200/30 to-gray-300/20 bg-[length:200%_100%] rounded';
  
  const variantStyles = {
    text: 'h-4 w-full',
    card: 'h-32 w-full',
    image: 'h-48 w-full',
    button: 'h-10 w-24',
    avatar: 'h-10 w-10 rounded-full'
  };

  const customStyle = {
    width: width || undefined,
    height: height || undefined
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <div 
            key={index}
            className={`${baseClasses} ${variantStyles.text}`}
            style={index === lines - 1 ? { width: '75%' } : undefined}
          />
        ))}
      </div>
    );
  }

  return (
    <div 
      className={`${baseClasses} ${variantStyles[variant]} ${className}`}
      style={customStyle}
    />
  );
};

// Pre-built skeleton components for common use cases
export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 p-6 ${className}`}>
    <div className="space-y-4">
      <SkeletonLoader variant="text" width="60%" />
      <SkeletonLoader variant="text" lines={3} />
      <div className="flex gap-2">
        <SkeletonLoader variant="button" />
        <SkeletonLoader variant="button" />
      </div>
    </div>
  </div>
);

export const HistoryItemSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 p-4 ${className}`}>
    <div className="flex justify-between items-start mb-3">
      <SkeletonLoader variant="text" width="40%" />
      <SkeletonLoader variant="text" width="20%" />
    </div>
    <SkeletonLoader variant="text" lines={2} className="mb-3" />
    <div className="flex gap-2">
      <SkeletonLoader variant="avatar" />
      <SkeletonLoader variant="text" width="30%" />
    </div>
  </div>
);

export const ImageSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 p-4 ${className}`}>
    <SkeletonLoader variant="image" className="mb-4" />
    <SkeletonLoader variant="text" width="60%" className="mb-2" />
    <SkeletonLoader variant="text" lines={2} />
  </div>
);

export default SkeletonLoader; 