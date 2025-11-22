"""
Authentication & Security Module for NETRA TAX
JWT tokens, user management, role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: str
    full_name: str
    role: str  # admin, auditor, gst_officer, analyst, viewer


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserInDB(UserBase):
    """User in database"""
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Token payload"""
    user_id: int
    username: str
    email: str
    roles: List[str]
    exp: datetime


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# Password Management
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(
    user_id: int,
    username: str,
    email: str,
    roles: List[str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# Dependency Injection
# ============================================================================

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> Dict:
    """Get current authenticated user from token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return payload


async def require_role(*required_roles: str):
    """Role-based access control dependency factory"""
    async def check_role(current_user: Dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    
    return check_role


# ============================================================================
# Permission Checking
# ============================================================================

def has_permission(user_roles: List[str], required_permission: str) -> bool:
    """Check if user roles have required permission"""
    for role in user_roles:
        permissions = settings.USER_ROLES.get(role, [])
        if required_permission in permissions:
            return True
    return False


def require_permissions(*permissions: str):
    """Check if user has any of the required permissions"""
    async def check_permissions(current_user: Dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(
            has_permission([role], perm) 
            for role in user_roles 
            for perm in permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions"
            )
        return current_user
    
    return check_permissions
