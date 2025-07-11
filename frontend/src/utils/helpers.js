// Utility functions for the application

// Format time from seconds to MM:SS
export const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Format time ago (e.g., "2h ago", "3d ago")
export const formatTimeAgo = (timestamp) => {
  const now = new Date();
  const time = new Date(timestamp);
  const diffInHours = Math.floor((now - time) / (1000 * 60 * 60));
  
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours}h ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays}d ago`;
  return time.toLocaleDateString();
};

// Get performance color based on score
export const getPerformanceColor = (score) => {
  if (score >= 80) return 'text-green-600 bg-green-100';
  if (score >= 60) return 'text-yellow-600 bg-yellow-100';
  return 'text-red-600 bg-red-100';
};

// Get progress bar color based on score
export const getProgressBarColor = (score) => {
  if (score >= 80) return 'bg-green-500';
  if (score >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
};

// Get subject icon from subject string
export const getSubjectIcon = (subject) => {
  const subjectIcons = {
    math: '🔢',
    physics: '⚛️',
    chemistry: '🧪',
    biology: '🧬',
    english: '📚',
    history: '🏛️',
    geography: '🌍'
  };
  return subjectIcons[subject] || '📖';
};

// Get subject color for gradients
export const getSubjectColor = (subject) => {
  const subjectColors = {
    math: 'from-blue-500 to-blue-600',
    physics: 'from-purple-500 to-purple-600',
    chemistry: 'from-green-500 to-green-600',
    biology: 'from-emerald-500 to-emerald-600',
    english: 'from-red-500 to-red-600',
    history: 'from-yellow-500 to-yellow-600',
    geography: 'from-teal-500 to-teal-600'
  };
  return subjectColors[subject] || 'from-gray-500 to-gray-600';
};

// Get notification icon based on type
export const getNotificationIcon = (type) => {
  switch (type) {
    case 'achievement': return '🏆';
    case 'reminder': return '⏰';
    case 'message': return '💬';
    case 'assignment': return '📝';
    case 'grade': return '📊';
    default: return '📢';
  }
};

// Get notification color based on type
export const getNotificationColor = (type) => {
  switch (type) {
    case 'achievement': return 'border-yellow-200 bg-yellow-50';
    case 'reminder': return 'border-blue-200 bg-blue-50';
    case 'message': return 'border-green-200 bg-green-50';
    case 'assignment': return 'border-purple-200 bg-purple-50';
    case 'grade': return 'border-indigo-200 bg-indigo-50';
    default: return 'border-gray-200 bg-gray-50';
  }
};

// Generate calendar days for a given month
export const generateCalendarDays = (year = null, month = null) => {
  const today = new Date();
  const currentMonth = month ?? today.getMonth();
  const currentYear = year ?? today.getFullYear();
  const firstDay = new Date(currentYear, currentMonth, 1);
  const lastDay = new Date(currentYear, currentMonth + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay();

  const days = [];
  
  // Add empty cells for days before the first day of the month
  for (let i = 0; i < startingDayOfWeek; i++) {
    days.push(null);
  }
  
  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(currentYear, currentMonth, day);
    days.push(date);
  }
  
  return days;
};

// Calculate XP level from total XP
export const calculateLevel = (totalXP) => {
  // Each level requires 100 more XP than the previous
  // Level 1: 0-99, Level 2: 100-299, Level 3: 300-599, etc.
  return Math.floor(Math.sqrt(totalXP / 100)) + 1;
};

// Calculate XP needed for next level
export const getXPForNextLevel = (totalXP) => {
  const currentLevel = calculateLevel(totalXP);
  const nextLevelXP = Math.pow(currentLevel, 2) * 100;
  return nextLevelXP - totalXP;
};

// Validate email format
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate password strength
export const validatePassword = (password) => {
  const errors = [];
  if (password.length < 8) errors.push('Password must be at least 8 characters long');
  if (!/[A-Z]/.test(password)) errors.push('Password must contain at least one uppercase letter');
  if (!/[a-z]/.test(password)) errors.push('Password must contain at least one lowercase letter');
  if (!/[0-9]/.test(password)) errors.push('Password must contain at least one number');
  if (!/[!@#$%^&*]/.test(password)) errors.push('Password must contain at least one special character');
  return errors;
};

// Local storage helpers
export const storage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
};

// Debounce function for search inputs
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Truncate text with ellipsis
export const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
};

// Capitalize first letter
export const capitalize = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Convert snake_case to Title Case
export const snakeToTitleCase = (str) => {
  return str
    .split('_')
    .map(word => capitalize(word))
    .join(' ');
};