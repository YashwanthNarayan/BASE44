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
      id: 'study-planner',
      title: 'Study Planner',
      description: 'AI-powered Pomodoro study sessions',
      icon: '🗓️',
      route: 'study-planner',
      gradient: 'from-blue-500/10 to-cyan-500/10'
    },
    {
      id: 'scheduled-tests',
      title: 'Review Schedule',
      description: 'Smart spaced repetition reviews',
      icon: '📅',
      route: 'scheduled-tests',
      gradient: 'from-emerald-500/10 to-teal-500/10'
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
      {/* Subtle background pattern */}
      <div className="quantum-grid fixed inset-0 opacity-5" />
      
      <div className="relative z-10 p-8 max-w-7xl mx-auto">
        
        {/* Professional Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-16">
          <div className="space-y-4">
            <h1 className="text-5xl lg:text-6xl font-bold text-primary tracking-tight">
              {getGreeting()}, {student?.name || 'Student'}
            </h1>
            <p className="text-xl text-secondary font-medium">
              Ready to continue your learning journey?
            </p>
          </div>
          
          <div className="flex items-center space-x-6 mt-8 lg:mt-0">
            <div className="flex items-center space-x-3 px-4 py-3 bg-glass/80 rounded-2xl border border-primary/10">
              <div className="w-3 h-3 bg-accent-green rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-secondary">Online</span>
            </div>
            <LiquidButton 
              variant="secondary" 
              size="md"
              onClick={onLogout}
            >
              Sign Out
            </LiquidButton>
          </div>
        </div>

        {/* Professional Stats Dashboard */}
        {dashboardData?.progress_summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
            <LiquidStatsCard
              title="Tests Completed"
              value={dashboardData.progress_summary.total_tests || 0}
              icon="📊"
              gradient="from-accent-blue/10 to-accent-purple/10"
              trend="This month"
            />
            <LiquidStatsCard
              title="Average Score"
              value={`${(dashboardData.progress_summary.average_score || 0).toFixed(1)}%`}
              icon="🎯"
              gradient="from-accent-green/10 to-accent-cyan/10"
              trend="Last 10 tests"
            />
            <LiquidStatsCard
              title="Study Streak"
              value="5 days"
              icon="🔥"
              gradient="from-accent-orange/10 to-accent-pink/10"
              trend="Keep it up!"
            />
          </div>
        )}

        {/* Core Features - Clean Professional Grid */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-3xl font-bold text-primary">Learning Tools</h2>
            <div className="w-24 h-1 bg-gradient-primary rounded-full"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {coreFeatures.map((feature) => (
              <LiquidCard
                key={feature.id}
                className="group cursor-pointer hover:shadow-xl transition-all duration-300 hover:scale-[1.02] border-primary/10 hover:border-accent/20"
                onClick={() => onNavigate(feature.route)}
              >
                <div className="p-8">
                  {/* Professional Icon */}
                  <div className="mb-6">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-2xl group-hover:scale-110 transition-transform duration-300`}>
                      {feature.icon}
                    </div>
                  </div>
                  
                  {/* Professional Typography */}
                  <h3 className="text-xl font-bold text-primary mb-3 group-hover:text-accent-blue transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-secondary leading-relaxed mb-4">
                    {feature.description}
                  </p>
                  
                  {/* Subtle call-to-action */}
                  <div className="flex items-center text-accent-blue opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">
                    Get started
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </LiquidCard>
            ))}
          </div>
        </div>

        {/* Secondary Features - Organized Grid */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-3xl font-bold text-primary">Additional Tools</h2>
            <div className="w-24 h-1 bg-gradient-secondary rounded-full"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {secondaryFeatures.map((feature) => (
              <LiquidCard
                key={feature.id}
                className="group cursor-pointer hover:shadow-lg transition-all duration-300 hover:scale-[1.02] border-primary/10 hover:border-accent/20"
                onClick={() => onNavigate(feature.route)}
              >
                <div className="p-6">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2 group-hover:text-accent-blue transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-secondary leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </LiquidCard>
            ))}
          </div>
        </div>

        {/* Recent Activity - Professional Section */}
        {dashboardData?.recent_tests && dashboardData.recent_tests.length > 0 && (
          <div className="mb-16">
            <div className="flex items-center justify-between mb-10">
              <h2 className="text-3xl font-bold text-primary">Recent Activity</h2>
              <LiquidButton 
                variant="ghost" 
                size="sm"
                onClick={() => onNavigate('progress')}
              >
                View All Activity
              </LiquidButton>
            </div>
            
            <LiquidCard className="border-primary/10">
              <div className="p-8">
                <div className="space-y-6">
                  {dashboardData.recent_tests.slice(0, 3).map((test, index) => (
                    <div key={index} className="flex items-center justify-between p-6 bg-glass/30 rounded-2xl border border-primary/5 hover:border-accent/20 transition-colors">
                      <div className="flex items-center space-x-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-subtle flex items-center justify-center text-xl">
                          📊
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-primary">
                            {test.subject} Assessment
                          </h3>
                          <p className="text-sm text-secondary">
                            Completed on {new Date(test.completed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-accent-blue mb-1">
                          {test.score}%
                        </div>
                        <div className="text-sm text-secondary">
                          {test.total_questions} questions
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </LiquidCard>
          </div>
        )}

        {/* Professional Footer */}
        <div className="text-center pt-12 border-t border-primary/5">
          <p className="text-secondary font-medium">
            Learning Platform • Enhanced Experience
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;