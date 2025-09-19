"""
Authentication API routes
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from ...services import auth_service
from ...schemas import UserRegistration, UserLogin, Token, UserProfile
from ...models import User
from .auth import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserRegistration):
    """Register a new user"""
    result = await auth_service.register_user(user_data)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Authenticate user and return token"""
    result = await auth_service.authenticate_user(login_data)
    
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )

@router.put("/me")
async def update_profile(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    result = await auth_service.update_user_profile(str(current_user.id), update_data)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/change-password")
async def change_password(
    password_data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400, 
            detail="Current password and new password are required"
        )
    
    result = await auth_service.change_password(
        str(current_user.id), 
        current_password, 
        new_password
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

__all__ = ["router"]