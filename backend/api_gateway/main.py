"""
API Gateway for LMS Microservices
Provides unified API endpoints for frontend integration
"""

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import jwt
import os
from datetime import datetime

# Service URLs
SERVICES = {
    "user": "http://localhost:8001",
    "course": "http://localhost:8002", 
    "enrollment": "http://localhost:8003",
    "assessment": "http://localhost:8004",
    "progress": "http://localhost:8004",
    "communication": "http://localhost:8006",
    "content": "http://localhost:8007",
    "analytics": "http://localhost:8005"
}

# JWT Configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

app = FastAPI(title="LMS API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_token(request: Request) -> Optional[Dict[str, Any]]:
    """Verify JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from JWT token."""
    payload = await verify_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return payload

@app.get("/api/health")
async def health_check():
    """Health check for API gateway."""
    return {"status": "ok", "gateway": "running", "timestamp": datetime.utcnow().isoformat()}

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login(request: Request):
    """Login endpoint - forwards to user service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['user']}/api/v1/auth/login",
                json=await request.json(),
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.post("/api/auth/register")
async def register(request: Request):
    """Register endpoint - forwards to user service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['user']}/api/v1/auth/register",
                json=await request.json(),
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout endpoint - forwards to user service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['user']}/api/v1/auth/logout",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/api/users/me")
async def get_current_user_info(request: Request):
    """Get current user info - forwards to user service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['user']}/api/v1/users/me",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.put("/api/users/me")
async def update_user_profile(request: Request):
    """Update user profile - forwards to user service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.put(
                f"{SERVICES['user']}/api/v1/users/{user['sub']}",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")



# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_all_users(request: Request):
    """Get all users (admin only) - forwards to user service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['user']}/api/v1/users",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: int, request: Request):
    """Update user (admin only) - forwards to user service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.put(
                f"{SERVICES['user']}/api/v1/users/{user_id}",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    """Delete user (admin only) - forwards to user service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.delete(
                f"{SERVICES['user']}/api/v1/users/{user_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

@app.get("/api/admin/stats")
async def get_admin_stats(request: Request):
    """Get admin statistics - forwards to user service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['user']}/api/v1/stats/users",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

# ============================================================================
# COURSE ENDPOINTS
# ============================================================================

@app.get("/api/courses")
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    instructor: Optional[str] = None
):
    """Get courses - forwards to course service."""
    async with httpx.AsyncClient() as client:
        try:
            params = {"skip": skip, "limit": limit}
            if search:
                params["search"] = search
            if category:
                params["category"] = category
            if instructor:
                params["instructor"] = instructor
            
            response = await client.get(
                f"{SERVICES['course']}/api/v1/courses",
                params=params,
                timeout=10.0
            )
            # Wrap the response in the expected format for frontend
            data = response.json()
            return JSONResponse(
                content={"success": True, "data": data, "message": "Courses retrieved successfully"},
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course service error: {str(e)}")

@app.get("/api/courses/{course_id}")
async def get_course(course_id: int):
    """Get specific course - forwards to course service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICES['course']}/api/v1/courses/{course_id}",
                timeout=10.0
            )
            # Wrap the response in the expected format for frontend
            data = response.json()
            return JSONResponse(
                content={"success": True, "data": data, "message": "Course retrieved successfully"},
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course service error: {str(e)}")

@app.post("/api/courses")
async def create_course(request: Request):
    """Create course - forwards to course service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['course']}/api/v1/courses",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course service error: {str(e)}")

@app.put("/api/admin/courses/{course_id}")
async def update_course(course_id: int, request: Request):
    """Update course (admin only) - forwards to course service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.put(
                f"{SERVICES['course']}/api/v1/courses/{course_id}",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course service error: {str(e)}")

@app.delete("/api/admin/courses/{course_id}")
async def delete_course(course_id: int, request: Request):
    """Delete course (admin only) - forwards to course service."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.delete(
                f"{SERVICES['course']}/api/v1/courses/{course_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course service error: {str(e)}")

# ============================================================================
# ENROLLMENT ENDPOINTS
# ============================================================================

@app.post("/api/enrollments")
async def enroll_in_course(request: Request):
    """Enroll in course - forwards to enrollment service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['enrollment']}/api/v1/enrollments",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            # Wrap the response in the expected format for frontend
            data = response.json()
            return JSONResponse(
                content={"success": True, "data": data, "message": "Enrollment successful"},
                status_code=201
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Enrollment service error: {str(e)}")

@app.get("/api/enrollments")
async def get_enrollments(request: Request):
    """Get user enrollments - forwards to enrollment service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['enrollment']}/api/v1/enrollments",
                params={"user_id": user["sub"]},
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Enrollment service error: {str(e)}")

# ============================================================================
# CONTENT ENDPOINTS
# ============================================================================

@app.get("/api/content")
async def get_content(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    content_type: Optional[str] = None,
    course_id: Optional[int] = None
):
    """Get content - forwards to content service."""
    async with httpx.AsyncClient() as client:
        try:
            params = {"skip": skip, "limit": limit}
            if search:
                params["search"] = search
            if content_type:
                params["content_type"] = content_type
            if course_id:
                params["course_id"] = course_id
            
            response = await client.get(
                f"{SERVICES['content']}/api/v1/content",
                params=params,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Content service error: {str(e)}")

@app.get("/api/content/{content_id}")
async def get_content_by_id(content_id: int):
    """Get specific content - forwards to content service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICES['content']}/api/v1/content/{content_id}",
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Content service error: {str(e)}")

@app.post("/api/content/upload")
async def upload_content(request: Request):
    """Upload content - forwards to content service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['content']}/api/v1/content/upload",
                data=await request.form(),
                headers=headers,
                timeout=30.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Content service error: {str(e)}")

# ============================================================================
# PROGRESS ENDPOINTS
# ============================================================================

@app.get("/api/progress")
async def get_progress(request: Request):
    """Get user progress - forwards to progress service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['progress']}/api/v1/progress",
                params={"user_id": user["sub"]},
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Progress service error: {str(e)}")

@app.post("/api/progress")
async def update_progress(request: Request):
    """Update progress - forwards to progress service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['progress']}/api/v1/progress",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Progress service error: {str(e)}")

# ============================================================================
# ASSESSMENT ENDPOINTS
# ============================================================================

@app.get("/api/assessments")
async def get_assessments(
    course_id: Optional[int] = None,
    assessment_type: Optional[str] = None
):
    """Get assessments - forwards to assessment service."""
    async with httpx.AsyncClient() as client:
        try:
            params = {}
            if course_id:
                params["course_id"] = course_id
            if assessment_type:
                params["assessment_type"] = assessment_type
            
            response = await client.get(
                f"{SERVICES['assessment']}/api/v1/assessments",
                params=params,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Assessment service error: {str(e)}")

@app.get("/api/assessments/{assessment_id}")
async def get_assessment(assessment_id: int):
    """Get specific assessment - forwards to assessment service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICES['assessment']}/api/v1/assessments/{assessment_id}",
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Assessment service error: {str(e)}")

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(request: Request):
    """Get dashboard analytics - forwards to analytics service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['analytics']}/api/v1/analytics/users/{user['sub']}/dashboard",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analytics service error: {str(e)}")

@app.get("/api/analytics/courses/{course_id}")
async def get_course_analytics(course_id: int, request: Request):
    """Get course analytics - forwards to analytics service."""
    user = await get_current_user(request)
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['analytics']}/api/v1/analytics/courses/{course_id}",
                params={"user_id": user["sub"]},
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analytics service error: {str(e)}")

# ============================================================================
# COMMUNICATION ENDPOINTS
# ============================================================================

@app.post("/api/messages")
async def create_message(request: Request):
    """Create a new message - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['communication']}/api/v1/messages",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/messages/user/{user_id}")
async def get_messages_by_user(user_id: int, request: Request):
    """Get messages for a user - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/messages/user/{user_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/messages/between/{user1_id}/{user2_id}")
async def get_messages_between_users(user1_id: int, user2_id: int, request: Request):
    """Get messages between two users - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/messages/between/{user1_id}/{user2_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.patch("/api/messages/{message_id}/read")
async def mark_message_as_read(message_id: int, request: Request):
    """Mark a message as read - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.patch(
                f"{SERVICES['communication']}/api/v1/messages/{message_id}/read",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.post("/api/announcements")
async def create_announcement(request: Request):
    """Create a new announcement - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.post(
                f"{SERVICES['communication']}/api/v1/announcements",
                json=await request.json(),
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/announcements/course/{course_id}")
async def get_announcements_by_course(course_id: int, request: Request):
    """Get announcements for a course - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/announcements/course/{course_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/announcements/system")
async def get_system_announcements(request: Request):
    """Get system-wide announcements - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/announcements/system",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/notifications/user/{user_id}")
async def get_notifications_by_user(user_id: int, request: Request):
    """Get notifications for a user - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/notifications/user/{user_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/notifications/user/{user_id}/unread")
async def get_unread_notifications_by_user(user_id: int, request: Request):
    """Get unread notifications for a user - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/notifications/user/{user_id}/unread",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.patch("/api/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: int, request: Request):
    """Mark a notification as read - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.patch(
                f"{SERVICES['communication']}/api/v1/notifications/{notification_id}/read",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.patch("/api/notifications/{notification_id}/dismiss")
async def dismiss_notification(notification_id: int, request: Request):
    """Dismiss a notification - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.patch(
                f"{SERVICES['communication']}/api/v1/notifications/{notification_id}/dismiss",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/conversations/user/{user_id}")
async def get_conversations_by_user(user_id: int, request: Request):
    """Get conversations for a user - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/conversations/user/{user_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, request: Request):
    """Get conversation by ID - forwards to communication service."""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": request.headers.get("Authorization", "")}
            response = await client.get(
                f"{SERVICES['communication']}/api/v1/conversations/{conversation_id}",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Communication service error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 