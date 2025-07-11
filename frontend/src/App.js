import React, { useState, useEffect } from 'react';
import './App.css';
import './styles/liquid-glass.css';

// Import components
import AuthPortal from './components/AuthPortal_Liquid';
import StudentDashboard from './components/StudentDashboard_Liquid';
import TeacherDashboard from './components/TeacherDashboard_Liquid';
import NotesComponent from './components/NotesComponent';
import PracticeTestComponent from './components/PracticeTestComponent_Liquid';

// Import lazy-loaded components (we'll create these next)
const MindfulnessComponent = React.lazy(() => import('./components/MindfulnessComponent'));
const CalendarComponent = React.lazy(() => import('./components/CalendarComponent'));
const ProgressComponent = React.lazy(() => import('./components/ProgressComponent'));
const TutorComponent = React.lazy(() => import('./components/TutorComponent'));
const NotificationsComponent = React.lazy(() => import('./components/NotificationsComponent'));
const ClassesComponent = React.lazy(() => import('./components/ClassesComponent'));
const TeacherAnalyticsDashboard = React.lazy(() => import('./components/TeacherAnalyticsDashboard'));

// Import services and utilities
import { setupAxiosAuth, studentAPI } from './services/api';
import { storage } from './utils/helpers';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('student-dashboard');
  const [userType, setUserType] = useState('student');
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = storage.get('access_token');
      const userType = storage.get('user_type');
      const user = storage.get('user');

      if (token && userType && user) {
        setupAxiosAuth(token);
        setIsAuthenticated(true);
        setUserType(userType);
        setUser(user);
        
        if (userType === 'student') {
          await loadDashboardData();
          setCurrentView('student-dashboard');
        } else {
          setCurrentView('teacher-dashboard');
        }
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      const data = await studentAPI.getDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const handleAuthSuccess = (userType, user) => {
    setIsAuthenticated(true);
    setUserType(userType);
    setUser(user);
    
    if (userType === 'student') {
      setCurrentView('student-dashboard');
      loadDashboardData();
    } else {
      setCurrentView('teacher-dashboard');
    }
  };

  const handleLogout = () => {
    storage.remove('access_token');
    storage.remove('user_type');
    storage.remove('user');
    setupAxiosAuth(null);
    setIsAuthenticated(false);
    setCurrentView('student-dashboard');
    setUser(null);
    setDashboardData(null);
  };

  const navigate = (view) => {
    setCurrentView(view);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPortal onAuthSuccess={handleAuthSuccess} />;
  }

  // Route to different views
  if (currentView === 'student-dashboard' && userType === 'student') {
    return (
      <StudentDashboard 
        student={user} 
        onNavigate={navigate}
        dashboardData={dashboardData}
        onLogout={handleLogout}
      />
    );
  }

  if (currentView === 'teacher-dashboard' && userType === 'teacher') {
    return (
      <TeacherDashboard 
        teacher={user} 
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (currentView === 'notes') {
    return <NotesComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'practice') {
    return <PracticeTestComponent student={user} onNavigate={navigate} />;
  }

  // Lazy-loaded components with Suspense
  const LoadingFallback = ({ message = "Loading component..." }) => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );

  if (currentView === 'mindfulness') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Mindfulness..." />}>
        <MindfulnessComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'calendar') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Calendar..." />}>
        <CalendarComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'progress') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Progress..." />}>
        <ProgressComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'tutor') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading AI Tutor..." />}>
        <TutorComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'notifications') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Notifications..." />}>
        <NotificationsComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'classes') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Classes..." />}>
        <ClassesComponent student={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'teacher-analytics') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Analytics..." />}>
        <TeacherAnalyticsDashboard teacher={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  // Default fallback
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h1>
        <button
          onClick={() => navigate(userType === 'student' ? 'student-dashboard' : 'teacher-dashboard')}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}

export default App;