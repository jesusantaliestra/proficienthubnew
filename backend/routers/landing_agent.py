"""Landing Agent Router - Interactive AI chat widget for landing page"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os

from database import db

router = APIRouter(prefix="/landing-agent", tags=["Landing Agent"])

# Models
class LandingChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class LandingAgentConfig(BaseModel):
    enabled: bool = True
    llm_provider: str = "openai"  # openai, claude, gemini
    llm_model: str = "gpt-4"
    max_messages_per_session: int = 5
    greeting_message: str = "¡Hola! Soy el asistente de ProficientHub. ¿En qué puedo ayudarte hoy?"
    system_prompt: Optional[str] = None

# Default system prompt for landing agent
DEFAULT_SYSTEM_PROMPT = """Eres un asistente amigable de ProficientHub, una plataforma educativa para preparación de exámenes como OET, IELTS, TOEFL.

Tu rol es:
1. Responder preguntas sobre ProficientHub y sus características
2. Explicar cómo funcionan los exámenes de práctica
3. Describir los beneficios del AI Tutor
4. Ayudar a visitantes interesados a registrarse
5. Responder preguntas básicas sobre los exámenes (OET, IELTS, TOEFL)

Características de ProficientHub:
- Exámenes de práctica con condiciones reales
- AI Tutor personalizado 24/7
- Feedback detallado en PDF
- Dashboard de progreso
- Material de estudio premium
- Preparación para Speaking con IA

