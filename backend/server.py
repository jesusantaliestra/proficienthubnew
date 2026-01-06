from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
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

EXAM_TYPES = ["toefl", "ielts", "cambridge", "pte", "oet"]
EXAM_SECTIONS = {
    "toefl": ["reading", "listening", "speaking", "writing"],
    "ielts": ["reading", "listening", "speaking", "writing"],
    "cambridge": ["reading", "writing", "listening", "speaking", "use_of_english"],
    "pte": ["speaking_writing", "reading", "listening"],
    "oet": ["reading", "listening", "speaking", "writing"]
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
            "pte": "Pearson Test of English - Computer-based testing",
            "oet": "Occupational English Test - Healthcare professionals"
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
# COSTOS INTERNOS REALES (basados en OpenAI/ElevenLabs pricing 2025)
# NO EXPONER ESTOS COSTOS AL CLIENTE

# Costos por tipo de examen (Mock Test completo: Speaking + Writing + Corrección)
EXAM_COSTS = {
    "toefl": {
        "speaking_minutes": 17,
        "writing_tasks": 1,
        "internal_cost": 1.70,  # $1.39 speaking + $0.26 writing + $0.05 correction
        "description": "TOEFL iBT - Academic English"
    },
    "ielts": {
        "speaking_minutes": 14,
        "writing_tasks": 1,
        "internal_cost": 1.56,  # $1.25 speaking + $0.26 writing + $0.05 correction
        "description": "IELTS Academic/General"
    },
    "cambridge": {
        "speaking_minutes": 15,
        "writing_tasks": 2,
        "internal_cost": 1.90,  # $1.30 speaking + $0.52 writing + $0.08 correction
        "description": "Cambridge C1/C2 Advanced"
    },
    "pte": {
        "speaking_minutes": 20,  # combined speaking-writing
        "writing_tasks": 1,
        "internal_cost": 1.76,  # $1.45 speaking + $0.26 writing + $0.05 correction
        "description": "PTE Academic"
    },
    "oet": {
        "speaking_minutes": 20,
        "writing_tasks": 1,
        "internal_cost": 1.91,  # $1.50 speaking (medical) + $0.35 writing + $0.06 correction
        "description": "OET - Healthcare Professionals"
    }
}

# Costo promedio por Mock Test = $1.77
AVG_MOCK_TEST_COST = 1.77

# Costos individuales de tests
INDIVIDUAL_TEST_COSTS = {
    "writing": 0.26,    # AI grading + basic feedback
    "speaking": 1.39,   # STT ($0.90) + AI eval ($0.01) + TTS feedback ($0.48)
    "ai_tutor_per_min_voice": 0.18,    # STT + GPT + TTS
    "ai_tutor_per_min_text": 0.004,    # Solo GPT
    "ai_tutor_per_min_mixed": 0.10     # Promedio mixto
}

# ==================== PAQUETES DE EXÁMENES ====================
# Estructura: paquetes de mock tests con/sin AI tutor

EXAM_PACKAGES = {
    # STARTER - 20 exámenes (70% margen)
    "starter_20": {
        "mock_tests": 20,
        "ai_tutor_minutes": 0,
        "internal_cost": 35.40,  # 20 × $1.77
        "price": 118.00,
        "margin": 0.70,
        "description": "20 Mock Tests - Sin AI Tutor",
        "features": ["20 mock tests completos", "Speaking con AI grading", "Writing con feedback", "Reading & Listening"]
    },
    "starter_20_ai": {
        "mock_tests": 20,
        "ai_tutor_minutes": 60,
        "internal_cost": 41.40,  # 35.40 + (60 × $0.10)
        "price": 138.00,
        "margin": 0.70,
        "description": "20 Mock Tests + 60 min AI Tutor",
        "features": ["20 mock tests completos", "60 min AI Tutor con voz", "Speaking con AI grading", "Writing con feedback"]
    },
    
    # GROWTH - 40 exámenes (80% margen)
    "growth_40": {
        "mock_tests": 40,
        "ai_tutor_minutes": 0,
        "internal_cost": 70.80,  # 40 × $1.77
        "price": 354.00,
        "margin": 0.80,
        "description": "40 Mock Tests - Sin AI Tutor",
        "features": ["40 mock tests completos", "Speaking con AI grading", "Writing con feedback", "Analytics básico"]
    },
    "growth_40_ai": {
        "mock_tests": 40,
        "ai_tutor_minutes": 150,
        "internal_cost": 85.80,  # 70.80 + (150 × $0.10)
        "price": 429.00,
        "margin": 0.80,
        "description": "40 Mock Tests + 150 min AI Tutor",
        "features": ["40 mock tests completos", "150 min AI Tutor con voz", "Analytics avanzado", "Soporte prioritario"]
    },
    
    # SCALE - 100 exámenes (90% margen)
    "scale_100": {
        "mock_tests": 100,
        "ai_tutor_minutes": 0,
        "internal_cost": 177.00,  # 100 × $1.77
        "price": 1770.00,
        "margin": 0.90,
        "description": "100 Mock Tests - Sin AI Tutor",
        "features": ["100 mock tests completos", "White-label portal", "Analytics completo", "API access"]
    },
    "scale_100_ai": {
        "mock_tests": 100,
        "ai_tutor_minutes": 500,
        "internal_cost": 227.00,  # 177 + (500 × $0.10)
        "price": 2270.00,
        "margin": 0.90,
        "description": "100 Mock Tests + 500 min AI Tutor",
        "features": ["100 mock tests completos", "500 min AI Tutor con voz", "White-label completo", "API + Webhooks"]
    }
}

# ==================== PAQUETES SEPARADOS WRITING & SPEAKING ====================
# Para instituciones que quieren comprar tests individuales para reventa

WRITING_TEST_PACKAGES = {
    "writing_20": {"tests": 20, "price": 21.00, "price_per_test": 1.05, "internal_cost": 5.20, "margin": 0.75},
    "writing_50": {"tests": 50, "price": 65.00, "price_per_test": 1.30, "internal_cost": 13.00, "margin": 0.80},
    "writing_100": {"tests": 100, "price": 173.00, "price_per_test": 1.73, "internal_cost": 26.00, "margin": 0.85},
}

SPEAKING_TEST_PACKAGES = {
    "speaking_20": {"tests": 20, "price": 111.00, "price_per_test": 5.55, "internal_cost": 27.80, "margin": 0.75},
    "speaking_50": {"tests": 50, "price": 348.00, "price_per_test": 6.96, "internal_cost": 69.50, "margin": 0.80},
    "speaking_100": {"tests": 100, "price": 927.00, "price_per_test": 9.27, "internal_cost": 139.00, "margin": 0.85},
}

# ==================== ADD-ONS ====================
AI_TUTOR_ADDONS = {
    "tutor_30min": {"minutes": 30, "price": 15.00, "internal_cost": 3.00},
    "tutor_100min": {"minutes": 100, "price": 45.00, "internal_cost": 10.00},
    "tutor_300min": {"minutes": 300, "price": 120.00, "internal_cost": 30.00},
}

# ==================== NUEVAS FUNCIONES DE PRICING ====================

@api_router.get("/pricing/exam-packages")
async def get_exam_packages():
    """Get all exam packages with pricing"""
    packages = []
    for pkg_id, pkg in EXAM_PACKAGES.items():
        packages.append({
            "id": pkg_id,
            "mock_tests": pkg["mock_tests"],
            "ai_tutor_minutes": pkg["ai_tutor_minutes"],
            "price": pkg["price"],
            "price_per_test": round(pkg["price"] / pkg["mock_tests"], 2),
            "has_ai_tutor": pkg["ai_tutor_minutes"] > 0,
            "description": pkg["description"],
            "features": pkg["features"],
            "margin": f"{int(pkg['margin'] * 100)}%"
        })
    return {
        "packages": packages,
        "exam_types": list(EXAM_COSTS.keys()),
        "exam_details": {k: {"description": v["description"]} for k, v in EXAM_COSTS.items()}
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

@api_router.get("/pricing/roi-calculator")
async def calculate_roi(
    package_id: str,
    num_students: int,
    price_per_student: float = 60.0
):
    """Calculate ROI for institutions"""
    if package_id not in EXAM_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    pkg = EXAM_PACKAGES[package_id]
    
    # Institution costs
    package_cost = pkg["price"]
    cost_per_student = package_cost / num_students
    tests_per_student = pkg["mock_tests"] / num_students
    tutor_mins_per_student = pkg["ai_tutor_minutes"] / num_students
    
    # Institution revenue
    revenue = price_per_student * num_students
    profit = revenue - package_cost
    roi_percentage = (profit / package_cost) * 100 if package_cost > 0 else 0
    
    return {
        "package": {
            "id": package_id,
            "description": pkg["description"],
            "mock_tests": pkg["mock_tests"],
            "ai_tutor_minutes": pkg["ai_tutor_minutes"],
            "price": package_cost
        },
        "students": num_students,
        "per_student": {
            "your_cost": round(cost_per_student, 2),
            "your_price": price_per_student,
            "your_margin": round(((price_per_student - cost_per_student) / price_per_student) * 100, 1),
            "mock_tests": round(tests_per_student, 1),
            "ai_tutor_minutes": round(tutor_mins_per_student, 1)
        },
        "totals": {
            "your_investment": package_cost,
            "your_revenue": revenue,
            "your_profit": round(profit, 2),
            "roi_percentage": round(roi_percentage, 1)
        },
        "recommendation": get_roi_recommendation(roi_percentage, num_students, tests_per_student)
    }

def get_roi_recommendation(roi: float, students: int, tests_per_student: float) -> str:
    if tests_per_student < 1:
        return "⚠️ Considera un paquete más pequeño o más estudiantes para mejor aprovechamiento"
    if roi > 200:
        return "🚀 Excelente ROI! Margen muy saludable para tu negocio"
    if roi > 100:
        return "✅ Buen ROI. Tienes margen para ofertas o servicios adicionales"
    if roi > 50:
        return "👍 ROI aceptable. Considera aumentar precio o agregar servicios premium"
    return "⚡ ROI bajo. Evalúa aumentar estudiantes o ajustar precios"

@api_router.get("/pricing/exam-costs")
async def get_exam_cost_breakdown():
    """Get detailed cost breakdown per exam type (for internal use)"""
    return {
        "exam_costs": {
            k: {
                "description": v["description"],
                "speaking_minutes": v["speaking_minutes"],
                "writing_tasks": v["writing_tasks"]
            } for k, v in EXAM_COSTS.items()
        },
        "average_mock_test_cost_display": f"${AVG_MOCK_TEST_COST}",
        "individual_test_costs_display": {
            "writing_test": f"${INDIVIDUAL_TEST_COSTS['writing']}",
            "speaking_test": f"${INDIVIDUAL_TEST_COSTS['speaking']}",
            "ai_tutor_per_minute": f"${INDIVIDUAL_TEST_COSTS['ai_tutor_per_min_mixed']}"
        }
    }

@api_router.get("/pricing/institutional")
async def get_institutional_pricing(exam_count: int = 1, credit_tier: str = "basic"):
    """Get institutional pricing"""
    return {
        "pricing_model": "per_student",
        "credit_tier": credit_tier,
        "tiers": get_pricing_tiers(exam_count, credit_tier),
        "exam_multipliers": EXAM_MULTIPLIERS,
        "credit_tiers": {k: {
            "credits": v["credits"],
            "label": v["label"],
            "description": v["description"],
            "includes": v["includes"]
        } for k, v in CREDIT_TIERS.items()}
    }

# ==================== WRITING & SPEAKING PACKAGES ENDPOINTS ====================

@api_router.get("/pricing/test-packages")
async def get_test_packages():
    """Get available writing and speaking test packages for institutions"""
    writing_packages = []
    for pkg_id, pkg in WRITING_TEST_PACKAGES.items():
        writing_packages.append({
            "id": pkg_id,
            "tests": pkg["tests"],
            "price": pkg["price"],
            "price_per_test": pkg["price_per_test"],
            "type": "writing",
            "description": f"{pkg['tests']} AI-graded writing tests with detailed feedback"
        })
    
    speaking_packages = []
    for pkg_id, pkg in SPEAKING_TEST_PACKAGES.items():
        speaking_packages.append({
            "id": pkg_id,
            "tests": pkg["tests"],
            "price": pkg["price"],
            "price_per_test": pkg["price_per_test"],
            "type": "speaking",
            "description": f"{pkg['tests']} AI-powered speaking tests with pronunciation feedback"
        })
    
    return {
        "writing_packages": writing_packages,
        "speaking_packages": speaking_packages,
        "monetization_info": {
            "description": "Institutions can resell these tests to recover subscription costs",
            "suggested_markup": "2x-3x for profit",
            "example": "Buy 100 writing tests at $1.00/test, sell at $3.00/test = $200 profit"
        }
    }

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
            # Use largest package, may need multiple
            largest = WRITING_TEST_PACKAGES["writing_1000"]
            num_packs = (tests + 999) // 1000
            return largest["price"] * num_packs, largest["price_per_test"], "writing_1000"
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
            largest = SPEAKING_TEST_PACKAGES["speaking_1000"]
            num_packs = (tests + 999) // 1000
            return largest["price"] * num_packs, largest["price_per_test"], "speaking_1000"
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
    """Create Stripe checkout session for subscription"""
    try:
        # Calculate price server-side
        pricing = get_unit_price(request.students, request.exams, request.credit_tier)
        
        if "message" in pricing:  # Enterprise custom
            raise HTTPException(status_code=400, detail="Contact sales for enterprise pricing")
        
        price = pricing["price_per_student"]
        if request.billing_cycle == "yearly":
            # 10 months for the price of 12 (17% discount)
            amount = price * request.students * 10
        else:
            amount = price * request.students
        
        # Initialize Stripe checkout
        webhook_url = f"{str(http_request.base_url).rstrip('/')}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build URLs
        success_url = f"{request.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/pricing"
        
        # Metadata for tracking
        metadata = {
            "type": "subscription",
            "students": str(request.students),
            "exams": str(request.exams),
            "credit_tier": request.credit_tier,
            "billing_cycle": request.billing_cycle,
            "price_per_student": str(price)
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
    """Individual learner pricing"""
    return {
        "plans": [
            {
                "id": "single_exam",
                "name": "Single Exam",
                "price_monthly": 39,
                "price_yearly": 390,
                "credits": 50,
                "extra_credit_price": 1.20,
                "includes": CREDIT_TIERS["basic"]["includes"],
                "features": ["1 exam type", "50 AI Teacher sessions", "5 Writing reviews", "20 min Voice"]
            },
            {
                "id": "multi_exam",
                "name": "Two Exams", 
                "price_monthly": 59,
                "price_yearly": 590,
                "credits": 100,
                "extra_credit_price": 1.00,
                "includes": CREDIT_TIERS["medium"]["includes"],
                "features": ["2 exam types", "100 AI Teacher sessions", "15 Writing reviews", "40 min Voice"]
            },
            {
                "id": "all_access",
                "name": "All Exams - Intensive",
                "price_monthly": 99,
                "price_yearly": 990,
                "credits": 200,
                "extra_credit_price": 0.85,
                "includes": CREDIT_TIERS["intensive"]["includes"],
                "features": ["All 5 exam types", "200 AI Teacher sessions", "30 Writing reviews", "80 min Voice"]
            }
        ]
    }

# Admin-only endpoint for internal cost analysis
@api_router.get("/admin/pricing-analysis")
async def get_pricing_analysis(current_user: dict = Depends(get_current_user)):
    """Internal pricing analysis - ADMIN ONLY"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analysis = []
    for tier_name, tier in UNIT_PRICING.items():
        for credit_tier_name, credit_mult in CREDIT_TIER_MULTIPLIERS.items():
            ai_cost = CREDIT_TIERS[credit_tier_name]["internal_cost"]
            price = tier["price_per_student"] * credit_mult
            margin = round((price - ai_cost) / price * 100, 1)
            
            analysis.append({
                "tier": tier_name,
                "students_range": f"{tier['min']}-{tier['max']}",
                "credit_tier": credit_tier_name,
                "credits": CREDIT_TIERS[credit_tier_name]["credits"],
                "ai_cost_per_student": ai_cost,
                "price_per_student": round(price, 2),
                "margin_percentage": margin
            })
    
    return {
        "credit_tier_costs": {k: v["internal_cost"] for k, v in CREDIT_TIERS.items()},
        "analysis": analysis,
        "note": "This data is internal only - never expose to clients"
    }

@api_router.post("/pricing/calculate-roi")
async def calculate_roi(
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
