import axios from 'axios';

// Dynamic API Base URL - automatically determines backend URL based on frontend URL
const getApiBaseUrl = () => {
  // Always use current origin for Emergent platform to avoid cross-origin issues
  return window.location.origin;
};

const API_BASE = getApiBaseUrl();

// Log the configuration for debugging
console.log('🔍 API Configuration:', {
  frontend_url: window.location.origin,
  backend_url: API_BASE,
  hostname: window.location.hostname
});

// Setup axios authentication and interceptors
export const setupAxiosAuth = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};



// Add response interceptor to handle token expiration
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear all authentication data - use direct localStorage for token
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_type');
      localStorage.removeItem('user');
      
      // Remove authorization header
      delete axios.defaults.headers.common['Authorization'];
      
      // Log the error for debugging instead of auto-reload
      console.error('🚨 401 Unauthorized error:', error.config?.url, error.response?.data);
      
      // Show alert but don't reload automatically
      alert('Authentication expired. Please log in again.');
      // Commented out auto-reload to prevent loops
      // window.location.reload();
    }
    return Promise.reject(error);
  }
);

// Function to clear all authentication
export const clearAuth = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_type');
  localStorage.removeItem('user');
  delete axios.defaults.headers.common['Authorization'];
};

// Auth API
export const authAPI = {
  login: async (credentials) => {
    const response = await axios.post(`${API_BASE}/api/auth/login`, credentials);
    return response.data;
  },
  
  register: async (formData) => {
    const response = await axios.post(`${API_BASE}/api/auth/register`, formData);
    return response.data;
  }
};

// Student API
export const studentAPI = {
  getProfile: async () => {
    const response = await axios.get(`${API_BASE}/api/student/profile`);
    return response.data;
  },
  
  getDashboard: async () => {
    const response = await axios.get(`${API_BASE}/api/dashboard`);
    return response.data;
  },
  
  joinClass: async (joinData) => {
    const response = await axios.post(`${API_BASE}/api/student/join-class`, joinData);
    return response.data;
  },
  
  getJoinedClasses: async () => {
    const response = await axios.get(`${API_BASE}/api/student/joined-classes`);
    return response.data;
  }
};

// Teacher API
export const teacherAPI = {
  getAnalyticsOverview: async () => {
    const response = await axios.get(`${API_BASE}/api/teacher/analytics/overview`);
    return response.data;
  },

  getTestResults: async (classId, studentId, subject) => {
    let url = `${API_BASE}/api/teacher/analytics/test-results`;
    const params = new URLSearchParams();
    
    if (classId) params.append('class_id', classId);
    if (studentId) params.append('student_id', studentId);
    if (subject) params.append('subject', subject);
    
    if (params.toString()) {
      url += '?' + params.toString();
    }
    
    const response = await axios.get(url);
    return response.data;
  },

  getClassPerformance: async (classId) => {
    const response = await axios.get(`${API_BASE}/api/teacher/analytics/class-performance/${classId}`);
    return response.data;
  },

  // NEW: Class-wide strengths and weaknesses analysis
  getClassStrengthsWeaknesses: async (classId = null) => {
    let url = `${API_BASE}/api/teacher/analytics/class-strengths-weaknesses`;
    if (classId) {
      url += `?class_id=${classId}`;
    }
    const response = await axios.get(url);
    return response.data;
  },

  // NEW: Individual student strengths and weaknesses analysis
  getStudentStrengthsWeaknesses: async (studentId) => {
    const response = await axios.get(`${API_BASE}/api/teacher/analytics/student-strengths-weaknesses/${studentId}`);
    return response.data;
  },
  
  createClass: async (classData) => {
    const response = await axios.post(`${API_BASE}/api/teacher/classes`, classData);
    return response.data;
  },
  
  getClasses: async () => {
    const response = await axios.get(`${API_BASE}/api/teacher/classes`);
    return response.data;
  },
  
  deleteClass: async (classId) => {
    const response = await axios.delete(`${API_BASE}/api/teacher/classes/${classId}`);
    return response.data;
  }
};

// Practice Test API
export const practiceAPI = {
  generate: async (testData) => {
    const response = await axios.post(`${API_BASE}/api/practice/generate`, testData);
    return response.data;
  },
  
  submit: async (testResults) => {
    const response = await axios.post(`${API_BASE}/api/practice/submit`, testResults);
    return response.data;
  },
  
  getResults: async (subject) => {
    const url = subject 
      ? `${API_BASE}/api/practice/results?subject=${subject}`
      : `${API_BASE}/api/practice/results`;
    const response = await axios.get(url);
    return response.data;
  },
  
  getDetailedResults: async (attemptId) => {
    const response = await axios.get(`${API_BASE}/api/practice/results/${attemptId}`);
    return response.data;
  },
  
  getStats: async (subject) => {
    const response = await axios.get(`${API_BASE}/api/practice/stats/${subject}`);
    return response.data;
  }
};

// Tutor API
export const tutorAPI = {
  createSession: async (data) => {
    const response = await axios.post(`${API_BASE}/api/tutor/session`, data);
    return response.data;
  },
  
  sendMessage: async (data) => {
    const response = await axios.post(`${API_BASE}/api/tutor/chat`, data);
    return response.data;
  },
  
  getSessions: async () => {
    const response = await axios.get(`${API_BASE}/api/tutor/sessions`);
    return response.data;
  },
  
  getSessionMessages: async (sessionId) => {
    const response = await axios.get(`${API_BASE}/api/tutor/session/${sessionId}/messages`);
    return response.data;
  },
  
  deleteSession: async (sessionId) => {
    const response = await axios.delete(`${API_BASE}/api/tutor/session/${sessionId}`);
    return response.data;
  },
  
  updateSessionTitle: async (sessionId, title) => {
    const response = await axios.patch(`${API_BASE}/api/tutor/session/${sessionId}/title?title=${encodeURIComponent(title)}`);
    return response.data;
  }
};

// Notes API
export const notesAPI = {
  getAll: async () => {
    const response = await axios.get(`${API_BASE}/api/notes/`);
    return response.data;
  },
  
  generate: async (subject, topic, gradeLevel) => {
    const response = await axios.post(`${API_BASE}/api/notes/generate`, {
      subject,
      topic,
      grade_level: gradeLevel
    });
    return response.data;
  },
  
  getById: async (noteId) => {
    const response = await axios.get(`${API_BASE}/api/notes/${noteId}`);
    return response.data;
  },
  
  favorite: async (noteId) => {
    const response = await axios.put(`${API_BASE}/api/notes/${noteId}/favorite`);
    return response.data;
  },
  
  delete: async (noteId) => {
    const response = await axios.delete(`${API_BASE}/api/notes/${noteId}/delete`);
    return response.data;
  }
};

// Mindfulness API
export const mindfulnessAPI = {
  startSession: async (sessionData) => {
    const response = await axios.post(`${API_BASE}/api/mindfulness/session`, sessionData);
    return response.data;
  },
  
  getActivities: async () => {
    const response = await axios.get(`${API_BASE}/api/mindfulness/activities`);
    return response.data;
  }
};

// Calendar API
export const calendarAPI = {
  createEvent: async (eventData) => {
    const response = await axios.post(`${API_BASE}/api/calendar/events`, eventData);
    return response.data;
  },
  
  getEvents: async () => {
    const response = await axios.get(`${API_BASE}/api/calendar/events`);
    return response.data;
  }
};

// Notifications API
export const notificationsAPI = {
  getAll: async () => {
    const response = await axios.get(`${API_BASE}/api/notifications`);
    return response.data;
  },
  
  markAsRead: async (notificationId) => {
    const response = await axios.put(`${API_BASE}/api/notifications/${notificationId}/read`);
    return response.data;
  }
};

// Study Planner API
export const studyPlannerAPI = {
  chat: async (message, context = null) => {
    const response = await axios.post(`${API_BASE}/api/study-planner/chat`, {
      message,
      context
    });
    return response.data;
  },
  
  generatePlan: async (planRequest) => {
    const response = await axios.post(`${API_BASE}/api/study-planner/generate-plan`, planRequest);
    return response.data;
  },
  
  getMyPlans: async () => {
    const response = await axios.get(`${API_BASE}/api/study-planner/my-plans`);
    return response.data;
  },
  
  startSession: async (planId) => {
    const response = await axios.post(`${API_BASE}/api/study-planner/start-session/${planId}`);
    return response.data;
  },
  
  deletePlan: async (planId) => {
    const response = await axios.delete(`${API_BASE}/api/study-planner/plan/${planId}`);
    return response.data;
  }
};

// Practice Scheduler API
export const practiceSchedulerAPI = {
  getUpcomingTests: async () => {
    const response = await axios.get(`${API_BASE}/api/practice-scheduler/upcoming-tests`);
    return response.data;
  },
  
  takeScheduledTest: async (testId) => {
    const response = await axios.post(`${API_BASE}/api/practice-scheduler/take-scheduled-test/${testId}`);
    return response.data;
  },
  
  completeScheduledTest: async (testId, score) => {
    const response = await axios.post(`${API_BASE}/api/practice-scheduler/complete-scheduled-test/${testId}`, {
      score
    });
    return response.data;
  },
  
  cancelTest: async (testId) => {
    const response = await axios.delete(`${API_BASE}/api/practice-scheduler/cancel-test/${testId}`);
    return response.data;
  },
  
  scheduleReview: async (subject, topics, difficulty, originalScore, questionCount) => {
    const response = await axios.post(`${API_BASE}/api/practice-scheduler/schedule-review`, {
      subject,
      topics,
      difficulty,
      original_score: originalScore,
      question_count: questionCount
    });
    return response.data;
  }
};

// Student Analytics API
export const studentAnalyticsAPI = {
  getStrengthsWeaknesses: async () => {
    const response = await axios.get(`${API_BASE}/api/student/analytics/strengths-weaknesses`);
    return response.data;
  },
  
  getPerformanceTrends: async (days = 30) => {
    const response = await axios.get(`${API_BASE}/api/student/analytics/performance-trends?days=${days}`);
    return response.data;
  },
  
  getSubjectBreakdown: async () => {
    const response = await axios.get(`${API_BASE}/api/student/analytics/subject-breakdown`);
    return response.data;
  },
  
  getLearningInsights: async () => {
    const response = await axios.get(`${API_BASE}/api/student/analytics/learning-insights`);
    return response.data;
  }
};

export default API_BASE;