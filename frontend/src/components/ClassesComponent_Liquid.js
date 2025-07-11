import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const ClassesComponent = ({ student, onNavigate }) => {
  const [joinedClasses, setJoinedClasses] = useState([]);
  const [joinCode, setJoinCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    loadJoinedClasses();
  }, []);

  const loadJoinedClasses = async () => {
    try {
      const response = await studentAPI.getProfile();
      setJoinedClasses(response.joined_classes || []);
    } catch (error) {
      console.error('Error loading joined classes:', error);
      setJoinedClasses([]);
    } finally {
      setLoading(false);
    }
  };

  const joinClass = async () => {
    if (!joinCode.trim()) {
      alert('Please input neural access code.');
      return;
    }

    setJoining(true);
    try {
      await studentAPI.joinClass({ join_code: joinCode });
      alert('Neural class connection established successfully!');
      setJoinCode('');
      loadJoinedClasses();
    } catch (error) {
      console.error('Error joining class:', error);
      alert(error.response?.data?.detail || 'Failed to establish neural class connection. Verify access code and retry.');
    } finally {
      setJoining(false);
    }
  };

  const getSubjectIcon = (subject) => {
    const subjectIcons = {
      math: '🔢',
      physics: '⚛️',
      chemistry: '🧪',
      biology: '🧬',
      english: '📚',
      history: '🏛️',
      geography: '🌍'
    };
    return subjectIcons[subject] || '📖';
  };

  const getSubjectGradient = (subject) => {
    const subjectGradients = {
      math: 'from-blue-500/20 to-cyan-500/20',
      physics: 'from-purple-500/20 to-indigo-500/20',
      chemistry: 'from-green-500/20 to-emerald-500/20',
      biology: 'from-emerald-500/20 to-teal-500/20',
      english: 'from-red-500/20 to-pink-500/20',
      history: 'from-yellow-500/20 to-orange-500/20',
      geography: 'from-teal-500/20 to-cyan-500/20'
    };
    return subjectGradients[subject] || 'from-gray-500/20 to-gray-600/20';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Synchronizing neural class matrix...</p>
        </LiquidCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Neural Header */}
        <div className="text-center mb-8">
          <LiquidButton
            variant="secondary"
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4"
          >
            ← Neural Dashboard
          </LiquidButton>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            🏫 Neural Class Matrix
          </h1>
          <p className="text-secondary">Access your connected learning environments and establish new neural links</p>
        </div>

        {/* Neural Class Connection Interface */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">⚡</span>
              </div>
              <h2 className="text-xl font-semibold text-primary">Establish Neural Class Connection</h2>
            </div>
            
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <LiquidInput
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                  placeholder="Enter neural access code"
                  className="w-full"
                  onKeyPress={(e) => e.key === 'Enter' && joinClass()}
                />
              </div>
              <LiquidButton
                onClick={joinClass}
                disabled={!joinCode.trim() || joining}
                className="whitespace-nowrap"
              >
                {joining ? (
                  <>
                    <div className="quantum-loader w-4 h-4 mr-2" />
                    Establishing Link...
                  </>
                ) : (
                  '⚡ Establish Connection'
                )}
              </LiquidButton>
            </div>
            <p className="text-sm text-secondary mt-3">
              Request neural access code from your cognitive enhancement instructor to establish class connection.
            </p>
          </div>
        </LiquidCard>

        {/* Neural Class Grid */}
        {joinedClasses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {joinedClasses.map((classroom, index) => (
              <LiquidCard
                key={classroom.class_id || index}
                className="overflow-hidden hover:scale-105 transform transition-all duration-300 group"
              >
                {/* Neural Class Header */}
                <div className={`bg-gradient-to-br ${getSubjectGradient(classroom.subject)} p-6 border-b border-primary/20`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-4xl">{getSubjectIcon(classroom.subject)}</div>
                    <div className="text-right">
                      <div className="text-sm text-secondary opacity-90">
                        Neural Level
                      </div>
                      <div className="text-lg font-bold text-neon-cyan glow-cyan">
                        {classroom.grade_level || 'N/A'}
                      </div>
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-primary mb-2">
                    {classroom.class_name || 'Neural Learning Matrix'}
                  </h3>
                  <p className="text-sm text-secondary capitalize">
                    {(classroom.subject || 'general').replace('_', ' ')} Enhancement Protocol
                  </p>
                </div>

                {/* Neural Class Info */}
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-secondary">Cognitive Instructor:</span>
                      <span className="font-medium text-primary">
                        Prof. {classroom.teacher_name || 'Neural Guide'}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-secondary">Access Code:</span>
                      <span className="font-mono text-sm bg-glass px-3 py-1 rounded border border-primary/20 text-neon-cyan">
                        {classroom.join_code || 'N/A'}
                      </span>
                    </div>

                    {classroom.description && (
                      <div className="mt-4 p-3 bg-glass rounded-lg border border-primary/20">
                        <p className="text-sm text-secondary">{classroom.description}</p>
                      </div>
                    )}
                  </div>

                  {/* Neural Quick Actions */}
                  <div className="mt-6 flex space-x-3">
                    <LiquidButton
                      variant="secondary"
                      onClick={() => onNavigate('practice')}
                      className="flex-1 text-sm"
                    >
                      📝 Neural Tests
                    </LiquidButton>
                    <LiquidButton
                      variant="secondary"
                      onClick={() => onNavigate('tutor')}
                      className="flex-1 text-sm"
                    >
                      🤖 AI Tutor
                    </LiquidButton>
                  </div>
                </div>

                {/* Neural Data Stream */}
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </LiquidCard>
            ))}
          </div>
        ) : (
          <LiquidCard className="text-center p-12">
            <div className="text-6xl mb-6">🏫</div>
            <h2 className="text-2xl font-bold text-primary mb-4">No Neural Class Connections Detected</h2>
            <p className="text-secondary mb-8">
              Your learning matrix is currently uninitialized. Request a neural access code from your cognitive enhancement instructor to establish your first class connection.
            </p>
            <div className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-4">
                <LiquidInput
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                  placeholder="Enter neural access code"
                  className="flex-1"
                  onKeyPress={(e) => e.key === 'Enter' && joinClass()}
                />
                <LiquidButton
                  onClick={joinClass}
                  disabled={!joinCode.trim() || joining}
                  className="whitespace-nowrap"
                >
                  {joining ? (
                    <>
                      <div className="quantum-loader w-4 h-4 mr-2" />
                      Connecting...
                    </>
                  ) : (
                    '⚡ Establish Connection'
                  )}
                </LiquidButton>
              </div>
            </div>
          </LiquidCard>
        )}

        {/* Neural Quick Actions Panel */}
        {joinedClasses.length > 0 && (
          <div className="mt-8">
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                    <span className="text-sm font-bold">⚡</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Neural Quick Actions</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <LiquidButton
                    onClick={() => onNavigate('practice')}
                    className="p-4 h-auto"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">📝</div>
                      <div className="font-semibold">Neural Assessment</div>
                      <div className="text-xs text-secondary mt-1">Initiate cognitive testing</div>
                    </div>
                  </LiquidButton>
                  
                  <LiquidButton
                    onClick={() => onNavigate('tutor')}
                    className="p-4 h-auto"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">🤖</div>
                      <div className="font-semibold">AI Enhancement</div>
                      <div className="text-xs text-secondary mt-1">Connect with neural tutor</div>
                    </div>
                  </LiquidButton>
                  
                  <LiquidButton
                    onClick={() => onNavigate('progress')}
                    className="p-4 h-auto"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-2">📊</div>
                      <div className="font-semibold">Progress Analysis</div>
                      <div className="text-xs text-secondary mt-1">Review neural evolution</div>
                    </div>
                  </LiquidButton>
                </div>
              </div>
            </LiquidCard>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClassesComponent;