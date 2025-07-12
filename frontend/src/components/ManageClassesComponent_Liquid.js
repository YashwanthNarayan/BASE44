import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const ManageClassesComponent = ({ teacher, onNavigate }) => {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState(null);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await teacherAPI.getClasses();
      setClasses(response);
    } catch (error) {
      console.error('Error loading classes:', error);
      setClasses([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClass = async (classId) => {
    if (window.confirm('Are you sure you want to delete this class? This action cannot be undone.')) {
      try {
        await teacherAPI.deleteClass(classId);
        loadClasses(); // Reload classes
      } catch (error) {
        console.error('Error deleting class:', error);
        alert('Failed to delete class. Please try again.');
      }
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      math: '🔢',
      physics: '⚛️',
      chemistry: '🧪',
      biology: '🧬',
      english: '📚',
      history: '🏛️',
      geography: '🌍',
      computer_science: '💻'
    };
    return icons[subject] || '📚';
  };

  const getSubjectName = (subject) => {
    const names = {
      math: 'Mathematics',
      physics: 'Physics',
      chemistry: 'Chemistry',
      biology: 'Biology',
      english: 'English',
      history: 'History',
      geography: 'Geography',
      computer_science: 'Computer Science'
    };
    return names[subject] || subject.charAt(0).toUpperCase() + subject.slice(1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Loading classes...</p>
        </LiquidCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <LiquidButton
            variant="secondary"
            onClick={() => onNavigate('teacher-dashboard')}
            className="mb-4"
          >
            ← Back to Dashboard
          </LiquidButton>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            🏫 Manage Classes
          </h1>
          <p className="text-secondary">View and manage your classes</p>
        </div>

        {/* Action Bar */}
        <div className="flex justify-between items-center mb-6">
          <div className="text-lg text-primary">
            {classes.length} {classes.length === 1 ? 'Class' : 'Classes'}
          </div>
          <LiquidButton onClick={() => onNavigate('create-class')}>
            ➕ Create New Class
          </LiquidButton>
        </div>

        {/* Classes Grid */}
        {classes.length === 0 ? (
          <LiquidCard className="p-12 text-center">
            <div className="text-8xl mb-6">🏫</div>
            <h2 className="text-2xl font-bold text-primary mb-4">No Classes Yet</h2>
            <p className="text-secondary mb-8">
              Create your first class to start teaching and managing students
            </p>
            <LiquidButton onClick={() => onNavigate('create-class')}>
              Create Your First Class
            </LiquidButton>
          </LiquidCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {classes.map((classItem) => (
              <LiquidCard key={classItem.class_id} className="p-6 hover:scale-105 transition-transform duration-300">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">
                      {getSubjectIcon(classItem.subject)}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-primary">
                        {classItem.class_name}
                      </h3>
                      <p className="text-sm text-secondary">
                        {getSubjectName(classItem.subject)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteClass(classItem.class_id)}
                    className="text-red-400 hover:text-red-300 transition-colors p-1"
                    title="Delete Class"
                  >
                    🗑️
                  </button>
                </div>

                {/* Class Code */}
                <div className="mb-4 p-3 bg-glass/50 rounded-lg">
                  <div className="text-xs text-secondary mb-1">Class Code</div>
                  <div className="text-lg font-mono font-bold text-primary tracking-wider">
                    {classItem.class_code}
                  </div>
                </div>

                {/* Stats */}
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span className="text-secondary">Students:</span>
                    <span className="text-primary font-semibold">
                      {classItem.student_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Tests Created:</span>
                    <span className="text-primary font-semibold">
                      {classItem.test_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Avg Score:</span>
                    <span className="text-primary font-semibold">
                      {classItem.average_score ? `${classItem.average_score.toFixed(1)}%` : 'N/A'}
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                {classItem.average_score && (
                  <div className="mb-4">
                    <LiquidProgress 
                      value={classItem.average_score} 
                      max={100}
                      className="h-2"
                    />
                  </div>
                )}

                {/* Description */}
                {classItem.description && (
                  <div className="mb-4 p-3 bg-glass/30 rounded-lg">
                    <p className="text-sm text-secondary italic">
                      "{classItem.description}"
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="space-y-2">
                  <LiquidButton
                    variant="secondary"
                    onClick={() => onNavigate('teacher-analytics')}
                    className="w-full text-sm"
                  >
                    📊 View Analytics
                  </LiquidButton>
                  <div className="grid grid-cols-2 gap-2">
                    <button className="px-3 py-2 bg-glass border border-primary/20 rounded-lg text-xs text-secondary hover:text-primary transition-colors">
                      👥 Students
                    </button>
                    <button className="px-3 py-2 bg-glass border border-primary/20 rounded-lg text-xs text-secondary hover:text-primary transition-colors">
                      📝 Tests
                    </button>
                  </div>
                </div>

                {/* Created Date */}
                <div className="mt-4 pt-3 border-t border-primary/20">
                  <p className="text-xs text-secondary">
                    Created: {new Date(classItem.created_at).toLocaleDateString()}
                  </p>
                </div>
              </LiquidCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManageClassesComponent;