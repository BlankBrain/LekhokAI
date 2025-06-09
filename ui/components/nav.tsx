'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import Image from 'next/image';
import { useState } from 'react';

export function Nav() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Home' },
    { href: '/generate', label: 'Generate Story' },
    { href: '/characters', label: 'Characters' },
    { href: '/history', label: 'History' },
    { href: '/analytics', label: 'Analytics' },
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <nav className="sticky top-0 z-40 w-full glass shadow-glass border-b border-white/30 backdrop-blur-glass">
      <div className="container mx-auto px-6 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3 group focus:outline-none">
          <LogoWithFallback />
          <span 
            className="text-2xl font-bold tracking-tight transition-colors duration-200"
            style={{ 
              color: '#22345C',
              '--hover-color': '#E6A426'
            } as React.CSSProperties & { '--hover-color': string }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#E6A426';
              const aiSpan = e.currentTarget.querySelector('span');
              if (aiSpan) aiSpan.style.color = '#22345C';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '#22345C';
              const aiSpan = e.currentTarget.querySelector('span');
              if (aiSpan) aiSpan.style.color = '#E6A426';
            }}
          >
            Karigor<span 
              className="font-black transition-colors duration-200"
              style={{ color: '#E6A426' }}
            >AI</span>
          </span>
        </Link>
        <div className="flex space-x-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                'text-sm font-semibold transition-colors hover:text-gold',
                pathname === link.href ? 'text-techno underline underline-offset-4' : 'text-techno/80'
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

function LogoWithFallback() {
  const [imgError, setImgError] = useState(false);
  if (imgError) {
    return (
      <div className="w-10 h-10 flex items-center justify-center bg-techno/10 rounded-md text-techno font-bold text-lg">
        KAI
      </div>
    );
  }
  return (
    <Image
      src="/logo.png"
      alt="KarigorAI Logo"
      width={40}
      height={40}
      className="rounded-md bg-white object-contain"
      onError={() => setImgError(true)}
      priority
    />
  );
} 