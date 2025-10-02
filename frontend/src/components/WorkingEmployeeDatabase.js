import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkingEmployeeDatabase = ({ currentUser }) => {
  const [workingEmployees, setWorkingEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [attendanceDetails, setAttendanceDetails] = useState([]);
  const [monthlyReport, setMonthlyReport] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [showDocumentUpload, setShowDocumentUpload] = useState(false);
  const [employeeDocuments, setEmployeeDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  // Document categories for working employees
  const documentCategories = {
    "Personal Documents": {
      icon: "🆔",
      color: "bg-blue-100 text-blue-800",
      documents: ["Aadhar Card", "PAN Card", "Passport Size Photo", "Address Proof"]
    },
    "Educational Documents": {
      icon: "🎓", 
      color: "bg-green-100 text-green-800",
      documents: ["10th Mark Sheet", "12th Mark Sheet", "Graduation Certificate", "Post Graduation Certificate"]
    },
    "Previous Employment": {
      icon: "💼",
      color: "bg-purple-100 text-purple-800", 
      documents: ["Resume/CV", "Previous Company Offer Letter", "Previous Company Appointment Letter", "Previous Salary Slips", "Experience Letter", "Relieving Letter"]
    },
    "Current Employment": {
      icon: "🏢",
      color: "bg-yellow-100 text-yellow-800",
      documents: ["Updated Resume", "Employee Agreement", "Medical Certificate", "Background Verification"]
    }
  };

  useEffect(() => {
    fetchWorkingEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmployee) {
      fetchEmployeeAttendanceDetails();
      fetchEmployeeDocuments();
    }
  }, [selectedEmployee, selectedMonth, selectedYear]);

  const fetchWorkingEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      // Filter only active working employees
      const workingEmp = response.data.filter(emp => emp.status === 'Active');
      setWorkingEmployees(workingEmp);
    } catch (error) {
      console.error('Error fetching working employees:', error);
    }
  };

  const fetchEmployeeAttendanceDetails = async () => {
    if (!selectedEmployee) return;
    
    setLoading(true);
    try {
      // Get monthly attendance summary
      const summaryResponse = await axios.get(
        `${API}/employees/${selectedEmployee.employee_id}/attendance-summary/${selectedYear}/${selectedMonth}`
      );
      setMonthlyReport(summaryResponse.data);

      // Get detailed attendance records
      const detailsResponse = await axios.get(`${API}/attendance/employee/${selectedEmployee.employee_id}`);
      
      // Filter for current month and add late login analysis
      const currentMonthRecords = detailsResponse.data.filter(record => {
        const recordDate = new Date(record.date);
        return recordDate.getMonth() + 1 === selectedMonth && recordDate.getFullYear() === selectedYear;
      });

      // Enhance records with late login analysis
      const enhancedRecords = currentMonthRecords.map(record => ({
        ...record,
        late_minutes: calculateLateMinutes(record.login_time),
        penalty_amount: calculatePenaltyAmount(record.login_time),
        working_hours: calculateWorkingHours(record.login_time, record.logout_time)
      }));

      setAttendanceDetails(enhancedRecords);
    } catch (error) {
      console.error('Error fetching attendance details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployeeDocuments = async () => {
    if (!selectedEmployee) return;

    try {
      const response = await axios.get(`${API}/employees/${selectedEmployee.employee_id}/documents`);
      setEmployeeDocuments(response.data);
    } catch (error) {
      console.error('Error fetching employee documents:', error);
    }
  };

  const calculateLateMinutes = (loginTimeStr) => {
    if (!loginTimeStr) return 0;
    
    const loginTime = new Date(loginTimeStr);
    const scheduledTime = new Date(loginTime);
    scheduledTime.setHours(9, 45, 0); // 9:45 AM
    
    const diffMs = loginTime - scheduledTime;
    const diffMinutes = Math.max(0, Math.floor(diffMs / (1000 * 60)));
    
    return diffMinutes;
  };

  const calculatePenaltyAmount = (loginTimeStr) => {
    const lateMinutes = calculateLateMinutes(loginTimeStr);
    
    if (lateMinutes <= 15) return 0;        // Grace period
    if (lateMinutes <= 30) return 200;      // 16-30 minutes
    if (lateMinutes <= 60) return 500;      // 31-60 minutes  
    return 1000;                            // More than 60 minutes
  };

  const calculateWorkingHours = (loginTimeStr, logoutTimeStr) => {
    if (!loginTimeStr || !logoutTimeStr) return 0;
    
    const loginTime = new Date(loginTimeStr);
    const logoutTime = new Date(logoutTimeStr);
    
    const diffMs = logoutTime - loginTime;
    const diffHours = diffMs / (1000 * 60 * 60);
    
    // Subtract 1 hour lunch break
    return Math.max(0, diffHours - 1);
  };

  const calculateTenure = (joinDate) => {
    const join = new Date(joinDate);
    const now = new Date();
    
    const years = now.getFullYear() - join.getFullYear();
    const months = now.getMonth() - join.getMonth();
    
    let totalMonths = years * 12 + months;
    if (totalMonths < 0) totalMonths = 0;
    
    const displayYears = Math.floor(totalMonths / 12);
    const displayMonths = totalMonths % 12;
    
    if (displayYears === 0) {
      return `${displayMonths} month${displayMonths !== 1 ? 's' : ''}`;
    } else if (displayMonths === 0) {
      return `${displayYears} year${displayYears !== 1 ? 's' : ''}`;
    } else {
      return `${displayYears} year${displayYears !== 1 ? 's' : ''}, ${displayMonths} month${displayMonths !== 1 ? 's' : ''}`;
    }
  };

  const getTotalPenalties = () => {
    return attendanceDetails.reduce((total, record) => total + (record.penalty_amount || 0), 0);
  };

  const getLateLoginCount = () => {
    return attendanceDetails.filter(record => record.late_minutes > 15).length;
  };

  const getDocumentCompletionPercentage = (empId) => {
    const totalRequired = Object.values(documentCategories).reduce(
      (sum, cat) => sum + cat.documents.length, 0
    );
    const uploadedCount = employeeDocuments.length;
    return totalRequired > 0 ? Math.round((uploadedCount / totalRequired) * 100) : 0;
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return '--';
    return new Date(timeStr).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-4 flex items-center">
          💼 Working Employee Database
        </h1>
        <p className="text-purple-100 text-lg">
          Comprehensive management of active employees with attendance tracking and document management
        </p>
      </div>

      {/* Employee Selection and Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Employee List Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center justify-between">
              👥 Working Employees
              <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                {workingEmployees.length} Active
              </span>
            </h2>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {workingEmployees.map((employee) => (
                <div
                  key={employee.id}
                  onClick={() => setSelectedEmployee(employee)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
                    selectedEmployee?.employee_id === employee.employee_id
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {employee.full_name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{employee.full_name}</h3>
                      <p className="text-sm text-gray-600">{employee.employee_id} • {employee.department}</p>
                      <p className="text-xs text-purple-600 font-medium">
                        🗓️ Joined: {formatDate(employee.join_date)}
                      </p>
                      <p className="text-xs text-gray-500">
                        ⏱️ Tenure: {calculateTenure(employee.join_date)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Employee Details Panel */}
        <div className="lg:col-span-2">
          {selectedEmployee ? (
            <div className="space-y-6">
              
              {/* Employee Profile Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                    👤 Employee Profile
                  </h2>
                  <div className="text-sm text-gray-600">
                    Last Updated: {new Date().toLocaleDateString()}
                  </div>
                </div>

                {/* Employee Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                    <h3 className="font-semibold text-purple-900 mb-3">Personal Information</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium text-gray-700">Full Name:</span> {selectedEmployee.full_name}</p>
                      <p><span className="font-medium text-gray-700">Employee ID:</span> {selectedEmployee.employee_id}</p>
                      <p><span className="font-medium text-gray-700">Email:</span> {selectedEmployee.email_address}</p>
                      <p><span className="font-medium text-gray-700">Contact:</span> {selectedEmployee.contact_number}</p>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                    <h3 className="font-semibold text-blue-900 mb-3">Employment Details</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium text-gray-700">Department:</span> {selectedEmployee.department}</p>
                      <p><span className="font-medium text-gray-700">Designation:</span> {selectedEmployee.designation}</p>
                      <p><span className="font-medium text-gray-700">🗓️ Joining Date:</span> 
                        <span className="font-bold text-blue-700 ml-1">
                          {formatDate(selectedEmployee.join_date)}
                        </span>
                      </p>
                      <p><span className="font-medium text-gray-700">⏱️ Tenure:</span> 
                        <span className="font-bold text-green-700 ml-1">
                          {calculateTenure(selectedEmployee.join_date)}
                        </span>
                      </p>
                      <p><span className="font-medium text-gray-700">💰 Basic Salary:</span> ₹{selectedEmployee.basic_salary.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* Month/Year Selection */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Select Month</label>
                    <select
                      value={selectedMonth}
                      onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      {[
                        {value: 1, name: 'January'}, {value: 2, name: 'February'}, {value: 3, name: 'March'},
                        {value: 4, name: 'April'}, {value: 5, name: 'May'}, {value: 6, name: 'June'},
                        {value: 7, name: 'July'}, {value: 8, name: 'August'}, {value: 9, name: 'September'},
                        {value: 10, name: 'October'}, {value: 11, name: 'November'}, {value: 12, name: 'December'}
                      ].map(month => (
                        <option key={month.value} value={month.value}>{month.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Select Year</label>
                    <select
                      value={selectedYear}
                      onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      {[2024, 2025, 2026].map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-end">
                    <button
                      onClick={() => setShowDocumentUpload(true)}
                      className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition flex items-center justify-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span>Upload Documents</span>
                    </button>
                  </div>
                </div>

                {/* Attendance Summary Cards */}
                {monthlyReport && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
                      <h4 className="font-semibold text-green-900">Present Days</h4>
                      <p className="text-3xl font-bold text-green-700">{monthlyReport.present_days}</p>
                      <p className="text-green-600 text-sm">out of {monthlyReport.total_working_days}</p>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
                      <h4 className="font-semibold text-yellow-900">Late Logins</h4>
                      <p className="text-3xl font-bold text-yellow-700">{getLateLoginCount()}</p>
                      <p className="text-yellow-600 text-sm">penalty days</p>
                    </div>

                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                      <h4 className="font-semibold text-red-900">Total Penalties</h4>
                      <p className="text-3xl font-bold text-red-700">₹{getTotalPenalties()}</p>
                      <p className="text-red-600 text-sm">salary deduction</p>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
                      <h4 className="font-semibold text-blue-900">Attendance %</h4>
                      <p className="text-3xl font-bold text-blue-700">{monthlyReport.attendance_percentage}%</p>
                      <p className="text-blue-600 text-sm">this month</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Login/Logout Details Table */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  ⏰ Daily Login/Logout Details - {new Date(selectedYear, selectedMonth - 1).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
                </h3>

                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading attendance details...</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full table-auto">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Login Time</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Logout Time</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Late Minutes</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Working Hours</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Penalty Amount</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {attendanceDetails.map((record, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm font-medium text-gray-900">
                              {formatDate(record.date)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {formatTime(record.login_time)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {formatTime(record.logout_time)}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                record.late_minutes === 0 ? 'bg-green-100 text-green-800' :
                                record.late_minutes <= 15 ? 'bg-yellow-100 text-yellow-800' :
                                record.late_minutes <= 30 ? 'bg-orange-100 text-orange-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {record.late_minutes} min
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {record.working_hours.toFixed(2)} hrs
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`font-bold ${
                                record.penalty_amount === 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                ₹{record.penalty_amount}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                record.status === 'Logged In' ? 'bg-green-100 text-green-800' :
                                record.status === 'Logged Out' ? 'bg-blue-100 text-blue-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {record.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                        
                        {attendanceDetails.length === 0 && (
                          <tr>
                            <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                              No attendance records found for {new Date(selectedYear, selectedMonth - 1).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Summary Section */}
                {attendanceDetails.length > 0 && (
                  <div className="mt-6 bg-gray-50 rounded-xl p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                      <div>
                        <span className="block text-2xl font-bold text-purple-700">{attendanceDetails.length}</span>
                        <span className="text-sm text-gray-600">Total Records</span>
                      </div>
                      <div>
                        <span className="block text-2xl font-bold text-red-700">{getLateLoginCount()}</span>
                        <span className="text-sm text-gray-600">Late Logins</span>
                      </div>
                      <div>
                        <span className="block text-2xl font-bold text-orange-700">
                          {attendanceDetails.reduce((sum, r) => sum + r.late_minutes, 0)} min
                        </span>
                        <span className="text-sm text-gray-600">Total Late Minutes</span>
                      </div>
                      <div>
                        <span className="block text-2xl font-bold text-green-700">
                          {attendanceDetails.reduce((sum, r) => sum + r.working_hours, 0).toFixed(1)} hrs
                        </span>
                        <span className="text-sm text-gray-600">Total Working Hours</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Document Management Section */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center">
                    📄 Employee Documents
                    <span className="ml-3 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                      {getDocumentCompletionPercentage()}% Complete
                    </span>
                  </h3>
                  <button
                    onClick={() => setShowDocumentUpload(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span>Upload</span>
                  </button>
                </div>

                {/* Document Categories */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(documentCategories).map(([categoryName, categoryInfo]) => (
                    <div key={categoryName} className="border border-gray-200 rounded-xl p-4">
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <span className="text-2xl mr-2">{categoryInfo.icon}</span>
                        {categoryName}
                      </h4>
                      
                      <div className="space-y-2">
                        {categoryInfo.documents.map((docType) => {
                          const isUploaded = employeeDocuments.some(doc => doc.document_type === docType);
                          return (
                            <div key={docType} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                              <span className="text-sm text-gray-700">{docType}</span>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                isUploaded ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {isUploaded ? '✅ Uploaded' : '❌ Missing'}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Document Upload Progress */}
                <div className="mt-6 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">Document Completion Progress</h4>
                    <span className="text-sm font-bold text-blue-700">{getDocumentCompletionPercentage()}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-blue-600 to-green-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${getDocumentCompletionPercentage()}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    {employeeDocuments.length} of {Object.values(documentCategories).reduce((sum, cat) => sum + cat.documents.length, 0)} documents uploaded
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* No Employee Selected */
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
              <div className="text-6xl mb-4">💼</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Select a Working Employee</h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Choose an employee from the list to view their detailed attendance records, 
                late login analysis, salary deductions, and document management.
              </p>
              
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-2xl mb-2">📊</div>
                  <h4 className="font-semibold text-blue-900">Attendance Tracking</h4>
                  <p className="text-blue-700 text-sm">Daily login/logout details</p>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-2xl mb-2">⚠️</div>
                  <h4 className="font-semibold text-yellow-900">Late Login Analysis</h4>
                  <p className="text-yellow-700 text-sm">Penalty calculations</p>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-2xl mb-2">📄</div>
                  <h4 className="font-semibold text-green-900">Document Management</h4>
                  <p className="text-green-700 text-sm">Upload & track documents</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Document Upload Modal */}
      {showDocumentUpload && selectedEmployee && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900">
                📤 Upload Documents for {selectedEmployee.full_name}
              </h3>
              <button
                onClick={() => setShowDocumentUpload(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Document Categories for Upload */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(documentCategories).map(([categoryName, categoryInfo]) => (
                <div key={categoryName} className={`border-2 border-gray-200 rounded-xl p-6 hover:border-purple-300 transition-colors`}>
                  <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <span className="text-3xl mr-3">{categoryInfo.icon}</span>
                    {categoryName}
                  </h4>
                  
                  <div className="space-y-3">
                    {categoryInfo.documents.map((docType) => {
                      const isUploaded = employeeDocuments.some(doc => doc.document_type === docType);
                      return (
                        <div key={docType} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium text-gray-700">{docType}</span>
                          {isUploaded ? (
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-bold">
                              ✅ Uploaded
                            </span>
                          ) : (
                            <button className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition">
                              Upload
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => setShowDocumentUpload(false)}
                className="bg-gray-600 text-white px-8 py-3 rounded-xl hover:bg-gray-700 transition font-semibold"
              >
                Close Document Manager
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkingEmployeeDatabase;