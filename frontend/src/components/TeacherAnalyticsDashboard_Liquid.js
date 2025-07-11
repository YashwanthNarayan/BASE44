import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidStatsCard, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const TeacherAnalyticsDashboard = ({ teacher, onNavigate }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedClass, setSelectedClass] = useState('all');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedClass, selectedSubject]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load test results with filters
      const testResults = await teacherAPI.getTestResults({
        class_id: selectedClass !== 'all' ? selectedClass : undefined,
        subject: selectedSubject !== 'all' ? selectedSubject : undefined
      });
      
      // Load class performance data if a specific class is selected
      let classPerformance = null;
      if (selectedClass !== 'all') {
        classPerformance = await teacherAPI.getClassPerformance(selectedClass);
      }

      setAnalyticsData({
        testResults,
        classPerformance,
        overview: testResults.length > 0 ? {
          total_tests: testResults.length,
          average_score: testResults.reduce((acc, test) => acc + test.score, 0) / testResults.length || 0,
          total_students: [...new Set(testResults.map(test => test.student_id))].length,
          completion_rate: 85 // Placeholder
        } : null
      });
    } catch (error) {
      console.error('Error loading analytics data:', error);
      setAnalyticsData(null);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-neon-green';
    if (score >= 60) return 'text-neon-yellow';
    return 'text-neon-pink';
  };

  const getGradeDistribution = () => {
    if (!analyticsData?.testResults) return [];
    
    const scores = analyticsData.testResults.map(test => test.score);
    const ranges = [
      { label: '90-100%', min: 90, max: 100, color: 'from-neon-green/20 to-emerald-500/20' },
      { label: '80-89%', min: 80, max: 89, color: 'from-green-500/20 to-teal-500/20' },
      { label: '70-79%', min: 70, max: 79, color: 'from-yellow-500/20 to-orange-500/20' },
      { label: '60-69%', min: 60, max: 69, color: 'from-orange-500/20 to-red-500/20' },
      { label: 'Below 60%', min: 0, max: 59, color: 'from-red-500/20 to-pink-500/20' }
    ];

    return ranges.map(range => ({
      ...range,
      count: scores.filter(score => score >= range.min && score <= range.max).length,
      percentage: scores.length > 0 ? ((scores.filter(score => score >= range.min && score <= range.max).length / scores.length) * 100).toFixed(1) : 0
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Processing neural analytics matrix...</p>
        </LiquidCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Neural Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
          <div className="space-y-2">
            <LiquidButton
              variant="secondary"
              onClick={() => onNavigate('teacher-dashboard')}
              className="mb-4"
            >
              ← Neural Command Center
            </LiquidButton>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              📊 Advanced Neural Analytics
            </h1>
            <p className="text-secondary text-lg">
              Deep cognitive performance analysis and student progression matrices
            </p>
          </div>
        </div>

        {/* Neural Filter Controls */}
        <LiquidCard className="mb-8" holographic>
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">🎯</span>
              </div>
              <h2 className="text-xl font-semibold text-primary">Neural Filter Matrix</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Neural Class Domain
                </label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full p-3 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary"
                >
                  <option value="all">🌐 All Neural Classes</option>
                  {/* Dynamic class options would go here */}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Subject Protocol
                </label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="w-full p-3 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary"
                >
                  <option value="all">🧠 All Subject Domains</option>
                  <option value="math">🔢 Quantum Mathematics</option>
                  <option value="physics">⚛️ Neural Physics</option>
                  <option value="chemistry">🧪 Molecular Chemistry</option>
                  <option value="biology">🧬 Bio-Neural Science</option>
                  <option value="english">📚 Linguistic Protocols</option>
                  <option value="history">🏛️ Temporal Archives</option>
                  <option value="geography">🌍 Planetary Systems</option>
                </select>
              </div>
            </div>
          </div>
        </LiquidCard>

        {analyticsData?.overview ? (
          <>
            {/* Neural Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <LiquidStatsCard
                title="Neural Tests"
                value={analyticsData.overview.total_tests}
                icon="📝"
                gradient="from-blue-500/20 to-cyan-500/20"
                trend="Cognitive assessments"
              />
              
              <LiquidStatsCard
                title="Active Minds"
                value={analyticsData.overview.total_students}
                icon="🧠"
                gradient="from-green-500/20 to-emerald-500/20"
                trend="Neural connections"
              />
              
              <LiquidStatsCard
                title="Neural Average"
                value={`${analyticsData.overview.average_score.toFixed(1)}%`}
                icon="📊"
                gradient="from-purple-500/20 to-indigo-500/20"
                trend="Cognitive performance"
              />
              
              <LiquidStatsCard
                title="Completion Rate"
                value={`${analyticsData.overview.completion_rate}%`}
                icon="✅"
                gradient="from-orange-500/20 to-red-500/20"
                trend="Task completion"
              />
            </div>

            {/* Performance Distribution & Recent Tests */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Neural Grade Distribution */}
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                      <span className="text-sm font-bold">📈</span>
                    </div>
                    <h2 className="text-xl font-bold text-primary">Neural Performance Distribution</h2>
                  </div>
                  
                  <div className="space-y-4">
                    {getGradeDistribution().map((range, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-primary font-medium">{range.label}</span>
                          <span className="text-secondary">{range.count} students ({range.percentage}%)</span>
                        </div>
                        <div className="w-full bg-glass rounded-full h-3 border border-primary/20">
                          <div 
                            className={`h-3 rounded-full bg-gradient-to-r ${range.color} transition-all duration-500`}
                            style={{ width: `${range.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </LiquidCard>

              {/* Recent Neural Activity */}
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                      <span className="text-sm font-bold">⚡</span>
                    </div>
                    <h2 className="text-xl font-bold text-primary">Recent Neural Assessments</h2>
                  </div>
                  
                  <div className="space-y-4 max-h-80 overflow-y-auto">
                    {analyticsData.testResults.slice(0, 10).map((test, index) => (
                      <div key={index} className="p-4 bg-glass border border-primary/20 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium text-primary">
                              Student ID: {test.student_id}
                            </div>
                            <div className="text-sm text-secondary">
                              {test.subject} • {new Date(test.completed_at).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`text-lg font-bold ${getPerformanceColor(test.score)}`}>
                              {test.score}%
                            </div>
                            <div className="text-xs text-secondary">
                              {test.total_questions} questions
                            </div>
                          </div>
                        </div>
                        <div className="mt-3">
                          <LiquidProgress 
                            value={test.score} 
                            max={100}
                            className="h-2"
                            color={test.score >= 80 ? 'bg-neon-green' : test.score >= 60 ? 'bg-neon-yellow' : 'bg-neon-pink'}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </LiquidCard>
            </div>

            {/* Detailed Test Results */}
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                    <span className="text-sm font-bold">📋</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Comprehensive Neural Assessment Matrix</h2>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-primary/20">
                        <th className="text-left p-3 text-secondary font-medium">Student Neural ID</th>
                        <th className="text-left p-3 text-secondary font-medium">Subject Domain</th>
                        <th className="text-left p-3 text-secondary font-medium">Neural Score</th>
                        <th className="text-left p-3 text-secondary font-medium">Data Points</th>
                        <th className="text-left p-3 text-secondary font-medium">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyticsData.testResults.map((test, index) => (
                        <tr key={index} className="border-b border-primary/10 hover:bg-glass transition-colors">
                          <td className="p-3 text-primary font-medium">{test.student_id}</td>
                          <td className="p-3 text-primary capitalize">{test.subject}</td>
                          <td className="p-3">
                            <span className={`font-bold ${getPerformanceColor(test.score)}`}>
                              {test.score}%
                            </span>
                          </td>
                          <td className="p-3 text-secondary">{test.total_questions} questions</td>
                          <td className="p-3 text-secondary">
                            {new Date(test.completed_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </LiquidCard>
          </>
        ) : (
          <LiquidCard className="text-center p-12">
            <div className="text-6xl mb-6">📊</div>
            <h2 className="text-2xl font-bold text-primary mb-4">Neural Analytics Matrix Empty</h2>
            <p className="text-secondary mb-8">
              No neural assessment data detected for the selected parameters. Students need to complete cognitive assessments to generate analytics.
            </p>
            <LiquidButton onClick={() => onNavigate('teacher-dashboard')}>
              ⚡ Return to Neural Command Center
            </LiquidButton>
          </LiquidCard>
        )}
      </div>
    </div>
  );
};

export default TeacherAnalyticsDashboard;