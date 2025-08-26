import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidStatsCard, LiquidProgress } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const TeacherAnalyticsDashboard = ({ teacher, onNavigate }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [classAnalytics, setClassAnalytics] = useState(null);
  const [studentAnalytics, setStudentAnalytics] = useState(null);
  const [selectedClass, setSelectedClass] = useState('all');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [availableStudents, setAvailableStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedClass, selectedSubject]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load test results with filters - FIX: Pass individual parameters, not object
      const classId = selectedClass !== 'all' ? selectedClass : undefined;
      const subject = selectedSubject !== 'all' ? selectedSubject : undefined;
      
      const testResults = await teacherAPI.getTestResults(classId, undefined, subject);
      
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

      // Extract unique students for individual analysis
      if (testResults.length > 0) {
        const uniqueStudents = testResults.reduce((students, test) => {
          if (!students.find(s => s.student_id === test.student_id)) {
            students.push({
              student_id: test.student_id,
              student_name: test.student_name || `Student ${test.student_id.slice(0, 8)}`
            });
          }
          return students;
        }, []);
        setAvailableStudents(uniqueStudents);
      }
      
    } catch (error) {
      console.error('Error loading analytics data:', error);
      setAnalyticsData(null);
    } finally {
      setLoading(false);
    }
  };

  const loadClassAnalytics = async () => {
    if (!classAnalytics) {
      try {
        const classId = selectedClass !== 'all' ? selectedClass : null;
        const data = await teacherAPI.getClassStrengthsWeaknesses(classId);
        setClassAnalytics(data);
      } catch (error) {
        console.error('Error loading class analytics:', error);
        setClassAnalytics(null);
      }
    }
  };

  const loadStudentAnalytics = async (studentId) => {
    try {
      const data = await teacherAPI.getStudentStrengthsWeaknesses(studentId);
      setStudentAnalytics(data);
    } catch (error) {
      console.error('Error loading student analytics:', error);
      setStudentAnalytics(null);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-neon-green';
    if (score >= 60) return 'text-neon-yellow';
    return 'text-neon-pink';
  };

  const getGradeDistribution = () => {
    if (!analyticsData?.testResults) return [];
    
    // Group test results by student to avoid counting the same student multiple times
    const studentScores = {};
    analyticsData.testResults.forEach(test => {
      const studentId = test.student_id;
      const score = test.score;
      
      // Keep track of each student's highest score to avoid inflating counts
      if (!studentScores[studentId] || studentScores[studentId] < score) {
        studentScores[studentId] = score;
      }
    });
    
    // Get unique student scores (highest score per student)
    const uniqueStudentScores = Object.values(studentScores);
    
    const ranges = [
      { label: '90-100%', min: 90, max: 100, color: 'from-neon-green/20 to-emerald-500/20' },
      { label: '80-89%', min: 80, max: 89, color: 'from-green-500/20 to-teal-500/20' },
      { label: '70-79%', min: 70, max: 79, color: 'from-yellow-500/20 to-orange-500/20' },
      { label: '60-69%', min: 60, max: 69, color: 'from-orange-500/20 to-red-500/20' },
      { label: 'Below 60%', min: 0, max: 59, color: 'from-red-500/20 to-pink-500/20' }
    ];

    return ranges.map(range => {
      const studentsInRange = uniqueStudentScores.filter(score => score >= range.min && score <= range.max).length;
      return {
        ...range,
        count: studentsInRange,
        percentage: uniqueStudentScores.length > 0 ? ((studentsInRange / uniqueStudentScores.length) * 100).toFixed(1) : 0
      };
    });
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
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
          <div className="space-y-2">
            <LiquidButton
              variant="secondary"
              onClick={() => onNavigate('teacher-dashboard')}
              className="mb-4"
            >
              ← Teacher Dashboard
            </LiquidButton>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              📊 Advanced Analytics
            </h1>
            <p className="text-secondary text-lg">
              Comprehensive performance analysis and student progress tracking
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-2xl p-2">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'class-analysis', label: '🏫 Class Analysis', icon: '🏫' },
              { id: 'individual', label: '👤 Individual Students', icon: '👤' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === 'class-analysis') {
                    loadClassAnalytics();
                  }
                }}
                className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-primary text-white shadow-lg'
                    : 'text-secondary hover:text-primary hover:bg-glass/50'
                }`}
              >
                {tab.icon} {tab.label.split(' ')[1]}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Filter Controls */}
            <LiquidCard className="mb-8" holographic>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                    <span className="text-sm font-bold">🎯</span>
                  </div>
                  <h2 className="text-xl font-semibold text-primary">Filter Options</h2>
                </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Select Class
                </label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full p-3 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary"
                  style={{
                    color: '#e2e8f0'
                  }}
                >
                  <option value="all" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    📚 All Classes
                  </option>
                  {/* Dynamic class options would go here */}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Subject Filter
                </label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="w-full p-3 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary"
                  style={{
                    color: '#e2e8f0'
                  }}
                >
                  <option value="all" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    📖 All Subjects
                  </option>
                  <option value="math" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    🔢 Mathematics
                  </option>
                  <option value="physics" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    ⚛️ Physics
                  </option>
                  <option value="chemistry" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    🧪 Chemistry
                  </option>
                  <option value="biology" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    🧬 Biology
                  </option>
                  <option value="english" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    📚 English
                  </option>
                  <option value="history" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    🏛️ History
                  </option>
                  <option value="geography" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>
                    🌍 Geography
                  </option>
                </select>
              </div>
            </div>
          </div>
        </LiquidCard>

        {analyticsData?.overview ? (
          <>
            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <LiquidStatsCard
                title="Total Tests"
                value={analyticsData.overview.total_tests}
                icon="📝"
                gradient="from-blue-500/20 to-cyan-500/20"
                trend="Practice assessments"
              />
              
              <LiquidStatsCard
                title="Active Students"
                value={analyticsData.overview.total_students}
                icon="👥"
                gradient="from-green-500/20 to-emerald-500/20"
                trend="Enrolled learners"
              />
              
              <LiquidStatsCard
                title="Average Score"
                value={`${analyticsData.overview.average_score.toFixed(1)}%`}
                icon="📊"
                gradient="from-purple-500/20 to-indigo-500/20"
                trend="Class performance"
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
              {/* Grade Distribution */}
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center">
                      <span className="text-sm font-bold">📈</span>
                    </div>
                    <h2 className="text-xl font-bold text-primary">Performance Distribution</h2>
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
                              {test.student_name || 'Unknown Student'}
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
                  <h2 className="text-xl font-bold text-primary">Detailed Test Results</h2>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-primary/20">
                        <th className="text-left p-3 text-secondary font-medium">Student Name</th>
                        <th className="text-left p-3 text-secondary font-medium">Subject</th>
                        <th className="text-left p-3 text-secondary font-medium">Score</th>
                        <th className="text-left p-3 text-secondary font-medium">Questions</th>
                        <th className="text-left p-3 text-secondary font-medium">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyticsData.testResults.map((test, index) => (
                        <tr key={index} className="border-b border-primary/10 hover:bg-glass transition-colors">
                          <td className="p-3 text-primary font-medium">{test.student_name || 'Unknown Student'}</td>
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
            <h2 className="text-2xl font-bold text-primary mb-4">No Analytics Data Available</h2>
            <p className="text-secondary mb-8">
              No test data found for the selected filters. Students need to complete practice tests to generate analytics.
            </p>
            <LiquidButton onClick={() => onNavigate('teacher-dashboard')}>
              ← Return to Dashboard
            </LiquidButton>
          </LiquidCard>
        )}
        </>
        )}

        {/* Class Analysis Tab */}
        {activeTab === 'class-analysis' && (
          <div className="space-y-8">
            {classAnalytics ? (
              <>
                {/* Class Overview Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-blue mb-2">
                      {classAnalytics.total_students}
                    </div>
                    <p className="text-secondary">Total Students</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-green mb-2">
                      {classAnalytics.total_tests}
                    </div>
                    <p className="text-secondary">Total Tests</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-purple mb-2">
                      {classAnalytics.class_strengths.length}
                    </div>
                    <p className="text-secondary">Class Strengths</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-yellow mb-2">
                      {classAnalytics.class_weaknesses.length}
                    </div>
                    <p className="text-secondary">Areas for Focus</p>
                  </LiquidCard>
                </div>

                {/* Class Strengths and Weaknesses */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Strengths */}
                  <LiquidCard className="p-6">
                    <div className="flex items-center space-x-3 mb-6">
                      <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <span className="text-xl">💪</span>
                      </div>
                      <h2 className="text-2xl font-bold text-green-400">Class Strengths</h2>
                    </div>
                    
                    {classAnalytics.class_strengths.length > 0 ? (
                      <div className="space-y-4">
                        {classAnalytics.class_strengths.map((strength, index) => (
                          <div key={index} className="p-4 bg-green-500/10 border border-green-400/30 rounded-xl">
                            <div className="flex justify-between items-center mb-2">
                              <h3 className="font-semibold text-green-400">{strength.subject_display}</h3>
                              <span className="text-green-400 font-bold">{strength.average_score}%</span>
                            </div>
                            <p className="text-sm text-secondary">
                              {strength.students_tested} students tested • {strength.total_tests} tests
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-secondary mt-2">
                              <span>Accuracy: {strength.accuracy_rate}%</span>
                              <span>Grade: {strength.grade}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="text-4xl mb-4">🌱</div>
                        <p className="text-secondary">No significant class strengths identified yet.</p>
                      </div>
                    )}
                  </LiquidCard>

                  {/* Weaknesses */}
                  <LiquidCard className="p-6">
                    <div className="flex items-center space-x-3 mb-6">
                      <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                        <span className="text-xl">🎯</span>
                      </div>
                      <h2 className="text-2xl font-bold text-red-400">Areas for Focus</h2>
                    </div>
                    
                    {classAnalytics.class_weaknesses.length > 0 ? (
                      <div className="space-y-4">
                        {classAnalytics.class_weaknesses.map((weakness, index) => (
                          <div key={index} className="p-4 bg-red-500/10 border border-red-400/30 rounded-xl">
                            <div className="flex justify-between items-center mb-2">
                              <h3 className="font-semibold text-red-400">{weakness.subject_display}</h3>
                              <span className="text-red-400 font-bold">{weakness.average_score}%</span>
                            </div>
                            <p className="text-sm text-secondary">
                              {weakness.students_tested} students need help • {weakness.total_tests} tests
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-secondary mt-2">
                              <span>Priority: {weakness.weakness_level}</span>
                              <span>Grade: {weakness.grade}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="text-4xl mb-4">🎉</div>
                        <p className="text-secondary">No significant class weaknesses identified!</p>
                      </div>
                    )}
                  </LiquidCard>
                </div>

                {/* Recommendations */}
                {classAnalytics.recommendations && classAnalytics.recommendations.length > 0 && (
                  <LiquidCard className="p-6">
                    <div className="flex items-center space-x-3 mb-6">
                      <div className="w-10 h-10 rounded-full bg-accent-blue/20 flex items-center justify-center">
                        <span className="text-xl">💡</span>
                      </div>
                      <h2 className="text-2xl font-bold text-accent-blue">Teaching Recommendations</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {classAnalytics.recommendations.map((rec, index) => (
                        <div key={index} className={`p-4 border rounded-xl ${
                          rec.priority === 'critical' ? 'border-red-400 bg-red-500/10 text-red-400' :
                          rec.priority === 'high' ? 'border-orange-400 bg-orange-500/10 text-orange-400' :
                          'border-blue-400 bg-blue-500/10 text-blue-400'
                        }`}>
                          <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold capitalize">{rec.type.replace('_', ' ')}</h3>
                            <span className="text-xs px-2 py-1 rounded-full bg-current/20 font-medium">
                              {rec.priority}
                            </span>
                          </div>
                          <p className="text-sm mb-3" dangerouslySetInnerHTML={{ __html: rec.message }} />
                          <div className="space-y-1">
                            {rec.suggested_actions.slice(0, 2).map((action, i) => (
                              <div key={i} className="text-xs opacity-80">• {action}</div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </LiquidCard>
                )}

                {/* Subject Analysis */}
                <LiquidCard className="p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 rounded-full bg-accent-purple/20 flex items-center justify-center">
                      <span className="text-xl">📚</span>
                    </div>
                    <h2 className="text-2xl font-bold text-accent-purple">Subject Performance</h2>
                  </div>
                  
                  {classAnalytics.subject_analysis.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {classAnalytics.subject_analysis.map((subject, index) => (
                        <div key={index} className="p-4 bg-glass/30 rounded-xl">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-bold text-primary">{subject.subject_display}</h3>
                            <div className={`px-2 py-1 rounded text-xs font-bold ${
                              subject.grade === 'A' ? 'bg-green-500/20 text-green-400' :
                              subject.grade === 'B' ? 'bg-blue-500/20 text-blue-400' :
                              subject.grade === 'C' ? 'bg-yellow-500/20 text-yellow-400' :
                              subject.grade === 'D' ? 'bg-orange-500/20 text-orange-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {subject.grade}
                            </div>
                          </div>
                          <div className="space-y-1 text-sm text-secondary">
                            <div>Average: <span className="text-primary font-medium">{subject.average_score}%</span></div>
                            <div>Students: <span className="text-primary font-medium">{subject.students_tested}</span></div>
                            <div>Tests: <span className="text-primary font-medium">{subject.total_tests}</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">📚</div>
                      <p className="text-secondary">No subject data available yet.</p>
                    </div>
                  )}
                </LiquidCard>
              </>
            ) : (
              <LiquidCard className="text-center p-12">
                <div className="text-6xl mb-6">📊</div>
                <h2 className="text-2xl font-bold text-primary mb-4">Loading Class Analysis...</h2>
                <p className="text-secondary">
                  Analyzing class-wide performance patterns and generating insights.
                </p>
              </LiquidCard>
            )}
          </div>
        )}

        {/* Individual Student Tab */}
        {activeTab === 'individual' && (
          <div className="space-y-8">
            <LiquidCard className="p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-accent-purple/20 flex items-center justify-center">
                  <span className="text-xl">👤</span>
                </div>
                <h2 className="text-2xl font-bold text-accent-purple">Select Student</h2>
              </div>
              
              {availableStudents.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availableStudents.map((student) => (
                    <button
                      key={student.student_id}
                      onClick={() => {
                        setSelectedStudent(student.student_id);
                        loadStudentAnalytics(student.student_id);
                      }}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                        selectedStudent === student.student_id
                          ? 'border-accent-blue bg-accent-blue/10'
                          : 'border-primary/20 bg-glass/30 hover:border-accent-blue/50'
                      }`}
                    >
                      <div className="font-semibold text-primary">{student.student_name}</div>
                      <div className="text-sm text-secondary">
                        ID: {student.student_id.slice(0, 8)}...
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-secondary">No students with test data found.</p>
                </div>
              )}
            </LiquidCard>

            {/* Student Analytics Display */}
            {studentAnalytics && selectedStudent && (
              <>
                {/* Student Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-blue mb-2">
                      {studentAnalytics.overall_performance.average_score}%
                    </div>
                    <p className="text-secondary">Average Score</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-green mb-2">
                      {studentAnalytics.overall_performance.total_tests}
                    </div>
                    <p className="text-secondary">Tests Taken</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-purple mb-2">
                      {studentAnalytics.strengths.length}
                    </div>
                    <p className="text-secondary">Strengths</p>
                  </LiquidCard>
                  
                  <LiquidCard className="text-center p-6">
                    <div className="text-3xl font-bold text-accent-yellow mb-2">
                      {studentAnalytics.weaknesses.length}
                    </div>
                    <p className="text-secondary">Focus Areas</p>
                  </LiquidCard>
                </div>

                {/* Student Strengths and Weaknesses */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <LiquidCard className="p-6">
                    <h3 className="text-xl font-bold text-green-400 mb-4">
                      💪 {studentAnalytics.student_name}'s Strengths
                    </h3>
                    {studentAnalytics.strengths.length > 0 ? (
                      <div className="space-y-3">
                        {studentAnalytics.strengths.map((strength, index) => (
                          <div key={index} className="p-3 bg-green-500/10 border border-green-400/30 rounded-lg">
                            <div className="flex justify-between">
                              <span className="font-medium text-green-400">{strength.subject_display}</span>
                              <span className="text-green-400 font-bold">{strength.average_score}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-secondary">No significant strengths identified yet.</p>
                    )}
                  </LiquidCard>

                  <LiquidCard className="p-6">
                    <h3 className="text-xl font-bold text-red-400 mb-4">
                      🎯 Areas for Improvement
                    </h3>
                    {studentAnalytics.weaknesses.length > 0 ? (
                      <div className="space-y-3">
                        {studentAnalytics.weaknesses.map((weakness, index) => (
                          <div key={index} className="p-3 bg-red-500/10 border border-red-400/30 rounded-lg">
                            <div className="flex justify-between">
                              <span className="font-medium text-red-400">{weakness.subject_display}</span>
                              <span className="text-red-400 font-bold">{weakness.average_score}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-secondary">No significant weaknesses identified!</p>
                    )}
                  </LiquidCard>
                </div>

                {/* Teacher Recommendations for Student */}
                {studentAnalytics.recommendations && studentAnalytics.recommendations.length > 0 && (
                  <LiquidCard className="p-6">
                    <h3 className="text-xl font-bold text-accent-blue mb-4">
                      💡 Teaching Recommendations for {studentAnalytics.student_name}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {studentAnalytics.recommendations.slice(0, 4).map((rec, index) => (
                        <div key={index} className={`p-4 border rounded-xl ${
                          rec.priority === 'high' ? 'border-red-400 bg-red-500/10' :
                          'border-blue-400 bg-blue-500/10'
                        }`}>
                          <h4 className="font-semibold mb-2 capitalize">
                            {rec.type.replace('_', ' ')}
                          </h4>
                          <p className="text-sm mb-2" dangerouslySetInnerHTML={{ __html: rec.message }} />
                          <div className="space-y-1">
                            {rec.suggested_actions.slice(0, 2).map((action, i) => (
                              <div key={i} className="text-xs opacity-80">• {action}</div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </LiquidCard>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherAnalyticsDashboard;