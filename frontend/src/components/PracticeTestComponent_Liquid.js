import React, { useState } from 'react';
import { practiceAPI, setupAxiosAuth } from '../services/api';
import { subjects, questionTypes, difficultyLevels, gradeLevels } from '../utils/constants';
import { LiquidCard, LiquidButton, LiquidSelect, LiquidProgress, LiquidNavItem } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const PracticeTestComponent = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('10th'); // Default to 10th grade
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState([]);
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [testStarted, setTestStarted] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [detailedResults, setDetailedResults] = useState([]);
  const [showDetailedResults, setShowDetailedResults] = useState(false);

  const handleUnitToggle = (unit) => {
    setSelectedUnits(prev => 
      prev.includes(unit)
        ? prev.filter(u => u !== unit)
        : [...prev, unit]
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
    if (!selectedSubject || !selectedGrade || selectedUnits.length === 0) {
      alert('Please select a subject, grade, and at least one NCERT unit.');
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
        topics: selectedUnits, // Send selected units as topics for backend compatibility
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

      const results = await practiceAPI.submit({
        questions: currentQuestions.map(q => q.id),
        student_answers: userAnswers,
        subject: selectedSubject, // Include subject for proper data storage
        time_taken: 300 // placeholder
      });

      setTestResults(results);
      setDetailedResults(results.detailed_results || []);
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
    setSelectedUnits([]);
    setSelectedQuestionTypes([]);
  };

  // Results View
  if (showResults && testResults) {
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
          <div className="max-w-6xl mx-auto">
            
            {!showDetailedResults ? (
              // Summary Results View
              <div className="text-center mb-8">
                <LiquidCard className="p-12 bg-gradient-to-br from-white/10 to-white/5">
                  <div className="text-8xl mb-8 animate-bounce">🎉</div>
                  <h1 className="text-4xl font-bold text-gradient mb-4">Test Complete!</h1>
                  <div className="text-6xl font-bold text-white mb-2">{testResults.score}%</div>
                  <p className="text-xl text-white/70 mb-4">
                    You scored {testResults.correct_answers} out of {testResults.total_questions} questions correctly
                  </p>
                  <div className="text-lg text-white/60 mb-8">
                    Grade: <span className="font-bold text-white">{testResults.grade}</span> • 
                    XP Gained: <span className="font-bold text-green-400">+{testResults.xp_gained}</span>
                  </div>
                  
                  {/* Smart Scheduling Message */}
                  <div className="bg-glass/50 rounded-2xl p-6 mb-8 border border-accent-blue/30">
                    <h3 className="text-lg font-semibold text-accent-blue mb-3 flex items-center">
                      🤖 Smart Review Scheduled
                    </h3>
                    <p className="text-white/80 text-sm">
                      Based on your {testResults.score}% score, your next review has been intelligently scheduled using spaced repetition principles. 
                      {testResults.score >= 90 
                        ? " Excellent performance! Your review is scheduled for optimal long-term retention."
                        : testResults.score >= 70 
                        ? " Good work! A medium-term review has been scheduled to strengthen your understanding."
                        : " Your review is scheduled soon to help reinforce these concepts."
                      }
                    </p>
                    <div className="mt-3">
                      <LiquidButton 
                        onClick={() => onNavigate('scheduled-tests')} 
                        variant="secondary"
                        size="sm"
                      >
                        📅 View Review Schedule
                      </LiquidButton>
                    </div>
                  </div>
                  
                  <LiquidProgress 
                    value={testResults.correct_answers} 
                    max={testResults.total_questions} 
                    className="mb-8"
                    showLabel={true}
                    label="Your Performance"
                  />
                  
                  <div className="flex justify-center gap-4 mb-6">
                    <LiquidButton 
                      onClick={() => setShowDetailedResults(true)} 
                      variant="primary"
                      className="px-8"
                    >
                      📊 View Detailed Results
                    </LiquidButton>
                  </div>
                  
                  <div className="flex justify-center gap-4">
                    <LiquidButton onClick={resetTest} variant="secondary">
                      Take Another Test
                    </LiquidButton>
                    <LiquidButton onClick={() => onNavigate('progress')} variant="primary">
                      View Progress
                    </LiquidButton>
                  </div>
                </LiquidCard>
              </div>
            ) : (
              // Detailed Results View
              <div>
                <div className="flex items-center justify-between mb-8">
                  <h1 className="text-3xl font-bold text-gradient">Detailed Results</h1>
                  <LiquidButton 
                    onClick={() => setShowDetailedResults(false)} 
                    variant="secondary"
                  >
                    ← Back to Summary
                  </LiquidButton>
                </div>

                {/* Summary Card */}
                <LiquidCard className="p-6 mb-8 bg-gradient-to-r from-white/10 to-white/5">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
                    <div>
                      <div className="text-3xl font-bold text-white">{testResults.score}%</div>
                      <div className="text-sm text-white/60">Overall Score</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-green-400">{testResults.correct_answers}</div>
                      <div className="text-sm text-white/60">Correct</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-red-400">{testResults.total_questions - testResults.correct_answers}</div>
                      <div className="text-sm text-white/60">Incorrect</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-blue-400">{testResults.grade}</div>
                      <div className="text-sm text-white/60">Grade</div>
                    </div>
                  </div>
                </LiquidCard>

                {/* Question by Question Results */}
                <div className="space-y-6">
                  {detailedResults.map((result, index) => (
                    <LiquidCard 
                      key={result.question_id} 
                      className={`p-6 border-l-4 ${
                        result.is_correct 
                          ? 'border-green-400 bg-green-500/5' 
                          : 'border-red-400 bg-red-500/5'
                      }`}
                    >
                      {/* Question Header */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                            result.is_correct 
                              ? 'bg-green-400 text-green-900' 
                              : 'bg-red-400 text-red-900'
                          }`}>
                            {result.is_correct ? '✓' : '✗'}
                          </div>
                          <span className="text-lg font-semibold text-white">Question {index + 1}</span>
                          <span className="text-sm text-white/60 bg-white/10 px-2 py-1 rounded capitalize">
                            {result.topic}
                          </span>
                        </div>
                        <div className={`text-sm font-medium ${
                          result.is_correct ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {result.is_correct ? 'Correct' : 'Incorrect'}
                        </div>
                      </div>

                      {/* Question Text */}
                      <div className="mb-4">
                        <h3 className="text-lg text-white mb-3">{result.question_text}</h3>
                        
                        {/* MCQ Options */}
                        {result.question_type === 'mcq' && result.options && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
                            {result.options.map((option, optIndex) => (
                              <div 
                                key={optIndex}
                                className={`p-3 rounded-lg border text-sm ${
                                  option === result.correct_answer
                                    ? 'border-green-400 bg-green-500/10 text-green-300'
                                    : option === result.student_answer && !result.is_correct
                                    ? 'border-red-400 bg-red-500/10 text-red-300'
                                    : 'border-white/20 text-white/70'
                                }`}
                              >
                                <span className="font-medium">{String.fromCharCode(65 + optIndex)}.</span> {option}
                                {option === result.correct_answer && (
                                  <span className="ml-2 text-green-400">✓ Correct</span>
                                )}
                                {option === result.student_answer && !result.is_correct && (
                                  <span className="ml-2 text-red-400">Your Answer</span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Answers */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-white/60 mb-1">Your Answer:</div>
                          <div className={`font-medium ${
                            result.is_correct ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {result.student_answer || 'No answer provided'}
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-white/60 mb-1">Correct Answer:</div>
                          <div className="font-medium text-green-400">
                            {result.correct_answer}
                          </div>
                        </div>
                      </div>

                      {/* Enhanced AI Feedback */}
                      <div className="space-y-4">
                        {/* Main Explanation */}
                        <div className="bg-white/5 rounded-lg p-4">
                          <div className="text-sm text-white/60 mb-2">💡 Explanation:</div>
                          <div className="text-white/90 text-sm leading-relaxed">
                            {result.explanation}
                          </div>
                        </div>

                        {/* AI Feedback (for non-MCQ questions) */}
                        {result.question_type !== 'mcq' && result.feedback && (
                          <div className="bg-blue-500/10 border border-blue-400/20 rounded-lg p-4">
                            <div className="text-sm text-blue-300 mb-2">🤖 AI Teacher Feedback:</div>
                            <div className="text-white/90 text-sm leading-relaxed mb-3">
                              {result.feedback}
                            </div>
                            
                            {/* Score Percentage for non-MCQ */}
                            {result.score_percentage !== undefined && result.question_type !== 'mcq' && (
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-xs text-blue-300">Understanding Score:</span>
                                <div className="bg-blue-400/20 px-2 py-1 rounded text-xs font-medium text-blue-200">
                                  {result.score_percentage}%
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Key Concepts Identified */}
                        {result.key_concepts_identified && result.key_concepts_identified.length > 0 && (
                          <div className="bg-green-500/10 border border-green-400/20 rounded-lg p-4">
                            <div className="text-sm text-green-300 mb-2">✅ Concepts You Demonstrated:</div>
                            <div className="flex flex-wrap gap-2">
                              {result.key_concepts_identified.map((concept, idx) => (
                                <span key={idx} className="bg-green-400/20 text-green-200 px-2 py-1 rounded-full text-xs">
                                  {concept}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Areas for Improvement */}
                        {result.areas_for_improvement && result.areas_for_improvement.length > 0 && (
                          <div className="bg-orange-500/10 border border-orange-400/20 rounded-lg p-4">
                            <div className="text-sm text-orange-300 mb-2">📚 Areas to Focus On:</div>
                            <ul className="space-y-1">
                              {result.areas_for_improvement.map((area, idx) => (
                                <li key={idx} className="text-orange-200 text-xs flex items-start gap-2">
                                  <span className="text-orange-400">•</span>
                                  {area}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </LiquidCard>
                  ))}
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center gap-4 mt-8">
                  <LiquidButton onClick={resetTest} variant="secondary">
                    Take Another Test
                  </LiquidButton>
                  <LiquidButton onClick={() => onNavigate('progress')} variant="primary">
                    View Progress Tracker
                  </LiquidButton>
                </div>
              </div>
            )}
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
                        w-full text-left p-6 rounded-2xl transition-all duration-300 relative
                        ${userAnswers[currentQuestion.id] === option
                          ? 'glass-strong border-2 border-green-400 text-white scale-102 bg-green-400/10 ring-2 ring-green-400/30'
                          : 'glass border-white/20 text-white/80 hover:glass-strong hover:scale-101 hover:border-white/40'
                        }
                      `}
                    >
                      {userAnswers[currentQuestion.id] === option && (
                        <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                          <span className="text-black font-bold">✓</span>
                        </div>
                      )}
                      <div className="flex items-center gap-4">
                        <div className={`
                          w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300
                          ${userAnswers[currentQuestion.id] === option
                            ? 'border-green-400 bg-green-400 scale-110'
                            : 'border-white/40 hover:border-white/60'
                          }
                        `}>
                          {userAnswers[currentQuestion.id] === option && (
                            <div className="w-3 h-3 rounded-full bg-white" />
                          )}
                        </div>
                        <span className={`text-lg ${userAnswers[currentQuestion.id] === option ? 'font-semibold' : ''}`}>
                          {String.fromCharCode(65 + index)}. {option}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
              
              {currentQuestion.question_type !== 'mcq' && (
                <div className="mb-8">
                  <textarea
                    className="w-full p-6 glass rounded-2xl text-primary placeholder-secondary border border-primary/20 focus:border-accent-blue/40 focus:glass-strong transition-all duration-300 bg-glass/80"
                    style={{
                      color: '#e2e8f0', // Ensure text is always light colored
                      backgroundColor: 'rgba(255, 255, 255, 0.05)' // Slight background to improve contrast
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
                    onClick={() => {
                      setSelectedSubject(key);
                      setSelectedUnits([]); // Reset units when subject changes
                    }}
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

            {/* Grade Selection */}
            {selectedSubject && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-white mb-4">Select Grade</h3>
                <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
                  {gradeLevels.map((grade) => (
                    <button
                      key={grade}
                      onClick={() => {
                        setSelectedGrade(grade);
                        setSelectedUnits([]); // Reset units when grade changes
                      }}
                      className={`
                        p-4 rounded-xl transition-all duration-300 text-sm relative
                        ${selectedGrade === grade
                          ? 'glass-strong border-2 border-purple-400 text-white bg-purple-400/10'
                          : 'glass border-white/20 text-white/70 hover:text-white hover:glass-strong hover:border-white/40'
                        }
                      `}
                    >
                      {selectedGrade === grade && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-purple-400 rounded-full flex items-center justify-center">
                          <span className="text-black text-xs font-bold">✓</span>
                        </div>
                      )}
                      <div className={`text-center ${selectedGrade === grade ? 'font-semibold' : ''}`}>
                        {grade}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* NCERT Units Selection */}
            {selectedSubject && selectedGrade && subjects[selectedSubject].units[selectedGrade] && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Select NCERT Units ({selectedUnits.length} selected)
                </h3>
                <p className="text-white/60 text-sm mb-4">
                  Choose units from {subjects[selectedSubject].name} - Class {selectedGrade}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {subjects[selectedSubject].units[selectedGrade].map((unit) => (
                    <button
                      key={unit}
                      onClick={() => handleUnitToggle(unit)}
                      className={`
                        p-4 rounded-xl transition-all duration-300 text-sm relative text-left
                        ${selectedUnits.includes(unit)
                          ? 'glass-strong border-2 border-blue-400 text-white bg-blue-400/10'
                          : 'glass border-white/20 text-white/70 hover:text-white hover:glass-strong hover:border-white/40'
                        }
                      `}
                    >
                      {selectedUnits.includes(unit) && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center">
                          <span className="text-black text-xs font-bold">✓</span>
                        </div>
                      )}
                      <div className={`flex items-start gap-3 ${selectedUnits.includes(unit) ? 'font-semibold' : ''}`}>
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center mt-0.5 flex-shrink-0 ${
                          selectedUnits.includes(unit) 
                            ? 'border-blue-400 bg-blue-400' 
                            : 'border-white/40'
                        }`}>
                          {selectedUnits.includes(unit) && (
                            <span className="text-black text-xs font-bold">✓</span>
                          )}
                        </div>
                        <span className="leading-5">{unit}</span>
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
                disabled={!selectedSubject || selectedUnits.length === 0 || isGenerating}
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