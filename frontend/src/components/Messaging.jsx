import React, { useState, useEffect, useRef } from 'react'
import { PaperAirplaneIcon, UserIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

function Messaging() {
  const { user } = useAuth()
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState([])
  const [showNewConversation, setShowNewConversation] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (user) {
      fetchConversations()
      fetchUsers()
    }
  }, [user])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchConversations = async () => {
    if (!user) return
    
    try {
      setLoading(true)
      const response = await api.get(`/conversations/user/${user.id}`)
      const conversationsData = response.data.success ? response.data.data : response.data
      setConversations(conversationsData)
    } catch (error) {
      console.error('Error fetching conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUsers = async () => {
    try {
      if (user.role === 'admin') {
        // Admins can see all users
        let response
        try {
          response = await api.get('/admin/users')
          const usersData = response.data.success ? response.data.data : response.data
          setUsers(usersData.filter(u => u.id !== user.id))
        } catch (error) {
          console.error('Error fetching users for admin:', error)
          setUsers([])
        }
      } else {
        // Regular users can only message admins
        setUsers([
          { id: 4, first_name: 'Admin', last_name: 'Support', email: 'admin@lms.com', role: 'admin' },
          { id: 5, first_name: 'Admin2', last_name: 'Support', email: 'admin2@lms.com', role: 'admin' }
        ])
      }
    } catch (error) {
      console.error('Error fetching users:', error)
      setUsers([])
    }
  }

  const fetchMessages = async (conversationId) => {
    try {
      const response = await api.get(`/conversations/${conversationId}`)
      const conversationData = response.data.success ? response.data.data : response.data
      setSelectedConversation(conversationData)
      
      // Fetch messages between users
      const messagesResponse = await api.get(`/messages/between/${user.id}/${conversationData.participants?.[0]?.user_id || user.id}`)
      const messagesData = messagesResponse.data.success ? messagesResponse.data.data : messagesResponse.data
      setMessages(messagesData)
    } catch (error) {
      console.error('Error fetching messages:', error)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return

    try {
      const messageData = {
        sender_id: user.id,
        receiver_id: selectedConversation.participants?.[0]?.user_id || user.id,
        content: newMessage.trim(),
        message_type: 'private'
      }

      await api.post('/messages', messageData)
      setNewMessage('')
      
      // Refresh messages
      await fetchMessages(selectedConversation.id)
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const startNewConversation = async () => {
    if (!selectedUser) return

    try {
      const conversationData = {
        title: `Chat with ${selectedUser.first_name} ${selectedUser.last_name}`,
        conversation_type: 'private',
        participants: [user.id, selectedUser.id]
      }

      const response = await api.post('/conversations', conversationData)
      const newConversation = response.data.success ? response.data.data : response.data
      
      setConversations(prev => [newConversation, ...prev])
      setSelectedConversation(newConversation)
      setShowNewConversation(false)
      setSelectedUser(null)
    } catch (error) {
      console.error('Error creating conversation:', error)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex h-full bg-white rounded-lg shadow">
      {/* Conversations List */}
      <div className="w-1/3 border-r border-secondary-200">
                       <div className="p-4 border-b border-secondary-200">
                 <div className="flex items-center justify-between">
                   <div>
                     <h2 className="text-lg font-semibold text-secondary-900">Messages</h2>
                     {user.role !== 'admin' && (
                       <p className="text-sm text-secondary-600 mt-1">
                         Contact support for help and questions
                       </p>
                     )}
                   </div>
                   <button
                     onClick={() => setShowNewConversation(true)}
                     className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                   >
                     {user.role === 'admin' ? 'New Chat' : 'Contact Support'}
                   </button>
                 </div>
               </div>

                       {showNewConversation && (
                 <div className="p-4 border-b border-secondary-200">
                   <h3 className="text-sm font-medium text-secondary-900 mb-2">
                     {user.role === 'admin' ? 'Select User' : 'Select Support Contact'}
                   </h3>
                   <select
                     value={selectedUser?.id || ''}
                     onChange={(e) => {
                       const user = users.find(u => u.id === parseInt(e.target.value))
                       setSelectedUser(user)
                     }}
                     className="w-full p-2 border border-secondary-300 rounded-md text-sm"
                   >
                     <option value="">
                       {user.role === 'admin' ? 'Choose a user...' : 'Choose support contact...'}
                     </option>
                     {users.map(user => (
                       <option key={user.id} value={user.id}>
                         {user.first_name} {user.last_name} ({user.email})
                       </option>
                     ))}
                   </select>
                   <div className="flex space-x-2 mt-2">
                     <button
                       onClick={startNewConversation}
                       disabled={!selectedUser}
                       className="btn-primary text-sm px-3 py-1"
                     >
                       {user.role === 'admin' ? 'Start Chat' : 'Contact Support'}
                     </button>
                     <button
                       onClick={() => {
                         setShowNewConversation(false)
                         setSelectedUser(null)
                       }}
                       className="btn-secondary text-sm px-3 py-1"
                     >
                       Cancel
                     </button>
                   </div>
                 </div>
               )}

        <div className="overflow-y-auto h-96">
          {loading ? (
            <div className="p-4 text-sm text-secondary-600">Loading conversations...</div>
                           ) : conversations.length === 0 ? (
                   <div className="p-4 text-sm text-secondary-600">
                     {user.role === 'admin' ? 'No conversations yet' : 'No support conversations yet'}
                   </div>
                 ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => fetchMessages(conversation.id)}
                className={`p-4 cursor-pointer hover:bg-secondary-50 ${
                  selectedConversation?.id === conversation.id ? 'bg-primary-50 border-r-2 border-primary-500' : ''
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <UserIcon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-secondary-900 truncate">
                      {conversation.title}
                    </p>
                    <p className="text-xs text-secondary-500">
                      {conversation.last_message_at ? formatTime(conversation.last_message_at) : 'No messages yet'}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Conversation Header */}
            <div className="p-4 border-b border-secondary-200">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <UserIcon className="h-4 w-4 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-secondary-900">
                    {selectedConversation.title}
                  </h3>
                  <p className="text-xs text-secondary-500">
                    {selectedConversation.participants?.length || 0} participants
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender_id === user.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-secondary-100 text-secondary-900'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.sender_id === user.id ? 'text-primary-200' : 'text-secondary-500'
                    }`}>
                      {formatTime(message.created_at)}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-secondary-200">
              <div className="flex space-x-2">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 p-2 border border-secondary-300 rounded-md text-sm resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  rows="2"
                />
                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim()}
                  className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </>
        ) : (
                           <div className="flex-1 flex items-center justify-center">
                   <div className="text-center">
                     <UserIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
                     <h3 className="text-lg font-medium text-secondary-900 mb-2">
                       {user.role === 'admin' ? 'Select a conversation' : 'Select a support contact'}
                     </h3>
                     <p className="text-sm text-secondary-600">
                       {user.role === 'admin' 
                         ? 'Choose a conversation from the list or start a new chat'
                         : 'Choose a support contact from the list or contact support for help'
                       }
                     </p>
                   </div>
                 </div>
        )}
      </div>
    </div>
  )
}

export default Messaging 