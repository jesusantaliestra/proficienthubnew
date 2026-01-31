"""
Avatar Provider Service - Dual System Support

Supports two avatar providers:
1. HeyGen (Premium) - Cloud-based streaming avatars via WebRTC
2. MetaHuman/Simli (Economic) - Alternative avatar service

This module provides a unified interface for both providers.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os
import aiohttp
import json
import uuid

router = APIRouter(prefix="/avatar-service", tags=["Avatar Service"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]


# =============================================
# Models
# =============================================

class AvatarSession(BaseModel):
    """Avatar session configuration"""
    provider: str = "heygen"  # "heygen" | "simli" | "custom"
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    language: str = "en"
    scenario_type: str = "oet_speaking"  # oet_speaking | tutor | general
    scenario_id: Optional[str] = None


class SpeakRequest(BaseModel):
    """Request for avatar to speak"""
    session_id: str
    text: str
    emotion: Optional[str] = "neutral"


class ConversationMessage(BaseModel):
    """A message in the conversation"""
    role: str  # "user" | "avatar"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request for conversational response"""
    session_id: str
    user_message: str
    conversation_history: List[ConversationMessage] = []


# =============================================
# Avatar Provider Configurations
# =============================================

# HeyGen Avatars (Premium)
HEYGEN_AVATARS = {
    "nurse_female": {
        "avatar_id": "Monica_public_3_20240108",
        "voice_id": "9b3e4e70-b4a9-4a2d-8a76-d7e0a9e7a6c3",
        "name": "Monica (Nurse)",
        "description": "Professional female nurse avatar",
        "tier": "premium"
    },
    "doctor_male": {
        "avatar_id": "josh_lite3_20230714",
        "voice_id": "f114a467-c40a-4db8-964d-aaba89cd08fa",
        "name": "Dr. Josh",
        "description": "Professional male doctor avatar",
        "tier": "premium"
    },
    "patient_elderly": {
        "avatar_id": "Ann_public_20240108",
        "voice_id": "c8f9f4e5-7c0f-4d5e-8c1a-b2d4e6f8a0c2",
        "name": "Ann (Patient)",
        "description": "Elderly patient avatar for OET roleplay",
        "tier": "premium"
    },
    "tutor_friendly": {
        "avatar_id": "Anna_public_3_20240108",
        "voice_id": "a7b8c9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d",
        "name": "Anna (Tutor)",
        "description": "Friendly AI tutor avatar",
        "tier": "premium"
    }
}

# Economic Avatars (Simli/Open Source alternatives)
ECONOMIC_AVATARS = {
    "nurse_basic": {
        "avatar_id": "nurse_generic_001",
        "voice_id": "tts_female_en",
        "name": "Nurse (Basic)",
        "description": "Basic nurse avatar - TTS voice",
        "tier": "economic"
    },
    "doctor_basic": {
        "avatar_id": "doctor_generic_001", 
        "voice_id": "tts_male_en",
        "name": "Doctor (Basic)",
        "description": "Basic doctor avatar - TTS voice",
        "tier": "economic"
    },
    "patient_basic": {
        "avatar_id": "patient_generic_001",
        "voice_id": "tts_elderly_en",
        "name": "Patient (Basic)",
        "description": "Basic patient avatar - TTS voice",
        "tier": "economic"
    },
    "tutor_basic": {
        "avatar_id": "tutor_generic_001",
        "voice_id": "tts_friendly_en",
        "name": "Tutor (Basic)",
        "description": "Basic tutor avatar - TTS voice",
        "tier": "economic"
    }
}


# =============================================
# HeyGen Integration (Premium)
# =============================================

class HeyGenProvider:
    """HeyGen Streaming Avatar Provider - Premium tier"""
    
    BASE_URL = "https://api.heygen.com/v1"
    
    def __init__(self):
        self.api_key = os.environ.get("HEYGEN_API_KEY")
    
    @property
    def headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_session_token(self) -> Optional[str]:
        """Generate streaming session token"""
        if not self.api_key:
            return None
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.BASE_URL}/streaming.create_token",
                    headers=self.headers,
                    json={}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("token")
            except Exception as e:
                print(f"HeyGen token error: {e}")
        return None
    
    async def list_avatars(self) -> List[dict]:
        """Get available streaming avatars"""
        if not self.api_key:
            return []
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.BASE_URL}/streaming.list_avatars_v2",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
            except Exception as e:
                print(f"HeyGen list error: {e}")
        return []
    
    async def list_voices(self) -> List[dict]:
        """Get available voices"""
        if not self.api_key:
            return []
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.BASE_URL}/list_voices_v2",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
            except Exception as e:
                print(f"HeyGen voices error: {e}")
        return []


