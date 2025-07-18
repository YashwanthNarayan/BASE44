from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from backend.utils.database import get_database, Collections
from backend.utils.security import get_current_student
from backend.services.ai_service import AIService
from backend.models.user import Subject

router = APIRouter(prefix="/api/study-planner", tags=["study-planner"])

# Request/Response models
class StudyRequirement(BaseModel):
    subject: str
    duration_minutes: int
    priority: Optional[str] = "medium"  # high, medium, low
    notes: Optional[str] = ""

class StudyPlanRequest(BaseModel):
    total_duration_minutes: int
    subjects: List[StudyRequirement]
    preferred_start_time: Optional[str] = None
    break_preferences: Optional[Dict[str, Any]] = None

class PomodoroSession(BaseModel):
    id: str
    session_type: str  # 'work' or 'break'
    subject: Optional[str] = None
    duration_minutes: int
    start_time: str
    end_time: str
    description: str
    break_activity: Optional[str] = None

class StudyPlanResponse(BaseModel):
    plan_id: str
    total_duration_minutes: int
    total_work_time: int
    total_break_time: int
    pomodoro_sessions: List[PomodoroSession]
    study_tips: List[str]
    created_at: datetime

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class BotResponse(BaseModel):
    response: str
    needs_input: bool
    input_type: Optional[str] = None  # 'subjects', 'duration', 'confirmation'
    suggested_actions: List[str] = []
    context: Optional[Dict[str, Any]] = None

# Initialize AI service
ai_service = AIService()

@router.post("/chat", response_model=BotResponse)
async def chat_with_planner_bot(
    request: ChatMessage,
    current_user = Depends(get_current_student)
):
    """Chat with the study planner bot to gather requirements"""
    try:
        # Analyze the student's message to understand their study needs
        bot_response = await ai_service.generate_study_planner_response(
            message=request.message,
            context=request.context,
            student_id=current_user["sub"]
        )
        
        return bot_response
        
    except Exception as e:
        print(f"Error in study planner chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process study planner request")

@router.post("/generate-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    current_user = Depends(get_current_student)
):
    """Generate a Pomodoro-based study plan"""
    try:
        db = get_database()
        
        # Create plan ID
        plan_id = str(uuid.uuid4())
        
        # Generate optimized study plan using AI
        study_plan = await ai_service.generate_pomodoro_study_plan(
            total_duration=request.total_duration_minutes,
            subjects=request.subjects,
            preferred_start_time=request.preferred_start_time,
            break_preferences=request.break_preferences
        )
        
        # Save the plan to database
        plan_data = {
            "plan_id": plan_id,
            "user_id": current_user["sub"],
            "total_duration_minutes": request.total_duration_minutes,
            "subjects": [subj.dict() for subj in request.subjects],
            "pomodoro_sessions": study_plan["sessions"],
            "study_tips": study_plan["tips"],
            "created_at": datetime.utcnow(),
            "used": False
        }
        
        await db[Collections.STUDY_PLANS].insert_one(plan_data)
        
        # Calculate totals
        total_work_time = sum(session.duration_minutes for session in study_plan["sessions"] if session.session_type == 'work')
        total_break_time = sum(session.duration_minutes for session in study_plan["sessions"] if session.session_type == 'break')
        
        return StudyPlanResponse(
            plan_id=plan_id,
            total_duration_minutes=request.total_duration_minutes,
            total_work_time=total_work_time,
            total_break_time=total_break_time,
            pomodoro_sessions=study_plan["sessions"],
            study_tips=study_plan["tips"],
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Error generating study plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate study plan")

@router.get("/my-plans")
async def get_my_study_plans(
    current_user = Depends(get_current_student)
):
    """Get all study plans for the current user"""
    try:
        db = get_database()
        
        plans = await db[Collections.STUDY_PLANS].find({
            "user_id": current_user["sub"]
        }).sort("created_at", -1).limit(10).to_list(length=10)
        
        return plans
        
    except Exception as e:
        print(f"Error fetching study plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch study plans")

@router.post("/start-session/{plan_id}")
async def start_study_session(
    plan_id: str,
    current_user = Depends(get_current_student)
):
    """Start a study session from a generated plan"""
    try:
        db = get_database()
        
        # Get the plan
        plan = await db[Collections.STUDY_PLANS].find_one({
            "plan_id": plan_id,
            "user_id": current_user["sub"]
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        # Mark plan as used
        await db[Collections.STUDY_PLANS].update_one(
            {"plan_id": plan_id},
            {"$set": {"used": True, "started_at": datetime.utcnow()}}
        )
        
        # Create calendar events for each session (optional)
        current_time = datetime.utcnow()
        calendar_events = []
        
        for session in plan["pomodoro_sessions"]:
            if session["session_type"] == "work":
                event_data = {
                    "title": f"Study: {session['subject']}",
                    "description": session["description"],
                    "start_time": current_time.isoformat(),
                    "end_time": (current_time + timedelta(minutes=session["duration_minutes"])).isoformat(),
                    "event_type": "study",
                    "subject": session["subject"]
                }
                calendar_events.append(event_data)
            
            current_time += timedelta(minutes=session["duration_minutes"])
        
        return {
            "message": "Study session started successfully",
            "plan_id": plan_id,
            "calendar_events": calendar_events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting study session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start study session")

@router.delete("/plan/{plan_id}")
async def delete_study_plan(
    plan_id: str,
    current_user = Depends(get_current_student)
):
    """Delete a study plan"""
    try:
        db = get_database()
        
        result = await db[Collections.STUDY_PLANS].delete_one({
            "plan_id": plan_id,
            "user_id": current_user["sub"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        return {"message": "Study plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting study plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete study plan")