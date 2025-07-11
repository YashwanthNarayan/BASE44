from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from backend.models.user import Subject, GradeLevel

class StudentNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: Subject
    topic: str
    content: str
    grade_level: GradeLevel
    is_favorite: bool = False
    tags: List[str] = []
    word_count: int = 0
    reading_time: int = 0  # estimated reading time in minutes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotesRequest(BaseModel):
    subject: Subject
    topic: str
    grade_level: GradeLevel

class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    event_type: str  # study, assignment, exam, personal
    subject: Optional[Subject] = None
    start_time: datetime
    end_time: datetime
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    reminder_minutes: int = 15
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MindfulnessActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str  # breathing, meditation, body_scan, gratitude
    duration: int  # in minutes
    mood_before: str
    mood_after: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str  # achievement, reminder, message, assignment, grade
    is_read: bool = False
    action_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None