import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";
import ProfessionalHeader from "./components/ProfessionalHeader";
import EnhancedDashboard from "./components/EnhancedDashboard";
import DocumentManagement from "./components/DocumentManagement";
import AnnouncementManagement from "./components/AnnouncementManagement";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, [token]);

  const login = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', userToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${userToken}`;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Professional Login Component with Logo
const LoginPage = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const logoUrl = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg";

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      login(response.data.employee, response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 flex items-center justify-center p-4">
      {/* Background Logo Watermark */}
      <div className="absolute inset-0 opacity-5 flex items-center justify-center">
        <img 
          src={logoUrl} 
          alt="Background Logo"
          className="w-96 h-96 object-contain"
        />
      </div>
      
      <div className="max-w-lg w-full bg-white rounded-2xl shadow-2xl p-10 relative z-10">
        <div className="text-center mb-8">
          {/* Company Logo */}
          <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <img 
              src={logoUrl} 
              alt="Vishwas World Tech Logo"
              className="w-20 h-20 object-contain rounded-full"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            <div className="w-20 h-20 bg-blue-600 rounded-full hidden items-center justify-center">
              <span className="text-white font-bold text-2xl">VWT</span>
            </div>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Vishwas World Tech</h1>
          <h2 className="text-xl font-semibold text-blue-600 mb-1">Private Limited</h2>
          <p className="text-gray-600 mb-2">Human Resource Management System</p>
          <p className="text-sm text-gray-500">100 DC Complex, Chandra Layout, Bangalore - 560040</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="Enter your username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing In...
              </span>
            ) : (
              'Sign In to HRMS'
            )}
          </button>
        </form>
        
        {/* Working Hours Notice */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800 text-center">
            <span className="font-semibold">Working Hours:</span> 9:45 AM - 6:45 PM (Mon-Fri)<br/>
            <span className="text-xs">Late login penalties apply as per company policy</span>
          </p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({});
  const [employees, setEmployees] = useState([]);
  const [todayAttendance, setTodayAttendance] = useState([]);
  const [currentView, setCurrentView] = useState('dashboard');
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [attendanceAction, setAttendanceAction] = useState(null);
  const [location, setLocation] = useState(null);
  const [locationError, setLocationError] = useState('');
  const [showSalaryCalculator, setShowSalaryCalculator] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [salaryCalculation, setSalaryCalculation] = useState(null);
  const [calculationMonth, setCalculationMonth] = useState(new Date().getMonth() + 1);
  const [calculationYear, setCalculationYear] = useState(new Date().getFullYear());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);

  const [newEmployee, setNewEmployee] = useState({
    employee_id: '',
    full_name: '',
    department: '',
    designation: '',
    join_date: '',
    manager: '',
    contact_number: '',
    email_address: '',
    address: '',
    basic_salary: '',
    username: '',
    password: ''
  });

  useEffect(() => {
    fetchDashboardStats();
    fetchEmployees();
    fetchTodayAttendance();
    getCurrentLocation();
  }, []);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            address: `${position.coords.latitude}, ${position.coords.longitude}`
          });
        },
        (error) => {
          setLocationError('Location access denied. Please enable location services.');
        }
      );
    } else {
      setLocationError('Geolocation is not supported by this browser.');
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchTodayAttendance = async () => {
    try {
      const response = await axios.get(`${API}/attendance/today`);
      setTodayAttendance(response.data);
    } catch (error) {
      console.error('Error fetching today attendance:', error);
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      const employeeData = {
        ...newEmployee,
        join_date: new Date(newEmployee.join_date).toISOString(),
        basic_salary: parseFloat(newEmployee.basic_salary)
      };
      
      await axios.post(`${API}/employees`, employeeData);
      setShowAddEmployee(false);
      setNewEmployee({
        employee_id: '',
        full_name: '',
        department: '',
        designation: '',
        join_date: '',
        manager: '',
        contact_number: '',
        email_address: '',
        address: '',
        basic_salary: '',
        username: '',
        password: ''
      });
      fetchEmployees();
      fetchDashboardStats();
      alert('Employee added successfully!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error adding employee');
    }
  };

  const handleAttendance = async (action, employeeId) => {
    if (!location) {
      alert('Location is required for attendance tracking');
      return;
    }

    try {
      const endpoint = action === 'login' ? '/attendance/login' : '/attendance/logout';
      const response = await axios.post(`${API}${endpoint}`, {
        employee_id: employeeId,
        location: location
      });
      
      alert(response.data.message);
      fetchTodayAttendance();
      fetchDashboardStats();
    } catch (error) {
      alert(error.response?.data?.detail || `Error during ${action}`);
    }
  };

  const generateDocument = async (employeeId, documentType) => {
    try {
      let endpoint;
      if (documentType === 'offer') {
        endpoint = `/employees/${employeeId}/generate-offer-letter`;
      } else if (documentType === 'appointment') {
        endpoint = `/employees/${employeeId}/generate-appointment-letter`;
      } else if (documentType === 'agreement') {
        endpoint = `/employees/${employeeId}/generate-employee-agreement`;
      }
      
      const response = await axios.post(`${API}${endpoint}`);
      
      // Convert base64 to blob and download
      const pdfData = response.data.pdf_data;
      const byteCharacters = atob(pdfData);
      const byteNumbers = new Array(byteCharacters.length);
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      
      // Create download link
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = response.data.filename;
      link.click();
      
      alert(`${response.data.document_type.replace('_', ' ')} generated and downloaded successfully!`);
    } catch (error) {
      alert(error.response?.data?.detail || `Error generating ${documentType} letter`);
    }
  };

  const calculateSalary = async (employeeId, year, month) => {
    try {
      const response = await axios.post(`${API}/employees/${employeeId}/calculate-salary`, {
        employee_id: employeeId,
        year: year,
        month: month
      });
      
      setSalaryCalculation(response.data.calculation);
      return response.data.calculation;
    } catch (error) {
      alert(error.response?.data?.detail || 'Error calculating salary');
      return null;
    }
  };

  const generateSalarySlip = async (employeeId, year, month) => {
    try {
      const response = await axios.post(`${API}/employees/${employeeId}/generate-salary-slip`, {
        employee_id: employeeId,
        year: year,
        month: month
      });
      
      // Convert base64 to blob and download
      const pdfData = response.data.pdf_data;
      const byteCharacters = atob(pdfData);
      const byteNumbers = new Array(byteCharacters.length);
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      
      // Create download link
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = response.data.filename;
      link.click();
      
      alert('Salary slip generated and downloaded successfully!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error generating salary slip');
    }
  };

  const openSalaryCalculator = (employee) => {
    setSelectedEmployee(employee);
    setShowSalaryCalculator(true);
    setSalaryCalculation(null);
  };

  const handleDeleteEmployee = async (employeeId) => {
    try {
      const response = await axios.delete(`${API}/employees/${employeeId}`);
      alert(response.data.message);
      fetchEmployees();
      fetchDashboardStats();
      setShowDeleteConfirm(null);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error deleting employee');
    }
  };

  const confirmDelete = (employee) => {
    setShowDeleteConfirm(employee);
  };

  const isLoggedInToday = (employeeId) => {
    return todayAttendance.some(record => 
      record.employee_id === employeeId && record.status === 'Logged In'
    );
  };

  const getTodayRecord = (employeeId) => {
    return todayAttendance.find(record => record.employee_id === employeeId);
  };

  const StatCard = ({ title, value, icon, color }) => (
    <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value || 0}</p>
        </div>
        <div className={`p-3 rounded-full ${color.replace('border-', 'bg-').replace('-500', '-100')}`}>
          {icon}
        </div>
      </div>
    </div>
  );

  if (showSalaryCalculator && selectedEmployee) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Salary Calculator</h2>
              <button
                onClick={() => setShowSalaryCalculator(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Employee Info */}
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Employee Information</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <span className="text-sm text-blue-600">Employee ID</span>
                  <div className="font-medium">{selectedEmployee.employee_id}</div>
                </div>
                <div>
                  <span className="text-sm text-blue-600">Name</span>
                  <div className="font-medium">{selectedEmployee.full_name}</div>
                </div>
                <div>
                  <span className="text-sm text-blue-600">Department</span>
                  <div className="font-medium">{selectedEmployee.department}</div>
                </div>
                <div>
                  <span className="text-sm text-blue-600">Basic Salary</span>
                  <div className="font-medium">₹{selectedEmployee.basic_salary.toLocaleString()}</div>
                </div>
              </div>
            </div>

            {/* Calculation Controls */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
                <select
                  value={calculationYear}
                  onChange={(e) => setCalculationYear(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {[2024, 2025, 2026].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Month</label>
                <select
                  value={calculationMonth}
                  onChange={(e) => setCalculationMonth(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
              
              <div className="flex items-end">
                <button
                  onClick={() => calculateSalary(selectedEmployee.employee_id, calculationYear, calculationMonth)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition"
                >
                  Calculate Salary
                </button>
              </div>
            </div>

            {/* Salary Calculation Results */}
            {salaryCalculation && (
              <div className="space-y-6">
                {/* Attendance Summary */}
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-yellow-800 mb-3">Attendance Summary</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <span className="text-sm text-yellow-600">Present Days</span>
                      <div className="text-xl font-bold">{salaryCalculation.employee_details.present_days}</div>
                    </div>
                    <div>
                      <span className="text-sm text-yellow-600">Total Working Days</span>
                      <div className="text-xl font-bold">{salaryCalculation.employee_details.total_working_days}</div>
                    </div>
                    <div>
                      <span className="text-sm text-yellow-600">Absent Days</span>
                      <div className="text-xl font-bold">{salaryCalculation.employee_details.total_working_days - salaryCalculation.employee_details.present_days}</div>
                    </div>
                    <div>
                      <span className="text-sm text-yellow-600">Attendance %</span>
                      <div className="text-xl font-bold">{salaryCalculation.employee_details.attendance_percentage}%</div>
                    </div>
                  </div>
                </div>

                {/* Salary Breakdown */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Earnings */}
                  <div className="bg-green-50 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-green-800 mb-4">Earnings</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span>Basic Salary</span>
                        <span className="font-medium">₹{salaryCalculation.earnings.basic_salary.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>HRA (40%)</span>
                        <span className="font-medium">₹{salaryCalculation.earnings.hra.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>DA (10%)</span>
                        <span className="font-medium">₹{salaryCalculation.earnings.da.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Medical Allowance</span>
                        <span className="font-medium">₹{salaryCalculation.earnings.medical_allowance.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Transport Allowance</span>
                        <span className="font-medium">₹{salaryCalculation.earnings.transport_allowance.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2 font-bold text-green-700">
                        <span>Gross Salary</span>
                        <span>₹{salaryCalculation.earnings.gross_salary.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Deductions */}
                  <div className="bg-red-50 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-red-800 mb-4">Deductions</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span>PF (12%)</span>
                        <span className="font-medium">₹{salaryCalculation.deductions.pf_employee.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>ESI (1.75%)</span>
                        <span className="font-medium">₹{salaryCalculation.deductions.esi_employee.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Professional Tax</span>
                        <span className="font-medium">₹{salaryCalculation.deductions.professional_tax.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Income Tax</span>
                        <span className="font-medium">₹{salaryCalculation.deductions.income_tax.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2 font-bold text-red-700">
                        <span>Total Deductions</span>
                        <span>₹{salaryCalculation.deductions.total_deductions.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Net Salary */}
                <div className="bg-blue-600 text-white rounded-lg p-6">
                  <div className="flex justify-between items-center">
                    <h4 className="text-2xl font-bold">Net Salary Payable</h4>
                    <span className="text-3xl font-bold">₹{salaryCalculation.net_salary.toLocaleString()}</span>
                  </div>
                </div>

                {/* Employer Contributions */}
                <div className="bg-purple-50 rounded-lg p-6">
                  <h4 className="text-lg font-semibold text-purple-800 mb-4">Employer Contributions</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex justify-between">
                      <span>PF (Employer)</span>
                      <span className="font-medium">₹{salaryCalculation.employer_contributions.pf_employer.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>ESI (Employer)</span>
                      <span className="font-medium">₹{salaryCalculation.employer_contributions.esi_employer.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between font-bold">
                      <span>Total</span>
                      <span>₹{salaryCalculation.employer_contributions.total_employer_contribution.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-4">
                  <button
                    onClick={() => generateSalarySlip(selectedEmployee.employee_id, calculationYear, calculationMonth)}
                    className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition flex items-center justify-center space-x-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Download Salary Slip</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (showAddEmployee) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Add New Employee</h2>
              <button
                onClick={() => setShowAddEmployee(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleAddEmployee} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Employee ID</label>
                <input
                  type="text"
                  value={newEmployee.employee_id}
                  onChange={(e) => setNewEmployee({...newEmployee, employee_id: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  value={newEmployee.full_name}
                  onChange={(e) => setNewEmployee({...newEmployee, full_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                <select
                  value={newEmployee.department}
                  onChange={(e) => setNewEmployee({...newEmployee, department: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Department</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Sales">Sales</option>
                  <option value="Marketing">Marketing</option>
                  <option value="HR">HR</option>
                  <option value="Finance">Finance</option>
                  <option value="Operations">Operations</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Designation</label>
                <input
                  type="text"
                  value={newEmployee.designation}
                  onChange={(e) => setNewEmployee({...newEmployee, designation: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Join Date</label>
                <input
                  type="date"
                  value={newEmployee.join_date}
                  onChange={(e) => setNewEmployee({...newEmployee, join_date: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Manager</label>
                <input
                  type="text"
                  value={newEmployee.manager}
                  onChange={(e) => setNewEmployee({...newEmployee, manager: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Number</label>
                <input
                  type="tel"
                  value={newEmployee.contact_number}
                  onChange={(e) => setNewEmployee({...newEmployee, contact_number: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  type="email"
                  value={newEmployee.email_address}
                  onChange={(e) => setNewEmployee({...newEmployee, email_address: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                <textarea
                  value={newEmployee.address}
                  onChange={(e) => setNewEmployee({...newEmployee, address: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Basic Salary</label>
                <input
                  type="number"
                  value={newEmployee.basic_salary}
                  onChange={(e) => setNewEmployee({...newEmployee, basic_salary: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                <input
                  type="text"
                  value={newEmployee.username}
                  onChange={(e) => setNewEmployee({...newEmployee, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                <input
                  type="password"
                  value={newEmployee.password}
                  onChange={(e) => setNewEmployee({...newEmployee, password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 font-medium transition"
                >
                  Add Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Professional Header with Logo */}
      <ProfessionalHeader user={user} logout={logout} />

      {/* Enhanced Navigation */}
      <nav className="bg-white border-b-2 border-blue-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`py-4 px-4 border-b-3 font-semibold text-base transition-all duration-200 ${
                currentView === 'dashboard' 
                  ? 'border-blue-600 text-blue-700 bg-blue-50' 
                  : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setCurrentView('employees')}
              className={`py-4 px-4 border-b-3 font-semibold text-base transition-all duration-200 ${
                currentView === 'employees' 
                  ? 'border-blue-600 text-blue-700 bg-blue-50' 
                  : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              👥 Employees
            </button>
            <button
              onClick={() => setCurrentView('attendance')}
              className={`py-4 px-4 border-b-3 font-semibold text-base transition-all duration-200 ${
                currentView === 'attendance' 
                  ? 'border-blue-600 text-blue-700 bg-blue-50' 
                  : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              📍 Attendance
            </button>
            <button
              onClick={() => setCurrentView('documents')}
              className={`py-4 px-4 border-b-3 font-semibold text-base transition-all duration-200 ${
                currentView === 'documents' 
                  ? 'border-blue-600 text-blue-700 bg-blue-50' 
                  : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              📁 Documents
            </button>
            <button
              onClick={() => setCurrentView('announcements')}
              className={`py-4 px-4 border-b-3 font-semibold text-base transition-all duration-200 ${
                currentView === 'announcements' 
                  ? 'border-blue-600 text-blue-700 bg-blue-50' 
                  : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              📢 Announcements
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {currentView === 'dashboard' && (
          <div className="space-y-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard
                title="Total Employees"
                value={stats.total_employees}
                color="border-blue-500"
                icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" /></svg>}
              />
              <StatCard
                title="Present Today"
                value={stats.present_today}
                color="border-green-500"
                icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
              />
              <StatCard
                title="Currently Online"
                value={stats.logged_in_now}
                color="border-yellow-500"
                icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>}
              />
              <StatCard
                title="Absent Today"
                value={stats.absent_today}
                color="border-red-500"
                icon={<svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
              />
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-2">
                <button
                  onClick={() => setShowAddEmployee(true)}
                  className="flex items-center justify-center space-x-1 bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Add Employee</span>
                </button>
                
                <button
                  onClick={() => handleAttendance('login', user?.employee_id)}
                  disabled={isLoggedInToday(user?.employee_id) || !location}
                  className="flex items-center justify-center space-x-1 bg-green-600 text-white p-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  <span>Clock In</span>
                </button>
                
                <button
                  onClick={() => handleAttendance('logout', user?.employee_id)}
                  disabled={!isLoggedInToday(user?.employee_id) || !location}
                  className="flex items-center justify-center space-x-1 bg-orange-600 text-white p-2 rounded-lg hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Clock Out</span>
                </button>
                
                <button
                  onClick={() => generateDocument(user?.employee_id, 'offer')}
                  className="flex items-center justify-center space-x-1 bg-purple-600 text-white p-2 rounded-lg hover:bg-purple-700 transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Offer Letter</span>
                </button>
                
                <button
                  onClick={() => generateDocument(user?.employee_id, 'appointment')}
                  className="flex items-center justify-center space-x-1 bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700 transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Appointment Letter</span>
                </button>
                
                <button
                  onClick={() => user && openSalaryCalculator(user)}
                  className="flex items-center justify-center space-x-1 bg-yellow-600 text-white p-2 rounded-lg hover:bg-yellow-700 transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span>Salary Calculator</span>
                </button>
                
                <button
                  onClick={() => generateDocument(user?.employee_id, 'agreement')}
                  className="flex items-center justify-center space-x-1 bg-red-600 text-white p-2 rounded-lg hover:bg-red-700 transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Agreement</span>
                </button>
              </div>
              
              {locationError && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 text-yellow-600 px-4 py-3 rounded-lg">
                  {locationError}
                </div>
              )}
            </div>
          </div>
        )}

        {currentView === 'employees' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Employee Management</h2>
              <button
                onClick={() => setShowAddEmployee(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Employee</span>
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Designation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Documents</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {employees.map((employee) => (
                      <tr key={employee.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{employee.full_name}</div>
                            <div className="text-sm text-gray-500">ID: {employee.employee_id}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{employee.department}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{employee.designation}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{employee.contact_number}</div>
                          <div className="text-sm text-gray-500">{employee.email_address}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            employee.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {employee.status}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm">
                          <div className="flex flex-wrap gap-1">
                            <button
                              onClick={() => generateDocument(employee.employee_id, 'offer')}
                              className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700 transition"
                              title="Generate Offer Letter"
                            >
                              Offer
                            </button>
                            <button
                              onClick={() => generateDocument(employee.employee_id, 'appointment')}
                              className="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700 transition"
                              title="Generate Appointment Letter"
                            >
                              Appointment
                            </button>
                            <button
                              onClick={() => openSalaryCalculator(employee)}
                              className="bg-yellow-600 text-white px-2 py-1 rounded text-xs hover:bg-yellow-700 transition"
                              title="Calculate Salary"
                            >
                              Salary
                            </button>
                            <button
                              onClick={() => generateDocument(employee.employee_id, 'agreement')}
                              className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700 transition"
                              title="Generate Employee Agreement"
                            >
                              Agreement
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
        )}

        {currentView === 'attendance' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Today's Attendance</h2>

            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Login Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Logout Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Hours</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {employees.map((employee) => {
                      const record = getTodayRecord(employee.employee_id);
                      const isLoggedIn = isLoggedInToday(employee.employee_id);
                      
                      return (
                        <tr key={employee.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{employee.full_name}</div>
                            <div className="text-sm text-gray-500">ID: {employee.employee_id}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {record ? new Date(record.login_time).toLocaleTimeString() : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {record?.logout_time ? new Date(record.logout_time).toLocaleTimeString() : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {record?.total_hours ? `${record.total_hours} hrs` : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              record ? 
                                (record.status === 'Logged In' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800') :
                                'bg-gray-100 text-gray-800'
                            }`}>
                              {record ? record.status : 'Absent'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleAttendance('login', employee.employee_id)}
                                disabled={isLoggedIn || !location}
                                className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Login
                              </button>
                              <button
                                onClick={() => handleAttendance('logout', employee.employee_id)}
                                disabled={!isLoggedIn || !location}
                                className="bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Logout
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

// Main App Component
function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <p className="text-gray-600">Loading HRMS...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {user ? <Dashboard /> : <LoginPage />}
    </div>
  );
}

function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}

export default AppWithAuth;
