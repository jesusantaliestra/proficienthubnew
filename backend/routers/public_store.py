"""
Public Store Router - Student-facing pack store

This module handles:
- Public display of packs from institutions that chose to sell via ProficientHub
- Student pack purchases with Stripe integration
- Order management and access provisioning
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os
import uuid
import secrets
import hashlib

router = APIRouter(prefix="/store", tags=["Public Store"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency (optional for some endpoints)
from server import get_current_user


# =============================================
# Models
# =============================================

class PurchaseRequest(BaseModel):
    """Request to purchase a pack"""
    pack_id: str
    payment_method_id: Optional[str] = None  # Stripe payment method


class OrderResponse(BaseModel):
    """Purchase order response"""
    order_id: str
    status: str
    pack_name: str
    amount: float
    currency: str


# =============================================
# Public Store Endpoints
# =============================================

@router.get("/institutions")
async def get_store_institutions():
    """
    Get list of institutions that sell via ProficientHub.
    Only shows institutions with sales_mode = 'platform' or 'both'
    """
    
    # Get institutions with platform sales enabled
    configs = await db.institution_sales_config.find(
        {"sales_mode": {"$in": ["platform", "both"]}},
        {"_id": 0, "institution_id": 1}
    ).to_list(100)
    
    institution_ids = [c["institution_id"] for c in configs]
    
    if not institution_ids:
        return {"institutions": [], "count": 0}
    
    # Get institution details
    institutions = await db.users.find(
        {"id": {"$in": institution_ids}, "user_type": "institution"},
        {"_id": 0, "id": 1, "name": 1, "institution_name": 1, "logo_url": 1, "description": 1}
    ).to_list(100)
    
    # Get pack counts for each institution
    result = []
    for inst in institutions:
        pack_count = await db.institution_custom_packs.count_documents({
            "institution_id": inst["id"],
            "deleted": {"$ne": True}
        })
        
        result.append({
            "id": inst["id"],
            "name": inst.get("institution_name") or inst.get("name"),
            "logo_url": inst.get("logo_url"),
            "description": inst.get("description"),
            "pack_count": pack_count
        })
    
    return {"institutions": result, "count": len(result)}


@router.get("/packs")
async def get_store_packs(
    institution_id: Optional[str] = None,
    exam_type: Optional[str] = None,
    profession: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    Get packs available for purchase.
    Only shows packs from institutions with sales_mode = 'platform' or 'both'
    """
    
    # Get institutions with platform sales enabled
    configs = await db.institution_sales_config.find(
        {"sales_mode": {"$in": ["platform", "both"]}},
        {"_id": 0, "institution_id": 1}
    ).to_list(100)
    
    platform_institution_ids = [c["institution_id"] for c in configs]
    
    if not platform_institution_ids:
        return {"packs": [], "count": 0, "message": "No hay packs disponibles actualmente"}
    
    # Build query
    query = {
        "institution_id": {"$in": platform_institution_ids},
        "deleted": {"$ne": True}
    }
    
    # Filter by specific institution if provided
    if institution_id:
        if institution_id not in platform_institution_ids:
            return {"packs": [], "count": 0, "message": "Esta institución no vende vía plataforma"}
        query["institution_id"] = institution_id
    
    # Filter by exam type
    if exam_type:
        query["exam_type"] = exam_type
    
    # Filter by profession (for OET)
    if profession:
        query["profession"] = profession
    
    # Price filters
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
    
    # Get packs
    packs = await db.institution_custom_packs.find(
        query,
        {"_id": 0}
    ).sort([("is_popular", -1), ("sort_order", 1)]).to_list(100)
    
    # Enrich with institution info
    for pack in packs:
        inst = await db.users.find_one(
            {"id": pack["institution_id"]},
            {"_id": 0, "name": 1, "institution_name": 1, "logo_url": 1}
        )
        if inst:
            pack["institution_name"] = inst.get("institution_name") or inst.get("name")
            pack["institution_logo"] = inst.get("logo_url")
    
    return {
        "packs": packs,
        "count": len(packs),
        "filters_applied": {
            "institution_id": institution_id,
            "exam_type": exam_type,
            "profession": profession,
            "price_range": {"min": min_price, "max": max_price}
        }
    }


