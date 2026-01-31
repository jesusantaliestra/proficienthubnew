"""OET Speaking Mock Router - Dynamic Speaking Test with HeyGen Avatar

This module implements a dynamic OET Speaking test where:
- The HeyGen avatar plays the role of the PATIENT
- The student plays the role of the NURSE
- Speech is transcribed in real-time using Whisper
- An LLM generates dynamic patient responses based on the role-play card
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os
import uuid
import httpx
import tempfile
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/oet-speaking", tags=["OET Speaking Mock"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency
from server import get_current_user

# Emergent integrations
from emergentintegrations.llm.openai import LlmChat, UserMessage

EMERGENT_KEY = os.getenv("EMERGENT_LLM_KEY")

# HeyGen configuration
HEYGEN_API_KEY = None  # Will be loaded from DB

# Avatar and Voice configurations for OET role-plays
ROLE_PLAY_CONFIGS = {
    "S-012-B": {
        "patient_name": "Mr. Graham Webb",
        "patient_age": 58,
        "patient_gender": "male",
        "avatar_id": "Aditya_public_4",  # Male avatar
        "voice_id": "2eca0d3dd5ec4a1ea6efa6194b19eb78",  # Ray (male voice)
        "setting": "Diabetes clinic",
        "scenario": "Medication Change - Treatment Fatigue",
        "patient_background": """You are Graham Webb, 58 years old, warehouse supervisor.
You have had Type 2 diabetes for 7 years and have been taking metformin since diagnosis.
You have worked hard on your diet and lost weight over the years.
Your recent blood test showed your diabetes control has worsened, and the consultant has now added another tablet (empagliflozin) to your treatment.

YOUR FEELINGS: You are frustrated and tired. You feel like you have been doing everything right but your body is 'letting you down'. You are reluctant to add another medication because you worry about becoming 'a pill for everything' patient. You are also concerned because when metformin was first started, you had terrible digestive problems for weeks.

KEY CONCERNS to express:
- 'I've worked so hard on my diet - why isn't it enough?'
- 'Will this new tablet make me feel ill like the metformin did at first?'
- 'How many tablets am I going to end up on?'
- 'My wife's worried - she thinks diabetes just gets worse no matter what you do.'

BEHAVIOUR: Start off sounding defeated and tired rather than angry. Respond well to acknowledgement of your efforts. Ask specific questions about side effects. If the nurse acknowledges your frustration and explains things clearly, gradually become more willing to try the new medication.""",
        "opening_line": "Oh, hello nurse. I suppose you're here to talk about these new tablets they want me to take. *sighs* I've just about had enough of all this, to be honest.",
        "exam_info": {
            "exam_type": "OET",
            "sub_test": "Speaking",
            "role_play_number": 1,
            "topic_id": "S-012-B"
        }
    },
    "S-046-C": {
        "patient_name": "Mrs. Patricia Holloway",
        "patient_age": 71,
        "patient_gender": "female",
        "avatar_id": "Abigail_expressive_2024112501",  # Female avatar
        "voice_id": "M2WosQ2Ju3f2b7jdddsj",  # Amy (female voice)
        "setting": "Medical ward, day of discharge",
        "scenario": "Patient Education - Warning Signs",
        "patient_background": """You are Patricia Holloway, 71 years old, retired teacher.
You were admitted 5 days ago with a painful swollen leg which turned out to be a blood clot (DVT). You are now going home on blood-thinning tablets (rivaroxaban).
You are relieved to be going home but feel overwhelmed by all the information you have been given.
You are particularly worried because your neighbour had a blood clot and ended up having a clot in her lungs which was 'very serious'.

YOUR FEELINGS: You are anxious but trying to appear calm. You tend to ask lots of questions because you like to understand things properly (you were a teacher for 35 years). You are worried about being at home alone and something going wrong.

KEY CONCERNS to express:
- 'My neighbour had a clot that went to her lungs - how would I know if that was happening?'
- 'If I cut myself, will I bleed to death?'
- 'What if something happens in the middle of the night?'
- 'There's so much to remember - can I write this down?'

