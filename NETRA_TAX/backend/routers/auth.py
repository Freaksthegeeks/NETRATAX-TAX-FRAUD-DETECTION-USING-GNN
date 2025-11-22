"""
Authentication Router
JWT-based authentication for NETRA TAX
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
import secrets

router = APIRouter()

# Security
SECRET_KEY = secrets.token_urlsafe(32)  # Generate random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory user store (replace with database in production)
# Initialize users lazily to avoid bcrypt issues at import time
def _init_users_db():
    return {
        "admin": {
            "username": "admin",
            "email": "admin@netratax.gov.in",
            "hashed_password": pwd_context.hash("admin123"),
            "role": "admin",
            "full_name": "System Administrator"
        },
        "auditor": {
            "username": "auditor",
            "email": "auditor@netratax.gov.in",
            "hashed_password": pwd_context.hash("auditor123"),
            "role": "auditor",
            "full_name": "Tax Auditor"
        }
    }

users_db = {}

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "analyst"

class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    """Get user from database"""
    if not users_db:
        users_db.update(_init_users_db())
    return users_db.get(username)

def authenticate_user(username: str, password: str):
    """Authenticate user"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup):
    """User registration"""
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "role": user_data.role,
        "full_name": user_data.full_name
    }
    
    return UserResponse(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        full_name=user_data.full_name
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout"""
    # In production, add token to blacklist
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        full_name=current_user["full_name"]
    )

