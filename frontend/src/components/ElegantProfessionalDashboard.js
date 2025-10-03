import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProfessionalFooter from './ProfessionalFooter';
import WorkingEmployeeDatabase from './WorkingEmployeeDatabase';
import DocumentManagement from './DocumentManagement';
import AnnouncementManagement from './AnnouncementManagement';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ElegantProfessionalDashboard = ({ user, logout }) => {
  const [currentTab, setCurrentTab] = useState('employee_database');
  const [dashboardStats, setDashboardStats] = useState({});
  const [employees, setEmployees] = useState([]);
  const [interviewCandidates, setInterviewCandidates] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [holidayCalendar, setHolidayCalendar] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Salary slip sharing modal states
  const [showSalaryShareModal, setShowSalaryShareModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [shareChannels, setShareChannels] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [shareLoading, setShareLoading] = useState(false);
  const [shareResults, setShareResults] = useState(null);
  
  // Add employee modal states
  const [showAddEmployeeModal, setShowAddEmployeeModal] = useState(false);
  const [addEmployeeLoading, setAddEmployeeLoading] = useState(false);
  const [newEmployeeData, setNewEmployeeData] = useState({
    full_name: '',
    employee_id: '',
    email_address: '',
    contact_number: '',
    department: '',
    designation: '',
    address: '',
    basic_salary: '',
    join_date: new Date().toISOString().split('T')[0]
  });

  const logoUrl = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg";

  // Professional Color Palette
  const colorPalette = {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe', 
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a'
    },
    accent: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e'
    },
    success: {
      50: '#ecfdf5',
      500: '#10b981',
      700: '#047857'
    },
    warning: {
      50: '#fffbeb',
      500: '#f59e0b',
      700: '#b45309'
    },
    danger: {
      50: '#fef2f2',
      500: '#ef4444',
      700: '#b91c1c'
    }
  };

  // Navigation tabs configuration
  const navigationTabs = [
    {
      id: 'employee_database',
      label: 'Employee Database',
      icon: '👥',
      description: 'Complete employee records',
      gradient: 'from-blue-600 to-blue-700',
      activeColor: 'border-blue-600 text-blue-700 bg-blue-50'
    },
    {
      id: 'interview_scheduled', 
      label: 'Interview Scheduled',
      icon: '📅',
      description: 'Candidate interviews & scheduling',
      gradient: 'from-green-600 to-green-700',
      activeColor: 'border-green-600 text-green-700 bg-green-50'
    },
    {
      id: 'working_employee',
      label: 'Working Employee Database', 
      icon: '💼',
      description: 'Active employee management',
      gradient: 'from-purple-600 to-purple-700',
      activeColor: 'border-purple-600 text-purple-700 bg-purple-50'
    },
    {
      id: 'announcements',
      label: 'Announcements',
      icon: '📢', 
      description: 'Company communications',
      gradient: 'from-orange-600 to-orange-700',
      activeColor: 'border-orange-600 text-orange-700 bg-orange-50'
    },
    {
      id: 'holiday_calendar',
      label: 'Yearly Holiday Calendar',
      icon: '📆',
      description: 'Company holidays & calendar',
      gradient: 'from-red-600 to-red-700', 
      activeColor: 'border-red-600 text-red-700 bg-red-50'
    }
  ];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch all required data
      const [employeesRes, statsRes] = await Promise.all([
        axios.get(`${API}/employees`),
        axios.get(`${API}/dashboard/stats`)
      ]);
      
      setEmployees(employeesRes.data);
      setDashboardStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const getCurrentTab = () => {
    return navigationTabs.find(tab => tab.id === currentTab) || navigationTabs[0];
  };

  const StatCard = ({ title, value, icon, gradient, subtitle, trend }) => (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 p-6 text-white transform hover:scale-105 border border-opacity-20 border-white`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-4xl filter drop-shadow-lg">{icon}</div>
          <div>
            <h3 className="text-white text-base font-bold opacity-90">{title}</h3>
            {subtitle && <p className="text-white text-sm opacity-75">{subtitle}</p>}
          </div>
        </div>
        {trend && (
          <div className="bg-white bg-opacity-20 text-white text-xs px-3 py-1 rounded-full font-semibold">
            {trend}
          </div>
        )}
      </div>
      <div className="text-white">
        <p className="text-4xl font-bold mb-2 filter drop-shadow-sm">{value || 0}</p>
        <div className="w-full bg-white bg-opacity-25 rounded-full h-2">
          <div className="bg-white h-2 rounded-full opacity-80 transition-all duration-1000" 
               style={{ width: `${Math.min((value / 20) * 100, 100)}%` }}>
          </div>
        </div>
      </div>
    </div>
  );

  // Salary slip sharing handlers
  const handleSalarySlipShare = (employee) => {
    setSelectedEmployee(employee);
    setShareChannels([]);
    setShareResults(null);
    setShowSalaryShareModal(true);
  };

  const handleEmployeeDocuments = (employee) => {
    // TODO: Implement employee documents modal
    alert(`Document management for ${employee.full_name} - Coming soon!`);
  };

  // Add employee handlers
  const handleAddEmployee = () => {
    setShowAddEmployeeModal(true);
    setNewEmployeeData({
      full_name: '',
      employee_id: '',
      email_address: '',
      contact_number: '',
      department: '',
      designation: '',
      address: '',
      basic_salary: '',
      join_date: new Date().toISOString().split('T')[0]
    });
  };

  const handleEmployeeInputChange = (field, value) => {
    setNewEmployeeData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddEmployeeSubmit = async (e) => {
    e.preventDefault();
    setAddEmployeeLoading(true);

    try {
      // Validate required fields
      const requiredFields = ['full_name', 'employee_id', 'email_address', 'contact_number', 'department', 'designation', 'basic_salary'];
      const missingFields = requiredFields.filter(field => !newEmployeeData[field]);
      
      if (missingFields.length > 0) {
        alert(`Please fill in all required fields: ${missingFields.join(', ')}`);
        return;
      }

      // Convert basic_salary to number
      const employeeData = {
        ...newEmployeeData,
        basic_salary: parseFloat(newEmployeeData.basic_salary),
        status: 'Active'
      };

      const response = await axios.post(`${API}/employees`, employeeData);
      
      alert('Employee added successfully!');
      setShowAddEmployeeModal(false);
      fetchEmployees(); // Refresh employee list
      fetchDashboardStats(); // Refresh dashboard stats
      
    } catch (error) {
      alert(error.response?.data?.detail || 'Error adding employee');
    } finally {
      setAddEmployeeLoading(false);
    }
  };

  const handleShareChannelToggle = (channel) => {
    setShareChannels(prev => 
      prev.includes(channel) 
        ? prev.filter(c => c !== channel)
        : [...prev, channel]
    );
  };

  const handleSalaryShareSubmit = async () => {
    if (!selectedEmployee || shareChannels.length === 0) {
      alert('Please select at least one sharing channel');
      return;
    }

    setShareLoading(true);
    setShareResults(null);

    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee.employee_id}/share-salary-slip`, {
        month: selectedMonth,
        year: selectedYear,
        channels: shareChannels
      });

      setShareResults(response.data);
      alert('Salary slip shared successfully!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error sharing salary slip');
    } finally {
      setShareLoading(false);
    }
  };

  const renderTabContent = () => {
    switch (currentTab) {
      case 'employee_database':
        return <EmployeeDatabaseTab 
          employees={employees} 
          onSalarySlipShare={handleSalarySlipShare}
          onEmployeeDocuments={handleEmployeeDocuments}
          onAddEmployee={handleAddEmployee}
        />;
      case 'interview_scheduled':
        return <InterviewScheduledTab />;
      case 'working_employee':
        return <WorkingEmployeeDatabase currentUser={user} />;
      case 'announcements':
        return <AnnouncementManagement currentUser={user} />;
      case 'holiday_calendar':
        return <HolidayCalendarTab />;
      default:
        return <EmployeeDatabaseTab employees={employees} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      
      {/* Professional Header */}
      <header className="bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 shadow-2xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            
            {/* LEFT SIDE: Logo and Company Info */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-4">
                {/* Large Professional Logo */}
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-br from-white to-blue-100 rounded-2xl p-3 shadow-2xl border-4 border-blue-300 hover:scale-105 transform transition-transform duration-300">
                    <img 
                      src={logoUrl} 
                      alt="Vishwas World Tech Logo"
                      className="w-full h-full object-contain rounded-xl"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    <div className="w-full h-full bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl hidden items-center justify-center">
                      <span className="text-white font-bold text-2xl">VWT</span>
                    </div>
                  </div>
                  <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  </div>
                </div>
                
                {/* Company Information */}
                <div className="text-white">
                  <h1 className="text-4xl font-bold tracking-wide bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                    VISHWAS WORLD TECH
                  </h1>
                  <p className="text-blue-200 text-lg font-bold">PRIVATE LIMITED</p>
                  <p className="text-blue-300 text-sm font-medium">100 DC Complex, Chandra Layout, Bangalore - 560040</p>
                  <p className="text-blue-400 text-xs">📞 +91-80-12345678 | 📧 hr@vishwasworldtech.com</p>
                </div>
              </div>
            </div>
            
            {/* RIGHT SIDE: HR Login Information */}
            <div className="flex items-center space-x-6">
              {/* HR Portal Card */}
              <div className="bg-gradient-to-br from-blue-800 to-indigo-800 rounded-2xl p-6 border-2 border-blue-500 shadow-xl">
                <div className="text-center">
                  <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg">
                    <span className="text-2xl font-bold text-blue-600">
                      {user?.full_name?.charAt(0) || 'H'}
                    </span>
                  </div>
                  <p className="text-blue-200 text-sm font-semibold">👨‍💼 HR Portal Access</p>
                  <p className="font-bold text-xl text-white mb-1">{user?.full_name}</p>
                  <p className="text-blue-300 text-sm">{user?.designation}</p>
                  <p className="text-blue-400 text-xs">{user?.department} Department</p>
                  <p className="text-blue-500 text-xs mt-1">ID: {user?.employee_id}</p>
                  
                  {/* Current Time */}
                  <div className="mt-3 bg-blue-700 bg-opacity-50 rounded-lg px-3 py-1">
                    <p className="text-yellow-300 text-xs font-semibold">
                      🕐 {new Date().toLocaleTimeString('en-IN', { 
                        timeZone: 'Asia/Kolkata',
                        hour12: true 
                      })} IST
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Professional Logout Button */}
              <button
                onClick={logout}
                className="bg-gradient-to-br from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-8 py-4 rounded-2xl font-bold transition-all duration-200 shadow-xl hover:shadow-2xl flex items-center space-x-3 border-2 border-red-500 hover:scale-105 transform"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="text-lg">HR Logout</span>
              </button>
            </div>
          </div>
          
          {/* Working Hours Banner */}
          <div className="mt-6 bg-gradient-to-r from-blue-800 to-indigo-800 bg-opacity-80 rounded-2xl p-4 border-2 border-blue-500 shadow-lg">
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-3">
                  <svg className="w-6 h-6 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-lg font-bold">Working Hours: 9:45 AM - 6:45 PM (Monday - Friday)</span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="bg-green-500 px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-2">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  <span>GPS Tracking Active</span>
                </span>
                <span className="bg-yellow-500 px-4 py-2 rounded-full text-sm font-bold">
                  ⚠️ Late Login Penalties Apply
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Elegant Navigation */}
      <nav className="bg-white shadow-lg border-b-4 border-blue-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              {navigationTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setCurrentTab(tab.id)}
                  className={`group px-6 py-4 border-b-4 font-bold text-base transition-all duration-300 hover:bg-gray-50 ${
                    currentTab === tab.id 
                      ? tab.activeColor
                      : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl group-hover:scale-110 transform transition-transform duration-200">
                      {tab.icon}
                    </span>
                    <div className="text-left">
                      <div className="font-bold">{tab.label}</div>
                      <div className="text-xs opacity-70">{tab.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            
            {/* Quick Stats in Navigation */}
            <div className="hidden lg:flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2 text-gray-600">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-medium">{dashboardStats.total_employees || 0} Active Employees</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="font-medium">{dashboardStats.present_today || 0} Present Today</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Dashboard Statistics Overview */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Employees"
            subtitle="Active Workforce" 
            value={dashboardStats.total_employees || 0}
            icon="👥"
            gradient="from-blue-600 to-blue-800"
            trend="+5 this month"
          />
          <StatCard
            title="Present Today"
            subtitle="Current Attendance"
            value={dashboardStats.present_today || 0}
            icon="✅"
            gradient="from-green-600 to-green-800"
            trend={`${Math.round(((dashboardStats.present_today || 0) / (dashboardStats.total_employees || 1)) * 100)}% rate`}
          />
          <StatCard
            title="Currently Online"
            subtitle="Active Now"
            value={dashboardStats.logged_in_now || 0}
            icon="🟢"
            gradient="from-yellow-600 to-orange-600"
            trend="Live"
          />
          <StatCard
            title="Absent Today"
            subtitle="Not Present"
            value={dashboardStats.absent_today || 0}
            icon="⚠️"
            gradient="from-red-600 to-red-800"
            trend="Tracking"
          />
        </div>

        {/* Main Content Area */}
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">
          
          {/* Tab Content Header */}
          <div className={`bg-gradient-to-r ${getCurrentTab().gradient} text-white p-8`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-5xl filter drop-shadow-lg">{getCurrentTab().icon}</div>
                <div>
                  <h1 className="text-3xl font-bold">{getCurrentTab().label}</h1>
                  <p className="text-lg opacity-90">{getCurrentTab().description}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm opacity-75">Vishwas World Tech</p>
                <p className="text-lg font-bold">HRMS Dashboard</p>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Professional Footer */}
      <ProfessionalFooter />
    </div>
  );
};

// Employee Database Tab Component
const EmployeeDatabaseTab = ({ employees, onSalarySlipShare, onEmployeeDocuments, onAddEmployee }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Complete Employee Database</h2>
        <button 
          onClick={onAddEmployee}
          className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition shadow-lg flex items-center space-x-2"
        >
          <span>+</span>
          <span>Add New Employee</span>
        </button>
      </div>

      {/* Employee Table */}
      <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-blue-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Employee</th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Department</th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Designation</th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Joining Date</th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Contact</th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-right text-sm font-bold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {employees.map((employee, index) => (
                <tr key={employee.id} className={`hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-md">
                        {employee.full_name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-base font-bold text-gray-900">{employee.full_name}</div>
                        <div className="text-sm text-blue-600 font-semibold">ID: {employee.employee_id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                      {employee.department}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {employee.designation}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-bold text-gray-900">
                      {new Date(employee.join_date).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>
                    <div className="text-xs text-green-600 font-semibold">
                      📅 {(() => {
                        const join = new Date(employee.join_date);
                        const now = new Date();
                        const diffTime = Math.abs(now - join);
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        const years = Math.floor(diffDays / 365);
                        const months = Math.floor((diffDays % 365) / 30);
                        return years > 0 ? `${years}y ${months}m` : `${months}m`;
                      })()} tenure
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{employee.contact_number}</div>
                    <div className="text-xs text-blue-600">{employee.email_address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-3 py-1 text-sm font-bold rounded-full ${
                      employee.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {employee.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onSalarySlipShare(employee)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
                        title="Generate & Share Salary Slip"
                      >
                        <span>💰</span>
                        <span>Share Salary</span>
                      </button>
                      <button
                        onClick={() => onEmployeeDocuments(employee)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
                        title="Employee Documents"
                      >
                        <span>📄</span>
                        <span>Docs</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Interview Scheduled Tab Component
const InterviewScheduledTab = () => {
  return (
    <div className="space-y-6">
      <div className="text-center py-16">
        <div className="text-6xl mb-6">📅</div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Interview Management System</h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">
          Schedule, manage, and track candidate interviews with comprehensive workflow management.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-6 shadow-xl">
            <div className="text-3xl mb-3">📋</div>
            <h3 className="text-xl font-bold mb-2">Schedule Interviews</h3>
            <p className="text-green-100">Manage candidate scheduling and interviewer assignments</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6 shadow-xl">
            <div className="text-3xl mb-3">👥</div>
            <h3 className="text-xl font-bold mb-2">Track Candidates</h3>
            <p className="text-blue-100">Monitor interview progress and candidate status</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-2xl p-6 shadow-xl">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-xl font-bold mb-2">Interview Analytics</h3>
            <p className="text-purple-100">Analyze interview success rates and hiring metrics</p>
          </div>
        </div>
        
        <button className="mt-8 bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-4 rounded-2xl hover:from-green-700 hover:to-green-800 transition shadow-xl font-bold text-lg">
          + Schedule New Interview
        </button>
      </div>
    </div>
  );
};

// Holiday Calendar Tab Component  
const HolidayCalendarTab = () => {
  const currentYear = new Date().getFullYear();
  
  const nationalHolidays = [
    { name: "New Year's Day", date: `${currentYear}-01-01`, type: "National" },
    { name: "Republic Day", date: `${currentYear}-01-26`, type: "National" },
    { name: "Holi", date: `${currentYear}-03-13`, type: "Festival" },
    { name: "Good Friday", date: `${currentYear}-04-18`, type: "National" },
    { name: "Independence Day", date: `${currentYear}-08-15`, type: "National" },
    { name: "Gandhi Jayanti", date: `${currentYear}-10-02`, type: "National" },
    { name: "Diwali", date: `${currentYear}-11-12`, type: "Festival" },
    { name: "Christmas Day", date: `${currentYear}-12-25`, type: "National" },
  ];

  const regionalHolidays = [
    { name: "Karnataka Rajyotsava", date: `${currentYear}-11-01`, type: "Regional" },
    { name: "Ugadi", date: `${currentYear}-04-09`, type: "Regional" },
    { name: "Gowri Ganesha", date: `${currentYear}-09-07`, type: "Regional" },
  ];

  const getHolidayColor = (type) => {
    switch (type) {
      case 'National': return 'bg-red-100 text-red-800 border-red-200';
      case 'Regional': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Festival': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-900">Holiday Calendar {currentYear}</h2>
        <button className="bg-red-600 text-white px-6 py-3 rounded-xl hover:bg-red-700 transition shadow-lg">
          + Add Custom Holiday
        </button>
      </div>

      {/* Holiday Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-6 shadow-xl">
          <div className="text-3xl mb-2">🏛️</div>
          <h3 className="text-xl font-bold">{nationalHolidays.length}</h3>
          <p className="text-red-100">National Holidays</p>
        </div>
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6 shadow-xl">
          <div className="text-3xl mb-2">🌍</div>
          <h3 className="text-xl font-bold">{regionalHolidays.length}</h3>
          <p className="text-blue-100">Regional Holidays</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-6 shadow-xl">
          <div className="text-3xl mb-2">📅</div>
          <h3 className="text-xl font-bold">{nationalHolidays.length + regionalHolidays.length}</h3>
          <p className="text-green-100">Total Holidays</p>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-2xl p-6 shadow-xl">
          <div className="text-3xl mb-2">⏰</div>
          <h3 className="text-xl font-bold">{365 - (nationalHolidays.length + regionalHolidays.length)}</h3>
          <p className="text-purple-100">Working Days</p>
        </div>
      </div>

      {/* Holiday List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* National Holidays */}
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            🏛️ National Holidays
          </h3>
          <div className="space-y-3">
            {nationalHolidays.map((holiday, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-red-50 border border-red-100 rounded-xl hover:shadow-md transition-shadow">
                <div>
                  <h4 className="font-semibold text-gray-900">{holiday.name}</h4>
                  <p className="text-sm text-gray-600">{new Date(holiday.date).toLocaleDateString('en-IN', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getHolidayColor(holiday.type)}`}>
                  {holiday.type}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Regional Holidays */}
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            🌍 Regional Holidays (Karnataka)
          </h3>
          <div className="space-y-3">
            {regionalHolidays.map((holiday, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-blue-50 border border-blue-100 rounded-xl hover:shadow-md transition-shadow">
                <div>
                  <h4 className="font-semibold text-gray-900">{holiday.name}</h4>
                  <p className="text-sm text-gray-600">{new Date(holiday.date).toLocaleDateString('en-IN', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getHolidayColor(holiday.type)}`}>
                  {holiday.type}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Salary Slip Sharing Modal */}
      {showSalaryShareModal && selectedEmployee && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  💰 Share Salary Slip
                </h2>
                <button
                  onClick={() => setShowSalaryShareModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <h3 className="font-semibold text-blue-900">{selectedEmployee.full_name}</h3>
                <p className="text-blue-700 text-sm mt-1">
                  Employee ID: {selectedEmployee.employee_id} • {selectedEmployee.department} • {selectedEmployee.designation}
                </p>
                <p className="text-blue-600 text-sm">Basic Salary: ₹{selectedEmployee.basic_salary?.toLocaleString()}</p>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Month and Year Selection */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Month</label>
                  <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none"
                  >
                    {Array.from({length: 12}, (_, i) => i + 1).map(month => (
                      <option key={month} value={month}>
                        {new Date(2024, month - 1, 1).toLocaleString('default', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Year</label>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none"
                  >
                    <option value={2024}>2024</option>
                    <option value={2025}>2025</option>
                  </select>
                </div>
              </div>

              {/* Sharing Channels */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  📡 Select Sharing Channels
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { id: 'email', label: 'Email', icon: '📧', color: 'blue', desc: 'Professional email with PDF attachment' },
                    { id: 'whatsapp', label: 'WhatsApp', icon: '💬', color: 'green', desc: 'Instant WhatsApp notification' },
                    { id: 'sms', label: 'SMS', icon: '📱', color: 'purple', desc: 'SMS text message notification' }
                  ].map(channel => (
                    <label key={channel.id} className="cursor-pointer">
                      <input
                        type="checkbox"
                        checked={shareChannels.includes(channel.id)}
                        onChange={() => handleShareChannelToggle(channel.id)}
                        className="sr-only"
                      />
                      <div className={`p-4 border-2 rounded-xl transition-all ${
                        shareChannels.includes(channel.id)
                          ? `border-${channel.color}-500 bg-${channel.color}-50`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{channel.icon}</span>
                          <div>
                            <div className="font-semibold text-gray-900">{channel.label}</div>
                            <div className="text-sm text-gray-600">{channel.desc}</div>
                          </div>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Share Results */}
              {shareResults && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                  <h3 className="font-semibold text-green-900 mb-3 flex items-center">
                    ✅ Sharing Results
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(shareResults.sharing_results).map(([channel, result]) => (
                      <div key={channel} className="flex items-center justify-between p-3 bg-white border border-green-100 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="capitalize font-medium text-gray-900">{channel}</span>
                          {result.status === 'success' ? (
                            <span className="text-green-600">✅ Sent</span>
                          ) : (
                            <span className="text-red-600">❌ Failed</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600">
                          To: {result.recipient}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 text-sm text-gray-600">
                    💼 Salary slip for {selectedEmployee.full_name} - {selectedMonth.toString().padStart(2, '0')}/{selectedYear}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 flex space-x-4">
              <button
                onClick={handleSalaryShareSubmit}
                disabled={shareLoading || shareChannels.length === 0}
                className="flex-1 bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50 font-semibold flex items-center justify-center space-x-2"
              >
                {shareLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating & Sharing...
                  </>
                ) : (
                  <>
                    <span>💰</span>
                    <span>Generate & Share Salary Slip</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setShowSalaryShareModal(false)}
                className="flex-1 bg-gray-600 text-white py-3 rounded-xl hover:bg-gray-700 transition font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ElegantProfessionalDashboard;