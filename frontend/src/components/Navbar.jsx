import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Bars3Icon } from '@heroicons/react/24/outline'
import NotificationBell from './NotificationBell'

function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white shadow-sm border-b border-secondary-200">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between">
          <div className="flex">
            <button
              type="button"
              className="lg:hidden -m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-secondary-700"
              onClick={onMenuClick}
            >
              <span className="sr-only">Open sidebar</span>
              <Bars3Icon className="h-6 w-6" aria-hidden="true" />
            </button>
            <div className="flex flex-shrink-0 items-center">
              <h1 className="text-xl font-semibold text-primary-600">LMS Platform</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <NotificationBell />
            
            <div className="flex items-center gap-3">
              <div className="text-sm">
                <p className="font-medium text-secondary-900">{user?.name}</p>
                <p className="text-secondary-500">{user?.email}</p>
              </div>
              
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              
              <button
                onClick={logout}
                className="text-sm text-secondary-500 hover:text-secondary-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar 