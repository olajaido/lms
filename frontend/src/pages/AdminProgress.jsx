import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  PauseIcon,
  ChartBarIcon,
  CalendarIcon,
  TrophyIcon,
  BookOpenIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

function AdminProgress() {
  const { user } = useAuth()
  const [progressData, setProgressData] = useState([])
  const [courses, setCourses] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedProgress, setSelectedProgress] = useState(null)
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterCourse, setFilterCourse] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch courses
      const coursesResponse = await api.get('/courses')
      const coursesData = coursesResponse.data.success ? coursesResponse.data.data : coursesResponse.data
      setCourses(coursesData)
      
      // Fetch users
      const usersResponse = await api.get('/admin/users')
      const usersData = usersResponse.data.success ? usersResponse.data.data : usersResponse.data
      setUsers(usersData)
      
      // Fetch all progress data
      const allProgress = []
      for (const course of coursesData) {
        try {
          const response = await api.get(`/progress/course/${course.id}`)
          const courseProgress = response.data.success ? response.data.data : response.data
          if (Array.isArray(courseProgress)) {
            allProgress.push(...courseProgress)
          }
        } catch (error) {
          console.error(`Error fetching progress for course ${course.id}:`, error)
        }
      }
      setProgressData(allProgress)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getProgressStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />
      case 'in_progress':
        return <PlayIcon className="h-6 w-6 text-blue-500" />
      case 'paused':
        return <PauseIcon className="h-6 w-6 text-yellow-500" />
      case 'not_started':
        return <BookOpenIcon className="h-6 w-6 text-gray-500" />
      default:
        return <BookOpenIcon className="h-6 w-6 text-gray-500" />
    }
  }

  const getProgressStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'not_started':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTime = (seconds) => {
    if (!seconds) return '0h 0m'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString()
  }

  const getCourseName = (courseId) => {
    const course = courses.find(c => c.id === courseId)
    return course ? course.title : `Course ${courseId}`
  }

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId)
    return user ? `${user.first_name} ${user.last_name}` : `User ${userId}`
  }

  const getUserEmail = (userId) => {
    const user = users.find(u => u.id === userId)
    return user ? user.email : `user${userId}@example.com`
  }

  const filteredProgress = progressData.filter(progress => {
    // Filter by status
    if (filterStatus !== 'all' && progress.status !== filterStatus) return false
    
    // Filter by course
    if (filterCourse !== 'all' && progress.course_id !== parseInt(filterCourse)) return false
    
    // Filter by search term
    if (searchTerm) {
      const courseName = getCourseName(progress.course_id).toLowerCase()
      const userName = getUserName(progress.user_id).toLowerCase()
      const userEmail = getUserEmail(progress.user_id).toLowerCase()
      const searchLower = searchTerm.toLowerCase()
      
      if (!courseName.includes(searchLower) && 
          !userName.includes(searchLower) && 
          !userEmail.includes(searchLower)) {
        return false
      }
    }
    
    return true
  })

  const getOverallStats = () => {
    const totalProgress = progressData.length
    const completedProgress = progressData.filter(p => p.status === 'completed').length
    const inProgressProgress = progressData.filter(p => p.status === 'in_progress').length
    const totalTimeSpent = progressData.reduce((sum, p) => sum + (p.time_spent || 0), 0)
    const averageCompletion = progressData.length > 0 
      ? progressData.reduce((sum, p) => sum + (p.completion_percentage || 0), 0) / progressData.length
      : 0

    return {
      totalProgress,
      completedProgress,
      inProgressProgress,
      totalTimeSpent,
      averageCompletion
    }
  }

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-secondary-900 mb-4">Access Denied</h1>
          <p className="text-secondary-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    )
  }

  const stats = getOverallStats()

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">Progress Management</h1>
          <p className="text-secondary-600 mt-2">
            Monitor and manage student progress across all courses
          </p>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Progress Records</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.totalProgress}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Completed</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.completedProgress}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <PlayIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">In Progress</p>
                <p className="text-2xl font-bold text-secondary-900">{stats.inProgressProgress}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <ClockIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Total Time</p>
                <p className="text-2xl font-bold text-secondary-900">{formatTime(stats.totalTimeSpent)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-secondary-900">Overall Progress</h2>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary-600">{stats.averageCompletion.toFixed(1)}%</p>
              <p className="text-sm text-secondary-600">Average Completion</p>
            </div>
          </div>
          
          <div className="w-full bg-secondary-200 rounded-full h-3">
            <div 
              className="bg-primary-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${stats.averageCompletion}%` }}
            ></div>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="mb-6 space-y-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterStatus === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              All Status
            </button>
            <button
              onClick={() => setFilterStatus('completed')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterStatus === 'completed'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Completed
            </button>
            <button
              onClick={() => setFilterStatus('in_progress')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterStatus === 'in_progress'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              In Progress
            </button>
            <button
              onClick={() => setFilterStatus('paused')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterStatus === 'paused'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Paused
            </button>
            <button
              onClick={() => setFilterStatus('not_started')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterStatus === 'not_started'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Not Started
            </button>
          </div>

          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-secondary-700 mb-2">Filter by Course</label>
              <select
                value={filterCourse}
                onChange={(e) => setFilterCourse(e.target.value)}
                className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Courses</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>
                    {course.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-secondary-700 mb-2">Search</label>
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search by course or student..."
                  className="w-full p-3 pl-10 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-3.5 h-5 w-5 text-secondary-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Progress List */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-xl font-semibold text-secondary-900">
              {filterStatus === 'all' ? 'All Progress Records' : 
               filterStatus === 'completed' ? 'Completed Progress' :
               filterStatus === 'in_progress' ? 'Progress In Progress' :
               filterStatus === 'paused' ? 'Paused Progress' : 'Not Started Progress'}
            </h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-secondary-600">Loading progress data...</p>
            </div>
          ) : filteredProgress.length === 0 ? (
            <div className="p-6 text-center">
              <AcademicCapIcon className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">
                {filterStatus === 'all' ? 'No progress data available' : 
                 filterStatus === 'completed' ? 'No completed progress' :
                 filterStatus === 'in_progress' ? 'No progress in progress' :
                 filterStatus === 'paused' ? 'No paused progress' : 'No progress not started'}
              </h3>
              <p className="text-secondary-600">
                {filterStatus === 'all' ? 'There are no progress records yet.' : 
                 filterStatus === 'completed' ? 'No progress has been completed yet.' :
                 filterStatus === 'in_progress' ? 'No progress is currently in progress.' :
                 filterStatus === 'paused' ? 'No progress is currently paused.' : 'No progress has been started yet.'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-secondary-200">
              {filteredProgress.map((progress) => (
                <div key={progress.id} className="p-6 hover:bg-secondary-50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      {getProgressStatusIcon(progress.status)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <h3 className="text-lg font-medium text-secondary-900">
                            {getCourseName(progress.course_id)}
                          </h3>
                          <span className="text-sm text-secondary-500">
                            by {getUserName(progress.user_id)}
                          </span>
                        </div>
                        <p className="text-sm text-secondary-600 mt-1">
                          {getUserEmail(progress.user_id)}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-secondary-500">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getProgressStatusColor(progress.status)}`}>
                            {progress.status.replace('_', ' ')}
                          </span>
                          <span>•</span>
                          <span>{progress.completion_percentage?.toFixed(1) || 0}% complete</span>
                          <span>•</span>
                          <span className="flex items-center">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            {formatTime(progress.time_spent)}
                          </span>
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="mt-3">
                          <div className="w-full bg-secondary-200 rounded-full h-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress.completion_percentage || 0}%` }}
                            ></div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                          <div>
                            <p className="text-secondary-600">Lessons</p>
                            <p className="font-medium">{progress.completed_lessons || 0}/{progress.total_lessons || 0}</p>
                          </div>
                          <div>
                            <p className="text-secondary-600">Assessments</p>
                            <p className="font-medium">{progress.completed_assessments || 0}/{progress.total_assessments || 0}</p>
                          </div>
                          <div>
                            <p className="text-secondary-600">Assignments</p>
                            <p className="font-medium">{progress.completed_assignments || 0}/{progress.total_assignments || 0}</p>
                          </div>
                          <div>
                            <p className="text-secondary-600">Last Accessed</p>
                            <p className="font-medium">{formatDate(progress.last_accessed)}</p>
                          </div>
                        </div>

                        {progress.certificate_earned && (
                          <div className="flex items-center space-x-2 mt-3">
                            <TrophyIcon className="h-5 w-5 text-yellow-500" />
                            <span className="text-sm font-medium text-yellow-700">Certificate Earned</span>
                            {progress.certificate_issued_at && (
                              <span className="text-sm text-secondary-500">
                                on {formatDate(progress.certificate_issued_at)}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setSelectedProgress(progress)}
                        className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md"
                        title="View Details"
                      >
                        <ChartBarIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Progress Detail Modal */}
        {selectedProgress && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-semibold text-secondary-900">
                  Progress Details
                </h2>
                <button
                  onClick={() => setSelectedProgress(null)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Course & Student</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Course:</span>
                        <span className="font-medium">{getCourseName(selectedProgress.course_id)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Student:</span>
                        <span className="font-medium">{getUserName(selectedProgress.user_id)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Email:</span>
                        <span className="font-medium">{getUserEmail(selectedProgress.user_id)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Progress Overview</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Status:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProgressStatusColor(selectedProgress.status)}`}>
                          {selectedProgress.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Completion:</span>
                        <span className="font-medium">{selectedProgress.completion_percentage?.toFixed(1) || 0}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Time Spent:</span>
                        <span className="font-medium">{formatTime(selectedProgress.time_spent)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Timeline</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Started:</span>
                        <span className="font-medium">{formatDate(selectedProgress.started_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Last Accessed:</span>
                        <span className="font-medium">{formatDate(selectedProgress.last_accessed)}</span>
                      </div>
                      {selectedProgress.completed_at && (
                        <div className="flex justify-between">
                          <span className="text-secondary-600">Completed:</span>
                          <span className="font-medium">{formatDate(selectedProgress.completed_at)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Activity Breakdown</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Lessons:</span>
                        <span className="font-medium">{selectedProgress.completed_lessons || 0}/{selectedProgress.total_lessons || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Assessments:</span>
                        <span className="font-medium">{selectedProgress.completed_assessments || 0}/{selectedProgress.total_assessments || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-secondary-600">Assignments:</span>
                        <span className="font-medium">{selectedProgress.completed_assignments || 0}/{selectedProgress.total_assignments || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {selectedProgress.notes && (
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Admin Notes</h3>
                    <p className="text-sm text-secondary-600 bg-secondary-50 p-3 rounded-lg">
                      {selectedProgress.notes}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminProgress 