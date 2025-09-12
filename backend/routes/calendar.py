from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.utils.security import get_current_student

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Calendar Event Model
class CalendarEvent(BaseModel):
    id: Optional[str] = None
    student_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    event_type: str  # "study", "assignment", "exam", "review_test", "personal"
    subject: Optional[str] = None
    start_time: str  # ISO format string
    end_time: str    # ISO format string
    is_completed: bool = False
    created_at: Optional[datetime] = None

class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str
    subject: Optional[str] = None
    start_time: str
    end_time: str

@router.post("/events")
async def create_calendar_event(
    event_data: CreateEventRequest,
    current_user = Depends(get_current_student)
):
    """Create a calendar event"""
    try:
        db = get_database()
        
        # Create event document
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "student_id": current_user["sub"],
            "title": event_data.title,
            "description": event_data.description,
            "event_type": event_data.event_type,
            "subject": event_data.subject,
            "start_time": event_data.start_time,
            "end_time": event_data.end_time,
            "is_completed": False,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        await db[Collections.CALENDAR_EVENTS].insert_one(event)
        
        # Return the created event
        return convert_objectid_to_str(event)
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create calendar event")

@router.get("/events")
async def get_calendar_events(
    current_user = Depends(get_current_student)
):
    """Get user's calendar events"""
    try:
        db = get_database()
        
        # Get all events for the user, sorted by start time
        events = await db[Collections.CALENDAR_EVENTS].find({
            "student_id": current_user["sub"]
        }).sort("start_time", 1).to_list(length=100)
        
        # Convert ObjectIds and return
        return [convert_objectid_to_str(event) for event in events]
        
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calendar events")

@router.get("/events/{event_id}")
async def get_calendar_event(
    event_id: str,
    current_user = Depends(get_current_student)
):
    """Get a specific calendar event"""
    try:
        db = get_database()
        
        event = await db[Collections.CALENDAR_EVENTS].find_one({
            "id": event_id,
            "student_id": current_user["sub"]
        })
        
        if not event:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
        return convert_objectid_to_str(event)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calendar event")

@router.put("/events/{event_id}")
async def update_calendar_event(
    event_id: str,
    event_data: CreateEventRequest,
    current_user = Depends(get_current_student)
):
    """Update a calendar event"""
    try:
        db = get_database()
        
        # Update the event
        result = await db[Collections.CALENDAR_EVENTS].update_one(
            {"id": event_id, "student_id": current_user["sub"]},
            {
                "$set": {
                    "title": event_data.title,
                    "description": event_data.description,
                    "event_type": event_data.event_type,
                    "subject": event_data.subject,
                    "start_time": event_data.start_time,
                    "end_time": event_data.end_time,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
        # Return updated event
        updated_event = await db[Collections.CALENDAR_EVENTS].find_one({
            "id": event_id,
            "student_id": current_user["sub"]
        })
        
        return convert_objectid_to_str(updated_event)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to update calendar event")

@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: str,
    current_user = Depends(get_current_student)
):
    """Delete a calendar event"""
    try:
        db = get_database()
        
        result = await db[Collections.CALENDAR_EVENTS].delete_one({
            "id": event_id,
            "student_id": current_user["sub"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
        return {"message": "Calendar event deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete calendar event")

@router.put("/events/{event_id}/complete")
async def mark_event_complete(
    event_id: str,
    current_user = Depends(get_current_student)
):
    """Mark a calendar event as completed"""
    try:
        db = get_database()
        
        result = await db[Collections.CALENDAR_EVENTS].update_one(
            {"id": event_id, "student_id": current_user["sub"]},
            {
                "$set": {
                    "is_completed": True,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
        return {"message": "Calendar event marked as completed"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking event complete: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark event complete")