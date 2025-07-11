import React, { useState, useEffect } from 'react';
import { notesAPI } from '../services/api';
import { subjects } from '../utils/constants';
import { truncateText, formatTimeAgo } from '../utils/helpers';

const NotesComponent = ({ student, onNavigate }) => {
  const [currentView, setCurrentView] = useState('library');
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generateForm, setGenerateForm] = useState({
    subject: '',
    topic: '',
    grade_level: student?.grade_level || '10th'
  });

  useEffect(() => {
    if (currentView === 'library') {
      loadNotes();
    }
  }, [currentView]);

  const loadNotes = async () => {
    setLoading(true);
    try {
      const notesData = await notesAPI.getAll();
      setNotes(notesData);
    } catch (error) {
      console.error('Error loading notes:', error);
      setNotes([]);
    } finally {
      setLoading(false);
    }
  };

  const generateNotes = async () => {
    if (!generateForm.subject || !generateForm.topic) {
      alert('Please fill in all fields');
      return;
    }

    setGenerating(true);
    try {
      await notesAPI.generate(generateForm.subject, generateForm.topic, generateForm.grade_level);
      alert('Notes generated successfully!');
      setGenerateForm({ subject: '', topic: '', grade_level: student?.grade_level || '10th' });
      setCurrentView('library');
    } catch (error) {
      console.error('Error generating notes:', error);
      alert('Failed to generate notes. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const deleteNote = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return;

    try {
      await notesAPI.delete(noteId);
      setNotes(notes.filter(note => note.id !== noteId));
      if (selectedNote && selectedNote.id === noteId) {
        setSelectedNote(null);
        setCurrentView('library');
      }
    } catch (error) {
      console.error('Error deleting note:', error);
      alert('Failed to delete note. Please try again.');
    }
  };

  const toggleFavorite = async (noteId) => {
    try {
      await notesAPI.toggleFavorite(noteId);
      setNotes(notes.map(note => 
        note.id === noteId 
          ? { ...note, is_favorite: !note.is_favorite }
          : note
      ));
      if (selectedNote && selectedNote.id === noteId) {
        setSelectedNote({ ...selectedNote, is_favorite: !selectedNote.is_favorite });
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  // Generate View
  if (currentView === 'generate') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <button
              onClick={() => setCurrentView('library')}
              className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
            >
              ← Back to Library
            </button>
            <h1 className="text-3xl font-bold text-gray-900">📝 Generate Study Notes</h1>
            <p className="text-gray-600">Create personalized study notes with AI</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <select
                  value={generateForm.subject}
                  onChange={(e) => setGenerateForm({...generateForm, subject: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">Choose a subject...</option>
                  {Object.entries(subjects).map(([key, subject]) => (
                    <option key={key} value={key}>{subject.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
                <input
                  type="text"
                  value={generateForm.topic}
                  onChange={(e) => setGenerateForm({...generateForm, topic: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Enter the topic you want to study..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Grade Level</label>
                <select
                  value={generateForm.grade_level}
                  onChange={(e) => setGenerateForm({...generateForm, grade_level: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="6th">6th Grade</option>
                  <option value="7th">7th Grade</option>
                  <option value="8th">8th Grade</option>
                  <option value="9th">9th Grade</option>
                  <option value="10th">10th Grade</option>
                  <option value="11th">11th Grade</option>
                  <option value="12th">12th Grade</option>
                </select>
              </div>

              <button
                onClick={generateNotes}
                disabled={!generateForm.subject || !generateForm.topic || generating}
                className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? 'Generating Notes...' : 'Generate Study Notes'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // View Note
  if (currentView === 'view' && selectedNote) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => {
                setCurrentView('library');
                setSelectedNote(null);
              }}
              className="text-indigo-600 hover:text-indigo-800 flex items-center mb-4"
            >
              ← Back to Library
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{selectedNote.topic}</h1>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span className="capitalize">{selectedNote.subject}</span>
                  <span>•</span>
                  <span>{selectedNote.grade_level} Grade</span>
                  <span>•</span>
                  <span>{formatTimeAgo(selectedNote.created_at)}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleFavorite(selectedNote.id)}
                  className={`p-2 rounded-lg transition-colors ${
                    selectedNote.is_favorite 
                      ? 'text-yellow-600 bg-yellow-100 hover:bg-yellow-200' 
                      : 'text-gray-600 bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {selectedNote.is_favorite ? '★' : '☆'}
                </button>
                <button
                  onClick={() => deleteNote(selectedNote.id)}
                  className="p-2 text-red-600 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                {selectedNote.content}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Library View (default)
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
          <h1 className="text-3xl font-bold text-gray-900">📚 My Study Notes</h1>
          <p className="text-gray-600">Your personalized AI-generated study notes</p>
        </div>

        <div className="flex justify-center mb-8">
          <button
            onClick={() => setCurrentView('generate')}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            ✨ Generate New Notes
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your notes...</p>
          </div>
        ) : notes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {notes.map((note) => (
              <div key={note.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{note.topic}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-600 mb-3">
                      <span className="capitalize">{note.subject}</span>
                      <span>•</span>
                      <span>{note.grade_level}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => toggleFavorite(note.id)}
                    className={`text-lg ${note.is_favorite ? 'text-yellow-500' : 'text-gray-400'}`}
                  >
                    {note.is_favorite ? '★' : '☆'}
                  </button>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {truncateText(note.content, 120)}
                </p>

                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(note.created_at)}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedNote(note);
                        setCurrentView('view');
                      }}
                      className="px-3 py-1 text-sm bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors"
                    >
                      Read
                    </button>
                    <button
                      onClick={() => deleteNote(note.id)}
                      className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-6">📚</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">No Notes Yet</h2>
            <p className="text-gray-600 mb-8">Generate your first set of AI-powered study notes to get started!</p>
            <button
              onClick={() => setCurrentView('generate')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              ✨ Generate Your First Notes
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotesComponent;