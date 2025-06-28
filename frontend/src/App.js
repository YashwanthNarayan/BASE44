import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Setup axios auth
const setupAxiosAuth = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Auth Portal Component
const AuthPortal = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [userType, setUserType] = useState('student');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    grade_level: '9th',
    school_name: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { ...formData, user_type: userType };

      const response = await axios.post(`${API_BASE}${endpoint}`, payload);
      
      // Store auth data
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_type', response.data.user_type);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Setup axios auth
      setupAxiosAuth(response.data.access_token);
      
      onAuthSuccess(response.data.user_type, response.data.user);
    } catch (error) {
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">K</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Project K</h1>
          <p className="text-gray-600">AI-Powered Educational Platform</p>
        </div>

        {/* Toggle between Login/Register */}
        <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              isLogin ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              !isLogin ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            Register
          </button>
        </div>

        {/* User Type Selection for Registration */}
        {!isLogin && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">I am a:</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setUserType('student')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  userType === 'student'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-1">🎓</div>
                <div className="font-medium">Student</div>
              </button>
              <button
                type="button"
                onClick={() => setUserType('teacher')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  userType === 'teacher'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-1">👩‍🏫</div>
                <div className="font-medium">Teacher</div>
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          {!isLogin && userType === 'student' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Grade Level</label>
              <select
                value={formData.grade_level}
                onChange={(e) => setFormData(prev => ({ ...prev, grade_level: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {['6th', '7th', '8th', '9th', '10th', '11th', '12th'].map(grade => (
                  <option key={grade} value={grade}>{grade} Grade</option>
                ))}
              </select>
            </div>
          )}

          {!isLogin && userType === 'teacher' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">School Name</label>
              <input
                type="text"
                value={formData.school_name}
                onChange={(e) => setFormData(prev => ({ ...prev, school_name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>
    </div>
  );
};

// Notes Component
const NotesComponent = ({ student, onNavigate }) => {
  const [currentView, setCurrentView] = useState('library'); // library, generate, view
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSubject, setFilterSubject] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  // Note generation form
  const [noteForm, setNoteForm] = useState({
    subject: '',
    topic: '',
    note_type: 'comprehensive'
  });

  const subjects = ['math', 'physics', 'chemistry', 'biology', 'english', 'history', 'geography'];
  const noteTypes = [
    { id: 'comprehensive', name: 'Comprehensive Notes', description: 'Detailed notes with examples and explanations' },
    { id: 'summary', name: 'Summary Notes', description: 'Concise overview of key points' },
    { id: 'quick_reference', name: 'Quick Reference', description: 'Essential formulas and facts' }
  ];

  useEffect(() => {
    if (currentView === 'library') {
      loadNotes();
    }
  }, [currentView, filterSubject, showFavoritesOnly]);

  const loadNotes = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterSubject) params.append('subject', filterSubject);
      if (showFavoritesOnly) params.append('favorites_only', 'true');
      
      const response = await axios.get(`${API_BASE}/api/notes?${params}`);
      setNotes(response.data);
    } catch (error) {
      console.error('Error loading notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNotes = async () => {
    if (!noteForm.subject || !noteForm.topic.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(`${API_BASE}/api/notes/generate`, {
        subject: noteForm.subject,
        topic: noteForm.topic.trim(),
        note_type: noteForm.note_type
      });

      // Show the generated note
      setSelectedNote(response.data);
      setCurrentView('view');
      
      // Reset form
      setNoteForm({ subject: '', topic: '', note_type: 'comprehensive' });
      
      // Reload notes library
      setTimeout(() => loadNotes(), 1000);
      
    } catch (error) {
      console.error('Error generating notes:', error);
      alert('Error generating notes. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const viewNote = async (noteId) => {
    try {
      const response = await axios.get(`${API_BASE}/api/notes/${noteId}`);
      setSelectedNote(response.data);
      setCurrentView('view');
    } catch (error) {
      console.error('Error loading note:', error);
    }
  };

  const toggleFavorite = async (noteId) => {
    try {
      await axios.put(`${API_BASE}/api/notes/${noteId}/favorite`);
      loadNotes(); // Reload to reflect changes
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const deleteNote = async (noteId) => {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
      await axios.delete(`${API_BASE}/api/notes/${noteId}`);
      loadNotes(); // Reload to reflect changes
      if (selectedNote && selectedNote.id === noteId) {
        setCurrentView('library');
        setSelectedNote(null);
      }
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      math: '🧮', physics: '⚡', chemistry: '🧪', biology: '🧬',
      english: '📖', history: '🏛️', geography: '🌍'
    };
    return icons[subject] || '📝';
  };

  const formatNoteContent = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold text-gray-900 mb-4">$1</h1>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-semibold text-gray-800 mb-3 mt-6">$1</h2>')
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-700 mb-2 mt-4">$1</h3>')
      .replace(/^\* (.+)$/gm, '<li class="text-gray-700 mb-1">$1</li>')
      .replace(/^- (.+)$/gm, '<li class="text-gray-700 mb-1">$1</li>')
      .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\n\n/g, '</p><p class="text-gray-700 mb-3">')
      .replace(/\n/g, '<br>');
  };

  const filteredNotes = notes.filter(note => {
    const matchesSearch = searchTerm === '' || 
      note.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.content.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Generate Notes View
  if (currentView === 'generate') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center mb-8">
            <button
              onClick={() => setCurrentView('library')}
              className="text-indigo-600 hover:text-indigo-700 mr-4"
            >
              ← Back to Library
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📝 Generate Notes</h1>
              <p className="text-gray-600">Create comprehensive study notes for any topic</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
                <select
                  name="subject"
                  value={noteForm.subject}
                  onChange={(e) => setNoteForm(prev => ({ ...prev, subject: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Choose a subject</option>
                  {subjects.map(subject => (
                    <option key={subject} value={subject}>
                      {getSubjectIcon(subject)} {subject.charAt(0).toUpperCase() + subject.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Topic *</label>
                <input
                  type="text"
                  value={noteForm.topic}
                  onChange={(e) => setNoteForm(prev => ({ ...prev, topic: e.target.value }))}
                  placeholder="e.g., Quadratic Equations, Photosynthesis, World War II"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Note Type</label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {noteTypes.map(type => (
                    <button
                      key={type.id}
                      onClick={() => setNoteForm(prev => ({ ...prev, note_type: type.id }))}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        noteForm.note_type === type.id
                          ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium mb-1">{type.name}</div>
                      <div className="text-sm text-gray-600">{type.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-4">
                <button
                  onClick={generateNotes}
                  disabled={generating || !noteForm.subject || !noteForm.topic.trim()}
                  className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-4 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? (
                    <div className="flex items-center justify-center">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Generating Notes...
                    </div>
                  ) : (
                    'Generate Notes'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // View Note View
  if (currentView === 'view' && selectedNote) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center mb-8">
            <button
              onClick={() => setCurrentView('library')}
              className="text-indigo-600 hover:text-indigo-700 mr-4"
            >
              ← Back to Library
            </button>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">{selectedNote.topic}</h1>
              <div className="flex items-center text-gray-600">
                <span className="mr-2">{getSubjectIcon(selectedNote.subject)}</span>
                <span className="capitalize">{selectedNote.subject}</span>
                <span className="mx-2">•</span>
                <span>{new Date(selectedNote.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => toggleFavorite(selectedNote.id)}
                className="p-2 rounded-full hover:bg-gray-100"
                title={selectedNote.is_favorite ? "Remove from favorites" : "Add to favorites"}
              >
                {selectedNote.is_favorite ? (
                  <span className="text-2xl">⭐</span>
                ) : (
                  <span className="text-2xl">☆</span>
                )}
              </button>
              <button
                onClick={() => deleteNote(selectedNote.id)}
                className="p-2 rounded-full hover:bg-gray-100"
                title="Delete note"
              >
                <span className="text-2xl">🗑️</span>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div 
              className="prose prose-indigo max-w-none"
              dangerouslySetInnerHTML={{ __html: `<p class="text-gray-700 mb-3">${formatNoteContent(selectedNote.content)}</p>` }}
            />
          </div>
        </div>
      </div>
    );
  }

  // Library View (Default)
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => onNavigate('student-dashboard')}
              className="text-indigo-600 hover:text-indigo-700 mr-4"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📚 My Notes</h1>
              <p className="text-gray-600">Your personal study notes library</p>
            </div>
          </div>
          <button
            onClick={() => setCurrentView('generate')}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all"
          >
            Generate New Notes
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search notes..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <div className="absolute left-3 top-2.5 text-gray-400">🔍</div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={filterSubject}
                onChange={(e) => setFilterSubject(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Subjects</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>
                    {subject.charAt(0).toUpperCase() + subject.slice(1)}
                  </option>
                ))}
              </select>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showFavoritesOnly}
                  onChange={(e) => setShowFavoritesOnly(e.target.checked)}
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="text-gray-700">Favorites only</span>
              </label>
            </div>
          </div>
        </div>

        {/* Notes Grid */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredNotes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredNotes.map(note => (
              <div
                key={note.id}
                className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 overflow-hidden cursor-pointer"
                onClick={() => viewNote(note.id)}
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                        <span className="text-xl">{getSubjectIcon(note.subject)}</span>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 capitalize">{note.subject}</div>
                        <div className="text-xs text-gray-500">{new Date(note.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                    {note.is_favorite && <div className="text-yellow-500">⭐</div>}
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">{note.topic}</h3>
                  <p className="text-gray-600 text-sm line-clamp-3">{note.content.replace(/#+\s|[*_]/g, '')}</p>
                </div>
                <div className="px-6 py-3 bg-gray-50 flex justify-between items-center">
                  <div className="text-xs text-gray-500">
                    {note.note_type === 'comprehensive' && 'Comprehensive Notes'}
                    {note.note_type === 'summary' && 'Summary Notes'}
                    {note.note_type === 'quick_reference' && 'Quick Reference'}
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavorite(note.id);
                      }}
                      className="text-gray-400 hover:text-yellow-500"
                    >
                      {note.is_favorite ? '⭐' : '☆'}
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNote(note.id);
                      }}
                      className="text-gray-400 hover:text-red-500"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No notes found</h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || filterSubject || showFavoritesOnly
                ? "No notes match your current filters. Try adjusting your search or filters."
                : "You haven't created any notes yet. Click the 'Generate New Notes' button to get started!"}
            </p>
            {(searchTerm || filterSubject || showFavoritesOnly) && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterSubject('');
                  setShowFavoritesOnly(false);
                }}
                className="text-indigo-600 hover:text-indigo-700"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Student Dashboard Component
const StudentDashboard = ({ student, onNavigate, dashboardData, onLogout }) => {
  const subjects = ['math', 'physics', 'chemistry', 'biology', 'english', 'history', 'geography'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Project K</h1>
                <p className="text-sm text-gray-600">Student Portal</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium text-gray-900">{student?.name}</div>
                <div className="text-xs text-gray-600">Grade {student?.grade_level}</div>
              </div>
              <button
                onClick={onLogout}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Card */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Welcome back, {student?.name}! 👋</h2>
              <p className="text-gray-600 mt-1">Ready to continue your learning journey?</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-indigo-600">{dashboardData?.stats?.total_xp || 0} XP</div>
              <div className="text-sm text-gray-600">🔥 {dashboardData?.stats?.study_streak || 0} day streak</div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">📚</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.stats?.subjects_studied || 0}</div>
                <div className="text-sm text-gray-600">Subjects Studied</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">💬</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.stats?.total_messages || 0}</div>
                <div className="text-sm text-gray-600">Questions Asked</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">🏆</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.profile?.level || 1}</div>
                <div className="text-sm text-gray-600">Current Level</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">🔔</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.notifications?.length || 0}</div>
                <div className="text-sm text-gray-600">New Notifications</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <button
            onClick={() => onNavigate('subjects')}
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
            <p className="text-sm text-gray-600">Check messages and updates</p>
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

        {/* Subjects Grid */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Choose a Subject to Study</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {subjects.map((subject) => (
              <button
                key={subject}
                onClick={() => onNavigate('chat', subject)}
                className="bg-gray-50 hover:bg-indigo-50 border border-gray-200 hover:border-indigo-300 p-4 rounded-xl transition-all duration-200 transform hover:scale-105 text-center"
              >
                <div className="text-3xl mb-2">
                  {subject === 'math' && '🧮'}
                  {subject === 'physics' && '⚡'}
                  {subject === 'chemistry' && '🧪'}
                  {subject === 'biology' && '🧬'}
                  {subject === 'english' && '📖'}
                  {subject === 'history' && '🏛️'}
                  {subject === 'geography' && '🌍'}
                </div>
                <div className="font-medium capitalize text-gray-900">{subject}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Today's Schedule */}
        {dashboardData?.today_events?.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Today's Schedule</h2>
            <div className="space-y-3">
              {dashboardData.today_events.map((event, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl">📅</div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{event.title}</div>
                    <div className="text-sm text-gray-600">
                      {new Date(event.start_time).toLocaleTimeString()} - {event.event_type}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Activity */}
        {dashboardData?.recent_activity?.messages?.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {dashboardData.recent_activity.messages.slice(0, 5).map((message, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl">
                    {message.subject === 'math' && '🧮'}
                    {message.subject === 'physics' && '⚡'}
                    {message.subject === 'chemistry' && '🧪'}
                    {message.subject === 'biology' && '🧬'}
                    {message.subject === 'english' && '📖'}
                    {message.subject === 'history' && '🏛️'}
                    {message.subject === 'geography' && '🌍'}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium capitalize text-gray-900">{message.subject}</div>
                    <div className="text-sm text-gray-600 truncate">{message.user_message}</div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Notifications Component
const NotificationsComponent = ({ student, onNavigate }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API_BASE}/api/notifications`, { headers });
      setNotifications(response.data);
    } catch (error) {
      console.error('Error loading notifications:', error);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      await axios.put(`${API_BASE}/api/notifications/${notificationId}/read`, {}, { headers });
      
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, is_read: true }
            : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'achievement': return '🏆';
      case 'reminder': return '⏰';
      case 'message': return '💬';
      case 'assignment': return '📝';
      case 'grade': return '📊';
      default: return '📢';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'achievement': return 'border-yellow-200 bg-yellow-50';
      case 'reminder': return 'border-blue-200 bg-blue-50';
      case 'message': return 'border-green-200 bg-green-50';
      case 'assignment': return 'border-purple-200 bg-purple-50';
      case 'grade': return 'border-indigo-200 bg-indigo-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now - time) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return time.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading notifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">🔔 Notifications</h1>
          <p className="text-gray-600">Stay updated with your learning progress and reminders</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg">
          {notifications.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {notifications.map((notification, index) => (
                <div
                  key={notification.id || index}
                  className={`p-6 border-l-4 transition-colors ${getNotificationColor(notification.type)} ${
                    !notification.is_read ? 'border-l-indigo-500' : 'border-l-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="text-2xl">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className={`font-semibold ${!notification.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                            {notification.title}
                          </h3>
                          {!notification.is_read && (
                            <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                          )}
                        </div>
                        <p className={`${!notification.is_read ? 'text-gray-700' : 'text-gray-600'} mb-2`}>
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">
                            {formatTimeAgo(notification.created_at)}
                          </span>
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <div className="text-6xl mb-4">🔔</div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">No notifications yet</h2>
              <p className="text-gray-600 mb-6">
                You'll receive notifications about your progress, achievements, and reminders here.
              </p>
              <button
                onClick={() => onNavigate('student-dashboard')}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        {notifications.length > 0 && (
          <div className="mt-8 text-center">
            <button
              onClick={() => {
                // Mark all as read
                notifications.forEach(notif => {
                  if (!notif.is_read) {
                    markAsRead(notif.id);
                  }
                });
              }}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors mr-4"
            >
              Mark All as Read
            </button>
            <button
              onClick={() => onNavigate('student-dashboard')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Tutor Component (AI Chat)
const TutorComponent = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');

  const subjects = [
    { value: 'math', name: 'Mathematics', icon: '🔢' },
    { value: 'physics', name: 'Physics', icon: '⚛️' },
    { value: 'chemistry', name: 'Chemistry', icon: '🧪' },
    { value: 'biology', name: 'Biology', icon: '🧬' },
    { value: 'english', name: 'English', icon: '📚' },
    { value: 'history', name: 'History', icon: '🏛️' },
    { value: 'geography', name: 'Geography', icon: '🌍' }
  ];

  useEffect(() => {
    if (selectedSubject) {
      startNewSession();
    }
  }, [selectedSubject]);

  const startNewSession = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await axios.post(`${API_BASE}/api/tutor/session`, {
        subject: selectedSubject
      }, { headers });

      setSessionId(response.data.session_id);
      setMessages([
        {
          role: 'assistant',
          content: `Hello! I'm your ${selectedSubject} tutor. I'm here to help you understand concepts, solve problems, and answer any questions you have. What would you like to learn about today?`,
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error('Error starting tutor session:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await axios.post(`${API_BASE}/api/tutor/chat`, {
        message: currentMessage,
        subject: selectedSubject,
        session_id: sessionId
      }, { headers });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!selectedSubject) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <button
              onClick={() => onNavigate('student-dashboard')}
              className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900">🤖 AI Tutor</h1>
            <p className="text-gray-600">Get personalized help from your AI tutor</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-semibold mb-6 text-center">Choose a Subject to Get Started</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {subjects.map(subject => (
                <button
                  key={subject.value}
                  onClick={() => setSelectedSubject(subject.value)}
                  className="p-6 border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all duration-200 text-center group"
                >
                  <div className="text-4xl mb-3">{subject.icon}</div>
                  <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {subject.name}
                  </h3>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const selectedSubjectData = subjects.find(s => s.value === selectedSubject);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg h-[600px] flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setSelectedSubject('')}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ← Back
                </button>
                <div className="text-2xl">{selectedSubjectData?.icon}</div>
                <div>
                  <h1 className="text-xl font-semibold">{selectedSubjectData?.name} Tutor</h1>
                  <p className="text-sm text-gray-600">Ask me anything about {selectedSubjectData?.name.toLowerCase()}</p>
                </div>
              </div>
              <button
                onClick={() => onNavigate('student-dashboard')}
                className="text-gray-600 hover:text-gray-800"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 p-4 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Message Input */}
          <div className="p-6 border-t border-gray-200">
            <div className="flex space-x-4">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask your ${selectedSubjectData?.name.toLowerCase()} question here...`}
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows="2"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={!currentMessage.trim() || loading}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Progress Component
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
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const endpoint = selectedSubject === 'all' 
        ? `${API_BASE}/api/practice/results`
        : `${API_BASE}/api/practice/stats/${selectedSubject}`;
        
      const response = await axios.get(endpoint, { headers });
      setProgressData(response.data);
    } catch (error) {
      console.error('Error loading progress data:', error);
      setProgressData(null);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProgressBarColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">📊 Progress Tracker</h1>
          <p className="text-gray-600">Monitor your learning journey and achievements</p>
        </div>

        {/* Subject Filter */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Filter by Subject</h2>
          <div className="flex flex-wrap gap-3">
            {subjects.map(subject => (
              <button
                key={subject}
                onClick={() => setSelectedSubject(subject)}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  selectedSubject === subject
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {subject === 'all' ? 'All Subjects' : subject.charAt(0).toUpperCase() + subject.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {progressData ? (
          <>
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="text-3xl mb-2">📝</div>
                <div className="text-2xl font-bold text-indigo-600">
                  {Array.isArray(progressData) ? progressData.length : progressData.total_tests || 0}
                </div>
                <div className="text-sm text-gray-600">Tests Taken</div>
              </div>
              
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="text-3xl mb-2">📈</div>
                <div className="text-2xl font-bold text-green-600">
                  {Array.isArray(progressData) 
                    ? (progressData.reduce((acc, test) => acc + test.score, 0) / progressData.length || 0).toFixed(1)
                    : (progressData.average_score || 0).toFixed(1)
                  }%
                </div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>
              
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="text-3xl mb-2">🏆</div>
                <div className="text-2xl font-bold text-yellow-600">
                  {Array.isArray(progressData) 
                    ? Math.max(...progressData.map(t => t.score), 0)
                    : (progressData.best_score || 0)
                  }%
                </div>
                <div className="text-sm text-gray-600">Best Score</div>
              </div>
              
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="text-3xl mb-2">❓</div>
                <div className="text-2xl font-bold text-purple-600">
                  {Array.isArray(progressData) 
                    ? progressData.reduce((acc, test) => acc + (test.total_questions || 0), 0)
                    : (progressData.total_questions_answered || 0)
                  }
                </div>
                <div className="text-sm text-gray-600">Questions Answered</div>
              </div>
            </div>

            {/* Recent Tests */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Recent Test Results</h2>
              {(Array.isArray(progressData) ? progressData : progressData.recent_tests || []).length > 0 ? (
                <div className="space-y-4">
                  {(Array.isArray(progressData) ? progressData : progressData.recent_tests || [])
                    .slice(0, 10)
                    .map((test, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getPerformanceColor(test.score)}`}>
                            {test.score}%
                          </div>
                          <div>
                            <div className="font-medium">
                              {test.subject ? test.subject.charAt(0).toUpperCase() + test.subject.slice(1) : 'General'} Test
                            </div>
                            <div className="text-sm text-gray-600">
                              {test.total_questions || test.question_count || 0} questions • {' '}
                              {test.completed_at ? new Date(test.completed_at).toLocaleDateString() : 'Recent'}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="w-24">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getProgressBarColor(test.score)}`}
                            style={{ width: `${test.score}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📝</div>
                  <p className="text-gray-600">No practice tests have been taken yet.</p>
                  <button
                    onClick={() => onNavigate('practice')}
                    className="mt-4 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Take Your First Practice Test
                  </button>
                </div>
              )}
            </div>

            {/* Performance Analysis */}
            {!Array.isArray(progressData) && progressData.subject && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4">
                  {progressData.subject.charAt(0).toUpperCase() + progressData.subject.slice(1)} Performance Analysis
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Study Time</h3>
                    <p className="text-2xl font-bold text-indigo-600">
                      {Math.floor((progressData.total_time_spent || 0) / 60)} minutes
                    </p>
                    <p className="text-sm text-gray-600">Total time spent practicing</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-3">Consistency</h3>
                    <p className="text-2xl font-bold text-green-600">
                      {progressData.total_tests > 5 ? 'Good' : progressData.total_tests > 2 ? 'Fair' : 'Needs Improvement'}
                    </p>
                    <p className="text-sm text-gray-600">Based on practice frequency</p>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-4xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Data Available</h2>
            <p className="text-gray-600 mb-6">Start taking practice tests to see your progress here.</p>
            <button
              onClick={() => onNavigate('practice')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Take a Practice Test
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Calendar Component  
const CalendarComponent = ({ student, onNavigate }) => {
  const [events, setEvents] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    event_type: 'study',
    subject: '',
    start_time: '',
    end_time: ''
  });
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const eventTypes = [
    { value: 'study', label: 'Study Session', icon: '📚' },
    { value: 'assignment', label: 'Assignment Due', icon: '📝' },
    { value: 'exam', label: 'Exam', icon: '📋' },
    { value: 'personal', label: 'Personal', icon: '🗓️' }
  ];

  const subjects = ['math', 'physics', 'chemistry', 'biology', 'english', 'history', 'geography'];

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API_BASE}/api/calendar/events`, { headers });
      setEvents(response.data);
    } catch (error) {
      console.error('Error loading calendar events:', error);
    }
  };

  const createEvent = async () => {
    if (!newEvent.title || !newEvent.start_time || !newEvent.end_time) {
      alert('Please fill in all required fields.');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      await axios.post(`${API_BASE}/api/calendar/events`, newEvent, { headers });
      
      setNewEvent({
        title: '',
        description: '',
        event_type: 'study',
        subject: '',
        start_time: '',
        end_time: ''
      });
      setShowCreateForm(false);
      loadEvents();
      alert('Event created successfully!');
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Failed to create event. Please try again.');
    }
  };

  const getEventsForDate = (date) => {
    return events.filter(event => {
      const eventDate = new Date(event.start_time).toISOString().split('T')[0];
      return eventDate === date;
    });
  };

  const generateCalendarDays = () => {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, currentMonth, day);
      days.push(date);
    }
    
    return days;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">📅 My Schedule</h1>
          <p className="text-gray-600">Manage your study schedule and important events</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Calendar */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">
                  {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h2>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  + Add Event
                </button>
              </div>

              <div className="grid grid-cols-7 gap-1 mb-4">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="p-2 text-center font-semibold text-gray-600">
                    {day}
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-7 gap-1">
                {generateCalendarDays().map((date, index) => {
                  const dateStr = date ? date.toISOString().split('T')[0] : '';
                  const dayEvents = date ? getEventsForDate(dateStr) : [];
                  const isToday = date && date.toDateString() === new Date().toDateString();
                  
                  return (
                    <div
                      key={index}
                      className={`min-h-[80px] p-1 border border-gray-200 ${
                        date ? 'bg-white hover:bg-gray-50' : 'bg-gray-100'
                      } ${isToday ? 'ring-2 ring-indigo-500' : ''}`}
                    >
                      {date && (
                        <>
                          <div className={`text-sm font-medium ${isToday ? 'text-indigo-600' : 'text-gray-900'}`}>
                            {date.getDate()}
                          </div>
                          <div className="space-y-1">
                            {dayEvents.slice(0, 2).map((event, idx) => {
                              const eventType = eventTypes.find(t => t.value === event.event_type);
                              return (
                                <div
                                  key={idx}
                                  className="text-xs p-1 bg-indigo-100 text-indigo-800 rounded truncate"
                                  title={event.title}
                                >
                                  {eventType?.icon} {event.title}
                                </div>
                              );
                            })}
                            {dayEvents.length > 2 && (
                              <div className="text-xs text-gray-500">
                                +{dayEvents.length - 2} more
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Upcoming Events */}
          <div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Upcoming Events</h2>
              <div className="space-y-3">
                {events
                  .filter(event => new Date(event.start_time) >= new Date())
                  .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
                  .slice(0, 5)
                  .map((event, index) => {
                    const eventType = eventTypes.find(t => t.value === event.event_type);
                    return (
                      <div key={index} className="p-3 border border-gray-200 rounded-lg">
                        <div className="flex items-center mb-1">
                          <span className="text-lg mr-2">{eventType?.icon}</span>
                          <span className="font-medium">{event.title}</span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {new Date(event.start_time).toLocaleDateString()} at{' '}
                          {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                        {event.description && (
                          <div className="text-sm text-gray-500 mt-1">{event.description}</div>
                        )}
                      </div>
                    );
                  })}
                {events.filter(event => new Date(event.start_time) >= new Date()).length === 0 && (
                  <p className="text-gray-500 text-center py-4">No upcoming events</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Create Event Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
              <h3 className="text-xl font-semibold mb-4">Create New Event</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                  <input
                    type="text"
                    value={newEvent.title}
                    onChange={(e) => setNewEvent({...newEvent, title: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="Event title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
                  <select
                    value={newEvent.event_type}
                    onChange={(e) => setNewEvent({...newEvent, event_type: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    {eventTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                  <select
                    value={newEvent.subject}
                    onChange={(e) => setNewEvent({...newEvent, subject: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select subject (optional)</option>
                    {subjects.map(subject => (
                      <option key={subject} value={subject}>
                        {subject.charAt(0).toUpperCase() + subject.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time *</label>
                  <input
                    type="datetime-local"
                    value={newEvent.start_time}
                    onChange={(e) => setNewEvent({...newEvent, start_time: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time *</label>
                  <input
                    type="datetime-local"
                    value={newEvent.end_time}
                    onChange={(e) => setNewEvent({...newEvent, end_time: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={newEvent.description}
                    onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    rows="3"
                    placeholder="Event description (optional)"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={createEvent}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Create Event
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Mindfulness Component
const MindfulnessComponent = ({ student, onNavigate }) => {
  const [activeSession, setActiveSession] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [moodBefore, setMoodBefore] = useState('');
  const [moodAfter, setMoodAfter] = useState('');

  const mindfulnessActivities = [
    {
      id: 'breathing',
      name: 'Deep Breathing',
      description: 'Focused breathing exercises to reduce stress',
      duration: 5,
      icon: '🫁',
      instructions: 'Breathe in for 4 counts, hold for 4, breathe out for 6. Focus on your breath.'
    },
    {
      id: 'meditation',
      name: 'Guided Meditation',
      description: 'Short meditation session for mental clarity',
      duration: 10,
      icon: '🧘‍♀️',
      instructions: 'Close your eyes, sit comfortably, and focus on the present moment.'
    },
    {
      id: 'body_scan',
      name: 'Body Scan',
      description: 'Progressive relaxation from head to toe',
      duration: 8,
      icon: '💆‍♀️',
      instructions: 'Start from your head and slowly scan down to your toes, releasing tension.'
    },
    {
      id: 'gratitude',
      name: 'Gratitude Practice',
      description: 'Reflect on things you are grateful for',
      duration: 3,
      icon: '🙏',
      instructions: 'Think of 3 things you are grateful for today and why they matter to you.'
    }
  ];

  const moods = ['😊 Great', '🙂 Good', '😐 Okay', '😔 Low', '😰 Stressed'];

  useEffect(() => {
    loadSessionHistory();
  }, []);

  useEffect(() => {
    let interval;
    if (activeSession && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
    } else if (timeRemaining === 0 && activeSession) {
      completeSession();
    }
    return () => clearInterval(interval);
  }, [activeSession, timeRemaining]);

  const loadSessionHistory = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API_BASE}/api/mindfulness/activities`, { headers });
      setSessionHistory(response.data);
    } catch (error) {
      console.error('Error loading mindfulness history:', error);
    }
  };

  const startSession = (activity) => {
    if (!moodBefore) {
      alert('Please select your current mood before starting the session.');
      return;
    }
    
    setActiveSession(activity);
    setTimeRemaining(activity.duration * 60); // Convert minutes to seconds
  };

  const completeSession = async () => {
    if (!activeSession || !moodAfter) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      await axios.post(`${API_BASE}/api/mindfulness/session`, {
        activity_type: activeSession.id,
        duration: activeSession.duration,
        mood_before: moodBefore,
        mood_after: moodAfter
      }, { headers });

      alert('Great job! Your mindfulness session has been completed.');
      setActiveSession(null);
      setMoodBefore('');
      setMoodAfter('');
      loadSessionHistory();
    } catch (error) {
      console.error('Error saving mindfulness session:', error);
      alert('Session completed, but there was an error saving it.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (activeSession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">{activeSession.icon}</div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{activeSession.name}</h1>
            <div className="text-5xl font-mono text-indigo-600 mb-6">
              {formatTime(timeRemaining)}
            </div>
            
            <div className="bg-gray-50 p-6 rounded-lg mb-6">
              <p className="text-lg text-gray-700">{activeSession.instructions}</p>
            </div>

            {timeRemaining === 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">How do you feel after the session?</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {moods.map((mood) => (
                    <button
                      key={mood}
                      onClick={() => setMoodAfter(mood)}
                      className={`p-3 rounded-lg border transition-colors ${
                        moodAfter === mood
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {mood}
                    </button>
                  ))}
                </div>
                <button
                  onClick={completeSession}
                  disabled={!moodAfter || loading}
                  className="mt-4 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Complete Session'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">🧘 Mindfulness Center</h1>
          <p className="text-gray-600">Take a moment to relax and recharge your mind</p>
        </div>

        {/* Mood Selection */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">How are you feeling right now?</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {moods.map((mood) => (
              <button
                key={mood}
                onClick={() => setMoodBefore(mood)}
                className={`p-4 rounded-lg border transition-colors ${
                  moodBefore === mood
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {mood}
              </button>
            ))}
          </div>
        </div>

        {/* Activities */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {mindfulnessActivities.map((activity) => (
            <div key={activity.id} className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-4xl mb-4">{activity.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{activity.name}</h3>
              <p className="text-gray-600 mb-4">{activity.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">{activity.duration} minutes</span>
                <button
                  onClick={() => startSession(activity)}
                  disabled={!moodBefore}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Start Session
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Session History */}
        {sessionHistory.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Sessions</h2>
            <div className="space-y-3">
              {sessionHistory.slice(0, 5).map((session, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <span className="font-medium capitalize">{session.activity_type.replace('_', ' ')}</span>
                    <span className="text-sm text-gray-600 ml-2">
                      {new Date(session.completed_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {session.duration} min
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Practice Test Component
const PracticeTestComponent = ({ student, onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState([]);
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [testStarted, setTestStarted] = useState(false);

  const subjects = {
    math: { 
      name: 'Mathematics', 
      topics: ['Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics', 'Probability', 'Number Theory', 'Linear Equations', 'Quadratic Equations'] 
    },
    physics: { 
      name: 'Physics', 
      topics: ['Mechanics', 'Thermodynamics', 'Waves', 'Optics', 'Electricity', 'Magnetism', 'Modern Physics', 'Kinematics', 'Dynamics'] 
    },
    chemistry: { 
      name: 'Chemistry', 
      topics: ['Atomic Structure', 'Organic Chemistry', 'Acids & Bases', 'Chemical Bonding', 'Periodic Table', 'Thermochemistry', 'Electrochemistry'] 
    },
    biology: { 
      name: 'Biology', 
      topics: ['Cell Biology', 'Genetics', 'Ecology', 'Human Physiology', 'Plant Biology', 'Evolution', 'Molecular Biology', 'Anatomy'] 
    },
    english: {
      name: 'English',
      topics: ['Grammar', 'Literature', 'Poetry', 'Essay Writing', 'Reading Comprehension', 'Creative Writing', 'Vocabulary', 'Sentence Structure']
    },
    history: {
      name: 'History',
      topics: ['Ancient History', 'Medieval History', 'Modern History', 'World Wars', 'Indian Independence', 'Civilizations', 'Cultural History']
    },
    geography: {
      name: 'Geography',
      topics: ['Physical Geography', 'Human Geography', 'Climate', 'Natural Resources', 'Population', 'Economic Geography', 'Environmental Geography']
    }
  };

  const questionTypes = [
    { value: 'mcq', label: 'Multiple Choice Questions (MCQ)', description: 'Questions with multiple options' },
    { value: 'short_answer', label: 'Short Answer', description: 'Brief written responses' },
    { value: 'long_answer', label: 'Long Answer', description: 'Detailed explanations' },
    { value: 'numerical', label: 'Numerical', description: 'Mathematical calculations' }
  ];

  const handleTopicToggle = (topic) => {
    setSelectedTopics(prev => 
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const handleQuestionTypeToggle = (type) => {
    setSelectedQuestionTypes(prev => 
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const generatePracticeTest = async () => {
    if (!selectedSubject || selectedTopics.length === 0) {
      alert('Please select a subject and at least one topic.');
      return;
    }

    setIsGenerating(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await axios.post(`${API_BASE}/api/practice/generate`, {
        subject: selectedSubject,
        topics: selectedTopics,
        difficulty,
        question_count: numQuestions,
        question_types: selectedQuestionTypes.length > 0 ? selectedQuestionTypes : undefined
      }, { headers });

      setCurrentQuestions(response.data.questions);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setTestStarted(true);
    } catch (error) {
      console.error('Error generating practice test:', error);
      alert('Failed to generate practice test. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAnswerSubmit = (questionId, answer) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < currentQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      submitTest();
    }
  };

  const submitTest = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      await axios.post(`${API_BASE}/api/practice/submit`, {
        questions: currentQuestions.map(q => q.id),
        student_answers: userAnswers,
        time_taken: 300 // placeholder
      }, { headers });

      setShowResults(true);
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Failed to submit test. Please try again.');
    }
  };

  const resetTest = () => {
    setTestStarted(false);
    setCurrentQuestions([]);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
    setSelectedSubject('');
    setSelectedTopics([]);
    setSelectedQuestionTypes([]);
  };

  if (showResults) {
    const score = Object.keys(userAnswers).reduce((acc, qId) => {
      const question = currentQuestions.find(q => q.id === qId);
      if (question && question.correct_answer.toLowerCase() === userAnswers[qId].toLowerCase()) {
        return acc + 1;
      }
      return acc;
    }, 0);

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🎉</div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Complete!</h1>
              <p className="text-lg text-gray-600">
                You scored {score} out of {currentQuestions.length} ({((score/currentQuestions.length)*100).toFixed(1)}%)
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={resetTest}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Take Another Test
              </button>
              <button
                onClick={() => onNavigate('student-dashboard')}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (testStarted && currentQuestions.length > 0) {
    const currentQuestion = currentQuestions[currentQuestionIndex];
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                Question {currentQuestionIndex + 1} of {currentQuestions.length}
              </h1>
              <div className="text-sm text-gray-500">
                {currentQuestion.question_type.toUpperCase()}
              </div>
            </div>
            
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {currentQuestion.question_text}
              </h2>
              
              {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
                <div className="space-y-3">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSubmit(currentQuestion.id, option)}
                      className={`w-full text-left p-4 rounded-lg border transition-colors ${
                        userAnswers[currentQuestion.id] === option
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
              
              {currentQuestion.question_type !== 'mcq' && (
                <textarea
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  rows="4"
                  placeholder="Enter your answer here..."
                  value={userAnswers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerSubmit(currentQuestion.id, e.target.value)}
                />
              )}
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                disabled={currentQuestionIndex === 0}
                className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={nextQuestion}
                disabled={!userAnswers[currentQuestion.id]}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {currentQuestionIndex === currentQuestions.length - 1 ? 'Submit Test' : 'Next Question'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <button
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">📝 Practice Tests</h1>
          <p className="text-gray-600">Create personalized tests to improve your understanding</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Subject Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Subject</label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Choose a subject...</option>
              {Object.entries(subjects).map(([key, subject]) => (
                <option key={key} value={key}>{subject.name}</option>
              ))}
            </select>
          </div>

          {/* Topics Selection */}
          {selectedSubject && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Topics ({selectedTopics.length} selected)
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {subjects[selectedSubject].topics.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => handleTopicToggle(topic)}
                    className={`p-3 text-sm rounded-lg border transition-colors ${
                      selectedTopics.includes(topic)
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Question Types Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Types ({selectedQuestionTypes.length > 0 ? selectedQuestionTypes.length + ' selected' : 'All types'})
            </label>
            <p className="text-sm text-gray-500 mb-3">Leave unselected to include all question types</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {questionTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleQuestionTypeToggle(type.value)}
                  className={`p-4 text-left rounded-lg border transition-colors ${
                    selectedQuestionTypes.includes(type.value)
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-gray-900">{type.label}</div>
                  <div className="text-sm text-gray-600">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Test Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
              <select
                value={numQuestions}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty Level</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
          </div>

          {/* Generate Test Button */}
          <div className="text-center">
            <button
              onClick={generatePracticeTest}
              disabled={!selectedSubject || selectedTopics.length === 0 || isGenerating}
              className="px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
            >
              {isGenerating ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Generating Test...
                </div>
              ) : (
                'Generate Notes'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
function App() {
  const [currentView, setCurrentView] = useState('auth'); // 'auth', 'student-dashboard', 'teacher-dashboard', 'chat', etc.
  const [currentSubject, setCurrentSubject] = useState(null);
  const [user, setUser] = useState(null);
  const [userType, setUserType] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [classPerformance, setClassPerformance] = useState(null);
  const [testResultsLoading, setTestResultsLoading] = useState(false);
  const [filters, setFilters] = useState({
    class_id: '',
    student_id: '',
    subject: ''
  });

  const loadTestResults = async (classId = '', studentId = '', subject = '') => {
    setTestResultsLoading(true);
    try {
      const params = new URLSearchParams();
      if (classId) params.append('class_id', classId);
      if (studentId) params.append('student_id', studentId);
      if (subject) params.append('subject', subject);
      
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/test-results?${params}`);
      setTestResults(response.data.test_results || []);
    } catch (error) {
      console.error('Error loading test results:', error);
      setTestResults([]);
    } finally {
      setTestResultsLoading(false);
    }
  };

  const loadClassPerformance = async (classId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/class-performance/${classId}`);
      setClassPerformance(response.data);
    } catch (error) {
      console.error('Error loading class performance:', error);
      setClassPerformance(null);
    } finally {
      setLoading(false);
    }
  };

  const loadOverviewAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/overview`);
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Error loading overview analytics:', error);
      // Set default structure to prevent crashes
      setAnalyticsData({
        overview_metrics: {
          total_classes: 0,
          total_students: 0,
          total_messages: 0,
          total_tests: 0,
          average_score: 0
        },
        class_summary: [],
        subject_distribution: [],
        weekly_activity_trend: []
      });
    } finally {
      setLoading(false);
    }
  };

  // Check for existing authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUserType = localStorage.getItem('user_type');
    const storedUser = localStorage.getItem('user');

    if (token && storedUserType && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setupAxiosAuth(token);
        setUser(userData);
        setUserType(storedUserType);
        
        if (storedUserType === 'student') {
          setCurrentView('student-dashboard');
          loadDashboardData();
        } else {
          setCurrentView('teacher-dashboard');
        }
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        handleLogout();
      }
    }
  }, []);

  const navigate = (view, subject = null) => {
    setCurrentView(view);
    if (subject) {
      setCurrentSubject(subject);
    }
  };

  const handleAuthSuccess = (userType, userData) => {
    setUser(userData);
    setUserType(userType);
    
    if (userType === 'student') {
      setCurrentView('student-dashboard');
      loadDashboardData();
    } else {
      setCurrentView('teacher-dashboard');
    }
  };

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_type');
    localStorage.removeItem('user');
    setupAxiosAuth(null);
    setUser(null);
    setUserType(null);
    setCurrentView('auth');
    setDashboardData(null);
  };

  if (currentView === 'auth') {
    return <AuthPortal onAuthSuccess={handleAuthSuccess} />;
  }

  if (currentView === 'student-dashboard') {
    return <StudentDashboard student={user} onNavigate={navigate} dashboardData={dashboardData} onLogout={handleLogout} />;
  }

  if (currentView === 'teacher-dashboard') {
    return <TeacherDashboard teacher={user} onNavigate={navigate} />;
  }

  if (currentView === 'teacher-analytics') {
    return <TeacherAnalyticsDashboard teacher={user} onNavigate={navigate} />;
  }

  if (currentView === 'notes') {
    return <NotesComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'practice') {
    return <PracticeTestComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'mindfulness') {
    return <MindfulnessComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'calendar') {
    return <CalendarComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'progress') {
    return <ProgressComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'tutor') {
    return <TutorComponent student={user} onNavigate={navigate} />;
  }

  if (currentView === 'notifications') {
    return <NotificationsComponent student={user} onNavigate={navigate} />;
  }

  // Other views coming soon

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
};

// Teacher Dashboard Component
const TeacherDashboard = ({ teacher, onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    console.log('TeacherDashboard component mounted');
    console.log('Teacher data:', teacher);
    console.log('Stored token:', localStorage.getItem('access_token') ? 'exists' : 'missing');
    console.log('Stored user_type:', localStorage.getItem('user_type'));
    loadTeacherDashboard();
  }, []);

  const loadTeacherDashboard = async () => {
    try {
      console.log('Loading teacher dashboard data...');
      console.log('API_BASE:', API_BASE);
      
      const token = localStorage.getItem('access_token');
      console.log('Token from localStorage:', token ? 'exists' : 'missing');
      
      if (!token) {
        console.error('No access token found');
        setLoading(false);
        return;
      }

      // Ensure the global axios auth header is set
      setupAxiosAuth(token);
      
      console.log('Making API call with global authorization header');
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/overview`);
      console.log('Teacher dashboard response:', response.data);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading teacher dashboard:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">👨‍🏫 Teacher Dashboard</h1>
            <p className="text-gray-600">Welcome back, {teacher?.name || 'Teacher'}!</p>
          </div>
          <button
            onClick={() => onNavigate('auth')}
            className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:border-gray-400 transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🏫</div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{dashboardData?.overview_metrics?.total_classes || 0}</div>
                <div className="text-sm text-gray-600">Classes</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">👥</div>
              <div>
                <div className="text-2xl font-bold text-green-600">{dashboardData?.overview_metrics?.total_students || 0}</div>
                <div className="text-sm text-gray-600">Students</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📝</div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{dashboardData?.overview_metrics?.total_tests || 0}</div>
                <div className="text-sm text-gray-600">Tests Taken</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">📊</div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{(dashboardData?.overview_metrics?.average_score || 0).toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Avg Score</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <button
            onClick={() => onNavigate('teacher-analytics')}
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow text-left group"
          >
            <div className="flex items-center mb-4">
              <div className="text-4xl mr-4">📊</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                  Detailed Analytics
                </h3>
                <p className="text-sm text-gray-600">View comprehensive test results</p>
              </div>
            </div>
            <div className="text-indigo-600 group-hover:text-indigo-700 transition-colors">
              View detailed student performance, question analysis, and insights →
            </div>
          </button>

          <button
            onClick={() => onNavigate('create-class')}
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow text-left group"
          >
            <div className="flex items-center mb-4">
              <div className="text-4xl mr-4">➕</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
                  Create Class
                </h3>
                <p className="text-sm text-gray-600">Set up a new class</p>
              </div>
            </div>
            <div className="text-green-600 group-hover:text-green-700 transition-colors">
              Create and manage your classes →
            </div>
          </button>

          <button
            onClick={() => onNavigate('manage-classes')}
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow text-left group"
          >
            <div className="flex items-center mb-4">
              <div className="text-4xl mr-4">🏫</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  Manage Classes
                </h3>
                <p className="text-sm text-gray-600">View and manage existing classes</p>
              </div>
            </div>
            <div className="text-blue-600 group-hover:text-blue-700 transition-colors">
              Manage students and class settings →
            </div>
          </button>
        </div>

        {/* Recent Classes */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Your Classes</h2>
          {dashboardData?.class_summary?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🏫</div>
              <p>No classes created yet.</p>
              <button
                onClick={() => onNavigate('create-class')}
                className="mt-4 bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Create Your First Class
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dashboardData?.class_summary?.map((cls) => (
                <div key={cls.class_info.class_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-900">{cls.class_info.class_name}</h3>
                    <span className="text-sm text-gray-500">{cls.student_count} students</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Avg Score:</span> {(cls.average_score || 0).toFixed(1)}%
                    </div>
                    <div>
                      <span className="font-medium">Tests:</span> {cls.total_tests || 0}
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Subject: {cls.class_info.subject} • Grade: {cls.class_info.grade_level}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Teacher Analytics Dashboard Component
const TeacherAnalyticsDashboard = ({ teacher, onNavigate }) => {
  const [selectedView, setSelectedView] = useState('overview'); // overview, test-results, class-performance
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [testResults, setTestResults] = useState([]);
  const [classPerformance, setClassPerformance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testResultsLoading, setTestResultsLoading] = useState(false);
  const [filters, setFilters] = useState({
    class_id: '',
    student_id: '',
    subject: ''
  });

  useEffect(() => {
    if (selectedView === 'overview') {
      loadOverviewAnalytics();
    } else if (selectedView === 'test-results') {
      loadTestResults(filters.class_id, filters.student_id, filters.subject);
    } else if (selectedView === 'class-performance' && selectedClass) {
      loadClassPerformance(selectedClass.class_id);
    }
  }, [selectedView, filters, selectedClass]);

  const loadOverviewAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/overview`);
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Error loading overview analytics:', error);
      setAnalyticsData({
        overview_metrics: {
          total_classes: 0,
          total_students: 0,
          total_messages: 0,
          total_tests: 0,
          average_score: 0
        },
        class_summary: [],
        subject_distribution: [],
        weekly_activity_trend: []
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTestResults = async (classId = '', studentId = '', subject = '') => {
    setTestResultsLoading(true);
    try {
      const params = new URLSearchParams();
      if (classId) params.append('class_id', classId);
      if (studentId) params.append('student_id', studentId);
      if (subject) params.append('subject', subject);
      
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/test-results?${params}`);
      setTestResults(response.data.test_results || []);
    } catch (error) {
      console.error('Error loading test results:', error);
      setTestResults([]);
    } finally {
      setTestResultsLoading(false);
    }
  };

  const loadClassPerformance = async (classId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/teacher/analytics/class-performance/${classId}`);
      setClassPerformance(response.data);
    } catch (error) {
      console.error('Error loading class performance:', error);
      setClassPerformance(null);
    } finally {
      setLoading(false);
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      math: '🧮', physics: '⚡', chemistry: '🧪', biology: '🧬',
      english: '📖', history: '🏛️', geography: '🌍'
    };
    return icons[subject] || '📚';
  };

  // Enhanced Test Results View
  if (selectedView === 'test-results') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center mb-8">
            <button
              onClick={() => onNavigate('teacher-dashboard')}
              className="text-indigo-600 hover:text-indigo-700 mr-4"
            >
              ← Back to Dashboard
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📊 Detailed Test Results</h1>
              <p className="text-gray-600">Comprehensive analysis of student performance</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="bg-white rounded-lg shadow-sm p-1 mb-6 inline-flex">
            <button
              onClick={() => setSelectedView('overview')}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            >
              Overview
            </button>
            <button
              onClick={() => setSelectedView('test-results')}
              className="px-4 py-2 text-sm font-medium bg-indigo-100 text-indigo-700 rounded transition-colors"
            >
              Test Results
            </button>
            <button
              onClick={() => setSelectedView('class-performance')}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            >
              Class Performance
            </button>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
                <select
                  value={filters.class_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, class_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">All Classes</option>
                  {analyticsData?.class_summary?.map(cls => (
                    <option key={cls.class_info.class_id} value={cls.class_info.class_id}>
                      {cls.class_info.class_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <select
                  value={filters.subject}
                  onChange={(e) => setFilters(prev => ({ ...prev, subject: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">All Subjects</option>
                  <option value="math">🧮 Math</option>
                  <option value="physics">⚡ Physics</option>
                  <option value="chemistry">🧪 Chemistry</option>
                  <option value="biology">🧬 Biology</option>
                  <option value="english">📖 English</option>
                  <option value="history">🏛️ History</option>
                  <option value="geography">🌍 Geography</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => loadTestResults(filters.class_id, filters.student_id, filters.subject)}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>

          {/* Test Results */}
          {testResultsLoading ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading test results...</p>
            </div>
          ) : testResults.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Test Results Found</h3>
              <p className="text-gray-600">No practice tests have been taken with the current filters.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {testResults.map((result) => (
                <div key={result.attempt_id} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="text-3xl">{getSubjectIcon(result.subject)}</div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{result.student_name}</h3>
                        <p className="text-sm text-gray-600">
                          {result.subject.charAt(0).toUpperCase() + result.subject.slice(1)} • 
                          Grade {result.student_grade} • 
                          {new Date(result.completed_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${
                        result.score >= 80 ? 'text-green-600' : 
                        result.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {result.score.toFixed(1)}%
                      </div>
                      <p className="text-sm text-gray-600">
                        {result.correct_answers}/{result.total_questions} correct
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-lg font-semibold text-blue-600">{result.total_questions}</div>
                      <div className="text-xs text-gray-600">Questions</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-lg font-semibold text-green-600">{result.correct_answers}</div>
                      <div className="text-xs text-gray-600">Correct</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                      <div className="text-lg font-semibold text-red-600">{result.incorrect_answers}</div>
                      <div className="text-xs text-gray-600">Incorrect</div>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <div className="text-lg font-semibold text-purple-600">{Math.floor(result.time_taken / 60)}m</div>
                      <div className="text-xs text-gray-600">Time Taken</div>
                    </div>
                  </div>

                  {/* Topics Covered */}
                  {result.topics_covered && result.topics_covered.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Topics Covered:</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.topics_covered.map((topic, index) => (
                          <span key={index} className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm rounded-full">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Question Analysis Toggle */}
                  <details className="group">
                    <summary className="cursor-pointer text-indigo-600 hover:text-indigo-700 font-medium flex items-center">
                      <span className="group-open:rotate-90 transition-transform mr-2">▶</span>
                      View Question-by-Question Analysis
                    </summary>
                    <div className="mt-4 space-y-3">
                      {result.question_analysis.map((question, index) => (
                        <div key={question.question_id} className={`p-4 rounded-lg border-l-4 ${
                          question.is_correct ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                        }`}>
                          <div className="flex items-start justify-between mb-2">
                            <span className="text-sm font-medium text-gray-600">Question {index + 1}</span>
                            <span className={`text-sm px-2 py-1 rounded ${
                              question.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {question.is_correct ? '✓ Correct' : '✗ Incorrect'}
                            </span>
                          </div>
                          <p className="text-gray-900 mb-2">{question.question_text}</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-gray-700">Student Answer:</span>
                              <span className={`ml-2 ${question.is_correct ? 'text-green-700' : 'text-red-700'}`}>
                                {question.student_answer || 'No answer'}
                              </span>
                            </div>
                            {!question.is_correct && (
                              <div>
                                <span className="font-medium text-gray-700">Correct Answer:</span>
                                <span className="ml-2 text-green-700 font-medium">{question.correct_answer}</span>
                              </div>
                            )}
                          </div>
                          {question.explanation && (
                            <div className="mt-3 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                              <div className="font-medium text-blue-800 mb-1">Explanation:</div>
                              <div className="text-blue-700 text-sm">{question.explanation}</div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Overview and other views would go here...
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => onNavigate('teacher-dashboard')}
              className="text-indigo-600 hover:text-indigo-700 mr-4"
            >
              ← Back to Dashboard
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📊 Analytics Dashboard</h1>
              <p className="text-gray-600">Comprehensive student performance insights</p>
            </div>
          </div>
          <button
            onClick={() => setSelectedView('test-results')}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            View Detailed Results →
          </button>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center">
            <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🚀</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Enhanced Analytics Coming Soon!</h2>
            <p className="text-gray-600 mb-6">Click "View Detailed Results" to see comprehensive test analytics.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;