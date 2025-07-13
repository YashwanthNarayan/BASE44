import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import './styles/liquid-glass.css';

// Import components
import AuthPortal from './components/AuthPortal_Liquid';
import StudentDashboard from './components/StudentDashboard_Liquid';
import TeacherDashboard from './components/TeacherDashboard_Liquid';
import NotesComponent from './components/NotesComponent_Liquid';
import PracticeTestComponent from './components/PracticeTestComponent_Liquid';
import AuthDebugComponent from './components/AuthDebugComponent';

// Import lazy-loaded components (now with liquid versions)
const MindfulnessComponent = React.lazy(() => import('./components/MindfulnessComponent_Liquid'));
const CalendarComponent = React.lazy(() => import('./components/CalendarComponent_Liquid'));
const ProgressComponent = React.lazy(() => import('./components/ProgressComponent_Liquid'));
const TutorComponent = React.lazy(() => import('./components/TutorComponent_Liquid'));
const NotificationsComponent = React.lazy(() => import('./components/NotificationsComponent_Liquid'));
const ClassesComponent = React.lazy(() => import('./components/ClassesComponent_Liquid'));
const TeacherAnalyticsDashboard = React.lazy(() => import('./components/TeacherAnalyticsDashboard_Liquid'));

// Teacher-specific components
const CreateClassComponent = React.lazy(() => import('./components/CreateClassComponent_Liquid'));
const ManageClassesComponent = React.lazy(() => import('./components/ManageClassesComponent_Liquid'));
const AssignmentsComponent = React.lazy(() => import('./components/AssignmentsComponent_Liquid'));

// Import services and utilities
import { setupAxiosAuth, studentAPI } from './services/api';
import { storage } from './utils/helpers';
import API_BASE from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('debug'); // Change to debug
  const [userType, setUserType] = useState('student');
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false); // Disable loading for debug

  // Show debug component directly
  if (currentView === 'debug') {
    return <AuthDebugComponent />;
  }

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

  if (currentView === 'create-class') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Create Class..." />}>
        <CreateClassComponent teacher={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'manage-classes') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Class Management..." />}>
        <ManageClassesComponent teacher={user} onNavigate={navigate} />
      </React.Suspense>
    );
  }

  if (currentView === 'assignments') {
    return (
      <React.Suspense fallback={<LoadingFallback message="Loading Assignments..." />}>
        <AssignmentsComponent teacher={user} onNavigate={navigate} />
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