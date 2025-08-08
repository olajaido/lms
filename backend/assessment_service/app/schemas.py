from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator
from .models import QuestionType, AssessmentType


class QuestionBase(BaseModel):
    course_id: int
    assessment_id: Optional[int] = None
    text: str
    type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: int = 1
    explanation: Optional[str] = None
    
    @field_validator('points')
    @classmethod
    def validate_points(cls, v):
        if v <= 0:
            raise ValueError('Points must be positive')
        return v


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = None
    explanation: Optional[str] = None
    is_active: Optional[bool] = None


class Question(QuestionBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    type: AssessmentType = AssessmentType.QUIZ
    total_points: int = 0
    time_limit: Optional[int] = None  # minutes
    passing_score: Optional[float] = None  # percentage
    allow_retakes: bool = False
    max_attempts: int = 1
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('total_points', 'max_attempts')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v
    
    @field_validator('passing_score')
    @classmethod
    def validate_passing_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Passing score must be between 0 and 100')
        return v


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AssessmentType] = None
    total_points: Optional[int] = None
    time_limit: Optional[int] = None
    passing_score: Optional[float] = None
    allow_retakes: Optional[bool] = None
    max_attempts: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Assessment(AssessmentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentSubmissionBase(BaseModel):
    assessment_id: int
    user_id: int
    answers: Dict[str, Any]  # {question_id: answer}
    time_taken: Optional[int] = None  # seconds


class AssessmentSubmissionCreate(AssessmentSubmissionBase):
    pass


class AssessmentSubmission(AssessmentSubmissionBase):
    id: int
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    is_passed: Optional[bool] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None
    feedback: Optional[str] = None
    attempt_number: int

    class Config:
        from_attributes = True


class QuestionResponseBase(BaseModel):
    submission_id: int
    question_id: int
    user_answer: str
    max_points: float


class QuestionResponseCreate(QuestionResponseBase):
    pass


class QuestionResponse(QuestionResponseBase):
    id: int
    is_correct: Optional[bool] = None
    points_earned: float
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None

    class Config:
        from_attributes = True


class AssessmentWithQuestions(Assessment):
    questions: List[Question] = []


class SubmissionWithResponses(AssessmentSubmission):
    question_responses: List[QuestionResponse] = []


class AssessmentStats(BaseModel):
    """Statistics for assessment analytics"""
    total_assessments: int
    total_submissions: int
    average_score: float
    pass_rate: float
    completion_rate: float


class GradingRequest(BaseModel):
    """Request model for grading submissions"""
    submission_id: int
    grader_id: int
    question_grades: Dict[int, Dict[str, Any]]  # {question_id: {score, feedback, is_correct}}


class AssessmentResponse(BaseModel):
    """Response model for assessment operations"""
    assessment: Assessment
    message: str
    success: bool = True