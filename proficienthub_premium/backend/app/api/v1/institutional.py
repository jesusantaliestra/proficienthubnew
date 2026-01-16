"""
ProficientHub - Institutional Dashboard API

Enterprise API for managing academies, products, students, and sales.
Includes upsell capabilities and institutional pricing.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models_b2b import (
    Academy,
    AcademyBillingPlan,
    AcademyCreditBalance,
    StudentEnrollment,
)
from app.db.models_marketplace import (
    AcademyProductPrice,
    AcademyWallet,
    CommissionConfig,
    CommissionRecord,
    CommissionType,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductCategory,
    ProductVariant,
    WalletTransaction,
    TransactionType,
)
from app.exceptions import (
    ProficientHubError,
    InsufficientCreditsError,
)

router = APIRouter(prefix="/institutional", tags=["institutional"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class AcademyDashboardResponse(BaseModel):
    """Academy dashboard overview data."""
    academy_id: str
    academy_name: str
    credit_balance: int
    total_students: int
    active_students: int
    total_revenue: float
    monthly_revenue: float
    pending_orders: int
    active_products: int
    wallet_balance: float


class ProductListResponse(BaseModel):
    """Product catalog for institutional purchasing."""
    products: List[Dict[str, Any]]
    total: int
    categories: List[str]


class ProductPurchaseRequest(BaseModel):
    """Request to purchase products."""
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(ge=1, le=1000)
    payment_method: str = Field(default="wallet")  # wallet, stripe, invoice

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        valid_methods = ["wallet", "stripe", "invoice"]
        if v not in valid_methods:
            raise ValueError(f"Invalid payment method. Valid: {valid_methods}")
        return v


class CustomPricingRequest(BaseModel):
    """Request to set custom pricing for resale."""
    product_id: str
    variant_id: Optional[str] = None
    custom_price: float = Field(ge=0)
    is_active: bool = True
    min_quantity: int = Field(default=1, ge=1)
    max_discount_percent: Optional[float] = Field(default=None, ge=0, le=100)


class StudentEnrollmentRequest(BaseModel):
    """Request to enroll student in a product/course."""
    student_user_id: str
    product_type: str  # mock_exam, writing_review, speaking_session, course
    exam_type: Optional[str] = None
    quantity: int = Field(default=1, ge=1)


class SalesAnalyticsRequest(BaseModel):
    """Request for sales analytics."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: str = Field(default="day")  # day, week, month

    @field_validator('group_by')
    @classmethod
    def validate_group_by(cls, v: str) -> str:
        valid = ["day", "week", "month"]
        if v not in valid:
            raise ValueError(f"Invalid group_by. Valid: {valid}")
        return v


class UpsellOfferResponse(BaseModel):
    """Upsell offer for institutions."""
    offer_id: str
    title: str
    description: str
    original_price: float
    offer_price: float
    discount_percent: float
    products: List[Dict[str, Any]]
    valid_until: datetime
    terms: List[str]


# ============================================================================
# DASHBOARD OVERVIEW ENDPOINTS
# ============================================================================

@router.get("/dashboard/{academy_id}", response_model=AcademyDashboardResponse)
async def get_academy_dashboard(
    academy_id: str,
    db: AsyncSession = Depends(get_db),
) -> AcademyDashboardResponse:
    """
    Get comprehensive dashboard overview for an academy.
    Includes credits, students, revenue, and product stats.
    """
    # Get academy
    academy_result = await db.execute(
        select(Academy).where(Academy.id == academy_id)
    )
    academy = academy_result.scalar_one_or_none()
    if not academy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academy {academy_id} not found"
        )

    # Get credit balance
    credit_result = await db.execute(
        select(AcademyCreditBalance).where(
            AcademyCreditBalance.academy_id == academy_id
        )
    )
    credit_balance = credit_result.scalar_one_or_none()
    credits = credit_balance.balance if credit_balance else 0

    # Count students
    student_count_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.academy_id == academy_id
        )
    )
    total_students = student_count_result.scalar() or 0

    active_student_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            and_(
                StudentEnrollment.academy_id == academy_id,
                StudentEnrollment.is_active == True
            )
        )
    )
    active_students = active_student_result.scalar() or 0

    # Calculate revenue
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            and_(
                Order.academy_id == academy_id,
                Order.status == OrderStatus.COMPLETED,
                Order.is_b2b_sale == True
            )
        )
    )
    total_revenue = float(revenue_result.scalar() or 0)

    # Monthly revenue
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0)
    monthly_revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            and_(
                Order.academy_id == academy_id,
                Order.status == OrderStatus.COMPLETED,
                Order.is_b2b_sale == True,
                Order.created_at >= month_start
            )
        )
    )
    monthly_revenue = float(monthly_revenue_result.scalar() or 0)

    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id)).where(
            and_(
                Order.academy_id == academy_id,
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING])
            )
        )
    )
    pending_orders = pending_result.scalar() or 0

    # Active products
    active_products_result = await db.execute(
        select(func.count(AcademyProductPrice.id)).where(
            and_(
                AcademyProductPrice.academy_id == academy_id,
                AcademyProductPrice.is_active == True
            )
        )
    )
    active_products = active_products_result.scalar() or 0

    # Wallet balance
    wallet_result = await db.execute(
        select(AcademyWallet).where(AcademyWallet.academy_id == academy_id)
    )
    wallet = wallet_result.scalar_one_or_none()
    wallet_balance = float(wallet.balance) if wallet else 0.0

    return AcademyDashboardResponse(
        academy_id=academy_id,
        academy_name=academy.name,
        credit_balance=credits,
        total_students=total_students,
        active_students=active_students,
        total_revenue=total_revenue,
        monthly_revenue=monthly_revenue,
        pending_orders=pending_orders,
        active_products=active_products,
        wallet_balance=wallet_balance,
    )


# ============================================================================
# PRODUCT CATALOG & PURCHASING
# ============================================================================

@router.get("/products", response_model=ProductListResponse)
async def get_product_catalog(
    category: Optional[str] = None,
    exam_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """
    Get available products for institutional purchase.
    Includes mock exams, writing reviews, speaking sessions, and courses.
    """
    query = select(Product).where(Product.is_active == True)

    if category:
        try:
            cat_enum = ProductCategory(category)
            query = query.where(Product.category == cat_enum)
        except ValueError:
            pass

    if exam_type:
        query = query.where(Product.exam_types.contains([exam_type]))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated products
    query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
    result = await db.execute(query)
    products = result.scalars().all()

    # Get variants for each product
    product_list = []
    for product in products:
        variant_result = await db.execute(
            select(ProductVariant).where(
                and_(
                    ProductVariant.product_id == product.id,
                    ProductVariant.is_active == True
                )
            )
        )
        variants = variant_result.scalars().all()

        product_list.append({
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "category": product.category.value,
            "exam_types": product.exam_types,
            "base_price": float(product.base_price),
            "features": product.features,
            "variants": [
                {
                    "id": str(v.id),
                    "name": v.name,
                    "price": float(v.price),
                    "credit_cost": v.credit_cost,
                    "attributes": v.attributes,
                }
                for v in variants
            ],
            "bulk_pricing": product.bulk_pricing,
        })

    # Get available categories
    categories = [c.value for c in ProductCategory]

    return ProductListResponse(
        products=product_list,
        total=total,
        categories=categories,
    )


@router.post("/products/purchase")
async def purchase_product(
    academy_id: str,
    request: ProductPurchaseRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Purchase products for the academy.
    Supports wallet, Stripe, or invoice payment methods.
    """
    # Verify academy exists
    academy_result = await db.execute(
        select(Academy).where(Academy.id == academy_id)
    )
    academy = academy_result.scalar_one_or_none()
    if not academy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academy not found"
        )

    # Get product
    product_result = await db.execute(
        select(Product).where(Product.id == request.product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Get variant if specified
    variant = None
    unit_price = product.base_price
    if request.variant_id:
        variant_result = await db.execute(
            select(ProductVariant).where(ProductVariant.id == request.variant_id)
        )
        variant = variant_result.scalar_one_or_none()
        if variant:
            unit_price = variant.price

    # Apply bulk pricing if available
    if product.bulk_pricing:
        for tier in sorted(product.bulk_pricing, key=lambda x: x.get("min_qty", 0), reverse=True):
            if request.quantity >= tier.get("min_qty", 0):
                unit_price = Decimal(str(tier.get("price_per_unit", unit_price)))
                break

    # Calculate total
    subtotal = unit_price * request.quantity
    platform_fee_rate = Decimal("0.03")  # 3% platform fee
    platform_fee = subtotal * platform_fee_rate
    total_amount = subtotal + platform_fee

    # Process payment based on method
    if request.payment_method == "wallet":
        # Check wallet balance
        wallet_result = await db.execute(
            select(AcademyWallet).where(AcademyWallet.academy_id == academy_id)
        )
        wallet = wallet_result.scalar_one_or_none()

        if not wallet or wallet.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient wallet balance. Required: {total_amount}, Available: {wallet.balance if wallet else 0}"
            )

        # Deduct from wallet
        wallet.balance -= total_amount
        wallet.updated_at = datetime.now(timezone.utc)

        # Create wallet transaction
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.PURCHASE,
            amount=-total_amount,
            balance_after=wallet.balance,
            description=f"Purchase: {product.name} x{request.quantity}",
            reference_type="order",
        )
        db.add(transaction)

        payment_status = "completed"

    elif request.payment_method == "stripe":
        # Return Stripe checkout session info (to be completed by frontend)
        return {
            "status": "pending_payment",
            "payment_method": "stripe",
            "checkout_session": {
                "amount": float(total_amount),
                "currency": "usd",
                "product_name": product.name,
                "quantity": request.quantity,
                # In production: create actual Stripe session
                "session_id": f"cs_pending_{academy_id}_{datetime.now(timezone.utc).timestamp()}",
            },
        }

    elif request.payment_method == "invoice":
        payment_status = "pending_invoice"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method"
        )

    # Create order
    order = Order(
        academy_id=academy_id,
        status=OrderStatus.COMPLETED if payment_status == "completed" else OrderStatus.PENDING,
        subtotal=subtotal,
        platform_fee=platform_fee,
        total_amount=total_amount,
        payment_method=request.payment_method,
        is_b2b_sale=False,  # This is a purchase, not a sale
    )
    db.add(order)
    await db.flush()

    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        variant_id=variant.id if variant else None,
        quantity=request.quantity,
        unit_price=unit_price,
        subtotal=subtotal,
    )
    db.add(order_item)

    # If completed, add credits to academy
    if payment_status == "completed" and variant and variant.credit_cost:
        total_credits = variant.credit_cost * request.quantity

        credit_result = await db.execute(
            select(AcademyCreditBalance).where(
                AcademyCreditBalance.academy_id == academy_id
            )
        )
        credit_balance = credit_result.scalar_one_or_none()

        if credit_balance:
            credit_balance.balance += total_credits
            credit_balance.updated_at = datetime.now(timezone.utc)
        else:
            credit_balance = AcademyCreditBalance(
                academy_id=academy_id,
                balance=total_credits,
            )
            db.add(credit_balance)

    await db.commit()

    return {
        "status": "success" if payment_status == "completed" else payment_status,
        "order_id": str(order.id),
        "product": product.name,
        "quantity": request.quantity,
        "total_amount": float(total_amount),
        "payment_method": request.payment_method,
    }


# ============================================================================
# CUSTOM PRICING FOR RESALE
# ============================================================================

@router.post("/pricing/custom")
async def set_custom_pricing(
    academy_id: str,
    request: CustomPricingRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Set custom pricing for products that the academy will resell to students.
    Academy sets their own margin on top of wholesale price.
    """
    # Verify product exists
    product_result = await db.execute(
        select(Product).where(Product.id == request.product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Get wholesale price
    wholesale_price = product.base_price
    if request.variant_id:
        variant_result = await db.execute(
            select(ProductVariant).where(ProductVariant.id == request.variant_id)
        )
        variant = variant_result.scalar_one_or_none()
        if variant:
            wholesale_price = variant.price

    # Validate custom price is above wholesale
    if Decimal(str(request.custom_price)) < wholesale_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom price must be at least {wholesale_price} (wholesale price)"
        )

    # Check for existing pricing
    existing_result = await db.execute(
        select(AcademyProductPrice).where(
            and_(
                AcademyProductPrice.academy_id == academy_id,
                AcademyProductPrice.product_id == request.product_id,
                AcademyProductPrice.variant_id == request.variant_id,
            )
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Update existing pricing
        existing.custom_price = Decimal(str(request.custom_price))
        existing.is_active = request.is_active
        existing.min_quantity = request.min_quantity
        existing.max_discount_percent = (
            Decimal(str(request.max_discount_percent))
            if request.max_discount_percent
            else None
        )
        existing.updated_at = datetime.now(timezone.utc)
        pricing_id = existing.id
    else:
        # Create new pricing
        new_pricing = AcademyProductPrice(
            academy_id=academy_id,
            product_id=request.product_id,
            variant_id=request.variant_id,
            custom_price=Decimal(str(request.custom_price)),
            is_active=request.is_active,
            min_quantity=request.min_quantity,
            max_discount_percent=(
                Decimal(str(request.max_discount_percent))
                if request.max_discount_percent
                else None
            ),
        )
        db.add(new_pricing)
        await db.flush()
        pricing_id = new_pricing.id

    await db.commit()

    margin = float(Decimal(str(request.custom_price)) - wholesale_price)
    margin_percent = (margin / float(wholesale_price)) * 100

    return {
        "status": "success",
        "pricing_id": str(pricing_id),
        "product_id": request.product_id,
        "wholesale_price": float(wholesale_price),
        "custom_price": request.custom_price,
        "margin": margin,
        "margin_percent": round(margin_percent, 2),
        "is_active": request.is_active,
    }


@router.get("/pricing/{academy_id}")
async def get_academy_pricing(
    academy_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get all custom pricing set by an academy.
    """
    query = select(AcademyProductPrice).where(
        AcademyProductPrice.academy_id == academy_id
    )

    # Count total
    count_result = await db.execute(
        select(func.count(AcademyProductPrice.id)).where(
            AcademyProductPrice.academy_id == academy_id
        )
    )
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(AcademyProductPrice.created_at.desc())
    )
    pricing_list = result.scalars().all()

    items = []
    for pricing in pricing_list:
        # Get product info
        product_result = await db.execute(
            select(Product).where(Product.id == pricing.product_id)
        )
        product = product_result.scalar_one_or_none()

        items.append({
            "pricing_id": str(pricing.id),
            "product_id": str(pricing.product_id),
            "product_name": product.name if product else "Unknown",
            "variant_id": str(pricing.variant_id) if pricing.variant_id else None,
            "custom_price": float(pricing.custom_price),
            "is_active": pricing.is_active,
            "min_quantity": pricing.min_quantity,
            "max_discount_percent": (
                float(pricing.max_discount_percent)
                if pricing.max_discount_percent
                else None
            ),
        })

    return {
        "pricing": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# STUDENT MANAGEMENT
# ============================================================================

@router.post("/students/enroll")
async def enroll_student(
    academy_id: str,
    request: StudentEnrollmentRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Enroll a student in a product/service using academy credits.
    This is how academies "sell" to their students.
    """
    # Verify academy has sufficient credits
    credit_result = await db.execute(
        select(AcademyCreditBalance).where(
            AcademyCreditBalance.academy_id == academy_id
        )
    )
    credit_balance = credit_result.scalar_one_or_none()

    if not credit_balance or credit_balance.balance < request.quantity:
        raise InsufficientCreditsError(
            required=request.quantity,
            available=credit_balance.balance if credit_balance else 0
        )

    # Deduct credits
    credit_balance.balance -= request.quantity
    credit_balance.updated_at = datetime.now(timezone.utc)

    # Create or update student enrollment
    existing_enrollment = await db.execute(
        select(StudentEnrollment).where(
            and_(
                StudentEnrollment.academy_id == academy_id,
                StudentEnrollment.user_id == request.student_user_id,
            )
        )
    )
    enrollment = existing_enrollment.scalar_one_or_none()

    if enrollment:
        enrollment.is_active = True
        enrollment.updated_at = datetime.now(timezone.utc)
    else:
        enrollment = StudentEnrollment(
            academy_id=academy_id,
            user_id=request.student_user_id,
            is_active=True,
        )
        db.add(enrollment)

    # Record the sale for the academy (adds to their revenue)
    # Get custom pricing if set
    product_type_to_category = {
        "mock_exam": ProductCategory.MOCK_EXAM,
        "writing_review": ProductCategory.WRITING_REVIEW,
        "speaking_session": ProductCategory.SPEAKING_SESSION,
        "course": ProductCategory.COURSE,
    }

    category = product_type_to_category.get(request.product_type)

    # Find the product
    product_query = select(Product).where(Product.category == category)
    if request.exam_type:
        product_query = product_query.where(
            Product.exam_types.contains([request.exam_type])
        )
    product_result = await db.execute(product_query.limit(1))
    product = product_result.scalar_one_or_none()

    if product:
        # Check for custom pricing
        pricing_result = await db.execute(
            select(AcademyProductPrice).where(
                and_(
                    AcademyProductPrice.academy_id == academy_id,
                    AcademyProductPrice.product_id == product.id,
                    AcademyProductPrice.is_active == True,
                )
            )
        )
        custom_pricing = pricing_result.scalar_one_or_none()

        sale_price = custom_pricing.custom_price if custom_pricing else product.base_price

        # Create B2B sale order
        order = Order(
            academy_id=academy_id,
            status=OrderStatus.COMPLETED,
            subtotal=sale_price * request.quantity,
            platform_fee=Decimal("0"),  # No platform fee on resale
            total_amount=sale_price * request.quantity,
            payment_method="credit",
            is_b2b_sale=True,
        )
        db.add(order)

    await db.commit()

    return {
        "status": "success",
        "student_user_id": request.student_user_id,
        "product_type": request.product_type,
        "exam_type": request.exam_type,
        "quantity": request.quantity,
        "credits_used": request.quantity,
        "remaining_credits": credit_balance.balance,
    }


@router.get("/students/{academy_id}")
async def get_academy_students(
    academy_id: str,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get all students enrolled with an academy.
    """
    query = select(StudentEnrollment).where(
        StudentEnrollment.academy_id == academy_id
    )

    if is_active is not None:
        query = query.where(StudentEnrollment.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(StudentEnrollment.created_at.desc())
    )
    enrollments = result.scalars().all()

    students = [
        {
            "enrollment_id": str(e.id),
            "user_id": str(e.user_id),
            "is_active": e.is_active,
            "enrolled_at": e.created_at.isoformat(),
        }
        for e in enrollments
    ]

    return {
        "students": students,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


# ============================================================================
# SALES ANALYTICS
# ============================================================================

@router.get("/analytics/{academy_id}")
async def get_sales_analytics(
    academy_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get comprehensive sales analytics for an academy.
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        from datetime import timedelta
        start_date = end_date - timedelta(days=30)

    # Get completed B2B sales in date range
    sales_query = select(Order).where(
        and_(
            Order.academy_id == academy_id,
            Order.is_b2b_sale == True,
            Order.status == OrderStatus.COMPLETED,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
        )
    )
    sales_result = await db.execute(sales_query)
    orders = sales_result.scalars().all()

    # Calculate metrics
    total_revenue = sum(float(o.total_amount) for o in orders)
    total_orders = len(orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Group by period
    from collections import defaultdict
    grouped_sales = defaultdict(lambda: {"revenue": 0, "orders": 0})

    for order in orders:
        if group_by == "day":
            key = order.created_at.strftime("%Y-%m-%d")
        elif group_by == "week":
            key = order.created_at.strftime("%Y-W%W")
        else:  # month
            key = order.created_at.strftime("%Y-%m")

        grouped_sales[key]["revenue"] += float(order.total_amount)
        grouped_sales[key]["orders"] += 1

    # Get top products
    item_query = select(OrderItem).join(Order).where(
        and_(
            Order.academy_id == academy_id,
            Order.is_b2b_sale == True,
            Order.status == OrderStatus.COMPLETED,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
        )
    )
    item_result = await db.execute(item_query)
    items = item_result.scalars().all()

    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    for item in items:
        product_sales[str(item.product_id)]["quantity"] += item.quantity
        product_sales[str(item.product_id)]["revenue"] += float(item.subtotal)

    # Sort by revenue
    top_products = sorted(
        product_sales.items(),
        key=lambda x: x[1]["revenue"],
        reverse=True
    )[:10]

    # Get commission earned
    commission_result = await db.execute(
        select(func.sum(CommissionRecord.amount)).where(
            and_(
                CommissionRecord.academy_id == academy_id,
                CommissionRecord.is_paid == True,
                CommissionRecord.created_at >= start_date,
                CommissionRecord.created_at <= end_date,
            )
        )
    )
    total_commission = float(commission_result.scalar() or 0)

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "group_by": group_by,
        },
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "average_order_value": round(avg_order_value, 2),
            "total_commission_earned": round(total_commission, 2),
        },
        "time_series": [
            {"period": k, **v}
            for k, v in sorted(grouped_sales.items())
        ],
        "top_products": [
            {"product_id": pid, **data}
            for pid, data in top_products
        ],
    }


# ============================================================================
# UPSELL OFFERS
# ============================================================================

@router.get("/upsell/{academy_id}", response_model=List[UpsellOfferResponse])
async def get_upsell_offers(
    academy_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[UpsellOfferResponse]:
    """
    Get personalized upsell offers for an academy.
    Based on usage patterns and available products.
    """
    # Get academy credit balance
    credit_result = await db.execute(
        select(AcademyCreditBalance).where(
            AcademyCreditBalance.academy_id == academy_id
        )
    )
    credit_balance = credit_result.scalar_one_or_none()
    current_credits = credit_balance.balance if credit_balance else 0

    offers = []

    # Offer 1: Bulk credit package if running low
    if current_credits < 50:
        offers.append(UpsellOfferResponse(
            offer_id=f"upsell_bulk_credits_{academy_id}",
            title="Bulk Credit Package",
            description="Running low on credits? Get 100 credits at a 20% discount!",
            original_price=500.00,
            offer_price=400.00,
            discount_percent=20.0,
            products=[
                {
                    "name": "100 Mock Exam Credits",
                    "type": "credits",
                    "quantity": 100,
                }
            ],
            valid_until=datetime.now(timezone.utc).replace(
                hour=23, minute=59, second=59
            ),
            terms=["Limited time offer", "Non-refundable", "Credits never expire"],
        ))

    # Offer 2: Premium exam bundle
    offers.append(UpsellOfferResponse(
        offer_id=f"upsell_premium_bundle_{academy_id}",
        title="Premium Exam Bundle",
        description="Get all exam types in one package with expert writing reviews included!",
        original_price=1200.00,
        offer_price=899.00,
        discount_percent=25.0,
        products=[
            {"name": "50 IELTS Mock Exams", "type": "mock_exam", "quantity": 50},
            {"name": "50 TOEFL Mock Exams", "type": "mock_exam", "quantity": 50},
            {"name": "25 Writing Reviews", "type": "writing_review", "quantity": 25},
        ],
        valid_until=datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59
        ),
        terms=["Best value package", "All exam types included", "Priority support"],
    ))

    # Offer 3: Speaking session add-on
    offers.append(UpsellOfferResponse(
        offer_id=f"upsell_speaking_{academy_id}",
        title="Speaking Practice Sessions",
        description="Add AI-powered speaking practice to enhance your students' preparation!",
        original_price=300.00,
        offer_price=249.00,
        discount_percent=17.0,
        products=[
            {"name": "30 Speaking Sessions", "type": "speaking_session", "quantity": 30},
        ],
        valid_until=datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59
        ),
        terms=["AI-powered feedback", "Multiple exam formats", "Instant results"],
    ))

    return offers


# ============================================================================
# WALLET MANAGEMENT
# ============================================================================

@router.get("/wallet/{academy_id}")
async def get_wallet_details(
    academy_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get wallet details and transaction history for an academy.
    """
    # Get or create wallet
    wallet_result = await db.execute(
        select(AcademyWallet).where(AcademyWallet.academy_id == academy_id)
    )
    wallet = wallet_result.scalar_one_or_none()

    if not wallet:
        wallet = AcademyWallet(
            academy_id=academy_id,
            balance=Decimal("0"),
            currency="USD",
        )
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)

    # Get transactions
    tx_result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
        .order_by(WalletTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    transactions = tx_result.scalars().all()

    # Count total transactions
    count_result = await db.execute(
        select(func.count(WalletTransaction.id)).where(
            WalletTransaction.wallet_id == wallet.id
        )
    )
    total_transactions = count_result.scalar() or 0

    return {
        "wallet": {
            "id": str(wallet.id),
            "balance": float(wallet.balance),
            "currency": wallet.currency,
            "updated_at": wallet.updated_at.isoformat(),
        },
        "transactions": [
            {
                "id": str(tx.id),
                "type": tx.type.value,
                "amount": float(tx.amount),
                "balance_after": float(tx.balance_after),
                "description": tx.description,
                "created_at": tx.created_at.isoformat(),
            }
            for tx in transactions
        ],
        "total_transactions": total_transactions,
        "skip": skip,
        "limit": limit,
    }


@router.post("/wallet/{academy_id}/deposit")
async def deposit_to_wallet(
    academy_id: str,
    amount: float = Query(gt=0),
    payment_method: str = Query(default="stripe"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Add funds to academy wallet.
    Returns payment intent for Stripe or invoice details.
    """
    if payment_method == "stripe":
        # In production: create actual Stripe payment intent
        return {
            "status": "pending_payment",
            "payment_method": "stripe",
            "payment_intent": {
                "amount": amount,
                "currency": "usd",
                "client_secret": f"pi_secret_{academy_id}_{datetime.now(timezone.utc).timestamp()}",
            },
        }
    elif payment_method == "invoice":
        return {
            "status": "invoice_pending",
            "invoice_id": f"INV-{academy_id[:8].upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            "amount": amount,
            "due_date": (datetime.now(timezone.utc).replace(day=1) +
                        __import__('datetime').timedelta(days=32)).replace(day=1).isoformat(),
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method. Use 'stripe' or 'invoice'."
        )
