"""
Event handling for service-to-service communication.
Provides event publishing and subscription for microservice events.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for service communication."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    COURSE_CREATED = "course.created"
    COURSE_UPDATED = "course.updated"
    COURSE_DELETED = "course.deleted"
    ENROLLMENT_CREATED = "enrollment.created"
    ENROLLMENT_UPDATED = "enrollment.updated"
    ENROLLMENT_COMPLETED = "enrollment.completed"
    ASSESSMENT_CREATED = "assessment.created"
    ASSESSMENT_SUBMITTED = "assessment.submitted"
    ASSESSMENT_GRADED = "assessment.graded"
    PROGRESS_UPDATED = "progress.updated"
    PROGRESS_COMPLETED = "progress.completed"
    NOTIFICATION_CREATED = "notification.created"
    MESSAGE_SENT = "message.sent"


class Event:
    """Event model for service communication."""
    
    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source_service: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.data = data
        self.source_service = source_service
        self.event_id = event_id or f"{source_service}_{event_type}_{datetime.utcnow().timestamp()}"
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "source_service": self.source_service,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, event_dict: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_type=EventType(event_dict["event_type"]),
            data=event_dict["data"],
            source_service=event_dict["source_service"],
            event_id=event_dict["event_id"],
            timestamp=datetime.fromisoformat(event_dict["timestamp"])
        )


class EventHandler:
    """Event handler for service-to-service communication."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type} in {self.service_name}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            logger.info(f"Unsubscribed from {event_type} in {self.service_name}")
    
    async def publish(self, event: Event):
        """Publish an event to subscribers."""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {event.event_type}: {e}")
        
        logger.info(f"Published event {event.event_type} from {self.service_name}")
    
    async def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ):
        """Publish an event with the given type and data."""
        event = Event(
            event_type=event_type,
            data=data,
            source_service=self.service_name,
            event_id=event_id
        )
        await self.publish(event)
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history, optionally filtered by event type."""
        if event_type:
            return [event for event in self.event_history if event.event_type == event_type]
        return self.event_history.copy()


class ServiceEventClient:
    """Client for sending events to other services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.event_handler = EventHandler(service_name)
    
    async def send_event_to_service(
        self,
        target_service: str,
        event: Event,
        service_registry
    ):
        """Send event to a specific service."""
        try:
            client = service_registry.get_client(target_service)
            async with client:
                await client.post("/api/v1/events", data=event.to_dict())
        except Exception as e:
            logger.error(f"Failed to send event to {target_service}: {e}")
    
    async def broadcast_event(self, event: Event, service_registry, target_services: List[str]):
        """Broadcast event to multiple services."""
        tasks = []
        for service in target_services:
            if service != self.service_name:
                task = self.send_event_to_service(service, event, service_registry)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convenience methods for common events
    async def user_created(self, user_data: Dict[str, Any]):
        """Publish user created event."""
        await self.event_handler.publish_event(EventType.USER_CREATED, user_data)
    
    async def user_updated(self, user_data: Dict[str, Any]):
        """Publish user updated event."""
        await self.event_handler.publish_event(EventType.USER_UPDATED, user_data)
    
    async def course_created(self, course_data: Dict[str, Any]):
        """Publish course created event."""
        await self.event_handler.publish_event(EventType.COURSE_CREATED, course_data)
    
    async def enrollment_created(self, enrollment_data: Dict[str, Any]):
        """Publish enrollment created event."""
        await self.event_handler.publish_event(EventType.ENROLLMENT_CREATED, enrollment_data)
    
    async def enrollment_completed(self, enrollment_data: Dict[str, Any]):
        """Publish enrollment completed event."""
        await self.event_handler.publish_event(EventType.ENROLLMENT_COMPLETED, enrollment_data)
    
    async def assessment_submitted(self, assessment_data: Dict[str, Any]):
        """Publish assessment submitted event."""
        await self.event_handler.publish_event(EventType.ASSESSMENT_SUBMITTED, assessment_data)
    
    async def progress_updated(self, progress_data: Dict[str, Any]):
        """Publish progress updated event."""
        await self.event_handler.publish_event(EventType.PROGRESS_UPDATED, progress_data)
    
    async def progress_completed(self, progress_data: Dict[str, Any]):
        """Publish progress completed event."""
        await self.event_handler.publish_event(EventType.PROGRESS_COMPLETED, progress_data)
    
    async def notification_created(self, notification_data: Dict[str, Any]):
        """Publish notification created event."""
        await self.event_handler.publish_event(EventType.NOTIFICATION_CREATED, notification_data)


# Global event handlers for each service
event_handlers = {
    "user": EventHandler("user"),
    "course": EventHandler("course"),
    "enrollment": EventHandler("enrollment"),
    "assessment": EventHandler("assessment"),
    "progress": EventHandler("progress"),
    "communication": EventHandler("communication")
}


def get_event_handler(service_name: str) -> EventHandler:
    """Get event handler for a service."""
    return event_handlers.get(service_name)


def get_event_client(service_name: str) -> ServiceEventClient:
    """Get event client for a service."""
    return ServiceEventClient(service_name) 