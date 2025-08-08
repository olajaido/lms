from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class UserAnalytics(Base):
    """User analytics and behavior tracking."""
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_duration = Column(Float, default=0.0)  # in minutes
    login_count = Column(Integer, default=0)
    last_login = Column(DateTime, default=func.now())
    total_courses_enrolled = Column(Integer, default=0)
    completed_courses = Column(Integer, default=0)
    average_grade = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)  # calculated engagement metric
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CourseAnalytics(Base):
    """Course performance and engagement analytics."""
    __tablename__ = "course_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, index=True, nullable=False)
    total_enrollments = Column(Integer, default=0)
    active_enrollments = Column(Integer, default=0)
    completed_enrollments = Column(Integer, default=0)
    average_completion_time = Column(Float, default=0.0)  # in days
    average_grade = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    dropout_rate = Column(Float, default=0.0)  # percentage
    satisfaction_score = Column(Float, default=0.0)  # from reviews
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class EnrollmentAnalytics(Base):
    """Detailed enrollment analytics and trends."""
    __tablename__ = "enrollment_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    course_id = Column(Integer, index=True, nullable=False)
    enrollment_date = Column(DateTime, default=func.now())
    completion_date = Column(DateTime, nullable=True)
    time_to_completion = Column(Float, nullable=True)  # in days
    progress_percentage = Column(Float, default=0.0)
    final_grade = Column(Float, nullable=True)
    engagement_level = Column(String(20), default="low")  # low, medium, high
    dropout_reason = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AssessmentAnalytics(Base):
    """Assessment and quiz performance analytics."""
    __tablename__ = "assessment_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    course_id = Column(Integer, index=True, nullable=False)
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=True)
    time_taken = Column(Float, nullable=True)  # in minutes
    attempts = Column(Integer, default=1)
    passed = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ProgressAnalytics(Base):
    """Detailed progress tracking analytics."""
    __tablename__ = "progress_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    course_id = Column(Integer, index=True, nullable=False)
    module_id = Column(Integer, index=True, nullable=True)
    activity_type = Column(String(50), nullable=False)  # video_watch, quiz_taken, assignment_submitted, etc.
    activity_duration = Column(Float, nullable=True)  # in minutes
    activity_score = Column(Float, nullable=True)
    completion_status = Column(String(20), default="in_progress")  # not_started, in_progress, completed
    activity_metadata = Column(JSON, nullable=True)  # additional activity data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SystemAnalytics(Base):
    """System-wide analytics and metrics."""
    __tablename__ = "system_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # count, percentage, average, etc.
    category = Column(String(50), nullable=False)  # users, courses, enrollments, etc.
    period = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    period_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class LearningPathAnalytics(Base):
    """Learning path and recommendation analytics."""
    __tablename__ = "learning_path_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    path_id = Column(Integer, index=True, nullable=True)
    recommended_courses = Column(JSON, nullable=True)  # list of recommended course IDs
    completion_rate = Column(Float, default=0.0)
    time_to_complete_path = Column(Float, nullable=True)  # in days
    skill_gaps = Column(JSON, nullable=True)  # identified skill gaps
    next_recommendations = Column(JSON, nullable=True)  # next recommended actions
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 