"""
ProficientHub - Marketplace B2B API

API for the B2B marketplace where institutions can offer services to each other.
Includes listing management, bookings, reviews, and commission tracking.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models_b2b import Academy
from app.db.models_marketplace import (
    AcademyWallet,
    CommissionConfig,
    CommissionRecord,
    CommissionType,
    MarketplaceBooking,
    BookingStatus,
    MarketplaceListing,
    ListingStatus,
    ListingType,
    MarketplaceReview,
    WalletTransaction,
    TransactionType,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ListingCreateRequest(BaseModel):
    """Request to create a marketplace listing."""
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20, max_length=5000)
    listing_type: str
    category: str
    price: float = Field(ge=0)
    price_unit: str = Field(default="per_session")  # per_session, per_hour, per_student, fixed
    min_booking_quantity: int = Field(default=1, ge=1)
    max_booking_quantity: Optional[int] = Field(default=None, ge=1)
    availability: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None

    @field_validator('listing_type')
    @classmethod
    def validate_listing_type(cls, v: str) -> str:
        valid_types = [t.value for t in ListingType]
        if v not in valid_types:
            raise ValueError(f"Invalid listing type. Valid: {valid_types}")
        return v

    @field_validator('price_unit')
    @classmethod
    def validate_price_unit(cls, v: str) -> str:
        valid_units = ["per_session", "per_hour", "per_student", "fixed", "per_exam"]
        if v not in valid_units:
            raise ValueError(f"Invalid price unit. Valid: {valid_units}")
        return v


class ListingUpdateRequest(BaseModel):
    """Request to update a marketplace listing."""
    title: Optional[str] = Field(default=None, min_length=5, max_length=200)
    description: Optional[str] = Field(default=None, min_length=20, max_length=5000)
    price: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    availability: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class BookingCreateRequest(BaseModel):
    """Request to create a booking."""
    listing_id: str
    quantity: int = Field(ge=1)
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=1000)
    contact_info: Optional[Dict[str, str]] = None


class BookingUpdateRequest(BaseModel):
    """Request to update a booking."""
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_statuses = [s.value for s in BookingStatus]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Valid: {valid_statuses}")
        return v


class ReviewCreateRequest(BaseModel):
    """Request to create a review."""
    booking_id: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=100)
    comment: Optional[str] = Field(default=None, max_length=2000)
    would_recommend: bool = True


class MarketplaceSearchRequest(BaseModel):
    """Search parameters for marketplace."""
    query: Optional[str] = None
    listing_type: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field(default="relevance")  # relevance, price_low, price_high, rating, newest

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        valid = ["relevance", "price_low", "price_high", "rating", "newest"]
        if v not in valid:
            raise ValueError(f"Invalid sort_by. Valid: {valid}")
        return v


# ============================================================================
# LISTING ENDPOINTS
# ============================================================================

@router.post("/listings")
async def create_listing(
    seller_academy_id: str,
    request: ListingCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a new marketplace listing.
    Academies can offer services to other institutions.
    """
    # Verify academy exists
    academy_result = await db.execute(
        select(Academy).where(Academy.id == seller_academy_id)
    )
    academy = academy_result.scalar_one_or_none()
    if not academy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academy not found"
        )

    # Create listing
    listing = MarketplaceListing(
        seller_academy_id=seller_academy_id,
        title=request.title,
        description=request.description,
        listing_type=ListingType(request.listing_type),
        category=request.category,
        price=Decimal(str(request.price)),
        price_unit=request.price_unit,
        min_booking_quantity=request.min_booking_quantity,
        max_booking_quantity=request.max_booking_quantity,
        availability=request.availability or {},
        requirements=request.requirements or [],
        tags=request.tags or [],
        images=request.images or [],
        status=ListingStatus.PENDING_REVIEW,  # Requires approval
        is_featured=False,
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)

    return {
        "status": "success",
        "listing_id": str(listing.id),
        "message": "Listing created and pending review",
        "listing": {
            "id": str(listing.id),
            "title": listing.title,
            "listing_type": listing.listing_type.value,
            "price": float(listing.price),
            "status": listing.status.value,
        },
    }


@router.get("/listings/{listing_id}")
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get detailed information about a listing.
    """
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Get seller academy info
    academy_result = await db.execute(
        select(Academy).where(Academy.id == listing.seller_academy_id)
    )
    academy = academy_result.scalar_one_or_none()

    # Get reviews
    reviews_result = await db.execute(
        select(MarketplaceReview)
        .where(MarketplaceReview.listing_id == listing_id)
        .order_by(MarketplaceReview.created_at.desc())
        .limit(10)
    )
    reviews = reviews_result.scalars().all()

    # Calculate average rating
    rating_result = await db.execute(
        select(func.avg(MarketplaceReview.rating)).where(
            MarketplaceReview.listing_id == listing_id
        )
    )
    avg_rating = rating_result.scalar() or 0

    # Count total bookings
    booking_count_result = await db.execute(
        select(func.count(MarketplaceBooking.id)).where(
            and_(
                MarketplaceBooking.listing_id == listing_id,
                MarketplaceBooking.status == BookingStatus.COMPLETED
            )
        )
    )
    total_bookings = booking_count_result.scalar() or 0

    return {
        "listing": {
            "id": str(listing.id),
            "title": listing.title,
            "description": listing.description,
            "listing_type": listing.listing_type.value,
            "category": listing.category,
            "price": float(listing.price),
            "price_unit": listing.price_unit,
            "min_booking_quantity": listing.min_booking_quantity,
            "max_booking_quantity": listing.max_booking_quantity,
            "availability": listing.availability,
            "requirements": listing.requirements,
            "tags": listing.tags,
            "images": listing.images,
            "status": listing.status.value,
            "is_featured": listing.is_featured,
            "created_at": listing.created_at.isoformat(),
        },
        "seller": {
            "id": str(academy.id) if academy else None,
            "name": academy.name if academy else "Unknown",
        },
        "stats": {
            "average_rating": round(float(avg_rating), 1),
            "total_reviews": len(reviews),
            "total_bookings": total_bookings,
        },
        "reviews": [
            {
                "id": str(r.id),
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    }


@router.put("/listings/{listing_id}")
async def update_listing(
    listing_id: str,
    seller_academy_id: str,
    request: ListingUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update a marketplace listing.
    Only the seller academy can update their listings.
    """
    result = await db.execute(
        select(MarketplaceListing).where(
            and_(
                MarketplaceListing.id == listing_id,
                MarketplaceListing.seller_academy_id == seller_academy_id
            )
        )
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or unauthorized"
        )

    # Update fields
    if request.title is not None:
        listing.title = request.title
    if request.description is not None:
        listing.description = request.description
    if request.price is not None:
        listing.price = Decimal(str(request.price))
    if request.is_active is not None:
        listing.status = ListingStatus.ACTIVE if request.is_active else ListingStatus.INACTIVE
    if request.availability is not None:
        listing.availability = request.availability
    if request.requirements is not None:
        listing.requirements = request.requirements
    if request.tags is not None:
        listing.tags = request.tags

    listing.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "listing_id": str(listing.id),
        "message": "Listing updated successfully",
    }


