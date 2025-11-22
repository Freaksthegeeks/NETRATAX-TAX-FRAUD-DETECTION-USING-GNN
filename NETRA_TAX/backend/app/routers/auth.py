"""
Authentication Router for NETRA TAX
Login, signup, token refresh, user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    get_current_user,
    decode_token
)
from app.core.config import settings
from app.models.schemas import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    UserResponse,
    TokenData
)
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Mock user database (replace with real DB later)
MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@netratax.com",
        "full_name": "Admin User",
        "hashed_password": hash_password("admin123"),
        "role": "admin",
        "roles": ["admin"],
        "is_active": True
    },
    "auditor": {
        "id": 2,
        "username": "auditor",
        "email": "auditor@netratax.com",
        "full_name": "Auditor User",
        "hashed_password": hash_password("auditor123"),
        "role": "auditor",
        "roles": ["auditor"],
        "is_active": True
    },
    "analyst": {
        "id": 3,
        "username": "analyst",
        "email": "analyst@netratax.com",
        "full_name": "Analyst User",
        "hashed_password": hash_password("analyst123"),
        "role": "analyst",
        "roles": ["analyst"],
        "is_active": True
    }
}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Returns access token and user information
    """
    # Find user
    user = MOCK_USERS.get(request.username)
    
    if not user or not verify_password(request.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(
        user_id=user['id'],
        username=user['username'],
        email=user['email'],
        roles=[user['role']]
    )
    
    refresh_token = create_refresh_token(user_id=user['id'])
    
    logger.info(f"User {request.username} logged in successfully")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active']
        }
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    User signup endpoint
    Creates new user account
    """
    # Check if user exists
    if request.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user
    new_user_id = max([u['id'] for u in MOCK_USERS.values()]) + 1
    new_user = {
        "id": new_user_id,
        "username": request.username,
        "email": request.email,
        "full_name": request.full_name,
        "hashed_password": hash_password(request.password),
        "role": request.role.value,
        "roles": [request.role.value],
        "is_active": True
    }
    
    MOCK_USERS[request.username] = new_user
    
    logger.info(f"New user registered: {request.username} with role {request.role}")
    
    return UserResponse(
        id=new_user['id'],
        username=new_user['username'],
        email=new_user['email'],
        full_name=new_user['full_name'],
        role=new_user['role'],
        is_active=new_user['is_active'],
        created_at=__import__('datetime').datetime.now()
    )


@router.post("/refresh")
async def refresh_token(token: str):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(token)
        
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get('user_id')
        
        # Find user (from mock DB for now)
        user = None
        for u in MOCK_USERS.values():
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            user_id=user['id'],
            username=user['username'],
            email=user['email'],
            roles=[user['role']]
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    # Find user from mock DB
    for user in MOCK_USERS.values():
        if user['id'] == current_user.get('user_id'):
            return UserResponse(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                full_name=user['full_name'],
                role=user['role'],
                is_active=user['is_active'],
                created_at=__import__('datetime').datetime.now()
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (client-side token management)
    """
    logger.info(f"User {current_user.get('username')} logged out")
    
    return {
        "message": "Successfully logged out",
        "status": "success"
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    """
    # Find user
    user = None
    for u in MOCK_USERS.values():
        if u['id'] == current_user.get('user_id'):
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(old_password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be at least 8 characters long"
        )
    
    # Update password
    user['hashed_password'] = hash_password(new_password)
    
    logger.info(f"User {user['username']} changed password")
    
    return {
        "message": "Password changed successfully",
        "status": "success"
    }
