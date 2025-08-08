from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from .database import get_db, create_tables
from . import crud, schemas

app = FastAPI(title="Analytics Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    await create_tables()

@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

# User Analytics Endpoints
@app.post("/api/v1/analytics/users", response_model=schemas.UserAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_user_analytics(
    analytics: schemas.UserAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.UserAnalyticsResponse:
    """Create user analytics record."""
    try:
        db_analytics = await crud.create_user_analytics(db, analytics)
        return schemas.UserAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="User analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/users/{user_id}", response_model=schemas.UserAnalyticsResponse)
async def get_user_analytics(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.UserAnalyticsResponse:
    """Get user analytics by user ID."""
    db_analytics = await crud.get_user_analytics(db, user_id)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User analytics not found"
        )
    
    return schemas.UserAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="User analytics retrieved successfully"
    )

@app.put("/api/v1/analytics/users/{user_id}", response_model=schemas.UserAnalyticsResponse)
async def update_user_analytics(
    user_id: int,
    analytics: schemas.UserAnalyticsUpdate,
    db: AsyncSession = Depends(get_db)
) -> schemas.UserAnalyticsResponse:
    """Update user analytics."""
    db_analytics = await crud.update_user_analytics(db, user_id, analytics)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User analytics not found"
        )
    
    return schemas.UserAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="User analytics updated successfully"
    )

@app.get("/api/v1/analytics/users/{user_id}/engagement-score")
async def get_user_engagement_score(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Calculate and return user engagement score."""
    engagement_score = await crud.calculate_user_engagement_score(db, user_id)
    return {
        "success": True,
        "data": {"user_id": user_id, "engagement_score": engagement_score},
        "message": "Engagement score calculated successfully"
    }

# Course Analytics Endpoints
@app.post("/api/v1/analytics/courses", response_model=schemas.CourseAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_course_analytics(
    analytics: schemas.CourseAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.CourseAnalyticsResponse:
    """Create course analytics record."""
    try:
        db_analytics = await crud.create_course_analytics(db, analytics)
        return schemas.CourseAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="Course analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create course analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/courses/{course_id}", response_model=schemas.CourseAnalyticsResponse)
async def get_course_analytics(
    course_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.CourseAnalyticsResponse:
    """Get course analytics by course ID."""
    db_analytics = await crud.get_course_analytics(db, course_id)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course analytics not found"
        )
    
    return schemas.CourseAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Course analytics retrieved successfully"
    )

@app.put("/api/v1/analytics/courses/{course_id}", response_model=schemas.CourseAnalyticsResponse)
async def update_course_analytics(
    course_id: int,
    analytics: schemas.CourseAnalyticsUpdate,
    db: AsyncSession = Depends(get_db)
) -> schemas.CourseAnalyticsResponse:
    """Update course analytics."""
    db_analytics = await crud.update_course_analytics(db, course_id, analytics)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course analytics not found"
        )
    
    return schemas.CourseAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Course analytics updated successfully"
    )

@app.get("/api/v1/analytics/courses/{course_id}/metrics")
async def get_course_metrics(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive course metrics."""
    metrics = await crud.calculate_course_metrics(db, course_id)
    return {
        "success": True,
        "data": metrics,
        "message": "Course metrics calculated successfully"
    }

# Enrollment Analytics Endpoints
@app.post("/api/v1/analytics/enrollments", response_model=schemas.EnrollmentAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment_analytics(
    analytics: schemas.EnrollmentAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.EnrollmentAnalyticsResponse:
    """Create enrollment analytics record."""
    try:
        db_analytics = await crud.create_enrollment_analytics(db, analytics)
        return schemas.EnrollmentAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="Enrollment analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create enrollment analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/enrollments/{enrollment_id}", response_model=schemas.EnrollmentAnalyticsResponse)
async def get_enrollment_analytics(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.EnrollmentAnalyticsResponse:
    """Get enrollment analytics by enrollment ID."""
    db_analytics = await crud.get_enrollment_analytics(db, enrollment_id)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment analytics not found"
        )
    
    return schemas.EnrollmentAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Enrollment analytics retrieved successfully"
    )

@app.put("/api/v1/analytics/enrollments/{enrollment_id}", response_model=schemas.EnrollmentAnalyticsResponse)
async def update_enrollment_analytics(
    enrollment_id: int,
    analytics: schemas.EnrollmentAnalyticsUpdate,
    db: AsyncSession = Depends(get_db)
) -> schemas.EnrollmentAnalyticsResponse:
    """Update enrollment analytics."""
    db_analytics = await crud.update_enrollment_analytics(db, enrollment_id, analytics)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment analytics not found"
        )
    
    return schemas.EnrollmentAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Enrollment analytics updated successfully"
    )

# Assessment Analytics Endpoints
@app.post("/api/v1/analytics/assessments", response_model=schemas.AssessmentAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment_analytics(
    analytics: schemas.AssessmentAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentAnalyticsResponse:
    """Create assessment analytics record."""
    try:
        db_analytics = await crud.create_assessment_analytics(db, analytics)
        return schemas.AssessmentAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="Assessment analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create assessment analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/assessments/{assessment_id}/users/{user_id}", response_model=schemas.AssessmentAnalyticsResponse)
async def get_assessment_analytics(
    assessment_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentAnalyticsResponse:
    """Get assessment analytics by assessment ID and user ID."""
    db_analytics = await crud.get_assessment_analytics(db, assessment_id, user_id)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment analytics not found"
        )
    
    return schemas.AssessmentAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Assessment analytics retrieved successfully"
    )

@app.get("/api/v1/analytics/users/{user_id}/assessments")
async def get_user_assessment_history(
    user_id: int,
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get user's assessment history."""
    assessments = await crud.get_user_assessment_history(db, user_id, course_id)
    return {
        "success": True,
        "data": assessments,
        "message": "User assessment history retrieved successfully"
    }

# Progress Analytics Endpoints
@app.post("/api/v1/analytics/progress", response_model=schemas.ProgressAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_progress_analytics(
    analytics: schemas.ProgressAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ProgressAnalyticsResponse:
    """Create progress analytics record."""
    try:
        db_analytics = await crud.create_progress_analytics(db, analytics)
        return schemas.ProgressAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="Progress analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create progress analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/users/{user_id}/progress")
async def get_user_progress(
    user_id: int,
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get user progress analytics."""
    progress = await crud.get_user_progress(db, user_id, course_id)
    return {
        "success": True,
        "data": progress,
        "message": "User progress retrieved successfully"
    }

@app.get("/api/v1/analytics/courses/{course_id}/progress-summary")
async def get_course_progress_summary(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get course progress summary."""
    summary = await crud.get_course_progress_summary(db, course_id)
    return {
        "success": True,
        "data": summary,
        "message": "Course progress summary retrieved successfully"
    }

# System Analytics Endpoints
@app.post("/api/v1/analytics/system", response_model=schemas.SystemAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_system_analytics(
    analytics: schemas.SystemAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.SystemAnalyticsResponse:
    """Create system analytics record."""
    try:
        db_analytics = await crud.create_system_analytics(db, analytics)
        return schemas.SystemAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="System analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create system analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/system/metrics")
async def get_system_metrics(
    period: str = Query(..., description="Time period (daily, weekly, monthly, yearly)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    """Get system metrics for a specific period and category."""
    metrics = await crud.get_system_metrics(db, period, category)
    return {
        "success": True,
        "data": metrics,
        "message": "System metrics retrieved successfully"
    }

# Learning Path Analytics Endpoints
@app.post("/api/v1/analytics/learning-paths", response_model=schemas.LearningPathAnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_path_analytics(
    analytics: schemas.LearningPathAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.LearningPathAnalyticsResponse:
    """Create learning path analytics record."""
    try:
        db_analytics = await crud.create_learning_path_analytics(db, analytics)
        return schemas.LearningPathAnalyticsResponse(
            success=True,
            data=db_analytics,
            message="Learning path analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create learning path analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/users/{user_id}/learning-path", response_model=schemas.LearningPathAnalyticsResponse)
async def get_learning_path_analytics(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.LearningPathAnalyticsResponse:
    """Get learning path analytics for a user."""
    db_analytics = await crud.get_learning_path_analytics(db, user_id)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path analytics not found"
        )
    
    return schemas.LearningPathAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Learning path analytics retrieved successfully"
    )

@app.put("/api/v1/analytics/users/{user_id}/learning-path", response_model=schemas.LearningPathAnalyticsResponse)
async def update_learning_path_analytics(
    user_id: int,
    analytics: schemas.LearningPathAnalyticsUpdate,
    db: AsyncSession = Depends(get_db)
) -> schemas.LearningPathAnalyticsResponse:
    """Update learning path analytics."""
    db_analytics = await crud.update_learning_path_analytics(db, user_id, analytics)
    if not db_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path analytics not found"
        )
    
    return schemas.LearningPathAnalyticsResponse(
        success=True,
        data=db_analytics,
        message="Learning path analytics updated successfully"
    )

# Dashboard and Summary Endpoints
@app.get("/api/v1/analytics/summary", response_model=schemas.AnalyticsSummaryResponse)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db)
) -> schemas.AnalyticsSummaryResponse:
    """Get system-wide analytics summary."""
    summary = await crud.get_analytics_summary(db)
    return schemas.AnalyticsSummaryResponse(
        success=True,
        data=summary,
        message="Analytics summary retrieved successfully"
    )

@app.get("/api/v1/analytics/users/{user_id}/dashboard", response_model=schemas.UserDashboardResponse)
async def get_user_dashboard(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.UserDashboardResponse:
    """Get user dashboard analytics."""
    dashboard = await crud.get_user_dashboard_analytics(db, user_id)
    return schemas.UserDashboardResponse(
        success=True,
        data=dashboard,
        message="User dashboard analytics retrieved successfully"
    )

@app.get("/api/v1/analytics/courses/{course_id}/performance", response_model=schemas.CoursePerformanceResponse)
async def get_course_performance(
    course_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.CoursePerformanceResponse:
    """Get comprehensive course performance analytics."""
    # Get course analytics
    course_analytics = await crud.get_course_analytics(db, course_id)
    if not course_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course analytics not found"
        )
    
    # Get assessment performance
    assessment_result = await db.execute(
        f"SELECT * FROM assessment_analytics WHERE course_id = {course_id}"
    )
    assessment_performance = []
    # This would need proper implementation based on your assessment analytics structure
    
    performance_data = {
        "course_id": course_id,
        "enrollment_count": course_analytics.total_enrollments,
        "completion_rate": (course_analytics.completed_enrollments / course_analytics.total_enrollments * 100) if course_analytics.total_enrollments > 0 else 0,
        "average_grade": course_analytics.average_grade,
        "average_completion_time": course_analytics.average_completion_time,
        "engagement_score": course_analytics.engagement_score,
        "dropout_rate": course_analytics.dropout_rate,
        "satisfaction_score": course_analytics.satisfaction_score,
        "assessment_performance": assessment_performance
    }
    
    return schemas.CoursePerformanceResponse(
        success=True,
        data=performance_data,
        message="Course performance analytics retrieved successfully"
    )