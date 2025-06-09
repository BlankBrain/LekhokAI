"use client";

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Activity, 
  Clock, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Zap,
  RefreshCw,
  Download,
  Calendar,
  Monitor,
  Brain,
  Hash,
  Target,
  CheckCircle,
  AlertTriangle,
  FileText,
  Database,
  Globe,
  Gauge,
  Server,
  Network,
  Eye,
  AlertCircle
} from 'lucide-react';

interface DashboardData {
  system_status: {
    system: {
      cpu_percent: number;
      memory_percent: number;
      memory_available_gb: number;
      disk_percent: number;
      uptime_seconds: number;
    };
    application: {
      total_requests: number;
      total_errors: number;
      total_generations: number;
      error_rate: number;
    };
  };
  recent_activity: {
    generations_24h: number;
    daily_counts: Array<{ date: string; count: number }>;
  };
  usage_statistics: {
    character_usage: Array<{ 
      character: string; 
      count: number;
      total_input_tokens: number;
      total_output_tokens: number;
    }>;
    model_usage: Array<{ 
      model: string; 
      count: number; 
      avg_input_tokens: number; 
      avg_output_tokens: number; 
    }>;
  };
  performance_metrics: Array<{
    timestamp: string;
    endpoint: string;
    success: boolean;
    response_time_ms: number;
  }>;
  system_metrics_history: Array<{
    timestamp: string;
    cpu_percent: number;
    memory_percent: number;
  }>;
}

