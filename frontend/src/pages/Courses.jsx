import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'
import api from '../services/api'

function Courses() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState('newest')

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'programming', name: 'Programming' },
    { id: 'design', name: 'Design' },
    { id: 'business', name: 'Business' },
    { id: 'marketing', name: 'Marketing' },
    { id: 'data-science', name: 'Data Science' }
  ]

  const sortOptions = [
    { id: 'newest', name: 'Newest' },
    { id: 'oldest', name: 'Oldest' },
    { id: 'popular', name: 'Most Popular' },
    { id: 'rating', name: 'Highest Rated' }
  ]

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true)
        const params = {
          skip: 0,
          limit: 100
        }
        
        if (searchTerm) {
          params.search = searchTerm
        }
        if (selectedCategory !== 'all') {
          params.category = selectedCategory
        }
        
        const response = await api.get('/courses', { params })
        
        // Handle both wrapped and direct array responses
        if (response.data.success && response.data.data) {
          setCourses(response.data.data)
        } else if (Array.isArray(response.data)) {
          setCourses(response.data)
        } else {
          console.error('Failed to fetch courses:', response.data.message || 'Unknown error')
          setCourses([])
        }
      } catch (error) {
        console.error('Error fetching courses:', error)
        setCourses([])
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()
  }, [searchTerm, selectedCategory])

  // Since we're now fetching filtered data from the API, we can use the courses directly
  const filteredCourses = courses

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
          <h1 className="text-2xl font-bold text-secondary-900">Courses</h1>
          <p className="text-secondary-600 mt-1">
            Discover and enroll in courses to advance your skills
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="btn-primary">
            Create Course
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-field"
            >
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-field"
            >
              {sortOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>

            {/* Filter Button */}
            <button className="btn-outline flex items-center justify-center">
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Course Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCourses.map(course => (
          <div key={course.id} className="card hover:shadow-lg transition-shadow duration-200">
            <div className="relative">
              <img
                src={course.image || 'https://via.placeholder.com/400x200?text=Course+Image'}
                alt={course.title}
                className="w-full h-48 object-cover rounded-t-lg"
              />
              {course.status === 'enrolled' && (
                <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                  Enrolled
                </div>
              )}
              <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full text-xs font-medium text-secondary-700">
                {course.level}
              </div>
            </div>
            
            <div className="card-body">
              <h3 className="font-semibold text-secondary-900 text-lg mb-2">
                {course.title}
              </h3>
              <p className="text-secondary-600 text-sm mb-4 line-clamp-2">
                {course.description}
              </p>
              
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-medium text-sm">
                      {course.instructor.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <span className="ml-2 text-sm text-secondary-600">{course.instructor}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-yellow-500">★</span>
                  <span className="ml-1 text-sm text-secondary-600">{course.rating}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm text-secondary-500 mb-4">
                <span>{course.duration}</span>
                <span>{course.students_enrolled?.toLocaleString() || 0} students</span>
              </div>
              
              {course.status === 'enrolled' && course.progress && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-secondary-600">Progress</span>
                    <span className="text-secondary-900 font-medium">{course.progress}%</span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-secondary-900">
                  ${course.price}
                </span>
                <Link
                  to={`/courses/${course.id}`}
                  className="btn-primary text-sm"
                >
                  {course.status === 'enrolled' ? 'Continue' : 'Enroll'}
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCourses.length === 0 && (
        <div className="text-center py-12">
          <p className="text-secondary-600">No courses found matching your criteria.</p>
        </div>
      )}
    </div>
  )
}

export default Courses 