import React, { useState } from 'react';
import { practiceAPI, setupAxiosAuth } from '../services/api';
import { subjects, questionTypes, difficultyLevels } from '../utils/constants';
import { LiquidCard, LiquidButton, LiquidSelect, LiquidProgress, LiquidNavItem } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const PracticeTestComponent = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState([]);
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [testStarted, setTestStarted] = useState(false);

  const handleTopicToggle = (topic) => {
    setSelectedTopics(prev => 
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const handleQuestionTypeToggle = (type) => {
    setSelectedQuestionTypes(prev => 
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const generatePracticeTest = async () => {
    if (!selectedSubject || selectedTopics.length === 0) {
      alert('Please select a subject and at least one topic.');
      return;
    }

    setIsGenerating(true);
    try {
      // Get token from localStorage and set up axios auth
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Authentication required. Please log in again.');
        onNavigate('auth');
        return;
      }

      // Ensure axios has the authorization header
      setupAxiosAuth(token);

      const response = await practiceAPI.generate({
        subject: selectedSubject,
        topics: selectedTopics,
        difficulty,
        question_count: numQuestions,
        question_types: selectedQuestionTypes.length > 0 ? selectedQuestionTypes : undefined
      });

      setCurrentQuestions(response.questions);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setTestStarted(true);
    } catch (error) {
      console.error('Error generating practice test:', error);
      
      // Handle specific error types
      if (error.response?.status === 401) {
        alert('Authentication expired. Please log in again.');
        onNavigate('auth');
      } else if (error.response?.status === 403) {
        alert('Access denied. Student account required.');
      } else {
        alert(`Failed to generate practice test: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAnswerSubmit = (questionId, answer) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < currentQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      submitTest();
    }
  };

  const submitTest = async () => {
    try {
      // Get token from localStorage and set up axios auth
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Authentication required. Please log in again.');
        onNavigate('auth');
        return;
      }

      // Ensure axios has the authorization header
      setupAxiosAuth(token);

      await practiceAPI.submit({
        questions: currentQuestions.map(q => q.id),
        student_answers: userAnswers,
        time_taken: 300 // placeholder
      });

      setShowResults(true);
    } catch (error) {
      console.error('Error submitting test:', error);
      
      // Handle specific error types
      if (error.response?.status === 401) {
        alert('Authentication expired. Please log in again.');
        onNavigate('auth');
      } else if (error.response?.status === 403) {
        alert('Access denied. Student account required.');
      } else {
        alert(`Failed to submit test: ${error.response?.data?.detail || error.message}`);
      }
    }
  };

  const resetTest = () => {
    setTestStarted(false);
    setCurrentQuestions([]);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
    setSelectedSubject('');
    setSelectedTopics([]);
    setSelectedQuestionTypes([]);
  };

  // Results View
  if (showResults) {
    const score = Object.keys(userAnswers).reduce((acc, qId) => {
      const question = currentQuestions.find(q => q.id === qId);
      if (question && question.correct_answer.toLowerCase() === userAnswers[qId].toLowerCase()) {
        return acc + 1;
      }
      return acc;
    }, 0);

    const percentage = ((score / currentQuestions.length) * 100).toFixed(1);

    return (
      <div className="min-h-screen relative overflow-hidden">
        <div className="animated-bg" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-green-400/30 to-blue-400/30 rounded-full blur-3xl animate-pulse" />
        
        <nav className="dynamic-nav">
          <LiquidNavItem onClick={() => onNavigate('student-dashboard')}>
            ← Dashboard
          </LiquidNavItem>
        </nav>

        <div className="relative z-10 pt-24 pb-12 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <LiquidCard className="p-12 bg-gradient-to-br from-white/10 to-white/5">
              <div className="text-8xl mb-8 animate-bounce">🎉</div>
              <h1 className="text-4xl font-bold text-gradient mb-4">Test Complete!</h1>
              <div className="text-6xl font-bold text-white mb-2">{percentage}%</div>
              <p className="text-xl text-white/70 mb-8">
                You scored {score} out of {currentQuestions.length} questions correctly
              </p>
              
              <LiquidProgress 
                value={score} 
                max={currentQuestions.length} 
                className="mb-8"
                showLabel={true}
                label="Your Performance"
              />
              
              <div className="flex justify-center gap-4">
                <LiquidButton onClick={resetTest} variant="secondary">
                  Take Another Test
                </LiquidButton>
                <LiquidButton onClick={() => onNavigate('student-dashboard')} variant="primary">
                  Back to Dashboard
                </LiquidButton>
              </div>
            </LiquidCard>
          </div>
        </div>
      </div>
    );
  }

  // Test Taking View
  if (testStarted && currentQuestions.length > 0) {
    const currentQuestion = currentQuestions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / currentQuestions.length) * 100;
    
    return (
      <div className="min-h-screen relative overflow-hidden">
        <div className="animated-bg" />
        
        <nav className="dynamic-nav">
          <div className="flex items-center gap-4">
            <span className="text-white/70 text-sm">
              Question {currentQuestionIndex + 1} of {currentQuestions.length}
            </span>
            <div className="w-px h-6 bg-white/20" />
            <span className="text-white/70 text-sm">
              {currentQuestion.question_type.toUpperCase()}
            </span>
          </div>
        </nav>

        <div className="relative z-10 pt-24 pb-12 px-6">
          <div className="max-w-4xl mx-auto">
            {/* Progress Bar */}
            <LiquidProgress 
              value={progress} 
              max={100} 
              className="mb-8"
              showLabel={true}
              label={`Progress: ${currentQuestionIndex + 1}/${currentQuestions.length}`}
            />

            <LiquidCard className="p-8">
              <h2 className="text-2xl font-semibold text-white mb-8">
                {currentQuestion.question_text}
              </h2>
              
              {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
                <div className="space-y-4 mb-8">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSubmit(currentQuestion.id, option)}
                      className={`
                        w-full text-left p-6 rounded-2xl transition-all duration-300
                        ${userAnswers[currentQuestion.id] === option
                          ? 'glass-strong border-white/40 text-white scale-105'
                          : 'glass border-white/20 text-white/80 hover:glass-strong hover:scale-102'
                        }
                      `}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`
                          w-6 h-6 rounded-full border-2 flex items-center justify-center
                          ${userAnswers[currentQuestion.id] === option
                            ? 'border-white bg-white/20'
                            : 'border-white/40'
                          }
                        `}>
                          {userAnswers[currentQuestion.id] === option && (
                            <div className="w-3 h-3 rounded-full bg-white" />
                          )}
                        </div>
                        <span className="text-lg">{option}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
              
              {currentQuestion.question_type !== 'mcq' && (
                <div className="mb-8">
                  <textarea
                    className="w-full p-6 glass rounded-2xl text-white placeholder-white/40 border border-white/20 focus:border-white/40 focus:glass-strong transition-all duration-300"
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
                  {currentQuestionIndex === currentQuestions.length - 1 ? 'Submit Test' : 'Next →'}
                </LiquidButton>
              </div>
            </LiquidCard>
          </div>
        </div>
      </div>
    );
  }

  // Setup View
  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="animated-bg" />
      <div className="absolute top-20 right-20 w-72 h-72 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-gradient-to-r from-green-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse delay-1000" />

      <nav className="dynamic-nav">
        <LiquidNavItem onClick={() => onNavigate('student-dashboard')}>
          ← Back to Dashboard
        </LiquidNavItem>
      </nav>

      <div className="relative z-10 pt-24 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-6xl mb-6">📝</div>
            <h1 className="text-4xl font-bold text-gradient mb-4">Practice Tests</h1>
            <p className="text-xl text-white/70">Create personalized tests to improve your understanding</p>
          </div>

          <LiquidCard className="p-8">
            {/* Subject Selection */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-white mb-4">Select Subject</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(subjects).map(([key, subject]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedSubject(key)}
                    className={`
                      p-6 rounded-2xl transition-all duration-300 text-center relative
                      ${selectedSubject === key
                        ? 'glass-strong border-2 border-green-400 text-white scale-105 ring-2 ring-green-400/50'
                        : 'glass border-white/20 text-white/80 hover:glass-strong hover:scale-102 hover:border-white/40'
                      }
                    `}
                  >
                    {selectedSubject === key && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center">
                        <span className="text-black text-sm font-bold">✓</span>
                      </div>
                    )}
                    <div className="text-3xl mb-2">{subject.icon}</div>
                    <div className="font-medium">{subject.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Topics Selection */}
            {selectedSubject && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Select Topics ({selectedTopics.length} selected)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {subjects[selectedSubject].topics.map((topic) => (
                    <button
                      key={topic}
                      onClick={() => handleTopicToggle(topic)}
                      className={`
                        p-4 rounded-xl transition-all duration-300 text-sm relative
                        ${selectedTopics.includes(topic)
                          ? 'glass-strong border-2 border-blue-400 text-white bg-blue-400/10'
                          : 'glass border-white/20 text-white/70 hover:text-white hover:glass-strong hover:border-white/40'
                        }
                      `}
                    >
                      {selectedTopics.includes(topic) && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center">
                          <span className="text-black text-xs font-bold">✓</span>
                        </div>
                      )}
                      <div className={`flex items-center gap-2 ${selectedTopics.includes(topic) ? 'font-semibold' : ''}`}>
                        <div className={`w-3 h-3 rounded border-2 flex items-center justify-center ${
                          selectedTopics.includes(topic) 
                            ? 'border-blue-400 bg-blue-400' 
                            : 'border-white/40'
                        }`}>
                          {selectedTopics.includes(topic) && (
                            <span className="text-black text-xs">✓</span>
                          )}
                        </div>
                        {topic}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Question Types Selection */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-white mb-4">
                Question Types ({selectedQuestionTypes.length > 0 ? selectedQuestionTypes.length + ' selected' : 'All types'})
              </h3>
              <p className="text-white/60 text-sm mb-4">Leave unselected to include all question types</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {questionTypes.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => handleQuestionTypeToggle(type.value)}
                    className={`
                      p-6 text-left rounded-2xl transition-all duration-300 relative
                      ${selectedQuestionTypes.includes(type.value)
                        ? 'glass-strong border-2 border-purple-400 bg-purple-400/10'
                        : 'glass border-white/20 hover:glass-strong hover:border-white/40'
                      }
                    `}
                  >
                    {selectedQuestionTypes.includes(type.value) && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-purple-400 rounded-full flex items-center justify-center">
                        <span className="text-black text-sm font-bold">✓</span>
                      </div>
                    )}
                    <div className="flex items-start gap-3">
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 ${
                        selectedQuestionTypes.includes(type.value) 
                          ? 'border-purple-400 bg-purple-400' 
                          : 'border-white/40'
                      }`}>
                        {selectedQuestionTypes.includes(type.value) && (
                          <span className="text-black text-xs font-bold">✓</span>
                        )}
                      </div>
                      <div>
                        <div className={`font-semibold text-white text-lg mb-2 ${
                          selectedQuestionTypes.includes(type.value) ? 'text-purple-200' : ''
                        }`}>
                          {type.label}
                        </div>
                        <div className="text-white/60 text-sm">{type.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Test Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Number of Questions</h4>
                <div className="grid grid-cols-2 gap-3">
                  {[5, 10, 15, 20].map(num => (
                    <button
                      key={num}
                      onClick={() => setNumQuestions(num)}
                      className={`
                        p-4 rounded-xl transition-all duration-300 relative
                        ${numQuestions === num
                          ? 'glass-strong border-2 border-yellow-400 text-white bg-yellow-400/10'
                          : 'glass border-white/20 text-white/70 hover:text-white hover:glass-strong hover:border-white/40'
                        }
                      `}
                    >
                      {numQuestions === num && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-400 rounded-full flex items-center justify-center">
                          <span className="text-black text-xs font-bold">✓</span>
                        </div>
                      )}
                      <div className={`flex items-center gap-2 justify-center ${
                        numQuestions === num ? 'font-semibold' : ''
                      }`}>
                        <div className={`w-3 h-3 rounded-full ${
                          numQuestions === num ? 'bg-yellow-400' : 'border-2 border-white/40'
                        }`}></div>
                        {num} Questions
                      </div>
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Difficulty Level</h4>
                <div className="grid grid-cols-2 gap-3">
                  {difficultyLevels.map(level => (
                    <button
                      key={level.value}
                      onClick={() => setDifficulty(level.value)}
                      className={`
                        p-4 rounded-xl transition-all duration-300 relative
                        ${difficulty === level.value
                          ? 'glass-strong border-2 border-red-400 text-white bg-red-400/10'
                          : 'glass border-white/20 text-white/70 hover:text-white hover:glass-strong hover:border-white/40'
                        }
                      `}
                    >
                      {difficulty === level.value && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-400 rounded-full flex items-center justify-center">
                          <span className="text-black text-xs font-bold">✓</span>
                        </div>
                      )}
                      <div className={`flex items-center gap-2 justify-center ${
                        difficulty === level.value ? 'font-semibold' : ''
                      }`}>
                        <div className={`w-3 h-3 rounded-full ${
                          difficulty === level.value ? 'bg-red-400' : 'border-2 border-white/40'
                        }`}></div>
                        {level.label}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Generate Test Button */}
            <div className="text-center">
              <LiquidButton
                onClick={generatePracticeTest}
                disabled={!selectedSubject || selectedTopics.length === 0 || isGenerating}
                variant="primary"
                size="lg"
                className="px-12 py-4"
              >
                {isGenerating ? (
                  <div className="flex items-center gap-3">
                    <div className="loading-dots">
                      <div className="loading-dot bg-white"></div>
                      <div className="loading-dot bg-white"></div>
                      <div className="loading-dot bg-white"></div>
                    </div>
                    <span>Generating Test...</span>
                  </div>
                ) : (
                  '🚀 Start Practice Test'
                )}
              </LiquidButton>
            </div>
          </LiquidCard>
        </div>
      </div>
    </div>
  );
};

export default PracticeTestComponent;