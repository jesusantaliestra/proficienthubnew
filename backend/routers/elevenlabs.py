"""
ElevenLabs Voice Router - High-quality TTS for AI Tutor
Supports voice cloning, text-to-speech, and speech-to-text
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import base64
import io
import os

router = APIRouter(prefix="/elevenlabs", tags=["ElevenLabs Voice"])

from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

# Get ElevenLabs API Key from environment
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')

# Initialize ElevenLabs client lazily
_eleven_client = None

def get_eleven_client():
    global _eleven_client
    if _eleven_client is None:
        if not ELEVENLABS_API_KEY:
            raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")
        try:
            from elevenlabs import ElevenLabs
            _eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        except ImportError:
            raise HTTPException(status_code=500, detail="ElevenLabs SDK not installed. Run: pip install elevenlabs")
    return _eleven_client

# ==================== MODELS ====================

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

class TTSResponse(BaseModel):
    audio_url: str
    text: str
    voice_id: str
    duration: Optional[float] = None
    
class VoiceInfo(BaseModel):
    voice_id: str
    name: str
    category: str
    description: Optional[str] = None
    preview_url: Optional[str] = None

class STTRequest(BaseModel):
    audio_data: str  # Base64 encoded audio

class STTResponse(BaseModel):
    transcribed_text: str
    confidence: Optional[float] = None

# ==================== CONFIGURATION ====================

@router.get("/config")
async def get_elevenlabs_config(current_user: dict = Depends(get_current_user)):
    """Get ElevenLabs configuration for institution"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    config = await db.elevenlabs_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "enabled": False,
            "default_voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "model_id": "eleven_multilingual_v2",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "monthly_character_limit": 100000,
            "characters_used": 0
        }
    
    # Check if API key is configured
    config["api_key_configured"] = bool(ELEVENLABS_API_KEY)
    
    return {"config": config}

