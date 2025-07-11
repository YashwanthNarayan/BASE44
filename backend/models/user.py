from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uuid

# Enums
class GradeLevel(str, Enum):
    SIXTH = "6th"
    SEVENTH = "7th"
    EIGHTH = "8th"
    NINTH = "9th"
    TENTH = "10th"
    ELEVENTH = "11th"
    TWELFTH = "12th"

class Subject(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    ENGLISH = "english"
    HISTORY = "history"
    GEOGRAPHY = "geography"

class UserType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    NUMERICAL = "numerical"

# User Models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    user_type: UserType
    grade_level: Optional[GradeLevel] = None
    school_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    name: str
    user_type: UserType
    grade_level: Optional[GradeLevel] = None
    school_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class StudentProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    email: str
    grade_level: GradeLevel
    joined_classes: List[str] = []
    total_messages: int = 0
    total_tests: int = 0
    average_score: float = 0.0
    recent_scores: List[dict] = []
    study_streak: int = 0
    total_study_time: int = 0  # in minutes
    achievements: List[dict] = []
    xp_points: int = 0
    level: int = 1
    subjects_studied: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TeacherProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    email: str
    school_name: str
    subjects_taught: List[Subject] = []
    created_classes: List[str] = []
    total_students: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)