@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: str,
    seller_academy_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Delete (deactivate) a marketplace listing.
    """
    result = await db.execute(
        select(MarketplaceListing).where(
            and_(
                MarketplaceListing.id == listing_id,
                MarketplaceListing.seller_academy_id == seller_academy_id
            )
        )
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or unauthorized"
        )

    # Check for active bookings
    active_bookings = await db.execute(
        select(func.count(MarketplaceBooking.id)).where(
            and_(
                MarketplaceBooking.listing_id == listing_id,
                MarketplaceBooking.status.in_([
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                    BookingStatus.IN_PROGRESS
                ])
            )
        )
    )
    if active_bookings.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete listing with active bookings"
        )

    listing.status = ListingStatus.DELETED
    listing.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "message": "Listing deleted",
    }


@router.get("/listings")
async def get_my_listings(
    seller_academy_id: str,
    status_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get all listings for a seller academy.
    """
    query = select(MarketplaceListing).where(
        MarketplaceListing.seller_academy_id == seller_academy_id
    )

    if status_filter:
        try:
            status_enum = ListingStatus(status_filter)
            query = query.where(MarketplaceListing.status == status_enum)
        except ValueError:
            pass

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(MarketplaceListing.created_at.desc())
    )
    listings = result.scalars().all()

    return {
        "listings": [
            {
                "id": str(l.id),
                "title": l.title,
                "listing_type": l.listing_type.value,
                "category": l.category,
                "price": float(l.price),
                "status": l.status.value,
                "is_featured": l.is_featured,
                "created_at": l.created_at.isoformat(),
            }
            for l in listings
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# SEARCH & BROWSE
# ============================================================================

@router.post("/search")
async def search_marketplace(
    request: MarketplaceSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Search and filter marketplace listings.
    """
    query = select(MarketplaceListing).where(
        MarketplaceListing.status == ListingStatus.ACTIVE
    )

    # Apply filters
    if request.listing_type:
        try:
            type_enum = ListingType(request.listing_type)
            query = query.where(MarketplaceListing.listing_type == type_enum)
        except ValueError:
            pass

    if request.category:
        query = query.where(MarketplaceListing.category == request.category)

    if request.min_price is not None:
        query = query.where(MarketplaceListing.price >= Decimal(str(request.min_price)))

    if request.max_price is not None:
        query = query.where(MarketplaceListing.price <= Decimal(str(request.max_price)))

    if request.tags:
        # Filter by tags (any match)
        for tag in request.tags:
            query = query.where(MarketplaceListing.tags.contains([tag]))

    # Text search on title and description
    if request.query:
        search_term = f"%{request.query}%"
        query = query.where(
            or_(
                MarketplaceListing.title.ilike(search_term),
                MarketplaceListing.description.ilike(search_term)
            )
        )

    # Apply sorting
    if request.sort_by == "price_low":
        query = query.order_by(MarketplaceListing.price.asc())
    elif request.sort_by == "price_high":
        query = query.order_by(MarketplaceListing.price.desc())
    elif request.sort_by == "newest":
        query = query.order_by(MarketplaceListing.created_at.desc())
    else:  # relevance or rating - default to featured first, then newest
        query = query.order_by(
            MarketplaceListing.is_featured.desc(),
            MarketplaceListing.created_at.desc()
        )

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(query.offset(skip).limit(limit))
    listings = result.scalars().all()

    # Get seller info and ratings for each listing
    enriched_listings = []
    for listing in listings:
        # Get seller
        academy_result = await db.execute(
            select(Academy).where(Academy.id == listing.seller_academy_id)
        )
        academy = academy_result.scalar_one_or_none()

        # Get average rating
        rating_result = await db.execute(
            select(func.avg(MarketplaceReview.rating)).where(
                MarketplaceReview.listing_id == listing.id
            )
        )
        avg_rating = rating_result.scalar() or 0

        enriched_listings.append({
            "id": str(listing.id),
            "title": listing.title,
            "description": listing.description[:200] + "..." if len(listing.description) > 200 else listing.description,
            "listing_type": listing.listing_type.value,
            "category": listing.category,
            "price": float(listing.price),
            "price_unit": listing.price_unit,
            "tags": listing.tags,
            "images": listing.images[:1] if listing.images else [],  # First image only
            "is_featured": listing.is_featured,
            "seller_name": academy.name if academy else "Unknown",
            "average_rating": round(float(avg_rating), 1),
        })

    return {
        "results": enriched_listings,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


@router.get("/categories")
async def get_marketplace_categories(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get all available marketplace categories with listing counts.
    """
    # Get categories with counts
    result = await db.execute(
        select(
            MarketplaceListing.category,
            func.count(MarketplaceListing.id).label("count")
        )
        .where(MarketplaceListing.status == ListingStatus.ACTIVE)
        .group_by(MarketplaceListing.category)
    )
    categories = result.all()

    # Predefined category metadata
    category_info = {
        "exam_preparation": {
            "name": "Exam Preparation",
            "description": "Mock exams, practice tests, and exam simulation services",
            "icon": "exam",
        },
        "teacher_training": {
            "name": "Teacher Training",
            "description": "Professional development and certification programs",
            "icon": "training",
        },
        "curriculum_development": {
            "name": "Curriculum Development",
            "description": "Custom course materials and syllabus design",
            "icon": "curriculum",
        },
        "technology_services": {
            "name": "Technology Services",
            "description": "LMS integration, platform customization, and tech support",
            "icon": "tech",
        },
        "marketing_services": {
            "name": "Marketing Services",
            "description": "Student recruitment and marketing support",
            "icon": "marketing",
        },
        "consulting": {
            "name": "Consulting",
            "description": "Educational consulting and advisory services",
            "icon": "consulting",
        },
        "content_creation": {
            "name": "Content Creation",
            "description": "Educational content, videos, and materials",
            "icon": "content",
        },
        "assessment_services": {
            "name": "Assessment Services",
            "description": "Student evaluation and placement testing",
            "icon": "assessment",
        },
    }

    enriched_categories = []
    for cat, count in categories:
        info = category_info.get(cat, {"name": cat, "description": "", "icon": "default"})
        enriched_categories.append({
            "id": cat,
            "name": info["name"],
            "description": info["description"],
            "icon": info["icon"],
            "listing_count": count,
        })

    return {
        "categories": enriched_categories,
        "total_categories": len(enriched_categories),
    }


# ============================================================================
# BOOKING ENDPOINTS
# ============================================================================

@router.post("/bookings")
async def create_booking(
    buyer_academy_id: str,
    request: BookingCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a booking for a marketplace listing.
    """
    # Get listing
    listing_result = await db.execute(
        select(MarketplaceListing).where(
            and_(
                MarketplaceListing.id == request.listing_id,
                MarketplaceListing.status == ListingStatus.ACTIVE
            )
        )
    )
    listing = listing_result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not available"
        )

    # Prevent self-booking
    if listing.seller_academy_id == buyer_academy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book your own listing"
        )

    # Validate quantity
    if request.quantity < listing.min_booking_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum booking quantity is {listing.min_booking_quantity}"
        )

    if listing.max_booking_quantity and request.quantity > listing.max_booking_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum booking quantity is {listing.max_booking_quantity}"
        )

    # Calculate total price
    total_price = listing.price * request.quantity

    # Get commission rate
    commission_result = await db.execute(
        select(CommissionConfig).where(
            CommissionConfig.commission_type == CommissionType.MARKETPLACE_SALE
        )
    )
    commission_config = commission_result.scalar_one_or_none()
    commission_rate = Decimal(str(commission_config.rate_percent / 100)) if commission_config else Decimal("0.15")

    platform_fee = total_price * commission_rate
    seller_amount = total_price - platform_fee

    # Create booking
    booking = MarketplaceBooking(
        listing_id=listing.id,
        buyer_academy_id=buyer_academy_id,
        seller_academy_id=listing.seller_academy_id,
        quantity=request.quantity,
        unit_price=listing.price,
        total_price=total_price,
        platform_fee=platform_fee,
        seller_amount=seller_amount,
        status=BookingStatus.PENDING,
        scheduled_date=request.scheduled_date,
        notes=request.notes,
        contact_info=request.contact_info or {},
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return {
        "status": "success",
        "booking_id": str(booking.id),
        "booking": {
            "id": str(booking.id),
            "listing_id": str(listing.id),
            "listing_title": listing.title,
            "quantity": request.quantity,
            "total_price": float(total_price),
            "platform_fee": float(platform_fee),
            "status": booking.status.value,
            "scheduled_date": booking.scheduled_date.isoformat() if booking.scheduled_date else None,
        },
    }


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: str,
    academy_id: str,  # Either buyer or seller
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get booking details.
    Accessible by both buyer and seller academies.
    """
    result = await db.execute(
        select(MarketplaceBooking).where(
            and_(
                MarketplaceBooking.id == booking_id,
                or_(
                    MarketplaceBooking.buyer_academy_id == academy_id,
                    MarketplaceBooking.seller_academy_id == academy_id
                )
            )
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or unauthorized"
        )

    # Get listing
    listing_result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == booking.listing_id)
    )
    listing = listing_result.scalar_one_or_none()

    # Get buyer and seller info
    buyer_result = await db.execute(
        select(Academy).where(Academy.id == booking.buyer_academy_id)
    )
    buyer = buyer_result.scalar_one_or_none()

    seller_result = await db.execute(
        select(Academy).where(Academy.id == booking.seller_academy_id)
    )
    seller = seller_result.scalar_one_or_none()

    return {
        "booking": {
            "id": str(booking.id),
            "status": booking.status.value,
            "quantity": booking.quantity,
            "unit_price": float(booking.unit_price),
            "total_price": float(booking.total_price),
            "platform_fee": float(booking.platform_fee),
            "seller_amount": float(booking.seller_amount),
            "scheduled_date": booking.scheduled_date.isoformat() if booking.scheduled_date else None,
            "completed_at": booking.completed_at.isoformat() if booking.completed_at else None,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat(),
        },
        "listing": {
            "id": str(listing.id) if listing else None,
            "title": listing.title if listing else "Unknown",
            "listing_type": listing.listing_type.value if listing else None,
        },
        "buyer": {
            "id": str(buyer.id) if buyer else None,
            "name": buyer.name if buyer else "Unknown",
        },
        "seller": {
            "id": str(seller.id) if seller else None,
            "name": seller.name if seller else "Unknown",
        },
        "is_buyer": str(booking.buyer_academy_id) == academy_id,
    }


@router.put("/bookings/{booking_id}")
async def update_booking(
    booking_id: str,
    academy_id: str,
    request: BookingUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update booking status or details.
    Sellers can confirm/complete, buyers can cancel pending bookings.
    """
    result = await db.execute(
        select(MarketplaceBooking).where(
            and_(
                MarketplaceBooking.id == booking_id,
                or_(
                    MarketplaceBooking.buyer_academy_id == academy_id,
                    MarketplaceBooking.seller_academy_id == academy_id
                )
            )
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or unauthorized"
        )

    is_seller = str(booking.seller_academy_id) == academy_id
    is_buyer = str(booking.buyer_academy_id) == academy_id

    # Status change logic
    if request.status:
        new_status = BookingStatus(request.status)

        # Validate status transitions
        valid_transitions = {
            BookingStatus.PENDING: {
                "seller": [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
                "buyer": [BookingStatus.CANCELLED],
            },
            BookingStatus.CONFIRMED: {
                "seller": [BookingStatus.IN_PROGRESS, BookingStatus.CANCELLED],
                "buyer": [BookingStatus.CANCELLED],
            },
            BookingStatus.IN_PROGRESS: {
                "seller": [BookingStatus.COMPLETED],
                "buyer": [],
            },
            BookingStatus.COMPLETED: {
                "seller": [],
                "buyer": [],
            },
        }

        role = "seller" if is_seller else "buyer"
        allowed = valid_transitions.get(booking.status, {}).get(role, [])

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {booking.status.value} to {new_status.value} as {role}"
            )

        booking.status = new_status

        # Handle completion
        if new_status == BookingStatus.COMPLETED:
            booking.completed_at = datetime.now(timezone.utc)

            # Create commission record
            commission_record = CommissionRecord(
                academy_id=booking.seller_academy_id,
                commission_type=CommissionType.MARKETPLACE_SALE,
                order_id=None,
                booking_id=booking.id,
                gross_amount=booking.total_price,
                commission_amount=booking.platform_fee,
                net_amount=booking.seller_amount,
                is_paid=False,
            )
            db.add(commission_record)

            # Add to seller wallet
            wallet_result = await db.execute(
                select(AcademyWallet).where(
                    AcademyWallet.academy_id == booking.seller_academy_id
                )
            )
            wallet = wallet_result.scalar_one_or_none()

            if wallet:
                wallet.balance += booking.seller_amount
                wallet.updated_at = datetime.now(timezone.utc)

                # Create transaction
                transaction = WalletTransaction(
                    wallet_id=wallet.id,
                    type=TransactionType.COMMISSION,
                    amount=booking.seller_amount,
                    balance_after=wallet.balance,
                    description=f"Marketplace sale: Booking #{str(booking.id)[:8]}",
                    reference_type="booking",
                    reference_id=str(booking.id),
                )
                db.add(transaction)

    if request.scheduled_date is not None:
        booking.scheduled_date = request.scheduled_date

    if request.notes is not None:
        booking.notes = request.notes

    booking.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "booking_id": str(booking.id),
        "new_status": booking.status.value,
    }


@router.get("/bookings")
async def get_my_bookings(
    academy_id: str,
    role: str = Query(default="all", regex="^(buyer|seller|all)$"),
    status_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get bookings for an academy.
    Filter by role (buyer, seller, or all).
    """
    query = select(MarketplaceBooking)

    if role == "buyer":
        query = query.where(MarketplaceBooking.buyer_academy_id == academy_id)
    elif role == "seller":
        query = query.where(MarketplaceBooking.seller_academy_id == academy_id)
    else:
        query = query.where(
            or_(
                MarketplaceBooking.buyer_academy_id == academy_id,
                MarketplaceBooking.seller_academy_id == academy_id
            )
        )

    if status_filter:
        try:
            status_enum = BookingStatus(status_filter)
            query = query.where(MarketplaceBooking.status == status_enum)
        except ValueError:
            pass

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(MarketplaceBooking.created_at.desc())
    )
    bookings = result.scalars().all()

    bookings_list = []
    for b in bookings:
        # Get listing title
        listing_result = await db.execute(
            select(MarketplaceListing).where(MarketplaceListing.id == b.listing_id)
        )
        listing = listing_result.scalar_one_or_none()

        bookings_list.append({
            "id": str(b.id),
            "listing_id": str(b.listing_id),
            "listing_title": listing.title if listing else "Unknown",
            "status": b.status.value,
            "quantity": b.quantity,
            "total_price": float(b.total_price),
            "is_buyer": str(b.buyer_academy_id) == academy_id,
            "scheduled_date": b.scheduled_date.isoformat() if b.scheduled_date else None,
            "created_at": b.created_at.isoformat(),
        })

    return {
        "bookings": bookings_list,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.post("/reviews")
async def create_review(
    buyer_academy_id: str,
    request: ReviewCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a review for a completed booking.
    Only buyers can leave reviews.
    """
    # Get booking
    booking_result = await db.execute(
        select(MarketplaceBooking).where(
            and_(
                MarketplaceBooking.id == request.booking_id,
                MarketplaceBooking.buyer_academy_id == buyer_academy_id,
                MarketplaceBooking.status == BookingStatus.COMPLETED
            )
        )
    )
    booking = booking_result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found, not yours, or not completed"
        )

    # Check if already reviewed
    existing_review = await db.execute(
        select(MarketplaceReview).where(
            MarketplaceReview.booking_id == request.booking_id
        )
    )
    if existing_review.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already exists for this booking"
        )

    # Create review
    review = MarketplaceReview(
        listing_id=booking.listing_id,
        booking_id=booking.id,
        reviewer_academy_id=buyer_academy_id,
        rating=request.rating,
        title=request.title,
        comment=request.comment,
        would_recommend=request.would_recommend,
        is_verified=True,  # Verified because linked to completed booking
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    return {
        "status": "success",
        "review_id": str(review.id),
        "review": {
            "id": str(review.id),
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "is_verified": review.is_verified,
        },
    }


@router.get("/reviews/{listing_id}")
async def get_listing_reviews(
    listing_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get reviews for a listing.
    """
    # Count total
    count_result = await db.execute(
        select(func.count(MarketplaceReview.id)).where(
            MarketplaceReview.listing_id == listing_id
        )
    )
    total = count_result.scalar() or 0

    # Get reviews
    result = await db.execute(
        select(MarketplaceReview)
        .where(MarketplaceReview.listing_id == listing_id)
        .order_by(MarketplaceReview.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()

    # Calculate stats
    stats_result = await db.execute(
        select(
            func.avg(MarketplaceReview.rating),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.rating == 5),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.rating == 4),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.rating == 3),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.rating == 2),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.rating == 1),
            func.count(MarketplaceReview.id).filter(MarketplaceReview.would_recommend == True),
        ).where(MarketplaceReview.listing_id == listing_id)
    )
    stats = stats_result.one()

    reviews_list = []
    for r in reviews:
        # Get reviewer name
        reviewer_result = await db.execute(
            select(Academy).where(Academy.id == r.reviewer_academy_id)
        )
        reviewer = reviewer_result.scalar_one_or_none()

        reviews_list.append({
            "id": str(r.id),
            "rating": r.rating,
            "title": r.title,
            "comment": r.comment,
            "would_recommend": r.would_recommend,
            "is_verified": r.is_verified,
            "reviewer_name": reviewer.name if reviewer else "Anonymous",
            "created_at": r.created_at.isoformat(),
        })

    return {
        "reviews": reviews_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "stats": {
            "average_rating": round(float(stats[0] or 0), 1),
            "rating_distribution": {
                5: stats[1] or 0,
                4: stats[2] or 0,
                3: stats[3] or 0,
                2: stats[4] or 0,
                1: stats[5] or 0,
            },
            "recommendation_rate": (
                round((stats[6] or 0) / total * 100, 1) if total > 0 else 0
            ),
        },
    }


# ============================================================================
# COMMISSION & EARNINGS
# ============================================================================

@router.get("/earnings/{academy_id}")
async def get_marketplace_earnings(
    academy_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get marketplace earnings for a seller academy.
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get completed bookings as seller
    bookings_result = await db.execute(
        select(MarketplaceBooking).where(
            and_(
                MarketplaceBooking.seller_academy_id == academy_id,
                MarketplaceBooking.status == BookingStatus.COMPLETED,
                MarketplaceBooking.completed_at >= start_date,
                MarketplaceBooking.completed_at <= end_date,
            )
        )
    )
    bookings = bookings_result.scalars().all()

    # Calculate totals
    total_gross = sum(float(b.total_price) for b in bookings)
    total_fees = sum(float(b.platform_fee) for b in bookings)
    total_net = sum(float(b.seller_amount) for b in bookings)

    # Get commission records
    commission_result = await db.execute(
        select(CommissionRecord).where(
            and_(
                CommissionRecord.academy_id == academy_id,
                CommissionRecord.commission_type == CommissionType.MARKETPLACE_SALE,
                CommissionRecord.created_at >= start_date,
                CommissionRecord.created_at <= end_date,
            )
        )
    )
    commissions = commission_result.scalars().all()

    pending_payout = sum(
        float(c.net_amount) for c in commissions if not c.is_paid
    )
    paid_out = sum(
        float(c.net_amount) for c in commissions if c.is_paid
    )

    # Group by month
    from collections import defaultdict
    monthly_earnings = defaultdict(lambda: {"gross": 0, "fees": 0, "net": 0, "bookings": 0})

    for b in bookings:
        month_key = b.completed_at.strftime("%Y-%m")
        monthly_earnings[month_key]["gross"] += float(b.total_price)
        monthly_earnings[month_key]["fees"] += float(b.platform_fee)
        monthly_earnings[month_key]["net"] += float(b.seller_amount)
        monthly_earnings[month_key]["bookings"] += 1

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "summary": {
            "total_gross_sales": round(total_gross, 2),
            "total_platform_fees": round(total_fees, 2),
            "total_net_earnings": round(total_net, 2),
            "total_bookings": len(bookings),
            "pending_payout": round(pending_payout, 2),
            "total_paid_out": round(paid_out, 2),
        },
        "monthly_breakdown": [
            {"month": k, **v}
            for k, v in sorted(monthly_earnings.items())
        ],
        "commission_rate": "15%",  # Default marketplace commission
    }


@router.post("/payout-request/{academy_id}")
async def request_payout(
    academy_id: str,
    amount: Optional[float] = Query(default=None, gt=0),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Request a payout of marketplace earnings.
    """
    # Get wallet
    wallet_result = await db.execute(
        select(AcademyWallet).where(AcademyWallet.academy_id == academy_id)
    )
    wallet = wallet_result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )

    # Determine payout amount
    payout_amount = Decimal(str(amount)) if amount else wallet.balance

    if payout_amount > wallet.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {wallet.balance}"
        )

    min_payout = Decimal("50.00")
    if payout_amount < min_payout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum payout amount is ${min_payout}"
        )

    # Create payout request (in production, would trigger actual payout)
    # Deduct from wallet
    wallet.balance -= payout_amount
    wallet.updated_at = datetime.now(timezone.utc)

    # Create transaction
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        type=TransactionType.PAYOUT,
        amount=-payout_amount,
        balance_after=wallet.balance,
        description="Payout request",
        reference_type="payout",
    )
    db.add(transaction)

    # Mark commissions as paid
    await db.execute(
        CommissionRecord.__table__.update()
        .where(
            and_(
                CommissionRecord.academy_id == academy_id,
                CommissionRecord.is_paid == False
            )
        )
        .values(is_paid=True, paid_at=datetime.now(timezone.utc))
    )

    await db.commit()

    return {
        "status": "success",
        "payout_amount": float(payout_amount),
        "remaining_balance": float(wallet.balance),
        "estimated_arrival": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "message": "Payout request submitted. Funds will be transferred within 3 business days.",
    }


# ============================================================================
# FEATURED LISTINGS (Admin)
# ============================================================================

@router.post("/admin/feature/{listing_id}")
async def feature_listing(
    listing_id: str,
    is_featured: bool = True,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Admin endpoint to feature/unfeature a listing.
    """
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    listing.is_featured = is_featured
    listing.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "listing_id": str(listing.id),
        "is_featured": listing.is_featured,
    }


@router.post("/admin/approve/{listing_id}")
async def approve_listing(
    listing_id: str,
    approved: bool = True,
    rejection_reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Admin endpoint to approve or reject a listing.
    """
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    if approved:
        listing.status = ListingStatus.ACTIVE
    else:
        listing.status = ListingStatus.REJECTED
        # Store rejection reason in metadata or separate field

    listing.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "listing_id": str(listing.id),
        "listing_status": listing.status.value,
        "approved": approved,
    }