# =============================================
# Economic Provider (Simli/TTS Based)
# =============================================

class EconomicProvider:
    """Economic avatar provider using TTS + static images or Simli"""
    
    def __init__(self):
        self.simli_api_key = os.environ.get("SIMLI_API_KEY")
        # Fallback to basic TTS if no Simli key
        self.use_simli = bool(self.simli_api_key)
    
    async def create_session_token(self) -> str:
        """Generate session token for economic avatars"""
        # Economic provider uses local session management
        return str(uuid.uuid4())
    
    async def generate_speech(self, text: str, voice_id: str) -> Optional[str]:
        """
        Generate speech audio URL.
        Uses Simli if available, otherwise returns TTS instructions
        """
        if self.use_simli:
            # Simli API integration would go here
            pass
        
        # Return placeholder - frontend will use Web Speech API
        return None
    
    def get_avatar_image(self, avatar_id: str) -> str:
        """Get static avatar image for economic mode"""
        # Map avatar IDs to static images
        images = {
            "nurse_generic_001": "/static/avatars/nurse_female.png",
            "doctor_generic_001": "/static/avatars/doctor_male.png",
            "patient_generic_001": "/static/avatars/patient_elderly.png",
            "tutor_generic_001": "/static/avatars/tutor_friendly.png"
        }
        return images.get(avatar_id, "/static/avatars/default.png")


# =============================================
# Unified Avatar Service
# =============================================

heygen_provider = HeyGenProvider()
economic_provider = EconomicProvider()


# =============================================
# API Endpoints
# =============================================

@router.get("/providers")
async def get_providers():
    """Get available avatar providers and their status"""
    
    heygen_available = bool(os.environ.get("HEYGEN_API_KEY"))
    simli_available = bool(os.environ.get("SIMLI_API_KEY"))
    
    return {
        "providers": [
            {
                "id": "heygen",
                "name": "HeyGen (Premium)",
                "tier": "premium",
                "available": heygen_available,
                "features": ["streaming_video", "lip_sync", "emotions", "custom_voices"],
                "cost_indicator": "$$$"
            },
            {
                "id": "economic",
                "name": "Avatar Básico",
                "tier": "economic",
                "available": True,  # Always available via TTS fallback
                "features": ["tts_voice", "static_avatar", "basic_emotions"],
                "cost_indicator": "$",
                "uses_simli": simli_available
            }
        ]
    }


@router.get("/avatars")
async def get_avatars(tier: Optional[str] = None):
    """Get available avatars, optionally filtered by tier"""
    
    all_avatars = []
    
    # Add HeyGen avatars if available
    if os.environ.get("HEYGEN_API_KEY"):
        for key, avatar in HEYGEN_AVATARS.items():
            all_avatars.append({
                "id": key,
                "provider": "heygen",
                **avatar
            })
    
    # Add economic avatars (always available)
    for key, avatar in ECONOMIC_AVATARS.items():
        all_avatars.append({
            "id": key,
            "provider": "economic",
            **avatar
        })
    
    # Filter by tier if specified
    if tier:
        all_avatars = [a for a in all_avatars if a.get("tier") == tier]
    
    return {"avatars": all_avatars, "count": len(all_avatars)}


