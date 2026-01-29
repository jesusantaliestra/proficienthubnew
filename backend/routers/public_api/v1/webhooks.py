"""
Public API v1 - Webhooks Endpoints
Webhook configuration and management for event notifications
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import hmac
import hashlib
import json
import httpx

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read, require_write, require_admin

router = APIRouter(prefix="/webhooks", tags=["Webhooks API"])

# Available webhook events
WEBHOOK_EVENTS = [
    "student.created",
    "student.updated",
    "student.deleted",
    "exam.completed",
    "exam.passed",
    "exam.failed",
    "invoice.created",
    "invoice.paid",
    "invoice.overdue",
    "subscription.created",
    "subscription.cancelled",
    "subscription.renewed",
    "credits.low",
    "credits.depleted",
    "ai_tutor.session_completed"
]

# Models
class WebhookCreate(BaseModel):
    url: str
    events: List[str]
    description: Optional[str] = None
    is_active: bool = True
    secret: Optional[str] = None  # If not provided, one will be generated

class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    description: Optional[str]
    is_active: bool
    created_at: str
    last_triggered_at: Optional[str]
    success_count: int
    failure_count: int

class WebhookWithSecret(WebhookResponse):
    secret: str  # Only returned on creation

class WebhookDeliveryResponse(BaseModel):
    id: str
    webhook_id: str
    event: str
    payload: Dict[str, Any]
    status_code: Optional[int]
    response_body: Optional[str]
    success: bool
    created_at: str
    duration_ms: Optional[int]

# Helper functions
def generate_webhook_secret() -> str:
    """Generate a secure webhook secret"""
    import secrets
    return f"whsec_{secrets.token_urlsafe(32)}"

def sign_webhook_payload(payload: dict, secret: str) -> str:
    """Generate HMAC signature for webhook payload"""
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    signature = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

async def deliver_webhook(webhook: dict, event: str, payload: dict) -> dict:
    """Deliver a webhook and record the result"""
    delivery_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    # Sign the payload
    signature = sign_webhook_payload(payload, webhook.get("secret", ""))
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Event": event,
        "X-Webhook-Signature": signature,
        "X-Webhook-Delivery-Id": delivery_id,
        "User-Agent": "ProficientHub-Webhooks/1.0"
    }
    
    delivery_doc = {
        "id": delivery_id,
        "webhook_id": webhook["id"],
        "event": event,
        "payload": payload,
        "status_code": None,
        "response_body": None,
        "success": False,
        "created_at": start_time.isoformat(),
        "duration_ms": None
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook["url"],
                json=payload,
                headers=headers
            )
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            delivery_doc["status_code"] = response.status_code
            delivery_doc["response_body"] = response.text[:1000]  # Truncate
            delivery_doc["success"] = 200 <= response.status_code < 300
            delivery_doc["duration_ms"] = duration_ms
            
    except Exception as e:
        delivery_doc["response_body"] = str(e)
        delivery_doc["success"] = False
    
    # Store delivery record
    await db.webhook_deliveries.insert_one(delivery_doc)
    
    # Update webhook stats
    update_field = "success_count" if delivery_doc["success"] else "failure_count"
    await db.webhooks.update_one(
        {"id": webhook["id"]},
        {
            "$inc": {update_field: 1},
            "$set": {"last_triggered_at": start_time.isoformat()}
        }
    )
    
    return delivery_doc

# Public function to trigger webhooks (called from other modules)
async def trigger_webhook_event(owner_id: str, event: str, payload: dict):
    """Trigger all webhooks for a specific event"""
    webhooks = await db.webhooks.find({
        "owner_id": owner_id,
        "is_active": True,
        "events": event
    }).to_list(100)
    
    for webhook in webhooks:
        # Deliver async (fire and forget for now)
        await deliver_webhook(webhook, event, payload)

# Endpoints
@router.get("/events")
async def list_available_events(
    api_auth: dict = Depends(require_read)
):
    """List all available webhook events"""
    return {
        "events": WEBHOOK_EVENTS,
        "categories": {
            "student": [e for e in WEBHOOK_EVENTS if e.startswith("student.")],
            "exam": [e for e in WEBHOOK_EVENTS if e.startswith("exam.")],
            "invoice": [e for e in WEBHOOK_EVENTS if e.startswith("invoice.")],
            "subscription": [e for e in WEBHOOK_EVENTS if e.startswith("subscription.")],
            "credits": [e for e in WEBHOOK_EVENTS if e.startswith("credits.")],
            "ai_tutor": [e for e in WEBHOOK_EVENTS if e.startswith("ai_tutor.")]
        }
    }

@router.post("", response_model=WebhookWithSecret)
async def create_webhook(
    webhook_data: WebhookCreate,
    api_auth: dict = Depends(require_write)
):
    """Create a new webhook endpoint"""
    # Validate events
    invalid_events = [e for e in webhook_data.events if e not in WEBHOOK_EVENTS]
    if invalid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid events: {invalid_events}. Valid events: {WEBHOOK_EVENTS}"
        )
    
    webhook_id = str(uuid.uuid4())
    secret = webhook_data.secret or generate_webhook_secret()
    
    webhook_doc = {
        "id": webhook_id,
        "owner_id": api_auth["owner_id"],
        "url": webhook_data.url,
        "events": webhook_data.events,
        "description": webhook_data.description,
        "secret": secret,
        "is_active": webhook_data.is_active,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_triggered_at": None,
        "success_count": 0,
        "failure_count": 0
    }
    
    await db.webhooks.insert_one(webhook_doc)
    
    return WebhookWithSecret(
        id=webhook_id,
        url=webhook_data.url,
        events=webhook_data.events,
        description=webhook_data.description,
        is_active=webhook_data.is_active,
        created_at=webhook_doc["created_at"],
        last_triggered_at=None,
        success_count=0,
        failure_count=0,
        secret=secret
    )

@router.get("", response_model=List[WebhookResponse])
async def list_webhooks(
    api_auth: dict = Depends(require_read)
):
    """List all webhooks for the authenticated owner"""
    webhooks = await db.webhooks.find(
        {"owner_id": api_auth["owner_id"]},
        {"_id": 0, "secret": 0}  # Don't return secret in list
    ).to_list(100)
    
    return [WebhookResponse(**w) for w in webhooks]

@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get a single webhook by ID"""
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "owner_id": api_auth["owner_id"]},
        {"_id": 0, "secret": 0}
    )
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return WebhookResponse(**webhook)

