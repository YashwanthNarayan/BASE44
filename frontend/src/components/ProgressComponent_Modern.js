import React, { useState, useEffect } from 'react';
import { studentAPI, setupAxiosAuth, practiceAPI } from '../services/api';
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
  const [allResults, setAllResults] = useState([]);
  const [displayedCount, setDisplayedCount] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');
  const [showDetailedResults, setShowDetailedResults] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [detailedResults, setDetailedResults] = useState([]);

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

      setupAxiosAuth(token);

      // Load progress data
      const progress = await studentAPI.getProgress();
      setProgressData(progress);

      // Load recent test results
      const results = await studentAPI.getTestResults();
      const allTestResults = Array.isArray(results) ? results : results.results || [];
      setAllResults(allTestResults);
      setRecentResults(allTestResults.slice(0, displayedCount));

    } catch (error) {
      console.error('Error loading progress:', error);
      setError('Failed to load progress data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadDetailedResults = async (testId) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      setupAxiosAuth(token);
      
      const results = await practiceAPI.getDetailedResults(testId);
      setDetailedResults(results.detailed_results || []);
      setShowDetailedResults(true);
    } catch (error) {
      console.error('Error loading detailed results:', error);
      setError('Failed to load detailed results. Please try again.');
    }
  };

  const handleTestClick = (result) => {
    setSelectedTest(result);
    if (result.id) {
      loadDetailedResults(result.id);
    } else {
      // If no detailed results available, show basic info
      setShowDetailedResults(true);
      setDetailedResults([]);
    }
  };

  const loadMoreResults = () => {
    const newCount = Math.min(displayedCount + 5, allResults.length);
    setDisplayedCount(newCount);
    setRecentResults(allResults.slice(0, newCount));
  };

  const calculateStats = () => {
    if (!allResults.length) {
      return {
        totalTests: 0,
        averageScore: 0,
        weeklyTests: 0,
        weeklyGoalProgress: 0,
        targetProgress: 0
      };
    }

    // Calculate overall statistics
    const totalTests = allResults.length;
    const averageScore = allResults.reduce((sum, test) => sum + (test.score || 0), 0) / totalTests;

    // Calculate weekly tests (tests from last 7 days)
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    
    const weeklyTests = allResults.filter(test => {
      const testDate = new Date(test.completed_at);
      return testDate >= oneWeekAgo;
    }).length;

    // Weekly goal progress (assuming goal of 5 tests per week)
    const weeklyGoal = 5;
    const weeklyGoalProgress = Math.min((weeklyTests / weeklyGoal) * 100, 100);

    // Target average progress (assuming target of 85%)
    const targetAverage = 85;
    const targetProgress = Math.min((averageScore / targetAverage) * 100, 100);

    return {
      totalTests,
      averageScore: Math.round(averageScore),
      weeklyTests,
      weeklyGoalProgress: Math.round(weeklyGoalProgress),
      targetProgress: Math.round(targetProgress),
      weeklyGoal,
      targetAverage
    };
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

  // Detailed Results View
  if (showDetailedResults && selectedTest) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <ModernContainer>
            <div className="flex items-center justify-between py-4">
              <ModernButton variant="ghost" onClick={() => setShowDetailedResults(false)}>
                ← Back to Progress
              </ModernButton>
              <ModernHeading level={4}>Test Details</ModernHeading>
              <div></div>
            </div>
          </ModernContainer>
        </header>

        <ModernContainer className="py-8 max-w-6xl">
          {/* Test Summary */}
          <div className="mb-8">
            <div className="text-center mb-6">
              <div className="text-5xl font-bold text-indigo-600 mb-2">
                {selectedTest.score || 0}%
              </div>
              <ModernText variant="body-large" className="text-gray-600 mb-2">
                {selectedTest.subject} • {new Date(selectedTest.completed_at).toLocaleDateString()}
              </ModernText>
              <ModernBadge variant="primary" className="text-lg px-4 py-2">
                Grade: {selectedTest.grade || 'N/A'}
              </ModernBadge>
            </div>

            {/* Summary Stats */}
            <ModernGrid cols={4} className="mb-8">
              <ModernCard>
                <ModernCardBody>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-indigo-600">{selectedTest.score || 0}%</div>
                    <ModernText variant="body-small" className="text-gray-500">Overall Score</ModernText>
                  </div>
                </ModernCardBody>
              </ModernCard>
              <ModernCard>
                <ModernCardBody>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-500">{selectedTest.correct_count || 0}</div>
                    <ModernText variant="body-small" className="text-gray-500">Correct</ModernText>
                  </div>
                </ModernCardBody>
              </ModernCard>
              <ModernCard>
                <ModernCardBody>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-500">{(selectedTest.total_questions || 0) - (selectedTest.correct_count || 0)}</div>
                    <ModernText variant="body-small" className="text-gray-500">Incorrect</ModernText>
                  </div>
                </ModernCardBody>
              </ModernCard>
              <ModernCard>
                <ModernCardBody>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{selectedTest.total_questions || 0}</div>
                    <ModernText variant="body-small" className="text-gray-500">Total Questions</ModernText>
                  </div>
                </ModernCardBody>
              </ModernCard>
            </ModernGrid>
          </div>

          {/* Detailed Question Results */}
          {detailedResults.length > 0 ? (
            <div className="space-y-6">
              <ModernHeading level={3} className="mb-6">Question by Question Results</ModernHeading>
              {detailedResults.map((result, index) => (
                <ModernCard 
                  key={result.question_id || index}
                  className={`border-l-4 ${result.is_correct ? 'border-l-green-500' : 'border-l-red-500'}`}
                >
                  <ModernCardBody>
                    {/* Question Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          result.is_correct ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                        }`}>
                          {result.is_correct ? '✓' : '✗'}
                        </div>
                        <ModernHeading level={4}>Question {index + 1}</ModernHeading>
                        {result.topic && <ModernBadge variant="secondary">{result.topic}</ModernBadge>}
                      </div>
                      <ModernBadge variant={result.is_correct ? 'success' : 'error'}>
                        {result.is_correct ? 'Correct' : 'Incorrect'}
                      </ModernBadge>
                    </div>

                    {/* Question Text */}
                    <ModernText className="mb-4 text-lg font-medium">
                      {result.question_text}
                    </ModernText>
                    
                    {/* MCQ Options */}
                    {result.question_type === 'mcq' && result.options && (
                      <ModernGrid cols={2} className="mb-4">
                        {result.options.map((option, optIndex) => (
                          <div 
                            key={optIndex}
                            className={`p-3 rounded-lg border ${
                              option === result.correct_answer
                                ? 'border-green-500 bg-green-50 text-green-800'
                                : option === result.student_answer && !result.is_correct
                                ? 'border-red-500 bg-red-50 text-red-800'
                                : 'border-gray-200'
                            }`}
                          >
                            <span className="font-medium">{String.fromCharCode(65 + optIndex)}.</span> {option}
                            {option === result.correct_answer && (
                              <span className="ml-2 text-green-600">✓ Correct</span>
                            )}
                            {option === result.student_answer && !result.is_correct && (
                              <span className="ml-2 text-red-600">Your Answer</span>
                            )}
                          </div>
                        ))}
                      </ModernGrid>
                    )}

                    {/* Answers */}
                    <ModernGrid cols={2} className="mb-4">
                      <div>
                        <ModernText variant="body-small" className="text-gray-500 mb-1">Your Answer:</ModernText>
                        <ModernText className={`font-medium ${
                          result.is_correct ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {result.student_answer || 'No answer provided'}
                        </ModernText>
                      </div>
                      <div>
                        <ModernText variant="body-small" className="text-gray-500 mb-1">Correct Answer:</ModernText>
                        <ModernText className="font-medium text-green-600">
                          {result.correct_answer}
                        </ModernText>
                      </div>
                    </ModernGrid>

                    {/* Explanation */}
                    {result.explanation && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <ModernText variant="body-small" className="text-blue-800 font-semibold mb-2">Explanation:</ModernText>
                        <ModernText className="text-blue-700 leading-relaxed">
                          {result.explanation}
                        </ModernText>
                      </div>
                    )}
                  </ModernCardBody>
                </ModernCard>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">Basic Test Information</ModernHeading>
              <ModernText variant="body-small" className="text-gray-500 font-medium mb-4">
                Detailed question-by-question results are not available for this test
              </ModernText>
            </div>
          )}
        </ModernContainer>
      </div>
    );
  }

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
                        <button 
                          key={index} 
                          onClick={() => handleTestClick(result)}
                          className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 transition-all duration-200 border border-transparent cursor-pointer group"
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-2 h-8 rounded-full bg-${color}-500`}></div>
                            <div className="text-left">
                              <ModernText className="font-semibold text-gray-800 capitalize group-hover:text-indigo-900">
                                {result.subject || 'General'}
                              </ModernText>
                              <ModernText variant="body-small" className="text-gray-600 font-medium group-hover:text-indigo-700">
                                {new Date(result.completed_at).toLocaleDateString()} • Click for details
                              </ModernText>
                            </div>
                          </div>
                          <div className="text-right flex items-center gap-3">
                            <div>
                              <ModernHeading level={5} className="text-gray-900 font-bold group-hover:text-indigo-900">
                                {result.score || 0}%
                              </ModernHeading>
                              <ModernBadge variant={performance.color} className="text-xs">
                                {performance.label}
                              </ModernBadge>
                            </div>
                            <svg className="w-5 h-5 text-gray-400 group-hover:text-indigo-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </button>
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