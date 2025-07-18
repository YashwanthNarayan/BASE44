from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.utils.security import get_current_student
from backend.services.ai_service import AIService
from backend.models.user import Subject

router = APIRouter(prefix="/api/notes", tags=["notes"])

# Request/Response models
class GenerateNotesRequest(BaseModel):
    subject: str
    topic: str
    grade_level: str

class NoteResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    topic: str
    grade_level: str
    content: str
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

# Initialize AI service
ai_service = AIService()

@router.post("/generate")
async def generate_notes(
    request: GenerateNotesRequest,
    current_user = Depends(get_current_student)
):
    """Generate AI-powered study notes"""
    try:
        db = get_database()
        
        # Generate notes using AI service
        notes_content = await ai_service.generate_study_notes(
            subject=request.subject,
            topic=request.topic,
            grade_level=request.grade_level
        )
        
        # Create note document
        note_id = str(uuid.uuid4())
        note_data = {
            "id": note_id,
            "user_id": current_user["sub"],
            "subject": request.subject,
            "topic": request.topic,
            "grade_level": request.grade_level,
            "content": notes_content,
            "is_favorite": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        await db[Collections.STUDENT_NOTES].insert_one(note_data)
        
        return {"message": "Notes generated successfully", "note_id": note_id}
        
    except Exception as e:
        print(f"Error generating notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate notes")

@router.get("/")
async def get_all_notes(
    current_user = Depends(get_current_student)
):
    """Get all notes for the current user"""
    try:
        db = get_database()
        
        # Get user's notes
        notes = await db[Collections.STUDENT_NOTES].find({
            "user_id": current_user["sub"]
        }).sort("created_at", -1).to_list(length=100)
        
        # Convert ObjectIds to strings
        notes = [convert_objectid_to_str(note) for note in notes]
        
        return notes
        
    except Exception as e:
        print(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notes")

@router.get("/{note_id}")
async def get_note(
    note_id: str,
    current_user = Depends(get_current_student)
):
    """Get a specific note by ID"""
    try:
        db = get_database()
        
        # Get note by ID and user
        note = await db[Collections.STUDENT_NOTES].find_one({
            "id": note_id,
            "user_id": current_user["sub"]
        })
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Convert ObjectIds to strings
        note = convert_objectid_to_str(note)
        
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching note: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch note")

@router.put("/{note_id}/favorite")
async def toggle_favorite(
    note_id: str,
    current_user = Depends(get_current_student)
):
    """Toggle favorite status of a note"""
    try:
        db = get_database()
        
        # Get current note
        note = await db[Collections.STUDENT_NOTES].find_one({
            "id": note_id,
            "user_id": current_user["sub"]
        })
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Toggle favorite status
        new_favorite_status = not note.get("is_favorite", False)
        
        # Update note
        await db[Collections.STUDENT_NOTES].update_one(
            {"id": note_id, "user_id": current_user["sub"]},
            {
                "$set": {
                    "is_favorite": new_favorite_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Favorite status updated", "is_favorite": new_favorite_status}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error toggling favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to update favorite status")

@router.delete("/{note_id}/delete")
async def delete_note(
    note_id: str,
    current_user = Depends(get_current_student)
):
    """Delete a note"""
    try:
        db = get_database()
        
        # Delete note
        result = await db[Collections.STUDENT_NOTES].delete_one({
            "id": note_id,
            "user_id": current_user["sub"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")