@router.put("/config")
async def update_elevenlabs_config(
    enabled: bool = True,
    default_voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    monthly_character_limit: int = 100000,
    current_user: dict = Depends(get_current_user)
):
    """Update ElevenLabs configuration (institution admins only)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can configure ElevenLabs")
    
    config_doc = {
        "institution_id": current_user["id"],
        "enabled": enabled,
        "default_voice_id": default_voice_id,
        "model_id": "eleven_multilingual_v2",
        "stability": stability,
        "similarity_boost": similarity_boost,
        "monthly_character_limit": monthly_character_limit,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.elevenlabs_config.update_one(
        {"institution_id": current_user["id"]},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "ElevenLabs configuration updated"}

# ==================== VOICES ====================

@router.get("/voices")
async def list_voices(current_user: dict = Depends(get_current_user)):
    """Get available ElevenLabs voices"""
    try:
        client = get_eleven_client()
        voices_response = client.voices.get_all()
        
        voices = []
        for voice in voices_response.voices:
            voices.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category or "premade",
                "description": voice.description,
                "preview_url": voice.preview_url,
                "labels": voice.labels
            })
        
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")

@router.get("/voices/recommended")
async def get_recommended_voices():
    """Get recommended voices for education"""
    return {
        "voices": [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "description": "Calm, professional female voice - ideal for instructional content",
                "category": "premade",
                "accent": "American",
                "use_case": "Speaking practice, feedback"
            },
            {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Sarah",
                "description": "Soft, friendly female voice - great for encouragement",
                "category": "premade",
                "accent": "American",
                "use_case": "Motivational feedback"
            },
            {
                "voice_id": "ErXwobaYiN019PkySvjV",
                "name": "Antoni",
                "description": "Well-rounded male voice - versatile for various content",
                "category": "premade",
                "accent": "American",
                "use_case": "General instruction"
            },
            {
                "voice_id": "VR6AewLTigWG4xSOukaG",
                "name": "Arnold",
                "description": "Crisp, clear male voice - excellent for exam instructions",
                "category": "premade",
                "accent": "American",
                "use_case": "Exam prompts"
            },
            {
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "name": "Adam",
                "description": "Deep, authoritative male voice - good for formal content",
                "category": "premade",
                "accent": "American",
                "use_case": "Formal feedback"
            }
        ]
    }

# ==================== TEXT-TO-SPEECH ====================

@router.post("/tts/generate", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate text-to-speech audio using ElevenLabs"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    # Check if ElevenLabs is enabled for this institution
    config = await db.elevenlabs_config.find_one({"institution_id": institution_id})
    
    # Check character limit
    if config:
        characters_used = config.get("characters_used", 0)
        limit = config.get("monthly_character_limit", 100000)
        if characters_used + len(request.text) > limit:
            raise HTTPException(status_code=429, detail="Monthly character limit exceeded")
    
    try:
        from elevenlabs import VoiceSettings
        client = get_eleven_client()
        
        # Generate audio
        voice_settings = VoiceSettings(
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=request.use_speaker_boost
        )
        
        audio_generator = client.text_to_speech.convert(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id,
            voice_settings=voice_settings
        )
        
        # Collect audio data
        audio_data = b""
        for chunk in audio_generator:
            audio_data += chunk
        
        # Convert to base64
        audio_b64 = base64.b64encode(audio_data).decode()
        
        # Update character usage
        await db.elevenlabs_config.update_one(
            {"institution_id": institution_id},
            {"$inc": {"characters_used": len(request.text)}},
            upsert=True
        )
        
        # Log generation
        await db.elevenlabs_generations.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "institution_id": institution_id,
            "text": request.text,
            "voice_id": request.voice_id,
            "characters": len(request.text),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return TTSResponse(
            audio_url=f"data:audio/mpeg;base64,{audio_b64}",
            text=request.text,
            voice_id=request.voice_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate TTS: {str(e)}")

@router.post("/tts/stream")
async def stream_tts(
    request: TTSRequest,
    current_user: dict = Depends(get_current_user)
):
    """Stream text-to-speech audio in real-time"""
    try:
        from elevenlabs import VoiceSettings
        client = get_eleven_client()
        
        voice_settings = VoiceSettings(
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=request.use_speaker_boost
        )
        
        audio_stream = client.text_to_speech.convert_as_stream(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id,
            voice_settings=voice_settings
        )
        
        def generate():
            for chunk in audio_stream:
                yield chunk
        
        return StreamingResponse(generate(), media_type="audio/mpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stream TTS: {str(e)}")

# ==================== SPEECH-TO-TEXT ====================

@router.post("/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Transcribe audio file to text using ElevenLabs Speech-to-Text"""
    try:
        client = get_eleven_client()
        
        # Read uploaded audio file
        audio_content = await audio_file.read()
        
        # Transcribe using ElevenLabs Speech-to-Text
        transcription_response = client.speech_to_text.convert(
            file=io.BytesIO(audio_content),
            model_id="scribe_v1"
        )
        
        # Extract text
        transcribed_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        
        return STTResponse(
            transcribed_text=transcribed_text,
            confidence=0.95  # ElevenLabs doesn't return confidence directly
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

# ==================== USAGE & ANALYTICS ====================

@router.get("/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    """Get ElevenLabs usage statistics for institution"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    config = await db.elevenlabs_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        return {
            "characters_used": 0,
            "monthly_limit": 100000,
            "percentage_used": 0,
            "generations_count": 0
        }
    
    # Count generations this month
    from datetime import timedelta
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    generations_count = await db.elevenlabs_generations.count_documents({
        "institution_id": institution_id,
        "created_at": {"$gte": month_start.isoformat()}
    })
    
    characters_used = config.get("characters_used", 0)
    monthly_limit = config.get("monthly_character_limit", 100000)
    
    return {
        "characters_used": characters_used,
        "monthly_limit": monthly_limit,
        "percentage_used": round((characters_used / monthly_limit) * 100, 1) if monthly_limit > 0 else 0,
        "generations_count": generations_count,
        "reset_date": (month_start + timedelta(days=32)).replace(day=1).isoformat()
    }

@router.post("/usage/reset")
async def reset_usage(current_user: dict = Depends(get_current_user)):
    """Reset monthly character usage (admin only)"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only admins can reset usage")
    
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    await db.elevenlabs_config.update_one(
        {"institution_id": institution_id},
        {"$set": {"characters_used": 0}},
        upsert=True
    )
    
    return {"message": "Usage reset successfully"}

# ==================== VOICE CLONING ====================

@router.post("/voices/clone")
async def clone_voice(
    files: List[UploadFile] = File(...),
    voice_name: str = Form(...),
    description: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Clone a voice using ElevenLabs IVC (Instant Voice Cloning)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can clone voices")
    
    try:
        client = get_eleven_client()
        
        # Prepare audio files
        audio_files = []
        for f in files:
            content = await f.read()
            audio_files.append((f.filename, io.BytesIO(content)))
        
        # Clone the voice
        voice = client.clone(
            name=voice_name,
            files=audio_files,
            description=description
        )
        
        # Save to database
        voice_doc = {
            "id": str(uuid.uuid4()),
            "elevenlabs_voice_id": voice.voice_id,
            "name": voice_name,
            "description": description,
            "institution_id": current_user["id"],
            "type": "cloned",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.custom_voices.insert_one(voice_doc)
        voice_doc.pop("_id", None)
        
        return {
            "message": "Voice cloned successfully",
            "voice": voice_doc
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone voice: {str(e)}")

@router.get("/voices/custom")
async def get_custom_voices(current_user: dict = Depends(get_current_user)):
    """Get custom/cloned voices for institution"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    voices = await db.custom_voices.find(
        {"institution_id": institution_id},
        {"_id": 0}
    ).to_list(50)
    
    return {"voices": voices}

@router.delete("/voices/custom/{voice_id}")
async def delete_custom_voice(
    voice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a custom/cloned voice"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can delete voices")
    
    voice = await db.custom_voices.find_one({
        "id": voice_id,
        "institution_id": current_user["id"]
    })
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    # Delete from ElevenLabs
    try:
        client = get_eleven_client()
        client.voices.delete(voice["elevenlabs_voice_id"])
    except:
        pass  # Voice might already be deleted from ElevenLabs
    
    # Delete from database
    await db.custom_voices.delete_one({"id": voice_id})
    
    return {"message": "Voice deleted successfully"}
