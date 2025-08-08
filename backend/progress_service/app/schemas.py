from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from .models import ProgressStatus, ActivityType


class ProgressBase(BaseModel):
    user_id: int
    course_id: int
    completion_percentage: float = 0.0
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    
    @field_validator('completion_percentage')
    @classmethod
    def validate_completion_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('Completion percentage must be between 0.0 and 100.0')
        return v


class ProgressCreate(ProgressBase):
    pass


class ProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    status: Optional[ProgressStatus] = None
    total_lessons: Optional[int] = None
    completed_lessons: Optional[int] = None
    total_assessments: Optional[int] = None
    completed_assessments: Optional[int] = None
    total_assignments: Optional[int] = None
    completed_assignments: Optional[int] = None
    time_spent: Optional[int] = None
    notes: Optional[str] = None
    
    @field_validator('completion_percentage')
    @classmethod
    def validate_completion_percentage(cls, v):
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError('Completion percentage must be between 0.0 and 100.0')
        return v


class Progress(ProgressBase):
    id: int
    total_lessons: int
    completed_lessons: int
    total_assessments: int
    completed_assessments: int
    total_assignments: int
    completed_assignments: int
    time_spent: int
    last_accessed: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    certificate_earned: bool
    certificate_issued_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgressActivityBase(BaseModel):
    progress_id: int
    user_id: int
    course_id: int
    activity_type: ActivityType
    activity_id: Optional[int] = None
    activity_title: Optional[str] = None
    duration: int = 0
    score: Optional[float] = None
    max_score: Optional[float] = None
    completed: bool = False
    activity_metadata: Optional[Dict[str, Any]] = None


class ProgressActivityCreate(ProgressActivityBase):
    pass


class ProgressActivity(ProgressActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CourseModuleBase(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    order_index: int = 0
    total_lessons: int = 0
    total_assessments: int = 0


class CourseModuleCreate(CourseModuleBase):
    pass


class CourseModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    total_lessons: Optional[int] = None
    total_assessments: Optional[int] = None
    is_active: Optional[bool] = None


class CourseModule(CourseModuleBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleProgressBase(BaseModel):
    progress_id: int
    module_id: int
    user_id: int
    completion_percentage: float = 0.0
    completed_lessons: int = 0
    completed_assessments: int = 0
    time_spent: int = 0


class ModuleProgressCreate(ModuleProgressBase):
    pass


class ModuleProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    completed_lessons: Optional[int] = None
    completed_assessments: Optional[int] = None
    time_spent: Optional[int] = None


class ModuleProgress(ModuleProgressBase):
    id: int
    last_accessed: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningPathBase(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    prerequisites: Optional[List[int]] = None


class LearningPathCreate(LearningPathBase):
    pass


class LearningPathUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    prerequisites: Optional[List[int]] = None
    is_active: Optional[bool] = None


class LearningPath(LearningPathBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    """Statistics for progress analytics"""
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    average_completion: float
    total_time_spent: int  # in seconds
    certificates_earned: int


class CourseProgressStats(BaseModel):
    """Statistics for a specific course"""
    total_students: int
    active_students: int
    completed_students: int
    average_completion: float
    average_time_spent: float
    completion_rate: float


class ProgressResponse(BaseModel):
    """Response model for progress operations"""
    progress: Progress
    message: str
    success: bool = True


class ActivityLogResponse(BaseModel):
    """Response model for activity logging"""
    activity: ProgressActivity
    message: str
    success: bool = True