import React, { useState, useEffect } from 'react';
import { mindfulnessAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const MindfulnessComponent = ({ student, onNavigate }) => {
  const [activeSession, setActiveSession] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [moodBefore, setMoodBefore] = useState('');
  const [moodAfter, setMoodAfter] = useState('');

  const mindfulnessActivities = [
    {
      id: 'breathing',
      name: 'Quantum Breathing',
      description: 'Synchronized neural respiration patterns',
      duration: 5,
      icon: '🫁',
      gradient: 'from-cyan-500/20 to-blue-500/20',
      instructions: 'Inhale for 4 cycles, hold for 4, exhale for 6. Synchronize with the quantum field.'
    },
    {
      id: 'meditation',
      name: 'Neural Meditation',
      description: 'Deep consciousness exploration protocol',
      duration: 10,
      icon: '🧘‍♀️',
      gradient: 'from-purple-500/20 to-indigo-500/20',
      instructions: 'Close optical sensors, establish neural comfort, focus on quantum present moment.'
    },
    {
      id: 'body_scan',
      name: 'Bio-Scan Protocol',
      description: 'Progressive cellular relaxation sequence',
      duration: 8,
      icon: '💆‍♀️',
      gradient: 'from-green-500/20 to-emerald-500/20',
      instructions: 'Initialize scan from neural center, progress through all biological systems.'
    },
    {
      id: 'gratitude',
      name: 'Gratitude Matrix',
      description: 'Positive neural pattern enhancement',
      duration: 3,
      icon: '🙏',
      gradient: 'from-yellow-500/20 to-orange-500/20',
      instructions: 'Identify 3 positive quantum states and analyze their neural significance.'
    }
  ];

  const moods = [
    { value: '😊 Excellent', color: 'text-neon-green' },
    { value: '🙂 Good', color: 'text-neon-cyan' },
    { value: '😐 Neutral', color: 'text-neon-yellow' },
    { value: '😔 Low', color: 'text-neon-magenta' },
    { value: '😰 Stressed', color: 'text-neon-pink' }
  ];

  useEffect(() => {
    loadSessionHistory();
  }, []);

  useEffect(() => {
    let interval;
    if (activeSession && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
    } else if (timeRemaining === 0 && activeSession) {
      completeSession();
    }
    return () => clearInterval(interval);
  }, [activeSession, timeRemaining]);

  const loadSessionHistory = async () => {
    try {
      const response = await mindfulnessAPI.getActivities();
      setSessionHistory(response);
    } catch (error) {
      console.error('Error loading mindfulness history:', error);
    }
  };

  const startSession = (activity) => {
    if (!moodBefore) {
      alert('Please select your current neural state before initializing session.');
      return;
    }
    
    setActiveSession(activity);
    setTimeRemaining(activity.duration * 60);
  };

  const completeSession = async () => {
    if (!activeSession || !moodAfter) return;

    setLoading(true);
    try {
      await mindfulnessAPI.createSession({
        activity_type: activeSession.id,
        duration: activeSession.duration,
        mood_before: moodBefore,
        mood_after: moodAfter
      });

      alert('Neural session completed successfully! Quantum patterns optimized.');
      setActiveSession(null);
      setMoodBefore('');
      setMoodAfter('');
      loadSessionHistory();
    } catch (error) {
      console.error('Error saving mindfulness session:', error);
      alert('Session completed, but neural storage encountered an error.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (activeSession) {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
          <LiquidCard holographic className="max-w-2xl w-full">
            <div className="p-8 text-center">
              {/* Session Header */}
              <div className="text-6xl mb-4 animate-pulse">{activeSession.icon}</div>
              <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
                {activeSession.name}
              </h1>
              
              {/* Quantum Timer */}
              <div className="text-6xl font-mono text-neon-cyan mb-6 glow-cyan">
                {formatTime(timeRemaining)}
              </div>

              {/* Progress Circle */}
              <div className="relative w-32 h-32 mx-auto mb-6">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="rgba(0, 255, 255, 0.2)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="var(--neon-cyan)"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (timeRemaining / (activeSession.duration * 60))}`}
                    className="transition-all duration-1000 ease-linear"
                    style={{ filter: 'drop-shadow(0 0 10px var(--neon-cyan))' }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 rounded-full bg-gradient-primary opacity-50 animate-pulse" />
                </div>
              </div>
              
              {/* Neural Instructions */}
              <LiquidCard className="mb-6">
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-primary mb-3">Neural Protocol</h3>
                  <p className="text-secondary leading-relaxed">{activeSession.instructions}</p>
                </div>
              </LiquidCard>

              {/* Post-Session Mood Selection */}
              {timeRemaining === 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-primary mb-4">Post-Session Neural State</h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                    {moods.map((mood) => (
                      <button
                        key={mood.value}
                        onClick={() => setMoodAfter(mood.value)}
                        className={`
                          p-3 rounded-lg border-2 transition-all duration-300
                          ${moodAfter === mood.value
                            ? 'border-neon-cyan bg-glass-strong text-neon-cyan'
                            : 'border-primary/20 bg-glass hover:border-neon-cyan/50'
                          }
                        `}
                      >
                        <div className={`text-lg ${mood.color}`}>{mood.value}</div>
                      </button>
                    ))}
                  </div>
                  <LiquidButton
                    onClick={completeSession}
                    disabled={!moodAfter || loading}
                    className="w-full"
                  >
                    {loading ? 'Optimizing Neural Patterns...' : '⚡ Complete Neural Session'}
                  </LiquidButton>
                </div>
              )}

              {/* Breathing Animation */}
              {timeRemaining > 0 && activeSession.id === 'breathing' && (
                <div className="mt-6">
                  <div className="w-24 h-24 mx-auto rounded-full bg-gradient-primary opacity-60 animate-pulse" 
                       style={{ animationDuration: '4s' }} />
                  <p className="text-secondary mt-2">Follow the quantum rhythm</p>
                </div>
              )}
            </div>
          </LiquidCard>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-6xl mx-auto">
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
            🧘‍♀️ Neural Wellness Center
          </h1>
          <p className="text-secondary">Quantum consciousness optimization protocols</p>
        </div>

        {/* Neural State Selection */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">🧠</span>
              </div>
              <h2 className="text-xl font-bold text-primary">Current Neural State Assessment</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {moods.map((mood) => (
                <button
                  key={mood.value}
                  onClick={() => setMoodBefore(mood.value)}
                  className={`
                    p-4 rounded-lg border-2 transition-all duration-300
                    ${moodBefore === mood.value
                      ? 'border-neon-cyan bg-glass-strong text-neon-cyan'
                      : 'border-primary/20 bg-glass hover:border-neon-cyan/50'
                    }
                  `}
                >
                  <div className={`text-lg ${mood.color} mb-1`}>{mood.value.split(' ')[0]}</div>
                  <div className="text-xs text-secondary">{mood.value.split(' ')[1]}</div>
                </button>
              ))}
            </div>
          </div>
        </LiquidCard>

        {/* Mindfulness Protocols */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {mindfulnessActivities.map((activity) => (
            <LiquidCard
              key={activity.id}
              className="hover:scale-105 transform transition-all duration-300 cursor-pointer"
              onClick={() => startSession(activity)}
            >
              <div className={`p-6 bg-gradient-to-br ${activity.gradient} rounded-xl`}>
                {/* Activity Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl">{activity.icon}</div>
                  <div className="text-right">
                    <div className="text-sm text-secondary">Duration</div>
                    <div className="text-lg font-bold text-neon-cyan">{activity.duration}m</div>
                  </div>
                </div>

                {/* Activity Content */}
                <h3 className="text-xl font-bold text-primary mb-2">{activity.name}</h3>
                <p className="text-secondary mb-4">{activity.description}</p>

                {/* Neural Start Button */}
                <LiquidButton
                  disabled={!moodBefore}
                  className="w-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    startSession(activity);
                  }}
                >
                  {!moodBefore ? 'Select Neural State First' : `⚡ Initialize ${activity.name}`}
                </LiquidButton>

                {/* Data Stream */}
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
              </div>
            </LiquidCard>
          ))}
        </div>

        {/* Neural Session History */}
        {sessionHistory.length > 0 && (
          <LiquidCard>
            <div className="p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                  <span className="text-sm font-bold">📊</span>
                </div>
                <h2 className="text-xl font-bold text-primary">Neural Session Archive</h2>
              </div>
              
              <div className="space-y-3">
                {sessionHistory.slice(0, 5).map((session, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-glass rounded-lg border border-primary/20">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">
                        {mindfulnessActivities.find(a => a.id === session.activity_type)?.icon || '🧘‍♀️'}
                      </div>
                      <div>
                        <div className="font-medium text-primary capitalize">
                          {session.activity_type.replace('_', ' ')}
                        </div>
                        <div className="text-sm text-secondary">
                          {new Date(session.completed_at).toLocaleDateString()} • {session.duration} minutes
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-secondary">
                      {session.mood_before} → {session.mood_after}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </LiquidCard>
        )}
      </div>
    </div>
  );
};

export default MindfulnessComponent;