from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status

from .models import (
    Message, Announcement, Notification, Conversation, ConversationParticipant,
    MessageTemplate, EmailLog, MessageType, MessageStatus, NotificationType,
    NotificationPriority
)
from .schemas import (
    MessageCreate, MessageUpdate, AnnouncementCreate, AnnouncementUpdate,
    NotificationCreate, NotificationUpdate, ConversationCreate, ConversationUpdate,
    ConversationParticipantCreate, MessageTemplateCreate, MessageTemplateUpdate,
    EmailLogCreate
)


# Message CRUD operations
async def create_message(db: AsyncSession, message_create: MessageCreate) -> Message:
    """Create a new message."""
    message = Message(**message_create.dict())
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_message(db: AsyncSession, message_id: int) -> Optional[Message]:
    """Get message by ID."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalar_one_or_none()


async def get_messages_by_user(
    db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0
) -> List[Message]:
    """Get messages for a user (sent and received)."""
    result = await db.execute(
        select(Message)
        .where(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        )
        .where(Message.is_deleted == False)
        .order_by(desc(Message.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_messages_between_users(
    db: AsyncSession, user1_id: int, user2_id: int, limit: int = 50
) -> List[Message]:
    """Get messages between two specific users."""
    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
            )
        )
        .where(Message.is_deleted == False)
        .order_by(Message.created_at)
        .limit(limit)
    )
    return result.scalars().all()


async def update_message(
    db: AsyncSession, message_id: int, message_update: MessageUpdate
) -> Optional[Message]:
    """Update message."""
    message = await get_message(db, message_id)
    if not message:
        return None
    
    update_data = message_update.dict(exclude_unset=True)
    
    # Handle read status
    if 'is_read' in update_data and update_data['is_read'] and not message.is_read:
        update_data['read_at'] = datetime.utcnow()
        update_data['status'] = MessageStatus.READ
    
    # Handle deletion
    if 'is_deleted' in update_data and update_data['is_deleted']:
        update_data['deleted_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(message, field, value)
    
    await db.commit()
    await db.refresh(message)
    return message


async def mark_message_as_read(db: AsyncSession, message_id: int, user_id: int) -> Optional[Message]:
    """Mark a message as read by the receiver."""
    message = await get_message(db, message_id)
    if not message or message.receiver_id != user_id:
        return None
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    message.status = MessageStatus.READ
    
    await db.commit()
    await db.refresh(message)
    return message


# Announcement CRUD operations
async def create_announcement(
    db: AsyncSession, announcement_create: AnnouncementCreate
) -> Announcement:
    """Create a new announcement."""
    announcement = Announcement(**announcement_create.dict())
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return announcement


async def get_announcement(db: AsyncSession, announcement_id: int) -> Optional[Announcement]:
    """Get announcement by ID."""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    return result.scalar_one_or_none()


async def get_announcements_by_course(
    db: AsyncSession, course_id: int, limit: int = 50, offset: int = 0
) -> List[Announcement]:
    """Get announcements for a specific course."""
    result = await db.execute(
        select(Announcement)
        .where(Announcement.course_id == course_id)
        .where(Announcement.is_published == True)
        .order_by(desc(Announcement.is_pinned), desc(Announcement.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_system_announcements(
    db: AsyncSession, limit: int = 50, offset: int = 0
) -> List[Announcement]:
    """Get system-wide announcements."""
    result = await db.execute(
        select(Announcement)
        .where(Announcement.course_id == None)
        .where(Announcement.is_published == True)
        .order_by(desc(Announcement.is_pinned), desc(Announcement.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_announcement(
    db: AsyncSession, announcement_id: int, announcement_update: AnnouncementUpdate
) -> Optional[Announcement]:
    """Update announcement."""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        return None
    
    update_data = announcement_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    announcement.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(announcement)
    return announcement


async def increment_announcement_views(db: AsyncSession, announcement_id: int) -> bool:
    """Increment the view count for an announcement."""
    announcement = await get_announcement(db, announcement_id)
    if not announcement:
        return False
    
    announcement.view_count += 1
    await db.commit()
    return True


# Notification CRUD operations
async def create_notification(
    db: AsyncSession, notification_create: NotificationCreate
) -> Notification:
    """Create a new notification."""
    notification = Notification(**notification_create.dict())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_notification(db: AsyncSession, notification_id: int) -> Optional[Notification]:
    """Get notification by ID."""
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    return result.scalar_one_or_none()


async def get_notifications_by_user(
    db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0
) -> List[Notification]:
    """Get notifications for a user."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .where(Notification.is_dismissed == False)
        .order_by(desc(Notification.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_unread_notifications_by_user(
    db: AsyncSession, user_id: int, limit: int = 50
) -> List[Notification]:
    """Get unread notifications for a user."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .where(Notification.is_read == False)
        .where(Notification.is_dismissed == False)
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    return result.scalars().all()


async def mark_notification_as_read(
    db: AsyncSession, notification_id: int, user_id: int
) -> Optional[Notification]:
    """Mark a notification as read."""
    notification = await get_notification(db, notification_id)
    if not notification or notification.user_id != user_id:
        return None
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(notification)
    return notification


async def dismiss_notification(
    db: AsyncSession, notification_id: int, user_id: int
) -> Optional[Notification]:
    """Dismiss a notification."""
    notification = await get_notification(db, notification_id)
    if not notification or notification.user_id != user_id:
        return None
    
    notification.is_dismissed = True
    notification.dismissed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(notification)
    return notification


# Conversation CRUD operations
async def create_conversation(
    db: AsyncSession, conversation_create: ConversationCreate
) -> Conversation:
    """Create a new conversation with participants."""
    conversation = Conversation(
        title=conversation_create.title,
        conversation_type=conversation_create.conversation_type,
        is_active=conversation_create.is_active,
        metadata=conversation_create.metadata
    )
    db.add(conversation)
    await db.flush()  # Get the ID
    
    # Add participants
    for user_id in conversation_create.participant_ids:
        participant = ConversationParticipant(
            conversation_id=conversation.id,
            user_id=user_id
        )
        db.add(participant)
    
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation(db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
    """Get conversation by ID."""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    return result.scalar_one_or_none()


async def get_conversations_by_user(
    db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0
) -> List[Conversation]:
    """Get conversations for a user."""
    result = await db.execute(
        select(Conversation)
        .join(ConversationParticipant)
        .where(ConversationParticipant.user_id == user_id)
        .where(ConversationParticipant.is_active == True)
        .where(Conversation.is_active == True)
        .order_by(desc(Conversation.last_message_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_conversation(
    db: AsyncSession, conversation_id: int, conversation_update: ConversationUpdate
) -> Optional[Conversation]:
    """Update conversation."""
    conversation = await get_conversation(db, conversation_id)
    if not conversation:
        return None
    
    update_data = conversation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)
    
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conversation)
    return conversation


# Message Template CRUD operations
async def create_message_template(
    db: AsyncSession, template_create: MessageTemplateCreate
) -> MessageTemplate:
    """Create a new message template."""
    template = MessageTemplate(**template_create.dict())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_message_template(db: AsyncSession, template_id: int) -> Optional[MessageTemplate]:
    """Get message template by ID."""
    result = await db.execute(select(MessageTemplate).where(MessageTemplate.id == template_id))
    return result.scalar_one_or_none()


async def get_message_templates(
    db: AsyncSession, template_type: Optional[str] = None, active_only: bool = True
) -> List[MessageTemplate]:
    """Get message templates."""
    query = select(MessageTemplate)
    if template_type:
        query = query.where(MessageTemplate.template_type == template_type)
    if active_only:
        query = query.where(MessageTemplate.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


# Email Log CRUD operations
async def create_email_log(db: AsyncSession, email_log_create: EmailLogCreate) -> EmailLog:
    """Create a new email log."""
    email_log = EmailLog(**email_log_create.dict())
    db.add(email_log)
    await db.commit()
    await db.refresh(email_log)
    return email_log


async def get_email_logs(
    db: AsyncSession, status: Optional[str] = None, limit: int = 50
) -> List[EmailLog]:
    """Get email logs."""
    query = select(EmailLog)
    if status:
        query = query.where(EmailLog.status == status)
    query = query.order_by(desc(EmailLog.sent_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Statistics and Analytics
async def get_communication_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get overall communication statistics."""
    # Count messages
    result = await db.execute(select(func.count(Message.id)))
    total_messages = result.scalar()
    
    # Count unread messages
    result = await db.execute(select(func.count(Message.id)).where(Message.is_read == False))
    unread_messages = result.scalar()
    
    # Count announcements
    result = await db.execute(select(func.count(Announcement.id)))
    total_announcements = result.scalar()
    
    # Count notifications
    result = await db.execute(select(func.count(Notification.id)))
    total_notifications = result.scalar()
    
    # Count unread notifications
    result = await db.execute(
        select(func.count(Notification.id))
        .where(and_(Notification.is_read == False, Notification.is_dismissed == False))
    )
    unread_notifications = result.scalar()
    
    # Count conversations
    result = await db.execute(select(func.count(Conversation.id)))
    total_conversations = result.scalar()
    
    return {
        "total_messages": total_messages,
        "total_announcements": total_announcements,
        "total_notifications": total_notifications,
        "total_conversations": total_conversations,
        "unread_messages": unread_messages,
        "unread_notifications": unread_notifications
    }


async def get_user_communication_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get communication statistics for a specific user."""
    # Count messages sent
    result = await db.execute(
        select(func.count(Message.id)).where(Message.sender_id == user_id)
    )
    total_messages_sent = result.scalar()
    
    # Count messages received
    result = await db.execute(
        select(func.count(Message.id)).where(Message.receiver_id == user_id)
    )
    total_messages_received = result.scalar()
    
    # Count unread messages
    result = await db.execute(
        select(func.count(Message.id))
        .where(and_(Message.receiver_id == user_id, Message.is_read == False))
    )
    unread_messages = result.scalar()
    
    # Count notifications
    result = await db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == user_id)
    )
    total_notifications = result.scalar()
    
    # Count unread notifications
    result = await db.execute(
        select(func.count(Notification.id))
        .where(and_(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_dismissed == False
        ))
    )
    unread_notifications = result.scalar()
    
    # Count conversations
    result = await db.execute(
        select(func.count(Conversation.id))
        .join(ConversationParticipant)
        .where(ConversationParticipant.user_id == user_id)
    )
    total_conversations = result.scalar()
    
    return {
        "user_id": user_id,
        "total_messages_sent": total_messages_sent,
        "total_messages_received": total_messages_received,
        "unread_messages": unread_messages,
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "total_conversations": total_conversations
    }