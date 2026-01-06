from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
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
    
    return TokenResponse(access_token=token, user=user_response)

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
        "descriptions": {
            "toefl": "Test of English as a Foreign Language - Academic English proficiency",
            "ielts": "International English Language Testing System - Global recognition",
            "cambridge": "Cambridge English Qualifications - Comprehensive assessment",
            "pte": "Pearson Test of English - Computer-based testing",
            "oet": "Occupational English Test - Healthcare professionals"
        }
    }

@api_router.get("/exams/{exam_type}/practice")
async def get_practice_questions(exam_type: str, section: str = "reading", current_user: dict = Depends(get_current_user)):
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    questions = generate_sample_questions(exam_type, section)
    
    return {
        "exam_type": exam_type,
        "section": section,
        "questions": questions,
        "time_limit": get_section_time_limit(exam_type, section),
        "instructions": get_section_instructions(exam_type, section)
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

# ==================== STRIPE CHECKOUT ====================

from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

stripe_api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

# ==================== PRICING ENDPOINTS ====================
# Credit tiers with detailed breakdown (internal costs hidden from clients)
CREDIT_TIERS = {
    "basic": {
        "credits": 50,
        "label": "Basic",
        "description": "Essential AI support for exam prep",
        "includes": {
            "ai_teacher_conversations": 50,
            "writing_essays_graded": 5,
            "voice_practice_minutes": 20
        },
        "internal_cost": 5.50  # INTERNAL ONLY
    },
    "medium": {
        "credits": 100,
        "label": "Medium",
        "description": "Enhanced AI with writing feedback focus",
        "includes": {
            "ai_teacher_conversations": 100,
            "writing_essays_graded": 15,
            "voice_practice_minutes": 40
        },
        "internal_cost": 12.50  # INTERNAL ONLY
    },
    "intensive": {
        "credits": 200,
        "label": "Intensive",
        "description": "Full AI immersion for maximum results",
        "includes": {
            "ai_teacher_conversations": 200,
            "writing_essays_graded": 30,
            "voice_practice_minutes": 80
        },
        "internal_cost": 25.00  # INTERNAL ONLY
    }
}

# ==================== WRITING & SPEAKING TEST PACKAGES ====================
# Institutions can purchase these separately and monetize them with their clients
# Internal AI cost per test: Writing = $0.30, Speaking = $0.40

WRITING_TEST_PACKAGES = {
    "writing_10": {"tests": 10, "price": 15.00, "price_per_test": 1.50, "internal_cost": 3.00},
    "writing_50": {"tests": 50, "price": 60.00, "price_per_test": 1.20, "internal_cost": 15.00},
    "writing_100": {"tests": 100, "price": 100.00, "price_per_test": 1.00, "internal_cost": 30.00},
    "writing_250": {"tests": 250, "price": 200.00, "price_per_test": 0.80, "internal_cost": 75.00},
    "writing_500": {"tests": 500, "price": 350.00, "price_per_test": 0.70, "internal_cost": 150.00},
    "writing_1000": {"tests": 1000, "price": 600.00, "price_per_test": 0.60, "internal_cost": 300.00},
}

SPEAKING_TEST_PACKAGES = {
    "speaking_10": {"tests": 10, "price": 20.00, "price_per_test": 2.00, "internal_cost": 4.00},
    "speaking_50": {"tests": 50, "price": 85.00, "price_per_test": 1.70, "internal_cost": 20.00},
    "speaking_100": {"tests": 100, "price": 150.00, "price_per_test": 1.50, "internal_cost": 40.00},
    "speaking_250": {"tests": 250, "price": 325.00, "price_per_test": 1.30, "internal_cost": 100.00},
    "speaking_500": {"tests": 500, "price": 550.00, "price_per_test": 1.10, "internal_cost": 200.00},
    "speaking_1000": {"tests": 1000, "price": 900.00, "price_per_test": 0.90, "internal_cost": 400.00},
}

# Dynamic unit pricing per student (price per student/month) - Basic tier base prices
# Calculated to maintain target margins after AI costs
UNIT_PRICING = {
    "tier_1": {"min": 1, "max": 10, "price_per_student": 49, "example_students": 5},
    "tier_2": {"min": 11, "max": 50, "price_per_student": 39, "example_students": 30},
    "tier_3": {"min": 51, "max": 100, "price_per_student": 32, "example_students": 75},
    "tier_4": {"min": 101, "max": 200, "price_per_student": 28, "example_students": 150},
    "tier_5": {"min": 201, "max": 500, "price_per_student": 25, "example_students": 300},
}

# Exam multipliers
EXAM_MULTIPLIERS = {
    1: 1.0,
    2: 1.4,
    3: 1.8
}

# Credit tier multipliers (for medium and intensive plans)
# Intensive has higher multiplier due to significant AI cost increase
CREDIT_TIER_MULTIPLIERS = {
    "basic": 1.0,      # 50 credits - base price
    "medium": 1.8,     # 100 credits - 80% more (covers $12.50 cost)
    "intensive": 3.2   # 200 credits - 220% more (covers $25 cost)
}

# Extra credits pricing (per credit) - varies by tier
EXTRA_CREDIT_PRICING = {
    "tier_1": 1.20,  # $1.20 per extra credit
    "tier_2": 1.00,  # $1.00 per extra credit
    "tier_3": 0.85,  # $0.85 per extra credit
    "tier_4": 0.70,  # $0.70 per extra credit
    "tier_5": 0.60,  # $0.60 per extra credit
}

def get_unit_price(num_students: int, num_exams: int = 1, credit_tier: str = "basic") -> dict:
    """Calculate unit price per student based on volume, exams, and credit tier"""
    exam_mult = EXAM_MULTIPLIERS.get(min(num_exams, 3), 1.8)
    credit_mult = CREDIT_TIER_MULTIPLIERS.get(credit_tier, 1.0)
    tier_info = CREDIT_TIERS.get(credit_tier, CREDIT_TIERS["basic"])
    
    for tier_name, tier in UNIT_PRICING.items():
        if tier["min"] <= num_students <= tier["max"]:
            base_price = tier["price_per_student"]
            final_price = round(base_price * exam_mult * credit_mult, 2)
            extra_credit_price = EXTRA_CREDIT_PRICING[tier_name]
            
            return {
                "tier": tier_name,
                "students_range": f"{tier['min']}-{tier['max']}",
                "price_per_student": final_price,
                "monthly_total": round(final_price * num_students, 2),
                "yearly_total": round(final_price * num_students * 10, 2),
                "credits_per_student": tier_info["credits"],
                "credit_tier": credit_tier,
                "credit_tier_label": tier_info["label"],
                "includes": tier_info["includes"],
                "extra_credit_price": extra_credit_price,
                "yearly_savings": "17%"
            }
    
    # For 500+ students
    return {
        "tier": "enterprise_custom",
        "students_range": "500+",
        "message": "Contact us for custom enterprise pricing",
        "price_per_student": round(22 * exam_mult * credit_mult, 2),
        "extra_credit_price": 0.50
    }

def get_pricing_tiers(num_exams: int = 1, credit_tier: str = "basic"):
    """Get all pricing tiers for display"""
    exam_mult = EXAM_MULTIPLIERS.get(min(num_exams, 3), 1.8)
    credit_mult = CREDIT_TIER_MULTIPLIERS.get(credit_tier, 1.0)
    tier_info = CREDIT_TIERS.get(credit_tier, CREDIT_TIERS["basic"])
    
    tiers = []
    for tier_name, tier in UNIT_PRICING.items():
        base_price = tier["price_per_student"]
        final_price = round(base_price * exam_mult * credit_mult, 2)
        example_students = tier["example_students"]
        extra_credit_price = EXTRA_CREDIT_PRICING[tier_name]
        
        tiers.append({
            "id": tier_name,
            "name": f"{tier['min']}-{tier['max']} Students",
            "students_min": tier["min"],
            "students_max": tier["max"],
            "price_per_student": final_price,
            "credits_per_student": tier_info["credits"],
            "credit_tier": credit_tier,
            "includes": tier_info["includes"],
            "extra_credit_price": extra_credit_price,
            "example": {
                "students": example_students,
                "monthly": round(final_price * example_students, 2),
                "yearly": round(final_price * example_students * 10, 2)
            },
            "features": get_tier_features(tier_name, num_exams, credit_tier)
        })
    
    return tiers

def get_tier_features(tier_name: str, num_exams: int, credit_tier: str) -> list:
    """Get features for each tier"""
    exam_text = f"{num_exams} exam{'s' if num_exams > 1 else ''}" if num_exams < 3 else "All 5 exams"
    tier_info = CREDIT_TIERS.get(credit_tier, CREDIT_TIERS["basic"])
    
    base_features = [
        exam_text,
        f"{tier_info['includes']['ai_teacher_conversations']} AI Teacher sessions",
        f"{tier_info['includes']['writing_essays_graded']} Writing reviews",
        f"{tier_info['includes']['voice_practice_minutes']} min Voice practice"
    ]
    
    if credit_tier == "intensive":
        base_features.append("Priority AI processing")
    
    if tier_name in ["tier_2", "tier_3", "tier_4", "tier_5"]:
        base_features.append("Premium Analytics")
    
    if tier_name in ["tier_3", "tier_4", "tier_5"]:
        base_features.append("Risk Prediction")
    
    if tier_name in ["tier_4", "tier_5"]:
        base_features.extend(["Video Classes", "Library 50GB"])
    
    if tier_name == "tier_5":
        base_features.extend(["White-label", "API Access"])
    
    return base_features

@api_router.get("/pricing/calculate")
async def calculate_pricing(students: int, exams: int = 1, credit_tier: str = "basic"):
    """Calculate exact pricing for specific configuration"""
    return get_unit_price(students, exams, credit_tier)

@api_router.get("/pricing/tiers")
async def get_pricing_tiers_endpoint(exams: int = 1, credit_tier: str = "basic"):
    """Get all pricing tiers for display"""
    tier_info = CREDIT_TIERS.get(credit_tier, CREDIT_TIERS["basic"])
    return {
        "exams_selected": exams,
        "exam_multiplier": EXAM_MULTIPLIERS.get(min(exams, 3), 1.8),
        "credit_tier": credit_tier,
        "credit_tier_info": tier_info,
        "credit_tiers_available": {k: {
            "credits": v["credits"],
            "label": v["label"],
            "description": v["description"],
            "includes": v["includes"]
        } for k, v in CREDIT_TIERS.items()},
        "tiers": get_pricing_tiers(exams, credit_tier),
        "extra_credits_info": {
            "description": "Additional credits can be purchased at tier-specific rates",
            "pricing": EXTRA_CREDIT_PRICING
        }
    }

@api_router.get("/pricing/credit-tiers")
async def get_credit_tiers():
    """Get available credit tier options"""
    return {
        "tiers": {k: {
            "credits": v["credits"],
            "label": v["label"],
            "description": v["description"],
            "includes": v["includes"]
        } for k, v in CREDIT_TIERS.items()},
        "multipliers": CREDIT_TIER_MULTIPLIERS
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
    
    return {
        "total_users": total_users,
        "total_institutions": total_institutions,
        "total_students": total_students,
        "total_exam_attempts": total_exams,
        "total_library_items": total_library_items
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
