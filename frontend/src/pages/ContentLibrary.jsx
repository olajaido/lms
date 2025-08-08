import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  DocumentTextIcon,
  VideoCameraIcon,
  PhotoIcon,
  DocumentIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  PlayIcon
} from '@heroicons/react/24/outline'

function ContentLibrary() {
  const { user } = useAuth()
  const [content, setContent] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedCourse, setSelectedCourse] = useState('all')

  useEffect(() => {
    fetchContent()
  }, [])

  const fetchContent = async () => {
    try {
      setLoading(true)
      const response = await api.get('/content')
      setContent(response.data.data || [])
    } catch (error) {
      console.error('Error fetching content:', error)
    } finally {
      setLoading(false)
    }
  }

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'video':
        return <VideoCameraIcon className="h-8 w-8 text-blue-500" />
      case 'image':
        return <PhotoIcon className="h-8 w-8 text-green-500" />
      case 'document':
        return <DocumentTextIcon className="h-8 w-8 text-purple-500" />
      default:
        return <DocumentIcon className="h-8 w-8 text-gray-500" />
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString()
  }

  const filteredContent = content.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === 'all' || item.content_type === selectedType
    const matchesCourse = selectedCourse === 'all' || item.course_id === parseInt(selectedCourse)
    
    return matchesSearch && matchesType && matchesCourse
  })

  const handleContentClick = (contentItem) => {
    // Open content in new tab or modal
    window.open(`/api/content/${contentItem.id}/download`, '_blank')
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">Content Library</h1>
          <p className="text-secondary-600 mt-2">
            Browse and access learning materials, documents, videos, and more
          </p>
        </div>

        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* Content Type Filter */}
            <div>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Types</option>
                <option value="document">Documents</option>
                <option value="video">Videos</option>
                <option value="image">Images</option>
                <option value="audio">Audio</option>
              </select>
            </div>

            {/* Course Filter */}
            <div>
              <select
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Courses</option>
                {/* Course options would be populated from API */}
              </select>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-secondary-600">Loading content library...</p>
          </div>
        ) : filteredContent.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-12 text-center">
            <DocumentTextIcon className="mx-auto h-16 w-16 text-secondary-400 mb-4" />
            <h3 className="text-xl font-medium text-secondary-900 mb-2">No content found</h3>
            <p className="text-secondary-600">
              {searchTerm || selectedType !== 'all' || selectedCourse !== 'all'
                ? 'Try adjusting your search or filters.'
                : 'No content has been uploaded yet.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-lg shadow-sm border border-secondary-200 hover:shadow-md transition-shadow duration-200 cursor-pointer"
                onClick={() => handleContentClick(item)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    {getContentIcon(item.content_type)}
                    <div className="flex items-center space-x-2">
                      {item.content_type === 'video' && (
                        <PlayIcon className="h-5 w-5 text-blue-500" />
                      )}
                      <EyeIcon className="h-5 w-5 text-secondary-400" />
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2 line-clamp-2">
                    {item.title}
                  </h3>
                  
                  <p className="text-secondary-600 text-sm mb-4 line-clamp-3">
                    {item.description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-secondary-500">
                    <span className="capitalize">{item.content_type}</span>
                    <span>{formatFileSize(item.file_size || 0)}</span>
                  </div>
                  
                  <div className="flex items-center justify-between mt-3 text-xs text-secondary-500">
                    <span>{formatDate(item.created_at)}</span>
                    {item.is_public ? (
                      <span className="text-green-600">Public</span>
                    ) : (
                      <span className="text-orange-600">Private</span>
                    )}
                  </div>
                  
                  {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {item.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-secondary-100 text-secondary-700 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                      {item.tags.length > 3 && (
                        <span className="px-2 py-1 text-xs text-secondary-500">
                          +{item.tags.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Summary */}
        {!loading && filteredContent.length > 0 && (
          <div className="mt-8 text-center">
            <p className="text-secondary-600">
              Showing {filteredContent.length} of {content.length} content items
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ContentLibrary 