BEHAVIOUR: Ask for clarification if medical terms are used without explanation. Express relief when key symptoms are clearly explained. Ask practical questions like 'So if I see X, I should do Y?'. If overwhelmed with too much information at once, look confused and ask them to slow down.""",
        "opening_line": "Oh, hello nurse. I'm so glad someone's come to explain things before I go home. I must admit, I'm feeling a bit nervous about leaving. My neighbour, you see, she had something similar and it went to her lungs...",
        "exam_info": {
            "exam_type": "OET",
            "sub_test": "Speaking",
            "role_play_number": 2,
            "topic_id": "S-046-C"
        }
    }
}


class StartSessionRequest(BaseModel):
    role_play_id: str
    student_name: Optional[str] = None


class StudentMessageRequest(BaseModel):
    session_id: str
    audio_base64: Optional[str] = None  # Base64 encoded audio
    text: Optional[str] = None  # Or direct text input for testing


class SessionResponse(BaseModel):
    session_id: str
    role_play_id: str
    patient_name: str
    setting: str
    scenario: str
    avatar_id: str
    status: str


async def get_heygen_api_key():
    """Get HeyGen API key from database"""
    config = await db.platform_config.find_one({"config_type": "heygen"})
    if config and config.get("api_key"):
        return config["api_key"]
    return os.getenv("HEYGEN_API_KEY")


async def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using Whisper"""
    try:
        stt = OpenAISpeechToText(api_key=EMERGENT_KEY)
        
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        with open(tmp_path, "rb") as audio_file:
            response = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                language="en",
                response_format="json"
            )
        
        os.unlink(tmp_path)
        return response.text
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


async def generate_patient_response(
    role_play_config: dict,
    conversation_history: list,
    nurse_message: str
) -> str:
    """Generate dynamic patient response using LLM"""
    
    system_prompt = f"""You are simulating a patient in an OET Speaking test role-play.

PATIENT DETAILS:
Name: {role_play_config['patient_name']}
Age: {role_play_config['patient_age']}
Setting: {role_play_config['setting']}

PATIENT BACKGROUND AND BEHAVIOUR:
{role_play_config['patient_background']}

INSTRUCTIONS:
1. Stay in character as the patient at all times
2. Respond naturally to what the nurse says
3. Express your concerns and feelings authentically
4. If the nurse shows empathy and explains well, become more cooperative
5. If the nurse is dismissive or too clinical, remain hesitant
6. Keep responses conversational - 1-3 sentences typically
7. Include natural hesitations, pauses, and emotions
8. Ask follow-up questions when appropriate
9. Never break character or mention this is a test

Remember: You are the PATIENT, not the nurse. The student is practicing their nursing communication skills."""

    # Build initial messages for context
    initial_messages = []
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        if msg["role"] == "patient":
            initial_messages.append({"role": "assistant", "content": msg["content"]})
        else:
            initial_messages.append({"role": "user", "content": msg["content"]})
    
    try:
        # Create unique session ID for this interaction
        session_id = f"oet-{uuid.uuid4()}"
        
        llm = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=session_id,
            system_message=system_prompt,
            initial_messages=initial_messages
        )
        
        msg = UserMessage(text=f"Nurse says: {nurse_message}")
        response = await llm.send_message(user_message=msg)
        return response  # Response is directly a string
    except Exception as e:
        print(f"LLM error: {e}")
        # Fallback response
        return "I'm sorry, could you repeat that? I didn't quite catch what you said."


async def generate_heygen_video(text: str, avatar_id: str, voice_id: str) -> dict:
    """Generate video response using HeyGen API"""
    api_key = await get_heygen_api_key()
    
    if not api_key:
        raise HTTPException(status_code=500, detail="HeyGen API key not configured")
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.heygen.com/v2/video/generate",
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": text,
                        "voice_id": voice_id
                    }
                }],
                "dimension": {
                    "width": 1280,
                    "height": 720
                },
                "test": False
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HeyGen API error: {response.text}"
            )
        
        return response.json()


# =============================================
# API Endpoints
# =============================================

