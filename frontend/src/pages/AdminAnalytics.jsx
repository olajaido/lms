import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  ChartBarIcon,
  UserGroupIcon,
  AcademicCapIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import api from '../services/api'

function AdminAnalytics() {
  const [analytics, setAnalytics] = useState({
    totalUsers: 0,
    totalCourses: 0,
    totalEnrollments: 0,
    activeUsers: 0,
    completedCourses: 0,
    averageCompletionRate: 0,
    recentActivity: []
  })
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')

  useEffect(() => {
    fetchAnalytics()
  }, [timeRange])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      
      // Fetch various analytics data
      const [usersResponse, coursesResponse, enrollmentsResponse] = await Promise.all([
        api.get('/admin/users'),
        api.get('/courses'),
        api.get('/enrollments')
      ])

      const users = usersResponse.data.success ? usersResponse.data.data : usersResponse.data
      const courses = coursesResponse.data.success ? coursesResponse.data.data : coursesResponse.data
      const enrollments = enrollmentsResponse.data.success ? enrollmentsResponse.data.data : enrollmentsResponse.data

      // Calculate analytics
      const activeUsers = users.filter(u => u.status === 'active').length
      const completedEnrollments = enrollments.filter(e => e.status === 'completed').length
      const completionRate = enrollments.length > 0 ? (completedEnrollments / enrollments.length) * 100 : 0

      setAnalytics({
        totalUsers: users.length,
        totalCourses: courses.length,
        totalEnrollments: enrollments.length,
        activeUsers,
        completedCourses: completedEnrollments,
        averageCompletionRate: completionRate,
        recentActivity: [
          { type: 'user_registration', count: users.filter(u => new Date(u.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length },
          { type: 'course_creation', count: courses.filter(c => new Date(c.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length },
          { type: 'enrollment', count: enrollments.filter(e => new Date(e.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length }
        ]
      })
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">System Analytics</h1>
          <p className="text-secondary-600 mt-1">
            View system-wide analytics and performance metrics
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-secondary-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Users</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.totalUsers}</p>
                <p className="text-xs text-secondary-500">Active: {analytics.activeUsers}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <AcademicCapIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Courses</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.totalCourses}</p>
                <p className="text-xs text-secondary-500">Available for enrollment</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Enrollments</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.totalEnrollments}</p>
                <p className="text-xs text-secondary-500">Completed: {analytics.completedCourses}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
                                   <div className="p-3 bg-yellow-100 rounded-lg">
                       <ChartBarIcon className="h-6 w-6 text-yellow-600" />
                     </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Completion Rate</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.averageCompletionRate.toFixed(1)}%</p>
                <p className="text-xs text-secondary-500">Average across all courses</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-secondary-900">Recent Activity</h2>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {analytics.recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <ClockIcon className="h-4 w-4 text-primary-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-secondary-900">
                        {activity.type === 'user_registration' && 'New User Registrations'}
                        {activity.type === 'course_creation' && 'New Courses Created'}
                        {activity.type === 'enrollment' && 'New Enrollments'}
                      </p>
                      <p className="text-xs text-secondary-500">Last 7 days</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-secondary-900">{activity.count}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-secondary-900">Quick Actions</h2>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              <Link
                to="/admin/users"
                className="flex items-center p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors"
              >
                <UserGroupIcon className="h-5 w-5 text-secondary-600 mr-3" />
                <span className="text-sm font-medium text-secondary-900">Manage Users</span>
              </Link>
              <Link
                to="/admin/courses"
                className="flex items-center p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors"
              >
                <AcademicCapIcon className="h-5 w-5 text-secondary-600 mr-3" />
                <span className="text-sm font-medium text-secondary-900">Manage Courses</span>
              </Link>
              <Link
                to="/admin/courses/create"
                className="flex items-center p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors"
              >
                <AcademicCapIcon className="h-5 w-5 text-secondary-600 mr-3" />
                <span className="text-sm font-medium text-secondary-900">Create New Course</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Performance Metrics</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">
                {analytics.totalUsers > 0 ? ((analytics.activeUsers / analytics.totalUsers) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-sm text-secondary-600">User Engagement Rate</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {analytics.totalCourses > 0 ? (analytics.totalEnrollments / analytics.totalCourses).toFixed(1) : 0}
              </div>
              <p className="text-sm text-secondary-600">Avg Enrollments per Course</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {analytics.totalUsers > 0 ? (analytics.totalEnrollments / analytics.totalUsers).toFixed(1) : 0}
              </div>
              <p className="text-sm text-secondary-600">Avg Enrollments per User</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminAnalytics 