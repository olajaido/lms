from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EngagementLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CompletionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ActivityType(str, Enum):
    VIDEO_WATCH = "video_watch"
    QUIZ_TAKEN = "quiz_taken"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    MODULE_COMPLETED = "module_completed"
    COURSE_ACCESSED = "course_accessed"

class MetricType(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    RATE = "rate"

class PeriodType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Base schemas
class UserAnalyticsBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    session_duration: float = Field(0.0, description="Session duration in minutes")
    login_count: int = Field(0, description="Number of logins")
    total_courses_enrolled: int = Field(0, description="Total courses enrolled")
    completed_courses: int = Field(0, description="Number of completed courses")
    average_grade: float = Field(0.0, description="Average grade across all courses")
    engagement_score: float = Field(0.0, description="Calculated engagement metric")

class UserAnalyticsCreate(UserAnalyticsBase):
    pass

class UserAnalyticsUpdate(BaseModel):
    session_duration: Optional[float] = None
    login_count: Optional[int] = None
    total_courses_enrolled: Optional[int] = None
    completed_courses: Optional[int] = None
    average_grade: Optional[float] = None
    engagement_score: Optional[float] = None

class UserAnalytics(UserAnalyticsBase):
    id: int
    last_login: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CourseAnalyticsBase(BaseModel):
    course_id: int = Field(..., description="Course ID")
    total_enrollments: int = Field(0, description="Total number of enrollments")
    active_enrollments: int = Field(0, description="Currently active enrollments")
    completed_enrollments: int = Field(0, description="Completed enrollments")
    average_completion_time: float = Field(0.0, description="Average completion time in days")
    average_grade: float = Field(0.0, description="Average grade for the course")
    engagement_score: float = Field(0.0, description="Course engagement score")
    dropout_rate: float = Field(0.0, description="Dropout rate percentage")
    satisfaction_score: float = Field(0.0, description="Satisfaction score from reviews")

class CourseAnalyticsCreate(CourseAnalyticsBase):
    pass

class CourseAnalyticsUpdate(BaseModel):
    total_enrollments: Optional[int] = None
    active_enrollments: Optional[int] = None
    completed_enrollments: Optional[int] = None
    average_completion_time: Optional[float] = None
    average_grade: Optional[float] = None
    engagement_score: Optional[float] = None
    dropout_rate: Optional[float] = None
    satisfaction_score: Optional[float] = None

class CourseAnalytics(CourseAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EnrollmentAnalyticsBase(BaseModel):
    enrollment_id: int = Field(..., description="Enrollment ID")
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    final_grade: Optional[float] = Field(None, description="Final grade")
    engagement_level: EngagementLevel = Field(EngagementLevel.LOW, description="Engagement level")
    dropout_reason: Optional[str] = Field(None, description="Reason for dropout")

class EnrollmentAnalyticsCreate(EnrollmentAnalyticsBase):
    pass

class EnrollmentAnalyticsUpdate(BaseModel):
    completion_date: Optional[datetime] = None
    time_to_completion: Optional[float] = None
    progress_percentage: Optional[float] = None
    final_grade: Optional[float] = None
    engagement_level: Optional[EngagementLevel] = None
    dropout_reason: Optional[str] = None

class EnrollmentAnalytics(EnrollmentAnalyticsBase):
    id: int
    enrollment_date: datetime
    completion_date: Optional[datetime] = None
    time_to_completion: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AssessmentAnalyticsBase(BaseModel):
    assessment_id: int = Field(..., description="Assessment ID")
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    score: Optional[float] = Field(None, description="Assessment score")
    max_score: float = Field(..., description="Maximum possible score")
    percentage: Optional[float] = Field(None, description="Score percentage")
    time_taken: Optional[float] = Field(None, description="Time taken in minutes")
    attempts: int = Field(1, description="Number of attempts")
    passed: bool = Field(False, description="Whether the assessment was passed")

class AssessmentAnalyticsCreate(AssessmentAnalyticsBase):
    pass

class AssessmentAnalyticsUpdate(BaseModel):
    score: Optional[float] = None
    percentage: Optional[float] = None
    time_taken: Optional[float] = None
    attempts: Optional[int] = None
    passed: Optional[bool] = None

class AssessmentAnalytics(AssessmentAnalyticsBase):
    id: int
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressAnalyticsBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    module_id: Optional[int] = Field(None, description="Module ID")
    activity_type: ActivityType = Field(..., description="Type of activity")
    activity_duration: Optional[float] = Field(None, description="Activity duration in minutes")
    activity_score: Optional[float] = Field(None, description="Activity score")
    completion_status: CompletionStatus = Field(CompletionStatus.IN_PROGRESS, description="Completion status")
    activity_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional activity data")

class ProgressAnalyticsCreate(ProgressAnalyticsBase):
    pass

class ProgressAnalyticsUpdate(BaseModel):
    activity_duration: Optional[float] = None
    activity_score: Optional[float] = None
    completion_status: Optional[CompletionStatus] = None
    activity_metadata: Optional[Dict[str, Any]] = None

class ProgressAnalytics(ProgressAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SystemAnalyticsBase(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Value of the metric")
    metric_type: MetricType = Field(..., description="Type of metric")
    category: str = Field(..., description="Category of the metric")
    period: PeriodType = Field(..., description="Time period")
    period_date: datetime = Field(..., description="Date for the period")

class SystemAnalyticsCreate(SystemAnalyticsBase):
    pass

class SystemAnalyticsUpdate(BaseModel):
    metric_value: Optional[float] = None
    period_date: Optional[datetime] = None

class SystemAnalytics(SystemAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearningPathAnalyticsBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    path_id: Optional[int] = Field(None, description="Learning path ID")
    recommended_courses: Optional[List[int]] = Field(None, description="List of recommended course IDs")
    completion_rate: float = Field(0.0, description="Completion rate percentage")
    time_to_complete_path: Optional[float] = Field(None, description="Time to complete path in days")
    skill_gaps: Optional[Dict[str, Any]] = Field(None, description="Identified skill gaps")
    next_recommendations: Optional[Dict[str, Any]] = Field(None, description="Next recommended actions")

class LearningPathAnalyticsCreate(LearningPathAnalyticsBase):
    pass

class LearningPathAnalyticsUpdate(BaseModel):
    recommended_courses: Optional[List[int]] = None
    completion_rate: Optional[float] = None
    time_to_complete_path: Optional[float] = None
    skill_gaps: Optional[Dict[str, Any]] = None
    next_recommendations: Optional[Dict[str, Any]] = None

class LearningPathAnalytics(LearningPathAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics Summary and Dashboard schemas
class AnalyticsSummary(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int
    active_enrollments: int
    completion_rate: float
    average_grade: float
    total_assessments: int
    average_engagement_score: float

class UserDashboardAnalytics(BaseModel):
    user_id: int
    total_courses_enrolled: int
    completed_courses: int
    average_grade: float
    engagement_score: float
    recent_activities: List[Dict[str, Any]]
    learning_path_progress: Optional[Dict[str, Any]] = None
    recommended_courses: List[int] = []

class CoursePerformanceAnalytics(BaseModel):
    course_id: int
    enrollment_count: int
    completion_rate: float
    average_grade: float
    average_completion_time: float
    engagement_score: float
    dropout_rate: float
    satisfaction_score: float
    assessment_performance: List[Dict[str, Any]] = []

class SystemMetrics(BaseModel):
    period: PeriodType
    period_date: datetime
    metrics: List[SystemAnalytics]

# Response schemas
class AnalyticsResponse(BaseModel):
    success: bool
    data: Any
    message: str

class UserAnalyticsResponse(AnalyticsResponse):
    data: UserAnalytics

class CourseAnalyticsResponse(AnalyticsResponse):
    data: CourseAnalytics

class EnrollmentAnalyticsResponse(AnalyticsResponse):
    data: EnrollmentAnalytics

class AssessmentAnalyticsResponse(AnalyticsResponse):
    data: AssessmentAnalytics

class ProgressAnalyticsResponse(AnalyticsResponse):
    data: ProgressAnalytics

class SystemAnalyticsResponse(AnalyticsResponse):
    data: SystemAnalytics

class LearningPathAnalyticsResponse(AnalyticsResponse):
    data: LearningPathAnalytics

class AnalyticsSummaryResponse(AnalyticsResponse):
    data: AnalyticsSummary

class UserDashboardResponse(AnalyticsResponse):
    data: UserDashboardAnalytics

class CoursePerformanceResponse(AnalyticsResponse):
    data: CoursePerformanceAnalytics

class SystemMetricsResponse(AnalyticsResponse):
    data: SystemMetrics 