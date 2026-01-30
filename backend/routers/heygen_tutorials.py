"""HeyGen Tutorial Router - Premium video avatars for tutorials"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import httpx
import uuid
import os

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/heygen", tags=["HeyGen Tutorials"])

# HeyGen API configuration
HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY")
HEYGEN_BASE_URL = "https://api.heygen.com"

# Models
class TutorialVideoRequest(BaseModel):
    tutorial_type: str  # "onboarding", "feature", "custom"
    script: str
    language: str = "es"  # Spanish by default
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    title: Optional[str] = None
    for_whitelabel: Optional[str] = None  # Institution slug if for white-label

class HeyGenConfig(BaseModel):
    enabled: bool = True
    default_avatar_id: Optional[str] = None
    default_voice_id_en: Optional[str] = None
    default_voice_id_es: Optional[str] = None
    tutorial_templates: List[Dict[str, Any]] = []

# Predefined tutorial scripts
TUTORIAL_SCRIPTS = {
    "onboarding_welcome": {
        "es": """¡Bienvenido a ProficientHub! Soy tu guía virtual y voy a ayudarte a configurar tu academia paso a paso.

En los próximos minutos, aprenderás cómo:
1. Configurar tu perfil institucional
2. Agregar estudiantes
3. Activar los tutores de IA
4. Personalizar tu marca

¡Comencemos!""",
        "en": """Welcome to ProficientHub! I'm your virtual guide and I'll help you set up your academy step by step.

In the next few minutes, you'll learn how to:
1. Configure your institutional profile
2. Add students
3. Activate AI tutors
4. Customize your branding

Let's get started!"""
    },
    "feature_ai_tutor": {
        "es": """Los tutores de IA son una de las características más potentes de ProficientHub.

Tienes tres tipos de tutores disponibles:
- El Tutor Oficial te ayuda con el contenido del examen
- El Mock Coach te asiste durante los exámenes de práctica
- El Planificador organiza tu estudio

Puedes personalizar el nombre y la voz de cada tutor para que se adapten a tu marca.""",
        "en": """AI Tutors are one of ProficientHub's most powerful features.

You have three types of tutors available:
- The Official Tutor helps with exam content
- The Mock Coach assists during practice exams
- The Planner organizes your study schedule

You can customize each tutor's name and voice to match your brand."""
    },
    "feature_analytics": {
        "es": """El dashboard de analíticas te permite ver el progreso de todos tus estudiantes en tiempo real.

Puedes ver:
- Puntuaciones promedio por sección
- Tiempo de estudio acumulado
- Comparativas entre estudiantes
- Predicciones de resultados

Los reportes se pueden exportar en PDF para compartir con padres o directivos.""",
        "en": """The analytics dashboard lets you see all your students' progress in real time.

You can view:
- Average scores by section
- Accumulated study time
- Student comparisons
- Result predictions

Reports can be exported as PDF to share with parents or management."""
    }
}

def get_heygen_headers():
    """Get HeyGen API headers"""
    if not HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="HeyGen API key not configured")
    return {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }

