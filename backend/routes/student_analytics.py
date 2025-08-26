from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta

from backend.utils.security import get_current_student
from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.services.analytics_service import StudentAnalyticsService

router = APIRouter(prefix="/api/student/analytics", tags=["Student Analytics"])

@router.get("/strengths-weaknesses")
async def get_strengths_weaknesses_analysis(
    current_user = Depends(get_current_student)
):
    """Get comprehensive strengths and weaknesses analysis for the student"""
    try:
        db = get_database()
        student_id = current_user['sub']
        
        # Get all practice attempts for this student
        practice_attempts_cursor = db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": student_id
        }).sort("completed_at", -1)
        
        practice_attempts = await practice_attempts_cursor.to_list(1000)
        
        # Convert ObjectIds for JSON serialization
        practice_attempts = [convert_objectid_to_str(attempt) for attempt in practice_attempts]
        
        # Analyze the data using our analytics service
        analysis = StudentAnalyticsService.analyze_strengths_weaknesses(practice_attempts)
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing strengths/weaknesses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance data: {str(e)}"
        )

@router.get("/performance-trends")
async def get_performance_trends(
    days: Optional[int] = 30,
    current_user = Depends(get_current_student)
):
    """Get performance trends over specified time period"""
    try:
        db = get_database()
        student_id = current_user['sub']
        
        # Debug logging
        print(f"🔍 TRENDS DEBUG: days parameter = {days}, type = {type(days)}")
        
        # Ensure days is an integer (defensive programming)
        if isinstance(days, str):
            print(f"🔍 TRENDS DEBUG: Converting string '{days}' to int")
            days = int(days)
        if days is None:
            days = 30
        
        print(f"🔍 TRENDS DEBUG: Final days value = {days}, type = {type(days)}")
        
        # Get practice attempts within the time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        practice_attempts_cursor = db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": student_id,
            "completed_at": {"$gte": cutoff_date}
        }).sort("completed_at", 1)
        
        practice_attempts = await practice_attempts_cursor.to_list(1000)
        practice_attempts = [convert_objectid_to_str(attempt) for attempt in practice_attempts]
        
        # Get trend analysis
        trends = StudentAnalyticsService.get_performance_trends(practice_attempts, days)
        
        return trends
        
    except Exception as e:
        print(f"Error getting performance trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance trends: {str(e)}"
        )

@router.get("/subject-breakdown")
async def get_subject_breakdown(
    current_user = Depends(get_current_student)
):
    """Get detailed breakdown by subject"""
    try:
        db = get_database()
        student_id = current_user['sub']
        
        # Aggregate performance by subject
        pipeline = [
            {"$match": {"student_id": student_id}},
            {"$group": {
                "_id": "$subject",
                "total_tests": {"$sum": 1},
                "average_score": {"$avg": "$score"},
                "highest_score": {"$max": "$score"},
                "lowest_score": {"$min": "$score"},
                "total_time": {"$sum": "$time_taken"},
                "recent_scores": {"$push": "$score"}
            }},
            {"$sort": {"average_score": -1}}
        ]
        
        subject_stats = await db[Collections.PRACTICE_ATTEMPTS].aggregate(pipeline).to_list(100)
        
        # Format the results
        breakdown = []
        for stat in subject_stats:
            subject = stat["_id"] or "General"
            
            breakdown.append({
                "subject": subject,
                "subject_display": subject.replace('_', ' ').title(),
                "total_tests": stat["total_tests"],
                "average_score": round(stat["average_score"], 1),
                "highest_score": stat["highest_score"],
                "lowest_score": stat["lowest_score"],
                "total_time_minutes": round(stat["total_time"] / 60, 1),
                "avg_time_per_test": round((stat["total_time"] / stat["total_tests"]) / 60, 1) if stat["total_tests"] > 0 else 0,
                "performance_grade": "A" if stat["average_score"] >= 90 else
                                   "B" if stat["average_score"] >= 80 else
                                   "C" if stat["average_score"] >= 70 else
                                   "D" if stat["average_score"] >= 60 else "F"
            })
        
        return {
            "subject_breakdown": breakdown,
            "total_subjects": len(breakdown),
            "best_subject": breakdown[0] if breakdown else None,
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting subject breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subject breakdown: {str(e)}"
        )

