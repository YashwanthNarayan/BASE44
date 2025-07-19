import React, { useState, useEffect } from 'react';
import { practiceSchedulerAPI, practiceAPI } from '../services/api';
import { LiquidCard, LiquidButton } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const ScheduledTestsComponent = ({ student, onNavigate }) => {
  const [upcomingTests, setUpcomingTests] = useState({
    overdue: [],
    today: [],
    this_week: [],
    later: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedTest, setSelectedTest] = useState(null);
  const [testQuestions, setTestQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [testInProgress, setTestInProgress] = useState(false);

  useEffect(() => {
    loadUpcomingTests();
  }, []);

  const loadUpcomingTests = async () => {
    try {
      setLoading(true);
      const tests = await practiceSchedulerAPI.getUpcomingTests();
      setUpcomingTests(tests);
    } catch (error) {
      console.error('Error loading upcoming tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const startScheduledTest = async (test) => {
    try {
      const response = await practiceSchedulerAPI.takeScheduledTest(test.id);
      setSelectedTest(response.scheduled_test);
      setTestQuestions(response.questions);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setTestInProgress(true);
    } catch (error) {
      console.error('Error starting scheduled test:', error);
      alert('Failed to start test. Please try again.');
    }
  };

  const handleAnswerSubmit = (questionId, answer) => {
    console.log('Answer submitted:', { questionId, answer, currentAnswers: userAnswers });
    setUserAnswers(prev => {
      const updated = { ...prev, [questionId]: answer };
      console.log('Updated answers:', updated);
      return updated;
    });
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < testQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      submitScheduledTest();
    }
  };

  const submitScheduledTest = async () => {
    try {
      // Create a temporary test session to submit the answers
      const testData = {
        questions: testQuestions.map(q => q.id),  // Send question IDs only (as strings)
        student_answers: userAnswers,
        subject: selectedTest.subject,
        time_taken: 300, // 5 minutes default
        question_data: testQuestions  // Include question data for validation
      };

      // Submit using a custom endpoint for scheduled tests
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/practice/submit-scheduled`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(testData)
      });

      if (!response.ok) {
        throw new Error(`Failed to submit test: ${response.status}`);
      }

      const results = await response.json();

      // Mark the scheduled test as completed
      await practiceSchedulerAPI.completeScheduledTest(selectedTest.id, results.score);

      // Reset state and reload upcoming tests
      setTestInProgress(false);
      setSelectedTest(null);
      setTestQuestions([]);
      setUserAnswers({});
      loadUpcomingTests();

      alert(`Test completed! Score: ${results.score}%. Your next review has been automatically scheduled.`);
    } catch (error) {
      console.error('Error submitting scheduled test:', error);
      alert('Failed to submit test. Please try again.');
    }
  };

  const cancelTest = async (testId) => {
    if (window.confirm('Are you sure you want to cancel this scheduled test?')) {
      try {
        await practiceSchedulerAPI.cancelTest(testId);
        loadUpcomingTests();
      } catch (error) {
        console.error('Error cancelling test:', error);
        alert('Failed to cancel test. Please try again.');
      }
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays < 7) return `In ${diffDays} days`;
    
    return date.toLocaleDateString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-400 bg-red-500/10';
      case 'medium': return 'border-yellow-400 bg-yellow-500/10';
      case 'low': return 'border-green-400 bg-green-500/10';
      default: return 'border-primary/20 bg-glass';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🔥';
      case 'medium': return '⚡';
      case 'low': return '📝';
      default: return '📚';
    }
  };

  // Test Taking View
  if (testInProgress && testQuestions.length > 0) {
    const currentQuestion = testQuestions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / testQuestions.length) * 100;
    
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary mb-2">📅 Scheduled Review Test</h1>
            <p className="text-secondary">Question {currentQuestionIndex + 1} of {testQuestions.length}</p>
            <div className="w-full bg-glass rounded-full h-2 mt-4">
              <div 
                className="bg-gradient-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <LiquidCard className="p-8">
            <h2 className="text-xl font-semibold text-primary mb-6">{currentQuestion.question_text}</h2>
            
            {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
              <div className="space-y-3 mb-8">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = userAnswers[currentQuestion.id] === option;
                  return (
                    <button
                      key={index}
                      onClick={() => handleAnswerSubmit(currentQuestion.id, option)}
                      className={`w-full p-4 rounded-xl border transition-all duration-300 text-left font-medium ${
                        isSelected
                          ? 'border-accent-blue bg-accent-blue/30 text-accent-blue shadow-lg shadow-accent-blue/20' 
                          : 'border-primary/20 hover:border-primary/40 hover:bg-glass/50 text-primary'
                      }`}
                      style={{
                        backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.2)' : undefined,
                        borderColor: isSelected ? 'rgb(59, 130, 246)' : undefined,
                        color: isSelected ? 'rgb(147, 197, 253)' : '#e2e8f0'
                      }}
                    >
                      <span className={`font-bold mr-3 ${isSelected ? 'text-accent-blue' : 'text-secondary'}`}>
                        {String.fromCharCode(65 + index)}.
                      </span>
                      <span className={isSelected ? 'text-accent-blue' : 'text-primary'}>
                        {option}
                      </span>
                      {isSelected && (
                        <span className="float-right text-accent-blue">✓</span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
            
            {currentQuestion.question_type !== 'mcq' && (
              <div className="mb-8">
                <textarea
                  className="w-full p-6 glass rounded-2xl text-primary placeholder-secondary border border-primary/20 focus:border-accent-blue/40 focus:glass-strong transition-all duration-300 bg-glass/80"
                  style={{
                    color: '#e2e8f0',
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }}
                  rows="6"
                  placeholder="Enter your answer here..."
                  value={userAnswers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerSubmit(currentQuestion.id, e.target.value)}
                />
              </div>
            )}
            
            <div className="flex justify-between">
              <LiquidButton
                onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                disabled={currentQuestionIndex === 0}
                variant="secondary"
              >
                ← Previous
              </LiquidButton>
              <LiquidButton
                onClick={nextQuestion}
                disabled={!userAnswers[currentQuestion.id]}
                variant="primary"
              >
                {currentQuestionIndex === testQuestions.length - 1 ? 'Complete Review' : 'Next →'}
              </LiquidButton>
            </div>
          </LiquidCard>
        </div>
      </div>
    );
  }

  // Main Scheduled Tests View
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
            📅 Scheduled Reviews
          </h1>
          <p className="text-secondary">AI-powered spaced repetition learning</p>
        </div>

        {loading ? (
          <LiquidCard className="text-center p-12">
            <div className="quantum-loader mx-auto mb-4" />
            <p className="text-secondary">Loading scheduled tests...</p>
          </LiquidCard>
        ) : (
          <div className="space-y-8">
            {/* Overdue Tests */}
            {upcomingTests.overdue.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-red-400 mb-4 flex items-center">
                  🚨 Overdue Reviews ({upcomingTests.overdue.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {upcomingTests.overdue.map((test) => (
                    <TestCard key={test.id} test={test} onStart={startScheduledTest} onCancel={cancelTest} />
                  ))}
                </div>
              </div>
            )}

            {/* Today's Tests */}
            {upcomingTests.today.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-accent-blue mb-4 flex items-center">
                  📚 Today's Reviews ({upcomingTests.today.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {upcomingTests.today.map((test) => (
                    <TestCard key={test.id} test={test} onStart={startScheduledTest} onCancel={cancelTest} />
                  ))}
                </div>
              </div>
            )}

            {/* This Week's Tests */}
            {upcomingTests.this_week.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-accent-green mb-4 flex items-center">
                  📅 This Week ({upcomingTests.this_week.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {upcomingTests.this_week.map((test) => (
                    <TestCard key={test.id} test={test} onStart={startScheduledTest} onCancel={cancelTest} />
                  ))}
                </div>
              </div>
            )}

            {/* Later Tests */}
            {upcomingTests.later.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-secondary mb-4 flex items-center">
                  📝 Upcoming ({upcomingTests.later.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {upcomingTests.later.map((test) => (
                    <TestCard key={test.id} test={test} onStart={startScheduledTest} onCancel={cancelTest} />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {Object.values(upcomingTests).every(arr => arr.length === 0) && (
              <LiquidCard className="text-center p-12">
                <div className="text-6xl mb-6">🎉</div>
                <h2 className="text-2xl font-bold text-primary mb-4">All Caught Up!</h2>
                <p className="text-secondary mb-6">
                  No scheduled review tests at the moment. Take some practice tests to get personalized review schedules.
                </p>
                <LiquidButton onClick={() => onNavigate('practice')}>
                  📝 Take Practice Test
                </LiquidButton>
              </LiquidCard>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Individual Test Card Component
const TestCard = ({ test, onStart, onCancel }) => {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays < 7) return `In ${diffDays} days`;
    
    return date.toLocaleDateString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-400 bg-red-500/10';
      case 'medium': return 'border-yellow-400 bg-yellow-500/10';
      case 'low': return 'border-green-400 bg-green-500/10';
      default: return 'border-primary/20 bg-glass';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🔥';
      case 'medium': return '⚡';
      case 'low': return '📝';
      default: return '📚';
    }
  };

  return (
    <LiquidCard className={`p-6 ${getPriorityColor(test.priority)} border-l-4`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getPriorityIcon(test.priority)}</span>
          <div>
            <h3 className="text-lg font-bold text-primary">{test.subject}</h3>
            <p className="text-sm text-secondary">{test.topics.join(', ')}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-accent-blue">{formatDate(test.scheduled_for)}</div>
          <div className="text-xs text-secondary">{test.priority} priority</div>
        </div>
      </div>
      
      <div className="mb-4">
        <p className="text-sm text-secondary mb-2">{test.reason}</p>
        <div className="text-xs text-secondary">
          Original Score: <span className="font-medium text-primary">{test.original_score}%</span>
        </div>
      </div>
      
      <div className="flex space-x-2">
        <LiquidButton
          onClick={() => onStart(test)}
          variant="primary"
          size="sm"
          className="flex-1"
        >
          🚀 Start Review
        </LiquidButton>
        <LiquidButton
          onClick={() => onCancel(test.id)}
          variant="secondary"
          size="sm"
          className="px-3"
        >
          ✕
        </LiquidButton>
      </div>
    </LiquidCard>
  );
};

export default ScheduledTestsComponent;