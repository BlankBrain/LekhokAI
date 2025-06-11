"use client"

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { 
  Mail, 
  CheckCircle2,
  Loader2,
  AlertCircle,
  ArrowRight
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [token, setToken] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isVerified, setIsVerified] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const verificationToken = searchParams.get('token')
    if (verificationToken) {
      setToken(verificationToken)
      verifyEmail(verificationToken)
    } else {
      setError('No verification token provided')
      setIsLoading(false)
    }
  }, [searchParams])

  const verifyEmail = async (verificationToken: string) => {
    try {
      const response = await fetch(`${API_BASE}/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: verificationToken }),
      })

      const data = await response.json()

      if (response.ok) {
        setIsVerified(true)
        // Redirect to auth page with success message after 3 seconds
        setTimeout(() => {
          router.push('/auth?verified=true')
        }, 3000)
      } else {
        setError(data.detail || 'Email verification failed')
      }
    } catch (error) {
      console.error('Email verification error:', error)
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Verifying Your Email
          </h2>
          <p className="text-gray-600">
            Please wait while we verify your email address...
          </p>
        </div>
      </div>
    )
  }

  // Success state
  if (isVerified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Email Verified Successfully!
          </h1>
          
          <p className="text-gray-600 mb-6">
            Your email address has been verified. You can now sign in to your account.
          </p>
          
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              You will be automatically redirected to the sign-in page in a few seconds...
            </p>
            
            <Link
              href="/auth"
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              Continue to Sign In
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Email Verification Failed
        </h1>
        
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {error || 'The verification link is invalid or has expired.'}
          </AlertDescription>
        </Alert>
        
        <div className="space-y-3">
          <Link
            href="/auth"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
          >
            Back to Sign In
          </Link>
          
          <p className="text-sm text-gray-600">
            Need help? Contact support or try requesting a new verification email.
          </p>
        </div>
      </div>
    </div>
  )
} 