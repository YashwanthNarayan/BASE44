from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from backend.models.user import Subject, DifficultyLevel, QuestionType

class PracticeQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None  # For MCQ questions
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: DifficultyLevel
    subject: Subject
    topic: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PracticeTestRequest(BaseModel):
    subject: Subject
    topics: List[str]
    difficulty: DifficultyLevel
    question_count: int = 5
    question_types: Optional[List[QuestionType]] = None

class StudentQuestionHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    question_id: str
    subject: Subject
    seen_count: int = 1
    last_seen: datetime = Field(default_factory=datetime.utcnow)

class PracticeAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    questions: List[str]  # Question IDs
    student_answers: Dict[str, str]  # Question ID -> Answer
    score: float
    total_questions: int
    subject: Subject
    difficulty: DifficultyLevel
    time_taken: int  # in seconds
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class TestSubmissionRequest(BaseModel):
    questions: List[str]  # Question IDs
    student_answers: Dict[str, str]  # Question ID -> Answer
    subject: str
    time_taken: int  # in seconds
    difficulty: Optional[str] = "medium"
    question_data: Optional[List[Dict[str, Any]]] = None  # For scheduled tests with embedded questions

class CompleteTestRequest(BaseModel):
    score: float