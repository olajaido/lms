import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  AcademicCapIcon,
  BookOpenIcon,
  ChartBarIcon,
  ClockIcon,
  TrophyIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    enrolledCourses: 0,
    completedCourses: 0,
    totalProgress: 0,
    certificates: 0,
    timeSpent: 0,
    achievements: 0
  })
  const [recentCourses, setRecentCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        
        // Fetch user enrollments
        const enrollmentsResponse = await api.get('/enrollments')
        const enrollments = enrollmentsResponse.data.data || []
        
        // Fetch analytics data
        const analyticsResponse = await api.get('/analytics/dashboard')
        const analytics = analyticsResponse.data.data || {}
        
        setStats({
          enrolledCourses: enrollments.length,
          completedCourses: analytics.completed_courses || 0,
          totalProgress: analytics.total_progress || 0,
          certificates: analytics.certificates || 0,
          timeSpent: analytics.time_spent || 0,
          achievements: analytics.achievements || 0
        })
        
        // Set recent courses from enrollments
        const recentCoursesData = enrollments.slice(0, 3).map(enrollment => ({
          id: enrollment.course_id,
          title: enrollment.course_title || 'Course Title',
          instructor: enrollment.instructor_name || 'Instructor',
          progress: enrollment.progress || 0,
          lastAccessed: enrollment.last_accessed || 'Recently'
        }))
        
        setRecentCourses(recentCoursesData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        // Set default values on error
        setStats({
          enrolledCourses: 0,
          completedCourses: 0,
          totalProgress: 0,
          certificates: 0,
          timeSpent: 0,
          achievements: 0
        })
        setRecentCourses([])
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <h1 className="text-2xl font-bold text-secondary-900">
          Welcome back, {user?.name}!
        </h1>
        <p className="text-secondary-600 mt-1">
          Continue your learning journey and track your progress.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AcademicCapIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Enrolled Courses</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.enrolledCourses}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrophyIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Completed Courses</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.completedCourses}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Overall Progress</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.totalProgress}%</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpenIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Certificates</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.certificates}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Time Spent</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.timeSpent}h</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Achievements</p>
                <p className="text-2xl font-semibold text-secondary-900">{stats.achievements}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Courses */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Recent Courses</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {recentCourses.map((course) => (
              <div key={course.id} className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium text-secondary-900">{course.title}</h4>
                  <p className="text-sm text-secondary-600">by {course.instructor}</p>
                  <p className="text-xs text-secondary-500 mt-1">{course.lastAccessed}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-secondary-900">{course.progress}%</p>
                    <p className="text-xs text-secondary-600">Complete</p>
                  </div>
                  <div className="w-16 bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Quick Actions</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="btn-primary">
              Browse Courses
            </button>
            <button className="btn-outline">
              View Certificates
            </button>
            <button className="btn-outline">
              Check Progress
            </button>
            <button className="btn-outline">
              Update Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 