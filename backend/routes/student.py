from fastapi import APIRouter, HTTPException, Depends, status
from backend.models.classroom import JoinClassRequest
from backend.utils.security import get_current_student
from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.services.auth_service import auth_service

router = APIRouter(prefix="/api/student", tags=["student"])

@router.get("/profile")
async def get_student_profile(current_user: dict = Depends(get_current_student)):
    """Get student profile"""
    try:
        profile = await auth_service.get_user_profile(
            current_user["sub"], 
            current_user["user_type"]
        )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student profile: {str(e)}"
        )

@router.post("/join-class")
async def join_class(
    join_request: JoinClassRequest,
    current_user: dict = Depends(get_current_student)
):
    """Join a class using join code"""
    db = get_database()
    
    try:
        # Find classroom by join code
        classroom = await db[Collections.CLASSROOMS].find_one({
            "join_code": join_request.join_code,
            "is_active": True
        })
        
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid join code"
            )
        
        # Check if student is already in the class
        student_profile = await db[Collections.STUDENT_PROFILES].find_one({
            "user_id": current_user["sub"]
        })
        
        if not student_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        class_id = classroom["id"]
        if class_id in student_profile.get("joined_classes", []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already joined this class"
            )
        
        # Add student to classroom
        await db[Collections.CLASSROOMS].update_one(
            {"id": class_id},
            {"$addToSet": {"student_ids": current_user["sub"]}}
        )
        
        # Add class to student's joined classes
        await db[Collections.STUDENT_PROFILES].update_one(
            {"user_id": current_user["sub"]},
            {"$addToSet": {"joined_classes": class_id}}
        )
        
        # Update teacher's total students count
        teacher_id = classroom["teacher_id"]
        await db[Collections.TEACHER_PROFILES].update_one(
            {"user_id": teacher_id},
            {"$inc": {"total_students": 1}}
        )
        
        return {
            "message": "Successfully joined class",
            "class_name": classroom["class_name"],
            "subject": classroom["subject"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join class: {str(e)}"
        )