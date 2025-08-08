import React, { useState, useEffect } from 'react'
import { BellIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

function NotificationBell() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) {
      fetchUnreadNotifications()
    }
  }, [user])

  const fetchUnreadNotifications = async () => {
    if (!user) return
    
    try {
      setLoading(true)
      const response = await api.get(`/notifications/user/${user.id}/unread`)
      const unreadNotifications = response.data.success ? response.data.data : response.data
      setNotifications(unreadNotifications)
      setUnreadCount(unreadNotifications.length)
    } catch (error) {
      console.error('Error fetching notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (notificationId) => {
    try {
      await api.patch(`/notifications/${notificationId}/read?user_id=${user.id}`)
      // Remove from unread list
      setNotifications(prev => prev.filter(n => n.id !== notificationId))
      setUnreadCount(prev => prev - 1)
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const dismissNotification = async (notificationId) => {
    try {
      await api.patch(`/notifications/${notificationId}/dismiss?user_id=${user.id}`)
      // Remove from list
      setNotifications(prev => prev.filter(n => n.id !== notificationId))
      setUnreadCount(prev => prev - 1)
    } catch (error) {
      console.error('Error dismissing notification:', error)
    }
  }

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'course_announcement':
        return '📢'
      case 'assessment_due':
        return '📝'
      case 'grade_available':
        return '📊'
      case 'course_completed':
        return '🎓'
      case 'certificate_earned':
        return '🏆'
      case 'system_update':
        return '🔧'
      case 'message_received':
        return '💬'
      default:
        return '🔔'
    }
  }

  const getNotificationColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600'
      case 'high':
        return 'text-orange-600'
      case 'normal':
        return 'text-blue-600'
      case 'low':
        return 'text-gray-600'
      default:
        return 'text-blue-600'
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-secondary-600 hover:text-secondary-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
      >
        <BellIcon className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-1">
            <div className="px-4 py-2 border-b border-secondary-200">
              <h3 className="text-sm font-medium text-secondary-900">Notifications</h3>
              {unreadCount > 0 && (
                <p className="text-xs text-secondary-600">{unreadCount} unread</p>
              )}
            </div>
            
            <div className="max-h-64 overflow-y-auto">
              {loading ? (
                <div className="px-4 py-2 text-sm text-secondary-600">
                  Loading notifications...
                </div>
              ) : notifications.length === 0 ? (
                <div className="px-4 py-2 text-sm text-secondary-600">
                  No unread notifications
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="px-4 py-3 hover:bg-secondary-50 border-b border-secondary-100 last:border-b-0"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <span className="text-lg">{getNotificationIcon(notification.notification_type)}</span>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium ${getNotificationColor(notification.priority)}`}>
                            {notification.title}
                          </p>
                          <p className="text-sm text-secondary-600 mt-1">
                            {notification.content}
                          </p>
                          <p className="text-xs text-secondary-400 mt-1">
                            {new Date(notification.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex space-x-1">
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="text-xs text-primary-600 hover:text-primary-800"
                        >
                          Mark read
                        </button>
                        <button
                          onClick={() => dismissNotification(notification.id)}
                          className="text-xs text-secondary-500 hover:text-secondary-700"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            {notifications.length > 0 && (
              <div className="px-4 py-2 border-t border-secondary-200">
                <button
                  onClick={() => {
                    // Mark all as read
                    notifications.forEach(n => markAsRead(n.id))
                  }}
                  className="text-xs text-primary-600 hover:text-primary-800"
                >
                  Mark all as read
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default NotificationBell 