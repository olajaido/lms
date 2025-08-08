from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructor: str
    category: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    students_enrolled: Optional[int] = 0
    status: Optional[str] = "active"


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    students_enrolled: Optional[int] = None
    status: Optional[str] = None


class Course(CourseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True