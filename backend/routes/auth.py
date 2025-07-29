from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
from utils.models import TokenResponse, UserSignupRequest, UserLoginRequest, UserResponse, PasswordChangeRequest
from utils.database import _select, _insert, _update
from utils.security import *
from utils.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignupRequest):
    """Register a new user with email and password"""
    
    existing_user = await _select("users", filters=[("email", user_data.email)])
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    password_hash = get_password_hash(user_data.password)
    user_record = {
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": password_hash,
        "is_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await _insert("users", user_record)
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    user = result.data[0]
    
    access_token = create_access_token(data={"sub": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(**user)
    )

@router.post("/signin", response_model=TokenResponse)
async def signin(login_data: UserLoginRequest):
    """Sign in with email and password"""
    
    result = await _select("users", filters=[("email", login_data.email)])
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user = result.data[0]
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(**user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    
    payload = verify_refresh_token(request.refresh_token)
    user_id = payload.get("sub")
    result = await _select("users", filters=[("id", user_id)])
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = result.data[0]
    
    access_token = create_access_token(data={"sub": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(**user)
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Change user password"""
    
    result = await _select("users", filters=[("id", current_user.id)], columns="password_hash")
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = result.data[0]
    
    if user_data["password_hash"] and not verify_password(request.current_password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    new_password_hash = get_password_hash(request.new_password)
    
    await _update("users", {"password_hash": new_password_hash, "updated_at": datetime.now(timezone.utc).isoformat()}, filters=[("id", current_user.id)])
    
    return MessageResponse(message="Password changed successfully")