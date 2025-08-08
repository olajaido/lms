"""
Service integration for content service.
Handles communication with other services using shared infrastructure.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from http_client import ServiceClient, service_registry
from event_handler import get_event_client, get_event_handler, EventType, Event
from auth_middleware import ServiceAuthDependency

# Initialize service registry with all services
service_registry.register_service("user", "http://localhost:8001")
service_registry.register_service("course", "http://localhost:8002")
service_registry.register_service("enrollment", "http://localhost:8003")
service_registry.register_service("assessment", "http://localhost:8004")
service_registry.register_service("progress", "http://localhost:8005")
service_registry.register_service("communication", "http://localhost:8006")
service_registry.register_service("content", "http://localhost:8007")
service_registry.register_service("analytics", "http://localhost:8008")


class ContentServiceIntegration:
    """Integration layer for content service with other services."""
    
    def __init__(self):
        self.service_client = ServiceClient("content")
        self.event_client = get_event_client("content")
        self.event_handler = get_event_handler("content")
        self.auth_dependency = ServiceAuthDependency(require_user=True)
    
    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from user service."""
        try:
            user_client = service_registry.get_client("user")
            async with user_client:
                response = await user_client.get(f"/api/v1/users/{user_id}")
                return response.get("data")
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    async def get_course_info(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Get course information from course service."""
        try:
            course_client = service_registry.get_client("course")
            async with course_client:
                response = await course_client.get(f"/api/v1/courses/{course_id}")
                return response.get("data")
        except Exception as e:
            print(f"Error getting course info: {e}")
            return None
    
    async def check_user_enrollment(self, user_id: int, course_id: int) -> bool:
        """Check if user is enrolled in course."""
        try:
            enrollment_client = service_registry.get_client("enrollment")
            async with enrollment_client:
                response = await enrollment_client.get("/api/v1/enrollments", params={
                    "user_id": user_id,
                    "course_id": course_id,
                    "status": "active"
                })
                enrollments = response.get("data", [])
                return len(enrollments) > 0
        except Exception as e:
            print(f"Error checking enrollment: {e}")
            return False
    
    async def update_user_progress(self, user_id: int, course_id: int, progress_data: Dict[str, Any]):
        """Update user progress in progress service."""
        try:
            progress_client = service_registry.get_client("progress")
            async with progress_client:
                await progress_client.post("/api/v1/progress", data={
                    "user_id": user_id,
                    "course_id": course_id,
                    **progress_data
                })
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    async def create_notification(self, notification_data: Dict[str, Any]):
        """Create notification in communication service."""
        try:
            await self.service_client.create_notification(notification_data)
        except Exception as e:
            print(f"Error creating notification: {e}")
    
    async def send_message(self, message_data: Dict[str, Any]):
        """Send message through communication service."""
        try:
            await self.service_client.send_message(message_data)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def publish_content_uploaded_event(self, content_data: Dict[str, Any]):
        """Publish content uploaded event."""
        try:
            await self.event_client.publish_event(
                EventType.COURSE_UPDATED,
                {
                    "content_id": content_data.get("id"),
                    "course_id": content_data.get("course_id"),
                    "title": content_data.get("title"),
                    "content_type": content_data.get("content_type"),
                    "uploaded_by": content_data.get("uploaded_by"),
                    "upload_date": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error publishing content uploaded event: {e}")
    
    async def publish_content_viewed_event(self, content_id: int, user_id: int):
        """Publish content viewed event."""
        try:
            await self.event_client.publish_event(
                EventType.PROGRESS_UPDATED,
                {
                    "content_id": content_id,
                    "user_id": user_id,
                    "action": "view",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error publishing content viewed event: {e}")
    
    async def publish_content_downloaded_event(self, content_id: int, user_id: int):
        """Publish content downloaded event."""
        try:
            await self.event_client.publish_event(
                EventType.PROGRESS_UPDATED,
                {
                    "content_id": content_id,
                    "user_id": user_id,
                    "action": "download",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error publishing content downloaded event: {e}")
    
    async def handle_user_created_event(self, user_data: Dict[str, Any]):
        """Handle user created event."""
        print(f"Content service: User created - {user_data.get('email')}")
        # Could create default content preferences or folders for new user
    
    async def handle_course_created_event(self, course_data: Dict[str, Any]):
        """Handle course created event."""
        print(f"Content service: Course created - {course_data.get('title')}")
        # Could create default content structure for new course
    
    async def handle_enrollment_created_event(self, enrollment_data: Dict[str, Any]):
        """Handle enrollment created event."""
        print(f"Content service: Enrollment created - User {enrollment_data.get('user_id')} enrolled in course {enrollment_data.get('course_id')}")
        # Could grant access to course content
    
    async def handle_progress_completed_event(self, progress_data: Dict[str, Any]):
        """Handle progress completed event."""
        print(f"Content service: Progress completed - User {progress_data.get('user_id')} completed course {progress_data.get('course_id')}")
        # Could unlock additional content or create certificates
    
    def setup_event_handlers(self):
        """Setup event handlers for content service."""
        if self.event_handler:
            self.event_handler.subscribe(EventType.USER_CREATED, self.handle_user_created_event)
            self.event_handler.subscribe(EventType.COURSE_CREATED, self.handle_course_created_event)
            self.event_handler.subscribe(EventType.ENROLLMENT_CREATED, self.handle_enrollment_created_event)
            self.event_handler.subscribe(EventType.PROGRESS_COMPLETED, self.handle_progress_completed_event)
            print("✅ Content service event handlers setup complete")
        else:
            print("⚠️  Event handler not available - skipping event handler setup")


# Global integration instance
content_integration = ContentServiceIntegration()


async def get_content_integration() -> ContentServiceIntegration:
    """Get content service integration instance."""
    return content_integration 