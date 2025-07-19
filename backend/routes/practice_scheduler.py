from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.utils.security import get_current_student
from backend.services.ai_service import AIService

router = APIRouter(prefix="/api/practice-scheduler", tags=["practice-scheduler"])

# Request/Response models
class ScheduledTest(BaseModel):
    id: str
    user_id: str
    subject: str
    topics: List[str]
    difficulty: str
    question_count: int
    scheduled_for: datetime
    created_at: datetime
    reason: str
    priority: str  # high, medium, low
    original_score: float
    is_completed: bool = False
    completed_at: Optional[datetime] = None

class ScheduleRecommendation(BaseModel):
    recommended_date: datetime
    priority: str
    reason: str
    study_tips: List[str]
    estimated_improvement: str

# Initialize AI service
ai_service = AIService()

@router.post("/schedule-review")
async def schedule_review_test(
    subject: str,
    topics: List[str],
    difficulty: str,
    original_score: float,
    question_count: int,
    current_user = Depends(get_current_student)
):
    """Automatically schedule a review test based on performance"""
    try:
        db = get_database()
        
        # Get AI recommendation for scheduling
        recommendation = await ai_service.generate_smart_schedule_recommendation(
            subject=subject,
            topics=topics,
            score=original_score,
            difficulty=difficulty,
            student_id=current_user["sub"]
        )
        
        # Create scheduled test record
        scheduled_test_id = str(uuid.uuid4())
        scheduled_test = {
            "id": scheduled_test_id,
            "user_id": current_user["sub"],
            "subject": subject,
            "topics": topics,
            "difficulty": difficulty,
            "question_count": question_count,
            "scheduled_for": recommendation["recommended_date"],
            "created_at": datetime.utcnow(),
            "reason": recommendation["reason"],
            "priority": recommendation["priority"],
            "original_score": original_score,
            "is_completed": False,
            "study_tips": recommendation.get("study_tips", []),
            "estimated_improvement": recommendation.get("estimated_improvement", "")
        }
        
        # Save to database
        await db[Collections.SCHEDULED_TESTS].insert_one(scheduled_test)
        
        return {
            "message": "Review test scheduled successfully",
            "scheduled_test_id": scheduled_test_id,
            "recommendation": recommendation
        }
        
    except Exception as e:
        print(f"Error scheduling review test: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule review test")

@router.get("/upcoming-tests")
async def get_upcoming_tests(
    current_user = Depends(get_current_student)
):
    """Get all upcoming scheduled tests for the user"""
    try:
        db = get_database()
        
        # Get upcoming tests (not completed and scheduled for future or overdue)
        upcoming_tests = await db[Collections.SCHEDULED_TESTS].find({
            "user_id": current_user["sub"],
            "is_completed": False
        }).sort("scheduled_for", 1).to_list(length=50)
        
        # Convert ObjectIds and categorize tests
        tests = [convert_objectid_to_str(test) for test in upcoming_tests]
        
        now = datetime.utcnow()
        categorized_tests = {
            "overdue": [],
            "today": [],
            "this_week": [],
            "later": []
        }
        
        for test in tests:
            scheduled_date = datetime.fromisoformat(test["scheduled_for"].replace('Z', '+00:00')) if isinstance(test["scheduled_for"], str) else test["scheduled_for"]
            days_diff = (scheduled_date - now).days
            
            if days_diff < 0:
                categorized_tests["overdue"].append(test)
            elif days_diff == 0:
                categorized_tests["today"].append(test)
            elif days_diff <= 7:
                categorized_tests["this_week"].append(test)
            else:
                categorized_tests["later"].append(test)
        
        return categorized_tests
        
    except Exception as e:
        print(f"Error fetching upcoming tests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch upcoming tests")

@router.post("/take-scheduled-test/{test_id}")
async def take_scheduled_test(
    test_id: str,
    current_user = Depends(get_current_student)
):
    """Start a scheduled test"""
    try:
        db = get_database()
        
        # Get the scheduled test
        scheduled_test = await db[Collections.SCHEDULED_TESTS].find_one({
            "id": test_id,
            "user_id": current_user["sub"],
            "is_completed": False
        })
        
        if not scheduled_test:
            raise HTTPException(status_code=404, detail="Scheduled test not found")
        
        # Generate practice test questions
        from backend.routes.practice import practiceAPI
        questions_response = await practiceAPI.generate({
            "subject": scheduled_test["subject"],
            "topics": scheduled_test["topics"],
            "difficulty": scheduled_test["difficulty"],
            "question_count": scheduled_test["question_count"]
        })
        
        return {
            "scheduled_test": convert_objectid_to_str(scheduled_test),
            "questions": questions_response["questions"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting scheduled test: {e}")
        raise HTTPException(status_code=500, detail="Failed to start scheduled test")

@router.post("/complete-scheduled-test/{test_id}")
async def complete_scheduled_test(
    test_id: str,
    score: float,
    current_user = Depends(get_current_student)
):
    """Mark a scheduled test as completed and potentially schedule the next one"""
    try:
        db = get_database()
        
        # Update the scheduled test as completed
        result = await db[Collections.SCHEDULED_TESTS].update_one(
            {"id": test_id, "user_id": current_user["sub"]},
            {
                "$set": {
                    "is_completed": True,
                    "completed_at": datetime.utcnow(),
                    "final_score": score
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled test not found")
        
        # Get the completed test details
        completed_test = await db[Collections.SCHEDULED_TESTS].find_one({"id": test_id})
        
        # Automatically schedule next review if score is below mastery (95%)
        if score < 95.0:
            await schedule_review_test(
                subject=completed_test["subject"],
                topics=completed_test["topics"],
                difficulty=completed_test["difficulty"],
                original_score=score,
                question_count=completed_test["question_count"],
                current_user=current_user
            )
            return {"message": "Test completed and next review scheduled"}
        else:
            return {"message": "Test completed - mastery achieved!"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing scheduled test: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete scheduled test")

@router.delete("/cancel-test/{test_id}")
async def cancel_scheduled_test(
    test_id: str,
    current_user = Depends(get_current_student)
):
    """Cancel a scheduled test"""
    try:
        db = get_database()
        
        result = await db[Collections.SCHEDULED_TESTS].delete_one({
            "id": test_id,
            "user_id": current_user["sub"],
            "is_completed": False
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled test not found")
        
        return {"message": "Scheduled test cancelled successfully"}
        
    except Exception as e:
        print(f"Error cancelling scheduled test: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel scheduled test")