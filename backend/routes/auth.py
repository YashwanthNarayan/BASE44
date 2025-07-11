from fastapi import APIRouter, HTTPException, Depends, status
from backend.models.user import UserCreate, UserLogin
from backend.services.auth_service import auth_service
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        result = await auth_service.register_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login(login_data: UserLogin):
    """Login user and return access token"""
    try:
        result = await auth_service.login_user(login_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
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
            detail=f"Failed to get profile: {str(e)}"
        )