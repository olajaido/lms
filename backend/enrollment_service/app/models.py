from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum

Base = declarative_base()


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class Enrollment(Base):
    """Model linking a student to a course with enhanced tracking."""
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    status = Column(String, default=EnrollmentStatus.ACTIVE, nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    progress_percentage = Column(Integer, default=0)  # 0-100
    last_accessed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional fields for tracking
    certificate_issued = Column(Boolean, default=False)
    certificate_issued_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)  # For admin notes