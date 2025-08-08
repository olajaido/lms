from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from passlib.context import CryptContext

from . import crud, models, schemas
from .database import engine, get_db

app = FastAPI(title="User Service", version="1.0.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# JWT Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[schemas.TokenData]:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if user_id is None:
            return None
        return schemas.TokenData(user_id=user_id, email=email, role=role)
    except jwt.PyJWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """Get current user from JWT token."""
    token = credentials.credentials
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await crud.get_user(db, user_id=token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: str):
    """Dependency to require specific user role."""
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AuthResponse:
    """Register a new user."""
    user = await crud.create_user(db, user_create)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    # Store refresh token in database
    await crud.create_refresh_token(db, user.id, refresh_token_expires)
    
    # Update user login info
    await crud.update_user_login(db, user.id)
    
    return schemas.AuthResponse(
        user=schemas.User.from_orm(user),
        token=schemas.Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        message="User registered successfully"
    )


@app.post("/api/v1/auth/login", response_model=schemas.AuthResponse)
async def login(
    user_login: schemas.UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> schemas.AuthResponse:
    """Login user."""
    user = await crud.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    # Store refresh token in database
    await crud.create_refresh_token(db, user.id, refresh_token_expires)
    
    # Update user login info
    await crud.update_user_login(db, user.id)
    
    return schemas.AuthResponse(
        user=schemas.User.from_orm(user),
        token=schemas.Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        message="Login successful"
    )


@app.post("/api/v1/auth/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_token_request: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> schemas.Token:
    """Refresh access token using refresh token."""
    # Verify refresh token
    token_data = verify_token(refresh_token_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists in database
    db_refresh_token = await crud.get_refresh_token(db, refresh_token_request.refresh_token)
    if not db_refresh_token or db_refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(token_data.user_id), "email": token_data.email, "role": token_data.role},
        expires_delta=access_token_expires
    )
    
    return schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token_request.refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.post("/api/v1/auth/logout")
async def logout(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout user by revoking all tokens."""
    await crud.revoke_all_user_tokens(db, current_user.id)
    await crud.revoke_all_user_sessions(db, current_user.id)
    return {"message": "Logout successful"}


# User endpoints
@app.get("/api/v1/users/me", response_model=schemas.UserProfile)
async def get_current_user_profile(
    current_user: models.User = Depends(get_current_active_user),
) -> schemas.UserProfile:
    """Get current user profile."""
    return schemas.UserProfile.from_orm(current_user)


@app.put("/api/v1/users/me", response_model=schemas.UserResponse)
async def update_current_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    """Update current user profile."""
    user = await crud.update_user(db, current_user.id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse(
        user=schemas.User.from_orm(user),
        message="Profile updated successfully"
    )


@app.get("/api/v1/users/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.User:
    """Get user by ID (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User.from_orm(user)


@app.get("/api/v1/users", response_model=List[schemas.User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: models.User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> List[schemas.User]:
    """Get users (admin only)."""
    users = await crud.get_users(db, skip=skip, limit=limit, role=role, status=status)
    return [schemas.User.from_orm(user) for user in users]


@app.put("/api/v1/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    """Update user (admin only)."""
    user = await crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse(
        user=schemas.User.from_orm(user),
        message="User updated successfully"
    )


@app.delete("/api/v1/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Delete user (admin only)."""
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# Password reset endpoints
@app.post("/api/v1/auth/password-reset")
async def request_password_reset(
    password_reset_request: schemas.PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset."""
    user = await crud.get_user_by_email(db, password_reset_request.email)
    if user:
        await crud.create_password_reset(db, user.id)
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@app.post("/api/v1/auth/password-reset/confirm")
async def confirm_password_reset(
    password_reset_confirm: schemas.PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Confirm password reset."""
    password_reset = await crud.get_password_reset(db, password_reset_confirm.token)
    if not password_reset or password_reset.is_used or password_reset.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Update user password
    user = await crud.get_user(db, password_reset.user_id)
    if user:
        hashed_password = crud.get_password_hash(password_reset_confirm.new_password)
        user.hashed_password = hashed_password
        user.updated_at = datetime.utcnow()
        await db.commit()
    
    # Mark token as used
    await crud.use_password_reset(db, password_reset_confirm.token)
    
    return {"message": "Password reset successful"}


# Email verification endpoints
@app.post("/api/v1/auth/email-verification")
async def request_email_verification(
    email_verification_request: schemas.EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request email verification."""
    user = await crud.get_user_by_email(db, email_verification_request.email)
    if user and not user.is_verified:
        await crud.create_email_verification(db, user.id)
    return {"message": "If the email exists and is not verified, a verification link has been sent"}


@app.post("/api/v1/auth/email-verification/confirm")
async def confirm_email_verification(
    email_verification_confirm: schemas.EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Confirm email verification."""
    success = await crud.use_email_verification(db, email_verification_confirm.token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Email verified successfully"}


# Statistics endpoints
@app.get("/api/v1/stats/users", response_model=schemas.UserStats)
async def get_user_stats(
    current_user: models.User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> schemas.UserStats:
    """Get user statistics (admin only)."""
    stats = await crud.get_user_stats(db)
    return schemas.UserStats(**stats)