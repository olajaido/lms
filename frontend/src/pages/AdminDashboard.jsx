import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  AcademicCapIcon,
  UserGroupIcon,
  ChartBarIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline'
import api from '../services/api'

function AdminDashboard() {
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalUsers: 0,
    totalEnrollments: 0,
    activeUsers: 0
  })
  const [recentCourses, setRecentCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true)
        
        // Fetch courses for stats
        const coursesResponse = await api.get('/courses')
        const courses = coursesResponse.data.success ? coursesResponse.data.data : coursesResponse.data
        
        // Fetch users (admin endpoint)
        const usersResponse = await api.get('/admin/users')
        const users = usersResponse.data.success ? usersResponse.data.data : usersResponse.data
        
        // Fetch enrollments
        const enrollmentsResponse = await api.get('/enrollments')
        const enrollments = enrollmentsResponse.data.success ? enrollmentsResponse.data.data : enrollmentsResponse.data
        
        setStats({
          totalCourses: courses.length,
          totalUsers: users.length,
          totalEnrollments: enrollments.length,
          activeUsers: users.filter(u => u.status === 'active').length
        })
        
        // Get recent courses (last 5)
        setRecentCourses(courses.slice(0, 5))
        
      } catch (error) {
        console.error('Error fetching admin data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAdminData()
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Admin Dashboard</h1>
          <p className="text-secondary-600 mt-1">
            Manage courses, users, and system analytics
          </p>
        </div>
        <div className="mt-4 sm:mt-0 space-x-3">
          <Link to="/admin/courses/create" className="btn-primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Course
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                <AcademicCapIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Courses</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.totalCourses}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Users</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.totalUsers}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Enrollments</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.totalEnrollments}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Active Users</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.activeUsers}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link to="/admin/courses" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                <AcademicCapIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Manage Courses</h3>
                <p className="text-secondary-600">Create, edit, and delete courses</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/admin/users" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Manage Users</h3>
                <p className="text-secondary-600">View and manage user accounts</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/admin/analytics" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Analytics</h3>
                <p className="text-secondary-600">View system analytics and reports</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/admin/content" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Content Management</h3>
                <p className="text-secondary-600">Upload and manage learning content</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/admin/assessments" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <ClipboardDocumentListIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Assessment Management</h3>
                <p className="text-secondary-600">Create and manage quizzes and exams</p>
              </div>
            </div>
          </div>
        </Link>
        
        <Link to="/admin/progress" className="card hover:shadow-lg transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-3 bg-teal-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-teal-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-secondary-900">Progress Management</h3>
                <p className="text-secondary-600">Monitor student progress and performance</p>
              </div>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Courses */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-secondary-900">Recent Courses</h2>
          <Link to="/admin/courses" className="text-primary-600 hover:text-primary-700 text-sm">
            View All
          </Link>
        </div>
        <div className="card-body">
          {recentCourses.length === 0 ? (
            <p className="text-secondary-600 text-center py-4">No courses found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-secondary-200">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                      Course
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                      Instructor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                      Students
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-secondary-200">
                  {recentCourses.map((course) => (
                    <tr key={course.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-secondary-900">{course.title}</div>
                          <div className="text-sm text-secondary-500">{course.category}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                        {course.instructor}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                        {course.students_enrolled}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          course.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {course.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <Link
                          to={`/admin/courses/${course.id}`}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </Link>
                        <Link
                          to={`/admin/courses/${course.id}/edit`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </Link>
                        <button
                          onClick={() => handleDeleteCourse(course.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard 