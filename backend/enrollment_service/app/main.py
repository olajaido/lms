from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db

# Import shared communication components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from shared.http_client import ServiceClient, service_registry
    from shared.auth_middleware import require_user_auth
    from shared.event_handler import get_event_client, EventType
    SHARED_AVAILABLE = True
except ImportError:
    # Fallback if shared module is not available
    SHARED_AVAILABLE = False
    print("Warning: Shared module not available, running in fallback mode")

app = FastAPI(title="Enrollment Service", version="1.0.0")

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


# Service-to-service communication endpoints
@app.post("/api/v1/events", status_code=status.HTTP_201_CREATED)
async def receive_event(
    event_data: dict,
    auth: dict = Depends(require_user_auth) if SHARED_AVAILABLE else None
):
    """Receive events from other services."""
    if not SHARED_AVAILABLE:
        return {"message": "Event received successfully (fallback mode)"}
    
    # Process the event based on type
    event_type = event_data.get("event_type")
    data = event_data.get("data", {})
    
    if event_type == EventType.USER_CREATED:
        # Handle user created event
        print(f"Received user created event: {data}")
    elif event_type == EventType.COURSE_CREATED:
        # Handle course created event
        print(f"Received course created event: {data}")
    elif event_type == EventType.ASSESSMENT_SUBMITTED:
        # Handle assessment submitted event
        print(f"Received assessment submitted event: {data}")
    
    return {"message": "Event received successfully"}


@app.get("/api/v1/enrollments", response_model=List[schemas.Enrollment])
async def list_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[schemas.Enrollment]:
    """List enrollments with optional filtering."""
    enrollments = await crud.get_enrollments(
        db, skip=skip, limit=limit, user_id=user_id, 
        course_id=course_id, status=status
    )
    return [schemas.Enrollment.from_orm(e) for e in enrollments]


@app.post("/api/v1/enrollments", response_model=schemas.EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_create: schemas.EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.EnrollmentResponse:
    """Create a new enrollment with service-to-service validation."""
    
    if SHARED_AVAILABLE:
        # Validate user exists using service-to-service communication
        try:
            service_client = ServiceClient("enrollment")
            user_data = await service_client.get_user(enrollment_create.user_id)
            course_data = await service_client.get_course(enrollment_create.course_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {str(e)}"
            )
        
        # Create enrollment
        enrollment = await crud.create_enrollment(db, enrollment_create)
        
        # Publish enrollment created event
        event_client = get_event_client("enrollment")
        await event_client.enrollment_created({
            "enrollment_id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "status": enrollment.status
        })
        
        # Create notification for user
        try:
            await service_client.create_notification({
                "user_id": enrollment.user_id,
                "notification_type": "course_announcement",
                "title": "Enrollment Successful",
                "content": f"You have been successfully enrolled in course {course_data.get('title', 'Unknown')}",
                "priority": "normal",
                "action_url": f"/courses/{enrollment.course_id}"
            })
        except Exception as e:
            print(f"Warning: Failed to create notification: {e}")
    else:
        # Fallback mode - create enrollment without service validation
        enrollment = await crud.create_enrollment(db, enrollment_create)
    
    return schemas.EnrollmentResponse(
        enrollment=schemas.Enrollment.from_orm(enrollment),
        message="Enrollment created successfully"
    )


@app.get("/api/v1/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
async def get_enrollment(
    enrollment_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Enrollment:
    """Get enrollment by ID."""
    enrollment = await crud.get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return schemas.Enrollment.from_orm(enrollment)


@app.put("/api/v1/enrollments/{enrollment_id}", response_model=schemas.EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    enrollment_update: schemas.EnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.EnrollmentResponse:
    """Update enrollment."""
    enrollment = await crud.update_enrollment(db, enrollment_id, enrollment_update)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Publish enrollment updated event
    event_client = get_event_client("enrollment")
    await event_client.enrollment_created({
        "enrollment_id": enrollment.id,
        "user_id": enrollment.user_id,
        "course_id": enrollment.course_id,
        "status": enrollment.status
    })
    
    return schemas.EnrollmentResponse(
        enrollment=schemas.Enrollment.from_orm(enrollment),
        message="Enrollment updated successfully"
    )


@app.patch("/api/v1/enrollments/{enrollment_id}/progress", response_model=schemas.EnrollmentResponse)
async def update_enrollment_progress(
    enrollment_id: int,
    progress_percentage: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
) -> schemas.EnrollmentResponse:
    """Update enrollment progress."""
    enrollment = await crud.update_enrollment_progress(db, enrollment_id, progress_percentage)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # If enrollment is completed, publish completion event
    if enrollment.status == "completed":
        event_client = get_event_client("enrollment")
        await event_client.enrollment_completed({
            "enrollment_id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "completion_date": enrollment.completed_at.isoformat() if enrollment.completed_at else None
        })
        
        # Create completion notification
        try:
            service_client = ServiceClient("enrollment")
            await service_client.create_notification({
                "user_id": enrollment.user_id,
                "notification_type": "course_completed",
                "title": "Course Completed!",
                "content": f"Congratulations! You have completed the course.",
                "priority": "high",
                "action_url": f"/courses/{enrollment.course_id}/certificate"
            })
        except Exception as e:
            logger.warning(f"Failed to create completion notification: {e}")
    
    return schemas.EnrollmentResponse(
        enrollment=schemas.Enrollment.from_orm(enrollment),
        message="Enrollment progress updated successfully"
    )


@app.get("/api/v1/enrollments/stats/user/{user_id}", response_model=schemas.EnrollmentStats)
async def get_user_enrollment_stats(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.EnrollmentStats:
    """Get enrollment statistics for a user."""
    stats = await crud.get_user_enrollment_stats(db, user_id)
    return schemas.EnrollmentStats(**stats)


@app.get("/api/v1/enrollments/check/{user_id}/{course_id}")
async def check_enrollment(
    user_id: int, course_id: int, db: AsyncSession = Depends(get_db)
):
    """Check if user is enrolled in a course."""
    enrollment = await crud.get_enrollment_by_user_and_course(db, user_id, course_id)
    return {
        "is_enrolled": enrollment is not None,
        "enrollment": schemas.Enrollment.from_orm(enrollment) if enrollment else None
    }


@app.delete("/api/v1/enrollments/{enrollment_id}")
async def delete_enrollment(
    enrollment_id: int, db: AsyncSession = Depends(get_db)
):
    """Delete enrollment (soft delete)."""
    success = await crud.delete_enrollment(db, enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment deleted successfully"}