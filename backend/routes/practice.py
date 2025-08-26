from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from backend.models.practice import PracticeTestRequest, PracticeAttempt, TestSubmissionRequest
from backend.models.user import Subject
from backend.utils.security import get_current_student
from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.services.ai_service import ai_service
from backend.utils.helpers import ScoreUtils
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/practice", tags=["practice"])

async def fix_null_subjects_in_database(db):
    """One-time data migration to fix NULL subjects in existing practice attempts"""
    try:
        # Find attempts with NULL/None subjects
        null_attempts = await db[Collections.PRACTICE_ATTEMPTS].find({
            "$or": [
                {"subject": {"$exists": False}},
                {"subject": None},
                {"subject": ""}
            ]
        }).to_list(None)
        
        if null_attempts:
            print(f"🔧 Data Migration: Found {len(null_attempts)} attempts with NULL subjects")
            
            # Update them to 'general' as fallback
            result = await db[Collections.PRACTICE_ATTEMPTS].update_many(
                {
                    "$or": [
                        {"subject": {"$exists": False}},
                        {"subject": None},
                        {"subject": ""}
                    ]
                },
                {"$set": {"subject": "general"}}
            )
            
            print(f"✅ Data Migration: Updated {result.modified_count} attempts with subject='general'")
    except Exception as e:
        print(f"❌ Data Migration Error: {e}")

