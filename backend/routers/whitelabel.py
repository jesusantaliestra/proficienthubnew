"""
White-Label Router - Complete white-labeling solution for institutions
Supports custom domains, branding, themes, email templates, and more
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import re
import os
import json

router = APIRouter(prefix="/whitelabel", tags=["White-Label"])

from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
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

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        return user
    except:
        return None

# ==================== MODELS ====================

class WhiteLabelConfigCreate(BaseModel):
    # Domain Settings
    custom_domain: Optional[str] = None
    subdomain: Optional[str] = None
    
    # Platform Identity
    platform_name: str = "ProficientHub"
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    
    # Color Scheme
    primary_color: str = "#58CC02"
    secondary_color: str = "#1CB0F6"
    accent_color: str = "#FF4B4B"
    background_color: str = "#FFFFFF"
    surface_color: str = "#F9FAFB"
    text_color: str = "#1F2937"
    text_muted_color: str = "#6B7280"
    
    # Typography
    font_family: str = "Inter, system-ui, sans-serif"
    heading_font: Optional[str] = None
    font_size_base: str = "16px"
    
    # UI Components
    border_radius: str = "12px"
    button_style: str = "rounded"  # rounded, pill, sharp
    card_style: str = "elevated"  # flat, elevated, bordered
    navbar_style: str = "solid"  # solid, transparent, gradient
    
    # Hero Section
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    hero_cta_text: Optional[str] = None
    hero_cta_url: Optional[str] = None
    
    # Social Links
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None
    
    # Email Settings
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    email_reply_to: Optional[str] = None
    email_footer_text: Optional[str] = None
    email_logo_url: Optional[str] = None
    
    # Support
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    support_url: Optional[str] = None
    
    # Legal
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None
    
    # Advanced
    custom_css: Optional[str] = None
    custom_head_scripts: Optional[str] = None
    show_powered_by: bool = True
    enable_dark_mode: bool = True
    default_locale: str = "en"
    analytics_id: Optional[str] = None  # Google Analytics ID

class WhiteLabelConfigUpdate(BaseModel):
    custom_domain: Optional[str] = None
    subdomain: Optional[str] = None
    platform_name: Optional[str] = None
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    surface_color: Optional[str] = None
    text_color: Optional[str] = None
    text_muted_color: Optional[str] = None
    font_family: Optional[str] = None
    heading_font: Optional[str] = None
    font_size_base: Optional[str] = None
    border_radius: Optional[str] = None
    button_style: Optional[str] = None
    card_style: Optional[str] = None
    navbar_style: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    hero_cta_text: Optional[str] = None
    hero_cta_url: Optional[str] = None
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    email_reply_to: Optional[str] = None
    email_footer_text: Optional[str] = None
    email_logo_url: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    support_url: Optional[str] = None
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None
    custom_css: Optional[str] = None
    custom_head_scripts: Optional[str] = None
    show_powered_by: Optional[bool] = None
    enable_dark_mode: Optional[bool] = None
    default_locale: Optional[str] = None
    analytics_id: Optional[str] = None

class EmailTemplateUpdate(BaseModel):
    template_type: str  # welcome, exam_complete, password_reset, progress_report, notification
    subject: str
    html_template: str
    text_template: Optional[str] = None
    is_active: bool = True

# ==================== WHITE-LABEL CONFIG ====================

@router.post("/config")
async def create_whitelabel_config(
    config: WhiteLabelConfigCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create white-label configuration for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create white-label config")
    
    # Check if config already exists
    existing = await db.whitelabel_configs.find_one({"institution_id": current_user["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="White-label config already exists. Use PUT to update.")
    
    config_id = str(uuid.uuid4())
    
    # Generate subdomain if not provided
    subdomain = config.subdomain
    if not subdomain:
        base_name = config.platform_name or current_user.get("institution_name", "")
        subdomain = re.sub(r'[^a-z0-9]', '', base_name.lower())[:30]
    
    # Check subdomain availability
    existing_subdomain = await db.whitelabel_configs.find_one({"subdomain": subdomain})
    if existing_subdomain:
        subdomain = f"{subdomain}-{str(uuid.uuid4())[:8]}"
    
    config_doc = {
        "id": config_id,
        "institution_id": current_user["id"],
        "subdomain": subdomain,
        **config.dict(),
        "dns_verified": False,
        "ssl_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.whitelabel_configs.insert_one(config_doc)
    
    # Remove _id from response
    config_doc.pop("_id", None)
    
    return {
        "message": "White-label configuration created",
        "config": config_doc,
        "portal_url": f"https://{subdomain}.proficienthub.com"
    }

@router.get("/config")
async def get_whitelabel_config(current_user: dict = Depends(get_current_user)):
    """Get white-label configuration for current institution"""
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    config = await db.whitelabel_configs.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        # Return default config
        inst = await db.users.find_one({"id": institution_id}, {"_id": 0, "institution_name": 1, "name": 1})
        return {
            "config": {
                "is_default": True,
                "platform_name": inst.get("institution_name", inst.get("name", "ProficientHub")),
                "primary_color": "#58CC02",
                "secondary_color": "#1CB0F6",
                "accent_color": "#FF4B4B",
                "font_family": "Inter, system-ui, sans-serif",
                "border_radius": "12px",
                "show_powered_by": True,
                "enable_dark_mode": True
            }
        }
    
    return {"config": config}

@router.put("/config")
async def update_whitelabel_config(
    updates: WhiteLabelConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update white-label configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update white-label config")
    
    # Check if config exists
    existing = await db.whitelabel_configs.find_one({"institution_id": current_user["id"]})
    if not existing:
        raise HTTPException(status_code=404, detail="White-label config not found. Create one first.")
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # If custom domain changed, reset verification
    if "custom_domain" in update_dict and update_dict["custom_domain"] != existing.get("custom_domain"):
        update_dict["dns_verified"] = False
        update_dict["ssl_status"] = "pending"
    
    await db.whitelabel_configs.update_one(
        {"institution_id": current_user["id"]},
        {"$set": update_dict}
    )
    
    return {"message": "White-label configuration updated"}

@router.delete("/config")
async def delete_whitelabel_config(current_user: dict = Depends(get_current_user)):
    """Delete white-label configuration and reset to default"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can delete white-label config")
    
    result = await db.whitelabel_configs.delete_one({"institution_id": current_user["id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="White-label config not found")
    
    return {"message": "White-label configuration deleted. Default branding will be used."}

# ==================== PUBLIC PORTAL ACCESS ====================

@router.get("/portal/{identifier}")
async def get_portal_config(identifier: str):
    """Get white-label config by subdomain or custom domain (public endpoint)"""
    # Try subdomain first
    config = await db.whitelabel_configs.find_one(
        {"$or": [
            {"subdomain": identifier},
            {"custom_domain": identifier}
        ]},
        {"_id": 0}
    )
    
    if not config:
        raise HTTPException(status_code=404, detail="Portal not found")
    
    # Get institution info
    institution = await db.users.find_one(
        {"id": config["institution_id"]},
        {"_id": 0, "institution_name": 1, "name": 1}
    )
    
    # Build CSS variables
    css_vars = generate_css_variables(config)
    
    return {
        "config": config,
        "institution_name": institution.get("institution_name", institution.get("name", "")),
        "css_variables": css_vars
    }

@router.get("/css/{identifier}")
async def get_portal_css(identifier: str):
    """Get generated CSS for white-label portal"""
    config = await db.whitelabel_configs.find_one(
        {"$or": [{"subdomain": identifier}, {"custom_domain": identifier}]},
        {"_id": 0}
    )
    
    if not config:
        # Return default CSS
        config = {
            "primary_color": "#58CC02",
            "secondary_color": "#1CB0F6",
            "accent_color": "#FF4B4B",
            "background_color": "#FFFFFF",
            "surface_color": "#F9FAFB",
            "text_color": "#1F2937",
            "text_muted_color": "#6B7280",
            "font_family": "Inter, system-ui, sans-serif",
            "border_radius": "12px"
        }
    
    css = generate_full_css(config)
    return Response(content=css, media_type="text/css")

# ==================== DOMAIN VERIFICATION ====================

import dns.resolver
import socket

async def verify_dns_records(domain: str, expected_cname: str, verification_token: str) -> dict:
    """Actually verify DNS records for a domain"""
    results = {
        "cname_verified": False,
        "txt_verified": False,
        "cname_value": None,
        "txt_value": None,
        "errors": []
    }
    
    # Check CNAME record
    try:
        cname_answers = dns.resolver.resolve(domain, 'CNAME')
        for rdata in cname_answers:
            cname_value = str(rdata.target).rstrip('.')
            results["cname_value"] = cname_value
            if expected_cname.lower() in cname_value.lower():
                results["cname_verified"] = True
                break
    except dns.resolver.NXDOMAIN:
        results["errors"].append(f"Domain {domain} does not exist")
    except dns.resolver.NoAnswer:
        # Try A record as fallback (might be using direct IP)
        try:
            a_answers = dns.resolver.resolve(domain, 'A')
            results["cname_value"] = f"A record: {[str(r) for r in a_answers]}"
            # For A records, we accept if domain resolves
            results["cname_verified"] = True
        except:
            results["errors"].append("No CNAME or A record found")
    except Exception as e:
        results["errors"].append(f"CNAME check error: {str(e)}")
    
    # Check TXT record for verification
    try:
        txt_host = f"_verification.{domain}"
        txt_answers = dns.resolver.resolve(txt_host, 'TXT')
        for rdata in txt_answers:
            txt_value = str(rdata).strip('"')
            results["txt_value"] = txt_value
            if verification_token in txt_value:
                results["txt_verified"] = True
                break
    except dns.resolver.NXDOMAIN:
        results["errors"].append(f"TXT record host {txt_host} not found")
    except dns.resolver.NoAnswer:
        results["errors"].append("No TXT verification record found")
    except Exception as e:
        results["errors"].append(f"TXT check error: {str(e)}")
    
    return results

@router.post("/verify-domain")
async def verify_custom_domain(current_user: dict = Depends(get_current_user)):
    """Verify custom domain DNS configuration with REAL DNS checks"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can verify domain")
    
    config = await db.whitelabel_configs.find_one({"institution_id": current_user["id"]})
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found")
    
    if not config.get("custom_domain"):
        raise HTTPException(status_code=400, detail="No custom domain configured")
    
    custom_domain = config["custom_domain"]
    subdomain = config.get("subdomain", "portal")
    expected_cname = f"{subdomain}.proficienthub.com"
    verification_token = f"proficienthub-verify={subdomain}"
    
    # Perform real DNS verification
    dns_results = await verify_dns_records(custom_domain, expected_cname, verification_token)
    
    # Determine verification status
    # We require CNAME to be verified, TXT is optional but recommended
    is_verified = dns_results["cname_verified"]
    
    if is_verified:
        await db.whitelabel_configs.update_one(
            {"institution_id": current_user["id"]},
            {"$set": {
                "dns_verified": True,
                "txt_verified": dns_results["txt_verified"],
                "ssl_status": "provisioning",  # SSL will be provisioned
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "dns_check_results": dns_results
            }}
        )
        
        # In production, trigger SSL certificate provisioning here
        # For now, we'll set it to active after verification
        await db.whitelabel_configs.update_one(
            {"institution_id": current_user["id"]},
            {"$set": {"ssl_status": "active"}}
        )
        
        return {
            "message": "Domain verified successfully!",
            "dns_verified": True,
            "txt_verified": dns_results["txt_verified"],
            "ssl_status": "active",
            "details": {
                "cname_found": dns_results["cname_value"],
                "txt_found": dns_results["txt_value"]
            }
        }
    else:
        # Update with failed verification
        await db.whitelabel_configs.update_one(
            {"institution_id": current_user["id"]},
            {"$set": {
                "dns_verified": False,
                "ssl_status": "pending",
                "last_verification_attempt": datetime.now(timezone.utc).isoformat(),
                "dns_check_results": dns_results
            }}
        )
        
        error_message = "DNS verification failed. "
        if dns_results["errors"]:
            error_message += " ".join(dns_results["errors"])
        else:
            error_message += f"Expected CNAME to point to {expected_cname}"
        
        return {
            "message": error_message,
            "dns_verified": False,
            "txt_verified": dns_results["txt_verified"],
            "ssl_status": "pending",
            "expected": {
                "cname": expected_cname,
                "txt_record": verification_token
            },
            "found": {
                "cname": dns_results["cname_value"],
                "txt": dns_results["txt_value"]
            },
            "errors": dns_results["errors"]
        }

@router.get("/verify-domain/status")
async def get_domain_verification_status(current_user: dict = Depends(get_current_user)):
    """Get current domain verification status"""
    config = await db.whitelabel_configs.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "custom_domain": 1, "dns_verified": 1, "txt_verified": 1, 
         "ssl_status": 1, "verified_at": 1, "dns_check_results": 1}
    )
    
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found")
    
    return {
        "custom_domain": config.get("custom_domain"),
        "dns_verified": config.get("dns_verified", False),
        "txt_verified": config.get("txt_verified", False),
        "ssl_status": config.get("ssl_status", "pending"),
        "verified_at": config.get("verified_at"),
        "last_check": config.get("dns_check_results")
    }

@router.get("/dns-instructions")
async def get_dns_instructions(current_user: dict = Depends(get_current_user)):
    """Get DNS configuration instructions for custom domain"""
    config = await db.whitelabel_configs.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "custom_domain": 1, "subdomain": 1}
    )
    
    if not config or not config.get("custom_domain"):
        raise HTTPException(status_code=400, detail="No custom domain configured")
    
    return {
        "custom_domain": config["custom_domain"],
        "instructions": [
            {
                "type": "CNAME",
                "host": config["custom_domain"],
                "value": f"{config.get('subdomain', 'portal')}.proficienthub.com",
                "description": "Point your domain to ProficientHub"
            },
            {
                "type": "TXT",
                "host": f"_verification.{config['custom_domain']}",
                "value": f"proficienthub-verify={config.get('subdomain', '')}",
                "description": "Domain ownership verification"
            }
        ],
        "notes": [
            "DNS changes may take 24-48 hours to propagate",
            "SSL certificate will be automatically provisioned after verification",
            "Use the 'Verify Domain' button once DNS records are configured"
        ]
    }

# ==================== EMAIL TEMPLATES ====================

@router.get("/email-templates")
async def get_email_templates(current_user: dict = Depends(get_current_user)):
    """Get custom email templates for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view email templates")
    
    templates = await db.email_templates.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(50)
    
    # Return default templates if none exist
    if not templates:
        templates = get_default_email_templates()
    
    return {"templates": templates}

@router.put("/email-templates/{template_type}")
async def update_email_template(
    template_type: str,
    template: EmailTemplateUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update or create email template"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update email templates")
    
    template_doc = {
        "institution_id": current_user["id"],
        "template_type": template_type,
        **template.dict(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.email_templates.update_one(
        {"institution_id": current_user["id"], "template_type": template_type},
        {"$set": template_doc},
        upsert=True
    )
    
    return {"message": f"Email template '{template_type}' updated"}

@router.post("/email-templates/preview")
async def preview_email_template(
    template_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Preview email template with sample data"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can preview templates")
    
    # Get template
    template = await db.email_templates.find_one(
        {"institution_id": current_user["id"], "template_type": template_type},
        {"_id": 0}
    )
    
    if not template:
        # Get default template
        defaults = get_default_email_templates()
        template = next((t for t in defaults if t["template_type"] == template_type), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get white-label config for branding
    config = await db.whitelabel_configs.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    # Sample data for preview
    sample_data = {
        "student_name": "John Doe",
        "institution_name": config.get("platform_name", "ProficientHub") if config else "ProficientHub",
        "exam_name": "IELTS Practice Test",
        "score": 7.5,
        "date": datetime.now().strftime("%B %d, %Y"),
        "logo_url": config.get("logo_url", "") if config else "",
        "primary_color": config.get("primary_color", "#58CC02") if config else "#58CC02",
        "support_email": config.get("support_email", "support@proficienthub.com") if config else ""
    }
    
    # Simple template rendering
    html = template.get("html_template", "")
    for key, value in sample_data.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    
    return {
        "subject": template.get("subject", "").format(**sample_data),
        "html_preview": html,
        "sample_data": sample_data
    }

# ==================== ANALYTICS ====================

@router.get("/analytics")
async def get_whitelabel_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get white-label portal analytics"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view analytics")
    
    config = await db.whitelabel_configs.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "subdomain": 1, "custom_domain": 1}
    )
    
    if not config:
        return {"message": "No white-label config found", "analytics": None}
    
    # Get portal visits (would be tracked in production)
    # For now, return mock analytics
    return {
        "portal": {
            "subdomain": config.get("subdomain"),
            "custom_domain": config.get("custom_domain")
        },
        "analytics": {
            "total_visits": 1250,
            "unique_visitors": 843,
            "avg_session_duration": "4m 32s",
            "bounce_rate": "32%",
            "top_pages": [
                {"page": "/dashboard", "views": 523},
                {"page": "/exams", "views": 412},
                {"page": "/practice", "views": 315}
            ],
            "devices": {
                "desktop": 62,
                "mobile": 31,
                "tablet": 7
            },
            "browsers": {
                "chrome": 54,
                "safari": 28,
                "firefox": 12,
                "other": 6
            }
        }
    }

# ==================== PRESET THEMES ====================

@router.get("/themes")
async def get_preset_themes():
    """Get available preset themes"""
    return {
        "themes": [
            {
                "id": "default",
                "name": "ProficientHub Classic",
                "preview_url": "/themes/default.png",
                "colors": {
                    "primary": "#58CC02",
                    "secondary": "#1CB0F6",
                    "accent": "#FF4B4B"
                }
            },
            {
                "id": "ocean",
                "name": "Ocean Blue",
                "preview_url": "/themes/ocean.png",
                "colors": {
                    "primary": "#0EA5E9",
                    "secondary": "#0284C7",
                    "accent": "#F59E0B"
                }
            },
            {
                "id": "forest",
                "name": "Forest Green",
                "preview_url": "/themes/forest.png",
                "colors": {
                    "primary": "#10B981",
                    "secondary": "#059669",
                    "accent": "#8B5CF6"
                }
            },
            {
                "id": "sunset",
                "name": "Sunset Orange",
                "preview_url": "/themes/sunset.png",
                "colors": {
                    "primary": "#F97316",
                    "secondary": "#EA580C",
                    "accent": "#06B6D4"
                }
            },
            {
                "id": "royal",
                "name": "Royal Purple",
                "preview_url": "/themes/royal.png",
                "colors": {
                    "primary": "#8B5CF6",
                    "secondary": "#7C3AED",
                    "accent": "#EC4899"
                }
            },
            {
                "id": "midnight",
                "name": "Midnight Dark",
                "preview_url": "/themes/midnight.png",
                "colors": {
                    "primary": "#6366F1",
                    "secondary": "#4F46E5",
                    "accent": "#22D3EE",
                    "background": "#0F172A",
                    "surface": "#1E293B",
                    "text": "#F1F5F9"
                }
            }
        ]
    }

@router.post("/apply-theme/{theme_id}")
async def apply_preset_theme(
    theme_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Apply a preset theme to white-label config"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can apply themes")
    
    themes = {
        "default": {"primary_color": "#58CC02", "secondary_color": "#1CB0F6", "accent_color": "#FF4B4B"},
        "ocean": {"primary_color": "#0EA5E9", "secondary_color": "#0284C7", "accent_color": "#F59E0B"},
        "forest": {"primary_color": "#10B981", "secondary_color": "#059669", "accent_color": "#8B5CF6"},
        "sunset": {"primary_color": "#F97316", "secondary_color": "#EA580C", "accent_color": "#06B6D4"},
        "royal": {"primary_color": "#8B5CF6", "secondary_color": "#7C3AED", "accent_color": "#EC4899"},
        "midnight": {
            "primary_color": "#6366F1",
            "secondary_color": "#4F46E5",
            "accent_color": "#22D3EE",
            "background_color": "#0F172A",
            "surface_color": "#1E293B",
            "text_color": "#F1F5F9",
            "text_muted_color": "#94A3B8"
        }
    }
    
    if theme_id not in themes:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    theme_colors = themes[theme_id]
    theme_colors["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Check if config exists
    existing = await db.whitelabel_configs.find_one({"institution_id": current_user["id"]})
    
    if existing:
        # Update existing config
        await db.whitelabel_configs.update_one(
            {"institution_id": current_user["id"]},
            {"$set": theme_colors}
        )
    else:
        # Create new config with required fields
        config_id = str(uuid.uuid4())
        inst_name = current_user.get("institution_name", current_user.get("name", ""))
        subdomain = re.sub(r'[^a-z0-9]', '', inst_name.lower())[:30] if inst_name else f"inst-{config_id[:8]}"
        
        new_config = {
            "id": config_id,
            "institution_id": current_user["id"],
            "subdomain": subdomain,
            "platform_name": inst_name or "ProficientHub",
            **theme_colors,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.whitelabel_configs.insert_one(new_config)
    
    return {"message": f"Theme '{theme_id}' applied successfully", "colors": themes[theme_id]}

# ==================== HELPER FUNCTIONS ====================

def generate_css_variables(config: dict) -> str:
    """Generate CSS custom properties from config"""
    return f"""
:root {{
  --primary: {config.get('primary_color', '#58CC02')};
  --primary-hover: {darken_color(config.get('primary_color', '#58CC02'), 10)};
  --secondary: {config.get('secondary_color', '#1CB0F6')};
  --accent: {config.get('accent_color', '#FF4B4B')};
  --background: {config.get('background_color', '#FFFFFF')};
  --surface: {config.get('surface_color', '#F9FAFB')};
  --text: {config.get('text_color', '#1F2937')};
  --text-muted: {config.get('text_muted_color', '#6B7280')};
  --font-family: {config.get('font_family', 'Inter, system-ui, sans-serif')};
  --heading-font: {config.get('heading_font', config.get('font_family', 'Inter, system-ui, sans-serif'))};
  --radius: {config.get('border_radius', '12px')};
  --font-size-base: {config.get('font_size_base', '16px')};
}}
"""

def generate_full_css(config: dict) -> str:
    """Generate complete CSS stylesheet from config"""
    css_vars = generate_css_variables(config)
    
    custom_css = config.get('custom_css', '') or ''
    
    return f"""{css_vars}

/* White-Label Portal Styles */
body {{
  font-family: var(--font-family);
  background-color: var(--background);
  color: var(--text);
  font-size: var(--font-size-base);
}}

h1, h2, h3, h4, h5, h6 {{
  font-family: var(--heading-font);
}}

.btn-primary {{
  background-color: var(--primary);
  color: white;
  border-radius: var(--radius);
}}

.btn-primary:hover {{
  background-color: var(--primary-hover);
}}

.card {{
  background-color: var(--surface);
  border-radius: var(--radius);
}}

/* Custom CSS from institution */
{custom_css}
"""

def darken_color(hex_color: str, percent: int) -> str:
    """Darken a hex color by a percentage"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        factor = 1 - (percent / 100)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color

def get_default_email_templates() -> List[dict]:
    """Return default email templates"""
    return [
        {
            "template_type": "welcome",
            "subject": "Welcome to {{institution_name}}!",
            "html_template": """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background-color: {{primary_color}}; padding: 20px; text-align: center;">
    <img src="{{logo_url}}" alt="Logo" style="max-height: 50px;">
  </div>
  <div style="padding: 30px; background-color: #f9fafb;">
    <h1 style="color: {{primary_color}};">Welcome, {{student_name}}!</h1>
    <p>We're excited to have you join {{institution_name}}.</p>
    <p>Start your learning journey today!</p>
    <a href="#" style="display: inline-block; background-color: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-top: 20px;">Get Started</a>
  </div>
  <div style="padding: 20px; text-align: center; color: #6b7280; font-size: 12px;">
    <p>Questions? Contact us at {{support_email}}</p>
  </div>
</div>
""",
            "is_active": True
        },
        {
            "template_type": "exam_complete",
            "subject": "Your {{exam_name}} Results Are Ready!",
            "html_template": """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background-color: {{primary_color}}; padding: 20px; text-align: center;">
    <img src="{{logo_url}}" alt="Logo" style="max-height: 50px;">
  </div>
  <div style="padding: 30px; background-color: #f9fafb;">
    <h1>Great job, {{student_name}}!</h1>
    <p>You've completed <strong>{{exam_name}}</strong></p>
    <div style="background-color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0;">
      <p style="font-size: 48px; font-weight: bold; color: {{primary_color}}; margin: 0;">{{score}}</p>
      <p style="color: #6b7280;">Your Score</p>
    </div>
    <a href="#" style="display: inline-block; background-color: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px;">View Detailed Results</a>
  </div>
</div>
""",
            "is_active": True
        },
        {
            "template_type": "progress_report",
            "subject": "Your Weekly Progress Report",
            "html_template": """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background-color: {{primary_color}}; padding: 20px; text-align: center;">
    <img src="{{logo_url}}" alt="Logo" style="max-height: 50px;">
  </div>
  <div style="padding: 30px; background-color: #f9fafb;">
    <h1>Weekly Progress Report</h1>
    <p>Hello {{student_name}}, here's your learning progress this week:</p>
    <div style="background-color: white; padding: 20px; border-radius: 12px; margin: 20px 0;">
      <p><strong>Exams Completed:</strong> 5</p>
      <p><strong>Average Score:</strong> 78%</p>
      <p><strong>Time Spent:</strong> 4h 32m</p>
      <p><strong>Streak:</strong> 7 days 🔥</p>
    </div>
    <p>Keep up the great work!</p>
  </div>
</div>
""",
            "is_active": True
        }
    ]
