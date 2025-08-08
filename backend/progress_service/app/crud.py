from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status

from .models import (
    Progress, ProgressActivity, CourseModule, ModuleProgress, LearningPath,
    ProgressStatus, ActivityType
)
from .schemas import (
    ProgressCreate, ProgressUpdate, ProgressActivityCreate, CourseModuleCreate,
    CourseModuleUpdate, ModuleProgressCreate, ModuleProgressUpdate,
    LearningPathCreate, LearningPathUpdate
)


# Progress CRUD operations
async def create_progress(db: AsyncSession, progress_create: ProgressCreate) -> Progress:
    """Create a new progress record."""
    # Check if progress already exists
    existing = await get_progress_by_user_and_course(
        db, progress_create.user_id, progress_create.course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Progress record already exists for this user and course"
        )
    
    progress = Progress(**progress_create.dict())
    progress.started_at = datetime.utcnow()
    progress.last_accessed = datetime.utcnow()
    
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress


async def get_progress(db: AsyncSession, progress_id: int) -> Optional[Progress]:
    """Get progress by ID."""
    result = await db.execute(select(Progress).where(Progress.id == progress_id))
    return result.scalar_one_or_none()


async def get_progress_by_user_and_course(
    db: AsyncSession, user_id: int, course_id: int
) -> Optional[Progress]:
    """Get progress by user and course combination."""
    result = await db.execute(
        select(Progress).where(
            and_(Progress.user_id == user_id, Progress.course_id == course_id)
        )
    )
    return result.scalar_one_or_none()


async def get_progress_by_user(
    db: AsyncSession, user_id: int
) -> List[Progress]:
    """Get all progress records for a user."""
    result = await db.execute(
        select(Progress)
        .where(Progress.user_id == user_id)
        .order_by(desc(Progress.last_accessed))
    )
    return result.scalars().all()


async def get_progress_by_course(
    db: AsyncSession, course_id: int
) -> List[Progress]:
    """Get all progress records for a course."""
    result = await db.execute(
        select(Progress)
        .where(Progress.course_id == course_id)
        .order_by(desc(Progress.last_accessed))
    )
    return result.scalars().all()


async def update_progress(
    db: AsyncSession, progress_id: int, progress_update: ProgressUpdate
) -> Optional[Progress]:
    """Update progress record."""
    progress = await get_progress(db, progress_id)
    if not progress:
        return None
    
    update_data = progress_update.dict(exclude_unset=True)
    
    # Handle status changes
    if 'status' in update_data:
        if update_data['status'] == ProgressStatus.COMPLETED and not progress.completed_at:
            update_data['completed_at'] = datetime.utcnow()
            update_data['certificate_earned'] = True
            update_data['certificate_issued_at'] = datetime.utcnow()
        elif update_data['status'] == ProgressStatus.IN_PROGRESS and not progress.started_at:
            update_data['started_at'] = datetime.utcnow()
    
    # Update last accessed
    update_data['last_accessed'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(progress, field, value)
    
    await db.commit()
    await db.refresh(progress)
    return progress


async def update_progress_completion(
    db: AsyncSession, progress_id: int, completion_percentage: float
) -> Optional[Progress]:
    """Update progress completion percentage with automatic status handling."""
    if not 0.0 <= completion_percentage <= 100.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completion percentage must be between 0.0 and 100.0"
        )
    
    progress = await get_progress(db, progress_id)
    if not progress:
        return None
    
    progress.completion_percentage = completion_percentage
    progress.last_accessed = datetime.utcnow()
    
    # Auto-update status based on completion
    if completion_percentage == 0.0:
        progress.status = ProgressStatus.NOT_STARTED
    elif completion_percentage == 100.0:
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = datetime.utcnow()
        progress.certificate_earned = True
        progress.certificate_issued_at = datetime.utcnow()
    else:
        progress.status = ProgressStatus.IN_PROGRESS
        if not progress.started_at:
            progress.started_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(progress)
    return progress


# Activity tracking
async def log_activity(
    db: AsyncSession, activity_create: ProgressActivityCreate
) -> ProgressActivity:
    """Log a progress activity."""
    activity = ProgressActivity(**activity_create.dict())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def get_activities_by_progress(
    db: AsyncSession, progress_id: int
) -> List[ProgressActivity]:
    """Get all activities for a progress record."""
    result = await db.execute(
        select(ProgressActivity)
        .where(ProgressActivity.progress_id == progress_id)
        .order_by(desc(ProgressActivity.created_at))
    )
    return result.scalars().all()


async def get_activities_by_user(
    db: AsyncSession, user_id: int, limit: int = 50
) -> List[ProgressActivity]:
    """Get recent activities for a user."""
    result = await db.execute(
        select(ProgressActivity)
        .where(ProgressActivity.user_id == user_id)
        .order_by(desc(ProgressActivity.created_at))
        .limit(limit)
    )
    return result.scalars().all()


# Course Module CRUD operations
async def create_course_module(
    db: AsyncSession, module_create: CourseModuleCreate
) -> CourseModule:
    """Create a new course module."""
    module = CourseModule(**module_create.dict())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


async def get_course_modules(
    db: AsyncSession, course_id: int, active_only: bool = True
) -> List[CourseModule]:
    """Get all modules for a course."""
    query = select(CourseModule).where(CourseModule.course_id == course_id)
    if active_only:
        query = query.where(CourseModule.is_active == True)
    query = query.order_by(CourseModule.order_index)
    result = await db.execute(query)
    return result.scalars().all()


