import React, { useState, useEffect } from 'react';
import { notesAPI, setupAxiosAuth } from '../services/api';
import NavigationBar_Modern from './NavigationBar_Modern';
import { 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernInput,
  ModernTextarea,
  ModernSelect,
  ModernAlert,
  ModernContainer,
  ModernHeading,
  ModernText,
  ModernGrid,
  ModernSpinner,
  ModernBadge,
  ModernModal,
  ModernModalHeader,
  ModernModalBody,
  ModernModalFooter
} from './ui/ModernComponents';
import '../styles/modern-ui.css';

const NotesComponent_Modern = ({ student, onNavigate }) => {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('all');

  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    subject: 'mathematics',
    tags: []
  });

  const subjects = [
    { value: 'all', label: 'All Subjects' },
    { value: 'mathematics', label: 'Mathematics' },
    { value: 'physics', label: 'Physics' },
    { value: 'chemistry', label: 'Chemistry' },
    { value: 'biology', label: 'Biology' },
    { value: 'english', label: 'English' }
  ];

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      setupAxiosAuth(token);
      const response = await notesAPI.getAll();
      setNotes(response.notes || []);
    } catch (error) {
      console.error('Error loading notes:', error);
      setError('Failed to load notes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const openModal = (note = null) => {
    if (note) {
      setSelectedNote(note);
      setNoteForm({
        title: note.title || '',
        content: note.content || '',
        subject: note.subject || 'mathematics',
        tags: note.tags || []
      });
      setIsEditing(true);
    } else {
      setSelectedNote(null);
      setNoteForm({
        title: '',
        content: '',
        subject: 'mathematics',
        tags: []
      });
      setIsEditing(false);
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedNote(null);
    setIsEditing(false);
    setError('');
  };

  const handleSave = async () => {
    if (!noteForm.title.trim() || !noteForm.content.trim()) {
      setError('Title and content are required.');
      return;
    }

    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');
      setupAxiosAuth(token);

      const noteData = {
        title: noteForm.title.trim(),
        content: noteForm.content.trim(),
        subject: noteForm.subject,
        tags: noteForm.tags
      };

      if (isEditing && selectedNote) {
        // Update not supported yet, log for debugging
        console.log('Update functionality not yet implemented');
        setError('Note editing not yet supported');
        return;
      } else {
        // Use generate method with subject and title as topic
        await notesAPI.generate(noteData.subject, noteData.title, 10); // Default grade level
      }

      closeModal();
      await loadNotes();
    } catch (error) {
      console.error('Error saving note:', error);
      setError('Failed to save note. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return;

    try {
      const token = localStorage.getItem('access_token');
      setupAxiosAuth(token);
      await notesAPI.deleteNote(noteId);
      await loadNotes();
    } catch (error) {
      console.error('Error deleting note:', error);
      setError('Failed to delete note. Please try again.');
    }
  };

  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         note.content?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSubject = selectedSubject === 'all' || note.subject === selectedSubject;
    return matchesSearch && matchesSubject;
  });

  const getSubjectColor = (subject) => {
    const colors = {
      mathematics: 'blue',
      physics: 'purple',
      chemistry: 'red',
      biology: 'green',
      english: 'indigo'
    };
    return colors[subject] || 'gray';
  };

  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-100 text-blue-800',
      purple: 'bg-purple-100 text-purple-800',
      red: 'bg-red-100 text-red-800',
      green: 'bg-green-100 text-green-800',
      indigo: 'bg-indigo-100 text-indigo-800',
      gray: 'bg-gray-100 text-gray-800'
    };
    return colorMap[color] || colorMap.gray;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ModernSpinner size="lg" />
          <ModernText className="mt-4 text-gray-600 font-medium">Loading your notes...</ModernText>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar_Modern 
        user={student}
        currentPage="notes"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
              Study Notes
            </ModernHeading>
            <ModernText variant="body-large" className="text-gray-600 font-medium">
              Organize your learning with smart digital notes
            </ModernText>
          </div>
          <ModernButton 
            variant="primary" 
            onClick={() => openModal()}
            className="font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
          >
            Create Note
          </ModernButton>
        </div>

        {error && (
          <ModernAlert variant="error" className="mb-6">
            {error}
          </ModernAlert>
        )}

        {/* Filters */}
        <ModernCard className="mb-8">
          <ModernCardBody>
            <ModernGrid cols={2}>
              <ModernInput
                placeholder="Search notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="font-medium"
              />
              <ModernSelect
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="font-medium"
              >
                {subjects.map(subject => (
                  <option key={subject.value} value={subject.value}>
                    {subject.label}
                  </option>
                ))}
              </ModernSelect>
            </ModernGrid>
          </ModernCardBody>
        </ModernCard>

        {/* Notes Grid */}
        {filteredNotes.length > 0 ? (
          <ModernGrid cols={3}>
            {filteredNotes.map((note) => {
              const color = getSubjectColor(note.subject);
              return (
                <ModernCard key={note.id} hover={true} className="cursor-pointer">
                  <ModernCardBody>
                    <div className="flex items-start justify-between mb-3">
                      <ModernBadge className={getColorClasses(color)}>
                        {note.subject}
                      </ModernBadge>
                      <div className="flex gap-2">
                        <button
                          onClick={() => openModal(note)}
                          className="text-gray-400 hover:text-indigo-600 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(note.id)}
                          className="text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM4 5a2 2 0 012-2h8a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 102 0v3a1 1 0 11-2 0V9zm4 0a1 1 0 10-2 0v3a1 1 0 102 0V9z" clipRule="evenodd"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <ModernHeading level={4} className="text-gray-800 font-semibold mb-2 line-clamp-2">
                      {note.title}
                    </ModernHeading>
                    
                    <ModernText variant="body-small" className="text-gray-600 font-medium mb-4 line-clamp-3">
                      {note.content}
                    </ModernText>
                    
                    <ModernText variant="caption" className="text-gray-500 font-medium">
                      {new Date(note.created_at).toLocaleDateString()}
                    </ModernText>
                    
                    {note.tags && note.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-3">
                        {note.tags.slice(0, 3).map((tag, index) => (
                          <span 
                            key={index}
                            className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </ModernCardBody>
                </ModernCard>
              );
            })}
          </ModernGrid>
        ) : (
          <ModernCard>
            <ModernCardBody>
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd"/>
                  </svg>
                </div>
                <ModernHeading level={4} className="text-gray-600 font-semibold mb-2">
                  No Notes Found
                </ModernHeading>
                <ModernText variant="body-small" className="text-gray-500 font-medium mb-6">
                  {searchTerm || selectedSubject !== 'all' 
                    ? 'No notes match your current filters'
                    : 'Create your first note to get started'
                  }
                </ModernText>
                {!searchTerm && selectedSubject === 'all' && (
                  <ModernButton 
                    variant="primary" 
                    onClick={() => openModal()}
                    className="font-medium"
                  >
                    Create Your First Note
                  </ModernButton>
                )}
              </div>
            </ModernCardBody>
          </ModernCard>
        )}

        {/* Note Modal */}
        <ModernModal isOpen={isModalOpen} onClose={closeModal}>
          <ModernModalHeader>
            {isEditing ? 'Edit Note' : 'Create New Note'}
          </ModernModalHeader>
          <ModernModalBody>
            <div className="space-y-4">
              <ModernInput
                label="Title"
                value={noteForm.title}
                onChange={(e) => setNoteForm(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter note title..."
                className="font-medium"
              />
              
              <ModernSelect
                label="Subject"
                value={noteForm.subject}
                onChange={(e) => setNoteForm(prev => ({ ...prev, subject: e.target.value }))}
                className="font-medium"
              >
                {subjects.slice(1).map(subject => (
                  <option key={subject.value} value={subject.value}>
                    {subject.label}
                  </option>
                ))}
              </ModernSelect>
              
              <ModernTextarea
                label="Content"
                value={noteForm.content}
                onChange={(e) => setNoteForm(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Write your note content here..."
                rows={8}
                className="font-medium"
              />
            </div>
            
            {error && (
              <ModernAlert variant="error" className="mt-4">
                {error}
              </ModernAlert>
            )}
          </ModernModalBody>
          <ModernModalFooter>
            <ModernButton variant="secondary" onClick={closeModal}>
              Cancel
            </ModernButton>
            <ModernButton 
              variant="primary" 
              onClick={handleSave}
              disabled={saving}
              className="font-medium"
            >
              {saving ? (
                <div className="flex items-center gap-2">
                  <ModernSpinner size="sm" />
                  Saving...
                </div>
              ) : (
                isEditing ? 'Update Note' : 'Create Note'
              )}
            </ModernButton>
          </ModernModalFooter>
        </ModernModal>
      </ModernContainer>
    </div>
  );
};

export default NotesComponent_Modern;