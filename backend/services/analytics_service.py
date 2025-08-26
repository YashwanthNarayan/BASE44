from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

class StudentAnalyticsService:
    """Service for analyzing student performance and generating insights"""
    
    @staticmethod
    def analyze_strengths_weaknesses(practice_attempts: List[Dict]) -> Dict[str, Any]:
        """
        Analyze student practice attempts to identify strengths and weaknesses
        
        Args:
            practice_attempts: List of practice test attempts
            
        Returns:
            Dict containing strengths, weaknesses, trends, and recommendations
        """
        if not practice_attempts:
            return {
                "strengths": [],
                "weaknesses": [],
                "improving_areas": [],
                "declining_areas": [],
                "overall_performance": {
                    "average_score": 0,
                    "total_tests": 0,
                    "subjects_tested": 0
                },
                "recommendations": []
            }
        
        # Group attempts by subject
        subject_performance = defaultdict(list)
        for attempt in practice_attempts:
            subject = attempt.get('subject', 'general')
            score = attempt.get('score', 0)
            date = attempt.get('completed_at') or attempt.get('created_at')
            
            subject_performance[subject].append({
                'score': score,
                'date': date,
                'attempt_id': attempt.get('id'),
                'questions_count': attempt.get('questions_count', 0),
                'time_taken': attempt.get('time_taken', 0)
            })
        
        # Analyze each subject
        strengths = []
        weaknesses = []
        improving_areas = []
        declining_areas = []
        
        for subject, attempts in subject_performance.items():
            analysis = StudentAnalyticsService._analyze_subject_performance(subject, attempts)
            
            # Classify as strength or weakness
            if analysis['classification'] == 'strength':
                strengths.append(analysis)
            elif analysis['classification'] == 'weakness':
                weaknesses.append(analysis)
            
            # Check for trends
            if analysis['trend'] == 'improving':
                improving_areas.append(analysis)
            elif analysis['trend'] == 'declining':
                declining_areas.append(analysis)
        
        # Calculate overall performance
        all_scores = [attempt.get('score', 0) for attempt in practice_attempts]
        overall_performance = {
            "average_score": round(statistics.mean(all_scores), 1) if all_scores else 0,
            "total_tests": len(practice_attempts),
            "subjects_tested": len(subject_performance),
            "highest_score": max(all_scores) if all_scores else 0,
            "lowest_score": min(all_scores) if all_scores else 0
        }
        
        # Generate recommendations
        recommendations = StudentAnalyticsService._generate_recommendations(
            strengths, weaknesses, improving_areas, declining_areas
        )
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improving_areas": improving_areas,
            "declining_areas": declining_areas,
            "overall_performance": overall_performance,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _analyze_subject_performance(subject: str, attempts: List[Dict]) -> Dict[str, Any]:
        """Analyze performance for a specific subject"""
        if not attempts:
            return {}
        
        # Sort attempts by date with safe access
        attempts.sort(key=lambda x: x.get('date') or datetime.min)
        
        # Extract scores safely
        scores = []
        for attempt in attempts:
            score = attempt.get('score', 0)
            if isinstance(score, (int, float)):
                scores.append(score)
        
        if not scores:
            return {}
        
        avg_score = statistics.mean(scores)
        attempt_count = len(scores)
        
        # Determine classification
        classification = 'neutral'
        if attempt_count >= 3:  # Need sufficient data
            if avg_score >= 80:
                classification = 'strength'
            elif avg_score <= 60:
                classification = 'weakness'
        
        # Analyze trend (last 5 attempts vs first 5)
        trend = 'stable'
        if attempt_count >= 6:
            recent_scores = scores[-3:]  # Last 3 attempts
            earlier_scores = scores[:3]  # First 3 attempts
            
            recent_avg = statistics.mean(recent_scores)
            earlier_avg = statistics.mean(earlier_scores)
            
            improvement = recent_avg - earlier_avg
            
            if improvement >= 10:
                trend = 'improving'
            elif improvement <= -10:
                trend = 'declining'
        
        # Calculate consistency with error handling
        consistency = 'stable'
        if len(scores) >= 3:
            try:
                std_dev = statistics.stdev(scores)
                if std_dev <= 5:
                    consistency = 'very_consistent'
                elif std_dev <= 15:
                    consistency = 'consistent'
                else:
                    consistency = 'inconsistent'
            except statistics.StatisticsError:
                consistency = 'stable'
        
        # Calculate time-related statistics safely
        total_time = 0
        for attempt in attempts:
            time_taken = attempt.get('time_taken', 0)
            if isinstance(time_taken, (int, float)):
                total_time += time_taken
        
        return {
            "subject": subject,
            "subject_display": subject.replace('_', ' ').title(),
            "average_score": round(avg_score, 1),
            "attempt_count": attempt_count,
            "classification": classification,
            "trend": trend,
            "consistency": consistency,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "recent_scores": scores[-3:] if len(scores) >= 3 else scores,  # Last 3 scores
            "total_time": total_time,
            "avg_time_per_test": round(total_time / attempt_count, 1) if attempt_count > 0 and total_time > 0 else 0
        }
    
    @staticmethod
    def _generate_recommendations(strengths: List, weaknesses: List, 
                                improving: List, declining: List) -> List[Dict]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Recommendations for weaknesses
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            subject = weakness['subject_display']
            avg_score = weakness['average_score']
            
            if avg_score < 40:
                priority = 'high'
                message = f"Focus on **{subject}** fundamentals - your current average is {avg_score}%. Start with basic concepts and practice daily."
            elif avg_score < 60:
                priority = 'medium'  
                message = f"Strengthen your **{subject}** skills - you're at {avg_score}%. Focus on problem-solving practice and review key concepts."
            
            recommendations.append({
                "type": "weakness_focus",
                "priority": priority,
                "subject": weakness['subject'],
                "message": message,
                "suggested_actions": [
                    f"Take practice tests in {subject} more frequently",
                    f"Review basic {subject} concepts",
                    f"Use the AI tutor for {subject} help"
                ]
            })
        
        # Recommendations for strengths
        if strengths:
            best_strength = max(strengths, key=lambda x: x['average_score'])
            subject = best_strength['subject_display']
            score = best_strength['average_score']
            
            recommendations.append({
                "type": "strength_leverage",
                "priority": "low",
                "subject": best_strength['subject'],
                "message": f"Excellent work in **{subject}** with {score}% average! Use this confidence to tackle challenging topics.",
                "suggested_actions": [
                    f"Try advanced {subject} problems",
                    f"Help other students with {subject}",
                    f"Maintain your {subject} skills with periodic review"
                ]
            })
        
        # Recommendations for improving areas
        for improving_area in improving[:2]:  # Top 2 improving areas
            subject = improving_area['subject_display']
            recommendations.append({
                "type": "momentum_keep",
                "priority": "medium",
                "subject": improving_area['subject'],
                "message": f"Great progress in **{subject}**! Keep up the momentum with consistent practice.",
                "suggested_actions": [
                    f"Continue regular {subject} practice",
                    f"Try slightly more challenging {subject} problems",
                    f"Track your {subject} improvement"
                ]
            })
        
        # Recommendations for declining areas
        for declining_area in declining[:2]:  # Top 2 declining areas
            subject = declining_area['subject_display']
            recommendations.append({
                "type": "attention_needed",
                "priority": "high",
                "subject": declining_area['subject'],
                "message": f"Your **{subject}** performance has declined recently. Let's get back on track!",
                "suggested_actions": [
                    f"Review recent {subject} mistakes",
                    f"Get help with challenging {subject} concepts",
                    f"Schedule more frequent {subject} practice"
                ]
            })
        
        # General recommendation if no specific patterns
        if not recommendations:
            recommendations.append({
                "type": "general",
                "priority": "medium", 
                "subject": "all",
                "message": "Keep practicing regularly across all subjects to build consistent performance!",
                "suggested_actions": [
                    "Take practice tests in different subjects",
                    "Use spaced repetition for review",
                    "Set daily study goals"
                ]
            })
        
        return recommendations
    
    @staticmethod
    def get_performance_trends(practice_attempts: List[Dict], days: int = 30) -> Dict[str, Any]:
        """Get performance trends over specified time period"""
        print(f"🔍 ANALYTICS DEBUG: get_performance_trends called with days={days}, type={type(days)}")
        
        # Ensure days is an integer (defensive programming)
        if isinstance(days, str):
            print(f"🔍 ANALYTICS DEBUG: Converting string '{days}' to int")
            days = int(days)
        if days is None:
            days = 30
            
        print(f"🔍 ANALYTICS DEBUG: Final days value = {days}, type = {type(days)}")
        print(f"🔍 ANALYTICS DEBUG: About to create timedelta with days={days}")
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        print(f"🔍 ANALYTICS DEBUG: Successfully created cutoff_date = {cutoff_date}")
        
        # Filter recent attempts with defensive programming
        recent_attempts = []
        for attempt in practice_attempts:
            completed_at = attempt.get('completed_at')
            if completed_at:
                try:
                    date = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    if date >= cutoff_date:
                        recent_attempts.append(attempt)
                except (ValueError, AttributeError):
                    # Skip attempts with invalid date formats
                    continue
        
        if not recent_attempts:
            return {"trend_data": [], "summary": "No recent test data available"}
        
        # Group by week with safe field access
        weekly_performance = defaultdict(list)
        for attempt in recent_attempts:
            completed_at = attempt.get('completed_at')
            score = attempt.get('score')
            
            if completed_at is not None and score is not None:
                try:
                    date = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    week_start = date - timedelta(days=date.weekday())
                    week_key = week_start.strftime('%Y-%m-%d')
                    
                    # Only add numeric scores
                    if isinstance(score, (int, float)):
                        weekly_performance[week_key].append(score)
                except (ValueError, AttributeError):
                    # Skip attempts with invalid dates or scores
                    continue
        
        # Calculate weekly averages with error handling
        trend_data = []
        for week, scores in sorted(weekly_performance.items()):
            if scores:  # Only add weeks with valid scores
                trend_data.append({
                    "week": week,
                    "average_score": round(statistics.mean(scores), 1),
                    "test_count": len(scores),
                    "highest_score": max(scores),
                    "lowest_score": min(scores)
                })
        
        # Calculate overall trend with safe access
        if len(trend_data) >= 2:
            recent_avg = statistics.mean([data['average_score'] for data in trend_data[-2:]])
            earlier_avg = statistics.mean([data['average_score'] for data in trend_data[:2]])
            trend_direction = "improving" if recent_avg > earlier_avg + 5 else \
                            "declining" if recent_avg < earlier_avg - 5 else "stable"
        else:
            trend_direction = "stable"
        
        return {
            "trend_data": trend_data,
            "trend_direction": trend_direction,
            "total_tests_period": len(recent_attempts),
            "period_days": days
        }