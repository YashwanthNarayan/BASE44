import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidStatsCard, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const StudentDashboard = ({ student, onNavigate, onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await studentAPI.getDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setDashboardData({
        recent_tests: [],
        progress_summary: { total_tests: 0, average_score: 0 },
        achievements: [],
        upcoming_events: []
      });
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // Organized main features into clean categories
  const coreFeatures = [
    {
      id: 'practice',
      title: 'Practice Tests',
      description: 'Take adaptive assessments to test your knowledge',
      icon: '📝',
      route: 'practice',
      gradient: 'from-blue-500/10 to-cyan-500/10',
      priority: 'high'
    },
    {
      id: 'tutor', 
      title: 'AI Tutor',
      description: 'Get personalized help from AI tutors',
      icon: '🤖',
      route: 'tutor',
      gradient: 'from-purple-500/10 to-indigo-500/10',
      priority: 'high'
    },
    {
      id: 'progress',
      title: 'Progress',
      description: 'Monitor your learning analytics',
      icon: '📊',
      route: 'progress',
      gradient: 'from-green-500/10 to-emerald-500/10',
      priority: 'high'
    },
    {
      id: 'classes',
      title: 'My Classes',
      description: 'View and manage your enrolled classes',
      icon: '🏫',
      route: 'classes',
      gradient: 'from-orange-500/10 to-red-500/10',
      priority: 'high'
    }
  ];

  const secondaryFeatures = [
    {
      id: 'notes',
      title: 'Notes Library',
      description: 'AI-generated study materials',
      icon: '📚',
      route: 'notes',
      gradient: 'from-indigo-500/10 to-purple-500/10'
    },
    {
      id: 'calendar',
      title: 'Schedule',
      description: 'Manage your study calendar',
      icon: '📅',
      route: 'calendar',
      gradient: 'from-pink-500/10 to-rose-500/10'
    },
    {
      id: 'mindfulness',
      title: 'Mindfulness',
      description: 'Relaxation and focus exercises',
      icon: '🧘‍♀️',
      route: 'mindfulness',
      gradient: 'from-teal-500/10 to-cyan-500/10'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'View your updates and alerts',
      icon: '🔔',
      route: 'notifications',
      gradient: 'from-yellow-500/10 to-orange-500/10'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-12 text-center">
          <div className="quantum-loader mx-auto mb-6"></div>
          <p className="text-secondary">Loading your dashboard...</p>
        </LiquidCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      {/* Subtle quantum grid - much less opacity */}
      <div className="quantum-grid fixed inset-0 opacity-10" />
      
      <div className="relative z-10 p-8 max-w-7xl mx-auto">
        
        {/* Clean Header Section with Better Spacing */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-12">
          <div className="space-y-3">
            <h1 className="text-4xl lg:text-5xl font-bold text-primary mb-2">
              {getGreeting()}, {student?.name || 'Student'}! 👋
            </h1>
            <p className="text-xl text-secondary">
              Ready to continue your learning journey?
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-6 lg:mt-0">
            <div className="flex items-center space-x-2 px-4 py-2 bg-glass/50 rounded-lg border border-primary/20">
              <div className="w-2 h-2 bg-neon-green rounded-full"></div>
              <span className="text-sm text-secondary">Online</span>
            </div>
            <LiquidButton 
              variant="secondary" 
              onClick={onLogout}
              className="text-sm"
            >
              Logout
            </LiquidButton>
          </div>
        </div>

        {/* Quick Stats - Cleaner Layout */}
        {dashboardData?.progress_summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <LiquidStatsCard
              title="Tests Completed"
              value={dashboardData.progress_summary.total_tests || 0}
              icon="📝"
              gradient="from-blue-500/10 to-cyan-500/10"
              className="text-center"
            />
            <LiquidStatsCard
              title="Average Score"
              value={`${(dashboardData.progress_summary.average_score || 0).toFixed(1)}%`}
              icon="🎯"
              gradient="from-green-500/10 to-emerald-500/10"
              className="text-center"
            />
            <LiquidStatsCard
              title="Study Streak"
              value="5 days"
              icon="🔥"
              gradient="from-orange-500/10 to-red-500/10"
              className="text-center"
            />
          </div>
        )}

        {/* Core Features - Much Cleaner Grid */}
        <div className="mb-16">
          <h2 className="text-2xl font-semibold text-primary mb-8">Main Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {coreFeatures.map((feature) => (
              <LiquidCard
                key={feature.id}
                className="group cursor-pointer hover:scale-[1.02] transform transition-all duration-300 p-6"
                onClick={() => onNavigate(feature.route)}
              >
                <div className={`bg-gradient-to-br ${feature.gradient} rounded-xl p-6 h-full`}>
                  {/* Clean Icon */}
                  <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  
                  {/* Clean Typography */}
                  <h3 className="text-lg font-semibold text-primary mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-secondary leading-relaxed">
                    {feature.description}
                  </p>
                  
                  {/* Subtle hover effect */}
                  <div className="mt-4 text-neon-cyan opacity-0 group-hover:opacity-100 transition-opacity text-sm">
                    Click to access →
                  </div>
                </div>
              </LiquidCard>
            ))}
          </div>
        </div>

        {/* Secondary Features - Better Organized */}
        <div className="mb-16">
          <h2 className="text-2xl font-semibold text-primary mb-8">Additional Tools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {secondaryFeatures.map((feature) => (
              <LiquidCard
                key={feature.id}
                className="group cursor-pointer hover:scale-[1.02] transform transition-all duration-300 p-4"
                onClick={() => onNavigate(feature.route)}
              >
                <div className={`bg-gradient-to-br ${feature.gradient} rounded-lg p-4 h-full text-center`}>
                  <div className="text-3xl mb-3">
                    {feature.icon}
                  </div>
                  <h3 className="text-base font-medium text-primary mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-secondary">
                    {feature.description}
                  </p>
                </div>
              </LiquidCard>
            ))}
          </div>
        </div>

        {/* Recent Activity - Cleaner Section */}
        {dashboardData?.recent_tests && dashboardData.recent_tests.length > 0 && (
          <div className="mb-12">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-semibold text-primary">Recent Activity</h2>
              <LiquidButton 
                variant="secondary" 
                onClick={() => onNavigate('progress')}
                className="text-sm"
              >
                View All
              </LiquidButton>
            </div>
            
            <LiquidCard className="p-6">
              <div className="space-y-4">
                {dashboardData.recent_tests.slice(0, 3).map((test, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-glass/30 rounded-lg border border-primary/10">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">📝</div>
                      <div>
                        <h3 className="font-medium text-primary">
                          {test.subject} Test
                        </h3>
                        <p className="text-sm text-secondary">
                          {new Date(test.completed_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-neon-cyan">
                        {test.score}%
                      </div>
                      <div className="text-xs text-secondary">
                        {test.total_questions} questions
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </LiquidCard>
          </div>
        )}

        {/* Clean Footer */}
        <div className="text-center pt-8 border-t border-primary/10">
          <p className="text-secondary text-sm">
            Educational Platform • Version 3.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;