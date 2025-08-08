#!/usr/bin/env python3
"""
Test script for service-to-service communication.
Demonstrates how services can communicate with each other.
"""

import asyncio
import sys
import os

# Add the shared directory to the path
sys.path.append(os.path.dirname(__file__))

from http_client import ServiceClient, service_registry
from event_handler import get_event_client, EventType


async def test_service_communication():
    """Test service-to-service communication."""
    print("🚀 Testing Service-to-Service Communication")
    print("=" * 50)
    
    # Test 1: Service Registry
    print("\n1. Testing Service Registry:")
    try:
        user_url = service_registry.get_service_url("user")
        print(f"✅ User service URL: {user_url}")
        
        course_url = service_registry.get_service_url("course")
        print(f"✅ Course service URL: {course_url}")
        
        enrollment_url = service_registry.get_service_url("enrollment")
        print(f"✅ Enrollment service URL: {enrollment_url}")
    except Exception as e:
        print(f"❌ Service registry error: {e}")
    
    # Test 2: HTTP Client
    print("\n2. Testing HTTP Client:")
    try:
        # Test health check for user service
        user_client = service_registry.get_client("user")
        async with user_client:
            health_response = await user_client.get("/api/v1/health")
            print(f"✅ User service health: {health_response}")
    except Exception as e:
        print(f"❌ HTTP client error: {e}")
    
    # Test 3: Service Client
    print("\n3. Testing Service Client:")
    try:
        enrollment_client = ServiceClient("enrollment")
        
        # Test getting user (this will fail if user service is not running)
        try:
            user_data = await enrollment_client.get_user(1)
            print(f"✅ Retrieved user data: {user_data}")
        except Exception as e:
            print(f"⚠️  User service not available: {e}")
        
        # Test getting course (this will fail if course service is not running)
        try:
            course_data = await enrollment_client.get_course(1)
            print(f"✅ Retrieved course data: {course_data}")
        except Exception as e:
            print(f"⚠️  Course service not available: {e}")
            
    except Exception as e:
        print(f"❌ Service client error: {e}")
    
    # Test 4: Event Handling
    print("\n4. Testing Event Handling:")
    try:
        event_client = get_event_client("enrollment")
        
        # Test publishing events
        await event_client.enrollment_created({
            "enrollment_id": 1,
            "user_id": 1,
            "course_id": 1,
            "status": "active"
        })
        print("✅ Published enrollment created event")
        
        await event_client.enrollment_completed({
            "enrollment_id": 1,
            "user_id": 1,
            "course_id": 1,
            "completion_date": "2025-08-04T14:00:00"
        })
        print("✅ Published enrollment completed event")
        
        # Test notification creation
        try:
            await enrollment_client.create_notification({
                "user_id": 1,
                "notification_type": "course_announcement",
                "title": "Test Notification",
                "content": "This is a test notification",
                "priority": "normal"
            })
            print("✅ Created test notification")
        except Exception as e:
            print(f"⚠️  Communication service not available: {e}")
            
    except Exception as e:
        print(f"❌ Event handling error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Service-to-Service Communication Test Complete!")
    print("\nKey Features Demonstrated:")
    print("• Service Registry with URL management")
    print("• HTTP Client with retry logic and circuit breaker")
    print("• Service Client for easy inter-service calls")
    print("• Event publishing and handling")
    print("• Notification creation across services")
    print("• Error handling and graceful degradation")


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n🔧 Testing Circuit Breaker:")
    print("=" * 30)
    
    from http_client import CircuitBreaker
    
    # Create a circuit breaker
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)
    
    print(f"Initial state: {cb.state}")
    print(f"Can execute: {cb.can_execute()}")
    
    # Simulate failures
    for i in range(4):
        cb.on_failure()
        print(f"After failure {i+1}: state={cb.state}, can_execute={cb.can_execute()}")
    
    # Simulate success
    cb.on_success()
    print(f"After success: state={cb.state}, can_execute={cb.can_execute()}")
    
    print("✅ Circuit breaker test complete!")


if __name__ == "__main__":
    print("🧪 Service-to-Service Communication Test Suite")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_service_communication())
    asyncio.run(test_circuit_breaker()) 