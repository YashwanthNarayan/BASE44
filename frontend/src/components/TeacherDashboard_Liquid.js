import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidStatsCard, LiquidProgress, LiquidNavItem } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const TeacherDashboard = ({ teacher, onNavigate, onLogout }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [classes, setClasses] = useState([]);
  const [activeQuickAction, setActiveQuickAction] = useState(null);

  useEffect(() => {
    loadTeacherDashboard();
  }, []);

  const loadTeacherDashboard = async () => {
    try {
      // Load both analytics and classes data
      const [analyticsResponse, classesResponse] = await Promise.all([
        teacherAPI.getAnalyticsOverview(),
        teacherAPI.getClasses()
      ]);
      
      setDashboardData(analyticsResponse);
      setClasses(classesResponse);
    } catch (error) {
      console.error('Error loading teacher dashboard:', error);
      setDashboardData({
        overview_metrics: {
          total_classes: 0,
          total_students: 0,
          total_tests: 0,
          average_score: 0
        },
        class_summary: [],
        subject_distribution: []
      });
      setClasses([]);
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

  const quickActions = [
    {
      id: 'analytics',
      title: 'Detailed Analytics',
      description: 'View comprehensive test results and insights',
      icon: '📊',
      gradient: 'from-purple-500/20 to-indigo-500/20',
      route: 'teacher-analytics'
    },
    {
      id: 'create-class',
      title: 'Create Class',
      description: 'Set up a new class for your students',
      icon: '➕',
      gradient: 'from-green-500/20 to-emerald-500/20',
      route: 'create-class'
    },
    {
      id: 'manage-classes',
      title: 'Manage Classes',
      description: 'View and manage existing classes',
      icon: '🏫',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      route: 'manage-classes'
    },
    {
      id: 'assignments',
      title: 'Assignments',
      description: 'Create and manage assignments',
      icon: '📝',
      gradient: 'from-orange-500/20 to-red-500/20',
      route: 'assignments'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Initializing Neural Dashboard...</p>
        </LiquidCard>
      </div>
    );
  }

  const metrics = dashboardData?.overview_metrics || {};

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      {/* Quantum Grid Background */}
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Neural Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
          <div className="space-y-2">
            <h1 className="text-4xl lg:text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              {getGreeting()}, {teacher?.name || 'Professor'}! 👩‍🏫
            </h1>
            <p className="text-secondary text-lg">
              Neural Command Center • Academic Excellence Interface
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-4 lg:mt-0">
            <div className="holographic-status">
              <span className="status-indicator"></span>
              <span className="text-sm text-neon-cyan">System Online</span>
            </div>
            <LiquidButton 
              variant="secondary" 
              onClick={onLogout}
              className="hover-holographic"
            >
              Neural Logout
            </LiquidButton>
          </div>
        </div>

        {/* Neural Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <LiquidStatsCard
            title="Active Classes"
            value={metrics.total_classes || 0}
            icon="🏫"
            gradient="from-blue-500/20 to-cyan-500/20"
            trend="+12% this term"
          />
          <LiquidStatsCard
            title="Total Students"
            value={metrics.total_students || 0}
            icon="👥"
            gradient="from-green-500/20 to-emerald-500/20"
            trend="+8% growth"
          />
          <LiquidStatsCard
            title="Tests Completed"
            value={metrics.total_tests || 0}
            icon="📊"
            gradient="from-purple-500/20 to-indigo-500/20"
            trend="+25% engagement"
          />
          <LiquidStatsCard
            title="Average Score"
            value={`${(metrics.average_score || 0).toFixed(1)}%`}
            icon="🎯"
            gradient="from-orange-500/20 to-red-500/20"
            trend="+5% improvement"
          />
        </div>

        {/* Quick Actions Neural Interface */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                <span className="text-sm font-bold">⚡</span>
              </div>
              <h2 className="text-xl font-bold text-primary">Neural Quick Actions</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-neon-cyan/50 to-transparent" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {quickActions.map((action) => (
                <div
                  key={action.id}
                  className={`
                    relative group cursor-pointer p-4 rounded-xl
                    bg-gradient-to-br ${action.gradient}
                    border border-primary/20 backdrop-blur-sm
                    hover:border-neon-cyan/50 hover:scale-105
                    transform transition-all duration-300
                    ${activeQuickAction === action.id ? 'scale-105 border-neon-cyan' : ''}
                  `}
                  onClick={() => {
                    setActiveQuickAction(action.id);
                    setTimeout(() => {
                      onNavigate(action.route);
                      setActiveQuickAction(null);
                    }, 200);
                  }}
                >
                  {/* Neural Glow Effect */}
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-neon-cyan/10 to-neon-magenta/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  <div className="relative z-10">
                    <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
                      {action.icon}
                    </div>
                    <h3 className="font-semibold text-primary mb-2 group-hover:text-neon-cyan transition-colors">
                      {action.title}
                    </h3>
                    <p className="text-sm text-secondary group-hover:text-primary transition-colors">
                      {action.description}
                    </p>
                  </div>
                  
                  {/* Data Stream Animation */}
                  <div className="absolute bottom-0 left-0 right-0 h-px">
                    <div className="h-full bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </LiquidCard>

        {/* Active Classes with Join Codes */}
        {classes && classes.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Active Classes */}
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                      <span className="text-sm font-bold">🏫</span>
                    </div>
                    <h2 className="text-xl font-bold text-primary">My Classes</h2>
                  </div>
                  <LiquidButton 
                    variant="secondary" 
                    onClick={() => onNavigate('manage-classes')}
                    className="text-sm"
                  >
                    View All
                  </LiquidButton>
                </div>
                
                <div className="space-y-4">
                  {classes.slice(0, 3).map((classItem, index) => (
                    <div
                      key={classItem.class_id || index}
                      className="p-4 rounded-lg bg-glass border border-primary/20 hover:border-neon-cyan/50 transition-colors cursor-pointer"
                      onClick={() => onNavigate('manage-classes')}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="font-medium text-primary">
                            {classItem.class_name}
                          </h3>
                          <p className="text-sm text-secondary capitalize">
                            {classItem.subject} • {classItem.student_count || 0} students
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-neon-cyan">
                            {classItem.average_score ? `${classItem.average_score.toFixed(1)}%` : 'N/A'}
                          </div>
                          <p className="text-xs text-secondary">Avg Score</p>
                        </div>
                      </div>
                      
                      {/* Join Code Display */}
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-secondary">
                          Class Code:
                        </div>
                        <div className="px-3 py-1 bg-gradient-to-r from-neon-cyan/20 to-neon-magenta/20 border border-neon-cyan/30 rounded-lg">
                          <span className="font-mono text-sm text-neon-cyan font-bold">
                            {classItem.join_code || 'N/A'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {classes.length === 0 && (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">🏫</div>
                      <p className="text-secondary">No classes created yet</p>
                      <LiquidButton 
                        onClick={() => onNavigate('create-class')}
                        className="mt-4"
                      >
                        Create Your First Class
                      </LiquidButton>
                    </div>
                  )}
                </div>
              </div>
            </LiquidCard>

            {/* Subject Distribution */}
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                    <span className="text-sm font-bold">📊</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Subject Distribution</h2>
                </div>
                
                {dashboardData?.subject_distribution && dashboardData.subject_distribution.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.subject_distribution.slice(0, 4).map((subject, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-primary capitalize">{subject.subject}</h3>
                          <p className="text-sm text-secondary">{subject.test_count} tests</p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-neon-cyan">
                            {subject.average_score.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📊</div>
                    <p className="text-secondary">No test data available yet</p>
                  </div>
                )}
              </div>
            </LiquidCard>
          </div>
        )}
                
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-glass border border-primary/20">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-success flex items-center justify-center text-sm">
                        📊
                      </div>
                      <div>
                        <p className="text-primary font-medium">New test submissions</p>
                        <p className="text-sm text-secondary">3 students completed Physics Test #2</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 rounded-lg bg-glass border border-primary/20">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-warning flex items-center justify-center text-sm">
                        👥
                      </div>
                      <div>
                        <p className="text-primary font-medium">New student joined</p>
                        <p className="text-sm text-secondary">Maria Garcia joined Chemistry 101</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 rounded-lg bg-glass border border-primary/20">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-primary flex items-center justify-center text-sm">
                        🎯
                      </div>
                      <div>
                        <p className="text-primary font-medium">Performance milestone</p>
                        <p className="text-sm text-secondary">Class average increased by 12%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </LiquidCard>
          </div>
        )}

        {/* Neural Footer */}
        <div className="text-center mt-12">
          <p className="text-secondary">
            Neural Education System v3.0 • Powered by Quantum Learning AI
          </p>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;