import React, { useState } from 'react';
import { practiceAPI, setupAxiosAuth } from '../services/api';
import { subjects, questionTypes, difficultyLevels, gradeLevels } from '../utils/constants';
import NavigationBar_Modern from './NavigationBar_Modern';
import { 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernSelect,
  ModernProgress,
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernGrid,
  ModernSpinner,
  ModernBadge
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

// Subject Icon Component
const SubjectIcon = ({ iconType, className = "w-8 h-8" }) => {
  const iconPaths = {
    math: (
      <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8 12H9.5v-2H11v2zm0-4H9.5V9H11v2zm4 4h-1.5v-2H15v2zm0-4h-1.5V9H15v2z"/>
      </svg>
    ),
    physics: (
      <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
    ),
    chemistry: (
      <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M9 2v6l-2 2v2h10v-2l-2-2V2H9zm2 2h2v5.5l1.5 1.5H9.5L11 9.5V4z"/>
        <path d="M6 14h12l-1 7H7l-1-7z"/>
      </svg>
    ),
    biology: (
      <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.84c.48.17.98.26 1.34.26C14 19.42 21 14 21 8c0-1.54-.87-2.93-2.16-3.53-.51-.24-1.07-.47-1.66-.47-.59 0-1.15.23-1.66.47C14.87 5.07 14 6.46 14 8s.87 2.93 2.18 3.53c.51.24 1.07.47 1.66.47s1.15-.23 1.66-.47C20.13 10.93 21 9.54 21 8z"/>
      </svg>
    ),
    english: (
      <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm0 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z"/>
      </svg>
    )
  };

  return iconPaths[iconType] || iconPaths.math;
};

const PracticeTestComponent_Modern = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('10th');
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
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Authentication required. Please log in again.');
        onNavigate('auth');
        return;
      }

      setupAxiosAuth(token);

      const response = await practiceAPI.generate({
        subject: selectedSubject,
        topics: selectedUnits,
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
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Authentication required. Please log in again.');
        onNavigate('auth');
        return;
      }

      setupAxiosAuth(token);

      const results = await practiceAPI.submit({
        questions: currentQuestions.map(q => q.id),
        student_answers: userAnswers,
        subject: selectedSubject,
        time_taken: 300
      });

      setTestResults(results);
      setDetailedResults(results.detailed_results || []);
      setShowResults(true);
    } catch (error) {
      console.error('Error submitting test:', error);
      
      if (error.response?.status === 401) {
        alert('Authentication expired. Please log in again.');
        onNavigate('auth');
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
    setSelectedGrade('10th');
    setSelectedUnits([]);
    setSelectedQuestionTypes([]);
  };

  // Results View
  if (showResults && testResults) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <ModernContainer>
            <div className="flex items-center justify-between py-4">
              <ModernButton variant="ghost" onClick={() => onNavigate('student-dashboard')}>
                ← Back to Dashboard
              </ModernButton>
              <ModernHeading level={4}>Test Results</ModernHeading>
              <div></div>
            </div>
          </ModernContainer>
        </header>

        <ModernContainer className="py-8">
          {!showDetailedResults ? (
            // Summary Results View
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <ModernHeading level={1} className="text-4xl font-bold mb-4">
                  Test Complete!
                </ModernHeading>
                <div className="text-6xl font-bold text-indigo-600 mb-4">
                  {testResults.score}%
                </div>
                <ModernText variant="body-large" className="text-gray-600 mb-4">
                  You scored {testResults.correct_answers} out of {testResults.total_questions} questions correctly
                </ModernText>
                <div className="flex items-center justify-center gap-4 mb-8">
                  <ModernBadge variant="primary" className="text-lg px-4 py-2">
                    Grade: {testResults.grade}
                  </ModernBadge>
                  <ModernBadge variant="success" className="text-lg px-4 py-2">
                    XP Gained: +{testResults.xp_gained}
                  </ModernBadge>
                </div>
              </div>

              <ModernGrid cols={1} className="max-w-2xl mx-auto mb-8">
                <ModernCard>
                  <ModernCardHeader>
                    <ModernHeading level={4} className="text-indigo-600">
                      Smart Review Scheduled
                    </ModernHeading>
                  </ModernCardHeader>
                  <ModernCardBody>
                    <ModernText className="mb-4">
                      Based on your {testResults.score}% score, your next review has been intelligently scheduled using spaced repetition principles.
                      {testResults.score >= 90 
                        ? " Excellent performance! Your review is scheduled for optimal long-term retention."
                        : testResults.score >= 70 
                        ? " Good work! A medium-term review has been scheduled to strengthen your understanding."
                        : " Your review is scheduled soon to help reinforce these concepts."
                      }
                    </ModernText>
                    <ModernButton 
                      variant="outline"
                      onClick={() => onNavigate('scheduled-tests')}
                    >
                      View Review Schedule
                    </ModernButton>
                  </ModernCardBody>
                </ModernCard>
              </ModernGrid>

              <ModernProgress 
                value={testResults.correct_answers} 
                max={testResults.total_questions} 
                label="Your Performance"
                className="max-w-2xl mx-auto mb-8"
              />

              <div className="flex justify-center gap-4 mb-8">
                <ModernButton 
                  variant="outline"
                  onClick={() => setShowDetailedResults(true)}
                >
                  📊 View Detailed Results
                </ModernButton>
              </div>

              <div className="flex justify-center gap-4">
                <ModernButton variant="secondary" onClick={resetTest}>
                  Take Another Test
                </ModernButton>
                <ModernButton variant="primary" onClick={() => onNavigate('progress')}>
                  View Progress
                </ModernButton>
              </div>
            </div>
          ) : (
            // Detailed Results View
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <ModernHeading level={2}>Detailed Results</ModernHeading>
                <ModernButton 
                  variant="outline"
                  onClick={() => setShowDetailedResults(false)}
                >
                  ← Back to Summary
                </ModernButton>
              </div>

              {/* Summary Stats */}
              <ModernGrid cols={4} className="mb-8">
                <ModernCard>
                  <ModernCardBody>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-indigo-600">{testResults.score}%</div>
                      <ModernText variant="body-small" className="text-gray-500">Overall Score</ModernText>
                    </div>
                  </ModernCardBody>
                </ModernCard>
                <ModernCard>
                  <ModernCardBody>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-500">{testResults.correct_answers}</div>
                      <ModernText variant="body-small" className="text-gray-500">Correct</ModernText>
                    </div>
                  </ModernCardBody>
                </ModernCard>
                <ModernCard>
                  <ModernCardBody>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-red-500">{testResults.total_questions - testResults.correct_answers}</div>
                      <ModernText variant="body-small" className="text-gray-500">Incorrect</ModernText>
                    </div>
                  </ModernCardBody>
                </ModernCard>
                <ModernCard>
                  <ModernCardBody>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">{testResults.grade}</div>
                      <ModernText variant="body-small" className="text-gray-500">Grade</ModernText>
                    </div>
                  </ModernCardBody>
                </ModernCard>
              </ModernGrid>

              {/* Question by Question Results */}
              <div className="space-y-6">
                {detailedResults.map((result, index) => (
                  <ModernCard 
                    key={result.question_id}
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
                          <ModernBadge variant="secondary">{result.topic}</ModernBadge>
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
                      <ModernAlert variant="info">
                        <div>
                          <ModernText variant="body-small" className="font-medium mb-2">💡 Explanation:</ModernText>
                          <ModernText variant="body-small">
                            {result.explanation}
                          </ModernText>
                        </div>
                      </ModernAlert>
                    </ModernCardBody>
                  </ModernCard>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-center gap-4 mt-8">
                <ModernButton variant="secondary" onClick={resetTest}>
                  Take Another Test
                </ModernButton>
                <ModernButton variant="primary" onClick={() => onNavigate('progress')}>
                  View Progress Tracker
                </ModernButton>
              </div>
            </div>
          )}
        </ModernContainer>
      </div>
    );
  }

  // Test Taking View
  if (testStarted && currentQuestions.length > 0) {
    const currentQuestion = currentQuestions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / currentQuestions.length) * 100;
    
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <ModernContainer>
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center gap-4">
                <ModernText variant="body-small" className="text-gray-500">
                  Question {currentQuestionIndex + 1} of {currentQuestions.length}
                </ModernText>
                <div className="w-px h-6 bg-gray-300"></div>
                <ModernBadge variant="secondary">
                  {currentQuestion.question_type.toUpperCase()}
                </ModernBadge>
              </div>
            </div>
          </ModernContainer>
        </header>

        <ModernContainer className="py-8 max-w-4xl">
          <ModernProgress 
            value={progress} 
            max={100} 
            label={`Progress: ${currentQuestionIndex + 1}/${currentQuestions.length}`}
            className="mb-8"
          />

          <ModernCard>
            <ModernCardBody>
              <ModernHeading level={3} className="mb-8">
                {currentQuestion.question_text}
              </ModernHeading>
              
              {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
                <div className="space-y-4 mb-8">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSubmit(currentQuestion.id, option)}
                      className={`w-full text-left p-6 rounded-xl border-2 transition-all duration-300 ${
                        userAnswers[currentQuestion.id] === option
                          ? 'border-indigo-500 bg-indigo-50 text-indigo-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          userAnswers[currentQuestion.id] === option
                            ? 'border-indigo-500 bg-indigo-500'
                            : 'border-gray-300'
                        }`}>
                          {userAnswers[currentQuestion.id] === option && (
                            <div className="w-3 h-3 rounded-full bg-white" />
                          )}
                        </div>
                        <span className="text-lg">
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
                    className="w-full p-6 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors duration-300"
                    rows="6"
                    placeholder="Enter your answer here..."
                    value={userAnswers[currentQuestion.id] || ''}
                    onChange={(e) => handleAnswerSubmit(currentQuestion.id, e.target.value)}
                  />
                </div>
              )}
              
              <div className="flex justify-between">
                <ModernButton
                  variant="outline"
                  onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                  disabled={currentQuestionIndex === 0}
                >
                  ← Previous
                </ModernButton>
                <ModernButton
                  variant="primary"
                  onClick={nextQuestion}
                  disabled={!userAnswers[currentQuestion.id]}
                >
                  {currentQuestionIndex === currentQuestions.length - 1 ? 'Submit Test' : 'Next →'}
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>
        </ModernContainer>
      </div>
    );
  }

  // Setup View
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Modern Navigation */}
      <NavigationBar_Modern 
        user={student}
        currentPage="practice-tests"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8 max-w-4xl">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <ModernHeading level={1} className="mb-4">
            NCERT Practice Tests
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600">
            Create tests based on NCERT curriculum units
          </ModernText>
        </div>

        <ModernCard>
          <ModernCardBody>
            {/* Subject Selection */}
            <div className="mb-8">
              <ModernHeading level={4} className="mb-4">Select Subject</ModernHeading>
              <ModernGrid cols={5}>
                {Object.entries(subjects).map(([key, subject]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedSubject(key);
                      setSelectedUnits([]);
                    }}
                    className={`p-6 rounded-xl border-2 transition-all duration-300 text-center ${
                      selectedSubject === key
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-900'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="mb-3 flex justify-center">
                      <SubjectIcon 
                        iconType={subject.icon} 
                        className={`w-8 h-8 ${
                          selectedSubject === key ? 'text-indigo-600' : 'text-gray-400'
                        }`}
                      />
                    </div>
                    <div className="font-medium text-sm">{subject.name}</div>
                  </button>
                ))}
              </ModernGrid>
            </div>

            {/* Grade Selection */}
            {selectedSubject && (
              <div className="mb-8">
                <ModernHeading level={4} className="mb-4">Select Grade</ModernHeading>
                <ModernGrid cols={7}>
                  {gradeLevels.map((grade) => (
                    <button
                      key={grade}
                      onClick={() => {
                        setSelectedGrade(grade);
                        setSelectedUnits([]);
                      }}
                      className={`p-4 rounded-lg border-2 transition-all duration-300 text-center ${
                        selectedGrade === grade
                          ? 'border-purple-500 bg-purple-50 text-purple-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{grade}</div>
                    </button>
                  ))}
                </ModernGrid>
              </div>
            )}

            {/* NCERT Units Selection */}
            {selectedSubject && selectedGrade && subjects[selectedSubject].units[selectedGrade] && (
              <div className="mb-8">
                <ModernHeading level={4} className="mb-4">
                  Select NCERT Units ({selectedUnits.length} selected)
                </ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 mb-4">
                  Choose units from {subjects[selectedSubject].name} - Class {selectedGrade}
                </ModernText>
                <ModernGrid cols={2}>
                  {subjects[selectedSubject].units[selectedGrade].map((unit) => (
                    <button
                      key={unit}
                      onClick={() => handleUnitToggle(unit)}
                      className={`p-4 rounded-lg border-2 transition-all duration-300 text-left ${
                        selectedUnits.includes(unit)
                          ? 'border-blue-500 bg-blue-50 text-blue-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 flex-shrink-0 ${
                          selectedUnits.includes(unit) 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-gray-300'
                        }`}>
                          {selectedUnits.includes(unit) && (
                            <span className="text-white text-xs font-bold">✓</span>
                          )}
                        </div>
                        <span className="leading-5 font-medium">{unit}</span>
                      </div>
                    </button>
                  ))}
                </ModernGrid>
              </div>
            )}

            {/* Test Configuration */}
            <ModernGrid cols={2} className="mb-8">
              <div>
                <ModernHeading level={4} className="mb-4">Number of Questions</ModernHeading>
                <ModernGrid cols={2}>
                  {[5, 10, 15, 20].map(num => (
                    <button
                      key={num}
                      onClick={() => setNumQuestions(num)}
                      className={`p-4 rounded-lg border-2 transition-all duration-300 text-center ${
                        numQuestions === num
                          ? 'border-yellow-500 bg-yellow-50 text-yellow-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{num} Questions</div>
                    </button>
                  ))}
                </ModernGrid>
              </div>
              
              <div>
                <ModernHeading level={4} className="mb-4">Difficulty Level</ModernHeading>
                <ModernGrid cols={2}>
                  {difficultyLevels.map(level => (
                    <button
                      key={level.value}
                      onClick={() => setDifficulty(level.value)}
                      className={`p-4 rounded-lg border-2 transition-all duration-300 text-center ${
                        difficulty === level.value
                          ? 'border-red-500 bg-red-50 text-red-900'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{level.label}</div>
                    </button>
                  ))}
                </ModernGrid>
              </div>
            </ModernGrid>

            {/* Generate Test Button */}
            <div className="text-center">
              <ModernButton
                variant="primary"
                className="px-12 py-4 text-lg"
                onClick={generatePracticeTest}
                disabled={!selectedSubject || !selectedGrade || selectedUnits.length === 0 || isGenerating}
              >
                {isGenerating ? (
                  <div className="flex items-center gap-3">
                    <ModernSpinner size="sm" />
                    <span>Generating Test...</span>
                  </div>
                ) : (
                  'Start Practice Test'
                )}
              </ModernButton>
            </div>
          </ModernCardBody>
        </ModernCard>
      </ModernContainer>
    </div>
  );
};

export default PracticeTestComponent_Modern;