from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum

Base = declarative_base()


class MessageType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class NotificationType(str, Enum):
    COURSE_ANNOUNCEMENT = "course_announcement"
    ASSESSMENT_DUE = "assessment_due"
    GRADE_AVAILABLE = "grade_available"
    COURSE_COMPLETED = "course_completed"
    CERTIFICATE_EARNED = "certificate_earned"
    SYSTEM_UPDATE = "system_update"
    MESSAGE_RECEIVED = "message_received"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Message(Base):
    """Represents a message between users."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False, index=True)
    receiver_id = Column(Integer, nullable=False, index=True)
    message_type = Column(String, default=MessageType.PRIVATE, nullable=False)
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    status = Column(String, default=MessageStatus.SENT, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    message_metadata = Column(JSON, nullable=True)  # Additional message data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Announcement(Base):
    """Represents course announcements and system-wide announcements."""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=True, index=True)  # Null for system-wide announcements
    announcement_type = Column(String, nullable=False)  # course, system, general
    priority = Column(String, default=NotificationPriority.NORMAL, nullable=False)
    is_published = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)
    announcement_metadata = Column(JSON, nullable=True)  # Additional announcement data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """Represents user notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String, default=NotificationPriority.NORMAL, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    is_dismissed = Column(Boolean, default=False)
    dismissed_at = Column(DateTime, nullable=True)
    action_url = Column(String, nullable=True)  # URL to navigate to when clicked
    action_data = Column(JSON, nullable=True)  # Additional action data
    notification_metadata = Column(JSON, nullable=True)  # Additional notification data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Represents a conversation between users."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)  # For group conversations
    conversation_type = Column(String, default=MessageType.PRIVATE, nullable=False)
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, nullable=True)
    conversation_metadata = Column(JSON, nullable=True)  # Additional conversation data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationParticipant(Base):
    """Represents participants in a conversation."""
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String, default="participant")  # participant, admin, moderator
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class MessageTemplate(Base):
    """Represents reusable message templates."""
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    template_type = Column(String, nullable=False)  # email, sms, notification
    is_active = Column(Boolean, default=True)
    variables = Column(JSON, nullable=True)  # Template variables
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailLog(Base):
    """Represents email sending logs."""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=True)
    status = Column(String, default="sent")  # sent, failed, pending
    sent_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    email_metadata = Column(JSON, nullable=True)  # Additional email data