import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  AcademicCapIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

function AdminAssessments() {
  const { user } = useAuth()
  const [assessments, setAssessments] = useState([])
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedAssessment, setSelectedAssessment] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'quiz',
    course_id: '',
    total_points: 100,
    time_limit: 30,
    passing_score: 70,
    allow_retakes: false,
    max_attempts: 1,
    start_date: '',
    end_date: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch courses for dropdown
      const coursesResponse = await api.get('/courses')
      const coursesData = coursesResponse.data.success ? coursesResponse.data.data : coursesResponse.data
      setCourses(coursesData)
      
      // Fetch assessments
      const assessmentsResponse = await api.get('/assessments')
      const assessmentsData = assessmentsResponse.data.success ? assessmentsResponse.data.data : assessmentsResponse.data
      setAssessments(assessmentsData || [])
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAssessment = async (e) => {
    e.preventDefault()
    try {
      const response = await api.post('/assessments', formData)
      if (response.data.success) {
        setShowCreateForm(false)
        setFormData({
          title: '',
          description: '',
          type: 'quiz',
          course_id: '',
          total_points: 100,
          time_limit: 30,
          passing_score: 70,
          allow_retakes: false,
          max_attempts: 1,
          start_date: '',
          end_date: ''
        })
        fetchData()
        alert('Assessment created successfully!')
      }
    } catch (error) {
      console.error('Error creating assessment:', error)
      alert('Error creating assessment. Please try again.')
    }
  }

  const handleDeleteAssessment = async (assessmentId) => {
    if (window.confirm('Are you sure you want to delete this assessment?')) {
      try {
        await api.delete(`/assessments/${assessmentId}`)
        fetchData()
        alert('Assessment deleted successfully!')
      } catch (error) {
        console.error('Error deleting assessment:', error)
        alert('Error deleting assessment. Please try again.')
      }
    }
  }

  const getAssessmentTypeIcon = (type) => {
    switch (type) {
      case 'quiz':
        return <AcademicCapIcon className="h-6 w-6 text-blue-500" />
      case 'exam':
        return <ChartBarIcon className="h-6 w-6 text-red-500" />
      case 'assignment':
        return <PencilIcon className="h-6 w-6 text-green-500" />
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

  const getCourseName = (courseId) => {
    const course = courses.find(c => c.id === courseId)
    return course ? course.title : `Course ${courseId}`
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

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">Assessment Management</h1>
          <p className="text-secondary-600 mt-2">
            Create and manage quizzes, exams, and assignments for your courses
          </p>
        </div>

        {/* Header with Create Button */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-semibold text-secondary-900">Assessments</h2>
            <p className="text-secondary-600">Manage all assessments across courses</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="h-5 w-5" />
            <span>Create Assessment</span>
          </button>
        </div>

        {/* Create Assessment Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Create New Assessment</h3>
            
            <form onSubmit={handleCreateAssessment} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Assessment Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Assessment Type
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="quiz">Quiz</option>
                    <option value="exam">Exam</option>
                    <option value="assignment">Assignment</option>
                    <option value="project">Project</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Course
                  </label>
                  <select
                    value={formData.course_id}
                    onChange={(e) => setFormData({...formData, course_id: parseInt(e.target.value)})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  >
                    <option value="">Select a course</option>
                    {courses.map(course => (
                      <option key={course.id} value={course.id}>
                        {course.title}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Total Points
                  </label>
                  <input
                    type="number"
                    value={formData.total_points}
                    onChange={(e) => setFormData({...formData, total_points: parseInt(e.target.value)})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Time Limit (minutes)
                  </label>
                  <input
                    type="number"
                    value={formData.time_limit}
                    onChange={(e) => setFormData({...formData, time_limit: parseInt(e.target.value)})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Passing Score (%)
                  </label>
                  <input
                    type="number"
                    value={formData.passing_score}
                    onChange={(e) => setFormData({...formData, passing_score: parseInt(e.target.value)})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="0"
                    max="100"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Max Attempts
                  </label>
                  <input
                    type="number"
                    value={formData.max_attempts}
                    onChange={(e) => setFormData({...formData, max_attempts: parseInt(e.target.value)})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="1"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="allow_retakes"
                    checked={formData.allow_retakes}
                    onChange={(e) => setFormData({...formData, allow_retakes: e.target.checked})}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded"
                  />
                  <label htmlFor="allow_retakes" className="text-sm font-medium text-secondary-700">
                    Allow Retakes
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.end_date}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                    className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Create Assessment
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Assessments List */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-xl font-semibold text-secondary-900">All Assessments</h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-secondary-600">Loading assessments...</p>
            </div>
          ) : assessments.length === 0 ? (
            <div className="p-6 text-center">
              <AcademicCapIcon className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No assessments created yet</h3>
              <p className="text-secondary-600">Create your first assessment to get started.</p>
            </div>
          ) : (
            <div className="divide-y divide-secondary-200">
              {assessments.map((assessment) => (
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
                          <span>{getCourseName(assessment.course_id)}</span>
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
                        </div>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-secondary-500">
                          <span>Passing: {assessment.passing_score}%</span>
                          <span>•</span>
                          <span>Max attempts: {assessment.max_attempts}</span>
                          <span>•</span>
                          <span>Start: {formatDate(assessment.start_date)}</span>
                          <span>•</span>
                          <span>End: {formatDate(assessment.end_date)}</span>
                        </div>
                        <div className="flex items-center space-x-2 mt-2">
                          {assessment.is_active ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircleIcon className="h-3 w-3 mr-1" />
                              Active
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              <XCircleIcon className="h-3 w-3 mr-1" />
                              Inactive
                            </span>
                          )}
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
                      <button
                        className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md"
                        title="Edit"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteAssessment(assessment.id)}
                        className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md"
                        title="Delete"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminAssessments 