import React from 'react';

const NotificationsComponent = ({ student, onNavigate }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">🔔 Notifications</h1>
          <p className="text-gray-600">Stay updated with your learning progress and reminders</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-6xl mb-4">🔔</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Notifications Component</h2>
          <p className="text-gray-600">This component is being restructured for better maintainability.</p>
        </div>
      </div>
    </div>
  );
};

export default NotificationsComponent;