Mantén las respuestas concisas (máximo 3-4 oraciones).
Si te preguntan algo fuera de este tema, amablemente redirige la conversación a ProficientHub.
Al final de cada respuesta, si es apropiado, sugiere registrarse para una prueba gratuita."""

# Session storage (in-memory for demo, use Redis in production)
landing_sessions: Dict[str, Dict] = {}

@router.get("/config")
async def get_landing_agent_config():
    """Get landing agent configuration (public)"""
    config = await db.platform_config.find_one(
        {"config_type": "landing_agent"},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "enabled": True,
            "greeting_message": "¡Hola! Soy el asistente de ProficientHub. ¿En qué puedo ayudarte hoy?",
            "max_messages": 5
        }
    
    # Don't expose internal config
    return {
        "enabled": config.get("enabled", True),
        "greeting_message": config.get("greeting_message"),
        "max_messages": config.get("max_messages_per_session", 5)
    }

@router.post("/chat")
async def landing_agent_chat(request: LandingChatMessage):
    """Chat with the landing page agent (public, rate limited)"""
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in landing_sessions:
        landing_sessions[session_id] = {
            "messages": [],
            "message_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    session = landing_sessions[session_id]
    
    # Check message limit
    config = await db.platform_config.find_one(
        {"config_type": "landing_agent"},
        {"_id": 0}
    )
    
    # Handle case when config is None
    if config is None:
        config = {}
    
    max_messages = config.get("max_messages_per_session", 5)
    
    if session["message_count"] >= max_messages:
        return {
            "session_id": session_id,
            "response": "Has alcanzado el límite de mensajes de la demo. ¡Regístrate para acceso completo al AI Tutor!",
            "limit_reached": True,
            "cta": {
                "text": "Registrarse Gratis",
                "url": "/register"
            }
        }
    
    # Get LLM configuration
    llm_provider = config.get("llm_provider", "openai")
    llm_model = config.get("llm_model", "gpt-4")
    system_prompt = config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    
    # Build conversation history
    messages_history = [{"role": "system", "content": system_prompt}]
    for msg in session["messages"][-6:]:  # Keep last 6 messages for context
        messages_history.append(msg)
    messages_history.append({"role": "user", "content": request.message})
    
    # Generate response using configured LLM
    try:
        response_text = await generate_llm_response(llm_provider, llm_model, messages_history)
    except Exception as e:
        response_text = "Lo siento, hubo un error. Por favor intenta de nuevo o visita nuestra página de registro para más información."
    
    # Update session
    session["messages"].append({"role": "user", "content": request.message})
    session["messages"].append({"role": "assistant", "content": response_text})
    session["message_count"] += 1
    
    # Log interaction
    await db.landing_agent_logs.insert_one({
        "session_id": session_id,
        "user_message": request.message[:500],
        "agent_response": response_text[:500],
        "llm_provider": llm_provider,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    remaining_messages = max_messages - session["message_count"]
    
    return {
        "session_id": session_id,
        "response": response_text,
        "remaining_messages": remaining_messages,
        "limit_reached": False,
        "cta": {
            "text": "Registrarse Gratis",
            "url": "/register"
        } if remaining_messages <= 2 else None
    }

async def generate_llm_response(provider: str, model: str, messages: List[Dict]) -> str:
    """Generate response using configured LLM provider"""
    
    # Try to get Emergent LLM key
    emergent_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if provider == "openai":
        try:
            from emergentintegrations.llm.openai import chat_completion
            response = await chat_completion(
                api_key=emergent_key,
                model=model,
                messages=messages
            )
            return response.get("content", "")
        except ImportError:
            # Fallback to direct OpenAI
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {emergent_key}"},
                    json={"model": model, "messages": messages, "max_tokens": 300},
                    timeout=30
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                raise Exception(f"OpenAI error: {resp.status_code}")
    
    elif provider == "claude":
        try:
            from emergentintegrations.llm.anthropic import chat_completion
            response = await chat_completion(
                api_key=emergent_key,
                model=model,
                messages=messages
            )
            return response.get("content", "")
        except:
            return "Estoy aquí para ayudarte con información sobre ProficientHub. ¿Qué te gustaría saber?"
    
    elif provider == "gemini":
        try:
            from emergentintegrations.llm.gemini import chat_completion
            response = await chat_completion(
                api_key=emergent_key,
                model=model,
                messages=messages
            )
            return response.get("content", "")
        except:
            return "¡Bienvenido a ProficientHub! ¿Tienes alguna pregunta sobre nuestra plataforma de preparación de exámenes?"
    
    return "Gracias por tu interés en ProficientHub. ¿Hay algo específico que te gustaría saber sobre nuestra plataforma?"


# Superadmin endpoints for configuration
@router.get("/admin/config")
async def get_full_landing_agent_config(
    # In production, add admin auth
):
    """Get full landing agent configuration (admin only)"""
    config = await db.platform_config.find_one(
        {"config_type": "landing_agent"},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "config_type": "landing_agent",
            "enabled": True,
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "max_messages_per_session": 5,
            "greeting_message": "¡Hola! Soy el asistente de ProficientHub. ¿En qué puedo ayudarte hoy?",
            "system_prompt": DEFAULT_SYSTEM_PROMPT
        }
    
    return config

@router.put("/admin/config")
async def update_landing_agent_config(
    config: LandingAgentConfig,
    # In production, add admin auth
):
    """Update landing agent configuration (admin only)"""
    update_data = config.dict(exclude_none=True)
    update_data["config_type"] = "landing_agent"
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.platform_config.update_one(
        {"config_type": "landing_agent"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Landing agent configuration updated"}

@router.get("/admin/stats")
async def get_landing_agent_stats():
    """Get landing agent usage statistics (admin only)"""
    
    # Count total sessions
    total_sessions = len(landing_sessions)
    
    # Get logs from DB
    total_messages = await db.landing_agent_logs.count_documents({})
    
    # Messages by provider
    provider_pipeline = [
        {"$group": {"_id": "$llm_provider", "count": {"$sum": 1}}}
    ]
    by_provider = await db.landing_agent_logs.aggregate(provider_pipeline).to_list(10)
    
    return {
        "active_sessions": total_sessions,
        "total_messages": total_messages,
        "by_provider": {p["_id"]: p["count"] for p in by_provider}
    }
