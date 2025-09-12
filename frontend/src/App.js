import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/modern-ui.css';
import './App.css';
import './styles/liquid-glass.css';

// Import components
import AuthPortal from './components/AuthPortal_Modern';
import StudentDashboard from './components/StudentDashboard_Modern';
import TeacherDashboard from './components/TeacherDashboard_Liquid';
import NotesComponent from './components/NotesComponent_Modern';
import PracticeTestComponent from './components/PracticeTestComponent_Modern';
import StudyTimer from './components/StudyTimer';

// Import lazy-loaded components (now with liquid versions)
const MindfulnessComponent = React.lazy(() => import('./components/MindfulnessComponent_Modern'));
const CalendarComponent = React.lazy(() => import('./components/CalendarComponent_Liquid'));
const ProgressComponent = React.lazy(() => import('./components/ProgressComponent_Modern'));
const TutorComponent = React.lazy(() => import('./components/TutorComponent_Modern'));
const NotificationsComponent = React.lazy(() => import('./components/NotificationsComponent_Liquid'));
const ClassesComponent = React.lazy(() => import('./components/ClassesComponent_Liquid'));
const TeacherAnalyticsDashboard = React.lazy(() => import('./components/TeacherAnalyticsDashboard_Liquid'));
const StudyPlannerComponent = React.lazy(() => import('./components/StudyPlannerComponent_Liquid'));
const ScheduledTestsComponent = React.lazy(() => import('./components/ScheduledTestsComponent_Modern'));
const StrengthsWeaknessesComponent = React.lazy(() => import('./components/StrengthsWeaknessesComponent_Modern'));

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
  const [currentView, setCurrentView] = useState('student-dashboard');
  const [userType, setUserType] = useState('student');
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Study timer state
  const [activeStudyPlan, setActiveStudyPlan] = useState(null);
  const [showStudyTimer, setShowStudyTimer] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token'); // Direct access to avoid quotes
      const userType = storage.get('user_type');
      const user = storage.get('user');

      if (token && userType && user) {
        setupAxiosAuth(token);
        
        // Test the token by making a simple API call
        try {
          const response = await axios.get(`${API_BASE}/api/dashboard`);
          // If successful, set auth state
          setIsAuthenticated(true);
          setUserType(userType);
          setUser(user);
          
          if (userType === 'student') {
            await loadDashboardData();
            setCurrentView('student-dashboard');
          } else {
            setCurrentView('teacher-dashboard');
          }
        } catch (tokenError) {
          console.error('Token validation failed:', tokenError);
          // Clear invalid tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_type');
          localStorage.removeItem('user');
          storage.remove('user_type');
          storage.remove('user');
          setupAxiosAuth(null);
          // Stay on login page
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
    // Get the token and setup axios auth
    const token = localStorage.getItem('access_token');
    if (token) {
      setupAxiosAuth(token);
    }
    
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
    localStorage.removeItem('access_token'); // Direct removal
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

  // Study timer functions
  const startStudySession = (studyPlan) => {
    setActiveStudyPlan(studyPlan);
    setShowStudyTimer(true);
  };

  const handleSessionComplete = (currentSession, nextSession) => {
    // Could add notifications or other logic here
    console.log('Session completed:', currentSession);
    if (nextSession) {
      console.log('Next session:', nextSession);
    } else {
      console.log('All sessions completed!');
      setShowStudyTimer(false);
      setActiveStudyPlan(null);
    }
  };

  const handleTimerStop = () => {
    setShowStudyTimer(false);
    setActiveStudyPlan(null);
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

  // Loading fallback component
  const LoadingFallback = ({ message = "Loading component..." }) => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );

  if (!isAuthenticated) {
    return <AuthPortal onLogin={handleAuthSuccess} onRegister={handleAuthSuccess} />;
  }

  return (
    <div className="App">
      {/* Study Timer - Always visible when active */}
      {showStudyTimer && activeStudyPlan && (
        <StudyTimer 
          studyPlan={activeStudyPlan}
          onSessionComplete={handleSessionComplete}
          onTimerStop={handleTimerStop}
        />
      )}
      
      {/* Main content with padding when timer is visible */}
      <div className={showStudyTimer ? 'pt-24' : ''}>
        {/* Route to different views */}
        {currentView === 'student-dashboard' && userType === 'student' && (
          <StudentDashboard 
            student={user} 
            onNavigate={navigate}
            dashboardData={dashboardData}
            onLogout={handleLogout}
          />
        )}

        {currentView === 'teacher-dashboard' && userType === 'teacher' && (
          <TeacherDashboard 
            teacher={user} 
            onNavigate={navigate}
            onLogout={handleLogout}
          />
        )}

        {currentView === 'notes' && (
          <NotesComponent student={user} onNavigate={navigate} />
        )}

        {currentView === 'practice-tests' && (
          <PracticeTestComponent student={user} onNavigate={navigate} />
        )}

        {/* Lazy-loaded components with Suspense */}
        <React.Suspense fallback={<LoadingFallback />}>
          {currentView === 'mindfulness' && (
            <MindfulnessComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'calendar' && (
            <CalendarComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'progress' && (
            <ProgressComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'tutor' && (
            <TutorComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'notifications' && (
            <NotificationsComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'classes' && (
            <ClassesComponent student={user} onNavigate={navigate} />
          )}

          {currentView === 'study-planner' && (
            <StudyPlannerComponent 
              student={user} 
              onNavigate={navigate}
              onStartStudySession={startStudySession}
            />
          )}

          {currentView === 'scheduled-tests' && (
            <ScheduledTestsComponent 
              student={user} 
              onNavigate={navigate}
            />
          )}

          {currentView === 'strengths-weaknesses' && (
            <StrengthsWeaknessesComponent 
              student={user} 
              onNavigate={navigate}
            />
          )}

          {currentView === 'teacher-analytics' && (
            <TeacherAnalyticsDashboard teacher={user} onNavigate={navigate} />
          )}

          {currentView === 'create-class' && (
            <CreateClassComponent teacher={user} onNavigate={navigate} />
          )}

          {currentView === 'manage-classes' && (
            <ManageClassesComponent teacher={user} onNavigate={navigate} />
          )}

          {currentView === 'assignments' && (
            <AssignmentsComponent teacher={user} onNavigate={navigate} />
          )}
        </React.Suspense>

        {/* Default fallback */}
        {!['student-dashboard', 'teacher-dashboard', 'notes', 'practice-tests', 'mindfulness', 'calendar', 'progress', 'tutor', 'notifications', 'classes', 'study-planner', 'scheduled-tests', 'strengths-weaknesses', 'teacher-analytics', 'create-class', 'manage-classes', 'assignments'].includes(currentView) && (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h1>
              <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
              <button
                onClick={() => navigate(userType === 'student' ? 'student-dashboard' : 'teacher-dashboard')}
                className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;