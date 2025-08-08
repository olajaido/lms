import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { UserIcon, EnvelopeIcon, PhoneIcon, CalendarIcon } from '@heroicons/react/24/outline'

function Profile() {
  const { user, updateProfile } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone_number || '',
    bio: user?.bio || '',
    dateOfBirth: user?.date_of_birth ? new Date(user.date_of_birth).toISOString().split('T')[0] : '',
    profilePicture: user?.profile_picture || ''
  })

  const handleChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    const result = await updateProfile(profileData)
    
    if (result.success) {
      setMessage('Profile updated successfully!')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'security', name: 'Security', icon: UserIcon },
    { id: 'notifications', name: 'Notifications', icon: UserIcon },
    { id: 'preferences', name: 'Preferences', icon: UserIcon }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Profile Settings</h1>
        <p className="text-secondary-600 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-body">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-900'
                        : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                    }`}
                  >
                    <tab.icon className="mr-3 h-5 w-5" />
                    {tab.name}
                  </button>
                ))}
              </nav>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {activeTab === 'profile' && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-secondary-900">Profile Information</h2>
              </div>
              <div className="card-body">
                {message && (
                  <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
                    <p className="text-sm text-green-600">{message}</p>
                  </div>
                )}
                
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Profile Picture */}
                  <div className="flex items-center space-x-6">
                    <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                      {profileData.profilePicture ? (
                        <img
                          src={profileData.profilePicture}
                          alt="Profile"
                          className="w-20 h-20 rounded-full object-cover"
                        />
                      ) : (
                        <UserIcon className="h-10 w-10 text-primary-600" />
                      )}
                    </div>
                    <div>
                      <button type="button" className="btn-outline">
                        Change Photo
                      </button>
                      <p className="text-sm text-secondary-600 mt-1">
                        JPG, GIF or PNG. Max size 2MB.
                      </p>
                    </div>
                  </div>

                  {/* Name */}
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-secondary-700">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={profileData.name}
                      onChange={handleChange}
                      className="input-field mt-1"
                      placeholder="Enter your full name"
                    />
                  </div>

                  {/* Email */}
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-secondary-700">
                      Email Address
                    </label>
                    <div className="relative mt-1">
                      <EnvelopeIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={profileData.email}
                        onChange={handleChange}
                        className="input-field pl-10"
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>

                  {/* Phone */}
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-secondary-700">
                      Phone Number
                    </label>
                    <div className="relative mt-1">
                      <PhoneIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={profileData.phone}
                        onChange={handleChange}
                        className="input-field pl-10"
                        placeholder="Enter your phone number"
                      />
                    </div>
                  </div>

                  {/* Date of Birth */}
                  <div>
                    <label htmlFor="dateOfBirth" className="block text-sm font-medium text-secondary-700">
                      Date of Birth
                    </label>
                    <div className="relative mt-1">
                      <CalendarIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
                      <input
                        type="date"
                        id="dateOfBirth"
                        name="dateOfBirth"
                        value={profileData.dateOfBirth}
                        onChange={handleChange}
                        className="input-field pl-10"
                      />
                    </div>
                  </div>

                  {/* Bio */}
                  <div>
                    <label htmlFor="bio" className="block text-sm font-medium text-secondary-700">
                      Bio
                    </label>
                    <textarea
                      id="bio"
                      name="bio"
                      rows={4}
                      value={profileData.bio}
                      onChange={handleChange}
                      className="input-field mt-1"
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={loading}
                      className="btn-primary"
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-secondary-900">Security Settings</h2>
              </div>
              <div className="card-body">
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-secondary-900 mb-4">Change Password</h3>
                    <button className="btn-outline">
                      Update Password
                    </button>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-secondary-900 mb-4">Two-Factor Authentication</h3>
                    <button className="btn-outline">
                      Enable 2FA
                    </button>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-secondary-900 mb-4">Active Sessions</h3>
                    <button className="btn-outline">
                      View All Sessions
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-secondary-900">Notification Preferences</h2>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-secondary-900">Email Notifications</h3>
                      <p className="text-sm text-secondary-600">Receive email updates about your courses</p>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-secondary-900">Push Notifications</h3>
                      <p className="text-sm text-secondary-600">Receive push notifications in your browser</p>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-primary-600" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-secondary-900">Course Updates</h3>
                      <p className="text-sm text-secondary-600">Get notified when courses are updated</p>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-secondary-900">Account Preferences</h2>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Language
                    </label>
                    <select className="input-field">
                      <option>English</option>
                      <option>Spanish</option>
                      <option>French</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Time Zone
                    </label>
                    <select className="input-field">
                      <option>UTC-8 (Pacific Time)</option>
                      <option>UTC-5 (Eastern Time)</option>
                      <option>UTC+0 (GMT)</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-secondary-900">Public Profile</h3>
                      <p className="text-sm text-secondary-600">Allow others to see your profile</p>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-primary-600" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile 