import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import NavigationBar_Modern from './NavigationBar_Modern';
import { 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernBadge,
  ModernProgress,
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernGrid,
  ModernSpinner
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

const StudentDashboard_Modern = ({ user, onNavigate, onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      const data = await studentAPI.getDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ModernSpinner size="lg" />
          <ModernText className="mt-4">Loading your dashboard...</ModernText>
        </div>
      </div>
    );
  }

  const level = Math.floor((dashboardData?.xp_points || 0) / 100) + 1;
  const xpProgress = ((dashboardData?.xp_points || 0) % 100);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Modern Navigation */}
      <NavigationBar_Modern 
        user={user}
        currentPage="student-dashboard"
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <ModernContainer className="py-8">
        {error && (
          <ModernAlert variant="error" className="mb-6">
            {error}
          </ModernAlert>
        )}

        {/* Welcome Section */}
        <div className="mb-8">
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name || 'Student'}! 
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600">
            Ready to continue your learning journey?
          </ModernText>
        </div>

        {/* Main Actions */}
        <ModernGrid cols={3} className="mb-8">
          <ModernCard hover={true} className="cursor-pointer border-2 border-transparent hover:border-indigo-200">
            <ModernCardBody>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <ModernHeading level={3} className="mb-2">
                  NCERT Practice Tests
                </ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 mb-4">
                  Test your knowledge with curriculum-aligned questions
                </ModernText>
                <ModernButton 
                  variant="primary" 
                  className="w-full"
                  onClick={() => onNavigate('practice-tests')}
                >
                  Start Practice
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>

          <ModernCard hover={true} className="cursor-pointer border-2 border-transparent hover:border-green-200">
            <ModernCardBody>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"/>
                    <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"/>
                  </svg>
                </div>
                <ModernHeading level={3} className="mb-2">
                  Learning Analytics
                </ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 mb-4">
                  Track your progress and identify areas for improvement
                </ModernText>
                <ModernButton 
                  variant="primary" 
                  className="w-full"
                  onClick={() => onNavigate('strengths-weaknesses')}
                >
                  View Analytics
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>

          <ModernCard hover={true} className="cursor-pointer border-2 border-transparent hover:border-blue-200">
            <ModernCardBody>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"/>
                  </svg>
                </div>
                <ModernHeading level={3} className="mb-2">
                  AI Tutor
                </ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 mb-4">
                  Get personalized help with your studies
                </ModernText>
                <ModernButton 
                  variant="primary" 
                  className="w-full"
                  onClick={() => onNavigate('tutor')}
                >
                  Ask Tutor
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>
        </ModernGrid>

        {/* Quick Actions Grid */}
        <ModernGrid cols={2} className="mb-8">
          <ModernCard>
            <ModernCardHeader>
              <ModernHeading level={4}>Study Tools</ModernHeading>
            </ModernCardHeader>
            <ModernCardBody>
              <div className="space-y-3">
                <ModernButton 
                  variant="ghost" 
                  className="w-full justify-start"
                  onClick={() => onNavigate('scheduled-tests')}
                >
                  <span className="text-gray-400 mr-3">●</span> Scheduled Tests
                </ModernButton>
                <ModernButton 
                  variant="ghost" 
                  className="w-full justify-start"
                  onClick={() => onNavigate('study-planner')}
                >
                  <span className="text-gray-400 mr-3">◆</span> Study Planner
                </ModernButton>
                <ModernButton 
                  variant="ghost" 
                  className="w-full justify-start"
                  onClick={() => onNavigate('notes')}
                >
                  <span className="text-gray-400 mr-3">◇</span> Notes
                </ModernButton>
                <ModernButton 
                  variant="ghost" 
                  className="w-full justify-start"
                  onClick={() => onNavigate('progress')}
                >
                  <span className="text-gray-400 mr-3">◎</span> Progress Tracker
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>

          <ModernCard>
            <ModernCardHeader>
              <ModernHeading level={4}>Recent Activity</ModernHeading>
            </ModernCardHeader>
            <ModernCardBody>
              {dashboardData?.recent_scores?.length > 0 ? (
                <div className="space-y-3">
                  {dashboardData.recent_scores.slice(0, 4).map((score, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div>
                        <ModernText variant="body-small" className="font-medium">
                          {score.subject || 'Practice Test'}
                        </ModernText>
                        <ModernText variant="caption" className="text-gray-500">
                          {score.date || 'Recent'}
                        </ModernText>
                      </div>
                      <ModernBadge 
                        variant={score.score >= 80 ? 'success' : score.score >= 60 ? 'warning' : 'error'}
                      >
                        {score.score}%
                      </ModernBadge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <ModernText variant="body-small" className="text-gray-500">
                    No recent activity. Take a practice test to get started!
                  </ModernText>
                </div>
              )}
            </ModernCardBody>
          </ModernCard>
        </ModernGrid>

        {/* Achievement Section */}
        {dashboardData?.achievements?.length > 0 && (
          <ModernCard>
            <ModernCardHeader>
              <ModernHeading level={4}>Recent Achievements</ModernHeading>
            </ModernCardHeader>
            <ModernCardBody>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {dashboardData.achievements.slice(0, 4).map((achievement, index) => (
                  <div key={index} className="text-center p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
                    <div className="text-2xl mb-2">{achievement.icon || '🏆'}</div>
                    <ModernText variant="body-small" className="font-medium">
                      {achievement.title}
                    </ModernText>
                  </div>
                ))}
              </div>
            </ModernCardBody>
          </ModernCard>
        )}
      </ModernContainer>
    </div>
  );
};

export default StudentDashboard_Modern;