@router.post("/session/create")
async def create_avatar_session(config: AvatarSession):
    """Create a new avatar session"""
    
    session_id = str(uuid.uuid4())
    
    # Determine provider
    if config.provider == "heygen":
        if not os.environ.get("HEYGEN_API_KEY"):
            raise HTTPException(status_code=400, detail="HeyGen not configured")
        
        # Get HeyGen streaming token
        token = await heygen_provider.create_session_token()
        if not token:
            raise HTTPException(status_code=500, detail="Failed to create HeyGen session")
        
        # Get avatar config
        avatar_config = HEYGEN_AVATARS.get(config.avatar_id, list(HEYGEN_AVATARS.values())[0])
        
        session_data = {
            "id": session_id,
            "provider": "heygen",
            "streaming_token": token,
            "avatar_id": avatar_config["avatar_id"],
            "voice_id": avatar_config["voice_id"],
            "avatar_name": avatar_config["name"],
            "tier": "premium",
            "connection_type": "webrtc"
        }
    else:
        # Economic provider
        token = await economic_provider.create_session_token()
        avatar_config = ECONOMIC_AVATARS.get(config.avatar_id, list(ECONOMIC_AVATARS.values())[0])
        
        session_data = {
            "id": session_id,
            "provider": "economic",
            "session_token": token,
            "avatar_id": avatar_config["avatar_id"],
            "voice_id": avatar_config["voice_id"],
            "avatar_name": avatar_config["name"],
            "avatar_image": economic_provider.get_avatar_image(avatar_config["avatar_id"]),
            "tier": "economic",
            "connection_type": "tts",
            "use_web_speech": True
        }
    
    # Store session in database
    session_record = {
        **session_data,
        "scenario_type": config.scenario_type,
        "scenario_id": config.scenario_id,
        "language": config.language,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "conversation_history": [],
        "status": "active"
    }
    
    await db.avatar_sessions.insert_one(session_record)
    
    # Remove MongoDB _id before returning
    session_data["scenario_type"] = config.scenario_type
    session_data["language"] = config.language
    
    return {"session": session_data}


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    
    session = await db.avatar_sessions.find_one(
        {"id": session_id},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session": session}


@router.post("/session/{session_id}/speak")
async def avatar_speak(session_id: str, request: SpeakRequest):
    """
    Make avatar speak text.
    For HeyGen: Returns instructions for frontend to use SDK
    For Economic: Returns TTS data or audio URL
    """
    
    session = await db.avatar_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["provider"] == "heygen":
        # HeyGen uses frontend SDK for speaking
        # We just return the text and let frontend handle it
        return {
            "method": "sdk",
            "text": request.text,
            "emotion": request.emotion,
            "instructions": "Use StreamingAvatar.speak() with this text"
        }
    else:
        # Economic provider - use Web Speech API on frontend
        return {
            "method": "tts",
            "text": request.text,
            "voice_id": session.get("voice_id"),
            "language": session.get("language", "en"),
            "instructions": "Use Web Speech API speechSynthesis"
        }


@router.post("/session/{session_id}/chat")
async def avatar_chat(session_id: str, request: ChatRequest):
    """
    Process user message and generate avatar response.
    Uses LLM for intelligent responses.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    session = await db.avatar_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    # Build system prompt based on scenario
    scenario_type = session.get("scenario_type", "general")
    
    system_prompts = {
        "oet_speaking": """You are a patient in an OET (Occupational English Test) speaking roleplay. 
You are being treated by a healthcare professional who is practicing their English communication skills.
Respond naturally as a patient would, showing appropriate emotions and asking relevant questions.
Keep responses concise (2-3 sentences max) to simulate natural conversation.
If the healthcare professional asks about symptoms, describe them realistically.
Express appropriate concerns a real patient would have.""",
        
        "tutor": """You are an AI English tutor helping students prepare for English proficiency exams (OET, IELTS, etc).
Be encouraging, patient, and provide constructive feedback.
Point out grammar or vocabulary errors gently and suggest improvements.
Keep responses educational but friendly.
If asked about exam strategies, provide helpful tips.""",
        
        "general": """You are a friendly AI assistant helping with language practice.
Be helpful, encouraging, and conversational.
Keep responses natural and concise."""
    }
    
    system_prompt = system_prompts.get(scenario_type, system_prompts["general"])
    
    # Build conversation context
    history = request.conversation_history
    context = "\n".join([f"{m.role}: {m.content}" for m in history[-6:]])  # Last 6 messages
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"avatar-{session_id}",
        system_message=system_prompt
    ).with_model("openai", "gpt-4.1-mini")
    
    user_msg = UserMessage(
        text=f"Conversation so far:\n{context}\n\nUser just said: {request.user_message}\n\nRespond as the avatar:"
    )
    
    try:
        response = await chat.send_message(user_msg)
        avatar_response = response.strip()
        
        # Save to conversation history
        await db.avatar_sessions.update_one(
            {"id": session_id},
            {
                "$push": {
                    "conversation_history": {
                        "$each": [
                            {"role": "user", "content": request.user_message, "timestamp": datetime.now(timezone.utc).isoformat()},
                            {"role": "avatar", "content": avatar_response, "timestamp": datetime.now(timezone.utc).isoformat()}
                        ]
                    }
                }
            }
        )
        
        return {
            "avatar_response": avatar_response,
            "provider": session["provider"],
            "speak_method": "sdk" if session["provider"] == "heygen" else "tts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End an avatar session"""
    
    result = await db.avatar_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "status": "ended",
                "ended_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session ended", "session_id": session_id}


