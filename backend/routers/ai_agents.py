"""
AI Agents Router
Handles AI tutor interactions, credits, and configuration
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

# ==================== AI AGENT DEFINITIONS ====================
AI_AGENTS = {
    "official_tutor": {
        "name": "Official IELTS Tutor",
        "name_es": "Tutor Oficial IELTS",
        "description": "Comprehensive exam preparation with official test strategies",
        "icon": "GraduationCap",
        "credits_per_message": 2,
        "voice_enabled": True,
        "system_prompt": """You are an official {exam_type} exam preparation tutor. Your role is to:
        1. Provide detailed explanations of exam formats and scoring
        2. Offer strategic tips for each section
        3. Give constructive feedback on practice responses
        4. Motivate and encourage students
        Always be supportive, patient, and thorough in your explanations."""
    },
    "mock_coach": {
        "name": "Mock Test Coach",
        "name_es": "Entrenador de Simulacros",
        "description": "Socratic method coach - guides without giving answers",
        "icon": "Brain",
        "credits_per_message": 1,
        "voice_enabled": True,
        "system_prompt": """You are a Socratic method coach for {exam_type} preparation. IMPORTANT RULES:
        1. NEVER give direct answers - instead ask guiding questions
        2. If student gets stuck, give hints not solutions
        3. Encourage critical thinking and self-discovery
        4. After 5 failed attempts, provide the answer with explanation
        5. Always celebrate small progress
        Use questions like: "What do you think about...?", "Why might that be...?", "What if you considered...?" """
    },
    "planner": {
        "name": "Study Planner",
        "name_es": "Planificador de Estudio",
        "description": "Creates personalized study schedules and tracks progress",
        "icon": "Calendar",
        "credits_per_message": 1,
        "voice_enabled": False,
        "system_prompt": """You are a study planning assistant for {exam_type} preparation. You help students:
        1. Create realistic study schedules based on their target date
        2. Balance practice across all exam sections
        3. Set achievable daily and weekly goals
        4. Adapt plans based on progress and weak areas
        Always consider the student's available time and learning pace."""
    }
}

# ==================== MODELS ====================
class CreditPurchase(BaseModel):
    credits: int

class AIAgentInteraction(BaseModel):
    agent_type: str
    message: str
    exam_type: str = "ielts"
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    voice_enabled: Optional[bool] = False

