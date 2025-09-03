import React, { useState, useEffect } from 'react';
import NavigationBar_Modern from './NavigationBar_Modern';
import { 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernBadge,
  ModernProgress,
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernGrid,
  ModernSpinner
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

const MindfulnessComponent_Modern = ({ student, onNavigate }) => {
  const [activeSession, setActiveSession] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [breathingPhase, setBreathingPhase] = useState('inhale');
  const [breathingCycle, setBreathingCycle] = useState(0);
  const [todayProgress, setTodayProgress] = useState(0);
  const [dailyGoal, setDailyGoal] = useState(10); // minutes

  const mindfulnessCategories = [
    { id: 'all', name: 'All Activities', color: 'gray' },
    { id: 'breathing', name: 'Breathing', color: 'blue' },
    { id: 'meditation', name: 'Meditation', color: 'purple' },
    { id: 'relaxation', name: 'Relaxation', color: 'green' },
    { id: 'focus', name: 'Focus', color: 'indigo' },
    { id: 'sleep', name: 'Sleep', color: 'violet' },
    { id: 'stress', name: 'Stress Relief', color: 'emerald' }
  ];

  const enhancedMindfulnessActivities = [
    // Breathing Exercises
    {
      id: 'box_breathing',
      name: 'Box Breathing',
      category: 'breathing',
      description: 'Structured breathing technique for focus and calm',
      duration: 5,
      color: 'blue'
    },
    {
      id: 'deep_breathing',
      name: 'Deep Breathing',
      category: 'breathing',
      description: 'Simple, effective breathing for instant relaxation',
      duration: 3,
      color: 'cyan'
    },
    // Meditation
    {
      id: 'body_scan',
      name: 'Body Scan Meditation',
      category: 'meditation',
      description: 'Progressive awareness of physical sensations',
      duration: 10,
      color: 'purple'
    },
    {
      id: 'mindful_observation',
      name: 'Mindful Observation',
      category: 'meditation',
      description: 'Present-moment awareness exercise',
      duration: 7,
      color: 'violet'
    },
    // Relaxation
    {
      id: 'progressive_relaxation',
      name: 'Progressive Muscle Relaxation',
      category: 'relaxation',
      description: 'Systematic tension release for deep relaxation',
      duration: 15,
      color: 'green'
    },
    {
      id: 'visualization',
      name: 'Guided Visualization',
      category: 'relaxation',
      description: 'Mental imagery for peace and calm',
      duration: 12,
      color: 'emerald'
    },
    // Focus
    {
      id: 'concentration',
      name: 'Concentration Training',
      category: 'focus',
      description: 'Build sustained attention and mental clarity',
      duration: 8,
      color: 'indigo'
    },
    {
      id: 'study_focus',
      name: 'Study Focus Session',
      category: 'focus',
      description: 'Optimize mental state for learning',
      duration: 5,
      color: 'blue'
    }
  ];

  const filteredActivities = selectedCategory === 'all' 
    ? enhancedMindfulnessActivities 
    : enhancedMindfulnessActivities.filter(activity => activity.category === selectedCategory);

  const startSession = (activity) => {
    setActiveSession(activity);
    setTimeRemaining(activity.duration * 60); // Convert to seconds
    setBreathingPhase('inhale');
    setBreathingCycle(0);
  };

  const endSession = () => {
    setActiveSession(null);
    setTimeRemaining(0);
    setTodayProgress(prev => prev + (activeSession?.duration || 0));
  };

  useEffect(() => {
    let timer;
    if (activeSession && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            endSession();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [activeSession, timeRemaining]);

  // Breathing animation effect
  useEffect(() => {
    if (activeSession?.category === 'breathing') {
      const breathingTimer = setInterval(() => {
        setBreathingPhase(prev => {
          if (prev === 'inhale') return 'hold1';
          if (prev === 'hold1') return 'exhale';
          if (prev === 'exhale') return 'hold2';
          setBreathingCycle(cycle => cycle + 1);
          return 'inhale';
        });
      }, 4000); // 4 second cycles

      return () => clearInterval(breathingTimer);
    }
  }, [activeSession]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'border-blue-500 bg-blue-50 text-blue-900 hover:border-blue-600',
      purple: 'border-purple-500 bg-purple-50 text-purple-900 hover:border-purple-600',
      green: 'border-green-500 bg-green-50 text-green-900 hover:border-green-600',
      indigo: 'border-indigo-500 bg-indigo-50 text-indigo-900 hover:border-indigo-600',
      cyan: 'border-cyan-500 bg-cyan-50 text-cyan-900 hover:border-cyan-600',
      violet: 'border-violet-500 bg-violet-50 text-violet-900 hover:border-violet-600',
      emerald: 'border-emerald-500 bg-emerald-50 text-emerald-900 hover:border-emerald-600',
      gray: 'border-gray-500 bg-gray-50 text-gray-900 hover:border-gray-600'
    };
    return colorMap[color] || colorMap.gray;
  };

  // Active Session View
  if (activeSession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <NavigationBar_Modern 
          user={student}
          currentPage="mindfulness"
          onNavigate={onNavigate}
          onLogout={() => onNavigate('auth')}
        />

        <ModernContainer className="py-8">
          <div className="text-center">
            {/* Session Header */}
            <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-4">
              {activeSession.name}
            </ModernHeading>
            <ModernText variant="body-large" className="text-gray-600 font-medium mb-8">
              {activeSession.description}
            </ModernText>

            {/* Timer Display */}
            <ModernCard className="max-w-md mx-auto mb-8">
              <ModernCardBody className="text-center py-12">
                <div className="text-6xl font-bold text-indigo-600 mb-4">
                  {formatTime(timeRemaining)}
                </div>
                <ModernProgress 
                  value={((activeSession.duration * 60) - timeRemaining)} 
                  max={activeSession.duration * 60}
                  className="mb-4"
                />
                <ModernText variant="body-small" className="text-gray-500">
                  {Math.round(((activeSession.duration * 60) - timeRemaining) / (activeSession.duration * 60) * 100)}% Complete
                </ModernText>
              </ModernCardBody>
            </ModernCard>

            {/* Breathing Animation */}
            {activeSession.category === 'breathing' && (
              <ModernCard className="max-w-md mx-auto mb-8">
                <ModernCardBody className="py-12">
                  <div className="flex flex-col items-center">
                    <div 
                      className={`w-32 h-32 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 transition-transform duration-4000 ease-in-out mb-6 ${
                        breathingPhase === 'inhale' ? 'scale-125' : 
                        breathingPhase === 'exhale' ? 'scale-75' : 'scale-100'
                      }`}
                    />
                    <ModernHeading level={3} className="text-2xl font-semibold text-gray-800 mb-2">
                      {breathingPhase === 'inhale' ? 'Breathe In' : 
                       breathingPhase === 'exhale' ? 'Breathe Out' : 'Hold'}
                    </ModernHeading>
                    <ModernText variant="body-small" className="text-gray-600">
                      Cycle {breathingCycle + 1}
                    </ModernText>
                  </div>
                </ModernCardBody>
              </ModernCard>
            )}

            {/* Session Controls */}
            <div className="flex justify-center gap-4">
              <ModernButton variant="secondary" onClick={endSession}>
                End Session
              </ModernButton>
            </div>
          </div>
        </ModernContainer>
      </div>
    );
  }

  // Main Mindfulness Dashboard
  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="mindfulness"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd"/>
            </svg>
          </div>
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-4">
            Mindfulness & Well-being
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Improve focus, reduce stress, and enhance your learning experience
          </ModernText>
        </div>

        {/* Daily Progress */}
        <ModernCard className="mb-8">
          <ModernCardHeader>
            <ModernHeading level={4} className="text-gray-800 font-semibold">Today's Progress</ModernHeading>
          </ModernCardHeader>
          <ModernCardBody>
            <div className="flex items-center justify-between mb-4">
              <ModernText variant="body" className="text-gray-700 font-medium">
                {todayProgress} of {dailyGoal} minutes completed
              </ModernText>
              <ModernBadge variant={todayProgress >= dailyGoal ? 'success' : 'secondary'}>
                {Math.round((todayProgress / dailyGoal) * 100)}%
              </ModernBadge>
            </div>
            <ModernProgress 
              value={todayProgress} 
              max={dailyGoal}
              label="Daily Goal Progress"
            />
          </ModernCardBody>
        </ModernCard>

        {/* Category Filter */}
        <div className="mb-8">
          <ModernHeading level={4} className="mb-6 text-gray-800 font-semibold">Browse Categories</ModernHeading>
          <div className="flex flex-wrap gap-3">
            {mindfulnessCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-full border-2 transition-all duration-300 font-medium text-sm ${
                  selectedCategory === category.id
                    ? getColorClasses(category.color)
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Activities Grid */}
        <ModernGrid cols={3} className="mb-8">
          {filteredActivities.map((activity) => (
            <ModernCard key={activity.id} hover={true} className="cursor-pointer">
              <ModernCardBody>
                <div className="text-center">
                  <div className={`w-12 h-12 rounded-xl mx-auto mb-4 flex items-center justify-center border-2 ${getColorClasses(activity.color)}`}>
                    <div className="w-6 h-6 bg-current rounded opacity-80"></div>
                  </div>
                  <ModernHeading level={4} className="text-gray-800 font-semibold mb-2">
                    {activity.name}
                  </ModernHeading>
                  <ModernText variant="body-small" className="text-gray-600 mb-4 font-medium">
                    {activity.description}
                  </ModernText>
                  <div className="flex items-center justify-between mb-4">
                    <ModernBadge variant="secondary">
                      {activity.duration} min
                    </ModernBadge>
                    <ModernBadge variant="primary">
                      {activity.category}
                    </ModernBadge>
                  </div>
                  <ModernButton
                    variant="primary"
                    className="w-full font-medium"
                    onClick={() => startSession(activity)}
                  >
                    Start Session
                  </ModernButton>
                </div>
              </ModernCardBody>
            </ModernCard>
          ))}
        </ModernGrid>

        {/* Quick Tips */}
        <ModernCard>
          <ModernCardHeader>
            <ModernHeading level={4} className="text-gray-800 font-semibold">Mindfulness Tips</ModernHeading>
          </ModernCardHeader>
          <ModernCardBody>
            <ModernGrid cols={2}>
              <div>
                <ModernHeading level={5} className="text-gray-700 font-semibold mb-2">For Better Focus</ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 font-medium">
                  Practice 5 minutes of breathing exercises before study sessions to improve concentration and retention.
                </ModernText>
              </div>
              <div>
                <ModernHeading level={5} className="text-gray-700 font-semibold mb-2">Stress Relief</ModernHeading>
                <ModernText variant="body-small" className="text-gray-600 font-medium">
                  Use progressive relaxation techniques during breaks to reduce exam anxiety and mental fatigue.
                </ModernText>
              </div>
            </ModernGrid>
          </ModernCardBody>
        </ModernCard>
      </ModernContainer>
    </div>
  );
};

export default MindfulnessComponent_Modern;