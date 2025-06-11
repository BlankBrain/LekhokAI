"use client"

import React, { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function GoogleCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { googleCallback } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [debugInfo, setDebugInfo] = useState<any>(null)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code')
        const state = searchParams.get('state')
        const error = searchParams.get('error')
        const errorDescription = searchParams.get('error_description')

        // Debug information
        const debug = {
          code: code ? `${code.substring(0, 10)}...` : 'null',
          state: state ? `${state.substring(0, 10)}...` : 'null',
          error: error,
          errorDescription: errorDescription,
          url: window.location.href
        }
        setDebugInfo(debug)

        if (error) {
          setStatus('error')
          setMessage(`Google OAuth error: ${error}${errorDescription ? ` - ${errorDescription}` : ''}`)
          return
        }

        if (!code) {
          setStatus('error')
          setMessage('No authorization code received from Google')
          return
        }

        // Process the OAuth callback
        const result = await googleCallback(code, state)
        
        if (result.success) {
          setStatus('success')
          setMessage('Successfully signed in with Google!')
          
          // Redirect to dashboard after a brief delay
          setTimeout(() => {
            router.push('/generate')
          }, 2000)
        } else {
          setStatus('error')
          setMessage(result.error || 'Failed to complete Google sign-in')
        }
      } catch (error) {
        console.error('Google callback error:', error)
        setStatus('error')
        
        let errorMessage = 'An unexpected error occurred during sign-in'
        if (error instanceof Error) {
          errorMessage = error.message
        } else if (typeof error === 'string') {
          errorMessage = error
        }
        
        setMessage(errorMessage)
      }
    }

    handleCallback()
  }, [searchParams, googleCallback, router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-full flex items-center justify-center mb-6">
            {status === 'loading' && <Loader2 className="h-8 w-8 text-white animate-spin" />}
            {status === 'success' && <CheckCircle2 className="h-8 w-8 text-white" />}
            {status === 'error' && <XCircle className="h-8 w-8 text-white" />}
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900">
            {status === 'loading' && 'Completing sign-in...'}
            {status === 'success' && 'Sign-in successful!'}
            {status === 'error' && 'Sign-in failed'}
          </h2>
          
          <p className="mt-2 text-sm text-gray-600">
            {status === 'loading' && 'Please wait while we complete your Google sign-in'}
            {status === 'success' && 'Redirecting you to your dashboard...'}
            {status === 'error' && 'There was an issue with your Google sign-in'}
          </p>
        </div>

        {message && (
          <Alert className={status === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}>
            <AlertDescription className={status === 'error' ? 'text-red-800' : 'text-green-800'}>
              {message}
            </AlertDescription>
          </Alert>
        )}

        {/* Debug information in development */}
        {process.env.NODE_ENV === 'development' && debugInfo && (
          <Alert className="bg-blue-50 border-blue-200">
            <AlertDescription className="text-blue-800">
              <strong>Debug Info:</strong>
              <pre className="mt-2 text-xs overflow-auto">
                {JSON.stringify(debugInfo, null, 2)}
              </pre>
            </AlertDescription>
          </Alert>
        )}

        {status === 'error' && (
          <div className="text-center space-y-4">
            <button
              onClick={() => router.push('/auth')}
              className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
            >
              ← Back to sign-in
            </button>
            
            {/* Retry button */}
            <div>
              <button
                onClick={() => {
                  setStatus('loading')
                  setMessage('')
                  window.location.reload()
                }}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 