from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
from passlib.context import CryptContext

from .models import (
    User, RefreshToken, UserSession, PasswordReset, EmailVerification,
    UserRole, UserStatus
)
from .schemas import (
    UserCreate, UserUpdate, TokenData
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


# User CRUD operations
async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        name=user_create.name,
        role=user_create.role,
        status=user_create.status,
        profile_picture=user_create.profile_picture,
        bio=user_create.bio,
        phone_number=user_create.phone_number,
        date_of_birth=user_create.date_of_birth,
        preferences=user_create.preferences
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None
) -> List[User]:
    """Get users with optional filtering."""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if status:
        query = query.where(User.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_user(
    db: AsyncSession, user_id: int, user_update: UserUpdate
) -> Optional[User]:
    """Update user."""
    user = await get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Soft delete user by setting is_active to False."""
    user = await get_user(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    user.status = UserStatus.INACTIVE
    user.updated_at = datetime.utcnow()
    await db.commit()
    return True


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def update_user_login(db: AsyncSession, user_id: int) -> Optional[User]:
    """Update user's last login time and increment login count."""
    user = await get_user(db, user_id)
    if not user:
        return None
    
    user.last_login = datetime.utcnow()
    user.login_count += 1
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


# Refresh Token CRUD operations
async def create_refresh_token(
    db: AsyncSession, user_id: int, expires_delta: timedelta
) -> RefreshToken:
    """Create a new refresh token."""
    token = generate_token()
    expires_at = datetime.utcnow() + expires_delta
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def get_refresh_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
    """Get refresh token by token string."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    """Revoke a refresh token."""
    refresh_token = await get_refresh_token(db, token)
    if not refresh_token:
        return False
    
    refresh_token.is_revoked = True
    refresh_token.revoked_at = datetime.utcnow()
    await db.commit()
    return True


async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> bool:
    """Revoke all refresh tokens for a user."""
    result = await db.execute(
        select(RefreshToken).where(
            and_(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
        )
    )
    tokens = result.scalars().all()
    
    for token in tokens:
        token.is_revoked = True
        token.revoked_at = datetime.utcnow()
    
    await db.commit()
    return True


# User Session CRUD operations
async def create_user_session(
    db: AsyncSession, 
    user_id: int, 
    session_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_delta: timedelta = timedelta(hours=24)
) -> UserSession:
    """Create a new user session."""
    expires_at = datetime.utcnow() + expires_delta
    
    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_user_session(db: AsyncSession, session_id: str) -> Optional[UserSession]:
    """Get user session by session ID."""
    result = await db.execute(
        select(UserSession).where(UserSession.session_id == session_id)
    )
    return result.scalar_one_or_none()


async def update_session_activity(db: AsyncSession, session_id: str) -> bool:
    """Update session last activity time."""
    session = await get_user_session(db, session_id)
    if not session:
        return False
    
    session.last_activity = datetime.utcnow()
    await db.commit()
    return True


async def revoke_user_session(db: AsyncSession, session_id: str) -> bool:
    """Revoke a user session."""
    session = await get_user_session(db, session_id)
    if not session:
        return False
    
    session.is_active = False
    await db.commit()
    return True


async def revoke_all_user_sessions(db: AsyncSession, user_id: int) -> bool:
    """Revoke all sessions for a user."""
    result = await db.execute(
        select(UserSession).where(
            and_(UserSession.user_id == user_id, UserSession.is_active == True)
        )
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        session.is_active = False
    
    await db.commit()
    return True


# Password Reset CRUD operations
async def create_password_reset(
    db: AsyncSession, user_id: int, expires_delta: timedelta = timedelta(hours=1)
) -> PasswordReset:
    """Create a password reset token."""
    token = generate_token()
    expires_at = datetime.utcnow() + expires_delta
    
    # Revoke any existing password reset tokens for this user
    await revoke_password_reset_tokens(db, user_id)
    
    password_reset = PasswordReset(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(password_reset)
    await db.commit()
    await db.refresh(password_reset)
    return password_reset


async def get_password_reset(db: AsyncSession, token: str) -> Optional[PasswordReset]:
    """Get password reset by token."""
    result = await db.execute(
        select(PasswordReset).where(PasswordReset.token == token)
    )
    return result.scalar_one_or_none()


async def use_password_reset(db: AsyncSession, token: str) -> bool:
    """Mark password reset token as used."""
    password_reset = await get_password_reset(db, token)
    if not password_reset:
        return False
    
    password_reset.is_used = True
    password_reset.used_at = datetime.utcnow()
    await db.commit()
    return True


async def revoke_password_reset_tokens(db: AsyncSession, user_id: int) -> bool:
    """Revoke all password reset tokens for a user."""
    result = await db.execute(
        select(PasswordReset).where(
            and_(PasswordReset.user_id == user_id, PasswordReset.is_used == False)
        )
    )
    tokens = result.scalars().all()
    
    for token in tokens:
        token.is_used = True
        token.used_at = datetime.utcnow()
    
    await db.commit()
    return True


# Email Verification CRUD operations
async def create_email_verification(
    db: AsyncSession, user_id: int, expires_delta: timedelta = timedelta(hours=24)
) -> EmailVerification:
    """Create an email verification token."""
    token = generate_token()
    expires_at = datetime.utcnow() + expires_delta
    
    # Revoke any existing email verification tokens for this user
    await revoke_email_verification_tokens(db, user_id)
    
    email_verification = EmailVerification(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(email_verification)
    await db.commit()
    await db.refresh(email_verification)
    return email_verification


async def get_email_verification(db: AsyncSession, token: str) -> Optional[EmailVerification]:
    """Get email verification by token."""
    result = await db.execute(
        select(EmailVerification).where(EmailVerification.token == token)
    )
    return result.scalar_one_or_none()


async def use_email_verification(db: AsyncSession, token: str) -> bool:
    """Mark email verification token as used and verify user."""
    email_verification = await get_email_verification(db, token)
    if not email_verification:
        return False
    
    # Mark token as used
    email_verification.is_used = True
    email_verification.used_at = datetime.utcnow()
    
    # Verify user
    user = await get_user(db, email_verification.user_id)
    if user:
        user.is_verified = True
        user.status = UserStatus.ACTIVE
        user.updated_at = datetime.utcnow()
    
    await db.commit()
    return True


async def revoke_email_verification_tokens(db: AsyncSession, user_id: int) -> bool:
    """Revoke all email verification tokens for a user."""
    result = await db.execute(
        select(EmailVerification).where(
            and_(EmailVerification.user_id == user_id, EmailVerification.is_used == False)
        )
    )
    tokens = result.scalars().all()
    
    for token in tokens:
        token.is_used = True
        token.used_at = datetime.utcnow()
    
    await db.commit()
    return True


# Statistics and Analytics
async def get_user_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get user statistics."""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Active users
    result = await db.execute(select(func.count(User.id)).where(User.is_active == True))
    active_users = result.scalar()
    
    # Verified users
    result = await db.execute(select(func.count(User.id)).where(User.is_verified == True))
    verified_users = result.scalar()
    
    # Users by role
    users_by_role = {}
    for role in UserRole:
        result = await db.execute(select(func.count(User.id)).where(User.role == role))
        users_by_role[role.value] = result.scalar()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    recent_registrations = result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "users_by_role": users_by_role,
        "recent_registrations": recent_registrations
    }