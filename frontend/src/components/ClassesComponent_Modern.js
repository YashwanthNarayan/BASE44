import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import { 
  ModernContainer, 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernInput, 
  ModernHeading, 
  ModernText, 
  ModernBadge, 
  ModernSpinner,
  ModernGrid 
} from './ui/ModernComponents';
import NavigationBar_Modern from './NavigationBar_Modern';

const ClassesComponent_Modern = ({ student, onNavigate }) => {
  const [joinedClasses, setJoinedClasses] = useState([]);
  const [joinCode, setJoinCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadJoinedClasses();
  }, []);

  const loadJoinedClasses = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await studentAPI.getJoinedClasses();
      setJoinedClasses(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading joined classes:', error);
      setError('Failed to load classes. Please try again.');
      setJoinedClasses([]);
    } finally {
      setLoading(false);
    }
  };

  const joinClass = async () => {
    if (!joinCode.trim()) {
      setError('Please enter a class code');
      return;
    }

    setJoining(true);
    setError('');
    setSuccess('');
    
    try {
      const normalizedCode = joinCode.trim().toUpperCase();
      await studentAPI.joinClass({ join_code: normalizedCode });
      setSuccess('Successfully joined class!');
      setJoinCode('');
      loadJoinedClasses();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error joining class:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to join class. Please verify the class code and try again.';
      setError(errorMessage);
    } finally {
      setJoining(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      joinClass();
    }
  };

  const getSubjectColor = (subject) => {
    const colors = {
      mathematics: 'blue',
      math: 'blue',
      physics: 'purple',
      chemistry: 'green',
      biology: 'emerald',
      english: 'pink',
      history: 'orange',
      geography: 'teal',
      science: 'indigo'
    };
    return colors[subject?.toLowerCase()] || 'gray';
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      mathematics: 'M',
      math: 'M',
      physics: 'P',  
      chemistry: 'C',
      biology: 'B',
      english: 'E',
      history: 'H',
      geography: 'G',
      science: 'S'
    };
    return icons[subject?.toLowerCase()] || 'G';
  };

  const getGradeColor = (grade) => {
    if (grade >= 90) return 'success';
    if (grade >= 80) return 'primary';
    if (grade >= 70) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavigationBar_Modern 
          user={student}
          currentPage="classes"
          onNavigate={onNavigate}
          onLogout={() => onNavigate('auth')}
        />
        
        <div className="flex items-center justify-center pt-32">
          <div className="text-center">
            <ModernSpinner size="lg" />
            <ModernText className="mt-4 text-gray-600 font-medium">Loading your classes...</ModernText>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <NavigationBar_Modern 
        user={student}
        currentPage="classes"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="mb-8">
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
            My Classes
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Join and manage your class enrollments
          </ModernText>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-red-800 font-medium">{error}</ModernText>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-green-800 font-medium">{success}</ModernText>
            </div>
          </div>
        )}

        {/* Join Class Section */}
        <ModernCard className="mb-8 shadow-lg">
          <ModernCardHeader>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                </svg>
              </div>
              <div>
                <ModernHeading level={3} className="text-gray-900 font-semibold">
                  Join a New Class
                </ModernHeading>
                <ModernText className="text-gray-600">
                  Enter the class code provided by your teacher
                </ModernText>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardBody>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <ModernInput
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                  placeholder="Enter class code (e.g., ABC123)"
                  onKeyPress={handleKeyPress}
                  className="w-full text-lg py-3 px-4 font-mono tracking-wider uppercase"
                />
                <ModernText variant="body-small" className="text-gray-500 mt-2">
                  Class codes are case-insensitive and spaces are automatically removed
                </ModernText>
              </div>
              
              <ModernButton
                variant="primary"
                onClick={joinClass}
                disabled={!joinCode.trim() || joining}
                className="px-8 py-3 font-semibold text-lg whitespace-nowrap"
              >
                {joining ? (
                  <div className="flex items-center gap-2">
                    <ModernSpinner size="sm" />
                    <span>Joining...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                    <span>Join Class</span>
                  </div>
                )}
              </ModernButton>
            </div>
          </ModernCardBody>
        </ModernCard>

        {/* Classes Grid */}
        {joinedClasses.length > 0 ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <ModernHeading level={2} className="text-2xl font-bold text-gray-900">
                Your Classes ({joinedClasses.length})
              </ModernHeading>
              <ModernButton variant="outline" onClick={loadJoinedClasses}>
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                </svg>
                Refresh
              </ModernButton>
            </div>
            
            <ModernGrid cols={3} className="gap-6">
              {joinedClasses.map((classroom, index) => {
                const subjectColor = getSubjectColor(classroom.subject);
                const subjectIcon = getSubjectIcon(classroom.subject);
                
                return (
                  <ModernCard 
                    key={classroom.class_id || index} 
                    className="group hover:shadow-xl transition-all duration-300 border-l-4 border-l-indigo-500"
                  >
                    {/* Class Header */}
                    <div className={`bg-gradient-to-br from-${subjectColor}-50 to-${subjectColor}-100 px-6 py-4 border-b border-gray-100`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-12 h-12 bg-${subjectColor}-500 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg`}>
                          {subjectIcon}
                        </div>
                        <div className="text-right">
                          <ModernBadge variant="secondary" className="text-xs">
                            Grade {classroom.grade_level || 'N/A'}
                          </ModernBadge>
                        </div>
                      </div>
                      
                      <ModernHeading level={4} className={`text-${subjectColor}-900 font-bold mb-1`}>
                        {classroom.class_name || 'Unnamed Class'}
                      </ModernHeading>
                      <ModernText className={`text-${subjectColor}-700 capitalize text-sm font-medium`}>
                        {(classroom.subject || 'General').replace('_', ' ')}
                      </ModernText>
                    </div>

                    {/* Class Body */}
                    <ModernCardBody className="space-y-4">
                      <div className="flex items-center justify-between">
                        <ModernText variant="body-small" className="text-gray-500 font-medium">
                          Instructor:
                        </ModernText>
                        <ModernText className="font-semibold text-gray-900">
                          {classroom.teacher_name || 'Unknown Teacher'}
                        </ModernText>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <ModernText variant="body-small" className="text-gray-500 font-medium">
                          Class Code:
                        </ModernText>
                        <div className="flex items-center gap-2">
                          <code className="bg-gray-100 text-gray-800 px-3 py-1 rounded-lg font-mono text-sm font-bold">
                            {classroom.join_code || 'N/A'}
                          </code>
                          <button 
                            onClick={() => navigator.clipboard.writeText(classroom.join_code || '')}
                            className="text-gray-400 hover:text-indigo-600 transition-colors p-1"
                            title="Copy class code"
                          >
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
                              <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
                            </svg>
                          </button>
                        </div>
                      </div>

                      {classroom.description && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <ModernText variant="body-small" className="text-gray-700 leading-relaxed">
                            {classroom.description}
                          </ModernText>
                        </div>
                      )}

                      {/* Class Stats */}
                      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                        <div className="text-center">
                          <div className="text-lg font-bold text-gray-900">
                            {classroom.student_count || 0}
                          </div>
                          <ModernText variant="body-small" className="text-gray-500">
                            Students
                          </ModernText>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-gray-900">
                            {classroom.assignment_count || 0}
                          </div>
                          <ModernText variant="body-small" className="text-gray-500">
                            Assignments
                          </ModernText>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2 pt-4">
                        <ModernButton 
                          variant="primary" 
                          className="flex-1 font-medium"
                          onClick={() => {
                            // Navigate to class details or assignments
                            console.log('View class details:', classroom.class_id);
                          }}
                        >
                          View Details
                        </ModernButton>
                        <ModernButton 
                          variant="outline" 
                          className="font-medium"
                          onClick={() => {
                            // Open class in new tab or navigate
                            console.log('Open class:', classroom.class_id);
                          }}
                        >
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12z" clipRule="evenodd" />
                          </svg>
                        </ModernButton>
                      </div>
                    </ModernCardBody>
                  </ModernCard>
                );
              })}
            </ModernGrid>
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            </div>
            <ModernHeading level={3} className="text-gray-800 font-semibold mb-3">
              No Classes Yet
            </ModernHeading>
            <ModernText className="text-gray-600 font-medium mb-6 max-w-md mx-auto">
              You haven't joined any classes yet. Ask your teacher for a class code to get started with your learning journey.
            </ModernText>
            <ModernButton 
              variant="primary" 
              onClick={() => document.querySelector('input[placeholder*="class code"]')?.focus()}
              className="font-semibold"
            >
              Join Your First Class
            </ModernButton>
          </div>
        )}
      </ModernContainer>
    </div>
  );
};

export default ClassesComponent_Modern;