import React, { useState, useEffect } from 'react';
import { practiceSchedulerAPI, practiceAPI, setupAxiosAuth } from '../services/api';
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

const ScheduledTestsComponent_Modern = ({ student, onNavigate }) => {
  const [scheduledTests, setScheduledTests] = useState([]);
  const [activeTest, setActiveTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadScheduledTests();
  }, []);

  const loadScheduledTests = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      setupAxiosAuth(token);
      const response = await practiceSchedulerAPI.getScheduledTests();
      setScheduledTests(response.scheduled_tests || []);
    } catch (error) {
      console.error('Error loading scheduled tests:', error);
      setError('Failed to load scheduled tests. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startTest = (test) => {
    setActiveTest(test);
    setCurrentQuestion(0);
    setAnswers({});
    setError('');
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < activeTest.questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      submitTest();
    }
  };

  const submitTest = async () => {
    try {
      setSubmitting(true);
      const token = localStorage.getItem('access_token');
      setupAxiosAuth(token);

      const submissionData = {
        questions: activeTest.questions.map(q => q.id),
        student_answers: answers,
        question_data: activeTest.questions
      };

      await practiceSchedulerAPI.completeScheduledTest(activeTest.id, submissionData);
      
      // Reload scheduled tests
      await loadScheduledTests();
      setActiveTest(null);
      setCurrentQuestion(0);
      setAnswers({});

    } catch (error) {
      console.error('Error submitting test:', error);
      setError('Failed to submit test. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimeUntilDue = (scheduledFor) => {
    const now = new Date();
    const scheduled = new Date(scheduledFor);
    const diff = scheduled.getTime() - now.getTime();
    
    if (diff <= 0) return 'Due now';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} left`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} left`;
    return 'Due soon';
  };

  const getUrgencyColor = (scheduledFor) => {
    const now = new Date();
    const scheduled = new Date(scheduledFor);
    const diff = scheduled.getTime() - now.getTime();
    const hours = diff / (1000 * 60 * 60);
    
    if (hours <= 0) return 'error';
    if (hours <= 24) return 'warning';
    return 'success';
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'success',
      medium: 'warning', 
      hard: 'error'
    };
    return colors[difficulty] || 'secondary';
  };

  // Active Test View
  if (activeTest) {
    const question = activeTest.questions[currentQuestion];
    const progress = ((currentQuestion + 1) / activeTest.questions.length) * 100;

    return (
      <div className="min-h-screen bg-gray-50">
        <NavigationBar_Modern 
          user={student}
          currentPage="scheduled-tests"
          onNavigate={onNavigate}
          onLogout={() => onNavigate('auth')}
        />

        <ModernContainer className="py-8 max-w-4xl">
          {/* Test Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <ModernHeading level={3} className="text-gray-800 font-semibold">
                {activeTest.subject} Review Test
              </ModernHeading>
              <ModernBadge variant="primary">
                Question {currentQuestion + 1} of {activeTest.questions.length}
              </ModernBadge>
            </div>
            <ModernProgress value={progress} max={100} label={`${Math.round(progress)}% Complete`} />
          </div>

          {/* Question Card */}
          <ModernCard className="mb-6">
            <ModernCardBody>
              <ModernHeading level={4} className="text-gray-800 font-semibold mb-6">
                {question.question_text}
              </ModernHeading>

              {question.question_type === 'mcq' && question.options && (
                <div className="space-y-3">
                  {question.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswer(question.id, option)}
                      className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-300 ${
                        answers[question.id] === option
                          ? 'border-indigo-500 bg-indigo-50 text-indigo-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          answers[question.id] === option
                            ? 'border-indigo-500 bg-indigo-500'
                            : 'border-gray-300'
                        }`}>
                          {answers[question.id] === option && (
                            <div className="w-2 h-2 rounded-full bg-white" />
                          )}
                        </div>
                        <span className="font-medium">{option}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {question.question_type !== 'mcq' && (
                <textarea
                  className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors duration-300 font-medium"
                  rows="6"
                  placeholder="Enter your answer here..."
                  value={answers[question.id] || ''}
                  onChange={(e) => handleAnswer(question.id, e.target.value)}
                />
              )}
            </ModernCardBody>
          </ModernCard>

          {/* Navigation */}
          <div className="flex justify-between">
            <ModernButton
              variant="outline"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              Previous
            </ModernButton>
            <ModernButton
              variant="primary"
              onClick={nextQuestion}
              disabled={!answers[question.id] || submitting}
              className="font-semibold"
            >
              {submitting ? (
                <div className="flex items-center gap-2">
                  <ModernSpinner size="sm" />
                  Submitting...
                </div>
              ) : (
                currentQuestion === activeTest.questions.length - 1 ? 'Submit Test' : 'Next'
              )}
            </ModernButton>
          </div>

          {error && (
            <ModernAlert variant="error" className="mt-6">
              {error}
            </ModernAlert>
          )}
        </ModernContainer>
      </div>
    );
  }

  // Main View
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ModernSpinner size="lg" />
          <ModernText className="mt-4 text-gray-600 font-medium">Loading scheduled tests...</ModernText>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="scheduled-tests"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
            </svg>
          </div>
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-4">
            Scheduled Reviews
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            AI-powered spaced repetition keeps your learning sharp
          </ModernText>
        </div>

        {error && (
          <ModernAlert variant="error" className="mb-6">
            {error}
          </ModernAlert>
        )}

        {scheduledTests.length > 0 ? (
          <>
            {/* Stats */}
            <ModernGrid cols={3} className="mb-8">
              <ModernCard>
                <ModernCardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <ModernText variant="body-small" className="text-gray-500 uppercase tracking-wide font-semibold">
                        Total Scheduled
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {scheduledTests.length}
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
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
                        Due Today
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {scheduledTests.filter(test => {
                          const now = new Date();
                          const scheduled = new Date(test.scheduled_for);
                          return scheduled.toDateString() === now.toDateString();
                        }).length}
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd"/>
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
                        Completed
                      </ModernText>
                      <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                        {scheduledTests.filter(test => test.completed).length}
                      </ModernHeading>
                    </div>
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                      </svg>
                    </div>
                  </div>
                </ModernCardBody>
              </ModernCard>
            </ModernGrid>

            {/* Test Cards */}
            <ModernGrid cols={2}>
              {scheduledTests.map((test) => {
                const urgencyColor = getUrgencyColor(test.scheduled_for);
                const difficultyColor = getDifficultyColor(test.difficulty);
                
                return (
                  <ModernCard key={test.id} hover={!test.completed}>
                    <ModernCardBody>
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex gap-2">
                          <ModernBadge variant={urgencyColor} className="text-xs font-semibold">
                            {formatTimeUntilDue(test.scheduled_for)}
                          </ModernBadge>
                          <ModernBadge variant={difficultyColor} className="text-xs font-semibold">
                            {test.difficulty}
                          </ModernBadge>
                        </div>
                        {test.completed && (
                          <ModernBadge variant="success" className="text-xs font-semibold">
                            Completed
                          </ModernBadge>
                        )}
                      </div>

                      <ModernHeading level={4} className="text-gray-800 font-semibold mb-2 capitalize">
                        {test.subject} Review
                      </ModernHeading>
                      
                      <ModernText variant="body-small" className="text-gray-600 font-medium mb-4">
                        Review test based on your previous performance in {test.subject}
                      </ModernText>

                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-4 text-sm">
                          <ModernText variant="body-small" className="text-gray-600 font-medium">
                            <span className="font-semibold">{test.questions?.length || 0}</span> questions
                          </ModernText>
                          <ModernText variant="body-small" className="text-gray-600 font-medium">
                            <span className="font-semibold">{Math.round((test.questions?.length || 0) * 1.5)}</span> min
                          </ModernText>
                        </div>
                      </div>

                      <ModernText variant="caption" className="text-gray-500 font-medium mb-4">
                        Scheduled: {new Date(test.scheduled_for).toLocaleDateString()} at {new Date(test.scheduled_for).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </ModernText>

                      {!test.completed ? (
                        <ModernButton
                          variant="primary"
                          onClick={() => startTest(test)}
                          className="w-full font-semibold"
                        >
                          Start Review
                        </ModernButton>
                      ) : (
                        <ModernButton
                          variant="outline"
                          disabled
                          className="w-full font-medium"
                        >
                          Review Complete
                        </ModernButton>
                      )}
                    </ModernCardBody>
                  </ModernCard>
                );
              })}
            </ModernGrid>
          </>
        ) : (
          <ModernCard>
            <ModernCardBody>
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
                  </svg>
                </div>
                <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">No Scheduled Reviews</ModernHeading>
                <ModernText variant="body-small" className="text-gray-500 font-medium mb-6">
                  Take practice tests to get personalized review schedules based on your performance
                </ModernText>
                <ModernButton 
                  variant="primary" 
                  onClick={() => onNavigate('practice-tests')}
                  className="font-semibold"
                >
                  Take Practice Test
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>
        )}
      </ModernContainer>
    </div>
  );
};

export default ScheduledTestsComponent_Modern;