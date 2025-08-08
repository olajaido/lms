import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  PhotoIcon,
  DocumentIcon,
  TrashIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/react/24/outline'

function AdminContent() {
  const { user } = useAuth()
  const [content, setContent] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    content_type: 'document',
    course_id: null,
    tags: '',
    is_public: true
  })

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

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    setSelectedFile(file)
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    if (!selectedFile) {
      alert('Please select a file to upload')
      return
    }

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('title', uploadForm.title)
      formData.append('description', uploadForm.description)
      formData.append('content_type', uploadForm.content_type)
      formData.append('is_public', uploadForm.is_public)
      
      if (uploadForm.course_id) {
        formData.append('course_id', uploadForm.course_id)
      }
      if (uploadForm.tags) {
        formData.append('tags', uploadForm.tags)
      }

      await api.post('/content/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Reset form
      setSelectedFile(null)
      setUploadForm({
        title: '',
        description: '',
        content_type: 'document',
        course_id: null,
        tags: '',
        is_public: true
      })
      
      // Refresh content list
      fetchContent()
      alert('Content uploaded successfully!')
    } catch (error) {
      console.error('Error uploading content:', error)
      alert('Error uploading content. Please try again.')
    } finally {
      setUploading(false)
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
          <h1 className="text-3xl font-bold text-secondary-900">Content Management</h1>
          <p className="text-secondary-600 mt-2">
            Upload and manage learning content for your courses
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Upload New Content</h2>
          
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Content Title
                </label>
                <input
                  type="text"
                  value={uploadForm.title}
                  onChange={(e) => setUploadForm({...uploadForm, title: e.target.value})}
                  className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Content Type
                </label>
                <select
                  value={uploadForm.content_type}
                  onChange={(e) => setUploadForm({...uploadForm, content_type: e.target.value})}
                  className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="document">Document</option>
                  <option value="video">Video</option>
                  <option value="image">Image</option>
                  <option value="audio">Audio</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Description
              </label>
              <textarea
                value={uploadForm.description}
                onChange={(e) => setUploadForm({...uploadForm, description: e.target.value})}
                rows={3}
                className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  value={uploadForm.tags}
                  onChange={(e) => setUploadForm({...uploadForm, tags: e.target.value})}
                  placeholder="e.g., tutorial, beginner, advanced"
                  className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Visibility
                </label>
                <select
                  value={uploadForm.is_public}
                  onChange={(e) => setUploadForm({...uploadForm, is_public: e.target.value === 'true'})}
                  className="w-full p-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value={true}>Public</option>
                  <option value={false}>Private</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Select File
              </label>
              <div className="border-2 border-dashed border-secondary-300 rounded-lg p-6 text-center">
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                  accept=".pdf,.doc,.docx,.txt,.mp4,.avi,.mov,.jpg,.jpeg,.png,.gif,.mp3,.wav"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="text-primary-600 hover:text-primary-800 font-medium">
                    Choose a file
                  </span>
                  <span className="text-secondary-500"> or drag and drop</span>
                </label>
                {selectedFile && (
                  <p className="mt-2 text-sm text-secondary-600">
                    Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={uploading || !selectedFile}
                className="btn-primary flex items-center space-x-2"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <CloudArrowUpIcon className="h-5 w-5" />
                    <span>Upload Content</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Content List */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-xl font-semibold text-secondary-900">Content Library</h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-secondary-600">Loading content...</p>
            </div>
          ) : content.length === 0 ? (
            <div className="p-6 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No content uploaded yet</h3>
              <p className="text-secondary-600">Upload your first piece of content to get started.</p>
            </div>
          ) : (
            <div className="divide-y divide-secondary-200">
              {content.map((item) => (
                <div key={item.id} className="p-6 hover:bg-secondary-50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      {getContentIcon(item.content_type)}
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-secondary-900">{item.title}</h3>
                        <p className="text-secondary-600 mt-1">{item.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-secondary-500">
                          <span>{item.content_type}</span>
                          <span>•</span>
                          <span>{formatFileSize(item.file_size || 0)}</span>
                          <span>•</span>
                          <span>{formatDate(item.created_at)}</span>
                          {item.is_public ? (
                            <>
                              <span>•</span>
                              <span className="text-green-600">Public</span>
                            </>
                          ) : (
                            <>
                              <span>•</span>
                              <span className="text-orange-600">Private</span>
                            </>
                          )}
                        </div>
                        {item.tags && item.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {item.tags.map((tag, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 text-xs bg-secondary-100 text-secondary-700 rounded-full"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => window.open(`/api/content/${item.id}/download`, '_blank')}
                        className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md"
                        title="Download"
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

export default AdminContent 