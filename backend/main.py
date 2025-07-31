from fastapi import FastAPI, HTTPException, status, Depends 
from fastapi.middleware.cors import CORSMiddleware
from utils.config import settings
from utils.helpers import enhanced_emotion_analysis, intelligent_media_parsing, enhanced_qloo_recommendations, create_personalized_ritual
from utils.logger import logger
from utils.database import _select, _insert, _update
from utils.models import *
from utils.security import *
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import json

app = FastAPI(name="Sanctuary API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"success": True}


@app.post("/signup", response_model=TokenResponse)
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

@app.post("/signin", response_model=TokenResponse)
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

@app.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.post("/refresh", response_model=TokenResponse)
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

@app.post("/change-password", response_model=MessageResponse)
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

@app.post("/analyze-emotion", response_model=Dict[str, Any])
async def analyze_emotion(request: EmotionRequest, user: str = Depends(get_current_user)):
    """Enhanced emotion analysis with detailed insights"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        analysis = await enhanced_emotion_analysis(request.text, user.id)
        
        return {
            "success": True,
            "emotional_need": analysis["primary_need"],
            "detailed_analysis": analysis,
            "user_id": user.id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Emotion analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/get-ritual", response_model=RitualResponse)
async def create_ritual(request: RitualRequest, user: str = Depends(get_current_user)):
    """Main ritual creation endpoint with full pipeline"""
    if not settings.OPENAI_API_KEY or not settings.QLOO_API_KEY:
        raise HTTPException(status_code=500, detail="Required API keys not configured")
        
    try:
        # Step 1: Enhanced emotion analysis
        emotional_analysis = await enhanced_emotion_analysis(request.text, user.id)
        # print("emotional_analysis", emotional_analysis)
        # {
        #     "primary_need": request.emotional_need,
        #     "wellness_category": "general",
        #     "recommended_duration": "30min",
        #     "urgency": "medium",
        #     "stress_level": 5
        # }
        
        # Step 2: Parse media intelligently
        structured_media = await intelligent_media_parsing(request.comfort_media)
        # print("structured_media", structured_media)
        if not structured_media:
            raise HTTPException(
                status_code=400,
                detail="Could not identify any media from your input. Please be more specific."
            )
        
        # Step 3: Get enhanced recommendations
        recommendations = await enhanced_qloo_recommendations(structured_media, emotional_analysis)
        # print("recommendations", recommendations)
        # Step 4: Create personalized ritual
        ritual_content = await create_personalized_ritual(
            emotional_analysis,
            recommendations,
            request.preferences
        )
        # print("ritual_content", ritual_content)
        
        # Step 5: Save to database
        # print("user id", user.id)
        ritual_record = RitualRecord(
            user_id=str(user.id),
            emotional_need=emotional_analysis.get("primary_need", "general"),
            comfort_media=request.comfort_media,
            ritual_content=ritual_content,
            recommendations=recommendations,
            estimated_duration=emotional_analysis.get("recommended_duration", "30min"),
            created_at=datetime.now(timezone.utc).isoformat()
        )
        with open("ritual.json", "w") as f:
            json.dump(ritual_record.dict(), f)
        ritual = await _insert("rituals", ritual_record.model_dump())
        
        return RitualResponse(
            ritual=ritual_record,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ritual creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ritual")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest, user: str = Depends(get_current_user)):
    """Submit feedback for a ritual"""
    ritual = await _select("rituals", {"id": request.ritual_id})
    if not ritual:
        raise HTTPException(status_code=404, detail="Ritual not found")
    
    await _update(table="rituals", filters=[("id", request.ritual_id)], data={"rating": request.rating})
    
    return {
        "success": True,
        "message": "Feedback submitted successfully",
        "ritual_id": request.ritual_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)