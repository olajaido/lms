import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { StarIcon, ClockIcon, UserIcon, AcademicCapIcon } from '@heroicons/react/24/solid'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'

function CourseDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [enrolled, setEnrolled] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true)
        const response = await api.get(`/courses/${id}`)
        
        // Handle both wrapped and direct object responses
        if (response.data.success && response.data.data) {
          setCourse(response.data.data)
        } else if (response.data.id) {
          setCourse(response.data)
        } else {
          console.error('Failed to fetch course:', response.data.message || 'Unknown error')
          setCourse(null)
        }
      } catch (error) {
        console.error('Error fetching course:', error)
        setCourse(null)
      } finally {
        setLoading(false)
      }
    }

    fetchCourse()
  }, [id])

  const handleEnroll = async () => {
    if (!user) {
      alert('Please log in to enroll in this course')
      return
    }
    
    try {
      const response = await api.post('/enrollments', {
        course_id: parseInt(id),
        user_id: user.id,
        enrollment_date: new Date().toISOString(),
        status: 'active'
      })
      
      // Handle both wrapped and direct responses
      if (response.data.success) {
        setEnrolled(true)
        setProgress(25) // Initial progress
      } else if (response.data.id) {
        setEnrolled(true)
        setProgress(25) // Initial progress
      } else {
        console.error('Failed to enroll:', response.data.message || 'Unknown error')
      }
    } catch (error) {
      console.error('Error enrolling in course:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-secondary-600">Course not found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Course Header */}
      <div className="relative">
        <img
          src={course.image}
          alt={course.title}
          className="w-full h-64 object-cover rounded-lg"
        />
        <div className="absolute inset-0 bg-black/40 rounded-lg"></div>
        <div className="absolute bottom-6 left-6 text-white">
          <h1 className="text-3xl font-bold mb-2">{course.title}</h1>
          <p className="text-lg opacity-90">{course.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Course Info */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-secondary-900">About this course</h2>
            </div>
            <div className="card-body">
              <p className="text-secondary-600 mb-4">{course.description}</p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="flex items-center">
                  <StarIcon className="h-5 w-5 text-yellow-500 mr-2" />
                  <span className="text-sm text-secondary-600">{course.rating || 'Not rated'}</span>
                </div>
                <div className="flex items-center">
                  <ClockIcon className="h-5 w-5 text-secondary-400 mr-2" />
                  <span className="text-sm text-secondary-600">{course.duration || 'Not specified'}</span>
                </div>
                <div className="flex items-center">
                  <UserIcon className="h-5 w-5 text-secondary-400 mr-2" />
                  <span className="text-sm text-secondary-600">{course.students_enrolled?.toLocaleString() || '0'} students</span>
                </div>
                <div className="flex items-center">
                  <AcademicCapIcon className="h-5 w-5 text-secondary-400 mr-2" />
                  <span className="text-sm text-secondary-600">{course.level || 'Not specified'}</span>
                </div>
              </div>

              {enrolled && (
                <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-primary-900">Your Progress</span>
                    <span className="text-sm font-medium text-primary-900">{progress}%</span>
                  </div>
                  <div className="w-full bg-primary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Course Details */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-secondary-900">Course Details</h2>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Instructor:</span>
                  <span className="font-medium text-secondary-900">{course.instructor}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Category:</span>
                  <span className="font-medium text-secondary-900">{course.category || 'Not specified'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Level:</span>
                  <span className="font-medium text-secondary-900">{course.level || 'Not specified'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Duration:</span>
                  <span className="font-medium text-secondary-900">{course.duration || 'Not specified'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Rating:</span>
                  <span className="font-medium text-secondary-900">{course.rating || 'Not rated'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600">Students Enrolled:</span>
                  <span className="font-medium text-secondary-900">{course.students_enrolled || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Enrollment Card */}
          <div className="card sticky top-6">
            <div className="card-body">
              <div className="text-center mb-4">
                <div className="text-3xl font-bold text-secondary-900">${course.price || 'Free'}</div>
              </div>

              {enrolled ? (
                <button className="btn-primary w-full mb-4">
                  Continue Learning
                </button>
              ) : (
                <button
                  onClick={handleEnroll}
                  className="btn-primary w-full mb-4"
                >
                  Enroll Now
                </button>
              )}

              <div className="text-center text-sm text-secondary-600">
                30-Day Money-Back Guarantee
              </div>
            </div>
          </div>

          {/* Instructor */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Instructor</h3>
            </div>
            <div className="card-body">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-primary-100 rounded-full mr-3 flex items-center justify-center">
                  <AcademicCapIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h4 className="font-medium text-secondary-900">{course.instructor}</h4>
                  <p className="text-sm text-secondary-600">Course Instructor</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CourseDetail 