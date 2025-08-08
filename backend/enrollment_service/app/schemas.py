from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator, field_validator
from .models import EnrollmentStatus


class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int
    
    @field_validator('user_id', 'course_id')
    @classmethod
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError('ID must be positive')
        return v


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatus] = None
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('progress_percentage')
    @classmethod
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Progress percentage must be between 0 and 100')
        return v


class Enrollment(EnrollmentBase):
    id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: int
    last_accessed: datetime
    is_active: bool
    certificate_issued: bool
    certificate_issued_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    """Response model for enrollment operations"""
    enrollment: Enrollment
    message: str
    success: bool = True


class EnrollmentStats(BaseModel):
    """Statistics for enrollment analytics"""
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    average_progress: float
    completion_rate: float