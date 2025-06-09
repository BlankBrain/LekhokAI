import React, { useState } from 'react';
import { Button } from './button';

interface CopyFieldProps {
  label: string;
  value: string;
  className?: string;
}

export const CopyField: React.FC<CopyFieldProps> = ({ label, value, className }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className={`glass rounded-xl p-4 mb-4 border border-white/20 shadow-glass ${className || ''}`.trim()}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-techno/90">{label}</span>
        <Button size="sm" variant="gold" onClick={handleCopy} type="button">
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>
      <pre className="whitespace-pre-wrap break-words font-mono text-techno/80 bg-transparent p-0 m-0 select-text text-sm min-h-[48px]">
        {value}
      </pre>
    </div>
  );
}; 