"""
Speech-to-Text Service using OpenAI Whisper

This module provides real-time audio transcription for the speaking practice feature.
Uses OpenAI Whisper model via Emergent LLM Key.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from datetime import datetime, timezone

router = APIRouter(prefix="/speech", tags=["Speech Services"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]


# =============================================
# Models
# =============================================

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    confidence: Optional[float] = None


class TranscriptionRequest(BaseModel):
    language: Optional[str] = "en"
    prompt: Optional[str] = None


# =============================================
# Supported Audio Formats
# =============================================

SUPPORTED_FORMATS = [
    "audio/webm",
    "audio/wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/ogg",
    "application/octet-stream"  # fallback for some browsers
]

# File extension mapping
EXTENSION_MAP = {
    "audio/webm": ".webm",
    "audio/wav": ".wav",
    "audio/mp3": ".mp3",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".mp4",
    "audio/m4a": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/ogg": ".ogg",
    "application/octet-stream": ".webm"
}


# =============================================
# Transcription Endpoint
# =============================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    prompt: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    """
    Transcribe audio file to text using OpenAI Whisper.
    
    Parameters:
    - file: Audio file (webm, wav, mp3, mp4, m4a, ogg, mpeg)
    - language: ISO-639-1 language code (default: en)
    - prompt: Optional context to guide transcription
    - session_id: Optional session ID for logging
    
    Returns:
    - TranscriptionResponse with transcribed text
    """
    from emergentintegrations.llm.openai import OpenAISpeechToText
    
    # Validate API key
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Speech-to-text service not configured"
        )
    
    # Validate content type
    content_type = file.content_type or "application/octet-stream"
    if content_type not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {content_type}. Supported: webm, wav, mp3, mp4, m4a, mpeg, ogg"
        )
    
    # Read file content
    try:
        audio_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio file: {str(e)}")
    
    # Check file size (max 25MB)
    file_size = len(audio_content)
    if file_size > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum: 25MB"
        )
    
    if file_size < 100:
        raise HTTPException(
            status_code=400,
            detail="Audio file too small or empty"
        )
    
    # Get file extension
    extension = EXTENSION_MAP.get(content_type, ".webm")
    
    # Create temporary file for transcription
    temp_file_path = None
    try:
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Initialize STT
        stt = OpenAISpeechToText(api_key=api_key)
        
        # Build transcription parameters
        transcribe_params = {
            "model": "whisper-1",
            "response_format": "verbose_json",
            "language": language or "en"
        }
        
        # Add prompt if provided
        if prompt:
            transcribe_params["prompt"] = prompt
        else:
            # Default prompt for OET context
            transcribe_params["prompt"] = "Healthcare professional speaking to a patient. Medical terminology may be used."
        
        # Transcribe
        with open(temp_file_path, "rb") as audio_file:
            response = await stt.transcribe(file=audio_file, **transcribe_params)
        
        # Extract text
        transcribed_text = response.text if hasattr(response, 'text') else str(response)
        
        # Extract duration if available
        duration = None
        if hasattr(response, 'duration'):
            duration = response.duration
        
        # Log transcription
        if session_id:
            await db.transcription_logs.insert_one({
                "session_id": session_id,
                "text": transcribed_text,
                "language": language,
                "duration": duration,
                "file_size": file_size,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return TranscriptionResponse(
            text=transcribed_text.strip(),
            language=language,
            duration=duration,
            confidence=0.95  # Whisper doesn't return confidence, using default
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        # Log error
        await db.transcription_errors.insert_one({
            "error": error_msg,
            "session_id": session_id,
            "file_size": file_size,
            "content_type": content_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {error_msg}"
        )
    finally:
        # Cleanup temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass


@router.post("/transcribe-base64")
async def transcribe_audio_base64(
    audio_data: str,
    language: Optional[str] = "en",
    prompt: Optional[str] = None,
    session_id: Optional[str] = None
):
    """
    Transcribe base64-encoded audio to text.
    
    Useful when sending audio directly from JavaScript without FormData.
    
    Parameters:
    - audio_data: Base64 encoded audio (with or without data URI prefix)
    - language: ISO-639-1 language code
    - prompt: Optional context
    - session_id: Optional session ID
    """
    import base64
    from emergentintegrations.llm.openai import OpenAISpeechToText
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Speech-to-text service not configured")
    
    try:
        # Remove data URI prefix if present
        if "base64," in audio_data:
            audio_data = audio_data.split("base64,")[1]
        
        # Decode base64
        audio_bytes = base64.b64decode(audio_data)
        
        if len(audio_bytes) < 100:
            raise HTTPException(status_code=400, detail="Audio data too small")
        
        if len(audio_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio data too large (max 25MB)")
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            stt = OpenAISpeechToText(api_key=api_key)
            
            with open(temp_file_path, "rb") as audio_file:
                response = await stt.transcribe(
                    file=audio_file,
                    model="whisper-1",
                    response_format="json",
                    language=language or "en",
                    prompt=prompt or "Healthcare professional speaking."
                )
            
            text = response.text if hasattr(response, 'text') else str(response)
            
            return {"text": text.strip(), "language": language}
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported audio formats for transcription"""
    return {
        "formats": ["webm", "wav", "mp3", "mp4", "m4a", "mpeg", "ogg"],
        "max_size_mb": 25,
        "default_language": "en",
        "supported_languages": [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "bn", "pa", "te", "mr", "ta", "tr", "vi", "th",
            "pl", "uk", "nl", "el", "cs", "sv", "da", "no", "fi", "he"
        ]
    }