export default function AnalyticsPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDashboardData();
    
    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/analytics/dashboard');
      const data = await response.json();
      setDashboardData(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    try {
      const response = await fetch('http://localhost:8000/analytics/export?format=json');
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `karigorai-analytics-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export data:', error);
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatBytes = (gb: number) => {
    return `${gb.toFixed(1)} GB`;
  };

  if (loading && !dashboardData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
        <div className="flex items-center justify-center h-screen">
          <div className="flex flex-col items-center gap-4">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-gray-600">Loading analytics data...</p>
          </div>
        </div>
      </main>
    );
  }

  if (!dashboardData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center py-16">
            <AlertTriangle className="w-16 h-16 mx-auto text-red-500 mb-6" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Failed to Load Analytics</h2>
            <p className="text-gray-600 mb-6">Unable to fetch dashboard data. Please try again.</p>
            <button
              onClick={loadDashboardData}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
      <div className="container mx-auto px-4 py-6">
        {/* Compact Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
          <div>
            <h1 className="text-3xl font-black text-techno mb-1">Analytics Dashboard</h1>
            <p className="text-sm text-techno/60">System performance and usage statistics</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-gray-500 glass px-2 py-1.5 rounded-lg border border-white/30">
              <Clock className="w-3 h-3" />
              <span className="hidden sm:inline">Last updated:</span>
              <span>{lastUpdated?.toLocaleTimeString()}</span>
            </div>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200 border border-green-200' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
              }`}
            >
              <Eye className="w-3 h-3 inline mr-1" />
              Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={loadDashboardData}
              disabled={loading}
              className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 text-xs"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={exportData}
              className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1 text-xs"
            >
              <Download className="w-3 h-3" />
              Export
            </button>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatusCard
            title="CPU Usage"
            value={`${dashboardData.system_status.system.cpu_percent.toFixed(1)}%`}
            icon={<Cpu className="w-4 h-4" />}
            color={dashboardData.system_status.system.cpu_percent > 80 ? "text-red-500" : 
                   dashboardData.system_status.system.cpu_percent > 60 ? "text-yellow-500" : "text-blue-500"}
            description="System processor utilization - monitors overall CPU load and performance"
            chartData={dashboardData.system_metrics_history}
            chartKey="cpu_percent"
          />
          <StatusCard
            title="Memory Usage"
            value={`${dashboardData.system_status.system.memory_percent.toFixed(1)}%`}
            icon={<MemoryStick className="w-4 h-4" />}
            color={dashboardData.system_status.system.memory_percent > 80 ? "text-red-500" : 
                   dashboardData.system_status.system.memory_percent > 60 ? "text-yellow-500" : "text-green-500"}
            description={`${formatBytes(dashboardData.system_status.system.memory_available_gb)} available - tracks RAM usage and available memory`}
            chartData={dashboardData.system_metrics_history}
            chartKey="memory_percent"
          />
          <StatusCard
            title="Total Requests"
            value={dashboardData.system_status.application.total_requests.toString()}
            icon={<Globe className="w-4 h-4" />}
            color="text-purple-500"
            description="All API requests served - includes successful and failed requests to all endpoints"
          />
          <StatusCard
            title="Stories Generated"
            value={dashboardData.system_status.application.total_generations.toString()}
            icon={<FileText className="w-4 h-4" />}
            color="text-orange-500"
            description="Total content created - counts all successful story generations across all characters"
          />
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatusCard
            title="System Uptime"
            value={formatUptime(dashboardData.system_status.system.uptime_seconds)}
            icon={<Activity className="w-4 h-4" />}
            color="text-blue-500"
            description="System running time - how long the server has been active without restart"
          />
          <StatusCard
            title="Error Rate"
            value={`${(dashboardData.system_status.application.error_rate * 100).toFixed(2)}%`}
            icon={<AlertCircle className="w-4 h-4" />}
            color={dashboardData.system_status.application.error_rate > 0.05 ? "text-red-500" : "text-green-500"}
            description={`${dashboardData.system_status.application.total_errors} total errors - percentage of failed requests vs successful ones`}
          />
          <StatusCard
            title="Recent Activity"
            value={dashboardData.recent_activity.generations_24h.toString()}
            icon={<Zap className="w-4 h-4" />}
            color="text-green-500"
            description="Stories in last 24h - recent content generation activity and user engagement"
          />
          <StatusCard
            title="Disk Usage"
            value={`${dashboardData.system_status.system.disk_percent.toFixed(1)}%`}
            icon={<HardDrive className="w-4 h-4" />}
            color={dashboardData.system_status.system.disk_percent > 80 ? "text-red-500" : 
                   dashboardData.system_status.system.disk_percent > 60 ? "text-yellow-500" : "text-yellow-500"}
            description="Storage utilization - monitors disk space usage for logs, cache, and application data"
          />
        </div>

        {/* Usage Statistics */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Character Usage */}
          <div className="glass border border-white/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-4 h-4 text-purple-500" />
              <h3 className="text-lg font-semibold text-techno">Character Usage</h3>
            </div>
            <p className="text-xs text-techno/60 mb-4">Most used characters - shows which storytelling personas are most popular with users and their total token consumption</p>
            <div className="space-y-3">
              {dashboardData.usage_statistics.character_usage.slice(0, 5).map((character, index) => (
                <CharacterUsageItem key={character.character} character={character} rank={index + 1} />
              ))}
            </div>
            {dashboardData.usage_statistics.character_usage.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No character usage data available</p>
            )}
          </div>

          {/* Model Usage */}
          <div className="glass border border-white/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-4 h-4 text-blue-500" />
              <h3 className="text-lg font-semibold text-techno">Model Usage</h3>
            </div>
            <p className="text-xs text-techno/60 mb-4">AI model statistics - tracks token usage and performance across different language models</p>
            <div className="space-y-3">
              {dashboardData.usage_statistics.model_usage.map((model) => (
                <ModelUsageItem key={model.model} model={model} />
              ))}
            </div>
            {dashboardData.usage_statistics.model_usage.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No model usage data available</p>
            )}
          </div>
        </div>

        {/* Performance Metrics */}
        {dashboardData.performance_metrics.length > 0 && (
          <div className="mt-6">
            <div className="glass border border-white/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-4">
                <Monitor className="w-4 h-4 text-green-500" />
                <h3 className="text-lg font-semibold text-techno">Recent Performance</h3>
              </div>
              <p className="text-xs text-techno/60 mb-4">API endpoint performance - response times and success rates for monitoring system health</p>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {dashboardData.performance_metrics.slice(0, 10).map((metric, index) => (
                  <PerformanceMetricItem key={index} metric={metric} />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function StatusCard({ title, value, icon, color, description, chartData, chartKey }: {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
  description: string;
  chartData?: Array<{timestamp: string; cpu_percent: number; memory_percent: number}>;
  chartKey?: 'cpu_percent' | 'memory_percent';
}) {
  return (
    <div className="glass border border-white/30 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className={`p-1.5 rounded-lg bg-gray-50 ${color}`}>
          {icon}
        </div>
        {chartData && chartKey && (
          <div className="w-16 h-8">
            <MiniChart data={chartData} dataKey={chartKey} color={color.replace('text-', '')} />
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-xs font-medium text-techno">{title}</p>
        <p className="text-lg font-bold text-techno">{value}</p>
        <p className="text-xs text-techno/50 leading-tight">{description}</p>
      </div>
    </div>
  );
}

function MiniChart({ data, dataKey, color }: {
  data: Array<{timestamp: string; cpu_percent: number; memory_percent: number}>;
  dataKey: 'cpu_percent' | 'memory_percent';
  color: string;
}) {
  if (!data || data.length < 2) {
    return (
      <div className="w-full h-full opacity-30 flex items-center justify-center">
        <div className="w-12 h-6 bg-gray-100 rounded animate-pulse"></div>
      </div>
    );
  }

  const values = data.map(d => d[dataKey]);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;

  // Create SVG path
  const width = 64;
  const height = 32;
  const padding = 2;
  const chartWidth = width - (padding * 2);
  const chartHeight = height - (padding * 2);

  const points = data.map((item, index) => {
    const x = padding + (index / (data.length - 1)) * chartWidth;
    const y = padding + chartHeight - ((item[dataKey] - minValue) / range) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  // Extract color from Tailwind class or use default
  const extractColor = (colorClass: string): string => {
    if (colorClass.includes('blue')) return '#3b82f6';
    if (colorClass.includes('green')) return '#10b981';
    if (colorClass.includes('red')) return '#ef4444';
    if (colorClass.includes('yellow')) return '#eab308';
    if (colorClass.includes('purple')) return '#8b5cf6';
    return '#3b82f6'; // default blue
  };

  const strokeColor = extractColor(color);

  return (
    <svg width={width} height={height} className="overflow-visible">
      {/* Background grid */}
      <defs>
        <pattern id={`grid-${dataKey}-${Math.random().toString(36).substr(2, 9)}`} width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M 8 0 L 0 0 0 8" fill="none" stroke="rgba(156, 163, 175, 0.1)" strokeWidth="0.5"/>
        </pattern>
      </defs>
      
      {/* Chart line */}
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.5"
        points={points}
        className="drop-shadow-sm"
      />
      
      {/* Chart area fill */}
      <polygon
        fill={strokeColor}
        fillOpacity="0.15"
        points={`${padding},${height - padding} ${points} ${width - padding},${height - padding}`}
      />
      
      {/* Current value indicator */}
      {data.length > 0 && (
        <circle
          cx={width - padding}
          cy={padding + chartHeight - ((values[values.length - 1] - minValue) / range) * chartHeight}
          r="1.5"
          fill={strokeColor}
          className="drop-shadow-sm"
        />
      )}
    </svg>
  );
}

function CharacterUsageItem({ character, rank }: { character: { character: string; count: number; total_input_tokens: number; total_output_tokens: number }; rank: number }) {
  return (
    <div className="p-3 rounded-lg bg-white/30 border border-white/20">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-purple-600 bg-purple-100 w-5 h-5 rounded-full flex items-center justify-center">
            {rank}
          </span>
          <span className="text-sm font-semibold text-techno">{character.character}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-sm font-bold text-purple-600">{character.count}</span>
          <span className="text-xs text-techno/60">uses</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1">
          <Hash className="w-3 h-3 text-green-500" />
          <span className="text-techno/70">Input:</span>
          <span className="font-medium text-techno">{character.total_input_tokens.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <Target className="w-3 h-3 text-orange-500" />
          <span className="text-techno/70">Output:</span>
          <span className="font-medium text-techno">{character.total_output_tokens.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

function ModelUsageItem({ model }: { model: { model: string; count: number; avg_input_tokens: number; avg_output_tokens: number } }) {
  return (
    <div className="p-3 rounded-lg bg-white/30 border border-white/20">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-techno">{model.model}</span>
        <div className="flex items-center gap-1">
          <span className="text-sm font-bold text-blue-600">{model.count}</span>
          <span className="text-xs text-techno/60">uses</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1">
          <Hash className="w-3 h-3 text-green-500" />
          <span className="text-techno/70">Input:</span>
          <span className="font-medium text-techno">{model.avg_input_tokens.toFixed(0)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Target className="w-3 h-3 text-orange-500" />
          <span className="text-techno/70">Output:</span>
          <span className="font-medium text-techno">{model.avg_output_tokens.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
}

function PerformanceMetricItem({ metric }: { metric: { timestamp: string; endpoint: string; success: boolean; response_time_ms: number } }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg bg-white/30 border border-white/20">
      <div className="flex items-center gap-2">
        {metric.success ? (
          <CheckCircle className="w-3 h-3 text-green-500" />
        ) : (
          <AlertCircle className="w-3 h-3 text-red-500" />
        )}
        <span className="text-sm font-medium text-techno">{metric.endpoint}</span>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span className="text-techno/70">{new Date(metric.timestamp).toLocaleTimeString()}</span>
        <span className={`font-medium ${metric.response_time_ms > 1000 ? 'text-red-600' : metric.response_time_ms > 500 ? 'text-yellow-600' : 'text-green-600'}`}>
          {metric.response_time_ms}ms
        </span>
      </div>
    </div>
  );
} 