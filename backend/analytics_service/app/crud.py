from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .models import (
    UserAnalytics, CourseAnalytics, EnrollmentAnalytics, 
    AssessmentAnalytics, ProgressAnalytics, SystemAnalytics, 
    LearningPathAnalytics
)
from .schemas import (
    UserAnalyticsCreate, UserAnalyticsUpdate,
    CourseAnalyticsCreate, CourseAnalyticsUpdate,
    EnrollmentAnalyticsCreate, EnrollmentAnalyticsUpdate,
    AssessmentAnalyticsCreate, AssessmentAnalyticsUpdate,
    ProgressAnalyticsCreate, ProgressAnalyticsUpdate,
    SystemAnalyticsCreate, SystemAnalyticsUpdate,
    LearningPathAnalyticsCreate, LearningPathAnalyticsUpdate
)

# User Analytics CRUD
async def create_user_analytics(db: AsyncSession, analytics: UserAnalyticsCreate) -> UserAnalytics:
    """Create user analytics record."""
    db_analytics = UserAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_user_analytics(db: AsyncSession, user_id: int) -> Optional[UserAnalytics]:
    """Get user analytics by user ID."""
    result = await db.execute(
        select(UserAnalytics).where(UserAnalytics.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def update_user_analytics(db: AsyncSession, user_id: int, analytics: UserAnalyticsUpdate) -> Optional[UserAnalytics]:
    """Update user analytics."""
    db_analytics = await get_user_analytics(db, user_id)
    if not db_analytics:
        return None
    
    update_data = analytics.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_analytics, field, value)
    
    db_analytics.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def calculate_user_engagement_score(db: AsyncSession, user_id: int) -> float:
    """Calculate user engagement score based on various metrics."""
    # Get user analytics
    user_analytics = await get_user_analytics(db, user_id)
    if not user_analytics:
        return 0.0
    
    # Calculate engagement score based on multiple factors
    login_factor = min(user_analytics.login_count / 10, 1.0)  # Normalize to 0-1
    session_factor = min(user_analytics.session_duration / 120, 1.0)  # Normalize to 0-1
    course_factor = min(user_analytics.total_courses_enrolled / 5, 1.0)  # Normalize to 0-1
    completion_factor = user_analytics.completed_courses / max(user_analytics.total_courses_enrolled, 1)
    grade_factor = user_analytics.average_grade / 100  # Normalize to 0-1
    
    # Weighted average
    engagement_score = (
        login_factor * 0.2 +
        session_factor * 0.2 +
        course_factor * 0.2 +
        completion_factor * 0.2 +
        grade_factor * 0.2
    ) * 100
    
    return min(engagement_score, 100.0)

# Course Analytics CRUD
async def create_course_analytics(db: AsyncSession, analytics: CourseAnalyticsCreate) -> CourseAnalytics:
    """Create course analytics record."""
    db_analytics = CourseAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_course_analytics(db: AsyncSession, course_id: int) -> Optional[CourseAnalytics]:
    """Get course analytics by course ID."""
    result = await db.execute(
        select(CourseAnalytics).where(CourseAnalytics.course_id == course_id)
    )
    return result.scalar_one_or_none()

async def update_course_analytics(db: AsyncSession, course_id: int, analytics: CourseAnalyticsUpdate) -> Optional[CourseAnalytics]:
    """Update course analytics."""
    db_analytics = await get_course_analytics(db, course_id)
    if not db_analytics:
        return None
    
    update_data = analytics.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_analytics, field, value)
    
    db_analytics.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def calculate_course_metrics(db: AsyncSession, course_id: int) -> Dict[str, Any]:
    """Calculate comprehensive course metrics."""
    # Get enrollment analytics for this course
    result = await db.execute(
        select(EnrollmentAnalytics).where(EnrollmentAnalytics.course_id == course_id)
    )
    enrollments = result.scalars().all()
    
    if not enrollments:
        return {
            "total_enrollments": 0,
            "active_enrollments": 0,
            "completed_enrollments": 0,
            "average_completion_time": 0.0,
            "average_grade": 0.0,
            "engagement_score": 0.0,
            "dropout_rate": 0.0
        }
    
    # Calculate metrics
    total_enrollments = len(enrollments)
    completed_enrollments = len([e for e in enrollments if e.completion_date])
    active_enrollments = len([e for e in enrollments if e.progress_percentage > 0 and not e.completion_date])
    
    # Calculate average completion time
    completion_times = [e.time_to_completion for e in enrollments if e.time_to_completion]
    average_completion_time = np.mean(completion_times) if completion_times else 0.0
    
    # Calculate average grade
    grades = [e.final_grade for e in enrollments if e.final_grade]
    average_grade = np.mean(grades) if grades else 0.0
    
    # Calculate dropout rate
    dropout_rate = ((total_enrollments - completed_enrollments) / total_enrollments) * 100
    
    # Calculate engagement score
    engagement_scores = [e.progress_percentage for e in enrollments]
    engagement_score = np.mean(engagement_scores) if engagement_scores else 0.0
    
    return {
        "total_enrollments": total_enrollments,
        "active_enrollments": active_enrollments,
        "completed_enrollments": completed_enrollments,
        "average_completion_time": average_completion_time,
        "average_grade": average_grade,
        "engagement_score": engagement_score,
        "dropout_rate": dropout_rate
    }

