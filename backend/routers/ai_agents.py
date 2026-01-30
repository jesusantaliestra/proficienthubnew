"""
AI Agents Configuration & Orchestration Router
Configurable multi-agent AI tutoring system with LLM abstraction layer.
Supports: GPT-4, Claude Opus, Gemini - easily switchable per academy.
Avatar tiers: Basic (Rive) | Premium (HeyGen)
Voice: ElevenLabs
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid
import os
import json

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

# Database connection
client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'proficienthub-secret-key')
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==================== LLM ABSTRACTION LAYER ====================

class LLMProvider(str, Enum):
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT4O = "openai_gpt4o"
    CLAUDE_OPUS = "claude_opus"
    CLAUDE_SONNET = "claude_sonnet"
    GEMINI_PRO = "gemini_pro"
    GEMINI_FLASH = "gemini_flash"

class AvatarTier(str, Enum):
    NONE = "none"
    BASIC = "basic"  # Rive 2D animated
    PREMIUM = "premium"  # HeyGen realistic video

class AgentType(str, Enum):
    MOCK_COACH = "mock_coach"  # Mock Exam Coach
    EXAM_TUTOR = "exam_tutor"  # Exam-specific tutor
    STUDY_PLANNER = "study_planner"  # Agent Planner

# Default agent personalities and prompts
DEFAULT_AGENT_CONFIGS = {
    "mock_coach": {
        "default_name": "Mock Coach",
        "default_personality": "Expert exam strategy coach. Helps students understand exam format, time management, and test-taking techniques.",
        "system_prompt_template": """You are {agent_name}, a professional exam coach specializing in {exam_type}.
Your role is to help students with:
- Exam format and structure understanding
- Time management strategies
- Test-taking techniques and tips
- Stress management during exams
- Identifying common pitfalls

Exam context: {exam_context}
Academy materials: {academy_materials}

Respond in the student's language. Be encouraging but realistic. Focus on actionable advice."""
    },
    "exam_tutor": {
        "default_name": "Exam Tutor",
        "default_personality": "Expert tutor for the specific exam content. Deep knowledge of all sections and question types.",
        "system_prompt_template": """You are {agent_name}, an expert tutor for {exam_type}.
Your role is to:
- Explain concepts and content for all exam sections
- Answer questions about {exam_type} topics
- Provide practice exercises and explanations
- Give feedback on student responses
- Help improve language skills specific to {exam_type}

Exam context: {exam_context}
Academy materials: {academy_materials}
Student profile: {student_profile}

Be patient and thorough. Use examples from real exam questions. Adapt to the student's level."""
    },
    "study_planner": {
        "default_name": "Study Planner",
        "default_personality": "Intelligent study planning assistant. Creates personalized study schedules based on exam date and student goals.",
        "system_prompt_template": """You are {agent_name}, a study planning assistant for {exam_type} preparation.
Your role is to:
- Create personalized study schedules
- Track student progress and adjust plans
- Recommend focus areas based on weaknesses
- Set realistic goals and milestones
- Motivate and keep students on track

Student exam date: {exam_date}
Student target score: {target_score}
Current performance: {current_performance}
Academy materials available: {academy_materials}

Create specific, actionable plans. Be realistic about time requirements. Celebrate progress."""
    }
}

# ==================== MODELS ====================

class AgentConfig(BaseModel):
    agent_type: AgentType
    is_enabled: bool = True
    custom_name: Optional[str] = None
    custom_personality: Optional[str] = None
    avatar_tier: AvatarTier = AvatarTier.BASIC
    # LLM is set at platform level by ProficientHub, not by academies
    voice_id: Optional[str] = None  # ElevenLabs voice ID
    heygen_avatar_id: Optional[str] = None  # For premium tier

class AIConfigUpdate(BaseModel):
    ai_tutor_enabled: bool = True
    agents: List[AgentConfig]
    # LLM selection removed - only ProficientHub admin can set this
    default_avatar_tier: AvatarTier = AvatarTier.BASIC
    elevenlabs_voice_id: Optional[str] = None
    heygen_avatar_id: Optional[str] = None
    custom_knowledge_base: Optional[str] = None  # Academy-specific content

# Platform-level LLM config (only ProficientHub admin)
class PlatformLLMConfig(BaseModel):
    default_llm: LLMProvider = LLMProvider.OPENAI_GPT4
    fallback_llm: LLMProvider = LLMProvider.GEMINI_FLASH

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str] = None

