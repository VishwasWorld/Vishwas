import React, { useState } from 'react';

const ProfessionalFooter = () => {
  const [showMap, setShowMap] = useState(false);
  const logoUrl = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg";

  // Company contact information
  const companyInfo = {
    name: "Vishwas World Tech Private Limited",
    address: "100 DC Complex, Chandra Layout",
    city: "Bangalore - 560040, Karnataka, India",
    phone: "+91-80-12345678",
    email: "hr@vishwasworldtech.com",
    website: "www.vishwasworldtech.com",
    established: "2020"
  };

  // Social media links
  const socialLinks = {
    facebook: "https://facebook.com/vishwasworldtech",
    instagram: "https://instagram.com/vishwasworldtech", 
    gmail: "mailto:hr@vishwasworldtech.com",
    linkedin: "https://linkedin.com/company/vishwasworldtech",
    twitter: "https://twitter.com/vishwasworldtech"
  };

  // Google Maps embed URL for the address
  const mapEmbedUrl = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.6649222394693!2d77.56020331482147!3d12.934732990888908!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15a2e0c0c5c7%3A0x8b2c9b7f8e0a1234!2sChandra%20Layout%2C%20Bengaluru%2C%20Karnataka!5e0!3m2!1sen!2sin!4v1634567890123!5m2!1sen!2sin";

  const openMap = () => {
    const mapUrl = `https://www.google.com/maps/search/?api=1&query=100+DC+Complex+Chandra+Layout+Bangalore+560040`;
    window.open(mapUrl, '_blank');
  };

  return (
    <footer className="bg-gradient-to-r from-gray-900 via-blue-900 to-gray-900 text-white">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Company Information */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white rounded-full p-2 shadow-lg">
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
                  <span className="text-white font-bold text-lg">VWT</span>
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">{companyInfo.name}</h3>
                <p className="text-blue-200 text-sm">Excellence in Technology Solutions</p>
              </div>
            </div>
            
            <div className="bg-blue-800 bg-opacity-50 rounded-xl p-6 border border-blue-600">
              <h4 className="text-lg font-semibold mb-4 flex items-center">
                🏢 Corporate Office
              </h4>
              <div className="space-y-2 text-blue-100">
                <p className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {companyInfo.address}
                </p>
                <p className="ml-6">{companyInfo.city}</p>
                
                <button
                  onClick={openMap}
                  className="flex items-center text-yellow-300 hover:text-yellow-100 transition-colors mt-3 bg-blue-700 px-3 py-2 rounded-lg hover:bg-blue-600"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3" />
                  </svg>
                  View on Google Maps
                </button>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-6">
            <h4 className="text-xl font-bold text-white mb-4 flex items-center">
              📞 Contact Information
            </h4>
            
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <h5 className="font-semibold text-blue-200 mb-2">Phone</h5>
                <a href={`tel:${companyInfo.phone}`} 
                   className="text-white hover:text-blue-300 transition-colors flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  {companyInfo.phone}
                </a>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h5 className="font-semibold text-blue-200 mb-2">Email</h5>
                <a href={socialLinks.gmail} 
                   className="text-white hover:text-blue-300 transition-colors flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  {companyInfo.email}
                </a>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h5 className="font-semibold text-blue-200 mb-2">Website</h5>
                <a href={`https://${companyInfo.website}`} 
                   target="_blank" 
                   rel="noopener noreferrer"
                   className="text-white hover:text-blue-300 transition-colors flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                  {companyInfo.website}
                </a>
              </div>
            </div>
          </div>

          {/* Social Media & Quick Links */}
          <div className="space-y-6">
            <h4 className="text-xl font-bold text-white mb-4 flex items-center">
              🌐 Connect With Us
            </h4>
            
            {/* Social Media Links */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h5 className="font-semibold text-blue-200 mb-4">Follow Us</h5>
              <div className="grid grid-cols-2 gap-3">
                
                {/* Facebook */}
                <a 
                  href={socialLinks.facebook}
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors group"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  <span className="text-sm font-medium">Facebook</span>
                </a>

                {/* Instagram */}
                <a 
                  href={socialLinks.instagram}
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center p-3 bg-pink-600 hover:bg-pink-700 rounded-lg transition-colors group"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.621 5.367 11.988 11.988 11.988s11.987-5.367 11.987-11.988C24.004 5.367 18.637.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.49-3.323-1.297C3.951 14.81 3.29 13.367 3.29 11.717c0-1.651.661-3.094 1.836-4.175.875-.808 2.026-1.297 3.323-1.297s2.448.49 3.323 1.297c1.175 1.081 1.836 2.524 1.836 4.175 0 1.65-.661 3.093-1.836 4.174-.875.807-2.026 1.297-3.323 1.297zm7.83-1.297c-.875.807-2.026 1.297-3.323 1.297s-2.448-.49-3.323-1.297c-1.175-1.081-1.836-2.524-1.836-4.174 0-1.651.661-3.094 1.836-4.175C10.508 6.535 11.659 6.045 12.956 6.045s2.448.49 3.323 1.297c1.175 1.081 1.836 2.524 1.836 4.175 0 1.65-.661 3.093-1.836 4.174z"/>
                    <path d="M12 8.865a3.135 3.135 0 100 6.27 3.135 3.135 0 000-6.27zm0 5.135a2 2 0 110-4 2 2 0 010 4z"/>
                    <circle cx="15.338" cy="8.662" r=".8"/>
                  </svg>
                  <span className="text-sm font-medium">Instagram</span>
                </a>

                {/* Gmail */}
                <a 
                  href={socialLinks.gmail}
                  className="flex items-center p-3 bg-red-600 hover:bg-red-700 rounded-lg transition-colors group"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                  </svg>
                  <span className="text-sm font-medium">Gmail</span>
                </a>

                {/* LinkedIn */}
                <a 
                  href={socialLinks.linkedin}
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center p-3 bg-blue-800 hover:bg-blue-900 rounded-lg transition-colors group"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  <span className="text-sm font-medium">LinkedIn</span>
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h5 className="font-semibold text-blue-200 mb-4">Quick Links</h5>
              <div className="space-y-2">
                <a href="#" className="block text-gray-300 hover:text-white transition-colors">
                  📋 Company Policies
                </a>
                <a href="#" className="block text-gray-300 hover:text-white transition-colors">
                  🎯 Career Opportunities
                </a>
                <a href="#" className="block text-gray-300 hover:text-white transition-colors">
                  📞 Support Center
                </a>
                <a href="#" className="block text-gray-300 hover:text-white transition-colors">
                  🔒 Privacy Policy
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Map Section */}
        <div className="mt-12 bg-gray-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-bold text-white flex items-center">
              📍 Our Location
            </h4>
            <button
              onClick={() => setShowMap(!showMap)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3" />
              </svg>
              <span>{showMap ? 'Hide Map' : 'Show Map'}</span>
            </button>
          </div>

          {showMap && (
            <div className="bg-white rounded-xl p-2">
              <iframe
                src={mapEmbedUrl}
                width="100%"
                height="300"
                style={{ border: 0, borderRadius: '0.5rem' }}
                allowFullScreen=""
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Vishwas World Tech Location"
                className="rounded-lg"
              ></iframe>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="bg-blue-900 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🚗</div>
              <h5 className="font-semibold text-white">By Car</h5>
              <p className="text-blue-200 text-sm">Ample parking available</p>
            </div>
            <div className="bg-blue-900 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🚌</div>
              <h5 className="font-semibold text-white">By Bus</h5>
              <p className="text-blue-200 text-sm">Multiple bus routes nearby</p>
            </div>
            <div className="bg-blue-900 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🚇</div>
              <h5 className="font-semibold text-white">By Metro</h5>
              <p className="text-blue-200 text-sm">Rajajinagar Metro Station</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-700 bg-gray-900">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="text-center md:text-left mb-4 md:mb-0">
              <p className="text-gray-300 text-sm">
                © {new Date().getFullYear()} {companyInfo.name}. All rights reserved.
              </p>
              <p className="text-gray-400 text-xs mt-1">
                Established {companyInfo.established} | Registered in Karnataka, India
              </p>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2 text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm">HRMS System Active</span>
              </div>
              
              <div className="text-gray-400 text-xs">
                Last Updated: {new Date().toLocaleDateString('en-IN')}
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-800">
            <div className="flex flex-wrap items-center justify-center space-x-6 text-xs text-gray-500">
              <a href="#" className="hover:text-gray-300 transition-colors">Terms of Service</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-300 transition-colors">Privacy Policy</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-300 transition-colors">Data Protection</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-300 transition-colors">Cookie Policy</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-300 transition-colors">Support</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default ProfessionalFooter;