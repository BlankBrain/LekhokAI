'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import Image from 'next/image';
import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { User, LogOut, Settings, ChevronDown, Shield } from 'lucide-react';

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const publicLinks = [
    { href: '/', label: 'Home' }
  ];

  const protectedLinks = [
    { href: '/generate', label: 'Generate Story' },
    { href: '/characters', label: 'Characters' },
    { href: '/history', label: 'History' },
    { href: '/analytics', label: 'Analytics' },
    { href: '/settings', label: 'Settings' },
  ];

  const handleLogout = async () => {
    try {
      await logout();
      setShowUserMenu(false);
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Fixed logo click handler to ensure proper navigation
  const handleLogoClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowUserMenu(false); // Close any open menus
    router.push('/');
  };

  return (
    <nav className="sticky top-0 z-50 w-full glass shadow-glass border-b border-white/30 backdrop-blur-glass">
      <div className="container mx-auto px-6 py-3 flex items-center justify-between">
        {/* Fixed Logo Navigation */}
        <div 
          onClick={handleLogoClick}
          className="flex items-center space-x-3 group cursor-pointer focus:outline-none"
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              handleLogoClick(e as any);
            }
          }}
        >
          <LogoWithFallback />
          <span 
            className="text-2xl font-bold tracking-tight transition-colors duration-200 select-none"
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
        </div>

        <div className="flex items-center space-x-6">
          {/* Public Navigation Links */}
          {publicLinks.map((link) => (
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

          {/* Protected Navigation Links - Only show if authenticated */}
          {isAuthenticated && (
            <>
              {protectedLinks.map((link) => (
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

              {/* Profile Link */}
              <Link
                href="/profile"
                className={cn(
                  'text-sm font-semibold transition-colors hover:text-gold',
                  pathname === '/profile' ? 'text-techno underline underline-offset-4' : 'text-techno/80'
                )}
              >
                Profile
              </Link>
            </>
          )}

          {/* Authentication Section */}
          {isAuthenticated ? (
            /* User Menu */
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-lg px-3 py-2 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-techno to-gold rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-techno">{user?.full_name || user?.username}</p>
                  <p className="text-xs text-techno/60 capitalize">{user?.role?.replace('_', ' ')}</p>
                </div>
                <ChevronDown className="w-4 h-4 text-techno/60" />
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={cn(
                        'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        user?.is_approved 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      )}>
                        {user?.is_approved ? 'Approved' : 'Pending'}
                      </span>
                      {user?.role === 'super_admin' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          <Shield className="w-3 h-3 mr-1" />
                          Admin
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <Link
                    href="/profile"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <User className="w-4 h-4 mr-3" />
                    Profile & Settings
                  </Link>
                  
                  <Link
                    href="/settings"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Settings className="w-4 h-4 mr-3" />
                    App Settings
                  </Link>
                  
                  <div className="border-t border-gray-100 my-1"></div>
                  
                  <button
                    onClick={handleLogout}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4 mr-3" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* Sign In Button */
            <Link
              href="/auth"
              className="bg-gradient-to-r from-techno to-gold hover:from-techno/90 hover:to-gold/90 text-white px-6 py-2 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>

      {/* Click outside to close user menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
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