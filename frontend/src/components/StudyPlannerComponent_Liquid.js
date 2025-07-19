import React, { useState, useEffect } from 'react';
import { studyPlannerAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput } from './ui/LiquidComponents';
import MessageFormatter from './MessageFormatter';
import '../styles/liquid-glass.css';

const StudyPlannerComponent = ({ student, onNavigate, onStartStudySession }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState(null);
  const [showPlanView, setShowPlanView] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [myPlans, setMyPlans] = useState([]);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'my-plans'

  useEffect(() => {
    startConversation();
    loadMyPlans();
  }, []);

  const startConversation = async () => {
    try {
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
    }
  };

  const loadMyPlans = async () => {
    try {
      const plans = await studyPlannerAPI.getMyPlans();
      setMyPlans(plans);
    } catch (error) {
      console.error('Error loading plans:', error);
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
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an issue. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const generatePlan = async (requirements) => {
    try {
      setLoading(true);
      
      // Convert requirements to API format
      const planRequest = {
        total_duration_minutes: requirements.total_duration,
        subjects: requirements.subjects.map(subj => ({
          subject: subj.subject,
          duration_minutes: subj.duration,
          priority: "medium"
        }))
      };

      const plan = await studyPlannerAPI.generatePlan(planRequest);
      setGeneratedPlan(plan);
      setShowPlanView(true);
      loadMyPlans(); // Refresh plans list

      // Add plan generation message
      const planMessage = {
        role: 'assistant',
        content: `🎉 **Your personalized study plan is ready!**\n\nI've created an optimized Pomodoro schedule with ${plan.pomodoro_sessions.length} sessions totaling ${plan.total_duration_minutes} minutes.\n\n📊 **Plan Summary:**\n• Work time: ${plan.total_work_time} minutes\n• Break time: ${plan.total_break_time} minutes\n• Total sessions: ${plan.pomodoro_sessions.filter(s => s.session_type === 'work').length}\n\nYour plan is now visible in the "My Plans" tab. You can start it anytime!`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, planMessage]);
    } catch (error) {
      console.error('Error generating plan:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I had trouble generating your plan. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const startStudySession = async (planId) => {
    try {
      // Start the session in the backend (this will update times to current time)
      const response = await studyPlannerAPI.startSession(planId);
      
      // Get the updated plan with actual times
      const updatedPlan = response.plan || myPlans.find(plan => plan.plan_id === planId);
      
      if (!updatedPlan) {
        alert('Plan not found. Please try again.');
        return;
      }
      
      // Add actual start time to the plan for real-time sync
      updatedPlan.actual_start_time = response.actual_start_time || new Date().toISOString();
      
      // Start the timer with the updated plan
      if (onStartStudySession) {
        onStartStudySession(updatedPlan);
      }
      
      // Update the plan list
      loadMyPlans();
      
      // Navigate to dashboard so user can see the timer
      onNavigate('student-dashboard');
    } catch (error) {
      console.error('Error starting session:', error);
      alert('Failed to start study session. Please try again.');
    }
  };

  const deletePlan = async (planId) => {
    if (window.confirm('Are you sure you want to delete this study plan?')) {
      try {
        await studyPlannerAPI.deletePlan(planId);
        loadMyPlans();
        alert('Study plan deleted successfully.');
      } catch (error) {
        console.error('Error deleting plan:', error);
        alert('Failed to delete study plan. Please try again.');
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatDuration = (minutes) => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
    return `${minutes}m`;
  };

  const formatTime = (timeStr) => {
    try {
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
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
            🗓️ Smart Study Planner
          </h1>
          <p className="text-secondary">AI-powered Pomodoro study sessions tailored for you</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-glass rounded-2xl p-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'chat' 
                ? 'bg-accent-blue text-white shadow-lg' 
                : 'text-secondary hover:text-primary'
              }`}
            >
              🤖 Plan Creator
            </button>
            <button
              onClick={() => setActiveTab('my-plans')}
              className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'my-plans' 
                ? 'bg-accent-blue text-white shadow-lg' 
                : 'text-secondary hover:text-primary'
              }`}
            >
              📋 My Plans ({myPlans.length})
            </button>
          </div>
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Chat Interface */}
            <div className="xl:col-span-1">
              <LiquidCard className="h-[600px] flex flex-col">
                {/* Chat Header */}
                <div className="p-6 border-b border-primary/20">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-secondary flex items-center justify-center">
                      <span className="text-2xl">🤖</span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-primary">Study Planner Bot</h2>
                      <p className="text-sm text-secondary">Your AI study scheduling assistant</p>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 p-6 overflow-y-auto space-y-6">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="flex items-start space-x-3 max-w-[85%]">
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center flex-shrink-0">
                            <span className="text-sm">🤖</span>
                          </div>
                        )}
                        <div
                          className={`
                            p-4 rounded-2xl border backdrop-blur-md
                            ${message.role === 'user'
                              ? 'bg-accent-blue/20 border-accent-blue/30 text-primary'
                              : 'bg-glass border-primary/20 text-primary'
                            }
                          `}
                        >
                          {message.role === 'user' ? (
                            <div className="whitespace-pre-wrap">{message.content}</div>
                          ) : (
                            <MessageFormatter content={message.content} />
                          )}
                          
                          {/* Suggested Actions */}
                          {message.suggested_actions && message.suggested_actions.length > 0 && (
                            <div className="mt-4 space-y-2">
                              {message.suggested_actions.map((action, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => {
                                    setCurrentMessage(action);
                                    setTimeout(() => sendMessage(), 100);
                                  }}
                                  className="block w-full text-left px-3 py-2 rounded-lg bg-accent-blue/10 hover:bg-accent-blue/20 text-accent-blue border border-accent-blue/30 transition-colors text-sm"
                                >
                                  {action}
                                </button>
                              ))}
                            </div>
                          )}
                          
                          <div className="text-xs text-secondary mt-2">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                        {message.role === 'user' && (
                          <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center flex-shrink-0">
                            <span className="text-sm">👤</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                          <span className="text-sm">🤖</span>
                        </div>
                        <div className="bg-glass border border-primary/20 rounded-2xl p-4">
                          <div className="flex items-center space-x-2">
                            <div className="quantum-loader w-4 h-4"></div>
                            <span className="text-secondary">Planning your perfect study session...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="p-6 border-t border-primary/20">
                  <div className="flex space-x-4">
                    <LiquidInput
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Tell me about your study goals..."
                      className="flex-1"
                      disabled={loading}
                    />
                    <LiquidButton
                      onClick={sendMessage}
                      disabled={!currentMessage.trim() || loading}
                      className="px-6"
                    >
                      {loading ? '⏳' : '📤'}
                    </LiquidButton>
                  </div>
                  <div className="mt-2 text-xs text-secondary text-center">
                    Press Enter to send • Example: "I want to study 2 hours - 1 hour math, 1 hour physics"
                  </div>
                </div>
              </LiquidCard>
            </div>

            {/* Plan Preview */}
            <div className="xl:col-span-1">
              <LiquidCard className="h-[600px] overflow-y-auto">
                <div className="p-6">
                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold text-primary mb-2">📊 Pomodoro Technique</h3>
                    <p className="text-secondary">Maximize your focus with scientifically-proven intervals</p>
                  </div>

                  <div className="space-y-6">
                    {/* Pomodoro Info */}
                    <div className="bg-glass/50 rounded-2xl p-6 border border-primary/10">
                      <h4 className="font-semibold text-primary mb-4">🍅 How it works:</h4>
                      <div className="space-y-3 text-sm">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-accent-blue/20 flex items-center justify-center">
                            <span className="text-accent-blue">25</span>
                          </div>
                          <span className="text-secondary">Minutes of focused study</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-accent-green/20 flex items-center justify-center">
                            <span className="text-accent-green">5</span>
                          </div>
                          <span className="text-secondary">Minutes of short break</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-accent-purple/20 flex items-center justify-center">
                            <span className="text-accent-purple">15</span>
                          </div>
                          <span className="text-secondary">Minutes of long break (every 4 sessions)</span>
                        </div>
                      </div>
                    </div>

                    {/* Benefits */}
                    <div className="bg-glass/50 rounded-2xl p-6 border border-primary/10">
                      <h4 className="font-semibold text-primary mb-4">✨ Benefits:</h4>
                      <ul className="space-y-2 text-sm text-secondary">
                        <li>• Improved focus and concentration</li>
                        <li>• Better time management</li>
                        <li>• Reduced mental fatigue</li>
                        <li>• Enhanced productivity</li>
                        <li>• Prevents burnout</li>
                      </ul>
                    </div>

                    {/* Tips */}
                    <div className="bg-glass/50 rounded-2xl p-6 border border-primary/10">
                      <h4 className="font-semibold text-primary mb-4">💡 Study Tips:</h4>
                      <ul className="space-y-2 text-sm text-secondary">
                        <li>• Find a quiet, distraction-free environment</li>
                        <li>• Turn off notifications during study sessions</li>
                        <li>• Stay hydrated and take care of your posture</li>
                        <li>• Use break time to stretch or walk</li>
                        <li>• Celebrate completing each session</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </LiquidCard>
            </div>
          </div>
        )}

        {/* My Plans Tab */}
        {activeTab === 'my-plans' && (
          <div className="space-y-6">
            {myPlans.length === 0 ? (
              <div className="text-center py-12">
                <LiquidCard className="max-w-md mx-auto">
                  <div className="p-8">
                    <div className="text-6xl mb-4">📋</div>
                    <h3 className="text-xl font-bold text-primary mb-2">No Study Plans Yet</h3>
                    <p className="text-secondary mb-6">Create your first AI-powered study plan using the Plan Creator!</p>
                    <LiquidButton
                      onClick={() => setActiveTab('chat')}
                      className="w-full"
                    >
                      🤖 Create My First Plan
                    </LiquidButton>
                  </div>
                </LiquidCard>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myPlans.map((plan) => (
                  <LiquidCard key={plan.plan_id} className="hover:shadow-lg transition-shadow">
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-primary">
                          📚 Study Session
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          plan.used 
                            ? 'bg-accent-green/20 text-accent-green' 
                            : 'bg-accent-blue/20 text-accent-blue'
                        }`}>
                          {plan.used ? 'Completed' : 'Ready'}
                        </span>
                      </div>
                      
                      <div className="space-y-3 mb-6">
                        <div className="flex justify-between text-sm">
                          <span className="text-secondary">Total Time:</span>
                          <span className="text-primary font-medium">{formatDuration(plan.total_duration_minutes)}</span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span className="text-secondary">Subjects:</span>
                          <span className="text-primary font-medium">{plan.subjects.length}</span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span className="text-secondary">Sessions:</span>
                          <span className="text-primary font-medium">
                            {plan.pomodoro_sessions.filter(s => s.session_type === 'work').length}
                          </span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span className="text-secondary">Created:</span>
                          <span className="text-primary font-medium">
                            {new Date(plan.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium text-secondary">Subjects:</h4>
                        <div className="flex flex-wrap gap-2">
                          {plan.subjects.map((subject, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-accent-purple/20 text-accent-purple rounded-lg text-xs"
                            >
                              {subject.subject} ({formatDuration(subject.duration_minutes)})
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 mt-6">
                        {!plan.used && (
                          <LiquidButton
                            onClick={() => startStudySession(plan.plan_id)}
                            variant="primary"
                            size="sm"
                            className="flex-1"
                          >
                            🚀 Start Session
                          </LiquidButton>
                        )}
                        <LiquidButton
                          onClick={() => {
                            setGeneratedPlan(plan);
                            setShowPlanView(true);
                          }}
                          variant="secondary"
                          size="sm"
                          className="flex-1"
                        >
                          👁️ View Details
                        </LiquidButton>
                        <LiquidButton
                          onClick={() => deletePlan(plan.plan_id)}
                          variant="secondary"
                          size="sm"
                          className="px-3"
                        >
                          🗑️
                        </LiquidButton>
                      </div>
                    </div>
                  </LiquidCard>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Plan Detail Modal */}
        {showPlanView && generatedPlan && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-dark-surface border border-primary/20 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-primary">📋 Study Plan Details</h2>
                  <button
                    onClick={() => setShowPlanView(false)}
                    className="w-8 h-8 rounded-full bg-glass hover:bg-glass/80 flex items-center justify-center text-secondary hover:text-primary transition-colors"
                  >
                    ✕
                  </button>
                </div>
                
                {/* Plan Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="bg-glass/50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-accent-blue">{formatDuration(generatedPlan.total_work_time)}</div>
                    <div className="text-sm text-secondary">Work Time</div>
                  </div>
                  <div className="bg-glass/50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-accent-green">{formatDuration(generatedPlan.total_break_time)}</div>
                    <div className="text-sm text-secondary">Break Time</div>
                  </div>
                  <div className="bg-glass/50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-accent-purple">
                      {generatedPlan.pomodoro_sessions.filter(s => s.session_type === 'work').length}
                    </div>
                    <div className="text-sm text-secondary">Sessions</div>
                  </div>
                </div>
                
                {/* Timeline */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-primary mb-4">⏱️ Session Timeline</h3>
                  <div className="space-y-3">
                    {generatedPlan.pomodoro_sessions.map((session, index) => (
                      <div
                        key={index}
                        className={`flex items-center p-4 rounded-xl border ${
                          session.session_type === 'work'
                            ? 'bg-accent-blue/10 border-accent-blue/30'
                            : 'bg-accent-green/10 border-accent-green/30'
                        }`}
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-4 ${
                          session.session_type === 'work'
                            ? 'bg-accent-blue/20 text-accent-blue'
                            : 'bg-accent-green/20 text-accent-green'
                        }`}>
                          {session.session_type === 'work' ? '📚' : '☕'}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-primary">{session.description}</div>
                          <div className="text-sm text-secondary">
                            {formatTime(session.start_time)} - {formatTime(session.end_time)} 
                            ({formatDuration(session.duration_minutes)})
                          </div>
                        </div>
                        {session.session_type === 'work' && (
                          <div className="px-3 py-1 bg-accent-blue/20 text-accent-blue rounded-full text-xs">
                            {session.subject}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Study Tips */}
                {generatedPlan.study_tips && generatedPlan.study_tips.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-primary mb-4">💡 Study Tips</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {generatedPlan.study_tips.map((tip, index) => (
                        <div key={index} className="bg-glass/50 rounded-xl p-4">
                          <div className="text-sm text-secondary">{tip}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-4">
                  <LiquidButton
                    onClick={() => setShowPlanView(false)}
                    variant="secondary"
                  >
                    Close
                  </LiquidButton>
                  {!generatedPlan.used && (
                    <LiquidButton
                      onClick={() => {
                        if (onStartStudySession) {
                          onStartStudySession(generatedPlan);
                        }
                        setShowPlanView(false);
                        onNavigate('student-dashboard');
                      }}
                      variant="primary"
                    >
                      🚀 Start This Session
                    </LiquidButton>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyPlannerComponent;