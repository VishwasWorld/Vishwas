import React from 'react';

const ProfessionalHeader = ({ user, logout }) => {
  const logoUrl = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg";

  return (
    <header className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 shadow-lg border-b-4 border-blue-600">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* LEFT SIDE: Logo and Company Information */}
          <div className="flex items-center space-x-6">
            {/* Large Company Logo */}
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-white rounded-full p-2 shadow-2xl border-4 border-blue-300">
                <img 
                  src={logoUrl} 
                  alt="Vishwas World Tech Logo"
                  className="w-full h-full object-contain rounded-full"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="w-full h-full bg-blue-600 rounded-full hidden items-center justify-center">
                  <span className="text-white font-bold text-xl">VWT</span>
                </div>
              </div>
              
              {/* Company Information */}
              <div className="text-white">
                <h1 className="text-3xl font-bold tracking-wide">VISHWAS WORLD TECH</h1>
                <p className="text-blue-200 text-base font-semibold">PRIVATE LIMITED</p>
                <p className="text-blue-300 text-sm">100 DC Complex, Chandra Layout, Bangalore - 560040</p>
                <p className="text-blue-400 text-xs">📞 +91-80-12345678 | 📧 hr@vishwasworldtech.com</p>
              </div>
            </div>
          </div>
          
          {/* RIGHT SIDE: HR User Information & Actions */}
          <div className="flex items-center space-x-6">
            {/* HR Login Info */}
            <div className="bg-blue-800 bg-opacity-50 rounded-xl p-4 border border-blue-500">
              <div className="text-right text-white">
                <p className="text-blue-200 text-sm font-medium">👨‍💼 HR Portal Login</p>
                <p className="font-bold text-xl text-white">{user?.full_name}</p>
                <p className="text-blue-300 text-sm">{user?.designation} - {user?.department}</p>
                <p className="text-blue-400 text-xs">Employee ID: {user?.employee_id}</p>
              </div>
            </div>
            
            {/* Logout Button */}
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-4 rounded-xl font-bold transition-all duration-200 shadow-lg hover:shadow-2xl flex items-center space-x-3 border-2 border-red-500 hover:scale-105 transform"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="text-base">HR Logout</span>
            </button>
          </div>
        </div>
        
        {/* Working Hours Banner */}
        <div className="mt-4 bg-blue-800 bg-opacity-50 rounded-lg p-3 border border-blue-600">
          <div className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-4">
              <svg className="w-5 h-5 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">Working Hours: 9:45 AM - 6:45 PM (Mon-Fri)</span>
            </div>
            <div className="flex items-center space-x-4 text-sm">
              <span className="bg-green-600 px-3 py-1 rounded-full">GPS Tracking Active</span>
              <span className="bg-yellow-600 px-3 py-1 rounded-full">Late Login Penalties Apply</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default ProfessionalHeader;