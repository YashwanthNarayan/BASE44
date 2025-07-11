import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidStatsCard, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const StudentDashboard = ({ student, onNavigate, onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const quickActions = [
    {
      id: 'tutor',
      title: 'AI Tutor',
      description: 'Get personalized help in any subject',
      icon: '🎓',
      gradient: 'from-purple-500/20 to-indigo-500/20',
      route: 'tutor'
    },
    {
      id: 'practice',
      title: 'Practice Tests',
      description: 'Take adaptive quizzes to test your knowledge',
      icon: '📝',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      route: 'practice'
    },
    {
      id: 'mindfulness',
      title: 'Mindfulness',
      description: 'Breathing exercises and stress management',
      icon: '🧘‍♀️',
      gradient: 'from-green-500/20 to-emerald-500/20',
      route: 'mindfulness'
    },
    {
      id: 'calendar',
      title: 'My Schedule',
      description: 'View your study schedule and events',
      icon: '📅',
      gradient: 'from-pink-500/20 to-rose-500/20',
      route: 'calendar'
    },
    {
      id: 'progress',
      title: 'Progress Tracker',
      description: 'Monitor your learning journey',
      icon: '📊',
      gradient: 'from-yellow-500/20 to-orange-500/20',
      route: 'progress'
    },
    {
      id: 'notes',
      title: 'My Notes',
      description: 'Access your study notes library',
      icon: '📚',
      gradient: 'from-indigo-500/20 to-purple-500/20',
      route: 'notes'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Check updates and announcements',
      icon: '🔔',
      gradient: 'from-red-500/20 to-pink-500/20',
      route: 'notifications'
    },
    {
      id: 'classes',
      title: 'My Classes',
      description: 'View joined classes and join new ones',
      icon: '🏫',
      gradient: 'from-teal-500/20 to-green-500/20',
      route: 'classes'
    }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="animated-bg" />
      
      {/* Floating Orbs */}
      <div className="absolute top-20 right-20 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 left-20 w-72 h-72 bg-gradient-to-r from-green-400/20 to-blue-400/20 rounded-full blur-3xl animate-pulse delay-1000" />

      {/* Dynamic Navigation */}
      <nav className="dynamic-nav">
        <div className="flex items-center gap-4">
          <LiquidNavItem active={true} onClick={() => onNavigate('student-dashboard')}>
            Dashboard
          </LiquidNavItem>
          <div className="w-px h-6 bg-white/20" />
          <LiquidNavItem onClick={onLogout}>
            Logout
          </LiquidNavItem>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          
          {/* Header Section */}
          <div className="mb-12">
            <LiquidCard className="p-8 bg-gradient-to-br from-white/10 to-white/5">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-bold text-white mb-2">
                    {getGreeting()}, {student?.name || 'Student'}! 
                    <span className="inline-block ml-3 text-3xl animate-bounce">🌟</span>
                  </h1>
                  <p className="text-white/70 text-lg">Ready to continue your learning journey?</p>
                </div>
                
                {/* Level & XP Display */}
                <div className="text-right">
                  <div className="glass-strong rounded-2xl px-6 py-4">
                    <div className="text-3xl font-bold text-gradient mb-1">Level {level}</div>
                    <div className="text-white/60 text-sm mb-3">{data.xp_points || 0} XP</div>
                    <LiquidProgress 
                      value={data.xp_points || 0} 
                      max={(data.xp_points || 0) + xpForNext}
                      className="w-32"
                    />
                    <div className="text-white/60 text-xs mt-2">{xpForNext} XP to next level</div>
                  </div>
                </div>
              </div>
            </LiquidCard>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <LiquidStatsCard
              title="AI Conversations"
              value={data.total_messages || 0}
              icon="💬"
              trend="+12%"
              trendDirection="up"
            />
            <LiquidStatsCard
              title="Practice Tests"
              value={data.total_tests || 0}
              icon="📝"
              trend="+8%"
              trendDirection="up"
            />
            <LiquidStatsCard
              title="Average Score"
              value={`${(data.average_score || 0).toFixed(1)}%`}
              icon="📊"
              trend="+5%"
              trendDirection="up"
            />
            <LiquidStatsCard
              title="Study Streak"
              value={`${data.study_streak || 0} days`}
              icon="🔥"
              trend="2 days"
              trendDirection="up"
            />
          </div>

          {/* Quick Actions Grid */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="text-3xl">🚀</span>
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {quickActions.map((action) => (
                <div
                  key={action.id}
                  className={`
                    group relative cursor-pointer transition-all duration-500 hover:scale-105
                    ${activeQuickAction === action.id ? 'scale-105' : ''}
                  `}
                  onClick={() => {
                    setActiveQuickAction(action.id);
                    setTimeout(() => onNavigate(action.route), 300);
                  }}
                  onMouseEnter={() => setActiveQuickAction(action.id)}
                  onMouseLeave={() => setActiveQuickAction(null)}
                >
                  <LiquidCard className={`h-full p-6 bg-gradient-to-br ${action.gradient} border-white/20 hover:border-white/40`}>
                    <div className="text-center">
                      <div className="text-4xl mb-4 transform transition-transform duration-300 group-hover:scale-110">
                        {action.icon}
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2">
                        {action.title}
                      </h3>
                      <p className="text-white/60 text-sm leading-relaxed">
                        {action.description}
                      </p>
                    </div>
                    
                    {/* Floating Indicator */}
                    {activeQuickAction === action.id && (
                      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/10 to-transparent border border-white/30 pointer-events-none" />
                    )}
                  </LiquidCard>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity & Achievements */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Recent Performance */}
            <LiquidCard className="p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                <span className="text-2xl">📈</span>
                Recent Performance
              </h3>
              {data.recent_scores && data.recent_scores.length > 0 ? (
                <div className="space-y-4">
                  {data.recent_scores.slice(0, 5).map((score, index) => (
                    <div key={index} className="flex items-center justify-between p-4 glass-dark rounded-xl">
                      <div>
                        <span className="font-medium text-white capitalize">
                          {score.subject || 'General'}
                        </span>
                        <span className="text-white/60 text-sm ml-2">
                          {score.date ? new Date(score.date).toLocaleDateString() : 'Recent'}
                        </span>
                      </div>
                      <div className={`
                        px-3 py-1 rounded-full text-sm font-semibold
                        ${score.score >= 80 ? 'bg-green-500/20 text-green-300 border border-green-400/30' :
                          score.score >= 60 ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/30' :
                          'bg-red-500/20 text-red-300 border border-red-400/30'}
                      `}>
                        {score.score}%
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📊</div>
                  <p className="text-white/60 mb-4">No recent test scores</p>
                  <LiquidButton 
                    onClick={() => onNavigate('practice')}
                    variant="secondary"
                    size="sm"
                  >
                    Take a Practice Test
                  </LiquidButton>
                </div>
              )}
            </LiquidCard>

            {/* Achievements */}
            <LiquidCard className="p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                <span className="text-2xl">🏆</span>
                Recent Achievements
              </h3>
              {data.achievements && data.achievements.length > 0 ? (
                <div className="space-y-4">
                  {data.achievements.slice(0, 5).map((achievement, index) => (
                    <div key={index} className="flex items-center p-4 glass-dark rounded-xl">
                      <div className="text-2xl mr-3">🏆</div>
                      <div>
                        <span className="font-medium text-white block">
                          {achievement.title}
                        </span>
                        <span className="text-white/60 text-sm">
                          {achievement.description}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">🏆</div>
                  <p className="text-white/60 mb-2">No achievements yet</p>
                  <p className="text-white/40 text-sm">
                    Start practicing to earn your first achievement!
                  </p>
                </div>
              )}
            </LiquidCard>
          </div>

          {/* Floating Action Button */}
          <div className="fixed bottom-8 right-8 z-50">
            <LiquidButton
              onClick={() => onNavigate('tutor')}
              className="rounded-full w-16 h-16 shadow-2xl hover:scale-110 transition-transform"
              variant="primary"
            >
              <span className="text-2xl">🤖</span>
            </LiquidButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;