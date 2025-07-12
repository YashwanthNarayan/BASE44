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

  useEffect(() => {
    loadEvents();
  }, []);

  const formatSelectedDate = (dateStr) => {
    if (!dateStr) return '';
    // Parse the YYYY-MM-DD string manually to avoid timezone issues
    const [year, month, day] = dateStr.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    return date.toLocaleDateString();
  };

  const loadEvents = async () => {
    try {
      const response = await calendarAPI.getEvents();
      setEvents(response);
    } catch (error) {
      console.error('Error loading calendar events:', error);
    }
  };

  const handleDayClick = (date) => {
    // Use local date instead of ISO string to avoid timezone issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
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
      // Use local date comparison to avoid timezone issues
      const eventDate = new Date(event.start_time);
      const eventYear = eventDate.getFullYear();
      const eventMonth = String(eventDate.getMonth() + 1).padStart(2, '0');
      const eventDay = String(eventDate.getDate()).padStart(2, '0');
      const eventDateStr = `${eventYear}-${eventMonth}-${eventDay}`;
      
      return eventDateStr === date;
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
        {/* Header */}
        <div className="text-center mb-8">
          <LiquidButton
            variant="secondary"
            onClick={() => onNavigate('student-dashboard')}
            className="mb-4"
          >
            ← Back to Dashboard
          </LiquidButton>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
            📅 Calendar & Events
          </h1>
          <p className="text-secondary">Manage your schedule and upcoming events</p>
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
                    let dateStr = '';
                    if (date) {
                      const year = date.getFullYear();
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const day = String(date.getDate()).padStart(2, '0');
                      dateStr = `${year}-${month}-${day}`;
                    }
                    
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

          {/* Upcoming Events & Quick Add */}
          <div className="space-y-6">
            {/* Quick Event Form */}
            {showQuickForm && selectedDate && (
              <LiquidCard>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-primary">
                      Add Event - {new Date(selectedDate).toLocaleDateString()}
                    </h3>
                    <button
                      onClick={() => {
                        setShowQuickForm(false);
                        setSelectedDate(null);
                      }}
                      className="text-secondary hover:text-primary transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary mb-2">Event Title</label>
                      <LiquidInput
                        type="text"
                        value={quickEvent.title}
                        onChange={(e) => setQuickEvent({...quickEvent, title: e.target.value})}
                        placeholder="What's happening?"
                        className="w-full"
                        onKeyPress={(e) => e.key === 'Enter' && createQuickEvent()}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-secondary mb-2">Event Type</label>
                      <div className="grid grid-cols-2 gap-2">
                        {eventTypes.map(type => (
                          <button
                            key={type.value}
                            onClick={() => setQuickEvent({...quickEvent, event_type: type.value})}
                            className={`
                              p-3 rounded-lg border transition-all duration-200 text-sm font-medium
                              ${quickEvent.event_type === type.value 
                                ? type.color + ' border-opacity-100 scale-105' 
                                : 'bg-glass border-primary/20 hover:border-primary/40'
                              }
                            `}
                          >
                            {type.icon} {type.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary mb-2">Start Time</label>
                        <LiquidInput
                          type="time"
                          value={quickEvent.start_time}
                          onChange={(e) => setQuickEvent({...quickEvent, start_time: e.target.value})}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary mb-2">End Time</label>
                        <LiquidInput
                          type="time"
                          value={quickEvent.end_time}
                          onChange={(e) => setQuickEvent({...quickEvent, end_time: e.target.value})}
                          className="w-full"
                        />
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <LiquidButton
                        variant="secondary"
                        onClick={() => {
                          setShowQuickForm(false);
                          setSelectedDate(null);
                        }}
                        className="flex-1"
                      >
                        Cancel
                      </LiquidButton>
                      <LiquidButton onClick={createQuickEvent} className="flex-1">
                        Add Event
                      </LiquidButton>
                    </div>
                  </div>
                </div>
              </LiquidCard>
            )}

            {/* Upcoming Events */}
            <LiquidCard>
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gradient-secondary flex items-center justify-center">
                    <span className="text-sm font-bold">⚡</span>
                  </div>
                  <h2 className="text-xl font-bold text-primary">Upcoming Events</h2>
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
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${eventType?.color || 'bg-gray-500/20'}`}>
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
                      <p className="text-secondary">No upcoming events</p>
                      <p className="text-sm text-secondary mt-2">Click on a calendar day to add your first event!</p>
                    </div>
                  )}
                </div>
              </div>
            </LiquidCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarComponent;