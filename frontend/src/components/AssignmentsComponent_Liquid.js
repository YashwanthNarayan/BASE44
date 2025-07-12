import React, { useState, useEffect } from 'react';
import { LiquidCard, LiquidButton } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const AssignmentsComponent = ({ teacher, onNavigate }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);

  // Mock data for now since we don't have assignment API yet
  useEffect(() => {
    setAssignments([
      {
        id: 1,
        title: 'Physics Chapter 5 Problems',
        class: 'Advanced Physics',
        due_date: '2024-07-20',
        status: 'active',
        submissions: 15,
        total_students: 20
      },
      {
        id: 2,
        title: 'Math Calculus Assignment',
        class: 'Mathematics 101',
        due_date: '2024-07-18',
        status: 'past_due',
        submissions: 18,
        total_students: 22
      }
    ]);
  }, []);

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
            📝 Assignments
          </h1>
          <p className="text-secondary">Create and manage assignments for your classes</p>
        </div>

        {/* Coming Soon Notice */}
        <LiquidCard className="p-12 text-center">
          <div className="text-8xl mb-6">🚧</div>
          <h2 className="text-3xl font-bold text-primary mb-4">Coming Soon!</h2>
          <p className="text-lg text-secondary mb-8">
            The Assignment Management system is currently under development.
          </p>
          <div className="space-y-4 mb-8">
            <p className="text-secondary">Planned features include:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left max-w-2xl mx-auto">
              <div className="p-4 bg-glass rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">📝</span>
                  <span className="font-semibold">Create Assignments</span>
                </div>
                <p className="text-sm text-secondary">Design custom assignments with deadlines</p>
              </div>
              <div className="p-4 bg-glass rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">📊</span>
                  <span className="font-semibold">Track Submissions</span>
                </div>
                <p className="text-sm text-secondary">Monitor student progress and submissions</p>
              </div>
              <div className="p-4 bg-glass rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">✅</span>
                  <span className="font-semibold">Auto-Grading</span>
                </div>
                <p className="text-sm text-secondary">AI-powered grading for quick feedback</p>
              </div>
              <div className="p-4 bg-glass rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">💬</span>
                  <span className="font-semibold">Feedback System</span>
                </div>
                <p className="text-sm text-secondary">Provide detailed feedback to students</p>
              </div>
            </div>
          </div>
          
          <div className="space-x-4">
            <LiquidButton 
              variant="secondary"
              onClick={() => onNavigate('create-class')}
            >
              Create a Class
            </LiquidButton>
            <LiquidButton onClick={() => onNavigate('teacher-analytics')}>
              View Analytics
            </LiquidButton>
          </div>
        </LiquidCard>

        {/* Mock Preview (for demonstration) */}
        <div className="mt-8">
          <h3 className="text-2xl font-bold text-primary mb-6 text-center">Preview: Future Assignment Dashboard</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-50">
            {assignments.map((assignment) => (
              <LiquidCard key={assignment.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-bold text-primary">{assignment.title}</h4>
                    <p className="text-sm text-secondary">{assignment.class}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    assignment.status === 'active' 
                      ? 'bg-green-400/20 text-green-400' 
                      : 'bg-red-400/20 text-red-400'
                  }`}>
                    {assignment.status === 'active' ? 'Active' : 'Past Due'}
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-secondary">Due Date:</span>
                    <span className="text-primary">{new Date(assignment.due_date).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-secondary">Submissions:</span>
                    <span className="text-primary">{assignment.submissions}/{assignment.total_students}</span>
                  </div>
                </div>
                
                <div className="w-full bg-glass rounded-full h-2 mb-4">
                  <div 
                    className="h-2 rounded-full bg-gradient-to-r from-neon-cyan to-neon-magenta"
                    style={{ width: `${(assignment.submissions / assignment.total_students) * 100}%` }}
                  ></div>
                </div>
                
                <div className="flex gap-2">
                  <button className="flex-1 px-3 py-2 bg-glass border border-primary/20 rounded-lg text-xs text-secondary">
                    View Details
                  </button>
                  <button className="flex-1 px-3 py-2 bg-glass border border-primary/20 rounded-lg text-xs text-secondary">
                    Grade
                  </button>
                </div>
              </LiquidCard>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentsComponent;