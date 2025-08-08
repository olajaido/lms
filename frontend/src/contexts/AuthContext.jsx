import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token')
      console.log('Initializing auth with stored token:', storedToken ? 'exists' : 'none')
      
      if (storedToken) {
        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
          console.log('Validating token...')
          const response = await api.get('/users/me')
          console.log('Token validation successful:', response.data)
          setUser(response.data)
          setToken(storedToken)
        } catch (error) {
          console.error('Token validation failed:', error.response?.status, error.response?.data)
          localStorage.removeItem('token')
          delete api.defaults.headers.common['Authorization']
          setToken(null)
          setUser(null)
        }
      } else {
        console.log('No stored token found')
      }
      setLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (email, password) => {
    try {
      console.log('Attempting login...')
      const response = await api.post('/auth/login', { email, password })
      console.log('Login response:', response.data)
      
      const { token, user: userData } = response.data
      
      const accessToken = token.access_token
      console.log('Access token:', accessToken)
      
      localStorage.setItem('token', accessToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      setToken(accessToken)
      setUser(userData)
      
      console.log('Login successful, user set:', userData)
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const register = async (userData) => {
    try {
      console.log('Attempting registration...')
      const response = await api.post('/auth/register', userData)
      console.log('Registration response:', response.data)
      
      const { token, user: userInfo } = response.data
      
      const accessToken = token.access_token
      console.log('Access token:', accessToken)
      
      localStorage.setItem('token', accessToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      setToken(accessToken)
      setUser(userInfo)
      
      console.log('Registration successful, user set:', userInfo)
      return { success: true }
    } catch (error) {
      console.error('Registration error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      setToken(null)
      setUser(null)
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/users/me', profileData)
      setUser(response.data)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Profile update failed' 
      }
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 