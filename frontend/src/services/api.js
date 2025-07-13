import axios from 'axios';

// Dynamic API Base URL - automatically determines backend URL based on frontend URL
const getApiBaseUrl = () => {
  // If we're in development and have an env var, use it
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // Otherwise, determine dynamically based on current URL
  const currentHost = window.location.hostname;
  const currentProtocol = window.location.protocol;
  const currentOrigin = window.location.origin;
  
  // For localhost development
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:8001';
  }
  
  // For Emergent platform, try different approaches based on protocol
  if (currentHost.includes('emergentagent.com') || currentHost.includes('preview')) {
    // If frontend is HTTPS, try HTTPS backend first, fall back to HTTP
    if (currentProtocol === 'https:') {
      return `https://${currentHost}:8001`;
    } else {
      return `http://${currentHost}:8001`;
    }
  }
  
  // For HTTPS sites, use HTTPS backend
  if (currentProtocol === 'https:') {
    return `https://${currentHost}:8001`;
  }
  
  // Fallback to HTTP for other cases
  return `http://${currentHost}:8001`;
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

// Add request interceptor to ensure token is always included
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear all authentication data
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_type');
      localStorage.removeItem('user');
      
      // Remove authorization header
      delete axios.defaults.headers.common['Authorization'];
      
      // Show alert and reload page
      alert('Authentication expired. Please log in again.');
      window.location.reload();
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
    const params = new URLSearchParams();
    if (classId) params.append('class_id', classId);
    if (studentId) params.append('student_id', studentId);
    if (subject) params.append('subject', subject);
    
    const response = await axios.get(`${API_BASE}/api/teacher/analytics/test-results?${params}`);
    return response.data;
  },
  
  getClassPerformance: async (classId) => {
    const response = await axios.get(`${API_BASE}/api/teacher/analytics/class-performance/${classId}`);
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
  generate: async (subject, topic, gradeLevel) => {
    const response = await axios.post(`${API_BASE}/api/notes/generate`, {
      subject,
      topic,
      grade_level: gradeLevel
    });
    return response.data;
  },
  
  getAll: async () => {
    const response = await axios.get(`${API_BASE}/api/notes`);
    return response.data;
  },
  
  delete: async (noteId) => {
    const response = await axios.delete(`${API_BASE}/api/notes/${noteId}/delete`);
    return response.data;
  },
  
  toggleFavorite: async (noteId) => {
    const response = await axios.put(`${API_BASE}/api/notes/${noteId}/favorite`);
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

export default API_BASE;