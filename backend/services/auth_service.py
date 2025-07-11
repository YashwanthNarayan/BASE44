from typing import Optional, Dict, Any
from backend.models.user import User, UserCreate, UserLogin, StudentProfile, TeacherProfile, UserType
from backend.utils.database import get_database, Collections, convert_objectid_to_str
from backend.utils.security import SecurityUtils, generate_join_code
from backend.utils.helpers import ValidationUtils
from fastapi import HTTPException, status
from datetime import datetime
import uuid

class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Get database instance"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user"""
        db = self._get_db()
        
        # Validate email format
        if not ValidationUtils.is_valid_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password strength
        if not ValidationUtils.is_strong_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
        
        # Check if user already exists
        existing_user = await db[Collections.USERS].find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = SecurityUtils.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "password": hashed_password,
            "name": user_data.name,
            "user_type": user_data.user_type,
            "grade_level": user_data.grade_level,
            "school_name": user_data.school_name,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert user
        await db[Collections.USERS].insert_one(user_doc)
        
        # Create profile based on user type
        if user_data.user_type == UserType.STUDENT:
            await self._create_student_profile(user_doc)
        else:
            await self._create_teacher_profile(user_doc)
        
        # Generate JWT token
        token_data = {
            "sub": user_doc["id"],
            "email": user_doc["email"],
            "user_type": user_doc["user_type"]
        }
        access_token = SecurityUtils.create_access_token(token_data)
        
        # Return user data without password
        user_response = convert_objectid_to_str(user_doc)
        del user_response["password"]
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response,
            "user_type": user_doc["user_type"]
        }
    
    async def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Login user and return JWT token"""
        db = self._get_db()
        
        # Find user by email
        user = await db[Collections.USERS].find_one({"email": login_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not SecurityUtils.verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Generate JWT token
        token_data = {
            "sub": user["id"],
            "email": user["email"],
            "user_type": user["user_type"]
        }
        access_token = SecurityUtils.create_access_token(token_data)
        
        # Return user data without password
        user_response = convert_objectid_to_str(user)
        del user_response["password"]
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response,
            "user_type": user["user_type"]
        }
    
    async def get_user_profile(self, user_id: str, user_type: str) -> Dict[str, Any]:
        """Get user profile data"""
        db = self._get_db()
        
        if user_type == UserType.STUDENT:
            profile = await db[Collections.STUDENT_PROFILES].find_one({"user_id": user_id})
            collection = Collections.STUDENT_PROFILES
        else:
            profile = await db[Collections.TEACHER_PROFILES].find_one({"user_id": user_id})
            collection = Collections.TEACHER_PROFILES
        
        if not profile:
            # Create profile if it doesn't exist
            user = await db[Collections.USERS].find_one({"id": user_id})
            if user:
                if user_type == UserType.STUDENT:
                    profile = await self._create_student_profile(user)
                else:
                    profile = await self._create_teacher_profile(user)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return convert_objectid_to_str(profile)
    
    async def _create_student_profile(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create student profile"""
        db = self._get_db()
        
        profile_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_doc["id"],
            "name": user_doc["name"],
            "email": user_doc["email"],
            "grade_level": user_doc["grade_level"],
            "joined_classes": [],
            "total_messages": 0,
            "total_tests": 0,
            "average_score": 0.0,
            "recent_scores": [],
            "study_streak": 0,
            "total_study_time": 0,
            "achievements": [],
            "xp_points": 0,
            "level": 1,
            "subjects_studied": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db[Collections.STUDENT_PROFILES].insert_one(profile_doc)
        return profile_doc
    
    async def _create_teacher_profile(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create teacher profile"""
        db = self._get_db()
        
        profile_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_doc["id"],
            "name": user_doc["name"],
            "email": user_doc["email"],
            "school_name": user_doc.get("school_name", ""),
            "subjects_taught": [],
            "created_classes": [],
            "total_students": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db[Collections.TEACHER_PROFILES].insert_one(profile_doc)
        return profile_doc

# Global auth service instance
auth_service = AuthService()