async def update_course_module(
    db: AsyncSession, module_id: int, module_update: CourseModuleUpdate
) -> Optional[CourseModule]:
    """Update course module."""
    result = await db.execute(select(CourseModule).where(CourseModule.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        return None
    
    update_data = module_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    
    module.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(module)
    return module


# Module Progress CRUD operations
async def create_module_progress(
    db: AsyncSession, module_progress_create: ModuleProgressCreate
) -> ModuleProgress:
    """Create a new module progress record."""
    module_progress = ModuleProgress(**module_progress_create.dict())
    module_progress.last_accessed = datetime.utcnow()
    db.add(module_progress)
    await db.commit()
    await db.refresh(module_progress)
    return module_progress


async def get_module_progress(
    db: AsyncSession, progress_id: int, module_id: int
) -> Optional[ModuleProgress]:
    """Get module progress by progress and module IDs."""
    result = await db.execute(
        select(ModuleProgress).where(
            and_(
                ModuleProgress.progress_id == progress_id,
                ModuleProgress.module_id == module_id
            )
        )
    )
    return result.scalar_one_or_none()


async def update_module_progress(
    db: AsyncSession, module_progress_id: int, module_progress_update: ModuleProgressUpdate
) -> Optional[ModuleProgress]:
    """Update module progress."""
    result = await db.execute(
        select(ModuleProgress).where(ModuleProgress.id == module_progress_id)
    )
    module_progress = result.scalar_one_or_none()
    if not module_progress:
        return None
    
    update_data = module_progress_update.dict(exclude_unset=True)
    
    # Handle completion
    if 'completion_percentage' in update_data:
        if update_data['completion_percentage'] == 100.0 and not module_progress.completed_at:
            update_data['completed_at'] = datetime.utcnow()
        elif update_data['completion_percentage'] > 0 and not module_progress.started_at:
            update_data['started_at'] = datetime.utcnow()
    
    update_data['last_accessed'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(module_progress, field, value)
    
    await db.commit()
    await db.refresh(module_progress)
    return module_progress


# Learning Path CRUD operations
async def create_learning_path(
    db: AsyncSession, learning_path_create: LearningPathCreate
) -> LearningPath:
    """Create a new learning path."""
    learning_path = LearningPath(**learning_path_create.dict())
    db.add(learning_path)
    await db.commit()
    await db.refresh(learning_path)
    return learning_path


async def get_learning_paths(
    db: AsyncSession, course_id: int, active_only: bool = True
) -> List[LearningPath]:
    """Get all learning paths for a course."""
    query = select(LearningPath).where(LearningPath.course_id == course_id)
    if active_only:
        query = query.where(LearningPath.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


# Analytics and Statistics
async def get_user_progress_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get comprehensive progress statistics for a user."""
    # Get all progress records for user
    progress_records = await get_progress_by_user(db, user_id)
    
    if not progress_records:
        return {
            "total_courses": 0,
            "completed_courses": 0,
            "in_progress_courses": 0,
            "average_completion": 0.0,
            "total_time_spent": 0,
            "certificates_earned": 0
        }
    
    total_courses = len(progress_records)
    completed_courses = len([p for p in progress_records if p.status == ProgressStatus.COMPLETED])
    in_progress_courses = len([p for p in progress_records if p.status == ProgressStatus.IN_PROGRESS])
    average_completion = sum(p.completion_percentage for p in progress_records) / total_courses
    total_time_spent = sum(p.time_spent for p in progress_records)
    certificates_earned = len([p for p in progress_records if p.certificate_earned])
    
    return {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "average_completion": round(average_completion, 2),
        "total_time_spent": total_time_spent,
        "certificates_earned": certificates_earned
    }


async def get_course_progress_stats(db: AsyncSession, course_id: int) -> Dict[str, Any]:
    """Get comprehensive progress statistics for a course."""
    # Get all progress records for course
    progress_records = await get_progress_by_course(db, course_id)
    
    if not progress_records:
        return {
            "total_students": 0,
            "active_students": 0,
            "completed_students": 0,
            "average_completion": 0.0,
            "average_time_spent": 0.0,
            "completion_rate": 0.0
        }
    
    total_students = len(progress_records)
    active_students = len([p for p in progress_records if p.status == ProgressStatus.IN_PROGRESS])
    completed_students = len([p for p in progress_records if p.status == ProgressStatus.COMPLETED])
    average_completion = sum(p.completion_percentage for p in progress_records) / total_students
    average_time_spent = sum(p.time_spent for p in progress_records) / total_students
    completion_rate = (completed_students / total_students * 100) if total_students > 0 else 0
    
    return {
        "total_students": total_students,
        "active_students": active_students,
        "completed_students": completed_students,
        "average_completion": round(average_completion, 2),
        "average_time_spent": round(average_time_spent, 2),
        "completion_rate": round(completion_rate, 2)
    }


async def get_overall_progress_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get overall progress statistics across all courses."""
    # Get all progress records
    result = await db.execute(select(Progress))
    all_progress = result.scalars().all()
    
    if not all_progress:
        return {
            "total_enrollments": 0,
            "active_enrollments": 0,
            "completed_enrollments": 0,
            "average_completion": 0.0,
            "total_time_spent": 0,
            "certificates_issued": 0
        }
    
    total_enrollments = len(all_progress)
    active_enrollments = len([p for p in all_progress if p.status == ProgressStatus.IN_PROGRESS])
    completed_enrollments = len([p for p in all_progress if p.status == ProgressStatus.COMPLETED])
    average_completion = sum(p.completion_percentage for p in all_progress) / total_enrollments
    total_time_spent = sum(p.time_spent for p in all_progress)
    certificates_issued = len([p for p in all_progress if p.certificate_earned])
    
    return {
        "total_enrollments": total_enrollments,
        "active_enrollments": active_enrollments,
        "completed_enrollments": completed_enrollments,
        "average_completion": round(average_completion, 2),
        "total_time_spent": total_time_spent,
        "certificates_issued": certificates_issued
    }