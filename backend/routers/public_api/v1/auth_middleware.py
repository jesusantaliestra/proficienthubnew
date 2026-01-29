"""
Public API v1 - Authentication Middleware
Handles API key authentication and rate limiting for public API
"""
from fastapi import HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
import sys

sys.path.append('/app/backend')
from database import db
from routers.public_api.api_keys import validate_api_key, check_rate_limit, log_api_request

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class APIKeyAuth:
    """Dependency for API key authentication with scope checking"""
    
    def __init__(self, required_scopes: list = None):
        self.required_scopes = required_scopes or ["read"]
    
    async def __call__(
        self,
        request: Request,
        api_key: str = Depends(api_key_header)
    ) -> dict:
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API key required. Include X-API-Key header.",
                headers={"WWW-Authenticate": "ApiKey"}
            )
        
        # Validate the key
        key_data = await validate_api_key(api_key)
        
        if not key_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key"
            )
        
        # Check scopes
        key_scopes = set(key_data.get("scopes", []))
        required = set(self.required_scopes)
        
        # Admin scope grants all permissions
        if "admin" in key_scopes:
            pass
        elif "write" in key_scopes and "read" in required:
            pass  # Write includes read
        elif not required.issubset(key_scopes):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required scopes: {self.required_scopes}"
            )
        
        # Check rate limit
        if not await check_rate_limit(key_data["id"], key_data.get("rate_limit", 1000)):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "3600"}
            )
        
        # Log the request (async, don't wait)
        endpoint = f"{request.method} {request.url.path}"
        
        return {
            "api_key_id": key_data["id"],
            "owner_id": key_data["owner_id"],
            "owner_type": key_data["owner_type"],
            "scopes": key_data["scopes"],
            "rate_limit": key_data.get("rate_limit", 1000)
        }

# Pre-configured auth dependencies
require_read = APIKeyAuth(required_scopes=["read"])
require_write = APIKeyAuth(required_scopes=["write"])
require_admin = APIKeyAuth(required_scopes=["admin"])

async def log_request(request: Request, api_key_data: dict, status_code: int):
    """Log API request after response"""
    await log_api_request(
        key_id=api_key_data["api_key_id"],
        endpoint=request.url.path,
        method=request.method,
        status_code=status_code
    )
