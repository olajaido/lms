from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import Course
from .schemas import CourseCreate, CourseUpdate


async def get_courses(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Course]:
    """
    Return a list of courses with pagination.
    """
    result = await db.execute(select(Course).offset(skip).limit(limit))
    return result.scalars().all()


async def get_course(db: AsyncSession, course_id: int) -> Optional[Course]:
    return await db.get(Course, course_id)


async def create_course(db: AsyncSession, course_create: CourseCreate) -> Course:
    db_course = Course(
        title=course_create.title,
        description=course_create.description,
        instructor=course_create.instructor,
        category=course_create.category,
        level=course_create.level,
        duration=course_create.duration,
        price=course_create.price,
        rating=course_create.rating,
        students_enrolled=course_create.students_enrolled,
        status=course_create.status,
    )
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


async def update_course(db: AsyncSession, course_id: int, update_data: CourseUpdate) -> Optional[Course]:
    course = await db.get(Course, course_id)
    if not course:
        return None
    if update_data.title is not None:
        course.title = update_data.title
    if update_data.description is not None:
        course.description = update_data.description
    if update_data.instructor is not None:
        course.instructor = update_data.instructor
    if update_data.category is not None:
        course.category = update_data.category
    if update_data.level is not None:
        course.level = update_data.level
    if update_data.duration is not None:
        course.duration = update_data.duration
    if update_data.price is not None:
        course.price = update_data.price
    if update_data.rating is not None:
        course.rating = update_data.rating
    if update_data.students_enrolled is not None:
        course.students_enrolled = update_data.students_enrolled
    if update_data.status is not None:
        course.status = update_data.status
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course_id: int) -> bool:
    course = await db.get(Course, course_id)
    if not course:
        return False
    await db.delete(course)
    await db.commit()
    return True