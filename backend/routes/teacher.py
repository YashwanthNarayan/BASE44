from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from backend.utils.security import get_current_teacher
from backend.utils.database import get_database, Collections
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

# Pydantic models
class CreateClassRequest(BaseModel):
    class_name: str
    subject: str
    description: Optional[str] = ""
    join_code: Optional[str] = None

class ClassResponse(BaseModel):
    class_id: str
    class_name: str
    subject: str
    description: str
    join_code: str
    teacher_id: str
    created_at: datetime
    student_count: int = 0
    test_count: int = 0
    average_score: Optional[float] = None

@router.post("/classes")
async def create_class(
    class_data: CreateClassRequest,
    current_user: dict = Depends(get_current_teacher)
):
    """Create a new class"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Check if user is a teacher
        teacher_profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": teacher_id})
        if not teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create classes"
            )
        
        # Generate class code if not provided
        if not class_data.class_code:
            import random
            import string
            class_data.class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Check if class code already exists
        existing_class = await db[Collections.CLASSROOMS].find_one({
            "class_code": class_data.class_code
        })
        if existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class code already exists. Please choose a different one."
            )
        
        # Create class
        class_id = str(uuid.uuid4())
        classroom = {
            "class_id": class_id,
            "class_name": class_data.class_name,
            "subject": class_data.subject,
            "description": class_data.description,
            "class_code": class_data.class_code,
            "teacher_id": teacher_id,
            "created_at": datetime.utcnow(),
            "student_ids": [],
            "active": True
        }
        
        # Insert into database
        await db[Collections.CLASSROOMS].insert_one(classroom)
        
        # Update teacher's class count
        await db[Collections.TEACHER_PROFILES].update_one(
            {"user_id": teacher_id},
            {"$inc": {"total_classes": 1}}
        )
        
        return {
            "message": "Class created successfully",
            "class_id": class_id,
            "class_code": class_data.class_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create class: {str(e)}"
        )

@router.get("/classes")
async def get_teacher_classes(
    current_user: dict = Depends(get_current_teacher)
):
    """Get all classes for the current teacher"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Check if user is a teacher
        teacher_profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": teacher_id})
        if not teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can access this endpoint"
            )
        
        # Get teacher's classes
        classes_cursor = db[Collections.CLASSROOMS].find({"teacher_id": teacher_id, "active": True})
        classes = await classes_cursor.to_list(100)
        
        # Enhance with statistics
        enhanced_classes = []
        for classroom in classes:
            # Count students
            student_count = len(classroom.get("student_ids", []))
            
            # Count tests (placeholder - you can implement based on your test schema)
            test_count = 0
            
            # Calculate average score (placeholder)
            average_score = None
            
            enhanced_class = {
                "class_id": classroom["class_id"],
                "class_name": classroom["class_name"],
                "subject": classroom["subject"],
                "description": classroom.get("description", ""),
                "class_code": classroom["class_code"],
                "teacher_id": classroom["teacher_id"],
                "created_at": classroom["created_at"],
                "student_count": student_count,
                "test_count": test_count,
                "average_score": average_score
            }
            enhanced_classes.append(enhanced_class)
        
        return enhanced_classes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get classes: {str(e)}"
        )

@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Delete a class"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Check if user is a teacher
        teacher_profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": teacher_id})
        if not teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can delete classes"
            )
        
        # Check if class exists and belongs to teacher
        classroom = await db[Collections.CLASSROOMS].find_one({
            "class_id": class_id,
            "teacher_id": teacher_id
        })
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to delete it"
            )
        
        # Remove students from this class
        await db[Collections.STUDENT_PROFILES].update_many(
            {"joined_classes": class_id},
            {"$pull": {"joined_classes": class_id}}
        )
        
        # Delete the class (soft delete by marking as inactive)
        await db[Collections.CLASSROOMS].update_one(
            {"class_id": class_id},
            {"$set": {"active": False, "deleted_at": datetime.utcnow()}}
        )
        
        # Update teacher's class count
        await db[Collections.TEACHER_PROFILES].update_one(
            {"user_id": teacher_id},
            {"$inc": {"total_classes": -1}}
        )
        
        return {"message": "Class deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete class: {str(e)}"
        )

# Analytics endpoints (moved from server_original.py)
@router.get("/analytics/overview")
async def get_teacher_analytics_overview(
    current_user: dict = Depends(get_current_teacher)
):
    """Get teacher's overall analytics across all classes"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Check if user is a teacher
        teacher_profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": teacher_id})
        if not teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can access analytics"
            )
        
        # Get teacher's classes
        teacher_classes_cursor = db[Collections.CLASSROOMS].find({"teacher_id": teacher_id, "active": True})
        teacher_classes = await teacher_classes_cursor.to_list(100)
        class_ids = [cls['class_id'] for cls in teacher_classes]
        
        # Get all students in teacher's classes using joined_classes array
        students_cursor = db[Collections.STUDENT_PROFILES].find({"joined_classes": {"$in": class_ids}})
        students = await students_cursor.to_list(1000)
        
        total_classes = len(teacher_classes)
        total_students = len(students)
        
        # Get all practice test results for these students
        practice_results_cursor = db[Collections.PRACTICE_RESULTS].find({
            "user_id": {"$in": [student['user_id'] for student in students]}
        })
        practice_results = await practice_results_cursor.to_list(1000)
        
        total_tests = len(practice_results)
        average_score = 0
        if practice_results:
            total_score = sum(result.get('score', 0) for result in practice_results)
            average_score = total_score / total_tests
        
        # Class summaries
        class_summary = []
        for class_data in teacher_classes:
            class_students = [s for s in students if class_data['class_id'] in s.get('joined_classes', [])]
            class_student_ids = [s['user_id'] for s in class_students]
            
            class_results = [r for r in practice_results if r['user_id'] in class_student_ids]
            class_avg = 0
            if class_results:
                class_avg = sum(r.get('score', 0) for r in class_results) / len(class_results)
            
            class_summary.append({
                "class_info": {
                    "class_id": class_data['class_id'],
                    "class_name": class_data['class_name'],
                    "subject": class_data['subject']
                },
                "student_count": len(class_students),
                "total_tests": len(class_results),
                "average_score": class_avg
            })
        
        # Subject distribution
        subject_distribution = {}
        for result in practice_results:
            subject = result.get('subject', 'Unknown')
            if subject not in subject_distribution:
                subject_distribution[subject] = {"count": 0, "total_score": 0}
            subject_distribution[subject]["count"] += 1
            subject_distribution[subject]["total_score"] += result.get('score', 0)
        
        # Convert to list with averages
        subject_dist_list = []
        for subject, data in subject_distribution.items():
            avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
            subject_dist_list.append({
                "subject": subject,
                "test_count": data["count"],
                "average_score": avg_score
            })
        
        return {
            "overview_metrics": {
                "total_classes": total_classes,
                "total_students": total_students,
                "total_tests": total_tests,
                "average_score": average_score
            },
            "class_summary": class_summary,
            "subject_distribution": subject_dist_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in teacher analytics: {str(e)}")
        # Return default data instead of error for better UX
        return {
            "overview_metrics": {
                "total_classes": 0,
                "total_students": 0,
                "total_tests": 0,
                "average_score": 0
            },
            "class_summary": [],
            "subject_distribution": []
        }