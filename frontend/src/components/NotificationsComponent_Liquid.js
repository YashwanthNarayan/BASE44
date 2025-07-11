import React, { useState, useEffect } from 'react';
import { notificationsAPI } from '../services/api';
import { LiquidCard, LiquidButton } from './ui/LiquidComponents';
import '../styles/liquid-glass.css';

const NotificationsComponent = ({ student, onNavigate }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await notificationsAPI.getAll();
      setNotifications(response);
    } catch (error) {
      console.error('Error loading notifications:', error);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationsAPI.markAsRead(notificationId);
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

  const getNotificationGradient = (type) => {
    switch (type) {
      case 'achievement': return 'from-yellow-500/20 to-orange-500/20';
      case 'reminder': return 'from-blue-500/20 to-cyan-500/20';
      case 'message': return 'from-green-500/20 to-emerald-500/20';
      case 'assignment': return 'from-purple-500/20 to-indigo-500/20';
      case 'grade': return 'from-indigo-500/20 to-purple-500/20';
      default: return 'from-gray-500/20 to-gray-600/20';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now - time) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Neural transmission just received';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return time.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-space flex items-center justify-center">
        <LiquidCard className="p-8 text-center">
          <div className="quantum-loader mx-auto mb-4"></div>
          <p className="text-secondary">Synchronizing neural transmissions...</p>
        </LiquidCard>
      </div>
    );
  }

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
            🔔 Neural Transmission Center
          </h1>
          <p className="text-secondary">Stay synchronized with your quantum learning updates and neural alerts</p>
        </div>

        <LiquidCard>
          {notifications.length > 0 ? (
            <div className="divide-y divide-primary/10">
              {notifications.map((notification, index) => (
                <div
                  key={notification.id || index}
                  className={`
                    p-6 transition-all duration-300
                    bg-gradient-to-r ${getNotificationGradient(notification.type)}
                    ${!notification.is_read ? 'border-l-4 border-neon-cyan' : 'border-l-4 border-transparent'}
                    hover:bg-glass-strong
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="w-12 h-12 rounded-full bg-glass border border-primary/20 flex items-center justify-center text-2xl">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className={`font-semibold ${!notification.is_read ? 'text-primary' : 'text-secondary'}`}>
                            {notification.title}
                          </h3>
                          {!notification.is_read && (
                            <div className="w-2 h-2 bg-neon-cyan rounded-full glow-cyan"></div>
                          )}
                        </div>
                        <p className={`${!notification.is_read ? 'text-primary' : 'text-secondary'} mb-3 leading-relaxed`}>
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-secondary">
                            {formatTimeAgo(notification.created_at)}
                          </span>
                          {!notification.is_read && (
                            <LiquidButton
                              variant="secondary"
                              onClick={() => markAsRead(notification.id)}
                              className="text-xs"
                            >
                              ⚡ Mark as Processed
                            </LiquidButton>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Neural data stream */}
                  {!notification.is_read && (
                    <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <div className="text-6xl mb-6">🔔</div>
              <h2 className="text-2xl font-bold text-primary mb-4">Neural Transmission Center Empty</h2>
              <p className="text-secondary mb-8">
                Your quantum communication channel is clear. You'll receive neural transmissions about progress updates, achievements, and learning alerts here.
              </p>
              <LiquidButton onClick={() => onNavigate('student-dashboard')}>
                ⚡ Return to Neural Dashboard
              </LiquidButton>
            </div>
          )}
        </LiquidCard>

        {/* Neural Quick Actions */}
        {notifications.length > 0 && (
          <div className="mt-8 text-center">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <LiquidButton
                variant="secondary"
                onClick={() => {
                  // Mark all as read
                  notifications.forEach(notif => {
                    if (!notif.is_read) {
                      markAsRead(notif.id);
                    }
                  });
                }}
                disabled={notifications.every(n => n.is_read)}
              >
                ⚡ Process All Transmissions
              </LiquidButton>
              <LiquidButton onClick={() => onNavigate('student-dashboard')}>
                🧠 Return to Neural Dashboard
              </LiquidButton>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationsComponent;