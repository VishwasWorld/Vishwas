import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentManagement = ({ currentUser, employees }) => {
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [documents, setDocuments] = useState([]);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadData, setUploadData] = useState({
    document_type: 'Resume',
    description: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const documentTypes = [
    'Resume', 'ID Proof', 'Address Proof', 'Educational Certificate', 
    'Experience Letter', 'Salary Certificate', 'Medical Certificate', 'Other'
  ];

  useEffect(() => {
    if (selectedEmployee) {
      fetchEmployeeDocuments();
    }
  }, [selectedEmployee]);

  const fetchEmployeeDocuments = async () => {
    try {
      const response = await axios.get(`${API}/employees/${selectedEmployee}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile || !selectedEmployee) {
      alert('Please select an employee and file');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', uploadData.document_type);
      formData.append('description', uploadData.description);

      await axios.post(
        `${API}/employees/${selectedEmployee}/upload-document?document_type=${uploadData.document_type}&description=${uploadData.description}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      alert('Document uploaded successfully!');
      setShowUploadForm(false);
      setSelectedFile(null);
      setUploadData({ document_type: 'Resume', description: '' });
      fetchEmployeeDocuments();
    } catch (error) {
      alert(error.response?.data?.detail || 'Error uploading document');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (employeeId, documentId, documentName) => {
    try {
      const response = await axios.get(`${API}/employees/${employeeId}/documents/${documentId}/download`);
      
      // Convert base64 to blob and download
      const byteCharacters = atob(response.data.file_data);
      const byteNumbers = new Array(byteCharacters.length);
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray]);
      
      // Create download link
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = documentName;
      link.click();
      
    } catch (error) {
      alert('Error downloading document');
    }
  };

  const getDocumentIcon = (type) => {
    const icons = {
      'Resume': '📄',
      'ID Proof': '🆔',
      'Address Proof': '🏠',
      'Educational Certificate': '🎓',
      'Experience Letter': '💼',
      'Salary Certificate': '💰',
      'Medical Certificate': '🏥',
      'Other': '📋'
    };
    return icons[type] || '📄';
  };

  const getDocumentColor = (type) => {
    const colors = {
      'Resume': 'bg-blue-100 text-blue-800 border-blue-200',
      'ID Proof': 'bg-green-100 text-green-800 border-green-200',
      'Address Proof': 'bg-purple-100 text-purple-800 border-purple-200',
      'Educational Certificate': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Experience Letter': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'Salary Certificate': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      'Medical Certificate': 'bg-red-100 text-red-800 border-red-200',
      'Other': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-4 flex items-center">
          📁 Document Management System
        </h1>
        <p className="text-blue-100 text-lg">
          Upload, manage, and access employee documents securely
        </p>
      </div>

      {/* Employee Selection and Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Employee Selection */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            👤 Select Employee
          </h2>
          
          <div className="space-y-4">
            <select
              value={selectedEmployee}
              onChange={(e) => setSelectedEmployee(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            >
              <option value="">Choose an employee...</option>
              {employees.map((employee) => (
                <option key={employee.id} value={employee.employee_id}>
                  {employee.full_name} ({employee.employee_id}) - {employee.department}
                </option>
              ))}
            </select>
            
            {selectedEmployee && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <h3 className="font-semibold text-blue-900">Selected Employee</h3>
                <p className="text-blue-800 text-sm">
                  {employees.find(emp => emp.employee_id === selectedEmployee)?.full_name} 
                  ({selectedEmployee})
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Upload */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            📤 Quick Upload
          </h2>
          
          {!showUploadForm ? (
            <button
              onClick={() => setShowUploadForm(true)}
              disabled={!selectedEmployee}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span className="text-lg font-semibold">Upload Document</span>
            </button>
          ) : (
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Document Type</label>
                <select
                  value={uploadData.document_type}
                  onChange={(e) => setUploadData({...uploadData, document_type: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {documentTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">File</label>
                <input
                  type="file"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Supported: PDF, DOC, DOCX, JPG, PNG, TXT (Max 10MB)
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Description (Optional)</label>
                <textarea
                  value={uploadData.description}
                  onChange={(e) => setUploadData({...uploadData, description: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Add a description for this document..."
                />
              </div>
              
              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                >
                  {loading ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Documents Display */}
      {selectedEmployee && (
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center justify-between">
            <span className="flex items-center">
              📚 Employee Documents 
              <span className="ml-3 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                {documents.length} files
              </span>
            </span>
            <button
              onClick={fetchEmployeeDocuments}
              className="text-blue-600 hover:text-blue-800 transition"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </h2>
          
          {documents.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {documents.map((doc) => (
                <div key={doc.id} className="bg-gray-50 border-2 border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getDocumentIcon(doc.document_type)}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-sm truncate max-w-32">
                          {doc.document_name}
                        </h3>
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${getDocumentColor(doc.document_type)}`}>
                          {doc.document_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-xs text-gray-600 mb-4">
                    <p><span className="font-medium">Size:</span> {formatFileSize(doc.file_size)}</p>
                    <p><span className="font-medium">Uploaded:</span> {new Date(doc.uploaded_at).toLocaleDateString()}</p>
                    <p><span className="font-medium">By:</span> {doc.uploaded_by}</p>
                    {doc.description && (
                      <p><span className="font-medium">Note:</span> {doc.description}</p>
                    )}
                  </div>
                  
                  <button
                    onClick={() => handleDownload(selectedEmployee, doc.id, doc.document_name)}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Download</span>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📂</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Documents Found</h3>
              <p className="text-gray-600">Upload the first document for this employee</p>
            </div>
          )}
        </div>
      )}

      {!selectedEmployee && (
        <div className="bg-white rounded-2xl shadow-lg p-12 border border-gray-100 text-center">
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Select an Employee</h3>
          <p className="text-gray-600">Choose an employee from the dropdown to view and manage their documents</p>
        </div>
      )}
    </div>
  );
};

export default DocumentManagement;