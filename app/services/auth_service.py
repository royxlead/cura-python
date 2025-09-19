"""
Authentication Service for user management and JWT tokens
Handles user registration, login, and authentication
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId

from ..models import User, UserRole
from ..core.config import settings
from ..schemas import UserRegistration, UserLogin, Token

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None
    
    async def register_user(self, user_data: UserRegistration) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await User.find_one(
                User.email == user_data.email
            )
            if existing_user:
                return {"error": "Email already registered"}
            
            existing_username = await User.find_one(
                User.username == user_data.username
            )
            if existing_username:
                return {"error": "Username already taken"}
            
            # Create new user
            user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=self.get_password_hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=UserRole.PATIENT,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            await user.insert()
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "created_at": user.created_at.isoformat()
                },
                "token": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": settings.access_token_expire_minutes * 60
                }
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {"error": f"Registration failed: {str(e)}"}
    
    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return token"""
        try:
            # Find user by email
            user = await User.find_one(User.email == login_data.email)
            if not user:
                return {"error": "Invalid email or password"}
            
            # Verify password
            if not self.verify_password(login_data.password, user.password_hash):
                return {"error": "Invalid email or password"}
            
            # Check if user is active
            if not user.is_active:
                return {"error": "Account is deactivated"}
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            await user.save()
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "last_login": user.last_login.isoformat()
                },
                "token": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": settings.access_token_expire_minutes * 60
                }
            }
            
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            return {"error": f"Authentication failed: {str(e)}"}
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = await User.get(ObjectId(user_id))
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Get current user failed: {e}")
            return None
    
    async def update_user_profile(
        self, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile"""
        try:
            user = await User.get(ObjectId(user_id))
            if not user:
                return {"error": "User not found"}
            
            # Update allowed fields
            allowed_fields = [
                "first_name", "last_name", "phone", 
                "date_of_birth", "address", "medical_history",
                "emergency_contact"
            ]
            
            for field, value in update_data.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone.utc)
            await user.save()
            
            return {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "updated_at": user.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"User profile update failed: {e}")
            return {"error": f"Profile update failed: {str(e)}"}
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> Dict[str, Any]:
        """Change user password"""
        try:
            user = await User.get(ObjectId(user_id))
            if not user:
                return {"error": "User not found"}
            
            # Verify current password
            if not self.verify_password(current_password, user.password_hash):
                return {"error": "Current password is incorrect"}
            
            # Update password
            user.password_hash = self.get_password_hash(new_password)
            user.updated_at = datetime.now(timezone.utc)
            await user.save()
            
            return {"message": "Password updated successfully"}
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return {"error": f"Password change failed: {str(e)}"}

# Global auth service instance
auth_service = AuthService()

__all__ = ["auth_service", "AuthService"]