@router.post("/generate")
async def generate_practice_test(
    test_request: PracticeTestRequest,
    current_user: dict = Depends(get_current_student)
):
    """Generate a practice test using AI"""
    try:
        # Generate questions using AI service
        questions = await ai_service.generate_practice_questions(
            subject=test_request.subject,
            topics=test_request.topics,
            difficulty=test_request.difficulty,
            question_count=test_request.question_count,
            question_types=test_request.question_types
        )
        
        # Store questions in database for tracking
        db = get_database()
        for question in questions:
            question["created_at"] = datetime.utcnow()
            await db[Collections.PRACTICE_QUESTIONS].insert_one(question.copy())  # Insert a copy to avoid modifying original
        
        # Convert any ObjectIds to strings before returning
        return convert_objectid_to_str({
            "questions": questions,
            "total_count": len(questions),
            "subject": test_request.subject,
            "difficulty": test_request.difficulty
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate practice test: {str(e)}"
        )

@router.post("/submit")
async def submit_practice_test(
    test_data: dict,
    current_user: dict = Depends(get_current_student)
):
    """Submit practice test answers with detailed results"""
    db = get_database()
    
    try:
        # Get questions from database
        question_ids = test_data.get("questions", [])
        questions = await db[Collections.PRACTICE_QUESTIONS].find({
            "id": {"$in": question_ids}
        }).to_list(None)
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questions not found"
            )
        
        # Calculate detailed results
        student_answers = test_data.get("student_answers", {})
        correct_count = 0
        total_questions = len(questions)
        detailed_results = []
        
        for question in questions:
            question_id = question["id"]
            student_answer = student_answers.get(question_id, "").strip()
            correct_answer = question["correct_answer"].strip()
            question_type = question.get("question_type", "mcq")
            
            # Use AI-powered evaluation for better accuracy
            evaluation = await ai_service.evaluate_answer_intelligently(
                question_text=question["question_text"],
                question_type=question_type,
                student_answer=student_answer,
                correct_answer=correct_answer,
                subject=question.get("subject", ""),
                topic=question.get("topic", "")
            )
            
            is_correct = evaluation["is_correct"]
            if is_correct:
                correct_count += 1
            
            # Store detailed result for this question
            detailed_result = {
                "question_id": question_id,
                "question_text": question["question_text"],
                "question_type": question_type,
                "options": question.get("options"),
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": evaluation.get("explanation", question.get("explanation", "No explanation available")),
                "feedback": evaluation.get("feedback", "Good effort!"),
                "partial_credit": evaluation.get("partial_credit", 1.0 if is_correct else 0.0),
                "score_percentage": evaluation.get("score_percentage", 100 if is_correct else 0),
                "key_concepts_identified": evaluation.get("key_concepts_identified", []),
                "areas_for_improvement": evaluation.get("areas_for_improvement", []),
                "topic": question.get("topic", "General")
            }
            detailed_results.append(detailed_result)
        
        score_percentage = ScoreUtils.calculate_percentage(correct_count, total_questions)
        
        # Create detailed practice attempt record
        # Ensure we have a valid subject - get from request data if questions don't have it
        subject = None
        if questions and questions[0].get("subject"):
            subject = questions[0]["subject"]
        else:
            # Fallback to getting subject from the original test request data
            subject = test_data.get("subject", "general")
        
        attempt_doc = {
            "id": str(uuid.uuid4()),
            "student_id": current_user["sub"],
            "questions": question_ids,
            "student_answers": student_answers,
            "detailed_results": detailed_results,  # Store question-by-question results
            "score": score_percentage,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "subject": subject,  # Use validated subject
            "difficulty": questions[0]["difficulty"] if questions and questions[0].get("difficulty") else "medium",
            "time_taken": test_data.get("time_taken", 0),
            "completed_at": datetime.utcnow()
        }
        
        # Save attempt to database
        await db[Collections.PRACTICE_ATTEMPTS].insert_one(attempt_doc)
        
        # Automatically schedule next review test based on performance
        try:
            # Import AI service and create schedule recommendation
            schedule_recommendation = await ai_service.generate_smart_schedule_recommendation(
                subject=subject,
                topics=list(set(q.get("topic", "General") for q in questions)),
                score=score_percentage,
                difficulty=attempt_doc["difficulty"],
                student_id=current_user["sub"]
            )
            
            # Create scheduled test record
            scheduled_test_id = str(uuid.uuid4())
            scheduled_test = {
                "id": scheduled_test_id,
                "user_id": current_user["sub"],
                "subject": subject,
                "topics": list(set(q.get("topic", "General") for q in questions)),
                "difficulty": attempt_doc["difficulty"],
                "question_count": min(total_questions, 5),  # Limit review tests to 5 questions
                "scheduled_for": schedule_recommendation["recommended_date"],
                "created_at": datetime.utcnow(),
                "reason": schedule_recommendation["reason"],
                "priority": schedule_recommendation["priority"],
                "original_score": score_percentage,
                "is_completed": False,
                "study_tips": schedule_recommendation.get("study_tips", []),
                "estimated_improvement": schedule_recommendation.get("estimated_improvement", "")
            }
            
            # Save to database
            await db[Collections.SCHEDULED_TESTS].insert_one(scheduled_test)
            
        except Exception as e:
            print(f"Warning: Failed to schedule automatic review: {e}")
            # Don't fail the entire test submission if scheduling fails
        
        # Update student profile
        await update_student_stats(current_user["sub"], score_percentage, subject)
        
        # Data migration: Fix any NULL subjects in existing attempts (one-time fix)
        await fix_null_subjects_in_database(db)
        
        return {
            "attempt_id": attempt_doc["id"],
            "score": score_percentage,
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "grade": ScoreUtils.get_grade_from_percentage(score_percentage),
            "xp_gained": ScoreUtils.calculate_xp_gain(score_percentage, questions[0]["difficulty"]),
            "detailed_results": detailed_results  # Return detailed results immediately
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit practice test: {str(e)}"
        )

