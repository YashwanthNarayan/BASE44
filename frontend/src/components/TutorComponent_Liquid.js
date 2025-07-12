import React, { useState, useEffect } from 'react';
import { tutorAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput } from './ui/LiquidComponents';
import MessageFormatter from './MessageFormatter';
import '../styles/liquid-glass.css';
import '../styles/chatbot-luxury.css';

const TutorComponent = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [chatSessions, setChatSessions] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [selectedSessionId, setSelectedSessionId] = useState('');
  const [loadingHistory, setLoadingHistory] = useState(false);

  const subjects = [
    { value: 'math', name: 'Quantum Mathematics', icon: '🔢', gradient: 'from-blue-500/20 to-cyan-500/20' },
    { value: 'physics', name: 'Neural Physics', icon: '⚛️', gradient: 'from-purple-500/20 to-indigo-500/20' },
    { value: 'chemistry', name: 'Molecular Chemistry', icon: '🧪', gradient: 'from-green-500/20 to-emerald-500/20' },
    { value: 'biology', name: 'Bio-Neural Science', icon: '🧬', gradient: 'from-emerald-500/20 to-teal-500/20' },
    { value: 'english', name: 'Linguistic Protocols', icon: '📚', gradient: 'from-red-500/20 to-pink-500/20' },
    { value: 'history', name: 'Temporal Archives', icon: '🏛️', gradient: 'from-yellow-500/20 to-orange-500/20' },
    { value: 'geography', name: 'Planetary Systems', icon: '🌍', gradient: 'from-teal-500/20 to-cyan-500/20' }
  ];

  useEffect(() => {
    loadChatSessions();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      startNewSession();
    }
  }, [selectedSubject]);

  const loadChatSessions = async () => {
    try {
      setLoadingHistory(true);
      const sessions = await tutorAPI.getSessions();
      setChatSessions(sessions);
    } catch (error) {
      console.error('Error loading chat sessions:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      setLoading(true);
      const messages = await tutorAPI.getSessionMessages(sessionId);
      
      // Convert backend messages to frontend format
      const formattedMessages = [];
      messages.forEach(msg => {
        // Add user message
        formattedMessages.push({
          role: 'user',
          content: msg.message,
          timestamp: new Date(msg.timestamp)
        });
        
        // Add assistant response
        if (msg.response) {
          formattedMessages.push({
            role: 'assistant',
            content: msg.response,
            timestamp: new Date(msg.timestamp)
          });
        }
      });
      
      setMessages(formattedMessages);
      setSelectedSessionId(sessionId);
      setSessionId(sessionId);
    } catch (error) {
      console.error('Error loading session messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const startNewSession = async () => {
    try {
      const response = await tutorAPI.createSession({ subject: selectedSubject });
      setSessionId(response.session_id);
      setSelectedSessionId(response.session_id);
      setMessages([
        {
          role: 'assistant',
          content: `Neural connection established! I'm your ${selectedSubject} cognitive enhancement specialist. I'm here to optimize your understanding, process complex algorithms, and guide you through advanced problem-solving protocols. What neural pathways shall we explore today?`,
          timestamp: new Date()
        }
      ]);
      
      // Reload sessions to include the new one
      loadChatSessions();
    } catch (error) {
      console.error('Error starting tutor session:', error);
    }
  };

  const deleteSession = async (sessionId, event) => {
    event.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this chat session? This action cannot be undone.')) {
      try {
        await tutorAPI.deleteSession(sessionId);
        
        // If deleted session was currently selected, clear it
        if (selectedSessionId === sessionId) {
          setMessages([]);
          setSelectedSessionId('');
          setSessionId('');
        }
        
        // Reload sessions
        loadChatSessions();
      } catch (error) {
        console.error('Error deleting session:', error);
        alert('Failed to delete session. Please try again.');
      }
    }
  };

  const getSessionTitle = (session) => {
    return session.session_title || `${session.subject} Chat - ${new Date(session.started_at).toLocaleDateString()}`;
  };

  const getSessionPreview = (session) => {
    if (session.message_count === 0) {
      return 'New conversation';
    }
    return `${session.message_count} messages`;
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response = await tutorAPI.sendMessage({
        message: currentMessage,
        subject: selectedSubject,
        session_id: sessionId
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Reload sessions to update message count
      loadChatSessions();
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Neural network connection interrupted. Please re-establish communication link.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!selectedSubject) {
    return (
      <div className="chatbot-container min-h-screen bg-dark-space text-primary relative">
        <div className="quantum-grid fixed inset-0 opacity-40" />
        
        {/* Floating Particles */}
        <div className="floating-particles">
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
        </div>
        
        <div className="relative z-10 p-6 max-w-5xl mx-auto">
          {/* Enhanced Neural Header */}
          <div className="text-center mb-8">
            <LiquidButton
              variant="secondary"
              onClick={() => onNavigate('student-dashboard')}
              className="mb-6 btn-holographic"
            >
              ← Neural Dashboard
            </LiquidButton>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-luxury-gold via-neon-cyan to-luxury-platinum bg-clip-text text-transparent mb-4">
              🤖 Neural Cognitive Enhancement System
            </h1>
            <p className="text-luxury-platinum text-lg">Connect with specialized AI tutors for personalized learning protocols</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Enhanced Chat History Sidebar */}
            <div className="lg:col-span-1">
              <div className="liquid-card-premium">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-luxury-gold">Neural Sessions</h2>
                    <div className="holographic-status">
                      <div className="status-indicator"></div>
                    </div>
                  </div>
                  
                  {loadingHistory ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="session-card-luxury p-4 animate-pulse">
                          <div className="h-4 bg-luxury-gold/20 rounded mb-2"></div>
                          <div className="h-3 bg-luxury-platinum/20 rounded w-2/3"></div>
                        </div>
                      ))}
                    </div>
                  ) : chatSessions.length > 0 ? (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {chatSessions.map(session => (
                        <div
                          key={session.session_id}
                          onClick={() => {
                            setSelectedSubject(session.subject);
                            loadSessionMessages(session.session_id);
                          }}
                          className="session-card-luxury p-4 cursor-pointer transition-all duration-300 group"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-3 mb-2">
                                <span className="text-2xl">
                                  {subjects.find(s => s.value === session.subject)?.icon || '🤖'}
                                </span>
                                <h3 className="text-sm font-semibold text-luxury-gold truncate">
                                  {getSessionTitle(session)}
                                </h3>
                              </div>
                              <p className="text-xs text-luxury-platinum">
                                {getSessionPreview(session)}
                              </p>
                              <p className="text-xs text-luxury-platinum/70 mt-1">
                                {new Date(session.last_activity).toLocaleDateString()}
                              </p>
                            </div>
                            <button
                              onClick={(e) => deleteSession(session.session_id, e)}
                              className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all duration-200 p-1 text-lg"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <div className="text-6xl mb-6">💭</div>
                      <p className="text-luxury-platinum text-lg">No previous neural sessions</p>
                      <p className="text-xs text-luxury-platinum/70 mt-2">Create your first cognitive enhancement session</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Enhanced Subject Selection */}
            <div className="lg:col-span-3">
              <div className="liquid-card-premium">
                <div className="p-8">
                  <div className="flex items-center space-x-4 mb-8">
                    <div className="avatar-premium w-12 h-12 rounded-full flex items-center justify-center">
                      <span className="text-2xl">🧠</span>
                    </div>
                    <h2 className="text-2xl font-bold text-luxury-gold">Select Neural Domain for Cognitive Enhancement</h2>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {subjects.map(subject => (
                      <div
                        key={subject.value}
                        onClick={() => setSelectedSubject(subject.value)}
                        className={`
                          relative p-8 rounded-2xl border-2 transition-all duration-500 cursor-pointer
                          bg-gradient-to-br ${subject.gradient}
                          border-luxury-gold/20 hover:border-luxury-gold hover:scale-105
                          transform group overflow-hidden
                        `}
                      >
                        {/* Holographic Glow Effect */}
                        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-neon-cyan/10 via-luxury-gold/10 to-neon-purple/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        
                        <div className="relative z-10 text-center">
                          <div className="text-5xl mb-6 group-hover:scale-125 transition-transform duration-500">
                            {subject.icon}
                          </div>
                          <h3 className="font-bold text-xl text-luxury-gold mb-3 group-hover:text-neon-cyan transition-colors duration-300">
                            {subject.name}
                          </h3>
                          <p className="text-sm text-luxury-platinum group-hover:text-white transition-colors duration-300">
                            Neural Enhancement Protocol
                          </p>
                        </div>
                        
                        {/* Premium Border Animation */}
                        <div className="absolute bottom-0 left-0 right-0 h-1">
                          <div className="h-full bg-gradient-to-r from-transparent via-luxury-gold to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const selectedSubjectData = subjects.find(s => s.value === selectedSubject);

  return (
    <div className="chatbot-container min-h-screen bg-dark-space text-primary relative">
      <div className="quantum-grid fixed inset-0 opacity-40" />
      
      {/* Floating Particles */}
      <div className="floating-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-[calc(100vh-3rem)]">
          
          {/* Enhanced Chat History Sidebar */}
          <div className={`lg:col-span-1 ${showSidebar ? 'block' : 'hidden lg:block'}`}>
            <div className="liquid-card-premium h-full flex flex-col">
              <div className="p-6 border-b border-luxury-gold/20">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-luxury-gold">Neural Sessions</h2>
                  <button
                    onClick={() => setShowSidebar(!showSidebar)}
                    className="lg:hidden text-luxury-platinum hover:text-luxury-gold transition-colors"
                  >
                    ✕
                  </button>
                </div>
                
                <button
                  onClick={() => {
                    setMessages([]);
                    setSessionId('');
                    setSelectedSessionId('');
                    setSelectedSubject('');
                  }}
                  className="w-full btn-holographic"
                >
                  ⚡ New Neural Session
                </button>
              </div>
              
              <div className="flex-1 p-6 overflow-y-auto">
                {loadingHistory ? (
                  <div className="space-y-4">
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="session-card-luxury p-4 animate-pulse">
                        <div className="h-4 bg-luxury-gold/20 rounded mb-2"></div>
                        <div className="h-3 bg-luxury-platinum/20 rounded w-2/3"></div>
                      </div>
                    ))}
                  </div>
                ) : chatSessions.length > 0 ? (
                  <div className="space-y-3">
                    {chatSessions.map(session => (
                      <div
                        key={session.session_id}
                        onClick={() => {
                          setSelectedSubject(session.subject);
                          loadSessionMessages(session.session_id);
                        }}
                        className={`
                          session-card-luxury p-4 cursor-pointer transition-all duration-300 group
                          ${selectedSessionId === session.session_id ? 'active' : ''}
                        `}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className="text-2xl">
                                {subjects.find(s => s.value === session.subject)?.icon || '🤖'}
                              </span>
                              <h3 className="text-sm font-semibold text-luxury-gold truncate">
                                {session.subject.charAt(0).toUpperCase() + session.subject.slice(1)}
                              </h3>
                            </div>
                            <p className="text-xs text-luxury-platinum">
                              {getSessionPreview(session)}
                            </p>
                            <p className="text-xs text-luxury-platinum/70 mt-1">
                              {new Date(session.last_activity).toLocaleDateString()}
                            </p>
                          </div>
                          <button
                            onClick={(e) => deleteSession(session.session_id, e)}
                            className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all duration-200 p-1 text-lg"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-6">💭</div>
                    <p className="text-luxury-platinum text-lg">No previous neural sessions</p>
                    <p className="text-xs text-luxury-platinum/70 mt-2">Create your first cognitive enhancement session</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Enhanced Main Chat Interface */}
          <div className="lg:col-span-3">
            <div className="liquid-card-premium h-full flex flex-col">
              {/* Premium Neural Header */}
              <div className="p-6 border-b border-luxury-gold/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => setShowSidebar(!showSidebar)}
                      className="lg:hidden text-luxury-platinum hover:text-luxury-gold transition-colors mr-2 text-xl"
                    >
                      ☰
                    </button>
                    <LiquidButton
                      variant="secondary"
                      onClick={() => {
                        setSelectedSubject('');
                        setMessages([]);
                        setSessionId('');
                        setSelectedSessionId('');
                      }}
                      className="mr-4 btn-holographic"
                    >
                      ← Select Domain
                    </LiquidButton>
                    <div className={`avatar-premium w-14 h-14 rounded-full bg-gradient-to-br ${selectedSubjectData?.gradient} flex items-center justify-center`}>
                      <span className="text-3xl">{selectedSubjectData?.icon}</span>
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-luxury-gold">{selectedSubjectData?.name} Neural Tutor</h1>
                      <p className="text-sm text-luxury-platinum">
                        {sessionId ? 'Active neural session' : 'Establishing neural link...'}
                      </p>
                    </div>
                  </div>
                  <div className="holographic-status">
                    <span className="status-indicator"></span>
                    <span className="text-sm text-success font-semibold">Neural Link Active</span>
                  </div>
                </div>
              </div>

              {/* Enhanced Neural Messages Stream */}
              <div className="flex-1 p-6 overflow-y-auto space-y-8">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className="flex items-start space-x-4 max-w-[85%]">
                      {message.role === 'assistant' && (
                        <div className="avatar-premium w-10 h-10 rounded-full bg-gradient-luxury flex items-center justify-center text-lg">
                          🤖
                        </div>
                      )}
                      <div
                        className={`
                          p-6 rounded-2xl border backdrop-blur-md transition-all duration-300
                          ${message.role === 'user'
                            ? 'chat-bubble-user text-white'
                            : 'chat-bubble-assistant text-luxury-platinum'
                          }
                        `}
                      >
                        {message.role === 'user' ? (
                          <div className="whitespace-pre-wrap leading-relaxed text-lg">{message.content}</div>
                        ) : (
                          <MessageFormatter 
                            content={message.content} 
                            className="leading-relaxed text-base"
                          />
                        )}
                        <div className={`text-xs mt-4 ${
                          message.role === 'user' ? 'text-neon-cyan/80' : 'text-luxury-gold/80'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      {message.role === 'user' && (
                        <div className="avatar-premium w-10 h-10 rounded-full bg-gradient-holographic flex items-center justify-center text-lg">
                          👤
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-4">
                      <div className="avatar-premium w-10 h-10 rounded-full bg-gradient-luxury flex items-center justify-center text-lg">
                        🤖
                      </div>
                      <div className="chat-bubble-assistant p-6">
                        <div className="flex items-center space-x-3">
                          <div className="quantum-loader w-5 h-5"></div>
                          <span className="text-luxury-platinum">Processing neural pathways...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Enhanced Neural Input Interface */}
              <div className="p-6 border-t border-luxury-gold/20">
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <textarea
                      value={currentMessage}
                      onChange={(e) => {
                        console.log('Textarea value changing:', e.target.value);
                        setCurrentMessage(e.target.value);
                      }}
                      onKeyPress={handleKeyPress}
                      placeholder={`Input your ${selectedSubjectData?.name.toLowerCase()} query here...`}
                      className="w-full p-6 input-luxury resize-none text-lg"
                      style={{
                        fontSize: '16px',
                        lineHeight: '1.5'
                      }}
                      rows="3"
                      disabled={loading}
                    />
                  </div>
                  <div className="flex flex-col justify-end">
                    <button
                      onClick={sendMessage}
                      disabled={!currentMessage.trim() || loading || !sessionId}
                      className="btn-holographic px-8 py-4 text-lg font-bold"
                    >
                      {loading ? '⚡ Processing...' : '⚡ Send Neural Query'}
                    </button>
                  </div>
                </div>
                <div className="mt-4 text-sm text-luxury-platinum/70 text-center">
                  Press Enter to transmit • Shift+Enter for new line • Neural protocols active
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TutorComponent;