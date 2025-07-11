import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import json

# Simple in-memory cache (in production, use Redis)
api_cache = {}
CACHE_DURATION = timedelta(hours=24)  # Cache for 24 hours

class CacheUtils:
    @staticmethod
    def get_cache_key(prompt: str, subject: Optional[str] = None) -> str:
        """Generate cache key for similar queries"""
        normalized = prompt.lower().strip()
        cache_data = f"{normalized}_{subject or 'general'}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    @staticmethod
    def get_cached_response(cache_key: str) -> Optional[str]:
        """Get cached response if it exists and is valid"""
        if cache_key in api_cache:
            cached_item = api_cache[cache_key]
            if datetime.utcnow() - cached_item['timestamp'] < CACHE_DURATION:
                return cached_item['response']
            else:
                # Remove expired cache
                del api_cache[cache_key]
        return None
    
    @staticmethod
    def cache_response(cache_key: str, response: str):
        """Cache a response"""
        api_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.utcnow()
        }
        
        # Simple cache cleanup - remove old entries (keep last 1000)
        if len(api_cache) > 1000:
            oldest_keys = sorted(api_cache.keys(), 
                               key=lambda k: api_cache[k]['timestamp'])[:100]
            for key in oldest_keys:
                del api_cache[key]

class ValidationUtils:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check if password meets security requirements"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special

class FormatUtils:
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def calculate_reading_time(text: str) -> int:
        """Calculate estimated reading time in minutes (assuming 200 WPM)"""
        word_count = len(text.split())
        reading_time = max(1, word_count // 200)  # Minimum 1 minute
        return reading_time
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

class ScoreUtils:
    @staticmethod
    def calculate_percentage(correct: int, total: int) -> float:
        """Calculate percentage score"""
        if total == 0:
            return 0.0
        return round((correct / total) * 100, 1)
    
    @staticmethod
    def get_grade_from_percentage(percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 85:
            return "A"
        elif percentage >= 80:
            return "A-"
        elif percentage >= 75:
            return "B+"
        elif percentage >= 70:
            return "B"
        elif percentage >= 65:
            return "B-"
        elif percentage >= 60:
            return "C+"
        elif percentage >= 55:
            return "C"
        elif percentage >= 50:
            return "C-"
        else:
            return "F"
    
    @staticmethod
    def calculate_xp_gain(score_percentage: float, difficulty: str) -> int:
        """Calculate XP gain based on score and difficulty"""
        base_xp = 10
        
        # Difficulty multiplier
        difficulty_multiplier = {
            "easy": 1.0,
            "medium": 1.5,
            "hard": 2.0,
            "mixed": 1.7
        }.get(difficulty, 1.0)
        
        # Score multiplier
        score_multiplier = score_percentage / 100
        
        xp_gain = int(base_xp * difficulty_multiplier * score_multiplier)
        return max(1, xp_gain)  # Minimum 1 XP

class DateUtils:
    @staticmethod
    def get_start_of_day(date: datetime) -> datetime:
        """Get start of day for given datetime"""
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_day(date: datetime) -> datetime:
        """Get end of day for given datetime"""
        return date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def days_between(date1: datetime, date2: datetime) -> int:
        """Calculate days between two dates"""
        return abs((date2 - date1).days)