import React, { useState, useEffect } from 'react';
import { studentAnalyticsAPI } from '../services/api';
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

const StrengthsWeaknessesComponent_Modern = ({ student, onNavigate }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      const [strengthsWeaknesses, trends, subjects, insights, testResults] = await Promise.all([
        studentAnalyticsAPI.getStrengthsWeaknesses().catch(err => ({ strengths: [], weaknesses: [] })),
        studentAnalyticsAPI.getPerformanceTrends().catch(err => ({ trends: [] })),
        studentAnalyticsAPI.getSubjectBreakdown().catch(err => ({ subjects: [] })),
        studentAnalyticsAPI.getLearningInsights().catch(err => ({ insights: [] })),
        studentAPI.getTestResults().catch(err => [])
      ]);

      // Store test results for subject performance calculation
      if (Array.isArray(testResults) && testResults.length > 0) {
        localStorage.setItem('recent_test_results', JSON.stringify(testResults));
      } else if (testResults.results && Array.isArray(testResults.results)) {
        localStorage.setItem('recent_test_results', JSON.stringify(testResults.results));
      }

      // Use calculated subject performance if API doesn't return it
      const calculatedSubjects = calculateSubjectPerformance();
      const apiSubjects = subjects.subject_breakdown || subjects.subjects || [];
      
      setAnalytics({
        strengths: strengthsWeaknesses.strengths || [],
        weaknesses: strengthsWeaknesses.weaknesses || [],
        trends: trends.trend_data || trends.trends || [],
        subjects: apiSubjects.length > 0 ? apiSubjects : calculatedSubjects,
        insights: insights.insights || insights || []
      });

    } catch (error) {
      console.error('Error loading analytics:', error);
      
      // Handle authentication errors
      if (error.response?.status === 403 || error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_type');
        localStorage.removeItem('user');
        setError('Authentication expired. Please refresh the page and log in again.');
      } else {
        setError('Failed to load analytics data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getSubjectColor = (subject) => {
    const colors = {
      mathematics: 'blue',
      physics: 'green',
      chemistry: 'purple',
      biology: 'emerald',
      english: 'indigo',
      science: 'teal',
      social: 'amber'
    };
    return colors[subject?.toLowerCase()] || 'gray';
  };

  // Calculate subject performance from test results
  const calculateSubjectPerformance = () => {
    // Get test results from localStorage or make API call
    const storedResults = localStorage.getItem('recent_test_results');
    let testResults = [];
    
    if (storedResults) {
      try {
        testResults = JSON.parse(storedResults);
      } catch (e) {
        console.warn('Could not parse stored results');
      }
    }

    if (!Array.isArray(testResults) || testResults.length === 0) {
      return [];
    }

    // Group tests by subject and calculate averages
    const subjectStats = {};
    
    testResults.forEach(result => {
      const subject = result.subject || 'general';
      if (!subjectStats[subject]) {
        subjectStats[subject] = {
          subject: subject,
          scores: [],
          totalQuestions: 0,
          correctAnswers: 0,
          testCount: 0
        };
      }
      
      subjectStats[subject].scores.push(result.score || 0);
      subjectStats[subject].totalQuestions += result.total_questions || 0;
      subjectStats[subject].correctAnswers += result.correct_count || 0;
      subjectStats[subject].testCount += 1;
    });

    // Convert to array format expected by the component
    return Object.values(subjectStats).map(stat => ({
      subject: stat.subject,
      average_score: stat.scores.reduce((sum, score) => sum + score, 0) / stat.scores.length,
      test_count: stat.testCount,
      total_questions: stat.totalQuestions,
      correct_answers: stat.correctAnswers,
      improvement_trend: stat.scores.length > 1 ? 
        (stat.scores[stat.scores.length - 1] - stat.scores[0]) : 0
    })).sort((a, b) => b.average_score - a.average_score);
  };

  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
      red: 'bg-red-100 text-red-800 border-red-200',
      green: 'bg-green-100 text-green-800 border-green-200',
      indigo: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      gray: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colorMap[color] || colorMap.gray;
  };

  const getPerformanceLabel = (score) => {
    if (score >= 90) return { label: 'Excellent', color: 'success' };
    if (score >= 80) return { label: 'Good', color: 'success' };
    if (score >= 70) return { label: 'Fair', color: 'warning' };
    if (score >= 60) return { label: 'Needs Work', color: 'warning' };
    return { label: 'Needs Help', color: 'error' };
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'subjects', label: 'Subjects' },
    { id: 'trends', label: 'Trends' },
    { id: 'insights', label: 'Insights' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ModernSpinner size="lg" />
          <ModernText className="mt-4 text-gray-600 font-medium">Loading your analytics...</ModernText>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="strengths-weaknesses"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"/>
              <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"/>
            </svg>
          </div>
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-4">
            Learning Analytics
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Understand your strengths, identify areas for improvement
          </ModernText>
        </div>

        {error && (
          <ModernAlert variant="error" className="mb-6">
            {error}
          </ModernAlert>
        )}

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 rounded-xl p-1 inline-flex">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {analytics && (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <ModernGrid cols={2}>
                  {/* Strengths */}
                  <ModernCard>
                    <ModernCardHeader>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                          <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                          </svg>
                        </div>
                        <ModernHeading level={4} className="text-gray-800 font-semibold">Your Strengths</ModernHeading>
                      </div>
                    </ModernCardHeader>
                    <ModernCardBody>
                      {analytics.strengths.length > 0 ? (
                        <div className="space-y-3">
                          {analytics.strengths.slice(0, 5).map((strength, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                              <ModernText className="font-semibold text-green-800 capitalize">
                                {strength.topic || strength.subject}
                              </ModernText>
                              <ModernBadge variant="success">
                                {Math.round(strength.performance || strength.score)}%
                              </ModernBadge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <ModernText variant="body-small" className="text-gray-500 font-medium">
                            Take more tests to identify your strengths
                          </ModernText>
                        </div>
                      )}
                    </ModernCardBody>
                  </ModernCard>

                  {/* Weaknesses */}
                  <ModernCard>
                    <ModernCardHeader>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                          <svg className="w-4 h-4 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                          </svg>
                        </div>
                        <ModernHeading level={4} className="text-gray-800 font-semibold">Areas to Improve</ModernHeading>
                      </div>
                    </ModernCardHeader>
                    <ModernCardBody>
                      {analytics.weaknesses.length > 0 ? (
                        <div className="space-y-3">
                          {analytics.weaknesses.slice(0, 5).map((weakness, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                              <ModernText className="font-semibold text-orange-800 capitalize">
                                {weakness.topic || weakness.subject}
                              </ModernText>
                              <ModernBadge variant="warning">
                                {Math.round(weakness.performance || weakness.score)}%
                              </ModernBadge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <ModernText variant="body-small" className="text-gray-500 font-medium">
                            Great job! No major weaknesses identified
                          </ModernText>
                        </div>
                      )}
                    </ModernCardBody>
                  </ModernCard>
                </ModernGrid>
              </div>
            )}

            {/* Subjects Tab */}
            {activeTab === 'subjects' && (
              <ModernGrid cols={1}>
                <ModernCard>
                  <ModernCardHeader>
                    <ModernHeading level={4} className="text-gray-800 font-semibold">Subject Performance</ModernHeading>
                  </ModernCardHeader>
                  <ModernCardBody>
                    {analytics.subjects.length > 0 ? (
                      <div className="space-y-4">
                        {analytics.subjects.map((subject, index) => {
                          const color = getSubjectColor(subject.subject);
                          const performance = getPerformanceLabel(subject.average_score || 0);
                          const improvementTrend = subject.improvement_trend || 0;
                          
                          return (
                            <div key={index} className="p-5 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                  <div className={`w-6 h-6 rounded-full bg-${color}-500 flex items-center justify-center`}>
                                    <span className="text-white text-xs font-bold">
                                      {subject.subject.charAt(0).toUpperCase()}
                                    </span>
                                  </div>
                                  <div>
                                    <ModernHeading level={5} className="text-gray-800 font-semibold capitalize">
                                      {subject.subject}
                                    </ModernHeading>
                                    <ModernText variant="body-small" className="text-gray-500">
                                      {subject.test_count || 0} tests • {subject.total_questions || 0} questions
                                    </ModernText>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <ModernHeading level={4} className="text-gray-900 font-bold text-2xl">
                                    {Math.round(subject.average_score || 0)}%
                                  </ModernHeading>
                                  <ModernBadge variant={performance.color} className="text-xs">
                                    {performance.label}
                                  </ModernBadge>
                                </div>
                              </div>
                              
                              <ModernProgress value={subject.average_score || 0} max={100} className="mb-4" />
                              
                              <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="p-3 bg-gray-50 rounded-lg">
                                  <div className="text-lg font-bold text-gray-900">
                                    {Math.round(((subject.correct_answers || 0) / (subject.total_questions || 1)) * 100)}%
                                  </div>
                                  <ModernText variant="body-small" className="text-gray-500 font-medium">
                                    Accuracy
                                  </ModernText>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-lg">
                                  <div className="text-lg font-bold text-gray-900">
                                    {subject.test_count || 0}
                                  </div>
                                  <ModernText variant="body-small" className="text-gray-500 font-medium">
                                    Tests
                                  </ModernText>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-lg">
                                  <div className={`text-lg font-bold flex items-center justify-center gap-1 ${
                                    improvementTrend > 0 ? 'text-green-600' : 
                                    improvementTrend < 0 ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {improvementTrend > 0 ? (
                                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                      </svg>
                                    ) : improvementTrend < 0 ? (
                                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                      </svg>
                                    ) : (
                                      <div className="w-4 h-4 border border-gray-400 rounded-full"></div>
                                    )}
                                    {Math.abs(improvementTrend) > 0 ? `${Math.abs(Math.round(improvementTrend))}%` : 'Stable'}
                                  </div>
                                  <ModernText variant="body-small" className="text-gray-500 font-medium">
                                    Trend
                                  </ModernText>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <ModernText variant="body-small" className="text-gray-500 font-medium">
                          Take tests in different subjects to see your performance breakdown
                        </ModernText>
                      </div>
                    )}
                  </ModernCardBody>
                </ModernCard>
              </ModernGrid>
            )}

            {/* Trends Tab */}
            {activeTab === 'trends' && (
              <ModernCard>
                <ModernCardHeader>
                  <ModernHeading level={4} className="text-gray-800 font-semibold">Performance Trends</ModernHeading>
                </ModernCardHeader>
                <ModernCardBody>
                  {analytics.trends.length > 0 ? (
                    <div className="space-y-4">
                      {analytics.trends.map((trend, index) => (
                        <div key={index} className="p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <ModernHeading level={5} className="text-gray-800 font-semibold">
                                {trend.period}
                              </ModernHeading>
                              <ModernText variant="body-small" className="text-gray-600 font-medium">
                                Average Score: {Math.round(trend.average_score || 0)}%
                              </ModernText>
                            </div>
                            <div className="text-right">
                              <ModernText className={`font-semibold ${
                                trend.trend === 'improving' ? 'text-green-600' :
                                trend.trend === 'declining' ? 'text-red-600' :
                                'text-gray-600'
                              }`}>
                                {trend.trend === 'improving' ? '↗ Improving' :
                                 trend.trend === 'declining' ? '↘ Declining' :
                                 '→ Stable'}
                              </ModernText>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <ModernText variant="body-small" className="text-gray-500 font-medium">
                        Take more tests over time to see your learning trends
                      </ModernText>
                    </div>
                  )}
                </ModernCardBody>
              </ModernCard>
            )}

            {/* Insights Tab */}
            {activeTab === 'insights' && (
              <ModernGrid cols={1}>
                <ModernCard>
                  <ModernCardHeader>
                    <ModernHeading level={4} className="text-gray-800 font-semibold">Learning Insights</ModernHeading>
                  </ModernCardHeader>
                  <ModernCardBody>
                    {analytics.insights.length > 0 ? (
                      <div className="space-y-4">
                        {analytics.insights.map((insight, index) => (
                          <div key={index} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <div className="flex items-start gap-3">
                              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                                </svg>
                              </div>
                              <div className="flex-1">
                                <ModernHeading level={5} className="text-blue-800 font-semibold mb-2">
                                  {insight.title || 'Learning Insight'}
                                </ModernHeading>
                                <ModernText variant="body-small" className="text-blue-700 font-medium">
                                  {insight.description || insight.insight}
                                </ModernText>
                                {insight.recommendation && (
                                  <ModernText variant="body-small" className="text-blue-600 font-medium mt-2">
                                    💡 {insight.recommendation}
                                  </ModernText>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                          </svg>
                        </div>
                        <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">No Insights Yet</ModernHeading>
                        <ModernText variant="body-small" className="text-gray-500 font-medium mb-6">
                          Complete more practice tests to get personalized learning insights
                        </ModernText>
                        <ModernButton 
                          variant="primary" 
                          onClick={() => onNavigate('practice-tests')}
                          className="font-semibold"
                        >
                          Take Practice Test
                        </ModernButton>
                      </div>
                    )}
                  </ModernCardBody>
                </ModernCard>
              </ModernGrid>
            )}
          </>
        )}
      </ModernContainer>
    </div>
  );
};

export default StrengthsWeaknessesComponent_Modern;