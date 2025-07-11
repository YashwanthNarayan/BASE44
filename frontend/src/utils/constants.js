// Subject definitions
export const subjects = {
  math: { 
    name: 'Mathematics', 
    icon: '🔢',
    topics: ['Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics', 'Probability', 'Number Theory', 'Linear Equations', 'Quadratic Equations'] 
  },
  physics: { 
    name: 'Physics', 
    icon: '⚛️',
    topics: ['Mechanics', 'Thermodynamics', 'Waves', 'Optics', 'Electricity', 'Magnetism', 'Modern Physics', 'Kinematics', 'Dynamics'] 
  },
  chemistry: { 
    name: 'Chemistry', 
    icon: '🧪',
    topics: ['Atomic Structure', 'Organic Chemistry', 'Acids & Bases', 'Chemical Bonding', 'Periodic Table', 'Thermochemistry', 'Electrochemistry'] 
  },
  biology: { 
    name: 'Biology', 
    icon: '🧬',
    topics: ['Cell Biology', 'Genetics', 'Ecology', 'Human Physiology', 'Plant Biology', 'Evolution', 'Molecular Biology', 'Anatomy'] 
  },
  english: {
    name: 'English',
    icon: '📚',
    topics: ['Grammar', 'Literature', 'Poetry', 'Essay Writing', 'Reading Comprehension', 'Creative Writing', 'Vocabulary', 'Sentence Structure']
  },
  history: {
    name: 'History',
    icon: '🏛️',
    topics: ['Ancient History', 'Medieval History', 'Modern History', 'World Wars', 'Indian Independence', 'Civilizations', 'Cultural History']
  },
  geography: {
    name: 'Geography',
    icon: '🌍',
    topics: ['Physical Geography', 'Human Geography', 'Climate', 'Natural Resources', 'Population', 'Economic Geography', 'Environmental Geography']
  }
};

// Question types
export const questionTypes = [
  { value: 'mcq', label: 'Multiple Choice Questions (MCQ)', description: 'Questions with multiple options' },
  { value: 'short_answer', label: 'Short Answer', description: 'Brief written responses' },
  { value: 'long_answer', label: 'Long Answer', description: 'Detailed explanations' },
  { value: 'numerical', label: 'Numerical', description: 'Mathematical calculations' }
];

// Difficulty levels
export const difficultyLevels = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
  { value: 'mixed', label: 'Mixed' }
];

// Mood options for mindfulness
export const moods = ['😊 Great', '🙂 Good', '😐 Okay', '😔 Low', '😰 Stressed'];

// Mindfulness activities
export const mindfulnessActivities = [
  {
    id: 'breathing',
    name: 'Deep Breathing',
    description: 'Focused breathing exercises to reduce stress',
    duration: 5,
    icon: '🫁',
    instructions: 'Breathe in for 4 counts, hold for 4, breathe out for 6. Focus on your breath.'
  },
  {
    id: 'meditation',
    name: 'Guided Meditation',
    description: 'Short meditation session for mental clarity',
    duration: 10,
    icon: '🧘‍♀️',
    instructions: 'Close your eyes, sit comfortably, and focus on the present moment.'
  },
  {
    id: 'body_scan',
    name: 'Body Scan',
    description: 'Progressive relaxation from head to toe',
    duration: 8,
    icon: '💆‍♀️',
    instructions: 'Start from your head and slowly scan down to your toes, releasing tension.'
  },
  {
    id: 'gratitude',
    name: 'Gratitude Practice',
    description: 'Reflect on things you are grateful for',
    duration: 3,
    icon: '🙏',
    instructions: 'Think of 3 things you are grateful for today and why they matter to you.'
  }
];

// Event types for calendar
export const eventTypes = [
  { value: 'study', label: 'Study Session', icon: '📚' },
  { value: 'assignment', label: 'Assignment Due', icon: '📝' },
  { value: 'exam', label: 'Exam', icon: '📋' },
  { value: 'personal', label: 'Personal', icon: '🗓️' }
];

// Grade levels
export const gradeLevels = [
  '6th', '7th', '8th', '9th', '10th', '11th', '12th'
];

// User types
export const userTypes = [
  { value: 'student', label: 'Student' },
  { value: 'teacher', label: 'Teacher' }
];

// Subject color mappings for styling
export const subjectColors = {
  math: 'from-blue-500 to-blue-600',
  physics: 'from-purple-500 to-purple-600',
  chemistry: 'from-green-500 to-green-600',
  biology: 'from-emerald-500 to-emerald-600',
  english: 'from-red-500 to-red-600',
  history: 'from-yellow-500 to-yellow-600',
  geography: 'from-teal-500 to-teal-600'
};

// Performance thresholds
export const performanceThresholds = {
  excellent: 90,
  good: 80,
  average: 60,
  needsImprovement: 40
};

// Default dashboard data structure
export const defaultDashboardData = {
  total_messages: 0,
  total_tests: 0,
  average_score: 0,
  recent_scores: [],
  study_streak: 0,
  total_study_time: 0,
  achievements: [],
  upcoming_events: [],
  notifications: [],
  xp_points: 0,
  level: 1,
  subjects_studied: [],
  joined_classes: []
};