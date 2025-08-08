from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from .models import Enrollment, EnrollmentStatus
from .schemas import EnrollmentCreate, EnrollmentUpdate


async def create_enrollment(db: AsyncSession, enrollment_create: EnrollmentCreate) -> Enrollment:
    """Create a new enrollment with validation."""
    # Check if enrollment already exists
    existing = await get_enrollment_by_user_and_course(
        db, enrollment_create.user_id, enrollment_create.course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already enrolled in this course"
        )
    
    # TODO: Validate user and course exist (requires service-to-service communication)
    # For now, we'll assume they exist
    
    enrollment = Enrollment(
        user_id=enrollment_create.user_id,
        course_id=enrollment_create.course_id,
        status=EnrollmentStatus.ACTIVE,
        enrolled_at=datetime.utcnow(),
        last_accessed=datetime.utcnow(),
        progress_percentage=0,
        is_active=True
    )
    
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def get_enrollment(db: AsyncSession, enrollment_id: int) -> Optional[Enrollment]:
    """Get enrollment by ID."""
    result = await db.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
    return result.scalar_one_or_none()


async def get_enrollment_by_user_and_course(
    db: AsyncSession, user_id: int, course_id: int
) -> Optional[Enrollment]:
    """Get enrollment by user and course combination."""
    result = await db.execute(
        select(Enrollment).where(
            and_(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        )
    )
    return result.scalar_one_or_none()


async def get_enrollments_by_user(
    db: AsyncSession, user_id: int, active_only: bool = False
) -> List[Enrollment]:
    """Get all enrollments for a user."""
    query = select(Enrollment).where(Enrollment.user_id == user_id)
    if active_only:
        query = query.where(Enrollment.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def get_enrollments_by_course(
    db: AsyncSession, course_id: int, active_only: bool = False
) -> List[Enrollment]:
    """Get all enrollments for a course."""
    query = select(Enrollment).where(Enrollment.course_id == course_id)
    if active_only:
        query = query.where(Enrollment.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def update_enrollment(
    db: AsyncSession, enrollment_id: int, enrollment_update: EnrollmentUpdate
) -> Optional[Enrollment]:
    """Update enrollment with validation."""
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        return None
    
    # Update fields
    update_data = enrollment_update.dict(exclude_unset=True)
    
    # Handle status changes
    if 'status' in update_data:
        if update_data['status'] == EnrollmentStatus.COMPLETED and not enrollment.completed_at:
            update_data['completed_at'] = datetime.utcnow()
        elif update_data['status'] == EnrollmentStatus.COMPLETED and enrollment.progress_percentage < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot mark as completed with less than 100% progress"
            )
    
    # Update progress
    if 'progress_percentage' in update_data:
        if update_data['progress_percentage'] == 100 and enrollment.status != EnrollmentStatus.COMPLETED:
            update_data['status'] = EnrollmentStatus.COMPLETED
            update_data['completed_at'] = datetime.utcnow()
    
    # Update last accessed
    update_data['last_accessed'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(enrollment, field, value)
    
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def delete_enrollment(db: AsyncSession, enrollment_id: int) -> bool:
    """Soft delete enrollment by setting is_active to False."""
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        return False
    
    enrollment.is_active = False
    enrollment.status = EnrollmentStatus.DROPPED
    await db.commit()
    return True


async def update_progress(
    db: AsyncSession, enrollment_id: int, progress_percentage: int
) -> Optional[Enrollment]:
    """Update enrollment progress with automatic completion handling."""
    if not 0 <= progress_percentage <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress percentage must be between 0 and 100"
        )
    
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        return None
    
    enrollment.progress_percentage = progress_percentage
    enrollment.last_accessed = datetime.utcnow()
    
    # Auto-complete if progress reaches 100%
    if progress_percentage == 100 and enrollment.status != EnrollmentStatus.COMPLETED:
        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def get_enrollments(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    course_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Enrollment]:
    """Get enrollments with optional filtering."""
    query = select(Enrollment)
    
    # Apply filters
    if user_id:
        query = query.where(Enrollment.user_id == user_id)
    if course_id:
        query = query.where(Enrollment.course_id == course_id)
    if status:
        query = query.where(Enrollment.status == status)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_enrollment_stats(db: AsyncSession, user_id: Optional[int] = None, course_id: Optional[int] = None):
    """Get enrollment statistics."""
    query = select(Enrollment)
    
    if user_id:
        query = query.where(Enrollment.user_id == user_id)
    if course_id:
        query = query.where(Enrollment.course_id == course_id)
    
    result = await db.execute(query)
    enrollments = result.scalars().all()
    
    if not enrollments:
        return {
            "total_enrollments": 0,
            "active_enrollments": 0,
            "completed_enrollments": 0,
            "average_progress": 0.0,
            "completion_rate": 0.0
        }
    
    total = len(enrollments)
    active = len([e for e in enrollments if e.is_active])
    completed = len([e for e in enrollments if e.status == EnrollmentStatus.COMPLETED])
    avg_progress = sum(e.progress_percentage for e in enrollments) / total
    completion_rate = (completed / total) * 100 if total > 0 else 0
    
    return {
        "total_enrollments": total,
        "active_enrollments": active,
        "completed_enrollments": completed,
        "average_progress": round(avg_progress, 2),
        "completion_rate": round(completion_rate, 2)
    }