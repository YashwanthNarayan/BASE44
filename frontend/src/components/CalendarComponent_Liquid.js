import React, { useState, useEffect } from 'react';
import { calendarAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput, LiquidSelect } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const CalendarComponent = ({ student, onNavigate }) => {
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showQuickForm, setShowQuickForm] = useState(false);
  const [quickEvent, setQuickEvent] = useState({
    title: '',
    event_type: 'study',
    start_time: '09:00',
    end_time: '10:00'
  });

  const eventTypes = [
    { value: 'study', label: 'Study Session', icon: '📚', color: 'bg-blue-500/20 border-blue-500/40' },
    { value: 'assignment', label: 'Assignment', icon: '📝', color: 'bg-green-500/20 border-green-500/40' },
    { value: 'exam', label: 'Exam', icon: '📋', color: 'bg-red-500/20 border-red-500/40' },
    { value: 'personal', label: 'Personal', icon: '🗓️', color: 'bg-purple-500/20 border-purple-500/40' }
  ];

  const subjects = ['math', 'physics', 'chemistry', 'biology', 'english', 'history', 'geography'];

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await calendarAPI.getEvents();
      setEvents(response);
    } catch (error) {
      console.error('Error loading calendar events:', error);
    }
  };

  const handleDayClick = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    setSelectedDate(dateStr);
    setQuickEvent({
      title: '',
      event_type: 'study',
      start_time: '09:00',
      end_time: '10:00'
    });
    setShowQuickForm(true);
  };

  const createQuickEvent = async () => {
    if (!quickEvent.title.trim()) {
      alert('Please enter an event title');
      return;
    }

    try {
      const eventData = {
        title: quickEvent.title,
        event_type: quickEvent.event_type,
        start_time: `${selectedDate}T${quickEvent.start_time}:00`,
        end_time: `${selectedDate}T${quickEvent.end_time}:00`,
        description: '',
        subject: ''
      };

      await calendarAPI.createEvent(eventData);
      
      setQuickEvent({
        title: '',
        event_type: 'study',
        start_time: '09:00',
        end_time: '10:00'
      });
      setShowQuickForm(false);
      setSelectedDate(null);
      loadEvents();
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
            📅 Temporal Synchronization Matrix
          </h1>
          <p className="text-secondary">Manage your quantum learning schedule and neural events</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Calendar Matrix */}
          <div className="lg:col-span-2">
            <LiquidCard>
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-primary">
                    {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} Calendar
                  </h2>
                  <div className="text-sm text-secondary">
                    Click on any day to add an event
                  </div>
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1 mb-4">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="p-3 text-center font-semibold text-secondary">
                      {day}
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-7 gap-1">
                  {generateCalendarDays().map((date, index) => {
                    const dateStr = date ? date.toISOString().split('T')[0] : '';
                    const dayEvents = date ? getEventsForDate(dateStr) : [];
                    const isToday = date && date.toDateString() === new Date().toDateString();
                    const isSelected = selectedDate === dateStr;
                    
                    return (
                      <div
                        key={index}
                        onClick={() => date && handleDayClick(date)}
                        className={`
                          min-h-[100px] p-2 border rounded-lg transition-all duration-300 relative
                          ${date ? 'bg-glass border-primary/20 hover:border-neon-cyan/50 cursor-pointer hover:bg-glass/50' : 'bg-transparent border-transparent'}
                          ${isToday ? 'ring-2 ring-neon-cyan border-neon-cyan' : ''}
                          ${isSelected ? 'ring-2 ring-yellow-400 border-yellow-400 bg-yellow-500/10' : ''}
                        `}
                      >
                        {date && (
                          <>
                            <div className={`text-sm font-medium mb-2 ${isToday ? 'text-neon-cyan glow-cyan' : 'text-primary'}`}>
                              {date.getDate()}
                            </div>
                            <div className="space-y-1">
                              {dayEvents.slice(0, 2).map((event, idx) => {
                                const eventType = eventTypes.find(t => t.value === event.event_type);
                                return (
                                  <div
                                    key={idx}
                                    className={`text-xs p-1 rounded border truncate ${eventType?.color || 'bg-gray-500/20 border-gray-500/40'}`}
                                    title={event.title}
                                  >
                                    {eventType?.icon} {event.title}
                                  </div>
                                );
                              })}
                              {dayEvents.length > 2 && (
                                <div className="text-xs text-secondary">
                                  +{dayEvents.length - 2} more
                                </div>
                              )}
                            </div>
                            {date && (
                              <div className="absolute bottom-1 right-1 text-xs text-secondary opacity-50">
                                +
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </LiquidCard>
          </div>

          {/* Upcoming Events Neural Stream */}
          <div>
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                    <span className="text-sm font-bold">⚡</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Neural Events Stream</h2>
                </div>
                
                <div className="space-y-4">
                  {events
                    .filter(event => new Date(event.start_time) >= new Date())
                    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
                    .slice(0, 5)
                    .map((event, index) => {
                      const eventType = eventTypes.find(t => t.value === event.event_type);
                      return (
                        <div key={index} className="p-4 bg-glass border border-primary/20 rounded-lg hover:border-neon-cyan/50 transition-colors">
                          <div className="flex items-center mb-2">
                            <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${eventType?.gradient} flex items-center justify-center mr-3`}>
                              <span className="text-lg">{eventType?.icon}</span>
                            </div>
                            <span className="font-medium text-primary">{event.title}</span>
                          </div>
                          <div className="text-sm text-secondary">
                            {new Date(event.start_time).toLocaleDateString()} at{' '}
                            {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                          {event.description && (
                            <div className="text-sm text-secondary mt-2">{event.description}</div>
                          )}
                        </div>
                      );
                    })}
                  {events.filter(event => new Date(event.start_time) >= new Date()).length === 0 && (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">⏰</div>
                      <p className="text-secondary">No upcoming neural events detected</p>
                    </div>
                  )}
                </div>
              </div>
            </LiquidCard>
          </div>
        </div>

        {/* Create Event Holographic Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <LiquidCard holographic className="w-full max-w-md">
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                    <span className="text-sm font-bold">⚡</span>
                  </div>
                  <h3 className="text-xl font-semibold text-primary">Neural Event Synchronization</h3>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Event Title *</label>
                    <LiquidInput
                      type="text"
                      value={newEvent.title}
                      onChange={(e) => setNewEvent({...newEvent, title: e.target.value})}
                      placeholder="Enter neural event title"
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Event Type</label>
                    <LiquidSelect
                      value={newEvent.event_type}
                      onChange={(e) => setNewEvent({...newEvent, event_type: e.target.value})}
                      className="w-full"
                    >
                      {eventTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </LiquidSelect>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Subject Domain</label>
                    <LiquidSelect
                      value={newEvent.subject}
                      onChange={(e) => setNewEvent({...newEvent, subject: e.target.value})}
                      className="w-full"
                    >
                      <option value="">Select domain (optional)</option>
                      {subjects.map(subject => (
                        <option key={subject} value={subject}>
                          {subject.charAt(0).toUpperCase() + subject.slice(1)}
                        </option>
                      ))}
                    </LiquidSelect>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Start Time *</label>
                    <LiquidInput
                      type="datetime-local"
                      value={newEvent.start_time}
                      onChange={(e) => setNewEvent({...newEvent, start_time: e.target.value})}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">End Time *</label>
                    <LiquidInput
                      type="datetime-local"
                      value={newEvent.end_time}
                      onChange={(e) => setNewEvent({...newEvent, end_time: e.target.value})}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Description</label>
                    <textarea
                      value={newEvent.description}
                      onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                      className="w-full p-3 bg-glass border border-primary/20 rounded-lg focus:ring-2 focus:ring-neon-cyan focus:border-transparent text-primary placeholder-secondary"
                      rows="3"
                      placeholder="Neural event description (optional)"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                  <LiquidButton
                    variant="secondary"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Cancel Sync
                  </LiquidButton>
                  <LiquidButton onClick={createEvent}>
                    ⚡ Synchronize Event
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

export default CalendarComponent;