"use client"

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Mail, 
  Lock, 
  User, 
  Building, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'

interface FormData {
  email: string
  password: string
  username?: string
  full_name?: string
  organization_name?: string
  accept_terms?: boolean
  accept_privacy?: boolean
}

export default function AuthPage() {
  const { login, register, isAuthenticated, isLoading, error, clearError } = useAuth()
  const router = useRouter()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    username: '',
    full_name: '',
    organization_name: '',
    accept_terms: false,
    accept_privacy: false,
  })
  const [localLoading, setLocalLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false)
  const [showResendVerification, setShowResendVerification] = useState(false)

  // Check for verification success from URL params
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('verified') === 'true') {
      setSuccessMessage('Email verified successfully! You can now sign in.')
    }
  }, [])

  // Redirect if already authenticated - FIXED to prevent infinite loops
  useEffect(() => {
    if (!isLoading) {
      setHasCheckedAuth(true)
      if (isAuthenticated) {
        router.push('/generate')
      }
    }
  }, [isAuthenticated, isLoading, router])

  // Clear error when switching modes
  useEffect(() => {
    clearError()
    setSuccessMessage('')
    setShowResendVerification(false)
  }, [mode, clearError])

  // Show loading while checking authentication
  if (!hasCheckedAuth && isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    )
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const resendVerificationEmail = async () => {
    if (!formData.email) {
      alert('Please enter your email address first')
      return
    }

    setLocalLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/resend-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: formData.email }),
      })

      const data = await response.json()

      if (response.ok) {
        setSuccessMessage('Verification email sent! Please check your inbox and spam folder.')
        setShowResendVerification(false)
      } else {
        console.error('Resend verification error:', data.detail)
      }
    } catch (error) {
      console.error('Network error:', error)
    } finally {
      setLocalLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalLoading(true)
    clearError()
    setShowResendVerification(false)

    try {
      if (mode === 'login') {
        await login({
          email: formData.email,
          password: formData.password
        })
        // Router will handle redirect via useEffect above
      } else {
        if (!formData.accept_terms || !formData.accept_privacy) {
          throw new Error('Please accept the terms of service and privacy policy')
        }

        const result = await register({
          email: formData.email,
          password: formData.password,
          username: formData.username!,
          full_name: formData.full_name!,
          organization_name: formData.organization_name,
          accept_terms: formData.accept_terms,
          accept_privacy: formData.accept_privacy
        })

        // Handle different response actions
        if (result?.action === 'redirect_to_login') {
          setSuccessMessage('User already exists. Please login below.')
          setMode('login')
          setFormData(prev => ({
            ...prev,
            password: '',
            username: '',
            full_name: '',
            organization_name: '',
            accept_terms: false,
            accept_privacy: false,
          }))
        } else if (result?.action === 'verification_resent') {
          setSuccessMessage('Verification email has been resent. Please check your inbox.')
          setMode('login')
          setFormData(prev => ({
            ...prev,
            password: '',
            username: '',
            full_name: '',
            organization_name: '',
            accept_terms: false,
            accept_privacy: false,
          }))
        } else {
          // Default success case
          setSuccessMessage('Account created successfully! Please check your email for verification.')
          setMode('login')
          setFormData({
            email: formData.email,
            password: '',
            username: '',
            full_name: '',
            organization_name: '',
            accept_terms: false,
            accept_privacy: false,
          })
        }
      }
    } catch (err: any) {
      console.error('Auth error:', err)
      // Show resend verification option if email not verified
      if (mode === 'login' && err.message && err.message.includes('not verified')) {
        setShowResendVerification(true)
      }
    } finally {
      setLocalLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    try {
      // Get Google OAuth URL from backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/google`)
      const data = await response.json()
      
      if (response.ok && data.auth_url) {
        // Redirect to Google OAuth
        window.location.href = data.auth_url
      } else {
        throw new Error(data.detail || 'Failed to initiate Google sign-in')
      }
    } catch (error) {
      console.error('Google sign-in error:', error)
      // You might want to show an error message to the user here
    }
  }

  const isFormValid = () => {
    if (mode === 'login') {
      return formData.email && formData.password
    } else {
      return (
        formData.email &&
        formData.password &&
        formData.username &&
        formData.full_name &&
        formData.accept_terms &&
        formData.accept_privacy
      )
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-full flex items-center justify-center mb-6">
            <User className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {mode === 'login' 
              ? 'Sign in to continue using KarigorAI' 
              : 'Join KarigorAI to start creating amazing stories'
            }
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {successMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Error Message */}
        {error && (
          <div className="space-y-3">
            <Alert className="bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
            
            {/* Show resend verification option for email verification errors */}
            {showResendVerification && (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">
                  Haven't received the verification email?
                </p>
                <button
                  onClick={resendVerificationEmail}
                  disabled={localLoading}
                  className="text-sm text-indigo-600 hover:text-indigo-500 underline disabled:opacity-50"
                >
                  {localLoading ? 'Sending...' : 'Resend verification email'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Auth Form */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
          {/* Mode Toggle */}
          <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                mode === 'login'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                mode === 'register'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {/* Registration Fields */}
            {mode === 'register' && (
              <>
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      value={formData.username}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Choose a username"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      id="full_name"
                      name="full_name"
                      type="text"
                      required
                      value={formData.full_name}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter your full name"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="organization_name" className="block text-sm font-medium text-gray-700 mb-1">
                    Organization (Optional)
                  </label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      id="organization_name"
                      name="organization_name"
                      type="text"
                      value={formData.organization_name}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter your organization name"
                    />
                  </div>
                </div>
              </>
            )}

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {/* Forgot Password Link - Only show in login mode */}
              {mode === 'login' && (
                <div className="text-right mt-2">
                  <Link
                    href="/auth/forgot-password"
                    className="text-sm text-indigo-600 hover:text-indigo-700 transition-colors"
                  >
                    Forgot your password?
                  </Link>
                </div>
              )}
            </div>

            {/* Terms and Privacy for Registration */}
            {mode === 'register' && (
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="accept_terms"
                    name="accept_terms"
                    checked={formData.accept_terms}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({ ...prev, accept_terms: checked as boolean }))
                    }
                  />
                  <label htmlFor="accept_terms" className="text-sm text-gray-600">
                    I agree to the{' '}
                    <Link href="/terms" className="text-indigo-600 hover:text-indigo-500">
                      Terms of Service
                    </Link>
                  </label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="accept_privacy"
                    name="accept_privacy"
                    checked={formData.accept_privacy}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({ ...prev, accept_privacy: checked as boolean }))
                    }
                  />
                  <label htmlFor="accept_privacy" className="text-sm text-gray-600">
                    I agree to the{' '}
                    <Link href="/privacy" className="text-indigo-600 hover:text-indigo-500">
                      Privacy Policy
                    </Link>
                  </label>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!isFormValid() || localLoading || isLoading}
              className="w-full flex items-center justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {localLoading || isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <ArrowRight className="w-4 h-4 mr-2" />
              )}
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>
          </div>

          {/* Google Sign-In */}
          <button
            onClick={handleGoogleSignIn}
            type="button"
            className="w-full mt-4 flex items-center justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </button>
        </div>

        {/* Back to Home */}
        <div className="text-center">
          <Link
            href="/"
            className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
          >
            ← Back to Homepage
          </Link>
        </div>
      </div>
    </div>
  )
} 