@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    update_data: WebhookUpdate,
    api_auth: dict = Depends(require_write)
):
    """Update a webhook"""
    # Validate events if provided
    if update_data.events:
        invalid_events = [e for e in update_data.events if e not in WEBHOOK_EVENTS]
        if invalid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid events: {invalid_events}"
            )
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.webhooks.update_one(
        {"id": webhook_id, "owner_id": api_auth["owner_id"]},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return await get_webhook(webhook_id, api_auth)

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    api_auth: dict = Depends(require_write)
):
    """Delete a webhook"""
    result = await db.webhooks.delete_one({
        "id": webhook_id,
        "owner_id": api_auth["owner_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Also delete delivery history
    await db.webhook_deliveries.delete_many({"webhook_id": webhook_id})
    
    return {"message": "Webhook deleted successfully"}

@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    api_auth: dict = Depends(require_write)
):
    """Send a test event to a webhook"""
    webhook = await db.webhooks.find_one({
        "id": webhook_id,
        "owner_id": api_auth["owner_id"]
    })
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    test_payload = {
        "event": "test",
        "data": {
            "message": "This is a test webhook delivery",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "webhook_id": webhook_id
        }
    }
    
    result = await deliver_webhook(webhook, "test", test_payload)
    
    return {
        "success": result["success"],
        "status_code": result["status_code"],
        "response_body": result["response_body"],
        "duration_ms": result["duration_ms"]
    }

@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def list_webhook_deliveries(
    webhook_id: str,
    limit: int = 20,
    api_auth: dict = Depends(require_read)
):
    """List recent deliveries for a webhook"""
    # Verify ownership
    webhook = await db.webhooks.find_one({
        "id": webhook_id,
        "owner_id": api_auth["owner_id"]
    })
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    deliveries = await db.webhook_deliveries.find(
        {"webhook_id": webhook_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return [WebhookDeliveryResponse(**d) for d in deliveries]

@router.post("/{webhook_id}/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    webhook_id: str,
    delivery_id: str,
    api_auth: dict = Depends(require_write)
):
    """Retry a failed webhook delivery"""
    # Get webhook
    webhook = await db.webhooks.find_one({
        "id": webhook_id,
        "owner_id": api_auth["owner_id"]
    })
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Get original delivery
    delivery = await db.webhook_deliveries.find_one({
        "id": delivery_id,
        "webhook_id": webhook_id
    })
    
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    # Retry
    result = await deliver_webhook(webhook, delivery["event"], delivery["payload"])
    
    return {
        "success": result["success"],
        "new_delivery_id": result["id"],
        "status_code": result["status_code"]
    }

@router.post("/{webhook_id}/rotate-secret")
async def rotate_webhook_secret(
    webhook_id: str,
    api_auth: dict = Depends(require_write)
):
    """Rotate the webhook secret"""
    new_secret = generate_webhook_secret()
    
    result = await db.webhooks.update_one(
        {"id": webhook_id, "owner_id": api_auth["owner_id"]},
        {"$set": {"secret": new_secret, "secret_rotated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {
        "message": "Secret rotated successfully",
        "new_secret": new_secret
    }
