import React, { useState, useRef, useEffect } from 'react';
import { tutorAPI, setupAxiosAuth } from '../services/api';
import NavigationBar_Modern from './NavigationBar_Modern';
import { 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernInput,
  ModernTextarea,
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernSpinner,
  ModernBadge
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

const TutorComponent_Modern = ({ student, onNavigate }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionActive, setSessionActive] = useState(false);
  const [helpTopics, setHelpTopics] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    {
      id: 1,
      question: "Help me understand quadratic equations",
      category: "Mathematics",
      color: "blue"
    },
    {
      id: 2,
      question: "Explain photosynthesis process",
      category: "Biology",
      color: "green"
    },
    {
      id: 3,
      question: "What is Newton's second law?",
      category: "Physics", 
      color: "purple"
    },
    {
      id: 4,
      question: "Help with essay writing structure",
      category: "English",
      color: "indigo"
    },
    {
      id: 5,
      question: "Explain acid-base reactions",
      category: "Chemistry",
      color: "red"
    }
  ];

  // Initialize session when component mounts
  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeSession = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      setupAxiosAuth(token);

      const sessionResponse = await tutorAPI.createSession({
        subject: 'general' // Default subject
      });

      if (sessionResponse && sessionResponse.session_id) {
        setCurrentSessionId(sessionResponse.session_id);
      }
    } catch (error) {
      console.error('Failed to initialize tutor session:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setLoading(true);
    setError('');

    // Add user message
    const newMessages = [...messages, {
      id: Date.now(),
      text: userMessage,
      sender: 'user',
      timestamp: new Date()
    }];
    setMessages(newMessages);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      setupAxiosAuth(token);

      // Initialize session if not exists
      let sessionId = currentSessionId;
      if (!sessionId) {
        const sessionResponse = await tutorAPI.createSession({
          subject: 'general'
        });
        sessionId = sessionResponse.session_id;
        setCurrentSessionId(sessionId);
      }

      const response = await tutorAPI.chat({
        message: userMessage,
        subject: 'general',
        session_id: sessionId
      });

      // Add tutor response
      setMessages([...newMessages, {
        id: Date.now() + 1,
        text: response.response,
        sender: 'tutor',
        timestamp: new Date()
      }]);

      setSessionActive(true);

    } catch (error) {
      console.error('Tutor error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to get response. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setCurrentMessage(question);
  };

  const clearConversation = () => {
    setMessages([]);
    setSessionActive(false);
    setError('');
  };

  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'border-blue-500 bg-blue-50 text-blue-900 hover:border-blue-600',
      green: 'border-green-500 bg-green-50 text-green-900 hover:border-green-600',
      purple: 'border-purple-500 bg-purple-50 text-purple-900 hover:border-purple-600',
      indigo: 'border-indigo-500 bg-indigo-50 text-indigo-900 hover:border-indigo-600',
      red: 'border-red-500 bg-red-50 text-red-900 hover:border-red-600'
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="tutor"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"/>
            </svg>
          </div>
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-4">
            AI Learning Assistant
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Get personalized help with your studies from our intelligent tutor
          </ModernText>
        </div>

        {!sessionActive && (
          <>
            {/* Quick Questions */}
            <div className="mb-8">
              <ModernHeading level={4} className="mb-6 text-gray-800 font-semibold">Quick Questions</ModernHeading>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quickQuestions.map((item) => (
                  <ModernCard key={item.id} hover={true} className="cursor-pointer">
                    <ModernCardBody>
                      <div className="flex items-start justify-between mb-3">
                        <ModernBadge variant="secondary" className="text-xs">
                          {item.category}
                        </ModernBadge>
                        <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                      </div>
                      <ModernText 
                        className="text-gray-700 font-medium cursor-pointer hover:text-gray-900 transition-colors"
                        onClick={() => handleQuickQuestion(item.question)}
                      >
                        {item.question}
                      </ModernText>
                    </ModernCardBody>
                  </ModernCard>
                ))}
              </div>
            </div>

            {/* Features */}
            <ModernCard className="mb-8">
              <ModernCardHeader>
                <ModernHeading level={4} className="text-gray-800 font-semibold">How I Can Help</ModernHeading>
              </ModernCardHeader>
              <ModernCardBody>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                    <div>
                      <ModernHeading level={5} className="text-gray-800 font-semibold mb-1">Explain Concepts</ModernHeading>
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        Break down complex topics into simple, understandable explanations
                      </ModernText>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                      </svg>
                    </div>
                    <div>
                      <ModernHeading level={5} className="text-gray-800 font-semibold mb-1">Solve Problems</ModernHeading>
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        Step-by-step solutions for math, science, and other subjects
                      </ModernText>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
                      </svg>
                    </div>
                    <div>
                      <ModernHeading level={5} className="text-gray-800 font-semibold mb-1">Study Tips</ModernHeading>
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        Personalized study strategies and learning techniques
                      </ModernText>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/>
                      </svg>
                    </div>
                    <div>
                      <ModernHeading level={5} className="text-gray-800 font-semibold mb-1">Exam Prep</ModernHeading>
                      <ModernText variant="body-small" className="text-gray-600 font-medium">
                        Preparation strategies and practice for upcoming tests
                      </ModernText>
                    </div>
                  </div>
                </div>
              </ModernCardBody>
            </ModernCard>
          </>
        )}

        {/* Chat Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <ModernCard className="h-96 lg:h-[600px]">
              <ModernCardHeader className="flex items-center justify-between">
                <ModernHeading level={4} className="text-gray-800 font-semibold">Conversation</ModernHeading>
                {sessionActive && (
                  <ModernButton variant="outline" onClick={clearConversation} className="text-sm">
                    Clear Chat
                  </ModernButton>
                )}
              </ModernCardHeader>
              <ModernCardBody className="flex flex-col h-full">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                  {messages.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"/>
                        </svg>
                      </div>
                      <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">Ready to Help!</ModernHeading>
                      <ModernText variant="body-small" className="text-gray-500 font-medium">
                        Ask me anything about your studies or choose a quick question above
                      </ModernText>
                    </div>
                  )}
                  
                  {messages.map((message) => (
                    <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-sm px-4 py-3 rounded-2xl ${
                        message.sender === 'user' 
                          ? 'bg-indigo-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <div className={`font-medium text-sm leading-relaxed ${
                          message.sender === 'user' ? 'text-white' : 'text-black'
                        }`}>
                          {message.text}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                        <ModernSpinner size="sm" />
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="flex gap-2">
                  <textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Ask me anything about your studies..."
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-black font-medium leading-relaxed min-h-[48px] max-h-32"
                    disabled={loading}
                    rows="2"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                  />
                  <ModernButton 
                    type="submit" 
                    variant="primary"
                    disabled={loading || !currentMessage.trim()}
                    className="px-6"
                  >
                    Send
                  </ModernButton>
                </form>

                {error && (
                  <ModernAlert variant="error" className="mt-4">
                    {error}
                  </ModernAlert>
                )}
              </ModernCardBody>
            </ModernCard>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={5} className="text-gray-800 font-semibold">Session Info</ModernHeading>
              </ModernCardHeader>
              <ModernCardBody>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <ModernText variant="body-small" className="text-gray-600 font-medium">Messages</ModernText>
                    <ModernBadge variant="secondary">{messages.length}</ModernBadge>
                  </div>
                  <div className="flex items-center justify-between">
                    <ModernText variant="body-small" className="text-gray-600 font-medium">Status</ModernText>
                    <ModernBadge variant={sessionActive ? 'success' : 'secondary'}>
                      {sessionActive ? 'Active' : 'Ready'}
                    </ModernBadge>
                  </div>
                </div>
              </ModernCardBody>
            </ModernCard>

            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={5} className="text-gray-800 font-semibold">Study Tips</ModernHeading>
              </ModernCardHeader>
              <ModernCardBody>
                <div className="space-y-3 text-sm">
                  <ModernText variant="body-small" className="text-gray-600 font-medium">
                    • Be specific in your questions for better answers
                  </ModernText>
                  <ModernText variant="body-small" className="text-gray-600 font-medium">
                    • Ask for step-by-step explanations
                  </ModernText>
                  <ModernText variant="body-small" className="text-gray-600 font-medium">
                    • Request practice problems to test understanding
                  </ModernText>
                </div>
              </ModernCardBody>
            </ModernCard>
          </div>
        </div>
      </ModernContainer>
    </div>
  );
};

export default TutorComponent_Modern;