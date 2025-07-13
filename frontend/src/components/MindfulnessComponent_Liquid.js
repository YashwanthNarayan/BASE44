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
    { id: 'silence', name: 'Silence', icon: '🔇' },
    { id: 'rain', name: 'Rain Sounds', icon: '🌧️' },
    { id: 'forest', name: 'Forest Sounds', icon: '🌲' },
    { id: 'ocean', name: 'Ocean Waves', icon: '🌊' },
    { id: 'wind', name: 'Wind Sounds', icon: '💨' },
    { id: 'bells', name: 'Meditation Bells', icon: '🔔' },
    { id: 'white_noise', name: 'White Noise', icon: '📡' },
    { id: 'binaural', name: 'Binaural Beats', icon: '🎵' }
  ];

  const enhancedMindfulnessActivities = [
    // Breathing Exercises
    {
      id: 'box_breathing',
      name: 'Box Breathing',
      category: 'breathing',
      description: 'Military-grade stress regulation technique',
      duration: 5,
      icon: '📦',
      gradient: 'from-cyan-500/20 to-blue-500/20',
      instructions: 'Inhale 4 counts → Hold 4 counts → Exhale 4 counts → Hold 4 counts. Focus on creating a steady, rhythmic breathing pattern.',
      benefits: ['Reduces cortisol', 'Improves focus', 'Regulates heart rate'],
      difficulty: 'beginner'
    },
    {
      id: 'triangle_breathing',
      name: 'Triangle Breathing',
      category: 'breathing',
      description: 'Triangular respiratory technique',
      duration: 7,
      icon: '🔺',
      gradient: 'from-purple-500/20 to-pink-500/20',
      instructions: 'Inhale 3 counts → Hold 3 counts → Exhale 3 counts. Focus on the triangular breathing pattern.',
      benefits: ['Calms nervous system', 'Improves concentration', 'Reduces anxiety'],
      difficulty: 'beginner'
    },
    {
      id: 'wim_hof',
      name: 'Wim Hof Breathing',
      category: 'breathing',
      description: 'Advanced breathing method',
      duration: 15,
      icon: '❄️',
      gradient: 'from-blue-500/20 to-indigo-500/20',
      instructions: '30 rapid breaths → Hold after exhale → Repeat 3 cycles. This technique helps build resilience and focus.',
      benefits: ['Boosts immunity', 'Increases energy', 'Improves cold tolerance'],
      difficulty: 'advanced'
    },

    // Meditation
    {
      id: 'mindfulness_scan',
      name: 'Body Scan Meditation',
      category: 'meditation',
      description: 'Progressive body awareness practice',
      duration: 12,
      icon: '🔍',
      gradient: 'from-green-500/20 to-emerald-500/20',
      instructions: 'Systematically scan each body region. Identify tension, observe without judgment, release with mindful intention.',
      benefits: ['Body awareness', 'Stress release', 'Improved sleep'],
      difficulty: 'intermediate'
    },
    {
      id: 'loving_kindness',
      name: 'Loving Kindness Meditation',
      category: 'meditation',
      description: 'Compassion enhancement practice',
      duration: 10,
      icon: '💝',
      gradient: 'from-pink-500/20 to-rose-500/20',
      instructions: 'Generate loving-kindness for self → loved ones → neutral people → difficult people → all beings.',
      benefits: ['Increases empathy', 'Reduces negativity', 'Improves relationships'],
      difficulty: 'intermediate'
    },
    {
      id: 'zen_counting',
      name: 'Counting Meditation',
      category: 'meditation',
      description: 'Focused attention training',
      duration: 8,
      icon: '🔢',
      gradient: 'from-yellow-500/20 to-orange-500/20',
      instructions: 'Count breaths from 1 to 10, restart when mind wanders. Each count strengthens focus and concentration.',
      benefits: ['Improves concentration', 'Reduces mind wandering', 'Builds patience'],
      difficulty: 'beginner'
    },

    // Relaxation
    {
      id: 'progressive_muscle',
      name: 'Progressive Muscle Relaxation',
      category: 'relaxation',
      description: 'Systematic muscle tension release',
      duration: 15,
      icon: '💪',
      gradient: 'from-violet-500/20 to-purple-500/20',
      instructions: 'Tense each muscle group for 5 seconds, then release. Start with toes, progress to head.',
      benefits: ['Releases physical tension', 'Improves sleep quality', 'Reduces chronic pain'],
      difficulty: 'beginner'
    },
    {
      id: 'visualization',
      name: 'Guided Visualization',
      category: 'relaxation',
      description: 'Peaceful scene visualization',
      duration: 12,
      icon: '🏞️',
      gradient: 'from-teal-500/20 to-cyan-500/20',
      instructions: 'Create a perfect peaceful sanctuary. Engage all senses: visual, auditory, tactile, olfactory details.',
      benefits: ['Reduces stress hormones', 'Enhances creativity', 'Improves mood'],
      difficulty: 'intermediate'
    },

    // Focus Training
    {
      id: 'single_point',
      name: 'Single-Point Focus',
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
      name: 'Open Monitoring',
      category: 'focus',
      description: 'Wide-spectrum awareness training',
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
      name: 'Sleep Stories',
      category: 'sleep',
      description: 'Guided sleep preparation',
      duration: 20,
      icon: '📖',
      gradient: 'from-slate-500/20 to-gray-500/20',
      instructions: 'Listen to calming narrative while progressively relaxing. Let the story guide you into a restful state.',
      benefits: ['Improves sleep onset', 'Reduces sleep anxiety', 'Enhances sleep quality'],
      difficulty: 'beginner'
    },
    {
      id: 'yoga_nidra',
      name: 'Yoga Nidra',
      category: 'sleep',
      description: 'Conscious relaxation practice',
      duration: 25,
      icon: '🕉️',
      gradient: 'from-purple-500/20 to-indigo-500/20',
      instructions: 'Systematic relaxation through body awareness, breath, and intention. Remain aware while body rests.',
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
    loadPersonalStats();
    loadTodayProgress();
  }, []);

  useEffect(() => {
    let interval;
    if (activeSession && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
        
        // Update breathing animation phases
        if (activeSession.category === 'breathing' && activeSession.id === 'box_breathing') {
          const cycleDuration = 16; // 4+4+4+4 seconds
          const currentPhaseTime = timeRemaining % cycleDuration;
          
          if (currentPhaseTime >= 12) setBreathingPhase('inhale');
          else if (currentPhaseTime >= 8) setBreathingPhase('hold-in');
          else if (currentPhaseTime >= 4) setBreathingPhase('exhale');
          else setBreathingPhase('hold-out');
        }
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

  const loadPersonalStats = () => {
    // Simulate loading personal stats - in real app this would come from API
    setPersonalStats({
      totalSessions: sessionHistory.length,
      totalMinutes: sessionHistory.reduce((sum, session) => sum + session.duration, 0),
      streakDays: 3,
      favoriteCategory: 'breathing',
      moodImprovement: 1.2 // average mood improvement per session
    });
  };

  const loadTodayProgress = () => {
    const today = new Date().toDateString();
    const todaySessions = sessionHistory.filter(session => 
      new Date(session.completed_at).toDateString() === today
    );
    const minutesToday = todaySessions.reduce((sum, session) => sum + session.duration, 0);
    setTodayProgress(minutesToday);
  };

  const getFilteredActivities = () => {
    if (selectedCategory === 'all') {
      return enhancedMindfulnessActivities;
    }
    return enhancedMindfulnessActivities.filter(activity => activity.category === selectedCategory);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-400 bg-green-500/20';
      case 'intermediate': return 'text-yellow-400 bg-yellow-500/20';
      case 'advanced': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const startSession = (activity) => {
    if (!moodBefore) {
      alert('Please select your current neural state before initializing session.');
      return;
    }
    
    setActiveSession(activity);
    setTimeRemaining(activity.duration * 60);
    setBreathingCycle(0);
  };

  const completeSession = async () => {
    if (!activeSession || !moodAfter) return;

    setLoading(true);
    try {
      await mindfulnessAPI.createSession({
        activity_type: activeSession.id,
        duration: activeSession.duration,
        mood_before: moodBefore,
        mood_after: moodAfter,
        background_sound: selectedBackgroundSound
      });

      // Update progress
      setTodayProgress(prev => prev + activeSession.duration);
      
      alert('Neural session completed successfully! Quantum patterns optimized.');
      setActiveSession(null);
      setMoodBefore('');
      setMoodAfter('');
      loadSessionHistory();
      loadPersonalStats();
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

  const getRecommendedActivities = () => {
    if (!moodBefore) return [];
    
    const moodScore = moods.find(m => m.value === moodBefore)?.score || 3;
    
    if (moodScore <= 2) {
      // Stressed/Low mood - recommend stress relief and relaxation
      return enhancedMindfulnessActivities.filter(a => 
        a.category === 'stress' || a.category === 'relaxation'
      ).slice(0, 3);
    } else if (moodScore === 3) {
      // Neutral - recommend focus and breathing
      return enhancedMindfulnessActivities.filter(a => 
        a.category === 'focus' || a.category === 'breathing'
      ).slice(0, 3);
    } else {
      // Good/Excellent - recommend meditation and advanced practices
      return enhancedMindfulnessActivities.filter(a => 
        a.category === 'meditation' || a.difficulty === 'advanced'
      ).slice(0, 3);
    }
  };

  if (activeSession) {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
          <LiquidCard holographic className="max-w-4xl w-full">
            <div className="p-8 text-center">
              {/* Session Header */}
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-4">
                  <div className="text-4xl animate-pulse">{activeSession.icon}</div>
                  <div className="text-left">
                    <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                      {activeSession.name}
                    </h1>
                    <div className={`text-xs px-2 py-1 rounded ${getDifficultyColor(activeSession.difficulty)}`}>
                      {activeSession.difficulty}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-secondary">
                  Sound: {backgroundSounds.find(s => s.id === selectedBackgroundSound)?.name}
                </div>
              </div>
              
              {/* Enhanced Timer Display */}
              <div className="text-7xl font-mono text-neon-cyan mb-6 glow-cyan">
                {formatTime(timeRemaining)}
              </div>

              {/* Enhanced Progress Circle with breathing animation */}
              <div className="relative w-40 h-40 mx-auto mb-6">
                <svg className="w-40 h-40 transform -rotate-90">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke="rgba(0, 255, 255, 0.2)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke="var(--neon-cyan)"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 70}`}
                    strokeDashoffset={`${2 * Math.PI * 70 * (timeRemaining / (activeSession.duration * 60))}`}
                    className="transition-all duration-1000 ease-linear"
                    style={{ filter: 'drop-shadow(0 0 10px var(--neon-cyan))' }}
                  />
                </svg>
                
                {/* Breathing Animation Center */}
                {activeSession.category === 'breathing' && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className={`w-24 h-24 rounded-full bg-gradient-primary transition-all duration-4000 ease-in-out ${
                      breathingPhase === 'inhale' ? 'scale-125 opacity-80' :
                      breathingPhase === 'hold-in' ? 'scale-125 opacity-80' :
                      breathingPhase === 'exhale' ? 'scale-75 opacity-40' :
                      'scale-75 opacity-40'
                    }`} />
                    <div className="absolute text-sm font-semibold text-white">
                      {breathingPhase === 'inhale' ? 'Inhale' :
                       breathingPhase === 'hold-in' ? 'Hold' :
                       breathingPhase === 'exhale' ? 'Exhale' :
                       'Hold'}
                    </div>
                  </div>
                )}
                
                {/* General animation for other activities */}
                {activeSession.category !== 'breathing' && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-20 h-20 rounded-full bg-gradient-primary opacity-50 animate-pulse" />
                  </div>
                )}
              </div>
              
              {/* Neural Instructions & Benefits */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <LiquidCard className="text-left">
                  <div className="p-4">
                    <h3 className="text-lg font-semibold text-primary mb-3 flex items-center gap-2">
                      <span>🧠</span> Neural Protocol
                    </h3>
                    <p className="text-secondary leading-relaxed text-sm">{activeSession.instructions}</p>
                  </div>
                </LiquidCard>
                
                <LiquidCard className="text-left">
                  <div className="p-4">
                    <h3 className="text-lg font-semibold text-primary mb-3 flex items-center gap-2">
                      <span>⚡</span> Neural Benefits
                    </h3>
                    <ul className="text-secondary text-sm space-y-1">
                      {activeSession.benefits?.map((benefit, index) => (
                        <li key={index} className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 bg-neon-cyan rounded-full"></span>
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                </LiquidCard>
              </div>

              {/* Session Controls */}
              <div className="flex justify-center gap-4 mb-6">
                <LiquidButton
                  variant="secondary"
                  onClick={() => {
                    setActiveSession(null);
                    setTimeRemaining(0);
                  }}
                  className="px-8"
                >
                  🛑 End Session
                </LiquidButton>
                
                <LiquidButton
                  variant="secondary"
                  onClick={() => setTimeRemaining(prev => prev + 60)}
                  className="px-8"
                >
                  ⏱️ +1 Minute
                </LiquidButton>
              </div>

              {/* Post-Session Mood Selection */}
              {timeRemaining === 0 && (
                <div className="mb-6 p-6 bg-glass rounded-lg border border-primary/20">
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

              {/* Special Activity Features */}
              {activeSession.id === 'box_breathing' && timeRemaining > 0 && (
                <div className="mt-6 p-4 bg-glass rounded-lg">
                  <div className="text-sm text-secondary mb-2">Box Breathing Visualization</div>
                  <div className="relative w-24 h-24 mx-auto border-2 border-neon-cyan">
                    <div className={`absolute w-2 h-2 bg-neon-cyan transition-all duration-4000 ease-linear ${
                      breathingPhase === 'inhale' ? 'top-0 left-0' :
                      breathingPhase === 'hold-in' ? 'top-0 right-0' :
                      breathingPhase === 'exhale' ? 'bottom-0 right-0' :
                      'bottom-0 left-0'
                    }`} />
                  </div>
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
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Enhanced Header */}
        <div className="text-center mb-8">
          <LiquidButton
            variant="secondary"
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4"
          >
            ← Neural Dashboard
          </LiquidButton>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            🧘‍♀️ Wellness & Mindfulness Center
          </h1>
          <p className="text-secondary">Stress management & mindfulness training programs</p>
        </div>

        {/* Daily Progress & Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <LiquidCard className="text-center">
            <div className="p-4">
              <div className="text-3xl mb-2">🎯</div>
              <div className="text-2xl font-bold text-neon-cyan">{todayProgress}/{dailyGoal}</div>
              <div className="text-sm text-secondary">Today's Minutes</div>
              <LiquidProgress value={todayProgress} max={dailyGoal} className="mt-2" />
            </div>
          </LiquidCard>
          
          <LiquidCard className="text-center">
            <div className="p-4">
              <div className="text-3xl mb-2">🔥</div>
              <div className="text-2xl font-bold text-neon-orange">{personalStats?.streakDays || 0}</div>
              <div className="text-sm text-secondary">Day Streak</div>
            </div>
          </LiquidCard>
          
          <LiquidCard className="text-center">
            <div className="p-4">
              <div className="text-3xl mb-2">⏱️</div>
              <div className="text-2xl font-bold text-neon-green">{personalStats?.totalMinutes || 0}</div>
              <div className="text-sm text-secondary">Total Minutes</div>
            </div>
          </LiquidCard>
          
          <LiquidCard className="text-center">
            <div className="p-4">
              <div className="text-3xl mb-2">📈</div>
              <div className="text-2xl font-bold text-neon-purple">+{(personalStats?.moodImprovement || 0).toFixed(1)}</div>
              <div className="text-sm text-secondary">Mood Boost</div>
            </div>
          </LiquidCard>
        </div>

        {/* Background Sound Selection */}
        <LiquidCard className="mb-8">
          <div className="p-6">
            <h2 className="text-xl font-bold text-primary mb-4 flex items-center gap-2">
              <span>🎵</span> Background Sound Environment
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {backgroundSounds.map((sound) => (
                <button
                  key={sound.id}
                  onClick={() => setSelectedBackgroundSound(sound.id)}
                  className={`
                    p-3 rounded-lg border-2 transition-all duration-300 text-center
                    ${selectedBackgroundSound === sound.id
                      ? 'border-neon-cyan bg-glass-strong text-neon-cyan'
                      : 'border-primary/20 bg-glass hover:border-neon-cyan/50'
                    }
                  `}
                >
                  <div className="text-xl mb-1">{sound.icon}</div>
                  <div className="text-xs">{sound.name}</div>
                </button>
              ))}
            </div>
          </div>
        </LiquidCard>

        {/* Current Neural State Assessment */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">🧠</span>
              </div>
              <h2 className="text-xl font-bold text-primary">Current Mood Assessment</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
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
            
            {/* Personalized Recommendations */}
            {moodBefore && (
              <div className="mt-6 p-4 bg-glass rounded-lg border border-primary/20">
                <h3 className="text-lg font-semibold text-primary mb-3">🎯 Recommended Protocols</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {getRecommendedActivities().map((activity) => (
                    <div key={activity.id} className="p-3 bg-glass-strong rounded-lg border border-primary/10 text-center">
                      <div className="text-2xl mb-1">{activity.icon}</div>
                      <div className="text-sm font-medium text-primary">{activity.name}</div>
                      <div className="text-xs text-secondary">{activity.duration}m</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </LiquidCard>

        {/* Category Filters */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-primary mb-4">Protocol Categories</h2>
          <div className="flex flex-wrap gap-3">
            {mindfulnessCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`
                  px-4 py-2 rounded-lg border-2 transition-all duration-300 flex items-center gap-2
                  ${selectedCategory === category.id
                    ? 'border-neon-cyan bg-glass-strong text-neon-cyan'
                    : 'border-primary/20 bg-glass hover:border-neon-cyan/50'
                  }
                `}
              >
                <span>{category.icon}</span>
                <span className="text-sm font-medium">{category.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Enhanced Mindfulness Protocols Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {getFilteredActivities().map((activity) => (
            <LiquidCard
              key={activity.id}
              className="hover:scale-105 transform transition-all duration-300 cursor-pointer group"
              onClick={() => startSession(activity)}
            >
              <div className={`p-6 bg-gradient-to-br ${activity.gradient} rounded-xl relative overflow-hidden`}>
                {/* Activity Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl group-hover:scale-110 transition-transform duration-300">
                    {activity.icon}
                  </div>
                  <div className="text-right">
                    <div className={`text-xs px-2 py-1 rounded mb-1 ${getDifficultyColor(activity.difficulty)}`}>
                      {activity.difficulty}
                    </div>
                    <div className="text-sm text-secondary">Duration</div>
                    <div className="text-lg font-bold text-neon-cyan">{activity.duration}m</div>
                  </div>
                </div>

                {/* Activity Content */}
                <h3 className="text-xl font-bold text-primary mb-2">{activity.name}</h3>
                <p className="text-secondary mb-4 text-sm">{activity.description}</p>

                {/* Benefits Preview */}
                {activity.benefits && (
                  <div className="mb-4">
                    <div className="text-xs text-secondary mb-2">Key Benefits:</div>
                    <div className="flex flex-wrap gap-1">
                      {activity.benefits.slice(0, 2).map((benefit, index) => (
                        <span key={index} className="text-xs bg-white/10 px-2 py-1 rounded">
                          {benefit}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

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

                {/* Quantum Data Stream */}
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
              </div>
            </LiquidCard>
          ))}
        </div>

        {/* Achievements Section */}
        <LiquidCard className="mb-8">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-primary flex items-center gap-2">
                <span>🏆</span> Achievements
              </h2>
              <LiquidButton
                variant="secondary"
                onClick={() => setShowAchievements(!showAchievements)}
              >
                {showAchievements ? 'Hide' : 'Show All'}
              </LiquidButton>
            </div>
            
            <div className={`grid grid-cols-2 md:grid-cols-5 gap-4 ${showAchievements ? '' : 'max-h-20 overflow-hidden'}`}>
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`p-4 rounded-lg border-2 text-center transition-all duration-300 ${
                    achievement.unlocked
                      ? 'border-yellow-400 bg-yellow-500/10 text-yellow-400'
                      : 'border-gray-500 bg-gray-500/10 text-gray-500'
                  }`}
                >
                  <div className="text-2xl mb-2">{achievement.icon}</div>
                  <div className="text-sm font-medium">{achievement.name}</div>
                  <div className="text-xs text-secondary">{achievement.description}</div>
                </div>
              ))}
            </div>
          </div>
        </LiquidCard>

        {/* Enhanced Session History */}
        {sessionHistory.length > 0 && (
          <LiquidCard>
            <div className="p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                  <span className="text-sm font-bold">📊</span>
                </div>
                <h2 className="text-xl font-bold text-primary">Session Archive</h2>
              </div>
              
              <div className="space-y-3">
                {sessionHistory.slice(0, 5).map((session, index) => {
                  const activity = enhancedMindfulnessActivities.find(a => a.id === session.activity_type);
                  return (
                    <div key={index} className="flex justify-between items-center p-4 bg-glass rounded-lg border border-primary/20">
                      <div className="flex items-center space-x-4">
                        <div className="text-2xl">
                          {activity?.icon || '🧘‍♀️'}
                        </div>
                        <div>
                          <div className="font-medium text-primary">
                            {activity?.name || session.activity_type.replace('_', ' ')}
                          </div>
                          <div className="text-sm text-secondary">
                            {new Date(session.completed_at).toLocaleDateString()} • {session.duration} minutes
                          </div>
                          {activity?.category && (
                            <div className="text-xs text-secondary capitalize">
                              {activity.category} • {activity.difficulty}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-primary">
                          {session.mood_before} → {session.mood_after}
                        </div>
                        {session.background_sound && (
                          <div className="text-xs text-secondary">
                            🎵 {backgroundSounds.find(s => s.id === session.background_sound)?.name}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </LiquidCard>
        )}
      </div>
    </div>
  );
};

export default MindfulnessComponent;