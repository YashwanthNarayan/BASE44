import React, { useState, useEffect } from 'react';
import { practiceAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidProgress, LiquidStatsCard } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const ProgressComponent = ({ student, onNavigate }) => {
  const [progressData, setProgressData] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [loading, setLoading] = useState(true);

  const subjects = ['all', 'math', 'physics', 'chemistry', 'biology', 'english', 'history', 'geography'];

  useEffect(() => {
    loadProgressData();
  }, [selectedSubject]);

  const loadProgressData = async () => {
    setLoading(true);
    try {
      const endpoint = selectedSubject === 'all' 
        ? practiceAPI.getResults()
        : practiceAPI.getStats(selectedSubject);
        
      const response = await endpoint;
      setProgressData(response);
    } catch (error) {
      console.error('Error loading progress data:', error);
      setProgressData(null);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-neon-green bg-gradient-to-r from-green-500/20 to-emerald-500/20';
    if (score >= 60) return 'text-neon-yellow bg-gradient-to-r from-yellow-500/20 to-orange-500/20';
    return 'text-neon-pink bg-gradient-to-r from-red-500/20 to-pink-500/20';
  };

  const getProgressBarColor = (score) => {
    if (score >= 80) return 'bg-gradient-to-r from-neon-green to-emerald-500';
    if (score >= 60) return 'bg-gradient-to-r from-neon-yellow to-orange-500';
    return 'bg-gradient-to-r from-neon-pink to-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Analyzing neural progression patterns...</p>
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
            📊 Neural Progress Analytics
          </h1>
          <p className="text-secondary">Monitor your quantum learning evolution and achievements</p>
        </div>

        {/* Subject Filter Matrix */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">🎯</span>
              </div>
              <h2 className="text-xl font-semibold text-primary">Domain Filter Matrix</h2>
            </div>
            <div className="flex flex-wrap gap-3">
              {subjects.map(subject => (
                <button
                  key={subject}
                  onClick={() => setSelectedSubject(subject)}
                  className={`
                    px-4 py-2 rounded-lg border-2 transition-all duration-300
                    ${selectedSubject === subject
                      ? 'border-neon-cyan bg-glass-strong text-neon-cyan glow-cyan'
                      : 'border-primary/20 bg-glass hover:border-neon-cyan/50 text-primary'
                    }
                  `}
                >
                  {subject === 'all' ? '🌐 All Domains' : `📚 ${subject.charAt(0).toUpperCase() + subject.slice(1)}`}
                </button>
              ))}
            </div>
          </div>
        </LiquidCard>

        {progressData ? (
          <>
            {/* Neural Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <LiquidStatsCard
                title="Neural Tests"
                value={Array.isArray(progressData) ? progressData.length : progressData.total_tests || 0}
                icon="📝"
                gradient="from-blue-500/20 to-cyan-500/20"
                trend="Cognitive assessments"
              />
              
              <LiquidStatsCard
                title="Neural Score"
                value={`${Array.isArray(progressData) 
                  ? (progressData.reduce((acc, test) => acc + test.score, 0) / progressData.length || 0).toFixed(1)
                  : (progressData.average_score || 0).toFixed(1)
                }%`}
                icon="📈"
                gradient="from-green-500/20 to-emerald-500/20"
                trend="Quantum average"
              />
              
              <LiquidStatsCard
                title="Peak Performance"
                value={`${Array.isArray(progressData) 
                  ? Math.max(...progressData.map(t => t.score), 0)
                  : (progressData.best_score || 0)
                }%`}
                icon="🏆"
                gradient="from-yellow-500/20 to-orange-500/20"
                trend="Maximum neural output"
              />
              
              <LiquidStatsCard
                title="Data Points"
                value={Array.isArray(progressData) 
                  ? progressData.reduce((acc, test) => acc + (test.total_questions || 0), 0)
                  : (progressData.total_questions_answered || 0)
                }
                icon="❓"
                gradient="from-purple-500/20 to-indigo-500/20"
                trend="Neural interactions"
              />
            </div>

            {/* Recent Neural Activity */}
            <LiquidCard className="mb-8">
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                    <span className="text-sm font-bold">⚡</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Recent Neural Assessments</h2>
                </div>
                
                {(Array.isArray(progressData) ? progressData : progressData.recent_tests || []).length > 0 ? (
                  <div className="space-y-4">
                    {(Array.isArray(progressData) ? progressData : progressData.recent_tests || [])
                      .slice(0, 10)
                      .map((test, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-glass border border-primary/20 rounded-lg hover:border-neon-cyan/50 transition-colors">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4">
                            <div className={`px-4 py-2 rounded-lg text-sm font-medium border ${getPerformanceColor(test.score)}`}>
                              {test.score}% Neural Output
                            </div>
                            <div>
                              <div className="font-medium text-primary">
                                {test.subject ? `🧠 ${test.subject.charAt(0).toUpperCase() + test.subject.slice(1)} Neural Test` : '🌐 General Assessment'}
                              </div>
                              <div className="text-sm text-secondary">
                                {test.total_questions || test.question_count || 0} data points • {' '}
                                {test.completed_at ? new Date(test.completed_at).toLocaleDateString() : 'Recent session'}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="w-32 ml-4">
                          <LiquidProgress 
                            value={test.score} 
                            max={100}
                            className="h-3"
                            color={getProgressBarColor(test.score)}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🧠</div>
                    <h3 className="text-2xl font-bold text-primary mb-4">No Neural Data Detected</h3>
                    <p className="text-secondary mb-6">Initialize your neural assessment protocols to begin tracking cognitive evolution.</p>
                    <LiquidButton onClick={() => onNavigate('practice')}>
                      ⚡ Initialize Neural Assessment
                    </LiquidButton>
                  </div>
                )}
              </div>
            </LiquidCard>

            {/* Neural Performance Analysis */}
            {!Array.isArray(progressData) && progressData.subject && (
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                      <span className="text-sm font-bold">🔬</span>
                    </div>
                    <h2 className="text-xl font-bold text-primary">
                      {progressData.subject.charAt(0).toUpperCase() + progressData.subject.slice(1)} Neural Analysis
                    </h2>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="p-4 bg-glass rounded-lg border border-primary/20">
                      <h3 className="font-semibold text-primary mb-3">⏱️ Neural Processing Time</h3>
                      <p className="text-3xl font-bold text-neon-cyan glow-cyan mb-2">
                        {Math.floor((progressData.total_time_spent || 0) / 60)} minutes
                      </p>
                      <p className="text-sm text-secondary">Total cognitive processing duration</p>
                    </div>
                    
                    <div className="p-4 bg-glass rounded-lg border border-primary/20">
                      <h3 className="font-semibold text-primary mb-3">📊 Neural Consistency</h3>
                      <p className="text-3xl font-bold text-neon-green glow-cyan mb-2">
                        {progressData.total_tests > 5 ? 'Optimal' : progressData.total_tests > 2 ? 'Developing' : 'Initialize'}
                      </p>
                      <p className="text-sm text-secondary">Based on assessment frequency patterns</p>
                    </div>
                  </div>
                </div>
              </LiquidCard>
            )}
          </>
        ) : (
          <LiquidCard className="text-center p-12">
            <div className="text-6xl mb-6">📊</div>
            <h2 className="text-2xl font-bold text-primary mb-4">Neural Data Matrix Empty</h2>
            <p className="text-secondary mb-8">
              Initialize neural assessment protocols to begin tracking your cognitive evolution patterns.
            </p>
            <LiquidButton onClick={() => onNavigate('practice')}>
              ⚡ Initialize Neural Assessment
            </LiquidButton>
          </LiquidCard>
        )}
      </div>
    </div>
  );
};

export default ProgressComponent;