# Superadmin endpoints
@router.get("/admin/config")
async def get_heygen_config(current_user: dict = Depends(get_current_user)):
    """Get HeyGen configuration (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede acceder")
    
    config = await db.platform_config.find_one(
        {"config_type": "heygen"},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "config_type": "heygen",
            "enabled": True,
            "api_key_configured": bool(HEYGEN_API_KEY),
            "default_avatar_id": None,
            "default_voice_id_en": None,
            "default_voice_id_es": None,
            "tutorial_templates": list(TUTORIAL_SCRIPTS.keys())
        }
    
    # Don't expose the actual API key
    config["api_key_configured"] = bool(HEYGEN_API_KEY)
    
    return config

@router.put("/admin/config")
async def update_heygen_config(
    config: HeyGenConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update HeyGen configuration (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede modificar")
    
    update_data = config.dict(exclude_none=True)
    update_data["config_type"] = "heygen"
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.platform_config.update_one(
        {"config_type": "heygen"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Configuración de HeyGen actualizada"}

@router.get("/admin/avatars")
async def list_available_avatars(current_user: dict = Depends(get_current_user)):
    """List available HeyGen avatars (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede acceder")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_BASE_URL}/v2/avatars",
                headers=get_heygen_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                avatars = data.get("data", {}).get("avatars", [])
                
                # Filter and format avatars
                formatted = []
                for avatar in avatars:
                    formatted.append({
                        "avatar_id": avatar.get("avatar_id"),
                        "avatar_name": avatar.get("avatar_name"),
                        "preview_image_url": avatar.get("preview_image_url"),
                        "preview_video_url": avatar.get("preview_video_url"),
                        "gender": avatar.get("gender")
                    })
                
                return {"avatars": formatted, "total": len(formatted)}
            else:
                return {"avatars": [], "error": f"HeyGen API error: {response.status_code}"}
                
    except Exception as e:
        return {"avatars": [], "error": str(e)}

@router.get("/admin/voices")
async def list_available_voices(current_user: dict = Depends(get_current_user)):
    """List available HeyGen voices (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede acceder")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_BASE_URL}/v2/voices",
                headers=get_heygen_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                voices = data.get("data", {}).get("voices", [])
                
                # Filter for Spanish and English voices
                filtered = [v for v in voices if v.get("language") in ["es", "en", "es-ES", "en-US"]]
                
                return {"voices": filtered, "total": len(filtered)}
            else:
                return {"voices": [], "error": f"HeyGen API error: {response.status_code}"}
                
    except Exception as e:
        return {"voices": [], "error": str(e)}

@router.post("/admin/generate-tutorial")
async def generate_tutorial_video(
    request: TutorialVideoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a tutorial video using HeyGen (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede generar videos")
    
    # Get configuration
    config = await db.platform_config.find_one({"config_type": "heygen"})
    
    avatar_id = request.avatar_id or (config.get("default_avatar_id") if config else None)
    voice_id = request.voice_id
    
    if not voice_id and config:
        voice_id = config.get(f"default_voice_id_{request.language}")
    
    if not avatar_id:
        raise HTTPException(status_code=400, detail="No se ha configurado un avatar por defecto")
    
    # Prepare video generation request
    video_payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "input_text": request.script,
                "voice_id": voice_id
            } if voice_id else {
                "type": "text",
                "input_text": request.script
            }
        }],
        "dimension": {
            "width": 1920,
            "height": 1080
        },
        "test": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEYGEN_BASE_URL}/v2/video/generate",
                headers=get_heygen_headers(),
                json=video_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                video_id = data.get("data", {}).get("video_id")
                
                # Store video record
                video_doc = {
                    "id": str(uuid.uuid4()),
                    "heygen_video_id": video_id,
                    "tutorial_type": request.tutorial_type,
                    "title": request.title or f"Tutorial: {request.tutorial_type}",
                    "language": request.language,
                    "for_whitelabel": request.for_whitelabel,
                    "status": "processing",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": current_user.get("id")
                }
                
                await db.tutorial_videos.insert_one(video_doc)
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "message": "Video en generación. Puede tomar 2-5 minutos.",
                    "status_url": f"/api/heygen/video/{video_id}/status"
                }
            else:
                error_detail = response.json().get("message", response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error de HeyGen: {error_detail}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")

@router.get("/video/{video_id}/status")
async def get_video_status(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video generation status"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_BASE_URL}/v1/video_status.get",
                params={"video_id": video_id},
                headers=get_heygen_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                status_data = data.get("data", {})
                
                # Update local record if completed
                if status_data.get("status") == "completed":
                    await db.tutorial_videos.update_one(
                        {"heygen_video_id": video_id},
                        {"$set": {
                            "status": "completed",
                            "video_url": status_data.get("video_url"),
                            "thumbnail_url": status_data.get("thumbnail_url"),
                            "duration": status_data.get("duration"),
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                
                return {
                    "video_id": video_id,
                    "status": status_data.get("status"),
                    "video_url": status_data.get("video_url"),
                    "thumbnail_url": status_data.get("thumbnail_url"),
                    "duration": status_data.get("duration")
                }
            else:
                return {"video_id": video_id, "status": "error", "message": response.text}
                
    except Exception as e:
        return {"video_id": video_id, "status": "error", "message": str(e)}

@router.get("/tutorials")
async def list_tutorial_videos(
    tutorial_type: Optional[str] = None,
    language: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List generated tutorial videos"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {"status": "completed"}
    if tutorial_type:
        query["tutorial_type"] = tutorial_type
    if language:
        query["language"] = language
    
    videos = await db.tutorial_videos.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return {"videos": videos, "total": len(videos)}

@router.get("/templates")
async def get_tutorial_templates():
    """Get predefined tutorial script templates (public)"""
    
    templates = []
    for key, scripts in TUTORIAL_SCRIPTS.items():
        templates.append({
            "id": key,
            "name": key.replace("_", " ").title(),
            "languages": list(scripts.keys()),
            "preview_es": scripts.get("es", "")[:100] + "...",
            "preview_en": scripts.get("en", "")[:100] + "..."
        })
    
    return {"templates": templates}

@router.get("/template/{template_id}")
async def get_template_script(template_id: str, language: str = "es"):
    """Get a specific template script"""
    
    if template_id not in TUTORIAL_SCRIPTS:
        raise HTTPException(status_code=404, detail="Template not found")
    
    script = TUTORIAL_SCRIPTS[template_id].get(language) or TUTORIAL_SCRIPTS[template_id].get("es")
    
    return {
        "template_id": template_id,
        "language": language,
        "script": script
    }



# =============================================
# HeyGen Webhook Endpoint
# =============================================

class HeyGenWebhookPayload(BaseModel):
    event_type: str  # "video.completed", "video.failed"
    video_id: str
    status: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None

@router.post("/webhook")
async def heygen_webhook(payload: HeyGenWebhookPayload):
    """
    Webhook endpoint for HeyGen API callbacks.
    
    Configure this URL in your HeyGen dashboard:
    https://your-domain.com/api/heygen/webhook
    
    HeyGen will call this endpoint when:
    - A video is completed (event_type: "video.completed" or "avatar_video.success")
    - A video fails (event_type: "video.failed" or "avatar_video.fail")
    """
    
    # Log the webhook event
    webhook_log = {
        "id": str(uuid.uuid4()),
        "event_type": payload.event_type,
        "video_id": payload.video_id,
        "status": payload.status,
        "video_url": payload.video_url,
        "error": payload.error,
        "received_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.heygen_webhook_logs.insert_one(webhook_log)
    
    # Update the video record based on event type
    if payload.event_type in ["video.completed", "avatar_video.success"]:
        await db.tutorial_videos.update_one(
            {"heygen_video_id": payload.video_id},
            {"$set": {
                "status": "completed",
                "video_url": payload.video_url,
                "thumbnail_url": payload.thumbnail_url,
                "duration": payload.duration,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"status": "success", "message": "Video marked as completed"}
    
    elif payload.event_type in ["video.failed", "avatar_video.fail"]:
        await db.tutorial_videos.update_one(
            {"heygen_video_id": payload.video_id},
            {"$set": {
                "status": "failed",
                "error": payload.error,
                "failed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"status": "success", "message": "Video marked as failed"}
    
    return {"status": "received", "event_type": payload.event_type}


@router.get("/webhook/logs")
async def get_webhook_logs(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get recent webhook logs (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    logs = await db.heygen_webhook_logs.find(
        {},
        {"_id": 0}
    ).sort("received_at", -1).limit(limit).to_list(limit)
    
    return {"logs": logs, "count": len(logs)}
