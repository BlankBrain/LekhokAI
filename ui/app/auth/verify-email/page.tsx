"use client"

import React, { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Mail,
  ArrowRight
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [isResending, setIsResending] = useState(false)

  const token = searchParams.get('token')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('No verification token provided')
      return
    }

    verifyEmail(token)
  }, [token])

  const verifyEmail = async (verificationToken: string) => {
    try {
      setStatus('loading')
      
      const response = await fetch(`${API_BASE}/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: verificationToken }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus('success')
        setMessage(data.message || 'Email verified successfully!')
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/auth?verified=true')
        }, 3000)
      } else {
        setStatus('error')
        setMessage(data.detail || 'Verification failed')
      }
    } catch (error) {
      console.error('Verification error:', error)
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  const resendVerification = async () => {
    const email = prompt('Please enter your email address to resend verification:')
    if (!email) return

    setIsResending(true)
    try {
      const response = await fetch(`${API_BASE}/auth/resend-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (response.ok) {
        alert('Verification email sent! Please check your inbox.')
      } else {
        alert(data.detail || 'Failed to send verification email')
      }
    } catch (error) {
      console.error('Resend error:', error)
      alert('Network error. Please try again.')
    } finally {
      setIsResending(false)
    }
  }

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
            {status === 'loading' && 'Verifying your email...'}
            {status === 'success' && 'Email verified!'}
            {status === 'error' && 'Verification failed'}
          </h2>
          
          <p className="mt-2 text-sm text-gray-600">
            {status === 'loading' && 'Please wait while we verify your email address'}
            {status === 'success' && 'Your account is now active. Redirecting to sign in...'}
            {status === 'error' && 'There was an issue verifying your email'}
          </p>
        </div>

        {message && (
          <Alert className={status === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}>
            <AlertDescription className={status === 'error' ? 'text-red-800' : 'text-green-800'}>
              {message}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          {status === 'success' && (
            <div className="text-center">
              <Link
                href="/auth"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
              >
                Continue to Sign In
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-3">
              <div className="text-center">
                <button
                  onClick={resendVerification}
                  disabled={isResending}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isResending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Resend Verification Email
                    </>
                  )}
                </button>
              </div>
              
              <div className="text-center">
                <Link
                  href="/auth"
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  Back to Sign In
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Help text */}
        <div className="text-center text-xs text-gray-500">
          <p>Need help? Check your spam folder or contact support.</p>
        </div>
      </div>
    </div>
  )
} 