import React, { useState } from 'react';
import { teacherAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const CreateClassComponent = ({ teacher, onNavigate }) => {
  const [classData, setClassData] = useState({
    class_name: '',
    subject: '',
    description: '',
    class_code: ''
  });
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const subjects = [
    { value: 'math', label: 'Mathematics', icon: '🔢' },
    { value: 'physics', label: 'Physics', icon: '⚛️' },
    { value: 'chemistry', label: 'Chemistry', icon: '🧪' },
    { value: 'biology', label: 'Biology', icon: '🧬' },
    { value: 'english', label: 'English', icon: '📚' },
    { value: 'history', label: 'History', icon: '🏛️' },
    { value: 'geography', label: 'Geography', icon: '🌍' },
    { value: 'computer_science', label: 'Computer Science', icon: '💻' }
  ];

  const handleInputChange = (field, value) => {
    setClassData(prev => ({ ...prev, [field]: value }));
  };

  const generateClassCode = () => {
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();
    setClassData(prev => ({ ...prev, class_code: code }));
  };

  const handleCreateClass = async () => {
    if (!classData.class_name || !classData.subject) {
      alert('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    try {
      await teacherAPI.createClass(classData);
      setSuccessMessage('Class created successfully!');
      
      // Reset form
      setClassData({
        class_name: '',
        subject: '',
        description: '',
        class_code: ''
      });
      
      // Redirect after success
      setTimeout(() => {
        onNavigate('manage-classes');
      }, 2000);
    } catch (error) {
      console.error('Error creating class:', error);
      alert('Failed to create class. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (successMessage) {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-4xl mx-auto">
          <div className="flex items-center justify-center min-h-screen">
            <LiquidCard className="p-12 text-center">
              <div className="text-8xl mb-8 animate-bounce">🎉</div>
              <h1 className="text-4xl font-bold text-green-400 mb-4">Success!</h1>
              <p className="text-xl text-primary mb-8">{successMessage}</p>
              <p className="text-secondary mb-8">Redirecting to class management...</p>
              <LiquidButton onClick={() => onNavigate('manage-classes')}>
                Go to Classes
              </LiquidButton>
            </LiquidCard>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-4xl mx-auto">
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
            ➕ Create New Class
          </h1>
          <p className="text-secondary">Set up a new class for your students</p>
        </div>

        <LiquidCard className="p-8">
          <div className="space-y-6">
            {/* Class Name */}
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">
                Class Name *
              </label>
              <LiquidInput
                type="text"
                value={classData.class_name}
                onChange={(e) => handleInputChange('class_name', e.target.value)}
                placeholder="e.g., Advanced Physics 2024"
                className="w-full"
              />
            </div>

            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-secondary mb-4">
                Subject *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {subjects.map((subject) => (
                  <button
                    key={subject.value}
                    onClick={() => handleInputChange('subject', subject.value)}
                    className={`
                      p-4 rounded-xl transition-all duration-300 text-center relative
                      ${classData.subject === subject.value
                        ? 'glass-strong border-2 border-green-400 text-white bg-green-400/10'
                        : 'glass border-white/20 text-white/80 hover:glass-strong hover:border-white/40'
                      }
                    `}
                  >
                    {classData.subject === subject.value && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-400 rounded-full flex items-center justify-center">
                        <span className="text-black text-xs font-bold">✓</span>
                      </div>
                    )}
                    <div className="text-2xl mb-2">{subject.icon}</div>
                    <div className="text-sm font-medium">{subject.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Class Code */}
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">
                Class Code
              </label>
              <div className="flex gap-3">
                <LiquidInput
                  type="text"
                  value={classData.class_code}
                  onChange={(e) => handleInputChange('class_code', e.target.value.toUpperCase())}
                  placeholder="Enter custom code or generate one"
                  className="flex-1"
                />
                <LiquidButton
                  variant="secondary"
                  onClick={generateClassCode}
                  className="px-6"
                >
                  Generate
                </LiquidButton>
              </div>
              <p className="text-xs text-secondary mt-2">
                Students will use this code to join your class
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">
                Description (Optional)
              </label>
              <textarea
                value={classData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className="w-full p-4 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary placeholder-secondary resize-none"
                rows="4"
                placeholder="Describe what this class is about..."
              />
            </div>

            {/* Preview */}
            <LiquidCard className="p-6 bg-glass/50">
              <h3 className="text-lg font-semibold text-primary mb-4">Class Preview</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {subjects.find(s => s.value === classData.subject)?.icon || '📚'}
                  </span>
                  <div>
                    <div className="font-medium text-primary">
                      {classData.class_name || 'Class Name'}
                    </div>
                    <div className="text-sm text-secondary">
                      {subjects.find(s => s.value === classData.subject)?.label || 'Subject'} 
                      {classData.class_code && ` • Code: ${classData.class_code}`}
                    </div>
                  </div>
                </div>
                {classData.description && (
                  <p className="text-sm text-secondary italic">
                    "{classData.description}"
                  </p>
                )}
              </div>
            </LiquidCard>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-6">
              <LiquidButton
                variant="secondary"
                onClick={() => onNavigate('teacher-dashboard')}
                className="flex-1"
              >
                Cancel
              </LiquidButton>
              <LiquidButton
                onClick={handleCreateClass}
                disabled={!classData.class_name || !classData.subject || loading}
                className="flex-1"
              >
                {loading ? 'Creating...' : 'Create Class'}
              </LiquidButton>
            </div>
          </div>
        </LiquidCard>
      </div>
    </div>
  );
};

export default CreateClassComponent;