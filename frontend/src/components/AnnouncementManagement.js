import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AnnouncementManagement = ({ currentUser }) => {
  const [announcements, setAnnouncements] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null);
  const [shareChannels, setShareChannels] = useState([]);
  const [targetEmployees, setTargetEmployees] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [shareLoading, setShareLoading] = useState(false);
  const [shareResults, setShareResults] = useState(null);
  const [newAnnouncement, setNewAnnouncement] = useState({
    title: '',
    content: '',
    announcement_type: 'General',
    priority: 'Medium',
    valid_until: '',
    target_departments: []
  });

  const announcementTypes = [
    'General', 'Policy', 'Event', 'Holiday', 'Important', 'HR Update', 'Safety', 'Technical'
  ];

  const priorityLevels = [
    { value: 'Low', color: 'bg-gray-100 text-gray-800', icon: '📝' },
    { value: 'Medium', color: 'bg-blue-100 text-blue-800', icon: '📢' },
    { value: 'High', color: 'bg-yellow-100 text-yellow-800', icon: '⚠️' },
    { value: 'Urgent', color: 'bg-red-100 text-red-800', icon: '🚨' }
  ];

  const departments = [
    'Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Support'
  ];

  useEffect(() => {
    fetchAnnouncements();
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchAnnouncements = async () => {
    try {
      const response = await axios.get(`${API}/announcements`);
      setAnnouncements(response.data);
    } catch (error) {
      console.error('Error fetching announcements:', error);
    }
  };

  const handleCreateAnnouncement = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const announcementData = {
        ...newAnnouncement,
        valid_until: newAnnouncement.valid_until ? new Date(newAnnouncement.valid_until).toISOString() : null
      };

      await axios.post(`${API}/announcements`, announcementData);
      
      alert('Announcement created successfully!');
      setShowCreateForm(false);
      setNewAnnouncement({
        title: '',
        content: '',
        announcement_type: 'General',
        priority: 'Medium',
        valid_until: '',
        target_departments: []
      });
      fetchAnnouncements();
    } catch (error) {
      alert(error.response?.data?.detail || 'Error creating announcement');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAnnouncement = async (announcementId) => {
    if (!window.confirm('Are you sure you want to delete this announcement?')) return;

    try {
      await axios.delete(`${API}/announcements/${announcementId}`);
      alert('Announcement deleted successfully!');
      fetchAnnouncements();
    } catch (error) {
      alert('Error deleting announcement');
    }
  };

  const handleDepartmentToggle = (department) => {
    const updatedDepartments = newAnnouncement.target_departments.includes(department)
      ? newAnnouncement.target_departments.filter(d => d !== department)
      : [...newAnnouncement.target_departments, department];
    
    setNewAnnouncement({
      ...newAnnouncement,
      target_departments: updatedDepartments
    });
  };

  const getAnnouncementIcon = (type) => {
    const icons = {
      'General': '📢',
      'Policy': '📋',
      'Event': '🎉',
      'Holiday': '🏖️',
      'Important': '❗',
      'HR Update': '👥',
      'Safety': '🛡️',
      'Technical': '⚙️'
    };
    return icons[type] || '📢';
  };

  const getPriorityConfig = (priority) => {
    return priorityLevels.find(p => p.value === priority) || priorityLevels[1];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleShareAnnouncement = (announcement) => {
    setSelectedAnnouncement(announcement);
    setShareChannels([]);
    setTargetEmployees([]);
    setShareResults(null);
    setShowShareModal(true);
  };

  const handleChannelToggle = (channel) => {
    setShareChannels(prev => 
      prev.includes(channel) 
        ? prev.filter(c => c !== channel)
        : [...prev, channel]
    );
  };

  const handleEmployeeToggle = (employeeId) => {
    setTargetEmployees(prev => 
      prev.includes(employeeId) 
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    );
  };

  const handleShareSubmit = async () => {
    if (!selectedAnnouncement || shareChannels.length === 0) {
      alert('Please select at least one sharing channel');
      return;
    }

    setShareLoading(true);
    setShareResults(null);

    try {
      const response = await axios.post(`${API}/announcements/${selectedAnnouncement.id}/share`, {
        announcement_id: selectedAnnouncement.id,
        channels: shareChannels,
        target_employees: targetEmployees.length > 0 ? targetEmployees : null
      });

      setShareResults(response.data);
      alert('Announcement shared successfully!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error sharing announcement');
    } finally {
      setShareLoading(false);
    }
  };

  const getShareResultsSummary = () => {
    if (!shareResults) return null;

    const totalSuccess = Object.values(shareResults.sharing_results).reduce(
      (acc, result) => acc + (result.total_sent || 0), 0
    );
    const totalFailed = Object.values(shareResults.sharing_results).reduce(
      (acc, result) => acc + (result.total_failed || 0), 0
    );

    return { totalSuccess, totalFailed };
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-4 flex items-center">
          📢 Company Announcements
        </h1>
        <p className="text-indigo-100 text-lg">
          Share important updates and communicate with your team
        </p>
      </div>

      {/* Create Announcement Button */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-gray-900">All Announcements</h2>
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
            {announcements.length} active
          </span>
        </div>
        
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 flex items-center space-x-2 shadow-lg"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span>New Announcement</span>
        </button>
      </div>

      {/* Create Announcement Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Create New Announcement</h3>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleCreateAnnouncement} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Title *</label>
                <input
                  type="text"
                  value={newAnnouncement.title}
                  onChange={(e) => setNewAnnouncement({...newAnnouncement, title: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="Enter announcement title..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Content *</label>
                <textarea
                  value={newAnnouncement.content}
                  onChange={(e) => setNewAnnouncement({...newAnnouncement, content: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  rows={6}
                  placeholder="Write your announcement content here..."
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Type</label>
                  <select
                    value={newAnnouncement.announcement_type}
                    onChange={(e) => setNewAnnouncement({...newAnnouncement, announcement_type: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  >
                    {announcementTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Priority</label>
                  <select
                    value={newAnnouncement.priority}
                    onChange={(e) => setNewAnnouncement({...newAnnouncement, priority: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  >
                    {priorityLevels.map(priority => (
                      <option key={priority.value} value={priority.value}>
                        {priority.icon} {priority.value}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Valid Until (Optional)</label>
                <input
                  type="datetime-local"
                  value={newAnnouncement.valid_until}
                  onChange={(e) => setNewAnnouncement({...newAnnouncement, valid_until: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">Target Departments (Leave empty for all)</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {departments.map(dept => (
                    <label key={dept} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newAnnouncement.target_departments.includes(dept)}
                        onChange={() => handleDepartmentToggle(dept)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{dept}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-3 rounded-xl hover:bg-green-700 transition disabled:opacity-50 font-semibold"
                >
                  {loading ? 'Creating...' : 'Create Announcement'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-600 text-white py-3 rounded-xl hover:bg-gray-700 transition font-semibold"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Announcements List */}
      <div className="space-y-6">
        {announcements.length > 0 ? (
          announcements.map((announcement) => {
            const priorityConfig = getPriorityConfig(announcement.priority);
            return (
              <div key={announcement.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                {/* Announcement Header */}
                <div className={`${announcement.priority === 'Urgent' ? 'bg-red-600' : announcement.priority === 'High' ? 'bg-yellow-500' : 'bg-blue-600'} text-white px-6 py-4`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getAnnouncementIcon(announcement.announcement_type)}</span>
                      <div>
                        <h3 className="text-xl font-bold">{announcement.title}</h3>
                        <p className="text-sm opacity-90">
                          {announcement.announcement_type} • Published by {announcement.published_by}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${priorityConfig.color}`}>
                        {priorityConfig.icon} {announcement.priority}
                      </span>
                      <button
                        onClick={() => handleShareAnnouncement(announcement)}
                        className="text-white hover:text-green-200 transition"
                        title="Share via Email/WhatsApp"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDeleteAnnouncement(announcement.id)}
                        className="text-white hover:text-red-200 transition"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Announcement Content */}
                <div className="px-6 py-6">
                  <div className="prose max-w-none mb-4">
                    <p className="text-gray-700 text-lg leading-relaxed whitespace-pre-wrap">
                      {announcement.content}
                    </p>
                  </div>

                  {/* Announcement Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {formatDate(announcement.published_at)}
                      </span>
                      
                      {announcement.valid_until && (
                        <span className="flex items-center text-red-600">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Valid until {formatDate(announcement.valid_until)}
                        </span>
                      )}
                    </div>

                    {announcement.target_departments && announcement.target_departments.length > 0 ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">Target:</span>
                        <div className="flex flex-wrap gap-1">
                          {announcement.target_departments.map(dept => (
                            <span key={dept} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                              {dept}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-600 bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                        All Departments
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">📢</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No Announcements Yet</h3>
            <p className="text-gray-600 mb-6">Create your first company announcement to get started</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition"
            >
              Create First Announcement
            </button>
          </div>
        )}
      </div>

      {/* Share Announcement Modal */}
      {showShareModal && selectedAnnouncement && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  📤 Share Announcement
                </h2>
                <button
                  onClick={() => setShowShareModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <h3 className="font-semibold text-blue-900">{selectedAnnouncement.title}</h3>
                <p className="text-blue-700 text-sm mt-1">{selectedAnnouncement.content.substring(0, 100)}...</p>
                <div className="flex items-center space-x-3 mt-2">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                    {selectedAnnouncement.announcement_type}
                  </span>
                  <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
                    {selectedAnnouncement.priority}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Sharing Channels */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  📡 Select Sharing Channels
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { id: 'email', label: 'Email', icon: '📧', color: 'blue' },
                    { id: 'whatsapp', label: 'WhatsApp', icon: '💬', color: 'green' },
                    { id: 'sms', label: 'SMS', icon: '📱', color: 'purple' }
                  ].map(channel => (
                    <label key={channel.id} className="cursor-pointer">
                      <input
                        type="checkbox"
                        checked={shareChannels.includes(channel.id)}
                        onChange={() => handleChannelToggle(channel.id)}
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
                            <div className="text-sm text-gray-600">
                              {channel.id === 'email' && 'Professional email delivery'}
                              {channel.id === 'whatsapp' && 'Instant WhatsApp notifications'}
                              {channel.id === 'sms' && 'SMS text messages'}
                            </div>
                          </div>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Target Employees */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  👥 Select Target Employees <span className="text-sm font-normal text-gray-600 ml-2">(Leave empty to send to all active employees)</span>
                </h3>
                <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-xl p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {employees.filter(emp => emp.status === 'Active').map(employee => (
                      <label key={employee.employee_id} className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded-lg">
                        <input
                          type="checkbox"
                          checked={targetEmployees.includes(employee.employee_id)}
                          onChange={() => handleEmployeeToggle(employee.employee_id)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 truncate">{employee.full_name}</div>
                          <div className="text-sm text-gray-600 truncate">
                            {employee.employee_id} • {employee.department}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  Selected: {targetEmployees.length > 0 ? `${targetEmployees.length} employees` : 'All active employees'}
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
                          {result.status === 'completed' ? (
                            <span className="text-green-600">✅ Completed</span>
                          ) : (
                            <span className="text-red-600">❌ Failed</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600">
                          {result.total_sent || 0} sent, {result.total_failed || 0} failed
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 text-sm text-gray-600">
                    📊 Total employees reached: {shareResults.target_employees}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 flex space-x-4">
              <button
                onClick={handleShareSubmit}
                disabled={shareLoading || shareChannels.length === 0}
                className="flex-1 bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50 font-semibold flex items-center justify-center space-x-2"
              >
                {shareLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Sharing...
                  </>
                ) : (
                  <>
                    <span>📤</span>
                    <span>Share Announcement</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setShowShareModal(false)}
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

export default AnnouncementManagement;