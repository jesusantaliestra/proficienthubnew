"""Zoom integration router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
import uuid
import httpx
import jwt as pyjwt
import time

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/zoom", tags=["Zoom"])

class ZoomMeetingCreate(BaseModel):
    topic: str
    start_time: str  # ISO format
    duration: int = 60
    description: Optional[str] = None
    password: Optional[str] = None
    waiting_room: bool = True
    join_before_host: bool = False
    mute_upon_entry: bool = True

class ZoomMeetingUpdate(BaseModel):
    topic: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[int] = None
    description: Optional[str] = None

async def get_zoom_access_token(zoom_config: dict) -> str:
    """Get OAuth access token from Zoom"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://zoom.us/oauth/token",
            params={
                "grant_type": "account_credentials",
                "account_id": zoom_config["zoom_account_id"]
            },
            auth=(zoom_config["zoom_client_id"], zoom_config["zoom_client_secret"]),
            timeout=15.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Zoom authentication failed: {response.text}")
        
        return response.json()["access_token"]

@router.post("/meetings/create")
async def create_zoom_meeting(
    meeting: ZoomMeetingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new Zoom meeting"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create meetings")
    
    # Get Zoom settings
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not zoom_config.get("zoom_enabled"):
        raise HTTPException(status_code=400, detail="Zoom not enabled. Please enable Zoom in settings.")
    
    if not all([zoom_config.get("zoom_account_id"), zoom_config.get("zoom_client_id"), zoom_config.get("zoom_client_secret")]):
        raise HTTPException(status_code=400, detail="Zoom credentials not configured. Please configure Zoom in settings.")
    
    try:
        access_token = await get_zoom_access_token(zoom_config)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.zoom.us/v2/users/me/meetings",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "topic": meeting.topic,
                    "type": 2,  # Scheduled meeting
                    "start_time": meeting.start_time,
                    "duration": meeting.duration,
                    "agenda": meeting.description or "",
                    "password": meeting.password,
                    "settings": {
                        "host_video": True,
                        "participant_video": True,
                        "join_before_host": meeting.join_before_host,
                        "waiting_room": meeting.waiting_room,
                        "mute_upon_entry": meeting.mute_upon_entry,
                        "auto_recording": "none"
                    }
                },
                timeout=15.0
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(status_code=400, detail=f"Failed to create Zoom meeting: {response.text}")
            
            meeting_data = response.json()
            
            # Store in database
            meeting_doc = {
                "id": str(uuid.uuid4()),
                "zoom_meeting_id": str(meeting_data["id"]),
                "institution_id": current_user["id"],
                "topic": meeting.topic,
                "description": meeting.description,
                "start_time": meeting.start_time,
                "duration": meeting.duration,
                "join_url": meeting_data["join_url"],
                "start_url": meeting_data["start_url"],
                "password": meeting_data.get("password", ""),
                "status": "scheduled",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.zoom_meetings.insert_one(meeting_doc)
            
            return {
                "id": meeting_doc["id"],
                "zoom_meeting_id": meeting_data["id"],
                "topic": meeting.topic,
                "start_time": meeting.start_time,
                "duration": meeting.duration,
                "join_url": meeting_data["join_url"],
                "start_url": meeting_data["start_url"],
                "password": meeting_data.get("password", ""),
                "created_at": meeting_doc["created_at"]
            }
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Zoom API error: {str(e)}")

@router.get("/meetings")
async def list_zoom_meetings(
    status: Optional[str] = Query(default=None, enum=["scheduled", "started", "ended"]),
    limit: int = Query(default=20, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List Zoom meetings for the institution"""
    if current_user["user_type"] not in ["institution", "student"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    query = {"institution_id": institution_id}
    if status:
        query["status"] = status
    
    meetings = await db.zoom_meetings.find(
        query,
        {"_id": 0}
    ).sort("start_time", 1).limit(limit).to_list(limit)
    
    # Mark meetings as past if start_time has passed
    now = datetime.now(timezone.utc).isoformat()
    for meeting in meetings:
        if meeting.get("start_time") and meeting.get("start_time") < now:
            if meeting.get("status") == "scheduled":
                meeting["status"] = "past"
    
    return {"meetings": meetings, "total": len(meetings)}

@router.get("/meetings/{meeting_id}")
async def get_zoom_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific Zoom meeting"""
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    meeting = await db.zoom_meetings.find_one(
        {"id": meeting_id, "institution_id": institution_id},
        {"_id": 0}
    )
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting

@router.put("/meetings/{meeting_id}")
async def update_zoom_meeting(
    meeting_id: str,
    update: ZoomMeetingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a Zoom meeting"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update meetings")
    
    meeting = await db.zoom_meetings.find_one({"id": meeting_id, "institution_id": current_user["id"]})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Get Zoom settings
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not zoom_config.get("zoom_enabled"):
        raise HTTPException(status_code=400, detail="Zoom not enabled")
    
    try:
        access_token = await get_zoom_access_token(zoom_config)
        
        # Prepare update data
        zoom_update = {}
        if update.topic:
            zoom_update["topic"] = update.topic
        if update.start_time:
            zoom_update["start_time"] = update.start_time
        if update.duration:
            zoom_update["duration"] = update.duration
        if update.description:
            zoom_update["agenda"] = update.description
        
        if zoom_update:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"https://api.zoom.us/v2/meetings/{meeting['zoom_meeting_id']}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=zoom_update,
                    timeout=15.0
                )
                
                if response.status_code not in [200, 204]:
                    raise HTTPException(status_code=400, detail=f"Failed to update Zoom meeting: {response.text}")
        
        # Update local database
        db_update = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if update.topic:
            db_update["topic"] = update.topic
        if update.start_time:
            db_update["start_time"] = update.start_time
        if update.duration:
            db_update["duration"] = update.duration
        if update.description:
            db_update["description"] = update.description
        
        await db.zoom_meetings.update_one({"id": meeting_id}, {"$set": db_update})
        
        return {"success": True, "message": "Meeting updated successfully"}
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Zoom API error: {str(e)}")

@router.delete("/meetings/{meeting_id}")
async def delete_zoom_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a Zoom meeting"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can delete meetings")
    
    meeting = await db.zoom_meetings.find_one({"id": meeting_id, "institution_id": current_user["id"]})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Get Zoom settings
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if zoom_config.get("zoom_enabled") and meeting.get("zoom_meeting_id"):
        try:
            access_token = await get_zoom_access_token(zoom_config)
            
            async with httpx.AsyncClient() as client:
                await client.delete(
                    f"https://api.zoom.us/v2/meetings/{meeting['zoom_meeting_id']}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=15.0
                )
        except Exception as e:
            # Log error but continue with local deletion
            pass
    
    await db.zoom_meetings.delete_one({"id": meeting_id})
    
    return {"success": True, "message": "Meeting deleted successfully"}

@router.get("/meetings/{meeting_id}/signature")
async def get_zoom_signature(
    meeting_id: str,
    role: int = Query(default=0, ge=0, le=1),  # 0 = participant, 1 = host
    current_user: dict = Depends(get_current_user)
):
    """Generate SDK signature for joining a Zoom meeting"""
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    meeting = await db.zoom_meetings.find_one({"id": meeting_id, "institution_id": institution_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    settings = await db.institution_settings.find_one({"institution_id": institution_id})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not zoom_config.get("zoom_client_id") or not zoom_config.get("zoom_client_secret"):
        raise HTTPException(status_code=400, detail="Zoom SDK credentials not configured")
    
    # Generate SDK signature
    iat = int(time.time())
    exp = iat + 60 * 60 * 2  # 2 hours
    
    payload = {
        "appKey": zoom_config["zoom_client_id"],
        "mn": int(meeting["zoom_meeting_id"]),
        "role": role,
        "iat": iat,
        "exp": exp,
        "tokenExp": exp
    }
    
    signature = pyjwt.encode(
        payload,
        zoom_config["zoom_client_secret"],
        algorithm="HS256"
    )
    
    return {
        "signature": signature,
        "meeting_number": meeting["zoom_meeting_id"],
        "sdk_key": zoom_config["zoom_client_id"],
        "password": meeting.get("password", ""),
        "topic": meeting.get("topic")
    }

@router.post("/test-connection")
async def test_zoom_connection(current_user: dict = Depends(get_current_user)):
    """Test Zoom API connection with configured credentials"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can test Zoom connection")
    
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    zoom_config = settings.get("zoom", {}) if settings else {}
    
    if not all([zoom_config.get("zoom_account_id"), zoom_config.get("zoom_client_id"), zoom_config.get("zoom_client_secret")]):
        return {
            "success": False,
            "error": "Zoom credentials not fully configured",
            "missing": [k for k in ["zoom_account_id", "zoom_client_id", "zoom_client_secret"] if not zoom_config.get(k)]
        }
    
    try:
        access_token = await get_zoom_access_token(zoom_config)
        
        # Test by getting user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.zoom.us/v2/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "Zoom connection successful",
                    "account_email": user_data.get("email"),
                    "account_type": user_data.get("type")
                }
            else:
                return {
                    "success": False,
                    "error": f"Zoom API returned error: {response.text}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
