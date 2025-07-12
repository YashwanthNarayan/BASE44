import React, { useState, useEffect } from 'react';
import { tutorAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput } from './ui/LiquidComponents';
import MessageFormatter from './MessageFormatter';
import '../styles/liquid-glass.css';

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
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-5xl mx-auto">
          {/* Neural Header */}
          <div className="text-center mb-8">
            <LiquidButton
              variant="secondary"
              onClick={() => onNavigate('student-dashboard')}
              className="mb-4"
            >
              ← Neural Dashboard
            </LiquidButton>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
              🤖 Neural Cognitive Enhancement System
            </h1>
            <p className="text-secondary">Connect with specialized AI tutors for personalized learning protocols</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Chat History Sidebar */}
            <div className="lg:col-span-1">
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-semibold text-primary">Chat History</h2>
                    <div className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse"></div>
                  </div>
                  
                  {loadingHistory ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="bg-glass rounded-lg p-3 animate-pulse">
                          <div className="h-4 bg-primary/20 rounded mb-2"></div>
                          <div className="h-3 bg-secondary/20 rounded w-2/3"></div>
                        </div>
                      ))}
                    </div>
                  ) : chatSessions.length > 0 ? (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {chatSessions.map(session => (
                        <div
                          key={session.session_id}
                          onClick={() => {
                            setSelectedSubject(session.subject);
                            loadSessionMessages(session.session_id);
                          }}
                          className="bg-glass hover:bg-glass-hover border border-primary/20 rounded-lg p-3 cursor-pointer transition-all duration-200 group"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-lg">
                                  {subjects.find(s => s.value === session.subject)?.icon || '🤖'}
                                </span>
                                <h3 className="text-sm font-medium text-primary truncate">
                                  {getSessionTitle(session)}
                                </h3>
                              </div>
                              <p className="text-xs text-secondary">
                                {getSessionPreview(session)}
                              </p>
                              <p className="text-xs text-secondary/70 mt-1">
                                {new Date(session.last_activity).toLocaleDateString()}
                              </p>
                            </div>
                            <button
                              onClick={(e) => deleteSession(session.session_id, e)}
                              className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all duration-200 p-1"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">💭</div>
                      <p className="text-secondary">No previous chats</p>
                      <p className="text-xs text-secondary/70 mt-1">Start a new conversation below</p>
                    </div>
                  )}
                </div>
              </LiquidCard>
            </div>

            {/* Subject Selection */}
            <div className="lg:col-span-3">
              <LiquidCard holographic>
                <div className="p-8">
                  <div className="flex items-center space-x-3 mb-8">
                    <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                      <span className="text-sm font-bold">🧠</span>
                    </div>
                    <h2 className="text-xl font-semibold text-primary">Select Neural Domain for Cognitive Enhancement</h2>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {subjects.map(subject => (
                      <div
                        key={subject.value}
                        onClick={() => setSelectedSubject(subject.value)}
                        className={`
                          p-6 rounded-xl border-2 transition-all duration-300 cursor-pointer
                          bg-gradient-to-br ${subject.gradient}
                          border-primary/20 hover:border-neon-cyan/50 hover:scale-105
                          transform group
                        `}
                      >
                        {/* Neural Glow Effect */}
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-neon-cyan/10 to-neon-magenta/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        
                        <div className="relative z-10 text-center">
                          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                            {subject.icon}
                          </div>
                          <h3 className="font-semibold text-primary mb-2 group-hover:text-neon-cyan transition-colors">
                            {subject.name}
                          </h3>
                          <p className="text-xs text-secondary group-hover:text-primary transition-colors">
                            Neural Enhancement Protocol
                          </p>
                        </div>
                        
                        {/* Data Stream Animation */}
                        <div className="absolute bottom-0 left-0 right-0 h-px">
                          <div className="h-full bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </LiquidCard>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const selectedSubjectData = subjects.find(s => s.value === selectedSubject);

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-3rem)]">
          
          {/* Chat History Sidebar */}
          <div className={`lg:col-span-1 ${showSidebar ? 'block' : 'hidden lg:block'}`}>
            <LiquidCard className="h-full flex flex-col">
              <div className="p-4 border-b border-primary/20">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-primary">Neural Sessions</h2>
                  <button
                    onClick={() => setShowSidebar(!showSidebar)}
                    className="lg:hidden text-secondary hover:text-primary"
                  >
                    ✕
                  </button>
                </div>
                
                <LiquidButton
                  onClick={() => {
                    setMessages([]);
                    setSessionId('');
                    setSelectedSessionId('');
                    setSelectedSubject('');
                  }}
                  className="w-full"
                  variant="primary"
                >
                  ⚡ New Neural Session
                </LiquidButton>
              </div>
              
              <div className="flex-1 p-4 overflow-y-auto">
                {loadingHistory ? (
                  <div className="space-y-3">
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="bg-glass rounded-lg p-3 animate-pulse">
                        <div className="h-4 bg-primary/20 rounded mb-2"></div>
                        <div className="h-3 bg-secondary/20 rounded w-2/3"></div>
                      </div>
                    ))}
                  </div>
                ) : chatSessions.length > 0 ? (
                  <div className="space-y-2">
                    {chatSessions.map(session => (
                      <div
                        key={session.session_id}
                        onClick={() => {
                          setSelectedSubject(session.subject);
                          loadSessionMessages(session.session_id);
                        }}
                        className={`
                          bg-glass hover:bg-glass-hover border rounded-lg p-3 cursor-pointer transition-all duration-200 group
                          ${selectedSessionId === session.session_id ? 'border-neon-cyan/50 bg-neon-cyan/10' : 'border-primary/20'}
                        `}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-lg">
                                {subjects.find(s => s.value === session.subject)?.icon || '🤖'}
                              </span>
                              <h3 className="text-sm font-medium text-primary truncate">
                                {session.subject.charAt(0).toUpperCase() + session.subject.slice(1)}
                              </h3>
                            </div>
                            <p className="text-xs text-secondary">
                              {getSessionPreview(session)}
                            </p>
                            <p className="text-xs text-secondary/70 mt-1">
                              {new Date(session.last_activity).toLocaleDateString()}
                            </p>
                          </div>
                          <button
                            onClick={(e) => deleteSession(session.session_id, e)}
                            className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all duration-200 p-1"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">💭</div>
                    <p className="text-secondary">No previous neural sessions</p>
                    <p className="text-xs text-secondary/70 mt-1">Create your first cognitive enhancement session</p>
                  </div>
                )}
              </div>
            </LiquidCard>
          </div>

          {/* Main Chat Interface */}
          <div className="lg:col-span-3">
            <LiquidCard className="h-full flex flex-col">
              {/* Neural Header */}
              <div className="p-6 border-b border-primary/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => setShowSidebar(!showSidebar)}
                      className="lg:hidden text-secondary hover:text-primary mr-2"
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
                      className="mr-2"
                    >
                      ← Select Domain
                    </LiquidButton>
                    <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${selectedSubjectData?.gradient} flex items-center justify-center`}>
                      <span className="text-2xl">{selectedSubjectData?.icon}</span>
                    </div>
                    <div>
                      <h1 className="text-xl font-bold text-primary">{selectedSubjectData?.name} Neural Tutor</h1>
                      <p className="text-sm text-secondary">
                        {sessionId ? 'Active neural session' : 'Establishing neural link...'}
                      </p>
                    </div>
                  </div>
                  <div className="holographic-status">
                    <span className="status-indicator"></span>
                    <span className="text-sm text-neon-cyan">Neural Link Active</span>
                  </div>
                </div>
              </div>

              {/* Neural Messages Stream */}
              <div className="flex-1 p-6 overflow-y-auto space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      {message.role === 'assistant' && (
                        <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center text-sm">
                          🤖
                        </div>
                      )}
                      <div
                        className={`
                          p-4 rounded-xl border backdrop-blur-sm
                          ${message.role === 'user'
                            ? 'bg-gradient-to-br from-neon-cyan/20 to-neon-magenta/20 border-neon-cyan/50 text-primary'
                            : 'bg-glass border-primary/20 text-primary'
                          }
                        `}
                      >
                        {message.role === 'user' ? (
                          <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
                        ) : (
                          <MessageFormatter 
                            content={message.content} 
                            className="leading-relaxed"
                          />
                        )}
                        <div className={`text-xs mt-3 ${
                          message.role === 'user' ? 'text-neon-cyan/70' : 'text-secondary'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      {message.role === 'user' && (
                        <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-sm">
                          👤
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center text-sm">
                        🤖
                      </div>
                      <div className="bg-glass border border-primary/20 p-4 rounded-xl">
                        <div className="flex items-center space-x-2">
                          <div className="quantum-loader w-4 h-4"></div>
                          <span className="text-secondary">Processing neural pathways...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Neural Input Interface */}
              <div className="p-6 border-t border-primary/20">
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
                      className="w-full p-4 bg-slate-800/50 border border-primary/20 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 text-white placeholder-slate-400 resize-none backdrop-blur-sm transition-all duration-200"
                      style={{
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        color: '#ffffff',
                        borderColor: 'rgba(248, 250, 252, 0.2)',
                        fontSize: '14px',
                        lineHeight: '1.5'
                      }}
                      rows="3"
                      disabled={loading}
                    />
                  </div>
                  <div className="flex flex-col justify-end">
                    <LiquidButton
                      onClick={sendMessage}
                      disabled={!currentMessage.trim() || loading || !sessionId}
                      className="whitespace-nowrap"
                    >
                      {loading ? '⚡ Processing...' : '⚡ Send Neural Query'}
                    </LiquidButton>
                  </div>
                </div>
                <div className="mt-3 text-xs text-secondary">
                  Press Enter to transmit • Shift+Enter for new line • Neural protocols active
                </div>
              </div>
            </LiquidCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TutorComponent;