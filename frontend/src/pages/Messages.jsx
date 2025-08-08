import React from 'react'
import Messaging from '../components/Messaging'
import { useAuth } from '../contexts/AuthContext'

function Messages() {
  const { user } = useAuth()
  
  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                       <div className="mb-8">
                 <h1 className="text-3xl font-bold text-secondary-900">Messages</h1>
                 <p className="text-secondary-600 mt-2">
                   {user?.role === 'admin' 
                     ? 'Communicate with users and provide support'
                     : 'Contact support for help and questions'
                   }
                 </p>
               </div>
        
        <div className="h-96">
          <Messaging />
        </div>
      </div>
    </div>
  )
}

export default Messages 