@router.post("/submit-scheduled")
async def submit_scheduled_test(
    test_data: TestSubmissionRequest,
    current_user = Depends(get_current_student)
):
    """Submit a scheduled test with embedded question data"""
    try:
        db = get_database()
        
        # Get the questions from the request (they're embedded)
        questions = test_data.question_data if hasattr(test_data, 'question_data') else []
        
        if not questions:
            raise HTTPException(status_code=400, detail="No question data provided")
        
        # Process the submission the same way as regular tests
        subject = test_data.subject or "general"
        difficulty = getattr(test_data, 'difficulty', 'medium')
        
        # Calculate detailed results
        student_answers = test_data.student_answers
        correct_count = 0
        total_questions = len(questions)
        detailed_results = []
        
        for question in questions:
            question_id = question.get("id", "")
            student_answer = student_answers.get(question_id, "").strip()
            correct_answer = question.get("correct_answer", "").strip()
            question_type = question.get("question_type", "short_answer")
            
            # Use AI-powered evaluation for better accuracy
            evaluation = await ai_service.evaluate_answer_intelligently(
                question_text=question.get("question_text", ""),
                question_type=question_type,
                student_answer=student_answer,
                correct_answer=correct_answer,
                subject=question.get("subject", subject),
                topic=question.get("topic", "Review")
            )
            
            is_correct = evaluation["is_correct"]
            if is_correct:
                correct_count += 1
            
            # Store detailed result for this question
            detailed_result = {
                "question_id": question_id,
                "question_text": question.get("question_text", ""),
                "question_type": question_type,
                "options": question.get("options"),
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": evaluation.get("explanation", question.get("explanation", "No explanation available")),
                "feedback": evaluation.get("feedback", "Good effort!"),
                "partial_credit": evaluation.get("partial_credit", 1.0 if is_correct else 0.0),
                "score_percentage": evaluation.get("score_percentage", 100 if is_correct else 0),
                "key_concepts_identified": evaluation.get("key_concepts_identified", []),
                "areas_for_improvement": evaluation.get("areas_for_improvement", []),
                "topic": question.get("topic", "Review")
            }
            detailed_results.append(detailed_result)
        
        # Calculate overall score
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Determine grade
        if score_percentage >= 90:
            grade = "A"
            xp_gained = 10
        elif score_percentage >= 80:
            grade = "B" 
            xp_gained = 8
        elif score_percentage >= 70:
            grade = "C"
            xp_gained = 6
        elif score_percentage >= 60:
            grade = "D"
            xp_gained = 4
        else:
            grade = "F"
            xp_gained = 1
        
        # Create attempt document
        attempt_doc = {
            "id": str(uuid.uuid4()),
            "student_id": current_user["sub"],
            "subject": subject,
            "difficulty": difficulty,
            "questions_count": total_questions,
            "correct_answers": correct_count,
            "score": score_percentage,
            "grade": grade,
            "xp_gained": xp_gained,
            "time_taken": test_data.time_taken,
            "detailed_results": detailed_results,
            "test_type": "scheduled_review",
            "created_at": datetime.utcnow()
        }
        
        # Save attempt to database
        await db[Collections.PRACTICE_ATTEMPTS].insert_one(attempt_doc)
        
        return {
            "attempt_id": attempt_doc["id"],
            "score": score_percentage,
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "grade": grade,
            "xp_gained": xp_gained,
            "detailed_results": detailed_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting scheduled test: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit scheduled test")

@router.get("/results/{attempt_id}")
async def get_detailed_results(
    attempt_id: str,
    current_user: dict = Depends(get_current_student)
):
    """Get detailed results for a specific practice attempt"""
    db = get_database()
    
    try:
        # Get attempt from database
        attempt = await db[Collections.PRACTICE_ATTEMPTS].find_one({
            "id": attempt_id,
            "student_id": current_user["sub"]
        })
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice attempt not found"
            )
        
        return convert_objectid_to_str({
            "id": attempt["id"],  # Use 'id' for consistency with frontend
            "attempt_id": attempt["id"],  # Keep attempt_id for backward compatibility
            "score": attempt["score"],
            "correct_count": attempt.get("correct_count", 0),
            "total_questions": attempt["total_questions"],
            "subject": attempt["subject"],
            "difficulty": attempt["difficulty"],
            "time_taken": attempt.get("time_taken", 0),
            "completed_at": attempt["completed_at"],
            "detailed_results": attempt.get("detailed_results", [])
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detailed results: {str(e)}"
        )

@router.get("/results")
async def get_practice_results(
    subject: Optional[str] = None,
    current_user: dict = Depends(get_current_student)
):
    """Get student's practice test results"""
    db = get_database()
    
    try:
        # Build query
        query = {"student_id": current_user["sub"]}
        if subject:
            query["subject"] = subject
        
        # Get practice attempts
        attempts = await db[Collections.PRACTICE_ATTEMPTS].find(query).sort("completed_at", -1).to_list(None)
        
        results = []
        for attempt in attempts:
            results.append({
                "id": attempt["id"],
                "subject": attempt.get("subject", "general"),
                "score": attempt.get("score", 0),
                "correct_count": attempt.get("correct_count", 0),
                "total_questions": attempt.get("total_questions", len(attempt.get("questions", []))),  # Fallback to question count
                "difficulty": attempt.get("difficulty", "medium"),
                "completed_at": attempt.get("completed_at"),
                "time_taken": attempt.get("time_taken", 0),
                "grade": ScoreUtils.get_grade_from_percentage(attempt.get("score", 0))
            })
        
        return convert_objectid_to_str(results)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get practice results: {str(e)}"
        )

