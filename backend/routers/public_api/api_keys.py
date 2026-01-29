"""
Public API - API Keys Management
Handles API key generation, validation, and rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import secrets
import hashlib
from functools import wraps

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

# Models
class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scopes: List[str] = ["read"]  # read, write, admin
    rate_limit: int = 1000  # requests per hour
    expires_in_days: Optional[int] = 365  # None = never expires

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str  # First 8 chars for identification
    scopes: List[str]
    rate_limit: int
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]
    is_active: bool
    usage_count: int

class APIKeyFullResponse(APIKeyResponse):
    """Only returned once when key is created"""
    api_key: str  # Full key - only shown once!

# Utility functions
def generate_api_key() -> tuple[str, str]:
    """Generate a secure API key and its hash"""
    # Format: ph_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 random chars)
    raw_key = f"ph_live_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash

def hash_api_key(key: str) -> str:
    """Hash an API key for storage/comparison"""
    return hashlib.sha256(key.encode()).hexdigest()

async def validate_api_key(api_key: str) -> dict:
    """Validate an API key and return the associated data"""
    key_hash = hash_api_key(api_key)
    
    key_doc = await db.api_keys.find_one(
        {"key_hash": key_hash, "is_active": True},
        {"_id": 0}
    )
    
    if not key_doc:
        return None
    
    # Check expiration
    if key_doc.get("expires_at"):
        expires_at = datetime.fromisoformat(key_doc["expires_at"].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) > expires_at:
            return None
    
    # Update last used
    await db.api_keys.update_one(
        {"id": key_doc["id"]},
        {
            "$set": {"last_used_at": datetime.now(timezone.utc).isoformat()},
            "$inc": {"usage_count": 1}
        }
    )
    
    return key_doc

async def check_rate_limit(key_id: str, rate_limit: int) -> bool:
    """Check if API key has exceeded rate limit"""
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    
    request_count = await db.api_requests.count_documents({
        "api_key_id": key_id,
        "timestamp": {"$gte": hour_ago.isoformat()}
    })
    
    return request_count < rate_limit

async def log_api_request(key_id: str, endpoint: str, method: str, status_code: int):
    """Log an API request for rate limiting and analytics"""
    await db.api_requests.insert_one({
        "id": str(uuid.uuid4()),
        "api_key_id": key_id,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# Endpoints
@router.post("", response_model=APIKeyFullResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new API key for programmatic access.
    The full key is only shown ONCE - store it securely!
    """
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions and admins can create API keys")
    
    # Generate key
    raw_key, key_hash = generate_api_key()
    key_id = str(uuid.uuid4())
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)).isoformat()
    
    key_doc = {
        "id": key_id,
        "owner_id": current_user["id"],
        "owner_type": current_user["user_type"],
        "name": key_data.name,
        "description": key_data.description,
        "key_hash": key_hash,
        "key_prefix": raw_key[:16],  # ph_live_xxxxxxxx
        "scopes": key_data.scopes,
        "rate_limit": key_data.rate_limit,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at,
        "last_used_at": None,
        "is_active": True,
        "usage_count": 0
    }
    
    await db.api_keys.insert_one(key_doc)
    
    return APIKeyFullResponse(
        id=key_id,
        name=key_data.name,
        key_prefix=raw_key[:16],
        scopes=key_data.scopes,
        rate_limit=key_data.rate_limit,
        created_at=key_doc["created_at"],
        expires_at=expires_at,
        last_used_at=None,
        is_active=True,
        usage_count=0,
        api_key=raw_key  # Only time the full key is returned!
    )

@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """List all API keys for the current user/institution"""
    keys = await db.api_keys.find(
        {"owner_id": current_user["id"]},
        {"_id": 0, "key_hash": 0}  # Never return the hash
    ).to_list(100)
    
    return [APIKeyResponse(**k) for k in keys]

@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke (deactivate) an API key"""
    result = await db.api_keys.update_one(
        {"id": key_id, "owner_id": current_user["id"]},
        {"$set": {"is_active": False, "revoked_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {"message": "API key revoked successfully"}

@router.post("/{key_id}/rotate")
async def rotate_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Rotate an API key - generates a new key while keeping the same settings.
    The old key is immediately invalidated.
    """
    # Get existing key
    existing_key = await db.api_keys.find_one(
        {"id": key_id, "owner_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not existing_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Generate new key
    raw_key, key_hash = generate_api_key()
    
    # Update with new key
    await db.api_keys.update_one(
        {"id": key_id},
        {
            "$set": {
                "key_hash": key_hash,
                "key_prefix": raw_key[:16],
                "rotated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "API key rotated successfully",
        "api_key": raw_key,  # Only time new key is shown
        "key_prefix": raw_key[:16]
    }

@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get usage statistics for an API key"""
    # Verify ownership
    key = await db.api_keys.find_one(
        {"id": key_id, "owner_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Aggregate usage by day
    pipeline = [
        {
            "$match": {
                "api_key_id": key_id,
                "timestamp": {"$gte": start_date.isoformat()}
            }
        },
        {
            "$group": {
                "_id": {"$substr": ["$timestamp", 0, 10]},  # Group by date
                "requests": {"$sum": 1},
                "endpoints": {"$addToSet": "$endpoint"},
                "errors": {
                    "$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
                }
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_stats = await db.api_requests.aggregate(pipeline).to_list(days)
    
    # Top endpoints
    endpoint_pipeline = [
        {
            "$match": {
                "api_key_id": key_id,
                "timestamp": {"$gte": start_date.isoformat()}
            }
        },
        {
            "$group": {
                "_id": "$endpoint",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    top_endpoints = await db.api_requests.aggregate(endpoint_pipeline).to_list(10)
    
    return {
        "key_id": key_id,
        "period_days": days,
        "total_requests": key.get("usage_count", 0),
        "daily_stats": [
            {
                "date": s["_id"],
                "requests": s["requests"],
                "unique_endpoints": len(s["endpoints"]),
                "errors": s["errors"]
            }
            for s in daily_stats
        ],
        "top_endpoints": [
            {"endpoint": e["_id"], "requests": e["count"]}
            for e in top_endpoints
        ],
        "rate_limit": key.get("rate_limit", 1000),
        "scopes": key.get("scopes", [])
    }
