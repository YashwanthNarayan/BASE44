import React, { useState, useEffect } from 'react';
import { calendarAPI, practiceSchedulerAPI } from '../services/api';
import { 
  ModernContainer, 
  ModernCard, 
  ModernCardHeader, 
  ModernCardBody, 
  ModernButton, 
  ModernInput, 
  ModernSelect,
  ModernHeading, 
  ModernText, 
  ModernBadge, 
  ModernSpinner,
  ModernGrid 
} from './ui/ModernComponents';
import NavigationBar_Modern from './NavigationBar_Modern';

const CalendarComponent_Modern = ({ student, onNavigate }) => {
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [showEventForm, setShowEventForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [eventForm, setEventForm] = useState({
    title: '',
    event_type: 'study',
    start_time: '09:00',
    end_time: '10:00',
    description: '',
    subject: ''
  });

  const eventTypes = [
    { value: 'study', label: 'Study Session', icon: 'St', color: 'blue', bgColor: 'bg-blue-50', borderColor: 'border-blue-200', textColor: 'text-blue-800' },
    { value: 'assignment', label: 'Assignment', icon: 'As', color: 'green', bgColor: 'bg-green-50', borderColor: 'border-green-200', textColor: 'text-green-800' },
    { value: 'exam', label: 'Exam', icon: 'Ex', color: 'red', bgColor: 'bg-red-50', borderColor: 'border-red-200', textColor: 'text-red-800' },
    { value: 'review_test', label: 'Review Test', icon: 'Rv', color: 'purple', bgColor: 'bg-purple-50', borderColor: 'border-purple-200', textColor: 'text-purple-800' },
    { value: 'personal', label: 'Personal', icon: 'Pr', color: 'gray', bgColor: 'bg-gray-50', borderColor: 'border-gray-200', textColor: 'text-gray-800' }
  ];

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load regular calendar events
      const calendarEvents = await calendarAPI.getEvents();
      
      // Load scheduled practice tests
      const scheduledTests = await practiceSchedulerAPI.getUpcomingTests();
      
      // Convert scheduled tests to calendar event format
      const testEvents = [];
      Object.values(scheduledTests).flat().forEach(test => {
        if (!test.is_completed) {
          testEvents.push({
            id: `scheduled-test-${test.id}`,
            title: `Review: ${test.subject} - ${test.topics.join(', ')}`,
            event_type: 'review_test',
            start_time: test.scheduled_for,
            end_time: test.scheduled_for,
            description: test.reason,
            subject: test.subject,
            priority: test.priority,
            original_score: test.original_score,
            scheduled_test_data: test
          });
        }
      });
      
      // Combine all events
      const allEvents = Array.isArray(calendarEvents) ? [...calendarEvents, ...testEvents] : testEvents;
      setEvents(allEvents);
    } catch (error) {
      console.error('Error loading calendar events:', error);
      setError('Failed to load calendar events. Please try again.');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const getEventTypeInfo = (eventType) => {
    return eventTypes.find(type => type.value === eventType) || eventTypes[0];
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return [];
    
    const dateStr = date.toISOString().split('T')[0];
    
    return events.filter(event => {
      const eventDate = new Date(event.start_time).toDateString();
      const targetDate = date.toDateString();
      return eventDate === targetDate;
    });
  };

  const handleDayClick = (date) => {
    if (!date) return;
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
    setSelectedDate(dateStr);
    setEventForm({
      title: '',
      event_type: 'study',
      start_time: '09:00',
      end_time: '10:00',
      description: '',
      subject: ''
    });
    setShowEventForm(true);
    setError('');
    setSuccess('');
  };

  const createEvent = async () => {
    if (!eventForm.title.trim()) {
      setError('Please enter an event title');
      return;
    }

    if (eventForm.start_time >= eventForm.end_time) {
      setError('End time must be after start time');
      return;
    }

    try {
      const eventData = {
        title: eventForm.title,
        event_type: eventForm.event_type,
        start_time: `${selectedDate}T${eventForm.start_time}:00`,
        end_time: `${selectedDate}T${eventForm.end_time}:00`,
        description: eventForm.description,
        subject: eventForm.subject
      };

      await calendarAPI.createEvent(eventData);
      
      setSuccess('Event created successfully!');
      setEventForm({
        title: '',
        event_type: 'study',
        start_time: '09:00',
        end_time: '10:00',
        description: '',
        subject: ''
      });
      setShowEventForm(false);
      setSelectedDate(null);
      loadEvents();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error creating event:', error);
      setError('Failed to create event. Please try again.');
    }
  };

  const navigateMonth = (direction) => {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(currentMonth.getMonth() + direction);
    setCurrentMonth(newMonth);
  };

  const formatTime = (timeStr) => {
    const time = new Date(`2000-01-01T${timeStr}`);
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavigationBar_Modern 
          user={student}
          currentPage="calendar"
          onNavigate={onNavigate}
          onLogout={() => onNavigate('auth')}
        />
        
        <div className="flex items-center justify-center pt-32">
          <div className="text-center">
            <ModernSpinner size="lg" />
            <ModernText className="mt-4 text-gray-600 font-medium">Loading your calendar...</ModernText>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <NavigationBar_Modern 
        user={student}
        currentPage="calendar"
        onNavigate={onNavigate}
        onLogout={() => onNavigate('auth')}
      />

      <ModernContainer className="py-8">
        {/* Header */}
        <div className="mb-8">
          <ModernHeading level={1} className="text-3xl font-bold text-gray-900 mb-2">
            Study Calendar
          </ModernHeading>
          <ModernText variant="body-large" className="text-gray-600 font-medium">
            Organize your study sessions, track assignments, and manage your schedule
          </ModernText>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-red-800 font-medium">{error}</ModernText>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <ModernText className="text-green-800 font-medium">{success}</ModernText>
            </div>
          </div>
        )}

        <ModernGrid cols={4} className="gap-8 mb-8">
          {/* Calendar Card */}
          <div className="col-span-3">
            <ModernCard className="shadow-lg">
              <ModernCardHeader>
                <div className="flex items-center justify-between">
                  <ModernHeading level={3} className="text-gray-900 font-bold">
                    {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                  </ModernHeading>
                  <div className="flex items-center gap-2">
                    <ModernButton
                      variant="outline"
                      onClick={() => navigateMonth(-1)}
                      className="p-2"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </ModernButton>
                    <ModernButton
                      variant="outline"
                      onClick={() => setCurrentMonth(new Date())}
                      className="px-4 py-2 text-sm font-medium"
                    >
                      Today
                    </ModernButton>
                    <ModernButton
                      variant="outline"
                      onClick={() => navigateMonth(1)}
                      className="p-2"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </ModernButton>
                  </div>
                </div>
              </ModernCardHeader>
              <ModernCardBody>
                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1 mb-4">
                  {dayNames.map(day => (
                    <div key={day} className="p-3 text-center font-semibold text-gray-500 text-sm">
                      {day}
                    </div>
                  ))}
                </div>
                
                <div className="grid grid-cols-7 gap-1">
                  {getDaysInMonth(currentMonth).map((date, index) => {
                    const dayEvents = date ? getEventsForDate(date) : [];
                    const isCurrentDay = date && isToday(date);
                    
                    return (
                      <div
                        key={index}
                        className={`min-h-[80px] p-2 border border-gray-100 rounded-lg cursor-pointer transition-all duration-200 ${
                          !date 
                            ? 'bg-gray-50' 
                            : isCurrentDay
                            ? 'bg-indigo-50 border-indigo-200 shadow-sm'
                            : 'hover:bg-gray-50 hover:border-gray-200'
                        }`}
                        onClick={() => date && handleDayClick(date)}
                      >
                        {date && (
                          <>
                            <div className={`text-sm font-medium mb-1 ${
                              isCurrentDay ? 'text-indigo-700' : 'text-gray-700'
                            }`}>
                              {date.getDate()}
                            </div>
                            <div className="space-y-1">
                              {dayEvents.slice(0, 2).map((event, eventIndex) => {
                                const typeInfo = getEventTypeInfo(event.event_type);
                                return (
                                  <div
                                    key={eventIndex}
                                    className={`text-xs px-2 py-1 rounded ${typeInfo.bgColor} ${typeInfo.textColor} truncate`}
                                    title={event.title}
                                  >
                                    {typeInfo.icon} {event.title}
                                  </div>
                                );
                              })}
                              {dayEvents.length > 2 && (
                                <div className="text-xs text-gray-500 px-2">
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
              </ModernCardBody>
            </ModernCard>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={4} className="text-gray-800 font-semibold">
                  This Month
                </ModernHeading>
              </ModernCardHeader>
              <ModernCardBody className="space-y-4">
                <div className="flex items-center justify-between">
                  <ModernText className="text-gray-600">Total Events</ModernText>
                  <ModernBadge variant="primary">{events.length}</ModernBadge>
                </div>
                <div className="flex items-center justify-between">
                  <ModernText className="text-gray-600">Study Sessions</ModernText>
                  <ModernBadge variant="secondary">
                    {events.filter(e => e.event_type === 'study').length}
                  </ModernBadge>
                </div>
                <div className="flex items-center justify-between">
                  <ModernText className="text-gray-600">Assignments</ModernText>
                  <ModernBadge variant="warning">
                    {events.filter(e => e.event_type === 'assignment').length}
                  </ModernBadge>
                </div>
                <div className="flex items-center justify-between">
                  <ModernText className="text-gray-600">Exams</ModernText>
                  <ModernBadge variant="error">
                    {events.filter(e => e.event_type === 'exam').length}
                  </ModernBadge>
                </div>
              </ModernCardBody>
            </ModernCard>

            {/* Event Types Legend */}
            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={4} className="text-gray-800 font-semibold">
                  Event Types
                </ModernHeading>
              </ModernCardHeader>
              <ModernCardBody className="space-y-3">
                {eventTypes.map(type => (
                  <div key={type.value} className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded ${type.bgColor} ${type.borderColor} border-2`}></div>
                    <ModernText className="text-gray-700 text-sm font-medium">
                      {type.icon} {type.label}
                    </ModernText>
                  </div>
                ))}
              </ModernCardBody>
            </ModernCard>

            {/* Quick Actions */}
            <ModernCard>
              <ModernCardHeader>
                <ModernHeading level={4} className="text-gray-800 font-semibold">
                  Quick Actions
                </ModernHeading>
              </ModernCardHeader>
              <ModernCardBody className="space-y-3">
                <ModernButton 
                  variant="primary" 
                  className="w-full font-medium"
                  onClick={() => handleDayClick(new Date())}
                >
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                  Add Today's Event
                </ModernButton>
                <ModernButton 
                  variant="outline" 
                  className="w-full font-medium"
                  onClick={loadEvents}
                >
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                  Refresh Events
                </ModernButton>
              </ModernCardBody>
            </ModernCard>
          </div>
        </ModernGrid>

        {/* Event Form Modal */}
        {showEventForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <ModernHeading level={3} className="text-gray-900 font-bold">
                    Create New Event
                  </ModernHeading>
                  <button 
                    onClick={() => {
                      setShowEventForm(false);
                      setSelectedDate(null);
                      setError('');
                    }}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>

                {selectedDate && (
                  <div className="mb-6 p-4 bg-indigo-50 rounded-xl">
                    <ModernText className="text-indigo-800 font-medium">
                      📅 {new Date(selectedDate).toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </ModernText>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Event Title *
                    </label>
                    <ModernInput
                      type="text"
                      value={eventForm.title}
                      onChange={(e) => setEventForm({...eventForm, title: e.target.value})}
                      placeholder="e.g., Mathematics Study Session"
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Event Type
                    </label>
                    <ModernSelect
                      value={eventForm.event_type}
                      onChange={(e) => setEventForm({...eventForm, event_type: e.target.value})}
                      className="w-full"
                    >
                      {eventTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </ModernSelect>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Start Time
                      </label>
                      <ModernInput
                        type="time"
                        value={eventForm.start_time}
                        onChange={(e) => setEventForm({...eventForm, start_time: e.target.value})}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        End Time
                      </label>
                      <ModernInput
                        type="time"
                        value={eventForm.end_time}
                        onChange={(e) => setEventForm({...eventForm, end_time: e.target.value})}
                        className="w-full"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subject (Optional)
                    </label>
                    <ModernInput
                      type="text"
                      value={eventForm.subject}
                      onChange={(e) => setEventForm({...eventForm, subject: e.target.value})}
                      placeholder="e.g., Mathematics, Physics"
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description (Optional)
                    </label>
                    <textarea
                      value={eventForm.description}
                      onChange={(e) => setEventForm({...eventForm, description: e.target.value})}
                      placeholder="Additional details about this event..."
                      rows="3"
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    />
                  </div>
                </div>

                <div className="flex gap-3 mt-8">
                  <ModernButton
                    variant="outline"
                    onClick={() => {
                      setShowEventForm(false);
                      setSelectedDate(null);
                      setError('');
                    }}
                    className="flex-1 font-medium"
                  >
                    Cancel
                  </ModernButton>
                  <ModernButton
                    variant="primary"
                    onClick={createEvent}
                    className="flex-1 font-medium"
                  >
                    Create Event
                  </ModernButton>
                </div>
              </div>
            </div>
          </div>
        )}
      </ModernContainer>
    </div>
  );
};

export default CalendarComponent_Modern;