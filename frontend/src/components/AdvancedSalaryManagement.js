import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdvancedSalaryManagement = ({ currentUser }) => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('name'); // 'name' or 'code'
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [calculationMonth, setCalculationMonth] = useState(new Date().getMonth() + 1);
  const [calculationYear, setCalculationYear] = useState(new Date().getFullYear());
  const [salaryCalculation, setSalaryCalculation] = useState(null);
  const [communicationChannels, setCommunicationChannels] = useState([]);
  const [selectedChannels, setSelectedChannels] = useState(['email', 'whatsapp']);
  const [loading, setLoading] = useState(false);
  const [sharingResults, setSharingResults] = useState(null);
  const [showEmployeeList, setShowEmployeeList] = useState(true);

  useEffect(() => {
    fetchEmployeesForSalary();
    fetchCommunicationChannels();
  }, []);

  useEffect(() => {
    filterEmployees();
  }, [employees, searchQuery, searchType, departmentFilter]);

  const fetchEmployeesForSalary = async () => {
    try {
      const response = await axios.get(`${API}/salary/employee-selection`);
      setEmployees(response.data.employees);
      setFilteredEmployees(response.data.employees);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchCommunicationChannels = async () => {
    try {
      const response = await axios.get(`${API}/salary/communication-channels`);
      setCommunicationChannels(response.data.channels);
      setSelectedChannels(response.data.default_selection);
    } catch (error) {
      console.error('Error fetching communication channels:', error);
    }
  };

  const filterEmployees = () => {
    let filtered = employees;

    // Filter by department
    if (departmentFilter) {
      filtered = filtered.filter(emp => emp.department === departmentFilter);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(emp => {
        if (searchType === 'name') {
          return emp.full_name.toLowerCase().includes(searchQuery.toLowerCase());
        } else if (searchType === 'code') {
          return emp.employee_id.toLowerCase().includes(searchQuery.toLowerCase());
        }
        return true;
      });
    }

    setFilteredEmployees(filtered);
  };

  const selectEmployee = (employee) => {
    setSelectedEmployee(employee);
    setShowEmployeeList(false);
    setSalaryCalculation(null);
    setSharingResults(null);
  };

  const calculateSalary = async () => {
    if (!selectedEmployee) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee.employee_id}/calculate-salary`, {
        employee_id: selectedEmployee.employee_id,
        year: calculationYear,
        month: calculationMonth
      });
      
      setSalaryCalculation(response.data.calculation);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error calculating salary');
    } finally {
      setLoading(false);
    }
  };

  const generateAndShareSalarySlip = async () => {
    if (!selectedEmployee || !salaryCalculation) {
      alert('Please calculate salary first');
      return;
    }

    if (selectedChannels.length === 0) {
      alert('Please select at least one communication channel');
      return;
    }

    setLoading(true);
    setSharingResults(null);

    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee.employee_id}/generate-and-share-salary-slip`, {
        employee_id: selectedEmployee.employee_id,
        year: calculationYear,
        month: calculationMonth,
        channels: selectedChannels
      });
      
      setSharingResults(response.data);
      alert(`✅ Standard salary slip generated and shared! Successful: ${response.data.successful_deliveries.join(', ')}`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error generating and sharing salary slip');
    } finally {
      setLoading(false);
    }
  };

  const downloadSalarySlip = async () => {
    if (!selectedEmployee) return;

    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee.employee_id}/generate-salary-slip`, {
        employee_id: selectedEmployee.employee_id,
        year: calculationYear,
        month: calculationMonth
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
      
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = response.data.filename;
      link.click();
      
      alert('✅ Standard salary slip downloaded successfully!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error generating salary slip');
    }
  };

  const handleChannelToggle = (channelId) => {
    if (selectedChannels.includes(channelId)) {
      setSelectedChannels(selectedChannels.filter(c => c !== channelId));
    } else {
      setSelectedChannels([...selectedChannels, channelId]);
    }
  };

  const resetSelection = () => {
    setSelectedEmployee(null);
    setShowEmployeeList(true);
    setSalaryCalculation(null);
    setSharingResults(null);
    setSearchQuery('');
  };

  const getDepartments = () => {
    const departments = [...new Set(employees.map(emp => emp.department))];
    return departments.sort();
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-bold mb-4 flex items-center">
              💰 Advanced Salary Management System
            </h1>
            <p className="text-emerald-100 text-xl font-medium">
              Generate standard format salary slips with digital signatures and multi-channel distribution
            </p>
          </div>
          <div className="text-right">
            <div className="bg-white bg-opacity-20 rounded-2xl p-4 backdrop-blur-sm">
              <p className="text-emerald-100 text-sm">Total Employees</p>
              <p className="text-4xl font-bold">{employees.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Employee Selection Interface */}
      {showEmployeeList && (
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">
          
          {/* Search Header */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 border-b border-gray-200">
            <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
              🔍 HR Employee Selection Portal
            </h2>

            {/* Search Controls */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              
              {/* Search Type Selection */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-3">Search By</label>
                <div className="flex bg-gray-100 rounded-xl p-1">
                  <button
                    onClick={() => setSearchType('name')}
                    className={`flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-200 ${
                      searchType === 'name' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'text-gray-600 hover:text-blue-600'
                    }`}
                  >
                    👤 Employee Name
                  </button>
                  <button
                    onClick={() => setSearchType('code')}
                    className={`flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-200 ${
                      searchType === 'code' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'text-gray-600 hover:text-blue-600'
                    }`}
                  >
                    🔢 Employee Code
                  </button>
                </div>
              </div>

              {/* Search Input */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-3">
                  {searchType === 'name' ? 'Search by Name' : 'Search by Employee Code'}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder={searchType === 'name' ? 'Enter employee name...' : 'Enter employee code...'}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors pl-10"
                  />
                  <svg className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>

              {/* Department Filter */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-3">Filter by Department</label>
                <select
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                >
                  <option value="">All Departments</option>
                  {getDepartments().map((dept) => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              {/* Results Count */}
              <div className="flex items-end">
                <div className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl p-3 text-center shadow-lg">
                  <p className="text-sm font-semibold opacity-90">Search Results</p>
                  <p className="text-2xl font-bold">{filteredEmployees.length}</p>
                  <p className="text-xs opacity-75">employees found</p>
                </div>
              </div>
            </div>
          </div>

          {/* Employee Grid */}
          <div className="p-8">
            {filteredEmployees.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredEmployees.map((employee) => (
                  <div
                    key={employee.employee_id}
                    onClick={() => selectEmployee(employee)}
                    className="bg-gradient-to-br from-white to-blue-50 border-2 border-gray-200 rounded-2xl p-6 cursor-pointer hover:border-blue-400 hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  >
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                        {employee.full_name.charAt(0)}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{employee.full_name}</h3>
                        <p className="text-blue-600 font-bold text-sm">ID: {employee.employee_id}</p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Department:</span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-bold">
                          {employee.department}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Designation:</span>
                        <span className="text-sm font-semibold text-gray-900">{employee.designation}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Basic Salary:</span>
                        <span className="text-sm font-bold text-green-700">₹{employee.basic_salary.toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-2 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition font-semibold">
                        Select for Salary Processing
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="text-6xl mb-6">🔍</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">No Employees Found</h3>
                <p className="text-gray-600 max-w-md mx-auto">
                  {searchQuery ? 
                    `No employees found matching "${searchQuery}" in ${searchType === 'name' ? 'names' : 'employee codes'}` :
                    'No employees available for salary processing'
                  }
                </p>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setDepartmentFilter('');
                  }}
                  className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition"
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Selected Employee Salary Processing */}
      {selectedEmployee && !showEmployeeList && (
        <div className="space-y-8">
          
          {/* Selected Employee Header */}
          <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center text-blue-600 font-bold text-2xl shadow-lg">
                    {selectedEmployee.full_name.charAt(0)}
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold mb-2">{selectedEmployee.full_name}</h2>
                    <div className="flex items-center space-x-4 text-blue-100">
                      <span className="flex items-center space-x-1">
                        <span>🆔</span>
                        <span className="font-semibold">{selectedEmployee.employee_id}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <span>🏢</span>
                        <span>{selectedEmployee.department}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <span>💼</span>
                        <span>{selectedEmployee.designation}</span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-blue-200 text-sm mt-1">
                      <span>📧 {selectedEmployee.email_address}</span>
                      <span>📞 {selectedEmployee.contact_number}</span>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={resetSelection}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-6 py-3 rounded-xl transition backdrop-blur-sm border border-white border-opacity-30"
                >
                  ← Back to Selection
                </button>
              </div>
            </div>

            {/* Salary Processing Controls */}
            <div className="p-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* Calculation Parameters */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 flex items-center">
                    ⚙️ Salary Calculation Parameters
                  </h3>

                  <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-3">Month</label>
                        <select
                          value={calculationMonth}
                          onChange={(e) => setCalculationMonth(parseInt(e.target.value))}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none transition-colors"
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
                        <label className="block text-sm font-bold text-gray-700 mb-3">Year</label>
                        <select
                          value={calculationYear}
                          onChange={(e) => setCalculationYear(parseInt(e.target.value))}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none transition-colors"
                        >
                          {[2024, 2025, 2026].map(year => (
                            <option key={year} value={year}>{year}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <button
                      onClick={calculateSalary}
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-bold text-lg shadow-lg"
                    >
                      {loading ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Processing Salary Calculation...
                        </span>
                      ) : (
                        '🧮 Calculate Standard Format Salary'
                      )}
                    </button>
                  </div>
                </div>

                {/* Communication Channels */}
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 flex items-center">
                    📡 Multi-Channel Distribution
                  </h3>

                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200">
                    <h4 className="text-lg font-bold text-gray-900 mb-4">Select Distribution Channels</h4>
                    
                    <div className="space-y-4">
                      {communicationChannels.map((channel) => (
                        <div key={channel.id} className="flex items-center justify-between p-4 bg-white border-2 border-gray-200 rounded-xl hover:border-green-400 transition-colors">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{channel.icon}</span>
                            <div>
                              <h5 className="font-bold text-gray-900">{channel.name}</h5>
                              <p className="text-gray-600 text-sm">{channel.description}</p>
                            </div>
                            {channel.recommended && (
                              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-bold">
                                Recommended
                              </span>
                            )}
                          </div>
                          <label className="flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedChannels.includes(channel.id)}
                              onChange={() => handleChannelToggle(channel.id)}
                              className="w-6 h-6 text-green-600 rounded-lg focus:ring-green-500 border-2 border-gray-300"
                            />
                          </label>
                        </div>
                      ))}
                    </div>

                    {/* Selected Channels Display */}
                    {selectedChannels.length > 0 && (
                      <div className="mt-4 bg-white rounded-xl p-4 border border-green-200">
                        <p className="text-green-900 font-bold text-sm mb-2">
                          Selected Channels ({selectedChannels.length}):
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {selectedChannels.map(channelId => {
                            const channel = communicationChannels.find(c => c.id === channelId);
                            return channel ? (
                              <span key={channelId} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                                {channel.icon} {channel.name}
                              </span>
                            ) : null;
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Salary Calculation Results */}
        {selectedEmployee && salaryCalculation && (
          <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 p-8">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-bold text-gray-900 flex items-center">
                📊 Standard Format Salary Calculation
              </h2>
              <div className="flex items-center space-x-2">
                <span className="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-bold">
                  ✅ Digitally Signed
                </span>
                <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-bold">
                  🏛️ Govt Compliant
                </span>
              </div>
            </div>

            {/* Salary Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-2">💰 Gross Salary</h3>
                <p className="text-3xl font-bold">₹{salaryCalculation.earnings.gross_salary.toLocaleString()}</p>
                <p className="text-green-100 text-sm">Before deductions</p>
              </div>
              <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-2">📉 Deductions</h3>
                <p className="text-3xl font-bold">₹{salaryCalculation.deductions.total_deductions.toLocaleString()}</p>
                <p className="text-red-100 text-sm">PF + ESI + PT + Tax</p>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-2">💸 Net Salary</h3>
                <p className="text-3xl font-bold">₹{salaryCalculation.net_salary.toLocaleString()}</p>
                <p className="text-blue-100 text-sm">Final payout</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-500 to-orange-600 text-white rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-2">📅 Attendance</h3>
                <p className="text-3xl font-bold">{salaryCalculation.employee_details.attendance_percentage}%</p>
                <p className="text-yellow-100 text-sm">{salaryCalculation.employee_details.present_days}/{salaryCalculation.employee_details.total_working_days} days</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={downloadSalarySlip}
                className="bg-gradient-to-r from-gray-600 to-gray-700 text-white py-4 px-6 rounded-xl hover:from-gray-700 hover:to-gray-800 transition font-bold shadow-lg flex items-center justify-center space-x-3"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Download PDF</span>
              </button>

              <button
                onClick={generateAndShareSalarySlip}
                disabled={loading || selectedChannels.length === 0}
                className="bg-gradient-to-r from-green-600 to-emerald-700 text-white py-4 px-6 rounded-xl hover:from-green-700 hover:to-emerald-800 transition disabled:opacity-50 disabled:cursor-not-allowed font-bold shadow-lg flex items-center justify-center space-x-3"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                </svg>
                <span>{loading ? 'Sharing...' : '📨 Generate & Share'}</span>
              </button>

              <button
                onClick={() => setSalaryCalculation(null)}
                className="bg-gradient-to-r from-yellow-600 to-orange-600 text-white py-4 px-6 rounded-xl hover:from-yellow-700 hover:to-orange-700 transition font-bold shadow-lg flex items-center justify-center space-x-3"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Recalculate</span>
              </button>
            </div>
          </div>

          {/* Sharing Results */}
          {sharingResults && (
            <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                📊 Distribution Results
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {sharingResults.sharing_results.successful_channels.map((channel) => (
                  <div key={channel} className="bg-green-50 border-2 border-green-200 rounded-xl p-6 shadow-md">
                    <div className="flex items-center space-x-3 mb-3">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-bold text-green-900 text-lg capitalize">{channel}</span>
                    </div>
                    <p className="text-green-700 font-medium">
                      ✅ {sharingResults.sharing_results.results[channel]?.message}
                    </p>
                  </div>
                ))}
                
                {sharingResults.sharing_results.failed_channels.map((channel) => (
                  <div key={channel} className="bg-red-50 border-2 border-red-200 rounded-xl p-6 shadow-md">
                    <div className="flex items-center space-x-3 mb-3">
                      <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <span className="font-bold text-red-900 text-lg capitalize">{channel}</span>
                    </div>
                    <p className="text-red-700 font-medium">
                      ❌ {sharingResults.sharing_results.results[channel]?.message}
                    </p>
                  </div>
                ))}
              </div>

              {/* Digital Signature Info */}
              {sharingResults.digital_signature && (
                <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 shadow-md">
                  <h3 className="font-bold text-blue-900 text-lg mb-3 flex items-center">
                    🔐 Digital Signature Applied
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-blue-800 text-sm">
                    <div>
                      <p><span className="font-bold">Signed by:</span> {sharingResults.digital_signature.signed_by}</p>
                      <p><span className="font-bold">Authority:</span> {sharingResults.digital_signature.authority}</p>
                    </div>
                    <div>
                      <p><span className="font-bold">Verification Code:</span> {sharingResults.digital_signature.verification_code}</p>
                      <p><span className="font-bold">Contact:</span> {sharingResults.digital_signature.contact_verification}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* No Employee Selected Message */}
      {!selectedEmployee && !showEmployeeList && (
        <div className="bg-white rounded-3xl shadow-2xl p-16 text-center border border-gray-200">
          <div className="text-6xl mb-6">💰</div>
          <h3 className="text-3xl font-bold text-gray-900 mb-4">Advanced Salary Processing</h3>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">
            Use the advanced employee selection system to find and process employee salaries 
            with government-compliant calculations and multi-channel distribution.
          </p>
          <button
            onClick={() => setShowEmployeeList(true)}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition font-bold text-lg shadow-xl"
          >
            🔍 Open Employee Selection Portal
          </button>
        </div>
      )}
    </div>
  );
};

export default AdvancedSalaryManagement;