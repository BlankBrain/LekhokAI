"use client";

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { useAuth } from '@/lib/auth';
import { 
  Shield, 
  Zap, 
  BookOpen, 
  Image, 
  Activity, 
  BarChart3, 
  Settings2,
  ChevronDown,
  ChevronRight,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Eye,
  EyeOff,
  Download,
  Upload,
  Lock,
  Unlock,
  Key,
  Monitor,
  Database,
  Clock,
  Cpu,
  HardDrive,
  Network,
  Bell,
  Mail,
  Slack,
  Github,
  Bug,
  Palette,
  Brush,
  FileText,
  Filter,
  Sliders,
  Target,
  Camera,
  Video,
  Mic,
  Volume2,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Power,
  Wifi,
  WifiOff,
  Globe,
  Server,
  Cloud,
  HardDriveIcon,
  MemoryStick,
  Gauge,
  TrendingUp,
  Users,
  UserCheck,
  Archive,
  Trash2,
  Download as DownloadIcon,
  ExternalLink,
  Brain,
  Layers,
  Sparkles,
  X
} from 'lucide-react';

interface SettingsSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
  expanded: boolean;
  color: string;
  category: 'core' | 'ai' | 'system' | 'advanced';
}

interface ConfigData {
  [key: string]: any;
}