class AgentChatRequest(BaseModel):
    agent_type: AgentType
    message: str
    session_id: Optional[str] = None
    include_voice: bool = False
    include_avatar: bool = False

class ExamFeedbackRequest(BaseModel):
    attempt_id: str
    answers: Dict[str, Any]
    exam_type: str
    section: Optional[str] = None

# ==================== INSTITUTION AI CONFIGURATION ====================

@router.get("/config")
async def get_ai_config(current_user: dict = Depends(get_current_user)):
    """Get AI agents configuration for institution"""
    if current_user["user_type"] == "institution":
        institution_id = current_user["id"]
    elif current_user["user_type"] == "student":
        institution_id = current_user.get("institution_id")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = await db.ai_agent_configs.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        # Return default config
        config = {
            "institution_id": institution_id,
            "ai_tutor_enabled": True,
            "agents": [
                {
                    "agent_type": "mock_coach",
                    "is_enabled": True,
                    "custom_name": "Mock Coach",
                    "avatar_tier": "basic",
                    "llm_provider": "openai_gpt4"
                },
                {
                    "agent_type": "exam_tutor",
                    "is_enabled": True,
                    "custom_name": "Exam Tutor",
                    "avatar_tier": "basic",
                    "llm_provider": "openai_gpt4"
                },
                {
                    "agent_type": "study_planner",
                    "is_enabled": True,
                    "custom_name": "Study Planner",
                    "avatar_tier": "basic",
                    "llm_provider": "openai_gpt4"
                }
            ],
            "default_llm": "openai_gpt4",
            "default_avatar_tier": "basic",
            "llm_options": [e.value for e in LLMProvider],
            "avatar_options": [e.value for e in AvatarTier]
        }
    
    # Add available options
    config["llm_options"] = [e.value for e in LLMProvider]
    config["avatar_options"] = [e.value for e in AvatarTier]
    config["agent_types"] = [e.value for e in AgentType]
    
    return config

@router.put("/config")
async def update_ai_config(config: AIConfigUpdate, current_user: dict = Depends(get_current_user)):
    """Update AI agents configuration - Institution only"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can configure AI agents")
    
    config_doc = {
        "institution_id": current_user["id"],
        "ai_tutor_enabled": config.ai_tutor_enabled,
        "agents": [a.dict() for a in config.agents],
        "default_llm": config.default_llm.value,
        "default_avatar_tier": config.default_avatar_tier.value,
        "elevenlabs_voice_id": config.elevenlabs_voice_id,
        "heygen_avatar_id": config.heygen_avatar_id,
        "custom_knowledge_base": config.custom_knowledge_base,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ai_agent_configs.update_one(
        {"institution_id": current_user["id"]},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "AI configuration updated"}

@router.get("/agents/available")
async def get_available_agents(current_user: dict = Depends(get_current_user)):
    """Get available AI agents for the student"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students access agents")
    
    institution_id = current_user.get("institution_id")
    
    # Check if student has AI tutor access
    has_ai_access = current_user.get("has_ai_tutor", False)
    
    # Check purchases for AI tutor
    if not has_ai_access:
        purchases = await db.student_purchases.find(
            {"student_id": current_user["id"], "status": "completed"}
        ).to_list(20)
        
        for p in purchases:
            if p.get("ai_tutor_hours_total", 0) > 0:
                ai_minutes_used = p.get("ai_tutor_minutes_used", 0)
                ai_minutes_total = p.get("ai_tutor_hours_total", 0) * 60
                if ai_minutes_used < ai_minutes_total:
                    has_ai_access = True
                    break
    
    if not has_ai_access:
        return {
            "has_access": False,
            "agents": [],
            "message": "AI Tutor access requires a paid plan with AI features."
        }
    
    # Get institution's AI config
    config = await db.ai_agent_configs.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config or not config.get("ai_tutor_enabled"):
        return {
            "has_access": False,
            "agents": [],
            "message": "AI Tutor is not enabled for your academy."
        }
    
    # Filter enabled agents
    enabled_agents = []
    for agent in config.get("agents", []):
        if agent.get("is_enabled"):
            agent_info = {
                "type": agent["agent_type"],
                "name": agent.get("custom_name") or DEFAULT_AGENT_CONFIGS[agent["agent_type"]]["default_name"],
                "personality": agent.get("custom_personality") or DEFAULT_AGENT_CONFIGS[agent["agent_type"]]["default_personality"],
                "avatar_tier": agent.get("avatar_tier", "basic"),
                "has_voice": config.get("elevenlabs_voice_id") is not None,
                "has_video_avatar": agent.get("avatar_tier") == "premium" and config.get("heygen_avatar_id")
            }
            enabled_agents.append(agent_info)
    
    return {
        "has_access": True,
        "agents": enabled_agents,
        "exam_type": current_user.get("current_exam", ""),
        "default_avatar_tier": config.get("default_avatar_tier", "basic")
    }