# Enrollment Analytics CRUD
async def create_enrollment_analytics(db: AsyncSession, analytics: EnrollmentAnalyticsCreate) -> EnrollmentAnalytics:
    """Create enrollment analytics record."""
    db_analytics = EnrollmentAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_enrollment_analytics(db: AsyncSession, enrollment_id: int) -> Optional[EnrollmentAnalytics]:
    """Get enrollment analytics by enrollment ID."""
    result = await db.execute(
        select(EnrollmentAnalytics).where(EnrollmentAnalytics.enrollment_id == enrollment_id)
    )
    return result.scalar_one_or_none()

async def update_enrollment_analytics(db: AsyncSession, enrollment_id: int, analytics: EnrollmentAnalyticsUpdate) -> Optional[EnrollmentAnalytics]:
    """Update enrollment analytics."""
    db_analytics = await get_enrollment_analytics(db, enrollment_id)
    if not db_analytics:
        return None
    
    update_data = analytics.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_analytics, field, value)
    
    db_analytics.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

# Assessment Analytics CRUD
async def create_assessment_analytics(db: AsyncSession, analytics: AssessmentAnalyticsCreate) -> AssessmentAnalytics:
    """Create assessment analytics record."""
    # Calculate percentage if score is provided
    if analytics.score is not None and analytics.max_score > 0:
        analytics.percentage = (analytics.score / analytics.max_score) * 100
        analytics.passed = analytics.percentage >= 70  # 70% passing threshold
    
    db_analytics = AssessmentAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_assessment_analytics(db: AsyncSession, assessment_id: int, user_id: int) -> Optional[AssessmentAnalytics]:
    """Get assessment analytics by assessment ID and user ID."""
    result = await db.execute(
        select(AssessmentAnalytics).where(
            and_(
                AssessmentAnalytics.assessment_id == assessment_id,
                AssessmentAnalytics.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()

async def get_user_assessment_history(db: AsyncSession, user_id: int, course_id: Optional[int] = None) -> List[AssessmentAnalytics]:
    """Get user's assessment history."""
    query = select(AssessmentAnalytics).where(AssessmentAnalytics.user_id == user_id)
    if course_id:
        query = query.where(AssessmentAnalytics.course_id == course_id)
    
    result = await db.execute(query.order_by(desc(AssessmentAnalytics.submitted_at)))
    return result.scalars().all()

# Progress Analytics CRUD
async def create_progress_analytics(db: AsyncSession, analytics: ProgressAnalyticsCreate) -> ProgressAnalytics:
    """Create progress analytics record."""
    db_analytics = ProgressAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_user_progress(db: AsyncSession, user_id: int, course_id: Optional[int] = None) -> List[ProgressAnalytics]:
    """Get user progress analytics."""
    query = select(ProgressAnalytics).where(ProgressAnalytics.user_id == user_id)
    if course_id:
        query = query.where(ProgressAnalytics.course_id == course_id)
    
    result = await db.execute(query.order_by(desc(ProgressAnalytics.created_at)))
    return result.scalars().all()

async def get_course_progress_summary(db: AsyncSession, course_id: int) -> Dict[str, Any]:
    """Get course progress summary."""
    result = await db.execute(
        select(ProgressAnalytics).where(ProgressAnalytics.course_id == course_id)
    )
    progress_records = result.scalars().all()
    
    if not progress_records:
        return {
            "total_activities": 0,
            "completed_activities": 0,
            "average_activity_score": 0.0,
            "total_time_spent": 0.0
        }
    
    total_activities = len(progress_records)
    completed_activities = len([p for p in progress_records if p.completion_status == "completed"])
    
    scores = [p.activity_score for p in progress_records if p.activity_score]
    average_score = np.mean(scores) if scores else 0.0
    
    time_spent = [p.activity_duration for p in progress_records if p.activity_duration]
    total_time = np.sum(time_spent) if time_spent else 0.0
    
    return {
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "average_activity_score": average_score,
        "total_time_spent": total_time
    }

# System Analytics CRUD
async def create_system_analytics(db: AsyncSession, analytics: SystemAnalyticsCreate) -> SystemAnalytics:
    """Create system analytics record."""
    db_analytics = SystemAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_system_metrics(db: AsyncSession, period: str, category: Optional[str] = None) -> List[SystemAnalytics]:
    """Get system metrics for a specific period and category."""
    query = select(SystemAnalytics).where(SystemAnalytics.period == period)
    if category:
        query = query.where(SystemAnalytics.category == category)
    
    result = await db.execute(query.order_by(desc(SystemAnalytics.period_date)))
    return result.scalars().all()

# Learning Path Analytics CRUD
async def create_learning_path_analytics(db: AsyncSession, analytics: LearningPathAnalyticsCreate) -> LearningPathAnalytics:
    """Create learning path analytics record."""
    db_analytics = LearningPathAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def get_learning_path_analytics(db: AsyncSession, user_id: int) -> Optional[LearningPathAnalytics]:
    """Get learning path analytics for a user."""
    result = await db.execute(
        select(LearningPathAnalytics).where(LearningPathAnalytics.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def update_learning_path_analytics(db: AsyncSession, user_id: int, analytics: LearningPathAnalyticsUpdate) -> Optional[LearningPathAnalytics]:
    """Update learning path analytics."""
    db_analytics = await get_learning_path_analytics(db, user_id)
    if not db_analytics:
        return None
    
    update_data = analytics.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_analytics, field, value)
    
    db_analytics.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

# Analytics Summary and Dashboard functions
async def get_analytics_summary(db: AsyncSession) -> Dict[str, Any]:
    """Get system-wide analytics summary."""
    # Count total users
    user_result = await db.execute(select(func.count(UserAnalytics.id)))
    total_users = user_result.scalar() or 0
    
    # Count total courses
    course_result = await db.execute(select(func.count(CourseAnalytics.id)))
    total_courses = course_result.scalar() or 0
    
    # Count total enrollments
    enrollment_result = await db.execute(select(func.count(EnrollmentAnalytics.id)))
    total_enrollments = enrollment_result.scalar() or 0
    
    # Count active enrollments
    active_result = await db.execute(
        select(func.count(EnrollmentAnalytics.id)).where(
            and_(
                EnrollmentAnalytics.progress_percentage > 0,
                EnrollmentAnalytics.completion_date.is_(None)
            )
        )
    )
    active_enrollments = active_result.scalar() or 0
    
    # Calculate completion rate
    completion_result = await db.execute(
        select(func.count(EnrollmentAnalytics.id)).where(
            EnrollmentAnalytics.completion_date.isnot(None)
        )
    )
    completed_enrollments = completion_result.scalar() or 0
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
    
    # Calculate average grade
    grade_result = await db.execute(
        select(func.avg(EnrollmentAnalytics.final_grade)).where(
            EnrollmentAnalytics.final_grade.isnot(None)
        )
    )
    average_grade = grade_result.scalar() or 0.0
    
    # Count total assessments
    assessment_result = await db.execute(select(func.count(AssessmentAnalytics.id)))
    total_assessments = assessment_result.scalar() or 0
    
    # Calculate average engagement score
    engagement_result = await db.execute(
        select(func.avg(UserAnalytics.engagement_score))
    )
    average_engagement_score = engagement_result.scalar() or 0.0
    
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "active_enrollments": active_enrollments,
        "completion_rate": completion_rate,
        "average_grade": average_grade,
        "total_assessments": total_assessments,
        "average_engagement_score": average_engagement_score
    }

async def get_user_dashboard_analytics(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get user dashboard analytics."""
    user_analytics = await get_user_analytics(db, user_id)
    if not user_analytics:
        return {
            "user_id": user_id,
            "total_courses_enrolled": 0,
            "completed_courses": 0,
            "average_grade": 0.0,
            "engagement_score": 0.0,
            "recent_activities": [],
            "learning_path_progress": None,
            "recommended_courses": []
        }
    
    # Get recent activities
    recent_activities = await get_user_progress(db, user_id)
    recent_activities_data = [
        {
            "id": activity.id,
            "activity_type": activity.activity_type,
            "course_id": activity.course_id,
            "completion_status": activity.completion_status,
            "created_at": activity.created_at.isoformat()
        }
        for activity in recent_activities[:10]  # Last 10 activities
    ]
    
    # Get learning path progress
    learning_path = await get_learning_path_analytics(db, user_id)
    learning_path_progress = None
    if learning_path:
        learning_path_progress = {
            "completion_rate": learning_path.completion_rate,
            "time_to_complete_path": learning_path.time_to_complete_path,
            "skill_gaps": learning_path.skill_gaps,
            "next_recommendations": learning_path.next_recommendations
        }
    
    return {
        "user_id": user_id,
        "total_courses_enrolled": user_analytics.total_courses_enrolled,
        "completed_courses": user_analytics.completed_courses,
        "average_grade": user_analytics.average_grade,
        "engagement_score": user_analytics.engagement_score,
        "recent_activities": recent_activities_data,
        "learning_path_progress": learning_path_progress,
        "recommended_courses": learning_path.recommended_courses if learning_path else []
    } 