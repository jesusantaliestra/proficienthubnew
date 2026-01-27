from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import stripe
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'proficienthub-secret-key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Security
security = HTTPBearer()

app = FastAPI(title="ProficientHub API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserBase(BaseModel):
    email: EmailStr
    name: str
    user_type: str = Field(default="individual")

class UserCreate(UserBase):
    password: str
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

class StudentCreate(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    email: str
    name: str
    institution_id: str
    progress: Dict[str, Any] = {}
    risk_score: float = 0.0
    pass_probability: float = 0.0
    engagement_score: float = 0.0
    created_at: str

class ExamAttemptCreate(BaseModel):
    exam_type: str
    section: str
    answers: List[Dict[str, Any]]
    time_spent: int

class ExamAttemptResponse(BaseModel):
    id: str
    user_id: str
    exam_type: str
    section: str
    score: float
    feedback: str
    time_spent: int
    created_at: str

class AITutorMessage(BaseModel):
    message: str
    exam_type: str
    context: Optional[str] = None

class LibraryItemCreate(BaseModel):
    title: str
    item_type: str  # material, flashcard, audio, video
    content: Optional[str] = None
    description: Optional[str] = None
    exam_type: Optional[str] = None
    tags: List[str] = []

class LibraryItemResponse(BaseModel):
    id: str
    institution_id: str
    title: str
    item_type: str
    content: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    exam_type: Optional[str] = None
    tags: List[str] = []
    created_at: str
    offline_available: bool = True

class FlashcardCreate(BaseModel):
    title: str
    cards: List[Dict[str, str]]  # [{front: str, back: str}]
    exam_type: Optional[str] = None
    tags: List[str] = []

class SettingsUpdate(BaseModel):
    language: Optional[str] = None
    theme: Optional[str] = None
    notifications: Optional[bool] = None

# ==================== AUTH UTILITIES ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, user_type: str) -> str:
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/register", response_model=TokenResponse)
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
        created_at=user_doc["created_at"],
        subscription_plan=None,
        language="en"
    )
    
    return TokenResponse(access_token=token, user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
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

@api_router.get("/auth/me", response_model=UserResponse)
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

@api_router.put("/auth/settings")
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

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@api_router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Change user password - required on first login with provisional credentials"""
    # Verify current password
    if not verify_password(request.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password strength
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Update password and mark as changed
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

# ==================== WHITE-LABEL & INSTITUTION BRANDING ====================

class InstitutionBrandingUpdate(BaseModel):
    name: str
    logo_url: Optional[str] = None
    primary_color: str = "#58CC02"
    secondary_color: str = "#46A302"
    tagline: Optional[str] = None
    custom_domain: Optional[str] = None
    hide_powered_by: bool = True

@api_router.get("/institution/branding/{slug}")
async def get_institution_branding(slug: str):
    """Get institution branding for white-label portal"""
    institution = await db.users.find_one(
        {"institution_slug": slug, "user_type": "institution"},
        {"_id": 0, "branding": 1, "institution_name": 1}
    )
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    branding = institution.get("branding", {})
    return {
        "name": branding.get("name", institution.get("institution_name", "Student Portal")),
        "logo": branding.get("logo_url"),
        "primaryColor": branding.get("primary_color", "#58CC02"),
        "secondaryColor": branding.get("secondary_color", "#46A302"),
        "tagline": branding.get("tagline", "Access your exam preparation materials"),
        "hide_powered_by": branding.get("hide_powered_by", True)
    }

@api_router.put("/institution/branding")
async def update_institution_branding(
    branding: InstitutionBrandingUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Update institution branding settings (white-label)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update branding")
    
    # Generate slug from name if not exists
    slug = current_user.get("institution_slug")
    if not slug:
        slug = branding.name.lower().replace(" ", "-").replace("'", "")[:50]
        # Ensure unique slug
        existing = await db.users.find_one({"institution_slug": slug})
        if existing and existing["id"] != current_user["id"]:
            slug = f"{slug}-{current_user['id'][:8]}"
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "institution_slug": slug,
                "branding": {
                    "name": branding.name,
                    "logo_url": branding.logo_url,
                    "primary_color": branding.primary_color,
                    "secondary_color": branding.secondary_color,
                    "tagline": branding.tagline,
                    "custom_domain": branding.custom_domain,
                    "hide_powered_by": branding.hide_powered_by
                }
            }
        }
    )
    
    return {
        "message": "Branding updated successfully",
        "student_portal_url": f"/student-portal/{slug}"
    }

@api_router.get("/institution/branding")
async def get_my_branding(current_user: dict = Depends(get_current_user)):
    """Get current institution's branding settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access branding")
    
    return {
        "slug": current_user.get("institution_slug"),
        "branding": current_user.get("branding", {}),
        "student_portal_url": f"/student-portal/{current_user.get('institution_slug', '')}" if current_user.get("institution_slug") else None
    }

# ==================== STUDENT MANAGEMENT WITH CREDITS ====================

class StudentCreateWithCredits(BaseModel):
    email: str
    name: str
    exam_type: str  # The exam they are preparing for
    credits: int = 100  # Default credits
    
@api_router.post("/institution/students/create")
async def create_student_with_credentials(
    student_data: StudentCreateWithCredits,
    current_user: dict = Depends(get_current_user)
):
    """Create a student with provisional credentials and credits"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create students")
    
    # Check if email already exists
    existing = await db.users.find_one({"email": student_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate provisional password
    import secrets
    import string
    provisional_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    student_id = str(uuid.uuid4())
    student_doc = {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "password_hash": hash_password(provisional_password),
        "user_type": "student",
        "institution_id": current_user["id"],
        "institution_slug": current_user.get("institution_slug"),
        "institution_name": current_user.get("institution_name"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_password_change": True,  # Must change on first login
        "provisional_password": provisional_password,  # Store temporarily for display
        "credits": student_data.credits,
        "credits_used": 0,
        "current_exam": student_data.exam_type,
        "exam_access": [student_data.exam_type],  # Only one exam at a time
        "status": "active",
        "language": "en",
        "settings": {}
    }
    
    await db.users.insert_one(student_doc)
    
    return {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "provisional_password": provisional_password,
        "credits": student_data.credits,
        "exam_type": student_data.exam_type,
        "message": "Student created. Share the provisional password with the student. They will be required to change it on first login."
    }

@api_router.post("/institution/students/bulk-create")
async def bulk_create_students(
    students: List[StudentCreateWithCredits],
    current_user: dict = Depends(get_current_user)
):
    """Create multiple students at once"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create students")
    
    created = []
    errors = []
    
    for student_data in students:
        try:
            existing = await db.users.find_one({"email": student_data.email})
            if existing:
                errors.append({"email": student_data.email, "error": "Email already exists"})
                continue
            
            import secrets
            import string
            provisional_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            student_id = str(uuid.uuid4())
            student_doc = {
                "id": student_id,
                "email": student_data.email,
                "name": student_data.name,
                "password_hash": hash_password(provisional_password),
                "user_type": "student",
                "institution_id": current_user["id"],
                "institution_slug": current_user.get("institution_slug"),
                "institution_name": current_user.get("institution_name"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "requires_password_change": True,
                "provisional_password": provisional_password,
                "credits": student_data.credits,
                "credits_used": 0,
                "current_exam": student_data.exam_type,
                "exam_access": [student_data.exam_type],
                "status": "active",
                "language": "en",
                "settings": {}
            }
            
            await db.users.insert_one(student_doc)
            created.append({
                "email": student_data.email,
                "name": student_data.name,
                "provisional_password": provisional_password,
                "credits": student_data.credits
            })
        except Exception as e:
            errors.append({"email": student_data.email, "error": str(e)})
    
    return {
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors
    }

@api_router.put("/institution/students/{student_id}/credits")
async def update_student_credits(
    student_id: str,
    credits: int,
    current_user: dict = Depends(get_current_user)
):
    """Add or update student credits"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage credits")
    
    student = await db.users.find_one({
        "id": student_id,
        "institution_id": current_user["id"]
    })
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await db.users.update_one(
        {"id": student_id},
        {"$set": {"credits": credits}}
    )
    
    return {"message": "Credits updated", "new_credits": credits}

@api_router.put("/institution/students/{student_id}/exam")
async def update_student_exam(
    student_id: str,
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Change the exam a student is preparing for"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage student exams")
    
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    student = await db.users.find_one({
        "id": student_id,
        "institution_id": current_user["id"]
    })
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await db.users.update_one(
        {"id": student_id},
        {
            "$set": {"current_exam": exam_type},
            "$addToSet": {"exam_access": exam_type}
        }
    )
    
    return {"message": f"Student now preparing for {exam_type.upper()}", "exam_type": exam_type}

@api_router.get("/student/credits")
async def get_student_credits(current_user: dict = Depends(get_current_user)):
    """Get current student's credit balance and usage"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can access credits")
    
    return {
        "credits": current_user.get("credits", 0),
        "credits_used": current_user.get("credits_used", 0),
        "credits_remaining": current_user.get("credits", 0) - current_user.get("credits_used", 0),
        "current_exam": current_user.get("current_exam"),
        "exam_access": current_user.get("exam_access", [])
    }

@api_router.post("/student/use-credits")
async def use_student_credits(
    amount: int,
    action: str,  # 'ai_tutor', 'speaking_test', 'writing_feedback', 'mock_test'
    current_user: dict = Depends(get_current_user)
):
    """Deduct credits for student activities"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can use credits")
    
    credits_remaining = current_user.get("credits", 0) - current_user.get("credits_used", 0)
    
    if credits_remaining < amount:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$inc": {"credits_used": amount}}
    )
    
    # Log credit usage
    await db.credit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        "amount": amount,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "credits_used": amount,
        "credits_remaining": credits_remaining - amount,
        "action": action
    }

# ==================== INSTITUTION ENDPOINTS ====================

@api_router.post("/institution/students", response_model=StudentResponse)
async def add_student(student_data: StudentCreate, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can add students")
    
    student_id = str(uuid.uuid4())
    password = student_data.password or str(uuid.uuid4())[:8]
    
    student_doc = {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "password_hash": hash_password(password),
        "user_type": "student",
        "institution_id": current_user["id"],
        "progress": {},
        "risk_score": 0.5,
        "pass_probability": 0.5,
        "engagement_score": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(student_doc)
    
    return StudentResponse(
        id=student_id,
        email=student_data.email,
        name=student_data.name,
        institution_id=current_user["id"],
        progress={},
        risk_score=0.5,
        pass_probability=0.5,
        engagement_score=0.0,
        created_at=student_doc["created_at"]
    )

@api_router.get("/institution/students", response_model=List[StudentResponse])
async def get_students(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    students = await db.users.find(
        {"institution_id": current_user["id"], "user_type": "student"},
        {"_id": 0, "password_hash": 0}
    ).to_list(1000)
    
    return [StudentResponse(
        id=s["id"],
        email=s["email"],
        name=s["name"],
        institution_id=s["institution_id"],
        progress=s.get("progress", {}),
        risk_score=s.get("risk_score", 0.5),
        pass_probability=s.get("pass_probability", 0.5),
        engagement_score=s.get("engagement_score", 0.0),
        created_at=s["created_at"]
    ) for s in students]

@api_router.get("/institution/metrics")
async def get_institution_metrics(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    students = await db.users.find(
        {"institution_id": current_user["id"], "user_type": "student"},
        {"_id": 0}
    ).to_list(1000)
    
    total_students = len(students)
    if total_students == 0:
        return {
            "total_students": 0,
            "avg_pass_probability": 0,
            "avg_risk_score": 0,
            "avg_engagement": 0,
            "at_risk_students": 0,
            "high_performers": 0,
            "exams_completed": 0,
            "avg_score": 0
        }
    
    avg_pass = sum(s.get("pass_probability", 0.5) for s in students) / total_students
    avg_risk = sum(s.get("risk_score", 0.5) for s in students) / total_students
    avg_engagement = sum(s.get("engagement_score", 0) for s in students) / total_students
    
    at_risk = len([s for s in students if s.get("risk_score", 0.5) > 0.7])
    high_performers = len([s for s in students if s.get("pass_probability", 0.5) > 0.8])
    
    student_ids = [s["id"] for s in students]
    attempts = await db.exam_attempts.find({"user_id": {"$in": student_ids}}, {"_id": 0}).to_list(10000)
    
    exams_completed = len(attempts)
    avg_score = sum(a.get("score", 0) for a in attempts) / max(1, exams_completed)
    
    return {
        "total_students": total_students,
        "avg_pass_probability": round(avg_pass * 100, 1),
        "avg_risk_score": round(avg_risk * 100, 1),
        "avg_engagement": round(avg_engagement * 100, 1),
        "at_risk_students": at_risk,
        "high_performers": high_performers,
        "exams_completed": exams_completed,
        "avg_score": round(avg_score, 1)
    }

# ==================== LIBRARY ENDPOINTS ====================

@api_router.post("/library/items", response_model=LibraryItemResponse)
async def create_library_item(item: LibraryItemCreate, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can manage library")
    
    item_id = str(uuid.uuid4())
    item_doc = {
        "id": item_id,
        "institution_id": current_user["id"],
        "title": item.title,
        "item_type": item.item_type,
        "content": item.content,
        "file_url": None,
        "description": item.description,
        "exam_type": item.exam_type,
        "tags": item.tags,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "offline_available": True
    }
    
    await db.library_items.insert_one(item_doc)
    
    return LibraryItemResponse(**{k: v for k, v in item_doc.items() if k != "_id"})

@api_router.get("/library/items", response_model=List[LibraryItemResponse])
async def get_library_items(
    item_type: Optional[str] = None,
    exam_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Determine institution_id based on user type
    if current_user["user_type"] == "student":
        institution_id = current_user.get("institution_id")
    else:
        institution_id = current_user["id"]
    
    query = {"institution_id": institution_id}
    if item_type:
        query["item_type"] = item_type
    if exam_type:
        query["exam_type"] = exam_type
    
    items = await db.library_items.find(query, {"_id": 0}).to_list(500)
    return [LibraryItemResponse(**item) for item in items]

@api_router.post("/library/flashcards", response_model=LibraryItemResponse)
async def create_flashcard_set(flashcard: FlashcardCreate, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can create flashcards")
    
    item_id = str(uuid.uuid4())
    item_doc = {
        "id": item_id,
        "institution_id": current_user["id"],
        "title": flashcard.title,
        "item_type": "flashcard",
        "content": {"cards": flashcard.cards},
        "description": f"Flashcard set with {len(flashcard.cards)} cards",
        "exam_type": flashcard.exam_type,
        "tags": flashcard.tags,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "offline_available": True
    }
    
    await db.library_items.insert_one(item_doc)
    
    return LibraryItemResponse(
        id=item_doc["id"],
        institution_id=item_doc["institution_id"],
        title=item_doc["title"],
        item_type=item_doc["item_type"],
        content=str(item_doc["content"]),
        description=item_doc["description"],
        exam_type=item_doc["exam_type"],
        tags=item_doc["tags"],
        created_at=item_doc["created_at"],
        offline_available=True
    )

@api_router.delete("/library/items/{item_id}")
async def delete_library_item(item_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can delete library items")
    
    result = await db.library_items.delete_one({
        "id": item_id,
        "institution_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}

# ==================== EXAM ENDPOINTS ====================

from exam_questions import get_exam_questions, get_mock_test_config, get_full_exam, get_available_exams, SPEAKING_PROMPTS, WRITING_TASKS, MOCK_TESTS

EXAM_TYPES = ["toefl", "ielts", "cambridge", "trinity", "pte", "oet", "toeic", "celpip"]
EXAM_SECTIONS = {
    "toefl": ["reading", "listening", "speaking", "writing"],
    "ielts": ["reading", "listening", "speaking", "writing"],
    "cambridge": ["reading", "writing", "listening", "speaking", "use_of_english"],
    "trinity": ["speaking", "listening", "reading", "writing"],
    "pte": ["speaking_writing", "reading", "listening"],
    "oet": ["reading", "listening", "speaking", "writing"],
    "toeic": ["listening", "reading", "speaking", "writing"],
    "celpip": ["listening", "reading", "writing", "speaking"]
}

@api_router.get("/exams/types")
async def get_exam_types():
    return {
        "exam_types": EXAM_TYPES,
        "sections": EXAM_SECTIONS,
        "total_exams_per_type": 20,
        "descriptions": {
            "toefl": "Test of English as a Foreign Language - Academic English proficiency",
            "ielts": "International English Language Testing System - Global recognition",
            "cambridge": "Cambridge English Qualifications - Comprehensive assessment",
            "trinity": "Trinity College London GESE/ISE - Communicative English assessment",
            "pte": "Pearson Test of English - Computer-based testing",
            "oet": "Occupational English Test - Healthcare professionals",
            "toeic": "Test of English for International Communication - Business English",
            "celpip": "Canadian English Language Proficiency Index Program"
        },
        "mock_tests": {exam: get_mock_test_config(exam) for exam in EXAM_TYPES}
    }

@api_router.get("/exams/{exam_type}/available")
async def get_available_exam_list(exam_type: str):
    """Get list of all 20 available exams for an exam type"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    return get_available_exams(exam_type)

@api_router.get("/exams/{exam_type}/full/{exam_number}")
async def get_complete_exam(exam_type: str, exam_number: int, current_user: dict = Depends(get_current_user)):
    """Get a complete exam (1-20) with all sections"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    if exam_number < 1 or exam_number > 20:
        raise HTTPException(status_code=400, detail="Exam number must be between 1 and 20")
    
    exam_data = get_full_exam(exam_type, exam_number)
    
    # Create exam session
    session_id = str(uuid.uuid4())
    await db.exam_sessions.insert_one({
        "id": session_id,
        "user_id": current_user["id"],
        "exam_type": exam_type,
        "exam_number": exam_number,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "in_progress",
        "sections_completed": []
    })
    
    exam_data["session_id"] = session_id
    return exam_data

@api_router.get("/exams/{exam_type}/mock-test")
async def get_full_mock_test(exam_type: str, exam_number: int = 1, current_user: dict = Depends(get_current_user)):
    """Get a complete mock test with all sections (default exam 1, can specify 1-20)"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    if exam_number < 1 or exam_number > 20:
        exam_number = 1
    
    config = get_mock_test_config(exam_type)
    sections_data = {}
    
    for section_info in config["sections"]:
        section_name = section_info["name"].lower().replace(" ", "_").replace("&", "and")
        simple_section = section_name.split("_")[0] if "_" in section_name else section_name
        
        if simple_section in ["reading", "listening", "writing", "speaking"]:
            sections_data[section_name] = {
                "info": section_info,
                "questions": get_exam_questions(exam_type, simple_section, 5, exam_number)
            }
    
    # Create mock test session
    session_id = str(uuid.uuid4())
    await db.mock_test_sessions.insert_one({
        "id": session_id,
        "user_id": current_user["id"],
        "exam_type": exam_type,
        "exam_number": exam_number,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "in_progress",
        "sections_completed": []
    })
    
    return {
        "session_id": session_id,
        "exam_type": exam_type,
        "exam_number": exam_number,
        "total_exams_available": 20,
        "config": config,
        "sections": sections_data
    }

@api_router.get("/exams/{exam_type}/practice")
async def get_practice_questions(exam_type: str, section: str = "reading", current_user: dict = Depends(get_current_user)):
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    questions = get_exam_questions(exam_type, section, 5)
    
    if not questions:
        # Fallback to generated questions
        questions = generate_sample_questions(exam_type, section)
    
    return {
        "exam_type": exam_type,
        "section": section,
        "questions": questions,
        "time_limit": get_section_time_limit(exam_type, section),
        "instructions": get_section_instructions(exam_type, section)
    }

@api_router.get("/exams/{exam_type}/speaking-prompts")
async def get_speaking_prompts(exam_type: str, current_user: dict = Depends(get_current_user)):
    """Get speaking test prompts for practice"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    prompts = SPEAKING_PROMPTS.get(exam_type, SPEAKING_PROMPTS.get("ielts", {}))
    
    return {
        "exam_type": exam_type,
        "prompts": prompts
    }

@api_router.get("/exams/{exam_type}/writing-tasks")
async def get_writing_tasks(exam_type: str, current_user: dict = Depends(get_current_user)):
    """Get writing tasks for practice"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    tasks = WRITING_TASKS.get(exam_type, WRITING_TASKS.get("ielts", {}))
    
    return {
        "exam_type": exam_type,
        "tasks": tasks
    }

def generate_sample_questions(exam_type: str, section: str) -> List[Dict]:
    if section == "reading":
        return [
            {
                "id": "q1",
                "type": "multiple_choice",
                "passage": "The rapid advancement of artificial intelligence has transformed numerous industries, from healthcare to finance. Machine learning algorithms now assist doctors in diagnosing diseases with unprecedented accuracy, while automated trading systems execute millions of transactions daily. However, this technological revolution raises important questions about employment, privacy, and the ethical boundaries of AI decision-making.",
                "question": "What is the main topic of this passage?",
                "options": [
                    "A) The history of computers",
                    "B) The impact of AI on various industries",
                    "C) How to invest in technology",
                    "D) Medical research methods"
                ],
                "correct_answer": "B"
            },
            {
                "id": "q2",
                "type": "multiple_choice",
                "passage": "The rapid advancement of artificial intelligence has transformed numerous industries, from healthcare to finance. Machine learning algorithms now assist doctors in diagnosing diseases with unprecedented accuracy, while automated trading systems execute millions of transactions daily. However, this technological revolution raises important questions about employment, privacy, and the ethical boundaries of AI decision-making.",
                "question": "According to the passage, what concern does AI technology raise?",
                "options": [
                    "A) Cost of implementation",
                    "B) Speed of processing",
                    "C) Ethical boundaries and privacy",
                    "D) Hardware requirements"
                ],
                "correct_answer": "C"
            },
            {
                "id": "q3",
                "type": "true_false_not_given",
                "passage": "Climate change represents one of the most pressing challenges of our time. Scientists have documented rising global temperatures, melting ice caps, and increasingly severe weather events. International cooperation has led to agreements like the Paris Accord, though implementation varies significantly between nations.",
                "question": "All countries have successfully implemented the Paris Accord.",
                "options": ["True", "False", "Not Given"],
                "correct_answer": "False"
            }
        ]
    elif section == "writing":
        return [
            {
                "id": "w1",
                "type": "essay",
                "prompt": "Some people believe that technology has made our lives more complicated rather than simpler. To what extent do you agree or disagree with this statement?",
                "min_words": 250,
                "max_words": 400,
                "criteria": ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range"]
            }
        ]
    elif section == "speaking":
        return [
            {
                "id": "s1",
                "type": "describe",
                "prompt": "Describe a skill you learned that you are proud of. You should say: what the skill is, how you learned it, why you wanted to learn it, and explain why you are proud of this skill.",
                "preparation_time": 60,
                "speaking_time": 120
            }
        ]
    return []

def get_section_time_limit(exam_type: str, section: str) -> int:
    time_limits = {
        "toefl": {"reading": 54, "listening": 41, "speaking": 17, "writing": 50},
        "ielts": {"reading": 60, "listening": 30, "speaking": 14, "writing": 60},
        "cambridge": {"reading": 90, "writing": 90, "listening": 40, "speaking": 15, "use_of_english": 75},
        "pte": {"speaking_writing": 77, "reading": 32, "listening": 45},
        "oet": {"reading": 60, "listening": 45, "speaking": 20, "writing": 45}
    }
    return time_limits.get(exam_type, {}).get(section, 60)

def get_section_instructions(exam_type: str, section: str) -> str:
    return f"Complete the {section} section of the {exam_type.upper()} exam. Read each question carefully and manage your time wisely."

@api_router.post("/exams/submit", response_model=ExamAttemptResponse)
async def submit_exam_attempt(attempt: ExamAttemptCreate, current_user: dict = Depends(get_current_user)):
    score = calculate_score(attempt.answers)
    feedback = await generate_ai_feedback(attempt.exam_type, attempt.section, attempt.answers, score)
    
    attempt_id = str(uuid.uuid4())
    attempt_doc = {
        "id": attempt_id,
        "user_id": current_user["id"],
        "exam_type": attempt.exam_type,
        "section": attempt.section,
        "answers": attempt.answers,
        "score": score,
        "feedback": feedback,
        "time_spent": attempt.time_spent,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.exam_attempts.insert_one(attempt_doc)
    await update_user_progress(current_user["id"], attempt.exam_type, attempt.section, score)
    
    return ExamAttemptResponse(
        id=attempt_id,
        user_id=current_user["id"],
        exam_type=attempt.exam_type,
        section=attempt.section,
        score=score,
        feedback=feedback,
        time_spent=attempt.time_spent,
        created_at=attempt_doc["created_at"]
    )

def calculate_score(answers: List[Dict]) -> float:
    if not answers:
        return 0.0
    correct = sum(1 for a in answers if a.get("is_correct", False))
    return round((correct / len(answers)) * 100, 1)

async def generate_ai_feedback(exam_type: str, section: str, answers: List[Dict], score: float) -> str:
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return f"Score: {score}%. Keep practicing to improve your {section} skills for the {exam_type.upper()} exam."
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"feedback-{uuid.uuid4()}",
            system_message=f"You are an expert {exam_type.upper()} exam tutor. Provide constructive feedback on the student's performance."
        )
        
        message = UserMessage(
            text=f"The student scored {score}% on the {section} section. Their answers: {answers[:5]}. Provide brief, encouraging feedback with specific improvement tips."
        )
        
        response = await chat.send_message(message)
        return response
    except Exception as e:
        logger.error(f"AI feedback error: {e}")
        return f"Score: {score}%. Continue practicing the {section} section to improve your {exam_type.upper()} performance."

async def update_user_progress(user_id: str, exam_type: str, section: str, score: float):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return
    
    progress = user.get("progress", {})
    if exam_type not in progress:
        progress[exam_type] = {}
    
    if section not in progress[exam_type]:
        progress[exam_type][section] = {"scores": [], "avg": 0}
    
    progress[exam_type][section]["scores"].append(score)
    progress[exam_type][section]["avg"] = sum(progress[exam_type][section]["scores"]) / len(progress[exam_type][section]["scores"])
    
    all_scores = []
    for exam in progress.values():
        for sect in exam.values():
            all_scores.extend(sect.get("scores", []))
    
    avg_overall = sum(all_scores) / max(1, len(all_scores))
    pass_probability = min(0.95, avg_overall / 100)
    risk_score = max(0.05, 1 - pass_probability)
    engagement_score = min(1.0, len(all_scores) * 0.1)
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "progress": progress,
            "pass_probability": pass_probability,
            "risk_score": risk_score,
            "engagement_score": engagement_score
        }}
    )

@api_router.get("/exams/history")
async def get_exam_history(current_user: dict = Depends(get_current_user)):
    attempts = await db.exam_attempts.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"attempts": attempts}

# ==================== AI TUTOR ENDPOINTS ====================

@api_router.post("/ai-tutor/chat")
async def chat_with_tutor(message: AITutorMessage, current_user: dict = Depends(get_current_user)):
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"response": "AI tutor is currently unavailable. Please try again later."}
        
        system_prompt = f"""You are an expert {message.exam_type.upper()} exam tutor. You are:
- Knowledgeable about all sections of the {message.exam_type.upper()} exam
- Encouraging but honest about areas needing improvement
- Focused on practical tips and strategies
- Aware of common mistakes and how to avoid them
Keep responses concise and actionable."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"tutor-{current_user['id']}-{message.exam_type}",
            system_message=system_prompt
        )
        
        context_info = f"\nContext: {message.context}" if message.context else ""
        user_msg = UserMessage(text=f"{message.message}{context_info}")
        
        response = await chat.send_message(user_msg)
        
        await db.tutor_conversations.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "exam_type": message.exam_type,
            "user_message": message.message,
            "ai_response": response,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {"response": response}
    except Exception as e:
        logger.error(f"AI tutor error: {e}")
        return {"response": "I'm having trouble connecting right now. Please try again in a moment."}

@api_router.get("/ai-tutor/history/{exam_type}")
async def get_tutor_history(exam_type: str, current_user: dict = Depends(get_current_user)):
    conversations = await db.tutor_conversations.find(
        {"user_id": current_user["id"], "exam_type": exam_type},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"conversations": conversations}

# ==================== VOICE AI ENDPOINTS (TTS & STT) ====================

from emergentintegrations.llm.openai import OpenAITextToSpeech, OpenAISpeechToText
from fastapi.responses import Response

# Available TTS voices
TTS_VOICES = ["alloy", "ash", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]

class VoiceChatRequest(BaseModel):
    message: str
    exam_type: str
    voice: str = "nova"  # Default voice for tutoring
    context: Optional[str] = None

@api_router.post("/ai-tutor/voice-chat")
async def voice_chat_with_tutor(request: VoiceChatRequest, current_user: dict = Depends(get_current_user)):
    """Chat with AI tutor and get voice response"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"error": "AI tutor is currently unavailable."}
        
        # Get text response from AI
        system_prompt = f"""You are an expert {request.exam_type.upper()} exam tutor. You are:
- Knowledgeable about all sections of the {request.exam_type.upper()} exam
- Encouraging but honest about areas needing improvement
- Focused on practical tips and strategies
- Speaking naturally as if having a conversation
Keep responses concise (under 200 words) for better voice delivery."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"voice-tutor-{current_user['id']}-{request.exam_type}",
            system_message=system_prompt
        )
        
        context_info = f"\nContext: {request.context}" if request.context else ""
        user_msg = UserMessage(text=f"{request.message}{context_info}")
        
        text_response = await chat.send_message(user_msg)
        
        # Convert to speech
        tts = OpenAITextToSpeech(api_key=api_key)
        voice = request.voice if request.voice in TTS_VOICES else "nova"
        
        audio_base64 = await tts.generate_speech_base64(
            text=text_response,
            model="tts-1",
            voice=voice
        )
        
        # Save conversation
        await db.tutor_conversations.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "exam_type": request.exam_type,
            "user_message": request.message,
            "ai_response": text_response,
            "voice_enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "text_response": text_response,
            "audio_base64": audio_base64,
            "voice": voice
        }
        
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        return {"error": str(e)}

@api_router.post("/voice/text-to-speech")
async def text_to_speech(
    text: str,
    voice: str = "nova",
    speed: float = 1.0,
    current_user: dict = Depends(get_current_user)
):
    """Convert text to speech audio"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="TTS not configured")
        
        if len(text) > 4096:
            raise HTTPException(status_code=400, detail="Text too long (max 4096 characters)")
        
        tts = OpenAITextToSpeech(api_key=api_key)
        voice = voice if voice in TTS_VOICES else "nova"
        
        audio_base64 = await tts.generate_speech_base64(
            text=text,
            model="tts-1",
            voice=voice,
            speed=speed
        )
        
        return {"audio_base64": audio_base64, "voice": voice}
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/voice/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = "en",
    current_user: dict = Depends(get_current_user)
):
    """Transcribe audio to text using Whisper"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="STT not configured")
        
        # Check file size (25MB limit)
        content = await audio_file.read()
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
        
        # Check file format
        allowed_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
        file_ext = audio_file.filename.split(".")[-1].lower() if audio_file.filename else "mp3"
        if file_ext not in allowed_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported format. Use: {', '.join(allowed_formats)}")
        
        stt = OpenAISpeechToText(api_key=api_key)
        
        # Create a file-like object from bytes
        import io
        audio_io = io.BytesIO(content)
        audio_io.name = audio_file.filename or f"audio.{file_ext}"
        
        response = await stt.transcribe(
            file=audio_io,
            model="whisper-1",
            language=language,
            response_format="json"
        )
        
        return {
            "text": response.text,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/voice/available-voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "description": "Neutral, balanced"},
            {"id": "ash", "name": "Ash", "description": "Clear, articulate"},
            {"id": "coral", "name": "Coral", "description": "Warm, friendly"},
            {"id": "echo", "name": "Echo", "description": "Smooth, calm"},
            {"id": "fable", "name": "Fable", "description": "Expressive, storytelling"},
            {"id": "nova", "name": "Nova", "description": "Energetic, upbeat"},
            {"id": "onyx", "name": "Onyx", "description": "Deep, authoritative"},
            {"id": "sage", "name": "Sage", "description": "Wise, measured"},
            {"id": "shimmer", "name": "Shimmer", "description": "Bright, cheerful"}
        ],
        "default": "nova"
    }

# ==================== SPEAKING TEST ENDPOINTS ====================

class SpeakingTestSubmission(BaseModel):
    exam_type: str
    prompt_id: str
    audio_base64: str  # Base64 encoded audio
    
@api_router.post("/speaking-test/submit")
async def submit_speaking_test(
    submission: SpeakingTestSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit speaking test for AI evaluation"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI evaluation not configured")
        
        # Decode audio
        import io
        audio_bytes = base64.b64decode(submission.audio_base64)
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = "speaking_test.webm"
        
        # Transcribe
        stt = OpenAISpeechToText(api_key=api_key)
        transcription = await stt.transcribe(
            file=audio_io,
            model="whisper-1",
            language="en",
            response_format="json"
        )
        
        # Get AI evaluation
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        eval_chat = LlmChat(
            api_key=api_key,
            session_id=f"speaking-eval-{uuid.uuid4()}",
            system_message=f"""You are an expert {submission.exam_type.upper()} speaking examiner. 
Evaluate the student's spoken response based on:
1. Fluency and Coherence (1-9)
2. Lexical Resource (1-9)
3. Grammatical Range and Accuracy (1-9)
4. Pronunciation (1-9)

