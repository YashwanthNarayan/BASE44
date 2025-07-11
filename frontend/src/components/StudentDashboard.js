import React from 'react';
import { defaultDashboardData } from '../utils/constants';
import { calculateLevel, getXPForNextLevel } from '../utils/helpers';

const StudentDashboard = ({ student, onNavigate, dashboardData, onLogout }) => {
  const data = dashboardData || defaultDashboardData;
  const level = calculateLevel(data.xp_points || 0);
  const xpForNext = getXPForNextLevel(data.xp_points || 0);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">
              {getGreeting()}, {student?.name || 'Student'}! 🌟
            </h1>
            <p className="text-gray-600 mt-2">Ready to continue your learning journey?</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-white rounded-xl px-4 py-2 shadow-sm">
              <div className="text-sm text-gray-600">Level {level}</div>
              <div className="text-lg font-bold text-indigo-600">{data.xp_points || 0} XP</div>
              <div className="text-xs text-gray-500">{xpForNext} XP to next level</div>
            </div>
            <button
              onClick={onLogout}
              className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:border-gray-400 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">💬</div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{data.total_messages || 0}</div>
                <div className="text-sm text-gray-600">AI Conversations</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📝</div>
              <div>
                <div className="text-2xl font-bold text-green-600">{data.total_tests || 0}</div>
                <div className="text-sm text-gray-600">Practice Tests</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📊</div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{(data.average_score || 0).toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🔥</div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{data.study_streak || 0}</div>
                <div className="text-sm text-gray-600">Day Streak</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <button
            onClick={() => onNavigate('tutor')}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 text-left"
          >
            <div className="text-3xl mb-3">🎓</div>
            <h3 className="font-semibold mb-2">Study with AI Tutor</h3>
            <p className="text-sm opacity-90">Get personalized help in any subject</p>
          </button>
          <button
            onClick={() => onNavigate('practice')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">📝</div>
            <h3 className="font-semibold text-gray-900 mb-2">Practice Tests</h3>
            <p className="text-sm text-gray-600">Take adaptive quizzes to test your knowledge</p>
          </button>
          <button
            onClick={() => onNavigate('mindfulness')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">🧘</div>
            <h3 className="font-semibold text-gray-900 mb-2">Mindfulness</h3>
            <p className="text-sm text-gray-600">Breathing exercises and stress management</p>
          </button>
          <button
            onClick={() => onNavigate('calendar')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">📅</div>
            <h3 className="font-semibold text-gray-900 mb-2">My Schedule</h3>
            <p className="text-sm text-gray-600">View your study schedule and events</p>
          </button>
        </div>

        {/* Additional Quick Actions Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <button
            onClick={() => onNavigate('progress')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">📊</div>
            <h3 className="font-semibold text-gray-900 mb-2">Progress Tracker</h3>
            <p className="text-sm text-gray-600">View your learning progress and achievements</p>
          </button>
          <button
            onClick={() => onNavigate('notes')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">📚</div>
            <h3 className="font-semibold text-gray-900 mb-2">My Notes</h3>
            <p className="text-sm text-gray-600">Access your study notes library</p>
          </button>
          <button
            onClick={() => onNavigate('notifications')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">🔔</div>
            <h3 className="font-semibold text-gray-900 mb-2">Notifications</h3>
            <p className="text-sm text-gray-600">Check updates and announcements</p>
          </button>
          <button
            onClick={() => onNavigate('classes')}
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-200 text-left"
          >
            <div className="text-3xl mb-3">🏫</div>
            <h3 className="font-semibold text-gray-900 mb-2">My Classes</h3>
            <p className="text-sm text-gray-600">View joined classes and join new ones</p>
          </button>
        </div>

        {/* Recent Activity & Achievements */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Scores */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Recent Performance</h2>
            {data.recent_scores && data.recent_scores.length > 0 ? (
              <div className="space-y-3">
                {data.recent_scores.slice(0, 5).map((score, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium capitalize">{score.subject || 'General'}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        {score.date ? new Date(score.date).toLocaleDateString() : 'Recent'}
                      </span>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      score.score >= 80 ? 'bg-green-100 text-green-800' :
                      score.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {score.score}%
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">📊</div>
                <p className="text-gray-600">No recent test scores</p>
                <button
                  onClick={() => onNavigate('practice')}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Take a Practice Test
                </button>
              </div>
            )}
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">🏆 Recent Achievements</h2>
            {data.achievements && data.achievements.length > 0 ? (
              <div className="space-y-3">
                {data.achievements.slice(0, 5).map((achievement, index) => (
                  <div key={index} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                    <div className="text-2xl mr-3">🏆</div>
                    <div>
                      <span className="font-medium">{achievement.title}</span>
                      <span className="text-sm text-gray-600 block">{achievement.description}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">🏆</div>
                <p className="text-gray-600">No achievements yet</p>
                <p className="text-sm text-gray-500 mt-2">Start practicing to earn your first achievement!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;