# ==================== HELPER FUNCTIONS ====================
async def consume_ai_credits(user_id: str, credits: int, agent_type: str, session_id: str):
    """Internal function to consume AI credits"""
    result = await db.ai_credits.find_one_and_update(
        {"user_id": user_id, "$expr": {"$gte": [{"$subtract": ["$total_credits", "$used_credits"]}, credits]}},
        {
            "$inc": {"used_credits": credits},
            "$set": {"last_updated": datetime.now(timezone.utc).isoformat()},
            "$push": {
                "usage_history": {
                    "credits": credits,
                    "agent_type": agent_type,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    return result is not None

# ==================== CREDITS ENDPOINTS ====================
@router.get("/credits")
async def get_ai_credits(current_user: dict = Depends(get_current_user)):
    """Get AI credits balance for institution or individual"""
    user_id = current_user.get("institution_id") or current_user["id"]
    user_type = current_user["user_type"]
    
    credits_doc = await db.ai_credits.find_one({"user_id": user_id}, {"_id": 0})
    
    if not credits_doc:
        initial_credits = 100 if user_type == "institution" else 10
        credits_doc = {
            "user_id": user_id,
            "user_type": user_type,
            "total_credits": initial_credits,
            "used_credits": 0,
            "free_credits": initial_credits,
            "purchased_credits": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        await db.ai_credits.insert_one(credits_doc)
    
    return {
        "total_credits": credits_doc.get("total_credits", 0),
        "used_credits": credits_doc.get("used_credits", 0),
        "remaining_credits": credits_doc.get("total_credits", 0) - credits_doc.get("used_credits", 0),
        "free_credits": credits_doc.get("free_credits", 0),
        "purchased_credits": credits_doc.get("purchased_credits", 0),
        "last_updated": credits_doc.get("last_updated")
    }

@router.post("/credits/purchase")
async def purchase_ai_credits(purchase: CreditPurchase, current_user: dict = Depends(get_current_user)):
    """Purchase AI credits for institution"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can purchase credits")
    
    user_id = current_user["id"]
    
    credit_prices = {
        100: 10,
        500: 40,
        1000: 70,
        5000: 300,
    }
    
    if purchase.credits not in credit_prices:
        raise HTTPException(status_code=400, detail=f"Invalid credit amount. Choose from: {list(credit_prices.keys())}")
    
    price = credit_prices[purchase.credits]
    
    await db.ai_credits.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "total_credits": purchase.credits,
                "purchased_credits": purchase.credits
            },
            "$set": {
                "last_purchase": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "purchase_history": {
                    "credits": purchase.credits,
                    "price": price,
                    "currency": "USD",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {
        "success": True,
        "credits_added": purchase.credits,
        "price": price,
        "message": f"Successfully added {purchase.credits} AI credits"
    }

# ==================== CONFIGURATION ENDPOINTS ====================
@router.get("/config")
async def get_agent_config(current_user: dict = Depends(get_current_user)):
    """Get AI agent configuration for institution"""
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    config = await db.ai_agent_config.find_one({"institution_id": institution_id}, {"_id": 0})
    
    if not config:
        config = {
            "institution_id": institution_id,
            "agents": {
                "official_tutor": {"enabled": True, "voice_id": "nova"},
                "mock_coach": {"enabled": True, "voice_id": "echo"},
                "planner": {"enabled": True, "voice_id": None}
            },
            "default_voice_enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.ai_agent_config.insert_one(config)
    
    agents_with_info = []
    for agent_id, agent_info in AI_AGENTS.items():
        agent_config = config.get("agents", {}).get(agent_id, {"enabled": True})
        agents_with_info.append({
            "id": agent_id,
            "name": agent_info["name"],
            "name_es": agent_info["name_es"],
            "description": agent_info["description"],
            "icon": agent_info["icon"],
            "credits_per_message": agent_info["credits_per_message"],
            "voice_enabled": agent_info["voice_enabled"],
            "enabled": agent_config.get("enabled", True),
            "custom_voice_id": agent_config.get("voice_id")
        })
    
    return {
        "agents": agents_with_info,
        "default_voice_enabled": config.get("default_voice_enabled", True)
    }

@router.post("/config")
async def update_agent_config(config_update: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Update AI agent configuration for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can configure agents")
    
    institution_id = current_user["id"]
    
    await db.ai_agent_config.update_one(
        {"institution_id": institution_id},
        {
            "$set": {
                **config_update,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": "Agent configuration updated"}

# ==================== AVAILABLE AGENTS ====================
@router.get("/available")
async def get_available_agents(current_user: dict = Depends(get_current_user)):
    """Get list of available AI agents for the user"""
    institution_id = current_user.get("institution_id")
    
    if institution_id:
        config = await db.ai_agent_config.find_one({"institution_id": institution_id}, {"_id": 0})
    else:
        config = None
    
    available_agents = []
    for agent_id, agent_info in AI_AGENTS.items():
        is_enabled = True
        if config:
            is_enabled = config.get("agents", {}).get(agent_id, {}).get("enabled", True)
        
        if is_enabled:
            available_agents.append({
                "id": agent_id,
                "name": agent_info["name"],
                "name_es": agent_info["name_es"],
                "description": agent_info["description"],
                "icon": agent_info["icon"],
                "credits_per_message": agent_info["credits_per_message"],
                "voice_enabled": agent_info["voice_enabled"]
            })
    
    return {"agents": available_agents}

# ==================== INTERACTION ENDPOINT ====================
@router.post("/interact")
async def interact_with_agent(interaction: AIAgentInteraction, current_user: dict = Depends(get_current_user)):
    """Main endpoint for interacting with AI agents"""
    
    if interaction.agent_type not in AI_AGENTS:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Choose from: {list(AI_AGENTS.keys())}")
    
    agent = AI_AGENTS[interaction.agent_type]
    user_id = current_user.get("institution_id") or current_user["id"]
    session_id = interaction.session_id or str(uuid.uuid4())
    
    credits_needed = agent["credits_per_message"]
    has_credits = await consume_ai_credits(user_id, credits_needed, interaction.agent_type, session_id)
    
    if not has_credits:
        return {
            "success": False,
            "error": "insufficient_credits",
            "message": "No hay créditos suficientes. Por favor compra más créditos para continuar.",
            "credits_needed": credits_needed
        }
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        system_prompt = agent["system_prompt"].format(exam_type=interaction.exam_type.upper())
        
        if interaction.agent_type == "mock_coach" and interaction.context:
            attempt_count = interaction.context.get("attempt_count", 0)
            current_question = interaction.context.get("current_question", "")
            if attempt_count > 0:
                system_prompt += f"\n\nCurrent question: {current_question}\nStudent's attempt number: {attempt_count}/5"
                if attempt_count >= 5:
                    system_prompt += "\nThis is their final attempt - provide the full answer and explanation."
        
        chat = LlmChat(
            api_key=api_key,
            model="gpt-4o-mini",
            system_message=system_prompt
        )
        
        response = await chat.send_async(UserMessage(interaction.message))
        
        # Store interaction history
        history_doc = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": current_user["id"],
            "institution_id": current_user.get("institution_id"),
            "agent_type": interaction.agent_type,
            "exam_type": interaction.exam_type,
            "user_message": interaction.message,
            "agent_response": response.content,
            "credits_used": credits_needed,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.ai_agent_history.insert_one(history_doc)
        
        return {
            "success": True,
            "response": response.content,
            "session_id": session_id,
            "agent_type": interaction.agent_type,
            "credits_used": credits_needed
        }
        
    except Exception as e:
        # Refund credits on error
        await db.ai_credits.update_one(
            {"user_id": user_id},
            {"$inc": {"used_credits": -credits_needed}}
        )
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# ==================== HISTORY ENDPOINTS ====================
@router.get("/history/{session_id}")
async def get_session_history(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get conversation history for a session"""
    history = await db.ai_agent_history.find(
        {"session_id": session_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    
    return {"history": history}

@router.get("/sessions")
async def get_user_sessions(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get recent sessions for the user"""
    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {"$group": {
            "_id": "$session_id",
            "agent_type": {"$first": "$agent_type"},
            "exam_type": {"$first": "$exam_type"},
            "message_count": {"$sum": 1},
            "last_message": {"$max": "$created_at"},
            "first_message": {"$min": "$created_at"}
        }},
        {"$sort": {"last_message": -1}},
        {"$limit": limit}
    ]
    
    sessions = await db.ai_agent_history.aggregate(pipeline).to_list(limit)
    
    return {
        "sessions": [
            {
                "session_id": s["_id"],
                "agent_type": s["agent_type"],
                "exam_type": s["exam_type"],
                "message_count": s["message_count"],
                "last_message": s["last_message"],
                "started_at": s["first_message"]
            }
            for s in sessions
        ]
    }
