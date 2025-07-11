import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../services/api';

const TeacherDashboard = ({ teacher, onNavigate, onLogout }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    loadTeacherDashboard();
  }, []);

  const loadTeacherDashboard = async () => {
    try {
      const response = await teacherAPI.getAnalyticsOverview();
      setDashboardData(response);
    } catch (error) {
      console.error('Error loading teacher dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">
              {getGreeting()}, {teacher?.name || 'Teacher'}! 👩‍🏫
            </h1>
            <p className="text-gray-600 mt-2">Welcome to your teacher dashboard</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => onNavigate('teacher-analytics')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Detailed Analytics
            </button>
            <button
              onClick={onLogout}
              className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:border-gray-400 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🏫</div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {dashboardData?.overview_metrics?.total_classes || 0}
                </div>
                <div className="text-sm text-gray-600">Total Classes</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">👥</div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {dashboardData?.overview_metrics?.total_students || 0}
                </div>
                <div className="text-sm text-gray-600">Total Students</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📝</div>
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {dashboardData?.overview_metrics?.total_tests || 0}
                </div>
                <div className="text-sm text-gray-600">Tests Taken</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📊</div>
              <div>
                <div className="text-2xl font-bold text-orange-600">
                  {(dashboardData?.overview_metrics?.average_score || 0).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="text-2xl mb-4">🏫</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Create New Class</h3>
            <p className="text-gray-600 mb-4">Set up a new class for your students</p>
            <button className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
              Create Class
            </button>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="text-2xl mb-4">📊</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">View Analytics</h3>
            <p className="text-gray-600 mb-4">Detailed student performance analytics</p>
            <button
              onClick={() => onNavigate('teacher-analytics')}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              View Analytics
            </button>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="text-2xl mb-4">👥</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Manage Students</h3>
            <p className="text-gray-600 mb-4">View and manage your students</p>
            <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
              Manage Students
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Class Summary */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📚 Class Summary</h2>
            {dashboardData?.class_summary && dashboardData.class_summary.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.class_summary.map((classItem, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">{classItem.class_name}</h3>
                        <p className="text-sm text-gray-600 capitalize">{classItem.subject}</p>
                        <p className="text-sm text-gray-500">{classItem.student_count} students</p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-indigo-600">
                          {(classItem.average_score || 0).toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">Avg Score</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">🏫</div>
                <p className="text-gray-600">No classes created yet</p>
                <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                  Create Your First Class
                </button>
              </div>
            )}
          </div>

          {/* Subject Distribution */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📊 Subject Distribution</h2>
            {dashboardData?.subject_distribution && dashboardData.subject_distribution.length > 0 ? (
              <div className="space-y-3">
                {dashboardData.subject_distribution.map((subject, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium capitalize">{subject.subject}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-gray-900">{subject.class_count} classes</div>
                      <div className="text-xs text-gray-600">{subject.student_count} students</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">📊</div>
                <p className="text-gray-600">No subject data available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;