@router.get("/learning-insights")
async def get_learning_insights(
    current_user = Depends(get_current_student)
):
    """Get AI-powered learning insights and recommendations"""
    try:
        db = get_database()
        student_id = current_user['sub']
        
        # Get recent practice attempts
        recent_cutoff = datetime.utcnow() - timedelta(days=14)  # Last 2 weeks
        
        practice_attempts_cursor = db[Collections.PRACTICE_ATTEMPTS].find({
            "student_id": student_id,
            "completed_at": {"$gte": recent_cutoff}
        }).sort("completed_at", -1)
        
        recent_attempts = await practice_attempts_cursor.to_list(100)
        recent_attempts = [convert_objectid_to_str(attempt) for attempt in recent_attempts]
        
        if not recent_attempts:
            return {
                "insights": [{
                    "type": "getting_started",
                    "title": "Start Your Learning Journey",
                    "message": "Take some practice tests to get personalized insights and recommendations!",
                    "icon": "🚀",
                    "action": "Take your first practice test to begin analyzing your learning patterns."
                }],
                "study_tips": [
                    "Regular practice leads to better retention",
                    "Focus on understanding concepts, not just memorizing",
                    "Review mistakes to learn from them"
                ]
            }
        
        # Analyze patterns
        insights = []
        
        # Test frequency insight
        avg_tests_per_week = len(recent_attempts) / 2  # 2 weeks of data
        if avg_tests_per_week < 2:
            insights.append({
                "type": "frequency",
                "title": "Consider More Regular Practice", 
                "message": f"You're taking {avg_tests_per_week:.1f} tests per week. Aim for 3-4 tests weekly for better progress.",
                "icon": "📅",
                "action": "Schedule more regular practice sessions"
            })
        
        # Score consistency insight
        scores = [attempt.get('score', 0) for attempt in recent_attempts]
        if len(scores) >= 3:
            import statistics
            std_dev = statistics.stdev(scores)
            
            if std_dev > 20:
                insights.append({
                    "type": "consistency",
                    "title": "Work on Consistency",
                    "message": f"Your scores vary by {std_dev:.0f} points. Focus on consistent preparation.",
                    "icon": "📊",
                    "action": "Review your study routine and maintain regular practice"
                })
        
        # Time management insight
        avg_time = sum(attempt.get('time_taken', 0) for attempt in recent_attempts) / len(recent_attempts)
        if avg_time > 600:  # More than 10 minutes per test
            insights.append({
                "type": "time_management",
                "title": "Improve Test Speed",
                "message": f"Average test time: {avg_time/60:.1f} minutes. Practice time management.",
                "icon": "⏱️",
                "action": "Practice solving problems more quickly"
            })
        
        # Subject focus insight
        from collections import Counter
        subject_counts = Counter(attempt.get('subject', 'general') for attempt in recent_attempts)
        
        if len(subject_counts) == 1:
            insights.append({
                "type": "variety",
                "title": "Diversify Your Practice",
                "message": "You're focusing on one subject. Try practicing different subjects for well-rounded learning.",
                "icon": "🌟",
                "action": "Take tests in different subjects"
            })
        
        # Progress insight
        if len(recent_attempts) >= 5:
            recent_avg = sum(scores[-3:]) / 3  # Last 3 tests
            earlier_avg = sum(scores[:3]) / 3  # First 3 tests
            
            if recent_avg > earlier_avg + 5:
                insights.append({
                    "type": "progress",
                    "title": "Great Progress!",
                    "message": f"Your scores improved by {recent_avg - earlier_avg:.1f} points recently. Keep it up!",
                    "icon": "📈",
                    "action": "Continue your current study approach"
                })
        
        # Default positive insight if no specific patterns
        if not insights:
            insights.append({
                "type": "encouragement",
                "title": "You're Doing Great!",
                "message": "Your practice patterns show consistent effort. Keep learning and growing!",
                "icon": "🎯", 
                "action": "Continue regular practice for best results"
            })
        
        # Study tips based on performance
        study_tips = [
            "Review incorrect answers to understand mistakes",
            "Use spaced repetition for long-term retention", 
            "Practice a little bit every day rather than cramming",
            "Focus on understanding concepts, not memorization"
        ]
        
        return {
            "insights": insights,
            "study_tips": study_tips,
            "recent_activity": {
                "tests_taken": len(recent_attempts),
                "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
                "subjects_practiced": len(subject_counts)
            }
        }
        
    except Exception as e:
        print(f"Error getting learning insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning insights: {str(e)}"
        )