import React from 'react';
import { 
  ModernNav, 
  ModernNavBrand, 
  ModernNavLinks, 
  ModernNavLink,
  ModernButton,
  ModernBadge
} from './ui/ModernComponents';

const NavigationBar_Modern = ({ user, currentPage, onNavigate, onLogout }) => {
  const navigationItems = [
    { id: 'student-dashboard', label: 'Dashboard', icon: '●' },
    { id: 'classes', label: 'Classes', icon: '⬢' },
    { id: 'calendar', label: 'Calendar', icon: '◈' },
    { id: 'study-planner', label: 'Study Planner', icon: '◉' },
    { id: 'practice-tests', label: 'Practice Tests', icon: '◆' },
    { id: 'strengths-weaknesses', label: 'Analytics', icon: '◇' },
    { id: 'tutor', label: 'AI Tutor', icon: '◎' },
    { id: 'mindfulness', label: 'Mindfulness', icon: '◐' },
    { id: 'scheduled-tests', label: 'Schedule', icon: '◯' },
    { id: 'progress', label: 'Progress', icon: '◑' },
    { id: 'notes', label: 'Notes', icon: '◒' }
  ];

  const teacherItems = [
    { id: 'teacher-dashboard', label: 'Dashboard', icon: '●' },
    { id: 'classes', label: 'Classes', icon: '◆' },
    { id: 'assignments', label: 'Assignments', icon: '◇' },
    { id: 'teacher-analytics', label: 'Analytics', icon: '◎' }
  ];

  const items = user?.user_type === 'teacher' ? teacherItems : navigationItems;
  const level = Math.floor((user?.xp_points || 0) / 100) + 1;

  return (
    <ModernNav className="sticky top-0 z-50">
      <ModernNavBrand onClick={() => onNavigate('student-dashboard')}>
        <div className="flex items-center gap-2 cursor-pointer">
          <div className="w-8 h-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
            <div className="w-4 h-4 bg-white rounded opacity-90"></div>
          </div>
          <span className="font-bold text-xl text-gray-900">NCERT Study Hub</span>
        </div>
      </ModernNavBrand>

      <ModernNavLinks>
        {/* Navigation Items */}
        <div className="hidden md:flex items-center gap-1">
          {items.slice(0, 5).map((item) => (
            <ModernButton
              key={item.id}
              variant="ghost"
              className={`flex items-center gap-2 text-sm ${
                currentPage === item.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => onNavigate(item.id)}
            >
              <span>{item.icon}</span>
              <span className="hidden lg:inline">{item.label}</span>
            </ModernButton>
          ))}
        </div>

        {/* User Section */}
        <div className="flex items-center gap-3">
          {user?.user_type === 'student' && (
            <ModernBadge variant="primary" className="hidden sm:flex">
              Level {level}
            </ModernBadge>
          )}
          
          {/* User Menu */}
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-gray-900">{user?.name}</div>
              <div className="text-xs text-gray-500 capitalize">{user?.user_type}</div>
            </div>
            
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">
                {user?.name?.charAt(0).toUpperCase()}
              </span>
            </div>
            
            <ModernButton variant="ghost" onClick={onLogout} className="text-gray-500 hover:text-red-600">
              Sign Out
            </ModernButton>
          </div>
        </div>
      </ModernNavLinks>
    </ModernNav>
  );
};

export default NavigationBar_Modern;