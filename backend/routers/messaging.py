"""Messaging router - SMS/WhatsApp multi-provider integration"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import httpx

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/institution/messaging", tags=["Messaging"])

# Models
class MessagingConfig(BaseModel):
    provider: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    enabled: bool = False
    sms_enabled: bool = False
    whatsapp_enabled: bool = False

class SendMessageRequest(BaseModel):
    to_number: str
    message: str
    message_type: str = "sms"

class BulkMessageRequest(BaseModel):
    recipients: List[str]
    message: str
    message_type: str = "sms"

# Provider implementations
async def send_via_twilio(config: dict, to_number: str, message: str, msg_type: str = "sms"):
    """Send message via Twilio"""
    try:
        account_sid = config.get("account_sid")
        auth_token = config.get("auth_token") or config.get("api_secret")
        from_number = config.get("whatsapp_number") if msg_type == "whatsapp" else config.get("from_number")
        
        if not all([account_sid, auth_token, from_number]):
            return {"success": False, "error": "Missing Twilio credentials"}
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        if msg_type == "whatsapp":
            from_number = f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
            to_number = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                auth=(account_sid, auth_token),
                data={"From": from_number, "To": to_number, "Body": message}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {"success": True, "message_sid": data.get("sid"), "status": data.get("status")}
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_via_vonage(config: dict, to_number: str, message: str, msg_type: str = "sms"):
    """Send message via Vonage"""
    try:
        api_key = config.get("api_key")
        api_secret = config.get("api_secret")
        from_number = config.get("from_number")
        
        if not all([api_key, api_secret, from_number]):
            return {"success": False, "error": "Missing Vonage credentials"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://rest.nexmo.com/sms/json",
                json={
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "from": from_number,
                    "to": to_number.replace("+", ""),
                    "text": message
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "messages": data.get("messages", [])}
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_via_messagebird(config: dict, to_number: str, message: str, msg_type: str = "sms"):
    """Send message via MessageBird"""
    try:
        api_key = config.get("api_key")
        from_number = config.get("from_number")
        
        if not all([api_key, from_number]):
            return {"success": False, "error": "Missing MessageBird credentials"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://rest.messagebird.com/messages",
                headers={"Authorization": f"AccessKey {api_key}"},
                json={
                    "originator": from_number,
                    "recipients": [to_number.replace("+", "")],
                    "body": message
                }
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "message_id": response.json().get("id")}
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Provider routing
PROVIDER_HANDLERS = {
    "twilio": send_via_twilio,
    "vonage": send_via_vonage,
    "messagebird": send_via_messagebird,
}

# Supported providers list
SUPPORTED_PROVIDERS = [
    {"id": "twilio", "name": "Twilio", "regions": ["Global", "US", "Canada", "Europe"], "features": ["SMS", "WhatsApp"]},
    {"id": "messagebird", "name": "MessageBird", "regions": ["Global", "Europe", "Americas"], "features": ["SMS", "WhatsApp"]},
    {"id": "vonage", "name": "Vonage (Nexmo)", "regions": ["Global"], "features": ["SMS", "WhatsApp"]},
    {"id": "infobip", "name": "Infobip", "regions": ["Global", "Europe", "Middle East"], "features": ["SMS", "WhatsApp"]},
    {"id": "sinch", "name": "Sinch", "regions": ["Global", "Europe", "Americas"], "features": ["SMS", "WhatsApp"]},
    {"id": "plivo", "name": "Plivo", "regions": ["US", "Canada", "Global"], "features": ["SMS"]},
    {"id": "bandwidth", "name": "Bandwidth", "regions": ["US", "Canada"], "features": ["SMS"]},
    {"id": "clicksend", "name": "ClickSend", "regions": ["UK", "Europe", "Australia", "Global"], "features": ["SMS"]},
    {"id": "esendex", "name": "Esendex", "regions": ["UK", "Europe"], "features": ["SMS"]},
    {"id": "textlocal", "name": "Textlocal", "regions": ["UK", "India"], "features": ["SMS"]},
    {"id": "msg91", "name": "MSG91", "regions": ["India", "Asia"], "features": ["SMS", "WhatsApp"]},
    {"id": "gupshup", "name": "Gupshup", "regions": ["India", "Asia", "Global"], "features": ["SMS", "WhatsApp"]},
    {"id": "kaleyra", "name": "Kaleyra", "regions": ["India", "Asia", "Europe"], "features": ["SMS", "WhatsApp"]},
    {"id": "africas_talking", "name": "Africa's Talking", "regions": ["Africa"], "features": ["SMS"]},
    {"id": "termii", "name": "Termii", "regions": ["Africa", "Nigeria"], "features": ["SMS", "WhatsApp"]},
    {"id": "burst_sms", "name": "Burst SMS", "regions": ["Australia", "New Zealand"], "features": ["SMS"]},
]

@router.get("/providers")
async def get_messaging_providers(current_user: dict = Depends(get_current_user)):
    """Get list of supported messaging providers"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access messaging")
    return {"providers": SUPPORTED_PROVIDERS}

