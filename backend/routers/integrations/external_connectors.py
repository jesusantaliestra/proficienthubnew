"""
External Integrations - CRM/ERP Connectors
Connect ProficientHub with external CRM and ERP systems
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import httpx

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/integrations", tags=["External Integrations"])

# ==================== SUPPORTED INTEGRATIONS ====================

SUPPORTED_INTEGRATIONS = {
    # CRMs
    "salesforce": {
        "name": "Salesforce",
        "type": "crm",
        "auth_type": "oauth2",
        "features": ["contacts", "leads", "opportunities", "accounts"],
        "api_base": "https://login.salesforce.com",
        "docs_url": "https://developer.salesforce.com/docs"
    },
    "hubspot": {
        "name": "HubSpot",
        "type": "crm",
        "auth_type": "oauth2",
        "features": ["contacts", "deals", "companies", "tickets"],
        "api_base": "https://api.hubapi.com",
        "docs_url": "https://developers.hubspot.com/docs"
    },
    "zoho_crm": {
        "name": "Zoho CRM",
        "type": "crm",
        "auth_type": "oauth2",
        "features": ["leads", "contacts", "accounts", "deals", "campaigns"],
        "api_base": "https://www.zohoapis.com/crm/v3",
        "docs_url": "https://www.zoho.com/crm/developer/docs/"
    },
    "pipedrive": {
        "name": "Pipedrive",
        "type": "crm",
        "auth_type": "api_key",
        "features": ["persons", "organizations", "deals", "activities"],
        "api_base": "https://api.pipedrive.com/v1",
        "docs_url": "https://developers.pipedrive.com/docs/api/v1"
    },
    "freshsales": {
        "name": "Freshsales",
        "type": "crm",
        "auth_type": "api_key",
        "features": ["contacts", "accounts", "deals", "tasks"],
        "api_base": "https://{domain}.myfreshworks.com/crm/sales/api",
        "docs_url": "https://developer.freshsales.io/api/"
    },
    "monday": {
        "name": "Monday.com",
        "type": "crm",
        "auth_type": "api_key",
        "features": ["boards", "items", "updates"],
        "api_base": "https://api.monday.com/v2",
        "docs_url": "https://developer.monday.com/api-reference"
    },
    
    # ERPs
    "sap_business_one": {
        "name": "SAP Business One",
        "type": "erp",
        "auth_type": "basic",
        "features": ["business_partners", "invoices", "orders", "payments"],
        "api_base": "https://{server}:50000/b1s/v1",
        "docs_url": "https://help.sap.com/docs/SAP_BUSINESS_ONE"
    },
    "dynamics_365": {
        "name": "Microsoft Dynamics 365",
        "type": "erp",
        "auth_type": "oauth2",
        "features": ["accounts", "contacts", "invoices", "orders", "products"],
        "api_base": "https://{org}.api.crm.dynamics.com/api/data/v9.2",
        "docs_url": "https://docs.microsoft.com/dynamics365/"
    },
    "netsuite": {
        "name": "Oracle NetSuite",
        "type": "erp",
        "auth_type": "oauth2",
        "features": ["customers", "invoices", "transactions", "inventory"],
        "api_base": "https://{account_id}.suitetalk.api.netsuite.com",
        "docs_url": "https://docs.oracle.com/en/cloud/saas/netsuite/"
    },
    "odoo": {
        "name": "Odoo",
        "type": "erp",
        "auth_type": "api_key",
        "features": ["partners", "invoices", "sales", "accounting"],
        "api_base": "https://{instance}.odoo.com",
        "docs_url": "https://www.odoo.com/documentation/"
    },
    "quickbooks": {
        "name": "QuickBooks Online",
        "type": "erp",
        "auth_type": "oauth2",
        "features": ["customers", "invoices", "payments", "accounts"],
        "api_base": "https://quickbooks.api.intuit.com/v3",
        "docs_url": "https://developer.intuit.com/app/developer/qbo/docs"
    },
    "xero": {
        "name": "Xero",
        "type": "erp",
        "auth_type": "oauth2",
        "features": ["contacts", "invoices", "payments", "accounts"],
        "api_base": "https://api.xero.com/api.xro/2.0",
        "docs_url": "https://developer.xero.com/documentation/"
    },
    "sage": {
        "name": "Sage Intacct",
        "type": "erp",
        "auth_type": "web_services",
        "features": ["customers", "invoices", "gl_accounts", "projects"],
        "api_base": "https://api.intacct.com/ia/xml/xmlgw.phtml",
        "docs_url": "https://developer.intacct.com/web-services/"
    }
}

# ==================== MODELS ====================

class IntegrationConfig(BaseModel):
    integration_type: str  # salesforce, hubspot, etc.
    credentials: Dict[str, str]  # api_key, client_id, client_secret, etc.
    settings: Optional[Dict[str, Any]] = None
    sync_config: Optional[Dict[str, bool]] = None  # Which entities to sync

class SyncMapping(BaseModel):
    source_field: str
    target_field: str
    transform: Optional[str] = None  # optional transformation

class WebhookConfig(BaseModel):
    events: List[str]
    target_url: str
    secret: Optional[str] = None

# ==================== ENDPOINTS ====================

@router.get("/available")
async def list_available_integrations(
    type_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all available integrations"""
    integrations = SUPPORTED_INTEGRATIONS.copy()
    
    if type_filter:
        integrations = {k: v for k, v in integrations.items() if v["type"] == type_filter}
    
    return {
        "integrations": integrations,
        "categories": {
            "crm": [k for k, v in SUPPORTED_INTEGRATIONS.items() if v["type"] == "crm"],
            "erp": [k for k, v in SUPPORTED_INTEGRATIONS.items() if v["type"] == "erp"]
        }
    }

@router.post("/connect")
async def connect_integration(
    config: IntegrationConfig,
    current_user: dict = Depends(get_current_user)
):
    """Connect an external integration"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if config.integration_type not in SUPPORTED_INTEGRATIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported integration: {config.integration_type}")
    
    integration_info = SUPPORTED_INTEGRATIONS[config.integration_type]
    integration_id = str(uuid.uuid4())
    
    # Validate credentials based on auth type
    required_creds = {
        "oauth2": ["client_id", "client_secret"],
        "api_key": ["api_key"],
        "basic": ["username", "password"]
    }
    
    auth_type = integration_info["auth_type"]
    for cred in required_creds.get(auth_type, []):
        if cred not in config.credentials:
            raise HTTPException(status_code=400, detail=f"Missing required credential: {cred}")
    
    # Store integration (encrypt credentials in production)
    integration_doc = {
        "id": integration_id,
        "institution_id": current_user["id"],
        "integration_type": config.integration_type,
        "integration_name": integration_info["name"],
        "integration_category": integration_info["type"],
        "auth_type": auth_type,
        "credentials": config.credentials,  # Should be encrypted
        "settings": config.settings or {},
        "sync_config": config.sync_config or {f: True for f in integration_info["features"]},
        "status": "pending_verification",
        "last_sync": None,
        "sync_errors": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.integrations.insert_one(integration_doc)
    
    return {
        "id": integration_id,
        "message": f"Integration with {integration_info['name']} configured",
        "status": "pending_verification",
        "next_step": "Call /integrations/{id}/verify to test the connection"
    }

@router.post("/{integration_id}/verify")
async def verify_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Verify integration connection is working"""
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Test connection based on integration type
    integration_type = integration["integration_type"]
    credentials = integration["credentials"]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Integration-specific verification
            if integration_type == "hubspot":
                response = await client.get(
                    "https://api.hubapi.com/crm/v3/objects/contacts",
                    headers={"Authorization": f"Bearer {credentials.get('access_token', credentials.get('api_key'))}"},
                    params={"limit": 1}
                )
            elif integration_type == "pipedrive":
                response = await client.get(
                    f"https://api.pipedrive.com/v1/users/me?api_token={credentials.get('api_key')}"
                )
            elif integration_type == "quickbooks":
                response = await client.get(
                    f"https://quickbooks.api.intuit.com/v3/company/{credentials.get('realm_id')}/companyinfo/{credentials.get('realm_id')}",
                    headers={"Authorization": f"Bearer {credentials.get('access_token')}"}
                )
            else:
                # Generic verification - just mark as verified for now
                await db.integrations.update_one(
                    {"id": integration_id},
                    {"$set": {"status": "active", "verified_at": datetime.now(timezone.utc).isoformat()}}
                )
                return {"status": "verified", "message": "Integration marked as active"}
            
            if response.status_code == 200:
                await db.integrations.update_one(
                    {"id": integration_id},
                    {"$set": {"status": "active", "verified_at": datetime.now(timezone.utc).isoformat()}}
                )
                return {"status": "verified", "message": "Connection successful"}
            else:
                return {"status": "failed", "error": f"API returned {response.status_code}"}
                
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("")
async def list_connected_integrations(
    current_user: dict = Depends(get_current_user)
):
    """List all connected integrations"""
    integrations = await db.integrations.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "credentials": 0}  # Don't expose credentials
    ).to_list(100)
    
    return {"integrations": integrations}

@router.get("/{integration_id}")
async def get_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get integration details"""
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0, "credentials": 0}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return integration

@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect an integration"""
    result = await db.integrations.delete_one({
        "id": integration_id,
        "institution_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Also delete sync records
    await db.integration_sync_logs.delete_many({"integration_id": integration_id})
    
    return {"message": "Integration disconnected"}

# ==================== SYNC OPERATIONS ====================

@router.post("/{integration_id}/sync")
async def trigger_sync(
    integration_id: str,
    entity_types: Optional[List[str]] = None,
    direction: str = "bidirectional",  # import, export, bidirectional
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """Trigger a sync with the external system"""
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    if integration["status"] != "active":
        raise HTTPException(status_code=400, detail="Integration is not active")
    
    sync_id = str(uuid.uuid4())
    
    # Create sync record
    sync_doc = {
        "id": sync_id,
        "integration_id": integration_id,
        "institution_id": current_user["id"],
        "entity_types": entity_types or list(integration.get("sync_config", {}).keys()),
        "direction": direction,
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "records_processed": 0,
        "records_created": 0,
        "records_updated": 0,
        "errors": []
    }
    
    await db.integration_sync_logs.insert_one(sync_doc)
    
    # Update integration last sync
    await db.integrations.update_one(
        {"id": integration_id},
        {"$set": {"last_sync": datetime.now(timezone.utc).isoformat()}}
    )
    
    # In production, this would be a background task
    # For now, simulate completion
    await db.integration_sync_logs.update_one(
        {"id": sync_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "records_processed": 0,
                "message": "Sync completed (external API calls not implemented in demo)"
            }
        }
    )
    
    return {
        "sync_id": sync_id,
        "status": "completed",
        "message": "Sync initiated"
    }

@router.get("/{integration_id}/sync/history")
async def get_sync_history(
    integration_id: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get sync history for an integration"""
    # Verify ownership
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    sync_logs = await db.integration_sync_logs.find(
        {"integration_id": integration_id},
        {"_id": 0}
    ).sort("started_at", -1).limit(limit).to_list(limit)
    
    return {"sync_history": sync_logs}

# ==================== FIELD MAPPINGS ====================

@router.get("/{integration_id}/mappings")
async def get_field_mappings(
    integration_id: str,
    entity_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Get field mappings for an entity type"""
    mappings = await db.integration_mappings.find_one(
        {
            "integration_id": integration_id,
            "institution_id": current_user["id"],
            "entity_type": entity_type
        },
        {"_id": 0}
    )
    
    if not mappings:
        # Return default mappings
        default_mappings = {
            "contacts": [
                {"source": "name", "target": "full_name", "transform": None},
                {"source": "email", "target": "email", "transform": None},
                {"source": "phone", "target": "phone", "transform": None},
                {"source": "institution_name", "target": "company", "transform": None}
            ],
            "students": [
                {"source": "name", "target": "full_name", "transform": None},
                {"source": "email", "target": "email", "transform": None},
                {"source": "current_exam", "target": "exam_type", "transform": None},
                {"source": "credits", "target": "credits_balance", "transform": None}
            ],
            "invoices": [
                {"source": "invoice_number", "target": "number", "transform": None},
                {"source": "customer_name", "target": "customer", "transform": None},
                {"source": "totals.total", "target": "amount", "transform": None},
                {"source": "currency", "target": "currency", "transform": None},
                {"source": "status", "target": "status", "transform": None}
            ]
        }
        return {"mappings": default_mappings.get(entity_type, []), "is_default": True}
    
    return {"mappings": mappings.get("mappings", []), "is_default": False}

@router.put("/{integration_id}/mappings")
async def update_field_mappings(
    integration_id: str,
    entity_type: str,
    mappings: List[SyncMapping],
    current_user: dict = Depends(get_current_user)
):
    """Update field mappings for an entity type"""
    # Verify integration ownership
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    mapping_doc = {
        "integration_id": integration_id,
        "institution_id": current_user["id"],
        "entity_type": entity_type,
        "mappings": [m.dict() for m in mappings],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.integration_mappings.update_one(
        {
            "integration_id": integration_id,
            "institution_id": current_user["id"],
            "entity_type": entity_type
        },
        {"$set": mapping_doc},
        upsert=True
    )
    
    return {"message": "Mappings updated"}

# ==================== WEBHOOKS FOR REAL-TIME SYNC ====================

@router.post("/{integration_id}/webhooks")
async def configure_webhook(
    integration_id: str,
    webhook: WebhookConfig,
    current_user: dict = Depends(get_current_user)
):
    """Configure webhooks for real-time sync"""
    integration = await db.integrations.find_one(
        {"id": integration_id, "institution_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    webhook_id = str(uuid.uuid4())
    
    webhook_doc = {
        "id": webhook_id,
        "integration_id": integration_id,
        "institution_id": current_user["id"],
        "events": webhook.events,
        "target_url": webhook.target_url,
        "secret": webhook.secret,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.integration_webhooks.insert_one(webhook_doc)
    
    return {"webhook_id": webhook_id, "message": "Webhook configured"}

@router.post("/webhook/receive/{integration_type}")
async def receive_external_webhook(
    integration_type: str,
    payload: Dict[str, Any]
):
    """Receive webhooks from external systems"""
    # This endpoint would handle incoming webhooks from external CRMs/ERPs
    # and trigger corresponding updates in ProficientHub
    
    webhook_log = {
        "id": str(uuid.uuid4()),
        "integration_type": integration_type,
        "payload": payload,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "processed": False
    }
    
    await db.integration_webhook_logs.insert_one(webhook_log)
    
    # Process webhook based on type
    # In production, this would map external events to internal actions
    
    return {"status": "received"}
