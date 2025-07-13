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
        
        # Generate join code if not provided
        if not class_data.join_code:
            import random
            import string
            class_data.join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Check if join code already exists
        existing_class = await db[Collections.CLASSROOMS].find_one({
            "join_code": class_data.join_code
        })
        if existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Join code already exists. Please choose a different one."
            )
        
        # Create class
        class_id = str(uuid.uuid4())
        classroom = {
            "class_id": class_id,
            "class_name": class_data.class_name,
            "subject": class_data.subject,
            "description": class_data.description,
            "join_code": class_data.join_code,
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
            "join_code": class_data.join_code
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
                "join_code": classroom["join_code"],
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
        practice_results_cursor = db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": {"$in": [student['user_id'] for student in students]}
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
            
            class_results = [r for r in practice_results if r['student_id'] in class_student_ids]
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

@router.get("/analytics/test-results")
async def get_test_results(
    class_id: Optional[str] = None,
    subject: Optional[str] = None,
    current_user: dict = Depends(get_current_teacher)
):
    """Get detailed test results with filtering options"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Verify teacher profile
        teacher_profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": teacher_id})
        if not teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can access test results"
            )
        
        # Build query for practice attempts
        query = {}
        
        # If specific class is requested, get students from that class
        if class_id:
            classroom = await db[Collections.CLASSROOMS].find_one({
                "class_id": class_id,
                "teacher_id": teacher_id
            })
            if not classroom:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Class not found"
                )
            
            # Get students in this class
            students_cursor = db[Collections.STUDENT_PROFILES].find({
                "joined_classes": {"$in": [class_id]}
            })
            students = await students_cursor.to_list(1000)
            student_ids = [student['user_id'] for student in students]
            
            if student_ids:
                query["student_id"] = {"$in": student_ids}
            else:
                # No students in class, return empty results
                return []
        else:
            # Get all students from all teacher's classes
            teacher_classes_cursor = db[Collections.CLASSROOMS].find({"teacher_id": teacher_id})
            teacher_classes = await teacher_classes_cursor.to_list(100)
            
            all_class_ids = [cls['class_id'] for cls in teacher_classes]
            
            if all_class_ids:
                students_cursor = db[Collections.STUDENT_PROFILES].find({
                    "joined_classes": {"$elemMatch": {"$in": all_class_ids}}
                })
                students = await students_cursor.to_list(1000)
                student_ids = [student['user_id'] for student in students]
                
                if student_ids:
                    query["student_id"] = {"$in": student_ids}
                else:
                    return []
            else:
                return []
        
        # Add subject filter if provided
        if subject and subject != 'all':
            query["subject"] = subject
        
        # Get practice attempts
        practice_attempts_cursor = db[Collections.PRACTICE_ATTEMPTS].find(query).sort("completed_at", -1)
        practice_attempts = await practice_attempts_cursor.to_list(1000)
        
        # Enrich with student information
        results = []
        for attempt in practice_attempts:
            # Get student info
            student = await db[Collections.STUDENT_PROFILES].find_one({"user_id": attempt["student_id"]})
            user = await db[Collections.USERS].find_one({"id": attempt["student_id"]})
            
            results.append({
                "id": attempt["id"],
                "student_id": attempt["student_id"],
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "student_email": user.get("email", "") if user else "",
                "subject": attempt.get("subject", "Unknown"),
                "score": attempt.get("score", 0),
                "correct_count": attempt.get("correct_count", 0),
                "total_questions": attempt.get("total_questions", 0),
                "difficulty": attempt.get("difficulty", "medium"),
                "time_taken": attempt.get("time_taken", 0),
                "completed_at": attempt.get("completed_at"),
                "grade": get_grade_from_score(attempt.get("score", 0))
            })
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting test results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test results: {str(e)}"
        )

@router.get("/analytics/class-performance/{class_id}")
async def get_class_performance(
    class_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Get detailed performance analytics for a specific class"""
    try:
        db = get_database()
        teacher_id = current_user['sub']
        
        # Verify teacher owns this class
        classroom = await db[Collections.CLASSROOMS].find_one({
            "class_id": class_id,
            "teacher_id": teacher_id
        })
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # Get students in this class
        students_cursor = db[Collections.STUDENT_PROFILES].find({
            "joined_classes": {"$in": [class_id]}
        })
        students = await students_cursor.to_list(1000)
        
        if not students:
            return {
                "class_info": {
                    "class_id": class_id,
                    "class_name": classroom.get("class_name", ""),
                    "subject": classroom.get("subject", ""),
                    "student_count": 0
                },
                "performance_summary": {
                    "total_tests": 0,
                    "average_score": 0,
                    "highest_score": 0,
                    "lowest_score": 0,
                    "completion_rate": 0
                },
                "student_performance": [],
                "subject_breakdown": [],
                "recent_activity": []
            }
        
        student_ids = [student['user_id'] for student in students]
        
        # Get practice attempts for these students
        practice_attempts_cursor = db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": {"$in": student_ids}
        }).sort("completed_at", -1)
        practice_attempts = await practice_attempts_cursor.to_list(1000)
        
        # Calculate performance metrics
        total_tests = len(practice_attempts)
        scores = [attempt.get("score", 0) for attempt in practice_attempts]
        
        performance_summary = {
            "total_tests": total_tests,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "completion_rate": 100 if total_tests > 0 else 0  # Simplified completion rate
        }
        
        # Student performance breakdown
        student_performance = []
        for student in students:
            user = await db[Collections.USERS].find_one({"id": student['user_id']})
            student_attempts = [a for a in practice_attempts if a['student_id'] == student['user_id']]
            student_scores = [a.get("score", 0) for a in student_attempts]
            
            student_performance.append({
                "student_id": student['user_id'],
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "total_tests": len(student_attempts),
                "average_score": sum(student_scores) / len(student_scores) if student_scores else 0,
                "best_score": max(student_scores) if student_scores else 0,
                "recent_tests": len([a for a in student_attempts if a.get("completed_at")])
            })
        
        # Subject breakdown
        subject_breakdown = {}
        for attempt in practice_attempts:
            subject = attempt.get("subject", "Unknown")
            if subject not in subject_breakdown:
                subject_breakdown[subject] = {"tests": 0, "total_score": 0}
            subject_breakdown[subject]["tests"] += 1
            subject_breakdown[subject]["total_score"] += attempt.get("score", 0)
        
        subject_list = []
        for subject, data in subject_breakdown.items():
            avg_score = data["total_score"] / data["tests"] if data["tests"] > 0 else 0
            subject_list.append({
                "subject": subject,
                "test_count": data["tests"],
                "average_score": avg_score
            })
        
        # Recent activity (last 10 tests)
        recent_activity = []
        for attempt in practice_attempts[:10]:
            user = await db[Collections.USERS].find_one({"id": attempt["student_id"]})
            recent_activity.append({
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "subject": attempt.get("subject", "Unknown"),
                "score": attempt.get("score", 0),
                "completed_at": attempt.get("completed_at"),
                "difficulty": attempt.get("difficulty", "medium")
            })
        
        return {
            "class_info": {
                "class_id": class_id,
                "class_name": classroom.get("class_name", ""),
                "subject": classroom.get("subject", ""),
                "student_count": len(students)
            },
            "performance_summary": performance_summary,
            "student_performance": student_performance,
            "subject_breakdown": subject_list,
            "recent_activity": recent_activity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting class performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get class performance: {str(e)}"
        )

def get_grade_from_score(score):
    """Convert numerical score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"