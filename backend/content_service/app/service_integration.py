"""
Service integration for content service.
Handles communication with other services using shared infrastructure.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Initialize variables
SHARED_MODULES_AVAILABLE = False
ServiceClient = None
service_registry = None
get_event_client = None
get_event_handler = None
EventType = None
Event = None
ServiceAuthDependency = None

# Try to find and import shared modules
try:
    # Try multiple paths for shared modules
    shared_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'shared'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'shared'),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'),
        '/app/shared',  # For container environment
        os.path.join(os.getcwd(), 'shared'),  # Current working directory
        os.path.join(os.getcwd(), '..', 'shared'),  # Parent of current working directory
    ]

    shared_modules_loaded = False
    for shared_path in shared_paths:
        if os.path.exists(shared_path) and os.path.exists(os.path.join(shared_path, 'http_client.py')):
            if shared_path not in sys.path:
                sys.path.insert(0, shared_path)
            print(f"✅ Found shared modules at: {shared_path}")
            shared_modules_loaded = True
            break

    if shared_modules_loaded:
        from http_client import ServiceClient, service_registry
        from event_handler import get_event_client, get_event_handler, EventType, Event
        from auth_middleware import ServiceAuthDependency
        SHARED_MODULES_AVAILABLE = True
        print("✅ Shared modules loaded successfully")
    else:
        raise ImportError("Shared modules not found")

except ImportError as e:
    print(f"⚠️  Shared modules not available - running in standalone mode: {e}")
    SHARED_MODULES_AVAILABLE = False
    
    # Create dummy classes for when shared modules are not available
    class ServiceClient:
        def __init__(self, service_name):
            self.service_name = service_name
        async def create_notification(self, data):
            print(f"Notification creation not available: {data}")
        async def send_message(self, data):
            print(f"Message sending not available: {data}")
    
    class service_registry:
        @staticmethod
        def register_service(name, url):
            print(f"Service registration not available: {name} -> {url}")
        @staticmethod
        def get_client(name):
            return None
        @staticmethod
        def get_service_url(name):
            return f"http://{name}-service:8000"
    
    def get_event_client(service_name):
        return None
    
    def get_event_handler(service_name):
        return None
    
    class EventType:
        COURSE_UPDATED = "course_updated"
        PROGRESS_UPDATED = "progress_updated"
        USER_CREATED = "user_created"
        COURSE_CREATED = "course_created"
        ENROLLMENT_CREATED = "enrollment_created"
        PROGRESS_COMPLETED = "progress_completed"
    
    class Event:
        pass
    
    class ServiceAuthDependency:
        def __init__(self, require_user=True):
            self.require_user = require_user

# Initialize service registry with all services
if service_registry:
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
        if SHARED_MODULES_AVAILABLE:
            self.service_client = ServiceClient("content")
            self.event_client = get_event_client("content") if get_event_client else None
            self.event_handler = get_event_handler("content") if get_event_handler else None
            self.auth_dependency = ServiceAuthDependency(require_user=True) if ServiceAuthDependency else None
        else:
            self.service_client = ServiceClient("content")
            self.event_client = None
            self.event_handler = None
            self.auth_dependency = ServiceAuthDependency(require_user=True) if ServiceAuthDependency else None
    
    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from user service."""
        if not SHARED_MODULES_AVAILABLE:
            print(f"User info not available - shared modules not loaded")
            return None
        try:
            user_client = service_registry.get_client("user")
            if user_client:
                async with user_client:
                    response = await user_client.get(f"/api/v1/users/{user_id}")
                    return response.get("data")
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    async def get_course_info(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Get course information from course service."""
        if not SHARED_MODULES_AVAILABLE:
            print(f"Course info not available - shared modules not loaded")
            return None
        try:
            course_client = service_registry.get_client("course")
            if course_client:
                async with course_client:
                    response = await course_client.get(f"/api/v1/courses/{course_id}")
                    return response.get("data")
            return None
        except Exception as e:
            print(f"Error getting course info: {e}")
            return None
    
    async def check_user_enrollment(self, user_id: int, course_id: int) -> bool:
        """Check if user is enrolled in course."""
        if not SHARED_MODULES_AVAILABLE:
            print(f"Enrollment check not available - shared modules not loaded")
            return False
        try:
            enrollment_client = service_registry.get_client("enrollment")
            if enrollment_client:
                async with enrollment_client:
                    response = await enrollment_client.get("/api/v1/enrollments", params={
                        "user_id": user_id,
                        "course_id": course_id,
                        "status": "active"
                    })
                    enrollments = response.get("data", [])
                    return len(enrollments) > 0
            return False
        except Exception as e:
            print(f"Error checking enrollment: {e}")
            return False
    
    async def update_user_progress(self, user_id: int, course_id: int, progress_data: Dict[str, Any]):
        """Update user progress in progress service."""
        if not SHARED_MODULES_AVAILABLE:
            print(f"Progress update not available - shared modules not loaded")
            return
        try:
            progress_client = service_registry.get_client("progress")
            if progress_client:
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
        if not SHARED_MODULES_AVAILABLE or not self.event_client:
            print(f"Event publishing not available - shared modules not loaded")
            return
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
        if not SHARED_MODULES_AVAILABLE or not self.event_client:
            print(f"Event publishing not available - shared modules not loaded")
            return
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
        if not SHARED_MODULES_AVAILABLE or not self.event_client:
            print(f"Event publishing not available - shared modules not loaded")
            return
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
        if self.event_handler and SHARED_MODULES_AVAILABLE:
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