import React, { useState, useEffect } from 'react';
import { calendarAPI } from '../services/api';
import { LiquidCard, LiquidButton, LiquidInput, LiquidSelect } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

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

  const eventTypes = [
    { value: 'study', label: 'Neural Study Session', icon: '📚', gradient: 'from-blue-500/20 to-cyan-500/20' },
    { value: 'assignment', label: 'Data Assignment', icon: '📝', gradient: 'from-green-500/20 to-emerald-500/20' },
    { value: 'exam', label: 'Neural Assessment', icon: '📋', gradient: 'from-red-500/20 to-pink-500/20' },
    { value: 'personal', label: 'Personal Matrix', icon: '🗓️', gradient: 'from-purple-500/20 to-indigo-500/20' }
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

  const createEvent = async () => {
    if (!newEvent.title || !newEvent.start_time || !newEvent.end_time) {
      alert('Please fill in all quantum parameters.');
      return;
    }

    try {
      await calendarAPI.createEvent(newEvent);
      
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
      alert('Neural event synchronized successfully!');
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Failed to synchronize neural event. Please try again.');
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
                    {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} Matrix
                  </h2>
                  <LiquidButton onClick={() => setShowCreateForm(true)}>
                    ⚡ Sync New Event
                  </LiquidButton>
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
                    
                    return (
                      <div
                        key={index}
                        className={`
                          min-h-[100px] p-2 border rounded-lg transition-all duration-300
                          ${date ? 'bg-glass border-primary/20 hover:border-neon-cyan/50 cursor-pointer' : 'bg-transparent border-transparent'}
                          ${isToday ? 'ring-2 ring-neon-cyan border-neon-cyan' : ''}
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
                                    className="text-xs p-1 bg-gradient-to-r from-neon-cyan/20 to-neon-magenta/20 text-primary rounded border border-neon-cyan/30 truncate"
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