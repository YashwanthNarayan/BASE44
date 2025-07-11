from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from backend.models.user import Subject

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    message: str
    response: Optional[str] = None
    subject: Subject
    message_type: str = "question"  # question, clarification, explanation
    context: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Enhanced context for better conversation flow
    learning_insights: List[str] = []  # Key learning points from this conversation
    follow_up_suggestions: List[str] = []  # Suggested follow-up questions
    difficulty_level: Optional[str] = None  # easy, medium, hard
    conversation_flow: str = "continuing"  # starting, continuing, concluding

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: Subject
    session_type: str = "tutoring"  # tutoring, practice, review
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Enhanced session tracking
    message_count: int = 0
    topics_covered: List[str] = []
    learning_objectives: List[str] = []
    session_summary: Optional[str] = None
    is_active: bool = True