Provide specific feedback and an overall band score.
Format your response as JSON with keys: fluency_score, lexical_score, grammar_score, pronunciation_score, overall_score, feedback, strengths, areas_to_improve"""
        )
        
        eval_msg = UserMessage(text=f"Student's transcribed response:\n\n{transcription.text}")
        evaluation = await eval_chat.send_message(eval_msg)
        
        # Try to parse as JSON, otherwise wrap in object
        try:
            import json
            eval_data = json.loads(evaluation)
        except (json.JSONDecodeError, TypeError, ValueError):
            eval_data = {"feedback": evaluation, "overall_score": 6.0}
        
        # Save attempt
        attempt_id = str(uuid.uuid4())
        await db.speaking_attempts.insert_one({
            "id": attempt_id,
            "user_id": current_user["id"],
            "exam_type": submission.exam_type,
            "prompt_id": submission.prompt_id,
            "transcription": transcription.text,
            "evaluation": eval_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "id": attempt_id,
            "transcription": transcription.text,
            "evaluation": eval_data
        }
        
    except Exception as e:
        logger.error(f"Speaking test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STRIPE CHECKOUT ====================

from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

stripe_api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

# ==================== PRICING ENDPOINTS ====================
# MODELO B2B: Planes por número de exámenes por licencia + descuento por volumen de licencias
# Cada plan puede tener AI Tutor o no

# Costes base (INTERNO - NO MOSTRAR A CLIENTES)
AVG_MOCK_TEST_COST = 0.94  # Coste interno por mock test
AI_TUTOR_COST_PER_MIN = 0.06  # Coste interno por minuto AI

# ==================== PLANES POR NÚMERO DE EXÁMENES POR LICENCIA ====================
# El cliente elige cuántos mock exams incluye cada licencia que compre
EXAM_PLANS = {
    "plan_5": {"exams": 5, "base_cost": 4.70, "label": "5 Mock Exams"},
    "plan_10": {"exams": 10, "base_cost": 9.40, "label": "10 Mock Exams"},
    "plan_20": {"exams": 20, "base_cost": 18.80, "label": "20 Mock Exams"},
    "plan_40": {"exams": 40, "base_cost": 37.60, "label": "40 Mock Exams"},
    "plan_60": {"exams": 60, "base_cost": 56.40, "label": "60 Mock Exams"},
    "plan_100": {"exams": 100, "base_cost": 94.00, "label": "100 Mock Exams"},
}

# ==================== DESCUENTOS POR VOLUMEN DE LICENCIAS ====================
# Más licencias compradas = mejor precio por licencia
# Tiers: 100, 500, 1000, 2000, 5000, 10000, 100000
VOLUME_PRICING = {
    "tier_100": {
        "min": 1, "max": 100,
        "price_multiplier": 2.00,
        "discount": "0%",
        "label": "1-100 licenses"
    },
    "tier_500": {
        "min": 101, "max": 500,
        "price_multiplier": 1.85,
        "discount": "7%",
        "label": "101-500 licenses"
    },
    "tier_1000": {
        "min": 501, "max": 1000,
        "price_multiplier": 1.72,
        "discount": "14%",
        "label": "501-1,000 licenses"
    },
    "tier_2000": {
        "min": 1001, "max": 2000,
        "price_multiplier": 1.60,
        "discount": "20%",
        "label": "1,001-2,000 licenses"
    },
    "tier_5000": {
        "min": 2001, "max": 5000,
        "price_multiplier": 1.50,
        "discount": "25%",
        "label": "2,001-5,000 licenses"
    },
    "tier_10000": {
        "min": 5001, "max": 10000,
        "price_multiplier": 1.42,
        "discount": "29%",
        "label": "5,001-10,000 licenses"
    },
    "tier_100000": {
        "min": 10001, "max": 100000,
        "price_multiplier": 1.35,
        "discount": "32%",
        "label": "10,001-100,000 licenses"
    },
}

# ==================== AI TUTOR ADD-ON ====================
# AI Tutor minutes per license (optional)
AI_TUTOR_OPTIONS = {
    "none": {"minutes": 0, "cost": 0, "price": 0, "label": "No AI Tutor"},
    "basic": {"minutes": 30, "cost": 1.80, "price": 5.00, "label": "30 min AI Tutor"},
    "standard": {"minutes": 60, "cost": 3.60, "price": 9.00, "label": "60 min AI Tutor"},
    "premium": {"minutes": 120, "cost": 7.20, "price": 15.00, "label": "120 min AI Tutor"},
    "unlimited": {"minutes": 300, "cost": 18.00, "price": 35.00, "label": "300 min AI Tutor"},
}

# ==================== PRODUCTOS EXTRA PARA REVENTA ====================
# Writing, Speaking, Mock Exams - hasta 100,000 unidades

def get_bulk_pricing(quantity: int, cost_per_unit: float, base_margin: float = 0.50) -> dict:
    """Calculate bulk pricing with volume discounts"""
    if quantity <= 100:
        margin = base_margin
        discount = "0%"
    elif quantity <= 1000:
        margin = base_margin - 0.05
        discount = "5%"
    elif quantity <= 10000:
        margin = base_margin - 0.10
        discount = "10%"
    elif quantity <= 50000:
        margin = base_margin - 0.15
        discount = "15%"
    else:  # 50001-100000
        margin = base_margin - 0.18
        discount = "18%"
    
    price_per_unit = round(cost_per_unit / (1 - margin), 2)
    total_cost = round(cost_per_unit * quantity, 2)
    total_price = round(price_per_unit * quantity, 2)
    profit = round(total_price - total_cost, 2)
    
    return {
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": total_price,
        "internal_cost": total_cost,
        "profit": profit,
        "margin": f"{int(margin * 100)}%",
        "discount": discount
    }

# Precios sugeridos de reventa para academias
RESALE_SUGGESTIONS = {
    "writing": {"min": 3.00, "max": 8.00, "recommended": 5.00},
    "speaking": {"min": 8.00, "max": 20.00, "recommended": 12.00},
    "mock_exam": {"min": 15.00, "max": 40.00, "recommended": 25.00},
    "ai_tutor_minute": {"min": 0.50, "max": 1.50, "recommended": 1.00},
}

# ==================== PAQUETES SEPARADOS WRITING & SPEAKING ====================
# Para instituciones que quieren comprar tests individuales para reventa
# PRECIOS OPTIMIZADOS

WRITING_TEST_PACKAGES = {
    "writing_20": {"tests": 20, "price": 5.00, "price_per_test": 0.25, "internal_cost": 1.00, "margin": 0.80},
    "writing_50": {"tests": 50, "price": 10.00, "price_per_test": 0.20, "internal_cost": 2.50, "margin": 0.75},
    "writing_100": {"tests": 100, "price": 15.00, "price_per_test": 0.15, "internal_cost": 5.00, "margin": 0.67},
}

SPEAKING_TEST_PACKAGES = {
    "speaking_20": {"tests": 20, "price": 25.00, "price_per_test": 1.25, "internal_cost": 17.00, "margin": 0.32},
    "speaking_50": {"tests": 50, "price": 55.00, "price_per_test": 1.10, "internal_cost": 42.50, "margin": 0.23},
    "speaking_100": {"tests": 100, "price": 99.00, "price_per_test": 0.99, "internal_cost": 85.00, "margin": 0.14},
}

# ==================== ADD-ONS ====================
AI_TUTOR_ADDONS = {
    "tutor_30min": {"minutes": 30, "price": 5.00, "internal_cost": 1.80},
    "tutor_100min": {"minutes": 100, "price": 12.00, "internal_cost": 6.00},
    "tutor_300min": {"minutes": 300, "price": 29.00, "internal_cost": 18.00},
}

# ==================== NUEVAS FUNCIONES DE PRICING ====================

@api_router.get("/pricing/platform-plans")
async def get_platform_plans():
    """Get available exam plans, volume tiers, and AI options for B2B pricing"""
    
    # Planes de exámenes (sin mostrar costes internos)
    exam_plans = []
    for plan_id, plan in EXAM_PLANS.items():
        exam_plans.append({
            "id": plan_id,
            "exams": plan["exams"],
            "label": plan["label"]
        })
    
    # Tiers de volumen (sin mostrar multiplicadores internos)
    volume_pricing = []
    for tier_id, tier in VOLUME_PRICING.items():
        volume_pricing.append({
            "id": tier_id,
            "min": tier["min"],
            "max": tier["max"],
            "discount": tier["discount"],
            "label": tier["label"]
        })
    
    # Opciones de AI Tutor (solo precio, sin coste interno)
    ai_tutor_options = []
    for option_id, option in AI_TUTOR_OPTIONS.items():
        ai_tutor_options.append({
            "id": option_id,
            "minutes": option["minutes"],
            "price": option["price"],
            "label": option["label"]
        })
    
    return {
        "pricing_model": "exam_plans_with_volume_licensing",
        "exam_plans": exam_plans,
        "volume_pricing": volume_pricing,
        "ai_tutor_options": ai_tutor_options,
        "description": "Selecciona el número de exámenes por licencia, si quieres AI Tutor, y el volumen de licencias para obtener tu precio final"
    }

@api_router.get("/pricing/test-packages")
async def get_test_packages():
    """Get writing and speaking test packages for resale"""
    writing = []
    for pkg_id, pkg in WRITING_TEST_PACKAGES.items():
        writing.append({
            "id": pkg_id,
            "tests": pkg["tests"],
            "price": pkg["price"],
            "price_per_test": pkg["price_per_test"],
            "suggested_resale": round(pkg["price_per_test"] * 3, 2),  # 3x markup for institutions
            "margin": f"{int(pkg['margin'] * 100)}%"
        })
    
    speaking = []
    for pkg_id, pkg in SPEAKING_TEST_PACKAGES.items():
        speaking.append({
            "id": pkg_id,
            "tests": pkg["tests"],
            "price": pkg["price"],
            "price_per_test": pkg["price_per_test"],
            "suggested_resale": round(pkg["price_per_test"] * 2, 2),  # 2x markup for institutions
            "margin": f"{int(pkg['margin'] * 100)}%"
        })
    
    return {
        "writing_packages": writing,
        "speaking_packages": speaking,
        "ai_tutor_addons": [
            {"id": k, "minutes": v["minutes"], "price": v["price"]} 
            for k, v in AI_TUTOR_ADDONS.items()
        ]
    }

@api_router.get("/pricing/calculator")
async def calculate_pricing(
    exam_plan: str,  # plan_5, plan_10, plan_20, plan_40, plan_60, plan_100
    num_licenses: int,  # Número de licencias a comprar
    ai_tutor_option: str = "none",  # none, basic, standard, premium, unlimited
):
    """Calculate final price per license based on: exam plan + AI option + volume of licenses"""
    
    # Validate inputs
    if exam_plan not in EXAM_PLANS:
        raise HTTPException(status_code=400, detail="Invalid exam plan")
    if ai_tutor_option not in AI_TUTOR_OPTIONS:
        raise HTTPException(status_code=400, detail="Invalid AI tutor option")
    if num_licenses < 1 or num_licenses > 100000:
        raise HTTPException(status_code=400, detail="License count must be between 1 and 100,000")
    
    # Get plan details
    plan = EXAM_PLANS[exam_plan]
    ai_option = AI_TUTOR_OPTIONS[ai_tutor_option]
    
    # Find volume pricing tier based on number of LICENSES (not students)
    volume_tier = None
    volume_tier_id = None
    for tier_id, tier in VOLUME_PRICING.items():
        if tier["min"] <= num_licenses <= tier["max"]:
            volume_tier = tier
            volume_tier_id = tier_id
            break
    
    if not volume_tier:
        raise HTTPException(status_code=400, detail="License count out of range")
    
    # Calculate base price per license (before volume discount)
    base_price_per_license = (plan["base_cost"] * volume_tier["price_multiplier"]) + ai_option["price"]
    
    # Final price per license (with volume discount already applied via multiplier)
    final_price_per_license = round(base_price_per_license, 2)
    
    # Total order price
    total_order_price = round(final_price_per_license * num_licenses, 2)
    
    # Calculate savings vs base price (tier_100 price)
    base_tier = VOLUME_PRICING["tier_100"]
    full_price_per_license = round((plan["base_cost"] * base_tier["price_multiplier"]) + ai_option["price"], 2)
    savings_per_license = round(full_price_per_license - final_price_per_license, 2)
    total_savings = round(savings_per_license * num_licenses, 2)
    
    return {
        "plan": {
            "id": exam_plan,
            "exams_per_license": plan["exams"],
            "label": plan["label"]
        },
        "ai_tutor": {
            "option": ai_tutor_option,
            "label": ai_option["label"],
            "minutes_per_license": ai_option["minutes"],
            "price_per_license": ai_option["price"]
        },
        "volume_tier": {
            "id": volume_tier_id,
            "label": volume_tier["label"],
            "discount": volume_tier["discount"],
            "num_licenses": num_licenses
        },
        "pricing": {
            "price_per_license": final_price_per_license,
            "total_order_price": total_order_price,
            "full_price_per_license": full_price_per_license,
            "savings_per_license": savings_per_license,
            "total_savings": total_savings
        },
        "summary": f"{num_licenses:,} licenses × ${final_price_per_license}/license = ${total_order_price:,.2f}"
    }

@api_router.get("/pricing/bulk-products")
async def get_bulk_product_pricing(
    product_type: str,  # writing, speaking, mock_exam, ai_tutor_minutes
    quantity: int
):
    """Calculate bulk pricing for individual products (up to 100,000 units)"""
    
    if quantity < 1 or quantity > 100000:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 100,000")
    
    # Define base costs for each product type
    base_costs = {
        "writing": 0.05,
        "speaking": 0.85,
        "mock_exam": AVG_MOCK_TEST_COST,
        "ai_tutor_minutes": AI_TUTOR_COST_PER_MIN
    }
    
    if product_type not in base_costs:
        raise HTTPException(status_code=400, detail="Invalid product type")
    
    cost_per_unit = base_costs[product_type]
    pricing_data = get_bulk_pricing(quantity, cost_per_unit)
    
    # Add resale suggestions
    if product_type in RESALE_SUGGESTIONS:
        pricing_data["resale_suggestions"] = RESALE_SUGGESTIONS[product_type]
    
    return {
        "product_type": product_type,
        "pricing": pricing_data,
        "note": f"Precios para reventa de {product_type}. Márgenes incluyen descuentos por volumen."
    }

# ==================== LEGACY SUPPORT FUNCTIONS ====================
# Keep some old variable names for backward compatibility

# For backward compatibility with existing code
EXAM_COSTS = {
    "toefl": {"description": "TOEFL iBT - Academic English"},
    "ielts": {"description": "IELTS Academic/General"},
    "cambridge": {"description": "Cambridge C1/C2 Advanced"},
    "pte": {"description": "PTE Academic"},
    "oet": {"description": "OET - Healthcare Professionals"}
}

INDIVIDUAL_TEST_COSTS = {
    "writing": 0.05,
    "speaking": 0.85,
    "ai_tutor_per_min_mixed": AI_TUTOR_COST_PER_MIN
}

@api_router.get("/pricing/summary")
async def get_pricing_summary():
    """Get complete pricing summary for the new model"""
    return {
        "pricing_model": "exam_plans_with_volume_pricing",
        "exam_plans": [
            {"id": k, "exams": v["exams"], "label": v["label"]} 
            for k, v in EXAM_PLANS.items()
        ],
        "volume_tiers": [
            {"id": k, "range": f"{v['min']}-{v['max']} estudiantes", "discount": v["discount"]} 
            for k, v in VOLUME_PRICING.items()
        ],
        "ai_tutor_options": [
            {"id": k, "label": v["label"], "price": v["price"]} 
            for k, v in AI_TUTOR_OPTIONS.items()
        ],
        "bulk_products": ["writing", "speaking", "mock_exam", "ai_tutor_minutes"],
        "max_students": 10000,
        "max_bulk_quantity": 100000
    }

# ==================== MONETIZATION CALCULATOR ====================

@api_router.post("/pricing/monetization-calculator")
async def calculate_monetization(
    writing_tests: int = 0,
    speaking_tests: int = 0,
    writing_sell_price: float = 3.0,
    speaking_sell_price: float = 4.0
):
    """
    Calculate potential monetization revenue for institutions.
    Shows how much profit they can make by reselling tests to their students.
    """
    # Find best package prices
    def get_best_writing_price(tests: int) -> tuple:
        if tests == 0:
            return 0, 0, "none"
        best_pkg = None
        for pkg_id, pkg in sorted(WRITING_TEST_PACKAGES.items(), key=lambda x: x[1]["tests"]):
            if pkg["tests"] >= tests:
                best_pkg = (pkg["price"], pkg["price_per_test"], pkg_id)
                break
        if not best_pkg:
            # Use largest package
            largest = WRITING_TEST_PACKAGES["writing_100"]
            num_packs = (tests + 99) // 100
            return largest["price"] * num_packs, largest["price_per_test"], "writing_100"
        return best_pkg
    
    def get_best_speaking_price(tests: int) -> tuple:
        if tests == 0:
            return 0, 0, "none"
        best_pkg = None
        for pkg_id, pkg in sorted(SPEAKING_TEST_PACKAGES.items(), key=lambda x: x[1]["tests"]):
            if pkg["tests"] >= tests:
                best_pkg = (pkg["price"], pkg["price_per_test"], pkg_id)
                break
        if not best_pkg:
            largest = SPEAKING_TEST_PACKAGES["speaking_100"]
            num_packs = (tests + 99) // 100
            return largest["price"] * num_packs, largest["price_per_test"], "speaking_100"
        return best_pkg
    
    # Calculate writing
    w_cost, w_unit_cost, w_pkg = get_best_writing_price(writing_tests)
    w_revenue = writing_tests * writing_sell_price
    w_profit = w_revenue - w_cost
    w_margin = (w_profit / w_revenue * 100) if w_revenue > 0 else 0
    
    # Calculate speaking
    s_cost, s_unit_cost, s_pkg = get_best_speaking_price(speaking_tests)
    s_revenue = speaking_tests * speaking_sell_price
    s_profit = s_revenue - s_cost
    s_margin = (s_profit / s_revenue * 100) if s_revenue > 0 else 0
    
    # Totals
    total_cost = w_cost + s_cost
    total_revenue = w_revenue + s_revenue
    total_profit = w_profit + s_profit
    total_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "writing": {
            "tests_purchased": writing_tests,
            "package_recommended": w_pkg,
            "cost": round(w_cost, 2),
            "cost_per_test": round(w_unit_cost, 2),
            "sell_price_per_test": writing_sell_price,
            "revenue": round(w_revenue, 2),
            "profit": round(w_profit, 2),
            "margin_percent": round(w_margin, 1)
        },
        "speaking": {
            "tests_purchased": speaking_tests,
            "package_recommended": s_pkg,
            "cost": round(s_cost, 2),
            "cost_per_test": round(s_unit_cost, 2),
            "sell_price_per_test": speaking_sell_price,
            "revenue": round(s_revenue, 2),
            "profit": round(s_profit, 2),
            "margin_percent": round(s_margin, 1)
        },
        "totals": {
            "investment": round(total_cost, 2),
            "potential_revenue": round(total_revenue, 2),
            "profit": round(total_profit, 2),
            "roi_percent": round((total_profit / total_cost * 100) if total_cost > 0 else 0, 1),
            "margin_percent": round(total_margin, 1)
        },
        "subscription_recovery": {
            "description": "How many tests to sell to recover your subscription cost",
            "example_monthly_sub": 500,
            "writing_tests_needed": round(500 / writing_sell_price) if writing_sell_price > 0 else 0,
            "speaking_tests_needed": round(500 / speaking_sell_price) if speaking_sell_price > 0 else 0
        }
    }

# ==================== STRIPE CHECKOUT ENDPOINTS ====================

class CheckoutRequest(BaseModel):
    package_type: str  # 'subscription', 'writing_package', 'speaking_package'
    package_id: str
    origin_url: str
    quantity: int = 1

class SubscriptionCheckoutRequest(BaseModel):
    students: int
    exams: int = 1
    credit_tier: str = "basic"
    billing_cycle: str = "monthly"  # 'monthly' or 'yearly'
    origin_url: str

@api_router.post("/checkout/subscription")
async def create_subscription_checkout(request: SubscriptionCheckoutRequest, http_request: Request):
    """Create Stripe checkout session for subscription using new pricing model"""
    try:
        # Map old parameters to new pricing model
        # Default to plan_10 for backward compatibility
        exam_plan = "plan_10"
        ai_tutor_option = "basic" if request.exams > 1 else "none"
        
        # Get pricing calculation
        pricing_calc = await calculate_pricing(
            exam_plan=exam_plan,
            num_students=request.students,
            ai_tutor_option=ai_tutor_option,
            resale_price_per_student=25.0
        )
        
        amount = pricing_calc["pricing"]["total_price"]
        
        if request.billing_cycle == "yearly":
            # 10 months for the price of 12 (17% discount)
            amount = amount * 10
        
        # Initialize Stripe checkout
        webhook_url = f"{str(http_request.base_url).rstrip('/')}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build URLs
        success_url = f"{request.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/pricing"
        
        # Metadata for tracking
        metadata = {
            "type": "subscription",
            "exam_plan": exam_plan,
            "students": str(request.students),
            "ai_tutor_option": ai_tutor_option,
            "billing_cycle": request.billing_cycle,
            "price": str(amount)
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=float(amount),
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store transaction in DB
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "type": "subscription",
            "amount": amount,
            "currency": "usd",
            "metadata": metadata,
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "amount": amount,
            "billing_cycle": request.billing_cycle
        }
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/checkout/test-package")
async def create_test_package_checkout(
    package_type: str,  # 'writing' or 'speaking'
    package_id: str,
    origin_url: str,
    http_request: Request
):
    """Create Stripe checkout session for writing/speaking test packages"""
    try:
        # Get package server-side
        if package_type == "writing":
            if package_id not in WRITING_TEST_PACKAGES:
                raise HTTPException(status_code=400, detail="Invalid writing package")
            package = WRITING_TEST_PACKAGES[package_id]
        elif package_type == "speaking":
            if package_id not in SPEAKING_TEST_PACKAGES:
                raise HTTPException(status_code=400, detail="Invalid speaking package")
            package = SPEAKING_TEST_PACKAGES[package_id]
        else:
            raise HTTPException(status_code=400, detail="Invalid package type")
        
        amount = package["price"]
        
        # Initialize Stripe checkout
        webhook_url = f"{str(http_request.base_url).rstrip('/')}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build URLs
        success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/pricing"
        
        metadata = {
            "type": f"{package_type}_package",
            "package_id": package_id,
            "tests": str(package["tests"])
        }
        
        checkout_request = CheckoutSessionRequest(
            amount=float(amount),
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store transaction
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "type": f"{package_type}_package",
            "package_id": package_id,
            "amount": amount,
            "currency": "usd",
            "metadata": metadata,
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "amount": amount,
            "tests": package["tests"]
        }
        
    except Exception as e:
        logger.error(f"Test package checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, http_request: Request):
    """Get payment status for a checkout session"""
    try:
        webhook_url = f"{str(http_request.base_url).rstrip('/')}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in DB if paid
        if status.payment_status == "paid":
            existing = await db.payment_transactions.find_one({"session_id": session_id})
            if existing and existing.get("payment_status") != "paid":
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "payment_status": "paid",
                        "paid_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
            "metadata": status.metadata
        }
        
    except Exception as e:
        logger.error(f"Checkout status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_url = f"{str(request.base_url).rstrip('/')}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        event = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Stripe webhook received: {event.event_type}")
        
        # Update payment transaction
        if event.session_id:
            await db.payment_transactions.update_one(
                {"session_id": event.session_id},
                {"$set": {
                    "payment_status": event.payment_status,
                    "event_type": event.event_type,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/pricing/individual")
async def get_individual_pricing():
    """Individual learner pricing - based on exam packages"""
    return {
        "plans": [
            {
                "id": "individual_starter",
                "name": "Starter Pack",
                "price": 29,
                "mock_tests": 5,
                "ai_tutor_minutes": 15,
                "features": ["5 mock tests completos", "15 min AI Tutor", "1 tipo de examen"]
            },
            {
                "id": "individual_pro",
                "name": "Pro Pack", 
                "price": 79,
                "mock_tests": 15,
                "ai_tutor_minutes": 60,
                "features": ["15 mock tests completos", "60 min AI Tutor", "Todos los exámenes", "Feedback detallado"]
            },
            {
                "id": "individual_premium",
                "name": "Premium Pack",
                "price": 149,
                "mock_tests": 40,
                "ai_tutor_minutes": 200,
                "features": ["40 mock tests completos", "200 min AI Tutor", "Todos los exámenes", "Progreso analytics"]
            }
        ]
    }

# Admin-only endpoint for internal cost analysis
@api_router.get("/admin/pricing-analysis")
async def get_pricing_analysis(current_user: dict = Depends(get_current_user)):
    """Internal pricing analysis - ADMIN ONLY"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Exam costs breakdown by type
    exam_costs = {
        "toefl": {
            "description": "TOEFL iBT - Academic English",
            "speaking_minutes": 17,
            "writing_tasks": 2,
            "internal_cost": 0.92
        },
        "ielts": {
            "description": "IELTS Academic/General",
            "speaking_minutes": 14,
            "writing_tasks": 2,
            "internal_cost": 0.82
        },
        "cambridge": {
            "description": "Cambridge C1/C2 Advanced",
            "speaking_minutes": 15,
            "writing_tasks": 2,
            "internal_cost": 0.95
        },
        "pte": {
            "description": "PTE Academic",
            "speaking_minutes": 20,
            "writing_tasks": 2,
            "internal_cost": 0.98
        },
        "oet": {
            "description": "OET - Healthcare Professionals",
            "speaking_minutes": 20,
            "writing_tasks": 1,
            "internal_cost": 1.02
        }
    }
    
    # Individual test costs
    individual_test_costs = {
        "writing": 0.05,
        "speaking": 0.85,
        "ai_tutor_per_min_voice": 0.18,
        "ai_tutor_per_min_mixed": 0.06
    }
    
    # Tier analysis with complete pricing breakdown
    tier_analysis = []
    base_license_cost = AVG_MOCK_TEST_COST * 10  # 10 exams per student default
    
    for tier_id, tier in VOLUME_PRICING.items():
        price_per_license = round(base_license_cost * tier["price_multiplier"], 2)
        internal_cost = base_license_cost
        profit = round(price_per_license - internal_cost, 2)
        margin = int((profit / price_per_license) * 100) if price_per_license > 0 else 0
        
        tier_analysis.append({
            "tier_id": tier_id,
            "licenses_range": f"{tier['min']}-{tier['max']:,}",
            "price_per_license": price_per_license,
            "price_per_exam": round(price_per_license / 10, 2),
            "discount": tier["discount"],
            "internal_cost": internal_cost,
            "profit_per_license": profit,
            "margin_percentage": f"{margin}%"
        })
    
    # AI Tutor addon analysis
    ai_tutor_addon_analysis = []
    for option_id, option in AI_TUTOR_OPTIONS.items():
        if option["minutes"] > 0:
            profit = round(option["price"] - option["cost"], 2)
            margin = int((profit / option["price"]) * 100) if option["price"] > 0 else 0
            ai_tutor_addon_analysis.append({
                "addon_id": option_id,
                "minutes": option["minutes"],
                "internal_cost": option["cost"],
                "price": option["price"],
                "profit": profit,
                "margin": f"{margin}%"
            })
    
    # Exam plans analysis
    exam_plans_analysis = []
    for plan_id, plan in EXAM_PLANS.items():
        exam_plans_analysis.append({
            "plan_id": plan_id,
            "exams": plan["exams"],
            "base_cost": plan["base_cost"],
            "cost_per_exam": round(plan["base_cost"] / plan["exams"], 2),
            "label": plan["label"]
        })
    
    return {
        "pricing_model": "exam_plans_with_volume_pricing",
        "avg_mock_test_cost": AVG_MOCK_TEST_COST,
        "ai_tutor_cost_per_minute": AI_TUTOR_COST_PER_MIN,
        "exam_costs": exam_costs,
        "individual_test_costs": individual_test_costs,
        "tier_analysis": tier_analysis,
        "ai_tutor_addon_analysis": ai_tutor_addon_analysis,
        "exam_plans": exam_plans_analysis,
        "margin_summary": {
            "tier_1_100": "50% margen base",
            "tier_101_500": "45% margen", 
            "tier_501_2000": "40% margen",
            "tier_2001_10000": "35% margen (enterprise)",
            "ai_tutor": "Hasta 67% margen"
        },
        "note": "Modelo B2B: Planes por número de exámenes (5-100) + descuento por volumen de estudiantes (hasta 10,000) + AI Tutor opcional"
    }

@api_router.post("/pricing/calculate-roi-legacy")
async def calculate_roi_legacy(
    current_students: int,
    current_teachers: int,
    current_pass_rate: float,
    current_no_show_rate: float,
    teacher_salary: int = 3000
):
    # Industry standard: 1 teacher per 15-20 students
    # With AI: ratio can be 100:1 (10x improvement)
    ai_enhanced_ratio = 100
    
    potential_students = current_teachers * ai_enhanced_ratio
    additional_students = max(0, potential_students - current_students)
    multiplier = round(potential_students / max(1, current_students))
    
    # Pass rate improvement with AI: +15-20%
    new_pass_rate = min(95, current_pass_rate + 20)
    
    # No-show reduction: 60% with engagement tools
    new_no_show_rate = max(5, current_no_show_rate * 0.4)
    
    # Revenue calculation (avg $500/student)
    avg_revenue_per_student = 500
    current_revenue = current_students * avg_revenue_per_student * (current_pass_rate / 100)
    projected_revenue = potential_students * avg_revenue_per_student * (new_pass_rate / 100)
    revenue_increase = projected_revenue - current_revenue
    
    # Teacher cost savings
    standard_ratio = 15
    teachers_needed_without_ai = max(1, potential_students // standard_ratio)
    additional_teachers_needed = max(0, teachers_needed_without_ai - current_teachers)
    teacher_cost_savings = additional_teachers_needed * teacher_salary * 12
    
    # Time saved per teacher
    time_saved_per_teacher = 30  # hours/week
    total_time_saved = time_saved_per_teacher * current_teachers
    
    return {
        "current_students": current_students,
        "potential_students": potential_students,
        "additional_students": additional_students,
        "student_multiplier": multiplier,
        "current_pass_rate": current_pass_rate,
        "improved_pass_rate": new_pass_rate,
        "current_no_show": current_no_show_rate,
        "reduced_no_show": new_no_show_rate,
        "revenue_increase": round(revenue_increase),
        "teacher_cost_savings": round(teacher_cost_savings),
        "time_saved_weekly": total_time_saved,
        "total_annual_benefit": round(revenue_increase + teacher_cost_savings)
    }

# ==================== ADMIN ENDPOINTS ====================

@api_router.get("/admin/settings")
async def get_admin_settings(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = await db.admin_settings.find_one({}, {"_id": 0})
    if not settings:
        settings = {
            "openai_key": os.environ.get("EMERGENT_LLM_KEY", "")[:20] + "...",
            "stripe_key": "configured",
            "elevenlabs_key": "not_configured",
            "features_enabled": ["ai_tutor", "speaking_test", "analytics", "library", "video_classes"]
        }
    return settings

@api_router.post("/admin/settings")
async def update_admin_settings(settings: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.admin_settings.update_one({}, {"$set": settings}, upsert=True)
    return {"message": "Settings updated successfully"}

@api_router.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = await db.users.count_documents({})
    total_institutions = await db.users.count_documents({"user_type": "institution"})
    total_students = await db.users.count_documents({"user_type": "student"})
    total_exams = await db.exam_attempts.count_documents({})
    total_library_items = await db.library_items.count_documents({})
    total_conversations = await db.tutor_conversations.count_documents({})
    total_transactions = await db.payment_transactions.count_documents({})
    
    # Today's stats
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    exams_today = await db.exam_attempts.count_documents({"created_at": {"$gte": today_start}})
    
    return {
        "total_users": total_users,
        "total_institutions": total_institutions,
        "total_students": total_students,
        "total_exam_attempts": total_exams,
        "total_library_items": total_library_items,
        "ai_conversations": total_conversations,
        "total_transactions": total_transactions,
        "exams_today": exams_today
    }

# ==================== LANGUAGES ====================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "de": "Deutsch",
    "it": "Italiano",
    "fr": "Français"
}

@api_router.get("/languages")
async def get_supported_languages():
    return {"languages": SUPPORTED_LANGUAGES}

# ==================== TRIAL REQUEST (LEAD CAPTURE) ====================

class TrialRequest(BaseModel):
    institutionName: str
    contactName: str
    email: str
    phone: str
    country: str
    studentsCount: str
    selectedExam: str

@api_router.post("/trial-request")
async def submit_trial_request(request: TrialRequest):
    """Capture institution lead for free trial verification"""
    trial_data = {
        "id": str(uuid4()),
        "institution_name": request.institutionName,
        "contact_name": request.contactName,
        "email": request.email,
        "phone": request.phone,
        "country": request.country,
        "students_count": request.studentsCount,
        "selected_exam": request.selectedExam,
        "status": "pending_verification",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.trial_requests.insert_one(trial_data)
    
    return {
        "success": True,
        "message": "Trial request received. Our team will contact you within 24 hours.",
        "request_id": trial_data["id"]
    }

@api_router.get("/admin/trial-requests")
async def get_trial_requests(current_user: dict = Depends(get_current_user)):
    """Get all trial requests for admin review"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    requests = await db.trial_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"trial_requests": requests}

# ==================== EXAM BANK MANAGEMENT ====================

class ExamQuestion(BaseModel):
    question_id: str
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    topic: str
    difficulty: str
    validation_status: str = "draft"

class ExamSection(BaseModel):
    section_type: str
    questions: List[Dict[str, Any]]

class CreateExamRequest(BaseModel):
    exam_type: str  # oet, ielts, toefl, etc.
    profession: Optional[str] = "nursing"
    topics: List[str]

@api_router.get("/admin/exam-bank")
async def get_exam_bank(
    exam_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all exams in the bank with filtering options"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = {}
    if exam_type:
        query["exam_type"] = exam_type
    if status:
        query["validation_status"] = status
    
    exams = await db.exam_bank.find(query, {"_id": 0}).to_list(100)
    
    # Calculate summary stats
    summary = {
        "total_exams": len(exams),
        "by_status": {},
        "by_type": {},
        "topics_coverage": {}
    }
    
    for exam in exams:
        status = exam.get("validation_status", "draft")
        exam_type = exam.get("exam_type", "unknown")
        
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
        summary["by_type"][exam_type] = summary["by_type"].get(exam_type, 0) + 1
        
        for topic in exam.get("topics_covered", []):
            summary["topics_coverage"][topic] = summary["topics_coverage"].get(topic, 0) + 1
    
    return {
        "exams": exams,
        "summary": summary
    }

@api_router.get("/admin/exam-bank/{exam_id}")
async def get_exam_details(exam_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed view of a single exam for admin review"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    exam = await db.exam_bank.find_one({"exam_id": exam_id}, {"_id": 0})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return exam

@api_router.post("/admin/exam-bank/validate/{exam_id}")
async def validate_exam(
    exam_id: str,
    action: str,  # approve, reject, request_changes
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Human validation of an exam"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    exam = await db.exam_bank.find_one({"exam_id": exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    new_status = {
        "approve": "approved",
        "reject": "rejected",
        "request_changes": "needs_revision"
    }.get(action, "pending_human_review")
    
    await db.exam_bank.update_one(
        {"exam_id": exam_id},
        {
            "$set": {
                "validation_status": new_status,
                "validated_by": current_user["email"],
                "validated_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "validation_history": {
                    "action": action,
                    "by": current_user["email"],
                    "at": datetime.now(timezone.utc).isoformat(),
                    "notes": notes
                }
            }
        }
    )
    
    return {"success": True, "new_status": new_status}

@api_router.put("/admin/exam-bank/{exam_id}/question/{question_id}")
async def update_question(
    exam_id: str,
    question_id: str,
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update a specific question in an exam"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would update the specific question in the exam document
    # Implementation depends on the exact structure
    
    await db.exam_bank.update_one(
        {"exam_id": exam_id},
        {
            "$set": {
                f"questions.{question_id}": updates,
                "last_modified": datetime.now(timezone.utc).isoformat(),
                "modified_by": current_user["email"]
            }
        }
    )
    
    return {"success": True}

@api_router.post("/admin/exam-bank/initialize-oet")
async def initialize_oet_exams(current_user: dict = Depends(get_current_user)):
    """Initialize the exam bank with OET sample exams"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Import the OET exam bank
    from exam_schemas.oet_exam_bank import OET_EXAM_BANK
    
    # Insert each exam
    for exam_key, exam_data in OET_EXAM_BANK.items():
        exam_data["exam_type"] = "oet"
        exam_data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Check if already exists
        existing = await db.exam_bank.find_one({"exam_id": exam_data["exam_id"]})
        if not existing:
            await db.exam_bank.insert_one(exam_data)
    
    return {"success": True, "message": "OET exams initialized"}

@api_router.get("/admin/exam-overview")
async def get_exam_overview(current_user: dict = Depends(get_current_user)):
    """Get a quick overview of all exams for admin dashboard"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pipeline = [
        {
            "$group": {
                "_id": {
                    "exam_type": "$exam_type",
                    "validation_status": "$validation_status"
                },
                "count": {"$sum": 1},
                "topics": {"$addToSet": "$topics_covered"}
            }
        }
    ]
    
    results = await db.exam_bank.aggregate(pipeline).to_list(100)
    
    # Get topic distribution
    all_exams = await db.exam_bank.find({}, {"topics_covered": 1, "_id": 0}).to_list(500)
    topic_counts = {}
    for exam in all_exams:
        for topic in exam.get("topics_covered", []):
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    return {
        "by_type_and_status": results,
        "topic_distribution": topic_counts,
        "exam_types": ["oet", "ielts", "toefl", "toeic", "celpip", "pte", "cambridge", "trinity"]
    }

# ==================== PREDICTIVE ANALYTICS ====================

def calculate_pass_probability(student_data: dict, exam_attempts: list) -> dict:
    """Calculate pass probability based on student performance metrics"""
    
    # Base probability starts at 50%
    probability = 50.0
    factors = []
    
    # Factor 1: Practice frequency (last 30 days)
    practice_count = len([a for a in exam_attempts if a.get("created_at", "") > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()])
    if practice_count >= 10:
        probability += 15
        factors.append({"factor": "High practice frequency", "impact": "+15%", "status": "positive"})
    elif practice_count >= 5:
        probability += 8
        factors.append({"factor": "Moderate practice frequency", "impact": "+8%", "status": "positive"})
    elif practice_count < 2:
        probability -= 10
        factors.append({"factor": "Low practice frequency", "impact": "-10%", "status": "negative"})
    
    # Factor 2: Average score trend
    if exam_attempts:
        scores = [a.get("score", 0) for a in exam_attempts if a.get("score")]
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / len(scores[-3:]) if len(scores) >= 3 else scores[-1]
            overall_avg = sum(scores) / len(scores)
            if recent_avg > overall_avg:
                probability += 12
                factors.append({"factor": "Improving score trend", "impact": "+12%", "status": "positive"})
            elif recent_avg < overall_avg * 0.9:
                probability -= 8
                factors.append({"factor": "Declining score trend", "impact": "-8%", "status": "negative"})
        
        # Factor 3: Overall performance level
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 80:
                probability += 20
                factors.append({"factor": "Excellent performance level", "impact": "+20%", "status": "positive"})
            elif avg_score >= 65:
                probability += 10
                factors.append({"factor": "Good performance level", "impact": "+10%", "status": "positive"})
            elif avg_score < 50:
                probability -= 15
                factors.append({"factor": "Below average performance", "impact": "-15%", "status": "negative"})
    
    # Factor 4: Time spent (credits used as proxy)
    credits_used = student_data.get("credits_used", 0)
    if credits_used >= 50:
        probability += 8
        factors.append({"factor": "High engagement (credits used)", "impact": "+8%", "status": "positive"})
    elif credits_used < 10:
        probability -= 5
        factors.append({"factor": "Low engagement", "impact": "-5%", "status": "negative"})
    
    # Factor 5: Days until exam (if set)
    exam_date = student_data.get("target_exam_date")
    if exam_date:
        try:
            days_until = (datetime.fromisoformat(exam_date.replace('Z', '+00:00')) - datetime.now(timezone.utc)).days
            if days_until > 30 and practice_count >= 5:
                probability += 5
                factors.append({"factor": "Good preparation time", "impact": "+5%", "status": "positive"})
            elif days_until < 7 and practice_count < 5:
                probability -= 10
                factors.append({"factor": "Limited time, low preparation", "impact": "-10%", "status": "negative"})
        except:
            pass
    
    # Ensure probability is within bounds
    probability = max(5, min(95, probability))
    
    # Determine risk level
    if probability >= 75:
        risk_level = "low"
        recommendation = "Student is on track. Maintain current practice schedule."
    elif probability >= 50:
        risk_level = "medium"
        recommendation = "Consider increasing practice frequency and focusing on weak areas."
    else:
        risk_level = "high"
        recommendation = "Immediate intervention recommended. Schedule tutoring session."
    
    return {
        "pass_probability": round(probability, 1),
        "risk_level": risk_level,
        "factors": factors,
        "recommendation": recommendation
    }

def calculate_dropout_risk(student_data: dict, activity_log: list) -> dict:
    """Calculate dropout risk based on engagement patterns"""
    
    risk_score = 0  # 0-100, higher = more likely to drop
    risk_factors = []
    
    # Factor 1: Days since last activity
    last_activity = student_data.get("last_activity")
    if last_activity:
        try:
            days_inactive = (datetime.now(timezone.utc) - datetime.fromisoformat(last_activity.replace('Z', '+00:00'))).days
            if days_inactive > 14:
                risk_score += 40
                risk_factors.append({"factor": f"No activity for {days_inactive} days", "impact": "High", "status": "critical"})
            elif days_inactive > 7:
                risk_score += 20
                risk_factors.append({"factor": f"No activity for {days_inactive} days", "impact": "Medium", "status": "warning"})
            elif days_inactive <= 2:
                risk_score -= 10
                risk_factors.append({"factor": "Recent activity", "impact": "Positive", "status": "good"})
        except:
            risk_score += 15
    else:
        risk_score += 30
        risk_factors.append({"factor": "No recorded activity", "impact": "High", "status": "critical"})
    
    # Factor 2: Login frequency trend
    recent_logins = len([a for a in activity_log if a.get("type") == "login" and a.get("timestamp", "") > (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()])
    if recent_logins == 0:
        risk_score += 25
        risk_factors.append({"factor": "No logins in 2 weeks", "impact": "High", "status": "critical"})
    elif recent_logins < 3:
        risk_score += 10
        risk_factors.append({"factor": "Low login frequency", "impact": "Medium", "status": "warning"})
    
    # Factor 3: Credits remaining vs used ratio
    credits = student_data.get("credits", 0)
    credits_used = student_data.get("credits_used", 0)
    if credits > 0 and credits_used == 0:
        risk_score += 20
        risk_factors.append({"factor": "Credits not being used", "impact": "High", "status": "critical"})
    
    # Factor 4: Exam attempts declining
    if activity_log:
        recent_exams = len([a for a in activity_log if a.get("type") == "exam" and a.get("timestamp", "") > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()])
        if recent_exams == 0 and credits_used > 0:
            risk_score += 15
            risk_factors.append({"factor": "No recent exam attempts", "impact": "Medium", "status": "warning"})
    
    # Ensure risk score is within bounds
    risk_score = max(0, min(100, risk_score))
    
    # Determine risk category
    if risk_score >= 60:
        risk_category = "high"
        action = "Immediate outreach required - call or personal message"
    elif risk_score >= 30:
        risk_category = "medium"
        action = "Send engagement email and offer support"
    else:
        risk_category = "low"
        action = "Continue monitoring"
    
    return {
        "dropout_risk": risk_score,
        "risk_category": risk_category,
        "risk_factors": risk_factors,
        "recommended_action": action
    }

@api_router.get("/institution/analytics/overview")
async def get_institution_analytics_overview(current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics overview for institution dashboard"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    # Get all students for this institution
    students = await db.users.find({"institution_id": institution_id, "user_type": "student"}).to_list(1000)
    
    # Get all exam attempts for these students
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find({"user_id": {"$in": student_ids}}).to_list(10000)
    
    # Calculate KPIs
    total_students = len(students)
    active_students = len([s for s in students if s.get("last_activity") and 
                          (datetime.now(timezone.utc) - datetime.fromisoformat(s.get("last_activity", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 7])
    
    # Pass rate calculation (students who passed at least one mock with >70%)
    students_with_pass = set()
    for attempt in exam_attempts:
        if attempt.get("score", 0) >= 70:
            students_with_pass.add(attempt.get("user_id"))
    pass_rate = (len(students_with_pass) / total_students * 100) if total_students > 0 else 0
    
    # Engagement rate (students active in last 30 days)
    engaged_students = len([s for s in students if s.get("last_activity") and 
                           (datetime.now(timezone.utc) - datetime.fromisoformat(s.get("last_activity", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 30])
    engagement_rate = (engaged_students / total_students * 100) if total_students > 0 else 0
    
    # Average score
    all_scores = [a.get("score", 0) for a in exam_attempts if a.get("score")]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Exams by type distribution
    exam_distribution = {}
    for student in students:
        exam_type = student.get("current_exam", "unknown")
        exam_distribution[exam_type] = exam_distribution.get(exam_type, 0) + 1
    
    # Risk analysis
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        analytics = calculate_pass_probability(student, student_attempts)
        if analytics["risk_level"] == "high":
            high_risk_count += 1
        elif analytics["risk_level"] == "medium":
            medium_risk_count += 1
        else:
            low_risk_count += 1
    
    return {
        "kpis": {
            "total_students": total_students,
            "active_students": active_students,
            "pass_rate": round(pass_rate, 1),
            "engagement_rate": round(engagement_rate, 1),
            "average_score": round(avg_score, 1),
            "total_exams_taken": len(exam_attempts)
        },
        "impact_metrics": {
            "capacity_multiplier": "10x",
            "pass_rate_increase": "+23%",
            "no_show_reduction": "-60%",
            "feedback_time": "Seconds vs Days"
        },
        "risk_distribution": {
            "high_risk": high_risk_count,
            "medium_risk": medium_risk_count,
            "low_risk": low_risk_count
        },
        "exam_distribution": exam_distribution,
        "trends": {
            "students_this_month": len([s for s in students if s.get("created_at", "") > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()]),
            "exams_this_month": len([a for a in exam_attempts if a.get("created_at", "") > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()])
        }
    }

@api_router.get("/institution/analytics/students")
async def get_students_analytics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics for all students with predictions"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    # Get all students
    students = await db.users.find({"institution_id": institution_id, "user_type": "student"}).to_list(1000)
    
    # Get activity logs
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find({"user_id": {"$in": student_ids}}).to_list(10000)
    activity_logs = await db.activity_log.find({"user_id": {"$in": student_ids}}).to_list(10000)
    
    students_analytics = []
    
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        student_activity = [a for a in activity_logs if a.get("user_id") == student["id"]]
        
        # Calculate pass probability
        pass_analysis = calculate_pass_probability(student, student_attempts)
        
        # Calculate dropout risk
        dropout_analysis = calculate_dropout_risk(student, student_activity)
        
        # Calculate scores
        scores = [a.get("score", 0) for a in student_attempts if a.get("score")]
        avg_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        students_analytics.append({
            "id": student["id"],
            "name": student.get("name", ""),
            "email": student.get("email", ""),
            "exam_type": student.get("current_exam", ""),
            "status": student.get("status", "active"),
            "created_at": student.get("created_at", ""),
            "last_activity": student.get("last_activity", ""),
            "credits": student.get("credits", 0),
            "credits_used": student.get("credits_used", 0),
            "performance": {
                "total_attempts": len(student_attempts),
                "average_score": round(avg_score, 1),
                "best_score": round(best_score, 1)
            },
            "pass_prediction": pass_analysis,
            "dropout_risk": dropout_analysis
        })
    
    # Sort by risk (high risk first)
    students_analytics.sort(key=lambda x: (-x["dropout_risk"]["dropout_risk"], -100 + x["pass_prediction"]["pass_probability"]))
    
    return {
        "total_students": len(students_analytics),
        "students": students_analytics
    }

@api_router.get("/institution/analytics/at-risk")
async def get_at_risk_students(current_user: dict = Depends(get_current_user)):
    """Get list of students at risk of dropping out or failing"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    # Get all students
    students = await db.users.find({"institution_id": institution_id, "user_type": "student"}).to_list(1000)
    student_ids = [s["id"] for s in students]
    
    exam_attempts = await db.exam_attempts.find({"user_id": {"$in": student_ids}}).to_list(10000)
    activity_logs = await db.activity_log.find({"user_id": {"$in": student_ids}}).to_list(10000)
    
    at_risk_students = []
    
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        student_activity = [a for a in activity_logs if a.get("user_id") == student["id"]]
        
        pass_analysis = calculate_pass_probability(student, student_attempts)
        dropout_analysis = calculate_dropout_risk(student, student_activity)
        
        # Include if high dropout risk OR low pass probability
        if dropout_analysis["risk_category"] in ["high", "medium"] or pass_analysis["risk_level"] == "high":
            at_risk_students.append({
                "id": student["id"],
                "name": student.get("name", ""),
                "email": student.get("email", ""),
                "exam_type": student.get("current_exam", ""),
                "last_activity": student.get("last_activity", "Never"),
                "pass_probability": pass_analysis["pass_probability"],
                "pass_risk_level": pass_analysis["risk_level"],
                "dropout_risk": dropout_analysis["dropout_risk"],
                "dropout_category": dropout_analysis["risk_category"],
                "primary_concern": "Dropout Risk" if dropout_analysis["dropout_risk"] > 50 else "Low Pass Probability",
                "recommended_action": dropout_analysis["recommended_action"] if dropout_analysis["dropout_risk"] > 50 else pass_analysis["recommendation"]
            })
    
    # Sort by combined risk
    at_risk_students.sort(key=lambda x: -(x["dropout_risk"] + (100 - x["pass_probability"])))
    
    return {
        "total_at_risk": len(at_risk_students),
        "high_priority": len([s for s in at_risk_students if s["dropout_category"] == "high" or s["pass_risk_level"] == "high"]),
        "students": at_risk_students
    }

@api_router.get("/institution/analytics/cohorts")
async def get_cohort_analytics(current_user: dict = Depends(get_current_user)):
    """Get analytics grouped by cohorts (exam type, enrollment month)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    students = await db.users.find({"institution_id": institution_id, "user_type": "student"}).to_list(1000)
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find({"user_id": {"$in": student_ids}}).to_list(10000)
    
    # Group by exam type
    by_exam = {}
    for student in students:
        exam = student.get("current_exam", "unknown")
        if exam not in by_exam:
            by_exam[exam] = {"students": [], "attempts": []}
        by_exam[exam]["students"].append(student)
    
    for attempt in exam_attempts:
        user_id = attempt.get("user_id")
        for student in students:
            if student["id"] == user_id:
                exam = student.get("current_exam", "unknown")
                by_exam[exam]["attempts"].append(attempt)
                break
    
    exam_cohorts = []
    for exam, data in by_exam.items():
        scores = [a.get("score", 0) for a in data["attempts"] if a.get("score")]
        exam_cohorts.append({
            "cohort_name": exam.upper(),
            "cohort_type": "exam",
            "total_students": len(data["students"]),
            "total_attempts": len(data["attempts"]),
            "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "pass_rate": round(len([s for s in scores if s >= 70]) / len(scores) * 100, 1) if scores else 0,
            "active_rate": round(len([s for s in data["students"] if s.get("last_activity") and 
                                     (datetime.now(timezone.utc) - datetime.fromisoformat(s.get("last_activity", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 7]) / len(data["students"]) * 100, 1) if data["students"] else 0
        })
    
    # Group by enrollment month
    by_month = {}
    for student in students:
        created = student.get("created_at", "")
        if created:
            month_key = created[:7]  # YYYY-MM
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(student)
    
    month_cohorts = []
    for month, month_students in sorted(by_month.items(), reverse=True)[:6]:
        month_ids = [s["id"] for s in month_students]
        month_attempts = [a for a in exam_attempts if a.get("user_id") in month_ids]
        scores = [a.get("score", 0) for a in month_attempts if a.get("score")]
        
        month_cohorts.append({
            "cohort_name": month,
            "cohort_type": "enrollment_month",
            "total_students": len(month_students),
            "total_attempts": len(month_attempts),
            "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "retention_rate": round(len([s for s in month_students if s.get("last_activity") and 
                                        (datetime.now(timezone.utc) - datetime.fromisoformat(s.get("last_activity", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 30]) / len(month_students) * 100, 1) if month_students else 0
        })
    
    return {
        "by_exam_type": exam_cohorts,
        "by_enrollment_month": month_cohorts
    }

@api_router.get("/institution/analytics/student/{student_id}")
async def get_student_detailed_analytics(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed analytics for a specific student"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    student = await db.users.find_one({"id": student_id, "institution_id": current_user["id"]})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all attempts and activities
    exam_attempts = await db.exam_attempts.find({"user_id": student_id}).sort("created_at", -1).to_list(100)
    activity_logs = await db.activity_log.find({"user_id": student_id}).sort("timestamp", -1).to_list(100)
    
    # Calculate predictions
    pass_analysis = calculate_pass_probability(student, exam_attempts)
    dropout_analysis = calculate_dropout_risk(student, activity_logs)
    
    # Performance by section
    section_scores = {"reading": [], "writing": [], "listening": [], "speaking": []}
    for attempt in exam_attempts:
        for section, score in attempt.get("section_scores", {}).items():
            if section in section_scores:
                section_scores[section].append(score)
    
    section_averages = {}
    for section, scores in section_scores.items():
        section_averages[section] = round(sum(scores) / len(scores), 1) if scores else 0
    
    # Score progression over time
    score_history = []
    for attempt in reversed(exam_attempts[-10:]):
        score_history.append({
            "date": attempt.get("created_at", "")[:10],
            "score": attempt.get("score", 0),
            "exam_type": attempt.get("exam_type", "")
        })
    
    return {
        "student": {
            "id": student["id"],
            "name": student.get("name", ""),
            "email": student.get("email", ""),
            "exam_type": student.get("current_exam", ""),
            "enrolled_at": student.get("created_at", ""),
            "last_activity": student.get("last_activity", ""),
            "credits": student.get("credits", 0),
            "credits_used": student.get("credits_used", 0)
        },
        "predictions": {
            "pass_probability": pass_analysis,
            "dropout_risk": dropout_analysis
        },
        "performance": {
            "total_attempts": len(exam_attempts),
            "average_score": round(sum([a.get("score", 0) for a in exam_attempts if a.get("score")]) / len(exam_attempts), 1) if exam_attempts else 0,
            "best_score": max([a.get("score", 0) for a in exam_attempts]) if exam_attempts else 0,
            "section_averages": section_averages,
            "score_history": score_history
        },
        "recent_activity": [{
            "type": a.get("type", ""),
            "timestamp": a.get("timestamp", ""),
            "details": a.get("details", "")
        } for a in activity_logs[:10]]
    }

# ==================== CRM & SALES PIPELINE ====================

# Lead/Deal stages for sales pipeline
PIPELINE_STAGES = {
    "new": {"label": "New Lead", "order": 1, "color": "#6366F1"},
    "contacted": {"label": "Contacted", "order": 2, "color": "#8B5CF6"},
    "demo_scheduled": {"label": "Demo Scheduled", "order": 3, "color": "#F59E0B"},
    "demo_completed": {"label": "Demo Completed", "order": 4, "color": "#3B82F6"},
    "proposal_sent": {"label": "Proposal Sent", "order": 5, "color": "#EC4899"},
    "negotiating": {"label": "Negotiating", "order": 6, "color": "#F97316"},
    "won": {"label": "Won 🎉", "order": 7, "color": "#10B981"},
    "lost": {"label": "Lost", "order": 8, "color": "#EF4444"}
}

class LeadCreate(BaseModel):
    institution_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None
    students_count: Optional[int] = None
    exam_types: Optional[List[str]] = []
    source: Optional[str] = "website"
    notes: Optional[str] = None
    estimated_value: Optional[float] = 0

class LeadUpdate(BaseModel):
    stage: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    students_count: Optional[int] = None
    exam_types: Optional[List[str]] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    next_follow_up: Optional[str] = None
    assigned_to: Optional[str] = None

class ActivityCreate(BaseModel):
    lead_id: str
    activity_type: str  # call, email, meeting, note, demo
    description: str
    outcome: Optional[str] = None

@api_router.get("/crm/pipeline-stages")
async def get_pipeline_stages():
    """Get all available pipeline stages"""
    return {"stages": PIPELINE_STAGES}

@api_router.post("/crm/leads")
async def create_lead(lead_data: LeadCreate, current_user: dict = Depends(get_current_user)):
    """Create a new lead in the CRM"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Only admins and institutions can create leads")
    
    # Check if lead with same email exists
    existing = await db.crm_leads.find_one({"email": lead_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Lead with this email already exists")
    
    lead_id = str(uuid.uuid4())
    lead_doc = {
        "id": lead_id,
        "institution_name": lead_data.institution_name,
        "contact_name": lead_data.contact_name,
        "email": lead_data.email,
        "phone": lead_data.phone,
        "country": lead_data.country,
        "students_count": lead_data.students_count,
        "exam_types": lead_data.exam_types or [],
        "source": lead_data.source,
        "notes": lead_data.notes,
        "estimated_value": lead_data.estimated_value or 0,
        "stage": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"],
        "assigned_to": current_user["id"],
        "next_follow_up": None,
        "activities": [],
        "tags": []
    }
    
    await db.crm_leads.insert_one(lead_doc)
    
    return {"id": lead_id, "message": "Lead created successfully", "lead": lead_doc}

@api_router.get("/crm/leads")
async def get_all_leads(
    stage: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all leads, optionally filtered by stage"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if stage:
        query["stage"] = stage
    
    # For institutions, only show their own leads
    if current_user["user_type"] == "institution":
        query["$or"] = [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    leads = await db.crm_leads.find(query).sort("updated_at", -1).to_list(500)
    
    # Group by stage for pipeline view
    pipeline = {stage: [] for stage in PIPELINE_STAGES.keys()}
    for lead in leads:
        lead_stage = lead.get("stage", "new")
        if lead_stage in pipeline:
            pipeline[lead_stage].append({
                "id": lead["id"],
                "institution_name": lead.get("institution_name", ""),
                "contact_name": lead.get("contact_name", ""),
                "email": lead.get("email", ""),
                "phone": lead.get("phone", ""),
                "country": lead.get("country", ""),
                "students_count": lead.get("students_count", 0),
                "exam_types": lead.get("exam_types", []),
                "estimated_value": lead.get("estimated_value", 0),
                "stage": lead_stage,
                "created_at": lead.get("created_at", ""),
                "updated_at": lead.get("updated_at", ""),
                "next_follow_up": lead.get("next_follow_up"),
                "source": lead.get("source", ""),
                "activities_count": len(lead.get("activities", []))
            })
    
    # Calculate totals
    total_leads = len(leads)
    total_value = sum(l.get("estimated_value", 0) for l in leads)
    won_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") == "won")
    
    return {
        "pipeline": pipeline,
        "stages": PIPELINE_STAGES,
        "stats": {
            "total_leads": total_leads,
            "total_value": total_value,
            "won_value": won_value,
            "conversion_rate": round(len([l for l in leads if l.get("stage") == "won"]) / total_leads * 100, 1) if total_leads > 0 else 0
        }
    }

@api_router.get("/crm/leads/{lead_id}")
async def get_lead_detail(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a lead"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "id": lead["id"],
        "institution_name": lead.get("institution_name", ""),
        "contact_name": lead.get("contact_name", ""),
        "email": lead.get("email", ""),
        "phone": lead.get("phone", ""),
        "country": lead.get("country", ""),
        "students_count": lead.get("students_count", 0),
        "exam_types": lead.get("exam_types", []),
        "estimated_value": lead.get("estimated_value", 0),
        "stage": lead.get("stage", "new"),
        "source": lead.get("source", ""),
        "notes": lead.get("notes", ""),
        "created_at": lead.get("created_at", ""),
        "updated_at": lead.get("updated_at", ""),
        "next_follow_up": lead.get("next_follow_up"),
        "assigned_to": lead.get("assigned_to"),
        "activities": lead.get("activities", []),
        "tags": lead.get("tags", [])
    }

@api_router.put("/crm/leads/{lead_id}")
async def update_lead(lead_id: str, updates: LeadUpdate, current_user: dict = Depends(get_current_user)):
    """Update a lead's information or stage"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if updates.stage:
        if updates.stage not in PIPELINE_STAGES:
            raise HTTPException(status_code=400, detail="Invalid stage")
        update_data["stage"] = updates.stage
        
        # Add stage change to activities
        activity = {
            "id": str(uuid.uuid4()),
            "type": "stage_change",
            "description": f"Stage changed from {lead.get('stage', 'new')} to {updates.stage}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": current_user["email"]
        }
        await db.crm_leads.update_one(
            {"id": lead_id},
            {"$push": {"activities": activity}}
        )
    
    if updates.contact_name:
        update_data["contact_name"] = updates.contact_name
    if updates.phone:
        update_data["phone"] = updates.phone
    if updates.country:
        update_data["country"] = updates.country
    if updates.students_count is not None:
        update_data["students_count"] = updates.students_count
    if updates.exam_types is not None:
        update_data["exam_types"] = updates.exam_types
    if updates.notes:
        update_data["notes"] = updates.notes
    if updates.estimated_value is not None:
        update_data["estimated_value"] = updates.estimated_value
    if updates.next_follow_up:
        update_data["next_follow_up"] = updates.next_follow_up
    if updates.assigned_to:
        update_data["assigned_to"] = updates.assigned_to
    
    await db.crm_leads.update_one({"id": lead_id}, {"$set": update_data})
    
    return {"message": "Lead updated successfully", "updated_fields": list(update_data.keys())}

@api_router.post("/crm/leads/{lead_id}/activities")
async def add_lead_activity(lead_id: str, activity: ActivityCreate, current_user: dict = Depends(get_current_user)):
    """Add an activity to a lead (call, email, meeting, note)"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    activity_doc = {
        "id": str(uuid.uuid4()),
        "type": activity.activity_type,
        "description": activity.description,
        "outcome": activity.outcome,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": current_user["email"]
    }
    
    await db.crm_leads.update_one(
        {"id": lead_id},
        {
            "$push": {"activities": activity_doc},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"message": "Activity added", "activity": activity_doc}

@api_router.delete("/crm/leads/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a lead"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete leads")
    
    result = await db.crm_leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"message": "Lead deleted successfully"}

@api_router.get("/crm/dashboard")
async def get_crm_dashboard(current_user: dict = Depends(get_current_user)):
    """Get CRM dashboard with key metrics"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if current_user["user_type"] == "institution":
        query["$or"] = [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    leads = await db.crm_leads.find(query).to_list(1000)
    
    # Calculate metrics
    total_leads = len(leads)
    new_leads = len([l for l in leads if l.get("stage") == "new"])
    won_deals = len([l for l in leads if l.get("stage") == "won"])
    lost_deals = len([l for l in leads if l.get("stage") == "lost"])
    
    total_value = sum(l.get("estimated_value", 0) for l in leads)
    won_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") == "won")
    pipeline_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") not in ["won", "lost"])
    
    # Leads by stage
    by_stage = {}
    for stage in PIPELINE_STAGES.keys():
        stage_leads = [l for l in leads if l.get("stage") == stage]
        by_stage[stage] = {
            "count": len(stage_leads),
            "value": sum(l.get("estimated_value", 0) for l in stage_leads)
        }
    
    # Leads by source
    by_source = {}
    for lead in leads:
        source = lead.get("source", "unknown")
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1
    
    # Recent activities
    recent_activities = []
    for lead in sorted(leads, key=lambda x: x.get("updated_at", ""), reverse=True)[:10]:
        activities = lead.get("activities", [])
        if activities:
            latest = activities[-1]
            recent_activities.append({
                "lead_id": lead["id"],
                "lead_name": lead.get("institution_name", ""),
                "activity": latest
            })
    
    # Follow-ups due
    today = datetime.now(timezone.utc).date().isoformat()
    follow_ups_due = []
    for lead in leads:
        follow_up = lead.get("next_follow_up")
        if follow_up and follow_up <= today:
            follow_ups_due.append({
                "id": lead["id"],
                "institution_name": lead.get("institution_name", ""),
                "contact_name": lead.get("contact_name", ""),
                "follow_up_date": follow_up,
                "stage": lead.get("stage", "")
            })
    
    return {
        "metrics": {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "won_deals": won_deals,
            "lost_deals": lost_deals,
            "conversion_rate": round(won_deals / (won_deals + lost_deals) * 100, 1) if (won_deals + lost_deals) > 0 else 0,
            "total_value": total_value,
            "won_value": won_value,
            "pipeline_value": pipeline_value,
            "avg_deal_size": round(won_value / won_deals, 2) if won_deals > 0 else 0
        },
        "by_stage": by_stage,
        "by_source": by_source,
        "recent_activities": recent_activities[:5],
        "follow_ups_due": follow_ups_due
    }

# Connect trial request form to CRM
@api_router.post("/trial-request")
async def submit_trial_request(request_data: dict):
    """Handle trial request form submission and create lead"""
    lead_id = str(uuid.uuid4())
    
    lead_doc = {
        "id": lead_id,
        "institution_name": request_data.get("institutionName", ""),
        "contact_name": request_data.get("contactName", ""),
        "email": request_data.get("email", ""),
        "phone": request_data.get("phone", ""),
        "country": request_data.get("country", ""),
        "students_count": int(request_data.get("studentsCount", 0)) if request_data.get("studentsCount") else 0,
        "exam_types": [request_data.get("selectedExam")] if request_data.get("selectedExam") else [],
        "source": "free_trial_form",
        "notes": f"Trial request submitted via website",
        "estimated_value": 0,
        "stage": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "website",
        "assigned_to": None,
        "next_follow_up": (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat(),
        "activities": [{
            "id": str(uuid.uuid4()),
            "type": "form_submission",
            "description": "Trial request form submitted",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "system"
        }],
        "tags": ["trial_request"]
    }
    
    # Check if lead already exists
    existing = await db.crm_leads.find_one({"email": request_data.get("email")})
    if existing:
        # Update existing lead
        await db.crm_leads.update_one(
            {"email": request_data.get("email")},
            {
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
                "$push": {"activities": lead_doc["activities"][0]}
            }
        )
        return {"message": "Trial request received", "lead_id": existing["id"]}
    
    await db.crm_leads.insert_one(lead_doc)
    
    return {"message": "Trial request received! We'll contact you within 24 hours.", "lead_id": lead_id}

# ==================== B2B MARKETPLACE ====================

class MarketplaceListingCreate(BaseModel):
    title: str
    description: str
    category: str  # tutoring, materials, courses, exam_prep, teacher_training
    price: float
    price_type: str  # per_student, per_session, per_course, flat_fee
    exam_types: Optional[List[str]] = []
    language: Optional[str] = "en"
    availability: Optional[str] = "available"  # available, limited, sold_out
    min_quantity: Optional[int] = 1
    max_quantity: Optional[int] = None
    delivery_method: Optional[str] = "online"  # online, in_person, hybrid

class MarketplaceListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[str] = None
    is_active: Optional[bool] = None

MARKETPLACE_CATEGORIES = {
    "tutoring": {"label": "Tutoring Services", "icon": "👨‍🏫"},
    "materials": {"label": "Study Materials", "icon": "📚"},
    "courses": {"label": "Full Courses", "icon": "🎓"},
    "exam_prep": {"label": "Exam Preparation", "icon": "📝"},
    "teacher_training": {"label": "Teacher Training", "icon": "👩‍🎓"},
    "mock_exams": {"label": "Mock Exams", "icon": "✍️"},
    "speaking_practice": {"label": "Speaking Practice", "icon": "🗣️"},
    "writing_review": {"label": "Writing Review", "icon": "✏️"}
}

@api_router.get("/marketplace/categories")
async def get_marketplace_categories():
    """Get all marketplace categories"""
    return {"categories": MARKETPLACE_CATEGORIES}

@api_router.post("/marketplace/listings")
async def create_marketplace_listing(listing: MarketplaceListingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new marketplace listing"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create listings")
    
    listing_id = str(uuid.uuid4())
    
    listing_doc = {
        "id": listing_id,
        "seller_id": current_user["id"],
        "seller_name": current_user.get("institution_name", current_user.get("name", "")),
        "seller_slug": current_user.get("institution_slug", ""),
        "title": listing.title,
        "description": listing.description,
        "category": listing.category,
        "price": listing.price,
        "price_type": listing.price_type,
        "exam_types": listing.exam_types,
        "language": listing.language,
        "availability": listing.availability,
        "min_quantity": listing.min_quantity,
        "max_quantity": listing.max_quantity,
        "delivery_method": listing.delivery_method,
        "rating": 0,
        "reviews_count": 0,
        "sales_count": 0,
        "is_active": True,
        "is_featured": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketplace_listings.insert_one(listing_doc)
    
    return {"id": listing_id, "message": "Listing created successfully", "listing": listing_doc}

@api_router.get("/marketplace/listings")
async def get_marketplace_listings(
    category: Optional[str] = None,
    exam_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "newest"  # newest, price_low, price_high, rating, popular
):
    """Get all active marketplace listings"""
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    if exam_type:
        query["exam_types"] = exam_type
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        query["price"] = {**query.get("price", {}), "$lte": max_price}
    
    # Sorting
    sort_field = "created_at"
    sort_order = -1
    if sort_by == "price_low":
        sort_field = "price"
        sort_order = 1
    elif sort_by == "price_high":
        sort_field = "price"
        sort_order = -1
    elif sort_by == "rating":
        sort_field = "rating"
        sort_order = -1
    elif sort_by == "popular":
        sort_field = "sales_count"
        sort_order = -1
    
    listings = await db.marketplace_listings.find(query).sort(sort_field, sort_order).to_list(100)
    
    # Calculate stats
    total_listings = await db.marketplace_listings.count_documents({"is_active": True})
    featured_listings = [l for l in listings if l.get("is_featured")]
    
    return {
        "total": len(listings),
        "listings": [{
            "id": l["id"],
            "title": l["title"],
            "description": l["description"],
            "category": l["category"],
            "category_info": MARKETPLACE_CATEGORIES.get(l["category"], {}),
            "price": l["price"],
            "price_type": l["price_type"],
            "exam_types": l.get("exam_types", []),
            "seller_name": l["seller_name"],
            "seller_id": l["seller_id"],
            "rating": l.get("rating", 0),
            "reviews_count": l.get("reviews_count", 0),
            "sales_count": l.get("sales_count", 0),
            "availability": l.get("availability", "available"),
            "delivery_method": l.get("delivery_method", "online"),
            "is_featured": l.get("is_featured", False),
            "created_at": l.get("created_at", "")
        } for l in listings],
        "featured": [{
            "id": l["id"],
            "title": l["title"],
            "price": l["price"],
            "seller_name": l["seller_name"],
            "category": l["category"]
        } for l in featured_listings],
        "stats": {
            "total_listings": total_listings,
            "categories_count": len(set(l["category"] for l in listings))
        }
    }

@api_router.get("/marketplace/listings/{listing_id}")
async def get_marketplace_listing_detail(listing_id: str):
    """Get detailed information about a listing"""
    listing = await db.marketplace_listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Get seller info
    seller = await db.users.find_one({"id": listing["seller_id"]})
    
    # Get reviews
    reviews = await db.marketplace_reviews.find({"listing_id": listing_id}).sort("created_at", -1).to_list(20)
    
    return {
        "listing": {
            "id": listing["id"],
            "title": listing["title"],
            "description": listing["description"],
            "category": listing["category"],
            "category_info": MARKETPLACE_CATEGORIES.get(listing["category"], {}),
            "price": listing["price"],
            "price_type": listing["price_type"],
            "exam_types": listing.get("exam_types", []),
            "availability": listing.get("availability", "available"),
            "min_quantity": listing.get("min_quantity", 1),
            "max_quantity": listing.get("max_quantity"),
            "delivery_method": listing.get("delivery_method", "online"),
            "rating": listing.get("rating", 0),
            "reviews_count": listing.get("reviews_count", 0),
            "sales_count": listing.get("sales_count", 0),
            "created_at": listing.get("created_at", "")
        },
        "seller": {
            "id": seller["id"] if seller else None,
            "name": seller.get("institution_name", "") if seller else "",
            "slug": seller.get("institution_slug", "") if seller else ""
        },
        "reviews": [{
            "id": r["id"],
            "rating": r["rating"],
            "comment": r["comment"],
            "buyer_name": r.get("buyer_name", ""),
            "created_at": r.get("created_at", "")
        } for r in reviews]
    }

@api_router.get("/marketplace/my-listings")
async def get_my_marketplace_listings(current_user: dict = Depends(get_current_user)):
    """Get listings created by the current user"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can have listings")
    
    listings = await db.marketplace_listings.find({"seller_id": current_user["id"]}).sort("created_at", -1).to_list(100)
    
    # Calculate total revenue from orders
    orders = await db.marketplace_orders.find({"seller_id": current_user["id"], "status": "completed"}).to_list(1000)
    total_revenue = sum(o.get("total_price", 0) for o in orders)
    
    return {
        "total": len(listings),
        "total_revenue": total_revenue,
        "listings": [{
            "id": l["id"],
            "title": l["title"],
            "category": l["category"],
            "price": l["price"],
            "price_type": l["price_type"],
            "sales_count": l.get("sales_count", 0),
            "rating": l.get("rating", 0),
            "is_active": l.get("is_active", True),
            "availability": l.get("availability", "available"),
            "created_at": l.get("created_at", "")
        } for l in listings]
    }

@api_router.put("/marketplace/listings/{listing_id}")
async def update_marketplace_listing(listing_id: str, updates: MarketplaceListingUpdate, current_user: dict = Depends(get_current_user)):
    """Update a marketplace listing"""
    listing = await db.marketplace_listings.find_one({"id": listing_id, "seller_id": current_user["id"]})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or not owned by you")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if updates.title:
        update_data["title"] = updates.title
    if updates.description:
        update_data["description"] = updates.description
    if updates.price is not None:
        update_data["price"] = updates.price
    if updates.availability:
        update_data["availability"] = updates.availability
    if updates.is_active is not None:
        update_data["is_active"] = updates.is_active
    
    await db.marketplace_listings.update_one({"id": listing_id}, {"$set": update_data})
    
    return {"message": "Listing updated successfully"}

@api_router.delete("/marketplace/listings/{listing_id}")
async def delete_marketplace_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a marketplace listing"""
    result = await db.marketplace_listings.delete_one({"id": listing_id, "seller_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found or not owned by you")
    
    return {"message": "Listing deleted successfully"}

@api_router.post("/marketplace/orders")
async def create_marketplace_order(order_data: dict, current_user: dict = Depends(get_current_user)):
    """Create an order for a marketplace listing"""
    listing = await db.marketplace_listings.find_one({"id": order_data.get("listing_id")})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.get("availability") == "sold_out":
        raise HTTPException(status_code=400, detail="This listing is sold out")
    
    quantity = order_data.get("quantity", 1)
    total_price = listing["price"] * quantity
    
    # Platform commission (10%)
    commission = total_price * 0.10
    seller_amount = total_price - commission
    
    order_id = str(uuid.uuid4())
    
    order_doc = {
        "id": order_id,
        "listing_id": listing["id"],
        "listing_title": listing["title"],
        "seller_id": listing["seller_id"],
        "seller_name": listing["seller_name"],
        "buyer_id": current_user["id"],
        "buyer_name": current_user.get("institution_name", current_user.get("name", "")),
        "quantity": quantity,
        "unit_price": listing["price"],
        "total_price": total_price,
        "commission": commission,
        "seller_amount": seller_amount,
        "status": "pending",  # pending, confirmed, completed, cancelled
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketplace_orders.insert_one(order_doc)
    
    # Update listing sales count
    await db.marketplace_listings.update_one(
        {"id": listing["id"]},
        {"$inc": {"sales_count": quantity}}
    )
    
    return {"order_id": order_id, "message": "Order created successfully", "order": order_doc}

@api_router.get("/marketplace/orders")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    """Get orders for the current user (as buyer or seller)"""
    
    # Get orders as buyer
    buyer_orders = await db.marketplace_orders.find({"buyer_id": current_user["id"]}).sort("created_at", -1).to_list(100)
    
    # Get orders as seller
    seller_orders = await db.marketplace_orders.find({"seller_id": current_user["id"]}).sort("created_at", -1).to_list(100)
    
    return {
        "as_buyer": [{
            "id": o["id"],
            "listing_title": o["listing_title"],
            "seller_name": o["seller_name"],
            "quantity": o["quantity"],
            "total_price": o["total_price"],
            "status": o["status"],
            "created_at": o["created_at"]
        } for o in buyer_orders],
        "as_seller": [{
            "id": o["id"],
            "listing_title": o["listing_title"],
            "buyer_name": o["buyer_name"],
            "quantity": o["quantity"],
            "total_price": o["total_price"],
            "seller_amount": o["seller_amount"],
            "commission": o["commission"],
            "status": o["status"],
            "created_at": o["created_at"]
        } for o in seller_orders]
    }

# ==================== VIDEO CLASSES & STREAMING ====================

class VideoClassCreate(BaseModel):
    title: str
    description: str
    exam_type: str
    skill: str  # reading, writing, listening, speaking
    scheduled_at: Optional[str] = None  # ISO datetime for live classes
    duration_minutes: Optional[int] = 60
    class_type: str  # live, recorded
    video_url: Optional[str] = None  # For recorded classes
    max_students: Optional[int] = 100

class VideoClassUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: Optional[str] = None  # scheduled, live, ended, cancelled

@api_router.post("/video-classes")
async def create_video_class(video_class: VideoClassCreate, current_user: dict = Depends(get_current_user)):
    """Create a new video class (live or recorded)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create video classes")
    
    class_id = str(uuid.uuid4())
    
    # Generate a simple room code for live classes
    room_code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6)) if video_class.class_type == "live" else None
    
    class_doc = {
        "id": class_id,
        "institution_id": current_user["id"],
        "institution_name": current_user.get("institution_name", ""),
        "title": video_class.title,
        "description": video_class.description,
        "exam_type": video_class.exam_type,
        "skill": video_class.skill,
        "class_type": video_class.class_type,
        "scheduled_at": video_class.scheduled_at,
        "duration_minutes": video_class.duration_minutes,
        "video_url": video_class.video_url,
        "max_students": video_class.max_students,
        "room_code": room_code,
        "status": "scheduled" if video_class.class_type == "live" else "available",
        "enrolled_students": [],
        "attendees_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.video_classes.insert_one(class_doc)
    
    return {"id": class_id, "room_code": room_code, "message": "Video class created successfully"}

@api_router.get("/video-classes")
async def get_video_classes(
    class_type: Optional[str] = None,
    exam_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get video classes for the institution"""
    if current_user["user_type"] == "institution":
        query = {"institution_id": current_user["id"]}
    elif current_user["user_type"] == "student":
        query = {"institution_id": current_user.get("institution_id")}
    else:
        query = {}
    
    if class_type:
        query["class_type"] = class_type
    if exam_type:
        query["exam_type"] = exam_type
    
    classes = await db.video_classes.find(query).sort("scheduled_at", -1).to_list(100)
    
    # Separate live and recorded
    live_classes = [c for c in classes if c.get("class_type") == "live"]
    recorded_classes = [c for c in classes if c.get("class_type") == "recorded"]
    
    return {
        "total": len(classes),
        "live_classes": [{
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "exam_type": c["exam_type"],
            "skill": c["skill"],
            "scheduled_at": c.get("scheduled_at"),
            "duration_minutes": c.get("duration_minutes", 60),
            "room_code": c.get("room_code"),
            "status": c.get("status", "scheduled"),
            "max_students": c.get("max_students", 100),
            "enrolled_count": len(c.get("enrolled_students", []))
        } for c in live_classes],
        "recorded_classes": [{
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "exam_type": c["exam_type"],
            "skill": c["skill"],
            "video_url": c.get("video_url"),
            "duration_minutes": c.get("duration_minutes", 60),
            "views_count": c.get("views_count", 0)
        } for c in recorded_classes],
        "stats": {
            "total_live": len(live_classes),
            "total_recorded": len(recorded_classes),
            "upcoming": len([c for c in live_classes if c.get("status") == "scheduled"])
        }
    }

@api_router.post("/video-classes/{class_id}/enroll")
async def enroll_in_video_class(class_id: str, current_user: dict = Depends(get_current_user)):
    """Enroll a student in a live video class"""
    video_class = await db.video_classes.find_one({"id": class_id})
    if not video_class:
        raise HTTPException(status_code=404, detail="Video class not found")
    
    if current_user["id"] in video_class.get("enrolled_students", []):
        return {"message": "Already enrolled", "room_code": video_class.get("room_code")}
    
    if len(video_class.get("enrolled_students", [])) >= video_class.get("max_students", 100):
        raise HTTPException(status_code=400, detail="Class is full")
    
    await db.video_classes.update_one(
        {"id": class_id},
        {"$push": {"enrolled_students": current_user["id"]}}
    )
    
    return {"message": "Enrolled successfully", "room_code": video_class.get("room_code")}

@api_router.put("/video-classes/{class_id}/status")
async def update_video_class_status(class_id: str, status: str, current_user: dict = Depends(get_current_user)):
    """Update video class status (start/end live class)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update class status")
    
    video_class = await db.video_classes.find_one({"id": class_id, "institution_id": current_user["id"]})
    if not video_class:
        raise HTTPException(status_code=404, detail="Video class not found")
    
    if status not in ["scheduled", "live", "ended", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    update_data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if status == "live":
        update_data["started_at"] = datetime.now(timezone.utc).isoformat()
    elif status == "ended":
        update_data["ended_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.video_classes.update_one({"id": class_id}, {"$set": update_data})
    
    return {"message": f"Class status updated to {status}"}

@api_router.delete("/video-classes/{class_id}")
async def delete_video_class(class_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a video class"""
    result = await db.video_classes.delete_one({"id": class_id, "institution_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video class not found")
    
    return {"message": "Video class deleted successfully"}

# ==================== WHITE-LABEL PREMIUM SYSTEM ====================

class WhiteLabelConfig(BaseModel):
    institution_id: str
    # Domain Configuration
    custom_domain: Optional[str] = None  # e.g., app.oxford-academy.com
    subdomain: Optional[str] = None  # e.g., oxford -> oxford.proficienthub.com
    # Branding
    platform_name: str = "ProficientHub"
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None  # For dark backgrounds
    favicon_url: Optional[str] = None
    # Colors
    primary_color: str = "#58CC02"
    secondary_color: str = "#1CB0F6"
    accent_color: str = "#FF4B4B"
    background_color: str = "#FFFFFF"
    text_color: str = "#1F2937"
    # Typography
    font_family: str = "Inter, system-ui, sans-serif"
    heading_font: Optional[str] = None
    # UI Customization
    border_radius: str = "12px"
    button_style: str = "rounded"  # rounded, square, pill
    card_style: str = "elevated"  # elevated, flat, bordered
    # Features Toggle
    show_powered_by: bool = True
    enable_dark_mode: bool = True
    enable_multi_language: bool = True
    # Email Branding
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    email_footer_text: Optional[str] = None
    email_logo_url: Optional[str] = None
    # Social Links
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    # Custom CSS
    custom_css: Optional[str] = None
    # Landing Page
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    # Contact
    support_email: Optional[str] = None
    support_phone: Optional[str] = None

class WhiteLabelUpdate(BaseModel):
    custom_domain: Optional[str] = None
    subdomain: Optional[str] = None
    platform_name: Optional[str] = None
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    font_family: Optional[str] = None
    heading_font: Optional[str] = None
    border_radius: Optional[str] = None
    button_style: Optional[str] = None
    card_style: Optional[str] = None
    show_powered_by: Optional[bool] = None
    enable_dark_mode: Optional[bool] = None
    email_from_name: Optional[str] = None
    email_footer_text: Optional[str] = None
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    custom_css: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None

@api_router.post("/whitelabel/config")
async def create_whitelabel_config(config: WhiteLabelConfig, current_user: dict = Depends(get_current_user)):
    """Create white-label configuration for an institution"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = config.institution_id if current_user["user_type"] == "admin" else current_user["id"]
    
    # Check if config already exists
    existing = await db.whitelabel_configs.find_one({"institution_id": institution_id})
    if existing:
        raise HTTPException(status_code=400, detail="White-label config already exists. Use PUT to update.")
    
    # Validate custom domain/subdomain uniqueness
    if config.custom_domain:
        domain_exists = await db.whitelabel_configs.find_one({"custom_domain": config.custom_domain})
        if domain_exists:
            raise HTTPException(status_code=400, detail="Custom domain already in use")
    
    if config.subdomain:
        subdomain_exists = await db.whitelabel_configs.find_one({"subdomain": config.subdomain})
        if subdomain_exists:
            raise HTTPException(status_code=400, detail="Subdomain already in use")
    
    config_doc = {
        "id": str(uuid.uuid4()),
        "institution_id": institution_id,
        **config.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "ssl_status": "pending" if config.custom_domain else None,
        "dns_verified": False if config.custom_domain else None
    }
    
    await db.whitelabel_configs.insert_one(config_doc)
    
    return {"message": "White-label configuration created", "config": config_doc}

@api_router.get("/whitelabel/config")
async def get_whitelabel_config(current_user: dict = Depends(get_current_user)):
    """Get white-label configuration for current institution"""
    institution_id = current_user["id"] if current_user["user_type"] == "institution" else current_user.get("institution_id")
    
    config = await db.whitelabel_configs.find_one({"institution_id": institution_id})
    
    if not config:
        # Return default config
        return {
            "config": {
                "platform_name": "ProficientHub",
                "primary_color": "#58CC02",
                "secondary_color": "#1CB0F6",
                "accent_color": "#FF4B4B",
                "show_powered_by": True,
                "is_default": True
            }
        }
    
    return {"config": config}

@api_router.get("/whitelabel/by-domain/{domain}")
async def get_whitelabel_by_domain(domain: str):
    """Get white-label config by custom domain or subdomain (public endpoint)"""
    # Try custom domain first
    config = await db.whitelabel_configs.find_one({"custom_domain": domain, "is_active": True})
    
    if not config:
        # Try subdomain
        subdomain = domain.split('.')[0] if '.' in domain else domain
        config = await db.whitelabel_configs.find_one({"subdomain": subdomain, "is_active": True})
    
    if not config:
        return {"config": None, "is_default": True}
    
    # Get institution info
    institution = await db.users.find_one({"id": config["institution_id"]})
    
    return {
        "config": {
            "platform_name": config.get("platform_name", "ProficientHub"),
            "logo_url": config.get("logo_url"),
            "logo_dark_url": config.get("logo_dark_url"),
            "favicon_url": config.get("favicon_url"),
            "primary_color": config.get("primary_color", "#58CC02"),
            "secondary_color": config.get("secondary_color", "#1CB0F6"),
            "accent_color": config.get("accent_color", "#FF4B4B"),
            "background_color": config.get("background_color", "#FFFFFF"),
            "text_color": config.get("text_color", "#1F2937"),
            "font_family": config.get("font_family", "Inter, system-ui, sans-serif"),
            "heading_font": config.get("heading_font"),
            "border_radius": config.get("border_radius", "12px"),
            "button_style": config.get("button_style", "rounded"),
            "card_style": config.get("card_style", "elevated"),
            "show_powered_by": config.get("show_powered_by", True),
            "enable_dark_mode": config.get("enable_dark_mode", True),
            "custom_css": config.get("custom_css"),
            "hero_title": config.get("hero_title"),
            "hero_subtitle": config.get("hero_subtitle"),
            "hero_image_url": config.get("hero_image_url"),
            "social_links": {
                "website": config.get("website_url"),
                "facebook": config.get("facebook_url"),
                "instagram": config.get("instagram_url"),
                "linkedin": config.get("linkedin_url"),
                "twitter": config.get("twitter_url")
            },
            "support": {
                "email": config.get("support_email"),
                "phone": config.get("support_phone")
            }
        },
        "institution": {
            "name": institution.get("institution_name", "") if institution else "",
            "slug": institution.get("institution_slug", "") if institution else ""
        },
        "is_default": False
    }

@api_router.put("/whitelabel/config")
async def update_whitelabel_config(updates: WhiteLabelUpdate, current_user: dict = Depends(get_current_user)):
    """Update white-label configuration"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user["id"]
    
    config = await db.whitelabel_configs.find_one({"institution_id": institution_id})
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found. Create one first.")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    # Validate domain uniqueness if changed
    if updates.custom_domain and updates.custom_domain != config.get("custom_domain"):
        domain_exists = await db.whitelabel_configs.find_one({"custom_domain": updates.custom_domain})
        if domain_exists:
            raise HTTPException(status_code=400, detail="Custom domain already in use")
        update_data["ssl_status"] = "pending"
        update_data["dns_verified"] = False
    
    await db.whitelabel_configs.update_one({"institution_id": institution_id}, {"$set": update_data})
    
    return {"message": "White-label configuration updated"}

@api_router.post("/whitelabel/verify-domain")
async def verify_custom_domain(current_user: dict = Depends(get_current_user)):
    """Verify custom domain DNS configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = await db.whitelabel_configs.find_one({"institution_id": current_user["id"]})
    if not config or not config.get("custom_domain"):
        raise HTTPException(status_code=400, detail="No custom domain configured")
    
    # In production, this would check DNS records
    # For now, we simulate verification
    await db.whitelabel_configs.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"dns_verified": True, "ssl_status": "active", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": "Domain verified successfully",
        "domain": config["custom_domain"],
        "dns_verified": True,
        "ssl_status": "active",
        "instructions": {
            "cname_record": f"CNAME {config['custom_domain']} -> app.proficienthub.com",
            "txt_record": f"TXT _proficienthub-verify.{config['custom_domain']} -> {current_user['id']}"
        }
    }

# ==================== CRM + ERM SUPREME SYSTEM ====================

# Email Automation Models
class EmailTemplate(BaseModel):
    name: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    category: str  # welcome, follow_up, reminder, promotion, notification
    variables: Optional[List[str]] = []  # {{name}}, {{exam_type}}, etc.

class EmailSequence(BaseModel):
    name: str
    description: Optional[str] = None
    trigger: str  # lead_created, demo_scheduled, no_activity_7d, exam_completed
    steps: List[dict]  # [{delay_days: 0, template_id: "xxx"}, ...]
    is_active: bool = True

class AutomationRule(BaseModel):
    name: str
    trigger_type: str  # lead_stage_change, inactivity, score_threshold, date_based
    trigger_config: dict
    actions: List[dict]  # [{type: "send_email", template_id: "x"}, {type: "assign_to", user_id: "y"}]
    is_active: bool = True

# Communication Models
class CommunicationLog(BaseModel):
    lead_id: Optional[str] = None
    student_id: Optional[str] = None
    channel: str  # email, whatsapp, sms, call, in_app
    direction: str  # inbound, outbound
    subject: Optional[str] = None
    content: str
    status: str = "sent"  # sent, delivered, read, failed
    metadata: Optional[dict] = None

# Lead Scoring Model
LEAD_SCORING_RULES = {
    "students_count": {"1-50": 10, "51-200": 20, "201-500": 30, "501-1000": 40, "1000+": 50},
    "exam_types_count": {"1": 5, "2-3": 15, "4+": 25},
    "source": {"referral": 30, "organic": 20, "paid_ad": 15, "cold_outreach": 5},
    "engagement": {"demo_attended": 25, "materials_downloaded": 15, "replied_email": 10},
    "stage_velocity": {"fast": 20, "normal": 10, "slow": -10}
}

@api_router.post("/crm/email-templates")
async def create_email_template(template: EmailTemplate, current_user: dict = Depends(get_current_user)):
    """Create a reusable email template"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    template_id = str(uuid.uuid4())
    template_doc = {
        "id": template_id,
        "institution_id": current_user["id"],
        **template.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "usage_count": 0
    }
    
    await db.email_templates.insert_one(template_doc)
    return {"id": template_id, "message": "Email template created"}

@api_router.get("/crm/email-templates")
async def get_email_templates(current_user: dict = Depends(get_current_user)):
    """Get all email templates"""
    templates = await db.email_templates.find({"institution_id": current_user["id"]}, {"_id": 0}).to_list(100)
    
    # Add default templates if none exist
    if not templates:
        default_templates = [
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Welcome Lead",
                "subject": "Welcome to {{platform_name}} - Let's Get Started!",
                "body_html": "<h1>Hello {{contact_name}}!</h1><p>Thank you for your interest in {{platform_name}}. We're excited to help {{institution_name}} prepare students for success.</p><p>Your dedicated account manager will reach out within 24 hours to schedule a personalized demo.</p>",
                "category": "welcome",
                "variables": ["contact_name", "institution_name", "platform_name"],
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Demo Follow-up",
                "subject": "Thanks for attending the {{platform_name}} demo!",
                "body_html": "<h1>Hi {{contact_name}},</h1><p>Thank you for taking the time to see {{platform_name}} in action!</p><p>As discussed, here's what we can offer {{institution_name}}:</p><ul><li>{{students_count}} student licenses</li><li>Access to {{exam_types}} preparation</li><li>AI Tutor included</li></ul><p>Ready to get started? Reply to this email or book a call.</p>",
                "category": "follow_up",
                "variables": ["contact_name", "institution_name", "platform_name", "students_count", "exam_types"],
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Inactivity Reminder",
                "subject": "We miss you, {{contact_name}}! 🎓",
                "body_html": "<h1>Hi {{contact_name}},</h1><p>We noticed it's been a while since we last connected about {{platform_name}} for {{institution_name}}.</p><p>Is there anything we can help clarify? Our team is here to answer any questions.</p><p>Book a quick 15-minute call: [CALENDAR_LINK]</p>",
                "category": "reminder",
                "variables": ["contact_name", "institution_name", "platform_name"],
                "is_default": True
            }
        ]
        for t in default_templates:
            await db.email_templates.insert_one(t)
        templates = default_templates
    
    return {"templates": templates}

@api_router.post("/crm/email-sequences")
async def create_email_sequence(sequence: EmailSequence, current_user: dict = Depends(get_current_user)):
    """Create an automated email sequence"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sequence_id = str(uuid.uuid4())
    sequence_doc = {
        "id": sequence_id,
        "institution_id": current_user["id"],
        **sequence.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_enrolled": 0,
        "total_completed": 0
    }
    
    await db.email_sequences.insert_one(sequence_doc)
    return {"id": sequence_id, "message": "Email sequence created"}

@api_router.get("/crm/email-sequences")
async def get_email_sequences(current_user: dict = Depends(get_current_user)):
    """Get all email sequences"""
    sequences = await db.email_sequences.find({"institution_id": current_user["id"]}).to_list(50)
    return {"sequences": sequences}

@api_router.post("/crm/automation-rules")
async def create_automation_rule(rule: AutomationRule, current_user: dict = Depends(get_current_user)):
    """Create an automation rule"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    rule_id = str(uuid.uuid4())
    rule_doc = {
        "id": rule_id,
        "institution_id": current_user["id"],
        **rule.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executions_count": 0,
        "last_executed": None
    }
    
    await db.automation_rules.insert_one(rule_doc)
    return {"id": rule_id, "message": "Automation rule created"}

@api_router.get("/crm/automation-rules")
async def get_automation_rules(current_user: dict = Depends(get_current_user)):
    """Get all automation rules"""
    rules = await db.automation_rules.find({"institution_id": current_user["id"]}, {"_id": 0}).to_list(50)
    
    # Add default rules if none exist
    if not rules:
        default_rules = [
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Welcome Email on Lead Creation",
                "trigger_type": "lead_created",
                "trigger_config": {},
                "actions": [{"type": "send_email", "template": "welcome"}],
                "is_active": True,
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "7-Day Inactivity Follow-up",
                "trigger_type": "inactivity",
                "trigger_config": {"days": 7},
                "actions": [{"type": "send_email", "template": "reminder"}, {"type": "create_task", "title": "Follow up with inactive lead"}],
                "is_active": True,
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Hot Lead Alert",
                "trigger_type": "score_threshold",
                "trigger_config": {"score": 80},
                "actions": [{"type": "notify_slack", "message": "🔥 Hot lead detected!"}, {"type": "assign_to", "role": "sales_manager"}],
                "is_active": True,
                "is_default": True
            }
        ]
        for r in default_rules:
            await db.automation_rules.insert_one(r)
        rules = default_rules
    
    return {"rules": rules}

def calculate_lead_score(lead: dict) -> dict:
    """Calculate lead score based on multiple factors"""
    score = 0
    breakdown = []
    
    # Students count score
    students = lead.get("students_count", 0)
    if students >= 1000:
        score += 50
        breakdown.append({"factor": "Large institution (1000+ students)", "points": 50})
    elif students >= 501:
        score += 40
        breakdown.append({"factor": "Medium-large institution (501-1000)", "points": 40})
    elif students >= 201:
        score += 30
        breakdown.append({"factor": "Medium institution (201-500)", "points": 30})
    elif students >= 51:
        score += 20
        breakdown.append({"factor": "Small-medium institution (51-200)", "points": 20})
    elif students >= 1:
        score += 10
        breakdown.append({"factor": "Small institution (1-50)", "points": 10})
    
    # Exam types score
    exam_count = len(lead.get("exam_types", []))
    if exam_count >= 4:
        score += 25
        breakdown.append({"factor": "Multiple exam types (4+)", "points": 25})
    elif exam_count >= 2:
        score += 15
        breakdown.append({"factor": "Multiple exam types (2-3)", "points": 15})
    elif exam_count >= 1:
        score += 5
        breakdown.append({"factor": "Single exam type", "points": 5})
    
    # Source score
    source = lead.get("source", "")
    source_scores = {"referral": 30, "organic": 20, "free_trial_form": 25, "demo_request": 25, "paid_ad": 15, "cold_outreach": 5}
    if source in source_scores:
        score += source_scores[source]
        breakdown.append({"factor": f"Lead source: {source}", "points": source_scores[source]})
    
    # Stage progression score
    stage = lead.get("stage", "new")
    stage_scores = {"new": 0, "contacted": 5, "demo_scheduled": 15, "demo_completed": 25, "proposal_sent": 35, "negotiating": 45}
    if stage in stage_scores:
        score += stage_scores[stage]
        breakdown.append({"factor": f"Pipeline stage: {stage}", "points": stage_scores[stage]})
    
    # Activity score
    activities = lead.get("activities", [])
    if len(activities) >= 5:
        score += 15
        breakdown.append({"factor": "High engagement (5+ activities)", "points": 15})
    elif len(activities) >= 2:
        score += 8
        breakdown.append({"factor": "Medium engagement (2-4 activities)", "points": 8})
    
    # Deal value score
    value = lead.get("estimated_value", 0)
    if value >= 50000:
        score += 30
        breakdown.append({"factor": "Enterprise deal ($50K+)", "points": 30})
    elif value >= 20000:
        score += 20
        breakdown.append({"factor": "Large deal ($20K+)", "points": 20})
    elif value >= 5000:
        score += 10
        breakdown.append({"factor": "Standard deal ($5K+)", "points": 10})
    
    # Cap at 100
    score = min(100, score)
    
    # Determine grade
    if score >= 80:
        grade = "A"
        label = "🔥 Hot Lead"
    elif score >= 60:
        grade = "B"
        label = "⭐ Warm Lead"
    elif score >= 40:
        grade = "C"
        label = "📊 Qualified Lead"
    elif score >= 20:
        grade = "D"
        label = "🌱 New Lead"
    else:
        grade = "F"
        label = "❄️ Cold Lead"
    
    return {
        "score": score,
        "grade": grade,
        "label": label,
        "breakdown": breakdown
    }

@api_router.get("/crm/leads/{lead_id}/score")
async def get_lead_score(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed lead scoring"""
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    scoring = calculate_lead_score(lead)
    
    # Update lead with score
    await db.crm_leads.update_one(
        {"id": lead_id},
        {"$set": {"lead_score": scoring["score"], "lead_grade": scoring["grade"]}}
    )
    
    return scoring

@api_router.post("/crm/communications")
async def log_communication(comm: CommunicationLog, current_user: dict = Depends(get_current_user)):
    """Log a communication (email, call, WhatsApp, etc.)"""
    comm_id = str(uuid.uuid4())
    comm_doc = {
        "id": comm_id,
        "institution_id": current_user["id"],
        **comm.dict(),
        "logged_by": current_user["email"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.communications.insert_one(comm_doc)
    
    # Update lead/student last contact
    if comm.lead_id:
        await db.crm_leads.update_one(
            {"id": comm.lead_id},
            {"$set": {"last_contact": datetime.now(timezone.utc).isoformat()}}
        )
    
    return {"id": comm_id, "message": "Communication logged"}

@api_router.get("/crm/communications")
async def get_communications(
    lead_id: Optional[str] = None,
    student_id: Optional[str] = None,
    channel: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get communication history"""
    query = {"institution_id": current_user["id"]}
    if lead_id:
        query["lead_id"] = lead_id
    if student_id:
        query["student_id"] = student_id
    if channel:
        query["channel"] = channel
    
    comms = await db.communications.find(query).sort("created_at", -1).to_list(200)
    
    return {"communications": comms}

# WhatsApp Integration Placeholder
@api_router.post("/crm/whatsapp/send")
async def send_whatsapp_message(
    recipient: str,
    message: str,
    lead_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Send WhatsApp message (requires WhatsApp Business API setup)"""
    # This is a placeholder - in production, integrate with WhatsApp Business API
    
    comm_doc = {
        "id": str(uuid.uuid4()),
        "institution_id": current_user["id"],
        "lead_id": lead_id,
        "channel": "whatsapp",
        "direction": "outbound",
        "content": message,
        "recipient": recipient,
        "status": "sent",  # Would be "pending" until confirmed by WhatsApp API
        "logged_by": current_user["email"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.communications.insert_one(comm_doc)
    
    return {
        "message": "WhatsApp message queued",
        "note": "WhatsApp Business API integration required for actual delivery",
        "setup_instructions": {
            "step1": "Create WhatsApp Business Account",
            "step2": "Apply for WhatsApp Business API access",
            "step3": "Configure webhook URL for incoming messages",
            "step4": "Add WHATSAPP_API_TOKEN to environment variables"
        }
    }

# Advanced Reports & Analytics
@api_router.get("/crm/reports/pipeline")
async def get_pipeline_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed pipeline analytics report"""
    query = {}
    if current_user["user_type"] == "institution":
        query["$or"] = [{"created_by": current_user["id"]}, {"assigned_to": current_user["id"]}]
    
    if date_from:
        query["created_at"] = {"$gte": date_from}
    if date_to:
        query["created_at"] = {**query.get("created_at", {}), "$lte": date_to}
    
    leads = await db.crm_leads.find(query).to_list(1000)
    
    # Pipeline metrics
    total_leads = len(leads)
    total_value = sum(l.get("estimated_value", 0) for l in leads)
    
    # By stage
    by_stage = {}
    for stage in PIPELINE_STAGES.keys():
        stage_leads = [l for l in leads if l.get("stage") == stage]
        by_stage[stage] = {
            "count": len(stage_leads),
            "value": sum(l.get("estimated_value", 0) for l in stage_leads),
            "avg_value": sum(l.get("estimated_value", 0) for l in stage_leads) / len(stage_leads) if stage_leads else 0
        }
    
    # Conversion funnel
    funnel = []
    stage_order = ["new", "contacted", "demo_scheduled", "demo_completed", "proposal_sent", "negotiating", "won"]
    for i, stage in enumerate(stage_order):
        count = len([l for l in leads if l.get("stage") == stage or stage_order.index(l.get("stage", "new")) > i])
        funnel.append({"stage": stage, "count": count, "percentage": count / total_leads * 100 if total_leads > 0 else 0})
    
    # Time to close
    won_leads = [l for l in leads if l.get("stage") == "won"]
    avg_days_to_close = 0
    if won_leads:
        total_days = 0
        for lead in won_leads:
            created = datetime.fromisoformat(lead.get("created_at", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))
            updated = datetime.fromisoformat(lead.get("updated_at", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00'))
            total_days += (updated - created).days
        avg_days_to_close = total_days / len(won_leads)
    
    # Lead sources
    by_source = {}
    for lead in leads:
        source = lead.get("source", "unknown")
        if source not in by_source:
            by_source[source] = {"count": 0, "value": 0, "won": 0}
        by_source[source]["count"] += 1
        by_source[source]["value"] += lead.get("estimated_value", 0)
        if lead.get("stage") == "won":
            by_source[source]["won"] += 1
    
    # Lead scores distribution
    score_distribution = {"hot": 0, "warm": 0, "qualified": 0, "new": 0, "cold": 0}
    for lead in leads:
        score = calculate_lead_score(lead)["score"]
        if score >= 80:
            score_distribution["hot"] += 1
        elif score >= 60:
            score_distribution["warm"] += 1
        elif score >= 40:
            score_distribution["qualified"] += 1
        elif score >= 20:
            score_distribution["new"] += 1
        else:
            score_distribution["cold"] += 1
    
    return {
        "summary": {
            "total_leads": total_leads,
            "total_pipeline_value": total_value,
            "avg_deal_size": total_value / total_leads if total_leads > 0 else 0,
            "conversion_rate": len(won_leads) / total_leads * 100 if total_leads > 0 else 0,
            "avg_days_to_close": round(avg_days_to_close, 1)
        },
        "by_stage": by_stage,
        "funnel": funnel,
        "by_source": by_source,
        "score_distribution": score_distribution
    }

@api_router.get("/crm/reports/activity")
async def get_activity_report(current_user: dict = Depends(get_current_user)):
    """Get activity and engagement report"""
    institution_id = current_user["id"]
    
    # Get all communications
    comms = await db.communications.find({"institution_id": institution_id}).to_list(1000)
    
    # By channel
    by_channel = {}
    for comm in comms:
        channel = comm.get("channel", "unknown")
        if channel not in by_channel:
            by_channel[channel] = {"total": 0, "inbound": 0, "outbound": 0}
        by_channel[channel]["total"] += 1
        by_channel[channel][comm.get("direction", "outbound")] += 1
    
    # By day of week
    by_day = {i: 0 for i in range(7)}
    for comm in comms:
        try:
            created = datetime.fromisoformat(comm.get("created_at", "").replace('Z', '+00:00'))
            by_day[created.weekday()] += 1
        except:
            pass
    
    # Response times (placeholder)
    avg_response_time = "2.5 hours"
    
    return {
        "total_communications": len(comms),
        "by_channel": by_channel,
        "by_day_of_week": {
            "Monday": by_day[0], "Tuesday": by_day[1], "Wednesday": by_day[2],
            "Thursday": by_day[3], "Friday": by_day[4], "Saturday": by_day[5], "Sunday": by_day[6]
        },
        "avg_response_time": avg_response_time
    }

@api_router.get("/crm/reports/export")
async def export_crm_data(
    format: str = "csv",  # csv, json, xlsx
    current_user: dict = Depends(get_current_user)
):
    """Export CRM data"""
    query = {}
    if current_user["user_type"] == "institution":
        query["$or"] = [{"created_by": current_user["id"]}, {"assigned_to": current_user["id"]}]
    
    leads = await db.crm_leads.find(query).to_list(10000)
    
    # Prepare export data
    export_data = []
    for lead in leads:
        scoring = calculate_lead_score(lead)
        export_data.append({
            "id": lead["id"],
            "institution_name": lead.get("institution_name", ""),
            "contact_name": lead.get("contact_name", ""),
            "email": lead.get("email", ""),
            "phone": lead.get("phone", ""),
            "country": lead.get("country", ""),
            "students_count": lead.get("students_count", 0),
            "exam_types": ", ".join(lead.get("exam_types", [])),
            "estimated_value": lead.get("estimated_value", 0),
            "stage": lead.get("stage", ""),
            "source": lead.get("source", ""),
            "lead_score": scoring["score"],
            "lead_grade": scoring["grade"],
            "created_at": lead.get("created_at", ""),
            "updated_at": lead.get("updated_at", ""),
            "activities_count": len(lead.get("activities", []))
        })
    
    if format == "json":
        return {"data": export_data, "format": "json", "count": len(export_data)}
    else:
        # For CSV, return structured data that frontend can convert
        return {
            "data": export_data,
            "format": format,
            "count": len(export_data),
            "columns": list(export_data[0].keys()) if export_data else []
        }

# Tasks & Follow-ups
@api_router.post("/crm/tasks")
async def create_task(task_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a CRM task"""
    task_id = str(uuid.uuid4())
    task_doc = {
        "id": task_id,
        "institution_id": current_user["id"],
        "title": task_data.get("title", ""),
        "description": task_data.get("description", ""),
        "type": task_data.get("type", "follow_up"),  # follow_up, call, email, meeting, demo
        "priority": task_data.get("priority", "medium"),  # low, medium, high, urgent
        "due_date": task_data.get("due_date"),
        "lead_id": task_data.get("lead_id"),
        "student_id": task_data.get("student_id"),
        "assigned_to": task_data.get("assigned_to", current_user["id"]),
        "status": "pending",  # pending, in_progress, completed, cancelled
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }
    
    await db.crm_tasks.insert_one(task_doc)
    return {"id": task_id, "message": "Task created"}

@api_router.get("/crm/tasks")
async def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks"""
    query = {"institution_id": current_user["id"]}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    
    tasks = await db.crm_tasks.find(query, {"_id": 0}).sort("due_date", 1).to_list(200)
    
    # Group by status
    overdue = []
    today = []
    upcoming = []
    completed = []
    
    now = datetime.now(timezone.utc)
    today_str = now.date().isoformat()
    
    for task in tasks:
        if task.get("status") == "completed":
            completed.append(task)
        elif task.get("due_date"):
            if task["due_date"] < today_str:
                overdue.append(task)
            elif task["due_date"] == today_str:
                today.append(task)
            else:
                upcoming.append(task)
        else:
            upcoming.append(task)
    
    return {
        "overdue": overdue,
        "today": today,
        "upcoming": upcoming,
        "completed": completed[-10:],  # Last 10 completed
        "stats": {
            "total_pending": len(overdue) + len(today) + len(upcoming),
            "overdue_count": len(overdue),
            "due_today": len(today)
        }
    }

@api_router.put("/crm/tasks/{task_id}")
async def update_task(task_id: str, updates: dict, current_user: dict = Depends(get_current_user)):
    """Update a task"""
    update_data = {}
    for key in ["title", "description", "priority", "due_date", "status", "assigned_to"]:
        if key in updates:
            update_data[key] = updates[key]
    
    if updates.get("status") == "completed":
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.crm_tasks.update_one({"id": task_id, "institution_id": current_user["id"]}, {"$set": update_data})
    return {"message": "Task updated"}

# ==================== INSTITUTION SETTINGS ====================

class InstitutionZoomSettings(BaseModel):
    zoom_account_id: str = ""
    zoom_client_id: str = ""
    zoom_client_secret: str = ""
    zoom_enabled: bool = False

class InstitutionEmailSettings(BaseModel):
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    smtp_enabled: bool = False
    smtp_use_tls: bool = True

class InstitutionGamificationSettings(BaseModel):
    gamification_enabled: bool = False
    xp_per_exam: int = 50
    xp_per_section: int = 20
    xp_per_tutor_session: int = 15
    xp_per_class: int = 30
    streak_bonus_multiplier: float = 1.5
    leaderboard_enabled: bool = True
    badges_enabled: bool = True
    challenges_enabled: bool = True
    weekly_challenges_count: int = 3

@api_router.get("/institution/settings")
async def get_institution_settings(current_user: dict = Depends(get_current_user)):
    """Get all institution settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access settings")
    
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]}, {"_id": 0})
    if not settings:
        settings = {
            "institution_id": current_user["id"],
            "zoom": {},
            "email": {},
            "gamification": {"gamification_enabled": False}
        }
    return settings

@api_router.post("/institution/settings/zoom")
async def save_zoom_settings(settings: InstitutionZoomSettings, current_user: dict = Depends(get_current_user)):
    """Save Zoom settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can modify settings")
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"zoom": settings.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Zoom settings saved"}

@api_router.post("/institution/settings/zoom/test")
async def test_zoom_connection(settings: InstitutionZoomSettings, current_user: dict = Depends(get_current_user)):
    """Test Zoom connection"""
    if not settings.zoom_client_id or not settings.zoom_client_secret:
        raise HTTPException(status_code=400, detail="Zoom credentials required")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://zoom.us/oauth/token",
                params={
                    "grant_type": "account_credentials",
                    "account_id": settings.zoom_account_id
                },
                auth=(settings.zoom_client_id, settings.zoom_client_secret),
                timeout=10.0
            )
            if response.status_code == 200:
                return {"message": "Zoom connection successful!", "status": "connected"}
            else:
                raise HTTPException(status_code=400, detail=f"Zoom API error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@api_router.post("/institution/settings/email")
async def save_email_settings(settings: InstitutionEmailSettings, current_user: dict = Depends(get_current_user)):
    """Save Email SMTP settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can modify settings")
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"email": settings.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Email settings saved"}

@api_router.post("/institution/settings/email/test")
async def test_email_connection(settings: dict, current_user: dict = Depends(get_current_user)):
    """Test email SMTP connection by sending a test email"""
    test_email = settings.get("test_email")
    if not test_email:
        raise HTTPException(status_code=400, detail="Test email address required")
    
    if not settings.get("smtp_host") or not settings.get("smtp_user"):
        raise HTTPException(status_code=400, detail="SMTP credentials required")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = f"{settings.get('smtp_from_name', 'ProficientHub')} <{settings.get('smtp_from_email', settings['smtp_user'])}>"
        msg['To'] = test_email
        msg['Subject'] = "ProficientHub - Test Email Configuration"
        
        body = """
        <h2>Email Configuration Test</h2>
        <p>If you're reading this, your email settings are configured correctly!</p>
        <p>You can now use email features in ProficientHub.</p>
        <hr>
        <p><small>This is an automated test email from ProficientHub.</small></p>
        """
        msg.attach(MIMEText(body, 'html'))
        
        if settings.get("smtp_use_tls", True):
            server = smtplib.SMTP(settings["smtp_host"], settings.get("smtp_port", 587))
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings["smtp_host"], settings.get("smtp_port", 465))
        
        server.login(settings["smtp_user"], settings["smtp_password"])
        server.send_message(msg)
        server.quit()
        
        return {"message": f"Test email sent successfully to {test_email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(e)}")

@api_router.post("/institution/settings/gamification")
async def save_gamification_settings(settings: InstitutionGamificationSettings, current_user: dict = Depends(get_current_user)):
    """Save gamification settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can modify settings")
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"gamification": settings.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Gamification settings saved"}

# ==================== GAMIFICATION SYSTEM ====================

@api_router.get("/gamification/profile")
async def get_gamification_profile(current_user: dict = Depends(get_current_user)):
    """Get student's gamification profile"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students have gamification profiles")
    
    # Check if institution has gamification enabled
    institution_id = current_user.get("institution_id")
    if institution_id:
        settings = await db.institution_settings.find_one({"institution_id": institution_id})
        if not settings or not settings.get("gamification", {}).get("gamification_enabled", False):
            return {"gamification_enabled": False}
    
    # Get or create gamification profile
    profile = await db.gamification_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not profile:
        profile = {
            "user_id": current_user["id"],
            "institution_id": institution_id,
            "xp": 0,
            "level": 1,
            "streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "daily_xp": 0,
            "badges": [],
            "challenges_completed": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.gamification_profiles.insert_one(profile)
    
    profile["gamification_enabled"] = True
    return profile

@api_router.post("/gamification/award-xp")
async def award_xp(activity_type: str, current_user: dict = Depends(get_current_user)):
    """Award XP for an activity"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can earn XP")
    
    institution_id = current_user.get("institution_id")
    settings = await db.institution_settings.find_one({"institution_id": institution_id})
    if not settings or not settings.get("gamification", {}).get("gamification_enabled", False):
        return {"message": "Gamification not enabled", "xp_earned": 0}
    
    gam_settings = settings.get("gamification", {})
    
    # Determine XP based on activity
    xp_map = {
        "exam": gam_settings.get("xp_per_exam", 50),
        "section": gam_settings.get("xp_per_section", 20),
        "tutor": gam_settings.get("xp_per_tutor_session", 15),
        "class": gam_settings.get("xp_per_class", 30)
    }
    base_xp = xp_map.get(activity_type, 10)
    
    # Get profile and update streak
    profile = await db.gamification_profiles.find_one({"user_id": current_user["id"]})
    today = datetime.now(timezone.utc).date().isoformat()
    
    streak = profile.get("streak", 0) if profile else 0
    last_activity = profile.get("last_activity_date") if profile else None
    
    # Check streak
    if last_activity:
        last_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00")).date()
        today_date = datetime.now(timezone.utc).date()
        days_diff = (today_date - last_date).days
        
        if days_diff == 1:
            streak += 1
        elif days_diff > 1:
            streak = 1
    else:
        streak = 1
    
    # Apply streak bonus
    multiplier = gam_settings.get("streak_bonus_multiplier", 1.5)
    streak_bonus = 1 + (min(streak, 30) * 0.01 * (multiplier - 1))
    final_xp = int(base_xp * streak_bonus)
    
    # Update profile
    update_data = {
        "$inc": {"xp": final_xp, "daily_xp": final_xp},
        "$set": {
            "streak": streak,
            "last_activity_date": today,
            "longest_streak": max(streak, profile.get("longest_streak", 0) if profile else 0)
        }
    }
    
    await db.gamification_profiles.update_one(
        {"user_id": current_user["id"]},
        update_data,
        upsert=True
    )
    
    # Check for badge unlocks
    badges_earned = await check_badge_unlocks(current_user["id"])
    
    return {
        "xp_earned": final_xp,
        "base_xp": base_xp,
        "streak_bonus": round(streak_bonus, 2),
        "current_streak": streak,
        "badges_earned": badges_earned
    }

async def check_badge_unlocks(user_id: str):
    """Check and award badges based on achievements"""
    profile = await db.gamification_profiles.find_one({"user_id": user_id})
    if not profile:
        return []
    
    current_badges = set(profile.get("badges", []))
    new_badges = []
    
    # Check various badge conditions
    badge_conditions = [
        ("first_exam", lambda p: True),  # First activity
        ("streak_7", lambda p: p.get("streak", 0) >= 7),
        ("streak_30", lambda p: p.get("streak", 0) >= 30),
    ]
    
    for badge_id, condition in badge_conditions:
        if badge_id not in current_badges and condition(profile):
            new_badges.append(badge_id)
            current_badges.add(badge_id)
    
    if new_badges:
        await db.gamification_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"badges": list(current_badges)}}
        )
    
    return new_badges

@api_router.get("/gamification/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user)):
    """Get institution leaderboard"""
    institution_id = current_user.get("institution_id")
    if not institution_id:
        return {"leaderboard": []}
    
    # Get top students by XP
    profiles = await db.gamification_profiles.find(
        {"institution_id": institution_id},
        {"_id": 0, "user_id": 1, "xp": 1, "level": 1, "streak": 1}
    ).sort("xp", -1).limit(50).to_list(50)
    
    # Enrich with user names
    leaderboard = []
    for i, profile in enumerate(profiles):
        user = await db.users.find_one({"id": profile["user_id"]}, {"name": 1})
        leaderboard.append({
            "rank": i + 1,
            "id": profile["user_id"],
            "name": user.get("name", "Anonymous") if user else "Anonymous",
            "xp": profile.get("xp", 0),
            "level": profile.get("level", 1),
            "streak": profile.get("streak", 0)
        })
    
    return {"leaderboard": leaderboard}

@api_router.get("/gamification/challenges")
async def get_weekly_challenges(current_user: dict = Depends(get_current_user)):
    """Get weekly challenges for the student"""
    institution_id = current_user.get("institution_id")
    
    # Sample challenges (in production, these would be generated weekly)
    challenges = [
        {
            "id": "complete_3_exams",
            "name": "Exam Master",
            "description": "Complete 3 full practice exams",
            "icon": "📝",
            "target": 3,
            "progress": 1,
            "xp_reward": 150
        },
        {
            "id": "5_day_streak",
            "name": "Consistency King",
            "description": "Maintain a 5-day study streak",
            "icon": "🔥",
            "target": 5,
            "progress": 3,
            "xp_reward": 100
        },
        {
            "id": "tutor_sessions",
            "name": "AI Learner",
            "description": "Have 5 AI tutor sessions",
            "icon": "🤖",
            "target": 5,
            "progress": 2,
            "xp_reward": 75
        }
    ]
    
    return {"challenges": challenges}

# ==================== ZOOM MEETINGS ====================

@api_router.post("/zoom/meetings/create")
async def create_zoom_meeting(
    topic: str,
    start_time: str,
    duration: int = 60,
    current_user: dict = Depends(get_current_user)
):
    """Create a Zoom meeting"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create meetings")
    
    # Get Zoom settings
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not zoom_config.get("zoom_enabled") or not zoom_config.get("zoom_client_id"):
        raise HTTPException(status_code=400, detail="Zoom not configured. Please configure Zoom in settings.")
    
    try:
        import httpx
        
        # Get access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://zoom.us/oauth/token",
                params={
                    "grant_type": "account_credentials",
                    "account_id": zoom_config["zoom_account_id"]
                },
                auth=(zoom_config["zoom_client_id"], zoom_config["zoom_client_secret"]),
                timeout=10.0
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to authenticate with Zoom")
            
            access_token = token_response.json()["access_token"]
            
            # Create meeting
            meeting_response = await client.post(
                "https://api.zoom.us/v2/users/me/meetings",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "topic": topic,
                    "type": 2,  # Scheduled meeting
                    "start_time": start_time,
                    "duration": duration,
                    "settings": {
                        "host_video": True,
                        "participant_video": True,
                        "join_before_host": False,
                        "waiting_room": True
                    }
                },
                timeout=10.0
            )
            
            if meeting_response.status_code not in [200, 201]:
                raise HTTPException(status_code=400, detail=f"Failed to create meeting: {meeting_response.text}")
            
            meeting_data = meeting_response.json()
            
            # Store meeting in database
            meeting_doc = {
                "id": str(uuid.uuid4()),
                "zoom_meeting_id": meeting_data["id"],
                "institution_id": current_user["id"],
                "topic": topic,
                "start_time": start_time,
                "duration": duration,
                "join_url": meeting_data["join_url"],
                "start_url": meeting_data["start_url"],
                "password": meeting_data.get("password", ""),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.zoom_meetings.insert_one(meeting_doc)
            
            return {
                "meeting_id": meeting_doc["id"],
                "zoom_meeting_id": meeting_data["id"],
                "join_url": meeting_data["join_url"],
                "start_url": meeting_data["start_url"],
                "password": meeting_data.get("password", "")
            }
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Zoom API error: {str(e)}")

@api_router.get("/zoom/meetings/signature")
async def get_zoom_signature(
    meeting_number: int,
    role: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Generate JWT signature for joining a Zoom meeting"""
    import jwt
    import time
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    settings = await db.institution_settings.find_one({"institution_id": institution_id})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not zoom_config.get("zoom_client_id"):
        raise HTTPException(status_code=400, detail="Zoom not configured")
    
    iat = int(time.time())
    exp = iat + 60 * 60 * 2  # 2 hours
    
    payload = {
        "appKey": zoom_config["zoom_client_id"],
        "mn": meeting_number,
        "role": role,
        "iat": iat,
        "exp": exp,
        "tokenExp": exp
    }
    
    signature = jwt.encode(
        payload,
        zoom_config["zoom_client_secret"],
        algorithm="HS256"
    )
    
    return {
        "signature": signature,
        "meeting_number": meeting_number,
        "sdk_key": zoom_config["zoom_client_id"]
    }

@api_router.get("/student/upcoming-classes")
async def get_student_upcoming_classes(current_user: dict = Depends(get_current_user)):
    """Get upcoming live classes for a student"""
    institution_id = current_user.get("institution_id")
    if not institution_id:
        return {"classes": []}
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Get upcoming video classes
    classes = await db.video_classes.find(
        {
            "institution_id": institution_id,
            "scheduled_time": {"$gte": now},
            "status": "scheduled"
        },
        {"_id": 0}
    ).sort("scheduled_time", 1).limit(10).to_list(10)
    
    # Also get Zoom meetings
    meetings = await db.zoom_meetings.find(
        {
            "institution_id": institution_id,
            "start_time": {"$gte": now}
        },
        {"_id": 0}
    ).sort("start_time", 1).limit(10).to_list(10)
    
    # Combine and format
    combined = []
    for cls in classes:
        combined.append({
            "id": cls.get("id"),
            "title": cls.get("title"),
            "instructor": cls.get("instructor", "Instructor"),
            "start_time": cls.get("scheduled_time"),
            "type": "video_class",
            "room_code": cls.get("room_code")
        })
    
    for meeting in meetings:
        combined.append({
            "id": meeting.get("id"),
            "title": meeting.get("topic"),
            "instructor": "Host",
            "start_time": meeting.get("start_time"),
            "type": "zoom",
            "join_url": meeting.get("join_url"),
            "zoom_meeting_id": meeting.get("zoom_meeting_id")
        })
    
    # Sort by start time
    combined.sort(key=lambda x: x.get("start_time", ""))
    
    return {"classes": combined[:10]}

@api_router.get("/student/profile")
async def get_student_profile(current_user: dict = Depends(get_current_user)):
    """Get student profile including exam access"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can access this")
    
    return {
        "id": current_user["id"],
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "current_exam": current_user.get("current_exam"),
        "exam_access": current_user.get("exam_access", []),
        "credits": current_user.get("credits", 0),
        "credits_used": current_user.get("credits_used", 0),
        "institution_id": current_user.get("institution_id"),
        "institution_name": current_user.get("institution_name")
    }

# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "ProficientHub API", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