@router.get("/stats/{subject}")
async def get_subject_stats(
    subject: str,
    current_user: dict = Depends(get_current_student)
):
    """Get statistics for a specific subject"""
    db = get_database()
    
    try:
        # Get attempts for the subject
        attempts = await db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": current_user["sub"],
            "subject": subject
        }).to_list(None)
        
        if not attempts:
            return {
                "subject": subject,
                "total_tests": 0,
                "average_score": 0.0,
                "best_score": 0.0,
                "total_questions_answered": 0,
                "recent_tests": []
            }
        
        # Calculate statistics with defensive programming
        total_tests = len(attempts)
        scores = []
        for attempt in attempts:
            score = attempt.get("score", 0)
            if isinstance(score, (int, float)):
                scores.append(score)
        
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        # Calculate total questions with safe fallbacks
        total_questions = 0
        for attempt in attempts:
            questions_count = attempt.get("total_questions")
            if questions_count is not None:
                total_questions += questions_count
            else:
                # Fallback to counting questions array
                questions = attempt.get("questions", [])
                total_questions += len(questions)
        
        # Recent tests (last 5) with safe sorting
        valid_recent_tests = []
        for test in attempts:
            completed_at = test.get("completed_at")
            if completed_at is not None:
                valid_recent_tests.append(test)
        
        # Sort by completed_at descending (most recent first)
        recent_tests = sorted(valid_recent_tests, 
                            key=lambda x: x.get("completed_at", ""), 
                            reverse=True)[:5]
        
        recent_formatted = []
        for test in recent_tests:
            # Safe field extraction
            total_questions_for_test = test.get("total_questions")
            if total_questions_for_test is None:
                questions = test.get("questions", [])
                total_questions_for_test = len(questions)
            
            recent_formatted.append({
                "id": test.get("id", ""),
                "score": test.get("score", 0),
                "total_questions": total_questions_for_test,
                "difficulty": test.get("difficulty", "medium"),
                "completed_at": test.get("completed_at")
            })
        
        return {
            "subject": subject,
            "total_tests": total_tests,
            "average_score": round(average_score, 1),
            "best_score": round(best_score, 1),
            "total_questions_answered": total_questions,
            "recent_tests": recent_formatted
        }
    
    except Exception as e:
        print(f"❌ ERROR in get_subject_stats for {subject}: {str(e)}")
        print(f"❌ ERROR TYPE: {type(e)}")
        import traceback
        print(f"❌ ERROR TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats for {subject}: {str(e)}"
        )

async def update_student_stats(student_id: str, score: float, subject: str):
    """Update student profile statistics"""
    db = get_database()
    
    try:
        # Get current profile
        profile = await db[Collections.STUDENT_PROFILES].find_one({"user_id": student_id})
        if not profile:
            return
        
        # Calculate new statistics
        total_tests = profile.get("total_tests", 0) + 1
        current_avg = profile.get("average_score", 0.0)
        new_avg = ((current_avg * (total_tests - 1)) + score) / total_tests
        
        # Update recent scores (keep last 10)
        recent_scores = profile.get("recent_scores", [])
        recent_scores.append({
            "score": score,
            "subject": subject,
            "date": datetime.utcnow()
        })
        recent_scores = recent_scores[-10:]  # Keep only last 10
        
        # Add subject to studied subjects if not already there
        subjects_studied = profile.get("subjects_studied", [])
        if subject not in subjects_studied:
            subjects_studied.append(subject)
        
        # Update profile
        await db[Collections.STUDENT_PROFILES].update_one(
            {"user_id": student_id},
            {
                "$set": {
                    "total_tests": total_tests,
                    "average_score": round(new_avg, 1),
                    "recent_scores": recent_scores,
                    "subjects_studied": subjects_studied,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    except Exception as e:
        print(f"Error updating student stats: {e}")