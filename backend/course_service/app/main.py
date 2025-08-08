from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db, async_session

app = FastAPI(title="Course Management Service", version="1.0.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # Add sample data
    async with async_session() as db:
        await add_sample_data(db)

async def add_sample_data(db: AsyncSession):
    """Add sample courses to the database."""
    from . import crud, schemas
    
    # Check if we already have courses
    existing_courses = await crud.get_courses(db, skip=0, limit=10)
    if existing_courses:
        return  # Already have data
    
    sample_courses = [
        {
            "title": "Introduction to React",
            "description": "Learn the fundamentals of React and build modern web applications.",
            "instructor": "John Doe",
            "category": "Programming",
            "level": "Beginner",
            "duration": "8 weeks",
            "price": 49.99,
            "rating": 4.8,
            "students_enrolled": 1250
        },
        {
            "title": "Advanced JavaScript",
            "description": "Master advanced JavaScript concepts and modern ES6+ features.",
            "instructor": "Jane Smith",
            "category": "Programming",
            "level": "Intermediate",
            "duration": "10 weeks",
            "price": 69.99,
            "rating": 4.9,
            "students_enrolled": 890
        },
        {
            "title": "UI/UX Design Principles",
            "description": "Learn the fundamentals of user interface and user experience design.",
            "instructor": "Mike Johnson",
            "category": "Design",
            "level": "Beginner",
            "duration": "6 weeks",
            "price": 39.99,
            "rating": 4.7,
            "students_enrolled": 2100
        },
        {
            "title": "Digital Marketing Strategy",
            "description": "Develop comprehensive digital marketing strategies for business growth.",
            "instructor": "Sarah Wilson",
            "category": "Marketing",
            "level": "Advanced",
            "duration": "12 weeks",
            "price": 79.99,
            "rating": 4.6,
            "students_enrolled": 1560
        },
        {
            "title": "Data Science Fundamentals",
            "description": "Introduction to data science, machine learning, and statistical analysis.",
            "instructor": "David Chen",
            "category": "Data Science",
            "level": "Intermediate",
            "duration": "14 weeks",
            "price": 89.99,
            "rating": 4.9,
            "students_enrolled": 980
        }
    ]
    
    for course_data in sample_courses:
        course_create = schemas.CourseCreate(**course_data)
        await crud.create_course(db, course_create)
    
    print("✅ Sample courses added to database")


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/courses", response_model=List[schemas.Course])
async def list_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[schemas.Course]:
    courses = await crud.get_courses(db, skip=skip, limit=limit)
    return [schemas.Course.from_orm(c) for c in courses]


@app.post("/api/v1/courses", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_create: schemas.CourseCreate, db: AsyncSession = Depends(get_db)
) -> schemas.Course:
    course = await crud.create_course(db, course_create)
    return schemas.Course.from_orm(course)


@app.get("/api/v1/courses/{course_id}", response_model=schemas.Course)
async def get_course(
    course_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Course:
    course = await crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return schemas.Course.from_orm(course)


@app.put("/api/v1/courses/{course_id}", response_model=schemas.Course)
async def update_course(
    course_id: int,
    update: schemas.CourseUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.Course:
    course = await crud.update_course(db, course_id, update)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return schemas.Course.from_orm(course)


@app.delete("/api/v1/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    success = await crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return None