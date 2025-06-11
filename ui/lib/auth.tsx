'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'

// Types
export interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: 'general_user' | 'organization_user' | 'super_admin'
  organization_id?: number
  organization_name?: string
  is_active: boolean
  is_approved: boolean
  created_at: string
  last_login?: string
  profile_picture?: string
  preferences?: Record<string, any>
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  username: string
  full_name: string
  organization_name?: string
  accept_terms: boolean
  accept_privacy: boolean
}

export interface RegisterResponse {
  message: string
  user_id?: number
  email_sent?: boolean
  action?: 'registration_complete' | 'verification_resent' | 'redirect_to_login'
  auth_provider?: string
}

// Context
interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<RegisterResponse>
  logout: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  refreshUser: () => Promise<void>
  clearError: () => void
  googleCallback: (code: string, state?: string | null) => Promise<{ success: boolean; error?: string }>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// API Base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Auth Provider Component
interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  })

  // Helper function to make authenticated API calls
  const apiCall = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('auth_token')
    
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...(token && { 'X-Session-Token': token }),
      ...options.headers,
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }, [])

  // Check authentication status on mount
  const checkAuthStatus = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }))
        return
      }

      const response = await apiCall('/auth/profile')
      setState({
        user: response,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error) {
      localStorage.removeItem('auth_token')
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
    }
  }, [apiCall])

  useEffect(() => {
    checkAuthStatus()
  }, [checkAuthStatus])

  const login = useCallback(async (credentials: LoginCredentials) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      localStorage.setItem('auth_token', data.access_token)

      // Get user profile
      const userProfile = await apiCall('/auth/profile')
      
      setState({
        user: userProfile,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      }))
      throw error
    }
  }, [apiCall])

  const register = useCallback(async (data: RegisterData) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          username: data.username,
          full_name: data.full_name,
          organization_name: data.organization_name,
          privacy_policy_accepted: data.accept_privacy,
          terms_of_service_accepted: data.accept_terms,
        }),
      })

      const result = await response.json()

      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 409) {
          // User already exists
          throw new Error(result.detail || 'User already exists. Please login instead.')
        }
        throw new Error(result.detail || 'Registration failed')
      }

      setState(prev => ({ ...prev, isLoading: false }))
      
      // Return the result so the UI can handle different actions
      return result
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      }))
      throw error
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiCall('/auth/logout', { method: 'POST' })
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error)
    } finally {
      localStorage.removeItem('auth_token')
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
    }
  }, [apiCall])

  const updateProfile = useCallback(async (data: Partial<User>) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    
    try {
      const response = await apiCall('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      })

      setState(prev => ({
        ...prev,
        user: response,
        isLoading: false,
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Profile update failed',
      }))
      throw error
    }
  }, [apiCall])

  const refreshUser = useCallback(async () => {
    try {
      const userProfile = await apiCall('/auth/profile')
      setState(prev => ({ ...prev, user: userProfile }))
    } catch (error) {
      console.warn('Failed to refresh user profile:', error)
    }
  }, [apiCall])

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  const googleCallback = useCallback(async (code: string, state?: string | null) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    
    try {
      console.log('Starting Google OAuth callback with code:', code?.substring(0, 10) + '...')
      
      const response = await fetch(`${API_BASE}/auth/google/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          code, 
          state,
          privacy_policy_accepted: true,
          terms_of_service_accepted: true
        }),
      })

      console.log('Google OAuth callback response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        console.error('Google OAuth callback error:', errorData)
        throw new Error(errorData.detail || 'Google sign-in failed')
      }

      const data = await response.json()
      console.log('Google OAuth callback success:', { hasToken: !!data.session_token || !!data.access_token })
      
      const token = data.session_token || data.access_token
      if (!token) {
        throw new Error('No authentication token received from server')
      }
      
      localStorage.setItem('auth_token', token)

      // Get user profile
      const userProfile = await apiCall('/auth/profile')
      console.log('User profile retrieved:', { email: userProfile.email, id: userProfile.id })
      
      setState({
        user: userProfile,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })

      return { success: true }
    } catch (error) {
      console.error('Google callback error:', error)
      
      let errorMessage = 'Google sign-in failed'
      if (error instanceof Error) {
        errorMessage = error.message
      } else if (typeof error === 'string') {
        errorMessage = error
      }
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }))
      
      return { success: false, error: errorMessage }
    }
  }, [apiCall])

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    refreshUser,
    clearError,
    googleCallback,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Hook for protected routes - FIXED infinite loop
export function useRequireAuth(redirectTo: string = '/auth') {
  const { isAuthenticated, isLoading, user } = useAuth()
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      window.location.href = redirectTo
    }
  }, [isAuthenticated, isLoading, redirectTo])

  return { isAuthenticated, isLoading, user }
} 