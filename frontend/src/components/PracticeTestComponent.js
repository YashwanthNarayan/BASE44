import React, { useState } from 'react';
import { practiceAPI } from '../services/api';
import { subjects, questionTypes, difficultyLevels } from '../utils/constants';

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
      alert('Failed to generate practice test. Please try again.');
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
      await practiceAPI.submit({
        questions: currentQuestions.map(q => q.id),
        student_answers: userAnswers,
        time_taken: 300 // placeholder
      });

      setShowResults(true);
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Failed to submit test. Please try again.');
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

  if (showResults) {
    const score = Object.keys(userAnswers).reduce((acc, qId) => {
      const question = currentQuestions.find(q => q.id === qId);
      if (question && question.correct_answer.toLowerCase() === userAnswers[qId].toLowerCase()) {
        return acc + 1;
      }
      return acc;
    }, 0);

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🎉</div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Complete!</h1>
              <p className="text-lg text-gray-600">
                You scored {score} out of {currentQuestions.length} ({((score/currentQuestions.length)*100).toFixed(1)}%)
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={resetTest}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Take Another Test
              </button>
              <button
                onClick={() => onNavigate('student-dashboard')}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (testStarted && currentQuestions.length > 0) {
    const currentQuestion = currentQuestions[currentQuestionIndex];
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                Question {currentQuestionIndex + 1} of {currentQuestions.length}
              </h1>
              <div className="text-sm text-gray-500">
                {currentQuestion.question_type.toUpperCase()}
              </div>
            </div>
            
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {currentQuestion.question_text}
              </h2>
              
              {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
                <div className="space-y-3">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSubmit(currentQuestion.id, option)}
                      className={`w-full text-left p-4 rounded-lg border transition-colors ${
                        userAnswers[currentQuestion.id] === option
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
              
              {currentQuestion.question_type !== 'mcq' && (
                <textarea
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  rows="4"
                  placeholder="Enter your answer here..."
                  value={userAnswers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerSubmit(currentQuestion.id, e.target.value)}
                />
              )}
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                disabled={currentQuestionIndex === 0}
                className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={nextQuestion}
                disabled={!userAnswers[currentQuestion.id]}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {currentQuestionIndex === currentQuestions.length - 1 ? 'Submit Test' : 'Next Question'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">📝 Practice Tests</h1>
          <p className="text-gray-600">Create personalized tests to improve your understanding</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Subject Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Subject</label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Choose a subject...</option>
              {Object.entries(subjects).map(([key, subject]) => (
                <option key={key} value={key}>{subject.name}</option>
              ))}
            </select>
          </div>

          {/* Topics Selection */}
          {selectedSubject && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Topics ({selectedTopics.length} selected)
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {subjects[selectedSubject].topics.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => handleTopicToggle(topic)}
                    className={`p-3 text-sm rounded-lg border transition-colors ${
                      selectedTopics.includes(topic)
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Question Types Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Types ({selectedQuestionTypes.length > 0 ? selectedQuestionTypes.length + ' selected' : 'All types'})
            </label>
            <p className="text-sm text-gray-500 mb-3">Leave unselected to include all question types</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {questionTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleQuestionTypeToggle(type.value)}
                  className={`p-4 text-left rounded-lg border transition-colors ${
                    selectedQuestionTypes.includes(type.value)
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-gray-900">{type.label}</div>
                  <div className="text-sm text-gray-600">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Test Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
              <select
                value={numQuestions}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty Level</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                {difficultyLevels.map(level => (
                  <option key={level.value} value={level.value}>{level.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Generate Test Button */}
          <div className="text-center">
            <button
              onClick={generatePracticeTest}
              disabled={!selectedSubject || selectedTopics.length === 0 || isGenerating}
              className="px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
            >
              {isGenerating ? 'Generating Test...' : 'Start Practice Test'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PracticeTestComponent;