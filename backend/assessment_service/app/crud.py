from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status

from .models import (
    Question, Assessment, AssessmentSubmission, QuestionResponse,
    QuestionType, AssessmentType
)
from .schemas import (
    QuestionCreate, QuestionUpdate, AssessmentCreate, AssessmentUpdate,
    AssessmentSubmissionCreate, QuestionResponseCreate, GradingRequest
)


# Question CRUD operations
async def create_question(db: AsyncSession, question_create: QuestionCreate) -> Question:
    """Create a new question."""
    question = Question(**question_create.dict())
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def get_question(db: AsyncSession, question_id: int) -> Optional[Question]:
    """Get question by ID."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def get_questions_by_course(
    db: AsyncSession, course_id: int, active_only: bool = True
) -> List[Question]:
    """Get all questions for a course."""
    query = select(Question).where(Question.course_id == course_id)
    if active_only:
        query = query.where(Question.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def get_questions_by_assessment(
    db: AsyncSession, assessment_id: int, active_only: bool = True
) -> List[Question]:
    """Get all questions for an assessment."""
    query = select(Question).where(Question.assessment_id == assessment_id)
    if active_only:
        query = query.where(Question.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def update_question(
    db: AsyncSession, question_id: int, question_update: QuestionUpdate
) -> Optional[Question]:
    """Update question."""
    question = await get_question(db, question_id)
    if not question:
        return None
    
    update_data = question_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    question.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    """Soft delete question."""
    question = await get_question(db, question_id)
    if not question:
        return False
    
    question.is_active = False
    question.updated_at = datetime.utcnow()
    await db.commit()
    return True


# Assessment CRUD operations
async def create_assessment(db: AsyncSession, assessment_create: AssessmentCreate) -> Assessment:
    """Create a new assessment."""
    assessment = Assessment(**assessment_create.dict())
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


async def get_assessment(db: AsyncSession, assessment_id: int) -> Optional[Assessment]:
    """Get assessment by ID."""
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    return result.scalar_one_or_none()


async def get_assessments_by_course(
    db: AsyncSession, course_id: int, active_only: bool = True
) -> List[Assessment]:
    """Get all assessments for a course."""
    query = select(Assessment).where(Assessment.course_id == course_id)
    if active_only:
        query = query.where(Assessment.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def update_assessment(
    db: AsyncSession, assessment_id: int, assessment_update: AssessmentUpdate
) -> Optional[Assessment]:
    """Update assessment."""
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        return None
    
    update_data = assessment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    
    assessment.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(assessment)
    return assessment


async def delete_assessment(db: AsyncSession, assessment_id: int) -> bool:
    """Soft delete assessment."""
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        return False
    
    assessment.is_active = False
    assessment.updated_at = datetime.utcnow()
    await db.commit()
    return True


# Submission CRUD operations
async def create_submission(
    db: AsyncSession, submission_create: AssessmentSubmissionCreate
) -> AssessmentSubmission:
    """Create a new submission."""
    # Check if user has already submitted
    existing_submissions = await get_submissions_by_user_and_assessment(
        db, submission_create.user_id, submission_create.assessment_id
    )
    
    # Get assessment to check max attempts
    assessment = await get_assessment(db, submission_create.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if len(existing_submissions) >= assessment.max_attempts and not assessment.allow_retakes:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum attempts ({assessment.max_attempts}) reached for this assessment"
        )
    
    # Set attempt number
    attempt_number = len(existing_submissions) + 1
    
    submission = AssessmentSubmission(
        **submission_create.dict(),
        attempt_number=attempt_number
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def get_submission(db: AsyncSession, submission_id: int) -> Optional[AssessmentSubmission]:
    """Get submission by ID."""
    result = await db.execute(
        select(AssessmentSubmission).where(AssessmentSubmission.id == submission_id)
    )
    return result.scalar_one_or_none()


async def get_submissions_by_user(
    db: AsyncSession, user_id: int
) -> List[AssessmentSubmission]:
    """Get all submissions for a user."""
    result = await db.execute(
        select(AssessmentSubmission)
        .where(AssessmentSubmission.user_id == user_id)
        .order_by(desc(AssessmentSubmission.submitted_at))
    )
    return result.scalars().all()


async def get_submissions_by_assessment(
    db: AsyncSession, assessment_id: int
) -> List[AssessmentSubmission]:
    """Get all submissions for an assessment."""
    result = await db.execute(
        select(AssessmentSubmission)
        .where(AssessmentSubmission.assessment_id == assessment_id)
        .order_by(desc(AssessmentSubmission.submitted_at))
    )
    return result.scalars().all()


async def get_submissions_by_user_and_assessment(
    db: AsyncSession, user_id: int, assessment_id: int
) -> List[AssessmentSubmission]:
    """Get all submissions for a user and assessment."""
    result = await db.execute(
        select(AssessmentSubmission)
        .where(
            and_(
                AssessmentSubmission.user_id == user_id,
                AssessmentSubmission.assessment_id == assessment_id
            )
        )
        .order_by(desc(AssessmentSubmission.submitted_at))
    )
    return result.scalars().all()


# Grading functions
async def auto_grade_submission(db: AsyncSession, submission_id: int) -> AssessmentSubmission:
    """Automatically grade a submission for auto-gradable questions."""
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get assessment and questions
    assessment = await get_assessment(db, submission.assessment_id)
    questions = await get_questions_by_assessment(db, submission.assessment_id)
    
    if not assessment or not questions:
        raise HTTPException(status_code=404, detail="Assessment or questions not found")
    
    total_score = 0
    max_score = 0
    question_responses = []
    
    for question in questions:
        max_score += question.points
        user_answer = submission.answers.get(str(question.id), "")
        
        # Create question response
        question_response = QuestionResponse(
            submission_id=submission.id,
            question_id=question.id,
            user_answer=user_answer,
            max_points=question.points
        )
        
        # Auto-grade if possible
        if question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
            is_correct = user_answer == question.correct_answer
            points_earned = question.points if is_correct else 0
            question_response.is_correct = is_correct
            question_response.points_earned = points_earned
            question_response.graded_at = datetime.utcnow()
            total_score += points_earned
        else:
            # Manual grading required
            question_response.points_earned = 0
        
        question_responses.append(question_response)
    
    # Update submission
    submission.score = total_score
    submission.max_score = max_score
    submission.percentage = (total_score / max_score * 100) if max_score > 0 else 0
    submission.is_passed = (
        submission.percentage >= assessment.passing_score
        if assessment.passing_score is not None
        else None
    )
    submission.graded_at = datetime.utcnow()
    
    # Save question responses
    db.add_all(question_responses)
    await db.commit()
    await db.refresh(submission)
    
    return submission


async def manual_grade_submission(
    db: AsyncSession, grading_request: GradingRequest
) -> AssessmentSubmission:
    """Manually grade a submission."""
    submission = await get_submission(db, grading_request.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get assessment
    assessment = await get_assessment(db, submission.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    total_score = 0
    max_score = 0
    
    # Update question responses with manual grades
    for question_id, grade_data in grading_request.question_grades.items():
        question_response = await get_question_response_by_submission_and_question(
            db, submission.id, question_id
        )
        
        if question_response:
            question_response.points_earned = grade_data.get('score', 0)
            question_response.feedback = grade_data.get('feedback')
            question_response.is_correct = grade_data.get('is_correct')
            question_response.graded_at = datetime.utcnow()
            question_response.graded_by = grading_request.grader_id
            
            total_score += question_response.points_earned
            max_score += question_response.max_points
    
    # Update submission
    submission.score = total_score
    submission.max_score = max_score
    submission.percentage = (total_score / max_score * 100) if max_score > 0 else 0
    submission.is_passed = (
        submission.percentage >= assessment.passing_score
        if assessment.passing_score is not None
        else None
    )
    submission.graded_at = datetime.utcnow()
    submission.graded_by = grading_request.grader_id
    
    await db.commit()
    await db.refresh(submission)
    
    return submission


async def get_question_response_by_submission_and_question(
    db: AsyncSession, submission_id: int, question_id: int
) -> Optional[QuestionResponse]:
    """Get question response by submission and question."""
    result = await db.execute(
        select(QuestionResponse).where(
            and_(
                QuestionResponse.submission_id == submission_id,
                QuestionResponse.question_id == question_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_assessment_stats(
    db: AsyncSession, course_id: Optional[int] = None, assessment_id: Optional[int] = None
) -> Dict[str, Any]:
    """Get assessment statistics."""
    # Base queries
    assessment_query = select(Assessment)
    submission_query = select(AssessmentSubmission)
    
    if course_id:
        assessment_query = assessment_query.where(Assessment.course_id == course_id)
        # For submissions, we need to join with assessments
        submission_query = submission_query.join(Assessment).where(Assessment.course_id == course_id)
    
    if assessment_id:
        assessment_query = assessment_query.where(Assessment.id == assessment_id)
        submission_query = submission_query.where(AssessmentSubmission.assessment_id == assessment_id)
    
    # Get counts
    assessment_result = await db.execute(assessment_query)
    assessments = assessment_result.scalars().all()
    
    submission_result = await db.execute(submission_query)
    submissions = submission_result.scalars().all()
    
    # Calculate statistics
    total_assessments = len(assessments)
    total_submissions = len(submissions)
    
    if total_submissions == 0:
        return {
            "total_assessments": total_assessments,
            "total_submissions": 0,
            "average_score": 0.0,
            "pass_rate": 0.0,
            "completion_rate": 0.0
        }
    
    # Calculate averages
    graded_submissions = [s for s in submissions if s.score is not None]
    if graded_submissions:
        average_score = sum(s.percentage or 0 for s in graded_submissions) / len(graded_submissions)
        pass_rate = sum(1 for s in graded_submissions if s.is_passed) / len(graded_submissions) * 100
    else:
        average_score = 0.0
        pass_rate = 0.0
    
    # Completion rate (submissions vs total possible enrollments)
    completion_rate = 0.0  # Would need enrollment data to calculate properly
    
    return {
        "total_assessments": total_assessments,
        "total_submissions": total_submissions,
        "average_score": round(average_score, 2),
        "pass_rate": round(pass_rate, 2),
        "completion_rate": round(completion_rate, 2)
    }