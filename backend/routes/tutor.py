from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.utils.security import get_current_student
from backend.services.ai_service import AIService
from backend.models.user import Subject
from backend.models.chat import ChatMessage, ChatSession

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

# Request/Response models
class CreateSessionRequest(BaseModel):
    subject: Subject
    session_type: str = "tutoring"

class SendMessageRequest(BaseModel):
    message: str
    subject: Subject
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    subject: str
    started_at: datetime
    last_activity: datetime
    message_count: int
    topics_covered: List[str]
    is_active: bool

class MessageResponse(BaseModel):
    id: str
    session_id: str
    message: str
    response: str
    timestamp: datetime
    message_type: str

class ChatResponse(BaseModel):
    message_id: str
    response: str
    session_id: str
    timestamp: datetime

# Initialize AI service
ai_service = AIService()

@router.post("/session", response_model=SessionResponse)
async def create_chat_session(
    request: CreateSessionRequest,
    current_user = Depends(get_current_student)
):
    """Create a new chat session"""
    try:
        db = get_database()
        
        # Create new session
        session = ChatSession(
            user_id=current_user["sub"],
            subject=request.subject,
            session_type=request.session_type
        )
        
        # Convert to dict and save to database
        session_dict = session.dict()
        session_dict["started_at"] = session.started_at
        session_dict["last_activity"] = session.last_activity
        
        result = await db[Collections.CHAT_SESSIONS].insert_one(session_dict)
        
        return SessionResponse(
            session_id=session.id,
            subject=session.subject.value,
            started_at=session.started_at,
            last_activity=session.last_activity,
            message_count=session.message_count,
            topics_covered=session.topics_covered,
            is_active=session.is_active
        )
        
    except Exception as e:
        print(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@router.post("/chat", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    current_user = Depends(get_current_student)
):
    """Send a message and get AI response"""
    try:
        db = get_database()
        
        # Verify session exists and belongs to user
        session = await db[Collections.CHAT_SESSIONS].find_one({
            "id": request.session_id,
            "user_id": current_user["sub"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get previous messages for context
        previous_messages = await db[Collections.CHAT_MESSAGES].find({
            "session_id": request.session_id
        }).sort("timestamp", -1).limit(5).to_list(length=5)
        
        # Build context from previous messages
        context = {
            "learning_insights": [],
            "conversation_history": []
        }
        
        for msg in reversed(previous_messages):
            context["conversation_history"].append({
                "user": msg.get("message", ""),
                "assistant": msg.get("response", "")
            })
        
        # Generate AI response
        ai_response = await ai_service.generate_tutor_response(
            message=request.message,
            subject=request.subject,
            context=context
        )
        
        # Create chat message
        chat_message = ChatMessage(
            session_id=request.session_id,
            user_id=current_user["sub"],
            message=request.message,
            response=ai_response,
            subject=request.subject,
            context=context
        )
        
        # Save message to database
        message_dict = chat_message.dict()
        message_dict["timestamp"] = chat_message.timestamp
        await db[Collections.CHAT_MESSAGES].insert_one(message_dict)
        
        # Update session last activity and message count
        await db[Collections.CHAT_SESSIONS].update_one(
            {"id": request.session_id},
            {
                "$set": {"last_activity": datetime.utcnow()},
                "$inc": {"message_count": 1}
            }
        )
        
        return ChatResponse(
            message_id=chat_message.id,
            response=ai_response,
            session_id=request.session_id,
            timestamp=chat_message.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/sessions", response_model=List[SessionResponse])
async def get_chat_sessions(
    current_user = Depends(get_current_student)
):
    """Get all chat sessions for the current user"""
    try:
        db = get_database()
        
        sessions = await db[Collections.CHAT_SESSIONS].find({
            "user_id": current_user["sub"]
        }).sort("last_activity", -1).to_list(length=100)
        
        result = []
        for session in sessions:
            result.append(SessionResponse(
                session_id=session["id"],
                subject=session["subject"],
                started_at=session["started_at"],
                last_activity=session["last_activity"],
                message_count=session.get("message_count", 0),
                topics_covered=session.get("topics_covered", []),
                is_active=session.get("is_active", True)
            ))
        
        return result
        
    except Exception as e:
        print(f"Error getting chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")

@router.get("/session/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    current_user = Depends(get_current_student)
):
    """Get all messages for a specific session"""
    try:
        db = get_database()
        
        # Verify session belongs to user
        session = await db[Collections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": current_user["user_id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        messages = await db[Collections.CHAT_MESSAGES].find({
            "session_id": session_id
        }).sort("timestamp", 1).to_list(length=1000)
        
        result = []
        for message in messages:
            result.append(MessageResponse(
                id=message["id"],
                session_id=message["session_id"],
                message=message["message"],
                response=message.get("response", ""),
                timestamp=message["timestamp"],
                message_type=message.get("message_type", "question")
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session messages")

@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user = Depends(get_current_student)
):
    """Delete a chat session and all its messages"""
    try:
        db = get_database()
        
        # Verify session belongs to user
        session = await db[Collections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": current_user["user_id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Delete all messages in the session
        await db[Collections.CHAT_MESSAGES].delete_many({
            "session_id": session_id
        })
        
        # Delete the session
        await db[Collections.CHAT_SESSIONS].delete_one({
            "id": session_id
        })
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

@router.patch("/session/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    current_user = Depends(get_current_student)
):
    """Update session title/name"""
    try:
        db = get_database()
        
        # Verify session belongs to user
        session = await db[Collections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": current_user["user_id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Update session title
        await db[Collections.CHAT_SESSIONS].update_one(
            {"id": session_id},
            {"$set": {"session_title": title}}
        )
        
        return {"message": "Session title updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating session title: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session title")