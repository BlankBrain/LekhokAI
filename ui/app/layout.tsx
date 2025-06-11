import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Nav } from '../components/nav';
import { Toaster } from 'sonner';
import ErrorBoundary from '../components/ErrorBoundary';
import { AuthProvider } from '../lib/auth';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'KarigorAI - AI Story Generator',
  description: 'Generate stories with AI characters - Professional storytelling platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>
        <ErrorBoundary>
          <AuthProvider>
            <Nav />
            <ErrorBoundary fallback={
              <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
                <div className="bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 p-6 text-center">
                  <p className="text-white">Failed to load page content. Please refresh the page.</p>
                </div>
              </div>
            }>
              {children}
            </ErrorBoundary>
            <Toaster />
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
} 