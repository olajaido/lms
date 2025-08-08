from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from .models import UserRole, UserStatus


class UserBase(BaseModel):
    """Common attributes shared by user create and update schemas."""
    email: EmailStr
    name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    status: UserStatus = UserStatus.ACTIVE
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    """Schema used when registering a new user."""
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """Schema used for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema used to update user profile data."""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None


class User(UserBase):
    """Schema returned to the client representing a user."""
    id: int
    is_verified: bool
    is_active: bool
    last_login: Optional[datetime] = None
    login_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation."""
    token: str


class UserProfile(BaseModel):
    """Schema for user profile information."""
    id: int
    email: str
    name: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_verified: bool
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_count: int
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Schema for user statistics."""
    total_users: int
    active_users: int
    verified_users: int
    users_by_role: Dict[str, int]
    recent_registrations: int  # Users registered in last 30 days


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: User
    token: Token
    message: str
    success: bool = True


class UserResponse(BaseModel):
    """Schema for user operation response."""
    user: User
    message: str
    success: bool = True