@router.get("/role-plays")
async def get_available_role_plays():
    """Get list of available OET Speaking role-plays"""
    role_plays = []
    for rp_id, config in ROLE_PLAY_CONFIGS.items():
        role_plays.append({
            "id": rp_id,
            "patient_name": config["patient_name"],
            "patient_age": config["patient_age"],
            "patient_gender": config["patient_gender"],
            "setting": config["setting"],
            "scenario": config["scenario"],
            "exam_info": config["exam_info"]
        })
    return {"role_plays": role_plays}


@router.get("/role-play/{role_play_id}")
async def get_role_play_details(role_play_id: str):
    """Get details of a specific role-play (for candidate card display)"""
    if role_play_id not in ROLE_PLAY_CONFIGS:
        raise HTTPException(status_code=404, detail="Role-play not found")
    
    config = ROLE_PLAY_CONFIGS[role_play_id]
    
    # Return candidate card info (not the full patient background)
    return {
        "id": role_play_id,
        "patient_name": config["patient_name"],
        "patient_age": config["patient_age"],
        "setting": config["setting"],
        "scenario": config["scenario"],
        "exam_info": config["exam_info"],
        "candidate_task": get_candidate_task(role_play_id)
    }


def get_candidate_task(role_play_id: str) -> str:
    """Get the candidate task description for a role-play"""
    tasks = {
        "S-012-B": """TASK:
• Explore Mr Webb's feelings about adding another medication to his regimen
• Explain why the additional medication is needed and how it works
• Address his concerns about side effects, particularly given his previous experience
• Negotiate a plan that acknowledges his feelings while ensuring he understands the importance of treatment""",
        "S-046-C": """TASK:
• Educate Mrs Holloway about warning signs that would require urgent medical attention (particularly symptoms of pulmonary embolism)
• Explain how to recognise and respond to bleeding problems while on anticoagulant medication
• Address her concerns and questions without overwhelming her with information
• Ensure she knows who to contact if she has concerns"""
    }
    return tasks.get(role_play_id, "")


