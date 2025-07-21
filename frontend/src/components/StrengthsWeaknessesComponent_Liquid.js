import React, { useState, useEffect } from 'react';
import { LiquidCard, LiquidButton } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const StrengthsWeaknessesComponent = ({ student, onNavigate }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [subjectBreakdown, setSubjectBreakdown] = useState(null);
  const [learningInsights, setLearningInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load analytics data individually with graceful error handling
      let strengthsWeaknesses = null;
      let trends = null;
      let subjects = null;
      let insights = null;

      // Load strengths & weaknesses data
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/student/analytics/strengths-weaknesses`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (response.ok) {
          strengthsWeaknesses = await response.json();
        } else {
          console.warn('Failed to load strengths & weaknesses data:', response.status);
        }
      } catch (error) {
        console.warn('Error loading strengths & weaknesses data:', error.message);
      }

      // Load trends data
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/student/analytics/performance-trends`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (response.ok) {
          trends = await response.json();
        } else {
          console.warn('Failed to load trends data:', response.status);
        }
      } catch (error) {
        console.warn('Error loading trends data:', error.message);
      }

      // Load subject breakdown data
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/student/analytics/subject-breakdown`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (response.ok) {
          subjects = await response.json();
        } else {
          console.warn('Failed to load subject breakdown data:', response.status);
        }
      } catch (error) {
        console.warn('Error loading subject breakdown data:', error.message);
      }

      // Load learning insights data
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/student/analytics/learning-insights`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (response.ok) {
          insights = await response.json();
        } else {
          console.warn('Failed to load learning insights data:', response.status);
        }
      } catch (error) {
        console.warn('Error loading learning insights data:', error.message);
      }

      // Set data with fallbacks for failed calls
      setAnalyticsData(strengthsWeaknesses || {
        strengths: [],
        weaknesses: [],
        improving_areas: [],
        declining_areas: [],
        overall_performance: { average_score: 0, total_tests: 0, subjects_tested: 0 },
        recommendations: []
      });
      
      setTrendsData(trends || {
        trend_data: [],
        trend_direction: 'stable',
        total_tests_period: 0,
        period_days: 30
      });
      
      setSubjectBreakdown(subjects || {
        subject_breakdown: [],
        total_subjects: 0,
        best_subject: null
      });
      
      setLearningInsights(insights || {
        insights: [{
          type: 'getting_started',
          title: 'Start Your Learning Journey',
          message: 'Take some practice tests to get personalized insights and recommendations!',
          icon: '🚀',
          action: 'Take your first practice test to begin analyzing your learning patterns.'
        }],
        study_tips: [
          'Regular practice leads to better retention',
          'Focus on understanding concepts, not just memorizing',
          'Review mistakes to learn from them'
        ]
      });
      
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400'; 
    return 'text-red-400';
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'bg-green-500/20 text-green-400 border-green-400/30',
      'B': 'bg-blue-500/20 text-blue-400 border-blue-400/30',
      'C': 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30',
      'D': 'bg-orange-500/20 text-orange-400 border-orange-400/30',
      'F': 'bg-red-500/20 text-red-400 border-red-400/30'
    };
    return colors[grade] || colors['C'];
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-400 bg-red-500/10 text-red-400';
      case 'medium': return 'border-yellow-400 bg-yellow-500/10 text-yellow-400';
      case 'low': return 'border-green-400 bg-green-500/10 text-green-400';
      default: return 'border-primary/20 bg-glass text-primary';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-6xl mx-auto">
          <LiquidCard className="text-center p-12">
            <div className="quantum-loader mx-auto mb-4" />
            <p className="text-secondary">Analyzing your learning patterns...</p>
          </LiquidCard>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <LiquidButton
            variant="secondary"
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4"
          >
            ← Back to Dashboard
          </LiquidButton>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            🎯 Strengths & Weaknesses
          </h1>
          <p className="text-secondary">Discover your learning patterns and get personalized insights</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-2xl p-2">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'subjects', label: '📚 Subjects', icon: '📚' },
              { id: 'trends', label: '📈 Trends', icon: '📈' },
              { id: 'insights', label: '💡 Insights', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-primary text-white shadow-lg'
                    : 'text-secondary hover:text-primary hover:bg-glass/50'
                }`}
              >
                {tab.icon} {tab.label.split(' ')[1]}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && analyticsData && (
          <div className="space-y-8">
            {/* Overall Performance */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <LiquidCard className="text-center p-6">
                <div className="text-3xl font-bold text-accent-blue mb-2">
                  {analyticsData.overall_performance.average_score}%
                </div>
                <p className="text-secondary">Overall Average</p>
              </LiquidCard>
              
              <LiquidCard className="text-center p-6">
                <div className="text-3xl font-bold text-accent-green mb-2">
                  {analyticsData.overall_performance.total_tests}
                </div>
                <p className="text-secondary">Tests Taken</p>
              </LiquidCard>
              
              <LiquidCard className="text-center p-6">
                <div className="text-3xl font-bold text-accent-purple mb-2">
                  {analyticsData.overall_performance.subjects_tested}
                </div>
                <p className="text-secondary">Subjects Practiced</p>
              </LiquidCard>
              
              <LiquidCard className="text-center p-6">
                <div className="text-3xl font-bold text-accent-yellow mb-2">
                  {analyticsData.overall_performance.highest_score}%
                </div>
                <p className="text-secondary">Best Score</p>
              </LiquidCard>
            </div>

            {/* Strengths and Weaknesses */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Strengths */}
              <LiquidCard className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                    <span className="text-xl">💪</span>
                  </div>
                  <h2 className="text-2xl font-bold text-green-400">Your Strengths</h2>
                </div>
                
                {analyticsData.strengths.length > 0 ? (
                  <div className="space-y-4">
                    {analyticsData.strengths.map((strength, index) => (
                      <div key={index} className="p-4 bg-green-500/10 border border-green-400/30 rounded-xl">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="font-semibold text-green-400">{strength.subject_display}</h3>
                          <span className="text-green-400 font-bold">{strength.average_score}%</span>
                        </div>
                        <p className="text-sm text-secondary">{strength.attempt_count} tests completed</p>
                        <div className="flex items-center space-x-4 text-xs text-secondary mt-2">
                          <span>Best: {strength.highest_score}%</span>
                          <span>Consistency: {strength.consistency}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🌱</div>
                    <p className="text-secondary">Keep practicing to discover your strengths!</p>
                  </div>
                )}
              </LiquidCard>

              {/* Weaknesses */}
              <LiquidCard className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                    <span className="text-xl">🎯</span>
                  </div>
                  <h2 className="text-2xl font-bold text-red-400">Areas for Improvement</h2>
                </div>
                
                {analyticsData.weaknesses.length > 0 ? (
                  <div className="space-y-4">
                    {analyticsData.weaknesses.map((weakness, index) => (
                      <div key={index} className="p-4 bg-red-500/10 border border-red-400/30 rounded-xl">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="font-semibold text-red-400">{weakness.subject_display}</h3>
                          <span className="text-red-400 font-bold">{weakness.average_score}%</span>
                        </div>
                        <p className="text-sm text-secondary">{weakness.attempt_count} tests completed</p>
                        <div className="flex items-center space-x-4 text-xs text-secondary mt-2">
                          <span>Best: {weakness.highest_score}%</span>
                          <span>Room for growth: {(80 - weakness.average_score).toFixed(0)} points</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🎉</div>
                    <p className="text-secondary">No significant weaknesses identified. Great job!</p>
                  </div>
                )}
              </LiquidCard>
            </div>

            {/* Recommendations */}
            {analyticsData.recommendations.length > 0 && (
              <LiquidCard className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-accent-blue/20 flex items-center justify-center">
                    <span className="text-xl">🎯</span>
                  </div>
                  <h2 className="text-2xl font-bold text-accent-blue">Personalized Recommendations</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analyticsData.recommendations.map((rec, index) => (
                    <div key={index} className={`p-4 border rounded-xl ${getPriorityColor(rec.priority)}`}>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">{rec.type.replace('_', ' ').toUpperCase()}</h3>
                        <span className="text-xs px-2 py-1 rounded-full bg-current/20 font-medium">
                          {rec.priority} priority
                        </span>
                      </div>
                      <p className="text-sm mb-3" dangerouslySetInnerHTML={{ __html: rec.message }} />
                      <div className="space-y-1">
                        {rec.suggested_actions.slice(0, 2).map((action, i) => (
                          <div key={i} className="text-xs opacity-80">• {action}</div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </LiquidCard>
            )}
          </div>
        )}

        {/* Subjects Tab */}
        {activeTab === 'subjects' && subjectBreakdown && (
          <div className="space-y-6">
            {subjectBreakdown.subject_breakdown.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {subjectBreakdown.subject_breakdown.map((subject, index) => (
                  <LiquidCard key={index} className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-primary">{subject.subject_display}</h3>
                      <div className={`px-3 py-1 rounded-full text-sm font-bold border ${getGradeColor(subject.performance_grade)}`}>
                        {subject.performance_grade}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-secondary">Average Score:</span>
                        <span className={`font-bold ${getPerformanceColor(subject.average_score)}`}>
                          {subject.average_score}%
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-secondary">Tests Taken:</span>
                        <span className="text-primary font-medium">{subject.total_tests}</span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-secondary">Best Score:</span>
                        <span className="text-green-400 font-medium">{subject.highest_score}%</span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-secondary">Avg Time:</span>
                        <span className="text-primary font-medium">{subject.avg_time_per_test} min</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-primary/20">
                      <LiquidButton
                        size="sm"
                        variant="secondary"
                        onClick={() => onNavigate('practice')}
                        className="w-full"
                      >
                        Practice {subject.subject_display}
                      </LiquidButton>
                    </div>
                  </LiquidCard>
                ))}
              </div>
            ) : (
              <LiquidCard className="text-center p-12">
                <div className="text-6xl mb-6">📚</div>
                <h2 className="text-2xl font-bold text-primary mb-4">No Subject Data Yet</h2>
                <p className="text-secondary mb-8">
                  Take practice tests in different subjects to see your performance breakdown.
                </p>
                <LiquidButton onClick={() => onNavigate('practice')}>
                  📝 Start Practice Tests
                </LiquidButton>
              </LiquidCard>
            )}
          </div>
        )}

        {/* Trends Tab */}
        {activeTab === 'trends' && trendsData && (
          <div className="space-y-6">
            {trendsData.trend_data && trendsData.trend_data.length > 0 ? (
              <>
                <LiquidCard className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 rounded-full bg-accent-purple/20 flex items-center justify-center">
                      <span className="text-xl">📈</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-accent-purple">Performance Trends</h2>
                      <p className="text-secondary">Your progress over the last {trendsData.period_days || 30} days</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-4 bg-glass/50 rounded-xl">
                      <div className="text-2xl font-bold text-accent-blue mb-1">
                        {trendsData.total_tests_period || 0}
                      </div>
                      <p className="text-secondary text-sm">Tests Taken</p>
                    </div>
                    <div className="text-center p-4 bg-glass/50 rounded-xl">
                      <div className={`text-2xl font-bold mb-1 ${
                        trendsData.trend_direction === 'improving' ? 'text-green-400' :
                        trendsData.trend_direction === 'declining' ? 'text-red-400' : 'text-yellow-400'
                      }`}>
                        {trendsData.trend_direction === 'improving' ? '↗️' :
                         trendsData.trend_direction === 'declining' ? '↘️' : '➡️'}
                      </div>
                      <p className="text-secondary text-sm capitalize">{trendsData.trend_direction || 'stable'}</p>
                    </div>
                    <div className="text-center p-4 bg-glass/50 rounded-xl">
                      <div className="text-2xl font-bold text-accent-green mb-1">
                        {trendsData.trend_data ? trendsData.trend_data.reduce((sum, week) => sum + week.test_count, 0) : 0}
                      </div>
                      <p className="text-secondary text-sm">Weekly Average</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-primary mb-4">Weekly Performance</h3>
                    {trendsData.trend_data.map((week, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-glass/30 rounded-lg">
                        <div>
                          <span className="text-primary font-medium">Week of {new Date(week.week).toLocaleDateString()}</span>
                          <span className="text-secondary text-sm ml-3">({week.test_count} tests)</span>
                        </div>
                        <div className="text-right">
                          <span className={`font-bold ${getPerformanceColor(week.average_score)}`}>
                            {week.average_score}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </LiquidCard>
              </>
            ) : (
              <LiquidCard className="text-center p-12">
                <div className="text-6xl mb-6">📈</div>
                <h2 className="text-2xl font-bold text-primary mb-4">No Trend Data Available</h2>
                <p className="text-secondary mb-8">
                  Take more practice tests over time to see your performance trends.
                </p>
                <LiquidButton onClick={() => onNavigate('practice')}>
                  📝 Start Building Your Progress
                </LiquidButton>
              </LiquidCard>
            )}
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && learningInsights && (
          <div className="space-y-6">
            {/* AI Insights */}
            {learningInsights.insights.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {learningInsights.insights.map((insight, index) => (
                  <LiquidCard key={index} className="p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <span className="text-3xl">{insight.icon}</span>
                      <h3 className="text-xl font-bold text-primary">{insight.title}</h3>
                    </div>
                    <p className="text-secondary mb-4">{insight.message}</p>
                    <div className="p-3 bg-glass/30 rounded-lg">
                      <p className="text-sm text-accent-blue font-medium">💡 Action:</p>
                      <p className="text-sm text-secondary mt-1">{insight.action}</p>
                    </div>
                  </LiquidCard>
                ))}
              </div>
            )}

            {/* Study Tips */}
            {learningInsights.study_tips && (
              <LiquidCard className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-accent-yellow/20 flex items-center justify-center">
                    <span className="text-xl">💡</span>
                  </div>
                  <h2 className="text-2xl font-bold text-accent-yellow">Study Tips</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {learningInsights.study_tips.map((tip, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-glass/30 rounded-lg">
                      <span className="text-accent-yellow mt-1">•</span>
                      <span className="text-secondary text-sm">{tip}</span>
                    </div>
                  ))}
                </div>
              </LiquidCard>
            )}

            {/* Recent Activity Summary */}
            {learningInsights.recent_activity && (
              <LiquidCard className="p-6">
                <h3 className="text-lg font-semibold text-primary mb-4">Recent Activity Summary</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-glass/30 rounded-xl">
                    <div className="text-2xl font-bold text-accent-blue mb-1">
                      {learningInsights.recent_activity.tests_taken}
                    </div>
                    <p className="text-secondary text-sm">Tests (2 weeks)</p>
                  </div>
                  <div className="text-center p-4 bg-glass/30 rounded-xl">
                    <div className="text-2xl font-bold text-accent-green mb-1">
                      {learningInsights.recent_activity.average_score}%
                    </div>
                    <p className="text-secondary text-sm">Average Score</p>
                  </div>
                  <div className="text-center p-4 bg-glass/30 rounded-xl">
                    <div className="text-2xl font-bold text-accent-purple mb-1">
                      {learningInsights.recent_activity.subjects_practiced}
                    </div>
                    <p className="text-secondary text-sm">Subjects</p>
                  </div>
                </div>
              </LiquidCard>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StrengthsWeaknessesComponent;