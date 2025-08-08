from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db

app = FastAPI(title="Communication Service", version="1.0.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Message endpoints
@app.post("/api/v1/messages", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_create: schemas.MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.MessageResponse:
    """Create a new message."""
    message = await crud.create_message(db, message_create)
    return schemas.MessageResponse(
        message=schemas.Message.from_orm(message),
        message_text="Message sent successfully"
    )


@app.get("/api/v1/messages/{message_id}", response_model=schemas.Message)
async def get_message(
    message_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Message:
    """Get message by ID."""
    message = await crud.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return schemas.Message.from_orm(message)


@app.get("/api/v1/messages/user/{user_id}", response_model=List[schemas.Message])
async def get_messages_by_user(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Message]:
    """Get messages for a user (sent and received)."""
    messages = await crud.get_messages_by_user(db, user_id, limit, offset)
    return [schemas.Message.from_orm(m) for m in messages]


@app.get("/api/v1/messages/between/{user1_id}/{user2_id}", response_model=List[schemas.Message])
async def get_messages_between_users(
    user1_id: int,
    user2_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Message]:
    """Get messages between two specific users."""
    messages = await crud.get_messages_between_users(db, user1_id, user2_id, limit)
    return [schemas.Message.from_orm(m) for m in messages]


@app.put("/api/v1/messages/{message_id}", response_model=schemas.MessageResponse)
async def update_message(
    message_id: int,
    message_update: schemas.MessageUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.MessageResponse:
    """Update message."""
    message = await crud.update_message(db, message_id, message_update)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return schemas.MessageResponse(
        message=schemas.Message.from_orm(message),
        message_text="Message updated successfully"
    )


@app.patch("/api/v1/messages/{message_id}/read", response_model=schemas.MessageResponse)
async def mark_message_as_read(
    message_id: int,
    user_id: int = Query(..., description="User ID marking the message as read"),
    db: AsyncSession = Depends(get_db),
) -> schemas.MessageResponse:
    """Mark a message as read."""
    message = await crud.mark_message_as_read(db, message_id, user_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or user not authorized")
    return schemas.MessageResponse(
        message=schemas.Message.from_orm(message),
        message_text="Message marked as read"
    )


# Announcement endpoints
@app.post("/api/v1/announcements", response_model=schemas.AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_create: schemas.AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AnnouncementResponse:
    """Create a new announcement."""
    announcement = await crud.create_announcement(db, announcement_create)
    return schemas.AnnouncementResponse(
        announcement=schemas.Announcement.from_orm(announcement),
        message="Announcement created successfully"
    )


@app.get("/api/v1/announcements/{announcement_id}", response_model=schemas.Announcement)
async def get_announcement(
    announcement_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Announcement:
    """Get announcement by ID."""
    announcement = await crud.get_announcement(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Increment view count
    await crud.increment_announcement_views(db, announcement_id)
    return schemas.Announcement.from_orm(announcement)


@app.get("/api/v1/announcements/course/{course_id}", response_model=List[schemas.Announcement])
async def get_announcements_by_course(
    course_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Announcement]:
    """Get announcements for a specific course."""
    announcements = await crud.get_announcements_by_course(db, course_id, limit, offset)
    return [schemas.Announcement.from_orm(a) for a in announcements]


@app.get("/api/v1/announcements/system", response_model=List[schemas.Announcement])
async def get_system_announcements(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Announcement]:
    """Get system-wide announcements."""
    announcements = await crud.get_system_announcements(db, limit, offset)
    return [schemas.Announcement.from_orm(a) for a in announcements]


@app.put("/api/v1/announcements/{announcement_id}", response_model=schemas.AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    announcement_update: schemas.AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AnnouncementResponse:
    """Update announcement."""
    announcement = await crud.update_announcement(db, announcement_id, announcement_update)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return schemas.AnnouncementResponse(
        announcement=schemas.Announcement.from_orm(announcement),
        message="Announcement updated successfully"
    )


# Notification endpoints
@app.post("/api/v1/notifications", response_model=schemas.NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_create: schemas.NotificationCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.NotificationResponse:
    """Create a new notification."""
    notification = await crud.create_notification(db, notification_create)
    return schemas.NotificationResponse(
        notification=schemas.Notification.from_orm(notification),
        message="Notification created successfully"
    )


@app.get("/api/v1/notifications/{notification_id}", response_model=schemas.Notification)
async def get_notification(
    notification_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Notification:
    """Get notification by ID."""
    notification = await crud.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return schemas.Notification.from_orm(notification)


@app.get("/api/v1/notifications/user/{user_id}", response_model=List[schemas.Notification])
async def get_notifications_by_user(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Notification]:
    """Get notifications for a user."""
    notifications = await crud.get_notifications_by_user(db, user_id, limit, offset)
    return [schemas.Notification.from_orm(n) for n in notifications]


@app.get("/api/v1/notifications/user/{user_id}/unread", response_model=List[schemas.Notification])
async def get_unread_notifications_by_user(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Notification]:
    """Get unread notifications for a user."""
    notifications = await crud.get_unread_notifications_by_user(db, user_id, limit)
    return [schemas.Notification.from_orm(n) for n in notifications]


@app.patch("/api/v1/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    user_id: int = Query(..., description="User ID marking the notification as read"),
    db: AsyncSession = Depends(get_db),
) -> schemas.NotificationResponse:
    """Mark a notification as read."""
    notification = await crud.mark_notification_as_read(db, notification_id, user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found or user not authorized")
    return schemas.NotificationResponse(
        notification=schemas.Notification.from_orm(notification),
        message="Notification marked as read"
    )


@app.patch("/api/v1/notifications/{notification_id}/dismiss", response_model=schemas.NotificationResponse)
async def dismiss_notification(
    notification_id: int,
    user_id: int = Query(..., description="User ID dismissing the notification"),
    db: AsyncSession = Depends(get_db),
) -> schemas.NotificationResponse:
    """Dismiss a notification."""
    notification = await crud.dismiss_notification(db, notification_id, user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found or user not authorized")
    return schemas.NotificationResponse(
        notification=schemas.Notification.from_orm(notification),
        message="Notification dismissed"
    )


# Conversation endpoints
@app.post("/api/v1/conversations", response_model=schemas.ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_create: schemas.ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ConversationResponse:
    """Create a new conversation."""
    conversation = await crud.create_conversation(db, conversation_create)
    return schemas.ConversationResponse(
        conversation=schemas.Conversation.from_orm(conversation),
        message="Conversation created successfully"
    )


@app.get("/api/v1/conversations/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Conversation:
    """Get conversation by ID."""
    conversation = await crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return schemas.Conversation.from_orm(conversation)


@app.get("/api/v1/conversations/user/{user_id}", response_model=List[schemas.Conversation])
async def get_conversations_by_user(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Conversation]:
    """Get conversations for a user."""
    conversations = await crud.get_conversations_by_user(db, user_id, limit, offset)
    return [schemas.Conversation.from_orm(c) for c in conversations]


@app.put("/api/v1/conversations/{conversation_id}", response_model=schemas.ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ConversationResponse:
    """Update conversation."""
    conversation = await crud.update_conversation(db, conversation_id, conversation_update)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return schemas.ConversationResponse(
        conversation=schemas.Conversation.from_orm(conversation),
        message="Conversation updated successfully"
    )


# Message Template endpoints
@app.post("/api/v1/templates", response_model=schemas.MessageTemplate, status_code=status.HTTP_201_CREATED)
async def create_message_template(
    template_create: schemas.MessageTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.MessageTemplate:
    """Create a new message template."""
    template = await crud.create_message_template(db, template_create)
    return schemas.MessageTemplate.from_orm(template)


@app.get("/api/v1/templates/{template_id}", response_model=schemas.MessageTemplate)
async def get_message_template(
    template_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.MessageTemplate:
    """Get message template by ID."""
    template = await crud.get_message_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Message template not found")
    return schemas.MessageTemplate.from_orm(template)


@app.get("/api/v1/templates", response_model=List[schemas.MessageTemplate])
async def get_message_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    active_only: bool = Query(True, description="Filter only active templates"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.MessageTemplate]:
    """Get message templates."""
    templates = await crud.get_message_templates(db, template_type, active_only)
    return [schemas.MessageTemplate.from_orm(t) for t in templates]


# Statistics endpoints
@app.get("/api/v1/stats/overall", response_model=schemas.CommunicationStats)
async def get_communication_stats(
    db: AsyncSession = Depends(get_db)
) -> schemas.CommunicationStats:
    """Get overall communication statistics."""
    stats = await crud.get_communication_stats(db)
    return schemas.CommunicationStats(**stats)


@app.get("/api/v1/stats/user/{user_id}", response_model=schemas.UserCommunicationStats)
async def get_user_communication_stats(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.UserCommunicationStats:
    """Get communication statistics for a specific user."""
    stats = await crud.get_user_communication_stats(db, user_id)
    return schemas.UserCommunicationStats(**stats)