import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  EyeIcon,
  ChartBarIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'

function Assessments() {
  const { user } = useAuth()
  const [assessments, setAssessments] = useState([])
  const [enrolledCourses, setEnrolledCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAssessment, setSelectedAssessment] = useState(null)
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch enrolled courses
      const enrollmentsResponse = await api.get('/enrollments')
      const enrollmentsData = enrollmentsResponse.data.success ? enrollmentsResponse.data.data : enrollmentsResponse.data
      const courseIds = enrollmentsData.map(enrollment => enrollment.course_id)
      setEnrolledCourses(courseIds)
      
      // Fetch assessments for enrolled courses
      const allAssessments = []
      for (const courseId of courseIds) {
        try {
          const response = await api.get(`/assessments/course/${courseId}`)
          const courseAssessments = response.data.success ? response.data.data : response.data
          if (Array.isArray(courseAssessments)) {
            allAssessments.push(...courseAssessments)
          }
        } catch (error) {
          console.error(`Error fetching assessments for course ${courseId}:`, error)
        }
      }
      setAssessments(allAssessments)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getAssessmentTypeIcon = (type) => {
    switch (type) {
      case 'quiz':
        return <AcademicCapIcon className="h-6 w-6 text-blue-500" />
      case 'exam':
        return <ChartBarIcon className="h-6 w-6 text-red-500" />
      case 'assignment':
        return <AcademicCapIcon className="h-6 w-6 text-green-500" />
      case 'project':
        return <AcademicCapIcon className="h-6 w-6 text-purple-500" />
      default:
        return <AcademicCapIcon className="h-6 w-6 text-gray-500" />
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString()
  }

  const isAssessmentAvailable = (assessment) => {
    const now = new Date()
    const startDate = assessment.start_date ? new Date(assessment.start_date) : null
    const endDate = assessment.end_date ? new Date(assessment.end_date) : null
    
    if (startDate && now < startDate) return false
    if (endDate && now > endDate) return false
    return assessment.is_active
  }

  const getAssessmentStatus = (assessment) => {
    const now = new Date()
    const startDate = assessment.start_date ? new Date(assessment.start_date) : null
    const endDate = assessment.end_date ? new Date(assessment.end_date) : null
    
    if (startDate && now < startDate) {
      return {
        status: 'upcoming',
        text: 'Upcoming',
        color: 'bg-yellow-100 text-yellow-800'
      }
    }
    
    if (endDate && now > endDate) {
      return {
        status: 'expired',
        text: 'Expired',
        color: 'bg-red-100 text-red-800'
      }
    }
    
    if (!assessment.is_active) {
      return {
        status: 'inactive',
        text: 'Inactive',
        color: 'bg-gray-100 text-gray-800'
      }
    }
    
    return {
      status: 'available',
      text: 'Available',
      color: 'bg-green-100 text-green-800'
    }
  }

  const filteredAssessments = assessments.filter(assessment => {
    if (filterType === 'all') return true
    if (filterType === 'available') return isAssessmentAvailable(assessment)
    if (filterType === 'upcoming') {
      const now = new Date()
      const startDate = assessment.start_date ? new Date(assessment.start_date) : null
      return startDate && now < startDate
    }
    if (filterType === 'expired') {
      const now = new Date()
      const endDate = assessment.end_date ? new Date(assessment.end_date) : null
      return endDate && now > endDate
    }
    return true
  })

  if (!user) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-secondary-900 mb-4">Please log in</h1>
          <p className="text-secondary-600">You need to be logged in to view assessments.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">My Assessments</h1>
          <p className="text-secondary-600 mt-2">
            View and take assessments for your enrolled courses
          </p>
        </div>

        {/* Filter Controls */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterType === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              All Assessments
            </button>
            <button
              onClick={() => setFilterType('available')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterType === 'available'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Available
            </button>
            <button
              onClick={() => setFilterType('upcoming')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterType === 'upcoming'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Upcoming
            </button>
            <button
              onClick={() => setFilterType('expired')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filterType === 'expired'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50'
              }`}
            >
              Expired
            </button>
          </div>
        </div>

        {/* Assessments List */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-xl font-semibold text-secondary-900">
              {filterType === 'all' ? 'All Assessments' : 
               filterType === 'available' ? 'Available Assessments' :
               filterType === 'upcoming' ? 'Upcoming Assessments' : 'Expired Assessments'}
            </h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-secondary-600">Loading assessments...</p>
            </div>
          ) : filteredAssessments.length === 0 ? (
            <div className="p-6 text-center">
              <AcademicCapIcon className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">
                {filterType === 'all' ? 'No assessments available' : 
                 filterType === 'available' ? 'No available assessments' :
                 filterType === 'upcoming' ? 'No upcoming assessments' : 'No expired assessments'}
              </h3>
              <p className="text-secondary-600">
                {filterType === 'all' ? 'You don\'t have any assessments yet.' : 
                 filterType === 'available' ? 'No assessments are currently available for you.' :
                 filterType === 'upcoming' ? 'No assessments are scheduled to start soon.' : 'No assessments have expired.'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-secondary-200">
              {filteredAssessments.map((assessment) => {
                const status = getAssessmentStatus(assessment)
                const isAvailable = isAssessmentAvailable(assessment)
                
                return (
                  <div key={assessment.id} className="p-6 hover:bg-secondary-50">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        {getAssessmentTypeIcon(assessment.type)}
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-secondary-900">{assessment.title}</h3>
                          <p className="text-secondary-600 mt-1">{assessment.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-secondary-500">
                            <span className="capitalize">{assessment.type}</span>
                            <span>•</span>
                            <span>{assessment.total_points} points</span>
                            {assessment.time_limit && (
                              <>
                                <span>•</span>
                                <span className="flex items-center">
                                  <ClockIcon className="h-4 w-4 mr-1" />
                                  {assessment.time_limit} min
                                </span>
                              </>
                            )}
                            <span>•</span>
                            <span>Passing: {assessment.passing_score}%</span>
                          </div>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-secondary-500">
                            {assessment.start_date && (
                              <>
                                <span className="flex items-center">
                                  <CalendarIcon className="h-4 w-4 mr-1" />
                                  Start: {formatDate(assessment.start_date)}
                                </span>
                                <span>•</span>
                              </>
                            )}
                            {assessment.end_date && (
                              <span className="flex items-center">
                                <CalendarIcon className="h-4 w-4 mr-1" />
                                End: {formatDate(assessment.end_date)}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 mt-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                              {status.status === 'available' && <CheckCircleIcon className="h-3 w-3 mr-1" />}
                              {status.status === 'expired' && <XCircleIcon className="h-3 w-3 mr-1" />}
                              {status.text}
                            </span>
                            {assessment.allow_retakes && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Retakes Allowed
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setSelectedAssessment(assessment)}
                          className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md"
                          title="View Details"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </button>
                        {isAvailable && (
                          <button
                            className="btn-primary flex items-center space-x-2"
                            title="Start Assessment"
                          >
                            <PlayIcon className="h-4 w-4" />
                            <span>Start</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Assessment Detail Modal */}
        {selectedAssessment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-semibold text-secondary-900">{selectedAssessment.title}</h2>
                <button
                  onClick={() => setSelectedAssessment(null)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-secondary-900 mb-2">Description</h3>
                  <p className="text-secondary-600">{selectedAssessment.description || 'No description provided.'}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Assessment Details</h3>
                    <div className="space-y-1 text-sm text-secondary-600">
                      <p><span className="font-medium">Type:</span> {selectedAssessment.type}</p>
                      <p><span className="font-medium">Points:</span> {selectedAssessment.total_points}</p>
                      <p><span className="font-medium">Time Limit:</span> {selectedAssessment.time_limit || 'No limit'} minutes</p>
                      <p><span className="font-medium">Passing Score:</span> {selectedAssessment.passing_score}%</p>
                      <p><span className="font-medium">Max Attempts:</span> {selectedAssessment.max_attempts}</p>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-secondary-900 mb-2">Schedule</h3>
                    <div className="space-y-1 text-sm text-secondary-600">
                      <p><span className="font-medium">Start Date:</span> {formatDate(selectedAssessment.start_date)}</p>
                      <p><span className="font-medium">End Date:</span> {formatDate(selectedAssessment.end_date)}</p>
                      <p><span className="font-medium">Status:</span> {getAssessmentStatus(selectedAssessment).text}</p>
                    </div>
                  </div>
                </div>
                
                {isAssessmentAvailable(selectedAssessment) && (
                  <div className="pt-4 border-t border-secondary-200">
                    <button className="btn-primary w-full">
                      Start Assessment
                    </button>
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

export default Assessments 