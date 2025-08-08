from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Course(Base):
    """Database model representing a course."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    instructor = Column(String, nullable=False)
    category = Column(String, nullable=True)
    level = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    students_enrolled = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)