interface ToastProps {
  message: string;
  type: 'success' | 'error';
  visible: boolean;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, type, visible, onClose }) => {
  useEffect(() => {
    if (visible) {
      const timer = setTimeout(() => {
        onClose();
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [visible, onClose]);

  if (!visible) return null;

  return (
    <div className={`fixed top-4 right-4 z-50 transform transition-all duration-300 ${
      visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    }`}>
      <div className={`flex items-center gap-3 px-6 py-4 rounded-xl shadow-lg border backdrop-blur-md ${
        type === 'success' 
          ? 'bg-green-50/90 border-green-200 text-green-800' 
          : 'bg-red-50/90 border-red-200 text-red-800'
      }`}>
        <div className={`p-1 rounded-full ${
          type === 'success' ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600" />
          )}
        </div>
        <span className="font-medium">{message}</span>
        <button
          onClick={onClose}
          className={`p-1 rounded-full hover:bg-white/50 transition-colors ${
            type === 'success' ? 'text-green-600' : 'text-red-600'
          }`}
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

function SettingsPageContent() {
  const [sections, setSections] = useState<SettingsSection[]>([
    {
      id: 'safety',
      title: 'Safety & Content Controls',
      icon: <Shield className="w-5 h-5" />,
      description: 'Content filtering, moderation, and compliance settings',
      expanded: false,
      color: 'from-red-500 to-red-600',
      category: 'core'
    },
    {
      id: 'story-generation',
      title: 'Story Generation',
      icon: <BookOpen className="w-5 h-5" />,
      description: 'Story style, structure, and quality configuration',
      expanded: false,
      color: 'from-blue-500 to-blue-600',
      category: 'ai'
    },
    {
      id: 'image-generation',
      title: 'Image Generation',
      icon: <Image className="w-5 h-5" />,
      description: 'Image quality, content filters, and generation options',
      expanded: false,
      color: 'from-purple-500 to-purple-600',
      category: 'ai'
    },
    {
      id: 'ai',
      title: 'AI Engine Settings',
      icon: <Brain className="w-5 h-5" />,
      description: 'Core AI model configuration and optimization',
      expanded: false,
      color: 'from-pink-500 to-pink-600',
      category: 'ai'
    },
    {
      id: 'performance',
      title: 'Performance & Reliability',
      icon: <Zap className="w-5 h-5" />,
      description: 'Caching, rate limiting, and system optimization',
      expanded: false,
      color: 'from-yellow-500 to-yellow-600',
      category: 'system'
    },
    {
      id: 'system',
      title: 'System & Monitoring',
      icon: <Activity className="w-5 h-5" />,
      description: 'Logging, monitoring, and notification settings',
      expanded: false,
      color: 'from-green-500 to-green-600',
      category: 'system'
    },
    {
      id: 'analytics',
      title: 'Analytics Dashboard',
      icon: <BarChart3 className="w-5 h-5" />,
      description: 'Usage tracking, reports, and data collection',
      expanded: false,
      color: 'from-indigo-500 to-indigo-600',
      category: 'system'
    },
    {
      id: 'developer',
      title: 'Developer Options',
      icon: <Settings2 className="w-5 h-5" />,
      description: 'Debug mode, API settings, and experimental features',
      expanded: false,
      color: 'from-gray-500 to-gray-600',
      category: 'advanced'
    }
  ]);

  const [configData, setConfigData] = useState<ConfigData>({});
  const [apiKey, setApiKey] = useState('');
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [toast, setToast] = useState<{
    visible: boolean;
    message: string;
    type: 'success' | 'error';
  }>({
    visible: false,
    message: '',
    type: 'success'
  });

  // Show toast when save status changes
  useEffect(() => {
    if (saveStatus === 'success') {
      setToast({
        visible: true,
        message: 'Settings saved successfully!',
        type: 'success'
      });
      setTimeout(() => setSaveStatus('idle'), 3000);
    } else if (saveStatus === 'error') {
      setToast({
        visible: true,
        message: 'Failed to save settings. Please try again.',
        type: 'error'
      });
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  }, [saveStatus]);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({
      visible: true,
      message,
      type
    });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, visible: false }));
  };

  useEffect(() => {
    loadAllSettings();
    loadSystemStatus();
    const interval = setInterval(loadSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAllSettings = async () => {
    try {
      setLoading(true);
      const responses = await Promise.all([
        fetch('http://localhost:8000/settings/safety'),
        fetch('http://localhost:8000/settings/performance'),
        fetch('http://localhost:8000/settings/story-generation'),
        fetch('http://localhost:8000/settings/image-generation'),
        fetch('http://localhost:8000/settings/system'),
        fetch('http://localhost:8000/settings/analytics'),
        fetch('http://localhost:8000/settings/developer'),
        fetch('http://localhost:8000/settings/ai'),
        fetch('http://localhost:8000/api-key')
      ]);

      const data = await Promise.all(responses.map(r => r.json()));
      
      setConfigData({
        safety: data[0].safety || {},
        performance: data[1].performance || {},
        'story-generation': data[2].story_generation || {},
        'image-generation': data[3].image_generation || {},
        system: data[4].system || {},
        analytics: data[5].analytics || {},
        developer: data[6].developer || {},
        ai: data[7].ai_settings || {}
      });

      if (data[8].set) {
        setApiKey(data[8].masked || '');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      showToast('Failed to load settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/system/status');
      const status = await response.json();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const toggleSection = (sectionId: string) => {
    setSections(sections.map(section => 
      section.id === sectionId 
        ? { ...section, expanded: !section.expanded }
        : section
    ));
  };

  const updateSectionData = (sectionId: string, newData: any) => {
    setConfigData(prev => ({
      ...prev,
      [sectionId]: newData
    }));
  };

  const saveSection = async (sectionId: string) => {
    try {
      setSaving(true);
      const endpoint = sectionId === 'story-generation' ? 'story-generation' : sectionId;
      let dataKey = sectionId;
      
      // Map section IDs to their corresponding data keys
      if (sectionId === 'story-generation') {
        dataKey = 'story_generation';
      } else if (sectionId === 'ai') {
        dataKey = 'ai_settings';
      }
      
      const response = await fetch(`http://localhost:8000/settings/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [dataKey]: configData[sectionId] })
      });

      if (response.ok) {
        setSaveStatus('success');
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      setSaveStatus('error');
      console.error('Failed to save settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const saveApiKey = async () => {
    try {
      setSaving(true);
      const response = await fetch('http://localhost:8000/api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
      });

      const result = await response.json();
      if (result.success) {
        setSaveStatus('success');
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      setSaveStatus('error');
      console.error('Failed to save API key:', error);
    } finally {
      setSaving(false);
    }
  };

  const exportSettings = async () => {
    try {
      const response = await fetch('http://localhost:8000/analytics/export?format=json');
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `karigorai-settings-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Settings exported successfully!', 'success');
    } catch (error) {
      console.error('Failed to export settings:', error);
      showToast('Failed to export settings', 'error');
    }
  };

  const filteredSections = activeCategory === 'all' 
    ? sections 
    : sections.filter(section => section.category === activeCategory);

  const categories = [
    { id: 'all', label: 'All Settings', icon: <Layers className="w-4 h-4" /> },
    { id: 'core', label: 'Core', icon: <Shield className="w-4 h-4" /> },
    { id: 'ai', label: 'AI Engine', icon: <Brain className="w-4 h-4" /> },
    { id: 'system', label: 'System', icon: <Activity className="w-4 h-4" /> },
    { id: 'advanced', label: 'Advanced', icon: <Settings2 className="w-4 h-4" /> }
  ];

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="flex flex-col items-center gap-6 glass border border-white/30 rounded-xl p-12">
              <div className="relative">
                <RefreshCw className="w-12 h-12 animate-spin text-techno" />
                <div className="absolute inset-0 w-12 h-12 border-2 border-techno/20 rounded-full animate-pulse"></div>
              </div>
              <div className="text-center">
                <p className="text-xl font-semibold text-techno mb-2">Loading Configuration</p>
                <p className="text-sm text-techno/60">Fetching your system settings...</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        visible={toast.visible}
        onClose={hideToast}
      />

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
          <div className="mb-4 lg:mb-0">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-gradient-to-r from-techno to-techno/80 text-white">
                <Settings2 className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-techno">System Configuration</h1>
                <p className="text-techno/60">Manage all aspects of your KarigorAI system</p>
              </div>
            </div>
          </div>
          
          {/* Category Filter */}
          <div className="flex items-center gap-2 glass border border-white/30 rounded-xl p-1">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeCategory === category.id
                    ? 'bg-techno text-white shadow-lg'
                    : 'text-techno/70 hover:text-techno hover:bg-white/50'
                }`}
              >
                {category.icon}
                <span className="hidden sm:inline">{category.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* System Status Overview */}
        {systemStatus && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="glass border border-white/30 rounded-xl p-4 hover:shadow-lg transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                  <Cpu className="w-5 h-5" />
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-techno">{systemStatus.system.cpu_percent?.toFixed(1)}%</p>
                  <p className="text-xs text-techno/60">CPU Usage</p>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${systemStatus.system.cpu_percent}%` }}
                ></div>
              </div>
            </div>
            
            <div className="glass border border-white/30 rounded-xl p-4 hover:shadow-lg transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-green-600 text-white">
                  <MemoryStick className="w-5 h-5" />
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-techno">{systemStatus.system.memory_percent?.toFixed(1)}%</p>
                  <p className="text-xs text-techno/60">Memory</p>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${systemStatus.system.memory_percent}%` }}
                ></div>
              </div>
            </div>
            
            <div className="glass border border-white/30 rounded-xl p-4 hover:shadow-lg transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-purple-600 text-white">
                  <Globe className="w-5 h-5" />
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-techno">{systemStatus.application.total_requests}</p>
                  <p className="text-xs text-techno/60">Requests</p>
                </div>
              </div>
              <p className="text-xs text-techno/50">Total API calls processed</p>
            </div>
            
            <div className="glass border border-white/30 rounded-xl p-4 hover:shadow-lg transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 text-white">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-techno">{systemStatus.application.total_generations}</p>
                  <p className="text-xs text-techno/60">Stories</p>
                </div>
              </div>
              <p className="text-xs text-techno/50">Total stories generated</p>
            </div>
          </div>
        )}

        {/* API Configuration */}
        <div className="glass border border-white/30 rounded-xl p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-xl bg-gradient-to-r from-gold to-gold/80 text-white">
              <Key className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-techno">API Configuration</h3>
              <p className="text-sm text-techno/60">Configure your Gemini API key for AI services</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <input
                type={apiKeyVisible ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your Gemini API key"
                className="w-full px-4 py-3 pr-12 glass border border-white/30 rounded-xl focus:border-gold/50 focus:outline-none text-techno bg-white/50 transition-all"
              />
              <button
                onClick={() => setApiKeyVisible(!apiKeyVisible)}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 text-techno/40 hover:text-techno/60 transition-colors"
              >
                {apiKeyVisible ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            <div className="flex gap-3">
              <button
                onClick={saveApiKey}
                disabled={saving}
                className="px-6 py-3 bg-gradient-to-r from-gold to-gold/90 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
              >
                {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save Key
              </button>
              <button
                onClick={exportSettings}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg transition-all flex items-center gap-2 font-medium"
              >
                <DownloadIcon className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Configuration Sections */}
        <div className="space-y-6">
          {filteredSections.map((section) => (
            <div key={section.id} className="glass border border-white/30 rounded-xl overflow-hidden hover:shadow-lg transition-all duration-300">
              <div className="w-full p-6 flex items-center justify-between group">
                <button
                  onClick={() => toggleSection(section.id)}
                  className="flex-1 text-left hover:bg-white/10 transition-all flex items-center gap-4 p-2 -m-2 rounded-lg"
                >
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${section.color} text-white shadow-lg group-hover:scale-105 transition-transform`}>
                    {section.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-techno mb-1">{section.title}</h3>
                    <p className="text-sm text-techno/60">{section.description}</p>
                  </div>
                </button>
                <div className="flex items-center gap-3 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      saveSection(section.id);
                    }}
                    disabled={saving}
                    className="px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2 text-sm font-medium"
                  >
                    {saving ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                    Save
                  </button>
                  <button
                    onClick={() => toggleSection(section.id)}
                    className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                  >
                    {section.expanded ? 
                      <ChevronDown className="w-5 h-5 text-techno/60" /> : 
                      <ChevronRight className="w-5 h-5 text-techno/60" />
                    }
                  </button>
                </div>
              </div>
              
              {section.expanded && (
                <div className="border-t border-white/20 bg-white/5 p-6 animate-in slide-in-from-top-2 duration-300">
                  <div className="max-w-4xl">
                    {renderSectionContent(section.id, configData[section.id] || {}, (data) => updateSectionData(section.id, data))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Status Footer */}
        <div className="mt-8 glass border border-white/30 rounded-xl p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-r from-green-500 to-green-600 text-white">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-techno">System Status</h3>
                <p className="text-sm text-techno/60">All systems operational and ready</p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <div className="text-sm text-techno/60">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

function renderSectionContent(sectionId: string, data: any, updateData: (data: any) => void) {
  const renderToggle = (key: string, label: string, description?: string) => (
    <div className="flex items-center justify-between p-5 glass border border-white/20 rounded-xl hover:bg-white/10 transition-all">
      <div className="flex-1">
        <label className="block text-sm font-semibold text-techno mb-1">{label}</label>
        {description && <p className="text-xs text-techno/60">{description}</p>}
      </div>
      <button
        onClick={() => updateData({ ...data, [key]: !data[key] })}
        className={`relative w-12 h-6 rounded-full transition-all duration-300 shadow-inner ${
          data[key] ? 'bg-gradient-to-r from-green-500 to-green-600' : 'bg-gray-300'
        }`}
      >
        <div className={`absolute w-5 h-5 bg-white rounded-full top-0.5 shadow-lg transition-transform duration-300 ${
          data[key] ? 'translate-x-6' : 'translate-x-0.5'
        }`} />
      </button>
    </div>
  );

  const renderSlider = (key: string, label: string, min: number, max: number, step: number = 0.1, suffix: string = '') => (
    <div className="p-5 glass border border-white/20 rounded-xl hover:bg-white/10 transition-all">
      <label className="block text-sm font-semibold text-techno mb-4">{label}</label>
      <div className="flex items-center gap-4">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={data[key] || min}
          onChange={(e) => updateData({ ...data, [key]: parseFloat(e.target.value) })}
          className="flex-1 h-3 bg-gray-200 rounded-full appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #22345C 0%, #22345C ${((data[key] || min) - min) / (max - min) * 100}%, #e5e7eb ${((data[key] || min) - min) / (max - min) * 100}%, #e5e7eb 100%)`
          }}
        />
        <div className="min-w-[80px] text-right">
          <span className="text-sm font-bold text-techno bg-techno/10 px-3 py-1 rounded-lg">
            {(data[key] || min).toFixed(step < 1 ? 1 : 0)}{suffix}
          </span>
        </div>
      </div>
    </div>
  );

  const renderSelect = (key: string, label: string, options: string[], description?: string) => (
    <div className="p-5 glass border border-white/20 rounded-xl hover:bg-white/10 transition-all">
      <label className="block text-sm font-semibold text-techno mb-2">{label}</label>
      {description && <p className="text-xs text-techno/60 mb-3">{description}</p>}
      <select
        value={data[key] || options[0]}
        onChange={(e) => updateData({ ...data, [key]: e.target.value })}
        className="w-full px-4 py-3 glass border border-white/30 rounded-xl focus:border-techno/50 focus:outline-none text-techno bg-white/50 transition-all"
      >
        {options.map(option => (
          <option key={option} value={option} className="bg-white text-techno">{option}</option>
        ))}
      </select>
    </div>
  );

  const renderInput = (key: string, label: string, type: string = 'text', description?: string) => (
    <div className="p-5 glass border border-white/20 rounded-xl hover:bg-white/10 transition-all">
      <label className="block text-sm font-semibold text-techno mb-2">{label}</label>
      {description && <p className="text-xs text-techno/60 mb-3">{description}</p>}
      <input
        type={type}
        value={data[key] || ''}
        onChange={(e) => updateData({ ...data, [key]: type === 'number' ? parseInt(e.target.value) : e.target.value })}
        className="w-full px-4 py-3 glass border border-white/30 rounded-xl focus:border-techno/50 focus:outline-none text-techno bg-white/50 transition-all"
        placeholder={type === 'number' ? '0' : 'Enter value...'}
      />
    </div>
  );

  const renderCategoryTitle = (title: string, icon: React.ReactNode) => (
    <div className="flex items-center gap-3 mb-6 mt-8 first:mt-0">
      <div className="p-2 rounded-xl bg-gradient-to-r from-techno to-techno/80 text-white shadow-lg">
        {icon}
      </div>
      <h4 className="text-lg font-bold text-techno">{title}</h4>
      <div className="flex-1 h-px bg-gradient-to-r from-techno/20 to-transparent"></div>
    </div>
  );

  switch (sectionId) {
    case 'safety':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Content Filtering', <Filter className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('content_filtering.enabled', 'Enable Content Filtering', 'Automatically filter inappropriate content')}
            {renderToggle('content_filtering.strict_mode', 'Strict Mode', 'Use stricter filtering rules')}
          </div>
          
          {renderCategoryTitle('Moderation', <UserCheck className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('moderation.auto_review', 'Auto Review', 'Automatically review generated content')}
            {renderToggle('moderation.toxicity_detection', 'Toxicity Detection', 'Detect and flag toxic content')}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSlider('moderation.flagging_threshold', 'Flagging Threshold', 0, 1, 0.1)}
          </div>
          
          {renderCategoryTitle('Compliance', <Lock className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('compliance.gdpr_mode', 'GDPR Mode', 'Enable GDPR compliance features')}
            {renderToggle('compliance.user_consent_required', 'Require User Consent', 'Require explicit user consent')}
            {renderInput('compliance.data_retention_days', 'Data Retention (Days)', 'number', 'How long to keep user data')}
          </div>
        </div>
      );

    case 'performance':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Caching', <Database className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('caching.enabled', 'Enable Caching', 'Cache responses to improve performance')}
            {renderToggle('caching.cache_embeddings', 'Cache Embeddings', 'Cache embedding calculations')}
            {renderInput('caching.ttl_seconds', 'Cache TTL (Seconds)', 'number', 'How long to cache data')}
            {renderInput('caching.max_cache_size_mb', 'Max Cache Size (MB)', 'number', 'Maximum cache size')}
          </div>
          
          {renderCategoryTitle('Rate Limiting', <Gauge className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderInput('rate_limiting.requests_per_minute', 'Requests Per Minute', 'number')}
            {renderInput('rate_limiting.burst_limit', 'Burst Limit', 'number')}
            {renderToggle('rate_limiting.per_user_limits', 'Per-User Limits', 'Apply limits per user')}
          </div>
          
          {renderCategoryTitle('Reliability', <Shield className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderInput('reliability.max_retries', 'Max Retries', 'number')}
            {renderInput('reliability.timeout_seconds', 'Timeout (Seconds)', 'number')}
            {renderSelect('reliability.fallback_model', 'Fallback Model', ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash'])}
          </div>
        </div>
      );

    case 'story-generation':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Style Settings', <Palette className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSelect('style.default_length', 'Default Length', ['short', 'medium', 'long', 'custom'])}
            {renderSelect('style.default_genre', 'Default Genre', ['adventure', 'romance', 'mystery', 'fantasy', 'sci-fi', 'drama'])}
            {renderSelect('style.narrative_style', 'Narrative Style', ['first_person', 'third_person', 'mixed'])}
            {renderSelect('style.dialogue_style', 'Dialogue Style', ['formal', 'natural', 'casual'])}
          </div>
          
          {renderCategoryTitle('Structure', <FileText className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('structure.include_dialogue', 'Include Dialogue', 'Add conversations between characters')}
            {renderToggle('structure.include_descriptions', 'Include Descriptions', 'Add detailed scene descriptions')}
            {renderToggle('structure.chapter_breaks', 'Chapter Breaks', 'Add chapter divisions')}
            {renderSelect('structure.scene_transitions', 'Scene Transitions', ['abrupt', 'smooth', 'fade'])}
          </div>
          
          {renderCategoryTitle('Creativity', <Brush className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSlider('creativity.randomness_level', 'Randomness Level', 0, 1, 0.1)}
            {renderToggle('creativity.prompt_expansion', 'Prompt Expansion', 'Automatically expand story prompts')}
            {renderToggle('creativity.character_development', 'Character Development', 'Focus on character growth')}
            {renderSelect('creativity.plot_complexity', 'Plot Complexity', ['simple', 'medium', 'complex'])}
          </div>
        </div>
      );

    case 'image-generation':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Quality Settings', <Camera className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSelect('quality.resolution', 'Resolution', ['512x512', '1024x1024', '1024x1792'])}
            {renderSelect('quality.style', 'Style', ['photorealistic', 'artistic', 'cartoon', 'anime'])}
            {renderToggle('quality.enhancement', 'Quality Enhancement', 'Apply post-processing enhancement')}
          </div>
          
          {renderCategoryTitle('Content Filters', <Filter className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('content.nsfw_filter', 'NSFW Filter', 'Filter inappropriate content')}
            {renderToggle('content.violence_filter', 'Violence Filter', 'Filter violent content')}
            {renderToggle('content.copyright_awareness', 'Copyright Awareness', 'Avoid copyrighted material')}
            {renderToggle('content.brand_safety', 'Brand Safety', 'Ensure brand-safe content')}
          </div>
          
          {renderCategoryTitle('Generation Options', <Settings2 className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('generation.prompt_enhancement', 'Prompt Enhancement', 'Automatically improve prompts')}
            {renderToggle('generation.negative_prompts', 'Negative Prompts', 'Use negative prompts to avoid unwanted elements')}
            {renderToggle('generation.style_transfer', 'Style Transfer', 'Apply artistic style transfer')}
          </div>
        </div>
      );

    case 'system':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Logging', <FileText className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSelect('logging.level', 'Log Level', ['DEBUG', 'INFO', 'WARNING', 'ERROR'])}
            {renderToggle('logging.log_to_file', 'Log to File', 'Save logs to files')}
            {renderSelect('logging.log_rotation', 'Log Rotation', ['daily', 'weekly', 'monthly'])}
            {renderInput('logging.max_log_size_mb', 'Max Log Size (MB)', 'number')}
          </div>
          
          {renderCategoryTitle('Monitoring', <Activity className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('monitoring.performance_tracking', 'Performance Tracking', 'Track system performance')}
            {renderToggle('monitoring.error_tracking', 'Error Tracking', 'Track and log errors')}
            {renderToggle('monitoring.usage_analytics', 'Usage Analytics', 'Collect usage statistics')}
          </div>
          
          {renderCategoryTitle('Notifications', <Bell className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('notifications.email_alerts', 'Email Alerts', 'Send email notifications')}
            {renderInput('notifications.slack_webhook', 'Slack Webhook URL', 'text', 'Slack webhook for notifications')}
            {renderInput('notifications.discord_webhook', 'Discord Webhook URL', 'text', 'Discord webhook for notifications')}
          </div>
        </div>
      );

    case 'ai':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Model Configuration', <Brain className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderSelect('model.primary_model', 'Primary Model', ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash'])}
            {renderSelect('model.fallback_model', 'Fallback Model', ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash'])}
            {renderSlider('model.temperature', 'Temperature', 0, 2, 0.1)}
            {renderSlider('model.top_p', 'Top P', 0, 1, 0.1)}
          </div>
          
          {renderCategoryTitle('Performance Optimization', <Zap className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('optimization.parallel_processing', 'Parallel Processing', 'Process multiple requests simultaneously')}
            {renderToggle('optimization.smart_caching', 'Smart Caching', 'Intelligently cache AI responses')}
            {renderInput('optimization.max_tokens', 'Max Tokens', 'number', 'Maximum tokens per response')}
            {renderInput('optimization.batch_size', 'Batch Size', 'number', 'Number of requests to batch together')}
          </div>
          
          {renderCategoryTitle('Safety & Ethics', <Shield className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('safety.content_safety', 'Content Safety', 'Enable AI content safety filters')}
            {renderToggle('safety.bias_detection', 'Bias Detection', 'Detect and mitigate AI bias')}
            {renderToggle('safety.ethical_guidelines', 'Ethical Guidelines', 'Follow ethical AI guidelines')}
          </div>
        </div>
      );

    case 'analytics':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Data Collection', <BarChart3 className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('collection.usage_tracking', 'Usage Tracking', 'Track user interactions')}
            {renderToggle('collection.performance_metrics', 'Performance Metrics', 'Collect performance data')}
            {renderToggle('collection.error_reporting', 'Error Reporting', 'Report errors and issues')}
            {renderToggle('collection.user_feedback', 'User Feedback', 'Collect user feedback')}
          </div>
          
          {renderCategoryTitle('Privacy', <Lock className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('privacy.anonymize_data', 'Anonymize Data', 'Remove personally identifiable information')}
            {renderToggle('privacy.opt_out_available', 'Opt-out Available', 'Allow users to opt out of tracking')}
            {renderInput('privacy.data_retention_days', 'Data Retention (Days)', 'number')}
          </div>
          
          {renderCategoryTitle('Reporting', <TrendingUp className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('reporting.daily_reports', 'Daily Reports', 'Generate daily analytics reports')}
            {renderToggle('reporting.weekly_summaries', 'Weekly Summaries', 'Generate weekly summaries')}
            {renderSelect('reporting.export_format', 'Export Format', ['json', 'csv', 'pdf'])}
          </div>
        </div>
      );

    case 'developer':
      return (
        <div className="space-y-6">
          {renderCategoryTitle('Debug Mode', <Bug className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('debug.enabled', 'Enable Debug Mode', 'Show detailed debug information')}
            {renderToggle('debug.verbose_logging', 'Verbose Logging', 'Enable detailed logging')}
            {renderToggle('debug.api_tracing', 'API Tracing', 'Trace API calls and responses')}
            {renderToggle('debug.performance_profiling', 'Performance Profiling', 'Profile system performance')}
          </div>
          
          {renderCategoryTitle('API Settings', <Globe className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('api.cors_enabled', 'CORS Enabled', 'Enable Cross-Origin Resource Sharing')}
            {renderInput('api.rate_limit_override', 'Rate Limit Override', 'number', 'Override default rate limits')}
            {renderToggle('api.detailed_errors', 'Detailed Errors', 'Return detailed error messages')}
          </div>
          
          {renderCategoryTitle('Experimental Features', <Settings2 className="w-5 h-5" />)}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {renderToggle('experimental.new_ui_features', 'New UI Features', 'Enable experimental UI features')}
            {renderToggle('experimental.beta_models', 'Beta Models', 'Access to beta AI models')}
            {renderToggle('experimental.advanced_analytics', 'Advanced Analytics', 'Enable experimental analytics')}
          </div>
        </div>
      );

    default:
      return (
        <div className="text-center py-12">
          <div className="p-4 rounded-xl bg-gray-100 text-gray-500 inline-block mb-4">
            <Settings2 className="w-8 h-8" />
          </div>
          <p className="text-gray-500">No configuration options available for this section.</p>
        </div>
      );
  }
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsPageContent />
    </ProtectedRoute>
  );
} 