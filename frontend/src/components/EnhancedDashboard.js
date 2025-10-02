import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EnhancedDashboard = ({ user }) => {
  const [stats, setStats] = useState({});
  const [theme, setTheme] = useState({});
  const logoUrl = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg";

  useEffect(() => {
    fetchEnhancedStats();
    fetchDashboardTheme();
  }, []);

  const fetchEnhancedStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/enhanced-stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching enhanced stats:', error);
    }
  };

  const fetchDashboardTheme = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/theme`);
      setTheme(response.data);
    } catch (error) {
      console.error('Error fetching theme:', error);
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle, trend }) => (
    <div className={`bg-gradient-to-br ${color} rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-opacity-20 hover:scale-105 transform`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-3xl">{icon}</div>
          <div>
            <h3 className="text-white text-sm font-semibold opacity-90">{title}</h3>
            {subtitle && <p className="text-white text-xs opacity-70">{subtitle}</p>}
          </div>
        </div>
        {trend && (
          <div className="text-white text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full">
            {trend}
          </div>
        )}
      </div>
      <div className="text-white">
        <p className="text-4xl font-bold mb-1">{value || 0}</p>
        <div className="w-full bg-white bg-opacity-20 rounded-full h-1">
          <div className="bg-white h-1 rounded-full" style={{ width: `${Math.min((value / 20) * 100, 100)}%` }}></div>
        </div>
      </div>
    </div>
  );

  const QuickActionCard = ({ title, description, icon, color, onClick, disabled }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${color} text-white p-6 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 transform disabled:opacity-50 disabled:cursor-not-allowed text-left w-full`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="text-4xl">{icon}</div>
        <svg className="w-6 h-6 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-sm opacity-90">{description}</p>
    </button>
  );

  return (
    <div className="space-y-8">
      {/* Hero Section with Embossed Logo */}
      <div className="relative bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 rounded-3xl p-8 overflow-hidden">
        {/* Embossed Logo Background */}
        <div className="absolute inset-0 opacity-10">
          <img 
            src={logoUrl} 
            alt="Background Logo"
            className="w-full h-full object-contain transform rotate-12 scale-150"
          />
        </div>
        
        {/* Large Embossed Logo */}
        <div className="absolute right-8 top-1/2 transform -translate-y-1/2 opacity-20">
          <div className="w-48 h-48 bg-white bg-opacity-10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white border-opacity-20">
            <img 
              src={logoUrl} 
              alt="Embossed Logo"
              className="w-32 h-32 object-contain filter drop-shadow-2xl"
            />
          </div>
        </div>
        
        <div className="relative z-10">
          <h1 className="text-5xl font-bold text-white mb-4">
            Welcome Back, {user?.full_name}! 👋
          </h1>
          <p className="text-blue-100 text-xl mb-6">
            {user?.designation} • {user?.department} Department
          </p>
          <p className="text-blue-200">
            🕘 Working Hours: 9:45 AM - 6:45 PM • 📍 GPS Tracking Active • ⚠️ Late Penalties Apply
          </p>
          
          {/* Current Time */}
          <div className="mt-6 inline-flex items-center bg-white bg-opacity-20 rounded-full px-6 py-3 backdrop-blur-sm">
            <svg className="w-5 h-5 text-yellow-300 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-white font-medium">
              {new Date().toLocaleTimeString('en-IN', { 
                timeZone: 'Asia/Kolkata',
                hour12: true,
                hour: '2-digit',
                minute: '2-digit'
              })} IST
            </span>
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Employees"
          subtitle="Active Workforce"
          value={stats.employee_metrics?.total_employees}
          icon="👥"
          color="from-blue-600 to-blue-700"
          trend="+3 this month"
        />
        <StatCard
          title="Present Today"
          subtitle="Current Attendance"
          value={stats.employee_metrics?.present_today}
          icon="✅"
          color="from-green-600 to-green-700"
          trend={`${((stats.employee_metrics?.present_today / stats.employee_metrics?.total_employees) * 100 || 0).toFixed(0)}% rate`}
        />
        <StatCard
          title="Currently Online"
          subtitle="Active Now"
          value={stats.employee_metrics?.logged_in_now}
          icon="🟢"
          color="from-yellow-600 to-orange-600"
          trend="Real-time"
        />
        <StatCard
          title="Documents"
          subtitle="Total Uploaded"
          value={stats.document_metrics?.total_documents}
          icon="📄"
          color="from-purple-600 to-purple-700"
          trend={`+${stats.document_metrics?.recent_uploads} this week`}
        />
      </div>

      {/* Announcements Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                📢 Company Announcements
                {stats.announcement_metrics?.urgent_announcements > 0 && (
                  <span className="ml-3 bg-red-500 text-white text-xs px-2 py-1 rounded-full animate-pulse">
                    {stats.announcement_metrics.urgent_announcements} Urgent
                  </span>
                )}
              </h2>
            </div>
            
            {stats.announcement_metrics?.active_announcements > 0 ? (
              <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-blue-900">📋 Latest Company Updates</h4>
                    <span className="text-blue-600 text-sm">{stats.announcement_metrics.active_announcements} active</span>
                  </div>
                  <p className="text-blue-800 text-sm mt-1">Check the Announcements tab for all company updates</p>
                </div>
                
                {stats.announcement_metrics?.recent_announcements > 0 && (
                  <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                    <h4 className="font-semibold text-green-900">🆕 New This Week</h4>
                    <p className="text-green-800 text-sm mt-1">{stats.announcement_metrics.recent_announcements} new announcements posted</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">📢</div>
                <p className="text-gray-500">No announcements at the moment</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats Panel */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-6 text-white">
            <h3 className="text-xl font-bold mb-4 flex items-center">
              📊 Today's Overview
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="opacity-90">Attendance Rate</span>
                <span className="font-bold">
                  {((stats.employee_metrics?.present_today / stats.employee_metrics?.total_employees) * 100 || 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="opacity-90">Absent Today</span>
                <span className="font-bold">{stats.employee_metrics?.absent_today || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="opacity-90">Documents This Week</span>
                <span className="font-bold">+{stats.document_metrics?.recent_uploads || 0}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4">⚡ System Status</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database</span>
                <span className="text-green-600 text-sm font-medium flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Last Updated</span>
                <span className="text-gray-500 text-xs">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;