# ==================== CHAT WITH AGENTS ====================

@router.post("/chat")
async def chat_with_agent(
    request: AgentChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Send message to AI agent and get response"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can chat with agents")
    
    institution_id = current_user.get("institution_id")
    
    # Verify AI access
    has_access = await verify_ai_access(current_user)
    if not has_access:
        raise HTTPException(status_code=402, detail="AI Tutor access required. Please upgrade your plan.")
    
    # Get agent config
    config = await db.ai_agent_configs.find_one({"institution_id": institution_id})
    if not config:
        raise HTTPException(status_code=404, detail="AI not configured for this academy")
    
    agent_config = None
    for agent in config.get("agents", []):
        if agent["agent_type"] == request.agent_type.value and agent.get("is_enabled"):
            agent_config = agent
            break
    
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent not available")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = await db.ai_chat_sessions.find_one({"session_id": session_id})
    
    if not session:
        session = {
            "session_id": session_id,
            "student_id": current_user["id"],
            "institution_id": institution_id,
            "agent_type": request.agent_type.value,
            "messages": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.ai_chat_sessions.insert_one(session)
    
    # Build context
    exam_type = current_user.get("current_exam", "general")
    context = await build_agent_context(
        agent_type=request.agent_type.value,
        exam_type=exam_type,
        institution_id=institution_id,
        student=current_user,
        agent_config=agent_config
    )
    
    # Get LLM response
    llm_provider = agent_config.get("llm_provider", "openai_gpt4")
    
    # Build messages for LLM
    messages = [{"role": "system", "content": context}]
    
    # Add conversation history (last 10 messages)
    history = session.get("messages", [])[-10:]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add user message
    messages.append({"role": "user", "content": request.message})
    
    # Call LLM
    response_text = await call_llm(llm_provider, messages)
    
    # Save messages to session
    await db.ai_chat_sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "$each": [
                        {"role": "user", "content": request.message, "timestamp": datetime.now(timezone.utc).isoformat()},
                        {"role": "assistant", "content": response_text, "timestamp": datetime.now(timezone.utc).isoformat()}
                    ]
                }
            },
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Track AI usage
    background_tasks.add_task(track_ai_usage, current_user["id"], 1)  # 1 minute per interaction
    
    # Prepare response
    response = {
        "session_id": session_id,
        "agent_type": request.agent_type.value,
        "agent_name": agent_config.get("custom_name") or DEFAULT_AGENT_CONFIGS[request.agent_type.value]["default_name"],
        "message": response_text
    }
    
    # Generate voice if requested
    if request.include_voice and config.get("elevenlabs_voice_id"):
        voice_url = await generate_voice(response_text, config["elevenlabs_voice_id"])
        response["voice_url"] = voice_url
    
    # Generate avatar video if requested (premium tier)
    if request.include_avatar and agent_config.get("avatar_tier") == "premium":
        if config.get("heygen_avatar_id"):
            response["avatar_video_status"] = "generating"
            response["avatar_video_id"] = str(uuid.uuid4())
    
    return response

