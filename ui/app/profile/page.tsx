'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { 
  User, 
  Mail, 
  Building, 
  Calendar, 
  Shield, 
  Settings, 
  Edit3, 
  Save, 
  X,
  BookOpen,
  TrendingUp,
  Award,
  Star,
  Crown,
  Clock,
  Target,
  BarChart3
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import LoadingSpinner from '@/components/LoadingSpinner'

interface ProfileStats {
  storiesGenerated: number
  charactersCreated: number
  totalWords: number
  daysActive: number
  favoriteStories: number
  lastActivity: string
}

interface UserPlan {
  name: string
  type: 'free' | 'pro' | 'enterprise'
  features: string[]
  limits: {
    stories: number
    characters: number
    wordsPerStory: number
  }
  usage: {
    stories: number
    characters: number
  }
}

export default function ProfilePage() {
  const { user, updateProfile, isLoading, error } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [localLoading, setLocalLoading] = useState(false)
  const [stats, setStats] = useState<ProfileStats | null>(null)
  const [plan, setPlan] = useState<UserPlan | null>(null)
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    organization_name: ''
  })

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        username: user.username || '',
        organization_name: user.organization_name || ''
      })
    }
  }, [user])

  useEffect(() => {
    loadProfileStats()
    loadUserPlan()
  }, [])

  const loadProfileStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/analytics/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'X-Session-Token': localStorage.getItem('auth_token') || ''
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStats({
          storiesGenerated: data.stories_generated || 0,
          charactersCreated: data.characters_created || 0,
          totalWords: data.total_words || 0,
          daysActive: data.days_active || 0,
          favoriteStories: data.favorite_stories || 0,
          lastActivity: data.last_activity || new Date().toISOString()
        })
      }
    } catch (error) {
      console.error('Failed to load profile stats:', error)
    }
  }

  const loadUserPlan = () => {
    // Mock plan data - in real app, this would come from backend
    const mockPlan: UserPlan = {
      name: user?.role === 'super_admin' ? 'Enterprise' : user?.role === 'organization_user' ? 'Pro' : 'Free',
      type: user?.role === 'super_admin' ? 'enterprise' : user?.role === 'organization_user' ? 'pro' : 'free',
      features: user?.role === 'super_admin' 
        ? ['Unlimited stories', 'Advanced analytics', 'Priority support', 'Custom integrations', 'Team management']
        : user?.role === 'organization_user'
        ? ['1000 stories/month', 'Advanced characters', 'Analytics dashboard', 'Priority support']
        : ['50 stories/month', 'Basic characters', 'Standard support'],
      limits: {
        stories: user?.role === 'super_admin' ? -1 : user?.role === 'organization_user' ? 1000 : 50,
        characters: user?.role === 'super_admin' ? -1 : user?.role === 'organization_user' ? 100 : 10,
        wordsPerStory: user?.role === 'super_admin' ? -1 : user?.role === 'organization_user' ? 5000 : 2000
      },
      usage: {
        stories: stats?.storiesGenerated || 0,
        characters: stats?.charactersCreated || 0
      }
    }
    setPlan(mockPlan)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSave = async () => {
    setLocalLoading(true)
    try {
      await updateProfile(formData)
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to update profile:', error)
    } finally {
      setLocalLoading(false)
    }
  }

  const handleCancel = () => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        username: user.username || '',
        organization_name: user.organization_name || ''
      })
    }
    setIsEditing(false)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0 // Unlimited
    return Math.min((used / limit) * 100, 100)
  }

  const getPlanIcon = (type: string) => {
    switch (type) {
      case 'enterprise': return <Crown className="w-5 h-5 text-purple-600" />
      case 'pro': return <Star className="w-5 h-5 text-blue-600" />
      default: return <User className="w-5 h-5 text-gray-600" />
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
            <p className="mt-2 text-gray-600">Manage your account and track your creative progress</p>
          </div>

          {error && (
            <Alert className="mb-6 bg-red-50 border-red-200">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Profile Information */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
                  {!isEditing ? (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                    >
                      <Edit3 className="w-4 h-4 mr-2" />
                      Edit Profile
                    </button>
                  ) : (
                    <div className="flex space-x-2">
                      <button
                        onClick={handleSave}
                        disabled={localLoading}
                        className="flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                      >
                        {localLoading ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Save className="w-4 h-4 mr-2" />
                        )}
                        Save
                      </button>
                      <button
                        onClick={handleCancel}
                        className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                      >
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                      </button>
                    </div>
                  )}
                </div>

                <div className="space-y-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                      <User className="w-10 h-10 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{user?.full_name}</h3>
                      <p className="text-gray-600">@{user?.username}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          user?.is_approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {user?.is_approved ? 'Approved' : 'Pending Approval'}
                        </span>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                          {user?.role?.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="full_name"
                          value={formData.full_name}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      ) : (
                        <p className="text-gray-900">{user?.full_name}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      ) : (
                        <p className="text-gray-900">@{user?.username}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address
                      </label>
                      <p className="text-gray-900">{user?.email}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Organization
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="organization_name"
                          value={formData.organization_name}
                          onChange={handleInputChange}
                          placeholder="Enter organization name"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      ) : (
                        <p className="text-gray-900">{user?.organization_name || 'Not specified'}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account Created
                      </label>
                      <p className="text-gray-900">{user?.created_at ? formatDate(user.created_at) : 'N/A'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Last Login
                      </label>
                      <p className="text-gray-900">{user?.last_login ? formatDate(user.last_login) : 'Never'}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress & Statistics */}
              <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Your Progress
                </h2>

                {stats ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <BookOpen className="w-8 h-8 text-blue-600" />
                      </div>
                      <div className="text-2xl font-bold text-gray-900">{stats.storiesGenerated}</div>
                      <div className="text-sm text-gray-600">Stories Created</div>
                    </div>

                    <div className="text-center">
                      <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <User className="w-8 h-8 text-purple-600" />
                      </div>
                      <div className="text-2xl font-bold text-gray-900">{stats.charactersCreated}</div>
                      <div className="text-sm text-gray-600">Characters</div>
                    </div>

                    <div className="text-center">
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <TrendingUp className="w-8 h-8 text-green-600" />
                      </div>
                      <div className="text-2xl font-bold text-gray-900">{stats.totalWords.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Total Words</div>
                    </div>

                    <div className="text-center">
                      <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Clock className="w-8 h-8 text-yellow-600" />
                      </div>
                      <div className="text-2xl font-bold text-gray-900">{stats.daysActive}</div>
                      <div className="text-sm text-gray-600">Days Active</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <LoadingSpinner />
                    <p className="mt-4 text-gray-600">Loading your progress...</p>
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Current Plan */}
              {plan && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    {getPlanIcon(plan.type)}
                    <span className="ml-2">Current Plan</span>
                  </h2>

                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-2xl font-bold text-gray-900">{plan.name}</span>
                      {plan.type === 'enterprise' && (
                        <Crown className="w-6 h-6 text-purple-600" />
                      )}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Features</h3>
                    <ul className="space-y-2">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600">
                          <Award className="w-4 h-4 mr-2 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {plan.type !== 'enterprise' && (
                    <div className="mt-6 space-y-4">
                      <h3 className="font-medium text-gray-900">Usage</h3>
                      
                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Stories</span>
                          <span>{plan.usage.stories} / {plan.limits.stories === -1 ? '∞' : plan.limits.stories}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${getUsagePercentage(plan.usage.stories, plan.limits.stories)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Characters</span>
                          <span>{plan.usage.characters} / {plan.limits.characters === -1 ? '∞' : plan.limits.characters}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full" 
                            style={{ width: `${getUsagePercentage(plan.usage.characters, plan.limits.characters)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {plan.type === 'free' && (
                    <button className="w-full mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-colors">
                      Upgrade Plan
                    </button>
                  )}
                </div>
              )}

              {/* Quick Actions */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <button className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Settings className="w-4 h-4 mr-3" />
                    Account Settings
                  </button>
                  <button className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Shield className="w-4 h-4 mr-3" />
                    Privacy & Security
                  </button>
                  <button className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Mail className="w-4 h-4 mr-3" />
                    Notification Preferences
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
} 