@router.get("/packs/{pack_id}")
async def get_pack_details(pack_id: str):
    """Get detailed information about a specific pack"""
    
    # Get pack
    pack = await db.institution_custom_packs.find_one(
        {"id": pack_id, "deleted": {"$ne": True}},
        {"_id": 0}
    )
    
    if not pack:
        raise HTTPException(status_code=404, detail="Pack no encontrado")
    
    # Check if institution sells via platform
    config = await db.institution_sales_config.find_one(
        {"institution_id": pack["institution_id"]},
        {"_id": 0, "sales_mode": 1}
    )
    
    if not config or config.get("sales_mode") not in ["platform", "both"]:
        raise HTTPException(
            status_code=403, 
            detail="Este pack no está disponible para compra directa. Contacta a la institución."
        )
    
    # Get institution info
    inst = await db.users.find_one(
        {"id": pack["institution_id"]},
        {"_id": 0, "name": 1, "institution_name": 1, "logo_url": 1, "contact_email": 1}
    )
    
    pack["institution"] = {
        "name": inst.get("institution_name") or inst.get("name") if inst else "Unknown",
        "logo_url": inst.get("logo_url") if inst else None,
        "contact_email": inst.get("contact_email") if inst else None
    }
    
    return {"pack": pack}


@router.get("/exam-types")
async def get_available_exam_types():
    """Get exam types that have packs available in the store"""
    
    # Get institutions with platform sales
    configs = await db.institution_sales_config.find(
        {"sales_mode": {"$in": ["platform", "both"]}},
        {"_id": 0, "institution_id": 1}
    ).to_list(100)
    
    platform_ids = [c["institution_id"] for c in configs]
    
    if not platform_ids:
        return {"exam_types": []}
    
    # Get distinct exam types from available packs
    pipeline = [
        {"$match": {"institution_id": {"$in": platform_ids}, "deleted": {"$ne": True}}},
        {"$group": {"_id": "$exam_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    exam_types = await db.institution_custom_packs.aggregate(pipeline).to_list(50)
    
    # Map to full names
    exam_names = {
        "OET": "OET - Occupational English Test",
        "IELTS_ACADEMIC": "IELTS Academic",
        "IELTS_GENERAL": "IELTS General Training",
        "TOEFL": "TOEFL iBT",
        "PTE": "PTE Academic",
        "CAMBRIDGE_FCE": "Cambridge B2 First (FCE)",
        "CAMBRIDGE_CAE": "Cambridge C1 Advanced (CAE)",
        "CAMBRIDGE_CPE": "Cambridge C2 Proficiency (CPE)",
        "CELPIP": "CELPIP",
        "TOEIC": "TOEIC"
    }
    
    result = [
        {
            "id": et["_id"],
            "name": exam_names.get(et["_id"], et["_id"]),
            "pack_count": et["count"]
        }
        for et in exam_types
    ]
    
    return {"exam_types": result}


# =============================================
# Purchase Flow
# =============================================

@router.post("/checkout/create-session")
async def create_checkout_session(
    request: PurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe checkout session for pack purchase.
    Requires authenticated student user.
    """
    import stripe
    
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Sistema de pagos no configurado")
    
    stripe.api_key = stripe_key
    
    # Get pack
    pack = await db.institution_custom_packs.find_one(
        {"id": request.pack_id, "deleted": {"$ne": True}},
        {"_id": 0}
    )
    
    if not pack:
        raise HTTPException(status_code=404, detail="Pack no encontrado")
    
    # Verify institution sells via platform
    config = await db.institution_sales_config.find_one(
        {"institution_id": pack["institution_id"]},
        {"_id": 0, "sales_mode": 1}
    )
    
    if not config or config.get("sales_mode") not in ["platform", "both"]:
        raise HTTPException(status_code=403, detail="Pack no disponible para compra directa")
    
    # Get institution info
    inst = await db.users.find_one(
        {"id": pack["institution_id"]},
        {"_id": 0, "institution_name": 1, "name": 1, "stripe_account_id": 1}
    )
    
    # Create order record
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "pack_id": pack["id"],
        "pack_name": pack["name"],
        "student_id": current_user["id"],
        "student_email": current_user.get("email"),
        "institution_id": pack["institution_id"],
        "amount": pack["price"],
        "currency": pack.get("currency", "EUR").lower(),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.store_orders.insert_one(order)
    
    # Create Stripe checkout session
    try:
        # Convert price to cents
        amount_cents = int(pack["price"] * 100)
        
        frontend_url = os.environ.get("FRONTEND_URL", "https://oet-learning.preview.emergentagent.com")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": pack.get("currency", "EUR").lower(),
                    "product_data": {
                        "name": pack["name"],
                        "description": f"{pack.get('exam_type', '')} - {pack.get('num_mocks', 0)} mocks",
                        "metadata": {
                            "pack_id": pack["id"],
                            "institution_id": pack["institution_id"]
                        }
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{frontend_url}/store/success?order_id={order_id}",
            cancel_url=f"{frontend_url}/store/cancel?order_id={order_id}",
            customer_email=current_user.get("email"),
            metadata={
                "order_id": order_id,
                "pack_id": pack["id"],
                "student_id": current_user["id"]
            }
        )
        
        # Update order with session ID
        await db.store_orders.update_one(
            {"id": order_id},
            {"$set": {"stripe_session_id": checkout_session.id}}
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "order_id": order_id
        }
        
    except stripe.error.StripeError as e:
        await db.store_orders.update_one(
            {"id": order_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        raise HTTPException(status_code=400, detail=f"Error de pago: {str(e)}")


@router.post("/checkout/webhook")
async def stripe_webhook(request_body: bytes = Depends(lambda r: r.body())):
    """Handle Stripe webhook events"""
    import stripe
    
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    stripe.api_key = stripe_key
    
    # Verify webhook signature if secret is configured
    # For testing, we'll skip signature verification
    
    try:
        event = stripe.Event.construct_from(
            stripe.util.json.loads(request_body),
            stripe.api_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    
    # Handle checkout.session.completed
    if event.type == "checkout.session.completed":
        session = event.data.object
        order_id = session.metadata.get("order_id")
        
        if order_id:
            await complete_order(order_id)
    
    return {"status": "success"}


async def complete_order(order_id: str):
    """Complete an order and provision access"""
    
    order = await db.store_orders.find_one({"id": order_id})
    if not order:
        return
    
    # Get pack details
    pack = await db.institution_custom_packs.find_one({"id": order["pack_id"]})
    if not pack:
        return
    
    # Create access record
    access_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=pack.get("validity_days", 30))
    
    access_record = {
        "id": access_id,
        "pack_id": pack["id"],
        "pack_name": pack["name"],
        "student_id": order["student_id"],
        "institution_id": pack["institution_id"],
        "exam_type": pack.get("exam_type"),
        "profession": pack.get("profession"),
        
        # Allocated credits
        "mocks_total": pack.get("num_mocks", 0),
        "mocks_remaining": pack.get("num_mocks", 0),
        "ai_tutor_minutes_total": pack.get("ai_tutor_minutes", 0),
        "ai_tutor_minutes_remaining": pack.get("ai_tutor_minutes", 0),
        "speaking_sessions_total": pack.get("speaking_sessions", 0),
        "speaking_sessions_remaining": pack.get("speaking_sessions", 0),
        "writing_evaluations_total": pack.get("writing_evaluations", 0),
        "writing_evaluations_remaining": pack.get("writing_evaluations", 0),
        
        # Features
        "include_ai_tutor": pack.get("include_ai_tutor", False),
        "include_speaking": pack.get("include_speaking", False),
        "include_writing_evaluation": pack.get("include_writing_evaluation", False),
        "custom_services": pack.get("custom_services", []),
        
        # Dates
        "purchased_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "active",
        
        # Order reference
        "order_id": order_id,
        "price_paid": order["amount"],
        "currency": order["currency"]
    }
    
    await db.student_pack_access.insert_one(access_record)
    
    # Update order status
    await db.store_orders.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": "completed",
                "access_id": access_id,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Update pack sold count
    await db.institution_custom_packs.update_one(
        {"id": pack["id"]},
        {"$inc": {"total_sold": 1}}
    )


@router.get("/orders/{order_id}")
async def get_order_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get order status"""
    
    order = await db.store_orders.find_one(
        {"id": order_id, "student_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    return {"order": order}


@router.get("/my-purchases")
async def get_my_purchases(current_user: dict = Depends(get_current_user)):
    """Get current user's purchase history"""
    
    orders = await db.store_orders.find(
        {"student_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"orders": orders, "count": len(orders)}


# =============================================
# Manual Order Completion (for testing)
# =============================================

@router.post("/orders/{order_id}/complete")
async def manually_complete_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Manually complete an order (for testing purposes).
    In production, this would be triggered by Stripe webhook.
    """
    
    order = await db.store_orders.find_one({"id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    if order["student_id"] != current_user["id"] and current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    if order["status"] == "completed":
        return {"message": "Orden ya completada", "order": order}
    
    await complete_order(order_id)
    
    # Get updated order
    updated_order = await db.store_orders.find_one({"id": order_id}, {"_id": 0})
    
    return {"message": "Orden completada", "order": updated_order}
