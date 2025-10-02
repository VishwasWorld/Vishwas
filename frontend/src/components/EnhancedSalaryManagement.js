import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EnhancedSalaryManagement = ({ currentUser }) => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [calculationMonth, setCalculationMonth] = useState(new Date().getMonth() + 1);
  const [calculationYear, setCalculationYear] = useState(new Date().getFullYear());
  const [salaryCalculation, setSalaryCalculation] = useState(null);
  const [communicationChannels, setCommunicationChannels] = useState([]);
  const [selectedChannels, setSelectedChannels] = useState(['email', 'whatsapp']);
  const [loading, setLoading] = useState(false);
  const [sharingResults, setSharingResults] = useState(null);

  useEffect(() => {
    fetchEmployeesForSalary();
    fetchCommunicationChannels();
  }, []);

  const fetchEmployeesForSalary = async () => {
    try {
      const response = await axios.get(`${API}/salary/employee-selection`);
      setEmployees(response.data.employees);
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

  const calculateSalary = async () => {
    if (!selectedEmployee) {
      alert('Please select an employee');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee}/calculate-salary`, {
        employee_id: selectedEmployee,
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
      const response = await axios.post(`${API}/employees/${selectedEmployee}/generate-and-share-salary-slip`, {
        employee_id: selectedEmployee,
        year: calculationYear,
        month: calculationMonth,
        channels: selectedChannels
      });
      
      setSharingResults(response.data);
      alert(`Salary slip generated and shared! Successful: ${response.data.successful_deliveries.join(', ')}`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error generating and sharing salary slip');
    } finally {
      setLoading(false);
    }
  };

  const downloadSalarySlip = async () => {
    if (!selectedEmployee) {
      alert('Please select an employee');
      return;
    }

    try {
      const response = await axios.post(`${API}/employees/${selectedEmployee}/generate-salary-slip`, {
        employee_id: selectedEmployee,
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
      
      // Create download link
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = response.data.filename;
      link.click();
      
      alert('Standard salary slip downloaded successfully!');
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

  const getSelectedEmployeeData = () => {
    return employees.find(emp => emp.employee_id === selectedEmployee);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-700 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-4 flex items-center">
          💰 Enhanced Salary Management System
        </h1>
        <p className="text-green-100 text-lg">
          Generate standard format salary slips with digital signatures and multi-channel sharing
        </p>
      </div>

      {/* Employee Selection and Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Employee Selection Panel */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            👤 Employee Selection
          </h2>
          
          <div className="space-y-4">
            {/* Employee Dropdown */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Select Employee</label>
              <select
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:outline-none transition-colors"
              >
                <option value="">Choose an employee...</option>
                {employees.map((employee) => (
                  <option key={employee.employee_id} value={employee.employee_id}>
                    {employee.full_name} ({employee.employee_id}) - {employee.department}
                  </option>
                ))}
              </select>
            </div>

            {/* Month and Year Selection */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Month</label>
                <select
                  value={calculationMonth}
                  onChange={(e) => setCalculationMonth(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
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
                <label className="block text-sm font-semibold text-gray-700 mb-2">Year</label>
                <select
                  value={calculationYear}
                  onChange={(e) => setCalculationYear(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  {[2024, 2025, 2026].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Selected Employee Info */}
            {selectedEmployee && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <h3 className="font-semibold text-green-900 mb-2">Selected Employee</h3>
                {(() => {
                  const empData = getSelectedEmployeeData();
                  return empData ? (
                    <div className="text-green-800 text-sm space-y-1">
                      <p><span className="font-medium">Name:</span> {empData.full_name}</p>
                      <p><span className="font-medium">Department:</span> {empData.department}</p>
                      <p><span className="font-medium">Email:</span> {empData.email_address}</p>
                      <p><span className="font-medium">Phone:</span> {empData.contact_number}</p>
                      <p><span className="font-medium">Basic Salary:</span> ₹{empData.basic_salary.toLocaleString()}</p>
                    </div>
                  ) : null;
                })()}
              </div>
            )}

            {/* Calculate Button */}
            <button
              onClick={calculateSalary}
              disabled={!selectedEmployee || loading}
              className="w-full bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              {loading ? 'Calculating...' : 'Calculate Salary'}
            </button>
          </div>
        </div>

        {/* Communication Channels Panel */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            📡 Communication Channels
          </h2>

          {/* Channel Selection */}
          <div className="space-y-4">
            <p className="text-gray-600 text-sm mb-4">
              Select channels to share the salary slip after generation:
            </p>
            
            {communicationChannels.map((channel) => (
              <div key={channel.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{channel.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{channel.name}</h3>
                    <p className="text-gray-600 text-sm">{channel.description}</p>
                  </div>
                  {channel.recommended && (
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                      Recommended
                    </span>
                  )}
                </div>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedChannels.includes(channel.id)}
                    onChange={() => handleChannelToggle(channel.id)}
                    className="w-5 h-5 text-green-600 rounded focus:ring-green-500"
                  />
                </label>
              </div>
            ))}

            {/* Selected Channels Summary */}
            {selectedChannels.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-blue-900 font-medium text-sm">
                  Selected: {selectedChannels.map(c => 
                    communicationChannels.find(ch => ch.id === c)?.name
                  ).join(', ')}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Salary Calculation Results */}
      {salaryCalculation && (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center justify-between">
            💰 Salary Calculation Results
            <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
              Standard Format
            </span>
          </h2>

          {/* Salary Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <h3 className="font-semibold text-green-900">Gross Salary</h3>
              <p className="text-2xl font-bold text-green-700">₹{salaryCalculation.earnings.gross_salary.toLocaleString()}</p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <h3 className="font-semibold text-red-900">Total Deductions</h3>
              <p className="text-2xl font-bold text-red-700">₹{salaryCalculation.deductions.total_deductions.toLocaleString()}</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h3 className="font-semibold text-blue-900">Net Salary</h3>
              <p className="text-2xl font-bold text-blue-700">₹{salaryCalculation.net_salary.toLocaleString()}</p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <h3 className="font-semibold text-yellow-900">Attendance</h3>
              <p className="text-2xl font-bold text-yellow-700">{salaryCalculation.employee_details.attendance_percentage}%</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={downloadSalarySlip}
              className="bg-gray-600 text-white py-3 px-6 rounded-xl hover:bg-gray-700 transition flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Download PDF</span>
            </button>

            <button
              onClick={generateAndShareSalarySlip}
              disabled={loading || selectedChannels.length === 0}
              className="bg-green-600 text-white py-3 px-6 rounded-xl hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              <span>{loading ? 'Sharing...' : 'Generate & Share'}</span>
            </button>

            <button
              onClick={() => setSalaryCalculation(null)}
              className="bg-yellow-600 text-white py-3 px-6 rounded-xl hover:bg-yellow-700 transition flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Recalculate</span>
            </button>
          </div>
        </div>
      )}

      {/* Sharing Results */}
      {sharingResults && (
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            📊 Sharing Results
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sharingResults.sharing_results.successful_channels.map((channel) => (
              <div key={channel} className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="font-semibold text-green-900 capitalize">{channel}</span>
                </div>
                <p className="text-green-700 text-sm mt-1">
                  {sharingResults.sharing_results.results[channel]?.message}
                </p>
              </div>
            ))}
            
            {sharingResults.sharing_results.failed_channels.map((channel) => (
              <div key={channel} className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <span className="font-semibold text-red-900 capitalize">{channel}</span>
                </div>
                <p className="text-red-700 text-sm mt-1">
                  {sharingResults.sharing_results.results[channel]?.message}
                </p>
              </div>
            ))}
          </div>

          {/* Digital Signature Info */}
          {sharingResults.digital_signature && (
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">🔐 Digital Signature Applied</h3>
              <div className="text-blue-800 text-sm space-y-1">
                <p><span className="font-medium">Signed by:</span> {sharingResults.digital_signature.signed_by}</p>
                <p><span className="font-medium">Verification Code:</span> {sharingResults.digital_signature.verification_code}</p>
                <p><span className="font-medium">Contact:</span> {sharingResults.digital_signature.contact_verification}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      {!selectedEmployee && (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
          <div className="text-6xl mb-4">💰</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Enhanced Salary Processing</h3>
          <div className="text-gray-600 space-y-2 max-w-2xl mx-auto">
            <p>• Select an employee from the dropdown to begin salary processing</p>
            <p>• Choose communication channels for automatic sharing</p>
            <p>• Generate standard format salary slips with digital signatures</p>
            <p>• Share via Email (with PDF), WhatsApp, and SMS automatically</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedSalaryManagement;