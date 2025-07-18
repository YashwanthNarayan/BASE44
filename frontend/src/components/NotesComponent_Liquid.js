import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { notesAPI } from '../services/api';
import { subjects } from '../utils/constants';
import { truncateText, formatTimeAgo } from '../utils/helpers';
import { LiquidCard, LiquidButton, LiquidInput, LiquidSelect } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

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
      alert('Please fill in all required fields');
      return;
    }

    setGenerating(true);
    try {
      await notesAPI.generate(generateForm.subject, generateForm.topic, generateForm.grade_level);
      alert('Study notes generated successfully!');
      setGenerateForm({ subject: '', topic: '', grade_level: student?.grade_level || '10th' });
      setCurrentView('library');
    } catch (error) {
      console.error('Error generating notes:', error);
      alert('Failed to generate notes. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const favoriteNote = async (noteId) => {
    try {
      await notesAPI.favorite(noteId);
      loadNotes();
    } catch (error) {
      console.error('Error favoriting note:', error);
    }
  };

  const deleteNote = async (noteId) => {
    if (window.confirm('Delete this study note?')) {
      try {
        await notesAPI.delete(noteId);
        loadNotes();
        if (selectedNote && selectedNote.id === noteId) {
          setSelectedNote(null);
          setCurrentView('library');
        }
      } catch (error) {
        console.error('Error deleting note:', error);
      }
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      math: '🔢', physics: '⚛️', chemistry: '🧪', biology: '🧬',
      english: '📚', history: '🏛️', geography: '🌍'
    };
    return icons[subject] || '📖';
  };

  const getSubjectGradient = (subject) => {
    const gradients = {
      math: 'from-blue-500/20 to-cyan-500/20',
      physics: 'from-purple-500/20 to-indigo-500/20',
      chemistry: 'from-green-500/20 to-emerald-500/20',
      biology: 'from-emerald-500/20 to-teal-500/20',
      english: 'from-red-500/20 to-pink-500/20',
      history: 'from-yellow-500/20 to-orange-500/20',
      geography: 'from-teal-500/20 to-cyan-500/20'
    };
    return gradients[subject] || 'from-gray-500/20 to-gray-600/20';
  };

  if (currentView === 'generate') {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-4xl mx-auto">
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
              🧠 Neural Note Synthesizer
            </h1>
            <p className="text-secondary">Generate advanced study materials using quantum AI</p>
          </div>

          <LiquidCard holographic className="max-w-2xl mx-auto">
            <div className="p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                  <span className="text-sm font-bold">⚡</span>
                </div>
                <h2 className="text-xl font-bold text-primary">Neural Parameters</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">
                    Subject Domain
                  </label>
                  <LiquidSelect
                    value={generateForm.subject}
                    onChange={(e) => setGenerateForm({...generateForm, subject: e.target.value})}
                    placeholder="Select subject domain..."
                  >
                    <option value="">Choose quantum domain...</option>
                    {Object.entries(subjects).map(([key, subject]) => (
                      <option key={key} value={key}>
                        {getSubjectIcon(key)} {subject.name}
                      </option>
                    ))}
                  </LiquidSelect>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">
                    Neural Topic Focus
                  </label>
                  <LiquidInput
                    type="text"
                    value={generateForm.topic}
                    onChange={(e) => setGenerateForm({...generateForm, topic: e.target.value})}
                    placeholder="e.g., Quantum mechanics, DNA structure, Shakespeare..."
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">
                    Academic Level
                  </label>
                  <LiquidSelect
                    value={generateForm.grade_level}
                    onChange={(e) => setGenerateForm({...generateForm, grade_level: e.target.value})}
                  >
                    {['6th', '7th', '8th', '9th', '10th', '11th', '12th'].map(grade => (
                      <option key={grade} value={grade}>{grade} Grade</option>
                    ))}
                  </LiquidSelect>
                </div>
              </div>

              <div className="flex justify-center space-x-4 mt-8">
                <LiquidButton
                  variant="secondary"
                  onClick={() => setCurrentView('library')}
                  disabled={generating}
                >
                  Cancel Synthesis
                </LiquidButton>
                <LiquidButton
                  onClick={generateNotes}
                  disabled={!generateForm.subject || !generateForm.topic || generating}
                  className="relative"
                >
                  {generating ? (
                    <>
                      <div className="quantum-loader w-4 h-4 mr-2" />
                      Synthesizing...
                    </>
                  ) : (
                    '⚡ Synthesize Neural Notes'
                  )}
                </LiquidButton>
              </div>
            </div>
          </LiquidCard>
        </div>
      </div>
    );
  }

  if (currentView === 'view' && selectedNote) {
    return (
      <div className="min-h-screen bg-dark-space text-primary">
        <div className="quantum-grid fixed inset-0 opacity-30" />
        
        <div className="relative z-10 p-6 max-w-4xl mx-auto">
          {/* Neural Header */}
          <div className="flex items-center justify-between mb-8">
            <LiquidButton
              variant="secondary"
              onClick={() => setCurrentView('library')}
            >
              ← Neural Library
            </LiquidButton>
            
            <div className="flex items-center space-x-3">
              <LiquidButton
                variant="secondary"
                onClick={() => favoriteNote(selectedNote.id)}
                className="hover:text-neon-yellow"
              >
                {selectedNote.is_favorite ? '⭐' : '☆'} 
                {selectedNote.is_favorite ? 'Favorited' : 'Add to Favorites'}
              </LiquidButton>
              <LiquidButton
                variant="danger"
                onClick={() => deleteNote(selectedNote.id)}
              >
                🗑️ Delete
              </LiquidButton>
            </div>
          </div>

          <LiquidCard>
            <div className="p-8">
              {/* Note Header */}
              <div className="flex items-center space-x-4 mb-6">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getSubjectGradient(selectedNote.subject)} flex items-center justify-center text-2xl`}>
                  {getSubjectIcon(selectedNote.subject)}
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-primary">
                    {selectedNote.topic}
                  </h1>
                  <p className="text-secondary">
                    {selectedNote.subject.charAt(0).toUpperCase() + selectedNote.subject.slice(1)} • 
                    {selectedNote.grade_level} Grade • 
                    Generated {formatTimeAgo(selectedNote.created_at)}
                  </p>
                </div>
                {selectedNote.is_favorite && (
                  <div className="text-neon-yellow text-2xl">⭐</div>
                )}
              </div>

              {/* Note Content */}
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown 
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  className="text-primary leading-relaxed"
                  components={{
                    // Custom components for better styling
                    h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-primary mb-4 border-b border-primary/20 pb-2" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-2xl font-semibold text-primary mb-3 mt-6" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-xl font-semibold text-primary mb-2 mt-4" {...props} />,
                    p: ({node, ...props}) => <p className="text-primary mb-4 leading-relaxed" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 text-primary space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 text-primary space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="text-primary" {...props} />,
                    strong: ({node, ...props}) => <strong className="text-accent-blue font-bold" {...props} />,
                    em: ({node, ...props}) => <em className="text-accent-cyan italic" {...props} />,
                    code: ({node, inline, ...props}) => 
                      inline ? (
                        <code className="bg-glass px-2 py-1 rounded text-accent-green font-mono text-sm" {...props} />
                      ) : (
                        <code className="block bg-glass p-4 rounded-lg text-accent-green font-mono text-sm overflow-x-auto" {...props} />
                      ),
                    blockquote: ({node, ...props}) => (
                      <blockquote className="border-l-4 border-accent-blue pl-4 italic text-secondary my-4" {...props} />
                    ),
                    table: ({node, ...props}) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full border border-primary/20 rounded-lg" {...props} />
                      </div>
                    ),
                    th: ({node, ...props}) => (
                      <th className="bg-glass border border-primary/20 px-4 py-2 text-primary font-semibold" {...props} />
                    ),
                    td: ({node, ...props}) => (
                      <td className="border border-primary/20 px-4 py-2 text-primary" {...props} />
                    ),
                    hr: ({node, ...props}) => (
                      <hr className="border-primary/20 my-6" {...props} />
                    )
                  }}
                >
                  {selectedNote.content}
                </ReactMarkdown>
              </div>
            </div>
          </LiquidCard>
        </div>
      </div>
    );
  }

  // Library View
  return (
    <div className="min-h-screen bg-dark-space text-primary">
      <div className="quantum-grid fixed inset-0 opacity-30" />
      
      <div className="relative z-10 p-6 max-w-6xl mx-auto">
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
            📚 Neural Knowledge Library
          </h1>
          <p className="text-secondary">Your quantum-enhanced study materials collection</p>
        </div>

        {/* Action Bar */}
        <LiquidCard className="mb-8">
          <div className="p-6 flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                <span className="text-sm font-bold">📖</span>
              </div>
              <h2 className="text-xl font-bold text-primary">Knowledge Matrix</h2>
              <span className="text-secondary">({notes.length} neural notes)</span>
            </div>
            
            <LiquidButton onClick={() => setCurrentView('generate')}>
              ⚡ Synthesize New Notes
            </LiquidButton>
          </div>
        </LiquidCard>

        {/* Notes Grid */}
        {loading ? (
          <LiquidCard className="text-center p-12">
            <div className="quantum-loader mx-auto mb-4" />
            <p className="text-secondary">Loading neural library...</p>
          </LiquidCard>
        ) : notes.length === 0 ? (
          <LiquidCard className="text-center p-12">
            <div className="text-6xl mb-6">🧠</div>
            <h2 className="text-2xl font-bold text-primary mb-4">Neural Library Empty</h2>
            <p className="text-secondary mb-6">
              Your quantum knowledge vault awaits. Generate your first neural notes to begin.
            </p>
            <LiquidButton onClick={() => setCurrentView('generate')}>
              ⚡ Synthesize First Notes
            </LiquidButton>
          </LiquidCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {notes.map((note) => (
              <LiquidCard
                key={note.id}
                className="cursor-pointer hover:scale-105 transform transition-all duration-300"
                onClick={() => {
                  setSelectedNote(note);
                  setCurrentView('view');
                }}
              >
                <div className="p-6">
                  {/* Note Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getSubjectGradient(note.subject)} flex items-center justify-center text-xl`}>
                      {getSubjectIcon(note.subject)}
                    </div>
                    {note.is_favorite && (
                      <div className="text-neon-yellow text-xl">⭐</div>
                    )}
                  </div>

                  {/* Note Content */}
                  <h3 className="text-lg font-semibold text-primary mb-2 line-clamp-2">
                    {note.topic}
                  </h3>
                  <p className="text-secondary text-sm mb-3 capitalize">
                    {note.subject} • {note.grade_level} Grade
                  </p>
                  <p className="text-primary text-sm line-clamp-3 mb-4">
                    {truncateText(
                      note.content
                        .replace(/\$\$[^$]*\$\$/g, '[Math Formula]') // Replace LaTeX blocks
                        .replace(/\$[^$]*\$/g, '[Math]') // Replace inline LaTeX
                        .replace(/#{1,6}\s/g, '') // Remove markdown headers
                        .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
                        .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
                        .replace(/`(.*?)`/g, '$1') // Remove code markdown
                        .replace(/\n+/g, ' ') // Replace line breaks with spaces
                        .trim(), 
                      100
                    )}
                  </p>

                  {/* Note Footer */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-secondary">
                      {formatTimeAgo(note.created_at)}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          favoriteNote(note.id);
                        }}
                        className="text-secondary hover:text-neon-yellow transition-colors"
                      >
                        {note.is_favorite ? '⭐' : '☆'}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNote(note.id);
                        }}
                        className="text-secondary hover:text-neon-pink transition-colors"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  {/* Data flow animation */}
                  <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
              </LiquidCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotesComponent;