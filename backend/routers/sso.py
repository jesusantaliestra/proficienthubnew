"""
SSO Router - SAML 2.0 Single Sign-On Implementation
Supports Azure AD, Okta, OneLogin, Google Workspace, and any SAML 2.0 IdP
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import base64
import zlib
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import hashlib
import secrets

router = APIRouter(prefix="/sso", tags=["SSO"])

import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
import bcrypt

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# ==================== MODELS ====================

class SAMLConfigCreate(BaseModel):
    name: str  # Display name (e.g., "Company SSO", "University Login")
    idp_entity_id: str  # Identity Provider Entity ID
    idp_sso_url: str  # IdP SSO URL (where to send SAML requests)
    idp_slo_url: Optional[str] = None  # IdP Single Logout URL
    idp_certificate: str  # IdP X.509 Certificate (PEM format)
    attribute_mapping: Dict[str, str] = {
        "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
        "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
    }
    auto_create_users: bool = True
    default_role: str = "student"
    allowed_domains: List[str] = []  # Empty = all domains allowed
    is_active: bool = True

class SAMLConfigUpdate(BaseModel):
    name: Optional[str] = None
    idp_sso_url: Optional[str] = None
    idp_slo_url: Optional[str] = None
    idp_certificate: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    auto_create_users: Optional[bool] = None
    default_role: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    is_active: Optional[bool] = None

# ==================== SSO CONFIGURATION MANAGEMENT ====================

from server import get_current_user

@router.post("/saml/config")
async def create_saml_config(
    config: SAMLConfigCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create SAML SSO configuration for institution"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    config_id = str(uuid.uuid4())
    
    # Generate SP metadata
    sp_entity_id = f"{FRONTEND_URL}/sso/metadata/{config_id}"
    sp_acs_url = f"{FRONTEND_URL}/api/sso/saml/acs/{config_id}"
    sp_slo_url = f"{FRONTEND_URL}/api/sso/saml/slo/{config_id}"
    
    config_doc = {
        "id": config_id,
        "institution_id": current_user["id"],
        "name": config.name,
        "idp_entity_id": config.idp_entity_id,
        "idp_sso_url": config.idp_sso_url,
        "idp_slo_url": config.idp_slo_url,
        "idp_certificate": config.idp_certificate,
        "sp_entity_id": sp_entity_id,
        "sp_acs_url": sp_acs_url,
        "sp_slo_url": sp_slo_url,
        "attribute_mapping": config.attribute_mapping,
        "auto_create_users": config.auto_create_users,
        "default_role": config.default_role,
        "allowed_domains": config.allowed_domains,
        "is_active": config.is_active,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.sso_configs.insert_one(config_doc)
    
    return {
        "id": config_id,
        "sp_entity_id": sp_entity_id,
        "sp_acs_url": sp_acs_url,
        "sp_slo_url": sp_slo_url,
        "message": "SAML SSO configuration created. Use these SP values in your IdP configuration."
    }

@router.get("/saml/configs")
async def list_saml_configs(current_user: dict = Depends(get_current_user)):
    """List SSO configurations for institution"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    configs = await db.sso_configs.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "idp_certificate": 0}  # Don't expose certificate in list
    ).to_list(100)
    
    return {"configs": configs}

@router.get("/saml/config/{config_id}")
async def get_saml_config(
    config_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific SSO configuration"""
    config = await db.sso_configs.find_one(
        {"id": config_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config

@router.patch("/saml/config/{config_id}")
async def update_saml_config(
    config_id: str,
    updates: SAMLConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update SSO configuration"""
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.sso_configs.update_one(
        {"id": config_id, "institution_id": current_user["id"]},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration updated"}

@router.delete("/saml/config/{config_id}")
async def delete_saml_config(
    config_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete SSO configuration"""
    result = await db.sso_configs.delete_one(
        {"id": config_id, "institution_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration deleted"}

# ==================== SP METADATA ====================

@router.get("/metadata/{config_id}")
async def get_sp_metadata(config_id: str):
    """Get Service Provider SAML metadata XML"""
    config = await db.sso_configs.find_one({"id": config_id})
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    metadata = f'''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" 
                     entityID="{config['sp_entity_id']}">
    <md:SPSSODescriptor AuthnRequestsSigned="false" 
                        WantAssertionsSigned="true" 
                        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" 
                                      Location="{config['sp_acs_url']}" 
                                      index="0"/>
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" 
                                 Location="{config['sp_slo_url']}"/>
    </md:SPSSODescriptor>
    <md:Organization>
        <md:OrganizationName xml:lang="en">ProficientHub</md:OrganizationName>
        <md:OrganizationDisplayName xml:lang="en">{config['name']}</md:OrganizationDisplayName>
        <md:OrganizationURL xml:lang="en">{FRONTEND_URL}</md:OrganizationURL>
    </md:Organization>
</md:EntityDescriptor>'''
    
    return Response(content=metadata, media_type="application/xml")

# ==================== SAML AUTHENTICATION FLOW ====================

@router.get("/saml/login/{config_id}")
async def initiate_saml_login(config_id: str, relay_state: Optional[str] = None):
    """Initiate SAML login - redirects to IdP"""
    config = await db.sso_configs.find_one({"id": config_id, "is_active": True})
    
    if not config:
        raise HTTPException(status_code=404, detail="SSO configuration not found or inactive")
    
    # Generate SAML AuthnRequest
    request_id = f"_{''.join(secrets.token_hex(16))}"
    issue_instant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    authn_request = f'''<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                                            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                                            ID="{request_id}"
                                            Version="2.0"
                                            IssueInstant="{issue_instant}"
                                            Destination="{config['idp_sso_url']}"
                                            AssertionConsumerServiceURL="{config['sp_acs_url']}"
                                            ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
        <saml:Issuer>{config['sp_entity_id']}</saml:Issuer>
        <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
                           AllowCreate="true"/>
    </samlp:AuthnRequest>'''
    
    # Compress and encode
    compressed = zlib.compress(authn_request.encode('utf-8'))[2:-4]
    encoded = base64.b64encode(compressed).decode('utf-8')
    
    # Store request for validation
    await db.saml_requests.insert_one({
        "request_id": request_id,
        "config_id": config_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    })
    
    # Build redirect URL
    params = {"SAMLRequest": encoded}
    if relay_state:
        params["RelayState"] = relay_state
    
    redirect_url = f"{config['idp_sso_url']}?{urlencode(params)}"
    
    return RedirectResponse(url=redirect_url, status_code=302)

@router.post("/saml/acs/{config_id}")
async def saml_assertion_consumer(config_id: str, request: Request):
    """SAML Assertion Consumer Service - processes IdP response"""
    config = await db.sso_configs.find_one({"id": config_id})
    
    if not config:
        raise HTTPException(status_code=404, detail="SSO configuration not found")
    
    form_data = await request.form()
    saml_response = form_data.get("SAMLResponse")
    relay_state = form_data.get("RelayState", "/")
    
    if not saml_response:
        raise HTTPException(status_code=400, detail="Missing SAML response")
    
    try:
        # Decode SAML response
        decoded = base64.b64decode(saml_response)
        xml_response = decoded.decode('utf-8')
        
        # Parse XML
        root = ET.fromstring(xml_response)
        ns = {
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
        }
        
        # Extract user attributes
        attributes = {}
        attr_elements = root.findall('.//saml:Attribute', ns)
        
        for attr in attr_elements:
            attr_name = attr.get('Name')
            attr_value = attr.find('saml:AttributeValue', ns)
            if attr_value is not None and attr_value.text:
                attributes[attr_name] = attr_value.text
        
        # Also try NameID
        name_id = root.find('.//saml:NameID', ns)
        if name_id is not None and name_id.text:
            attributes['NameID'] = name_id.text
        
        # Map attributes to user fields
        mapping = config.get('attribute_mapping', {})
        user_email = None
        user_name = None
        
        # Try to find email
        for field, saml_attr in mapping.items():
            if field == 'email':
                user_email = attributes.get(saml_attr) or attributes.get('NameID')
            elif field == 'name':
                user_name = attributes.get(saml_attr)
            elif field == 'first_name':
                first_name = attributes.get(saml_attr, '')
            elif field == 'last_name':
                last_name = attributes.get(saml_attr, '')
        
        if not user_email:
            # Fallback to common attribute names
            user_email = (
                attributes.get('email') or 
                attributes.get('Email') or 
                attributes.get('NameID') or
                attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress')
            )
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Could not extract email from SAML response")
        
        # Check allowed domains
        if config.get('allowed_domains'):
            domain = user_email.split('@')[-1]
            if domain not in config['allowed_domains']:
                raise HTTPException(status_code=403, detail=f"Domain {domain} not allowed for this SSO")
        
        # Find or create user
        user = await db.users.find_one({"email": user_email})
        
        if not user:
            if not config.get('auto_create_users', True):
                raise HTTPException(status_code=403, detail="User not found and auto-creation is disabled")
            
            # Create new user
            user_id = str(uuid.uuid4())
            user_name = user_name or f"{first_name} {last_name}".strip() or user_email.split('@')[0]
            
            user = {
                "id": user_id,
                "email": user_email,
                "name": user_name,
                "user_type": config.get('default_role', 'student'),
                "institution_id": config['institution_id'],
                "sso_provider": config_id,
                "created_via_sso": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(user)
        
        # Generate JWT token
        token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "user_type": user.get("user_type", "student"),
            "institution_id": user.get("institution_id"),
            "sso_login": True,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
        
        # Log SSO login
        await db.sso_logins.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "config_id": config_id,
            "ip_address": request.client.host if request.client else None,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/sso/callback?token={token}&relay_state={quote(relay_state)}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid SAML response XML: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSO processing error: {str(e)}")

@router.get("/saml/slo/{config_id}")
async def saml_single_logout(config_id: str, SAMLRequest: Optional[str] = None):
    """SAML Single Logout Service"""
    # For now, just redirect to login page
    # Full SLO implementation would process the logout request
    return RedirectResponse(url=f"{FRONTEND_URL}/login?slo=true", status_code=302)

# ==================== SSO LOGIN PAGE ====================

@router.get("/providers/{institution_id}")
async def get_sso_providers(institution_id: str):
    """Get available SSO providers for an institution (public endpoint)"""
    providers = await db.sso_configs.find(
        {"institution_id": institution_id, "is_active": True},
        {"_id": 0, "id": 1, "name": 1}
    ).to_list(10)
    
    return {"providers": providers}

@router.get("/login-url")
async def get_sso_login_url(email: str):
    """Get SSO login URL for a user's email domain"""
    domain = email.split('@')[-1]
    
    # Find matching SSO config
    config = await db.sso_configs.find_one({
        "$or": [
            {"allowed_domains": domain},
            {"allowed_domains": {"$size": 0}}  # Empty = all domains
        ],
        "is_active": True
    }, {"_id": 0, "id": 1, "name": 1, "institution_id": 1})
    
    if not config:
        return {"sso_available": False}
    
    return {
        "sso_available": True,
        "provider_name": config["name"],
        "login_url": f"/api/sso/saml/login/{config['id']}"
    }

# ==================== SSO ANALYTICS ====================

@router.get("/analytics")
async def get_sso_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get SSO usage analytics"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Get login counts by config
    pipeline = [
        {"$match": {
            "created_at": {"$gte": start_date}
        }},
        {"$lookup": {
            "from": "sso_configs",
            "localField": "config_id",
            "foreignField": "id",
            "as": "config"
        }},
        {"$unwind": "$config"},
        {"$match": {"config.institution_id": current_user["id"]}},
        {"$group": {
            "_id": "$config_id",
            "config_name": {"$first": "$config.name"},
            "login_count": {"$sum": 1},
            "unique_users": {"$addToSet": "$user_id"}
        }},
        {"$project": {
            "config_id": "$_id",
            "config_name": 1,
            "login_count": 1,
            "unique_users": {"$size": "$unique_users"}
        }}
    ]
    
    stats = await db.sso_logins.aggregate(pipeline).to_list(100)
    
    # Total users created via SSO
    sso_users = await db.users.count_documents({
        "institution_id": current_user["id"],
        "created_via_sso": True
    })
    
    return {
        "period_days": days,
        "by_provider": stats,
        "total_sso_users": sso_users
    }