@router.post("/session/start")
async def start_speaking_session(
    request: StartSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start a new OET Speaking mock session"""
    
    if request.role_play_id not in ROLE_PLAY_CONFIGS:
        raise HTTPException(status_code=404, detail="Role-play not found")
    
    config = ROLE_PLAY_CONFIGS[request.role_play_id]
    session_id = str(uuid.uuid4())
    
    # Create session record
    session = {
        "id": session_id,
        "user_id": current_user["id"],
        "student_name": request.student_name or current_user.get("name", "Student"),
        "role_play_id": request.role_play_id,
        "patient_name": config["patient_name"],
        "setting": config["setting"],
        "scenario": config["scenario"],
        "avatar_id": config["avatar_id"],
        "voice_id": config["voice_id"],
        "status": "active",
        "conversation_history": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "institution_id": current_user.get("institution_id")
    }
    
    # Add opening line from patient
    session["conversation_history"].append({
        "role": "patient",
        "content": config["opening_line"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    await db.oet_speaking_sessions.insert_one(session)
    
    return {
        "session_id": session_id,
        "role_play_id": request.role_play_id,
        "patient_name": config["patient_name"],
        "setting": config["setting"],
        "scenario": config["scenario"],
        "avatar_id": config["avatar_id"],
        "opening_message": config["opening_line"],
        "status": "active",
        "message": "Session started. The patient is ready to speak with you."
    }


@router.post("/session/respond")
async def process_nurse_response(
    request: StudentMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process nurse's response and generate patient reply"""
    
    # Get session
    session = await db.oet_speaking_sessions.find_one({
        "id": request.session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get nurse's message (either from audio or text)
    nurse_message = request.text
    if request.audio_base64 and not nurse_message:
        import base64
        audio_data = base64.b64decode(request.audio_base64)
        nurse_message = await transcribe_audio(audio_data)
    
    if not nurse_message:
        raise HTTPException(status_code=400, detail="No message provided")
    
    # Get role-play config
    config = ROLE_PLAY_CONFIGS[session["role_play_id"]]
    
    # Add nurse message to history
    conversation_history = session.get("conversation_history", [])
    conversation_history.append({
        "role": "nurse",
        "content": nurse_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Generate patient response
    patient_response = await generate_patient_response(
        config,
        conversation_history,
        nurse_message
    )
    
    # Add patient response to history
    conversation_history.append({
        "role": "patient",
        "content": patient_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Update session
    await db.oet_speaking_sessions.update_one(
        {"id": request.session_id},
        {"$set": {
            "conversation_history": conversation_history,
            "last_activity": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Generate video for patient response
    video_info = None
    try:
        video_result = await generate_heygen_video(
            patient_response,
            config["avatar_id"],
            config["voice_id"]
        )
        video_info = {
            "video_id": video_result.get("data", {}).get("video_id"),
            "status": "processing"
        }
    except Exception as e:
        print(f"Video generation error: {e}")
        video_info = {"error": str(e)}
    
    return {
        "session_id": request.session_id,
        "nurse_message": nurse_message,
        "patient_response": patient_response,
        "video": video_info,
        "turn_number": len([m for m in conversation_history if m["role"] == "nurse"])
    }


@router.post("/session/respond-text")
async def process_nurse_response_text_only(
    request: StudentMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process nurse's response (text only, no video generation) - for faster testing"""
    
    session = await db.oet_speaking_sessions.find_one({
        "id": request.session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    nurse_message = request.text
    if not nurse_message:
        raise HTTPException(status_code=400, detail="No message provided")
    
    config = ROLE_PLAY_CONFIGS[session["role_play_id"]]
    conversation_history = session.get("conversation_history", [])
    
    conversation_history.append({
        "role": "nurse",
        "content": nurse_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    patient_response = await generate_patient_response(
        config,
        conversation_history,
        nurse_message
    )
    
    conversation_history.append({
        "role": "patient",
        "content": patient_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    await db.oet_speaking_sessions.update_one(
        {"id": request.session_id},
        {"$set": {
            "conversation_history": conversation_history,
            "last_activity": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "session_id": request.session_id,
        "nurse_message": nurse_message,
        "patient_response": patient_response,
        "turn_number": len([m for m in conversation_history if m["role"] == "nurse"])
    }


@router.post("/session/transcribe")
async def transcribe_audio_endpoint(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Transcribe audio file to text using Whisper"""
    
    audio_data = await audio.read()
    
    if len(audio_data) > 25 * 1024 * 1024:  # 25MB limit
        raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
    
    transcript = await transcribe_audio(audio_data)
    
    return {
        "transcript": transcript,
        "audio_size": len(audio_data)
    }


@router.post("/session/end")
async def end_speaking_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a speaking session and get summary"""
    
    session = await db.oet_speaking_sessions.find_one({
        "id": session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation_history = session.get("conversation_history", [])
    nurse_turns = [m for m in conversation_history if m["role"] == "nurse"]
    patient_turns = [m for m in conversation_history if m["role"] == "patient"]
    
    # Update session status
    await db.oet_speaking_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": "completed",
            "ended_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "session_id": session_id,
        "status": "completed",
        "summary": {
            "role_play": session["role_play_id"],
            "patient_name": session["patient_name"],
            "total_turns": len(nurse_turns),
            "duration_minutes": calculate_duration(session),
            "conversation_length": len(conversation_history)
        },
        "conversation_history": conversation_history
    }


def calculate_duration(session: dict) -> float:
    """Calculate session duration in minutes"""
    try:
        start = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
        end = datetime.now(timezone.utc)
        if session.get("ended_at"):
            end = datetime.fromisoformat(session["ended_at"].replace("Z", "+00:00"))
        return round((end - start).total_seconds() / 60, 1)
    except:
        return 0


@router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a speaking session"""
    
    session = await db.oet_speaking_sessions.find_one(
        {"id": session_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.get("/sessions")
async def get_user_sessions(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's speaking session history"""
    
    sessions = await db.oet_speaking_sessions.find(
        {"user_id": current_user["id"]},
        {"_id": 0, "conversation_history": 0}
    ).sort("started_at", -1).limit(limit).to_list(limit)
    
    return {"sessions": sessions, "count": len(sessions)}
