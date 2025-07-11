from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from backend.models.user import Subject, GradeLevel

class ClassRoom(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    class_name: str
    subject: Subject
    teacher_id: str
    teacher_name: str
    grade_level: GradeLevel
    description: Optional[str] = None
    join_code: str
    student_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class JoinClassRequest(BaseModel):
    join_code: str