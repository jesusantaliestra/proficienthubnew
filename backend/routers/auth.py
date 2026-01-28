"""Authentication router"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid

from database import db
from utils.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    user_type: str = "individual"
    institution_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    user_type: str
    institution_name: Optional[str] = None
    institution_id: Optional[str] = None
    created_at: str
    subscription_plan: Optional[str] = None
    language: str = "en"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    requires_password_change: bool = False

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class SettingsUpdate(BaseModel):
    language: Optional[str] = None
    theme: Optional[str] = None
    notifications: Optional[bool] = None

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hash_password(user_data.password),
        "user_type": user_data.user_type,
        "institution_name": user_data.institution_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subscription_plan": None,
        "language": "en",
        "settings": {}
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user_data.user_type)
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        user_type=user_data.user_type,
        institution_name=user_data.institution_name,
        institution_id=None,
        created_at=user_doc["created_at"],
        subscription_plan=None,
        language="en"
    )
    
    return TokenResponse(access_token=token, user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["user_type"])
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        user_type=user["user_type"],
        institution_name=user.get("institution_name"),
        institution_id=user.get("institution_id"),
        created_at=user["created_at"],
        subscription_plan=user.get("subscription_plan"),
        language=user.get("language", "en")
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response,
        "requires_password_change": user.get("requires_password_change", False)
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        user_type=current_user["user_type"],
        institution_name=current_user.get("institution_name"),
        institution_id=current_user.get("institution_id"),
        created_at=current_user["created_at"],
        subscription_plan=current_user.get("subscription_plan"),
        language=current_user.get("language", "en")
    )

@router.put("/settings")
async def update_settings(settings: SettingsUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {}
    if settings.language:
        update_data["language"] = settings.language
    if settings.theme:
        update_data["settings.theme"] = settings.theme
    if settings.notifications is not None:
        update_data["settings.notifications"] = settings.notifications
    
    if update_data:
        await db.users.update_one({"id": current_user["id"]}, {"$set": update_data})
    
    return {"message": "Settings updated successfully"}

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Change user password - required on first login with provisional credentials"""
    if not verify_password(request.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "password_hash": hash_password(request.new_password),
                "requires_password_change": False,
                "password_changed_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "Password changed successfully"}
