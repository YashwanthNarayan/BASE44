import React, { useState, useEffect } from 'react';
import { studyPlannerAPI } from '../services/api';
import { 
  ModernContainer, 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernInput, 
  ModernHeading, 
  ModernText, 
  ModernBadge, 
  ModernSpinner,
  ModernGrid,
  ModernProgress
} from './ui/ModernComponents';
import NavigationBar_Modern from './NavigationBar_Modern';

const StudyPlannerComponent_Modern = ({ student, onNavigate }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState(null);
  const [myPlans, setMyPlans] = useState([]);
  const [activeTab, setActiveTab] = useState('create'); // 'create', 'plans', 'templates'
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [planCreating, setPlanCreating] = useState(false);
  const [activeSession, setActiveSession] = useState(null);
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(0);
  const [showSessionDetails, setShowSessionDetails] = useState(false);

  // Quick plan templates
  const planTemplates = [
    {
      id: 'quick-review',
      name: 'Quick Review Session',
      duration: 90,
      description: '1.5 hours focused review',
      subjects: [{ subject: 'Mathematics', duration: 45 }, { subject: 'Science', duration: 45 }],
      icon: 'Qr',
      color: 'blue'
    },
    {
      id: 'exam-prep',
      name: 'Exam Preparation',
      duration: 180,
      description: '3 hours intensive study',
      subjects: [{ subject: 'Primary Subject', duration: 120 }, { subject: 'Secondary Subject', duration: 60 }],
      icon: 'Ex',
      color: 'red'
    },
    {
      id: 'daily-routine',
      name: 'Daily Study Routine',
      duration: 120,
      description: '2 hours balanced learning',
      subjects: [{ subject: 'Mathematics', duration: 40 }, { subject: 'Science', duration: 40 }, { subject: 'English', duration: 40 }],
      icon: 'Dr',
      color: 'green'
    },
    {
      id: 'subject-deep-dive',
      name: 'Subject Deep Dive',
      duration: 240,
      description: '4 hours comprehensive study',
      subjects: [{ subject: 'Focus Subject', duration: 240 }],
      icon: 'Sd',
      color: 'purple'
    }
  ];

  useEffect(() => {
    loadMyPlans();
    if (activeTab === 'create' && messages.length === 0) {
      startConversation();
    }
  }, [activeTab]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (activeSession && activeSession.timerId) {
        clearInterval(activeSession.timerId);
      }
    };
  }, [activeSession]);

  const startConversation = async () => {
    try {
      setLoading(true);
      const response = await studyPlannerAPI.chat("Hello", null);
      setMessages([{
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        needs_input: response.needs_input,
        input_type: response.input_type,
        suggested_actions: response.suggested_actions
      }]);
      setContext(response.context);
    } catch (error) {
      console.error('Error starting conversation:', error);
      setError('Failed to start study planner. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadMyPlans = async () => {
    try {
      const plans = await studyPlannerAPI.getMyPlans();
      setMyPlans(Array.isArray(plans) ? plans : []);
    } catch (error) {
      console.error('Error loading plans:', error);
      setMyPlans([]);
    }
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
    setError('');

    try {
      const response = await studyPlannerAPI.chat(currentMessage, context);

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        needs_input: response.needs_input,
        input_type: response.input_type,
        suggested_actions: response.suggested_actions
      };

      setMessages(prev => [...prev, assistantMessage]);
      setContext(response.context);

      // Check if we need to generate a plan
      if (response.input_type === 'generate_plan' && response.context?.requirements) {
        await generatePlan(response.context.requirements);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generatePlan = async (requirements) => {
    try {
      setPlanCreating(true);
      
      const planRequest = {
        total_duration_minutes: requirements.total_duration,
        subjects: requirements.subjects.map(subj => ({
          subject: subj.subject,
          duration_minutes: subj.duration,
          priority: "medium"
        }))
      };

      const plan = await studyPlannerAPI.generatePlan(planRequest);
      
      setSuccess('Study plan created successfully!');
      loadMyPlans();

      const planMessage = {
        role: 'assistant',
        content: `Your personalized study plan is ready! I've created an optimized Pomodoro schedule with ${plan.pomodoro_sessions?.length || 0} sessions totaling ${plan.total_duration_minutes} minutes. Check the "My Plans" tab to view and start your plan.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, planMessage]);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error generating plan:', error);
      setError('Failed to generate study plan. Please try again.');
    } finally {
      setPlanCreating(false);
    }
  };

  const createQuickPlan = async (template) => {
    try {
      setPlanCreating(true);
      setError('');
      
      const planRequest = {
        total_duration_minutes: template.duration,
        subjects: template.subjects.map(subj => ({
          subject: subj.subject,
          duration_minutes: subj.duration,
          priority: "medium"
        }))
      };

      await studyPlannerAPI.generatePlan(planRequest);
      setSuccess(`${template.name} created successfully!`);
      loadMyPlans();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error creating quick plan:', error);
      setError('Failed to create study plan. Please try again.');
    } finally {
      setPlanCreating(false);
    }
  };

  const startStudySession = async (planId) => {
    try {
      // Find the plan to get session details
      const plan = myPlans.find(p => p.id === planId || p.plan_id === planId);
      console.log('Found plan:', plan);
      
      if (!plan || !plan.pomodoro_sessions) {
        console.error('Invalid plan or missing pomodoro_sessions:', plan);
        setError('Invalid study plan selected.');
        return;
      }

      // Get the first incomplete session
      const nextSession = plan.pomodoro_sessions.find(session => !session.completed && !session.status);
      console.log('Next session:', nextSession);
      console.log('All sessions:', plan.pomodoro_sessions);
      
      if (!nextSession) {
        setError('All sessions in this plan are completed.');
        return;
      }

      // Start the session
      const response = await studyPlannerAPI.startSession(planId);
      
      // Set up active session tracking
      const sessionData = {
        planId: planId,
        plan: plan,
        currentSession: nextSession,
        sessionIndex: plan.pomodoro_sessions.indexOf(nextSession),
        totalSessions: plan.pomodoro_sessions.length,
        startTime: new Date(),
        duration: nextSession.duration_minutes * 60 * 1000 // Convert to milliseconds
      };
      
      console.log('Session data:', sessionData);
      console.log('Session duration in minutes:', nextSession.duration_minutes);
      console.log('Session duration in milliseconds:', sessionData.duration);
      
      setSessionTimeRemaining(sessionData.duration);
      setSuccess('Study session started! Focus time begins now.');
      
      // Start countdown timer and set active session with timer ID
      startSessionTimer(sessionData);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error starting session:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to start study session. Please try again.';
      setError(errorMessage);
    }
  };

  const startSessionTimer = (sessionData) => {
    let timeLeft = sessionData.duration;
    
    const timer = setInterval(() => {
      timeLeft -= 1000;
      setSessionTimeRemaining(timeLeft);
      
      if (timeLeft <= 0) {
        clearInterval(timer);
        completeCurrentSession();
      }
    }, 1000);
    
    // Store timer reference in session data
    const updatedSessionData = { ...sessionData, timerId: timer };
    setActiveSession(updatedSessionData);
    
    return timer;
  };

  const completeCurrentSession = () => {
    if (activeSession) {
      // Clear timer
      if (activeSession.timerId) {
        clearInterval(activeSession.timerId);
      }
      
      // Check if there are more sessions
      const nextSessionIndex = activeSession.sessionIndex + 1;
      const hasMoreSessions = nextSessionIndex < activeSession.totalSessions;
      
      if (hasMoreSessions) {
        const nextSession = activeSession.plan.pomodoro_sessions[nextSessionIndex];
        setSuccess(`Session completed! ${nextSession.session_type === 'work' ? 'Work' : 'Break'} session is next.`);
      } else {
        setSuccess('Congratulations! You have completed all sessions in this study plan!');
      }
      
      // Clear active session after a delay
      setTimeout(() => {
        setActiveSession(null);
        setSessionTimeRemaining(0);
        loadMyPlans(); // Refresh plans to show updated progress
      }, 3000);
    }
  };

  const stopSession = () => {
    if (activeSession && activeSession.timerId) {
      clearInterval(activeSession.timerId);
    }
    setActiveSession(null);
    setSessionTimeRemaining(0);
    setSuccess('Study session stopped.');
    setTimeout(() => setSuccess(''), 3000);
  };

  const deletePlan = async (planId) => {
    try {
      await studyPlannerAPI.deletePlan(planId);
      setSuccess('Study plan deleted successfully.');
      loadMyPlans();
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error deleting plan:', error);
      setError('Failed to delete study plan. Please try again.');
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const formatTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  };

  const getPlanProgress = (plan) => {
    if (!plan.pomodoro_sessions || plan.pomodoro_sessions.length === 0) return 0;
    const completedSessions = plan.pomodoro_sessions.filter(s => s.completed || s.status === 'completed').length;
    return Math.round((completedSessions / plan.pomodoro_sessions.length) * 100);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <NavigationBar_Modern 
        user={student}
        currentPage="study-planner"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      {/* Dynamic Island - Active Session Tracker */}
      {activeSession && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
          <div 
            className={`bg-black rounded-full px-6 py-3 shadow-2xl transition-all duration-300 cursor-pointer ${
              showSessionDetails ? 'px-8 py-4' : ''
            }`}
            onMouseEnter={() => setShowSessionDetails(true)}
            onMouseLeave={() => setShowSessionDetails(false)}
          >
            <div className="flex items-center gap-4 text-white">
              {/* Timer Display */}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  activeSession.currentSession.session_type === 'work' 
                    ? 'bg-green-400' 
                    : 'bg-blue-400'
                } animate-pulse`}></div>
                <span className="font-mono text-lg font-bold">
                  {Math.floor(Math.max(0, sessionTimeRemaining) / 60000)}:
                  {String(Math.floor((Math.max(0, sessionTimeRemaining) % 60000) / 1000)).padStart(2, '0')}
                </span>
              </div>

              {/* Expanded Details */}
              {showSessionDetails && (
                <>
                  <div className="h-6 w-px bg-gray-600"></div>
                  <div className="flex items-center gap-3">
                    <div className="text-sm">
                      <div className="font-semibold">
                        {activeSession.currentSession.session_type === 'work' ? 'Focus Time' : 'Break Time'}
                      </div>
                      <div className="text-gray-300 text-xs">
                        Session {activeSession.sessionIndex + 1} of {activeSession.totalSessions}
                      </div>
                    </div>
                    
                    {activeSession.currentSession.subject && (
                      <>
                        <div className="h-6 w-px bg-gray-600"></div>
                        <div className="text-sm">
                          <div className="font-medium text-gray-300">
                            {activeSession.currentSession.subject}
                          </div>
                        </div>
                      </>
                    )}
                    
                    <button
                      onClick={stopSession}
                      className="ml-3 w-6 h-6 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors"
                      title="Stop session"
                    >
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* Progress Bar */}
            <div className="mt-2">
              <div className="w-full bg-gray-700 rounded-full h-1">
                <div 
                  className={`h-1 rounded-full transition-all duration-1000 ${
                    activeSession.currentSession.session_type === 'work' 
                      ? 'bg-green-400' 
                      : 'bg-blue-400'
                  }`}
                  style={{
                    width: `${Math.max(0, (activeSession.duration - sessionTimeRemaining) / activeSession.duration * 100)}%`
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="mb-8">
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
            Study Planner
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Create personalized study plans with AI-powered Pomodoro scheduling
          </ModernText>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-red-800 font-medium">{error}</ModernText>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-green-800 font-medium">{success}</ModernText>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex bg-white rounded-2xl p-2 shadow-sm border border-gray-100">
            {[
              { id: 'create', label: 'Create Plan', icon: 'Cr' },
              { id: 'plans', label: 'My Plans', icon: 'Mp' },
              { id: 'templates', label: 'Templates', icon: 'Tp' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-indigo-500 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span className="font-bold text-sm">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Create Plan Tab */}
        {activeTab === 'create' && (
          <ModernCard className="shadow-lg">
            <ModernCardHeader>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div>
                  <ModernHeading level={3} className="text-gray-900 font-semibold">
                    AI Study Planner
                  </ModernHeading>
                  <ModernText className="text-gray-600">
                    Tell me about your study goals and I'll create a personalized plan
                  </ModernText>
                </div>
              </div>
            </ModernCardHeader>
            <ModernCardBody>
              {/* Chat Messages */}
              <div className="mb-6 max-h-96 overflow-y-auto space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-4 rounded-2xl ${
                        message.role === 'user'
                          ? 'bg-indigo-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      <div className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-4 rounded-2xl">
                      <div className="flex items-center gap-2">
                        <ModernSpinner size="sm" />
                        <ModernText className="text-gray-600">AI is thinking...</ModernText>
                      </div>
                    </div>
                  </div>
                )}
                {planCreating && (
                  <div className="flex justify-start">
                    <div className="bg-blue-100 p-4 rounded-2xl">
                      <div className="flex items-center gap-2">
                        <ModernSpinner size="sm" />
                        <ModernText className="text-blue-800">Creating your study plan...</ModernText>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="flex gap-3">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Tell me about your study goals, subjects, and time available..."
                  rows="3"
                  className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-500"
                />
                <ModernButton
                  variant="primary"
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || loading}
                  className="px-6 font-semibold self-end"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </ModernButton>
              </div>
            </ModernCardBody>
          </ModernCard>
        )}

        {/* My Plans Tab */}
        {activeTab === 'plans' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                My Study Plans ({myPlans.length})
              </ModernHeading>
              <ModernButton variant="outline" onClick={loadMyPlans}>
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                </svg>
                Refresh
              </ModernButton>
            </div>

            {myPlans.length > 0 ? (
              <ModernGrid cols={2} className="gap-6">
                {myPlans.map((plan, index) => {
                  const progress = getPlanProgress(plan);
                  const isCompleted = progress === 100;
                  
                  return (
                    <ModernCard key={plan.id || index} className="hover:shadow-xl transition-shadow">
                      <ModernCardBody className="space-y-4">
                        <div className="flex items-start justify-between">
                          <div>
                            <ModernHeading level={4} className="text-gray-900 font-bold mb-1">
                              Study Plan #{index + 1}
                            </ModernHeading>
                            <ModernText className="text-gray-600 text-sm">
                              Created {new Date(plan.created_at || Date.now()).toLocaleDateString()}
                            </ModernText>
                          </div>
                          <ModernBadge variant={isCompleted ? 'success' : 'primary'}>
                            {isCompleted ? 'Completed' : 'Active'}
                          </ModernBadge>
                        </div>

                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <ModernText className="text-gray-600 font-medium">Duration:</ModernText>
                            <ModernText className="font-bold text-gray-900">
                              {formatDuration(plan.total_duration_minutes || 0)}
                            </ModernText>
                          </div>
                          <div className="flex items-center justify-between">
                            <ModernText className="text-gray-600 font-medium">Sessions:</ModernText>
                            <ModernText className="font-bold text-gray-900">
                              {plan.pomodoro_sessions?.length || 0}
                            </ModernText>
                          </div>
                          {progress > 0 && (
                            <div>
                              <div className="flex items-center justify-between mb-2">
                                <ModernText className="text-gray-600 font-medium">Progress:</ModernText>
                                <ModernText className="font-bold text-gray-900">{progress}%</ModernText>
                              </div>
                              <ModernProgress value={progress} max={100} />
                            </div>
                          )}
                        </div>

                        <div className="flex gap-2 pt-4 border-t border-gray-100">
                          <ModernButton
                            variant="primary"
                            onClick={() => startStudySession(plan.plan_id || plan.id)}
                            disabled={isCompleted || (activeSession && (activeSession.planId === (plan.plan_id || plan.id)))}
                            className="flex-1 font-medium"
                          >
                            {activeSession && (activeSession.planId === (plan.plan_id || plan.id)) 
                              ? 'In Progress' 
                              : isCompleted 
                                ? 'Completed' 
                                : 'Start Study'
                            }
                          </ModernButton>
                          <ModernButton
                            variant="outline"
                            onClick={() => deletePlan(plan.plan_id || plan.id)}
                            disabled={activeSession && (activeSession.planId === (plan.plan_id || plan.id))}
                            className="font-medium text-red-600 border-red-200 hover:bg-red-50 disabled:opacity-50"
                          >
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 012 0v6a1 1 0 11-2 0V7zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V7a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                          </ModernButton>
                        </div>
                      </ModernCardBody>
                    </ModernCard>
                  );
                })}
              </ModernGrid>
            ) : (
              <div className="text-center py-16">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <ModernHeading level={3} className="text-gray-800 font-semibold mb-3">
                  No Study Plans Yet
                </ModernHeading>
                <ModernText className="text-gray-600 font-medium mb-6">
                  Create your first personalized study plan to get started with organized learning.
                </ModernText>
                <ModernButton 
                  variant="primary" 
                  onClick={() => setActiveTab('create')}
                  className="font-semibold"
                >
                  Create Your First Plan
                </ModernButton>
              </div>
            )}
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="space-y-6">
            <div>
              <ModernHeading level={2} className="text-2xl font-bold text-gray-900 mb-3">
                Quick Plan Templates
              </ModernHeading>
              <ModernText className="text-gray-600 font-medium">
                Choose from pre-designed study plans to get started quickly
              </ModernText>
            </div>

            <ModernGrid cols={2} className="gap-6">
              {planTemplates.map((template) => (
                <ModernCard key={template.id} className="hover:shadow-xl transition-shadow">
                  <ModernCardBody className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 bg-${template.color}-100 rounded-xl flex items-center justify-center`}>
                        <span className={`font-bold text-lg text-${template.color}-600`}>
                          {template.icon}
                        </span>
                      </div>
                      <div className="flex-1">
                        <ModernHeading level={4} className="text-gray-900 font-bold mb-1">
                          {template.name}
                        </ModernHeading>
                        <ModernText className="text-gray-600 text-sm">
                          {template.description}
                        </ModernText>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <ModernText className="text-gray-600 font-medium">Duration:</ModernText>
                        <ModernBadge variant="secondary">{formatDuration(template.duration)}</ModernBadge>
                      </div>
                      <div className="flex items-center justify-between">
                        <ModernText className="text-gray-600 font-medium">Subjects:</ModernText>
                        <ModernText className="font-bold text-gray-900">{template.subjects.length}</ModernText>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-gray-100">
                      <ModernButton
                        variant="primary"
                        onClick={() => createQuickPlan(template)}
                        disabled={planCreating}
                        className="w-full font-medium"
                      >
                        {planCreating ? (
                          <div className="flex items-center gap-2">
                            <ModernSpinner size="sm" />
                            <span>Creating...</span>
                          </div>
                        ) : (
                          <div className="flex items-center justify-center gap-2">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                            </svg>
                            Use This Template
                          </div>
                        )}
                      </ModernButton>
                    </div>
                  </ModernCardBody>
                </ModernCard>
              ))}
            </ModernGrid>
          </div>
        )}
      </ModernContainer>
    </div>
  );
};

export default StudyPlannerComponent_Modern;