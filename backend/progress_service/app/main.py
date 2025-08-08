from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db

app = FastAPI(title="Progress Service", version="1.0.0")

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


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Progress endpoints
@app.post("/api/v1/progress", response_model=schemas.ProgressResponse, status_code=status.HTTP_201_CREATED)
async def create_progress(
    progress_create: schemas.ProgressCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ProgressResponse:
    """Create a new progress record."""
    progress = await crud.create_progress(db, progress_create)
    return schemas.ProgressResponse(
        progress=schemas.Progress.from_orm(progress),
        message="Progress record created successfully"
    )


@app.get("/api/v1/progress/{progress_id}", response_model=schemas.Progress)
async def get_progress(
    progress_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Progress:
    """Get progress by ID."""
    progress = await crud.get_progress(db, progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    return schemas.Progress.from_orm(progress)


@app.get("/api/v1/progress/user/{user_id}/course/{course_id}", response_model=schemas.Progress)
async def get_progress_by_user_and_course(
    user_id: int, course_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Progress:
    """Get progress by user and course combination."""
    progress = await crud.get_progress_by_user_and_course(db, user_id, course_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    return schemas.Progress.from_orm(progress)


@app.get("/api/v1/progress/user/{user_id}", response_model=List[schemas.Progress])
async def get_progress_by_user(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.Progress]:
    """Get all progress records for a user."""
    progress_records = await crud.get_progress_by_user(db, user_id)
    return [schemas.Progress.from_orm(p) for p in progress_records]


@app.get("/api/v1/progress/course/{course_id}", response_model=List[schemas.Progress])
async def get_progress_by_course(
    course_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.Progress]:
    """Get all progress records for a course."""
    progress_records = await crud.get_progress_by_course(db, course_id)
    return [schemas.Progress.from_orm(p) for p in progress_records]


@app.put("/api/v1/progress/{progress_id}", response_model=schemas.ProgressResponse)
async def update_progress(
    progress_id: int,
    progress_update: schemas.ProgressUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ProgressResponse:
    """Update progress record."""
    progress = await crud.update_progress(db, progress_id, progress_update)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    return schemas.ProgressResponse(
        progress=schemas.Progress.from_orm(progress),
        message="Progress updated successfully"
    )


@app.patch("/api/v1/progress/{progress_id}/completion", response_model=schemas.ProgressResponse)
async def update_progress_completion(
    progress_id: int,
    completion_percentage: float = Query(..., ge=0.0, le=100.0, description="Completion percentage (0.0-100.0)"),
    db: AsyncSession = Depends(get_db),
) -> schemas.ProgressResponse:
    """Update progress completion percentage."""
    progress = await crud.update_progress_completion(db, progress_id, completion_percentage)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    message = "Progress updated successfully"
    if progress.completion_percentage == 100.0:
        message = "Course completed! Certificate earned!"
    
    return schemas.ProgressResponse(
        progress=schemas.Progress.from_orm(progress),
        message=message
    )


# Activity tracking endpoints
@app.post("/api/v1/activities", response_model=schemas.ActivityLogResponse, status_code=status.HTTP_201_CREATED)
async def log_activity(
    activity_create: schemas.ProgressActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ActivityLogResponse:
    """Log a progress activity."""
    activity = await crud.log_activity(db, activity_create)
    return schemas.ActivityLogResponse(
        activity=schemas.ProgressActivity.from_orm(activity),
        message="Activity logged successfully"
    )


@app.get("/api/v1/activities/progress/{progress_id}", response_model=List[schemas.ProgressActivity])
async def get_activities_by_progress(
    progress_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.ProgressActivity]:
    """Get all activities for a progress record."""
    activities = await crud.get_activities_by_progress(db, progress_id)
    return [schemas.ProgressActivity.from_orm(a) for a in activities]


@app.get("/api/v1/activities/user/{user_id}", response_model=List[schemas.ProgressActivity])
async def get_activities_by_user(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of activities to return"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.ProgressActivity]:
    """Get recent activities for a user."""
    activities = await crud.get_activities_by_user(db, user_id, limit)
    return [schemas.ProgressActivity.from_orm(a) for a in activities]


# Course Module endpoints
@app.post("/api/v1/modules", response_model=schemas.CourseModule, status_code=status.HTTP_201_CREATED)
async def create_course_module(
    module_create: schemas.CourseModuleCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.CourseModule:
    """Create a new course module."""
    module = await crud.create_course_module(db, module_create)
    return schemas.CourseModule.from_orm(module)


@app.get("/api/v1/modules/course/{course_id}", response_model=List[schemas.CourseModule])
async def get_course_modules(
    course_id: int,
    active_only: bool = Query(True, description="Filter only active modules"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.CourseModule]:
    """Get all modules for a course."""
    modules = await crud.get_course_modules(db, course_id, active_only)
    return [schemas.CourseModule.from_orm(m) for m in modules]


@app.put("/api/v1/modules/{module_id}", response_model=schemas.CourseModule)
async def update_course_module(
    module_id: int,
    module_update: schemas.CourseModuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.CourseModule:
    """Update course module."""
    module = await crud.update_course_module(db, module_id, module_update)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return schemas.CourseModule.from_orm(module)


# Module Progress endpoints
@app.post("/api/v1/module-progress", response_model=schemas.ModuleProgress, status_code=status.HTTP_201_CREATED)
async def create_module_progress(
    module_progress_create: schemas.ModuleProgressCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ModuleProgress:
    """Create a new module progress record."""
    module_progress = await crud.create_module_progress(db, module_progress_create)
    return schemas.ModuleProgress.from_orm(module_progress)


@app.get("/api/v1/module-progress/{progress_id}/{module_id}", response_model=schemas.ModuleProgress)
async def get_module_progress(
    progress_id: int, module_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.ModuleProgress:
    """Get module progress by progress and module IDs."""
    module_progress = await crud.get_module_progress(db, progress_id, module_id)
    if not module_progress:
        raise HTTPException(status_code=404, detail="Module progress not found")
    return schemas.ModuleProgress.from_orm(module_progress)


@app.put("/api/v1/module-progress/{module_progress_id}", response_model=schemas.ModuleProgress)
async def update_module_progress(
    module_progress_id: int,
    module_progress_update: schemas.ModuleProgressUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ModuleProgress:
    """Update module progress."""
    module_progress = await crud.update_module_progress(db, module_progress_id, module_progress_update)
    if not module_progress:
        raise HTTPException(status_code=404, detail="Module progress not found")
    return schemas.ModuleProgress.from_orm(module_progress)


# Learning Path endpoints
@app.post("/api/v1/learning-paths", response_model=schemas.LearningPath, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    learning_path_create: schemas.LearningPathCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.LearningPath:
    """Create a new learning path."""
    learning_path = await crud.create_learning_path(db, learning_path_create)
    return schemas.LearningPath.from_orm(learning_path)


@app.get("/api/v1/learning-paths/course/{course_id}", response_model=List[schemas.LearningPath])
async def get_learning_paths(
    course_id: int,
    active_only: bool = Query(True, description="Filter only active learning paths"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.LearningPath]:
    """Get all learning paths for a course."""
    learning_paths = await crud.get_learning_paths(db, course_id, active_only)
    return [schemas.LearningPath.from_orm(lp) for lp in learning_paths]


# Statistics endpoints
@app.get("/api/v1/stats/user/{user_id}", response_model=schemas.ProgressStats)
async def get_user_progress_stats(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.ProgressStats:
    """Get progress statistics for a user."""
    stats = await crud.get_user_progress_stats(db, user_id)
    return schemas.ProgressStats(**stats)


@app.get("/api/v1/stats/course/{course_id}", response_model=schemas.CourseProgressStats)
async def get_course_progress_stats(
    course_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.CourseProgressStats:
    """Get progress statistics for a course."""
    stats = await crud.get_course_progress_stats(db, course_id)
    return schemas.CourseProgressStats(**stats)


@app.get("/api/v1/stats/overall", response_model=schemas.ProgressStats)
async def get_overall_progress_stats(
    db: AsyncSession = Depends(get_db)
) -> schemas.ProgressStats:
    """Get overall progress statistics."""
    stats = await crud.get_overall_progress_stats(db)
    return schemas.ProgressStats(**stats)