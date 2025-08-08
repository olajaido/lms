from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum

Base = declarative_base()


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"
    SHORT_ANSWER = "short_answer"
    MATCHING = "matching"


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    PROJECT = "project"


class Question(Base):
    """Model representing a quiz or exam question."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    assessment_id = Column(Integer, nullable=True, index=True)  # For questions in specific assessments
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False, default=QuestionType.MULTIPLE_CHOICE)
    options = Column(JSON, nullable=True)  # For MCQ questions
    correct_answer = Column(String, nullable=True)
    points = Column(Integer, default=1)  # Points for this question
    explanation = Column(Text, nullable=True)  # Explanation of the answer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Assessment(Base):
    """Model representing a quiz, exam, or assignment."""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False, default=AssessmentType.QUIZ)
    total_points = Column(Integer, default=0)
    time_limit = Column(Integer, nullable=True)  # Time limit in minutes
    passing_score = Column(Float, nullable=True)  # Passing percentage
    is_active = Column(Boolean, default=True)
    allow_retakes = Column(Boolean, default=False)
    max_attempts = Column(Integer, default=1)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssessmentSubmission(Base):
    """Model representing a student's submission for an assessment."""
    __tablename__ = "assessment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    answers = Column(JSON, nullable=False)  # {question_id: answer}
    score = Column(Float, nullable=True)  # Calculated score
    max_score = Column(Float, nullable=True)  # Maximum possible score
    percentage = Column(Float, nullable=True)  # Score as percentage
    is_passed = Column(Boolean, nullable=True)  # Whether student passed
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime, nullable=True)
    graded_by = Column(Integer, nullable=True)  # User ID of grader
    feedback = Column(Text, nullable=True)  # General feedback
    attempt_number = Column(Integer, default=1)  # Which attempt this is
    time_taken = Column(Integer, nullable=True)  # Time taken in seconds


class QuestionResponse(Base):
    """Model representing individual question responses for detailed grading."""
    __tablename__ = "question_responses"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, nullable=False, index=True)
    question_id = Column(Integer, nullable=False, index=True)
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, default=0)
    max_points = Column(Float, nullable=False)
    feedback = Column(Text, nullable=True)  # Specific feedback for this question
    graded_at = Column(DateTime, nullable=True)
    graded_by = Column(Integer, nullable=True)