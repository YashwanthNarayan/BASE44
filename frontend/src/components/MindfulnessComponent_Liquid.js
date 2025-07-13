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
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedBackgroundSound, setSelectedBackgroundSound] = useState('silence');
  const [breathingPhase, setBreathingPhase] = useState('inhale');
  const [breathingCycle, setBreathingCycle] = useState(0);
  const [personalStats, setPersonalStats] = useState(null);
  const [dailyGoal, setDailyGoal] = useState(10); // minutes
  const [todayProgress, setTodayProgress] = useState(0);
  const [showAchievements, setShowAchievements] = useState(false);

  const mindfulnessCategories = [
    { id: 'all', name: 'All Protocols', icon: '🧘‍♀️' },
    { id: 'breathing', name: 'Breathing', icon: '🫁' },
    { id: 'meditation', name: 'Meditation', icon: '🧠' },
    { id: 'relaxation', name: 'Relaxation', icon: '💆‍♀️' },
    { id: 'focus', name: 'Focus', icon: '🎯' },
    { id: 'sleep', name: 'Sleep', icon: '😴' },
    { id: 'stress', name: 'Stress Relief', icon: '🌿' }
  ];

  const backgroundSounds = [
    { id: 'silence', name: 'Quantum Silence', icon: '🔇' },
    { id: 'rain', name: 'Digital Rain', icon: '🌧️' },
    { id: 'forest', name: 'Bio-Forest', icon: '🌲' },
    { id: 'ocean', name: 'Cyber Ocean', icon: '🌊' },
    { id: 'wind', name: 'Neural Wind', icon: '💨' },
    { id: 'bells', name: 'Quantum Bells', icon: '🔔' },
    { id: 'white_noise', name: 'White Static', icon: '📡' },
    { id: 'binaural', name: 'Binaural Beats', icon: '🎵' }
  ];

  const enhancedMindfulnessActivities = [
    // Breathing Exercises
    {
      id: 'box_breathing',
      name: 'Quantum Box Breathing',
      category: 'breathing',
      description: 'Military-grade stress regulation protocol',
      duration: 5,
      icon: '📦',
      gradient: 'from-cyan-500/20 to-blue-500/20',
      instructions: 'Inhale 4 counts → Hold 4 counts → Exhale 4 counts → Hold 4 counts. Visualize quantum energy flowing through your neural pathways.',
      benefits: ['Reduces cortisol', 'Improves focus', 'Regulates heart rate'],
      difficulty: 'beginner'
    },
    {
      id: 'triangle_breathing',
      name: 'Neural Triangle Sync',
      category: 'breathing',
      description: 'Triangular respiratory optimization',
      duration: 7,
      icon: '🔺',
      gradient: 'from-purple-500/20 to-pink-500/20',
      instructions: 'Inhale 3 counts → Hold 3 counts → Exhale 3 counts. Focus on the triangular energy flow pattern.',
      benefits: ['Calms nervous system', 'Improves concentration', 'Reduces anxiety'],
      difficulty: 'beginner'
    },
    {
      id: 'wim_hof',
      name: 'Cryo-Neural Breathing',
      category: 'breathing',
      description: 'Advanced thermal regulation protocol',
      duration: 15,
      icon: '❄️',
      gradient: 'from-blue-500/20 to-indigo-500/20',
      instructions: '30 rapid breaths → Hold after exhale → Repeat 3 cycles. Activates cold-shock proteins and neural resilience.',
      benefits: ['Boosts immunity', 'Increases energy', 'Improves cold tolerance'],
      difficulty: 'advanced'
    },

    // Meditation
    {
      id: 'mindfulness_scan',
      name: 'Bio-Scan Meditation',
      category: 'meditation',
      description: 'Progressive consciousness mapping',
      duration: 12,
      icon: '🔍',
      gradient: 'from-green-500/20 to-emerald-500/20',
      instructions: 'Systematically scan each body region. Identify tension, observe without judgment, release with quantum intention.',
      benefits: ['Body awareness', 'Stress release', 'Improved sleep'],
      difficulty: 'intermediate'
    },
    {
      id: 'loving_kindness',
      name: 'Compassion Matrix',
      category: 'meditation',
      description: 'Neural empathy enhancement protocol',
      duration: 10,
      icon: '💝',
      gradient: 'from-pink-500/20 to-rose-500/20',
      instructions: 'Generate loving-kindness for self → loved ones → neutral people → difficult people → all beings.',
      benefits: ['Increases empathy', 'Reduces negativity', 'Improves relationships'],
      difficulty: 'intermediate'
    },
    {
      id: 'zen_counting',
      name: 'Quantum Counting Zen',
      category: 'meditation',
      description: 'Numerical consciousness anchor',
      duration: 8,
      icon: '🔢',
      gradient: 'from-yellow-500/20 to-orange-500/20',
      instructions: 'Count breaths from 1 to 10, restart when mind wanders. Each count strengthens neural focus pathways.',
      benefits: ['Improves concentration', 'Reduces mind wandering', 'Builds patience'],
      difficulty: 'beginner'
    },

    // Relaxation
    {
      id: 'progressive_muscle',
      name: 'Systematic Muscle Release',
      category: 'relaxation',
      description: 'Targeted tension elimination protocol',
      duration: 15,
      icon: '💪',
      gradient: 'from-violet-500/20 to-purple-500/20',
      instructions: 'Tense each muscle group for 5 seconds, then release. Start with toes, progress to head.',
      benefits: ['Releases physical tension', 'Improves sleep quality', 'Reduces chronic pain'],
      difficulty: 'beginner'
    },
    {
      id: 'visualization',
      name: 'Quantum Sanctuary Visualization',
      category: 'relaxation',
      description: 'Neural-space construction protocol',
      duration: 12,
      icon: '🏞️',
      gradient: 'from-teal-500/20 to-cyan-500/20',
      instructions: 'Construct a perfect digital sanctuary. Engage all senses: visual, auditory, tactile, olfactory details.',
      benefits: ['Reduces stress hormones', 'Enhances creativity', 'Improves mood'],
      difficulty: 'intermediate'
    },

    // Focus Training
    {
      id: 'single_point',
      name: 'Laser Focus Protocol',
      category: 'focus',
      description: 'Concentration enhancement training',
      duration: 10,
      icon: '🎯',
      gradient: 'from-red-500/20 to-pink-500/20',
      instructions: 'Focus on a single point (breath, mantra, or visual). When mind wanders, gently return focus.',
      benefits: ['Improves attention span', 'Enhances cognitive control', 'Reduces distractibility'],
      difficulty: 'intermediate'
    },
    {
      id: 'open_monitoring',
      name: 'Panoramic Awareness',
      category: 'focus',
      description: 'Wide-spectrum consciousness training',
      duration: 15,
      icon: '👁️',
      gradient: 'from-indigo-500/20 to-blue-500/20',
      instructions: 'Observe all thoughts, feelings, sensations without attachment. Maintain panoramic awareness.',
      benefits: ['Increases mindfulness', 'Improves emotional regulation', 'Enhances metacognition'],
      difficulty: 'advanced'
    },

    // Sleep Preparation
    {
      id: 'sleep_stories',
      name: 'Neural Sleep Narrative',
      category: 'sleep',
      description: 'Consciousness transition protocol',
      duration: 20,
      icon: '📖',
      gradient: 'from-slate-500/20 to-gray-500/20',
      instructions: 'Listen to calming narrative while progressively relaxing. Let the story guide you into sleep state.',
      benefits: ['Improves sleep onset', 'Reduces sleep anxiety', 'Enhances sleep quality'],
      difficulty: 'beginner'
    },
    {
      id: 'yoga_nidra',
      name: 'Quantum Sleep Yoga',
      category: 'sleep',
      description: 'Conscious sleep induction protocol',
      duration: 25,
      icon: '🕉️',
      gradient: 'from-purple-500/20 to-indigo-500/20',
      instructions: 'Systematic relaxation through body awareness, breath, and intention. Remain conscious while body sleeps.',
      benefits: ['Deep restoration', 'Reduces insomnia', 'Enhances recovery'],
      difficulty: 'intermediate'
    },

    // Stress Relief
    {
      id: 'quick_calm',
      name: 'Emergency Calm Protocol',
      category: 'stress',
      description: 'Rapid stress deactivation sequence',
      duration: 3,
      icon: '🚨',
      gradient: 'from-red-500/20 to-orange-500/20',
      instructions: '4-7-8 breathing + grounding technique. Name 5 things you see, 4 you hear, 3 you feel, 2 you smell, 1 you taste.',
      benefits: ['Rapid stress relief', 'Anxiety reduction', 'Emotional reset'],
      difficulty: 'beginner'
    },
    {
      id: 'stress_release',
      name: 'Cortisol Neutralization',
      category: 'stress',
      description: 'Advanced stress hormone regulation',
      duration: 18,
      icon: '🌿',
      gradient: 'from-green-500/20 to-teal-500/20',
      instructions: 'Combine breathwork, body scanning, and positive visualization to systematically release stress accumulation.',
      benefits: ['Lowers cortisol', 'Improves immunity', 'Enhances wellbeing'],
      difficulty: 'intermediate'
    }
  ];

  const achievements = [
    { id: 'first_session', name: 'Neural Pioneer', description: 'Complete your first mindfulness session', icon: '🎖️', unlocked: false },
    { id: 'week_streak', name: 'Consistency Matrix', description: 'Practice 7 days in a row', icon: '🔥', unlocked: false },
    { id: 'total_hours', name: 'Zen Master', description: 'Complete 10 hours of practice', icon: '🧙‍♂️', unlocked: false },
    { id: 'all_categories', name: 'Protocol Explorer', description: 'Try all activity categories', icon: '🗺️', unlocked: false },
    { id: 'advanced_user', name: 'Neural Expert', description: 'Complete 5 advanced protocols', icon: '🚀', unlocked: false }
  ];

  const moods = [
    { value: '😊 Excellent', color: 'text-neon-green', score: 5 },
    { value: '🙂 Good', color: 'text-neon-cyan', score: 4 },
    { value: '😐 Neutral', color: 'text-neon-yellow', score: 3 },
    { value: '😔 Low', color: 'text-neon-magenta', score: 2 },
    { value: '😰 Stressed', color: 'text-neon-pink', score: 1 }
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