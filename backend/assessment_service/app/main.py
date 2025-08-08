from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db

app = FastAPI(title="Assessment Service", version="1.0.0")

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


# Question endpoints
@app.post("/api/v1/questions", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_create: schemas.QuestionCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.Question:
    """Create a new question."""
    question = await crud.create_question(db, question_create)
    return schemas.Question.from_orm(question)


@app.get("/api/v1/questions/{question_id}", response_model=schemas.Question)
async def get_question(
    question_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Question:
    """Get question by ID."""
    question = await crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return schemas.Question.from_orm(question)


@app.get("/api/v1/questions/course/{course_id}", response_model=List[schemas.Question])
async def get_questions_by_course(
    course_id: int,
    active_only: bool = Query(True, description="Filter only active questions"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Question]:
    """Get all questions for a course."""
    questions = await crud.get_questions_by_course(db, course_id, active_only)
    return [schemas.Question.from_orm(q) for q in questions]


@app.get("/api/v1/questions/assessment/{assessment_id}", response_model=List[schemas.Question])
async def get_questions_by_assessment(
    assessment_id: int,
    active_only: bool = Query(True, description="Filter only active questions"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Question]:
    """Get all questions for an assessment."""
    questions = await crud.get_questions_by_assessment(db, assessment_id, active_only)
    return [schemas.Question.from_orm(q) for q in questions]


@app.put("/api/v1/questions/{question_id}", response_model=schemas.Question)
async def update_question(
    question_id: int,
    question_update: schemas.QuestionUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.Question:
    """Update question."""
    question = await crud.update_question(db, question_id, question_update)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return schemas.Question.from_orm(question)


@app.delete("/api/v1/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    """Soft delete question."""
    success = await crud.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return None


# Assessment endpoints
@app.post("/api/v1/assessments", response_model=schemas.AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_create: schemas.AssessmentCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AssessmentResponse:
    """Create a new assessment."""
    assessment = await crud.create_assessment(db, assessment_create)
    return schemas.AssessmentResponse(
        assessment=schemas.Assessment.from_orm(assessment),
        message="Assessment created successfully"
    )


@app.get("/api/v1/assessments/{assessment_id}", response_model=schemas.Assessment)
async def get_assessment(
    assessment_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Assessment:
    """Get assessment by ID."""
    assessment = await crud.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return schemas.Assessment.from_orm(assessment)


@app.get("/api/v1/assessments/course/{course_id}", response_model=List[schemas.Assessment])
async def get_assessments_by_course(
    course_id: int,
    active_only: bool = Query(True, description="Filter only active assessments"),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Assessment]:
    """Get all assessments for a course."""
    assessments = await crud.get_assessments_by_course(db, course_id, active_only)
    return [schemas.Assessment.from_orm(a) for a in assessments]


@app.put("/api/v1/assessments/{assessment_id}", response_model=schemas.AssessmentResponse)
async def update_assessment(
    assessment_id: int,
    assessment_update: schemas.AssessmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AssessmentResponse:
    """Update assessment."""
    assessment = await crud.update_assessment(db, assessment_id, assessment_update)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return schemas.AssessmentResponse(
        assessment=schemas.Assessment.from_orm(assessment),
        message="Assessment updated successfully"
    )


@app.delete("/api/v1/assessments/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    """Soft delete assessment."""
    success = await crud.delete_assessment(db, assessment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return None


# Submission endpoints
@app.post("/api/v1/submissions", response_model=schemas.AssessmentSubmission, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission_create: schemas.AssessmentSubmissionCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AssessmentSubmission:
    """Submit an assessment."""
    submission = await crud.create_submission(db, submission_create)
    return schemas.AssessmentSubmission.from_orm(submission)


@app.get("/api/v1/submissions/{submission_id}", response_model=schemas.AssessmentSubmission)
async def get_submission(
    submission_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentSubmission:
    """Get submission by ID."""
    submission = await crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return schemas.AssessmentSubmission.from_orm(submission)


@app.get("/api/v1/submissions/user/{user_id}", response_model=List[schemas.AssessmentSubmission])
async def get_submissions_by_user(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.AssessmentSubmission]:
    """Get all submissions for a user."""
    submissions = await crud.get_submissions_by_user(db, user_id)
    return [schemas.AssessmentSubmission.from_orm(s) for s in submissions]


@app.get("/api/v1/submissions/assessment/{assessment_id}", response_model=List[schemas.AssessmentSubmission])
async def get_submissions_by_assessment(
    assessment_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.AssessmentSubmission]:
    """Get all submissions for an assessment."""
    submissions = await crud.get_submissions_by_assessment(db, assessment_id)
    return [schemas.AssessmentSubmission.from_orm(s) for s in submissions]


@app.get("/api/v1/submissions/user/{user_id}/assessment/{assessment_id}", response_model=List[schemas.AssessmentSubmission])
async def get_submissions_by_user_and_assessment(
    user_id: int, assessment_id: int, db: AsyncSession = Depends(get_db)
) -> List[schemas.AssessmentSubmission]:
    """Get all submissions for a user and assessment."""
    submissions = await crud.get_submissions_by_user_and_assessment(db, user_id, assessment_id)
    return [schemas.AssessmentSubmission.from_orm(s) for s in submissions]


# Grading endpoints
@app.post("/api/v1/submissions/{submission_id}/auto-grade", response_model=schemas.AssessmentSubmission)
async def auto_grade_submission(
    submission_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentSubmission:
    """Automatically grade a submission."""
    submission = await crud.auto_grade_submission(db, submission_id)
    return schemas.AssessmentSubmission.from_orm(submission)


@app.post("/api/v1/submissions/grade", response_model=schemas.AssessmentSubmission)
async def manual_grade_submission(
    grading_request: schemas.GradingRequest,
    db: AsyncSession = Depends(get_db),
) -> schemas.AssessmentSubmission:
    """Manually grade a submission."""
    submission = await crud.manual_grade_submission(db, grading_request)
    return schemas.AssessmentSubmission.from_orm(submission)


# Statistics endpoints
@app.get("/api/v1/stats/course/{course_id}", response_model=schemas.AssessmentStats)
async def get_course_assessment_stats(
    course_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentStats:
    """Get assessment statistics for a course."""
    stats = await crud.get_assessment_stats(db, course_id=course_id)
    return schemas.AssessmentStats(**stats)


@app.get("/api/v1/stats/assessment/{assessment_id}", response_model=schemas.AssessmentStats)
async def get_assessment_stats(
    assessment_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentStats:
    """Get statistics for a specific assessment."""
    stats = await crud.get_assessment_stats(db, assessment_id=assessment_id)
    return schemas.AssessmentStats(**stats)


@app.get("/api/v1/stats/overall", response_model=schemas.AssessmentStats)
async def get_overall_assessment_stats(
    db: AsyncSession = Depends(get_db)
) -> schemas.AssessmentStats:
    """Get overall assessment statistics."""
    stats = await crud.get_assessment_stats(db)
    return schemas.AssessmentStats(**stats)