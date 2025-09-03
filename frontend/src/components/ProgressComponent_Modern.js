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

const ProgressComponent_Modern = ({ student, onNavigate }) => {
  const [progressData, setProgressData] = useState(null);
  const [recentResults, setRecentResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');

  useEffect(() => {
    loadProgressData();
  }, [selectedTimeframe]);

  const loadProgressData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      // Load progress data
      const progress = await studentAPI.getProgress();
      setProgressData(progress);

      // Load recent test results
      const results = await studentAPI.getTestResults();
      setRecentResults(results.results || []);

    } catch (error) {
      console.error('Error loading progress:', error);
      setError('Failed to load progress data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSubjectColor = (subject) => {
    const colors = {
      mathematics: 'blue',
      physics: 'purple', 
      chemistry: 'red',
      biology: 'green',
      english: 'indigo'
    };
    return colors[subject?.toLowerCase()] || 'gray';
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

  const timeframeOptions = [
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'all', label: 'All Time' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ModernSpinner size="lg" />
          <ModernText className="mt-4 text-gray-600 font-medium">Loading your progress...</ModernText>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="progress"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
              Progress Tracker
            </ModernHeading>
            <ModernText variant="body-large" className="text-gray-600 font-medium">
              Monitor your learning journey and academic performance
            </ModernText>
          </div>
          <div className="flex gap-2">
            {timeframeOptions.map((option) => (
              <ModernButton
                key={option.value}
                variant={selectedTimeframe === option.value ? 'primary' : 'outline'}
                onClick={() => setSelectedTimeframe(option.value)}
                className="text-sm font-medium"
              >
                {option.label}
              </ModernButton>
            ))}
          </div>
        </div>

        {error && (
          <ModernAlert variant="error" className="mb-6">
            {error}
          </ModernAlert>
        )}

        {progressData && (
          <>
            {/* Overall Statistics */}
            <ModernGrid cols={4} className="mb-8">
              <ModernCard>
                <ModernCardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <ModernText variant="body-small" className="text-gray-500 uppercase tracking-wide font-semibold">
                        Tests Completed
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {progressData.total_tests || 0}
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                  </div>
                </ModernCardBody>
              </ModernCard>

              <ModernCard>
                <ModernCardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <ModernText variant="body-small" className="text-gray-500 uppercase tracking-wide font-semibold">
                        Average Score
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {Math.round(progressData.average_score || 0)}%
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"/>
                      </svg>
                    </div>
                  </div>
                  <div className="mt-2">
                    <ModernProgress value={progressData.average_score || 0} max={100} />
                  </div>
                </ModernCardBody>
              </ModernCard>

              <ModernCard>
                <ModernCardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <ModernText variant="body-small" className="text-gray-500 uppercase tracking-wide font-semibold">
                        Study Streak
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {progressData.study_streak || 0} days
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd"/>
                      </svg>
                    </div>
                  </div>
                </ModernCardBody>
              </ModernCard>

              <ModernCard>
                <ModernCardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <ModernText variant="body-small" className="text-gray-500 uppercase tracking-wide font-semibold">
                        XP Points
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {progressData.xp_points || 0}
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/>
                      </svg>
                    </div>
                  </div>
                </ModernCardBody>
              </ModernCard>
            </ModernGrid>

            {/* Subject Performance */}
            <ModernGrid cols={2} className="mb-8">
              <ModernCard>
                <ModernCardHeader>
                  <ModernHeading level={4} className="text-gray-800 font-semibold">Subject Performance</ModernHeading>
                </ModernCardHeader>
                <ModernCardBody>
                  <div className="space-y-4">
                    {progressData.subject_breakdown?.map((subject) => {
                      const color = getSubjectColor(subject.subject);
                      const performance = getPerformanceLabel(subject.average_score || 0);
                      
                      return (
                        <div key={subject.subject} className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full bg-${color}-500`}></div>
                            <div>
                              <ModernText className="font-semibold text-gray-800 capitalize">
                                {subject.subject}
                              </ModernText>
                              <ModernText variant="body-small" className="text-gray-600 font-medium">
                                {subject.tests_taken || 0} tests completed
                              </ModernText>
                            </div>
                          </div>
                          <div className="text-right">
                            <ModernHeading level={5} className="text-gray-900 font-bold">
                              {Math.round(subject.average_score || 0)}%
                            </ModernHeading>
                            <ModernBadge variant={performance.color} className="text-xs">
                              {performance.label}
                            </ModernBadge>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </ModernCardBody>
              </ModernCard>

              <ModernCard>
                <ModernCardHeader>
                  <ModernHeading level={4} className="text-gray-800 font-semibold">Learning Goals</ModernHeading>
                </ModernCardHeader>
                <ModernCardBody>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <ModernText className="font-semibold text-gray-800">Weekly Test Goal</ModernText>
                        <ModernText className="text-gray-600 font-medium">3/5</ModernText>
                      </div>
                      <ModernProgress value={60} max={100} className="mb-1" />
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        2 more tests to reach your weekly goal
                      </ModernText>
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <ModernText className="font-semibold text-gray-800">Target Average</ModernText>
                        <ModernText className="text-gray-600 font-medium">82/85%</ModernText>
                      </div>
                      <ModernProgress value={96} max={100} className="mb-1" />
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        You're almost at your target!
                      </ModernText>
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <ModernText className="font-semibold text-gray-800">Study Streak</ModernText>
                        <ModernText className="text-gray-600 font-medium">7/10 days</ModernText>
                      </div>
                      <ModernProgress value={70} max={100} className="mb-1" />
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        Keep going to reach 10 days!
                      </ModernText>
                    </div>
                  </div>
                </ModernCardBody>
              </ModernCard>
            </ModernGrid>

            {/* Recent Test Results */}
            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={4} className="text-gray-800 font-semibold">Recent Test Results</ModernHeading>
              </ModernCardHeader>
              <ModernCardBody>
                {recentResults.length > 0 ? (
                  <div className="space-y-3">
                    {recentResults.slice(0, 10).map((result, index) => {
                      const performance = getPerformanceLabel(result.score || 0);
                      const color = getSubjectColor(result.subject);
                      
                      return (
                        <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                          <div className="flex items-center gap-4">
                            <div className={`w-2 h-8 rounded-full bg-${color}-500`}></div>
                            <div>
                              <ModernText className="font-semibold text-gray-800 capitalize">
                                {result.subject || 'General'}
                              </ModernText>
                              <ModernText variant="body-small" className="text-gray-600 font-medium">
                                {new Date(result.completed_at).toLocaleDateString()}
                              </ModernText>
                            </div>
                          </div>
                          <div className="text-right">
                            <ModernHeading level={5} className="text-gray-900 font-bold">
                              {result.score || 0}%
                            </ModernHeading>
                            <ModernBadge variant={performance.color} className="text-xs">
                              {performance.label}
                            </ModernBadge>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                    <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">No Test Results Yet</ModernHeading>
                    <ModernText variant="body-small" className="text-gray-500 font-medium mb-4">
                      Take your first practice test to start tracking progress
                    </ModernText>
                    <ModernButton 
                      variant="primary" 
                      onClick={() => onNavigate('practice-tests')}
                      className="font-medium"
                    >
                      Start Practice Test
                    </ModernButton>
                  </div>
                )}
              </ModernCardBody>
            </ModernCard>
          </>
        )}
      </ModernContainer>
    </div>
  );
};

export default ProgressComponent_Modern;