# =============================================
# OET Speaking Scenarios
# =============================================

OET_SCENARIOS = [
    {
        "id": "s012b_diabetes",
        "title": "Cambio de Medicación para Diabetes",
        "title_en": "Diabetes Medication Change",
        "patient_name": "Graham Webb",
        "patient_age": 58,
        "patient_gender": "male",
        "setting": "Community Health Centre",
        "situation": "El paciente fue diagnosticado con diabetes tipo 2 hace 6 meses. Regresa para revisión después de cambio de medicación.",
        "tasks": [
            "Pregunta sobre el nuevo régimen de medicación",
            "Discute los efectos secundarios experimentados",
            "Explica la importancia de monitorear niveles de glucosa",
            "Responde preguntas sobre dieta y ejercicio"
        ],
        "avatar_role": "patient",
        "difficulty": "intermediate"
    },
    {
        "id": "s046c_pe_warning",
        "title": "Signos de Alerta de Embolia Pulmonar",
        "title_en": "PE Warning Signs",
        "patient_name": "Patricia Holloway",
        "patient_age": 71,
        "patient_gender": "female",
        "setting": "Hospital Ward",
        "situation": "La paciente se recupera de cirugía de reemplazo de rodilla. Necesita educación sobre signos de alerta de embolia pulmonar.",
        "tasks": [
            "Explica qué es una embolia pulmonar",
            "Describe los signos de alerta a observar",
            "Discute factores de riesgo post-cirugía",
            "Proporciona instrucciones para buscar ayuda"
        ],
        "avatar_role": "patient",
        "difficulty": "advanced"
    },
    {
        "id": "s023a_wound_care",
        "title": "Cuidado de Heridas Post-Operatorio",
        "title_en": "Post-Operative Wound Care",
        "patient_name": "James Chen",
        "patient_age": 45,
        "patient_gender": "male",
        "setting": "Outpatient Clinic",
        "situation": "El paciente está siendo dado de alta después de una apendicectomía. Necesita instrucciones de cuidado de heridas.",
        "tasks": [
            "Explica cómo mantener la herida limpia",
            "Describe signos de infección",
            "Discute restricciones de actividad",
            "Programa cita de seguimiento"
        ],
        "avatar_role": "patient",
        "difficulty": "beginner"
    }
]


@router.get("/oet/scenarios")
async def get_oet_scenarios():
    """Get available OET speaking practice scenarios"""
    return {"scenarios": OET_SCENARIOS, "count": len(OET_SCENARIOS)}


@router.get("/oet/scenario/{scenario_id}")
async def get_oet_scenario(scenario_id: str):
    """Get specific OET scenario details"""
    
    scenario = next((s for s in OET_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return {"scenario": scenario}


@router.post("/oet/start-roleplay")
async def start_oet_roleplay(
    scenario_id: str,
    provider: str = "economic",
    avatar_id: Optional[str] = None
):
    """
    Start an OET speaking roleplay session.
    Returns session info and initial patient greeting.
    """
    
    scenario = next((s for s in OET_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Select appropriate avatar
    if not avatar_id:
        if scenario["patient_gender"] == "female":
            avatar_id = "patient_basic" if provider == "economic" else "patient_elderly"
        else:
            avatar_id = "patient_basic" if provider == "economic" else "doctor_male"
    
    # Create session
    session_config = AvatarSession(
        provider=provider,
        avatar_id=avatar_id,
        scenario_type="oet_speaking",
        scenario_id=scenario_id,
        language="en"
    )
    
    session_response = await create_avatar_session(session_config)
    session = session_response["session"]
    
    # Generate initial patient greeting
    initial_greeting = f"Hello, I'm {scenario['patient_name']}. Thank you for seeing me today."
    
    # Save initial message
    await db.avatar_sessions.update_one(
        {"id": session["id"]},
        {
            "$push": {
                "conversation_history": {
                    "role": "avatar",
                    "content": initial_greeting,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    
    return {
        "session": session,
        "scenario": scenario,
        "initial_greeting": initial_greeting,
        "instructions": {
            "prep_time": 180,  # 3 minutes preparation
            "speaking_time": 300,  # 5 minutes speaking
            "tasks": scenario["tasks"]
        }
    }
