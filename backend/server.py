from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, BackgroundTasks
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
from bson import ObjectId
import stripe

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
    user_type: str = Field(default="individual")  # institution, individual, student, admin

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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class InstitutionSettings(BaseModel):
    name: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#3b82f6"
    exams_enabled: List[str] = []
    max_students: int = 100

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

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    max_students: int
    exams_included: List[str]

class ROICalculatorInput(BaseModel):
    current_students: int
    current_teachers: int
    current_pass_rate: float
    current_no_show_rate: float

class ROICalculatorResult(BaseModel):
    additional_students: int
    improved_pass_rate: float
    reduced_no_show_rate: float
    estimated_revenue_increase: float
    teacher_time_saved_hours: float

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
        subscription_plan=None
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
        subscription_plan=user.get("subscription_plan")
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
        subscription_plan=current_user.get("subscription_plan")
    )

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
    
    # Get exam attempts
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
    
    # Sample practice questions based on exam type and section
    questions = generate_sample_questions(exam_type, section)
    
    return {
        "exam_type": exam_type,
        "section": section,
        "questions": questions,
        "time_limit": get_section_time_limit(exam_type, section),
        "instructions": get_section_instructions(exam_type, section)
    }

def generate_sample_questions(exam_type: str, section: str) -> List[Dict]:
    """Generate sample practice questions"""
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
    elif section == "listening":
        return [
            {
                "id": "l1",
                "type": "fill_blank",
                "audio_url": "/audio/sample_lecture.mp3",
                "transcript": "The lecture discusses how renewable energy sources are becoming more cost-effective. Solar panel efficiency has increased by ___ percent over the last decade.",
                "question": "Fill in the blank based on the audio.",
                "correct_answer": "40"
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
    """Get time limit in minutes for each section"""
    time_limits = {
        "toefl": {"reading": 54, "listening": 41, "speaking": 17, "writing": 50},
        "ielts": {"reading": 60, "listening": 30, "speaking": 14, "writing": 60},
        "cambridge": {"reading": 90, "writing": 90, "listening": 40, "speaking": 15, "use_of_english": 75},
        "pte": {"speaking_writing": 77, "reading": 32, "listening": 45},
        "oet": {"reading": 60, "listening": 45, "speaking": 20, "writing": 45}
    }
    return time_limits.get(exam_type, {}).get(section, 60)

def get_section_instructions(exam_type: str, section: str) -> str:
    """Get instructions for each section"""
    return f"Complete the {section} section of the {exam_type.upper()} exam. Read each question carefully and manage your time wisely."

@api_router.post("/exams/submit", response_model=ExamAttemptResponse)
async def submit_exam_attempt(attempt: ExamAttemptCreate, current_user: dict = Depends(get_current_user)):
    # Calculate score based on answers
    score = calculate_score(attempt.answers)
    
    # Generate AI feedback
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
    
    # Update user progress
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
    """Calculate score based on answers"""
    if not answers:
        return 0.0
    correct = sum(1 for a in answers if a.get("is_correct", False))
    return round((correct / len(answers)) * 100, 1)

async def generate_ai_feedback(exam_type: str, section: str, answers: List[Dict], score: float) -> str:
    """Generate AI-powered feedback using OpenAI via Emergent"""
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
    """Update user's progress and risk metrics"""
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
    
    # Calculate risk and pass probability
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
        
        # Save conversation
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

# ==================== SUBSCRIPTION/PRICING ENDPOINTS ====================

PRICING_PLANS = [
    {
        "id": "starter",
        "name": "Starter",
        "price_monthly": 49,
        "price_yearly": 470,
        "features": ["1 exam type", "Up to 50 students", "Basic analytics", "Email support"],
        "max_students": 50,
        "exams_included": ["ielts"]
    },
    {
        "id": "professional",
        "name": "Professional",
        "price_monthly": 149,
        "price_yearly": 1430,
        "features": ["3 exam types", "Up to 200 students", "Advanced analytics", "AI tutoring", "Priority support"],
        "max_students": 200,
        "exams_included": ["ielts", "toefl", "cambridge"]
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price_monthly": 399,
        "price_yearly": 3830,
        "features": ["All exam types", "Unlimited students", "Premium analytics", "AI tutoring", "Dedicated support", "Custom branding"],
        "max_students": 10000,
        "exams_included": ["ielts", "toefl", "cambridge", "pte", "oet"]
    }
]

INDIVIDUAL_PLANS = [
    {
        "id": "single_exam",
        "name": "Single Exam",
        "price_monthly": 19,
        "price_yearly": 180,
        "features": ["1 exam type", "Unlimited practice", "AI feedback", "Progress tracking"],
        "exams_included": ["choice_of_one"]
    },
    {
        "id": "all_access",
        "name": "All Access",
        "price_monthly": 39,
        "price_yearly": 374,
        "features": ["All exam types", "Unlimited practice", "AI tutoring", "Speaking practice", "Priority support"],
        "exams_included": ["all"]
    }
]

@api_router.get("/pricing/institutional")
async def get_institutional_pricing():
    return {"plans": PRICING_PLANS}

@api_router.get("/pricing/individual")
async def get_individual_pricing():
    return {"plans": INDIVIDUAL_PLANS}

@api_router.post("/pricing/calculate-roi")
async def calculate_roi(input_data: ROICalculatorInput):
    # ROI calculation logic
    additional_students = int(input_data.current_students * 0.3)  # 30% more capacity
    improved_pass_rate = min(0.95, input_data.current_pass_rate + 0.15)  # 15% improvement
    reduced_no_show = max(0.02, input_data.current_no_show_rate - 0.12)  # 12% reduction
    
    # Revenue calculations (assuming $500 per student exam fee)
    current_revenue = input_data.current_students * 500 * input_data.current_pass_rate
    new_revenue = (input_data.current_students + additional_students) * 500 * improved_pass_rate
    revenue_increase = new_revenue - current_revenue
    
    # Teacher time saved (hours per week)
    time_saved = input_data.current_teachers * 8  # 8 hours per teacher per week
    
    return ROICalculatorResult(
        additional_students=additional_students,
        improved_pass_rate=round(improved_pass_rate * 100, 1),
        reduced_no_show_rate=round(reduced_no_show * 100, 1),
        estimated_revenue_increase=round(revenue_increase, 2),
        teacher_time_saved_hours=time_saved
    )

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
            "features_enabled": ["ai_tutor", "speaking_test", "analytics"]
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
    
    return {
        "total_users": total_users,
        "total_institutions": total_institutions,
        "total_students": total_students,
        "total_exam_attempts": total_exams
    }

# ==================== STRIPE ENDPOINTS ====================

@api_router.post("/stripe/create-checkout")
async def create_checkout_session(plan_id: str, billing_cycle: str = "monthly", current_user: dict = Depends(get_current_user)):
    try:
        # Find the plan
        all_plans = PRICING_PLANS + INDIVIDUAL_PLANS
        plan = next((p for p in all_plans if p["id"] == plan_id), None)
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        price = plan["price_monthly"] if billing_cycle == "monthly" else plan["price_yearly"]
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"ProficientHub - {plan['name']}"},
                    "unit_amount": int(price * 100),
                    "recurring": {"interval": "month" if billing_cycle == "monthly" else "year"}
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/dashboard?success=true",
            cancel_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/pricing?canceled=true",
            metadata={"user_id": current_user["id"], "plan_id": plan_id}
        )
        
        return {"checkout_url": session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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