@router.get("/chat/sessions")
async def get_chat_sessions(current_user: dict = Depends(get_current_user)):
    """Get student's chat session history"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view sessions")
    
    sessions = await db.ai_chat_sessions.find(
        {"student_id": current_user["id"]},
        {"_id": 0, "messages": {"$slice": -1}}
    ).sort("updated_at", -1).limit(20).to_list(20)
    
    return {"sessions": sessions}

@router.get("/chat/session/{session_id}")
async def get_session_history(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get full conversation history for a session"""
    session = await db.ai_chat_sessions.find_one(
        {"session_id": session_id, "student_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

# ==================== REAL-TIME EXAM HELP (Mock Exam Coach) ====================

class ExamHelpRequest(BaseModel):
    attempt_id: str
    question_id: str
    question_text: str
    student_question: str
    current_answer: Optional[str] = None

@router.post("/exam-help")
async def get_exam_help(
    request: ExamHelpRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get real-time help from Mock Exam Coach during an exam"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can request help")
    
    # Verify AI access
    has_access = await verify_ai_access(current_user)
    if not has_access:
        raise HTTPException(status_code=402, detail="AI Tutor access required")
    
    institution_id = current_user.get("institution_id")
    
    # Verify the attempt exists and belongs to the student
    attempt = await db.mock_attempts.find_one({
        "id": request.attempt_id,
        "student_id": current_user["id"],
        "status": "in_progress"
    })
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found or already completed")
    
    # Get institution's AI config to check if mock_coach is enabled
    config = await db.ai_agent_configs.find_one({"institution_id": institution_id})
    
    mock_coach_enabled = False
    coach_name = "Mock Coach"
    
    if config:
        for agent in config.get("agents", []):
            if agent.get("agent_type") == "mock_coach" and agent.get("is_enabled"):
                mock_coach_enabled = True
                coach_name = agent.get("custom_name") or "Mock Coach"
                break
    
    if not mock_coach_enabled:
        raise HTTPException(status_code=403, detail="Mock Exam Coach is not enabled for your academy")
    
    exam_type = attempt.get("exam_type", "")
    
    # Build help prompt - guides without giving direct answers
    help_prompt = f"""You are {coach_name}, helping a student during their {exam_type.upper()} mock exam.

The student is stuck on this question and needs guidance:

QUESTION:
{request.question_text}

STUDENT'S CURRENT ANSWER (if any):
{request.current_answer or "No answer yet"}

STUDENT'S QUESTION:
{request.student_question}

IMPORTANT RULES:
1. NEVER give the direct answer
2. Guide the student to find the answer themselves
3. Provide hints, strategies, and thinking frameworks
4. Point out relevant parts of the question they might have missed
5. Suggest elimination strategies for multiple choice
6. Remind them of time management if relevant
7. Be encouraging and supportive

Respond in a helpful, coaching manner. Help them learn, don't solve it for them."""

    # Get platform LLM config
    platform_config = await db.platform_config.find_one({"type": "llm"})
    llm_provider = platform_config.get("default_llm", "openai_gpt4") if platform_config else "openai_gpt4"
    
    messages = [
        {"role": "system", "content": help_prompt},
        {"role": "user", "content": request.student_question}
    ]
    
    # Get AI response
    response_text = await call_llm(llm_provider, messages)
    
    # Log the help request (for analytics and to prevent abuse)
    help_log = {
        "id": str(uuid.uuid4()),
        "attempt_id": request.attempt_id,
        "student_id": current_user["id"],
        "question_id": request.question_id,
        "student_question": request.student_question,
        "coach_response": response_text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.exam_help_logs.insert_one(help_log)
    
    # Update attempt with help count
    await db.mock_attempts.update_one(
        {"id": request.attempt_id},
        {"$inc": {"help_requests": 1}}
    )
    
    return {
        "coach_name": coach_name,
        "response": response_text,
        "help_count": (attempt.get("help_requests", 0) + 1),
        "note": "Remember, the coach helps you think - the answer is yours to find!"
    }

# ==================== INSTANT EXAM FEEDBACK ====================

@router.post("/exam-feedback")
async def get_instant_exam_feedback(
    request: ExamFeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get instant AI feedback on exam answers - identical to official format"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can get feedback")
    
    # Verify AI access
    has_access = await verify_ai_access(current_user)
    if not has_access:
        raise HTTPException(status_code=402, detail="AI feedback requires a paid plan")
    
    institution_id = current_user.get("institution_id")
    
    # Get LLM config
    config = await db.ai_agent_configs.find_one({"institution_id": institution_id})
    llm_provider = config.get("default_llm", "openai_gpt4") if config else "openai_gpt4"
    
    # Build feedback prompt
    feedback_prompt = build_exam_feedback_prompt(
        exam_type=request.exam_type,
        section=request.section,
        answers=request.answers
    )
    
    # Get AI feedback
    messages = [
        {"role": "system", "content": f"You are an official {request.exam_type.upper()} exam evaluator. Provide feedback exactly as the official exam would. Be specific, constructive, and accurate."},
        {"role": "user", "content": feedback_prompt}
    ]
    
    feedback_text = await call_llm(llm_provider, messages)
    
    # Parse structured feedback
    feedback = parse_exam_feedback(feedback_text, request.exam_type, request.section)
    
    # Save feedback to attempt
    await db.mock_attempts.update_one(
        {"id": request.attempt_id},
        {
            "$set": {
                "ai_feedback": feedback,
                "feedback_generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "attempt_id": request.attempt_id,
        "feedback": feedback,
        "official_format": True,
        "exam_type": request.exam_type
    }

# ==================== HELPER FUNCTIONS ====================

async def verify_ai_access(user: dict) -> bool:
    """Check if user has AI tutor access"""
    if user.get("has_ai_tutor"):
        return True
    
    purchases = await db.student_purchases.find(
        {"student_id": user["id"], "status": "completed"}
    ).to_list(20)
    
    for p in purchases:
        total_minutes = p.get("ai_tutor_hours_total", 0) * 60
        used_minutes = p.get("ai_tutor_minutes_used", 0)
        if total_minutes > used_minutes:
            return True
    
    return False

async def track_ai_usage(student_id: str, minutes: int):
    """Track AI usage for billing"""
    purchases = await db.student_purchases.find(
        {
            "student_id": student_id,
            "status": "completed",
            "$expr": {"$gt": [{"$multiply": ["$ai_tutor_hours_total", 60]}, "$ai_tutor_minutes_used"]}
        }
    ).sort("purchased_at", 1).to_list(1)
    
    if purchases:
        await db.student_purchases.update_one(
            {"id": purchases[0]["id"]},
            {"$inc": {"ai_tutor_minutes_used": minutes}}
        )

async def build_agent_context(
    agent_type: str,
    exam_type: str,
    institution_id: str,
    student: dict,
    agent_config: dict
) -> str:
    """Build system prompt with all context for the agent"""
    template = DEFAULT_AGENT_CONFIGS[agent_type]["system_prompt_template"]
    
    exam_context = await get_exam_context(exam_type)
    academy_materials = await get_academy_materials(institution_id, exam_type)
    
    student_profile = {
        "name": student.get("name", "Student"),
        "exam": exam_type,
        "target_score": student.get("target_score"),
        "exam_date": student.get("exam_date")
    }
    
    prompt = template.format(
        agent_name=agent_config.get("custom_name") or DEFAULT_AGENT_CONFIGS[agent_type]["default_name"],
        exam_type=exam_type.upper(),
        exam_context=exam_context,
        academy_materials=academy_materials,
        student_profile=json.dumps(student_profile),
        exam_date=student.get("exam_date", "Not set"),
        target_score=student.get("target_score", "Not set"),
        current_performance="Based on recent exams"
    )
    
    return prompt

async def get_exam_context(exam_type: str) -> str:
    """Get official exam context and structure"""
    exam_info = {
        "oet": "Occupational English Test for healthcare professionals. 4 sections: Listening (45min), Reading (60min), Writing (45min), Speaking (20min). Graded A-E.",
        "ielts": "International English Language Testing System. 4 sections: Listening (30min), Reading (60min), Writing (60min), Speaking (11-14min). Band scores 0-9.",
        "toefl": "Test of English as a Foreign Language. 4 sections: Reading (54-72min), Listening (41-57min), Speaking (17min), Writing (50min). Score 0-120.",
        "pte": "Pearson Test of English Academic. Computer-based. Speaking & Writing (77-93min), Reading (32-41min), Listening (45-57min). Score 10-90.",
        "cambridge": "Cambridge English Qualifications. Multiple levels (B2 First, C1 Advanced, C2 Proficiency). 4 papers: Reading & Use of English, Writing, Listening, Speaking."
    }
    return exam_info.get(exam_type, "Standard English proficiency exam with Reading, Writing, Listening, and Speaking sections.")

async def get_academy_materials(institution_id: str, exam_type: str) -> str:
    """Get academy-specific materials for context"""
    materials = await db.academy_materials.find(
        {"institution_id": institution_id, "exam_type": exam_type}
    ).to_list(50)
    
    if not materials:
        return "No additional academy-specific materials."
    
    material_list = [f"- {m.get('title', 'Material')}: {m.get('description', '')}" for m in materials[:10]]
    return "\n".join(material_list)

async def call_llm(provider: str, messages: List[dict]) -> str:
    """Call the specified LLM provider - Abstraction layer for easy switching"""
    try:
        if provider in ["openai_gpt4", "openai_gpt4o"]:
            return await call_openai(messages, provider)
        elif provider in ["claude_opus", "claude_sonnet"]:
            return await call_claude(messages, provider)
        elif provider in ["gemini_pro", "gemini_flash"]:
            return await call_gemini(messages, provider)
        else:
            return await call_openai(messages, "openai_gpt4")
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I apologize, but I'm having trouble processing your request. Please try again."

async def call_openai(messages: List[dict], model: str) -> str:
    """Call OpenAI API using emergentintegrations"""
    try:
        from emergentintegrations.llm.openai import OpenAIChat, OpenAIMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API key not configured."
        
        model_name = "gpt-4" if model == "openai_gpt4" else "gpt-4o"
        
        chat = OpenAIChat(api_key=api_key, model=model_name)
        openai_messages = [OpenAIMessage(role=m["role"], content=m["content"]) for m in messages]
        
        response = await chat.async_chat(openai_messages)
        return response.content
    except ImportError:
        return "OpenAI integration not available. Please install emergentintegrations."
    except Exception as e:
        print(f"OpenAI error: {e}")
        return f"Error communicating with AI: {str(e)}"

async def call_claude(messages: List[dict], model: str) -> str:
    """Call Anthropic Claude API using emergentintegrations"""
    try:
        from emergentintegrations.llm.anthropic import AnthropicChat, AnthropicMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Claude API key not configured."
        
        model_name = "claude-3-opus-20240229" if model == "claude_opus" else "claude-3-sonnet-20240229"
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]
        
        chat = AnthropicChat(api_key=api_key, model=model_name, system=system_msg)
        anthropic_messages = [AnthropicMessage(role=m["role"], content=m["content"]) for m in user_messages]
        
        response = await chat.async_chat(anthropic_messages)
        return response.content
    except ImportError:
        return "Claude integration not available."
    except Exception as e:
        print(f"Claude error: {e}")
        return f"Error communicating with AI: {str(e)}"

async def call_gemini(messages: List[dict], model: str) -> str:
    """Call Google Gemini API using emergentintegrations"""
    try:
        from emergentintegrations.llm.gemini import GeminiChat, GeminiMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Gemini API key not configured."
        
        model_name = "gemini-1.5-pro" if model == "gemini_pro" else "gemini-1.5-flash"
        
        chat = GeminiChat(api_key=api_key, model=model_name)
        gemini_messages = [GeminiMessage(role="user" if m["role"] != "assistant" else "model", content=m["content"]) for m in messages]
        
        response = await chat.async_chat(gemini_messages)
        return response.content
    except ImportError:
        return "Gemini integration not available."
    except Exception as e:
        print(f"Gemini error: {e}")
        return f"Error communicating with AI: {str(e)}"

async def generate_voice(text: str, voice_id: str) -> Optional[str]:
    """Generate voice using ElevenLabs"""
    try:
        return None  # Placeholder - would call ElevenLabs API
    except Exception as e:
        print(f"Voice generation error: {e}")
        return None

def build_exam_feedback_prompt(exam_type: str, section: Optional[str], answers: Dict) -> str:
    """Build prompt for exam feedback"""
    return f"""Evaluate these {exam_type.upper()} exam answers and provide detailed feedback.

Section: {section or 'Full Exam'}
Answers: {json.dumps(answers, indent=2)}

Provide feedback in this exact format:
1. Overall Score: X/100
2. Band/Grade equivalent
3. Section-by-section breakdown
4. Specific strengths (with examples from answers)
5. Areas needing improvement (with specific corrections)
6. Actionable recommendations for improvement
7. Estimated time to reach target score

Be specific, reference actual answers, and match official exam scoring criteria."""

def parse_exam_feedback(feedback_text: str, exam_type: str, section: Optional[str]) -> dict:
    """Parse AI feedback into structured format"""
    return {
        "raw_feedback": feedback_text,
        "exam_type": exam_type,
        "section": section,
        "official_format": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
