import React, { useState, useEffect } from 'react';
import { LiquidButton } from './ui/LiquidComponents';

const StudyTimer = ({ studyPlan, onSessionComplete, onTimerStop }) => {
  const [currentSessionIndex, setCurrentSessionIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  const [currentTime, setCurrentTime] = useState(new Date());

  const currentSession = studyPlan?.pomodoro_sessions?.[currentSessionIndex];
  const totalSessions = studyPlan?.pomodoro_sessions?.length || 0;

  // Update current time every second
  useEffect(() => {
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timeInterval);
  }, []);

  useEffect(() => {
    if (studyPlan && studyPlan.pomodoro_sessions && studyPlan.pomodoro_sessions.length > 0) {
      // Calculate which session should be active based on actual time
      const now = new Date();
      const actualStartTime = studyPlan.actual_start_time ? new Date(studyPlan.actual_start_time) : now;
      
      // Calculate elapsed time since session started
      const elapsedSeconds = Math.floor((now - actualStartTime) / 1000);
      
      // Find which session should be active and how much time is remaining
      let totalElapsed = 0;
      let activeSessionIndex = 0;
      let sessionStartElapsed = 0;
      
      for (let i = 0; i < studyPlan.pomodoro_sessions.length; i++) {
        const sessionDuration = studyPlan.pomodoro_sessions[i].duration_minutes * 60;
        
        if (elapsedSeconds >= totalElapsed && elapsedSeconds < totalElapsed + sessionDuration) {
          activeSessionIndex = i;
          sessionStartElapsed = totalElapsed;
          break;
        }
        
        totalElapsed += sessionDuration;
        
        // If we've passed all sessions, stop at the last one
        if (i === studyPlan.pomodoro_sessions.length - 1) {
          activeSessionIndex = i;
          sessionStartElapsed = totalElapsed - sessionDuration;
        }
      }
      
      // Calculate remaining time in current session
      const currentSessionDuration = studyPlan.pomodoro_sessions[activeSessionIndex].duration_minutes * 60;
      const timeIntoCurrentSession = elapsedSeconds - sessionStartElapsed;
      const remainingTime = Math.max(0, currentSessionDuration - timeIntoCurrentSession);
      
      setCurrentSessionIndex(activeSessionIndex);
      setTimeRemaining(remainingTime);
      setIsActive(remainingTime > 0);
    }
  }, [studyPlan]);

  useEffect(() => {
    let interval = null;
    
    if (isActive && !isPaused && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => {
          if (time <= 1) {
            // Session completed
            handleSessionComplete();
            return 0;
          }
          return time - 1;
        });
      }, 1000);
    } else if (timeRemaining === 0) {
      clearInterval(interval);
    }
    
    return () => clearInterval(interval);
  }, [isActive, isPaused, timeRemaining]);

  const handleSessionComplete = () => {
    // Check if there are more sessions
    if (currentSessionIndex < totalSessions - 1) {
      // Move to next session
      const nextIndex = currentSessionIndex + 1;
      const nextSession = studyPlan.pomodoro_sessions[nextIndex];
      
      setCurrentSessionIndex(nextIndex);
      setTimeRemaining(nextSession.duration_minutes * 60);
      
      // Notify parent component
      if (onSessionComplete) {
        onSessionComplete(currentSession, nextSession);
      }
      
      // Show notification
      showSessionNotification(nextSession);
    } else {
      // All sessions completed
      setIsActive(false);
      showCompletionNotification();
      if (onSessionComplete) {
        onSessionComplete(currentSession, null);
      }
    }
  };

  // Add a sync function to periodically check time accuracy
  useEffect(() => {
    if (!isActive || !studyPlan?.actual_start_time) return;
    
    // Sync with actual time every 30 seconds to prevent drift
    const syncInterval = setInterval(() => {
      const now = new Date();
      const actualStartTime = new Date(studyPlan.actual_start_time);
      const elapsedSeconds = Math.floor((now - actualStartTime) / 1000);
      
      // Find current session and remaining time
      let totalElapsed = 0;
      let correctSessionIndex = 0;
      let sessionStartElapsed = 0;
      
      for (let i = 0; i < studyPlan.pomodoro_sessions.length; i++) {
        const sessionDuration = studyPlan.pomodoro_sessions[i].duration_minutes * 60;
        
        if (elapsedSeconds >= totalElapsed && elapsedSeconds < totalElapsed + sessionDuration) {
          correctSessionIndex = i;
          sessionStartElapsed = totalElapsed;
          break;
        }
        
        totalElapsed += sessionDuration;
      }
      
      // Only update if we're off by more than 2 seconds
      if (correctSessionIndex !== currentSessionIndex) {
        setCurrentSessionIndex(correctSessionIndex);
        const currentSessionDuration = studyPlan.pomodoro_sessions[correctSessionIndex].duration_minutes * 60;
        const timeIntoCurrentSession = elapsedSeconds - sessionStartElapsed;
        const correctTimeRemaining = Math.max(0, currentSessionDuration - timeIntoCurrentSession);
        setTimeRemaining(correctTimeRemaining);
      }
    }, 30000); // Sync every 30 seconds
    
    return () => clearInterval(syncInterval);
  }, [isActive, studyPlan?.actual_start_time, currentSessionIndex]);

  const showSessionNotification = (session) => {
    if (Notification.permission === 'granted') {
      const title = session.session_type === 'work' 
        ? `📚 ${session.subject} Study Time!`
        : `☕ Break Time!`;
      const body = session.session_type === 'work'
        ? `Focus on ${session.subject} for ${session.duration_minutes} minutes`
        : `Take a ${session.duration_minutes} minute break - ${session.break_activity}`;
      
      new Notification(title, { body, icon: '/favicon.ico' });
    }
  };

  const showCompletionNotification = () => {
    if (Notification.permission === 'granted') {
      new Notification('🎉 Study Session Complete!', {
        body: 'Congratulations! You completed your entire study plan.',
        icon: '/favicon.ico'
      });
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getSessionEmoji = (session) => {
    if (session.session_type === 'break') return '☕';
    
    const subjectEmojis = {
      'math': '🔢',
      'physics': '⚛️',
      'chemistry': '🧪',
      'biology': '🧬',
      'english': '📚',
      'history': '🏛️',
      'geography': '🌍'
    };
    
    return subjectEmojis[session.subject?.toLowerCase()] || '📖';
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  const stopTimer = () => {
    setIsActive(false);
    setIsPaused(false);
    if (onTimerStop) {
      onTimerStop();
    }
  };

  const skipSession = () => {
    if (currentSessionIndex < totalSessions - 1) {
      handleSessionComplete();
    } else {
      stopTimer();
    }
  };

  // Request notification permission on mount
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  if (!isActive || !currentSession || !isVisible) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-dark-surface/95 backdrop-blur-md border-b border-primary/20 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Session Info */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full bg-gradient-secondary flex items-center justify-center text-xl">
                {getSessionEmoji(currentSession)}
              </div>
              <div>
                <div className="font-bold text-lg text-primary">
                  {currentSession.session_type === 'work' 
                    ? `${currentSession.subject?.charAt(0).toUpperCase()}${currentSession.subject?.slice(1)} Study`
                    : 'Break Time'
                  }
                </div>
                <div className="text-sm text-secondary">
                  {currentSession.session_type === 'work' 
                    ? 'Focus and learn' 
                    : currentSession.break_activity || 'Take a rest'
                  }
                </div>
              </div>
            </div>
          </div>

          {/* Timer Display */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-accent-blue">
                {formatTime(timeRemaining)}
              </div>
              <div className="text-xs text-secondary">
                Session {currentSessionIndex + 1} of {totalSessions}
              </div>
            </div>
            
            {/* Current Time Display */}
            <div className="text-center">
              <div className="text-lg font-semibold text-primary">
                {currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </div>
              <div className="text-xs text-secondary">
                Current Time
              </div>
            </div>

            {/* Progress Bar */}
            <div className="hidden md:flex items-center space-x-2">
              <div className="w-32 h-2 bg-glass rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-primary transition-all duration-1000"
                  style={{ 
                    width: `${((currentSession.duration_minutes * 60 - timeRemaining) / (currentSession.duration_minutes * 60)) * 100}%` 
                  }}
                />
              </div>
              <div className="text-xs text-secondary">
                {Math.round(((currentSession.duration_minutes * 60 - timeRemaining) / (currentSession.duration_minutes * 60)) * 100)}%
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            <LiquidButton
              onClick={togglePause}
              variant="secondary"
              size="sm"
              className="px-3 py-1"
            >
              {isPaused ? '▶️' : '⏸️'}
            </LiquidButton>
            
            <LiquidButton
              onClick={skipSession}
              variant="secondary"
              size="sm"
              className="px-3 py-1"
            >
              ⏭️
            </LiquidButton>
            
            <LiquidButton
              onClick={stopTimer}
              variant="secondary"
              size="sm"
              className="px-3 py-1"
            >
              ⏹️
            </LiquidButton>
            
            <button
              onClick={() => setIsVisible(false)}
              className="p-1 text-secondary hover:text-primary transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Session Progress Indicator */}
        <div className="mt-2 flex justify-center">
          <div className="flex space-x-1">
            {studyPlan.pomodoro_sessions.map((session, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === currentSessionIndex
                    ? session.session_type === 'work' 
                      ? 'bg-accent-blue scale-125' 
                      : 'bg-accent-green scale-125'
                    : index < currentSessionIndex
                    ? 'bg-primary/50'
                    : 'bg-primary/20'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyTimer;