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
      </div>
    </div>
  );
};

export default TeacherAnalyticsDashboard;