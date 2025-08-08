from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from .models import MessageType, MessageStatus, NotificationType, NotificationPriority


class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    message_type: MessageType = MessageType.PRIVATE
    subject: Optional[str] = None
    content: str
    message_metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[MessageStatus] = None
    is_read: Optional[bool] = None
    is_deleted: Optional[bool] = None
    message_metadata: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    id: int
    status: MessageStatus
    is_read: bool
    read_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnouncementBase(BaseModel):
    title: str
    content: str
    author_id: int
    course_id: Optional[int] = None
    announcement_type: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    is_published: bool = True
    is_pinned: bool = False
    expires_at: Optional[datetime] = None
    announcement_metadata: Optional[Dict[str, Any]] = None


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    is_published: Optional[bool] = None
    is_pinned: Optional[bool] = None
    expires_at: Optional[datetime] = None
    announcement_metadata: Optional[Dict[str, Any]] = None


class Announcement(AnnouncementBase):
    id: int
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    user_id: int
    notification_type: NotificationType
    title: str
    content: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    notification_metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    action_url: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    notification_metadata: Optional[Dict[str, Any]] = None


class Notification(NotificationBase):
    id: int
    is_read: bool
    read_at: Optional[datetime] = None
    is_dismissed: bool
    dismissed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None
    conversation_type: MessageType = MessageType.PRIVATE
    is_active: bool = True
    conversation_metadata: Optional[Dict[str, Any]] = None


class ConversationCreate(ConversationBase):
    participant_ids: List[int]


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    conversation_metadata: Optional[Dict[str, Any]] = None


class Conversation(ConversationBase):
    id: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationParticipantBase(BaseModel):
    conversation_id: int
    user_id: int
    role: str = "participant"
    is_active: bool = True


class ConversationParticipantCreate(ConversationParticipantBase):
    pass


class ConversationParticipant(ConversationParticipantBase):
    id: int
    joined_at: datetime
    left_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageTemplateBase(BaseModel):
    name: str
    subject: Optional[str] = None
    content: str
    template_type: str
    is_active: bool = True
    variables: Optional[Dict[str, Any]] = None


class MessageTemplateCreate(MessageTemplateBase):
    pass


class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    template_type: Optional[str] = None
    is_active: Optional[bool] = None
    variables: Optional[Dict[str, Any]] = None


class MessageTemplate(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailLogBase(BaseModel):
    recipient_email: str
    subject: str
    content: str
    template_id: Optional[int] = None
    status: str = "sent"
    error_message: Optional[str] = None
    email_metadata: Optional[Dict[str, Any]] = None


class EmailLogCreate(EmailLogBase):
    pass


class EmailLog(EmailLogBase):
    id: int
    sent_at: datetime

    class Config:
        from_attributes = True


# Response models
class MessageResponse(BaseModel):
    """Response model for message operations"""
    message: Message
    message_text: str
    success: bool = True


class AnnouncementResponse(BaseModel):
    """Response model for announcement operations"""
    announcement: Announcement
    message: str
    success: bool = True


class NotificationResponse(BaseModel):
    """Response model for notification operations"""
    notification: Notification
    message: str
    success: bool = True


class ConversationResponse(BaseModel):
    """Response model for conversation operations"""
    conversation: Conversation
    message: str
    success: bool = True


# Statistics models
class CommunicationStats(BaseModel):
    """Statistics for communication analytics"""
    total_messages: int
    total_announcements: int
    total_notifications: int
    total_conversations: int
    unread_messages: int
    unread_notifications: int


class UserCommunicationStats(BaseModel):
    """Statistics for a specific user"""
    user_id: int
    total_messages_sent: int
    total_messages_received: int
    unread_messages: int
    total_notifications: int
    unread_notifications: int
    total_conversations: int