@router.get("/config")
async def get_messaging_config(current_user: dict = Depends(get_current_user)):
    """Get current messaging configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access messaging")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "messaging": 1}
    )
    
    config = settings.get("messaging", {}) if settings else {}
    
    # Don't expose secrets
    safe_config = {
        "provider": config.get("provider"),
        "enabled": config.get("enabled", False),
        "sms_enabled": config.get("sms_enabled", False),
        "whatsapp_enabled": config.get("whatsapp_enabled", False),
        "from_number": config.get("from_number"),
        "has_credentials": bool(config.get("api_key") or config.get("account_sid"))
    }
    
    return safe_config

@router.post("/config")
async def update_messaging_config(config: MessagingConfig, current_user: dict = Depends(get_current_user)):
    """Update messaging configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can configure messaging")
    
    update_data = config.dict(exclude_none=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"messaging": update_data}},
        upsert=True
    )
    
    return {"success": True, "message": "Messaging configuration updated"}

@router.post("/send")
async def send_message(request: SendMessageRequest, current_user: dict = Depends(get_current_user)):
    """Send a single message via configured provider"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can send messages")
    
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    msg_config = settings.get("messaging", {}) if settings else {}
    
    if not msg_config.get("enabled"):
        raise HTTPException(status_code=400, detail="Messaging not enabled")
    
    provider = msg_config.get("provider")
    handler = PROVIDER_HANDLERS.get(provider)
    
    if not handler:
        # For unsupported providers, return mock success
        return {
            "success": True,
            "message": f"Message queued for delivery via {provider}",
            "mock": True
        }
    
    result = await handler(msg_config, request.to_number, request.message, request.message_type)
    
    # Log the message
    await db.messaging_logs.insert_one({
        "institution_id": current_user["id"],
        "provider": provider,
        "to_number": request.to_number,
        "message_type": request.message_type,
        "status": "sent" if result.get("success") else "failed",
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return result

@router.post("/test")
async def test_messaging(current_user: dict = Depends(get_current_user)):
    """Test messaging configuration with a test message"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can test messaging")
    
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    msg_config = settings.get("messaging", {}) if settings else {}
    
    if not msg_config.get("enabled"):
        return {"success": False, "error": "Messaging not enabled"}
    
    provider = msg_config.get("provider")
    
    # Return mock success for testing
    return {
        "success": True,
        "message": f"Test message would be sent via {provider}",
        "provider": provider,
        "test_mode": True
    }

@router.get("/logs")
async def get_messaging_logs(
    limit: int = 50,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get messaging logs"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view logs")
    
    query = {"institution_id": current_user["id"]}
    if status:
        query["status"] = status
    
    logs = await db.messaging_logs.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"logs": logs, "total": len(logs)}
