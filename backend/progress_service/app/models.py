from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum

Base = declarative_base()


class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class ActivityType(str, Enum):
    LESSON_VIEWED = "lesson_viewed"
    ASSESSMENT_COMPLETED = "assessment_completed"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    QUIZ_TAKEN = "quiz_taken"
    RESOURCE_ACCESSED = "resource_accessed"
    DISCUSSION_PARTICIPATED = "discussion_participated"


class Progress(Base):
    """Tracks a student's progress through a course."""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    status = Column(String, default=ProgressStatus.NOT_STARTED, nullable=False)
    completion_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    total_lessons = Column(Integer, default=0)
    completed_lessons = Column(Integer, default=0)
    total_assessments = Column(Integer, default=0)
    completed_assessments = Column(Integer, default=0)
    total_assignments = Column(Integer, default=0)
    completed_assignments = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)  # Total time spent in seconds
    last_accessed = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    certificate_earned = Column(Boolean, default=False)
    certificate_issued_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)  # For admin notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProgressActivity(Base):
    """Tracks individual activities that contribute to progress."""
    __tablename__ = "progress_activities"

    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    activity_type = Column(String, nullable=False)
    activity_id = Column(Integer, nullable=True)  # ID of the specific activity (lesson, assessment, etc.)
    activity_title = Column(String, nullable=True)
    duration = Column(Integer, default=0)  # Time spent in seconds
    score = Column(Float, nullable=True)  # For assessments/quizzes
    max_score = Column(Float, nullable=True)
    completed = Column(Boolean, default=False)
    activity_metadata = Column(JSON, nullable=True)  # Additional activity-specific data
    created_at = Column(DateTime, default=datetime.utcnow)


class CourseModule(Base):
    """Represents modules/sections within a course for detailed progress tracking."""
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)  # For ordering modules
    total_lessons = Column(Integer, default=0)
    total_assessments = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModuleProgress(Base):
    """Tracks progress within individual course modules."""
    __tablename__ = "module_progress"

    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    completion_percentage = Column(Float, default=0.0)
    completed_lessons = Column(Integer, default=0)
    completed_assessments = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)  # Time spent in seconds
    last_accessed = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPath(Base):
    """Represents learning paths or tracks within a course."""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # Estimated time in minutes
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite course IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)