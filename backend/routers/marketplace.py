"""
Marketplace Router - Content marketplace endpoints
Handles listings, orders, and marketplace operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# Import shared dependencies
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth dependency - import from main server
from server import get_current_user

# ==================== MODELS ====================

class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    exam_type: str
    content_type: str  # material, course, exam_pack
    price: float
    currency: str = "USD"
    preview_content: Optional[str] = None
    tags: List[str] = []

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None

class OrderCreate(BaseModel):
    listing_id: str
    quantity: int = 1

# ==================== CATEGORIES ====================

MARKETPLACE_CATEGORIES = [
    {"id": "exam_packs", "name": "Exam Packs", "icon": "FileText"},
    {"id": "study_materials", "name": "Study Materials", "icon": "BookOpen"},
    {"id": "video_courses", "name": "Video Courses", "icon": "Video"},
    {"id": "practice_tests", "name": "Practice Tests", "icon": "Target"},
    {"id": "writing_samples", "name": "Writing Samples", "icon": "Edit"},
    {"id": "speaking_prompts", "name": "Speaking Prompts", "icon": "Mic"}
]

@router.get("/categories")
async def get_categories():
    """Get marketplace categories"""
    return {"categories": MARKETPLACE_CATEGORIES}

# ==================== LISTINGS ====================

@router.post("/listings")
async def create_listing(
    listing: ListingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new marketplace listing"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can create listings")
    
    listing_id = str(uuid.uuid4())
    
    listing_doc = {
        "id": listing_id,
        "seller_id": current_user["id"],
        "seller_name": current_user.get("institution_name") or current_user.get("name"),
        "title": listing.title,
        "description": listing.description,
        "category": listing.category,
        "exam_type": listing.exam_type,
        "content_type": listing.content_type,
        "price": listing.price,
        "currency": listing.currency,
        "preview_content": listing.preview_content,
        "tags": listing.tags,
        "is_active": True,
        "sales_count": 0,
        "rating": 0,
        "review_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketplace_listings.insert_one(listing_doc)
    
    return {"id": listing_id, "message": "Listing created successfully"}

@router.get("/listings")
async def get_listings(
    category: Optional[str] = None,
    exam_type: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    page: int = 1,
    per_page: int = 20
):
    """Get marketplace listings"""
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    if exam_type:
        query["exam_type"] = exam_type
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        query.setdefault("price", {})["$lte"] = max_price
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    skip = (page - 1) * per_page
    sort_dir = -1 if sort_by in ["created_at", "sales_count", "rating"] else 1
    
    listings = await db.marketplace_listings.find(
        query, {"_id": 0}
    ).sort(sort_by, sort_dir).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.marketplace_listings.count_documents(query)
    
    return {
        "listings": listings,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get a specific listing"""
    listing = await db.marketplace_listings.find_one(
        {"id": listing_id},
        {"_id": 0}
    )
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return listing

@router.get("/my-listings")
async def get_my_listings(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's listings"""
    skip = (page - 1) * per_page
    
    listings = await db.marketplace_listings.find(
        {"seller_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.marketplace_listings.count_documents({"seller_id": current_user["id"]})
    
    return {
        "listings": listings,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.put("/listings/{listing_id}")
async def update_listing(
    listing_id: str,
    updates: ListingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a listing"""
    listing = await db.marketplace_listings.find_one({"id": listing_id})
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing["seller_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.marketplace_listings.update_one(
        {"id": listing_id},
        {"$set": update_dict}
    )
    
    return {"message": "Listing updated"}

@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a listing"""
    listing = await db.marketplace_listings.find_one({"id": listing_id})
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing["seller_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    await db.marketplace_listings.delete_one({"id": listing_id})
    
    return {"message": "Listing deleted"}

# ==================== ORDERS ====================

@router.post("/orders")
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a marketplace order"""
    listing = await db.marketplace_listings.find_one({"id": order.listing_id})
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if not listing.get("is_active"):
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    order_id = str(uuid.uuid4())
    total = listing["price"] * order.quantity
    
    order_doc = {
        "id": order_id,
        "buyer_id": current_user["id"],
        "buyer_name": current_user.get("name") or current_user.get("institution_name"),
        "seller_id": listing["seller_id"],
        "listing_id": order.listing_id,
        "listing_title": listing["title"],
        "quantity": order.quantity,
        "unit_price": listing["price"],
        "total": total,
        "currency": listing["currency"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketplace_orders.insert_one(order_doc)
    
    # Update sales count
    await db.marketplace_listings.update_one(
        {"id": order.listing_id},
        {"$inc": {"sales_count": order.quantity}}
    )
    
    return {"id": order_id, "total": total, "message": "Order created"}

@router.get("/orders")
async def get_orders(
    role: str = "buyer",  # buyer or seller
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get orders (as buyer or seller)"""
    query = {}
    
    if role == "buyer":
        query["buyer_id"] = current_user["id"]
    else:
        query["seller_id"] = current_user["id"]
    
    if status:
        query["status"] = status
    
    skip = (page - 1) * per_page
    
    orders = await db.marketplace_orders.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.marketplace_orders.count_documents(query)
    
    return {
        "orders": orders,
        "total": total,
        "page": page,
        "per_page": per_page
    }
